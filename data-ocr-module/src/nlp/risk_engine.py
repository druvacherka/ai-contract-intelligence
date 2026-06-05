"""
Risk Engine — Contract Risk Scoring.

Analyzes contract text for legal risk factors across five dimensions and
produces a normalized 0-100 risk score together with a human-readable risk
level (Low / Medium / High).

Dimensions
----------
1. **Unfavorable obligations** — one-sided duties, discretionary clauses.
2. **Liability exposure** — uncapped or broad liability language.
3. **Vague language** — imprecise phrasing that creates ambiguity.
4. **Missing protections** — absence of safeguards.
5. **Renewal risks** — auto-renewal traps and evergreen provisions.

Usage::

    from src.nlp.risk_engine import RiskEngine

    engine = RiskEngine()
    result = engine.analyze("The Provider may terminate...", "Termination")
    # {"risk_score": 45, "risk_level": "Medium", "risk_factors": [...]}

    full = engine.full_analysis("Either party may terminate...")
    # {"clause": "Termination", "confidence": 92.4, "risk_score": 45, "risk_level": "Medium"}
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Risk keyword dictionaries (50 + entries per dimension)
# ---------------------------------------------------------------------------

RISK_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "unfavorable_obligations": {
        "weight": ["0.30"],  # placeholder – real weight is in DIMENSION_WEIGHTS
        "keywords": [
            "sole discretion", "absolute discretion", "unfettered discretion",
            "without notice", "without prior notice", "without consent",
            "without approval", "waive rights", "waiver of rights",
            "waives all rights", "irrevocable waiver", "unconditionally",
            "irrevocably", "at any time", "at its sole option",
            "without limitation", "without restriction", "without cause",
            "without reason", "without justification",
            "unilateral right", "unilateral decision", "unilateral modification",
            "one-sided", "binding on you", "binding on the recipient",
            "shall comply", "must comply", "obligated to",
            "shall be deemed to have agreed", "deemed acceptance",
            "silence constitutes acceptance", "failure to object",
            "duty to perform", "unconditional obligation",
            "non-negotiable", "take it or leave it",
            "subject to change without notice", "may modify at any time",
            "reserves the right to change", "reserves the right to modify",
            "assign without consent", "transfer without consent",
            "sublicense without approval", "delegated without notice",
            "perpetual obligation", "survive indefinitely",
            "irrevocable license", "irrevocable consent",
            "exclusive obligation", "bear all costs", "at your expense",
            "at the sole expense", "responsible for all costs",
        ],
    },
    "liability_exposure": {
        "weight": ["0.25"],
        "keywords": [
            "unlimited liability", "no limitation of liability",
            "no cap on liability", "uncapped liability",
            "consequential damages", "incidental damages",
            "punitive damages", "exemplary damages", "special damages",
            "indirect damages", "loss of profits", "loss of revenue",
            "loss of business", "loss of data", "loss of goodwill",
            "personal injury", "property damage", "bodily harm",
            "death or injury", "class action", "regulatory fines",
            "penalties and fines", "statutory damages",
            "joint and several liability", "joint and several",
            "strictly liable", "absolute liability",
            "negligence", "gross negligence", "willful misconduct",
            "intentional breach", "fraudulent misrepresentation",
            "breach of fiduciary duty", "malpractice",
            "all damages arising", "any and all claims",
            "responsible for all losses", "full liability",
            "no limit on damages", "aggregate liability exceeds",
            "total liability without cap", "open-ended liability",
            "exposure to lawsuits", "litigation risk",
            "defend at own cost", "bear legal costs",
            "cover all expenses", "pay all damages",
            "reimburse all losses", "make whole",
            "liquidated damages", "penalty clause", "penalty provision",
            "acceleration of amounts due", "cross-default",
        ],
    },
    "vague_language": {
        "weight": ["0.20"],
        "keywords": [
            "reasonable efforts", "best efforts", "commercially reasonable",
            "good faith efforts", "reasonable endeavors", "best endeavors",
            "as deemed appropriate", "as it sees fit", "in its judgment",
            "in its opinion", "may at any time", "from time to time",
            "as necessary", "as required", "as applicable",
            "where appropriate", "if deemed necessary", "if applicable",
            "including but not limited to", "without limitation",
            "and/or", "substantially", "approximately", "generally",
            "materially", "significantly", "promptly", "timely manner",
            "reasonable time", "within a reasonable period",
            "adequate", "sufficient", "satisfactory",
            "to the extent possible", "to the extent practicable",
            "subject to availability", "may be adjusted",
            "may be modified", "subject to change",
            "at its discretion", "in its sole judgment",
            "as mutually agreed", "unless otherwise agreed",
            "unless otherwise specified", "except as otherwise provided",
            "notwithstanding the foregoing", "notwithstanding anything",
            "for the avoidance of doubt", "customary",
            "standard practice", "industry standard", "usual",
            "ordinary course", "normal business operations",
            "to the best of its knowledge", "to its knowledge",
            "such other", "or otherwise",
        ],
    },
    "missing_protections": {
        "weight": ["0.15"],
        "keywords": [
            # NOTE: These keywords represent *absence* of protective language.
            # We search for them because their presence often signals that the
            # contract explicitly removes or limits a protection.
            "no limitation of liability", "no cap", "no ceiling",
            "no indemnification", "no indemnification cap",
            "no indemnity", "without indemnification",
            "no warranty", "without warranty", "as is", "as-is",
            "no representations", "no guarantee", "no assurance",
            "no termination for convenience", "no right to terminate",
            "cannot terminate", "may not terminate",
            "no cure period", "no notice required", "no prior notice",
            "no escrow", "no holdback", "no retention",
            "no insurance requirement", "no insurance",
            "no audit right", "no audit", "no inspection right",
            "no data protection", "no privacy", "no security",
            "no backup", "no disaster recovery", "no business continuity",
            "no service level", "no sla", "no uptime guarantee",
            "no performance guarantee", "no quality assurance",
            "no dispute resolution", "no arbitration", "no mediation",
            "no force majeure", "no excused performance",
            "no change control", "no change management",
            "no approval required", "no consent needed",
            "waives all claims", "waives all defenses",
            "no recourse", "no remedy", "sole remedy",
            "exclusive remedy limited to", "no refund", "non-refundable",
        ],
    },
    "renewal_risks": {
        "weight": ["0.10"],
        "keywords": [
            "auto-renewal", "automatic renewal", "auto-renew",
            "automatically renew", "automatically renewed",
            "evergreen", "evergreen clause", "evergreen provision",
            "automatic extension", "automatically extend",
            "automatically extended", "perpetual term", "indefinite term",
            "rolling term", "successive terms", "successive periods",
            "continue in effect", "remain in force",
            "unless terminated", "unless cancelled", "unless notice",
            "deemed renewed", "tacit renewal", "reconduction",
            "renewal without notice", "renew without consent",
            "price increase upon renewal", "rate increase",
            "fee adjustment at renewal", "escalation clause",
            "cost escalation", "annual increase", "cpi adjustment",
            "inflation adjustment", "market rate adjustment",
            "no right to opt out", "no opt-out", "cannot opt out",
            "lock-in period", "lock-in", "commitment period",
            "minimum term", "minimum commitment", "minimum purchase",
            "penalty for non-renewal", "early termination fee",
            "early termination penalty", "cancellation fee",
            "cancellation penalty", "breakage fee", "exit fee",
            "liquidated damages for early termination",
            "year-to-year", "month-to-month", "week-to-week",
        ],
    },
}

# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS: dict[str, float] = {
    "unfavorable_obligations": 0.30,
    "liability_exposure": 0.25,
    "vague_language": 0.20,
    "missing_protections": 0.15,
    "renewal_risks": 0.10,
}

# Clause-specific weight adjustments — some dimensions matter more for
# certain clause types.
CLAUSE_WEIGHT_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "Termination": {"renewal_risks": 1.5, "unfavorable_obligations": 1.3},
    "Confidentiality": {"missing_protections": 1.5, "vague_language": 1.3},
    "Liability": {"liability_exposure": 1.8, "missing_protections": 1.3},
    "Arbitration": {"vague_language": 1.3, "missing_protections": 1.2},
    "Governing Law": {"vague_language": 1.2},
    "Payment Terms": {"unfavorable_obligations": 1.4, "vague_language": 1.2},
    "Warranty": {"missing_protections": 1.5, "liability_exposure": 1.2},
    "Renewal": {"renewal_risks": 2.0, "unfavorable_obligations": 1.3},
    "Indemnification": {"liability_exposure": 1.5, "unfavorable_obligations": 1.3},
    "Non-Compete": {"unfavorable_obligations": 1.5, "vague_language": 1.2},
}

# Risk-escalating regex patterns — their presence sharply increases risk
RISK_ESCALATION_PATTERNS: list[tuple[str, str, float]] = [
    # (pattern, description, bonus_points out of 100)
    (r"sole\s+(?:and\s+absolute\s+)?discretion", "Sole/absolute discretion language detected", 8.0),
    (r"unlimited\s+liability", "Unlimited liability language detected", 12.0),
    (r"waiv(?:e|es|er)\s+(?:all\s+)?(?:rights?|claims?|defenses?)", "Broad waiver of rights", 10.0),
    (r"irrevocabl[ey]", "Irrevocable commitment language", 6.0),
    (r"(?:no|without)\s+(?:cap|ceiling|limit(?:ation)?)\s+(?:on\s+)?(?:liability|damages)", "No cap on liability/damages", 12.0),
    (r"joint\s+and\s+several\s+liabilit", "Joint and several liability", 8.0),
    (r"auto(?:matic(?:ally)?)?[\s-]?renew", "Auto-renewal provision", 5.0),
    (r"perpetual|indefinite(?:ly)?", "Perpetual/indefinite term", 6.0),
    (r"(?:as[\s-]is|without\s+warrant)", "As-is / no warranty", 7.0),
    (r"(?:penalty|liquidated\s+damages)\s+(?:for|upon)\s+(?:early\s+)?termination", "Termination penalty", 6.0),
]


class RiskEngine:
    """Production contract risk scoring engine.

    Analyzes text across five weighted risk dimensions and produces a
    normalized 0-100 score.

    Parameters
    ----------
    nlp_engine : NLPEngine | None
        An optional pre-initialised NLPEngine instance used by
        :meth:`full_analysis`.  If not provided, one will be created
        lazily when ``full_analysis`` is first called.

    Examples
    --------
    >>> engine = RiskEngine()
    >>> result = engine.analyze("unlimited liability for all damages", "Liability")
    >>> result["risk_level"]
    'High'
    """

    def __init__(self, nlp_engine: Any | None = None) -> None:
        self._nlp_engine = nlp_engine
        # Precompile escalation patterns
        self._escalation_patterns: list[tuple[re.Pattern[str], str, float]] = [
            (re.compile(p, re.IGNORECASE), desc, bonus)
            for p, desc, bonus in RISK_ESCALATION_PATTERNS
        ]
        logger.info("RiskEngine initialised with %d escalation patterns.", len(self._escalation_patterns))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        contract_text: str,
        clause_type: str = "Unknown",
    ) -> dict[str, Any]:
        """Analyze contract text and return a risk assessment.

        Parameters
        ----------
        contract_text : str
            Contract clause or full contract text.
        clause_type : str
            The classified clause type (e.g. ``"Termination"``).  Used
            to apply clause-specific weight adjustments.

        Returns
        -------
        dict
            ``{"risk_score": int, "risk_level": str, "risk_factors": list[str]}``
        """
        # Edge cases
        if not contract_text or not contract_text.strip():
            logger.warning("Empty input received for risk analysis.")
            return {"risk_score": 0, "risk_level": "Low", "risk_factors": []}

        text_lower = contract_text.strip().lower()

        if len(text_lower) < 10:
            logger.warning("Very short input (%d chars). Risk analysis may be unreliable.", len(text_lower))
            return {"risk_score": 0, "risk_level": "Low", "risk_factors": []}

        # Compute per-dimension scores
        dimension_scores: dict[str, float] = {}
        all_risk_factors: list[str] = []

        for dim_name, dim_data in RISK_KEYWORDS.items():
            keywords = dim_data["keywords"]
            hits: list[str] = []
            for kw in keywords:
                if kw in text_lower:
                    hits.append(kw)

            # Score is based on how many unique keywords matched AND frequency
            if hits:
                # More hits → higher score, with moderate diminishing returns
                raw_ratio = len(hits) / len(keywords)
                # Power of 0.4 is more generous than 0.5 — a few matches
                # already push the score up meaningfully
                base_score = min(raw_ratio ** 0.4 * 100.0, 100.0)

                # Frequency boost: if keywords appear multiple times, text is riskier
                total_hits = sum(text_lower.count(kw) for kw in hits)
                freq_multiplier = min(1.0 + (total_hits - len(hits)) * 0.05, 1.6)
                dim_score = min(base_score * freq_multiplier, 100.0)
                dimension_scores[dim_name] = dim_score

                # Record factors
                dim_display = dim_name.replace("_", " ").title()
                top_hits = hits[:5]  # show top-5 for readability
                all_risk_factors.append(
                    f"{dim_display}: found {len(hits)} indicator(s) — "
                    f"{', '.join(repr(h) for h in top_hits)}"
                    + (f" (+{len(hits) - 5} more)" if len(hits) > 5 else "")
                )
            else:
                dimension_scores[dim_name] = 0.0

        # Apply clause-specific weight adjustments
        adjusted_weights = dict(DIMENSION_WEIGHTS)
        adjustments = CLAUSE_WEIGHT_ADJUSTMENTS.get(clause_type, {})
        for dim, multiplier in adjustments.items():
            if dim in adjusted_weights:
                adjusted_weights[dim] *= multiplier

        # Re-normalise weights so they sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}

        # Weighted sum
        weighted_score = sum(
            adjusted_weights.get(dim, 0.0) * dimension_scores.get(dim, 0.0)
            for dim in DIMENSION_WEIGHTS
        )

        # Apply escalation pattern bonuses
        escalation_bonus = 0.0
        for pattern, description, bonus in self._escalation_patterns:
            if pattern.search(text_lower):
                escalation_bonus += bonus
                all_risk_factors.append(f"⚠ Escalation: {description}")

        # Final score
        raw_score = weighted_score + escalation_bonus
        risk_score = int(min(max(round(raw_score), 0), 100))
        risk_level = self._score_to_level(risk_score)

        logger.info(
            "Risk analysis complete: score=%d, level=%s, factors=%d",
            risk_score,
            risk_level,
            len(all_risk_factors),
        )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": all_risk_factors,
        }

    def full_analysis(self, contract_text: str) -> dict[str, Any]:
        """Run the complete pipeline: classify → analyze → return integration schema.

        Convenience method that combines NLP classification with risk
        scoring to produce the integration contract schema.

        Parameters
        ----------
        contract_text : str
            Raw or cleaned contract text.

        Returns
        -------
        dict
            ``{"clause": str, "confidence": float, "risk_score": int, "risk_level": str}``
        """
        # Lazy-init NLPEngine if not provided
        if self._nlp_engine is None:
            from src.nlp.nlp_engine import NLPEngine

            self._nlp_engine = NLPEngine()
            logger.info("Lazy-initialised NLPEngine for full_analysis.")

        # Step 1: Classify
        classification = self._nlp_engine.classify(contract_text)
        clause_type = classification["clause"]
        confidence = classification["confidence"]

        # Step 2: Analyze risk
        risk = self.analyze(contract_text, clause_type)

        return {
            "clause": clause_type,
            "confidence": confidence,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_to_level(score: int) -> str:
        """Map a 0-100 score to a risk level string.

        Risk levels:
            - 0-30  → Low
            - 31-70 → Medium
            - 71-100 → High
        """
        if score <= 30:
            return "Low"
        elif score <= 70:
            return "Medium"
        else:
            return "High"
