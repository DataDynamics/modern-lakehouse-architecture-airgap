# 솔루션별 기능표

여덟 제품의 핵심 기능을 **제품마다 표 하나, 10행 내외**로 압축한 문서입니다. 도입 검토
회의에서 제품 단위로 한 장씩 보는 용도이며, 전체 기능 목록과 출처는
[solution-features.md](solution-features.md), 이 아키텍처에서 담당하는 범위는
[solutions.md](solutions.md), 동작 환경은 [solution-runtimes.md](solution-runtimes.md) 에
있습니다. Argus 두 제품은 공개 저장소의 README · 문서 · 코드로 확인했습니다.

| 표기 | 의미 |
|---|---|
| ● | [참조 아키텍처](../assets/lakehouse-architecture-lr.svg) 다이어그램에 명시된 기능 |
| ○ | 다이어그램에는 없으나 운영상 전제가 되는 기능 |
| － | 이번 아키텍처 범위 밖 |

## 목차

- [한눈에 보기](#한눈에-보기)
- [Cloudera CFM](#cloudera-cfm)
- [Cloudera CDE](#cloudera-cde)
- [Cloudera CDP (Streams Messaging)](#cloudera-cdp-streams-messaging)
- [Cloudera AI](#cloudera-ai)
- [Starburst Enterprise](#starburst-enterprise)
- [MinIO AIStor](#minio-aistor)
- [Argus RAG Studio](#argus-rag-studio)
- [Argus Catalog](#argus-catalog)

---

## 한눈에 보기

| 제품 | 아키텍처 위치 | 핵심 역할 | 결정적인 기능 |
|---|---|---|---|
| Cloudera CFM | 2. Ingestion | 원천 수집 · 변환 · 라우팅 | Guaranteed Delivery, Data Provenance |
| Cloudera CDE | 5. Processing & Orchestration | Spark 변환 · Airflow 오케스트레이션 | Spark on K8s, Iceberg MERGE, 내장 Airflow |
| Cloudera CDP | 3. Streaming Bus | Kafka 이벤트 스트리밍 · 관제 | Consumer lag 관제 |
| Cloudera AI | 7. Consumption · 모델 서빙 | 모델 학습 · 서빙 · 에이전트 | Inference Service (OpenAI 호환) |
| Starburst Enterprise | 6. Data Federation | 단일 SQL 조회 접점 · AI 기능 | Ranger 행·열 필터링, Resource groups, MCP |
| MinIO AIStor | 4. Storage | S3 호환 오브젝트 저장소 | S3 API, IAM, WORM |
| Argus RAG Studio | RAG | 문서 인제스천 · 검색/생성 · 평가 | 소스 워치, 하이브리드 검색, REST API |
| Argus Catalog | Data Catalog | 메타데이터 · 리니지 · 거버넌스 | Query Listener 리니지, AI Agent 카탈로그 |

---

## Cloudera CFM

Apache NiFi 기반 Flow Management.

| 기능 | 설명 | 범위 |
|---|---|---|
| Guaranteed Delivery | write-ahead log · content repository 기반 전달 보증 | ● |
| Back Pressure · Pressure Release | 큐 적체 시 상류 억제, 임계 초과분 해제 | ● |
| Prioritized Queuing | 큐 내 처리 순서 지정 | ● |
| Visual Command and Control | 동작 중인 흐름을 GUI 에서 변경·중단·재구성 | ● |
| Data Provenance | 출처·변형·전달 이력을 건 단위로 기록 | ● |
| Site-to-Site | NiFi 인스턴스 간 전용 전송 프로토콜 | ● |
| 사전 제공 프로세서 | 커넥티비티·변환·라우팅 프로세서 다수 기본 제공 | ● |
| 보안 | 2-way SSL, 사용자 인증, 흐름 단위 권한 분리 | ○ |
| Clustering | 노드 추가로 수평 확장 | ○ |
| NiFi Registry · Cloudera Manager | 흐름 버전 관리 · 환경 간 승격, 설치·모니터링 일원화 | ○ |

---

## Cloudera CDE

Spark on Kubernetes 와 내장 Airflow 를 제공하는 Data Engineering 서비스.

| 기능 | 설명 | 범위 |
|---|---|---|
| Virtual Cluster | CPU·메모리 범위가 정의된 오토스케일링 클러스터, ACL 로 팀 격리 | ● |
| Jobs · Job run · Resource | 코드 + 설정 + 의존성 파일을 작업 단위로 정의·실행 | ● |
| Spark on Kubernetes | 클러스터 유지 없이 Spark 작업 실행 | ● |
| 오토스케일링 | Job 단위(dynamic allocation) · 클러스터 단위(YuniKorn) | ○ |
| Iceberg 런타임 기본 포함 | Spark classpath 에 Iceberg 의존성 탑재 | ● |
| Iceberg row-level 연산 | copy-on-write MERGE / UPDATE / DELETE | ● |
| Iceberg Compaction | 작은 파일 압축 | ● |
| 내장 Airflow | Virtual Cluster 생성 시 자동 배포, Airflow 타입 Job | ● |
| Operator · 커스텀 DAG | CDE/CDW/Bash/Python Operator, 직접 작성한 DAG 배포 | ● |
| Web UI · CLI · REST API | 작업 생성·실행·모니터링 인터페이스 | ● |

---

## Cloudera CDP (Streams Messaging)

CDP Runtime 의 Kafka 계열 구성요소.

| 기능 | 설명 | 범위 |
|---|---|---|
| Apache Kafka | 이벤트 스트리밍 백본 | ● |
| Streams Messaging Manager | Kafka 및 연관 서비스 모니터링·관리 | ● |
| ZooKeeper | 브로커 등록 · 리더 선출 | ● |
| End-to-end visibility | 프로듀서 → 토픽 → 컨슈머 전 구간 가시화 | ● |
| Intelligence-based filtering | 선택한 엔티티와 연관된 것만 표시 | ● |
| Consumer lag 관제 | 컨슈머별 LAG 로 지연 식별 | ● |
| Schema Registry | 스키마 등록 · 버전 관리 | ○ |
| Cruise Control | Kafka 리밸런싱 워크플로 | ○ |
| Ranger 연동 · REST endpoints | 토픽 단위 접근 통제, 외부 시스템 연동 | ○ |
| Streams Replication Manager | 클러스터 간 토픽 복제 | － |

---

## Cloudera AI

AI Workbench · Inference Service · Agent Studio.

| 기능 | 설명 | 범위 |
|---|---|---|
| Sessions | CPU·메모리·GPU 자원으로 데이터 레이크에 직접 연결 | ● |
| Models | HA REST 엔드포인트로 모델 서빙 | ● |
| 격리 워크로드 | Python · R · Spark-on-K8s 컨테이너 격리 실행 | ● |
| Experiments · Jobs · Applications | 실험 추적, 파이프라인, 현업용 화면 | ○ |
| Model Governance | 배포 모델의 데이터 계보 추적 | ○ |
| Inference Service | 예측형·생성형 모델의 프로덕션 서빙 | ● |
| OpenAI 호환 엔드포인트 | Starburst · Argus · AI Agent 가 같은 사내 엔드포인트 호출 | ● |
| Hugging Face 모델 배포 | text generation · embedding · reranking task 선택 | ○ |
| Agent Studio | 로우코드 에이전트 작성, 커스텀 도구 결합 | ● |
| 에이전트 운영 | 라이프사이클 관리, 관측·로깅 | ○ |

---

## Starburst Enterprise

Trino 상용 배포판(SEP).

| 기능 | 설명 | 범위 |
|---|---|---|
| 커넥터 | Iceberg · Kafka · Hive · Oracle 등, pushdown 강화 | ● |
| Ranger 연동 | catalog · schema · table · column · row 수준 필터링 | ● |
| 접근 통제 · 감사 | Built-in access control, Query auditing | ● |
| Resource groups | 동시 질의 수 · 자원 상한. 원천 페더레이션 부하 제한 | ● |
| HA · autoscaling | Coordinator HA, 워커 오토스케일 | ● |
| 웹 UI · Insights | 관리 화면, 클러스터 메트릭 대시보드 | ● |
| Warp Speed · Cached Views | 자동 인덱싱·캐싱 가속 | ○ |
| Fault-tolerant execution | 실패 재시도로 장기 질의 보호 | ○ |
| AI Agent · AIDA · AI functions | NL-to-SQL 에이전트, 분석 보조, embedding/prompt 함수 | ● |
| MCP server · Model provider | 읽기 전용 MCP 도구, OpenAI 호환 온프레미스 모델 연동 | ● |

---

## MinIO AIStor

S3 호환 오브젝트 스토리지.

| 기능 | 설명 | 범위 |
|---|---|---|
| S3 API | 별도 메타데이터 DB 없는 네이티브 S3 호환 | ● |
| Identity and Access Management | LDAP · OIDC · Keycloak 연동, 정책 기반 통제. S3 직접 접근 경로의 유일한 통제 | ● |
| Iceberg Catalog interface | AIStor Tables. 별도 REST Catalog 대체 여부 검토 | ○ |
| Erasure Coding · Healing | 분산 패리티 보호, 자동 복구 | ○ |
| Object Versioning | 오브젝트 버전 관리 | ○ |
| Object Locking (WORM) | 삭제 방지 · 보존기한 관리. `docs/raw/` 적용 | ○ |
| Bucket Replication | active-passive · active-active 복제 | ○ |
| Server-Side Encryption | MinIO KMS / KES 키 관리 | ○ |
| Lifecycle Management | 자동 만료 · 계층화 | ○ |
| Observability · Multi-tenancy | 메트릭 · 감사 로그 · OpenTelemetry, 테넌트 격리 | ○ |

---

## Argus RAG Studio

RAG 파이프라인의 구축 · 검색/생성 · 평가 · 운영 · 배포 플랫폼
([저장소](https://github.com/DataDynamics-OSS/argus-rag-studio), Apache-2.0).

| 기능 | 설명 | 범위 |
|---|---|---|
| 스토리지 소스 · 소스 워치 | S3 호환 · NAS 를 읽기 전용 소스로 등록, 주기 스캔으로 무인 반입 | ● |
| 문서 라우팅 | 경로·메타 규칙 + 내용 임베딩 유사도로 지식베이스 자동 배정 | ○ |
| 멀티포맷 인제스천 | txt · pdf · docx · xlsx · pptx · hwp/hwpx, 파싱 전략 text · layout · docai · vlm · rhwp | ● |
| 청킹 · 임베딩 | 청킹 8종, 컬렉션별 임베딩 모델 · 차원 · 거리 메트릭 | ● |
| 하이브리드 검색 | 벡터 + 렉시컬 + RRF, 리랭킹 none / llm / cross_encoder | ● |
| 생성 | 인용 답변, 멀티턴 챗(SSE), 페더레이션 검색·질의 | ● |
| REST API | `search` · `query` · `chat` · `federated`, JWT · Keycloak OIDC · API 키 | ● |
| VectorStore 교체 | pgvector 기본, Qdrant · Weaviate · Milvus · Databricks 로 전환 | ● |
| 평가 · 피드백 | 골든셋, Hit Rate · MRR, LLM-as-judge, 👍/👎 → 골든셋 승격 | ○ |
| 운영 · 배포 | 파이프라인 버전·롤백, 트레이스, 에이전트 기반 원격 배포, 에어갭 모델 반입 | ○ |

---

## Argus Catalog

데이터 카탈로그 + ML 모델 레지스트리 메타데이터 플랫폼
([저장소](https://github.com/DataDynamics-OSS/argus-catalog), Apache-2.0).

| 기능 | 설명 | 범위 |
|---|---|---|
| 데이터셋 관리 | 등록 · 검색 · 태그 · 소유자(Technical / Business / Steward) | ● |
| 메타데이터 동기화 | Trino · Hive · Kafka · S3 · Oracle 등 11종 플랫폼, Metadata Sync 서비스 | ● |
| 리니지 · ERD | 컬럼 수준 리니지, Trino Query Listener · Hive Hook, NiFi · Airflow 파이프라인 등록 | ● |
| 데이터 표준 · 용어집 | 멀티 표준 사전, 형태소 분석 기반 용어 생성, 준수율 | ○ |
| 시맨틱 검색 | pgvector 키워드 + 시맨틱 하이브리드 | ○ |
| 데이터 품질 | 프로파일링, 규칙 10종, GOOD/WARN/BAD 점수와 리니지 전파 | ○ |
| API 카탈로그 | OpenAPI 스펙 등록, 버전 diff · 린트 | ○ |
| AI Agent 카탈로그 | 에이전트 등록, 도구/MCP, 평가, 호출 미터링 | ● |
| ML 모델 레지스트리 | MLflow · OCI 호환, Stage 관리, 에어갭 모델 반입 SDK | ○ |
| External API | URN 기반 메타데이터 · Avro 스키마 조회. Agent 가 질의 전 참조 | ● |
