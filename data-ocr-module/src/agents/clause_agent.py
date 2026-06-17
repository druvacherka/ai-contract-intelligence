"""
Clause Detection Agent — Legal Clause Classification (Agent 4).

Wraps the existing ``NLPEngine`` to classify each paragraph of a
contract into one of 10 legal clause types with a confidence score.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.nlp.nlp_engine import NLPEngine
from src.utils.logger import logger

# Minimum confidence (0-100) to keep a clause classification
_MIN_CONFIDENCE: float = 40.0


class ClauseAgent(BaseAgent):
    """Agent 4 — Per-paragraph clause classification.

    Classifies each paragraph independently using ``NLPEngine.classify()``
    and retains only results with confidence ≥ 40%.

    Context contract:

    * **Input:**  ``{clean_text: str, paragraphs: list[str]}``
    * **Output adds:** ``{clauses, primary_clause, primary_confidence}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "ClauseAgent"
        self._engine = NLPEngine()

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        clean_text: str = context.get("clean_text", "")
        paragraphs: list[str] = context.get("paragraphs", [])

        if not clean_text.strip() or not paragraphs:
            logger.warning("ClauseAgent received empty text / no paragraphs")
            context["clauses"] = []
            context["primary_clause"] = "Unknown"
            context["primary_confidence"] = 0.0
            return context

        clauses: list[dict[str, Any]] = []
        running_offset = 0

        for para in paragraphs:
            if not para.strip():
                continue

            # Classify the paragraph
            result = self._engine.classify(para)
            clause_type: str = result.get("clause", "Unknown")
            confidence: float = result.get("confidence", 0.0)

            # Skip low-confidence or Unknown results
            if clause_type == "Unknown" or confidence < _MIN_CONFIDENCE:
                # Advance offset past this paragraph
                idx = clean_text.find(para, running_offset)
                if idx != -1:
                    running_offset = idx + len(para)
                continue

            # Locate paragraph within the full text
            start_index = clean_text.find(para, running_offset)
            if start_index == -1:
                start_index = 0
            end_index = start_index + len(para)
            running_offset = end_index

            clauses.append({
                "type": clause_type,
                "text": para,
                "confidence": confidence,
                "startIndex": start_index,
                "endIndex": end_index,
            })

        # Determine primary clause (highest confidence)
        if clauses:
            best = max(clauses, key=lambda c: c["confidence"])
            primary_clause = best["type"]
            primary_confidence = best["confidence"]
        else:
            primary_clause = "Unknown"
            primary_confidence = 0.0

        context["clauses"] = clauses
        context["primary_clause"] = primary_clause
        context["primary_confidence"] = primary_confidence

        logger.info(
            "ClauseAgent found {} clauses | primary='{}' ({:.1f}%)",
            len(clauses),
            primary_clause,
            primary_confidence,
        )

        return context
