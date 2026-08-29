# Modern Lakehouse Architecture (Air-gapped)

폐쇄망 환경의 금융권 Lakehouse 참조 아키텍처입니다. 좌에서 우로 데이터가 흐르며,
7개 Layer와 그 사이를 잇는 10개의 경로로 구성됩니다.

![Lakehouse Reference Architecture](../assets/lakehouse-architecture-lr.svg)

---

## 구성 소프트웨어

| Layer | 제품 |
|---|---|
| Ingestion | Cloudera CFM (Apache NiFi) |
| Streaming Bus | Cloudera CDP — Kafka, Streams Messaging Manager, ZooKeeper |
| Storage | MinIO (S3 호환) + Apache Iceberg |
| Processing & Orchestration | Cloudera CDE — Airflow, Spark on Kubernetes |
| Data Federation | Starburst Trino |
| Consumption | Spotfire, Cloudera AI |

---

## Layer 설명

### 1. Data Source Layer

금융권 원천을 성격별로 다섯 도메인으로 묶었습니다. 각 도메인은 접근 방식과 규제 제약이
서로 달라서, 뒤쪽 Layer의 연동 방식을 결정하는 기준선이 됩니다.

| 도메인 | 원천 | 수집 특성 |
|---|---|---|
| 계정계·정보계 | Oracle Exadata, DB2, DW, 여·수신 원장, 회계 | CDC 중심, 정합성 최우선 |
| 카드·결제 | 승인·매입 거래 원장, VAN·PG 전문 로그 | 대용량 트랜잭션, 준실시간 |
| 채널 | 인터넷뱅킹, 모바일앱, ATM, 콜센터 STT | 로그·비정형 혼재 |
| 대외계·시장 | 금융결제원, 신용정보원, KRX, Bloomberg | 외부 규격 전문, 배치 위주 |
| 리스크·컴플라이언스 | FDS 이벤트, AML/STR, 약관·규정 문서 | 이벤트 스트림 + 문서(RAG 대상) |

> **설계 주의** 계정계 운영 DB에 로그마이너 기반 CDC를 직접 거는 것은 성능 영향과 감사
> 이슈를 유발합니다. 대기계 또는 정보계 복제본을 대상으로 잡는 것을 권장합니다.

### 2. Ingestion Layer — Cloudera CFM

원천마다 다른 프로토콜을 하나의 흐름 설계 도구로 흡수하는 Layer입니다.

- **수집·연결** — DB, 파일, MQ, API, 스트림. 400+ 프로세서로 연동 코드를 제거
- **변환** — CSV/XML/JSON을 Parquet·Avro로 통일, 스키마 검증, 레코드 단위 처리
- **라우팅·흐름 제어** — 조건 분기, 우선순위 큐, Back-pressure, 재시도
- **전달 보증·추적** — Guaranteed Delivery, Data Provenance
- **운영·보안** — GUI 흐름 설계, 실시간 모니터링, Site-to-Site, TLS

금융권에서 결정적인 것은 **Data Provenance**입니다. 데이터가 어디서 와서 어떻게 변형됐는지를
건 단위로 남기므로 감독당국 소명과 내부 감사의 근거가 됩니다.

### 3. Streaming Bus Layer — Cloudera CDP

생산자와 소비자를 시간적으로 분리하는 버퍼입니다. 소비자가 중단돼도 원천은 계속 적재할 수
있고, 하나의 이벤트를 여러 소비자가 각자의 속도로 읽습니다.

- **Kafka** — `raw.*` / `cdc.*` / `evt.*` 토픽, replication factor 3
- **Streams Messaging Manager** — 토픽·컨슈머·지연(lag) 관제
- **ZooKeeper Ensemble** — 브로커 등록, 리더 선출 (3 또는 5 노드)

CFM과 CDE가 서로 다른 컨슈머 그룹으로 붙으므로, 그룹 ID를 분리하고 SMM에서 각각의 lag을
따로 관제해야 합니다.

