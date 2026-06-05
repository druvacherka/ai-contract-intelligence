# Data + OCR Module — Contract Intelligence Platform

> Enterprise-grade document ingestion, OCR, and text extraction pipeline
> for the AI-powered Contract Intelligence platform.

---

## 🏗️ Architecture

```
data-ocr-module/
│
├── datasets/                  # Data storage
│   ├── raw/                   # Raw CUAD dataset files
│   ├── processed/             # Processed document outputs
│   ├── exports/               # Training-ready exports
│   └── schemas/               # JSON schemas for output validation
│
├── src/                       # Source code
│   ├── ingestion/             # Document ingestion & loading
│   │   ├── document_loader.py # Universal file loader + validator
│   │   └── docx_parser.py     # DOCX text extraction
│   │
│   ├── ocr/                   # OCR processing pipeline
│   │   ├── pdf_parser.py      # Native PDF text extraction
│   │   ├── ocr_engine.py      # Tesseract OCR engine
│   │   ├── image_preprocessor.py  # Image enhancement for OCR
│   │   └── scan_detector.py   # Scanned vs native PDF detection
│   │
│   ├── preprocessing/         # Text processing
│   │   ├── clean_text.py      # Legal text cleaning pipeline
│   │   └── json_formatter.py  # Structured JSON output
│   │
│   ├── dataset/               # CUAD dataset pipeline
│   │   ├── cuad_loader.py     # Dataset loading & inspection
│   │   ├── cuad_parser.py     # Annotation normalization
│   │   └── cuad_exporter.py   # Training data export
│   │
│   ├── utils/                 # Shared utilities
│   │   ├── config.py          # Centralized configuration
│   │   └── logger.py          # Loguru logging setup
│   │
│   └── tests/                 # Test suite
│       ├── conftest.py        # Shared fixtures
│       ├── test_pdf_parser.py # PDF + document loader tests
│       ├── test_ocr.py        # OCR + image processing tests
│       └── test_dataset.py    # CUAD + cleaning + formatting tests
│
├── uploads/                   # Document upload directory
├── logs/                      # Pipeline logs (rotating)
├── scripts/                   # Utility scripts
│
├── run.py                     # Master CLI orchestrator
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.11+**
- **Tesseract OCR** — [Install Guide](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler** (Windows only) — [Download](https://github.com/oschwartz10612/poppler-windows/releases)

### 2. Installation

```bash
# Clone and enter the module
cd data-ocr-module

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure environment
copy .env.example .env
# Edit .env with your Tesseract and Poppler paths
```

### 3. Usage

#### Process a Single Document

```bash
# PDF (native text)
python run.py --file uploads/contract.pdf

# DOCX
python run.py --file uploads/agreement.docx

# TXT
python run.py --file uploads/terms.txt

# Scanned PDF (auto-detects and uses OCR)
python run.py --file uploads/scanned_contract.pdf
```

#### Process a Directory

```bash
python run.py --dir uploads/
```

#### Run CUAD Dataset Pipeline

```bash
# Place CUADv1.json in datasets/raw/
python run.py --cuad
```

---

## 📋 Pipeline Modules

### Module 1 — CUAD Dataset Pipeline

| File | Purpose |
|------|---------|
| `cuad_loader.py` | Loads CUAD SQuAD-format JSON, inspects all 41 clause types |
| `cuad_parser.py` | Normalizes annotations, validates spans, deduplicates |
| `cuad_exporter.py` | Exports training JSON, individual files, CSV, reports |

**Output Schema:**
```json
{
  "contract_id": "a1b2c3d4e5f67890",
  "text": "Full contract text...",
  "clauses": [
    {
      "type": "Governing Law",
      "start": 1234,
      "end": 1280,
      "text": "laws of the State of Delaware"
    }
  ]
}
```

### Module 2 — Document Ingestion

| Feature | Details |
|---------|---------|
| File type detection | Extension + MIME type analysis |
| Validation | Existence, size limits, format support |
| Metadata extraction | File stats, timestamps, encoding |
| Supported formats | PDF, DOCX, TXT, scanned PDFs |

### Module 3 — PDF Extraction

| Engine | Role |
|--------|------|
| **pdfplumber** | Primary native text extraction |
| **PyMuPDF (fitz)** | Fallback extraction + metadata |

Handles corrupted PDFs, empty pages, and automatic OCR fallback.

### Module 4 — OCR Pipeline

```
PDF → detect text → if empty → convert to images
    → preprocess images → OCR each page → merge text
