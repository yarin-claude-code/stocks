"""PDF report generator for stock rankings using ReportLab."""

from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── palette ──────────────────────────────────────────────────────────────────
BRAND_DARK = colors.HexColor("#0F172A")  # slate-900
BRAND_BLUE = colors.HexColor("#3B82F6")  # blue-500
BRAND_LIGHT = colors.HexColor("#F8FAFC")  # slate-50
ACCENT_GREEN = colors.HexColor("#22C55E")
ACCENT_RED = colors.HexColor("#EF4444")
GRAY = colors.HexColor("#64748B")


def _score_color(score: float) -> colors.Color:
    if score >= 70:
        return ACCENT_GREEN
    if score >= 40:
        return BRAND_BLUE
    return ACCENT_RED


def _fmt(val: float | None, suffix: str = "") -> str:
    if val is None:
        return "—"
    return f"{val:.1f}{suffix}"


def generate_rankings_pdf(
    domains: list[dict],
    best_overall: dict | None,
    generated_at: datetime,
) -> bytes:
    """Return PDF bytes for the given rankings data."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=BRAND_DARK,
        fontSize=22,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        textColor=GRAY,
        fontSize=10,
        spaceAfter=2,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        textColor=BRAND_DARK,
        fontSize=13,
        spaceBefore=16,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        textColor=GRAY,
        fontSize=8,
    )

    story = []

    # ── Header ─────────────────────────────────────────────────────────────
    story.append(Paragraph("📈 Smart Stock Ranker", title_style))
    story.append(Paragraph("Quantitative Rankings Report", subtitle_style))
    story.append(
        Paragraph(
            f"Generated: {generated_at.strftime('%B %d, %Y at %H:%M UTC')}",
            label_style,
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    # ── Best Overall ────────────────────────────────────────────────────────
    if best_overall:
        story.append(Paragraph("🏆 Best Overall Pick", section_style))
        score = best_overall["composite_score"]
        best_data = [
            ["Ticker", "Domain", "Score", "Rank"],
            [
                best_overall["ticker"],
                best_overall.get("domain", "—"),
                f"{score:.1f}",
                f"#{best_overall['rank']}",
            ],
        ]
        best_table = Table(best_data, colWidths=[3.5 * cm, 5 * cm, 3 * cm, 3 * cm])
        best_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, 1), BRAND_LIGHT),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (-1, 1), 13),
                    ("TEXTCOLOR", (2, 1), (2, 1), _score_color(score)),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUND", (0, 1), (-1, 1), BRAND_LIGHT),
                    ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(best_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Domain Rankings ─────────────────────────────────────────────────────
    for domain_data in domains:
        domain_name = domain_data["domain"]
        stocks = domain_data.get("top5", [])
        if not stocks:
            continue

        story.append(Paragraph(f"📊 {domain_name}", section_style))

        header = [
            "Rank",
            "Ticker",
            "Score",
            "Momentum",
            "Volume Δ",
            "Volatility",
            "Rel. Strength",
            "P/E Ratio",
        ]
        rows = [header]
        for s in stocks:
            f = s.get("factors", {})
            rows.append(
                [
                    f"#{s['rank']}",
                    s["ticker"],
                    f"{s['composite_score']:.1f}",
                    _fmt(f.get("momentum")),
                    _fmt(f.get("volume_change")),
                    _fmt(f.get("volatility")),
                    _fmt(f.get("relative_strength")),
                    _fmt(f.get("financial_ratio")),
                ]
            )

        col_w = [1.5 * cm, 2.5 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.8 * cm, 2.3 * cm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)

        ts = [
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        # Alternating rows
        for i, row in enumerate(rows[1:], 1):
            bg = BRAND_LIGHT if i % 2 == 0 else colors.white
            ts.append(("BACKGROUND", (0, i), (-1, i), bg))
            score_val = stocks[i - 1]["composite_score"]
            ts.append(("TEXTCOLOR", (2, i), (2, i), _score_color(score_val)))
            ts.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

        tbl.setStyle(TableStyle(ts))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

    # ── Footer ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY))
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "Scoring model: Momentum 30% · Volume Change 20% · Volatility 20% · "
            "Relative Strength 15% · Financial Ratio 15% · Scores 0–100 (higher = better)",
            label_style,
        )
    )
    story.append(
        Paragraph(
            "⚠ For informational purposes only. Not financial advice.",
            ParagraphStyle("Disclaimer", parent=label_style, textColor=ACCENT_RED),
        )
    )

    doc.build(story)
    return buf.getvalue()
