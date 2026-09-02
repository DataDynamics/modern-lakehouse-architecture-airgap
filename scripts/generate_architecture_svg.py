#!/usr/bin/env python3
"""Generate the air-gapped modern lakehouse architecture diagram as an SVG.

The diagram is described declaratively below (PALETTE / BOXES / ARROWS) and
rendered to a single self-contained SVG file with a white background.

SVG 를 쓰고 나면 같은 이름의 PNG 도 함께 생성한다. 래스터화에는 시스템에 설치된
렌더러(rsvg-convert, Inkscape, Chromium, CairoSVG, ImageMagick) 중 하나를 사용한다.

Usage:
    python scripts/generate_architecture_svg.py
    python scripts/generate_architecture_svg.py -o assets/lakehouse-architecture-lr.svg
    python scripts/generate_architecture_svg.py --png-width 4360
    python scripts/generate_architecture_svg.py --no-png
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

CANVAS_W = 2180
CANVAS_H = 1670
BACKGROUND = "#FFFFFF"

FONT_STACK = (
    "'Pretendard','Malgun Gothic','Apple SD Gothic Neo',"
    "'Noto Sans KR','Segoe UI',sans-serif"
)

TITLE = "Lakehouse Reference Architecture"
SUBTITLE = (
    "Cloudera CFM \u00b7 CDP \u00b7 CDE  |  Starburst Trino  |  MinIO  |  "
    "Spotfire \u00b7 Cloudera AI  |  Argus RAG Studio \u00b7 Argus Catalog "
    "\u00b7 Vector DB  |  \uace0\uac1d AI Agent"
)

# --------------------------------------------------------------------------
# Colour palette - one ramp per layer, 800/600/200/50 stops
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Ramp:
    fill: str
    stroke: str
    title: str
    body: str
    muted: str
    rule: str


PALETTE = {
    "gray": Ramp("#F1EFE8", "#5F5E5A", "#2C2C2A", "#444441", "#888780", "#B4B2A9"),
    "teal": Ramp("#E1F5EE", "#0F6E56", "#04342C", "#085041", "#0F6E56", "#5DCAA5"),
    "coral": Ramp("#FAECE7", "#993C1D", "#4A1B0C", "#712B13", "#993C1D", "#F0997B"),
    "blue": Ramp("#E6F1FB", "#185FA5", "#042C53", "#0C447C", "#185FA5", "#85B7EB"),
    "purple": Ramp("#EEEDFE", "#534AB7", "#26215C", "#3C3489", "#534AB7", "#AFA9EC"),
    "amber": Ramp("#FAEEDA", "#854F0B", "#412402", "#633806", "#854F0B", "#EF9F27"),
    "green": Ramp("#EAF3DE", "#3B6D11", "#173404", "#27500A", "#3B6D11", "#97C459"),
    "cyan": Ramp("#E2F1F7", "#0C6480", "#04303F", "#08495E", "#0C6480", "#63B4CE"),
    "rose": Ramp("#FBEBF0", "#9B2D4F", "#450F21", "#6E1F38", "#9B2D4F", "#E294AC"),
    "plum": Ramp("#F6E9F7", "#7B2E86", "#350E3A", "#551F5D", "#7B2E86", "#CE97D6"),
    "steel": Ramp("#E9EEF2", "#3E5D72", "#12242E", "#26414F", "#3E5D72", "#9BB3C2"),
    "olive": Ramp("#F3F1DC", "#6B6414", "#2C2A05", "#4A4509", "#6B6414", "#CFC760"),
}

INK = "#5F5E5A"          # neutral flow lines
STREAM = "#993C1D"       # streaming (dashed)
DIRECT = "#185FA5"       # S3 direct access
FEDERATE = "#534AB7"     # source-level federation
MODEL = "#0C6480"        # inference model call
AGENT = "#9B2D4F"        # agent tool call
CATALOG = "#6B6414"      # metadata sync / lineage (dashed)
HAIRLINE = "#D3D1C7"

# Vertical rhythm inside a box
PAD_X = 18
TITLE_DY = 32
SUBTITLE_DY = 21
RULE_DY = 15
GROUP_LEAD = 26
ITEM_LEAD = 21
ITEM_STEP = 19
GROUP_GAP = 34

FS_BOX_TITLE = 15
FS_BOX_SUB = 12.5
FS_GROUP = 12.5
FS_ITEM = 11.5
FS_NOTE = 10.5
FS_EDGE = 11

# --------------------------------------------------------------------------
# Content blocks
# --------------------------------------------------------------------------


@dataclass
class Group:
    """Bold label followed by indented detail lines."""
    label: str
    items: list[str] = field(default_factory=list)


@dataclass
class Items:
    """Plain lines with no bold label."""
    items: list[str] = field(default_factory=list)
    lead: int = GROUP_LEAD
    step: int = ITEM_STEP


@dataclass
class Cards:
    """White sub-rectangles, each with a mono-ish path and a caption."""
    rows: list[tuple[str, str]]
    height: int = 52
    gap: int = 10
    lead: int = 14


@dataclass
class Rule:
    lead: int = 22


@dataclass
class Note:
    text: str
    lead: int = 32


@dataclass
class Box:
    key: str
    x: int
    y: int
    w: int
    h: int
    ramp: str
    title: str
    subtitle: str | None
    blocks: list = field(default_factory=list)

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h


# --------------------------------------------------------------------------
# The seven layers, plus the model serving / AI agent / RAG boxes
# --------------------------------------------------------------------------

BOXES: list[Box] = [
    Box(
        key="source", x=40, y=260, w=250, h=490, ramp="gray",
        title="1. Data Source Layer",
        subtitle="\uae08\uc735\uad8c \uc6d0\ucc9c \uc2dc\uc2a4\ud15c",
        blocks=[
            Group("\uacc4\uc815\uacc4 \u00b7 \uc815\ubcf4\uacc4", [
                "Oracle Exadata \u00b7 DB2 \u00b7 DW",
                "\uc5ec\u00b7\uc218\uc2e0 \uc6d0\uc7a5, \ud68c\uacc4 (CDC)",
            ]),
            Group("\uce74\ub4dc \u00b7 \uacb0\uc81c", [
                "\uc2b9\uc778 / \ub9e4\uc785 \uac70\ub798 \uc6d0\uc7a5",
                "VAN \u00b7 PG \uc804\ubb38 \ub85c\uadf8",
            ]),
            Group("\ucc44\ub110", [
                "\uc778\ud130\ub137\ubc45\ud0b9 \u00b7 \ubaa8\ubc14\uc77c\uc571",
                "ATM \u00b7 \ucf5c\uc13c\ud130 STT",
            ]),
            Group("\ub300\uc678\uacc4 \u00b7 \uc2dc\uc7a5 \ub370\uc774\ud130", [
                "\uae08\uc735\uacb0\uc81c\uc6d0 \u00b7 \uc2e0\uc6a9\uc815\ubcf4\uc6d0",
                "KRX \u00b7 Bloomberg \uc2dc\uc138",
            ]),
            Group("\ub9ac\uc2a4\ud06c \u00b7 \ucef4\ud50c\ub77c\uc774\uc5b8\uc2a4", [
                "FDS \uc774\ubca4\ud2b8, AML / STR",
                "\uc57d\uad00 \u00b7 \uaddc\uc815 \u00b7 \uc0c1\ud488\uc124\uba85\uc11c",
            ]),
            Note("JDBC/CDC \u00b7 MQ \u00b7 SFTP \u00b7 REST"),
        ],
    ),
    Box(
        key="ingestion", x=360, y=260, w=300, h=490, ramp="teal",
        title="2. Ingestion Layer",
        subtitle="Cloudera CFM (Apache NiFi)",
        blocks=[
            Group("\uc218\uc9d1 \u00b7 \uc5f0\uacb0 (Connectivity)", [
                "DB \u00b7 \ud30c\uc77c \u00b7 MQ \u00b7 API \u00b7 \uc2a4\ud2b8\ub9bc",
                "400+ \ud504\ub85c\uc138\uc11c, No-Code \uc5f0\ub3d9",
            ]),
            Group("\ubcc0\ud658 (Transformation)", [
                "CSV / XML / JSON \u2192 Parquet \u00b7 Avro",
                "\uc2a4\ud0a4\ub9c8 \uac80\uc99d \u00b7 \ub808\ucf54\ub4dc \ub2e8\uc704 \ucc98\ub9ac",
            ]),
            Group("\ub77c\uc6b0\ud305 \u00b7 \ud750\ub984 \uc81c\uc5b4", [
                "\uc870\uac74 \ubd84\uae30 \u00b7 \uc6b0\uc120\uc21c\uc704 \ud050",
                "Back-pressure \u00b7 \uc7ac\uc2dc\ub3c4",
            ]),
            Group("\uc804\ub2ec \ubcf4\uc99d \u00b7 \ucd94\uc801", [
                "Guaranteed Delivery",
                "Data Provenance (\uc774\ub825 \ucd94\uc801)",
            ]),
            Group("\uc6b4\uc601 \u00b7 \ubcf4\uc548", [
                "GUI \ud750\ub984 \uc124\uacc4 \u00b7 \uc2e4\uc2dc\uac04 \ubaa8\ub2c8\ud130\ub9c1",
                "Site-to-Site \u00b7 TLS \u00b7 \ud30c\ub77c\ubbf8\ud130",
            ]),
            Note("\ubc30\uce58 \u00b7 \ub9c8\uc774\ud06c\ub85c\ubc30\uce58 \u00b7 \uc2a4\ud2b8\ub9ac\ubc0d"),
        ],
    ),
    Box(
        key="streaming", x=730, y=120, w=300, h=265, ramp="coral",
        title="3. Streaming Bus Layer",
        subtitle="Cloudera CDP",
        blocks=[
            Group("Apache Kafka", [
                "topics : raw.* / cdc.* / evt.*",
                "partition \u00b7 replication = 3",
            ]),
            Group("Streams Messaging Manager", [
                "\ud1a0\ud53d \u00b7 \ucee8\uc288\uba38 \u00b7 \uc9c0\uc5f0(lag) \uad00\uc81c",
            ]),
            Group("ZooKeeper Ensemble (3 / 5 EA)", [
                "\ube0c\ub85c\ucee4 \ub4f1\ub85d \u00b7 \ub9ac\ub354 \uc120\ucd9c",
            ]),
        ],
    ),
    Box(
        key="storage", x=730, y=430, w=300, h=440, ramp="blue",
        title="4. Storage Layer",
        subtitle="MinIO (S3 \ud638\ud658 \uc2a4\ud1a0\ub9ac\uc9c0)",
        blocks=[
            Cards([
                ("s3a://lake/bronze/", "\uc6d0\ucc9c \uadf8\ub300\ub85c (append)"),
                ("s3a://lake/silver/", "\uc815\uc81c \u00b7 \uc911\ubcf5\uc81c\uac70 \u00b7 SCD"),
                ("s3a://lake/gold/", "\uc9d1\uacc4 \u00b7 \ub9c8\ud2b8 \u00b7 \ud53c\ucc98"),
                ("s3a://lake/docs/", "\ubb38\uc11c \u00b7 \uc774\ubbf8\uc9c0 \uc6d0\ubcf8 (RAG \uc785\ub825)"),
            ]),
            Rule(),
            Items(["Table Format : Iceberg Table"], lead=22),
            Items(["snapshot \u00b7 time-travel \u00b7 schema evol."], lead=19),
            Items(["Catalog : Iceberg REST Catalog"], lead=28),
        ],
    ),
    Box(
        key="processing", x=1100, y=140, w=330, h=260, ramp="purple",
        title="5. Processing &amp; Orchestration Layer",
        subtitle="Cloudera CDE",
        blocks=[],  # rendered from PROCESSING_LINES
    ),
    Box(
        key="federation", x=1100, y=440, w=330, h=530, ramp="amber",
        title="6. Data Federation Layer",
        subtitle="Starburst Trino",
        blocks=[
            Items(["Coordinator \u00d71 (HA)", "Worker \u00d7N (autoscale)"],
                  lead=26, step=21),
            Group("Connectors", [
                "\u251c Iceberg \u2192 MinIO",
                "\u251c Kafka \u2192 \uc2e4\uc2dc\uac04 \uc870\ud68c",
                "\u251c Hive \u2192 \ub808\uac70\uc2dc HDFS",
                "\u2514 Oracle \u2192 \ud398\ub354\ub808\uc774\uc158",
            ]),
            Group("AI Features", [
                "\u251c NL-to-SQL (AIDA)",
                "\u251c AI Agent \u00b7 AI Functions",
                "\u251c RAG",
                "\u2514 MCP Server",
            ]),
            Group("Model Provider", [
                "\u251c OpenAI \ud638\ud658 \uc5d4\ub4dc\ud3ec\uc778\ud2b8",
                "\u2514 \uc0ac\ub0b4 \ubaa8\ub378 \uc5f0\ub3d9 (on-prem)",
            ]),
            Group("Vector DB Support", [
                "\u251c Iceberg",
                "\u251c PostgreSQL / PGVector",
                "\u2514 Elasticsearch",
            ]),
        ],
    ),
    Box(
        key="consumption", x=1500, y=440, w=280, h=330, ramp="green",
        title="7. Consumption Layer",
        subtitle=None,
        blocks=[
            Group("Spotfire", [
                "\ub300\uc2dc\ubcf4\ub4dc \u00b7 Ad-hoc \ubd84\uc11d",
                "In-DB \ubaa8\ub4dc\ub85c Trino \uc9c1\uc811 \uc9c8\uc758",
            ]),
            Group("Cloudera AI", [
                "AI Workbench \u00b7 \ubaa8\ub378 \ud559\uc2b5",
                "AI Studio \u00b7 Agent Studio",
            ]),
            Items([
                "SQL Client (DBeaver)",
                "ML / Notebook (Jupyter)",
                "API",
            ], lead=34, step=24),
        ],
    ),
    Box(
        key="serving", x=1850, y=120, w=290, h=290, ramp="cyan",
        title="모델 서빙 (고객 보유 모델)",
        subtitle="OpenAI 호환 엔드포인트",
        blocks=[
            Group("Cloudera AI Inference Service", [
                "사내 추론 엔드포인트 (on-prem)",
                "OpenAI 호환 API",
            ]),
            Group("고객 보유 모델", [
                "생성 모델 (NL-to-SQL · 답변)",
                "임베딩 모델 (한국어)",
                "리랭커",
            ]),
            Note("외부 모델 API 호출 없음 · 전 구간 내부"),
        ],
    ),
    Box(
        key="agent", x=1850, y=440, w=290, h=330, ramp="rose",
        title="고객 AI Agent",
        subtitle="업무 질의 · 문서 조회",
        blocks=[
            Group("Agent 런타임", [
                "대화 세션 · 도구 호출 계획",
                "사용자 권한 위임 (impersonation)",
            ]),
            Group("도구 (MCP)", [
                "├ Starburst MCP Server",
                "├ 문서 검색 (Vector DB · RAG API)",
                "└ Argus Catalog (스키마 · 리니지) · KG",
            ]),
            Group("감사", [
                "질문 → 근거 → SQL → 답변 기록",
            ]),
        ],
    ),
    Box(
        key="catalog", x=360, y=1050, w=300, h=420, ramp="olive",
        title="Argus Catalog",
        subtitle="Data Catalog (FastAPI :4600) · Next.js UI",
        blocks=[
            Group("데이터 카탈로그", [
                "데이터셋 · 스키마 · 태그 · 소유자",
                "컬럼 리니지 · ERD · 표준 · 용어집",
            ]),
            Group("메타데이터 수집 (11종 플랫폼)", [
                "Trino · Hive · Kafka · S3 · Oracle · PG",
                "Metadata Sync (:4610) · Query Listener",
            ]),
            Group("데이터 품질", [
                "프로파일링 · 규칙 10종 · 점수 전파",
            ]),
            Group("거버넌스 · 검색", [
                "API · AI Agent 카탈로그 (도구 · MCP)",
                "하이브리드 검색 (pgvector) · 변경 관리",
            ]),
            Group("ML 모델 레지스트리", [
                "MLflow · OCI 호환 · 에어갭 모델 반입",
            ]),
        ],
    ),
    Box(
        key="rag", x=730, y=1050, w=300, h=420, ramp="plum",
        title="Argus RAG Studio",
        subtitle="RAG 백엔드 (FastAPI :4700) · Next.js UI",
        blocks=[
            Group("문서 반입 (Build)", [
                "스토리지 소스 : S3 호환 (읽기 전용)",
                "소스 워치 주기 스캔 · 문서 라우팅",
            ]),
            Group("인제스천 파이프라인", [
                "파싱 text · layout · docai · vlm · rhwp",
                "청킹 8종 → 임베딩 → 색인",
            ]),
            Group("검색 · 생성 · 평가", [
                "하이브리드 (벡터 + 렉시컬 + RRF) → 리랭크",
                "인용 답변 · 챗 (SSE) · 골든셋 평가",
            ]),
            Group("REST API", [
                "search · query · chat · federated",
                "JWT · Keycloak OIDC · API 키",
            ]),
            Note("임베딩 · 리랭커 · LLM 은 OpenAI 호환 → 모델 서빙 연동"),
        ],
    ),
    Box(
        key="vectordb", x=1100, y=1050, w=330, h=420, ramp="steel",
        title="Vector DB",
        subtitle="PostgreSQL + pgvector (기본)",
        blocks=[
            Group("저장 대상", [
                "청크 · 벡터 (1024d) · tsvector",
                "메타데이터 · 출처 경로 · 트레이스",
            ]),
            Group("교체 가능 백엔드 (VectorStore)", [
                "├ pgvector (기본)",
                "├ Qdrant · Weaviate · Milvus",
                "└ Databricks Vector Search",
            ]),
            Group("검색", [
                "벡터 (cosine · l2 · ip) + 렉시컬 (tsvector)",
                "RRF 융합 → 리랭커 (cross-encoder · LLM)",
            ]),
            Group("호출 주체", [
                "├ Argus RAG Studio (색인 · 검색)",
                "├ AI Agent (직접 조회)",
                "└ Starburst Trino (PostgreSQL 커넥터)",
            ]),
        ],
    ),
]

# The processing box has a nested tree shape, so it is described separately.
PROCESSING_LINES = [
    ("group", "Airflow (DAG \uc2a4\ucf00\uc904 \u00b7 \uc758\uc874\uc131 \u00b7 SLA)"),
    ("item", "\u251c NiFi \ud750\ub984 \ud2b8\ub9ac\uac70 (REST API)"),
    ("item", "\u251c Spark Job \uc81c\ucd9c"),
    ("item", "\u2514 Trino DDL / MERGE \uc2e4\ud589 (JDBC)"),
    ("group", "Spark on K8s"),
    ("item", "\u251c Bronze \u2192 Silver \u2192 Gold \ubcc0\ud658"),
    ("item", "\u2514 Iceberg MERGE \u00b7 Compaction"),
]

# --------------------------------------------------------------------------
# Edges
# --------------------------------------------------------------------------


@dataclass
class Edge:
    d: str
    color: str = INK
    dash: str | None = None
    both: bool = False
    label: str | None = None
    label_xy: tuple[int, int] | None = None


EDGES: list[Edge] = [
    Edge("M165 260 V100 H700 V200 H722", STREAM, "6 4",
         label="\uc2e4\uc2dc\uac04 \uc774\ubca4\ud2b8 \uc9c1\uacb0 : CDC \u00b7 MQ \u00b7 "
               "\ucc44\ub110 \ub85c\uadf8 \u00b7 FDS",
         label_xy=(340, 120)),
    Edge("M290 505 H352"),
    Edge("M660 320 H690 V240 H722"),
    Edge("M722 300 H706 V420 H668", STREAM, "6 4"),
    Edge("M660 600 H722"),
    Edge("M1030 250 H1092", STREAM, "6 4",
         label="Kafka \uc18c\ube44 \u2192 Spark Structured Streaming",
         label_xy=(1100, 128)),
    Edge("M1034 460 H1065 V300 H1092", both=True),
    Edge("M1030 650 H1092"),
    Edge("M1030 448 H1050 V422 H1460 V540 H1492", DIRECT,
         label="S3 API \uc9c1\uc811 \uc811\uadfc (\ud559\uc2b5 \ub370\uc774\ud130 \u00b7 "
               "\ubb38\uc11c \uc6d0\ubcf8)",
         label_xy=(1150, 414)),
    Edge("M1430 620 H1492", label="JDBC/ODBC", label_xy=(1436, 608)),
    Edge("M165 750 V990 H1075 V944 H1092", FEDERATE, "10 3 2 3",
         label="Multi Data Source\uc758 Data Federation",
         label_xy=(520, 980)),
    Edge("M1430 860 H1815 V412", MODEL,
         label="Model Provider \ud638\ucd9c",
         label_xy=(1500, 852)),
    Edge("M1900 772 V900 H1442", AGENT, both=True,
         label="MCP \u00b7 \uba54\ud0c0\ub370\uc774\ud130 \u00b7 SQL",
         label_xy=(1610, 892)),
    Edge("M1995 436 V412", MODEL,
         label="\ucd94\ub860 \ud638\ucd9c", label_xy=(2010, 431)),
    # RAG: MinIO docs/ -> RAG pipeline -> Vector DB -> AI Agent / Trino
    Edge("M880 870 V1042", DIRECT,
         label="\uc18c\uc2a4 \uc6cc\uce58 \uc2a4\uce94 (S3 API) : s3a://lake/docs/",
         label_xy=(893, 925)),
    Edge("M1030 1230 H1092", both=True,
         label="upsert \u00b7 \uac80\uc0c9", label_xy=(1034, 1218)),
    Edge("M1430 1150 H1990 V778", AGENT,
         label="Vector DB \uc9c1\uc811 \uc870\ud68c (Top-K) \u00b7 \uadfc\uac70 \ubb38\uc11c",
         label_xy=(1450, 1140)),
    Edge("M2060 772 V1500 H880 V1474", AGENT, both=True,
         label="Argus REST API (search \u00b7 query \u00b7 chat) \u00b7 API \ud0a4",
         label_xy=(1300, 1492)),
    Edge("M1265 1042 V978", both=True,
         label="\ubca1\ud130 \ud14c\uc774\ube14 \uc870\ud68c",
         label_xy=(1278, 1022)),
    # Data catalog: NiFi / Trino -> Argus Catalog -> AI Agent
    Edge("M600 750 V1042", CATALOG, "3 3",
         label="NiFi Flow \ub9ac\ub2c8\uc9c0 \u00b7 \uba54\ud0c0\ub370\uc774\ud130",
         label_xy=(418, 850)),
    Edge("M1140 974 V1015 H700 V1120 H668", CATALOG, "3 3",
         label="Trino Query Listener \u00b7 Metadata Sync",
         label_xy=(905, 1008)),
    Edge("M2100 772 V1522 H510 V1474", CATALOG, "3 3", both=True,
         label="Agent \ub4f1\ub85d \u00b7 \ubbf8\ud130\ub9c1 \u00b7 "
               "\uba54\ud0c0\ub370\uc774\ud130 API (URN)",
         label_xy=(700, 1541)),
]

LEGEND = [
    "\ubc30\uce58 \uacbd\ub85c : Source \u2192 CFM \u2192 MinIO   |   "
    "\uc2e4\uc2dc\uac04 \uacbd\ub85c : Source / CFM \u2192 Kafka(CDP) \u2192 "
    "CDE Spark Streaming \u2192 MinIO   |   \uc870\ud68c \uacbd\ub85c : "
    "Starburst Trino \u2192 Spotfire \u00b7 Cloudera AI   |   "
    "Agent \uacbd\ub85c : AI Agent \u2192 MCP \u2192 Starburst \u2192 "
    "\uc0ac\ub0b4 \ubaa8\ub378",
    "RAG \uacbd\ub85c : MinIO s3a://lake/docs/ \u2192 Argus RAG Studio "
    "\u2192 Vector DB \u2192 AI Agent (\uc9c1\uc811 \uc870\ud68c \ub610\ub294 "
    "Argus REST API) \u00b7 Starburst Trino   |   "
    "\uce74\ud0c8\ub85c\uadf8 \uacbd\ub85c : NiFi \u00b7 Trino \u2192 "
    "Argus Catalog (\uba54\ud0c0\ub370\uc774\ud130 \u00b7 \ub9ac\ub2c8\uc9c0) "
    "\u2194 AI Agent",
    "\uc2e4\uc120 = \uc0c1\uc2dc \ub370\uc774\ud130 \ud750\ub984   \u00b7   "
    "\uc8fc\ud669 \uc810\uc120 = \uc2a4\ud2b8\ub9ac\ubc0d \uacbd\ub85c   \u00b7   "
    "\ud30c\ub791 \uc2e4\uc120 = S3 \uc9c1\uc811 \uc811\uadfc   \u00b7   "
    "\ubcf4\ub77c \uc77c\uc810\uc1c4\uc120 = \uc6d0\ucc9c \uc9c1\uc811 "
    "\ud398\ub354\ub808\uc774\uc158   \u00b7   "
    "\uccad\ub85d \uc2e4\uc120 = \ubaa8\ub378 \ud638\ucd9c   \u00b7   "
    "\uc790\uc8fc \uc2e4\uc120 = Agent \ub3c4\uad6c \ud638\ucd9c   \u00b7   "
    "\uc62c\ub9ac\ube0c \uc810\uc120 = \uba54\ud0c0\ub370\uc774\ud130 "
    "\uc218\uc9d1 \u00b7 \ub9ac\ub2c8\uc9c0",
]

# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def text(x, y, s, size, fill, weight=None) -> str:
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}"{w} '
            f'fill="{fill}">{escape(s)}</text>')


def render_box(box: Box) -> list[str]:
    ramp = PALETTE[box.ramp]
    out = [
        f'<rect x="{box.x}" y="{box.y}" width="{box.w}" height="{box.h}" '
        f'rx="12" fill="{ramp.fill}" stroke="{ramp.stroke}" stroke-width="0.9"/>'
    ]
    tx = box.x + PAD_X
    inner_r = box.right - PAD_X
    cur = box.y + TITLE_DY
    out.append(f'<text x="{tx}" y="{cur}" font-size="{FS_BOX_TITLE}" '
               f'font-weight="500" fill="{ramp.title}">{box.title}</text>')
    if box.subtitle:
        cur += SUBTITLE_DY
        out.append(text(tx, cur, box.subtitle, FS_BOX_SUB, ramp.muted))
    cur += RULE_DY
    out.append(f'<line x1="{tx}" y1="{cur}" x2="{inner_r}" y2="{cur}" '
               f'stroke="{ramp.rule}" stroke-width="0.9"/>')

    if box.key == "processing":
        first = True
        for kind, line in PROCESSING_LINES:
            if kind == "group":
                cur += GROUP_LEAD if first else GROUP_GAP - 4
                out.append(text(tx, cur, line, FS_GROUP, ramp.body, "500"))
            else:
                cur += ITEM_LEAD if first else ITEM_STEP + 1
                out.append(text(tx + 14, cur, line, FS_ITEM, ramp.muted))
            first = False
        return out

    for block in box.blocks:
        if isinstance(block, Group):
            cur += GROUP_LEAD if block is box.blocks[0] else GROUP_GAP
            out.append(text(tx, cur, block.label, FS_GROUP, ramp.title, "500"))
            for i, item in enumerate(block.items):
                cur += ITEM_LEAD if i == 0 else ITEM_STEP
                out.append(text(tx + 14, cur, item, FS_ITEM, ramp.body))
        elif isinstance(block, Items):
            for i, item in enumerate(block.items):
                cur += block.lead if i == 0 else block.step
                out.append(text(tx, cur, item, 12, ramp.body))
        elif isinstance(block, Cards):
            cur += block.lead
            for path, caption in block.rows:
                out.append(
                    f'<rect x="{tx}" y="{cur}" width="{box.w - 2 * PAD_X + 10}" '
                    f'height="{block.height}" rx="7" fill="#FFFFFF" '
                    f'stroke="#B5D4F4" stroke-width="0.9"/>')
                out.append(text(tx + 14, cur + 22, path, 12, ramp.body))
                out.append(text(tx + 14, cur + 41, caption, 11, ramp.muted))
                cur += block.height + block.gap
            cur -= block.gap
        elif isinstance(block, Rule):
            cur += block.lead
            out.append(f'<line x1="{tx}" y1="{cur}" x2="{inner_r}" y2="{cur}" '
                       f'stroke="{ramp.rule}" stroke-width="0.9"/>')
        elif isinstance(block, Note):
            cur += block.lead
            out.append(text(tx, cur, block.text, FS_NOTE, ramp.muted))
    return out


def render_edge(e: Edge) -> list[str]:
    attrs = [f'd="{e.d}"', 'fill="none"', f'stroke="{e.color}"',
             'stroke-width="1.6"']
    if e.dash:
        attrs.append(f'stroke-dasharray="{e.dash}"')
    if e.both:
        attrs.append('marker-start="url(#arrow)"')
    attrs.append('marker-end="url(#arrow)"')
    out = [f'<path {" ".join(attrs)}/>']
    if e.label and e.label_xy:
        x, y = e.label_xy
        out.append(text(x, y, e.label, FS_EDGE, e.color))
    return out


def build() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" '
        f'height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'role="img" font-family="{FONT_STACK}">',
        f'<title>{TITLE}</title>',
        '<desc>Air-gapped modern lakehouse reference architecture, '
        'left to right: financial data sources, Cloudera CFM ingestion, '
        'Cloudera CDP streaming bus, MinIO storage with Iceberg, '
        'Cloudera CDE processing, Starburst Trino federation with an '
        'on-premises model provider, consumption, a customer AI agent '
        'calling Starburst over MCP, and internally served customer '
        'models. Along the bottom, Argus RAG Studio reads document '
        'originals from the MinIO docs zone over the S3 API, parses, '
        'chunks and embeds them, and writes the embeddings into a '
        'vector database (PostgreSQL + pgvector by default). The AI '
        'agent reaches the vectors either by querying the vector '
        'database directly or through the Argus REST API (search, '
        'query, chat); Starburst Trino exposes the same vectors as '
        'tables. Argus Catalog, the data catalog, collects metadata '
        'and lineage from NiFi flows and Trino queries and serves '
        'schemas, lineage and an AI agent registry to the customer '
        'agent.</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '</marker></defs>',
        f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'fill="{BACKGROUND}"/>',
        f'<text x="40" y="48" font-size="22" font-weight="500" '
        f'fill="#2C2C2A">{TITLE}</text>',
        text(40, 72, SUBTITLE, 13, INK),
    ]
    for e in EDGES:
        parts += render_edge(e)
    for box in BOXES:
        parts += render_box(box)

    parts.append(f'<line x1="40" y1="1580" x2="{CANVAS_W - 40}" y2="1580" '
                 f'stroke="{HAIRLINE}" stroke-width="0.9"/>')
    for i, line in enumerate(LEGEND):
        parts.append(text(40, 1600 + i * 18, line, 11, "#888780"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# PNG rasterisation
# --------------------------------------------------------------------------

PNG_SCALE = 2  # PNG 기본 폭 = CANVAS_W x PNG_SCALE


def _which(*names: str) -> str | None:
    """PATH 에서 첫 번째로 발견되는 실행 파일. 환경 변수 지정도 함께 확인한다."""
    for env in ("SVG_RENDERER", "CHROME_BIN", "CHROMIUM_BIN"):
        cand = os.environ.get(env)
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            if env == "SVG_RENDERER" or Path(cand).name in names:
                return cand
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


# Headless Chromium 은 창 높이에서 브라우저 UI 몫을 빼고 뷰포트를 잡는다.
# 캔버스가 잘리지 않도록 넉넉히 키워 렌더한 뒤 정확한 높이로 잘라낸다.
CHROME_VIEWPORT_PAD = 400


def _crop_png_rows(path: Path, keep: int) -> None:
    """PNG 의 위쪽 keep 행만 남기고 다시 쓴다 (표준 라이브러리만 사용)."""
    raw = path.read_bytes()
    pos, idat = 8, b""
    while pos < len(raw):
        ln = struct.unpack(">I", raw[pos:pos + 4])[0]
        typ, data = raw[pos + 4:pos + 8], raw[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", data[:10])
            rest = data[10:]
        elif typ == b"IDAT":
            idat += data
        pos += 12 + ln
    if depth != 8 or ctype not in (0, 2, 4, 6) or keep >= h:
        return
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    buf, stride = zlib.decompress(idat), w * bpp
    prev, rows, o = bytearray(stride), [], 0
    for _ in range(keep):
        f = buf[o]
        line = bytearray(buf[o + 1:o + 1 + stride])
        o += 1 + stride
        if f:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                if f == 1:
                    line[i] = (line[i] + a) & 255
                elif f == 2:
                    line[i] = (line[i] + b) & 255
                elif f == 3:
                    line[i] = (line[i] + (a + b) // 2) & 255
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    line[i] = (line[i] + (a if pa <= pb and pa <= pc
                                          else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        prev = line

    def chunk(typ: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBB", w, keep, depth, ctype) + rest)
        + chunk(b"IDAT", zlib.compress(
            b"".join(b"\x00" + r for r in rows), 9))
        + chunk(b"IEND", b""))


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def render_png(svg: Path, png: Path, width: int,
               canvas: tuple[int, int] = (CANVAS_W, CANVAS_H)) -> str:
    """SVG 를 PNG 로 래스터화하고 사용한 렌더러 이름을 반환한다.

    canvas 는 SVG 의 (폭, 높이). 설치된 렌더러가 하나도 없으면 RuntimeError 를
    발생시킨다.
    """
    cw, ch = canvas
    height = round(width * ch / cw)
    svg, png = svg.resolve(), png.resolve()

    if (exe := _which("rsvg-convert")):
        _run([exe, "-w", str(width), "-h", str(height),
              "-b", BACKGROUND, str(svg), "-o", str(png)])
        return "rsvg-convert"

    if (exe := _which("inkscape")):
        _run([exe, str(svg), "--export-type=png",
              f"--export-width={width}", f"--export-filename={png}"])
        return "inkscape"

    if (exe := _which("chromium", "chromium-browser", "chrome",
                      "google-chrome", "google-chrome-stable")):
        # SVG 를 단독 문서로 열면 body 기본 여백 때문에 하단이 잘린다.
        # 여백 0 인 HTML 에 인라인으로 넣어 캔버스 크기와 정확히 일치시킨다.
        with tempfile.TemporaryDirectory() as td:
            page = Path(td) / "page.html"
            page.write_text(
                '<!doctype html><meta charset="utf-8">'
                "<style>html,body{margin:0;padding:0;overflow:hidden;"
                f"background:{BACKGROUND}}}"
                f"svg{{display:block;width:{cw}px;height:{ch}px}}"
                "</style>" + svg.read_text(encoding="utf-8"),
                encoding="utf-8")
            scale = width / cw
            _run([exe, "--headless", "--disable-gpu", "--no-sandbox",
                  "--hide-scrollbars",
                  f"--default-background-color={BACKGROUND[1:]}FF",
                  f"--window-size={cw},{ch + CHROME_VIEWPORT_PAD}",
                  f"--force-device-scale-factor={scale:.4f}",
                  "--virtual-time-budget=3000",
                  f"--screenshot={png}", page.as_uri()])
        _crop_png_rows(png, round(ch * scale))
        return "chromium"

    try:
        import cairosvg  # type: ignore
    except ImportError:
        pass
    else:
        cairosvg.svg2png(url=str(svg), write_to=str(png),
                         output_width=width, output_height=height,
                         background_color=BACKGROUND)
        return "cairosvg"

    if (exe := _which("magick", "convert")):
        _run([exe, "-background", BACKGROUND, "-density", "192",
              str(svg), "-resize", f"{width}x", str(png)])
        return "imagemagick"

    raise RuntimeError(
        "PNG 를 만들 렌더러를 찾지 못했습니다. 다음 중 하나를 설치하십시오.\n"
        "  rsvg-convert (librsvg)  |  inkscape  |  chromium  |  "
        "python -m pip install cairosvg  |  imagemagick\n"
        "설치된 실행 파일 경로를 SVG_RENDERER 환경 변수로 직접 지정할 수도 있습니다.\n"
        "PNG 없이 SVG 만 생성하려면 --no-png 를 사용하십시오.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=Path,
                    default=Path("assets/lakehouse-architecture-lr.svg"),
                    help="SVG 출력 경로 (기본: assets/lakehouse-architecture-lr.svg)")
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
        renderer = render_png(args.output, png, args.png_width)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"PNG 생성 실패: {exc}", file=sys.stderr)
        raise SystemExit(1)
    height = round(args.png_width * CANVAS_H / CANVAS_W)
    print(f"wrote {png} ({args.png_width}x{height}, {renderer})")


if __name__ == "__main__":
    main()
