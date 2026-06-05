"""
CUAD Dataset Parser.

Parses raw CUAD SQuAD-format data into normalized contract structures
with clause annotations, span offsets, and clean text.
"""

import hashlib
import re
from typing import Any

from tqdm import tqdm

from src.dataset.cuad_loader import CUAD_CLAUSE_TYPES
from src.utils.logger import logger


class CUADParser:
    """
    Parses CUAD dataset articles into structured contract objects.

    Converts SQuAD-format QA pairs into normalized clause annotations
    with character-level span offsets.
    """

    def __init__(self) -> None:
        self._parsed_contracts: list[dict[str, Any]] = []
        self._parse_errors: list[dict[str, Any]] = []

        logger.info("CUADParser initialized")

    @property
    def parsed_contracts(self) -> list[dict[str, Any]]:
        """Return all parsed contracts."""
        return self._parsed_contracts

    @property
    def parse_errors(self) -> list[dict[str, Any]]:
        """Return list of parse errors encountered."""
        return self._parse_errors

    @staticmethod
    def generate_contract_id(title: str, text: str) -> str:
        """Generate a deterministic contract ID from title and text hash."""
        content = f"{title}:{text[:500]}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _match_clause_type(question: str) -> str | None:
        """Match a CUAD question string to its clause type."""
        question_lower = question.lower().strip()
        for clause_type in CUAD_CLAUSE_TYPES:
            if clause_type.lower() in question_lower:
                return clause_type
        return None

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Basic normalization of contract text."""
        # Normalize unicode
        text = text.replace("\u00a0", " ")  # non-breaking space
        text = text.replace("\u2019", "'")   # right single quote
        text = text.replace("\u201c", '"')   # left double quote
        text = text.replace("\u201d", '"')   # right double quote
        text = text.replace("\u2013", "-")   # en-dash
        text = text.replace("\u2014", "-")   # em-dash

        # Collapse excessive whitespace (preserve paragraph breaks)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _extract_clauses(
        self, qas: list[dict[str, Any]], context: str
    ) -> list[dict[str, Any]]:
        """
        Extract clause annotations from QA pairs.

        Args:
            qas: List of question-answer objects from SQuAD format.
            context: The paragraph context text.

        Returns:
            List of clause annotation dictionaries.
        """
        clauses: list[dict[str, Any]] = []

        for qa in qas:
            question = qa.get("question", "")
            clause_type = self._match_clause_type(question)

            if clause_type is None:
                continue

            answers = qa.get("answers", [])
            is_impossible = qa.get("is_impossible", len(answers) == 0)

            if is_impossible or not answers:
                continue

            for answer in answers:
                answer_text = answer.get("text", "").strip()
                answer_start = answer.get("answer_start", -1)

                if not answer_text or answer_start < 0:
                    continue

                answer_end = answer_start + len(answer_text)

                # Validate span against context
                if answer_start < len(context):
                    extracted = context[answer_start:answer_end]
                    # Check for reasonable match (allow minor whitespace diffs)
                    if extracted.strip() != answer_text.strip():
                        # Try to find the correct offset
                        corrected_start = context.find(answer_text)
                        if corrected_start >= 0:
                            answer_start = corrected_start
                            answer_end = corrected_start + len(answer_text)
                        else:
                            self._parse_errors.append(
                                {
                                    "type": "span_mismatch",
                                    "clause_type": clause_type,
                                    "expected": answer_text[:80],
                                    "found": extracted[:80],
                                }
                            )

                clauses.append(
                    {
                        "type": clause_type,
                        "start": answer_start,
                        "end": answer_end,
                        "text": answer_text,
                    }
                )

        return clauses

    def parse_article(self, article: dict[str, Any]) -> dict[str, Any] | None:
        """
        Parse a single CUAD article into a structured contract.

        Args:
            article: A single article dict from the CUAD dataset.

        Returns:
            Structured contract dict or None on failure.
        """
        try:
            title = article.get("title", "untitled")
            paragraphs = article.get("paragraphs", [])

            if not paragraphs:
                logger.warning("Article '{}' has no paragraphs", title)
                return None

            # Merge all paragraphs into a single contract text
            all_clauses: list[dict[str, Any]] = []
            text_parts: list[str] = []
            current_offset = 0

            for para in paragraphs:
                context = para.get("context", "")
                if not context.strip():
                    continue

                normalized_context = self._normalize_text(context)

                # Extract clauses with offset adjustment
                qas = para.get("qas", [])
                clauses = self._extract_clauses(qas, context)

                # Adjust clause offsets for merged text
                for clause in clauses:
                    clause["start"] += current_offset
                    clause["end"] += current_offset

                all_clauses.extend(clauses)
                text_parts.append(normalized_context)
                current_offset += len(normalized_context) + 2  # +2 for \n\n separator

            full_text = "\n\n".join(text_parts)
            contract_id = self.generate_contract_id(title, full_text)

            # Deduplicate clauses
            seen_spans: set[tuple[str, int, int]] = set()
            unique_clauses: list[dict[str, Any]] = []
            for clause in all_clauses:
                key = (clause["type"], clause["start"], clause["end"])
                if key not in seen_spans:
                    seen_spans.add(key)
                    unique_clauses.append(clause)

            # Sort clauses by start position
            unique_clauses.sort(key=lambda c: c["start"])

            return {
                "contract_id": contract_id,
                "title": title,
                "text": full_text,
                "clauses": unique_clauses,
                "metadata": {
                    "num_paragraphs": len(paragraphs),
                    "num_clauses": len(unique_clauses),
                    "clause_types_found": list(
                        set(c["type"] for c in unique_clauses)
                    ),
                    "text_length": len(full_text),
                },
            }

        except Exception as e:
            logger.error("Failed to parse article '{}': {}", article.get("title", "?"), e)
            self._parse_errors.append(
                {
                    "type": "parse_failure",
                    "title": article.get("title", "?"),
                    "error": str(e),
                }
            )
            return None

    def parse_all(
        self, articles: list[dict[str, Any]], show_progress: bool = True
    ) -> list[dict[str, Any]]:
        """
        Parse all CUAD articles into structured contracts.

        Args:
            articles: List of article dicts from the CUAD dataset.
            show_progress: Whether to display a progress bar.

        Returns:
            List of structured contract dicts.
        """
        self._parsed_contracts = []
        self._parse_errors = []

        iterator = tqdm(articles, desc="Parsing contracts") if show_progress else articles

        for article in iterator:
            contract = self.parse_article(article)
            if contract is not None:
                self._parsed_contracts.append(contract)

        logger.info(
            "Parsing complete | contracts={} | errors={} | clauses={}",
            len(self._parsed_contracts),
            len(self._parse_errors),
            sum(len(c["clauses"]) for c in self._parsed_contracts),
        )

        return self._parsed_contracts

    def get_clause_statistics(self) -> dict[str, Any]:
        """
        Compute statistics over all parsed contracts.

        Returns:
            Dictionary of aggregate statistics.
        """
        if not self._parsed_contracts:
            return {"status": "no_data"}

        total_clauses = 0
        clause_type_counts: dict[str, int] = {}
        text_lengths: list[int] = []

        for contract in self._parsed_contracts:
            text_lengths.append(len(contract["text"]))
            for clause in contract["clauses"]:
                total_clauses += 1
                ctype = clause["type"]
                clause_type_counts[ctype] = clause_type_counts.get(ctype, 0) + 1

        return {
            "total_contracts": len(self._parsed_contracts),
            "total_clauses": total_clauses,
            "avg_clauses_per_contract": round(
                total_clauses / len(self._parsed_contracts), 2
            ),
            "avg_text_length": round(
                sum(text_lengths) / len(text_lengths), 0
            ),
            "clause_type_distribution": dict(
                sorted(clause_type_counts.items(), key=lambda x: x[1], reverse=True)
            ),
            "parse_errors": len(self._parse_errors),
        }
