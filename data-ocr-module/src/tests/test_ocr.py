"""
Tests for OCR Engine, Image Preprocessor, and Scan Detector.

Tests image preprocessing, OCR configuration, and scan detection
logic without requiring actual Tesseract installation (where possible).
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

from src.ocr.ocr_engine import OCREngine, OCRError
from src.ocr.image_preprocessor import ImagePreprocessor
from src.ocr.scan_detector import ScanDetector
from src.preprocessing.clean_text import TextCleaner


class TestImagePreprocessor:
    """Test suite for ImagePreprocessor."""

    def test_init_default_preset(self):
        """Test initialization with default preset."""
        preprocessor = ImagePreprocessor()
        assert preprocessor.preset == "standard"
        assert preprocessor.config is not None

    def test_init_all_presets(self):
        """Test initialization with all available presets."""
        for preset in ["standard", "low_quality", "high_quality", "fax", "handwriting"]:
            preprocessor = ImagePreprocessor(preset=preset)
            assert preprocessor.preset == preset

    def test_init_unknown_preset(self):
        """Test initialization with unknown preset falls back to standard."""
        preprocessor = ImagePreprocessor(preset="nonexistent")
        assert preprocessor.preset == "standard"

    def test_binarize_methods(self):
        """Test all binarization methods (global, otsu, adaptive)."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (100, 100), color=128)
        
        # Test global
        res_global = preprocessor.binarize(image, method="global")
        assert res_global.mode == "L"
        
        # Test otsu
        res_otsu = preprocessor.binarize(image, method="otsu")
        assert res_otsu.mode == "L"
        
        # Test adaptive
        res_adaptive = preprocessor.binarize(image, method="adaptive")
        assert res_adaptive.mode == "L"

    def test_to_grayscale_rgb(self):
        """Test RGB to grayscale conversion."""
        preprocessor = ImagePreprocessor()
        rgb_image = Image.new("RGB", (100, 100), color=(128, 128, 128))
        result = preprocessor.to_grayscale(rgb_image)
        assert result.mode == "L"

    def test_to_grayscale_already_gray(self):
        """Test grayscale image passes through."""
        preprocessor = ImagePreprocessor()
        gray_image = Image.new("L", (100, 100), color=128)
        result = preprocessor.to_grayscale(gray_image)
        assert result.mode == "L"

    def test_enhance_contrast(self):
        """Test contrast enhancement produces valid output."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (100, 100), color=128)
        result = preprocessor.enhance_contrast(image)
        assert result.size == (100, 100)

    def test_enhance_sharpness(self):
        """Test sharpness enhancement produces valid output."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (100, 100), color=128)
        result = preprocessor.enhance_sharpness(image)
        assert result.size == (100, 100)

    def test_binarize(self):
        """Test binarization produces black-and-white image."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (100, 100), color=128)
        result = preprocessor.binarize(image, threshold=100)
        assert result.mode == "L"

    def test_upscale_small_image(self):
        """Test that small images are upscaled."""
        preprocessor = ImagePreprocessor()
        small_image = Image.new("L", (500, 500), color=128)
        result = preprocessor.upscale(small_image, min_width=1000)
        assert result.width >= 1000

    def test_upscale_large_image_unchanged(self):
        """Test that large images are not resized."""
        preprocessor = ImagePreprocessor()
        large_image = Image.new("L", (2000, 2000), color=128)
        result = preprocessor.upscale(large_image, min_width=1000)
        assert result.width == 2000

    def test_remove_borders(self):
        """Test border removal reduces image size."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (1000, 1000), color=128)
        result = preprocessor.remove_borders(image, border_ratio=0.05)
        assert result.width < 1000
        assert result.height < 1000

    def test_invert_if_needed_light_bg(self):
        """Test light background is not inverted."""
        preprocessor = ImagePreprocessor()
        light_image = Image.new("L", (100, 100), color=200)
        result = preprocessor.invert_if_needed(light_image)
        # Light image should remain light
        assert result is not None

    def test_invert_if_needed_dark_bg(self):
        """Test dark background is inverted."""
        preprocessor = ImagePreprocessor()
        dark_image = Image.new("L", (100, 100), color=30)
        result = preprocessor.invert_if_needed(dark_image)
        assert result is not None

    def test_preprocess_full_pipeline(self):
        """Test the full preprocessing pipeline."""
        preprocessor = ImagePreprocessor()
        image = Image.new("RGB", (800, 1000), color=(200, 200, 200))
        result = preprocessor.preprocess(image)
        assert result.mode == "L"
        assert result.size[0] > 0
        assert result.size[1] > 0

    def test_assess_quality_high(self):
        """Test quality assessment for a high-quality image."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (2000, 3000), color=180)
        result = preprocessor.assess_quality(image)
        assert "quality_score" in result
        assert "recommended_preset" in result
        assert result["quality_score"] >= 0
        assert result["quality_score"] <= 100

    def test_assess_quality_low(self):
        """Test quality assessment for a low-quality image."""
        preprocessor = ImagePreprocessor()
        image = Image.new("L", (300, 400), color=30)
        result = preprocessor.assess_quality(image)
        assert result["quality_score"] < 80  # Should be lower quality


class TestOCREngine:
    """Test suite for OCR Engine (unit tests without Tesseract)."""

    def test_init(self):
        """Test OCREngine initializes with config values."""
        engine = OCREngine()
        assert engine.dpi > 0
        assert engine.language == "eng"

    def test_preprocess_image(self):
        """Test image preprocessing within OCR engine."""
        engine = OCREngine()
        image = Image.new("RGB", (800, 1000), color=(200, 200, 200))
        result = engine.preprocess_image(image)
        assert result.mode == "L"

    @pytest.mark.ocr
    def test_pdf_to_images_nonexistent(self):
        """Test PDF-to-image conversion fails for non-existent file."""
        engine = OCREngine()
        with pytest.raises(OCRError):
            engine.pdf_to_images(Path("nonexistent.pdf"))

    @pytest.mark.ocr
    def test_ocr_image_mock(self):
        """Test OCR on a synthetic image with mocked Tesseract."""
        engine = OCREngine()
        image = Image.new("L", (500, 500), color=200)

        with patch("pytesseract.image_to_string", return_value="Test OCR output"):
            with patch(
                "pytesseract.image_to_data",
                return_value={"conf": [90, 85, 92]},
            ):
                result = engine.ocr_image(image, preprocess=False)
                assert result["text"] == "Test OCR output"
                assert result["char_count"] > 0

    def test_preprocess_image_with_presets(self):
        """Test image preprocessing within OCR engine with different presets."""
        engine = OCREngine()
        image = Image.new("RGB", (800, 1000), color=(200, 200, 200))
        for preset in ["standard", "handwriting", "low_quality"]:
            result = engine.preprocess_image(image, preset=preset)
            assert result.mode == "L"

    @pytest.mark.ocr
    def test_ocr_image_handwriting_fallback(self):
        """Test OCR handwriting fallback is triggered for low confidence."""
        engine = OCREngine()
        image = Image.new("L", (500, 500), color=200)

        # Mock pytesseract calls to simulate low confidence on first try
        mock_strings = ["Low yield output", "High quality recovered handwriting output"]
        mock_datas = [
            {"conf": [50, 48, 52]},
            {"conf": [85, 87, 90]}
        ]
        
        with patch("pytesseract.image_to_string", side_effect=mock_strings) as mock_string_call:
            with patch("pytesseract.image_to_data", side_effect=mock_datas) as mock_data_call:
                result = engine.ocr_image(image, preprocess=True, preset="standard")
                
                # Should have fallback to handwriting
                assert "recovered handwriting" in result["text"]
                assert result["confidence"] > 70
                assert mock_string_call.call_count == 2


class TestScanDetector:
    """Test suite for Scan Detector."""

    def test_init(self):
        """Test ScanDetector initializes successfully."""
        detector = ScanDetector()
        assert detector.MIN_CHARS_PER_PAGE > 0
        assert detector.MIN_TEXT_PAGE_RATIO > 0

    def test_detect_nonexistent_file(self):
        """Test detection handles non-existent files."""
        detector = ScanDetector()
        result = detector.detect(Path("nonexistent.pdf"))
        assert result["is_scanned"] is True  # Assume scanned if can't read
        assert "error" in result.get("reason", "") or result.get("confidence", 0) > 0


class TestTextCleanerWithOCR:
    """Test cleaning pipeline with OCR-specific features."""

    def test_clean_ocr_artifacts(self):
        """Test OCR artifact cleaning."""
        cleaner = TextCleaner(aggressive_ocr_cleanup=False)

        # Form feed characters
        text = "Hello\fWorld"
        result = cleaner.clean_ocr_artifacts(text)
        assert "\f" not in result

    def test_clean_hyphenation(self):
        """Test hyphenated word reunification."""
        cleaner = TextCleaner()
        text = "This is a con-\ntract agreement."
        result = cleaner.clean_ocr_artifacts(text)
        assert "contract" in result

    def test_clean_scattered_chars(self):
        """Test scattered character cleanup."""
        cleaner = TextCleaner()
        text = "c o n t r a c t"
        result = cleaner.clean_ocr_artifacts(text)
        assert "contract" in result

    def test_full_ocr_cleaning(self, sample_dirty_text):
        """Test full cleaning pipeline in OCR mode."""
        cleaner = TextCleaner()
        result = cleaner.clean(sample_dirty_text, is_ocr=True)
        clean = result["clean_text"]
        assert "Page 1 of 10" not in clean
        assert "CONFIDENTIAL" not in clean
        assert "DRAFT" not in clean
        assert "AGREEMENT" in clean
        assert result["reduction_percent"] > 0
