"""
PDF Parser — Native PDF Text Extraction.

Extracts text from native (non-scanned) PDFs using pdfplumber
and PyMuPDF (fitz) with page-by-page parsing, metadata extraction,
and fallback handling for corrupted files.
"""

import time
from pathlib import Path
from typing import Any

from src.utils.logger import logger


class PDFParseError(Exception):
    """Raised when PDF parsing fails."""
    pass


class PDFParser:
    """
    Extracts text from native PDFs using pdfplumber (primary)
    and PyMuPDF/fitz (fallback).

    Features:
    - Page-by-page text extraction
    - PDF metadata extraction
    - Table detection hints
    - Fallback between extraction engines
    - Corrupted PDF handling
    """

    def __init__(self) -> None:
        logger.info("PDFParser initialized")

    def extract_with_pdfplumber(self, filepath: Path) -> dict[str, Any]:
        """
        Extract text using pdfplumber (primary method).

        Args:
            filepath: Path to the PDF file.

        Returns:
            Dict with pages, full text, and metadata.
        """
        import pdfplumber

        logger.info("Extracting with pdfplumber: {}", filepath.name)
        start_time = time.time()

        pages_text: list[dict[str, Any]] = []
        metadata: dict[str, Any] = {}

        try:
            with pdfplumber.open(str(filepath)) as pdf:
                # Extract PDF metadata
                metadata = {
                    "num_pages": len(pdf.pages),
                    "pdf_metadata": pdf.metadata or {},
                }

                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ""
                        # Get page dimensions
                        page_info = {
                            "page_number": i + 1,
                            "text": text,
                            "char_count": len(text),
                            "width": float(page.width),
                            "height": float(page.height),
                            "has_text": len(text.strip()) > 0,
                        }

                        # Check for tables
                        try:
                            tables = page.extract_tables()
                            page_info["num_tables"] = len(tables) if tables else 0
                        except Exception:
                            page_info["num_tables"] = 0

                        pages_text.append(page_info)

                    except Exception as e:
                        logger.warning(
                            "pdfplumber: Failed to extract page {}: {}", i + 1, e
                        )
                        pages_text.append(
                            {
                                "page_number": i + 1,
                                "text": "",
                                "char_count": 0,
                                "has_text": False,
                                "error": str(e),
                            }
                        )

        except Exception as e:
            logger.error("pdfplumber extraction failed for {}: {}", filepath.name, e)
            raise PDFParseError(f"pdfplumber failed: {e}")

        elapsed = time.time() - start_time
        full_text = "\n\n".join(p["text"] for p in pages_text if p.get("text"))

        logger.info(
            "pdfplumber extraction complete | pages={} | chars={} | time={:.2f}s",
            len(pages_text),
            len(full_text),
            elapsed,
        )

        return {
            "pages": pages_text,
            "full_text": full_text,
            "metadata": metadata,
            "extraction_method": "pdfplumber",
            "processing_time_seconds": round(elapsed, 3),
        }

    def extract_with_pymupdf(self, filepath: Path) -> dict[str, Any]:
        """
        Extract text using PyMuPDF/fitz (fallback method).

        Args:
            filepath: Path to the PDF file.

        Returns:
            Dict with pages, full text, and metadata.
        """
        import fitz  # PyMuPDF

        logger.info("Extracting with PyMuPDF: {}", filepath.name)
        start_time = time.time()

        pages_text: list[dict[str, Any]] = []
        metadata: dict[str, Any] = {}

        try:
            doc = fitz.open(str(filepath))

            # Extract metadata
            metadata = {
                "num_pages": doc.page_count,
                "pdf_metadata": dict(doc.metadata) if doc.metadata else {},
                "is_encrypted": doc.is_encrypted,
                "is_pdf": doc.is_pdf,
            }

            for i in range(doc.page_count):
                try:
                    page = doc.load_page(i)
                    text = page.get_text("text") or ""

                    page_info = {
                        "page_number": i + 1,
                        "text": text,
                        "char_count": len(text),
                        "width": float(page.rect.width),
                        "height": float(page.rect.height),
                        "has_text": len(text.strip()) > 0,
                    }
                    pages_text.append(page_info)

                except Exception as e:
                    logger.warning("PyMuPDF: Failed to extract page {}: {}", i + 1, e)
                    pages_text.append(
                        {
                            "page_number": i + 1,
                            "text": "",
                            "char_count": 0,
                            "has_text": False,
                            "error": str(e),
                        }
                    )

            doc.close()

        except Exception as e:
            logger.error("PyMuPDF extraction failed for {}: {}", filepath.name, e)
            raise PDFParseError(f"PyMuPDF failed: {e}")

        elapsed = time.time() - start_time
        full_text = "\n\n".join(p["text"] for p in pages_text if p.get("text"))

        logger.info(
            "PyMuPDF extraction complete | pages={} | chars={} | time={:.2f}s",
            len(pages_text),
            len(full_text),
            elapsed,
        )

        return {
            "pages": pages_text,
            "full_text": full_text,
            "metadata": metadata,
            "extraction_method": "pymupdf",
            "processing_time_seconds": round(elapsed, 3),
        }

    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """
        Extract only metadata from a PDF (fast, no text extraction).

        Args:
            filepath: Path to the PDF file.

        Returns:
            PDF metadata dictionary.
        """
        import fitz

        try:
            doc = fitz.open(str(filepath))
            metadata = {
                "num_pages": doc.page_count,
                "pdf_metadata": dict(doc.metadata) if doc.metadata else {},
                "is_encrypted": doc.is_encrypted,
                "file_size_mb": round(
                    Path(filepath).stat().st_size / (1024 * 1024), 3
                ),
            }
            doc.close()
            return metadata
        except Exception as e:
            logger.error("Metadata extraction failed: {}", e)
            return {"error": str(e)}

    def is_scanned_pdf(self, filepath: Path, threshold: float = 0.1) -> bool:
        """
        Detect whether a PDF is scanned (image-based) or native text.

        A PDF is considered scanned if the average text per page
        falls below the threshold ratio.

        Args:
            filepath: Path to the PDF file.
            threshold: Minimum average chars-per-page / expected-chars ratio.

        Returns:
            True if the PDF appears to be scanned.
        """
        try:
            result = self.extract_with_pymupdf(filepath)
            pages = result.get("pages", [])
            if not pages:
                return True

            pages_with_text = sum(1 for p in pages if p.get("has_text", False))
            text_ratio = pages_with_text / len(pages)

            is_scanned = text_ratio < threshold
            logger.info(
                "Scanned PDF detection | file={} | pages_with_text={}/{} | ratio={:.2f} | is_scanned={}",
                filepath.name,
                pages_with_text,
                len(pages),
                text_ratio,
                is_scanned,
            )
            return is_scanned

        except PDFParseError:
            logger.warning("Could not analyze PDF for scan detection: {}", filepath.name)
            return True  # Assume scanned if we can't read it

    def extract(self, filepath: str | Path) -> dict[str, Any]:
        """
        Extract text from a PDF using the best available method.

        Tries pdfplumber first, falls back to PyMuPDF.
        If both produce empty text, signals that OCR may be needed.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Extraction result dict.
        """
        filepath = Path(filepath)
        logger.info("Starting PDF extraction: {}", filepath.name)

        if not filepath.exists():
            raise PDFParseError(f"File not found: {filepath}")

        if filepath.suffix.lower() != ".pdf":
            raise PDFParseError(f"Not a PDF file: {filepath}")

        # Try pdfplumber first
        result = None
        try:
            result = self.extract_with_pdfplumber(filepath)
            if result["full_text"].strip():
                result["needs_ocr"] = False
                return result
            logger.info("pdfplumber returned empty text, trying PyMuPDF fallback")
        except PDFParseError as e:
            logger.warning("pdfplumber failed, trying PyMuPDF: {}", e)

        # Fallback to PyMuPDF
        try:
            result = self.extract_with_pymupdf(filepath)
            if result["full_text"].strip():
                result["needs_ocr"] = False
                return result
            logger.info("PyMuPDF also returned empty text — likely a scanned PDF")
        except PDFParseError as e:
            logger.error("Both extraction methods failed for: {}", filepath.name)
            if result is None:
                raise PDFParseError(
                    f"All PDF extraction methods failed for {filepath.name}: {e}"
                )

        # If we get here, both methods returned empty text
        result["needs_ocr"] = True
        result["full_text"] = ""
        logger.info("PDF needs OCR processing: {}", filepath.name)
        return result
