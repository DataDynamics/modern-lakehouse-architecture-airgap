#!/usr/bin/env python3
"""Lakehouse 아키텍처 간략판(기능 개요도)을 SVG(+PNG)로 생성한다.

상세도(generate_architecture_svg.py)와 같은 배치·색·경로 구조를 유지하되,
상자 안의 긴 텍스트를 "기능명 + 한 줄 설명" 타일(sub-box)로 정리한 그림이다.
경로 라벨도 짧게 줄여 처음 보는 사람이 구성요소의 역할을 먼저 파악하도록 한다.

Usage:
    python scripts/generate_concept_svg.py
    python scripts/generate_concept_svg.py -o assets/lakehouse-concept.svg
    python scripts/generate_concept_svg.py --no-png
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_architecture_svg import (  # noqa: E402
    AGENT, BACKGROUND, CATALOG, DIRECT, FEDERATE, FONT_STACK, HAIRLINE, INK, MODEL,
    PALETTE, PNG_SCALE, STREAM, Edge, render_edge, render_png, text,
)

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

CANVAS_W = 2180
CANVAS_H = 1360

TITLE = "Lakehouse Reference Architecture — 기능 개요"
SUBTITLE = ("구성요소별 핵심 기능만 타일로 표시  ·  "
            "제품 사양 · 경로 설계 근거는 lakehouse-architecture-lr.svg 와 docs/architecture.md")

# 타일 치수
TILE_H = 46
TILE_GAP = 8
PAD_X = 18
HEAD_H = 68          # 제목 + 부제 + 구분선
FOOT_H = 12

# --------------------------------------------------------------------------
# Boxes — 각 상자는 제목, 제품명, 기능 타일 목록
# --------------------------------------------------------------------------


@dataclass
class Tile:
    label: str
    caption: str = ""


@dataclass
class Box:
    key: str
    x: int
    y: int
    w: int
    ramp: str
    title: str
    subtitle: str
    tiles: list[Tile]

    @property
    def h(self) -> int:
        return HEAD_H + len(self.tiles) * (TILE_H + TILE_GAP) + FOOT_H

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def mid_y(self) -> int:
        return self.y + self.h // 2


BOXES: list[Box] = [
    Box("source", 40, 260, 250, "gray", "1. Data Source", "금융권 원천 시스템", [
        Tile("계정계 · 정보계", "원장 · 회계 (CDC)"),
        Tile("카드 · 결제", "승인 · 매입 · VAN/PG 전문"),
        Tile("채널", "인터넷뱅킹 · 앱 · ATM · 콜센터"),
        Tile("대외계 · 시장", "금결원 · 신정원 · KRX 시세"),
        Tile("리스크 · 컴플라이언스", "FDS · AML · 약관 / 규정 문서"),
    ]),
    Box("ingestion", 360, 260, 300, "teal", "2. Ingestion", "Cloudera CFM (Apache NiFi)", [
        Tile("수집 · 연결", "DB · 파일 · MQ · API · 스트림"),
        Tile("변환", "CSV / XML / JSON → Parquet · Avro"),
        Tile("라우팅 · 흐름 제어", "조건 분기 · 우선순위 · Back-pressure"),
        Tile("전달 보증 · 이력", "Guaranteed Delivery · Provenance"),
        Tile("운영 · 보안", "GUI 흐름 설계 · 모니터링 · TLS"),
    ]),
    Box("streaming", 730, 120, 300, "coral", "3. Streaming Bus", "Cloudera CDP", [
        Tile("Apache Kafka", "raw.* / cdc.* / evt.* 토픽 · 복제 3"),
        Tile("Streams Messaging Manager", "토픽 · 컨슈머 · 지연 관제"),
        Tile("ZooKeeper", "브로커 등록 · 리더 선출"),
    ]),
    Box("storage", 730, 410, 300, "blue", "4. Storage", "MinIO (S3 호환) + Apache Iceberg", [
        Tile("Bronze", "원천 그대로 (append)"),
        Tile("Silver", "정제 · 중복제거 · SCD"),
        Tile("Gold", "집계 · 마트 · 피처"),
        Tile("Docs", "문서 · 이미지 원본 (RAG 입력)"),
        Tile("Iceberg Table · REST Catalog", "스냅샷 · time-travel · 스키마 변경"),
    ]),
    Box("processing", 1100, 120, 330, "purple", "5. Processing & Orchestration", "Cloudera CDE", [
        Tile("Airflow", "DAG 스케줄 · 의존성 · SLA"),
        Tile("Spark on Kubernetes", "Bronze → Silver → Gold · MERGE · Compaction"),
    ]),
    Box("federation", 1100, 410, 330, "amber", "6. Data Federation", "Starburst Trino", [
        Tile("Coordinator · Worker", "HA · autoscale"),
        Tile("Connectors", "Iceberg · Kafka · Hive · Oracle · PostgreSQL"),
        Tile("AI Features", "NL-to-SQL · AI Functions · MCP Server"),
        Tile("Model Provider", "OpenAI 호환 · 사내 모델 (on-prem)"),
        Tile("Vector DB Support", "Iceberg · pgvector · Elasticsearch"),
    ]),
    Box("consumption", 1500, 410, 280, "green", "7. Consumption", "사람이 쓰는 접점", [
        Tile("Spotfire", "대시보드 · Ad-hoc 분석"),
        Tile("Cloudera AI", "Workbench · AI Studio · Agent Studio"),
        Tile("SQL Client · Notebook · API", "DBeaver · Jupyter"),
    ]),
    Box("serving", 1850, 120, 290, "cyan", "모델 서빙", "Cloudera AI Inference (OpenAI 호환)", [
        Tile("추론 엔드포인트", "사내 on-prem · 외부 호출 없음"),
        Tile("생성 모델", "NL-to-SQL · 답변 생성"),
        Tile("임베딩 · 리랭커", "한국어 모델 · 고객 보유"),
    ]),
    Box("agent", 1850, 410, 290, "rose", "고객 AI Agent", "업무 질의 · 문서 조회", [
        Tile("Agent 런타임", "세션 · 도구 계획 · 권한 위임"),
        Tile("도구 (MCP)", "Starburst · 문서 검색 · Catalog"),
        Tile("감사", "질문 → 근거 → SQL → 답변 기록"),
    ]),
    Box("catalog", 360, 830, 300, "olive", "Data Catalog", "Argus Catalog", [
        Tile("데이터 카탈로그", "데이터셋 · 스키마 · 리니지 · 용어집"),
        Tile("메타데이터 수집", "11종 플랫폼 · Trino Query Listener"),
        Tile("데이터 품질", "프로파일링 · 규칙 검증 · 점수 전파"),
        Tile("거버넌스", "API 카탈로그 · AI Agent 카탈로그"),
        Tile("모델 레지스트리", "MLflow · OCI · 에어갭 반입"),
    ]),
    Box("rag", 730, 830, 300, "plum", "RAG", "Argus RAG Studio", [
        Tile("문서 반입", "S3 소스 · 소스 워치 · 라우팅"),
        Tile("인제스천", "파싱 · 청킹 · 임베딩 · 색인"),
        Tile("검색 · 생성", "하이브리드 · 리랭크 · 인용 답변"),
        Tile("REST API", "search · query · chat · API 키"),
        Tile("평가 · 운영", "골든셋 · 트레이스 · 피드백"),
    ]),
    Box("vectordb", 1100, 830, 330, "steel", "Vector DB", "PostgreSQL + pgvector (기본)", [
        Tile("저장 대상", "청크 · 벡터 · tsvector · 메타데이터"),
        Tile("교체 가능 백엔드", "Qdrant · Weaviate · Milvus"),
        Tile("검색", "벡터 + 렉시컬 → RRF → 리랭크"),
        Tile("호출 주체", "RAG Studio · AI Agent · Trino"),
    ]),
]

B = {b.key: b for b in BOXES}

# --------------------------------------------------------------------------
# Edges — 상세도와 같은 구조, 라벨만 짧게
# --------------------------------------------------------------------------


def edges() -> list[Edge]:
    s, i, st, sto = B["source"], B["ingestion"], B["streaming"], B["storage"]
    p, f, c = B["processing"], B["federation"], B["consumption"]
    sv, a, cat, r, v = B["serving"], B["agent"], B["catalog"], B["rag"], B["vectordb"]
    return [
        # 수집 · 스트리밍
        Edge(f"M165 {s.y} V90 H700 V200 H{st.x - 8}", STREAM, "6 4",
             label="실시간 이벤트 직결 (CDC · MQ · FDS)", label_xy=(330, 108)),
        Edge(f"M{s.right} {s.mid_y} H{i.x - 8}"),
        Edge(f"M{i.right} 300 H690 V240 H{st.x - 8}"),
        Edge(f"M{st.x - 8} 320 H706 V400 H{i.right + 8}", STREAM, "6 4"),
        Edge(f"M{i.right} 520 H{sto.x - 8}"),
        Edge(f"M{st.right} 220 H{p.x - 8}", STREAM, "6 4",
             label="Kafka → Spark Streaming", label_xy=(1100, 108)),
        # 저장 · 처리 · 조회
        Edge(f"M{sto.right + 4} 430 H1065 V260 H{p.x - 8}", both=True),
        Edge(f"M{sto.right} 600 H{f.x - 8}"),
        Edge(f"M{sto.right} 425 H1050 V385 H1460 V500 H{c.x - 8}", DIRECT,
             label="S3 직접 접근 (학습 데이터 · 문서 원본)", label_xy=(1150, 378)),
        Edge(f"M{f.right} 560 H{c.x - 8}", label="JDBC / ODBC", label_xy=(1436, 548)),
        Edge(f"M165 {s.bottom} V784 H1075 V690 H{f.x - 8}", FEDERATE, "10 3 2 3",
             label="원천 직접 페더레이션", label_xy=(520, 776)),
        # 모델 · Agent
        Edge(f"M{f.right} 690 H1815 V{sv.bottom + 2}", MODEL,
             label="모델 호출", label_xy=(1500, 682)),
        Edge(f"M1900 {a.bottom + 2} V740 H{f.right + 12}", AGENT, both=True,
             label="MCP · 메타데이터 · SQL", label_xy=(1610, 732)),
        Edge(f"M1995 {a.y - 4} V{sv.bottom + 2}", MODEL,
             label="추론 호출", label_xy=(2010, 392)),
        # RAG
        Edge(f"M880 {sto.bottom} V{r.y - 8}", DIRECT,
             label="소스 워치 (S3 API)", label_xy=(893, 770)),
        Edge(f"M{r.right} 1000 H{v.x - 8}", both=True,
             label="upsert · 검색", label_xy=(1034, 988)),
        Edge(f"M{v.right} 900 H1990 V{a.bottom + 8}", AGENT,
             label="Vector DB 직접 조회 (Top-K)", label_xy=(1450, 890)),
        Edge(f"M1265 {v.y - 8} V{f.bottom + 8}", both=True,
             label="벡터 테이블 조회", label_xy=(1278, 806)),
        Edge(f"M2060 {a.bottom + 2} V1210 H880 V{r.bottom + 8}", AGENT, both=True,
             label="Argus REST API (search · query · chat)", label_xy=(1300, 1202)),
        # Catalog
        Edge(f"M600 {i.bottom} V{cat.y - 8}", CATALOG, "3 3",
             label="NiFi 리니지", label_xy=(612, 700)),
        Edge(f"M1140 {f.bottom} V808 H700 V900 H{cat.right + 8}", CATALOG, "3 3",
             label="Query Listener · Metadata Sync", label_xy=(905, 803)),
        Edge(f"M2100 {a.bottom + 2} V1232 H510 V{cat.bottom + 8}", CATALOG, "3 3",
             both=True, label="Agent 등록 · 미터링 · 메타데이터 API",
             label_xy=(700, 1250)),
    ]


LEGEND = [
    "배치 : Source → CFM → MinIO   |   실시간 : Source / CFM → Kafka → Spark Streaming → MinIO   |   "
    "조회 : Trino → Spotfire · Cloudera AI   |   Agent : AI Agent → MCP → Trino · 사내 모델",
    "RAG : MinIO docs/ → Argus RAG Studio → Vector DB → AI Agent (직접 조회 또는 REST API)   |   "
    "카탈로그 : NiFi · Trino → Argus Catalog ↔ AI Agent",
    "실선 = 상시 흐름 · 주황 점선 = 스트리밍 · 파랑 = S3 직접 접근 · 보라 일점쇄선 = 원천 페더레이션 · "
    "청록 = 모델 호출 · 자주 = Agent 호출 · 올리브 점선 = 메타데이터 · 리니지",
]

# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def render_box(b: Box) -> list[str]:
    ramp = PALETTE[b.ramp]
    out = [
        f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" rx="12" '
        f'fill="{ramp.fill}" stroke="{ramp.stroke}" stroke-width="0.9"/>'
    ]
    tx, inner_r = b.x + PAD_X, b.right - PAD_X
    out.append(f'<text x="{tx}" y="{b.y + 32}" font-size="15" font-weight="500" '
               f'fill="{ramp.title}">{b.title}</text>')
    out.append(text(tx, b.y + 53, b.subtitle, 12.5, ramp.muted))
    out.append(f'<line x1="{tx}" y1="{b.y + HEAD_H}" x2="{inner_r}" y2="{b.y + HEAD_H}" '
               f'stroke="{ramp.rule}" stroke-width="0.9"/>')
    cur = b.y + HEAD_H + TILE_GAP
    for t in b.tiles:
        out.append(f'<rect x="{tx}" y="{cur}" width="{b.w - 2 * PAD_X}" height="{TILE_H}" '
                   f'rx="7" fill="#FFFFFF" stroke="{ramp.rule}" stroke-width="0.9"/>')
        out.append(f'<rect x="{tx}" y="{cur + 8}" width="3" height="{TILE_H - 16}" '
                   f'rx="1.5" fill="{ramp.stroke}"/>')
        out.append(text(tx + 14, cur + 19, t.label, 12.5, ramp.title, "500"))
        if t.caption:
            out.append(text(tx + 14, cur + 36, t.caption, 10.5, ramp.muted))
        cur += TILE_H + TILE_GAP
    return out


def build() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" '
        f'height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'role="img" font-family="{FONT_STACK}">',
        f'<title>{TITLE}</title>',
        '<desc>Simplified view of the air-gapped lakehouse reference '
        'architecture. Same layout and paths as the detailed diagram, but '
        'each component box lists only its main functions as small tiles '
        'with one-line captions.</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '</marker></defs>',
        f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="{BACKGROUND}"/>',
        f'<text x="40" y="48" font-size="22" font-weight="500" fill="#2C2C2A">{TITLE}</text>',
        text(40, 72, SUBTITLE, 13, INK),
    ]
    for e in edges():
        parts += render_edge(e)
    for b in BOXES:
        parts += render_box(b)
    parts.append(f'<line x1="40" y1="1270" x2="{CANVAS_W - 40}" y2="1270" '
                 f'stroke="{HAIRLINE}" stroke-width="0.9"/>')
    for k, line in enumerate(LEGEND):
        parts.append(text(40, 1290 + k * 18, line, 11, "#888780"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=Path,
                    default=Path("assets/lakehouse-concept.svg"),
                    help="SVG 출력 경로 (기본: assets/lakehouse-concept.svg)")
    ap.add_argument("--png", type=Path, default=None,
                    help="PNG 출력 경로 (기본: SVG 와 같은 이름의 .png)")
    ap.add_argument("--png-width", type=int, default=CANVAS_W * PNG_SCALE,
                    help=f"PNG 가로 픽셀 (기본: {CANVAS_W * PNG_SCALE})")
    ap.add_argument("--no-png", action="store_true",
                    help="PNG 를 생성하지 않고 SVG 만 만든다")
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(), encoding="utf-8")
    print(f"wrote {args.output}")

    if args.no_png:
        return
    png = args.png or args.output.with_suffix(".png")
    png.parent.mkdir(parents=True, exist_ok=True)
    try:
        renderer = render_png(args.output, png, args.png_width,
                              canvas=(CANVAS_W, CANVAS_H))
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"PNG 생성 실패: {exc}", file=sys.stderr)
        raise SystemExit(1)
    height = round(args.png_width * CANVAS_H / CANVAS_W)
    print(f"wrote {png} ({args.png_width}x{height}, {renderer})")


if __name__ == "__main__":
    main()
