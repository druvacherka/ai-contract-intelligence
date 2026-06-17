"""
Compiler Agent — Final Report Assembly (Agent 7).

Compiles all outputs from the previous six agents into a single
structured report, calculates contract completeness, and identifies
missing clause types.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.agents.base_agent import BaseAgent
from src.utils.logger import logger

# All 10 clause types the system recognises
ALL_CLAUSE_TYPES: list[str] = [
    "Termination",
    "Confidentiality",
    "Liability",
    "Arbitration",
    "Governing Law",
    "Payment Terms",
    "Warranty",
    "Renewal",
    "Indemnification",
    "Non-Compete",
]


class CompilerAgent(BaseAgent):
    """Agent 7 — Final report compiler.

    Aggregates all preceding agent outputs into a single structured
    report dictionary, adds completeness scoring, and identifies
    missing clause types.

    Context contract:

    * **Input:** Full pipeline context with outputs from agents 1-6.
    * **Output adds:** ``{missing_clauses, completeness_score,
      compiled_report}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "CompilerAgent"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        clauses: list[dict[str, Any]] = context.get("clauses", [])

        # Determine found vs missing clause types
        found_types: set[str] = {c["type"] for c in clauses if c.get("type")}
        missing_clauses: list[str] = [
            ct for ct in ALL_CLAUSE_TYPES if ct not in found_types
        ]
        completeness_score: int = int(
            (len(found_types) / len(ALL_CLAUSE_TYPES)) * 100
        )

        # Compile final report
        compiled_report: dict[str, Any] = {
            # --- Metadata ---
            "metadata": {
                "file_path": context.get("file_path", ""),
                "filename": context.get("filename", ""),
                "file_ext": context.get("file_ext", ""),
                "analysed_at": datetime.now(timezone.utc).isoformat(),
            },
            # --- OCR / Extraction ---
            "extraction": {
                "ocr_method": context.get("ocr_method", ""),
                "ocr_confidence": context.get("ocr_confidence", 0.0),
                "pages": context.get("pages", 0),
                "raw_text_length": len(context.get("raw_text", "")),
            },
            # --- Cleaned Text ---
            "text_stats": {
                "clean_text_length": context.get("char_count", 0),
                "word_count": context.get("word_count", 0),
                "sentence_count": len(context.get("sentences", [])),
                "paragraph_count": len(context.get("paragraphs", [])),
            },
            # --- Entities ---
            "entities": context.get("entities", {}),
            # --- Clauses ---
            "clauses": {
                "detected": clauses,
                "primary_clause": context.get("primary_clause", "Unknown"),
                "primary_confidence": context.get("primary_confidence", 0.0),
                "total_detected": len(clauses),
                "found_types": sorted(found_types),
                "missing_types": missing_clauses,
            },
            # --- Risk ---
            "risk": {
                "clause_risks": context.get("clause_risks", []),
                "overall_risk_score": context.get("overall_risk_score", 0),
                "overall_risk_level": context.get("overall_risk_level", "Low"),
                "risk_factors": context.get("risk_factors", []),
            },
            # --- AI Summary ---
            "ai_analysis": {
                "summary": context.get("ai_summary", ""),
                "key_findings": context.get("key_findings", []),
                "recommendations": context.get("recommendations", []),
            },
            # --- Completeness ---
            "completeness": {
                "score": completeness_score,
                "found_count": len(found_types),
                "total_possible": len(ALL_CLAUSE_TYPES),
                "missing_clauses": missing_clauses,
            },
            # --- Pipeline Telemetry ---
            "pipeline": {
                "agent_timings": context.get("agent_timings", {}),
                "errors": (
                    {
                        "agent": context.get("agent_error_name", ""),
                        "message": context.get("agent_error", ""),
                    }
                    if context.get("agent_error")
                    else None
                ),
            },
        }

        context["missing_clauses"] = missing_clauses
        context["completeness_score"] = completeness_score
        context["compiled_report"] = compiled_report

        logger.info(
            "CompilerAgent | completeness={}% | found={} | missing={} | report_keys={}",
            completeness_score,
            len(found_types),
            len(missing_clauses),
            len(compiled_report),
        )

        return context
