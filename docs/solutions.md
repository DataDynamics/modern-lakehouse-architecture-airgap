# 구성 솔루션별 역할

이 문서는 [lakehouse-architecture-lr.svg](../assets/lakehouse-architecture-lr.svg) 에
그려진 범위에 한정해, 각 솔루션이 이 아키텍처 안에서 무엇을 담당하고 무엇을 담당하지
않는지를 정리한 것입니다. 제품의 전체 기능 소개가 아니라 **이 그림에서의 역할 정의**가
목적이므로, 다이어그램에 표기되지 않은 기능은 다루지 않습니다. 제품이 제공하는 기능
전체 목록은 [solution-features.md](solution-features.md)에 따로 정리했습니다.

## 목차

- [배치 요약](#배치-요약)
- [Cloudera CFM — Layer 2, Ingestion](#cloudera-cfm--layer-2-ingestion)
- [Cloudera CDP — Layer 3, Streaming Bus](#cloudera-cdp--layer-3-streaming-bus)
- [MinIO AIStor — Layer 4, Storage](#minio-aistor--layer-4-storage)
- [Cloudera CDE — Layer 5, Processing & Orchestration](#cloudera-cde--layer-5-processing--orchestration)
- [Starburst Enterprise — Layer 6, Data Federation](#starburst-enterprise--layer-6-data-federation)
- [Spotfire — Layer 7, Consumption](#spotfire--layer-7-consumption)
- [Cloudera AI — Layer 7, Consumption](#cloudera-ai--layer-7-consumption)
- [역할이 겹쳐 보이는 지점](#역할이-겹쳐-보이는-지점)
- [폐쇄망 전제에서의 공통 사항](#폐쇄망-전제에서의-공통-사항)
- [용어집](#용어집)
  - [제품·구성요소](#제품구성요소)
  - [데이터 흐름](#데이터-흐름)
  - [저장](#저장)
  - [조회·통제](#조회통제)
  - [AI](#ai)

## 배치 요약

| Layer | 솔루션 | 한 줄 역할 |
|---|---|---|
| 2. Ingestion | Cloudera CFM | 원천의 이기종 프로토콜을 흡수해 정규화하고 하류로 배분 |
| 3. Streaming Bus | Cloudera CDP | 생산자와 소비자를 시간적으로 분리하는 이벤트 버퍼 |
| 4. Storage | MinIO AIStor | 정형 3계층과 문서 존을 담는 단일 S3 호환 저장소 |
| 5. Processing & Orchestration | Cloudera CDE | 무거운 변환 실행과 테이블 단위 일정·의존성 관리 |
| 6. Data Federation | Starburst Enterprise | 이기종 저장소를 하나의 SQL 네임스페이스로 통합 |
| 7. Consumption | Spotfire | 대시보드와 Ad-hoc 분석의 SQL 소비 접점 |
| 7. Consumption | Cloudera AI | 모델 학습·서빙과 Agent의 데이터 소비 접점 |

---

## Cloudera CFM — Layer 2, Ingestion

Apache NiFi 기반. 원천마다 다른 접속 방식과 포맷을 **하나의 흐름 설계 도구로 흡수**하는
것이 이 아키텍처에서의 역할입니다. 상류(Layer 1)의 다양성을 여기서 끝내고, 하류에는
정규화된 형태만 전달합니다.

**담당하는 것**

- **수집·연결** — DB, 파일, MQ, API, 스트림을 400+ 프로세서로 연동. 원천별 연동 코드를
  작성하지 않는 것이 이 박스의 존재 이유입니다
- **변환** — CSV / XML / JSON 을 Parquet · Avro 로 통일, 스키마 검증, 레코드 단위 처리
- **라우팅·흐름 제어** — 조건 분기, 우선순위 큐, Back-pressure, 재시도
- **전달 보증·추적** — Guaranteed Delivery, Data Provenance
- **운영·보안** — GUI 흐름 설계, 실시간 모니터링, Site-to-Site, TLS

**연결 경로**

| 방향 | 상대 | 성격 |
|---|---|---|
| 수신 | 1. Data Source | JDBC/CDC · MQ · SFTP · REST |
| 송신 | 3. Streaming Bus | 수집 데이터를 토픽으로 발행 |
| 수신 | 3. Streaming Bus | 토픽을 구독해 경량 라우팅·외부 전달 (주황 점선) |
| 송신 | 4. Storage | 스트리밍이 아닌 대부분의 데이터를 배치 적재 |

Kafka 와 양방향으로 붙는 점이 특징입니다. 발행만 하는 것이 아니라 소비자 역할도 하므로,
CDE 와 **컨슈머 그룹 ID를 분리**해야 SMM 에서 lag 을 따로 관제할 수 있습니다.

**담당하지 않는 것**

테이블 단위 의존성과 SLA 관리는 CDE Airflow 의 몫입니다. 경계는 **흐름 내부 제어는
NiFi, 테이블 간 의존성은 Airflow** 로 나눕니다. 대용량 조인·집계 변환도 CFM 이 아니라
Spark 에서 수행합니다.

**금융권 관점**

Data Provenance 가 결정적입니다. 데이터가 어디서 와서 어떻게 변형됐는지를 건 단위로
남기므로 감독당국 소명과 내부 감사의 근거 자료가 됩니다.

---

## Cloudera CDP — Layer 3, Streaming Bus

이 그림에서 CDP 는 **Kafka 를 중심으로 한 스트리밍 버스**로 한정해 표기했습니다.
생산자와 소비자를 시간적으로 분리하는 버퍼이며, 소비자가 중단돼도 원천은 계속 적재할 수
있고 하나의 이벤트를 여러 소비자가 각자의 속도로 읽습니다.

**담당하는 것**

- **Apache Kafka** — `raw.*` / `cdc.*` / `evt.*` 토픽 체계, partition 구성,
  replication factor 3
- **Streams Messaging Manager** — 토픽·컨슈머·지연(lag) 관제
- **ZooKeeper Ensemble (3 또는 5 노드)** — 브로커 등록, 리더 선출

**연결 경로**

| 방향 | 상대 | 성격 |
|---|---|---|
| 수신 | 1. Data Source | 실시간 직결 (주황 점선). CDC · MQ · 채널 로그 · FDS |
| 수신 | 2. Ingestion | CFM 이 수집한 데이터의 이벤트 발행 |
| 송신 | 2. Ingestion | 토픽 소비 (주황 점선) |
| 송신 | 5. Processing | Kafka 소비 → Spark Structured Streaming (주황 점선) |
| 조회 | 6. Federation | Starburst Kafka 커넥터가 토픽을 직접 조회 |

원천에서 CFM 을 거치지 않고 **직결되는 주황 점선**이 있는 이유는 홉이 늘면 지연이
발생하기 때문입니다. 초 단위 요건이 있는 토픽만 선별 적용하고, 나머지는 검증과 이력
추적이 가능한 CFM 경유 경로를 사용합니다.

**담당하지 않는 것**

Kafka 에서 MinIO 로 직결하는 경로를 두지 않았습니다. Iceberg 커밋과 스키마 관리를
Spark 가 담당하기 때문이며, 그 결과 **스트리밍 적재 지연은 Spark 마이크로배치 주기에
종속**됩니다. 초 단위 조회가 필요하면 적재를 기다리지 말고 Starburst 의 Kafka 커넥터로
토픽을 직접 조회합니다.

---

## MinIO AIStor — Layer 4, Storage

이 아키텍처의 **단일 저장 계층**입니다. S3 호환 API 를 제공하므로 CFM, Spark, Trino,
Cloudera AI 가 모두 같은 프로토콜로 같은 데이터에 접근합니다. 폐쇄망에서 오브젝트
스토리지를 내부에 두기 위한 선택입니다.

**담당하는 것**

- **정형 3계층 + 문서 존** — 하나의 버킷 안에 medallion 구조와 비정형 문서를 함께 배치

  ```
  s3a://lake/bronze/    원천 그대로 (append)
  s3a://lake/silver/    정제 · 중복제거 · SCD
  s3a://lake/gold/      집계 · 마트 · 피처
  s3a://lake/docs/      문서 · 이미지 · 임베딩 (RAG)
  ```

- **Table Format : Iceberg Table** — snapshot, time-travel, schema evolution.
  금융권의 시점 조회와 감사 재현에 직접 활용됩니다
- **Catalog : Iceberg REST Catalog** — Hive Metastore 를 제거해 Thrift 의존성을 없앴고,
  REST 스펙만 맞추면 엔진을 추가·교체할 수 있습니다

**연결 경로**

| 방향 | 상대 | 성격 |
|---|---|---|
| 수신 | 2. Ingestion | 배치 적재 |
| 양방향 | 5. Processing | 읽어서 정제하고 다시 쓰는 medallion 왕복 |
| 송신 | 6. Federation | Trino Iceberg 커넥터의 주 조회 경로 |
| 송신 | 7. Consumption | S3 API 직접 접근 (파랑 실선) |

**담당하지 않는 것**

접근 제어의 일부만 담당합니다. Layer 7 이 **Trino 를 우회해 S3 로 직접 접근**하는
파랑 실선 경로에는 Starburst 의 행·열 수준 마스킹이 적용되지 않으므로, MinIO IAM
정책과 버킷 경로 단위 통제를 별도로 수립해야 합니다.

**설계 시 주의**

- Trino, Spark, NiFi 모두에 `path-style-access=true` 를 설정합니다. 가상 호스트 스타일
  URL 은 폐쇄망 DNS 에서 해석되지 않는 경우가 많습니다
- REST Catalog 구현체(Nessie, Polaris, Lakekeeper 등)는 대부분 PostgreSQL 을 메타
  저장소로 사용합니다. 개요도에는 표기하지 않았으나 HA 구성과 백업 정책이 필요합니다

---

## Cloudera CDE — Layer 5, Processing & Orchestration

무거운 변환의 **실행 엔진**과 파이프라인의 **일정 관리자**를 함께 제공합니다. 이 그림에서
CDE 는 두 개의 하위 블록으로 나뉩니다.

**Airflow — DAG 스케줄 · 의존성 · SLA**

다른 Layer 를 직접 호출해 전체 파이프라인을 구동하는 제어 주체입니다.

- NiFi 흐름 트리거 (REST API)
- Spark Job 제출
- Trino DDL / MERGE 실행 (JDBC)

**Spark on Kubernetes — 변환 실행**

- Bronze → Silver → Gold 변환
- Iceberg MERGE · Compaction · Snapshot Expiration
- Kafka 토픽을 Structured Streaming 으로 소비해 Iceberg 에 커밋

**연결 경로**

| 방향 | 상대 | 성격 |
|---|---|---|
| 수신 | 3. Streaming Bus | Kafka 소비 → Spark Structured Streaming (주황 점선) |
| 양방향 | 4. Storage | medallion 변환 왕복 |
| 제어 | 2 · 6 | NiFi 흐름 트리거, Trino DDL/MERGE 실행 |

**담당하지 않는 것**

원천 접속과 프로토콜 변환은 CFM 의 몫입니다. CDE 는 이미 수집된 데이터를 대상으로
동작하며, 대화형 조회 서비스도 제공하지 않습니다 — 조회는 Starburst 가 받습니다.

**역할 경계**

Kafka → MinIO 직결을 두지 않은 설계 결정 때문에, **스트리밍 적재의 정합성 책임이 전부
Spark 에 모여 있습니다.** Iceberg 커밋 주기와 Compaction 정책이 곧 실시간 조회 품질을
결정하므로 이 Layer 의 튜닝 비중이 큽니다.

---

## Starburst Enterprise — Layer 6, Data Federation

서로 다른 저장소를 하나의 SQL 네임스페이스로 묶는 **단일 조회 접점**입니다. 상위
애플리케이션이 저장소별 클라이언트를 각각 연결하지 않아도 되는 것이 이 Layer 의 존재
이유입니다.

**담당하는 것**

- **구성** — Coordinator ×1 (HA), Worker ×N (autoscale)
- **Connectors**
  - Iceberg → MinIO (주 조회 경로)
  - Kafka → 실시간 조회 (적재 지연을 우회하는 경로)
  - Hive → 레거시 HDFS
  - Oracle → 원천 페더레이션
- **AI Features** — NL-to-SQL, RAG, MCP Server
- **Vector DB Support** — Iceberg, PostgreSQL/PGVector, Elasticsearch

**연결 경로**

| 방향 | 상대 | 성격 |
|---|---|---|
| 수신 | 4. Storage | Iceberg 카탈로그 조회 |
| 수신 | 1. Data Source | 원천 직접 페더레이션 (보라 일점쇄선) |
| 수신 | 3. Streaming Bus | Kafka 커넥터로 토픽 직접 조회 |
| 송신 | 7. Consumption | JDBC / ODBC |

**원천 직접 페더레이션 경로 (1 → 6)**

적재를 거치지 않고 원천을 직접 조회하는 유일한 경로입니다. 적재 지연을 허용할 수 없거나,
규제상 복제본 생성이 불가한 데이터에 한정합니다. **원천에 직접 부하가 발생**하므로 대기계
또는 정보계 복제본에 커넥터를 연결하고, 리소스 그룹으로 동시 실행 쿼리 수와 스캔 행 수를
제한해야 합니다.

**Vector Store 선택 기준**

| 저장소 | 적합 규모 | 강점 |
|---|---|---|
| Iceberg | 수천만~억 건 | 스냅샷 단위 관리, 전체 재색인 유리 |
| PostgreSQL/PGVector | 수십만~수백만 건 | HNSW 인덱스, 메타데이터 필터와 트랜잭션 |
| Elasticsearch | 문서 검색 중심 | 한국어 형태소 분석(Nori) + BM25, RRF 하이브리드 |

**담당하지 않는 것**

대용량 스캔을 담당하지 않습니다. 학습 데이터 수천만 건을 Trino 로 조회하면 Coordinator
병목이 발생하므로, 그런 소비는 Layer 4 → 7 의 S3 직접 접근 경로로 우회시킵니다.
데이터를 저장하지도, 변환 일정을 관리하지도 않습니다.

---

## Spotfire — Layer 7, Consumption

**SQL 조회 계열 소비 접점**입니다. 행 수는 적고 연산이 무거운 대시보드 질의를 담당합니다.

**담당하는 것**

- 대시보드, Ad-hoc 분석
- In-DB 모드로 Trino 직접 질의 — 데이터를 BI 서버로 복제하지 않고 Starburst 에서
  연산합니다

**연결 경로**

Starburst Enterprise 와 JDBC / ODBC 로 연결합니다. 이 그림에서 Spotfire 는 MinIO 에
직접 붙지 않습니다.

**금융권 관점**

In-DB 모드를 사용하면 조회가 전부 Trino 를 경유하므로, Starburst 의 행·열 수준 마스킹과
접근 제어가 그대로 적용됩니다. 데이터 사본이 BI 계층에 남지 않는다는 점이 통제상
유리합니다.

---

## Cloudera AI — Layer 7, Consumption

**AI 계열 소비 접점**입니다. Spotfire 와 달리 두 경로를 함께 사용합니다.

**담당하는 것**

- **AI Workbench** — 모델 학습 · 서빙
- **AI Studio · Agent**

**연결 경로**

| 경로 | 상대 | 용도 |
|---|---|---|
| S3 API 직접 접근 (파랑 실선) | 4. Storage | 학습 데이터 대량 스캔, `docs/` 문서 원본 |
| JDBC / ODBC | 6. Federation | 집계 결과·피처 조회 |

**두 경로를 나눈 이유**

학습 데이터 수천만 건을 Trino 로 조회하면 Coordinator 가 병목이 되고, 문서 원본은 애초에
SQL 조회 대상이 아닙니다. 반대로 gold 마트의 집계 결과처럼 행 수가 적고 연산이 무거운
조회는 Trino 를 경유하는 편이 낫습니다.

```
행 수가 많고 SQL 연산이 적다   →  4 → 7  (S3 직접 접근)
행 수가 적고 SQL 연산이 무겁다  →  6 → 7  (Trino 경유)
원천의 최신 상태가 필요하다     →  1 → 6  (페더레이션)
```

**Starburst AI Features 와의 관계**

Layer 6 의 NL-to-SQL 과 RAG 는 추론 엔드포인트를 필요로 합니다. 폐쇄망에서는 외부 모델
API 를 호출할 수 없으므로 Cloudera AI 의 모델 서빙이 그 공급자가 됩니다. 즉 Cloudera AI 는
**Layer 7 의 소비자이면서 동시에 Layer 6 AI 기능의 공급자**로도 동작합니다.

**주의**

S3 직접 접근 경로에는 Starburst 의 마스킹이 적용되지 않습니다. 학습 데이터셋 구성 단계에서
비식별 처리를 완료하거나, MinIO 버킷 경로 단위 IAM 정책으로 통제해야 합니다.

---

## 역할이 겹쳐 보이는 지점

| 비교 | 경계 |
|---|---|
| CFM vs CDE Airflow | 흐름 **내부** 제어와 백프레셔는 NiFi, 테이블 **간** 의존성과 SLA 는 Airflow |
| CFM vs CDE Spark | 레코드 단위 포맷 변환·라우팅은 NiFi, 조인·집계·Iceberg MERGE 는 Spark |
| CDP Kafka vs MinIO | 소비되면 만료되는 단기 버퍼는 Kafka, 보존 대상 원본은 MinIO |
| Starburst vs MinIO 직접 접근 | 통제된 SQL 조회는 Trino, 대용량 스캔·문서 원본은 S3 직접 |
| Starburst vs CDE Spark | 대화형 조회는 Trino, 스케줄 기반 대량 변환은 Spark |

## 폐쇄망 전제에서의 공통 사항

- 모든 솔루션이 내부망에 배치되며 외부 서비스 호출 경로가 없습니다. Starburst 의
  NL-to-SQL · RAG 도 내부 모델 서빙(Cloudera AI)에 의존합니다
- S3 접근은 예외 없이 `path-style-access=true` 로 통일합니다
- 제품 설치 미디어, 컨테이너 이미지, 라이브러리 의존성은 내부 레지스트리·미러를 통해
  공급해야 하며, 이 부분은 다이어그램의 범위 밖입니다

---

## 용어집

이 문서에 등장하는 용어입니다. Layer별 상세 설명은
[architecture.md](architecture.md), 제품이 제공하는 기능 목록은
[solution-features.md](solution-features.md)를 참고하십시오.

### 제품·구성요소

| 용어 | 설명 |
|---|---|
| Cloudera CFM | Cloudera Flow Management. Apache NiFi 기반의 수집·흐름 관리 제품 |
| Apache NiFi | GUI로 데이터 흐름을 설계하고 전달을 보증하는 데이터 통합 도구 |
| Cloudera CDP | Cloudera Data Platform. 이 아키텍처에서는 Kafka 중심의 스트리밍 버스를 가리킵니다 |
| Streams Messaging Manager (SMM) | Kafka의 토픽·컨슈머·지연을 관제하는 운영 도구 |
| ZooKeeper Ensemble | 브로커 등록과 리더 선출을 담당하는 코디네이션 노드 묶음. 3 또는 5노드로 홀수 구성합니다 |
| MinIO AIStor | MinIO의 상용 오브젝트 스토리지 제품. S3 API를 네이티브로 제공합니다 |
| Cloudera CDE | Cloudera Data Engineering. Airflow와 Spark on Kubernetes를 제공합니다 |
| Starburst Enterprise | 분산 SQL 질의 엔진 Trino의 상용 배포판 |
| Spotfire | 시각화 기반 분석 플랫폼 |
| Cloudera AI | 모델 학습·서빙과 AI 에이전트를 제공하는 제품 |
| AI Workbench | Cloudera AI에서 모델 학습·서빙을 수행하는 작업 환경 |
| Agent | 도구를 사용해 다단계 작업을 스스로 수행하는 AI 실행 단위 |

### 데이터 흐름

| 용어 | 설명 |
|---|---|
| CDC | Change Data Capture. 원본 DB의 변경분만 추출해 전달하는 방식 |
| 배치 | 일정 주기로 데이터를 모아 한 번에 처리하는 방식 |
| 스트리밍 | 발생하는 이벤트를 연속적으로 처리하는 방식 |
| 마이크로배치 | 스트림을 짧은 시간 단위로 잘라 배치처럼 처리하는 방식 |
| Structured Streaming | Spark의 스트리밍 처리 방식 |
| Back-pressure | 하류가 처리하지 못할 때 상류 유입을 억제하는 흐름 제어 |
| Guaranteed Delivery | 장애 시에도 데이터 유실을 막는 전달 보증 |
| Data Provenance | 데이터의 출처와 변형 이력을 건 단위로 기록하는 기능 |
| Site-to-Site | NiFi 인스턴스 간 전용 전송 프로토콜 |
| 컨슈머 그룹 | Kafka에서 토픽을 나눠 읽는 소비자 묶음. CFM과 CDE는 그룹 ID를 분리해야 합니다 |
| lag | 컨슈머가 최신 메시지보다 뒤처진 정도 |
| 토픽 | Kafka에서 메시지를 분류해 담는 논리적 채널 |
| replication factor | 파티션 복제본 수. 3이면 브로커 2대 장애까지 견딥니다 |
| 홉 | 데이터가 거쳐 가는 중간 구간. 홉이 늘수록 지연이 증가합니다 |

### 저장

| 용어 | 설명 |
|---|---|
| medallion | Bronze → Silver → Gold로 단계적으로 정제하는 레이어링 패턴 |
| Bronze · Silver · Gold | 각각 원천 그대로, 정제 완료, 소비용 가공 단계의 계층 |
| SCD | Slowly Changing Dimension. 변하는 속성의 이력 관리 기법 |
| Apache Iceberg | 오브젝트 스토리지 위의 테이블 포맷. 스냅샷과 스키마 변경을 지원합니다 |
| Iceberg REST Catalog | Iceberg 메타데이터를 REST 규격으로 제공하는 카탈로그 |
| snapshot · time-travel | 특정 시점의 테이블 상태 기록과, 그 시점으로 되돌려 조회하는 기능 |
| MERGE · Compaction | 신규 삽입·기존 갱신을 함께 처리하는 연산과, 작은 파일을 병합하는 유지관리 작업 |
| `s3a://` | Hadoop 계열 엔진의 S3 호환 저장소 접근 스킴 |
| path-style-access | `호스트/버킷/키` 형식의 S3 접근 방식. 폐쇄망 DNS 환경에서 필요합니다 |
| WORM | Write Once Read Many. 한 번 기록하면 변경·삭제할 수 없는 보존 방식 |

### 조회·통제

| 용어 | 설명 |
|---|---|
| 페더레이션 | 데이터를 모으지 않고 여러 원천을 질의 시점에 통합 조회하는 방식 |
| Connector | Trino가 개별 데이터 소스에 접속하기 위한 플러그인 |
| Coordinator · Worker | 질의를 계획·분배하는 노드와, 실제 연산을 수행하는 노드 |
| 리소스 그룹 | 동시 실행 질의 수와 자원 사용량을 제한하는 통제 단위 |
| 마스킹 | 민감 정보를 가리거나 대체해 조회 결과에 노출되지 않게 하는 기법 |
| 행·열 수준 통제 | 권한에 따라 조회 가능한 행과 열을 제한하는 접근 제어 |
| IAM | Identity and Access Management. 사용자·정책 기반 접근 통제 |
| In-DB 모드 | BI 도구가 데이터를 가져오지 않고 원천에서 연산해 결과만 받는 방식 |
| JDBC · ODBC | 각각 Java 기반, 언어 중립적 DB 접속 표준 |
| S3 API 직접 접근 | Trino를 거치지 않고 오브젝트 스토리지에서 직접 읽는 경로. 마스킹이 적용되지 않습니다 |

### AI

| 용어 | 설명 |
|---|---|
| RAG | 관련 문서를 검색해 근거로 제공한 뒤 답변을 생성하는 방식 |
| 임베딩 | 텍스트를 의미가 반영된 숫자 벡터로 변환한 것 |
| NL-to-SQL | 자연어 질문을 SQL로 변환하는 기능 |
| MCP | Model Context Protocol. AI 에이전트의 외부 도구·데이터 접근 규약 |
| Vector Store | 임베딩 벡터를 저장하고 유사도 검색을 제공하는 저장소 |
| PGVector · HNSW | PostgreSQL의 벡터 검색 확장과, 근사 최근접 이웃 검색 인덱스 구조 |
| BM25 · Nori · RRF | 단어 빈도 기반 랭킹 알고리즘, 한국어 형태소 분석기, 서로 다른 검색 결과의 순위 결합 기법 |
| 모델 서빙 | 학습된 모델을 호출 가능한 엔드포인트로 배포해 운영하는 것 |
| 추론 엔드포인트 | 모델에 입력을 보내 결과를 받는 API 접점. 폐쇄망에서는 내부에 두어야 합니다 |
| 비식별 처리 | 개인을 특정할 수 없도록 데이터를 가공하는 것 |
