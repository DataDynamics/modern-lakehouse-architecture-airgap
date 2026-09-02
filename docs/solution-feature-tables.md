# 솔루션별 기능표

Cloudera CFM · CDE · CDP · Cloudera AI · Starburst Enterprise · MinIO AIStor 여섯 제품의
기능을 **제품마다 표 하나**로 정리한 문서입니다. 도입 검토 회의에서 제품 단위로 한 장씩
펼쳐 보는 용도를 전제로 했습니다.

기능 항목과 설명은 [solution-features.md](solution-features.md) 에서 공식 문서로 확인한
내용을 그대로 옮기고 영역별로 한 표에 합친 것입니다. 출처 링크, 확인 시점의 주의 사항,
검토 항목은 그 문서를 참고하십시오. 각 제품이 이 아키텍처에서 담당하는 범위는
[solutions.md](solutions.md), 동작 환경은 [solution-runtimes.md](solution-runtimes.md) 에
있습니다.

**범위 표기**

| 표기 | 의미 |
|---|---|
| ● | [참조 아키텍처](../assets/lakehouse-architecture-lr.svg) 다이어그램에 명시된 기능 |
| ○ | 다이어그램에는 없으나 운영상 전제가 되는 기능 |
| － | 이번 아키텍처 범위 밖 (제품은 제공하나 사용하지 않음) |

## 목차

