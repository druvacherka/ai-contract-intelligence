"""
NER Agent — Named Entity Recognition (Agent 3).

Extracts structured entities from cleaned contract text using spaCy
(preferred) with a regex fallback when no spaCy model is available.
"""

from __future__ import annotations

import re
from typing import Any

from src.agents.base_agent import BaseAgent
from src.utils.logger import logger


def _load_spacy_model() -> Any | None:
    """Try to load a spaCy model, returning *None* on failure."""
    try:
        import spacy  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("spacy is not installed — NER will use regex fallback")
        return None

    for model_name in ("en_core_web_lg", "en_core_web_sm"):
        try:
            nlp = spacy.load(model_name)
            logger.info("Loaded spaCy model: {}", model_name)
            return nlp
        except OSError:
            logger.info("spaCy model '{}' not found, trying next…", model_name)

    logger.warning("No spaCy model available — NER will use regex fallback")
    return None


# One-time model load at import
_nlp = _load_spacy_model()


class NERAgent(BaseAgent):
    """Agent 3 — Named Entity Recognition.

    Extracts five entity categories from contract text:

    * **organizations** — ORG entities
    * **dates** — DATE entities
    * **money_values** — MONEY entities
    * **jurisdictions** — GPE + LOC entities
    * **persons** — PERSON entities

    Context contract:

    * **Input:**  ``{clean_text: str}``
    * **Output adds:** ``{entities: dict[str, list[str]]}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "NERAgent"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        clean_text: str = context.get("clean_text", "")

        if not clean_text.strip():
            logger.warning("NERAgent received empty clean_text")
            context["entities"] = self._empty_entities()
            return context

        if _nlp is not None:
            entities = self._extract_with_spacy(clean_text)
        else:
            entities = self._extract_with_regex(clean_text)

        context["entities"] = entities

        total = sum(len(v) for v in entities.values())
        logger.info(
            "NERAgent extracted {} entities | orgs={} dates={} money={} jurisdictions={} persons={}",
            total,
            len(entities["organizations"]),
            len(entities["dates"]),
            len(entities["money_values"]),
            len(entities["jurisdictions"]),
            len(entities["persons"]),
        )

        return context

    # ------------------------------------------------------------------
    # spaCy extraction
    # ------------------------------------------------------------------

    def _extract_with_spacy(self, text: str) -> dict[str, list[str]]:
        """Use spaCy NER to extract entities."""
        # Process only up to 100 000 chars to avoid memory issues
        doc = _nlp(text[:100_000])  # type: ignore[misc]

        orgs: set[str] = set()
        dates: set[str] = set()
        money: set[str] = set()
        jurisdictions: set[str] = set()
        persons: set[str] = set()

        for ent in doc.ents:
            label = ent.label_
            value = ent.text.strip()
            if not value:
                continue

            if label == "ORG":
                orgs.add(value)
            elif label == "DATE":
                dates.add(value)
            elif label == "MONEY":
                money.add(value)
            elif label in {"GPE", "LOC"}:
                jurisdictions.add(value)
            elif label == "PERSON":
                persons.add(value)

        return {
            "organizations": sorted(orgs),
            "dates": sorted(dates),
            "money_values": sorted(money),
            "jurisdictions": sorted(jurisdictions),
            "persons": sorted(persons),
        }

    # ------------------------------------------------------------------
    # Regex fallback
    # ------------------------------------------------------------------

    _DATE_RE = re.compile(
        r"\b(?:"
        # ISO-like: 2024-01-15
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        r"|"
        # US-style: 01/15/2024
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"
        r"|"
        # Written: January 15, 2024 / 15 January 2024
        r"(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\.?\s+\d{1,2},?\s+\d{4}"
        r"|"
        r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\.?\s+\d{4}"
        r")\b",
        re.IGNORECASE,
    )

    _MONEY_RE = re.compile(
        r"(?:"
        r"[\$\£\€\¥][\s]?\d[\d,]*(?:\.\d{1,2})?"
        r"|"
        r"\d[\d,]*(?:\.\d{1,2})?\s*(?:dollars?|USD|GBP|EUR|pounds?|euros?)"
        r")",
        re.IGNORECASE,
    )

    _ORG_RE = re.compile(
        r"\b[A-Z][A-Za-z&',.-]+(?:\s+[A-Z][A-Za-z&',.-]+)*"
        r"\s+(?:Inc\.?|Corp\.?|LLC|Ltd\.?|Co\.?|LP|LLP|PLC|GmbH|AG|SA|NV|BV)\b"
    )

    _PERSON_RE = re.compile(
        r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b"
    )

    _JURISDICTION_RE = re.compile(
        r"(?:State\s+of|Commonwealth\s+of|Province\s+of|County\s+of)\s+"
        r"[A-Z][A-Za-z\s]+",
        re.IGNORECASE,
    )

    def _extract_with_regex(self, text: str) -> dict[str, list[str]]:
        """Regex-based entity extraction as a fallback."""
        return {
            "organizations": sorted(set(self._ORG_RE.findall(text))),
            "dates": sorted(set(self._DATE_RE.findall(text))),
            "money_values": sorted(set(self._MONEY_RE.findall(text))),
            "jurisdictions": sorted(set(self._JURISDICTION_RE.findall(text))),
            "persons": sorted(set(self._PERSON_RE.findall(text))),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_entities() -> dict[str, list[str]]:
        return {
            "organizations": [],
            "dates": [],
            "money_values": [],
            "jurisdictions": [],
            "persons": [],
        }
