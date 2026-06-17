"""
Gemini AI Agent — Contract Summary Generation (Agent 6).

Uses Google Gemini (``google.generativeai``) to generate an executive
summary, key findings, and recommendations for a contract.  Falls back
to a rule-based summary when the API is unavailable or fails.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.utils.config import Config
from src.utils.logger import logger

# Maximum contract text length sent to Gemini (approx 30 000 chars)
_MAX_TEXT_LENGTH: int = 30_000


class GeminiAgent(BaseAgent):
    """Agent 6 — AI-powered contract summary generation.

    Context contract:

    * **Input:**  ``{clean_text, clauses, entities, overall_risk_score,
      overall_risk_level}``
    * **Output adds:** ``{ai_summary: str, key_findings: list[str],
      recommendations: list[str]}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "GeminiAgent"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        clean_text: str = context.get("clean_text", "")
        clauses: list[dict[str, Any]] = context.get("clauses", [])
        entities: dict[str, list[str]] = context.get("entities", {})
        overall_risk_score: int = context.get("overall_risk_score", 0)
        overall_risk_level: str = context.get("overall_risk_level", "Low")

        # Try Gemini API first
        api_key = Config.GEMINI_API_KEY
        if api_key and api_key.strip():
            try:
                summary, findings, recommendations = self._call_gemini(
                    clean_text, clauses, entities,
                    overall_risk_score, overall_risk_level,
                )
                context["ai_summary"] = summary
                context["key_findings"] = findings
                context["recommendations"] = recommendations
                logger.info(
                    "GeminiAgent | Gemini API success | findings={} | recommendations={}",
                    len(findings),
                    len(recommendations),
                )
                return context
            except Exception as exc:
                logger.warning("Gemini API call failed: {}. Trying Groq fallback.", exc)
        else:
            logger.info("Gemini API key not configured — trying Groq fallback")

        # Try Groq API as fallback
        groq_key = Config.GROQ_API_KEY
        if groq_key and groq_key.strip():
            try:
                summary, findings, recommendations = self._call_groq(
                    clean_text, clauses, entities,
                    overall_risk_score, overall_risk_level,
                )
                context["ai_summary"] = summary
                context["key_findings"] = findings
                context["recommendations"] = recommendations
                logger.info(
                    "GeminiAgent | Groq fallback success | findings={} | recommendations={}",
                    len(findings),
                    len(recommendations),
                )
                return context
            except Exception as groq_exc:
                logger.warning("Groq API call failed: {}. Using rule-based fallback.", groq_exc)
        else:
            logger.info("Groq API key not configured — using rule-based fallback")

        # Fallback: rule-based summary
        summary, findings, recommendations = self._rule_based_summary(
            clean_text, clauses, entities,
            overall_risk_score, overall_risk_level,
        )
        context["ai_summary"] = summary
        context["key_findings"] = findings
        context["recommendations"] = recommendations

        logger.info(
            "GeminiAgent | rule-based fallback | findings={} | recommendations={}",
            len(findings),
            len(recommendations),
        )
        return context

    # ------------------------------------------------------------------
    # Gemini API
    # ------------------------------------------------------------------

    def _call_gemini(
        self,
        text: str,
        clauses: list[dict[str, Any]],
        entities: dict[str, list[str]],
        risk_score: int,
        risk_level: str,
    ) -> tuple[str, list[str], list[str]]:
        """Call the Google Gemini API and parse the structured response."""
        import google.generativeai as genai  # type: ignore[import-untyped]

        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            getattr(Config, "GEMINI_MODEL", "gemini-2.0-flash")
        )

        # Build the structured prompt
        prompt = self._build_prompt(text, clauses, entities, risk_score, risk_level)

        response = model.generate_content(prompt)
        response_text: str = response.text if response.text else ""

        if not response_text.strip():
            raise ValueError("Gemini returned an empty response")

        return self._parse_response(response_text)

    def _build_prompt(
        self,
        text: str,
        clauses: list[dict[str, Any]],
        entities: dict[str, list[str]],
        risk_score: int,
        risk_level: str,
    ) -> str:
        """Construct a structured prompt for Gemini."""
        # Truncate text
        truncated = text[:_MAX_TEXT_LENGTH]

        # Format clauses summary
        clause_lines: list[str] = []
        for c in clauses:
            clause_lines.append(
                f"  - {c['type']} (confidence: {c['confidence']:.1f}%)"
            )
        clauses_str = "\n".join(clause_lines) if clause_lines else "  None detected"

        # Format entities
        entity_lines: list[str] = []
        for category, values in entities.items():
            if values:
                entity_lines.append(f"  - {category}: {', '.join(values[:10])}")
        entities_str = "\n".join(entity_lines) if entity_lines else "  None detected"

        return f"""You are a legal contract analyst. Analyze the following contract and provide a structured analysis.

CONTRACT TEXT (truncated to {len(truncated)} chars):
---
{truncated}
---

DETECTED CLAUSES:
{clauses_str}

DETECTED ENTITIES:
{entities_str}

RISK ASSESSMENT:
  Overall Risk Score: {risk_score}/100
  Risk Level: {risk_level}

Please provide your analysis in EXACTLY this format:

EXECUTIVE SUMMARY:
[Write a concise 2-4 sentence executive summary of the contract]

KEY FINDINGS:
- [Finding 1]
- [Finding 2]
- [Finding 3]
(list 3-7 key findings)

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]
(list 3-7 recommendations for the reviewing party)
"""

    def _parse_response(self, text: str) -> tuple[str, list[str], list[str]]:
        """Parse Gemini's structured response into components."""
        summary = ""
        findings: list[str] = []
        recommendations: list[str] = []

        # Split into sections
        sections = text.split("\n")
        current_section = ""

        for line in sections:
            stripped = line.strip()

            if stripped.upper().startswith("EXECUTIVE SUMMARY"):
                current_section = "summary"
                continue
            elif stripped.upper().startswith("KEY FINDINGS"):
                current_section = "findings"
                continue
            elif stripped.upper().startswith("RECOMMENDATIONS"):
                current_section = "recommendations"
                continue

            if current_section == "summary" and stripped:
                summary = f"{summary} {stripped}".strip() if summary else stripped
            elif current_section == "findings" and stripped.startswith("-"):
                findings.append(stripped.lstrip("- ").strip())
            elif current_section == "recommendations" and stripped.startswith("-"):
                recommendations.append(stripped.lstrip("- ").strip())

        # Ensure we have at least some content
        if not summary:
            summary = text[:500].strip()
        if not findings:
            findings = ["Contract analysis completed — see full text for details."]
        if not recommendations:
            recommendations = ["Review the full contract carefully before signing."]

        return summary, findings, recommendations

    # ------------------------------------------------------------------
    # Groq API (fallback)
    # ------------------------------------------------------------------

    def _call_groq(
        self,
        text: str,
        clauses: list[dict[str, Any]],
        entities: dict[str, list[str]],
        risk_score: int,
        risk_level: str,
    ) -> tuple[str, list[str], list[str]]:
        """Call the Groq API (Llama 3.3 70B) as fallback when Gemini fails."""
        from groq import Groq  # type: ignore[import-untyped]

        client = Groq(api_key=Config.GROQ_API_KEY)

        # Build the same structured prompt
        prompt = self._build_prompt(text, clauses, entities, risk_score, risk_level)

        response = client.chat.completions.create(
            model=getattr(Config, "GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal contract analyst AI. Analyze contracts and provide structured analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        response_text = response.choices[0].message.content or ""
        if not response_text.strip():
            raise ValueError("Groq returned an empty response")

        return self._parse_response(response_text)
    # ------------------------------------------------------------------
    # Rule-based fallback
    # ------------------------------------------------------------------

    def _rule_based_summary(
        self,
        text: str,
        clauses: list[dict[str, Any]],
        entities: dict[str, list[str]],
        risk_score: int,
        risk_level: str,
    ) -> tuple[str, list[str], list[str]]:
        """Generate a summary without the Gemini API."""
        # --- Executive summary ---
        clause_types = sorted(set(c["type"] for c in clauses)) if clauses else []
        num_clauses = len(clauses)

        orgs = entities.get("organizations", [])
        org_str = f" involving {', '.join(orgs[:3])}" if orgs else ""

        summary = (
            f"This contract{org_str} contains {num_clauses} identified clause(s) "
            f"spanning {len(clause_types)} clause type(s): "
            f"{', '.join(clause_types) if clause_types else 'none detected'}. "
            f"The overall risk assessment is {risk_level} ({risk_score}/100)."
        )

        # --- Key findings ---
        findings: list[str] = []

        if clause_types:
            findings.append(
                f"Detected clause types: {', '.join(clause_types)}."
            )

        if risk_level == "High":
            findings.append(
                f"HIGH RISK: Overall risk score is {risk_score}/100 — "
                "immediate legal review is recommended."
            )
        elif risk_level == "Medium":
            findings.append(
                f"MODERATE RISK: Overall risk score is {risk_score}/100 — "
                "review flagged clauses."
            )
        else:
            findings.append(
                f"LOW RISK: Overall risk score is {risk_score}/100."
            )

        dates = entities.get("dates", [])
        if dates:
            findings.append(f"Key dates mentioned: {', '.join(dates[:5])}.")

        money = entities.get("money_values", [])
        if money:
            findings.append(f"Monetary values found: {', '.join(money[:5])}.")

        jurisdictions = entities.get("jurisdictions", [])
        if jurisdictions:
            findings.append(f"Jurisdictions referenced: {', '.join(jurisdictions[:5])}.")

        if not findings:
            findings.append("No significant findings from automated analysis.")

        # --- Recommendations ---
        recommendations: list[str] = []

        if risk_level in {"Medium", "High"}:
            recommendations.append(
                "Have a qualified attorney review the high-risk clauses."
            )

        if "Termination" not in clause_types:
            recommendations.append(
                "Consider adding or verifying termination provisions."
            )
        if "Liability" not in clause_types:
            recommendations.append(
                "Ensure liability limitations are clearly defined."
            )
        if "Confidentiality" not in clause_types:
            recommendations.append(
                "Review whether a confidentiality clause is needed."
            )
        if "Governing Law" not in clause_types:
            recommendations.append(
                "Specify governing law and jurisdiction to avoid disputes."
            )

        recommendations.append(
            "Review the full contract text before execution."
        )

        return summary, findings, recommendations
