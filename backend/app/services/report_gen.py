"""
VeriGreen AI — PDF report and badge generation using ReportLab.

Generates:
  • A multi-page audit report PDF with title page, summary, and claim details.
  • Single-page badge PDFs for individual claims.
"""

from __future__ import annotations

import json
import os
from xml.sax.saxutils import escape
from datetime import datetime, timezone
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def _score_color(score: int) -> colors.Color:
    """Return a colour representing credibility score (1=red … 5=green)."""
    palette = {
        1: colors.HexColor("#e74c3c"),
        2: colors.HexColor("#e67e22"),
        3: colors.HexColor("#f1c40f"),
        4: colors.HexColor("#2ecc71"),
        5: colors.HexColor("#27ae60"),
    }
    return palette.get(score, colors.gray)


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generates audit report PDFs and claim badge PDFs."""

    def generate_report(
        self,
        audit_id: str,
        company: str,
        claims: list[dict[str, Any]],
        output_path: str,
        report_year: Optional[str] = None,
    ) -> str:
        """Create a multi-page audit report PDF.

        Args:
            audit_id: Unique audit identifier.
            company: Company name.
            claims: List of claim dicts (from DB rows).
            output_path: Where to save the PDF.
            report_year: Optional reporting period.

        Returns:
            The output file path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )
        styles = getSampleStyleSheet()
        story: list[Any] = []

        th_style = ParagraphStyle(
            "ReportTableHead",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
        )
        cell_style = ParagraphStyle(
            "ReportTableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#2c3e50"),
        )
        cell_center_style = ParagraphStyle(
            "ReportTableCellCenter",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#2c3e50"),
            alignment=1,
        )

        def score_paragraph(val: int) -> Paragraph:
            color = _score_color(val)
            s_style = ParagraphStyle(
                f"Score_{val}",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=11,
                textColor=color,
                alignment=1,
            )
            return Paragraph(f"<b>{val}/5</b>", s_style)

        # --- Title page ---
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=24,
            spaceAfter=20,
        )
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph("VeriGreen AI — ESG Audit Report", title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"<b>Company:</b> {escape(company)}", styles["Normal"]))
        if report_year:
            story.append(Paragraph(f"<b>Report Year:</b> {escape(report_year)}", styles["Normal"]))
        story.append(Paragraph(f"<b>Audit ID:</b> {audit_id}", styles["Normal"]))
        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.now(timezone.utc).isoformat()}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 1 * cm))

        # --- Summary ---
        pillar_scores: dict[str, list[int]] = {}
        total = len(claims)
        flagged = 0
        for c in claims:
            fs = c.get("final_score") or c.get("score", 3)
            pillar = c.get("pillar", "Unknown")
            pillar_scores.setdefault(pillar, []).append(fs)
            if fs <= 3:
                flagged += 1

        story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
        summary_data = [
            [Paragraph("<b>Metric</b>", th_style), Paragraph("<b>Value</b>", th_style)],
            [Paragraph("Total Claims", cell_style), Paragraph(str(total), cell_style)],
            [Paragraph("Flagged (score ≤ 3)", cell_style), Paragraph(str(flagged), cell_style)],
            [Paragraph("Verified (score ≥ 4)", cell_style), Paragraph(str(total - flagged), cell_style)],
        ]
        for pillar, scores in sorted(pillar_scores.items()):
            avg = round(sum(scores) / len(scores), 2) if scores else 0
            summary_data.append([
                Paragraph(f"Avg — {escape(pillar)}", cell_style),
                Paragraph(str(avg), cell_style),
            ])

        t = Table(summary_data, colWidths=[8 * cm, 5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 1 * cm))

        # --- Claims table ---
        story.append(Paragraph("<b>Claims Detail</b>", styles["Heading2"]))
        claims_header = [
            Paragraph("<b>#</b>", th_style),
            Paragraph("<b>Pillar</b>", th_style),
            Paragraph("<b>Score</b>", th_style),
            Paragraph("<b>Claim</b>", th_style),
            Paragraph("<b>Reason / Evidence Finding</b>", th_style),
        ]
        claims_data = [claims_header]
        for i, c in enumerate(claims, 1):
            fs = int(c.get("final_score") or c.get("score", 0))
            claim_text = escape(str(c.get("text", "")))
            reason_str = escape(str(c.get("reason") or ""))
            verdict_str = c.get("verdict")
            if verdict_str:
                verdict_badge = f"<b>[{escape(verdict_str)}]</b> "
            else:
                verdict_badge = ""

            claims_data.append([
                Paragraph(str(i), cell_center_style),
                Paragraph(escape(str(c.get("pillar", ""))), cell_style),
                score_paragraph(fs),
                Paragraph(claim_text, cell_style),
                Paragraph(f"{verdict_badge}{reason_str}", cell_style),
            ])

        ct = Table(claims_data, colWidths=[0.8 * cm, 2.4 * cm, 1.3 * cm, 7.5 * cm, 6.0 * cm], repeatRows=1)
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(ct)

        doc.build(story)
        return output_path

    def generate_badge(
        self,
        claim: dict[str, Any],
        output_path: str,
    ) -> str:
        """Create a single-page badge PDF for a claim.

        Args:
            claim: Claim dict (from DB row or schema).
            output_path: Where to save the badge PDF.

        Returns:
            The output file path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=(10 * cm, 14 * cm),
            leftMargin=0.5 * cm,
            rightMargin=0.5 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.5 * cm,
        )
        styles = getSampleStyleSheet()
        story: list[Any] = []

        score = claim.get("final_score") or claim.get("score", 0)
        sc = _score_color(score)

        badge_title = ParagraphStyle(
            "BadgeTitle", parent=styles["Title"], fontSize=14, textColor=sc,
        )
        story.append(Paragraph("VeriGreen Trust Badge", badge_title))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph(
            f"<b>Pillar:</b> {claim.get('pillar', 'N/A')}", styles["Normal"],
        ))
        story.append(Paragraph(
            f"<b>Score:</b> {score}/5", styles["Normal"],
        ))
        story.append(Spacer(1, 0.3 * cm))

        claim_text = claim.get("text", "N/A")[:200]
        story.append(Paragraph(f"<i>\"{escape(claim_text)}\"</i>", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

        citations_raw = claim.get("citations", "[]")
        if isinstance(citations_raw, str):
            try:
                citations = json.loads(citations_raw)
            except json.JSONDecodeError:
                citations = []
        else:
            citations = citations_raw
        if citations:
            story.append(Paragraph("<b>Citations:</b>", styles["Normal"]))
            for cit in citations:
                story.append(Paragraph(f"• {escape(str(cit))}", styles["Normal"]))

        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            f"<font size=7>Generated {datetime.now(timezone.utc).isoformat()}</font>",
            styles["Normal"],
        ))

        doc.build(story)
        return output_path
