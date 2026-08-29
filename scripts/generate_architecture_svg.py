#!/usr/bin/env python3
"""Generate the air-gapped modern lakehouse architecture diagram as an SVG.

The diagram is described declaratively below (PALETTE / BOXES / ARROWS) and
rendered to a single self-contained SVG file with a white background.

Usage:
    python scripts/generate_architecture_svg.py
    python scripts/generate_architecture_svg.py -o assets/lakehouse-architecture-lr.svg
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

CANVAS_W = 1820
CANVAS_H = 1030
BACKGROUND = "#FFFFFF"

FONT_STACK = (
    "'Pretendard','Malgun Gothic','Apple SD Gothic Neo',"
    "'Noto Sans KR','Segoe UI',sans-serif"
)

TITLE = "Lakehouse Reference Architecture"
SUBTITLE = (
    "Cloudera CFM \u00b7 CDP \u00b7 CDE  |  Starburst Trino  |  MinIO  |  "
    "Spotfire \u00b7 Cloudera AI"
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
}

INK = "#5F5E5A"          # neutral flow lines
STREAM = "#993C1D"       # streaming (dashed)
DIRECT = "#185FA5"       # S3 direct access
FEDERATE = "#534AB7"     # source-level federation
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
# The seven layers
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
                ("s3a://lake/docs/", "\ubb38\uc11c \u00b7 \uc774\ubbf8\uc9c0 \u00b7 \uc784\ubca0\ub529 (RAG)"),
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
        key="federation", x=1100, y=440, w=330, h=440, ramp="amber",
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
                "\u251c NL-to-SQL",
                "\u251c RAG",
                "\u2514 MCP Server",
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
                "AI Workbench \u00b7 \ubaa8\ub378 \ud559\uc2b5 / \uc11c\ube59",
                "AI Studio \u00b7 Agent",
            ]),
            Items([
                "SQL Client (DBeaver)",
                "ML / Notebook (Jupyter)",
                "API",
            ], lead=34, step=24),
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
    Edge("M1430 620 H1492", label="JDBC / ODBC", label_xy=(1436, 610)),
    Edge("M165 750 V940 H1265 V884", FEDERATE, "10 3 2 3",
         label="Multi Data Source\uc758 Data Federation",
         label_xy=(520, 930)),
]

LEGEND = [
    "\ubc30\uce58 \uacbd\ub85c : Source \u2192 CFM \u2192 MinIO   |   "
    "\uc2e4\uc2dc\uac04 \uacbd\ub85c : Source / CFM \u2192 Kafka(CDP) \u2192 "
    "CDE Spark Streaming \u2192 MinIO   |   \uc870\ud68c \uacbd\ub85c : "
    "Starburst Trino \u2192 Spotfire \u00b7 Cloudera AI",
    "\uc2e4\uc120 = \uc0c1\uc2dc \ub370\uc774\ud130 \ud750\ub984   \u00b7   "
    "\uc8fc\ud669 \uc810\uc120 = \uc2a4\ud2b8\ub9ac\ubc0d \uacbd\ub85c   \u00b7   "
    "\ud30c\ub791 \uc2e4\uc120 = S3 \uc9c1\uc811 \uc811\uadfc   \u00b7   "
    "\ubcf4\ub77c \uc77c\uc810\uc1c4\uc120 = \uc6d0\ucc9c \uc9c1\uc811 \ud398\ub354\ub808\uc774\uc158",
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
        'Cloudera CDE processing, Starburst Trino federation, '
        'and consumption.</desc>',
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

    parts.append(f'<line x1="40" y1="970" x2="{CANVAS_W - 40}" y2="970" '
                 f'stroke="{HAIRLINE}" stroke-width="0.9"/>')
    for i, line in enumerate(LEGEND):
        parts.append(text(40, 990 + i * 18, line, 11, "#888780"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", type=Path,
                    default=Path("assets/lakehouse-architecture-lr.svg"))
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
