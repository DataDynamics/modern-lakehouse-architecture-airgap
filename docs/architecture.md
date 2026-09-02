# Modern Lakehouse Architecture (Air-gapped)

폐쇄망 환경의 금융권 Lakehouse 참조 아키텍처입니다. 좌에서 우로 데이터가 흐르며,
7개 Layer와 이를 뒷받침하는 Argus Catalog · Argus RAG Studio · Vector DB · 모델 서빙 ·
고객 AI Agent 구성요소, 그리고 이들을 잇는 22개의 경로로 구성됩니다.

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
  - [Data Catalog — Argus Catalog](#data-catalog--argus-catalog)
  - [RAG — Argus RAG Studio](#rag--argus-rag-studio)
  - [Vector DB — 임베딩 인덱스 저장소](#vector-db--임베딩-인덱스-저장소)
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
| Data Catalog | Argus Catalog (메타데이터 · 리니지 · 품질 · 모델 레지스트리) |
| RAG | Argus RAG Studio (파이프라인 + 검색 API) |
| Vector DB | PostgreSQL + pgvector (기본) — Qdrant · Weaviate · Milvus 교체 가능 |
| 모델 서빙 | Cloudera AI Inference Service (OpenAI 호환 엔드포인트) + 고객 보유 모델 |
| AI Agent | 고객 AI Agent (Starburst MCP 도구 · 권한 위임 · 감사) |

각 솔루션이 이 아키텍처 안에서 담당하는 범위와 역할 경계는 [solutions.md](solutions.md)에,
각 제품을 선택한 근거는 [architecture-rationale.md](architecture-rationale.md)에 따로
정리했습니다.

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
s3a://lake/docs/      문서 · 이미지 원본 (RAG 입력)
```

Table Format은 Iceberg Table, Catalog는 Iceberg REST Catalog 단일 구성입니다. Hive
Metastore를 제거해 Thrift 의존성을 없앴고, REST 스펙만 맞추면 엔진을 추가·교체할 수 있습니다.
스냅샷과 time-travel은 금융권의 시점 조회와 감사 재현에 직접 활용됩니다.

`docs/` 존은 Argus RAG Studio의 **스토리지 소스**로 등록되는 드롭존입니다. Argus는
소스를 읽기 전용으로 다루므로, 폴더 구조가 곧 라우팅 규칙이 되도록 지식베이스별로
prefix를 나누는 편이 유리합니다.

```
docs/raw/           원본 PDF·HWP·이미지 (불변, 보존기한 관리) — 소스 워치 스캔 대상
docs/raw/terms/     ├ 약관·규정      → 지식베이스 "terms"   (경로 규칙으로 자동 배정)
docs/raw/products/  └ 상품설명서     → 지식베이스 "products"
docs/export/        선택 — 청크·벡터를 Iceberg로 내보내 Trino에서 대량 분석할 때
```

파싱 결과·청크·벡터는 Argus가 PostgreSQL(+ pgvector)에 보관하므로 `docs/` 아래에
파생물 폴더를 따로 두지 않습니다. 임베딩 모델을 교체할 때는 Argus의 재인덱싱이 청크
단위로 다시 임베딩하므로 파싱을 반복하지 않습니다.

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

위 표는 Starburst가 커넥터로 붙을 수 있는 저장소 기준입니다. 이 아키텍처의 Vector DB는
Argus RAG Studio의 기본값인 PostgreSQL + pgvector이며, Trino는 PostgreSQL 커넥터로
같은 테이블을 읽습니다.

### 7. Consumption Layer

- **Spotfire** — 대시보드, Ad-hoc 분석. In-DB 모드로 Trino 직접 질의
- **Cloudera AI** — AI Workbench(모델 학습·서빙), AI Studio, Agent
- **SQL Client / Notebook / API**

성격이 다른 두 소비 패턴이 공존합니다. 집계 결과 조회는 Trino를, 대용량 학습 데이터는
스토리지 직접 접근을 사용합니다.

### Data Catalog — Argus Catalog

여러 Layer에 흩어진 자산의 메타데이터를 한곳에 모으는 구성요소입니다. 데이터 흐름에는
끼어들지 않고 각 시스템에서 메타데이터와 리니지만 수집하므로, 다이어그램에서 다른
상자와 점선으로만 연결됩니다.

[Argus Catalog](https://github.com/DataDynamics-OSS/argus-catalog)는 DataHub 스타일
데이터 카탈로그와 Unity Catalog OSS 호환 ML 모델 레지스트리를 하나로 묶은 Data
Dynamics의 오픈소스(Apache-2.0) 메타데이터 플랫폼입니다. FastAPI 백엔드(:4600)와
Next.js UI, PostgreSQL + pgvector로 구성되며, 폐쇄망을 전제로 설계되었습니다.

- **데이터 카탈로그** — 데이터셋·스키마·태그·소유자(Technical / Business / Data Steward),
  컬럼 수준 리니지와 DDL 기반 ERD, 데이터 표준·용어집(형태소 분석 기반 자동 생성, 준수율)
- **메타데이터 수집** — Trino · Hive · Impala · Kafka · S3 · HDFS · Oracle · PostgreSQL ·
  Elasticsearch 등 11종 플랫폼. **Metadata Sync** 서비스(:4610, 상시 또는 배치)가 스키마 ·
  키 · DDL · 행 수를 동기화하고 변경분을 스냅샷으로 남김
- **리니지 수집** — **Trino Query Listener**(EventListener SPI)가 실행된 질의의 입출력
  테이블·컬럼을 그대로 보고. Hive Query Hook · Impala Query Agent, 그리고 NiFi Flow ·
  Airflow DAG 파이프라인 자동 등록
- **데이터 품질** — 소스 직접 프로파일링, 규칙 10종 검증, GOOD / WARN / BAD 점수와
  리니지 업스트림 전파 경고
- **거버넌스** — OpenAPI 스펙 **API 카탈로그**, **AI Agent 카탈로그**(에이전트 등록 · 도구/MCP
  서버 · 리니지 · 평가 · 호출 미터링 · 정책 번들), Temporal 기반 변경 관리
- **ML 모델 레지스트리** — MLflow · OCI 호환, Stage 관리, 모델 카드, `argus-model` CLI로
  외부 모델을 에어갭으로 반입
- **검색 · AI** — pgvector 하이브리드 검색, LLM 기반 메타데이터 자동 생성(설명 · 태그 ·
  PII 감지), tool-use AI 어시스턴트

이 아키텍처에서 자리를 잡는 방식은 다음과 같습니다.

| Argus Catalog 기능 | 이 아키텍처에서의 대응 |
|---|---|
| Trino 플랫폼 동기화 + Query Listener | 6번 Layer. Trino가 페더레이션하는 원천(Oracle · Hive · Kafka · Iceberg)의 메타데이터를 한 번에 수집하고, 실행 질의에서 리니지를 얻음 |
| NiFi Flow 등록 | 2번 Layer의 CFM. 수집 흐름을 파이프라인 자산으로 등록 |
| Airflow DAG 등록 | 5번 Layer의 CDE. Bronze → Silver → Gold 변환의 리니지 |
| S3 · Kafka 플랫폼 동기화 | 4번 · 3번 Layer. 필요 시 Trino를 거치지 않고 직접 동기화 |
| AI Agent 카탈로그 | 고객 AI Agent를 등록하고 도구/MCP · 호출 지표를 거버넌스 |
| External API (URN 기반 메타데이터 · Avro 스키마) | Agent가 질의 계획 전에 스키마 · 리니지 · 용어집을 조회 |
| ML 모델 레지스트리 + 에어갭 반입 | 모델 서빙 상자의 고객 보유 모델을 반입 · 버전 관리 |
| LLM 프로바이더 (OpenAI 호환) | 모델 서빙 상자의 Cloudera AI Inference |

다이어그램에서는 NiFi → Catalog, Trino → Catalog, Catalog ↔ Agent 세 경로만 그렸습니다.
S3 · Kafka · Airflow 동기화는 Trino 경유 수집과 겹치므로 선을 생략했습니다.

> **설계 주의** Query Listener는 Trino Coordinator 플러그인이므로 Starburst 업그레이드
> 시 SPI 호환성을 함께 검증해야 합니다. 리니지가 끊기면 품질 전파 경고와 영향 분석이
> 침묵하므로, 수집 지연을 알림 규칙으로 감시하십시오.

### RAG — Argus RAG Studio

Storage Layer의 `docs/` 존에 쌓인 비정형 문서를 Agent가 근거로 쓸 수 있는 형태로
바꾸고, 그 결과를 API로 내어주는 구성요소입니다. 정형 데이터의 Bronze→Silver→Gold와
같은 자리에 있는, 비정형 데이터의 medallion 경로라고 보면 됩니다.

[Argus RAG Studio](https://github.com/DataDynamics-OSS/argus-rag-studio)는 RAG
파이프라인의 **구축 · 검색/생성 · 평가 · 운영 · 배포**를 한 플랫폼에서 다루는 Data
Dynamics의 오픈소스(Apache-2.0)입니다. FastAPI 백엔드(:4700)와 Next.js UI, 호스트별
Agent(:4501)를 통한 원격 배포로 구성되며, 임베딩·리랭커·OCR 같은 추론 서버는
`extensions/`로 분리 배포합니다.

- **문서 반입 (Build)** — S3 호환 · NAS를 **스토리지 소스**로 등록(읽기 전용)하고,
  **소스 워치**가 지정 prefix를 주기 스캔해 새 문서를 자동 반입. 경로·메타 규칙과
  내용 임베딩 유사도로 지식베이스(컬렉션)를 자동 배정하는 **문서 라우팅** 포함
- **인제스천 파이프라인** — 파싱 전략 `text` · `layout` · `docai` · `vlm` · `rhwp`(HWP/HWPX),
  청킹 8종, 컬렉션별 임베딩 모델·차원·거리 메트릭 → pgvector `vector` + `tsvector` 색인
- **검색 · 생성 · 평가** — 하이브리드 검색(벡터 + 렉시컬 + RRF) → 리랭킹(none / llm /
  cross_encoder) → 인용 답변 · 멀티턴 챗(SSE) · 페더레이션 검색. 골든셋 기반 Hit Rate ·
  MRR · LLM-as-judge 평가와 👍/👎 피드백 루프, 파이프라인 버전·롤백
- **REST API** — `POST /collections/{id}/search` · `/query` · `/chat`,
  `/search/federated` · `/query/federated`. 인증은 로컬 JWT · Keycloak OIDC · **API 키
  (서비스 계정)** — Agent 같은 기계 호출자는 API 키를 사용

이 아키텍처에서 자리를 잡는 방식은 다음과 같습니다.

| Argus 구성요소 | 이 아키텍처에서의 대응 |
|---|---|
| 스토리지 소스 (S3 호환) | MinIO `s3a://lake/docs/` — 4 → RAG 경로 |
| 오브젝트 스토리지 (원본·이미지 보관) | 같은 MinIO. 별도 버킷을 두지 않고 `docs/` 존을 공유 |
| PostgreSQL + pgvector | Vector DB 상자. REST Catalog의 메타 저장소와 같은 PostgreSQL 클러스터를 쓸 수도, 분리할 수도 있음 |
| 임베딩 · 리랭커 · 생성 LLM 프로바이더 (OpenAI 호환) | 모델 서빙 상자의 Cloudera AI Inference. Argus의 자체 `embedding_server` · `reranker_server`를 쓸 수도 있음 |
| 문서 수집 파이프라인을 NiFi로 운영 | 2번 Layer의 Cloudera CFM. Argus는 NiFi를 느슨히 결합된 외부 런타임으로 취급 |
| 모델 레지스트리 + 에어갭 모델 반입 | 폐쇄망 요건과 정합. 모델 팩을 Model Repository 버킷에 반입해 오프라인 서빙 |

원본을 읽는 경로는 Trino가 아니라 **S3 API**입니다. Argus의 스토리지 소스가 S3 호환
프로토콜로 직접 붙고, 문서 원본은 SQL 조회 대상이 아니기 때문입니다.

> **설계 주의** 청크에 붙은 메타데이터가 검색 시점에 필터로 검증되지 않으면, 문서
> 원본에 걸어 둔 접근 통제가 벡터 검색으로 우회됩니다. Argus의 컬렉션 단위 권한과
> Agent 측 사용자 권한 위임을 한 쌍으로 설계해야 합니다.

### Vector DB — 임베딩 인덱스 저장소

Argus RAG Studio 파이프라인의 산출물을 담고 유사도 검색을 제공하는 저장소입니다.

- **저장 대상** — 청크, 벡터(기본 1024d), 렉시컬 검색용 `tsvector`, 메타데이터, 출처
  경로, 질의 트레이스
- **백엔드** — 기본은 **PostgreSQL + pgvector**. Argus의 `VectorStore` 추상화로 Qdrant ·
  Weaviate · Milvus · Databricks Vector Search로 교체 가능하며, 전환 시 pgvector에서
  hydrate합니다. 거리 메트릭은 cosine / l2 / inner_product
- **검색** — 벡터 검색과 `tsvector` 렉시컬 검색을 RRF로 융합한 뒤 리랭커(cross-encoder
  또는 LLM)로 재정렬

호출 주체는 셋입니다. **Argus RAG Studio**가 색인을 쓰고 API 처리 시 검색하며,
**AI Agent**는 문서 검색 도구로 직접 조회할 수 있고, **Starburst Trino**는 PostgreSQL
커넥터로 벡터 테이블을 SQL 네임스페이스에 편입해 정형 데이터와 함께 조회합니다.

Agent 입장에서 문서 근거를 얻는 길은 두 갈래입니다.

| 경로 | 적합한 경우 | 유의점 |
|---|---|---|
| Vector DB 직접 조회 | 청크 벡터를 그대로 받아 Agent가 리랭킹·조합을 직접 제어해야 할 때 | 질의 임베딩을 Agent가 직접 만들어야 하고, 권한 필터를 빠뜨리면 통제가 우회됨 |
| Argus REST API 호출 | 하이브리드 검색·리랭킹·인용·트레이스를 Studio 정책에 맡길 때. 평가·피드백 루프에 자동 편입 | 응답 형식과 인용 규칙이 Studio에 종속. API 키 발급·회전 필요 |

수치와 문서를 한 질의에서 묶어야 하면 어느 쪽도 아닌 Trino 경유입니다.

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
| 4 → RAG | 파랑 실선 | 소스 워치 스캔 | `s3a://lake/docs/` 를 Argus 스토리지 소스로 등록하고 소스 워치가 주기 스캔. 문서 원본은 SQL 대상이 아님 |
| RAG ↔ Vector DB | 양방향 실선 | 색인 · 검색 | 인제스천 워커가 청크·벡터·tsvector를 적재하고, API 처리 시 하이브리드 검색 |
| Vector DB → Agent | 자주 실선 | Vector DB 직접 조회 | Agent의 문서 검색 도구가 Top-K 근거 청크를 직접 조회 |
| Agent ↔ RAG | 자주 실선 (양방향) | Argus REST API 호출 | `search` · `query` · `chat` 호출(API 키). 하이브리드 검색·리랭킹·인용·트레이스를 Studio가 처리 |
| Vector DB ↔ 6 | 양방향 실선 | 벡터 테이블 조회 | Trino의 PostgreSQL 커넥터로 pgvector 테이블과 정형 데이터를 한 질의에서 결합 |
| 2 → Catalog | 올리브 점선 | NiFi Flow 리니지 | CFM 수집 흐름을 파이프라인 자산으로 등록. 원천 → Bronze 구간의 리니지 |
| 6 → Catalog | 올리브 점선 | Trino Query Listener · Metadata Sync | 페더레이션된 모든 원천의 메타데이터를 한 번에 동기화하고, 실행 질의에서 컬럼 수준 리니지를 수집 |
| Agent ↔ Catalog | 올리브 점선 (양방향) | Agent 등록 · 미터링 · 메타데이터 API | Agent는 URN 기반 External API로 스키마·리니지·용어집을 조회하고, 자신을 AI Agent 카탈로그에 등록해 호출 지표를 보고 |

### 조회 경로 선택 기준

```
행 수가 많고 SQL 연산이 적다   →  4 → 7  (S3 직접 접근)
행 수가 적고 SQL 연산이 무겁다  →  6 → 7  (Trino 경유)
원천의 최신 상태가 필요하다     →  1 → 6  (페더레이션)
문서 근거가 필요하다            →  Vector DB → Agent (직접 조회) 또는 Agent ↔ RAG (Argus REST API)
문서와 수치를 함께 묶는다       →  Vector DB → 6 → 7 (Trino 경유)
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

**4. RAG 인덱스의 권한 통제**
Vector DB에는 원본 문서의 텍스트 조각이 그대로 들어갑니다. 원본에 걸린 접근 통제가
인덱스에서 유지되지 않으면 검색으로 우회됩니다. 청크에 권한 태그를 부여하고, 검색
시점에 질문한 사용자의 권한으로 필터링해야 합니다.

**5. 임베딩 모델의 고정**
색인에 쓴 임베딩 모델과 질의에 쓰는 모델이 다르면 검색 품질이 무너집니다. 모델
버전을 인덱스 메타데이터에 기록하고, 교체 시 `docs/parsed/` 부터 전체 재임베딩하는
절차를 준비해야 합니다.

**6. MinIO 연동 설정**
Trino, Spark, NiFi 모두에 `path-style-access=true`를 설정해야 합니다. 가상 호스트 스타일
URL은 폐쇄망 DNS에서 해석되지 않는 경우가 많습니다.

---

## 다이어그램 재생성

```bash
python scripts/generate_architecture_svg.py
```

SVG와 PNG(4360 x 3340)가 함께 생성됩니다. 초보자용 개념도는
`scripts/generate_concept_svg.py` 로 따로 만듭니다(`assets/lakehouse-concept.svg`). PNG 래스터화에는 시스템에 설치된 렌더러
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
| Argus RAG Studio | RAG 파이프라인의 구축·검색/생성·평가·운영·배포를 한 곳에서 다루는 Data Dynamics의 오픈소스 플랫폼. 검색(`search`)·답변(`query`)·챗(`chat`) REST API 제공 |
| 소스 워치 | Argus RAG Studio가 등록된 스토리지 소스의 폴더를 주기 스캔해 새 문서를 자동 반입하는 기능 |
| 하이브리드 검색 | 벡터 유사도 검색과 렉시컬(키워드) 검색을 함께 수행하고 결과를 융합하는 방식 |
| RRF | Reciprocal Rank Fusion. 서로 다른 검색 결과의 순위를 합쳐 하나의 순위로 만드는 융합 기법 |
| Argus Catalog | DataHub 스타일 데이터 카탈로그와 Unity Catalog 호환 ML 모델 레지스트리를 하나로 묶은 Data Dynamics의 오픈소스 메타데이터 플랫폼 |
| Query Listener | Trino의 EventListener SPI로 실행 질의의 입출력 테이블·컬럼을 받아 리니지를 만드는 Argus Catalog 확장 |
| Metadata Sync | 여러 플랫폼의 스키마·키·DDL을 주기적으로 수집해 Argus Catalog에 동기화하는 서비스(:4610) |
| URN | Uniform Resource Name. Argus Catalog가 데이터셋·API·모델 같은 자산을 식별하는 고유 이름 |
| 청킹 (chunking) | 긴 문서를 검색 단위로 잘라내는 것. 조각마다 출처와 메타데이터를 붙입니다 |
| 임베딩 (embedding) | 텍스트를 의미를 담은 숫자 벡터로 변환하는 것. 유사도 검색의 기준값이 됩니다 |
| Vector DB | 임베딩 벡터와 메타데이터를 저장하고 유사도 검색을 제공하는 저장소 |
| Top-K 검색 | 질의 벡터와 가장 가까운 K개의 청크를 찾아 반환하는 검색 |
| upsert | 없으면 삽입하고 있으면 갱신하는 쓰기. 증분 색인에서 사용합니다 |
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
