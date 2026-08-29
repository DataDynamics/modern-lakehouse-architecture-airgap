# 솔루션별 주요 기능 목록

각 솔루션의 공식 문서에서 확인한 주요 기능을 정리한 것입니다. 기능명은 원문 표기를
유지했고, 각 절 머리에 확인에 사용한 문서 링크를 두었습니다. 전체 출처는 문서 끝의
[출처](#출처)에 모아두었습니다.

[solutions.md](solutions.md) 가 "이 아키텍처에서 무엇을 담당하는가"를 다룬다면, 이
문서는 "제품이 무엇을 제공하는가"의 목록입니다. 도입 검토와 기능 대조에 사용하는 것을
전제로 했습니다. 각 제품이 "어디에서 도는가"는
[solution-runtimes.md](solution-runtimes.md) 에 따로 정리했습니다.

**범위 표기** — 각 기능이 [참조 아키텍처](../assets/lakehouse-architecture-lr.svg) 에서
차지하는 위치를 함께 표시했습니다.

| 표기 | 의미 |
|---|---|
| ● | 다이어그램에 명시적으로 표기된 기능 |
| ○ | 다이어그램에 표기되지 않았으나 운영상 전제가 되는 기능 |
| － | 이번 아키텍처 범위 밖 (제품은 제공하나 사용하지 않음) |

> 문서에 명시된 버전·수치는 확인 시점(2026-08) 기준입니다. 폐쇄망 도입 시에는 실제
> 반입할 릴리스의 문서로 재확인하시기 바랍니다.

## 목차

- [Cloudera CFM (Apache NiFi)](#cloudera-cfm-apache-nifi)
  - [Flow Management](#flow-management)
  - [Ease of Use](#ease-of-use)
  - [Security](#security)
  - [Extensible Architecture](#extensible-architecture)
  - [Flexible Scaling Model](#flexible-scaling-model)
  - [CFM 배포판이 추가로 제공하는 것](#cfm-배포판이-추가로-제공하는-것)
- [Cloudera CDP — Streams Messaging](#cloudera-cdp--streams-messaging)
  - [Streams Messaging Manager 주요 기능](#streams-messaging-manager-주요-기능)
- [MinIO AIStor](#minio-aistor)
  - [인터페이스](#인터페이스)
  - [데이터 보호](#데이터-보호)
  - [접근 제어와 운영](#접근-제어와-운영)
  - [함께 제공되는 도구](#함께-제공되는-도구)
- [Cloudera CDE (Data Engineering)](#cloudera-cde-data-engineering)
  - [핵심 개념](#핵심-개념)
  - [Spark](#spark)
  - [Airflow](#airflow)
  - [인터페이스](#인터페이스-1)
- [Starburst Enterprise (SEP)](#starburst-enterprise-sep)
  - [커넥터](#커넥터)
  - [보안·접근 제어](#보안접근-제어)
  - [성능](#성능)
  - [운영·거버넌스](#운영거버넌스)
  - [AI 기능](#ai-기능)
- [Spotfire](#spotfire)
- [Cloudera AI](#cloudera-ai)
  - [AI Workbench](#ai-workbench)
  - [Cloudera AI Inference Service](#cloudera-ai-inference-service)
  - [AI Studio (Agent Studio)](#ai-studio-agent-studio)
- [확인 과정에서 드러난 검토 항목](#확인-과정에서-드러난-검토-항목)
- [출처](#출처)
- [용어집](#용어집)
  - [공통](#공통)
  - [Cloudera CFM (NiFi)](#cloudera-cfm-nifi)
  - [Cloudera CDP (Streams Messaging)](#cloudera-cdp-streams-messaging)
  - [MinIO AIStor](#minio-aistor-1)
  - [Cloudera CDE](#cloudera-cde)
  - [Starburst Enterprise](#starburst-enterprise)
  - [Spotfire](#spotfire-1)
  - [Cloudera AI](#cloudera-ai-1)

---

## Cloudera CFM (Apache NiFi)

문서: [Flow Management Overview](https://docs.cloudera.com/cfm/2.1.5/flow-management-overview/index.html) ·
[High Level Overview of Key NiFi Features](https://docs-archive.cloudera.com/cfm/2.0.1/nifi-overview/topics/nifi-features.html) ·
[What is Apache NiFi](https://docs.cloudera.com/cdf-datahub/7.3.1/flow-management-overview/topics/cfm-what-is-apache-nifi.html)

Cloudera 문서는 NiFi의 핵심 기능을 다섯 범주로 묶어 제시합니다. 아래 기능명은 문서의
원문 표기입니다.

### Flow Management

| 기능 | 설명 | 범위 |
|---|---|---|
| Guaranteed Delivery | write-ahead log 와 content repository 기반의 전달 보증 | ● |
| Data Buffering w/ Back Pressure and Pressure Release | 큐 적체 시 상류 억제, 임계 초과분 해제 | ● |
| Prioritized Queuing | 큐 내 처리 순서 지정 (최신 우선, 최대 크기 우선 등) | ● |
| Flow Specific QoS | 흐름 구간별 지연 대 처리량, 손실 허용도 설정 | ○ |

### Ease of Use

| 기능 | 설명 | 범위 |
|---|---|---|
| Visual Command and Control | 동작 중인 흐름을 GUI에서 변경·중단·재구성 | ● |
| Flow Templates | 흐름 구성의 템플릿화와 재사용 | ○ |
| Data Provenance | 데이터의 출처·변형·전달 이력을 건 단위로 기록 | ● |
| Recovery / Recording a rolling buffer of fine-grained history | 세밀한 이력 버퍼 기반 콘텐츠 복원 | ● |

### Security

| 기능 | 설명 | 범위 |
|---|---|---|
| System to System | 2-way SSL 등 암호화 프로토콜로 시스템 간 교환 | ● |
| User to System | 사용자 인증과 시스템 접근 통제 | ○ |
| Multi-tenant Authorization | 흐름 단위 권한 분리 | ○ |

### Extensible Architecture

| 기능 | 설명 | 범위 |
|---|---|---|
| Extension | 프로세서·컨트롤러 서비스·리포팅 태스크 확장 | ○ |
| Classloader Isolation | 확장 간 의존성 충돌 격리 | ○ |
| Site-to-Site Communication Protocol | NiFi 인스턴스 간 전용 전송 프로토콜 | ● |

### Flexible Scaling Model

| 기능 | 설명 | 범위 |
|---|---|---|
| Scale-out (Clustering) | 노드 추가를 통한 수평 확장 | ○ |
| Scale-up & down | 단일 노드 내 동시성 조정 | ○ |

### CFM 배포판이 추가로 제공하는 것

| 기능 | 설명 | 범위 |
|---|---|---|
| NiFi Registry | 흐름 정의 버전 관리와 환경 간 승격 | ○ |
| Cloudera Manager 통합 | 설치·설정·모니터링 일원화 | ○ |
| 사전 제공 프로세서 | 커넥티비티·변환·라우팅용 프로세서 다수 기본 제공 | ● |

> **표기 확인 필요** 저장소의 다이어그램과 `architecture.md` 는 "400+ 프로세서"로
> 표기하고 있으나, 확인한 Cloudera 문서 중에는 "300+ processors"로 기술된 페이지가
> 있습니다. 반입 버전의 [Components Reference Guide](https://docs.cloudera.com/cfm/2.1.6/nifi-components/docs/nifi-docs/html/overview.html)
> 로 실제 수치를 확정한 뒤 표기를 맞추는 것을 권장합니다.

---

## Cloudera CDP — Streams Messaging

문서: [Streams Messaging Documentation](https://docs.cloudera.com/cdp-private-cloud-base/latest/howto-streaming.html) ·
[Introduction to Streams Messaging Manager](https://docs.cloudera.com/runtime/7.2.18/smm-overview/topics/smm-overview.html)

CDP Runtime 의 스트리밍 구성요소는 다섯 가지입니다.

| 구성요소 | 역할 | 범위 |
|---|---|---|
| Apache Kafka | 이벤트 스트리밍 백본 | ● |
| Streams Messaging Manager (SMM) | Kafka 및 연관 서비스의 모니터링·관리 | ● |
| Streams Replication Manager (SRM) | 클러스터 간 Kafka 토픽 복제 | － |
| Schema Registry | 스키마 등록·버전 관리 | ○ |
| Cruise Control | Kafka 부하 분산(리밸런싱) 워크플로 | ○ |

다이어그램에는 Kafka, SMM, ZooKeeper Ensemble 만 표기했습니다. Schema Registry 와
Cruise Control 은 표기하지 않았으나 운영 구성에서는 함께 검토할 대상입니다.

### Streams Messaging Manager 주요 기능

| 기능 | 설명 | 범위 |
|---|---|---|
| End-to-end visibility | 프로듀서 → 토픽 → 컨슈머 전 구간 흐름 가시화 | ● |
| Intelligence-based filtering | 프로듀서·브로커·토픽·컨슈머 중 하나를 선택하면 연관 엔티티만 표시 | ● |
| Consumer lag 관제 | 컨슈머별 LAG 지표로 지연 컨슈머 식별 | ● |
| Data flow / lineage 시각화 | Atlas 연동으로 multi-hop 계보 추적 | ○ |
| REST endpoints | 전 기능에 대한 REST 제공, APM·티켓 시스템 연동 | ○ |
| Kafka Connect 관리 | Kafka Connect 커넥터 관리·모니터링 | － |
| Ranger 연동 | 토픽 단위 접근 통제 | ○ |

CFM 과 CDE 가 서로 다른 컨슈머 그룹으로 붙는 구성이므로, **Consumer lag 관제**와
**Intelligence-based filtering** 이 이 아키텍처에서 실질적으로 가장 자주 쓰이는
기능입니다.

---

## MinIO AIStor

문서: [MinIO AIStor Documentation](https://docs.min.io/aistor/) ·
[Core Concepts](https://docs.min.io/aistor/operations/core-concepts/) ·
[Objects and Versioning](https://docs.min.io/aistor/administration/objects-and-versioning/) ·
[Product — AIStor](https://www.min.io/product/aistor)

### 인터페이스

문서상 AIStor 는 오브젝트는 S3 API, 테이블은 Iceberg, 파일은 SFTP 로 접근하는 단일
저장소로 기술됩니다.

| 인터페이스 | 설명 | 범위 |
|---|---|---|
| S3 API | 별도 메타데이터 DB 없이 동작하는 네이티브 S3 호환 | ● |
| S3 Express | 저지연 워크로드용 S3 프로토콜 변형 | － |
| Iceberg Catalog interface | Iceberg 테이블 네이티브 지원 (AIStor Tables) | ○ |
| SFTP / FTP / FTPS | 게이트웨이 없이 동일 버킷을 파일 클라이언트에 노출 | － |
| MCP | Model Context Protocol 연동 | － |
| OpenSharing | Delta Sharing 프로토콜 지원 | － |

> **설계 검토 사항** 이 아키텍처는 Iceberg REST Catalog 를 별도 컴포넌트로 두고
> 있습니다. AIStor 가 자체 Iceberg Catalog 인터페이스(AIStor Tables)를 제공하므로,
> Nessie·Polaris 등 별도 구현체와 그 PostgreSQL 의존성을 대체할 수 있는지 검토할
> 여지가 있습니다.

### 데이터 보호

| 기능 | 설명 | 범위 |
|---|---|---|
| Erasure Coding | 분산 패리티 기반 데이터 보호 | ○ |
| Healing | 장애 발생 시 자동 복구 | ○ |
| Object Versioning | 오브젝트 버전 관리 | ○ |
| Object Locking / Immutability (WORM) | 버전 오브젝트의 삭제 방지, 규제 대응 | ○ |
| Bucket Replication | active-passive · active-active 복제 | ○ |
| Server-Side Encryption (MinIO KMS / KES) | 저장 시 암호화와 키 관리 | ○ |

WORM 은 금융권 보존기한 관리에 직접 대응하는 기능입니다. 다이어그램의 `docs/raw/`
(원본 PDF·이미지, 불변, 보존기한 관리) 존이 이 기능의 적용 대상입니다.

### 접근 제어와 운영

| 기능 | 설명 | 범위 |
|---|---|---|
| Identity and Access Management | LDAP, OpenID Connect, Azure AD, Okta, Keycloak 연동과 정책 기반 통제 | ● |
| Object Lifecycle Management | 자동 만료(expiration)와 계층화(tiering) | ○ |
| Bucket Notifications | 오브젝트 이벤트 알림 | － |
| Observability | 메트릭 수집, 감사 로그, OpenTelemetry 트레이싱 | ○ |
| Multi-tenancy | 테넌트 격리 | ○ |
| RDMA Acceleration | RDMA 기반 전송 가속 | － |

**IAM 을 ●로 표기한 이유**는 Layer 7 이 Trino 를 우회해 S3 로 직접 접근하는 경로
때문입니다. 이 경로에는 Starburst 의 마스킹이 적용되지 않으므로, MinIO IAM 정책이
유일한 통제 수단이 됩니다.

### 함께 제공되는 도구

| 도구 | 설명 | 범위 |
|---|---|---|
| MinIO KMS | 저장 시 암호화를 위한 키 관리 서버 | ○ |
| MinIO DirectPV | 직접 연결 스토리지용 Kubernetes CSI 드라이버 | ○ |
| MinIO Warp | S3 호환 벤치마킹 도구 (처리량·지연 측정) | ○ |
| MinIO Sidekick | 분산 HTTP 서비스용 클라이언트 사이드 로드밸런서 | － |

> **용량 산정 참고** 문서는 단일 서버 풀 구성의 최소 요건을 동일 사양 호스트 8대로
> 기술합니다. 폐쇄망 초기 도입 규모를 잡을 때 확인이 필요한 값입니다.

---

## Cloudera CDE (Data Engineering)

문서: [Cloudera Data Engineering service](https://docs.cloudera.com/data-engineering/cloud/overview/topics/cde-service-overview.html) ·
[Orchestrating workflows and pipelines](https://docs.cloudera.com/data-engineering/cloud/orchestrate-workflows/cde-orchestrate-workflows.pdf) ·
[Iceberg library dependencies for Spark applications](https://docs.cloudera.com/data-engineering/1.5.0/manage-jobs/topics/cde-iceberg-library-dependency.html)

### 핵심 개념

문서에서 정의하는 구성 단위입니다.

| 개념 | 정의 (문서 표현) | 범위 |
|---|---|---|
| Virtual Cluster | CPU·메모리 범위가 정의된 개별 오토스케일링 클러스터 | ● |
| Jobs | 설정·리소스와 함께 정의된 애플리케이션 코드 | ● |
| Job run | 개별 작업 실행 | ● |
| Resource | Python 파일, JAR, 의존성 등 참조 파일의 정의된 모음 | ○ |

Virtual Cluster 는 사용자 기반 ACL 로 팀·사업부 단위 격리에 사용할 수 있습니다.

### Spark

| 기능 | 설명 | 범위 |
|---|---|---|
| Spark on Kubernetes | 클러스터 생성·유지 없이 Spark 작업 실행 | ● |
| Job 단위 오토스케일링 | Spark dynamic allocation 기반 | ○ |
| 서비스·Virtual Cluster 오토스케일링 | Apache YuniKorn 기반 리소스 스케줄링 | ○ |
| Iceberg 런타임 기본 포함 | Spark classpath 에 Iceberg 의존성 기본 탑재 | ● |
| Iceberg row-level 연산 | copy-on-write 방식 MERGE / UPDATE / DELETE | ● |
| Iceberg Compaction | Spark Iceberg API 기반 압축 | ● |
| Spark History Server | 작업 실행 이력 조회와 트러블슈팅 | ○ |

### Airflow

| 기능 | 설명 | 범위 |
|---|---|---|
| 내장 Airflow | Virtual Cluster 생성 시 자동 배포, 별도 유지보수 불필요 | ● |
| Airflow 타입 Job | CDE Job 으로서의 Airflow DAG | ● |
| Pipeline Authoring UI | Airflow 숙련도와 무관하게 다단계 파이프라인 작성 | ○ |
| 기본 제공 Operator | CDEOperator, CDWOperator, BashOperator, PythonOperator | ● |
| 커스텀 DAG 배포 | 직접 작성한 Python DAG 배포 | ● |

### 인터페이스

| 기능 | 설명 | 범위 |
|---|---|---|
| Web UI | 작업 생성·관리·모니터링 | ● |
| CDE CLI | 명령행 기반 작업 관리 | ○ |
| Jobs REST API | 작업 생성·실행·파라미터 전달 | ● |

Airflow Job 은 Web UI · CLI · REST API 세 가지 방식으로 생성할 수 있고, 수동 실행 시
설정 파라미터를 넘겨 재정의할 수 있습니다. 다이어그램의 **NiFi 흐름 트리거(REST API)**
와 **Trino DDL/MERGE 실행(JDBC)** 은 커스텀 DAG 로 구현하는 부분입니다.

> **버전 확인 필요** 확인한 문서(Cloud 판)에는 Spark 3.5.1, Airflow 2.9, Iceberg 1.5.2
> 로 기술되어 있습니다. 다만 해당 문서는 AWS·Azure 배포를 전제로 하고 있어, 폐쇄망
> 구성에 해당하는 것은 CDP Private Cloud 의 온프레미스 CDE 입니다. 반입 릴리스의
> 온프레미스 문서로 구성요소 버전을 재확인해야 합니다.

---

## Starburst Enterprise (SEP)

문서: [What is Starburst Enterprise?](https://docs.starburst.io/latest/get-started/starburst-enterprise.html) ·
[Performance, logging, and governance features](https://docs.starburst.io/latest/admin.html) ·
[Starburst AI](https://docs.starburst.io/latest/starburst-ai/)

SEP 는 문서상 "Trino 의 상용 배포판(the commercial distribution of Trino)"으로
정의됩니다. 아래는 오픈소스 Trino 대비 SEP 가 제공하는 기능 위주의 목록입니다.

### 커넥터

| 기능 | 설명 | 범위 |
|---|---|---|
| 확장 커넥터 세트 | Trino 커넥터에 더해 다수 커넥터 추가 제공 | ● |
| 커넥터 성능·보안 개선 | 기존 Trino 커넥터의 pushdown·보안 강화 | ● |
| Dynamic filtering | 조인 시 스캔 대상 동적 축소 | ○ |
| 커넥터별 pushdown 매트릭스 | 커넥터별 지원 기능 비교표 제공 | ○ |

이 아키텍처가 사용하는 커넥터는 Iceberg(→MinIO), Kafka, Hive, Oracle 네 가지입니다.

### 보안·접근 제어

| 기능 | 설명 | 범위 |
|---|---|---|
| Built-in access control | SEP 자체 접근 통제 | ● |
| Apache Ranger 연동 | global · catalog · schema · table · column · row 수준 필터링 | ● |
| Kerberos 지원 | credential passthrough 및 캐싱 포함 | ○ |
| LDAP 인증 | 디렉터리 기반 사용자 인증 | ○ |
| Secrets management | 자격증명 보호 | ○ |
| Encrypted internal communication | 클러스터 내부 통신 암호화 | ○ |
| User impersonation | 데이터 소스별 사용자 위임 | ○ |
| Password credential passthrough | 원천으로 자격증명 전달 | ○ |
| Query auditing | 질의 감사 | ● |

**column · row 수준 필터링**은 이 아키텍처에서 특히 중요합니다. Layer 6 을 경유하는
조회에만 적용되고 S3 직접 접근 경로(4 → 7)에는 적용되지 않기 때문에, 두 경로의 통제
수준 차이를 설계 단계에서 명시해야 합니다.

### 성능

| 기능 | 설명 | 범위 |
|---|---|---|
| Cost-based optimizer | Trino CBO 포함 | ○ |
| Starburst Warp Speed | 자동 인덱싱·캐싱 기반 가속 | ○ |
| Starburst Cached Views | 캐시된 뷰 (구 materialized view) | ○ |
| Table scan redirection | 스캔 대상을 캐시 테이블로 전환 | ○ |
| Cache service / Cache service CLI | 캐시 관리 서비스와 명령행 도구 | ○ |
| Fault-tolerant execution | 작업 실패 시 재시도 기반 장기 질의 보호 | ○ |
| Resource groups | 동시 실행 질의 수·자원 상한 통제 | ● |
| Session property managers | 세션 속성 자동 적용 | ○ |
| Workload management | 워크로드 단위 관리 | ○ |
| Distributed sort · Spill to disk · CTE reuse | 대형 질의 처리 보조 | ○ |
| Graceful shutdown | 워커 무중단 축소 | ○ |

**Resource groups** 를 ●로 표기한 것은 원천 직접 페더레이션(1 → 6) 경로 때문입니다.
원천에 부하가 직접 전달되므로 동시 실행 질의 수와 스캔 행 수 제한이 필수입니다.

### 운영·거버넌스

| 기능 | 설명 | 범위 |
|---|---|---|
| Starburst Enterprise 웹 UI | 전용 관리 화면 | ● |
| Starburst Insights | 클러스터 메트릭 대시보드 | ● |
| High availability · autoscaling | Coordinator HA, 워커 오토스케일 | ● |
| Data products | 데이터 상품 정의·게시 | ○ |
| Apache Atlas 연동 | Starburst Atlas plugin, Atlas CLI, Ranger TagSync and Atlas | ○ |
| Backend service | 부가 기능용 백엔드 | ○ |
| Monitoring with JMX · OpenMetrics | 메트릭 노출 | ○ |
| Observability with OpenTelemetry | 분산 트레이싱 | ○ |
| Starburst Admin | 배포 자동화 도구 | ○ |

### AI 기능

| 기능 | 설명 | 범위 |
|---|---|---|
| Starburst AI Agent | 자연어 질문을 SQL 로 변환·실행하는 대화형 에이전트 | ● |
| AI Data Assistant (AIDA) | 분석 보조 어시스턴트 | ● |
| Starburst MCP server | 인증된 stateless HTTP 엔드포인트. 읽기 전용 질의 도구, 데이터 상품 검색·상세 조회 도구 제공 | ● |
| AI functions | embedding · prompt · task(감성 분석, 분류) 함수 | ● |
| Data product AI agent-based enrichment | 에이전트 기반 데이터 상품 보강 | ○ |
| Guardrails | AI 기능 안전장치 | ○ |

> **폐쇄망 지원 — 확인 완료** 모델 통합 방식은 Amazon Bedrock, **OpenAI & OpenAI API
> Compatible**, Google Gemini Enterprise Agent Platform 세 가지이며, 문서는 "compatible
> APIs from these supported providers, whether these external models are deployed
> **on-premises** or in the cloud" 로 온프레미스 배포를 명시합니다. 사내 모델을 쓰려면
> 제공자로 OpenAI 를 선택하고 엔드포인트 URL 에 사내 주소를 입력하며, 해당 엔드포인트가
> 요구하지 않으면 API 키는 생략할 수 있습니다. Cloudera AI Inference Service 가 OpenAI
> 호환 엔드포인트를 제공하므로 전 구간이 내부에서 닫힙니다.
>
> 다만 `ai.agent.allowed-models-regex` 의 기본값이 검증된 모델군만 허용하므로, 고객 보유
> 모델이 패턴에 걸리지 않으면 정규식을 직접 지정해야 하고 이 경우 Starburst 가 검증하지
> 않은 모델이 됩니다. 연동은 되지만 **품질은 실측이 필요**합니다. 상세는
> [agent-readiness-analysis.md](agent-readiness-analysis.md) 를 참고하십시오.

---

## Spotfire

문서: [Spotfire Documentation](https://www.spotfire.com/learn-connect/docs) ·
[Spotfire Data Access](https://community.spotfire.com/articles/spotfire/spotfire-data-access/) ·
[Hybrid in-database/in-memory aggregations](https://community.spotfire.com/articles/spotfire/spotfire-primer-blog-2-hybrid-in-database-in-memory-aggregations/) ·
[What's New in Spotfire](https://community.spotfire.com/articles/spotfire/what-s-new-in-spotfire/)

| 기능 | 설명 | 범위 |
|---|---|---|
| Interactive visualizations | 대화형 시각화 기반 분석 | ● |
| In-database (live query) | 데이터를 원천에 둔 채 커넥터로 직접 질의 | ● |
| Hybrid in-database / in-memory | DB 에서 원시 합계를 가져와 메모리에서 추가 지표 계산 | ● |
| On-demand data | 사용자 상호작용에 따라 필요한 구간만 적재 | ○ |
| Spotfire Connectors | 다양한 데이터 소스에 대한 셀프서비스 연결 | ● |
| Data wrangling | 분석 전 데이터 정리·가공 | ○ |
| Predictive analytics | 예측 분석 기능 내장 | ○ |
| Python data functions | Spotfire 10.7 이상 네이티브 지원, 인터프리터 번들 | ○ |
| Spotfire Service for R | 자체 R 환경 연동, 오픈소스 R 패키지 활용 | ○ |
| Spotfire Mods | 커스텀 시각화 유형을 만드는 경량 프레임워크 | ○ |
| 외부 스크립트 파일 임포트 | VS Code, RStudio, Jupyter 등에서 작성한 R·Python 스크립트 반입 | ○ |

이 아키텍처에서 결정적인 것은 **In-database (live query)** 입니다. Trino 를 In-DB 모드로
질의하면 데이터 사본이 BI 계층에 남지 않으므로, Starburst 의 행·열 수준 마스킹과 감사가
그대로 적용됩니다. 반대로 데이터를 Spotfire 로 가져오는 in-memory 방식은 통제 경계가
BI 계층으로 넘어가므로 금융권 구성에서는 신중히 결정해야 합니다.

> **출처 관련 참고** 확인 시점에 `docs.spotfire.com` 에 접근할 수 없어, 이 절은
> spotfire.com 제품 문서 포털과 Spotfire Community 문서를 근거로 작성했습니다. 제품
> 구성요소(Analyst · Server · Web Player 등)의 정확한 에디션별 기능 경계는 공식 제품
> 문서로 재확인이 필요합니다.

---

## Cloudera AI

문서: [Cloudera AI overview](https://docs.cloudera.com/machine-learning/cloud/product/topics/ml-product-overview.html) ·
[Agent Studio Overview](https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-agent-studio-overview.html) ·
[Using Cloudera AI Inference service](https://docs.cloudera.com/machine-learning/cloud/ai-inference/ml-ai-inference.pdf)

### AI Workbench

| 기능 | 설명 (문서 표현) | 범위 |
|---|---|---|
| Sessions | Workbench 전반의 CPU·메모리·GPU 자원을 직접 활용, 데이터 레이크에 직접 연결 | ● |
| Experiments | 학습 워크로드의 여러 변형을 실행하고 결과를 추적 | ○ |
| Models | 클릭 몇 번으로 배포, HA 방식의 REST 엔드포인트로 서빙 | ● |
| Jobs | 모델 드리프트 모니터링을 포함한 종단간 파이프라인 오케스트레이션 | ○ |
| Applications | Flask, Streamlit 등으로 현업용 대화형 화면 제공 | ○ |
| Model Governance | 배포 모델을 Cloudera Data Catalog 에 추적, 모델-데이터 계보 관리 | ○ |
| 격리·컨테이너화 워크로드 | Python · R · Spark-on-Kubernetes 를 격리 실행, 분산 의존성 관리 | ● |

**Sessions 와 격리 워크로드**를 ●로 표기한 것은 다이어그램의 S3 직접 접근 경로
(4 → 7) 때문입니다. 학습 데이터를 Trino 를 거치지 않고 MinIO 에서 직접 읽는 소비가
여기에 해당합니다.

### Cloudera AI Inference Service

| 기능 | 설명 | 범위 |
|---|---|---|
| 프로덕션 서빙 환경 | 예측형·생성형 AI 모델의 운영 서빙 | ● |
| 고가용성 · 확장성 | HA, 성능, 내결함성, 확장성 대응 | ○ |
| Hugging Face 모델 배포 | 배포 시 text generation · embedding · reranking 등 task 선택 | ○ |

이 아키텍처에서 Inference Service 는 Layer 7 의 소비자 역할에 더해, **Layer 6 Starburst
AI 기능의 내부 모델 공급자 후보**이기도 합니다. 위 Starburst 절의 model provider 확인
사항과 함께 검토해야 합니다.

### AI Studio (Agent Studio)

| 기능 | 설명 | 범위 |
|---|---|---|
| 로우코드 에이전트 작성 | 에이전트 생성, 작업 할당, 커스텀 AI 도구 결합 | ● |
| 워크플로 구성 | 다단계 자동화 워크플로로 조합 | ○ |
| 하이코드 전환 | Workbench 에서 에이전트·도구를 직접 구현 | ○ |
| 라이프사이클 관리 | 프로덕션 에이전트 워크플로의 전 주기 관리 | ○ |
| 내장 관측·로깅 | 모니터링과 트러블슈팅용 observability, logging | ○ |

---

## 확인 과정에서 드러난 검토 항목

문서 대조 중 이 저장소의 설계와 맞춰볼 필요가 있는 항목을 모았습니다.

| # | 항목 | 내용 |
|---|---|---|
| 1 | CFM 프로세서 수 표기 | 저장소는 "400+", 확인한 Cloudera 문서 일부는 "300+". 반입 버전 기준으로 확정 필요 |
| 2 | Starburst AI 의 model provider | **해소됨.** OpenAI 호환 엔드포인트로 온프레미스 모델 사용 가능. 남은 확인 사항은 `ai.agent.allowed-models-regex` 기본 허용 목록과 고객 보유 모델의 품질 실측 |
| 3 | Iceberg Catalog 이중화 | AIStor 가 Iceberg Catalog 인터페이스를 제공. 별도 REST Catalog 구현체와 그 PostgreSQL 의존성을 대체할 수 있는지 검토 |
| 4 | CDE 버전 근거 | 확인한 버전 정보가 Cloud 판 문서 기준. 온프레미스 CDE 문서로 재확인 필요 |
| 5 | MinIO 최소 구성 | 단일 서버 풀 최소 요건이 동일 사양 호스트 8대. 초기 도입 규모 산정에 반영 |
| 6 | 미표기 CDP 구성요소 | Schema Registry, Cruise Control 은 다이어그램에 없으나 운영 구성에서 검토 대상 |

---

## 출처

확인 시점: 2026-08

**Cloudera CFM**
- https://docs.cloudera.com/cfm/2.1.5/flow-management-overview/index.html
- https://docs-archive.cloudera.com/cfm/2.0.1/nifi-overview/topics/nifi-features.html
- https://docs.cloudera.com/cdf-datahub/7.3.1/flow-management-overview/topics/cfm-what-is-apache-nifi.html
- https://docs.cloudera.com/cfm/2.1.6/nifi-components/docs/nifi-docs/html/overview.html

**Cloudera CDP — Streams Messaging**
- https://docs.cloudera.com/cdp-private-cloud-base/latest/howto-streaming.html
- https://docs.cloudera.com/runtime/7.2.18/smm-overview/topics/smm-overview.html

**MinIO AIStor**
- https://docs.min.io/aistor/
- https://docs.min.io/aistor/operations/core-concepts/
- https://docs.min.io/aistor/administration/objects-and-versioning/
- https://www.min.io/product/aistor

**Cloudera CDE**
- https://docs.cloudera.com/data-engineering/cloud/overview/topics/cde-service-overview.html
- https://docs.cloudera.com/data-engineering/cloud/orchestrate-workflows/cde-orchestrate-workflows.pdf
- https://docs.cloudera.com/data-engineering/1.5.0/manage-jobs/topics/cde-iceberg-library-dependency.html

**Starburst Enterprise**
- https://docs.starburst.io/latest/get-started/starburst-enterprise.html
- https://docs.starburst.io/latest/admin.html
- https://docs.starburst.io/latest/starburst-ai/
- https://docs.starburst.io/latest/starburst-ai/mcp-server.html
- https://docs.starburst.io/latest/starburst-ai/starburst-agent-ai.html

**Spotfire**
- https://www.spotfire.com/learn-connect/docs
- https://community.spotfire.com/articles/spotfire/spotfire-data-access/
- https://community.spotfire.com/articles/spotfire/spotfire-primer-blog-2-hybrid-in-database-in-memory-aggregations/
- https://community.spotfire.com/articles/spotfire/what-s-new-in-spotfire/

**Cloudera AI**
- https://docs.cloudera.com/machine-learning/cloud/product/topics/ml-product-overview.html
- https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-agent-studio-overview.html
- https://docs.cloudera.com/machine-learning/cloud/ai-inference/ml-ai-inference.pdf

---

## 용어집

이 문서에 등장하는 기능명과 용어입니다. 아키텍처 전반의 용어는
[architecture.md](architecture.md)의 용어집을 참고하십시오.

### 공통

| 용어 | 설명 |
|---|---|
| 폐쇄망 (air-gapped) | 외부 인터넷과 분리된 망. 외부 SaaS 호출과 온라인 패키지 설치가 불가합니다 |
| 오케스트레이션 | 여러 작업의 실행 순서·의존성·일정을 관리하는 것 |
| 커넥터 | 특정 데이터 소스에 접속하기 위한 플러그인 |
| pushdown | 필터·집계 연산을 원천 시스템에 위임해 전송량을 줄이는 최적화 |
| 오토스케일링 | 부하에 따라 자원을 자동으로 늘리고 줄이는 것 |
| 관측(observability) | 메트릭·로그·트레이스로 시스템 내부 상태를 파악하는 것 |
| OpenTelemetry | 메트릭·로그·트레이스 수집의 벤더 중립 표준 |
| 계보(lineage) | 데이터가 어디서 와서 어디로 갔는지의 이력 |
| REST API | HTTP 기반으로 기능을 외부에 노출하는 인터페이스 |
| CLI | Command Line Interface. 명령행 도구 |

### Cloudera CFM (NiFi)

| 용어 | 설명 |
|---|---|
| Guaranteed Delivery | write-ahead log와 content repository로 전달을 보증하는 방식 |
| Back Pressure / Pressure Release | 큐 적체 시 상류 유입을 억제하고, 임계를 넘은 데이터를 해제하는 흐름 제어 |
| Prioritized Queuing | 큐 안에서 처리 순서를 지정하는 기능 |
| Flow Specific QoS | 흐름 구간별로 지연 대 처리량, 손실 허용도를 다르게 설정하는 것 |
| Visual Command and Control | 동작 중인 흐름을 GUI에서 변경·중단·재구성하는 기능 |
| Flow Templates | 흐름 구성을 템플릿으로 저장해 재사용하는 기능 |
| Data Provenance | 데이터의 출처·변형·전달 이력을 건 단위로 기록하는 기능 |
| Multi-tenant Authorization | 흐름 단위로 사용자·팀 권한을 분리하는 인가 방식 |
| Classloader Isolation | 확장 간 라이브러리 의존성 충돌을 격리하는 구조 |
| Site-to-Site | NiFi 인스턴스 간 전용 전송 프로토콜 |
| NiFi Registry | 흐름 정의를 버전 관리하고 환경 간 승격하는 구성요소 |
| 프로세서 | 수집·변환·라우팅 등 하나의 처리 동작을 담당하는 구성 단위 |
| 2-way SSL | 서버와 클라이언트가 서로 인증서를 검증하는 상호 인증 방식 |

### Cloudera CDP (Streams Messaging)

| 용어 | 설명 |
|---|---|
| Streams Replication Manager (SRM) | Kafka 클러스터 간 토픽을 복제하는 구성요소 |
| Schema Registry | 메시지 스키마를 등록·버전 관리해 생산자와 소비자의 호환성을 유지하는 저장소 |
| Cruise Control | Kafka 파티션 배치를 재조정해 브로커 간 부하를 분산하는 도구 |
| Kafka Connect | 코드 없이 외부 시스템과 Kafka를 연결하는 커넥터 프레임워크 |
| Intelligence-based filtering | 프로듀서·브로커·토픽·컨슈머 중 하나를 선택하면 연관 엔티티만 표시하는 SMM 기능 |
| Consumer lag | 컨슈머가 최신 메시지보다 뒤처진 메시지 수 |
| Apache Atlas | 하둡 생태계의 메타데이터·계보 관리 도구 |
| Apache Ranger | 하둡 생태계의 중앙 집중 접근 통제 도구 |

### MinIO AIStor

| 용어 | 설명 |
|---|---|
| S3 API | AWS S3의 오브젝트 접근 규격. AIStor가 네이티브로 제공합니다 |
| S3 Express | 저지연 워크로드를 위한 S3 프로토콜 변형 |
| AIStor Tables | Iceberg 테이블을 네이티브로 지원하는 AIStor 기능 |
| OpenSharing | Delta Sharing 프로토콜 기반의 데이터 공유 기능 |
| Erasure Coding | 데이터를 조각과 패리티로 분산 저장해 일부 디스크 장애를 견디는 보호 방식 |
| Healing | 장애가 발생한 데이터 조각을 자동으로 복구하는 동작 |
| Object Versioning | 같은 키의 오브젝트를 버전별로 보관하는 기능 |
| Object Locking / WORM | 지정 기간 동안 오브젝트의 변경·삭제를 금지하는 보존 기능 |
| Bucket Replication | 버킷 단위 복제. active-passive는 단방향, active-active는 양방향입니다 |
| Server-Side Encryption (SSE) | 저장 시점에 서버가 데이터를 암호화하는 방식 |
| KMS · KES | 암호화 키를 관리하는 서버와, MinIO의 키 관리 연동 서비스 |
| OpenID Connect (OIDC) | OAuth 2.0 기반의 표준 인증 프로토콜 |
| Lifecycle Management | 오브젝트를 자동 만료시키거나 다른 저장 계층으로 이동시키는 정책 |
| Tiering | 접근 빈도가 낮은 데이터를 저렴한 저장 계층으로 옮기는 것 |
| Bucket Notifications | 오브젝트 생성·삭제 등의 이벤트를 외부에 알리는 기능 |
| RDMA | Remote Direct Memory Access. CPU를 거치지 않는 고속 네트워크 전송 |
| DirectPV | 직접 연결 스토리지를 다루는 Kubernetes CSI 드라이버 |
| CSI | Container Storage Interface. Kubernetes의 스토리지 연동 표준 |
| Warp · Sidekick | S3 벤치마킹 도구와, 클라이언트 측 로드밸런서 |
| 서버 풀 | AIStor에서 하나의 저장소를 이루는 호스트 묶음 단위 |
| 멀티테넌시 | 하나의 시스템을 여러 조직이 격리된 상태로 나눠 쓰는 구성 |

### Cloudera CDE

| 용어 | 설명 |
|---|---|
| Virtual Cluster | CPU·메모리 범위가 정의된 개별 오토스케일링 클러스터 |
| Job · Job run | 설정·리소스를 포함한 애플리케이션 코드와, 그 개별 실행 |
| Resource | Python 파일, JAR, 의존성 등 작업이 참조하는 파일 모음 |
| ACL | Access Control List. 사용자·그룹별 접근 권한 목록 |
| Apache YuniKorn | Kubernetes용 자원 스케줄러. 서비스·클러스터 단위 오토스케일링에 사용됩니다 |
| Spark dynamic allocation | 작업 부하에 따라 Executor 수를 늘리고 줄이는 Spark 기능 |
| copy-on-write | 변경 시 해당 데이터 파일을 새로 쓰는 방식. 조회는 빠르고 쓰기는 무겁습니다 |
| Spark History Server | 완료된 Spark 작업의 실행 이력을 조회하는 도구 |
| DAG | 작업 의존 관계를 순환 없이 표현한 그래프. Airflow 파이프라인의 정의 단위 |
| Operator | Airflow에서 하나의 작업 유형을 수행하는 구성 단위 |
| CDEOperator · CDWOperator | 각각 CDE의 Spark 작업, CDW의 Hive 작업을 실행하는 Airflow Operator |

### Starburst Enterprise

| 용어 | 설명 |
|---|---|
| Trino | 여러 데이터 소스를 대상으로 하는 분산 SQL 질의 엔진. SEP는 그 상용 배포판입니다 |
| Dynamic filtering | 조인 상대의 값을 이용해 스캔 대상을 실행 중에 줄이는 최적화 |
| Cost-based optimizer (CBO) | 통계를 근거로 실행 계획을 선택하는 최적화기 |
| Starburst Warp Speed | 자동 인덱싱·캐싱으로 조회를 가속하는 기능 |
| Starburst Cached Views | 질의 결과를 미리 계산해 캐시해 두는 뷰 |
| Table scan redirection | 원본 테이블 대신 캐시된 테이블을 읽도록 전환하는 기능 |
| Fault-tolerant execution | 작업 실패 시 재시도로 장기 질의를 완주시키는 실행 방식 |
| Resource groups | 동시 실행 질의 수와 자원 상한을 통제하는 단위 |
| Session property managers | 세션 속성을 규칙에 따라 자동 적용하는 기능 |
| Spill to disk | 메모리가 부족할 때 중간 결과를 디스크로 내보내는 처리 |
| CTE reuse | 공통 테이블 식(WITH 절)의 결과를 재사용해 중복 연산을 없애는 최적화 |
| Distributed sort | 여러 워커에 나눠 수행하는 정렬 |
| Graceful shutdown | 처리 중인 질의를 마친 뒤 워커를 종료해 무중단 축소를 가능하게 하는 기능 |
| Credential passthrough | 최종 사용자의 자격증명을 원천 시스템까지 전달하는 방식 |
| User impersonation | 질의를 요청한 사용자 자격으로 원천에 접근하는 위임 방식 |
| Starburst Insights | 클러스터 메트릭과 질의 이력을 보여주는 대시보드 |
| Data products | 목적별로 정의·게시해 재사용하는 데이터 묶음 |
| JMX | Java Management Extensions. JVM 메트릭 노출 표준 |
| OpenMetrics | 메트릭 노출 형식 표준 |
| Starburst Admin | SEP 배포·운영을 자동화하는 도구 |
| AI Data Assistant (AIDA) | 분석을 보조하는 Starburst의 AI 어시스턴트 |
| Starburst AI Agent | 자연어 질문을 SQL로 변환·실행하는 대화형 에이전트 |
| MCP server | AI 에이전트가 인증된 상태로 클러스터에 질의하도록 노출하는 엔드포인트 |
| AI functions | SQL에서 호출하는 임베딩·프롬프트·분류 등의 AI 함수 |
| model provider | AI 기능이 호출하는 추론 모델 공급자. 폐쇄망에서는 내부 엔드포인트 지원 여부가 관건입니다 |
| Guardrails | AI 기능의 오·남용을 막는 안전장치 |

### Spotfire

| 용어 | 설명 |
|---|---|
| In-database (live query) | 데이터를 가져오지 않고 원천에 직접 질의해 결과만 받는 방식 |
| In-memory | 데이터를 Spotfire로 가져와 메모리에서 연산하는 방식 |
| Hybrid in-database / in-memory | DB에서 원시 합계를 받아 메모리에서 추가 지표를 계산하는 혼합 방식 |
| On-demand data | 사용자 상호작용에 따라 필요한 구간만 그때그때 적재하는 기능 |
| Data wrangling | 분석 전에 데이터를 정리·변형·결합하는 작업 |
| Data functions | Python·R 스크립트로 새 컬럼이나 테이블을 계산하는 확장 기능 |
| Spotfire Service for R | 자체 R 환경을 연결해 오픈소스 R 패키지를 활용하는 구성요소 |
| Spotfire Mods | 커스텀 시각화 유형을 만드는 경량 프레임워크 |
| Ad-hoc 분석 | 사전 정의된 보고서 없이 즉석 질문에 따라 수행하는 분석 |

### Cloudera AI

| 용어 | 설명 |
|---|---|
| AI Workbench | 학습·개발 작업을 수행하는 Cloudera AI의 작업 환경 |
| Sessions | Workbench의 CPU·메모리·GPU를 직접 사용하는 대화형 작업 단위 |
| Experiments | 학습 워크로드의 여러 변형을 실행하고 결과를 추적하는 기능 |
| Models | 배포되어 REST 엔드포인트로 서빙되는 모델 |
| Jobs | 학습·평가 등 파이프라인을 자동 실행하는 작업 단위 |
| Applications | Flask·Streamlit 등으로 만든 현업용 대화형 화면 |
| Model Governance | 배포 모델을 카탈로그에 등록하고 모델-데이터 계보를 관리하는 것 |
| 모델 드리프트 | 시간이 지나며 입력 분포가 변해 모델 성능이 저하되는 현상 |
| Cloudera AI Inference Service | 예측형·생성형 모델을 운영 수준으로 서빙하는 환경 |
| Agent Studio | 로우코드로 AI 에이전트와 도구를 구성하는 스튜디오 |
| Hugging Face | 오픈소스 모델을 공유·배포하는 플랫폼 |
| text generation · embedding · reranking | 각각 텍스트 생성, 벡터 변환, 검색 결과 재정렬 작업 유형 |
| 로우코드 · 하이코드 | 최소한의 코드로 구성하는 방식과, 직접 코드로 구현하는 방식 |
| GPU | 대규모 병렬 연산에 쓰이는 프로세서. 모델 학습·추론의 핵심 자원 |