```

| Feature | Details |
|---------|---------|
| Image conversion | pdf2image with configurable DPI |
| Preprocessing | Grayscale, contrast, binarization, upscaling |
| Quality presets | `standard`, `low_quality`, `high_quality`, `fax` |
| Scan detection | Multi-heuristic analysis with confidence scoring |

### Module 5 — DOCX Extraction

Dual-engine extraction:
- **python-docx**: Full paragraph, table, and metadata extraction
- **docx2txt**: Fallback for complex documents

### Module 6 — Text Cleaning

| Feature | Details |
|---------|---------|
| Unicode normalization | Smart quotes, dashes, symbols |
| Header/footer removal | Pattern-based detection |
| Page number removal | Multiple formats handled |
| Legal text cleanup | Section numbers, exhibit refs |
| OCR artifact cleanup | Hyphenation, scattered chars |
| Sentence splitting | Legal abbreviation-aware |
| Clause formatting | Preserves section structure |

### Module 7 — Structured Output

**Document Output Schema:**
```json
{
  "document_id": "abc123def456...",
  "filename": "contract.pdf",
  "pages": 15,
  "document_type": "service_agreement",
  "metadata": {},
  "clean_text": "Full cleaned text...",
  "text_preview": "First 500 chars...",
  "processing_method": "native"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest src/tests/test_dataset.py

# Run only non-OCR tests (no Tesseract needed)
pytest -m "not ocr"

# Run with coverage
pytest --cov=src
```

---

## ⚙️ Configuration

All settings are configurable via `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `TESSERACT_CMD` | `C:\Program Files\Tesseract-OCR\tesseract.exe` | Tesseract executable path |
| `POPPLER_PATH` | `None` | Poppler bin directory (Windows) |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size |
| `OCR_DPI` | `300` | Image conversion DPI |
| `OCR_LANGUAGE` | `eng` | Tesseract language |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity |
| `LOG_ROTATION` | `10 MB` | Log file rotation size |

---

## 📦 Output Handoff

This module produces clean, structured outputs ready for the NLP team:

1. **Training JSON** (`datasets/exports/cuad_training_data.json`) — CUAD with normalized annotations
2. **Document JSON** (`datasets/processed/*.json`) — Individually processed documents
3. **Clause CSV** (`datasets/exports/cuad_clauses.csv`) — Flat clause analysis

All outputs follow validated JSON schemas in `datasets/schemas/`.

---

## 📝 Logging

Logs are written to `logs/pipeline.log` with automatic rotation.

```
2024-01-15 10:30:45.123 | INFO     | src.ocr.pdf_parser:extract:215 | Starting PDF extraction: contract.pdf
2024-01-15 10:30:46.456 | INFO     | src.ocr.scan_detector:detect:178 | Scan detection: is_scanned=False
2024-01-15 10:30:47.789 | INFO     | src.preprocessing.clean_text:clean:312 | Text cleaned | reduction=12.3%
```

---

## 🔗 Integration Points

This module is designed to hand off to:

| Consumer | Interface | Format |
|----------|-----------|--------|
| NLP Pipeline | `datasets/exports/` | JSON with spans |
| Vector DB | `datasets/processed/` | Clean text per document |
| AI Chat | `datasets/processed/` | Structured JSON |
| Analytics | `datasets/exports/cuad_clauses.csv` | Flat CSV |

---

## 📄 License

Internal use — Contract Intelligence Platform.
