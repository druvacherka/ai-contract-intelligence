"""
Image Preprocessing — Advanced Image Enhancement for OCR.

Provides dedicated image preprocessing utilities to improve
OCR accuracy on low-quality scans, faxes, and photographs.
"""

from typing import Any

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from src.utils.logger import logger


class ImagePreprocessor:
    """
    Advanced image preprocessing pipeline for OCR optimization.

    Handles:
    - Grayscale conversion
    - Noise removal
    - Contrast enhancement
    - Deskewing
    - Border removal
    - Adaptive binarization
    - Resolution upscaling
    """

    # Preset configurations for different scan qualities
    PRESETS: dict[str, dict[str, Any]] = {
        "standard": {
            "contrast": 1.5,
            "sharpness": 1.3,
            "threshold": 140,
            "min_width": 1000,
            "denoise": False,
            "binarize_method": "global",
        },
        "low_quality": {
            "contrast": 2.0,
            "sharpness": 1.5,
            "threshold": "adaptive",
            "min_width": 1500,
            "denoise": True,
            "binarize_method": "adaptive",
            "adaptive_block_size": 41,
            "adaptive_c": 10,
        },
        "high_quality": {
            "contrast": 1.2,
            "sharpness": 1.1,
            "threshold": 150,
            "min_width": 800,
            "denoise": False,
            "binarize_method": "global",
        },
        "fax": {
            "contrast": 2.5,
            "sharpness": 2.0,
            "threshold": 120,
            "min_width": 2000,
            "denoise": True,
            "binarize_method": "global",
        },
        "handwriting": {
            "contrast": 1.8,
            "sharpness": 1.4,
            "threshold": "adaptive",
            "min_width": 1800,
            "denoise": True,
            "binarize_method": "adaptive",
            "adaptive_block_size": 31,
            "adaptive_c": 7,
        },
    }

    def __init__(self, preset: str = "standard") -> None:
        if preset not in self.PRESETS:
            logger.warning(
                "Unknown preset '{}', using 'standard'", preset
            )
            preset = "standard"

        self.config = self.PRESETS[preset]
        self.preset = preset
        logger.info("ImagePreprocessor initialized | preset={}", preset)

    def to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale."""
        if image.mode != "L":
            image = image.convert("L")
            logger.debug("Converted to grayscale")
        return image

    def enhance_contrast(
        self, image: Image.Image, factor: float | None = None
    ) -> Image.Image:
        """Enhance image contrast."""
        factor = factor or self.config["contrast"]
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor)
        logger.debug("Contrast enhanced: factor={}", factor)
        return image

    def enhance_sharpness(
        self, image: Image.Image, factor: float | None = None
    ) -> Image.Image:
        """Enhance image sharpness."""
        factor = factor or self.config["sharpness"]
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(factor)
        logger.debug("Sharpness enhanced: factor={}", factor)
        return image

    def binarize(
        self,
        image: Image.Image,
        threshold: int | str | None = None,
        method: str | None = None,
    ) -> Image.Image:
        """
        Apply binary thresholding to create black-and-white image.

        Args:
            image: Grayscale PIL Image.
            threshold: Pixel intensity threshold (0-255) or 'adaptive'/'otsu'.
            method: Binarization method ('global', 'otsu', 'adaptive').

        Returns:
            Binarized PIL Image.
        """
        if image.mode != "L":
            image = image.convert("L")

        method = method or self.config.get("binarize_method", "global")
        threshold = threshold or self.config.get("threshold", 128)

        # Allow threshold parameter to override method
        if isinstance(threshold, str):
            if threshold in ("adaptive", "otsu", "global"):
                method = threshold
                threshold = None

        if method == "adaptive":
            block_size = self.config.get("adaptive_block_size", 41)
            C = self.config.get("adaptive_c", 10)
            logger.debug("Applying adaptive local thresholding (block_size={}, C={})", block_size, C)
            return self._adaptive_threshold_integral(image, block_size=block_size, C=C)

        elif method == "otsu":
            computed_threshold = self._compute_otsu_threshold(image)
            logger.debug("Applying Otsu thresholding (computed threshold={})", computed_threshold)
            image = image.point(lambda p: 255 if p > computed_threshold else 0, mode="1")
            return image.convert("L")

        else:  # global
            val = int(threshold) if threshold is not None else 128
            logger.debug("Applying global thresholding (threshold={})", val)
            image = image.point(lambda p: 255 if p > val else 0, mode="1")
            return image.convert("L")

    def _compute_otsu_threshold(self, image: Image.Image) -> int:
        """Compute the Otsu threshold for a grayscale image."""
        import numpy as np

        img_arr = np.array(image, dtype=np.uint8)
        hist, _ = np.histogram(img_arr, bins=256, range=(0, 256))
        
        total = img_arr.size
        current_max = 0.0
        threshold = 127
        
        sum_total = np.sum(np.arange(256) * hist)
        sum_back = 0.0
        weight_back = 0.0
        
        for t in range(256):
            weight_back += hist[t]
            if weight_back == 0:
                continue
            weight_fore = total - weight_back
            if weight_fore == 0:
                break
                
            sum_back += t * hist[t]
            mean_back = sum_back / weight_back
            mean_fore = (sum_total - sum_back) / weight_fore
            
            var_between = weight_back * weight_fore * (mean_back - mean_fore) ** 2
            
            if var_between > current_max:
                current_max = var_between
                threshold = t
                
        return threshold

    def _adaptive_threshold_integral(self, image: Image.Image, block_size: int = 41, C: int = 10) -> Image.Image:
        """Apply local adaptive thresholding using integral image for O(1) performance."""
        import numpy as np

        # Convert to grayscale array
        img_arr = np.array(image, dtype=np.float32)
        h, w = img_arr.shape
        
        # Calculate integral image
        integral = np.zeros((h + 1, w + 1), dtype=np.float32)
        integral[1:, 1:] = np.cumsum(np.cumsum(img_arr, axis=0), axis=1)
        
        # Grid of coordinates
        y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        
        # Block boundaries
        r = block_size // 2
        y1 = np.maximum(0, y - r)
        y2 = np.minimum(h - 1, y + r)
        x1 = np.maximum(0, x - r)
        x2 = np.minimum(w - 1, x + r)
        
        # Sum of block using integral image
        count = (y2 - y1 + 1) * (x2 - x1 + 1)
        block_sum = (
            integral[y2 + 1, x2 + 1]
            - integral[y1, x2 + 1]
            - integral[y2 + 1, x1]
            + integral[y1, x1]
        )
        
        mean = block_sum / count
        
        # Threshold: if pixel value < mean - C, it is text (0), else background (255)
        binary = np.where(img_arr < (mean - C), 0, 255).astype(np.uint8)
        return Image.fromarray(binary)


    def remove_noise(self, image: Image.Image) -> Image.Image:
        """Apply median filter for noise removal."""
        image = image.filter(ImageFilter.MedianFilter(size=3))
        logger.debug("Noise removed via median filter")
        return image

    def upscale(
        self, image: Image.Image, min_width: int | None = None
    ) -> Image.Image:
        """
        Upscale image if too small for reliable OCR.

        Args:
            image: PIL Image.
            min_width: Minimum acceptable width in pixels.

        Returns:
            Upscaled PIL Image (or original if already large enough).
        """
        min_width = min_width or self.config["min_width"]
        width, height = image.size

        if width < min_width:
            scale = min_width / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.LANCZOS)
            logger.debug("Upscaled: {}x{} -> {}x{}", width, height, *new_size)

        return image

    def remove_borders(
        self, image: Image.Image, border_ratio: float = 0.02
    ) -> Image.Image:
        """
        Remove dark borders from scanned images.

        Args:
            image: PIL Image.
            border_ratio: Percentage of each edge to crop.

        Returns:
            Cropped PIL Image.
        """
        width, height = image.size
        crop_x = int(width * border_ratio)
        crop_y = int(height * border_ratio)

        if crop_x > 0 and crop_y > 0:
            image = image.crop((crop_x, crop_y, width - crop_x, height - crop_y))
            logger.debug(
                "Borders removed: {}px horizontal, {}px vertical",
                crop_x,
                crop_y,
            )

        return image

    def auto_rotate(self, image: Image.Image) -> Image.Image:
        """
        Auto-rotate image based on EXIF orientation data.

        Args:
            image: PIL Image.

        Returns:
            Correctly oriented PIL Image.
        """
        try:
            image = ImageOps.exif_transpose(image)
            logger.debug("Auto-rotation applied from EXIF")
        except Exception:
            pass  # No EXIF data or rotation not needed
        return image

    def invert_if_needed(self, image: Image.Image) -> Image.Image:
        """
        Invert image if background is dark (white text on black).

        Uses average pixel value to detect dark backgrounds.

        Args:
            image: Grayscale PIL Image.

        Returns:
            Potentially inverted PIL Image.
        """
        if image.mode != "L":
            image = image.convert("L")

        # Sample center region
        width, height = image.size
        center_crop = image.crop(
            (width // 4, height // 4, 3 * width // 4, 3 * height // 4)
        )

        pixels = list(center_crop.getdata())
        avg_brightness = sum(pixels) / len(pixels) if pixels else 128

        if avg_brightness < 100:  # Dark background
            image = ImageOps.invert(image)
            logger.debug(
                "Image inverted: avg_brightness={:.0f}", avg_brightness
            )

        return image

    def preprocess(self, image: Image.Image) -> Image.Image:
        """
        Run the full preprocessing pipeline.

        Pipeline order:
        1. Auto-rotate
        2. Grayscale conversion
        3. Invert if needed
        4. Upscale
        5. Remove borders
        6. Noise removal (if enabled)
        7. Contrast enhancement
        8. Sharpness enhancement
        9. Binarization

        Args:
            image: Raw PIL Image.

        Returns:
            Preprocessed PIL Image ready for OCR.
        """
        logger.info(
            "Preprocessing image | preset={} | size={}x{}",
            self.preset,
            image.width,
            image.height,
        )

        image = self.auto_rotate(image)
        image = self.to_grayscale(image)
        image = self.invert_if_needed(image)
        image = self.upscale(image)
        image = self.remove_borders(image)

        if self.config.get("denoise", False):
            image = self.remove_noise(image)

        image = self.enhance_contrast(image)
        image = self.enhance_sharpness(image)
        image = self.binarize(image)

        logger.info(
            "Preprocessing complete | final_size={}x{}",
            image.width,
            image.height,
        )
        return image

    def assess_quality(self, image: Image.Image) -> dict[str, Any]:
        """
        Assess the quality of a scan for OCR readiness.

        Args:
            image: PIL Image to assess.

        Returns:
            Quality assessment dict with score and recommendations.
        """
        if image.mode != "L":
            image = image.convert("L")

        width, height = image.size
        pixels = list(image.getdata())
        avg_brightness = sum(pixels) / len(pixels) if pixels else 0
        contrast = max(pixels) - min(pixels) if pixels else 0

        # Quality score (0-100)
        score = 50.0

        # Resolution bonus
        if width >= 2000:
            score += 20
        elif width >= 1000:
            score += 10
        else:
            score -= 10

        # Contrast bonus
        if contrast > 200:
            score += 15
        elif contrast > 150:
            score += 10
        elif contrast < 100:
            score -= 15

        # Brightness (not too dark, not too light)
        if 100 < avg_brightness < 200:
            score += 15
        elif avg_brightness < 50 or avg_brightness > 240:
            score -= 20

        score = max(0, min(100, score))

        # Recommend preset
        if score >= 70:
            recommended_preset = "high_quality"
        elif score >= 40:
            recommended_preset = "standard"
        else:
            recommended_preset = "low_quality"

        return {
            "quality_score": round(score, 1),
            "resolution": f"{width}x{height}",
            "avg_brightness": round(avg_brightness, 1),
            "contrast_range": contrast,
            "recommended_preset": recommended_preset,
            "needs_preprocessing": score < 60,
        }
