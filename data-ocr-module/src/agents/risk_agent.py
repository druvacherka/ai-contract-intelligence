"""
Risk Analysis Agent — Contract Risk Scoring (Agent 5).

Wraps the existing ``RiskEngine`` to compute per-clause risk scores
and an overall weighted-average risk assessment for the contract.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.nlp.risk_engine import RiskEngine
from src.utils.logger import logger


class RiskAgent(BaseAgent):
    """Agent 5 — Per-clause and overall risk analysis.

    Analyses each detected clause with ``RiskEngine.analyze()`` and
    computes a weighted-average overall risk score.

    Context contract:

    * **Input:**  ``{clean_text: str, clauses: list[dict]}``
    * **Output adds:** ``{clause_risks, overall_risk_score,
      overall_risk_level, risk_factors}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "RiskAgent"
        self._engine = RiskEngine()

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        clauses: list[dict[str, Any]] = context.get("clauses", [])
        clean_text: str = context.get("clean_text", "")

        if not clauses:
            logger.warning("RiskAgent received no clauses — running whole-text analysis")
            # Analyse full text as a generic clause
            if clean_text.strip():
                result = self._engine.analyze(clean_text, "Unknown")
                context["clause_risks"] = []
                context["overall_risk_score"] = result["risk_score"]
                context["overall_risk_level"] = result["risk_level"]
                context["risk_factors"] = result["risk_factors"]
            else:
                context["clause_risks"] = []
                context["overall_risk_score"] = 0
                context["overall_risk_level"] = "Low"
                context["risk_factors"] = []
            return context

        clause_risks: list[dict[str, Any]] = []
        all_risk_factors: list[str] = []
        weighted_sum: float = 0.0
        total_weight: float = 0.0

        for clause in clauses:
            clause_text: str = clause.get("text", "")
            clause_type: str = clause.get("type", "Unknown")
            clause_confidence: float = clause.get("confidence", 50.0)

            try:
                result = self._engine.analyze(clause_text, clause_type)
            except Exception as exc:
                logger.warning(
                    "RiskEngine.analyze failed for clause '{}': {}",
                    clause_type,
                    exc,
                )
                result = {"risk_score": 0, "risk_level": "Low", "risk_factors": []}

            risk_entry = {
                "clause_type": clause_type,
                "clause_text_preview": clause_text[:200],
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "risk_factors": result["risk_factors"],
                "clause_confidence": clause_confidence,
            }
            clause_risks.append(risk_entry)
            all_risk_factors.extend(result["risk_factors"])

            # Weight by clause confidence (higher confidence = more weight)
            weight = clause_confidence / 100.0
            weighted_sum += result["risk_score"] * weight
            total_weight += weight

        # Compute overall risk
        if total_weight > 0:
            overall_score = int(round(weighted_sum / total_weight))
        else:
            overall_score = 0

        overall_score = max(0, min(100, overall_score))

        if overall_score <= 30:
            overall_level = "Low"
        elif overall_score <= 70:
            overall_level = "Medium"
        else:
            overall_level = "High"

        # Deduplicate risk factors while preserving order
        seen: set[str] = set()
        unique_factors: list[str] = []
        for factor in all_risk_factors:
            if factor not in seen:
                seen.add(factor)
                unique_factors.append(factor)

        context["clause_risks"] = clause_risks
        context["overall_risk_score"] = overall_score
        context["overall_risk_level"] = overall_level
        context["risk_factors"] = unique_factors

        logger.info(
            "RiskAgent | clauses_analysed={} | overall_score={} | level={} | factors={}",
            len(clause_risks),
            overall_score,
            overall_level,
            len(unique_factors),
        )

        return context
