"""
Document Loader — Universal Document Ingestion.

Handles file type detection, validation, metadata extraction,
and routing to appropriate parsers for PDF, DOCX, and TXT files.
"""

import mimetypes
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.config import Config
from src.utils.logger import logger


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded."""
    pass


class UnsupportedFileError(DocumentLoadError):
    """Raised when a file type is not supported."""
    pass


class FileSizeError(DocumentLoadError):
    """Raised when a file exceeds the maximum size limit."""
    pass


class DocumentLoader:
    """
    Universal document loader with file type detection,
    validation, and metadata extraction.

    Supports: PDF, DOCX, TXT, scanned PDFs
    """

    # MIME type to extension mapping
    MIME_MAP: dict[str, str] = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "text/plain": ".txt",
    }

    def __init__(self, max_file_size_mb: int | None = None) -> None:
        self.max_file_size_mb = max_file_size_mb if max_file_size_mb is not None else Config.MAX_FILE_SIZE_MB
        self.supported_extensions = Config.SUPPORTED_EXTENSIONS

        logger.info(
            "DocumentLoader initialized | max_size={}MB | supported={}",
            self.max_file_size_mb,
            self.supported_extensions,
        )

    def detect_file_type(self, filepath: Path) -> dict[str, str]:
        """
        Detect the file type using extension and MIME type.

        Args:
            filepath: Path to the file.

        Returns:
            Dict with 'extension', 'mime_type', and 'category'.
        """
        extension = filepath.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(filepath))

        # Determine category
        if extension == ".pdf":
            category = "pdf"
        elif extension in {".docx", ".doc"}:
            category = "docx"
        elif extension == ".txt":
            category = "text"
        else:
            category = "unknown"

        result = {
            "extension": extension,
            "mime_type": mime_type or "unknown",
            "category": category,
        }

        logger.debug("File type detected: {} -> {}", filepath.name, result)
        return result

    def validate_file(self, filepath: Path) -> dict[str, Any]:
        """
        Validate a file for processing.

        Checks:
        - File exists
        - File is not empty
        - File extension is supported
        - File size is within limits

        Args:
            filepath: Path to the file.

        Returns:
            Validation result dict.

        Raises:
            DocumentLoadError: On validation failure.
        """
        filepath = Path(filepath)

        # Existence check
        if not filepath.exists():
            raise DocumentLoadError(f"File not found: {filepath}")

        if not filepath.is_file():
            raise DocumentLoadError(f"Not a file: {filepath}")

        # Empty file check
        file_size = filepath.stat().st_size
        if file_size == 0:
            raise DocumentLoadError(f"File is empty: {filepath}")

        # Extension check
        extension = filepath.suffix.lower()
        if extension not in self.supported_extensions:
            raise UnsupportedFileError(
                f"Unsupported file type: {extension}. "
                f"Supported: {self.supported_extensions}"
            )

        # Size check
        max_bytes = self.max_file_size_mb * 1024 * 1024
        if file_size > max_bytes:
            raise FileSizeError(
                f"File too large: {file_size / (1024*1024):.1f}MB "
                f"(max: {self.max_file_size_mb}MB)"
            )

        logger.debug(
            "File validated: {} | size={:.2f}KB",
            filepath.name,
            file_size / 1024,
        )

        return {
            "valid": True,
            "filepath": str(filepath),
            "filename": filepath.name,
            "extension": extension,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 3),
        }

    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """
        Extract file-system metadata from a document.

        Args:
            filepath: Path to the file.

        Returns:
            Metadata dictionary.
        """
        filepath = Path(filepath)
        stat = filepath.stat()

        metadata = {
            "filename": filepath.name,
            "filepath": str(filepath.resolve()),
            "extension": filepath.suffix.lower(),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 3),
            "created_at": datetime.fromtimestamp(
                stat.st_ctime, tz=timezone.utc
            ).isoformat(),
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat(),
        }

        # Detect file type
        file_type = self.detect_file_type(filepath)
        metadata.update(file_type)

        logger.debug("Metadata extracted for: {}", filepath.name)
        return metadata

    def load_text_file(self, filepath: Path) -> dict[str, Any]:
        """
        Load a plain text file.

        Args:
            filepath: Path to the .txt file.

        Returns:
            Dict with extracted text and metadata.
        """
        filepath = Path(filepath)
        start_time = time.time()

        logger.info("Loading text file: {}", filepath.name)

        # Detect encoding
        try:
            import chardet
            with open(filepath, "rb") as f:
                raw = f.read()
            detected = chardet.detect(raw)
            encoding = detected.get("encoding", "utf-8") or "utf-8"
        except ImportError:
            encoding = "utf-8"

        try:
            with open(filepath, "r", encoding=encoding, errors="replace") as f:
                text = f.read()
        except Exception as e:
            raise DocumentLoadError(f"Failed to read text file: {e}")

        elapsed = time.time() - start_time
        metadata = self.extract_metadata(filepath)

        logger.info(
            "Text file loaded | file={} | chars={} | encoding={} | time={:.2f}s",
            filepath.name,
            len(text),
            encoding,
            elapsed,
        )

        return {
            "text": text,
            "metadata": metadata,
            "processing_method": "native",
            "encoding": encoding,
            "pages": 1,
            "processing_time_seconds": round(elapsed, 3),
        }

    def load(self, filepath: str | Path) -> dict[str, Any]:
        """
        Load a document from the given filepath.

        Routes to the appropriate parser based on file type.

        Args:
            filepath: Path to the document file.

        Returns:
            Dict with extracted text and metadata.

        Raises:
            DocumentLoadError: On any loading failure.
        """
        filepath = Path(filepath)
        start_time = time.time()

        logger.info("Loading document: {}", filepath.name)

        # Validate
        self.validate_file(filepath)

        # Route by file type
        file_type = self.detect_file_type(filepath)
        category = file_type["category"]

        if category == "text":
            return self.load_text_file(filepath)
        elif category == "pdf":
            # PDF loading is handled by the OCR/PDF parser modules
            # Return metadata + routing info
            metadata = self.extract_metadata(filepath)
            elapsed = time.time() - start_time
            return {
                "text": None,  # Will be filled by PDF/OCR pipeline
                "metadata": metadata,
                "processing_method": "pending_pdf_extraction",
                "pages": None,
                "processing_time_seconds": round(elapsed, 3),
                "requires_pdf_parser": True,
            }
        elif category == "docx":
            # DOCX loading is handled by the DOCX parser module
            metadata = self.extract_metadata(filepath)
            elapsed = time.time() - start_time
            return {
                "text": None,  # Will be filled by DOCX parser
                "metadata": metadata,
                "processing_method": "pending_docx_extraction",
                "pages": None,
                "processing_time_seconds": round(elapsed, 3),
                "requires_docx_parser": True,
            }
        else:
            raise UnsupportedFileError(
                f"No parser available for file type: {category}"
            )

    def batch_validate(self, filepaths: list[Path]) -> dict[str, list[Any]]:
        """
        Validate multiple files at once.

        Args:
            filepaths: List of file paths.

        Returns:
            Dict with 'valid' and 'invalid' lists.
        """
        valid: list[dict[str, Any]] = []
        invalid: list[dict[str, Any]] = []

        for fp in filepaths:
            try:
                result = self.validate_file(Path(fp))
                valid.append(result)
            except DocumentLoadError as e:
                invalid.append({"filepath": str(fp), "error": str(e)})

        logger.info(
            "Batch validation | total={} | valid={} | invalid={}",
            len(filepaths),
            len(valid),
            len(invalid),
        )

        return {"valid": valid, "invalid": invalid}
