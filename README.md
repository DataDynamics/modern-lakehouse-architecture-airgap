# modern-lakehouse-architecture-airgap

폐쇄망(air-gapped) 환경을 전제로 한 금융권 Modern Lakehouse 참조 아키텍처 다이어그램과
설계 문서입니다.

![Lakehouse Reference Architecture](assets/lakehouse-architecture-lr.svg)

## 목차

- [구성](#구성)
- [아키텍처 개요](#아키텍처-개요)
- [다이어그램 재생성](#다이어그램-재생성)
  - [PNG 변환](#png-변환)
- [폰트](#폰트)
- [용어집](#용어집)
  - [환경·구조](#환경구조)
  - [제품](#제품)
  - [기타](#기타)

## 구성

```
.
├── assets/
│   └── lakehouse-architecture-lr.svg     다이어그램 (빌드 산출물)
├── docs/
│   ├── architecture.md                   Layer별 설명과 경로 설계 근거
│   ├── solutions.md                      솔루션별 역할과 담당 범위
│   ├── solution-features.md              솔루션별 주요 기능 목록 (공식 문서 기준)
│   └── agent-readiness-analysis.md       Agent 대상 데이터 제공 요건 분석
└── scripts/
    └── generate_architecture_svg.py      다이어그램 생성 스크립트
```

## 아키텍처 개요

좌에서 우로 흐르는 7개 Layer 구조입니다.

| # | Layer | 제품 |
|---|---|---|
| 1 | Data Source | 계정계·정보계, 카드·결제, 채널, 대외계·시장, 리스크·컴플라이언스 |
| 2 | Ingestion | Cloudera CFM (Apache NiFi) |
| 3 | Streaming Bus | Cloudera CDP — Kafka, Streams Messaging Manager, ZooKeeper |
| 4 | Storage | MinIO (S3 호환) + Apache Iceberg |
| 5 | Processing & Orchestration | Cloudera CDE — Airflow, Spark on Kubernetes |
| 6 | Data Federation | Starburst Trino |
| 7 | Consumption | Spotfire, Cloudera AI, SQL Client, Notebook |

상세 설명은 [docs/architecture.md](docs/architecture.md), 각 솔루션이 이 아키텍처에서
담당하는 역할은 [docs/solutions.md](docs/solutions.md), 공식 문서에서 확인한 제품별 기능
목록은 [docs/solution-features.md](docs/solution-features.md)를 참고하십시오.

## 다이어그램 재생성

Python 3.10 이상이 필요하며 외부 의존성은 없습니다.

```bash
python scripts/generate_architecture_svg.py
```

기본 출력 경로는 `assets/lakehouse-architecture-lr.svg` 입니다. `-o` 옵션으로 변경할 수
있습니다.

```bash
python scripts/generate_architecture_svg.py -o /tmp/diagram.svg
```

레이아웃, 문구, 색상은 스크립트 상단의 `BOXES`, `EDGES`, `PALETTE` 선언에 모여 있습니다.
`assets/` 의 SVG는 빌드 산출물이므로 직접 편집하지 말고 스크립트를 수정한 뒤 재생성하십시오.

### PNG 변환

```bash
# rsvg-convert
rsvg-convert -w 3640 assets/lakehouse-architecture-lr.svg -o diagram.png

# Inkscape
inkscape assets/lakehouse-architecture-lr.svg --export-type=png \
         --export-width=3640 --export-filename=diagram.png
```

## 폰트

SVG는 `Pretendard → Malgun Gothic → Apple SD Gothic Neo → Noto Sans KR` 순으로 폰트를
탐색합니다. 한글이 깨지는 환경에서는 스크립트의 `FONT_STACK` 상수를 수정하십시오.

## 용어집

이 문서에 등장하는 용어입니다. Layer별 상세 설명은
[docs/architecture.md](docs/architecture.md), 제품 기능은
[docs/solution-features.md](docs/solution-features.md)를 참고하십시오.

### 환경·구조

| 용어 | 설명 |
|---|---|
| 폐쇄망 (air-gapped) | 외부 인터넷과 물리적·논리적으로 분리된 망. 외부 서비스 호출과 온라인 패키지 설치가 불가하므로, 모든 구성요소를 내부에 배치하고 설치 미디어를 반입해 공급해야 합니다 |
| Lakehouse | 데이터 레이크의 저비용 대용량 저장과 데이터 웨어하우스의 테이블·트랜잭션 특성을 한 저장소에서 함께 제공하는 아키텍처 |
| Layer | 이 아키텍처의 논리 구획 단위. 좌에서 우로 Data Source → Ingestion → Streaming Bus → Storage → Processing & Orchestration → Data Federation → Consumption 7개로 구성됩니다 |
| 계정계 · 정보계 | 금융 IT의 전통적 구분. 계정계는 예금·여신 등 거래를 처리하는 원장 시스템, 정보계는 계정계 데이터를 분석 목적으로 재구성한 시스템 |
| 대외계 | 금융결제원, 신용정보원 등 외부 기관과 전문을 주고받는 시스템 |

### 제품

| 용어 | 설명 |
|---|---|
| Cloudera CFM | Cloudera Flow Management. Apache NiFi 기반의 데이터 수집·흐름 관리 제품 |
| Apache NiFi | GUI로 데이터 흐름을 설계하고 전달을 보증하는 데이터 통합 도구 |
| Cloudera CDP | Cloudera Data Platform. 이 아키텍처에서는 Kafka 중심의 스트리밍 구성요소를 가리킵니다 |
| Apache Kafka | 분산 이벤트 스트리밍 플랫폼. 생산자와 소비자를 시간적으로 분리하는 버퍼 역할 |
| Streams Messaging Manager (SMM) | Kafka의 토픽·컨슈머·지연을 관제하는 Cloudera 운영 도구 |
| ZooKeeper | 분산 코디네이션 서비스. Kafka 브로커 등록과 리더 선출에 사용 |
| MinIO | S3 호환 오브젝트 스토리지. 폐쇄망에 오브젝트 저장소를 자체 구축할 때 사용합니다 |
| Apache Iceberg | 오브젝트 스토리지 위에서 스냅샷·스키마 변경·트랜잭션을 지원하는 테이블 포맷 |
| Cloudera CDE | Cloudera Data Engineering. Airflow와 Spark on Kubernetes를 제공하는 데이터 처리·오케스트레이션 제품 |
| Apache Airflow | DAG로 작업 의존성과 일정을 정의하는 워크플로 오케스트레이터 |
| Spark on Kubernetes | Apache Spark를 Kubernetes 위에서 실행하는 배포 방식. 작업 단위로 자원을 할당·회수합니다 |
| Starburst Trino | 분산 SQL 질의 엔진 Trino의 상용 배포판. 여러 저장소를 하나의 SQL 네임스페이스로 묶습니다 |
| Spotfire | 시각화 기반 분석 플랫폼. 대시보드와 Ad-hoc 분석에 사용 |
| Cloudera AI | 모델 학습·서빙과 AI 에이전트를 제공하는 Cloudera 제품 |

### 기타

| 용어 | 설명 |
|---|---|
| S3 호환 | AWS S3의 API 규격을 그대로 따르는 것. 애플리케이션 변경 없이 저장소를 교체할 수 있습니다 |
| 빌드 산출물 | 스크립트가 생성하는 파일. 직접 편집하지 않고 생성 스크립트를 수정한 뒤 재생성합니다 |
| SVG | 확대해도 깨지지 않는 벡터 이미지 형식. 이 저장소의 다이어그램 형식입니다 |
| rsvg-convert · Inkscape | SVG를 PNG 등 래스터 이미지로 변환하는 도구 |
| 폰트 스택 | 폰트를 우선순위대로 나열한 목록. 앞의 폰트가 없으면 다음 폰트를 사용합니다 |
| Ad-hoc 분석 | 미리 정의된 보고서가 아니라, 그때그때 질문에 따라 즉석으로 수행하는 분석 |
