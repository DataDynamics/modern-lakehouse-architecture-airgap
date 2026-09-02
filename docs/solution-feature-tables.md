# 솔루션별 기능표

여덟 제품의 핵심 기능을 **제품마다 표 하나, 10행**으로 정리한 문서입니다. 도입 검토 회의에서
제품 단위로 한 장씩 보는 용도이며, 전체 기능 목록과 출처는
[solution-features.md](solution-features.md), 각 제품이 담당하는 범위는
[solutions.md](solutions.md), 동작 환경은 [solution-runtimes.md](solution-runtimes.md) 에
있습니다. 검토 포인트에 나오는 `4→7` 같은 표기는 [architecture.md — Layer 간 경로](architecture.md#layer-간-경로)
의 경로 번호입니다. Argus 두 제품은 공개 저장소의 README · 문서 · 코드로 확인했습니다.

**열 설명**

| 열 | 내용 |
|---|---|
| 기능 | 제품 문서의 기능명 (원문 표기 우선) |
| 설명 | 동작 방식 한 문장 + 특징 한 문장 |
| 범위 | ● 다이어그램에 명시 · ○ 운영상 전제 · － 이번 아키텍처 범위 밖 |
| 검토 포인트 | 금융권 요건 · 폐쇄망 제약 · 다른 제품과의 중복. 없으면 － |

라이선스 · 에디션 경계(예: SEP 와 Trino OSS, AIStor 와 MinIO 커뮤니티판의 기능 차이)는
저장소에 근거 자료가 없어 표에 넣지 않았습니다. 견적 단계에서 벤더 확인이 필요합니다.

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
- [제품 간 중복 기능 정리](#제품-간-중복-기능-정리)

---

## 한눈에 보기

| 제품 | 아키텍처 위치 | 핵심 역할 | 결정적인 기능 | 가장 큰 검토 포인트 |
|---|---|---|---|---|
| Cloudera CFM | 2. Ingestion | 원천 수집 · 변환 · 라우팅 | Guaranteed Delivery, Data Provenance | 계정계 CDC 대상은 대기계·정보계 복제본으로 |
| Cloudera CDE | 5. Processing & Orchestration | Spark 변환 · Airflow 오케스트레이션 | Spark on K8s, Iceberg MERGE, 내장 Airflow | 온프레미스 릴리스의 Spark · Airflow · Iceberg 버전 재확인 |
| Cloudera CDP | 3. Streaming Bus | Kafka 이벤트 스트리밍 · 관제 | Consumer lag 관제 | Kafka → MinIO 직결을 두지 않아 지연 하한이 Spark 주기 |
| Cloudera AI | 7. Consumption · 모델 서빙 | 모델 학습 · 서빙 · 에이전트 | Inference Service (OpenAI 호환) | 모델 반입은 오프라인, GPU 용량 산정 |
| Starburst Enterprise | 6. Data Federation | 단일 SQL 조회 접점 · AI 기능 | Ranger 행·열 필터링, Resource groups, MCP | 마스킹이 S3 직접 접근 경로에는 적용되지 않음 |
| MinIO AIStor | 4. Storage | S3 호환 오브젝트 저장소 | S3 API, IAM, WORM | AIStor Tables 로 별도 REST Catalog 대체 여부 |
| Argus RAG Studio | RAG | 문서 인제스천 · 검색/생성 · 평가 | 소스 워치, 하이브리드 검색, REST API | 인덱스 권한 태그와 Agent 권한 위임을 한 쌍으로 |
| Argus Catalog | Data Catalog | 메타데이터 · 리니지 · 거버넌스 | Query Listener 리니지, AI Agent 카탈로그 | Starburst 업그레이드 시 Listener SPI 호환성 |

---

## Cloudera CFM

Apache NiFi 기반 Flow Management. 원천마다 다른 프로토콜을 하나의 흐름 설계 도구로
흡수하는 Layer 2 의 제품입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| Guaranteed Delivery | 수신한 데이터를 write-ahead log 와 content repository 에 먼저 기록한 뒤 처리하므로 노드 장애 시에도 유실되지 않는다. 전달 완료까지 재시도가 흐름 단위로 보장된다 | ● | 계정계 거래 원장처럼 누락이 허용되지 않는 데이터의 기본 전제. 유실 방지 대가로 디스크 I/O 가 늘어나므로 repository 볼륨을 별도 디스크로 분리 |
| Back Pressure · Pressure Release | 큐가 설정한 건수·용량을 넘으면 상류 프로세서를 멈춰 적체를 억제하고, 임계를 넘긴 오래된 항목은 만료시킬 수 있다. 하류 장애가 상류로 전파되지 않는다 | ● | Kafka · MinIO 점검 중에도 원천 연결을 끊지 않아도 됨. 만료 정책은 데이터 성격별로 달리 잡아야 함 (거래 데이터는 만료 금지) |
| Prioritized Queuing | 큐 안의 FlowFile 처리 순서를 최신 우선 · 최대 크기 우선 · 속성 기반 등으로 지정한다. 지연에 민감한 흐름을 먼저 보낼 수 있다 | ● | FDS 이벤트처럼 초 단위 요건 데이터를 배치 파일보다 앞세우는 데 사용 |
| Visual Command and Control | 동작 중인 흐름을 GUI 에서 멈추지 않고 변경 · 중단 · 재구성한다. 각 큐의 적체 상태를 실시간으로 본다 | ● | 운영자가 코드 없이 흐름을 고치는 만큼, 변경 이력은 NiFi Registry 로 남겨야 감사 대응 가능 |
| Data Provenance | 데이터 한 건이 어디서 들어와 어떤 변환을 거쳐 어디로 나갔는지를 이벤트 단위로 기록한다. 특정 건을 추적해 내용까지 재생할 수 있다 | ● | 금융 감사에서 "이 값이 어디서 왔나"에 답하는 1차 근거. 이력 저장소 용량과 보존 기간을 정해야 함. Argus Catalog 의 NiFi Flow 리니지와 상보적 (건 단위 vs 흐름 단위) |
| Site-to-Site | NiFi 인스턴스 간 전용 프로토콜로 데이터를 압축 · 암호화해 전송하며 부하를 자동 분산한다. 망 분리 구간을 잇는 표준 방법이다 | ● | 업무망과 분석망 사이에 NiFi 를 양쪽에 두고 Site-to-Site 로 연결하면 망 연계 솔루션 역할을 일부 대체 가능. 보안 부서와 프로토콜 승인 필요 |
| 사전 제공 프로세서 | DB · 파일 · MQ · REST · Kafka · S3 등 연동과 변환 · 라우팅용 프로세서를 기본 제공한다. 대부분의 원천은 설정만으로 연결된다 | ● | 문서마다 "300+" 와 "400+" 표기가 갈리므로 반입 버전의 Components Reference 로 확정. 대외계 전문 규격은 커스텀 프로세서가 필요할 수 있음 |
| 보안 | 시스템 간은 2-way SSL, 사용자는 LDAP · Kerberos 인증, 흐름 단위로 권한을 분리한다. 프로세서 그룹마다 접근 정책을 둔다 | ○ | 팀별 흐름을 한 클러스터에 두려면 Multi-tenant Authorization 이 전제. 인증서 갱신 절차를 폐쇄망에서 수립 |
| Clustering | 노드를 추가하면 흐름이 자동 분산되고, ZooKeeper 로 코디네이터를 선출한다. 노드 하나가 빠져도 흐름은 유지된다 | ○ | Streaming Bus 의 ZooKeeper 앙상블을 공유할지, NiFi 전용으로 둘지 결정 |
| NiFi Registry · Cloudera Manager | Registry 는 흐름 정의를 버전 관리하고 개발 → 운영으로 승격한다. Cloudera Manager 는 설치 · 설정 · 모니터링을 다른 Cloudera 제품과 한 화면에서 다룬다 | ○ | 흐름 변경도 코드처럼 리뷰 · 승인 절차를 태우려면 Registry 가 필수. CDP · CDE 와 같은 Manager 로 관리되므로 운영 인력 통합 가능 |

---

## Cloudera CDE

Spark on Kubernetes 와 내장 Airflow 를 제공하는 Data Engineering 서비스. 무거운 변환과
일정 관리를 담당하는 Layer 5 의 제품입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| Virtual Cluster | CPU · 메모리 상한을 정한 독립 오토스케일링 클러스터를 여러 개 두고, 사용자 ACL 로 접근을 나눈다. 팀 · 사업부마다 자원 경계를 만든다 | ● | 배치 · 스트리밍 · 임시 분석을 별도 Virtual Cluster 로 나눠야 야간 배치가 임시 작업에 밀리지 않음 |
| Jobs · Job run · Resource | 코드와 설정, 의존성 파일(Python · JAR)을 Job 으로 묶어 등록하고, 실행마다 Job run 으로 이력을 남긴다. 같은 Job 을 파라미터만 바꿔 재실행한다 | ● | 재실행 · 재처리 이력이 자동으로 남아 감사 대응에 유리. Resource 로 사내 라이브러리를 반입하는 절차 필요 |
| Spark on Kubernetes | 상시 클러스터 없이 작업마다 Executor Pod 를 띄우고 끝나면 회수한다. 유휴 자원이 남지 않는다 | ● | YARN 기반 레거시 Spark 작업이 있으면 이관 검증 필요. K8s 노드 풀 용량이 곧 동시 실행 상한 |
| 오토스케일링 | Job 안에서는 Spark dynamic allocation 으로 Executor 수를, 클러스터 수준에서는 YuniKorn 이 큐 · 우선순위로 자원을 배분한다. 두 단계로 확장한다 | ○ | 폐쇄망은 노드 추가가 느리므로 상한을 물리 용량에 맞춰 보수적으로 설정 |
| Iceberg 런타임 기본 포함 | Spark classpath 에 Iceberg 라이브러리가 탑재되어 별도 설치 없이 Iceberg 테이블을 읽고 쓴다. 버전 충돌을 Cloudera 가 검증한다 | ● | Trino 와 Spark 의 Iceberg 스펙 버전(V2) 을 맞춰야 함. REST Catalog 접속 설정은 두 엔진에 동일하게 |
| Iceberg row-level 연산 | MERGE · UPDATE · DELETE 를 copy-on-write 로 수행해 영향받는 파일을 새로 쓴다. 트랜잭션 단위로 스냅샷이 남는다 | ● | CDC 반영(Silver) 의 핵심. 갱신 비율이 높은 테이블은 파일 재작성 비용이 커서 파티션 설계가 중요. merge-on-read 지원 여부는 반입 버전에서 확인 |
| Iceberg Compaction | 작은 파일을 병합하고 오래된 스냅샷 · 고아 파일을 정리한다. 조회 성능과 저장 효율을 유지한다 | ● | 스트리밍 적재는 작은 파일을 계속 만들므로 Compaction 주기를 Airflow 로 강제. 스냅샷 만료는 time-travel 요건(감사 재현 기간) 과 상충하니 보존 기간 먼저 확정 |
| 내장 Airflow | Virtual Cluster 를 만들면 Airflow 가 함께 배포되고 업그레이드 · 백업을 CDE 가 관리한다. DAG 를 Airflow 타입 Job 으로 등록한다 | ● | 별도 Airflow 를 운영할 인력이 없어도 됨. 대신 Airflow 버전 선택권이 CDE 릴리스에 묶임 |
| Operator · 커스텀 DAG | CDEOperator · CDWOperator · Bash · Python Operator 를 기본 제공하고, 직접 작성한 Python DAG 를 배포한다. NiFi REST 트리거와 Trino JDBC 실행은 커스텀 DAG 로 구현한다 | ● | NiFi · Trino 호출용 Operator 는 직접 작성 · 관리해야 하므로 DAG 코드 저장소와 배포 파이프라인 필요. Argus Catalog 가 DAG 를 파이프라인 자산으로 등록 |
| Web UI · CLI · REST API | 작업 생성 · 실행 · 모니터링을 UI 와 CLI, REST 세 방식으로 제공한다. 수동 실행 시 파라미터를 넘겨 설정을 재정의한다 | ● | 운영 자동화는 CLI · REST 로, 장애 대응은 UI 로 역할 분리. API 토큰 발급 · 회전 절차 필요 |

---

## Cloudera CDP (Streams Messaging)

CDP Runtime 의 Kafka 계열 구성요소. 생산자와 소비자를 시간적으로 분리하는 Layer 3 의
제품입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| Apache Kafka | 토픽 · 파티션 단위로 이벤트를 저장하고 복제(기본 3) 로 브로커 장애를 견딘다. 소비자는 각자 오프셋으로 독립 소비한다 | ● | 토픽 명명 규칙(raw.* / cdc.* / evt.*) 과 보존 기간을 먼저 정의. 재처리 요건이 있으면 보존 기간을 길게 |
| Streams Messaging Manager | Kafka 와 연관 서비스의 토픽 · 브로커 · 컨슈머 상태를 한 화면에서 관제한다. 알림 정책을 설정한다 | ● | CFM · CDE 가 서로 다른 컨슈머 그룹으로 붙으므로 그룹별 관제가 실질적 운영 도구 |
| ZooKeeper | 브로커 등록과 컨트롤러 선출을 담당하는 코디네이션 서비스로, 3 또는 5 노드 앙상블로 운영한다 | ● | 최근 Kafka 는 KRaft 로 ZooKeeper 를 제거하는 추세. 반입 CDP 버전이 KRaft 를 지원하는지 확인해 다이어그램 표기 조정 |
| End-to-end visibility | 프로듀서 → 토픽 → 컨슈머 전 구간의 흐름과 처리량을 시각화한다. 어느 구간에서 병목이 생기는지 바로 보인다 | ● | － |
| Intelligence-based filtering | 프로듀서 · 브로커 · 토픽 · 컨슈머 중 하나를 고르면 연관된 엔티티만 남긴다. 장애 범위를 빠르게 좁힌다 | ● | － |
| Consumer lag 관제 | 컨슈머 그룹별 LAG(미소비 오프셋 수) 를 추적해 지연 컨슈머를 식별하고 알림을 보낸다 | ● | Spark Streaming 지연이 곧 MinIO 적재 지연이므로 LAG 임계값이 SLA 의 선행 지표 |
| Schema Registry | 토픽 메시지의 스키마를 등록 · 버전 관리하고 호환성 규칙(backward · forward) 을 강제한다 | ○ | 원천 스키마 변경이 Spark 작업을 깨뜨리지 않게 하려면 필수. Argus Catalog 의 스키마 스냅샷과 역할 분담 정의 |
| Cruise Control | 파티션 분포와 브로커 부하를 분석해 리밸런싱을 자동 수행한다. 브로커 추가 · 제거 시 재배치를 맡는다 | ○ | 브로커 증설이 드문 폐쇄망에서는 우선순위 낮음 |
| Ranger 연동 · REST endpoints | Ranger 정책으로 토픽 단위 읽기 · 쓰기 권한을 통제하고, SMM 전 기능을 REST 로 노출해 APM · 티켓 시스템과 연동한다 | ○ | 토픽 권한을 Ranger 로 통합하면 Starburst · Kafka 권한을 한 정책 저장소에서 관리 가능 |
| Streams Replication Manager | 클러스터 간 토픽을 복제해 DR 이나 데이터센터 간 동기화를 구성한다 | － | 이번 범위 밖. DR 센터 요건이 생기면 재검토 |

---

## Cloudera AI

AI Workbench · Inference Service · Agent Studio. 사람의 모델 개발 접점(Layer 7) 이면서
Starburst · Argus · AI Agent 의 내부 모델 공급자(모델 서빙) 입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| Sessions | Workbench 의 CPU · 메모리 · GPU 를 할당받은 대화형 세션에서 데이터 레이크에 직접 연결해 작업한다. Jupyter · RStudio 등 편집기를 고른다 | ● | 학습 데이터를 Trino 를 거치지 않고 S3 에서 읽는 경로. Starburst 마스킹이 적용되지 않으므로 MinIO IAM 으로 버킷 단위 통제 |
| Models | 학습한 모델을 클릭 몇 번으로 배포해 HA 구성의 REST 엔드포인트로 서빙한다. 버전별로 트래픽을 나눈다 | ● | 예측형(스코어링) 모델 서빙. 생성형 모델은 Inference Service 로 분리 |
| 격리 워크로드 | Python · R · Spark-on-Kubernetes 작업을 컨테이너로 격리 실행하고 의존성을 런타임 이미지로 관리한다 | ● | 폐쇄망에서는 런타임 이미지와 pip · conda 미러를 사내에 두어야 함. 이미지 반입 절차가 운영의 핵심 |
| Experiments · Jobs · Applications | 학습 변형을 추적하고, 파이프라인(드리프트 모니터링 포함) 을 스케줄하며, Flask · Streamlit 화면을 현업에 배포한다 | ○ | Jobs 는 CDE Airflow 와 역할이 겹침. 모델 파이프라인은 Workbench Jobs, 데이터 파이프라인은 CDE 로 경계 설정 |
| Model Governance | 배포한 모델을 Data Catalog 에 등록해 학습 데이터 · 모델 · 배포의 계보를 남긴다 | ○ | Argus Catalog 의 ML 모델 레지스트리와 중복. 어느 쪽을 모델 대장(system of record) 으로 삼을지 결정 |
| Inference Service | 예측형 · 생성형 모델을 프로덕션 등급으로 서빙한다. HA · 오토스케일 · 내결함성을 갖춘다 | ● | GPU 노드 용량이 동시 추론 상한. 임베딩 · 리랭커 · 생성 모델을 한 서비스에서 서빙할지 분리할지 결정 |
| OpenAI 호환 엔드포인트 | OpenAI API 규격으로 chat · embedding 엔드포인트를 노출한다. 클라이언트 코드 변경 없이 외부 API 를 사내 모델로 대체한다 | ● | Starburst · Argus RAG Studio · AI Agent 가 모두 이 엔드포인트를 쓰므로 전 구간이 내부에서 닫힘. Starburst 의 허용 모델 정규식은 별도 설정 |
| Hugging Face 모델 배포 | 모델 저장소에서 가져온 모델을 text generation · embedding · reranking 등 task 를 골라 배포한다 | ○ | 폐쇄망은 Hugging Face 직접 접근 불가. 모델 파일을 오프라인 반입해 사내 저장소에 두는 절차 필요 (Argus Catalog 의 에어갭 반입 SDK 활용 가능) |
| Agent Studio | 로우코드로 에이전트를 만들고 작업과 커스텀 도구를 결합한다. 필요하면 Workbench 에서 하이코드로 전환한다 | ● | 고객 AI Agent 를 Agent Studio 로 만들지, 별도 프레임워크로 만들지가 설계 분기점 |
| 에이전트 운영 | 프로덕션 에이전트 워크플로의 라이프사이클을 관리하고 내장 관측 · 로깅을 제공한다 | ○ | 감사 요건(질문 → 근거 → SQL → 답변) 을 내장 로깅이 충족하는지, Argus Catalog 의 AI Agent 미터링과 어떻게 합칠지 확인 |

---

## Starburst Enterprise

Trino 상용 배포판(SEP). 서로 다른 저장소를 하나의 SQL 네임스페이스로 묶는 Layer 6 의
제품입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| 커넥터 | Iceberg · Kafka · Hive · Oracle · PostgreSQL 등을 카탈로그로 등록해 한 SQL 에서 조인한다. SEP 커넥터는 pushdown 과 보안이 강화되어 있다 | ● | 원천(Oracle) 커넥터는 부하를 원천에 직접 전달하므로 대기계 · 정보계 복제본에 연결. PostgreSQL 커넥터로 pgvector 테이블도 조회 |
| Ranger 연동 | catalog · schema · table · column · row 수준 정책을 Ranger 에서 관리하고 사용자 · 그룹별 컬럼 마스킹과 행 필터를 적용한다 | ● | Layer 6 을 거치는 조회에만 적용됨. S3 직접 접근(4→7) 은 MinIO IAM 이 통제하므로 두 경로의 통제 수준 차이를 설계 문서에 명시 |
| 접근 통제 · 감사 | Ranger 없이도 SEP 자체 접근 통제를 쓸 수 있고, 모든 질의를 사용자 · 대상 · 시각과 함께 감사 로그로 남긴다 | ● | 감사 로그를 어디에 보관하고 얼마나 유지할지 결정. Agent 감사(질문 → SQL) 와 연결하면 전 구간 추적 가능 |
| Resource groups | 사용자 · 소스 · 질의 유형별로 동시 실행 수와 CPU · 메모리 상한을 두고 초과분을 큐에 넣는다 | ● | 원천 직접 페더레이션의 부하 제한 수단. 스캔 행 수 제한과 함께 설정하지 않으면 실수 하나가 원천을 멈춤 |
| HA · autoscaling | Coordinator 를 이중화하고 Worker 를 부하에 따라 늘리고 줄인다. Graceful shutdown 으로 실행 중 질의를 끝내고 축소한다 | ● | K8s 배포 전제. 폐쇄망은 노드 풀 상한이 곧 최대 규모 |
| 웹 UI · Insights | 관리 화면에서 클러스터 · 카탈로그를 설정하고, Insights 대시보드로 질의 이력 · 자원 사용 · 실패 원인을 본다 | ● | Insights 는 backend service(PostgreSQL) 가 필요. REST Catalog 메타 저장소와 같은 인스턴스를 쓸지 결정 |
| Warp Speed · Cached Views | Warp Speed 는 자주 읽는 데이터를 워커 로컬에 자동 인덱싱 · 캐싱하고, Cached Views 는 뷰 결과를 캐시 테이블로 유지한다 | ○ | 대시보드 반복 질의에 효과. 캐시된 데이터에도 Ranger 정책이 동일하게 적용되는지 확인 |
| Fault-tolerant execution | 중간 결과를 외부 저장소에 spill 하고 실패한 태스크만 재시도해 장기 질의를 보호한다 | ○ | 배치성 대형 질의(월말 집계) 에 적용. spill 저장소로 MinIO 버킷 하나를 별도 할당 |
| AI Agent · AIDA · AI functions | AI Agent 는 자연어를 SQL 로 바꿔 실행하고, AIDA 는 분석을 보조하며, AI functions 는 SQL 안에서 embedding · prompt · 분류를 호출한다 | ● | 모델 제공자로 사내 OpenAI 호환 엔드포인트를 지정. `ai.agent.allowed-models-regex` 기본값이 검증 모델만 허용하므로 고객 모델은 정규식 직접 지정 → 품질 실측 필요 |
| MCP server · Model provider | MCP server 는 인증된 HTTP 엔드포인트로 읽기 전용 질의 · 데이터 상품 조회 도구를 노출한다. Model provider 는 온프레미스 OpenAI 호환 모델을 명시적으로 허용한다 | ● | Agent 가 MCP 로 붙을 때 사용자 권한 위임(impersonation) 이 되는지가 핵심. Argus RAG Studio 의 검색과 Starburst 자체 RAG 기능이 겹치므로 문서 검색은 Argus 로 일원화 |

---

## MinIO AIStor

S3 호환 오브젝트 스토리지. 정형 3계층과 문서 존을 한 저장소에 두는 Layer 4 의 제품입니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| S3 API | 별도 메타데이터 DB 없이 네이티브로 S3 API 를 제공한다. NiFi · Spark · Trino · Argus 가 같은 프로토콜로 같은 데이터에 접근한다 | ● | 폐쇄망 DNS 에서 가상 호스트 스타일 URL 이 해석되지 않는 경우가 많으므로 모든 클라이언트에 `path-style-access=true` |
| Identity and Access Management | LDAP · OpenID Connect · Keycloak 과 연동해 사용자 · 서비스 계정을 인증하고, 버킷 · prefix 단위 정책으로 접근을 통제한다 | ● | S3 직접 접근 경로에는 Starburst 마스킹이 없으므로 IAM 정책이 유일한 통제. Argus RAG Studio 소스 계정은 `docs/` 읽기 전용으로 제한 |
| Iceberg Catalog interface | AIStor Tables 로 Iceberg 테이블 카탈로그를 스토리지가 직접 제공한다. 별도 카탈로그 서버 없이 엔진이 접속한다 | ○ | 이 아키텍처의 별도 REST Catalog(Nessie · Polaris 등) 와 그 PostgreSQL 의존성을 대체할 수 있는지 검토. Spark · Trino 양쪽 호환성 검증 필요 |
| Erasure Coding · Healing | 오브젝트를 데이터 · 패리티 조각으로 나눠 여러 드라이브 · 노드에 분산 저장하고, 손상된 조각을 자동 복구한다 | ○ | 최소 구성이 동일 사양 호스트 8대. 패리티 비율이 가용 용량을 결정하므로 초기 용량 산정에 반영 |
| Object Versioning | 같은 키에 쓴 오브젝트를 버전으로 보관해 덮어쓰기 · 삭제를 되돌린다 | ○ | Iceberg 스냅샷과 역할이 겹치므로 테이블 존은 끄고 `docs/raw/` 만 켜는 식으로 존별로 결정 |
| Object Locking (WORM) | 버전 오브젝트를 보존기한 동안 삭제 · 변경 불가로 잠근다. 거버넌스 모드는 관리자가 해제할 수 있고 컴플라이언스 모드는 누구도 해제할 수 없다 | ○ | 전자금융 문서 보존의무에 직접 대응. 컴플라이언스 모드는 되돌릴 수 없으므로 보존기간 정책을 먼저 확정. Argus 는 소스를 읽기 전용으로 다루므로 충돌 없음 |
| Bucket Replication | 버킷 단위로 다른 클러스터에 active-passive 또는 active-active 로 복제한다 | ○ | DR 요건이 생기면 적용. 복제 대역폭이 폐쇄망 회선에 맞는지 확인 |
| Server-Side Encryption | 저장 시 오브젝트를 암호화하고 키는 MinIO KMS / KES 가 관리한다. 사내 HSM 과 연동할 수 있다 | ○ | 금융권 암호화 요건에 대응. 키 관리 서버의 HA 와 백업이 별도 과제 |
| Lifecycle Management | 규칙에 따라 오브젝트를 자동 만료시키거나 저비용 계층으로 옮긴다 | ○ | Bronze 존의 보존 기간과 WORM 보존기한을 일치시켜야 함. 계층화 대상 저장소가 폐쇄망 안에 있어야 함 |
| Observability · Multi-tenancy | 메트릭 · 감사 로그 · OpenTelemetry 트레이싱을 제공하고 테넌트별로 자원과 네임스페이스를 격리한다 | ○ | 감사 로그는 S3 직접 접근 경로의 유일한 접근 기록. 보관 위치와 기간을 Starburst 감사 로그와 맞춤 |

---

## Argus RAG Studio

RAG 파이프라인의 구축 · 검색/생성 · 평가 · 운영 · 배포 플랫폼
([저장소](https://github.com/DataDynamics-OSS/argus-rag-studio), Apache-2.0). FastAPI 백엔드(:4700)
와 Next.js UI, 호스트별 Agent(:4501) 로 구성됩니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| 스토리지 소스 · 소스 워치 | S3 호환 · NAS 를 읽기 전용 소스로 등록하고 지정 prefix 를 주기 스캔해 새 문서를 자동 반입한다. 지문 캐시로 본 파일은 건너뛰고 정책이 바뀌면 자동 재평가한다 | ● | 원본을 수정 · 삭제하지 않으므로 WORM 존과 충돌 없음. 실시간 반입이 필요하면 CFM 푸시 연동 검토. 폴더 구조가 곧 라우팅 규칙이므로 `docs/` prefix 규약 먼저 확정 |
| 문서 라우팅 | 경로 · 메타 규칙과 내용 임베딩 유사도로 문서를 지식베이스(컬렉션) 에 자동 배정한다. 저신뢰 결정은 검토 대기열로 보낸다 | ○ | 약관 · 상품설명서 · 규정처럼 컬렉션을 나누는 기준을 업무 부서와 합의. 검토 대기열 담당자 지정 |
| 멀티포맷 인제스천 | txt · pdf · docx · xlsx · pptx · hwp/hwpx 를 파싱 전략(text · layout · docai · vlm · rhwp) 으로 텍스트화한다. 스캔 문서는 OCR, HWP 는 rhwp 렌더로 처리한다 | ● | 금융권 문서의 상당수가 HWP · 스캔 PDF 이므로 rhwp · OCR 품질을 샘플로 먼저 검증. vlm 전략이 쓰는 PyMuPDF 는 AGPL 이라 번들되지 않음 |
| 청킹 · 임베딩 | 청킹 8종 중 문서 유형에 맞는 방식을 고르고, 컬렉션마다 임베딩 모델 · 차원 · 거리 메트릭을 달리 지정한다. 임베딩 제공자는 OpenAI 호환 엔드포인트 | ● | 임베딩 모델을 Cloudera AI Inference 로 통일할지 Argus 자체 embedding_server 를 쓸지 결정. 모델 교체 시 컬렉션 단위 재인덱싱 |
| 하이브리드 검색 | 벡터 검색과 tsvector 렉시컬 검색을 RRF 로 융합한 뒤 리랭커(none / llm / cross_encoder) 로 재정렬한다. 메타데이터 필터를 함께 건다 | ● | 청크 메타데이터의 권한 태그를 검색 시점 필터로 강제하지 않으면 원본 접근 통제가 우회됨. Starburst 자체 RAG 기능과 중복 → 문서 검색은 Argus 로 일원화 |
| 생성 | 검색 결과를 컨텍스트로 넣어 인용이 달린 답변을 만들고, 멀티턴 챗(SSE) 과 여러 컬렉션을 한 번에 묻는 페더레이션 질의를 지원한다 | ● | 생성 LLM 도 사내 OpenAI 호환 엔드포인트로. 답변에 붙는 출처(s3 경로) 가 감사 근거가 되므로 형식을 Agent 감사 로그와 맞춤 |
| REST API | `/collections/{id}/search` · `/query` · `/chat` 과 `/search/federated` · `/query/federated` 를 제공한다. 인증은 로컬 JWT · Keycloak OIDC · API 키(서비스 계정) | ● | AI Agent 는 API 키로 호출. Agent 가 Vector DB 를 직접 조회할지 이 API 를 쓸지는 권한 필터 · 인용 규칙을 어디서 강제할지로 결정 |
| VectorStore 교체 | 기본 pgvector 를 `VectorStore` 추상화로 Qdrant · Weaviate · Milvus · Databricks 로 바꾼다. 전환 시 pgvector 에서 hydrate 한다 | ● | pgvector 를 유지하면 Trino PostgreSQL 커넥터로 벡터 테이블을 SQL 에서 바로 조회 가능. 다른 백엔드로 바꾸면 이 경로(VectorDB↔6) 가 사라짐 |
| 평가 · 피드백 | 골든 데이터셋으로 Hit Rate · MRR 을 재고 LLM-as-judge 로 faithfulness · 정확성을 채점한다. 👍/👎 피드백을 골든셋으로 승격한다 | ○ | LLM-as-judge 도 사내 모델로 돌아야 함. 평가 주기와 합격 기준을 도입 전에 정해야 "동작하는 RAG" 에서 멈추지 않음 |
| 운영 · 배포 | 파이프라인 버전 · 롤백 · diff, 질의 트레이스와 p50/p95 통계를 제공한다. 호스트별 Agent 가 Docker/systemd 로 워커 · 추론 서버를 원격 배포하고 모델 팩을 에어갭으로 반입한다 | ○ | 폐쇄망 배포 방식이 제품에 내장되어 있어 반입 절차가 단순. zot 레지스트리와 Model Repository 버킷을 MinIO 에 둘지 결정 |

---

## Argus Catalog

데이터 카탈로그 + ML 모델 레지스트리 메타데이터 플랫폼
([저장소](https://github.com/DataDynamics-OSS/argus-catalog), Apache-2.0). FastAPI 백엔드(:4600)
와 Next.js UI, PostgreSQL + pgvector 로 구성됩니다.

| 기능 | 설명 | 범위 | 검토 포인트 |
|---|---|---|---|
| 데이터셋 관리 | 데이터셋을 등록 · 검색하고 태그와 소유자(Technical / Business / Data Steward) 를 붙인다. 스키마 변경은 스냅샷으로 남아 알림 규칙을 탄다 | ● | 소유자 세 역할을 실제 조직에 매핑해야 함. 데이터 스튜어드 지정이 없는 조직은 도입 전에 역할부터 정의 |
| 메타데이터 동기화 | Trino · Hive · Kafka · S3 · Oracle · PostgreSQL 등 11종 플랫폼에서 스키마 · 키 · DDL · 행 수를 Metadata Sync 서비스(:4610) 가 상시 또는 배치로 수집한다 | ● | Trino 를 동기화하면 페더레이션된 원천 전체가 한 번에 수집됨. S3 · Kafka 직접 동기화는 Trino 경유와 중복이므로 필요할 때만 |
| 리니지 · ERD | Trino Query Listener(EventListener SPI) 와 Hive Hook 이 실행 질의의 입출력 컬럼을 보고해 컬럼 수준 리니지를 만든다. NiFi Flow · Airflow DAG 를 파이프라인 자산으로 등록하고 DDL 에서 ERD 를 생성한다 | ● | Listener 는 Trino Coordinator 플러그인이므로 Starburst 업그레이드 시 SPI 호환성 검증. 리니지가 끊기면 영향 분석이 침묵하므로 수집 지연 알림 필요 |
| 데이터 표준 · 용어집 | 멀티 표준 사전을 두고 형태소 분석으로 용어를 자동 생성하며, 컬럼명 표준 준수율을 측정한다. 용어집은 트리로 분류한다 | ○ | 금융권 표준 용어(계정계 코드 체계) 를 초기 사전으로 반입해야 자동 생성 품질이 나옴 |
| 시맨틱 검색 | pgvector 로 키워드 + 시맨틱 하이브리드 검색을 제공한다. 임베딩 제공자는 Local(sentence-transformers) · OpenAI 호환 · Ollama 중 선택 | ○ | Local 제공자면 외부 모델 없이 동작. 사내 Inference 로 통일하려면 OpenAI 호환 설정 |
| 데이터 품질 | 소스 DB 를 직접 프로파일링하고 규칙 10종(기본 8 + CUSTOM_SQL / PYTHON) 으로 검증한다. GOOD / WARN / BAD 점수를 리니지 업스트림으로 전파해 경고한다 | ○ | 프로파일링이 원천에 부하를 주므로 Starburst 와 마찬가지로 복제본 대상. 외부 품질 배치(pandas / PySpark) 는 CDE 에서 실행 가능 |
| API 카탈로그 | OpenAPI 스펙을 등록해 버전 diff 와 린트를 수행하고 URN 으로 관리한다 | ○ | Argus RAG Studio · Starburst MCP · Inference 엔드포인트를 등록하면 Agent 가 쓰는 API 목록이 한 곳에 모임 |
| AI Agent 카탈로그 | 에이전트를 등록하고 도구 · MCP 서버 · 의존 데이터셋을 리니지로 연결한다. 호출(invocation) 을 수집해 지연 · 토큰 · 성공률을 미터링하고 평가 기록과 정책 번들을 관리한다 | ● | 고객 AI Agent 의 감사 요건과 겹침. 질문 → 근거 → 답변 기록은 Agent 가, 호출 지표 · 정책은 Catalog 가 맡는 식으로 경계 정의 |
| ML 모델 레지스트리 | MLflow 호환으로 버전 · Stage(STAGING / PRODUCTION) 를 관리하고 모델 카드를 둔다. OCI 매니페스트 기반 Model Hub 와 `argus-model` CLI 로 외부 모델을 에어갭 반입한다 | ○ | Cloudera AI Model Governance 와 중복 → 모델 대장을 어느 쪽으로 할지 결정. 반입 SDK 는 Inference Service 의 Hugging Face 모델 반입에 활용 가능 |
| External API | `GET /metadata?urn=` · `/avro-schema?urn=` 으로 외부 시스템이 URN 기준 메타데이터와 스키마를 조회한다. 캐시와 강제 갱신 옵션을 둔다 | ● | Agent 가 질의 계획 전에 스키마 · 용어집을 읽는 경로. 서비스 토큰 발급과 캐시 TTL 을 Agent 응답 시간 요건에 맞춤 |

---

## 제품 간 중복 기능 정리

검토 포인트에 흩어진 중복 항목을 한 표로 모았습니다. 도입 전에 어느 쪽을 기준으로 삼을지
정해야 하는 지점입니다.

| 기능 | 제공 제품 | 권장 기준 | 근거 |
|---|---|---|---|
| Iceberg 카탈로그 | 별도 REST Catalog(Nessie · Polaris) / MinIO AIStor Tables | 검증 후 결정 | AIStor Tables 가 Spark · Trino 양쪽에서 검증되면 PostgreSQL 의존성을 하나 줄일 수 있음 |
| 문서 검색(RAG) | Argus RAG Studio / Starburst AI(RAG) | Argus RAG Studio | 인제스천 · 평가 · 권한 필터까지 한 제품. Starburst 는 SQL 쪽 AI 기능에 집중 |
| 리니지 | Argus Catalog / CFM Data Provenance / Cloudera Atlas / SMM 리니지 | Argus Catalog (통합), Provenance (건 단위) | Provenance 는 건 단위 추적, Catalog 는 자산 단위 계보로 역할이 다름. Atlas · SMM 리니지는 Catalog 로 흡수 |
| 모델 대장 | Argus Catalog 모델 레지스트리 / Cloudera AI Model Governance | 결정 필요 | 학습이 Workbench 에서 일어나면 Governance, 외부 모델 반입이 많으면 Catalog 가 유리 |
| 파이프라인 스케줄 | CDE Airflow / Cloudera AI Jobs / Argus RAG Studio 스케줄 | CDE Airflow (데이터), 각 제품 (자체 작업) | 데이터 파이프라인은 Airflow 로 일원화, 모델 · RAG 내부 작업은 제품 자체 스케줄 |
| Agent 감사 · 미터링 | 고객 AI Agent 감사 / Argus Catalog AI Agent 카탈로그 / Cloudera AI 에이전트 관측 | Agent (기록), Catalog (지표 · 정책) | 질문 → 근거 → 답변 원문은 Agent 가, 호출 지표와 정책 번들은 Catalog 가 |
| 스키마 변경 감지 | CDP Schema Registry / Argus Catalog 스키마 스냅샷 | Schema Registry (토픽), Catalog (테이블) | 실행 시점 강제는 Registry, 사후 영향 분석은 Catalog |
| 권한 정책 저장소 | Ranger (Starburst · Kafka) / MinIO IAM / Argus 컬렉션 권한 | Ranger 우선, 나머지는 매핑 | S3 직접 접근과 벡터 검색은 Ranger 가 닿지 않으므로 IAM · 컬렉션 권한을 Ranger 정책과 대응표로 관리 |
