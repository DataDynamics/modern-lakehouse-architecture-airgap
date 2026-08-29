# 제안 아키텍처의 특징

이 참조 아키텍처가 각 계층에서 해당 제품을 선택한 이유를 정리한 문서입니다. 제안 설명과
기술 검토 자리에서 근거로 사용하는 것을 전제로 했습니다.

구성은 [architecture.md](architecture.md), 제품별 역할은 [solutions.md](solutions.md),
기능 목록은 [solution-features.md](solution-features.md), 배포 방식은
[solution-runtimes.md](solution-runtimes.md)를 참고하십시오.

> **근거 표기 원칙** 각 절의 주장은 공식 문서로 확인한 내용을 근거로 합니다. 벤더가
> 자사 자료에서 제시한 수치는 **벤더 자료**로 구분해 표기했습니다. 중립 벤치마크가
> 아니므로 고객 환경에서의 검증이 별도로 필요합니다.

## 목차

- [한눈에 보기](#한눈에-보기)
- [1. HDFS 대신 MinIO를 스토리지로 두는 이유](#1-hdfs-대신-minio를-스토리지로-두는-이유)
  - [스토리지와 컴퓨트를 따로 늘릴 수 있습니다](#스토리지와-컴퓨트를-따로-늘릴-수-있습니다)
  - [저장 효율이 크게 다릅니다](#저장-효율이-크게-다릅니다)
  - [단일 지점이 없습니다](#단일-지점이-없습니다)
  - [S3 호환이 곧 접근성입니다](#s3-호환이-곧-접근성입니다)
  - [AI 워크로드를 같은 저장소에 담습니다](#ai-워크로드를-같은-저장소에-담습니다)
  - [적용 시 유의사항](#적용-시-유의사항)
- [2. Starburst Enterprise + Iceberg가 Hive·Impala보다 강한 이유](#2-starburst-enterprise--iceberg가-hiveimpala보다-강한-이유)
  - [성능 차이는 "스캔"이 아니라 "플래닝"에서 먼저 벌어집니다](#성능-차이는-스캔이-아니라-플래닝에서-먼저-벌어집니다)
  - [Starburst가 그 위에 더하는 것](#starburst가-그-위에-더하는-것)
  - [Impala와 비교했을 때](#impala와-비교했을-때)
  - [적용 시 유의사항](#적용-시-유의사항-1)
- [3. Starburst가 MCP Server와 Model Provider를 지원하는 의미](#3-starburst가-mcp-server와-model-provider를-지원하는-의미)
  - [Federation을 하면 메타데이터가 이미 한곳에 모입니다](#federation을-하면-메타데이터가-이미-한곳에-모입니다)
  - [금융권에서 `parametrizedQuery`가 갖는 값](#금융권에서-parametrizedquery가-갖는-값)
  - [Model Provider — 폐쇄망에서 고객 모델을 그대로 씁니다](#model-provider--폐쇄망에서-고객-모델을-그대로-씁니다)
  - [적용 시 유의사항](#적용-시-유의사항-2)
- [4. 데이터 파이프라인으로서 NiFi의 강점과 확장성](#4-데이터-파이프라인으로서-nifi의-강점과-확장성)
  - [원천의 다양성을 한 계층에서 끝냅니다](#원천의-다양성을-한-계층에서-끝냅니다)
  - [금융권에서 결정적인 것은 Data Provenance입니다](#금융권에서-결정적인-것은-data-provenance입니다)
  - [확장성은 세 방향입니다](#확장성은-세-방향입니다)
  - [역할 경계를 분명히 해두는 편이 좋습니다](#역할-경계를-분명히-해두는-편이-좋습니다)
- [5. Cloudera CDP — Kafka와 SMM의 실시간 처리 강점](#5-cloudera-cdp--kafka와-smm의-실시간-처리-강점)
  - [생산자와 소비자를 시간적으로 분리합니다](#생산자와-소비자를-시간적으로-분리합니다)
  - [운영 가시성이 함께 제공됩니다](#운영-가시성이-함께-제공됩니다)
  - [구성요소가 함께 제공됩니다](#구성요소가-함께-제공됩니다)
  - [실시간 요건은 경로를 나눠 대응합니다](#실시간-요건은-경로를-나눠-대응합니다)
- [6. Cloudera CDE — 배치·스트리밍·AI 전처리의 단일 실행 기반](#6-cloudera-cde--배치스트리밍ai-전처리의-단일-실행-기반)
  - [하나의 기반에서 세 가지 작업이 돕니다](#하나의-기반에서-세-가지-작업이-돕니다)
  - [Airflow가 다른 계층을 직접 구동합니다](#airflow가-다른-계층을-직접-구동합니다)
  - [Iceberg 운영이 기본 제공됩니다](#iceberg-운영이-기본-제공됩니다)
  - [자원 격리와 오토스케일](#자원-격리와-오토스케일)
  - [적용 시 유의사항](#적용-시-유의사항-3)
- [7. Cloudera AI — 폐쇄망에서의 단일 통합 AI 환경](#7-cloudera-ai--폐쇄망에서의-단일-통합-ai-환경)
  - [폐쇄망 AI에서 실제로 어려운 것은 "조합"입니다](#폐쇄망-ai에서-실제로-어려운-것은-조합입니다)
  - [이 아키텍처에서 특히 중요한 두 가지](#이-아키텍처에서-특히-중요한-두-가지)
  - [거버넌스가 함께 옵니다](#거버넌스가-함께-옵니다)
  - [적용 시 유의사항](#적용-시-유의사항-4)
- [종합 — 이 조합이 만드는 것](#종합--이-조합이-만드는-것)
- [제안 시 함께 설명할 사항](#제안-시-함께-설명할-사항)
- [출처](#출처)
- [용어집](#용어집)
  - [스토리지](#스토리지)
  - [테이블 포맷과 조회](#테이블-포맷과-조회)
  - [AI 연동](#ai-연동)
  - [파이프라인과 운영](#파이프라인과-운영)

## 한눈에 보기

| 선택 | 대체하는 것 | 핵심 근거 |
|---|---|---|
| MinIO AIStor | HDFS | 스토리지·컴퓨트 분리, 저장 효율, S3 호환 접근성, AI 워크로드 수용 |
| Starburst Enterprise + Iceberg | Hive, Impala | 메타데이터 기반 플래닝, 카탈로그 통합, 파티션·스키마 진화 |
| Starburst MCP · Model Provider | 개별 연동 | Agent가 쓸 수 있는 단일 데이터 접점, 폐쇄망 모델 연동 |
| Cloudera CFM (NiFi) | 개별 연동 스크립트 | 이력 추적, 흐름 제어, 확장 구조 |
| Cloudera CDP (Kafka·SMM) | 직접 연동 | 생산자·소비자 분리, 종단 가시성 |
| Cloudera CDE | 별도 스케줄러 | 배치·스트리밍·AI 전처리의 단일 실행 기반 |
| Cloudera AI | 개별 도구 조합 | 폐쇄망에서 개발·실험·파인튜닝·RAG·Agent·서빙의 단일 환경 |

---

## 1. HDFS 대신 MinIO를 스토리지로 두는 이유

근거: [Migrating from Hadoop HDFS to Object Storage](https://www.min.io/solutions/hdfs-migration) ·
[Hardware and System Requirements](https://docs.min.io/aistor/reference/aistor-server/requirements/) ·
[MinIO AIStor Documentation](https://docs.min.io/aistor/)

### 스토리지와 컴퓨트를 따로 늘릴 수 있습니다

HDFS는 저장과 연산이 같은 노드에 묶여 있습니다. 데이터가 늘어 저장 공간을 늘리려면
연산 자원까지 함께 늘어나고, 반대로 연산만 필요해도 디스크가 따라옵니다. 오브젝트
스토리지로 분리하면 **필요한 쪽만 증설**합니다.

이 아키텍처에서는 그 효과가 구체적으로 드러납니다. Spark 워크로드가 몰리는 시기에는
CDE 가상 클러스터만 확장하고, 문서 적재가 늘어나는 시기에는 MinIO 서버 풀만 확장합니다.

### 저장 효율이 크게 다릅니다

| 방식 | 10 PB 데이터 저장에 필요한 물리 용량 |
|---|---|
| HDFS 3중 복제 | 30 PB 초과 |
| Erasure Coding | 15 ~ 20 PB |

**벤더 자료** 기준이며, 실제 값은 패리티 설정에 따라 달라집니다. 다만 3중 복제가 원본의
200% 오버헤드를 고정적으로 요구하는 것은 구조적 사실이고, Erasure Coding이 그보다 적은
오버헤드로 동등 이상의 내구성을 얻는 것도 방식 자체의 성질입니다. **금융권처럼 원장·거래
이력을 장기 보존하는 환경에서 이 차이는 도입 규모에 직접 반영됩니다.**

### 단일 지점이 없습니다

HDFS는 NameNode가 전체 파일 메타데이터를 관리하므로, 이 노드가 규모의 상한이자 장애의
집중 지점이 됩니다. MinIO는 중앙 NameNode 없이 분산 구조로 동작하며, AIStor는 별도
메타데이터 데이터베이스 없이 S3 API를 네이티브로 처리합니다.

### S3 호환이 곧 접근성입니다

이 아키텍처에서 저장소에 접근하는 주체는 다섯입니다.

| 주체 | 접근 방식 |
|---|---|
| NiFi (CFM) | S3 프로세서 |
| Spark (CDE) | `s3a://` |
| Trino (Starburst) | Iceberg 커넥터 → S3 |
| Cloudera AI | S3 API 직접 접근 (학습 데이터·문서 원본) |
| AI Agent · 도구 | S3 API |

**모두 같은 규격 하나로 붙습니다.** HDFS였다면 Hadoop 클라이언트에 종속되는 경로가
생기고, 특히 파이썬 기반 AI 도구들은 별도 연동이 필요합니다. S3는 사실상 표준이므로
앞으로 추가될 도구도 같은 방식으로 붙습니다. **엔진을 교체·추가할 때 저장소를 건드리지
않아도 되는 것**이 이 선택의 실질적 이득입니다.

### AI 워크로드를 같은 저장소에 담습니다

`docs/` 존 하나에 원본 문서, 파싱 결과, 청크, 임베딩을 함께 두고, 정형 데이터와 같은
저장소를 씁니다. 학습 데이터 수천만 건을 읽을 때는 SQL 엔진을 거치지 않고 S3로 직접
접근합니다. AIStor는 오브젝트(S3)·테이블(Iceberg)·파일(SFTP)을 한 저장소에서 제공하고,
RDMA 가속과 멀티테넌시를 지원합니다.

### 적용 시 유의사항

- 드라이브는 **XFS 필수**, 운영 패리티는 **EC:3 이상**, 노드당 물리 코어 8개 이상 권장
- 풀 내 노드의 하드웨어·OS 설정을 동일하게 맞춰야 성능이 안정적입니다
- Trino·Spark·NiFi 모두 `path-style-access=true` 설정이 필요합니다

---

## 2. Starburst Enterprise + Iceberg가 Hive·Impala보다 강한 이유

근거: [Iceberg — Partitioning](https://iceberg.apache.org/docs/latest/partitioning/) ·
[Iceberg — Performance](https://iceberg.apache.org/docs/latest/performance/) ·
[Iceberg connector](https://docs.starburst.io/latest/connector/iceberg.html) ·
[Performance, logging, and governance features](https://docs.starburst.io/latest/admin.html) ·
[Data maintenance](https://docs.starburst.io/latest/data-engineering/data-maintenance.html)

### 성능 차이는 "스캔"이 아니라 "플래닝"에서 먼저 벌어집니다

Hive 테이블은 질의를 계획할 때 디렉터리를 나열해 어떤 파일을 읽을지 정합니다. 파티션과
파일이 늘수록 이 단계가 비싸집니다. Iceberg는 매니페스트에 **파일별 파티션 값과 컬럼
통계**를 들고 있어, 매니페스트 목록의 값 범위로 먼저 매니페스트를 거르고 그다음 데이터
파일을 거릅니다. 그래서 **모든 매니페스트를 읽지 않고도 계획이 끝나며, 플래닝이 단일
노드에서 처리됩니다.**

| 항목 | Hive 테이블 | Iceberg 테이블 |
|---|---|---|
| 스캔 대상 결정 | 디렉터리 나열 | 매니페스트 메타데이터 프루닝 |
| 파티션 지정 | 사용자가 파티션 컬럼을 명시하고 질의에도 필터 추가 | **Hidden partitioning** — 엔진이 자동 변환 |
| 파티션 레이아웃 변경 | 새 테이블 생성 후 질의 재작성 | **파티션 진화**로 기존 테이블에서 변경 |
| 스키마 변경 | 제약이 큼 | 스키마 진화 지원 |
| 시점 조회 | 없음 | 스냅샷 · time-travel |

**Hidden partitioning의 실제 효과**는 금융권에서 특히 큽니다. 사용자가 테이블의 물리
레이아웃을 모른 채 질의해도 파티션 프루닝이 동작합니다. Hive에서는 담당자가
`event_date` 같은 파티션 컬럼을 알고 필터를 넣어야 하고, 모르면 전체를 훑습니다. 이는
NL-to-SQL로 Agent가 질의를 생성하는 구조에서 결정적입니다 — **Agent에게 파티션 컬럼
사용법까지 학습시킬 필요가 없습니다.**

**파티션 진화**도 운영에서 값이 큽니다. 일 단위 파티션을 시간 단위로 바꿔야 할 때, Hive는
테이블을 새로 만들고 이를 참조하는 질의를 전부 고쳐야 합니다. Iceberg는 기존 테이블에서
스킴을 바꿉니다.

### Starburst가 그 위에 더하는 것

| 기능 | 효과 |
|---|---|
| Starburst Warp Speed | 자동 인덱싱·캐싱 기반 가속 |
| Cached Views · 구체화 뷰 | 사전 계산 결과 제공. **정의와 스냅샷 이력에 따라 증분 갱신** |
| Table scan redirection | 원본 대신 캐시 테이블을 읽도록 전환 |
| Dynamic filtering | 조인 상대 값으로 실행 중 스캔 축소 |
| Cost-based optimizer | 통계 기반 실행 계획 선택 |
| Fault-tolerant execution | 장기 질의를 재시도로 완주 |
| Resource groups | 동시 질의·자원 상한 통제 |
| Data maintenance | 데이터 파일 압축, 통계 수집, 만료 스냅샷·고아 파일 정리 |

**Data maintenance가 SQL로 제공된다는 점**을 짚어둘 만합니다. Iceberg 테이블은 방치하면
작은 파일과 스냅샷이 쌓여 성능이 저하되는데, 이 유지관리를 Starburst가 작업으로
수행합니다. Spark 배치로만 처리하던 부분을 조회 계층에서도 다룰 수 있습니다.

### Impala와 비교했을 때

Impala는 빠른 대화형 엔진이지만 하둡 생태계 안에서 동작하며, 이 아키텍처가 요구하는
**이기종 원천 통합 조회**를 담당하지 않습니다. Starburst는 Iceberg·Kafka·Hive·Oracle
커넥터를 **하나의 SQL 네임스페이스로 묶습니다.** 상위 애플리케이션이 저장소별 클라이언트를
각각 연결하지 않아도 되는 것이 이 계층의 존재 이유입니다.

카탈로그가 하나로 통합된다는 것은 **접근 통제도 한 곳에서 걸린다**는 뜻입니다.
행·열 수준 통제와 질의 감사가 원천별로 흩어지지 않습니다.

### 적용 시 유의사항

- Hive Metastore를 제거하고 Iceberg REST Catalog 단일 구성으로 가면, 카탈로그 구현체의
  HA와 백업이 새로운 필수 항목이 됩니다
- 조회 계층을 우회하는 S3 직접 접근 경로에는 Starburst의 마스킹이 적용되지 않습니다

---

## 3. Starburst가 MCP Server와 Model Provider를 지원하는 의미

근거: [Starburst MCP server](https://docs.starburst.io/latest/starburst-ai/mcp-server.html) ·
[Configure Starburst AI](https://docs.starburst.io/latest/starburst-ai/configuration-ai.html) ·
[AI Data Assistant (AIDA)](https://docs.starburst.io/latest/starburst-ai/aida-ai.html) ·
[AI functions](https://docs.starburst.io/latest/starburst-ai/functions-ai.html)

### Federation을 하면 메타데이터가 이미 한곳에 모입니다

Agent에게 데이터를 주려면 먼저 **무엇이 어디에 있는지**를 줘야 합니다. Starburst는
커넥터로 원천에 연결되는 순간 카탈로그·스키마·테이블·컬럼·타입을 확보합니다. 별도
메타데이터 수집 파이프라인을 만들 필요가 없습니다.

**MCP Server는 그 메타데이터를 Agent가 쓸 수 있는 형태로 노출하는 장치입니다.** 이미 갖고
있는 것을 표준 규약으로 내보내는 것이므로, 이 조합은 자연스럽습니다.

| 도구 | 제공 내용 |
|---|---|
| `queryReadOnly` | 읽기 전용 SQL 실행. 컬럼 메타데이터와 결과를 JSON으로 반환 |
| `searchDataProducts` | 데이터 상품을 이름·요약·설명으로 검색 |
| `getDataProductDetails` | 뷰·구체화 뷰의 컬럼, 타입, **설명**, 정의 |
| `listParametrizedQueryTools` · `parametrizedQuery` | 사전 승인된 SQL 템플릿 목록과 실행 |

### 금융권에서 `parametrizedQuery`가 갖는 값

자유 형식 NL-to-SQL을 전면 허용하는 것이 부담스러운 영역에는, **승인된 SQL 템플릿에
파라미터만 채우게** 할 수 있습니다. SQL 주입을 차단하고 조회 범위를 통제하면서도 Agent가
쓸 수 있습니다. 민감도가 높은 영역은 이 방식으로 시작하고 낮은 영역만 자유 질의를 여는
단계적 개방이 가능합니다.

또한 MCP 서버는 모든 요청에 인증을 요구하며 Starburst의 기존 인증 방식을 사용하므로,
**Agent 접근이 기존 권한 체계 밖으로 벗어나지 않습니다.**

### Model Provider — 폐쇄망에서 고객 모델을 그대로 씁니다

Starburst 문서는 모델 통합 방식으로 Amazon Bedrock, **OpenAI 및 OpenAI API 호환**, Google
Gemini를 제시하며, 해당 모델이 **온프레미스에 배포된 경우도 명시적으로 허용**합니다.

```
Starburst AI (OpenAI 호환 제공자로 설정)
   → 사내 OpenAI 호환 엔드포인트 (Cloudera AI Inference Service 등)
      → 고객 보유 모델
```

외부 API 호출 없이 전 구간이 내부에서 닫힙니다. **폐쇄망이라서 AI 기능을 포기해야 하는
구조가 아니라는 점**이 이 아키텍처의 중요한 전제입니다.

여기에 더해 `starburst.ai.generate_embedding()` 같은 AI 함수가 SQL로 제공되므로, 문서
청크가 Iceberg 테이블에 있다면 **SQL 한 문장으로 임베딩 컬럼을 채울 수 있습니다.** 대량
초기 색인은 Spark, 증분 갱신은 SQL로 나누는 구성이 가능합니다.

### 적용 시 유의사항

`ai.agent.allowed-models-regex`의 기본값은 검증된 모델군만 허용합니다. 고객 보유 모델이
패턴에 걸리지 않으면 정규식을 지정해 우회해야 하고, 이 경우 Starburst가 검증하지 않은
모델이 됩니다. **연동은 되지만 NL-to-SQL 품질은 실측이 필요합니다.**

---

## 4. 데이터 파이프라인으로서 NiFi의 강점과 확장성

근거: [High Level Overview of Key NiFi Features](https://docs-archive.cloudera.com/cfm/2.0.1/nifi-overview/topics/nifi-features.html) ·
[What is Apache NiFi](https://docs.cloudera.com/cdf-datahub/7.3.1/flow-management-overview/topics/cfm-what-is-apache-nifi.html) ·
[CFM Operator for Kubernetes](https://docs.cloudera.com/cfm-operator/2.11.0/index.html)

### 원천의 다양성을 한 계층에서 끝냅니다

금융권 원천은 계정계 DB, 카드 전문 로그, 채널 로그, 대외계 전문, 문서까지 성격이 제각각
입니다. 각각을 개별 스크립트로 연동하면 그 수만큼 유지보수 대상이 생깁니다. NiFi는 다수의
프로세서로 DB·파일·MQ·API·스트림을 GUI에서 연결하고, 하류에는 정규화된 형태만 넘깁니다.

### 금융권에서 결정적인 것은 Data Provenance입니다

NiFi의 기능은 문서상 다섯 범주로 정리됩니다.

| 범주 | 대표 기능 |
|---|---|
| Flow Management | Guaranteed Delivery, Back Pressure, Prioritized Queuing, Flow Specific QoS |
| Ease of Use | Visual Command and Control, Flow Templates, **Data Provenance** |
| Security | System to System (2-way SSL), User to System, Multi-tenant Authorization |
| Extensible Architecture | Extension, Classloader Isolation, Site-to-Site |
| Flexible Scaling Model | Scale-out (Clustering), Scale-up & down |

이 중 **Data Provenance**가 다른 도구와의 차이를 만듭니다. 데이터가 어디서 와서 어떻게
변형됐는지를 건 단위로 남기므로, 감독당국 소명과 내부 감사에 그대로 근거 자료가 됩니다.
직접 만든 파이프라인에서 이 수준의 이력을 남기려면 별도 설계와 개발이 필요합니다.

**Back-pressure**도 실무적으로 중요합니다. 하류가 밀릴 때 상류 유입을 억제하므로, 야간
배치가 몰려도 큐가 폭주해 데이터가 유실되는 상황을 구조적으로 막습니다.

### 확장성은 세 방향입니다

| 방향 | 내용 |
|---|---|
| 기능 확장 | 커스텀 프로세서 개발. **Classloader Isolation**으로 확장 간 라이브러리 충돌 격리 |
| 처리량 확장 | 클러스터 노드 추가(scale-out)와 노드 내 동시성 조정(scale-up/down) |
| 배포 확장 | Base 클러스터 parcel 방식, 또는 **CFM Operator로 Kubernetes 배포** |

CFM Operator는 NiFi **1.x와 2.x를 동시에 운영**할 수 있고 NiFi Registry로 흐름을 버전
관리합니다. 흐름 수가 늘고 팀별 격리가 필요해지는 시점에 배포 방식을 바꿀 수 있다는 것이
장기 확장성 측면의 강점입니다.

### 역할 경계를 분명히 해두는 편이 좋습니다

NiFi와 Airflow는 겹쳐 보이지만 **흐름 내부 제어는 NiFi, 테이블 단위 의존성과 SLA는
Airflow**입니다. 이 경계를 초기에 합의하지 않으면 양쪽에 로직이 흩어집니다.

---

## 5. Cloudera CDP — Kafka와 SMM의 실시간 처리 강점

근거: [Streams Messaging Documentation](https://docs.cloudera.com/cdp-private-cloud-base/latest/howto-streaming.html) ·
[Introduction to Streams Messaging Manager](https://docs.cloudera.com/runtime/7.2.18/smm-overview/topics/smm-overview.html)

### 생산자와 소비자를 시간적으로 분리합니다

Kafka를 두는 이유는 단순히 빠르기 때문이 아니라 **원천과 소비자를 떼어놓기 때문**입니다.

- 소비자가 중단돼도 원천은 계속 적재합니다
- 하나의 이벤트를 여러 소비자가 각자의 속도로 읽습니다
- 보관 기간 안에서는 재처리가 가능합니다

이 아키텍처에서 CFM과 CDE가 서로 다른 컨슈머 그룹으로 붙는 구조가 여기에 해당합니다.
장애 복구 시 원천에 다시 요청하지 않고 토픽에서 재소비합니다. **계정계에 재조회 부하를
주지 않는다는 점**이 금융권에서 특히 중요합니다.

### 운영 가시성이 함께 제공됩니다

Kafka 단독 운영의 어려움은 대개 "지금 어디가 밀리는지 모른다"는 데서 옵니다. SMM은 이
부분을 채웁니다.

| 기능 | 내용 |
|---|---|
| End-to-end visibility | 프로듀서 → 토픽 → 컨슈머 전 구간 흐름 가시화 |
| Intelligence-based filtering | 프로듀서·브로커·토픽·컨슈머 중 하나를 고르면 연관 엔티티만 표시 |
| Consumer lag 관제 | 컨슈머별 지연으로 느린 소비자를 식별 |
| Lineage 시각화 | Atlas 연동으로 multi-hop 계보 추적 |
| REST endpoints | 전 기능을 API로 제공해 사내 APM·티켓 시스템과 연동 |

**Consumer lag 관제**가 이 아키텍처의 실질적 운영 지표입니다. CFM과 CDE의 그룹 ID를
분리해 두면 어느 소비 경로가 밀리는지 따로 볼 수 있습니다.

### 구성요소가 함께 제공됩니다

Kafka 외에 Streams Replication Manager(클러스터 간 복제), Schema Registry(스키마 호환성),
Cruise Control(파티션 부하 재분산)이 같은 플랫폼에서 제공됩니다. 개별 오픈소스를 조합해
운영하는 것과 비교하면 **버전 정합성과 지원 창구가 하나**라는 차이가 있습니다.

### 실시간 요건은 경로를 나눠 대응합니다

초 단위 요건이 있는 토픽은 CFM을 거치지 않고 원천에서 Kafka로 직결합니다. 홉이 줄어
지연이 낮아집니다. 검증과 이력 추적이 필요한 나머지는 CFM 경유 경로를 씁니다. **한 가지
경로로 모든 요건을 맞추려 하지 않는 것**이 이 설계의 방침입니다.

---

## 6. Cloudera CDE — 배치·스트리밍·AI 전처리의 단일 실행 기반

근거: [Cloudera Data Engineering service](https://docs.cloudera.com/data-engineering/cloud/overview/topics/cde-service-overview.html) ·
[Orchestrating workflows and pipelines](https://docs.cloudera.com/data-engineering/cloud/orchestrate-workflows/cde-orchestrate-workflows.pdf) ·
[Iceberg library dependencies](https://docs.cloudera.com/data-engineering/1.5.0/manage-jobs/topics/cde-iceberg-library-dependency.html)

### 하나의 기반에서 세 가지 작업이 돕니다

| 작업 | 실행 방식 |
|---|---|
| 배치 변환 | Spark on Kubernetes — Bronze → Silver → Gold |
| 스트리밍 적재 | Spark Structured Streaming — Kafka 소비 후 Iceberg 커밋 |
| AI 전처리 | 문서 파싱 · 청킹 · 임베딩 생성 배치 |

**세 가지가 같은 오케스트레이터 아래 있다는 점**이 이 선택의 핵심입니다. 문서를 파싱해
임베딩을 만들고, 그 결과를 벡터 저장소에 반영하고, 관련 정형 마트를 갱신하는 일련의
작업이 하나의 Airflow DAG에서 의존성을 갖고 실행됩니다. 별도 스케줄러를 두면 이 의존성이
시스템 경계를 넘어가면서 실패 추적이 어려워집니다.

### Airflow가 다른 계층을 직접 구동합니다

- NiFi 흐름 트리거 (REST API)
- Spark Job 제출
- Trino DDL / MERGE 실행 (JDBC)

Airflow가 **파이프라인 전체의 제어 주체**가 되므로, 수집부터 조회 계층 갱신까지가 하나의
DAG로 표현됩니다.

### Iceberg 운영이 기본 제공됩니다

Spark classpath에 Iceberg 런타임이 기본 포함되어 있고, copy-on-write 방식의
MERGE / UPDATE / DELETE와 Spark Iceberg API 기반 compaction을 지원합니다. **Lakehouse
테이블의 유지관리를 별도 도구 없이 같은 파이프라인에서 처리합니다.**

### 자원 격리와 오토스케일

| 항목 | 내용 |
|---|---|
| Virtual Cluster | CPU·메모리 범위가 정의된 개별 오토스케일링 클러스터. **사용자 ACL로 팀·사업부 단위 격리** |
| 서비스·클러스터 오토스케일 | Apache YuniKorn 기반 |
| Job 단위 오토스케일 | Spark dynamic allocation |
| Pipeline Authoring UI | Airflow 숙련도와 무관하게 다단계 파이프라인 작성 |

**Virtual Cluster 격리**는 금융권 조직 구조와 잘 맞습니다. 리스크·마케팅·경영관리 부서의
작업을 각각의 가상 클러스터에 두면 자원 경합과 권한이 함께 분리됩니다.

### 적용 시 유의사항

Kafka에서 MinIO로 직결하는 경로를 두지 않았으므로, **스트리밍 적재의 정합성 책임이 전부
Spark에 모입니다.** Iceberg 커밋 주기와 compaction 정책이 곧 실시간 조회 품질을 결정하므로
이 계층의 튜닝 비중이 큽니다. 초 단위 조회가 필요하면 적재를 기다리지 말고 Starburst의
Kafka 커넥터로 토픽을 직접 조회합니다.

---

## 7. Cloudera AI — 폐쇄망에서의 단일 통합 AI 환경

근거: [Cloudera AI overview](https://docs.cloudera.com/machine-learning/cloud/product/topics/ml-product-overview.html) ·
[AI Studios Overview](https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-ai-studios-overview.html) ·
[RAG Studio Overview](https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-rag-studio-overview.html) ·
[Fine Tuning Studio Overview](https://docs.cloudera.com/machine-learning/1.5.5/use-ai-studios/topics/ml-fine-tuning-studio-overview.html) ·
[Cloudera AI Inference service](https://docs.cloudera.com/machine-learning/cloud/ai-inference/ml-ai-inference.pdf)

### 폐쇄망 AI에서 실제로 어려운 것은 "조합"입니다

외부 SaaS를 쓸 수 없는 환경에서 모델 개발·실험·파인튜닝·RAG·Agent·서빙을 각각 오픈소스로
구성하면, 도구 수만큼 반입·버전 정합성·권한 연동·감사 대응이 늘어납니다. Cloudera AI는
이를 **하나의 플랫폼 안에서 제공**합니다.

| 단계 | 제공 요소 |
|---|---|
| 개발 | AI Workbench — Python · R · Spark-on-Kubernetes 워크로드를 격리·컨테이너 실행. CPU·메모리·GPU 직접 사용, 데이터 레이크에 직접 연결 |
| 실험 | Experiments — 학습 워크로드의 여러 변형을 실행하고 결과 추적 |
| 파인튜닝 | **Fine Tuning Studio** — 데이터 준비부터 모델 배포까지 중앙 관리 |
| RAG | **RAG Studio** — 온프레미스 배포 가능. 기존 데이터 인프라·워크플로와 연동 |
| Agent | **Agent Studio** — 다중 에이전트 워크플로 설계·배포, 내장 관측·로깅 |
| 서빙 | **Cloudera AI Inference Service** — 예측형·생성형 모델의 운영 서빙. HA·내결함성·확장성 |
| 자동화 | Jobs — 모델 드리프트 모니터링을 포함한 종단간 파이프라인 |
| 거버넌스 | Model Governance — 배포 모델을 Data Catalog에 추적, 모델-데이터 계보 관리 |

### 이 아키텍처에서 특히 중요한 두 가지

**첫째, Inference Service가 OpenAI 호환 엔드포인트를 제공합니다.** 이 덕분에 Starburst의
model provider로 등록할 수 있고, Layer 6의 NL-to-SQL과 AI 함수가 폐쇄망에서 동작합니다.
Cloudera AI는 **Layer 7의 소비자이면서 동시에 Layer 6 AI 기능의 공급자**가 됩니다.

**둘째, 데이터 레이크에 직접 연결됩니다.** 학습 데이터 수천만 건을 SQL 엔진을 거치지 않고
S3로 직접 읽으므로 Coordinator 병목이 발생하지 않습니다. 문서 원본은 애초에 SQL 조회
대상이 아닙니다.

### 거버넌스가 함께 옵니다

Model Governance로 배포 모델이 Data Catalog에 등록되고 모델-데이터 계보가 관리됩니다.
금융권에서 "이 모델이 어떤 데이터로 학습됐는가"에 답해야 하는 상황에 대응하는 요소입니다.

### 적용 시 유의사항

- AI Studios는 문서에 **Technical Preview**로 표기된 시점이 있습니다. 반입 예정 버전의
  릴리스 노트로 정식 지원 여부를 확인해야 합니다
- 요건 문서에서 GPU 항목을 확인하지 못했습니다. GPU 노드 사양·드라이버·operator 요건은
  별도 확인이 필요합니다
- Kubernetes(OpenShift 또는 ECS) 위에서만 동작하며, Cloudera AI는 **NFS 4.1**과 별도
  스토리지 클래스를 요구합니다

---

## 종합 — 이 조합이 만드는 것

| 요구 | 이 아키텍처의 답 |
|---|---|
| 저장 비용과 확장성 | 스토리지·컴퓨트 분리, Erasure Coding |
| 엔진 교체·추가 자유도 | S3 호환 + Iceberg REST Catalog |
| 대규모 조회 성능 | Iceberg 메타데이터 플래닝 + Starburst 최적화 |
| 이기종 원천 통합 | Starburst Federation, 단일 SQL 네임스페이스 |
| Agent 대응 | MCP Server, NL-to-SQL, 사내 model provider |
| 감사 대응 | NiFi Provenance, Starburst 질의 감사, Model Governance |
| 실시간 요건 | Kafka 직결 경로 + Starburst Kafka 커넥터 |
| 폐쇄망 | 전 구성요소 온프레미스 배포, 외부 모델 API 불필요 |

**하나의 원칙으로 요약하면, 계층 사이를 표준 규격으로 연결해 각 계층을 독립적으로
교체·확장할 수 있게 한 것입니다.** 저장은 S3 API, 테이블은 Iceberg, 카탈로그는 REST,
조회는 SQL, Agent 연동은 MCP, 모델 호출은 OpenAI 호환 규격입니다. 특정 제품에 종속되는
지점을 줄이는 것이 장기 운영에서 갖는 값이 크다고 봅니다.

## 제안 시 함께 설명할 사항

기술 검토 자리에서 먼저 나올 만한 질문들입니다. 미리 정리해 두는 편이 신뢰를 얻습니다.

| 항목 | 설명 |
|---|---|
| 벤더 수치의 성격 | MinIO의 저장 효율 수치는 벤더 자료이며 중립 벤치마크가 아닙니다. 고객 데이터 특성으로 검증이 필요합니다 |
| REST Catalog HA | Hive Metastore를 제거한 대신 카탈로그 구현체의 HA·백업이 새 필수 항목이 됩니다 |
| S3 직접 접근의 통제 | Trino를 우회하는 경로에는 마스킹이 적용되지 않아 MinIO IAM으로 별도 통제가 필요합니다 |
| 두 종류의 클러스터 | Base(베어메탈·VM)와 Data Services(Kubernetes)를 함께 운영하게 됩니다 |
| Spotfire Web Player | Linux Node Manager는 TERR·Python만 실행하므로 Windows Server 노드가 필요합니다 |
| 폐쇄망 반입 부담 | Cloudera Data Services 배포물이 약 500 GB이며 이미지 복사에 4~5시간이 걸립니다 |
| Agent 대응의 남은 과제 | 의미 메타데이터 작성, 문서 파이프라인, 평가 체계는 별도 구축이 필요합니다 ([agent-readiness-analysis.md](agent-readiness-analysis.md)) |

---

## 출처

확인 시점: 2026-08

**MinIO**
- https://www.min.io/solutions/hdfs-migration
- https://docs.min.io/aistor/
- https://docs.min.io/aistor/reference/aistor-server/requirements/
- https://docs.min.io/aistor/operations/core-concepts/

**Apache Iceberg**
- https://iceberg.apache.org/docs/latest/partitioning/
- https://iceberg.apache.org/docs/latest/performance/
- https://iceberg.apache.org/docs/latest/evolution/

**Starburst Enterprise**
- https://docs.starburst.io/latest/connector/iceberg.html
- https://docs.starburst.io/latest/admin.html
- https://docs.starburst.io/latest/data-engineering/data-maintenance.html
- https://docs.starburst.io/latest/data-engineering/materialized-views.html
- https://docs.starburst.io/latest/starburst-ai/mcp-server.html
- https://docs.starburst.io/latest/starburst-ai/configuration-ai.html
- https://docs.starburst.io/latest/starburst-ai/functions-ai.html

**Cloudera**
- https://docs-archive.cloudera.com/cfm/2.0.1/nifi-overview/topics/nifi-features.html
- https://docs.cloudera.com/cfm-operator/2.11.0/index.html
- https://docs.cloudera.com/cdp-private-cloud-base/latest/howto-streaming.html
- https://docs.cloudera.com/runtime/7.2.18/smm-overview/topics/smm-overview.html
- https://docs.cloudera.com/data-engineering/cloud/overview/topics/cde-service-overview.html
- https://docs.cloudera.com/machine-learning/cloud/product/topics/ml-product-overview.html
- https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-ai-studios-overview.html
- https://docs.cloudera.com/machine-learning/1.5.5/use-ai-studios/topics/ml-fine-tuning-studio-overview.html

---

## 용어집

이 문서에 등장하는 용어입니다. 아키텍처 전반의 용어는 [architecture.md](architecture.md),
제품 기능 용어는 [solution-features.md](solution-features.md)의 용어집을 참고하십시오.

### 스토리지

| 용어 | 설명 |
|---|---|
| HDFS | Hadoop Distributed File System. 저장과 연산을 같은 노드에 두는 분산 파일시스템 |
| NameNode | HDFS의 메타데이터를 관리하는 중앙 노드. 규모 상한이자 장애 집중 지점 |
| 스토리지·컴퓨트 분리 | 저장 계층과 연산 계층을 나눠 각각 독립적으로 증설하는 구조 |
| Erasure Coding | 데이터를 조각과 패리티로 분산 저장해 장애를 견디는 보호 방식 |
| 3중 복제 | 같은 데이터를 3벌 저장하는 HDFS 기본 방식. 200% 저장 오버헤드 |
| S3 API | AWS S3의 오브젝트 접근 규격. 사실상의 업계 표준 |
| `s3a://` | Hadoop 계열 엔진이 S3 호환 저장소에 접근할 때 쓰는 경로 스킴 |
| RDMA | CPU를 거치지 않는 고속 네트워크 전송 |

### 테이블 포맷과 조회

| 용어 | 설명 |
|---|---|
| Apache Iceberg | 오브젝트 스토리지 위에서 트랜잭션·스냅샷·스키마 변경을 지원하는 테이블 포맷 |
| 매니페스트 | 데이터 파일 목록과 파일별 파티션 값·컬럼 통계를 담은 Iceberg 메타데이터 |
| 메타데이터 프루닝 | 통계를 근거로 읽지 않아도 되는 메타데이터·데이터 파일을 걸러내는 것 |
| Hidden partitioning | 사용자가 파티션 컬럼을 몰라도 엔진이 자동으로 파티션 프루닝을 수행하는 Iceberg 기능 |
| 파티션 진화 | 기존 테이블을 유지한 채 파티션 스킴을 변경하는 기능 |
| 스키마 진화 | 기존 데이터를 다시 쓰지 않고 컬럼을 추가·변경하는 기능 |
| 스냅샷 · time-travel | 특정 시점의 테이블 상태 기록과, 그 시점으로 조회하는 기능 |
| 플래닝 | 질의 실행 전에 어떤 파일을 읽을지 결정하는 단계 |
| Hive Metastore | 하둡 생태계의 전통적 메타데이터 저장소 |
| Impala | 하둡 생태계의 대화형 SQL 엔진 |
| Data Federation | 데이터를 모으지 않고 여러 원천을 질의 시점에 통합 조회하는 방식 |
| 구체화 뷰 (Materialized View) | 질의 결과를 미리 계산해 저장해 두는 뷰 |
| Dynamic filtering | 조인 상대의 값으로 실행 중 스캔 대상을 줄이는 최적화 |
| Compaction | 작은 파일을 병합해 조회 성능을 회복시키는 유지관리 작업 |
| copy-on-write | 변경 시 해당 데이터 파일을 새로 쓰는 방식 |

### AI 연동

| 용어 | 설명 |
|---|---|
| MCP | Model Context Protocol. Agent가 외부 도구·데이터에 접근하기 위한 개방형 규약 |
| NL-to-SQL | 자연어 질문을 SQL로 변환하는 기능 |
| RAG | 관련 문서를 검색해 근거로 제공한 뒤 답변을 생성하는 방식 |
| 파인튜닝 | 사전 학습된 모델을 특정 용도에 맞게 추가 학습시키는 것 |
| Model Provider | AI 기능이 호출하는 추론 모델 공급자 |
| OpenAI 호환 엔드포인트 | OpenAI API 규격을 따르는 추론 엔드포인트 |
| 임베딩 | 텍스트를 의미가 반영된 숫자 벡터로 변환한 것 |
| Agent | 도구를 사용해 다단계 작업을 스스로 수행하는 AI 실행 단위 |
| Technical Preview | 정식 지원 이전 단계의 기능 표기 |

### 파이프라인과 운영

| 용어 | 설명 |
|---|---|
| Data Provenance | 데이터의 출처·변형·전달 이력을 건 단위로 기록하는 NiFi 기능 |
| Back-pressure | 하류가 처리하지 못할 때 상류 유입을 억제하는 흐름 제어 |
| Guaranteed Delivery | 장애 시에도 데이터 유실을 막는 전달 보증 |
| Classloader Isolation | 확장 간 라이브러리 의존성 충돌을 격리하는 구조 |
| Site-to-Site | NiFi 인스턴스 간 전용 전송 프로토콜 |
| 컨슈머 그룹 | Kafka에서 토픽을 나눠 읽는 소비자 묶음 |
| Consumer lag | 컨슈머가 최신 메시지보다 뒤처진 정도 |
| Schema Registry | 메시지 스키마를 등록·버전 관리해 호환성을 유지하는 저장소 |
| Cruise Control | Kafka 파티션 배치를 재조정해 부하를 분산하는 도구 |
| Structured Streaming | Spark의 스트리밍 처리 방식 |
| Virtual Cluster | CDE에서 CPU·메모리 범위가 정의된 개별 오토스케일링 클러스터 |
| YuniKorn | Kubernetes용 자원 스케줄러 |
| DAG | 작업 의존 관계를 순환 없이 표현한 그래프 |
| Model Governance | 배포 모델을 카탈로그에 등록하고 모델-데이터 계보를 관리하는 것 |
