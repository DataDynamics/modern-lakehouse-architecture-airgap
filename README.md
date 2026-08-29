# modern-lakehouse-architecture-airgap

폐쇄망(air-gapped) 환경을 전제로 한 금융권 Modern Lakehouse 참조 아키텍처 다이어그램과
설계 문서입니다.

![Lakehouse Reference Architecture](assets/lakehouse-architecture-lr.svg)

## 구성

```
.
├── assets/
│   └── lakehouse-architecture-lr.svg     다이어그램 (빌드 산출물)
├── docs/
│   └── architecture.md                   Layer별 설명과 경로 설계 근거
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

상세 설명은 [docs/architecture.md](docs/architecture.md)를 참고하십시오.

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