### 4. Storage Layer — MinIO + Iceberg

단일 저장소에 정형 3계층과 비정형 문서 존을 함께 둡니다.

```
s3a://lake/bronze/    원천 그대로 (append)
s3a://lake/silver/    정제 · 중복제거 · SCD
s3a://lake/gold/      집계 · 마트 · 피처
s3a://lake/docs/      문서 · 이미지 · 임베딩 (RAG)
```

Table Format은 Iceberg Table, Catalog는 Iceberg REST Catalog 단일 구성입니다. Hive
Metastore를 제거해 Thrift 의존성을 없앴고, REST 스펙만 맞추면 엔진을 추가·교체할 수 있습니다.
스냅샷과 time-travel은 금융권의 시점 조회와 감사 재현에 직접 활용됩니다.

`docs/` 존은 내부적으로 원본과 파생물을 나누는 편이 관리에 유리합니다.

```
docs/raw/       원본 PDF·이미지 (불변, 보존기한 관리)
docs/parsed/    텍스트 추출 결과 (Markdown/JSON)
docs/chunks/    청킹 결과 + 메타데이터 (Iceberg 테이블)
docs/vectors/   임베딩 (Iceberg 또는 PGVector/ES 동기화)
```

임베딩 모델을 교체할 때 `parsed/`부터 재처리하면 되므로, 가장 비싼 단계인 파싱 비용을
반복하지 않습니다.

> **설계 주의** REST Catalog 구현체(Nessie, Polaris, Lakekeeper 등)는 대부분 PostgreSQL을
> 메타 저장소로 사용합니다. 개요도에는 표기하지 않았으나 HA 구성과 백업 정책은 별도로
> 수립해야 합니다.

### 5. Processing & Orchestration Layer — Cloudera CDE

무거운 변환과 일정 관리를 담당합니다.

- **Airflow** — DAG 스케줄, 의존성, SLA. NiFi 흐름 트리거(REST API), Spark Job 제출,
  Trino DDL/MERGE 실행(JDBC)
- **Spark on K8s** — Bronze→Silver→Gold 변환, Iceberg MERGE·Compaction, Snapshot Expiration

NiFi와 역할이 겹쳐 보이지만 경계는 명확합니다. **흐름 내부 제어는 NiFi, 테이블 단위
의존성과 SLA는 Airflow**입니다.

### 6. Data Federation Layer — Starburst Trino

서로 다른 저장소를 하나의 SQL 네임스페이스로 묶는 단일 조회 접점입니다.

- **Connectors** — Iceberg→MinIO, Kafka(실시간 조회), Hive(레거시 HDFS), Oracle(페더레이션)
- **AI Features** — NL-to-SQL, RAG, MCP Server
- **Vector DB Support** — Iceberg, PostgreSQL/PGVector, Elasticsearch

상위 애플리케이션이 저장소별 클라이언트를 각각 연결하지 않아도 되는 것이 이 Layer의
존재 이유입니다.

Vector Store 선택 기준:

| 저장소 | 적합 규모 | 강점 |
|---|---|---|
| Iceberg | 수천만~억 건 | 스냅샷 단위 관리, 전체 재색인 유리 |
| PostgreSQL/PGVector | 수십만~수백만 건 | HNSW 인덱스, 메타데이터 필터와 트랜잭션 |
| Elasticsearch | 문서 검색 중심 | 한국어 형태소 분석(Nori) + BM25, RRF 하이브리드 |

### 7. Consumption Layer

- **Spotfire** — 대시보드, Ad-hoc 분석. In-DB 모드로 Trino 직접 질의
- **Cloudera AI** — AI Workbench(모델 학습·서빙), AI Studio, Agent
- **SQL Client / Notebook / API**

성격이 다른 두 소비 패턴이 공존합니다. 집계 결과 조회는 Trino를, 대용량 학습 데이터는
스토리지 직접 접근을 사용합니다.

