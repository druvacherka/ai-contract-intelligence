"""
OCR Engine — Tesseract-based OCR Pipeline.

Converts scanned PDF pages to images, applies image preprocessing,
runs Tesseract OCR, and merges results into clean text output.
"""

import time
from pathlib import Path
from typing import Any

from PIL import Image

from src.utils.config import Config
from src.utils.logger import logger


class OCRError(Exception):
    """Raised when OCR processing fails."""
    pass


class OCREngine:
    """
    Full OCR pipeline using Tesseract OCR.

    Workflow:
        PDF → detect text → if empty → convert to images
        → preprocess images → OCR each page → merge text

    Features:
    - Scanned PDF detection
    - PDF-to-image conversion via pdf2image
    - Image preprocessing for better OCR accuracy
    - Batch OCR processing
    - Low-quality scan handling
    - Configurable DPI and language
    """

    def __init__(
        self,
        tesseract_cmd: str | None = None,
        poppler_path: str | None = None,
        dpi: int | None = None,
        language: str | None = None,
    ) -> None:
        self.tesseract_cmd = tesseract_cmd or Config.TESSERACT_CMD
        self.poppler_path = poppler_path or Config.POPPLER_PATH
        self.dpi = dpi or Config.OCR_DPI
        self.language = language or Config.OCR_LANGUAGE

        # Configure Tesseract
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        logger.info(
            "OCREngine initialized | dpi={} | lang={} | tesseract={}",
            self.dpi,
            self.language,
            self.tesseract_cmd,
        )

    def pdf_to_images(
        self, filepath: Path, dpi: int | None = None
    ) -> list[Image.Image]:
        """
        Convert PDF pages to PIL Images using PyMuPDF (fitz).

        Uses fitz (PyMuPDF) for rendering — 10-50x faster than
        pdf2image/Poppler and requires no external binaries.

        Args:
            filepath: Path to the PDF file.
            dpi: DPI for image conversion (default: configured DPI).

        Returns:
            List of PIL Image objects, one per page.
        """
        import fitz  # PyMuPDF

        dpi = dpi or self.dpi
        # Cap at 200 DPI for scanned PDFs — higher isn't needed for
        # handwriting and just wastes time
        if dpi > 200:
            dpi = 200
        logger.info("Converting PDF to images: {} @ {}dpi (fitz)", filepath.name, dpi)

        start_time = time.time()

        try:
            doc = fitz.open(str(filepath))
            images: list[Image.Image] = []
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)

            doc.close()

            elapsed = time.time() - start_time
            logger.info(
                "PDF to images complete | pages={} | time={:.2f}s",
                len(images),
                elapsed,
            )
            return images

        except Exception as e:
            logger.error("PDF to image conversion failed: {}", e)
            raise OCRError(f"PDF to image conversion failed: {e}")

    def preprocess_image(self, image: Image.Image, preset: str = "standard") -> Image.Image:
        """
        Preprocess an image for better OCR accuracy.

        Args:
            image: PIL Image to preprocess.
            preset: Quality preset to use (e.g. 'standard', 'handwriting', 'low_quality').

        Returns:
            Preprocessed PIL Image.
        """
        from src.ocr.image_preprocessor import ImagePreprocessor
        preprocessor = ImagePreprocessor(preset=preset)
        return preprocessor.preprocess(image)

    def ocr_image(
        self,
        image: Image.Image,
        preprocess: bool = True,
        preset: str = "standard",
        config: str = "",
    ) -> dict[str, Any]:
        """
        Run OCR on a single image.

        Args:
            image: PIL Image to OCR.
            preprocess: Whether to preprocess the image first.
            preset: Quality preset to use.
            config: Additional Tesseract config flags.

        Returns:
            Dict with 'text', 'confidence', and processing info.
        """
        import pytesseract

        start_time = time.time()

        # Preprocess if requested
        if preprocess:
            processed_image = self.preprocess_image(image, preset=preset)
        else:
            processed_image = image

        # Default Tesseract config — PSM 3 = fully automatic page segmentation
        # OEM 3 = default, uses LSTM + legacy combined
        if not config:
            config = "--psm 3 --oem 3"

        try:
            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=config,
            )

            # Get confidence data
            try:
                data = pytesseract.image_to_data(
                    processed_image,
                    lang=self.language,
                    config=config,
                    output_type=pytesseract.Output.DICT,
                )
                confidences = [
                    int(c)
                    for c in data.get("conf", [])
                    if str(c).strip() and int(c) > 0
                ]
                avg_confidence = (
                    round(sum(confidences) / len(confidences), 2)
                    if confidences
                    else 0.0
                )
            except Exception:
                avg_confidence = -1.0

            stripped = text.strip()

            # Fallback 1: if OCR confidence is low, or char count is low, retry with "handwriting" preset
            # (which uses adaptive local thresholding and is optimized for handwritten text)
            if preprocess and preset != "handwriting" and (avg_confidence < 65.0 or len(stripped) < 30):
                logger.info(
                    "Low OCR confidence ({:.1f}%) or yield ({} chars) with preset '{}'. "
                    "Retrying with 'handwriting' preset (adaptive thresholding)...",
                    avg_confidence, len(stripped), preset
                )
                try:
                    handwriting_result = self.ocr_image(
                        image,
                        preprocess=True,
                        preset="handwriting",
                        config=config
                    )
                    # If the handwriting result yielded better confidence OR significantly more text, use it
                    h_text = handwriting_result["text"]
                    h_conf = handwriting_result["confidence"]
                    if len(h_text.strip()) > len(stripped) * 1.5 or h_conf > avg_confidence + 10:
                        logger.info(
                            "Handwriting preset improved OCR: confidence {:.1f}% -> {:.1f}%, chars {} -> {}",
                            avg_confidence, h_conf, len(stripped), len(h_text)
                        )
                        return handwriting_result
                except Exception as he:
                    logger.warning("Handwriting preset fallback failed: {}", he)

            # Fallback 2: if very little text extracted, retry with different
            # PSM modes better suited for handwritten / irregular layouts
            if len(stripped) < 20 and preprocess:
                logger.info("Low text yield (%d chars), retrying with PSM 4 + no preprocess", len(stripped))
                for fallback_psm in ["--psm 4 --oem 3", "--psm 6 --oem 3", "--psm 1 --oem 3"]:
                    try:
                        # Retry on the ORIGINAL image (no binarization)
                        raw_gray = image if image.mode == "L" else image.convert("L")
                        retry_text = pytesseract.image_to_string(
                            raw_gray,
                            lang=self.language,
                            config=fallback_psm,
                        )
                        if len(retry_text.strip()) > len(stripped):
                            text = retry_text
                            stripped = text.strip()
                            logger.info("Fallback %s yielded %d chars", fallback_psm, len(stripped))
                            break
                    except Exception:
                        continue

            elapsed = time.time() - start_time

            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "char_count": len(text.strip()),
                "processing_time_seconds": round(elapsed, 3),
            }

        except Exception as e:
            logger.error("OCR failed for image: {}", e)
            raise OCRError(f"Tesseract OCR failed: {e}")

    def ocr_pdf(
        self,
        filepath: str | Path,
        preprocess: bool = True,
        preset: str = "standard",
    ) -> dict[str, Any]:
        """
        Full OCR pipeline for a scanned PDF.

        Converts all pages to images, preprocesses, runs OCR,
        and merges into a single text output.

        Args:
            filepath: Path to the scanned PDF.
            preprocess: Whether to preprocess images.
            preset: Quality preset to use.

        Returns:
            Dict with merged text, per-page results, and metadata.
        """
        filepath = Path(filepath)
        logger.info("Starting OCR pipeline for: {}", filepath.name)
        overall_start = time.time()

        # Convert PDF to images
        images = self.pdf_to_images(filepath)

        if not images:
            raise OCRError(f"No images extracted from PDF: {filepath.name}")

        # OCR each page
        page_results: list[dict[str, Any]] = []
        for i, image in enumerate(images):
            logger.info("OCR processing page {}/{}", i + 1, len(images))
            try:
                result = self.ocr_image(image, preprocess=preprocess, preset=preset)
                result["page_number"] = i + 1
                page_results.append(result)
            except OCRError as e:
                logger.warning("OCR failed for page {}: {}", i + 1, e)
                page_results.append(
                    {
                        "page_number": i + 1,
                        "text": "",
                        "confidence": 0.0,
                        "char_count": 0,
                        "error": str(e),
                    }
                )

        # Merge results
        full_text = "\n\n".join(
            pr["text"] for pr in page_results if pr.get("text")
        )

        # Calculate overall confidence
        confidences = [
            pr["confidence"]
            for pr in page_results
            if pr.get("confidence", 0) > 0
        ]
        avg_confidence = (
            round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        )

        overall_elapsed = time.time() - overall_start

        result = {
            "full_text": full_text,
            "pages": page_results,
            "metadata": {
                "num_pages": len(images),
                "pages_with_text": sum(
                    1 for pr in page_results if pr.get("char_count", 0) > 0
                ),
                "total_chars": len(full_text),
                "avg_confidence": avg_confidence,
                "dpi": self.dpi,
                "language": self.language,
            },
            "extraction_method": "ocr_tesseract",
            "needs_ocr": False,  # Already OCR'd
            "processing_time_seconds": round(overall_elapsed, 3),
        }

        logger.info(
            "OCR pipeline complete | file={} | pages={} | chars={} | "
            "confidence={:.1f}% | time={:.2f}s",
            filepath.name,
            len(images),
            len(full_text),
            avg_confidence,
            overall_elapsed,
        )

        return result

    def batch_ocr(
        self,
        filepaths: list[Path],
        preprocess: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Run OCR on multiple PDF files.

        Args:
            filepaths: List of PDF file paths.
            preprocess: Whether to preprocess images.

        Returns:
            List of OCR results.
        """
        from tqdm import tqdm

        results: list[dict[str, Any]] = []
        logger.info("Starting batch OCR for {} files", len(filepaths))

        for filepath in tqdm(filepaths, desc="Batch OCR"):
            try:
                result = self.ocr_pdf(filepath, preprocess=preprocess)
                result["filename"] = Path(filepath).name
                results.append(result)
            except OCRError as e:
                logger.error("Batch OCR failed for {}: {}", filepath, e)
                results.append(
                    {
                        "filename": Path(filepath).name,
                        "full_text": "",
                        "error": str(e),
                    }
                )

        logger.info(
            "Batch OCR complete | total={} | successful={}",
            len(filepaths),
            sum(1 for r in results if "error" not in r),
        )
        return results
