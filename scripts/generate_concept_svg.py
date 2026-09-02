#!/usr/bin/env python3
"""초보자용 Lakehouse 개념도를 SVG(+PNG)로 생성한다.

엔지니어용 상세도(generate_architecture_svg.py)와 같은 팔레트·폰트·PNG 렌더러를
공유하되, 제품명 대신 "데이터가 흘러가는 길"을 일상어로 설명하는 그림이다.

  위 줄 : 데이터가 생겨서 쓰이기까지의 6단계
  아래 줄 : AI 비서(Agent)가 질문에 답을 찾는 4단계

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
    BACKGROUND, FONT_STACK, HAIRLINE, INK, PALETTE, PNG_SCALE, render_png, text,
)

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

CANVAS_W = 2180
CANVAS_H = 960

TITLE = "한눈에 보는 Lakehouse — 데이터가 흘러가는 길"
SUBTITLE = ("금융권 폐쇄망 데이터 플랫폼 개념도 (초보자용)  ·  "
            "괄호 안 영문은 실제 제품명  ·  기술 상세는 lakehouse-architecture-lr.svg")

ENCLOSURE = "사내망 (폐쇄망) — 아래 모든 구성요소는 외부 인터넷과 연결되지 않은 우리 회사 안에서 동작합니다"

# --------------------------------------------------------------------------
# Cards
# --------------------------------------------------------------------------


@dataclass
class Card:
    ramp: str
    title: str
    tagline: list[str]            # 1~2줄 한 줄 설명
    bullets: list[str]
    product: str                  # 카드 하단의 실제 제품명
    x: int = 0
    y: int = 0
    w: int = 290
    h: int = 400
    number: int | None = None

    @property
    def right(self) -> int:
        return self.x + self.w


# 위 줄 — 데이터가 흘러가는 길
FLOW_Y, FLOW_H, FLOW_W, FLOW_GAP, FLOW_X0 = 190, 330, 290, 60, 70

FLOW: list[Card] = [
    Card("gray", "데이터가 생기는 곳",
         ["은행 업무에서 매일 쌓이는", "기록들입니다"],
         ["계좌 · 대출 거래 (계정계)",
          "카드 승인 · 결제 내역",
          "앱 · ATM · 콜센터 이용 기록",
          "외부 기관 전문 · 시세",
          "약관 · 규정 같은 문서"],
         "Oracle · DB2 · 파일 · MQ"),
    Card("teal", "모으기",
         ["흩어진 데이터를 한 길로", "모아 옵니다"],
         ["매일 밤 한꺼번에 (배치)",
          "생기는 즉시 바로 (실시간)",
          "형식 통일 · 빠진 것 확인",
          "어디서 왔는지 이력 기록"],
         "Cloudera CFM (NiFi) · Kafka"),
    Card("blue", "쌓아두기",
         ["한 창고에 단계별로", "정리해 보관합니다"],
         ["원본 그대로 (Bronze)",
          "깨끗이 정리한 것 (Silver)",
          "바로 쓰는 요약본 (Gold)",
          "문서 · 이미지 원본",
          "과거 시점으로 되돌아보기 가능"],
         "MinIO (S3 호환) + Iceberg"),
    Card("purple", "다듬기",
         ["정해진 일정에 따라", "정리하고 계산합니다"],
         ["중복 제거 · 오류 정정",
          "부서별 · 상품별 집계",
          "'매일 새벽 3시' 같은 일정",
          "앞 단계가 끝나야 다음 단계"],
         "Cloudera CDE (Spark · Airflow)"),
    Card("amber", "찾아 쓰기",
         ["어디에 있든 한 창구에서", "물어봅니다"],
         ["창고 + 원천을 하나의 창구로",
          "SQL 한 번에 여러 저장소 조회",
          "누가 무엇을 볼 수 있는지 통제",
          "말로 물으면 SQL로 바꿔 줌"],
         "Starburst Trino"),
    Card("green", "활용하기",
         ["사람과 AI가", "답을 얻는 곳입니다"],
         ["대시보드 · 리포트",
          "분석가의 노트북 · SQL",
          "AI 비서에게 말로 질문",
          "→ 아래 'AI 비서' 흐름 참고"],
         "Spotfire · Cloudera AI · AI Agent"),
]

# 아래 줄 — AI 비서가 답을 찾는 길
AI_TITLE = "AI 비서(Agent)는 어떻게 답을 찾나요?"
AI_Y, AI_H, AI_W, AI_GAP, AI_X0 = 610, 250, 440, 60, 80

AI_FLOW: list[Card] = [
    Card("olive", "참고 자료 준비",
         ["AI가 볼 자료를 미리 정리해 둡니다"],
         ["데이터 사전 — 어떤 데이터가 어디에, 무슨 뜻인지",
          "문서 검색 준비 — 약관·규정을 잘게 나눠 의미로 찾게",
          "나눈 문서 조각을 검색용 저장소에 보관"],
         "Argus Catalog · Argus RAG Studio · Vector DB"),
    Card("rose", "AI 비서가 근거 찾기",
         ["질문을 이해하고 필요한 자료를 모읍니다"],
         ["관련 문서 조각 찾기 (RAG)",
          "데이터 창구(⑤)에 SQL로 수치 조회",
          "질문한 사람의 권한 범위 안에서만"],
         "고객 AI Agent (MCP 도구)"),
    Card("cyan", "사내 AI 모델이 답 쓰기",
         ["모은 근거로 답변을 만듭니다"],
         ["회사 안에서 돌아가는 모델 — 외부로 보내지 않음",
          "답변 작성 · 요약 · SQL 생성 · 문서 이해",
          "한국어 모델을 회사가 직접 보유"],
         "Cloudera AI Inference (OpenAI 호환)"),
    Card("steel", "답변과 기록",
         ["사람에게 답을 주고 과정을 남깁니다"],
         ["답 + 근거 문서 + 사용한 SQL을 함께 제시",
          "질문 → 근거 → 답변 전 과정을 감사 기록",
          "잘못된 답은 피드백으로 개선"],
         "감사 로그 · 피드백"),
]

FS_CARD_TITLE = 21
FS_TAGLINE = 13.5
FS_BULLET = 13.5
FS_PRODUCT = 11.5

# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def block_arrow(x: int, y: int, w: int = 48) -> str:
    """카드 사이의 굵은 오른쪽 화살표. x=왼쪽 끝, y=세로 중심."""
    hx = x + w - 22
    return (f'<path d="M{x} {y - 11} H{hx} V{y - 22} L{x + w} {y} '
            f'L{hx} {y + 22} V{y + 11} H{x} Z" fill="{HAIRLINE}"/>')


def render_card(c: Card) -> list[str]:
    ramp = PALETTE[c.ramp]
    out = [
        f'<rect x="{c.x}" y="{c.y}" width="{c.w}" height="{c.h}" rx="16" '
        f'fill="{ramp.fill}" stroke="{ramp.stroke}" stroke-width="1.2"/>'
    ]
    pad = 22
    tx = c.x + pad
    cur = c.y + 46
    if c.number is not None:
        cx, cy = c.x + pad + 16, c.y + 38
        out.append(f'<circle cx="{cx}" cy="{cy}" r="17" fill="{ramp.stroke}"/>')
        out.append(f'<text x="{cx}" y="{cy + 6}" font-size="16" font-weight="600" '
                   f'fill="#FFFFFF" text-anchor="middle">{c.number}</text>')
        tx_title = tx + 44
    else:
        tx_title = tx
    out.append(text(tx_title, cur, c.title, FS_CARD_TITLE, ramp.title, "600"))
    cur += 14
    for line in c.tagline:
        cur += 20
        out.append(text(tx, cur, line, FS_TAGLINE, ramp.muted))
    cur += 16
    out.append(f'<line x1="{tx}" y1="{cur}" x2="{c.right - pad}" y2="{cur}" '
               f'stroke="{ramp.rule}" stroke-width="1"/>')
    for b in c.bullets:
        cur += 27
        out.append(f'<circle cx="{tx + 4}" cy="{cur - 5}" r="3" fill="{ramp.stroke}"/>')
        out.append(text(tx + 16, cur, b, FS_BULLET, ramp.body))
    # 하단 제품명 pill
    py = c.y + c.h - 44
    out.append(f'<rect x="{tx}" y="{py}" width="{c.w - 2 * pad}" height="28" rx="14" '
               f'fill="#FFFFFF" stroke="{ramp.rule}" stroke-width="1"/>')
    out.append(text(tx + 14, py + 18, f"실제 제품 · {c.product}", FS_PRODUCT, ramp.muted))
    return out


def layout() -> None:
    for i, c in enumerate(FLOW):
        c.x, c.y, c.w, c.h = FLOW_X0 + i * (FLOW_W + FLOW_GAP), FLOW_Y, FLOW_W, FLOW_H
        c.number = i + 1
    for i, c in enumerate(AI_FLOW):
        c.x, c.y, c.w, c.h = AI_X0 + i * (AI_W + AI_GAP), AI_Y, AI_W, AI_H
        c.number = i + 1


def build() -> str:
    layout()
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" '
        f'height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'role="img" font-family="{FONT_STACK}">',
        f'<title>{TITLE}</title>',
        '<desc>Beginner-friendly concept view of the air-gapped lakehouse: '
        'six plain-language steps from where data is born to where people '
        'and AI use it, and four steps showing how the AI assistant '
        'prepares references, gathers evidence, writes an answer with an '
        'in-house model, and records the whole process.</desc>',
        f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="{BACKGROUND}"/>',
        f'<text x="40" y="52" font-size="26" font-weight="600" fill="#2C2C2A">{TITLE}</text>',
        text(40, 80, SUBTITLE, 13, INK),
        # 폐쇄망 울타리
        f'<rect x="40" y="112" width="{CANVAS_W - 80}" height="{CANVAS_H - 160}" rx="22" '
        f'fill="none" stroke="#9B2D4F" stroke-width="1.4" stroke-dasharray="10 6"/>',
        f'<rect x="60" y="100" width="{CANVAS_W - 120}" height="26" fill="{BACKGROUND}"/>',
        text(72, 118, "🔒 " + ENCLOSURE, 14, "#9B2D4F", "500"),
        text(70, 166, "데이터가 흘러가는 길", 19, "#2C2C2A", "600"),
    ]
    for i, c in enumerate(FLOW):
        parts += render_card(c)
        if i < len(FLOW) - 1:
            parts.append(block_arrow(c.right + 6, c.y + c.h // 2))

    parts.append(f'<line x1="70" y1="{AI_Y - 66}" x2="{CANVAS_W - 70}" y2="{AI_Y - 66}" '
                 f'stroke="{HAIRLINE}" stroke-width="1"/>')
    parts.append(text(70, AI_Y - 26, AI_TITLE, 19, "#2C2C2A", "600"))
    for i, c in enumerate(AI_FLOW):
        parts += render_card(c)
        if i < len(AI_FLOW) - 1:
            parts.append(block_arrow(c.right + 6, c.y + c.h // 2))

    parts.append(text(40, CANVAS_H - 22,
                      "위 줄의 ③ 창고에 보관한 문서와 ⑤ 창구의 데이터를 아래 줄의 AI 비서가 "
                      "함께 사용합니다.   ·   화살표 = 데이터·정보가 넘어가는 방향",
                      12, "#888780"))
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