---

## Layer 간 경로

| 경로 | 표기 | 의미 | 왜 이렇게 설계했는가 |
|---|---|---|---|
| 1 → 2 | 실선 | 원천 수집 | 기본 경로. 검증과 이력 추적이 필요한 모든 데이터 |
| 1 → 3 | 주황 점선 | 실시간 직결 | CFM 경유 시 홉이 늘어 지연 발생. 초 단위 요건 토픽만 선별 적용 |
| 2 → 3 | 실선 | 이벤트 발행 | 수집한 데이터를 토픽으로 발행 |
| 3 → 2 | 주황 점선 | 토픽 소비 | 토픽을 구독해 경량 라우팅 또는 외부 시스템 전달 |
| 2 → 4 | 실선 | 배치 적재 | 스트리밍이 아닌 대부분의 데이터 |
| 3 → 5 | 주황 점선 | 스트림 소비 | Kafka→MinIO 직결을 두지 않은 이유는 Iceberg 커밋과 스키마 관리를 Spark가 담당하기 때문 |
| 4 ↔ 5 | 양방향 실선 | 변환 왕복 | 읽어서 정제하고 다시 쓰는 medallion 파이프라인의 실제 동작 |
| 4 → 6 | 실선 | 카탈로그 조회 | Trino가 Iceberg 테이블을 읽는 주 경로 |
| 1 → 6 | 보라 일점쇄선 | 원천 직접 페더레이션 | 적재 지연을 허용할 수 없거나, 규제상 복제본 생성이 불가한 데이터 |
| 4 → 7 | 파랑 실선 | S3 API 직접 접근 | 학습 데이터 수천만 건을 Trino로 조회하면 Coordinator 병목. 문서 원본은 SQL 대상이 아님 |
| 6 → 7 | 실선 | SQL 조회 | 행 수는 적고 연산이 무거운 대시보드 질의 |

### 조회 경로 선택 기준

```
행 수가 많고 SQL 연산이 적다   →  4 → 7  (S3 직접 접근)
행 수가 적고 SQL 연산이 무겁다  →  6 → 7  (Trino 경유)
원천의 최신 상태가 필요하다     →  1 → 6  (페더레이션)
```

---

## 검토 시 확인할 사항

**1. Trino 우회 경로의 접근 제어**
4 → 7 직접 접근에는 Starburst의 행·열 수준 마스킹이 적용되지 않습니다. MinIO IAM 정책과
버킷 경로 단위로 별도 통제를 수립해야 합니다.

**2. 페더레이션 대상 시스템의 부하**
1 → 6 경로는 원천에 직접 부하를 발생시킵니다. 대기계나 정보계 복제본에 커넥터를 연결하고,
Starburst 리소스 그룹으로 동시 실행 쿼리 수와 스캔 행 수를 제한해야 합니다.

**3. 실시간 적재의 지연 하한**
Kafka→MinIO 직결을 제거했으므로 스트리밍 적재 지연은 Spark 마이크로배치 주기에 종속됩니다.
초 단위 조회가 필요하면 Starburst의 Kafka 커넥터를 활용합니다.

**4. MinIO 연동 설정**
Trino, Spark, NiFi 모두에 `path-style-access=true`를 설정해야 합니다. 가상 호스트 스타일
URL은 폐쇄망 DNS에서 해석되지 않는 경우가 많습니다.

---

## 다이어그램 재생성

```bash
python scripts/generate_architecture_svg.py -o assets/lakehouse-architecture-lr.svg
```

레이아웃과 문구는 `scripts/generate_architecture_svg.py` 상단의 `BOXES`, `EDGES`,
`PALETTE` 상수에 선언되어 있습니다. `assets/` 의 SVG는 빌드 산출물이므로, 수정이
필요하면 SVG를 직접 편집하지 말고 스크립트를 고친 뒤 재생성하시기 바랍니다.