- [한눈에 보기](#한눈에-보기)
- [Cloudera CFM](#cloudera-cfm)
- [Cloudera CDE](#cloudera-cde)
- [Cloudera CDP (Streams Messaging)](#cloudera-cdp-streams-messaging)
- [Cloudera AI](#cloudera-ai)
- [Starburst Enterprise](#starburst-enterprise)
- [MinIO AIStor](#minio-aistor)

---

## 한눈에 보기

| 제품 | 아키텍처 위치 | 핵심 역할 | 이 아키텍처에서 결정적인 기능 |
|---|---|---|---|
| Cloudera CFM | 2. Ingestion | 원천 수집 · 변환 · 라우팅 | Guaranteed Delivery, Data Provenance, Back Pressure |
| Cloudera CDE | 5. Processing & Orchestration | Spark 변환 · Airflow 오케스트레이션 | Spark on Kubernetes, Iceberg row-level 연산, 내장 Airflow |
| Cloudera CDP | 3. Streaming Bus | Kafka 이벤트 스트리밍 · 관제 | Consumer lag 관제, Intelligence-based filtering |
| Cloudera AI | 7. Consumption · 모델 서빙 | 모델 학습 · 서빙 · 에이전트 | Inference Service (OpenAI 호환), Sessions 의 S3 직접 접근 |
| Starburst Enterprise | 6. Data Federation | 단일 SQL 조회 접점 · AI 기능 | Ranger 행·열 필터링, Resource groups, MCP server |
| MinIO AIStor | 4. Storage | S3 호환 오브젝트 저장소 | S3 API, IAM, WORM (Object Locking) |

---

## Cloudera CFM

Apache NiFi 기반의 Cloudera Flow Management. Cloudera 문서가 NiFi 핵심 기능을 묶는 다섯
범주에 CFM 배포판이 추가로 제공하는 것을 더했습니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| Flow Management | Guaranteed Delivery | write-ahead log 와 content repository 기반의 전달 보증 | ● |
| Flow Management | Data Buffering w/ Back Pressure and Pressure Release | 큐 적체 시 상류 억제, 임계 초과분 해제 | ● |
| Flow Management | Prioritized Queuing | 큐 내 처리 순서 지정 (최신 우선, 최대 크기 우선 등) | ● |
| Flow Management | Flow Specific QoS | 흐름 구간별 지연 대 처리량, 손실 허용도 설정 | ○ |
| Ease of Use | Visual Command and Control | 동작 중인 흐름을 GUI에서 변경·중단·재구성 | ● |
| Ease of Use | Flow Templates | 흐름 구성의 템플릿화와 재사용 | ○ |
| Ease of Use | Data Provenance | 데이터의 출처·변형·전달 이력을 건 단위로 기록 | ● |
| Ease of Use | Recovery / Rolling buffer of fine-grained history | 세밀한 이력 버퍼 기반 콘텐츠 복원 | ● |
| Security | System to System | 2-way SSL 등 암호화 프로토콜로 시스템 간 교환 | ● |
| Security | User to System | 사용자 인증과 시스템 접근 통제 | ○ |
| Security | Multi-tenant Authorization | 흐름 단위 권한 분리 | ○ |
| Extensible Architecture | Extension | 프로세서·컨트롤러 서비스·리포팅 태스크 확장 | ○ |
| Extensible Architecture | Classloader Isolation | 확장 간 의존성 충돌 격리 | ○ |
| Extensible Architecture | Site-to-Site Communication Protocol | NiFi 인스턴스 간 전용 전송 프로토콜 | ● |
| Flexible Scaling Model | Scale-out (Clustering) | 노드 추가를 통한 수평 확장 | ○ |
| Flexible Scaling Model | Scale-up & down | 단일 노드 내 동시성 조정 | ○ |
| CFM 배포판 | NiFi Registry | 흐름 정의 버전 관리와 환경 간 승격 | ○ |
| CFM 배포판 | Cloudera Manager 통합 | 설치·설정·모니터링 일원화 | ○ |
| CFM 배포판 | 사전 제공 프로세서 | 커넥티비티·변환·라우팅용 프로세서 다수 기본 제공 | ● |

---

## Cloudera CDE

Cloudera Data Engineering. Spark on Kubernetes 와 내장 Airflow 를 제공하는 처리·오케스트레이션
서비스입니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| 핵심 개념 | Virtual Cluster | CPU·메모리 범위가 정의된 개별 오토스케일링 클러스터. 사용자 기반 ACL 로 팀·사업부 격리 | ● |
| 핵심 개념 | Jobs | 설정·리소스와 함께 정의된 애플리케이션 코드 | ● |
| 핵심 개념 | Job run | 개별 작업 실행 | ● |
| 핵심 개념 | Resource | Python 파일, JAR, 의존성 등 참조 파일의 정의된 모음 | ○ |
| Spark | Spark on Kubernetes | 클러스터 생성·유지 없이 Spark 작업 실행 | ● |
| Spark | Job 단위 오토스케일링 | Spark dynamic allocation 기반 | ○ |
| Spark | 서비스·Virtual Cluster 오토스케일링 | Apache YuniKorn 기반 리소스 스케줄링 | ○ |
| Spark | Iceberg 런타임 기본 포함 | Spark classpath 에 Iceberg 의존성 기본 탑재 | ● |
| Spark | Iceberg row-level 연산 | copy-on-write 방식 MERGE / UPDATE / DELETE | ● |
| Spark | Iceberg Compaction | Spark Iceberg API 기반 압축 | ● |
| Spark | Spark History Server | 작업 실행 이력 조회와 트러블슈팅 | ○ |
| Airflow | 내장 Airflow | Virtual Cluster 생성 시 자동 배포, 별도 유지보수 불필요 | ● |
| Airflow | Airflow 타입 Job | CDE Job 으로서의 Airflow DAG | ● |
| Airflow | Pipeline Authoring UI | Airflow 숙련도와 무관하게 다단계 파이프라인 작성 | ○ |
| Airflow | 기본 제공 Operator | CDEOperator, CDWOperator, BashOperator, PythonOperator | ● |
| Airflow | 커스텀 DAG 배포 | 직접 작성한 Python DAG 배포. NiFi 흐름 트리거(REST API)와 Trino DDL/MERGE 실행(JDBC)이 여기에 해당 | ● |
| 인터페이스 | Web UI | 작업 생성·관리·모니터링 | ● |
| 인터페이스 | CDE CLI | 명령행 기반 작업 관리 | ○ |
| 인터페이스 | Jobs REST API | 작업 생성·실행·파라미터 전달 | ● |

---

## Cloudera CDP (Streams Messaging)

CDP Runtime 의 스트리밍 구성요소와 Streams Messaging Manager 의 기능입니다. 다이어그램에는
Kafka · SMM · ZooKeeper 만 표기했습니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| 구성요소 | Apache Kafka | 이벤트 스트리밍 백본 | ● |
| 구성요소 | Streams Messaging Manager (SMM) | Kafka 및 연관 서비스의 모니터링·관리 | ● |
| 구성요소 | Streams Replication Manager (SRM) | 클러스터 간 Kafka 토픽 복제 | － |
| 구성요소 | Schema Registry | 스키마 등록·버전 관리 | ○ |
| 구성요소 | Cruise Control | Kafka 부하 분산(리밸런싱) 워크플로 | ○ |
| SMM | End-to-end visibility | 프로듀서 → 토픽 → 컨슈머 전 구간 흐름 가시화 | ● |
| SMM | Intelligence-based filtering | 프로듀서·브로커·토픽·컨슈머 중 하나를 선택하면 연관 엔티티만 표시 | ● |
| SMM | Consumer lag 관제 | 컨슈머별 LAG 지표로 지연 컨슈머 식별 | ● |
| SMM | Data flow / lineage 시각화 | Atlas 연동으로 multi-hop 계보 추적 | ○ |
| SMM | REST endpoints | 전 기능에 대한 REST 제공, APM·티켓 시스템 연동 | ○ |
| SMM | Kafka Connect 관리 | Kafka Connect 커넥터 관리·모니터링 | － |
| SMM | Ranger 연동 | 토픽 단위 접근 통제 | ○ |

---

## Cloudera AI

AI Workbench, Cloudera AI Inference Service, AI Studio(Agent Studio) 세 구성요소입니다.
Inference Service 는 소비 접점이면서 Starburst AI 기능의 내부 모델 공급자이기도 합니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| AI Workbench | Sessions | Workbench 전반의 CPU·메모리·GPU 자원을 직접 활용, 데이터 레이크에 직접 연결 | ● |
| AI Workbench | Experiments | 학습 워크로드의 여러 변형을 실행하고 결과를 추적 | ○ |
| AI Workbench | Models | 클릭 몇 번으로 배포, HA 방식의 REST 엔드포인트로 서빙 | ● |
| AI Workbench | Jobs | 모델 드리프트 모니터링을 포함한 종단간 파이프라인 오케스트레이션 | ○ |
| AI Workbench | Applications | Flask, Streamlit 등으로 현업용 대화형 화면 제공 | ○ |
| AI Workbench | Model Governance | 배포 모델을 Cloudera Data Catalog 에 추적, 모델-데이터 계보 관리 | ○ |
| AI Workbench | 격리·컨테이너화 워크로드 | Python · R · Spark-on-Kubernetes 를 격리 실행, 분산 의존성 관리 | ● |
| Inference Service | 프로덕션 서빙 환경 | 예측형·생성형 AI 모델의 운영 서빙 | ● |
| Inference Service | 고가용성 · 확장성 | HA, 성능, 내결함성, 확장성 대응 | ○ |
| Inference Service | Hugging Face 모델 배포 | 배포 시 text generation · embedding · reranking 등 task 선택 | ○ |
| Inference Service | OpenAI 호환 엔드포인트 | Starburst · Argus RAG Studio · AI Agent 가 같은 사내 엔드포인트를 호출 | ● |
| AI Studio (Agent Studio) | 로우코드 에이전트 작성 | 에이전트 생성, 작업 할당, 커스텀 AI 도구 결합 | ● |
| AI Studio (Agent Studio) | 워크플로 구성 | 다단계 자동화 워크플로로 조합 | ○ |
| AI Studio (Agent Studio) | 하이코드 전환 | Workbench 에서 에이전트·도구를 직접 구현 | ○ |
| AI Studio (Agent Studio) | 라이프사이클 관리 | 프로덕션 에이전트 워크플로의 전 주기 관리 | ○ |
| AI Studio (Agent Studio) | 내장 관측·로깅 | 모니터링과 트러블슈팅용 observability, logging | ○ |

---

## Starburst Enterprise

Trino 의 상용 배포판(SEP). 오픈소스 Trino 대비 SEP 가 제공하는 기능 위주입니다. 이
아키텍처가 쓰는 커넥터는 Iceberg(→MinIO) · Kafka · Hive · Oracle 네 가지입니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| 커넥터 | 확장 커넥터 세트 | Trino 커넥터에 더해 다수 커넥터 추가 제공 | ● |
| 커넥터 | 커넥터 성능·보안 개선 | 기존 Trino 커넥터의 pushdown·보안 강화 | ● |
| 커넥터 | Dynamic filtering | 조인 시 스캔 대상 동적 축소 | ○ |
| 커넥터 | 커넥터별 pushdown 매트릭스 | 커넥터별 지원 기능 비교표 제공 | ○ |
| 보안·접근 제어 | Built-in access control | SEP 자체 접근 통제 | ● |
| 보안·접근 제어 | Apache Ranger 연동 | global · catalog · schema · table · column · row 수준 필터링. Layer 6 경유 조회에만 적용 | ● |
| 보안·접근 제어 | Kerberos 지원 | credential passthrough 및 캐싱 포함 | ○ |
| 보안·접근 제어 | LDAP 인증 | 디렉터리 기반 사용자 인증 | ○ |
| 보안·접근 제어 | Secrets management | 자격증명 보호 | ○ |
| 보안·접근 제어 | Encrypted internal communication | 클러스터 내부 통신 암호화 | ○ |
| 보안·접근 제어 | User impersonation | 데이터 소스별 사용자 위임 | ○ |
| 보안·접근 제어 | Password credential passthrough | 원천으로 자격증명 전달 | ○ |
| 보안·접근 제어 | Query auditing | 질의 감사 | ● |
| 성능 | Cost-based optimizer | Trino CBO 포함 | ○ |
| 성능 | Starburst Warp Speed | 자동 인덱싱·캐싱 기반 가속 | ○ |
| 성능 | Starburst Cached Views | 캐시된 뷰 (구 materialized view) | ○ |
| 성능 | Table scan redirection | 스캔 대상을 캐시 테이블로 전환 | ○ |
| 성능 | Cache service / Cache service CLI | 캐시 관리 서비스와 명령행 도구 | ○ |
| 성능 | Fault-tolerant execution | 작업 실패 시 재시도 기반 장기 질의 보호 | ○ |
| 성능 | Resource groups | 동시 실행 질의 수·자원 상한 통제. 원천 직접 페더레이션(1 → 6) 부하 제한에 필수 | ● |
| 성능 | Session property managers | 세션 속성 자동 적용 | ○ |
| 성능 | Workload management | 워크로드 단위 관리 | ○ |
| 성능 | Distributed sort · Spill to disk · CTE reuse | 대형 질의 처리 보조 | ○ |
| 성능 | Graceful shutdown | 워커 무중단 축소 | ○ |
| 운영·거버넌스 | Starburst Enterprise 웹 UI | 전용 관리 화면 | ● |
| 운영·거버넌스 | Starburst Insights | 클러스터 메트릭 대시보드 | ● |
| 운영·거버넌스 | High availability · autoscaling | Coordinator HA, 워커 오토스케일 | ● |
| 운영·거버넌스 | Data products | 데이터 상품 정의·게시 | ○ |
| 운영·거버넌스 | Apache Atlas 연동 | Starburst Atlas plugin, Atlas CLI, Ranger TagSync and Atlas | ○ |
| 운영·거버넌스 | Backend service | 부가 기능용 백엔드 | ○ |
| 운영·거버넌스 | Monitoring with JMX · OpenMetrics | 메트릭 노출 | ○ |
| 운영·거버넌스 | Observability with OpenTelemetry | 분산 트레이싱 | ○ |
| 운영·거버넌스 | Starburst Admin | 배포 자동화 도구 | ○ |
| AI | Starburst AI Agent | 자연어 질문을 SQL 로 변환·실행하는 대화형 에이전트 | ● |
| AI | AI Data Assistant (AIDA) | 분석 보조 어시스턴트 | ● |
| AI | Starburst MCP server | 인증된 stateless HTTP 엔드포인트. 읽기 전용 질의 도구, 데이터 상품 검색·상세 조회 도구 | ● |
| AI | AI functions | embedding · prompt · task(감성 분석, 분류) 함수 | ● |
| AI | Model provider — OpenAI 호환 | 온프레미스 배포 모델을 명시적으로 허용. 사내 엔드포인트 URL 지정, API 키 생략 가능 | ● |
| AI | Data product AI agent-based enrichment | 에이전트 기반 데이터 상품 보강 | ○ |
| AI | Guardrails | AI 기능 안전장치 | ○ |

---

## MinIO AIStor

S3 호환 오브젝트 스토리지. 문서상 오브젝트는 S3 API, 테이블은 Iceberg, 파일은 SFTP 로
접근하는 단일 저장소로 기술됩니다.

| 영역 | 기능 | 설명 | 범위 |
|---|---|---|---|
| 인터페이스 | S3 API | 별도 메타데이터 DB 없이 동작하는 네이티브 S3 호환 | ● |
| 인터페이스 | S3 Express | 저지연 워크로드용 S3 프로토콜 변형 | － |
| 인터페이스 | Iceberg Catalog interface (AIStor Tables) | Iceberg 테이블 네이티브 지원. 별도 REST Catalog 구현체 대체 여부 검토 대상 | ○ |
| 인터페이스 | SFTP / FTP / FTPS | 게이트웨이 없이 동일 버킷을 파일 클라이언트에 노출 | － |
| 인터페이스 | MCP | Model Context Protocol 연동 | － |
| 인터페이스 | OpenSharing | Delta Sharing 프로토콜 지원 | － |
| 데이터 보호 | Erasure Coding | 분산 패리티 기반 데이터 보호 | ○ |
| 데이터 보호 | Healing | 장애 발생 시 자동 복구 | ○ |
| 데이터 보호 | Object Versioning | 오브젝트 버전 관리 | ○ |
| 데이터 보호 | Object Locking / Immutability (WORM) | 버전 오브젝트의 삭제 방지. `docs/raw/` 원본 보존기한 관리에 적용 | ○ |
| 데이터 보호 | Bucket Replication | active-passive · active-active 복제 | ○ |
| 데이터 보호 | Server-Side Encryption (MinIO KMS / KES) | 저장 시 암호화와 키 관리 | ○ |
| 접근 제어·운영 | Identity and Access Management | LDAP, OpenID Connect, Azure AD, Okta, Keycloak 연동과 정책 기반 통제. S3 직접 접근 경로(4 → 7)의 유일한 통제 수단 | ● |
| 접근 제어·운영 | Object Lifecycle Management | 자동 만료(expiration)와 계층화(tiering) | ○ |
| 접근 제어·운영 | Bucket Notifications | 오브젝트 이벤트 알림 | － |
| 접근 제어·운영 | Observability | 메트릭 수집, 감사 로그, OpenTelemetry 트레이싱 | ○ |
| 접근 제어·운영 | Multi-tenancy | 테넌트 격리 | ○ |
| 접근 제어·운영 | RDMA Acceleration | RDMA 기반 전송 가속 | － |
| 도구 | MinIO KMS | 저장 시 암호화를 위한 키 관리 서버 | ○ |
| 도구 | MinIO DirectPV | 직접 연결 스토리지용 Kubernetes CSI 드라이버 | ○ |
| 도구 | MinIO Warp | S3 호환 벤치마킹 도구 (처리량·지연 측정) | ○ |
| 도구 | MinIO Sidekick | 분산 HTTP 서비스용 클라이언트 사이드 로드밸런서 | － |
