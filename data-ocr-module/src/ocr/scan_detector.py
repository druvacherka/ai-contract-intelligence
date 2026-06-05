"""
Scanned PDF Detector — Intelligent Scan Detection.

Determines whether a PDF is natively digitized or scanned (image-based)
using multiple heuristics: text density, font analysis, and image coverage.
"""

import time
from pathlib import Path
from typing import Any

from src.utils.logger import logger


class ScanDetector:
    """
    Multi-heuristic scanner to determine if a PDF is scanned or native.

    Heuristics used:
    1. Text density per page (char count)
    2. Font presence analysis (via PyMuPDF)
    3. Image-to-page area ratio
    4. Embedded image count vs page count

    A PDF is considered "scanned" if most pages lack embedded text.
    """

    # Minimum chars per page to consider it as having native text
    MIN_CHARS_PER_PAGE: int = 50

    # Minimum ratio of pages with text to total pages
    MIN_TEXT_PAGE_RATIO: float = 0.3

    def __init__(self) -> None:
        logger.info("ScanDetector initialized")

    def analyze_text_density(self, filepath: Path) -> dict[str, Any]:
        """
        Analyze text density across all pages using PyMuPDF.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Analysis result with per-page and aggregate metrics.
        """
        import fitz

        logger.info("Analyzing text density: {}", filepath.name)

        try:
            doc = fitz.open(str(filepath))
        except Exception as e:
            logger.error("Cannot open PDF for analysis: {}", e)
            return {"error": str(e), "is_scanned": True}

        page_analyses: list[dict[str, Any]] = []

        for i in range(doc.page_count):
            page = doc.load_page(i)
            text = page.get_text("text") or ""
            char_count = len(text.strip())

            # Count fonts on the page
            font_count = 0
            try:
                fonts = page.get_fonts()
                font_count = len(fonts)
            except Exception:
                pass

            # Count images on the page
            image_count = 0
            try:
                images = page.get_images(full=True)
                image_count = len(images)
            except Exception:
                pass

            # Calculate image coverage ratio
            image_area_ratio = 0.0
            page_area = page.rect.width * page.rect.height
            if image_count > 0 and page_area > 0:
                try:
                    for img in page.get_images(full=True):
                        xref = img[0]
                        try:
                            img_rects = page.get_image_rects(xref)
                            for rect in img_rects:
                                img_area = rect.width * rect.height
                                image_area_ratio += img_area / page_area
                        except Exception:
                            pass
                except Exception:
                    pass

            has_text = char_count >= self.MIN_CHARS_PER_PAGE

            page_analyses.append(
                {
                    "page_number": i + 1,
                    "char_count": char_count,
                    "has_text": has_text,
                    "font_count": font_count,
                    "image_count": image_count,
                    "image_area_ratio": round(image_area_ratio, 3),
                }
            )

        doc.close()

        # Aggregate analysis
        total_pages = len(page_analyses)
        pages_with_text = sum(1 for p in page_analyses if p["has_text"])
        text_page_ratio = pages_with_text / max(total_pages, 1)

        total_images = sum(p["image_count"] for p in page_analyses)
        avg_chars = (
            sum(p["char_count"] for p in page_analyses) / max(total_pages, 1)
        )
        avg_image_ratio = (
            sum(p["image_area_ratio"] for p in page_analyses) / max(total_pages, 1)
        )

        return {
            "total_pages": total_pages,
            "pages_with_text": pages_with_text,
            "text_page_ratio": round(text_page_ratio, 3),
            "avg_chars_per_page": round(avg_chars, 1),
            "total_images": total_images,
            "avg_image_area_ratio": round(avg_image_ratio, 3),
            "page_analyses": page_analyses,
        }

    def detect(self, filepath: str | Path) -> dict[str, Any]:
        """
        Determine whether a PDF is scanned or native.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Detection result with 'is_scanned' boolean,
            confidence, and analysis details.
        """
        filepath = Path(filepath)
        logger.info("Running scan detection: {}", filepath.name)
        start_time = time.time()

        analysis = self.analyze_text_density(filepath)

        if "error" in analysis:
            return {
                "filepath": str(filepath),
                "is_scanned": True,
                "confidence": 0.5,
                "reason": f"Could not analyze PDF: {analysis['error']}",
                "recommended_method": "ocr",
            }

        text_ratio = analysis["text_page_ratio"]
        avg_chars = analysis["avg_chars_per_page"]
        avg_image_ratio = analysis["avg_image_area_ratio"]

        # Decision logic
        is_scanned = False
        confidence = 0.0
        reasons: list[str] = []

        # Low text ratio
        if text_ratio < self.MIN_TEXT_PAGE_RATIO:
            is_scanned = True
            confidence += 0.4
            reasons.append(
                f"Low text page ratio: {text_ratio:.2f} "
                f"(threshold: {self.MIN_TEXT_PAGE_RATIO})"
            )

        # Very low average chars
        if avg_chars < self.MIN_CHARS_PER_PAGE:
            is_scanned = True
            confidence += 0.3
            reasons.append(
                f"Low avg chars/page: {avg_chars:.0f} "
                f"(threshold: {self.MIN_CHARS_PER_PAGE})"
            )

        # High image coverage
        if avg_image_ratio > 0.7:
            is_scanned = True
            confidence += 0.2
            reasons.append(
                f"High image coverage: {avg_image_ratio:.2f}"
            )

        # If text ratio is high and chars are good, it's native
        if text_ratio > 0.8 and avg_chars > 200:
            is_scanned = False
            confidence = 0.9
            reasons = ["High text density indicates native PDF"]

        if not reasons:
            reasons = ["Moderate text density — likely native PDF"]
            confidence = 0.7

        confidence = min(confidence, 1.0)
        elapsed = time.time() - start_time

        recommended = "ocr" if is_scanned else "native"

        result = {
            "filepath": str(filepath),
            "filename": filepath.name,
            "is_scanned": is_scanned,
            "confidence": round(confidence, 2),
            "recommended_method": recommended,
            "reasons": reasons,
            "analysis": {
                "text_page_ratio": analysis["text_page_ratio"],
                "avg_chars_per_page": analysis["avg_chars_per_page"],
                "total_pages": analysis["total_pages"],
                "total_images": analysis["total_images"],
                "avg_image_area_ratio": analysis["avg_image_area_ratio"],
            },
            "detection_time_seconds": round(elapsed, 3),
        }

        logger.info(
            "Scan detection result | file={} | is_scanned={} | confidence={:.0%} | method={}",
            filepath.name,
            is_scanned,
            confidence,
            recommended,
        )

        return result
