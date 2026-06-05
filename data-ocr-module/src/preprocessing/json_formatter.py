"""
JSON Formatter — Structured Output Generator.

Produces standardized JSON output for processed documents,
ready for handoff to downstream NLP/AI systems.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.config import Config
from src.utils.logger import logger


class JSONFormatter:
    """
    Formats processed document data into a standardized JSON structure
    suitable for NLP pipeline consumption.

    Output Schema:
    {
        "document_id": "",
        "filename": "",
        "pages": 0,
        "document_type": "",
        "metadata": {},
        "clean_text": "",
        "text_preview": "",
        "processing_method": "native|ocr"
    }
    """

    PREVIEW_LENGTH: int = 500

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Config.PROCESSED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("JSONFormatter initialized | output_dir={}", self.output_dir)

    @staticmethod
    def generate_document_id(filename: str, text: str) -> str:
        """Generate a deterministic document ID from filename and content."""
        content = f"{filename}:{text[:1000]}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:20]

    @staticmethod
    def determine_document_type(
        filename: str, text: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Infer the document type from filename, content, and metadata.

        Returns:
            One of: 'contract', 'amendment', 'nda', 'lease',
            'employment', 'service_agreement', 'unknown'
        """
        combined = f"{filename} {text[:2000]}".lower()

        type_keywords = {
            "nda": ["non-disclosure", "nda", "confidentiality agreement"],
            "employment": [
                "employment agreement",
                "employment contract",
                "offer letter",
            ],
            "lease": ["lease agreement", "rental agreement", "tenancy"],
            "amendment": ["amendment", "addendum", "modification"],
            "service_agreement": [
                "service agreement",
                "master service",
                "statement of work",
                "sow",
            ],
            "license": ["license agreement", "licensing", "software license"],
            "merger": ["merger agreement", "acquisition agreement"],
            "loan": ["loan agreement", "credit agreement", "promissory note"],
            "partnership": ["partnership agreement", "joint venture"],
            "contract": ["agreement", "contract", "terms and conditions"],
        }

        for doc_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in combined:
                    return doc_type

        return "unknown"

    def format_document(
        self,
        filename: str,
        clean_text: str,
        pages: int | None = None,
        processing_method: str = "native",
        metadata: dict[str, Any] | None = None,
        sentences: list[str] | None = None,
        confidence: float | None = None,
        processing_time: float | None = None,
    ) -> dict[str, Any]:
        """
        Format a processed document into the standardized output schema.

        Args:
            filename: Original filename.
            clean_text: Cleaned text content.
            pages: Number of pages (if applicable).
            processing_method: "native" or "ocr".
            metadata: Additional metadata dict.
            sentences: Pre-split sentences.
            confidence: OCR confidence score.
            processing_time: Total processing time in seconds.

        Returns:
            Standardized document JSON dict.
        """
        document_id = self.generate_document_id(filename, clean_text)
        document_type = self.determine_document_type(
            filename, clean_text, metadata
        )

        # Generate preview
        text_preview = clean_text[: self.PREVIEW_LENGTH].strip()
        if len(clean_text) > self.PREVIEW_LENGTH:
            text_preview += "..."

        # Build output
        output: dict[str, Any] = {
            "document_id": document_id,
            "filename": filename,
            "pages": pages or 0,
            "document_type": document_type,
            "metadata": {
                **(metadata or {}),
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "pipeline_version": "1.0.0",
                "text_length": len(clean_text),
                "word_count": len(clean_text.split()),
            },
            "clean_text": clean_text,
            "text_preview": text_preview,
            "processing_method": processing_method,
        }

        # Optional fields
        if sentences is not None:
            output["num_sentences"] = len(sentences)

        if confidence is not None:
            output["ocr_confidence"] = confidence

        if processing_time is not None:
            output["processing_time_seconds"] = round(processing_time, 3)

        logger.info(
            "Document formatted | id={} | type={} | method={} | chars={}",
            document_id,
            document_type,
            processing_method,
            len(clean_text),
        )

        return output

    def save(
        self,
        document: dict[str, Any],
        filename: str | None = None,
    ) -> Path:
        """
        Save a formatted document to disk as JSON.

        Args:
            document: Formatted document dict.
            filename: Output filename (auto-generated if not provided).

        Returns:
            Path to the saved JSON file.
        """
        if filename is None:
            doc_id = document.get("document_id", "unknown")
            original_name = Path(document.get("filename", "doc")).stem
            safe_name = original_name.replace(" ", "_")[:60]
            filename = f"{safe_name}_{doc_id}.json"

        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(document, f, ensure_ascii=False, indent=2)

        size_kb = output_path.stat().st_size / 1024
        logger.info("Document saved | file={} | size={:.1f}KB", output_path, size_kb)

        return output_path

    def format_and_save(
        self,
        filename: str,
        clean_text: str,
        pages: int | None = None,
        processing_method: str = "native",
        metadata: dict[str, Any] | None = None,
        sentences: list[str] | None = None,
        confidence: float | None = None,
        processing_time: float | None = None,
    ) -> tuple[dict[str, Any], Path]:
        """
        Format and save a document in one step.

        Returns:
            Tuple of (formatted document dict, output file path).
        """
        document = self.format_document(
            filename=filename,
            clean_text=clean_text,
            pages=pages,
            processing_method=processing_method,
            metadata=metadata,
            sentences=sentences,
            confidence=confidence,
            processing_time=processing_time,
        )
        output_path = self.save(document)
        return document, output_path

    def batch_format(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Format multiple documents.

        Args:
            documents: List of dicts with keys matching format_document params.

        Returns:
            List of formatted document dicts.
        """
        from tqdm import tqdm

        results: list[dict[str, Any]] = []

        for doc_params in tqdm(documents, desc="Formatting documents"):
            formatted = self.format_document(**doc_params)
            results.append(formatted)

        logger.info("Batch formatting complete | count={}", len(results))
        return results

    def export_batch(
        self,
        documents: list[dict[str, Any]],
        filename: str = "batch_output.json",
    ) -> Path:
        """
        Export multiple formatted documents to a single JSON file.

        Args:
            documents: List of formatted document dicts.
            filename: Output filename.

        Returns:
            Path to the exported file.
        """
        output = {
            "metadata": {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "num_documents": len(documents),
                "pipeline_version": "1.0.0",
            },
            "documents": documents,
        }

        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(
            "Batch export complete | file={} | documents={}",
            output_path,
            len(documents),
        )
        return output_path

    @staticmethod
    def validate_output(document: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a formatted document against the expected schema.

        Args:
            document: Document dict to validate.

        Returns:
            Validation result with 'valid' bool and any 'errors'.
        """
        required_fields = [
            "document_id",
            "filename",
            "pages",
            "document_type",
            "metadata",
            "clean_text",
            "text_preview",
            "processing_method",
        ]

        errors: list[str] = []
        for field in required_fields:
            if field not in document:
                errors.append(f"Missing required field: {field}")

        # Type checks
        if "pages" in document and not isinstance(document["pages"], int):
            errors.append("'pages' must be an integer")

        if "processing_method" in document:
            if document["processing_method"] not in {"native", "ocr", "pending"}:
                errors.append(
                    f"Invalid processing_method: {document['processing_method']}"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
