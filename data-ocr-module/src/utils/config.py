"""
Centralized configuration management for the Data + OCR pipeline.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Config:
    """Pipeline configuration loaded from environment variables."""

    # --- Project Paths ---
    PROJECT_ROOT: Path = _PROJECT_ROOT
    DATASETS_DIR: Path = _PROJECT_ROOT / "datasets"
    RAW_DIR: Path = _PROJECT_ROOT / "datasets" / "raw"
    PROCESSED_DIR: Path = _PROJECT_ROOT / "datasets" / "processed"
    EXPORTS_DIR: Path = _PROJECT_ROOT / "datasets" / "exports"
    SCHEMAS_DIR: Path = _PROJECT_ROOT / "datasets" / "schemas"
    UPLOADS_DIR: Path = _PROJECT_ROOT / "uploads"
    LOGS_DIR: Path = _PROJECT_ROOT / "logs"

    # --- Tesseract OCR ---
    @staticmethod
    def _find_tesseract() -> str:
        """Auto-detect Tesseract from common install locations."""
        import shutil
        # Check if tesseract is on PATH first
        path_cmd = shutil.which("tesseract")
        if path_cmd:
            return path_cmd
        # Common Windows install locations
        candidates = [
            os.path.expanduser(r"~\tesseract.exe"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\ProgramData\chocolatey\bin\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "") or _find_tesseract()

    # --- Poppler ---
    POPPLER_PATH: str | None = os.getenv("POPPLER_PATH", None)

    # --- Dataset Paths ---
    CUAD_DATASET_PATH: Path = Path(
        os.getenv("CUAD_DATASET_PATH", str(_PROJECT_ROOT / "datasets" / "raw"))
    )
    CUAD_OUTPUT_PATH: Path = Path(
        os.getenv("CUAD_OUTPUT_PATH", str(_PROJECT_ROOT / "datasets" / "processed"))
    )
    EXPORT_PATH: Path = Path(
        os.getenv("EXPORT_PATH", str(_PROJECT_ROOT / "datasets" / "exports"))
    )

    # --- Processing Settings ---
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    OCR_DPI: int = int(os.getenv("OCR_DPI", "300"))
    OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "eng")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE: str = os.getenv("LOG_FILE", str(_PROJECT_ROOT / "logs" / "pipeline.log"))
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "10 MB")

    # --- SpaCy ---
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")

    # --- Supported File Types ---
    SUPPORTED_EXTENSIONS: set[str] = {
        ".pdf", ".docx", ".doc", ".txt",
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp",
    }

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required directories if they don't exist."""
        for dir_path in [
            cls.RAW_DIR,
            cls.PROCESSED_DIR,
            cls.EXPORTS_DIR,
            cls.SCHEMAS_DIR,
            cls.UPLOADS_DIR,
            cls.LOGS_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def max_file_size_bytes(cls) -> int:
        """Return max file size in bytes."""
        return cls.MAX_FILE_SIZE_MB * 1024 * 1024
