"""
Text Cleaning Agent — Post-OCR Text Normalisation (Agent 2).

Wraps the existing ``TextCleaner`` to normalise raw extracted text,
split it into sentences and paragraphs, and compute basic text
statistics.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.preprocessing.clean_text import TextCleaner
from src.utils.logger import logger


class TextCleaningAgent(BaseAgent):
    """Agent 2 — Clean and structure raw extracted text.

    Context contract:

    * **Input:**  ``{raw_text: str, ocr_method: str}``
    * **Output adds:** ``{clean_text, sentences, paragraphs, word_count, char_count}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "TextCleaningAgent"
        self._cleaner = TextCleaner()

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        raw_text: str = context.get("raw_text", "")

        if not raw_text.strip():
            logger.warning("TextCleaningAgent received empty raw_text")
            context["clean_text"] = ""
            context["sentences"] = []
            context["paragraphs"] = []
            context["word_count"] = 0
            context["char_count"] = 0
            return context

        # Determine whether the text came from OCR (affects cleaning strategy)
        ocr_method: str = context.get("ocr_method", "")
        is_ocr = ocr_method.startswith("ocr_") or ocr_method == "easyocr"

        # Run the TextCleaner pipeline
        result = self._cleaner.clean(raw_text, is_ocr=is_ocr)

        clean_text: str = result.get("clean_text", "")
        sentences: list[str] = result.get("sentences", [])

        # Split clean text into paragraphs (double-newline delimited)
        paragraphs = [
            p.strip()
            for p in clean_text.split("\n\n")
            if p.strip()
        ]

        context["clean_text"] = clean_text
        context["sentences"] = sentences
        context["paragraphs"] = paragraphs
        context["word_count"] = len(clean_text.split()) if clean_text else 0
        context["char_count"] = len(clean_text)

        logger.info(
            "TextCleaningAgent | sentences={} | paragraphs={} | words={} | chars={} | reduction={:.1f}%",
            len(sentences),
            len(paragraphs),
            context["word_count"],
            context["char_count"],
            result.get("reduction_percent", 0.0),
        )

        return context
