# Modern Lakehouse Architecture (Air-gapped)

폐쇄망 환경의 금융권 Lakehouse 참조 아키텍처입니다. 좌에서 우로 데이터가 흐르며,
7개 Layer와 이를 뒷받침하는 모델 서빙 · 고객 AI Agent 구성요소, 그리고 이들을 잇는
14개의 경로로 구성됩니다.

![Lakehouse Reference Architecture](../assets/lakehouse-architecture-lr.svg)

## 목차

- [구성 소프트웨어](#구성-소프트웨어)
- [Layer 설명](#layer-설명)
  - [1. Data Source Layer](#1-data-source-layer)
  - [2. Ingestion Layer — Cloudera CFM](#2-ingestion-layer--cloudera-cfm)
  - [3. Streaming Bus Layer — Cloudera CDP](#3-streaming-bus-layer--cloudera-cdp)
  - [4. Storage Layer — MinIO + Iceberg](#4-storage-layer--minio--iceberg)
  - [5. Processing & Orchestration Layer — Cloudera CDE](#5-processing--orchestration-layer--cloudera-cde)
  - [6. Data Federation Layer — Starburst Trino](#6-data-federation-layer--starburst-trino)
  - [7. Consumption Layer](#7-consumption-layer)
  - [모델 서빙 — 고객 보유 모델](#모델-서빙--고객-보유-모델)
  - [고객 AI Agent](#고객-ai-agent)
- [Layer 간 경로](#layer-간-경로)
  - [조회 경로 선택 기준](#조회-경로-선택-기준)
- [검토 시 확인할 사항](#검토-시-확인할-사항)
- [다이어그램 재생성](#다이어그램-재생성)
- [용어집](#용어집)
  - [금융 업무·원천](#금융-업무원천)
  - [데이터 수집·연동](#데이터-수집연동)
  - [저장·테이블 포맷](#저장테이블-포맷)
  - [처리·조회](#처리조회)
  - [AI·검색](#ai검색)

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
| 모델 서빙 | Cloudera AI Inference Service (OpenAI 호환 엔드포인트) + 고객 보유 모델 |
| AI Agent | 고객 AI Agent (Starburst MCP 도구 · 권한 위임 · 감사) |

각 솔루션이 이 아키텍처 안에서 담당하는 범위와 역할 경계는 [solutions.md](solutions.md)에
따로 정리했습니다.

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

### 모델 서빙 — 고객 보유 모델

Starburst의 AI 기능과 AI Agent가 공통으로 사용하는 추론 엔드포인트입니다.

- **Cloudera AI Inference Service** — 사내 추론 엔드포인트, OpenAI 호환 API
- **고객 보유 모델** — 생성 모델(NL-to-SQL·답변), 임베딩 모델(한국어), 리랭커

Starburst는 모델 통합 방식으로 OpenAI API 호환 엔드포인트를 지원하며, 문서상 해당 모델이
온프레미스에 배포된 경우도 명시적으로 허용합니다. 따라서 **폐쇄망에서 외부 모델 API를
호출하지 않고 고객이 보유한 모델을 그대로 사용할 수 있습니다.**

### 고객 AI Agent

사람이 아닌 Agent가 데이터를 소비하는 접점입니다. Layer 7의 Spotfire·Notebook이 사람용
접점이라면, 이 상자는 기계용 접점입니다.

- **Agent 런타임** — 대화 세션, 도구 호출 계획, 사용자 권한 위임(impersonation)
- **도구 (MCP)** — Starburst MCP Server, 문서 검색(RAG), Knowledge Graph 조회
- **감사** — 질문 → 근거 → SQL → 답변의 전 과정 기록

Agent가 자체 계정으로 조회하면 권한 통제가 무력화되므로, **질문한 사용자의 권한으로
조회가 수행되어야 합니다.** 상세한 요건과 미결 사항은
[agent-readiness-analysis.md](agent-readiness-analysis.md)를 참고하십시오.

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
| 6 → 모델 서빙 | 청록 실선 | Model Provider 호출 | Starburst AI 기능이 사내 추론 엔드포인트를 호출. OpenAI 호환 규격이므로 폐쇄망에서 고객 보유 모델을 그대로 사용 |
| Agent ↔ 6 | 자주 실선 (양방향) | MCP 도구 호출 | Agent가 메타데이터를 조회하고 SQL을 실행. Federation 덕분에 원천 메타데이터가 한 지점에 모임 |
| Agent → 모델 서빙 | 청록 실선 | 추론 호출 | 답변 생성과 임베딩에 Starburst와 같은 내부 엔드포인트를 사용 |

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
python scripts/generate_architecture_svg.py
```

SVG와 PNG(4360 x 2300)가 함께 생성됩니다. PNG 래스터화에는 시스템에 설치된 렌더러
(rsvg-convert · Inkscape · Chromium · CairoSVG · ImageMagick 중 하나)를 사용하며,
자세한 옵션은 [README](../README.md#png-렌더러)를 참고하십시오.

레이아웃과 문구는 `scripts/generate_architecture_svg.py` 상단의 `BOXES`, `EDGES`,
`PALETTE` 상수에 선언되어 있습니다. `assets/` 의 SVG와 PNG는 빌드 산출물이므로, 수정이
필요하면 직접 편집하지 말고 스크립트를 고친 뒤 재생성하시기 바랍니다.

---

## 용어집

이 문서에 등장하는 용어입니다.

### 금융 업무·원천

| 용어 | 설명 |
|---|---|
| 계정계 | 예금·여신 등 금융 거래를 실시간 처리하는 원장 시스템. 정합성과 가용성 요구가 가장 높습니다 |
| 정보계 | 계정계 데이터를 분석 목적으로 재구성해 보관하는 시스템. 계정계에 부하를 주지 않고 조회하기 위한 계층입니다 |
| 대기계 | 계정계 장애에 대비한 대기 시스템. 평상시 유휴 자원이므로 CDC나 페더레이션의 대상으로 활용하기 좋습니다 |
| 대외계 | 금융결제원, 신용정보원 등 외부 기관과 규격화된 전문을 주고받는 시스템 |
| 여·수신 원장 | 대출(여신)과 예금(수신)의 거래 기록 원본 |
| VAN | Value Added Network. 카드 결제 승인 중계 사업자 |
| PG | Payment Gateway. 온라인 결제 대행 사업자 |
| 전문 | 금융 시스템 간 주고받는 고정 규격의 메시지 |
| STT | Speech-to-Text. 콜센터 통화 음성을 텍스트로 변환한 결과 |
| FDS | Fraud Detection System. 이상 거래 탐지 시스템 |
| AML | Anti-Money Laundering. 자금세탁방지 |
| STR | Suspicious Transaction Report. 의심거래보고 |
| KRX | 한국거래소. 시세 데이터의 원천 |
| 로그마이너 | Oracle의 리두 로그 분석 기능. CDC 구현에 쓰이나 운영 DB에 직접 적용하면 성능·감사 이슈가 발생합니다 |

### 데이터 수집·연동

| 용어 | 설명 |
|---|---|
| CDC | Change Data Capture. 원본 DB의 변경분만 추출해 전달하는 방식. 전체 재적재 없이 최신 상태를 유지합니다 |
| JDBC | Java Database Connectivity. Java 기반 DB 접속 표준 API |
| ODBC | Open Database Connectivity. 언어 중립적 DB 접속 표준 |
| MQ | Message Queue. 시스템 간 비동기 메시지 전달 미들웨어 |
| SFTP | SSH File Transfer Protocol. 암호화된 파일 전송 |
| REST | HTTP 기반의 API 설계 방식 |
| Back-pressure | 하류가 처리하지 못할 때 상류의 유입을 억제하는 흐름 제어. 큐 폭주와 데이터 유실을 방지합니다 |
| Guaranteed Delivery | 장애가 발생해도 데이터가 유실되지 않도록 보장하는 전달 방식 |
| Data Provenance | 데이터의 출처와 변형 이력을 건 단위로 기록하는 기능. 감독당국 소명과 내부 감사의 근거가 됩니다 |
| Site-to-Site | NiFi 인스턴스 간 데이터를 전송하는 전용 프로토콜 |
| 프로세서 | NiFi에서 하나의 처리 동작(수집·변환·라우팅 등)을 담당하는 구성 단위 |
| 컨슈머 그룹 | Kafka에서 토픽을 나눠 읽는 소비자 묶음. 그룹이 다르면 같은 메시지를 각각 독립적으로 읽습니다 |
| lag | 컨슈머가 최신 메시지보다 얼마나 뒤처져 있는지를 나타내는 지표 |
| replication factor | Kafka에서 각 파티션의 복제본 수. 3이면 브로커 2대까지 장애를 견딥니다 |
| partition | 토픽을 병렬 처리 단위로 나눈 것 |

### 저장·테이블 포맷

| 용어 | 설명 |
|---|---|
| medallion | 데이터를 Bronze → Silver → Gold 단계로 정제해 나가는 레이어링 패턴 |
| Bronze | 원천 데이터를 가공 없이 그대로 적재하는 계층 |
| Silver | 정제·중복제거·표준화를 마친 계층 |
| Gold | 집계·마트·피처 등 소비 목적에 맞춰 가공한 계층 |
| SCD | Slowly Changing Dimension. 시간에 따라 변하는 속성의 이력을 관리하는 기법 |
| Iceberg Table | 오브젝트 스토리지 위에서 트랜잭션과 스키마 변경을 지원하는 테이블 포맷 |
| Iceberg REST Catalog | Iceberg 테이블의 메타데이터를 REST 규격으로 제공하는 카탈로그. 엔진 교체·추가가 용이합니다 |
| Hive Metastore | 하둡 생태계의 전통적 메타데이터 저장소. Thrift 의존성 때문에 이 아키텍처에서는 제거했습니다 |
| Thrift | 언어 간 RPC 프레임워크. Hive Metastore의 통신 규약 |
| snapshot | 특정 시점의 테이블 상태 기록. 시점 조회와 감사 재현의 근거가 됩니다 |
| time-travel | 과거 스냅샷 시점의 데이터를 조회하는 기능 |
| schema evolution | 기존 데이터를 다시 쓰지 않고 컬럼을 추가·변경하는 기능 |
| MERGE | 대상 테이블에 신규는 삽입하고 기존은 갱신하는 SQL 연산 |
| Compaction | 작은 파일을 병합해 조회 성능을 회복시키는 유지관리 작업 |
| Snapshot Expiration | 오래된 스냅샷을 정리해 저장 공간을 회수하는 작업 |
| `s3a://` | Hadoop 계열 엔진이 S3 호환 저장소에 접근할 때 쓰는 경로 스킴 |
| path-style-access | `호스트/버킷/키` 형식으로 S3에 접근하는 방식. 폐쇄망 DNS에서 가상 호스트 스타일 URL이 해석되지 않는 경우가 많아 필요합니다 |

### 처리·조회

| 용어 | 설명 |
|---|---|
| DAG | Directed Acyclic Graph. 작업 간 의존 관계를 순환 없이 표현한 그래프. Airflow의 파이프라인 정의 단위 |
| SLA | Service Level Agreement. 작업이 완료돼야 하는 기한 기준 |
| Structured Streaming | Spark의 스트리밍 처리 방식. 마이크로배치 단위로 연속 데이터를 처리합니다 |
| 마이크로배치 | 스트림을 짧은 시간 단위로 잘라 배치처럼 처리하는 방식. 이 주기가 실시간 적재 지연의 하한을 결정합니다 |
| Coordinator | Trino에서 질의를 파싱·계획하고 워커에 분배하는 노드 |
| Worker | Trino에서 실제 데이터를 읽고 연산하는 노드 |
| Connector | Trino가 개별 데이터 소스에 접속하기 위한 플러그인 |
| 페더레이션 | 데이터를 한곳에 모으지 않고, 여러 원천을 질의 시점에 통합 조회하는 방식 |
| 리소스 그룹 | Trino에서 동시 실행 질의 수와 자원 사용량을 제한하는 통제 단위 |
| 마스킹 | 민감 정보를 가리거나 대체해 조회 결과에 노출되지 않게 하는 기법 |
| 행·열 수준 통제 | 사용자 권한에 따라 조회 가능한 행과 열을 제한하는 접근 제어 |
| In-DB 모드 | 데이터를 BI 도구로 가져오지 않고 원천 DB에서 연산해 결과만 받는 방식 |

### AI·검색

| 용어 | 설명 |
|---|---|
| RAG | Retrieval-Augmented Generation. 질문과 관련된 문서를 검색해 근거로 제공한 뒤 답변을 생성하는 방식 |
| 임베딩 | 텍스트를 의미가 반영된 숫자 벡터로 변환한 것. 유사도 검색의 기준이 됩니다 |
| 청킹 | 긴 문서를 검색·임베딩에 적합한 크기로 나누는 작업 |
| 파싱 | PDF·이미지 등에서 텍스트를 추출하는 단계. 파이프라인에서 비용이 가장 큰 구간입니다 |
| NL-to-SQL | 자연어 질문을 SQL로 변환하는 기능 |
| MCP | Model Context Protocol. AI 에이전트가 외부 도구·데이터에 접근하기 위한 개방형 규약 |
| Vector Store | 임베딩 벡터를 저장하고 유사도 검색을 제공하는 저장소 |
| PGVector | PostgreSQL에서 벡터 검색을 제공하는 확장 |
| HNSW | Hierarchical Navigable Small World. 근사 최근접 이웃 검색에 널리 쓰이는 인덱스 구조 |
| BM25 | 단어 빈도 기반의 전통적 문서 검색 랭킹 알고리즘 |
| Nori | Elasticsearch의 한국어 형태소 분석기 |
| RRF | Reciprocal Rank Fusion. 서로 다른 검색 결과의 순위를 결합하는 하이브리드 검색 기법 |
