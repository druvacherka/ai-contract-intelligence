"""
OCR Agent — Dual-Engine Document Text Extraction (Agent 1).

Handles text extraction from all supported file types using a
dual-engine strategy: native PDF parsing for digital PDFs, Tesseract
OCR for scanned documents, EasyOCR for images (with Tesseract fallback),
and dedicated parsers for DOCX / TXT files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.base_agent import BaseAgent
from src.ingestion.docx_parser import DOCXParser
from src.ocr.ocr_engine import OCREngine
from src.ocr.pdf_parser import PDFParser
from src.utils.logger import logger

# Image file extensions handled by the OCR path
_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}

# Try to import EasyOCR once at module level
_easyocr_reader: Any | None = None
_easyocr_available: bool = False

try:
    import easyocr  # type: ignore[import-untyped]
    _easyocr_reader = easyocr.Reader(["en"], gpu=False)
    _easyocr_available = True
    logger.info("EasyOCR reader initialised (GPU=False)")
except ImportError:
    logger.info("easyocr not installed — will use Tesseract for images")
except Exception as exc:
    logger.warning("EasyOCR init failed ({}). Falling back to Tesseract.", exc)


class OCRAgent(BaseAgent):
    """Agent 1 — Dual-engine OCR / text extraction.

    Routing logic:

    * **PDF (digital):** ``PDFParser.extract()`` for native text.
    * **PDF (scanned):** ``OCREngine.ocr_pdf()`` via Tesseract.
    * **Images:** EasyOCR first (better for handwriting), Tesseract fallback.
    * **DOCX:** ``DOCXParser.extract()``.
    * **TXT:** Direct file read.

    Context contract:

    * **Input:**  ``{file_path: str}``
    * **Output adds:** ``{raw_text, pages, ocr_method, ocr_confidence, file_ext}``
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = "OCRAgent"
        self._pdf_parser = PDFParser()
        self._ocr_engine = OCREngine()
        self._docx_parser = DOCXParser()

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        file_path = Path(context["file_path"])
        ext = file_path.suffix.lower()
        context["file_ext"] = ext

        logger.info("OCRAgent processing '{}' (ext={})", file_path.name, ext)

        if ext == ".pdf":
            context = self._handle_pdf(file_path, context)
        elif ext in _IMAGE_EXTENSIONS:
            context = self._handle_image(file_path, context)
        elif ext in {".docx", ".doc"}:
            context = self._handle_docx(file_path, context)
        elif ext == ".txt":
            context = self._handle_txt(file_path, context)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        logger.info(
            "OCRAgent result | method={} | chars={} | pages={} | confidence={:.1f}",
            context.get("ocr_method", "unknown"),
            len(context.get("raw_text", "")),
            context.get("pages", 0),
            context.get("ocr_confidence", 0.0),
        )
        return context

    # ------------------------------------------------------------------
    # File-type handlers
    # ------------------------------------------------------------------

    def _handle_pdf(self, path: Path, ctx: dict[str, Any]) -> dict[str, Any]:
        """Handle PDF files — try native extraction, fall back to OCR."""
        # Step 1: Try native text extraction
        try:
            result = self._pdf_parser.extract(path)
            full_text: str = result.get("full_text", "")
            needs_ocr: bool = result.get("needs_ocr", False)
            num_pages: int = result.get("metadata", {}).get("num_pages", 1)

            if full_text.strip() and not needs_ocr:
                ctx["raw_text"] = full_text
                ctx["pages"] = num_pages
                ctx["ocr_method"] = result.get("extraction_method", "pdf_native")
                ctx["ocr_confidence"] = 95.0  # native extraction is high-confidence
                return ctx

            logger.info("PDF has no native text — switching to OCR pipeline")
        except Exception as exc:
            logger.warning("PDFParser.extract failed ({}). Trying OCR.", exc)

        # Step 2: Scanned PDF — Tesseract OCR
        try:
            ocr_result = self._ocr_engine.ocr_pdf(path)
            ctx["raw_text"] = ocr_result.get("full_text", "")
            ctx["pages"] = ocr_result.get("metadata", {}).get("num_pages", 1)
            ctx["ocr_method"] = "ocr_tesseract"
            ctx["ocr_confidence"] = ocr_result.get("metadata", {}).get(
                "avg_confidence", 0.0
            )
        except Exception as exc:
            logger.error("OCR pipeline failed for PDF: {}", exc)
            ctx["raw_text"] = ""
            ctx["pages"] = 0
            ctx["ocr_method"] = "ocr_failed"
            ctx["ocr_confidence"] = 0.0

        return ctx

    def _handle_image(self, path: Path, ctx: dict[str, Any]) -> dict[str, Any]:
        """Handle image files — EasyOCR first (best for handwriting), Tesseract fallback."""
        from PIL import Image

        image = Image.open(str(path))

        # Strategy 1: EasyOCR (preferred — handles handwritten + printed text)
        if _easyocr_available and _easyocr_reader is not None:
            try:
                # Always use detail=1 to get confidence scores and handle handwriting
                results = _easyocr_reader.readtext(str(path), detail=1)

                if results:
                    texts = [r[1] for r in results]
                    confs = [r[2] for r in results]
                    text = " ".join(texts).strip()

                    if text:
                        avg_conf = round(sum(confs) / len(confs) * 100, 1) if confs else 80.0
                        ctx["raw_text"] = text
                        ctx["pages"] = 1
                        ctx["ocr_method"] = "easyocr"
                        ctx["ocr_confidence"] = avg_conf
                        ctx["is_handwritten"] = avg_conf < 85.0  # auto-detect hint
                        return ctx

                logger.info("EasyOCR returned empty text — trying Tesseract")
            except Exception as exc:
                logger.warning("EasyOCR failed ({}). Falling back to Tesseract.", exc)

        # Strategy 2: Tesseract — try standard first, then handwriting preset
        try:
            # First try standard preset
            ocr_result = self._ocr_engine.ocr_image(image, preprocess=True, preset="standard")
            text = ocr_result.get("text", "")
            confidence = ocr_result.get("confidence", 0.0)

            # If low confidence or little text, retry with handwriting preset
            if confidence < 60.0 or len(text.strip()) < 30:
                logger.info("Low confidence ({:.1f}%) — retrying with handwriting preset", confidence)
                hw_result = self._ocr_engine.ocr_image(image, preprocess=True, preset="handwriting")
                hw_text = hw_result.get("text", "")
                hw_conf = hw_result.get("confidence", 0.0)

                if len(hw_text.strip()) > len(text.strip()) or hw_conf > confidence:
                    text = hw_text
                    confidence = hw_conf
                    ctx["is_handwritten"] = True

            ctx["raw_text"] = text
            ctx["pages"] = 1
            ctx["ocr_method"] = "ocr_tesseract"
            ctx["ocr_confidence"] = confidence
        except Exception as exc:
            logger.error("Tesseract OCR failed for image: {}", exc)
            ctx["raw_text"] = ""
            ctx["pages"] = 1
            ctx["ocr_method"] = "ocr_failed"
            ctx["ocr_confidence"] = 0.0

        return ctx

    def _handle_docx(self, path: Path, ctx: dict[str, Any]) -> dict[str, Any]:
        """Handle DOCX files via DOCXParser."""
        try:
            result = self._docx_parser.extract(path)
            ctx["raw_text"] = result.get("full_text", "")
            ctx["pages"] = result.get("stats", {}).get("num_paragraphs", 1)
            ctx["ocr_method"] = "docx_parser"
            ctx["ocr_confidence"] = 99.0
        except Exception as exc:
            logger.error("DOCXParser failed: {}", exc)
            ctx["raw_text"] = ""
            ctx["pages"] = 0
            ctx["ocr_method"] = "docx_failed"
            ctx["ocr_confidence"] = 0.0
        return ctx

    def _handle_txt(self, path: Path, ctx: dict[str, Any]) -> dict[str, Any]:
        """Handle plain text files via direct read."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            ctx["raw_text"] = text
            ctx["pages"] = 1
            ctx["ocr_method"] = "direct_read"
            ctx["ocr_confidence"] = 100.0
        except Exception as exc:
            logger.error("Text file read failed: {}", exc)
            ctx["raw_text"] = ""
            ctx["pages"] = 1
            ctx["ocr_method"] = "read_failed"
            ctx["ocr_confidence"] = 0.0
        return ctx
