"""
Text Cleaning Pipeline — Legal Document Text Processing.

Comprehensive text cleaning tailored for contract and legal documents.
Handles whitespace, headers/footers, page numbers, unicode,
legal-specific patterns, sentence splitting, and clause formatting.
"""

import re
import unicodedata
from typing import Any

from src.utils.logger import logger


class TextCleaner:
    """
    Production-grade text cleaning pipeline for legal/contract documents.

    Features:
    - Excessive whitespace removal
    - Header/footer detection and removal
    - Page number removal
    - Unicode normalization
    - Legal text cleanup (section numbers, exhibit refs)
    - Sentence splitting
    - Clause formatting preservation
    - OCR artifact cleanup
    """

    # Common header/footer patterns in legal documents
    HEADER_FOOTER_PATTERNS: list[str] = [
        r"(?i)^page\s+\d+\s*(of\s+\d+)?\s*$",
        r"(?i)^-\s*\d+\s*-\s*$",
        r"(?i)^\d+\s*$",  # Standalone page numbers
        r"(?i)^confidential\s*$",
        r"(?i)^draft\s*$",
        r"(?i)^privileged\s+and\s+confidential\s*$",
        r"(?i)^attorney[\s-]client\s+privilege\s*$",
        r"(?i)^work\s+product\s*$",
        r"(?i)^exhibit\s+[a-z]\s*$",
        r"(?i)^schedule\s+\d+\s*$",
        r"(?i)^appendix\s+[a-z]\s*$",
        r"(?i)^\[.*\]\s*$",  # Bracketed references like [Page 1]
    ]

    # OCR common artifacts
    OCR_ARTIFACT_PATTERNS: list[tuple[str, str]] = [
        (r"[|]", "I"),       # Pipe mistaken for I
        (r"(?<!\d)0(?!\d)", "O"),  # Zero mistaken for O (only between non-digits)
        (r"\bll\b", "II"),   # Double L mistaken for II
        (r"rn", "m"),        # rn ligature
    ]

    def __init__(self, aggressive_ocr_cleanup: bool = False) -> None:
        """
        Initialize the text cleaner.

        Args:
            aggressive_ocr_cleanup: If True, apply aggressive OCR artifact
                                     correction (may cause false positives).
        """
        self.aggressive_ocr_cleanup = aggressive_ocr_cleanup
        self._compiled_header_patterns = [
            re.compile(p) for p in self.HEADER_FOOTER_PATTERNS
        ]

        logger.info(
            "TextCleaner initialized | aggressive_ocr={}",
            aggressive_ocr_cleanup,
        )

    def normalize_unicode(self, text: str) -> str:
        """
        Normalize unicode characters to their closest ASCII equivalents
        while preserving legal symbols.

        Args:
            text: Raw text.

        Returns:
            Unicode-normalized text.
        """
        # NFC normalization
        text = unicodedata.normalize("NFC", text)

        # Common unicode replacements
        replacements = {
            "\u00a0": " ",       # Non-breaking space
            "\u2019": "'",       # Right single quotation
            "\u2018": "'",       # Left single quotation
            "\u201c": '"',       # Left double quotation
            "\u201d": '"',       # Right double quotation
            "\u2013": "-",       # En-dash
            "\u2014": " - ",     # Em-dash (with spaces)
            "\u2026": "...",     # Ellipsis
            "\u00b7": "*",       # Middle dot
            "\u2022": "*",       # Bullet
            "\u00a7": "Section", # Section sign
            "\u00b6": "",        # Pilcrow
            "\u2010": "-",       # Hyphen
            "\u2011": "-",       # Non-breaking hyphen
            "\u2012": "-",       # Figure dash
            "\u200b": "",        # Zero-width space
            "\u200c": "",        # Zero-width non-joiner
            "\u200d": "",        # Zero-width joiner
            "\ufeff": "",        # BOM
            "\u00ad": "",        # Soft hyphen
            "\u00ae": "(R)",     # Registered trademark
            "\u2122": "(TM)",    # Trademark
            "\u00a9": "(C)",     # Copyright
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def remove_excessive_whitespace(self, text: str) -> str:
        """
        Clean up whitespace while preserving paragraph structure.

        Args:
            text: Input text.

        Returns:
            Whitespace-normalized text.
        """
        # Replace tabs with spaces
        text = text.replace("\t", "    ")

        # Collapse multiple spaces to single
        text = re.sub(r"[ ]{2,}", " ", text)

        # Collapse 3+ newlines to double newline (paragraph break)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove trailing whitespace from each line
        lines = text.split("\n")
        lines = [line.rstrip() for line in lines]
        text = "\n".join(lines)

        return text.strip()

    def remove_headers_footers(self, text: str) -> str:
        """
        Remove common headers and footers from legal documents.

        Detects and removes page numbers, confidentiality notices,
        and other recurring header/footer patterns.

        Args:
            text: Input text.

        Returns:
            Text with headers/footers removed.
        """
        lines = text.split("\n")
        cleaned_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines (preserve them for paragraph structure)
            if not stripped:
                cleaned_lines.append(line)
                continue

            # Check against header/footer patterns
            is_header_footer = False
            for pattern in self._compiled_header_patterns:
                if pattern.match(stripped):
                    is_header_footer = True
                    break

            if not is_header_footer:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def remove_page_numbers(self, text: str) -> str:
        """
        Remove standalone page numbers from text.

        Handles various page number formats:
        - "Page 1 of 10"
        - "- 3 -"
        - Standalone numbers at line boundaries

        Args:
            text: Input text.

        Returns:
            Text with page numbers removed.
        """
        # Page X of Y
        text = re.sub(
            r"(?im)^\s*page\s+\d+\s*(of\s+\d+)?\s*$", "", text
        )

        # Centered dash numbers: - 3 -
        text = re.sub(r"(?m)^\s*-\s*\d+\s*-\s*$", "", text)

        # Standalone numbers on their own line (likely page numbers)
        text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)

        return text

    def clean_legal_text(self, text: str) -> str:
        """
        Legal-specific text cleanup.

        Normalizes section numbering, exhibit references,
        and legal formatting conventions.

        Args:
            text: Input text.

        Returns:
            Cleaned legal text.
        """
        # Normalize section numbering: "Section  3.1" -> "Section 3.1"
        text = re.sub(r"(?i)(section)\s+(\d)", r"\1 \2", text)

        # Normalize article references
        text = re.sub(r"(?i)(article)\s+(\d)", r"\1 \2", text)

        # Clean up subsection numbering: "(a)  " -> "(a) "
        text = re.sub(r"\(([a-z])\)\s{2,}", r"(\1) ", text)
        text = re.sub(r"\((\d+)\)\s{2,}", r"(\1) ", text)

        # Clean numbered lists: "1.  " -> "1. "
        text = re.sub(r"(\d+\.)\s{2,}", r"\1 ", text)

        # Normalize "herein", "thereof", "therein" (don't remove, just normalize spacing)
        text = re.sub(r"\s+(herein|thereof|therein|hereby|thereto)\s+", r" \1 ", text)

        # Remove excessive underscores (signature lines)
        text = re.sub(r"_{5,}", "", text)

        # Remove excessive equals signs (section dividers)
        text = re.sub(r"={5,}", "", text)

        # Remove excessive dashes (horizontal rules)
        text = re.sub(r"-{5,}", "", text)

        return text

    def clean_ocr_artifacts(self, text: str) -> str:
        """
        Remove common OCR artifacts and fix OCR-specific errors.

        Only applies aggressive corrections when enabled.

        Args:
            text: OCR'd text.

        Returns:
            Text with OCR artifacts cleaned.
        """
        # Always clean these
        # Remove form feed characters
        text = text.replace("\f", "\n\n")

        # Remove control characters (except newline, tab)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Fix broken words at line endings (hyphenation)
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Fix scattered characters: "c o n t r a c t" -> "contract"
        # Only for sequences of 5+ single characters separated by spaces
        text = re.sub(
            r"\b((?:[a-zA-Z] ){4,}[a-zA-Z])\b",
            lambda m: m.group(0).replace(" ", ""),
            text,
        )

        # Aggressive OCR cleanup (optional)
        if self.aggressive_ocr_cleanup:
            for pattern, replacement in self.OCR_ARTIFACT_PATTERNS:
                text = re.sub(pattern, replacement, text)

        return text

    def split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences with legal-document awareness.

        Handles abbreviations, section references, and legal citations
        that commonly cause false splits.

        Args:
            text: Input text.

        Returns:
            List of sentence strings.
        """
        # Protect common abbreviations from splitting
        abbreviations = [
            "Inc", "Corp", "Ltd", "LLC", "Co", "No", "Dr", "Mr",
            "Mrs", "Ms", "Jr", "Sr", "vs", "etc", "approx", "est",
            "Dept", "Div", "Vol", "Rev", "Sec", "Art", "Par", "Ex",
            "i.e", "e.g", "cf", "al",
        ]
        protected_text = text
        for abbr in abbreviations:
            # Replace "Inc." with "Inc[DOT]" temporarily
            protected_text = protected_text.replace(
                f"{abbr}.", f"{abbr}[DOT]"
            )

        # Protect section numbers like "3.1"
        protected_text = re.sub(
            r"(\d+)\.(\d+)", r"\1[DOT]\2", protected_text
        )

        # Split on sentence-ending punctuation followed by whitespace + capital
        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z\(])", protected_text
        )

        # Restore dots
        sentences = [s.replace("[DOT]", ".") for s in sentences]

        # Remove empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def preserve_clause_formatting(self, text: str) -> str:
        """
        Preserve legal clause structure while cleaning.

        Ensures numbered sections, lettered subsections, and
        indentation patterns remain intact.

        Args:
            text: Input text.

        Returns:
            Text with clause formatting preserved.
        """
        lines = text.split("\n")
        result_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Preserve section headings (add double newline before)
            if re.match(r"^(ARTICLE|SECTION|EXHIBIT|SCHEDULE)\s", stripped, re.I):
                if result_lines and result_lines[-1].strip():
                    result_lines.append("")  # Add blank line before heading
                result_lines.append(stripped)
                continue

            # Preserve numbered sections
            if re.match(r"^\d+\.\d*\s", stripped):
                if result_lines and result_lines[-1].strip():
                    result_lines.append("")
                result_lines.append(stripped)
                continue

            # Preserve lettered subsections with indentation
            if re.match(r"^\([a-z]\)\s", stripped):
                result_lines.append(f"    {stripped}")
                continue

            # Preserve roman numeral subsections
            if re.match(r"^\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\)\s", stripped, re.I):
                result_lines.append(f"        {stripped}")
                continue

            result_lines.append(stripped)

        return "\n".join(result_lines)

    def clean(
        self,
        text: str,
        is_ocr: bool = False,
        preserve_formatting: bool = True,
    ) -> dict[str, Any]:
        """
        Run the full text cleaning pipeline.

        Pipeline order:
        1. Unicode normalization
        2. OCR artifact cleanup (if OCR'd)
        3. Header/footer removal
        4. Page number removal
        5. Legal text cleanup
        6. Whitespace normalization
        7. Clause formatting (if preserve_formatting)

        Args:
            text: Raw text to clean.
            is_ocr: Whether the text came from OCR processing.
            preserve_formatting: Whether to preserve clause formatting.

        Returns:
            Dict with cleaned text and processing info.
        """
        if not text or not text.strip():
            return {
                "clean_text": "",
                "original_length": 0,
                "clean_length": 0,
                "reduction_percent": 0,
                "sentences": [],
                "num_sentences": 0,
            }

        original_length = len(text)
        logger.info(
            "Cleaning text | length={} | is_ocr={}", original_length, is_ocr
        )

        # Step 1: Unicode normalization
        text = self.normalize_unicode(text)

        # Step 2: OCR artifact cleanup
        if is_ocr:
            text = self.clean_ocr_artifacts(text)

        # Step 3: Header/footer removal
        text = self.remove_headers_footers(text)

        # Step 4: Page number removal
        text = self.remove_page_numbers(text)

        # Step 5: Legal text cleanup
        text = self.clean_legal_text(text)

        # Step 6: Whitespace normalization
        text = self.remove_excessive_whitespace(text)

        # Step 7: Clause formatting
        if preserve_formatting:
            text = self.preserve_clause_formatting(text)
            text = self.remove_excessive_whitespace(text)  # Re-clean after formatting

        # Split sentences
        sentences = self.split_sentences(text)

        clean_length = len(text)
        reduction = round(
            (1 - clean_length / max(original_length, 1)) * 100, 1
        )

        logger.info(
            "Text cleaning complete | original={} | clean={} | reduction={:.1f}%",
            original_length,
            clean_length,
            reduction,
        )

        return {
            "clean_text": text,
            "original_length": original_length,
            "clean_length": clean_length,
            "reduction_percent": reduction,
            "sentences": sentences,
            "num_sentences": len(sentences),
        }
