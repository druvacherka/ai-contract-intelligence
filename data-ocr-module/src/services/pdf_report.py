"""
PDF report generator — produces professional contract analysis reports.

Uses *fpdf2* (FPDF) to build a multi-section PDF and saves it into
``Config.REPORTS_DIR``.  Handles unicode text by falling back to latin-1
for characters outside the basic latin range.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.config import Config
from src.utils.logger import logger

# Optional import — fpdf2
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None  # type: ignore[assignment,misc]
    logger.warning("fpdf2 is not installed — PDF report generation disabled")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_text(text: str) -> str:
    """Encode *text* to latin-1 with replacement so FPDF never crashes."""
    if not text:
        return ""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _risk_color(level: str) -> tuple[int, int, int]:
    """Return an RGB tuple for the given risk level."""
    level_lower = (level or "").lower()
    if level_lower == "high":
        return (220, 53, 69)    # red
    if level_lower == "medium":
        return (255, 165, 0)    # orange
    return (40, 167, 69)        # green


# ---------------------------------------------------------------------------
# PDF Builder
# ---------------------------------------------------------------------------

class _ContractReportPDF(FPDF if FPDF else object):  # type: ignore[misc]
    """Custom FPDF subclass with header / footer branding."""

    def __init__(self) -> None:
        if FPDF is None:
            raise RuntimeError("fpdf2 is not installed")
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    # --- header ---
    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, _safe_text("IntelliAnalyze AI — Analysis Report"), align="L")
        self.ln(4)
        self.set_draw_color(41, 128, 185)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(6)

    # --- footer ---
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # --- convenience writers ---
    def section_title(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, _safe_text(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(220, 220, 220)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(3)

    def label_value(self, label: str, value: str) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(50, 7, _safe_text(label + ":"))
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 7, _safe_text(str(value)))
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(6, 6, _safe_text("\u2022"))
        self.multi_cell(0, 6, _safe_text(text))
        self.ln(1)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_report(contract_data: dict[str, Any]) -> str:
    """
    Build a professional PDF report from *contract_data* and return the
    absolute file path.

    Raises ``RuntimeError`` if *fpdf2* is not installed.
    """
    if FPDF is None:
        raise RuntimeError("fpdf2 is not installed — cannot generate PDF report")

    pdf = _ContractReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # ── Title ──────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 14, _safe_text("Contract Analysis Report"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # ── Metadata ───────────────────────────────────────────────────
    pdf.section_title("Contract Metadata")
    pdf.label_value("Filename", contract_data.get("filename", "N/A"))
    pdf.label_value("Document Type", contract_data.get("document_type", "N/A"))
    pdf.label_value("Pages", str(contract_data.get("pages", "N/A")))
    pdf.label_value("Processing Method", contract_data.get("processing_method", "N/A"))
    pdf.label_value(
        "Analysis Date",
        contract_data.get("created_at", datetime.now(timezone.utc).isoformat()),
    )
    file_mb = contract_data.get("file_size_mb") or contract_data.get("original_size_mb")
    if file_mb:
        pdf.label_value("File Size", f"{file_mb} MB")
    proc_time = contract_data.get("processing_time_seconds")
    if proc_time:
        pdf.label_value("Processing Time", f"{proc_time:.2f}s")

    # ── Executive Summary ──────────────────────────────────────────
    ai_summary = contract_data.get("ai_summary")
    if ai_summary:
        pdf.section_title("Executive Summary")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, _safe_text(ai_summary))
        pdf.ln(2)

    # ── Detected Entities ──────────────────────────────────────────
    entities = contract_data.get("entities", {})
    if entities and any(entities.values()):
        pdf.section_title("Detected Entities")
        entity_categories = [
            ("Organizations", entities.get("organizations", [])),
            ("Persons", entities.get("persons", [])),
            ("Dates", entities.get("dates", [])),
            ("Monetary Values", entities.get("money", [])),
            ("Jurisdictions", entities.get("jurisdictions", [])),
        ]
        # Table header
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(50, 8, "Category", border=1, fill=True)
        pdf.cell(0, 8, "Values", border=1, fill=True,
                 new_x="LMARGIN", new_y="NEXT")
        # Rows
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        for idx, (cat, vals) in enumerate(entity_categories):
            if not vals:
                continue
            fill = idx % 2 == 0
            if fill:
                pdf.set_fill_color(240, 248, 255)
            vals_text = ", ".join(str(v) for v in vals[:10])
            if len(vals) > 10:
                vals_text += f" … (+{len(vals) - 10} more)"
            pdf.cell(50, 7, _safe_text(cat), border=1, fill=fill)
            pdf.cell(0, 7, _safe_text(vals_text), border=1, fill=fill,
                     new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ── Clause Analysis ────────────────────────────────────────────
    clauses = contract_data.get("clauses", [])
    if clauses:
        pdf.section_title("Clause Analysis")
        # Table header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(55, 8, "Clause Type", border=1, fill=True)
        pdf.cell(30, 8, "Confidence", border=1, fill=True)
        pdf.cell(30, 8, "Risk Score", border=1, fill=True)
        pdf.cell(0, 8, "Risk Level", border=1, fill=True,
                 new_x="LMARGIN", new_y="NEXT")
        # Rows
        pdf.set_font("Helvetica", "", 9)
        for idx, clause in enumerate(clauses):
            fill = idx % 2 == 0
            if fill:
                pdf.set_fill_color(240, 248, 255)

            clause_type = clause.get("type", "Unknown")
            confidence = clause.get("confidence", 0)
            risk_score = clause.get("risk_score", 0)
            risk_level = clause.get("risk_level", "Low")

            pdf.set_text_color(30, 30, 30)
            pdf.cell(55, 7, _safe_text(clause_type), border=1, fill=fill)
            pdf.cell(30, 7, f"{confidence:.1f}%", border=1, fill=fill)
            pdf.cell(30, 7, f"{risk_score:.1f}", border=1, fill=fill)

            r, g, b = _risk_color(risk_level)
            pdf.set_text_color(r, g, b)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 7, _safe_text(risk_level), border=1, fill=fill,
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
        pdf.ln(3)

    # ── Risk Assessment ────────────────────────────────────────────
    pdf.section_title("Risk Assessment")
    overall_score = contract_data.get("overall_risk_score",
                                      contract_data.get("risk_score", 0))
    overall_level = contract_data.get("overall_risk_level",
                                      contract_data.get("risk_level", "Low"))

    pdf.set_font("Helvetica", "B", 12)
    r, g, b = _risk_color(overall_level)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 10,
             _safe_text(f"Overall Risk: {overall_score:.1f}/100 ({overall_level})"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    risk_factors = contract_data.get("risk_factors", [])
    if risk_factors:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 7, "Risk Factors:", new_x="LMARGIN", new_y="NEXT")
        for rf in risk_factors:
            if isinstance(rf, dict):
                rf_text = rf.get("description", str(rf))
            else:
                rf_text = str(rf)
            pdf.bullet(rf_text)
        pdf.ln(2)

    # ── Missing Clauses ────────────────────────────────────────────
    missing = contract_data.get("missing_clauses", [])
    if missing:
        pdf.section_title("Missing Clauses")
        for mc in missing:
            if isinstance(mc, dict):
                mc_text = mc.get("clause", str(mc))
            else:
                mc_text = str(mc)
            pdf.bullet(mc_text)
        pdf.ln(2)

    # ── Key Findings ───────────────────────────────────────────────
    findings = contract_data.get("key_findings", [])
    if findings:
        pdf.section_title("Key Findings")
        for finding in findings:
            if isinstance(finding, dict):
                finding_text = finding.get("finding", str(finding))
            else:
                finding_text = str(finding)
            pdf.bullet(finding_text)
        pdf.ln(2)

    # ── Recommendations ────────────────────────────────────────────
    recommendations = contract_data.get("recommendations", [])
    if recommendations:
        pdf.section_title("Recommendations")
        for rec in recommendations:
            if isinstance(rec, dict):
                rec_text = rec.get("recommendation", str(rec))
            else:
                rec_text = str(rec)
            pdf.bullet(rec_text)
        pdf.ln(2)

    # ── Completeness Score ─────────────────────────────────────────
    completeness = contract_data.get("completeness_score")
    if completeness is not None:
        pdf.section_title("Completeness Score")
        pdf.set_font("Helvetica", "B", 14)
        score_val = float(completeness)
        if score_val >= 80:
            pdf.set_text_color(40, 167, 69)
        elif score_val >= 50:
            pdf.set_text_color(255, 165, 0)
        else:
            pdf.set_text_color(220, 53, 69)
        pdf.cell(0, 10, f"{score_val:.0f}%", new_x="LMARGIN", new_y="NEXT")

    # ── Save ───────────────────────────────────────────────────────
    Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    contract_id = contract_data.get("id", contract_data.get("document_id", "unknown"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"report_{contract_id}_{timestamp}.pdf"
    filepath = Config.REPORTS_DIR / filename

    pdf.output(str(filepath))
    logger.info("PDF report generated: {}", filepath)

    return str(filepath)
