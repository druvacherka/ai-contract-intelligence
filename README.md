<div align="center">

# 📄 AI Contract Intelligence & Risk Scoring System

**Enterprise-grade OCR + NLP + Risk Analysis platform for legal and compliance teams**

[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/DevOps-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)

</div>

---

## 🔍 Project Overview

The **AI Contract Intelligence** platform is an enterprise-grade system designed to help legal and compliance teams analyze contracts at scale. The platform combines **OCR**, **NLP**, and **Risk Scoring** to extract, classify, and score legal documents with AI precision.

### Key Capabilities

- **📸 OCR Engine** — Extracts text from scanned PDFs, images, DOCX, and handwritten documents using Tesseract + PyMuPDF with self-healing retry logic
- **🧠 NLP Clause Classifier** — Identifies 10 legal clause types (Termination, Confidentiality, Liability, Arbitration, etc.) using TF-IDF + keyword analysis
- **⚠️ Risk Scoring Engine** — Evaluates contracts across 5 risk dimensions and produces a 0–100 risk score with severity levels
- **🚀 Full Pipeline API** — Upload a contract (PDF/DOCX/image) and get clause classification + risk score in a single API call

---

## 📁 Repository Structure

```
ai-contract-intelligence/
│
├── frontend/                    # React 19 + Vite
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Main dashboard
│   │   │   ├── Upload.jsx       # Contract upload page
│   │   │   └── ContractResults.jsx  # Analysis results display
│   │   ├── services/
│   │   │   └── api.js           # Backend API client
│   │   ├── App.jsx              # Root app with routing
│   │   └── index.css            # Global styles
│   ├── package.json
│   └── vite.config.js
│
├── data-ocr-module/             # Python Backend (FastAPI)
│   ├── server.py                # FastAPI server with all endpoints
│   ├── requirements.txt         # Python dependencies
│   ├── src/
│   │   ├── ocr/
│   │   │   ├── document_loader.py   # File type detection & loading
│   │   │   ├── pdf_parser.py        # PDF text extraction (PyMuPDF)
│   │   │   ├── docx_parser.py       # DOCX text extraction
│   │   │   ├── scan_detector.py     # Scanned vs digital detection
│   │   │   ├── ocr_engine.py        # Tesseract OCR with self-healing retries
│   │   │   ├── image_preprocessor.py # Adaptive binarization & presets
│   │   │   └── text_cleaner.py      # Post-OCR text normalization
│   │   ├── nlp/
│   │   │   ├── nlp_engine.py        # Legal clause classifier (TF-IDF)
│   │   │   └── risk_engine.py       # Multi-dimensional risk scorer
│   │   └── tests/
│   │       ├── test_ocr.py          # OCR unit tests (130 tests)
│   │       ├── test_nlp.py          # NLP classifier tests
│   │       ├── test_risk.py         # Risk engine tests
│   │       └── test_api.py          # API endpoint tests
│
├── ml/                          # NLP & ML Engineering (Legal-BERT, Embeddings, FAISS)
│   ├── api/                     # High-level Python interface
│   ├── embeddings/              # Semantic embeddings & FAISS vector search
│   ├── inference/               # Model inference (clause, severity, risk scoring)
│   ├── training/                # Legal-BERT fine-tuning pipelines
│   └── evaluation/              # Model performance evaluation & reports
│
├── backend/                     # Integrated FastAPI Backend (FastAPI, Uvicorn)
│   ├── routes/                  # API endpoint routers (analyze, upload, etc.)
│   └── services/                # Backend adapters (OCR, NLP, FAISS integration)
│
├── infra/                       # DevOps & Infrastructure
│   ├── docker/
│   ├── github_actions/
│   └── terraform/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

| Layer          | Technology                                |
|---------------|-------------------------------------------|
| **Frontend**  | React 19, Vite, CSS                       |
| **Backend**   | FastAPI, Uvicorn, Pydantic                |
| **OCR**       | Tesseract, PyMuPDF (fitz), Pillow         |
| **NLP**       | scikit-learn (TF-IDF), regex patterns     |
| **Risk**      | Custom multi-dimensional scoring engine   |
| **DevOps**    | Docker, Docker Compose, Nginx             |

---

## 🚀 Quick Start

### Prerequisites

- **Python** >= 3.11
- **Node.js** >= 20
- **Tesseract OCR** installed and on PATH
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/druvacherka/ai-contract-intelligence.git
cd ai-contract-intelligence
```

### 2. Set Up Backend

```bash
cd data-ocr-module
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 3. Start Backend Server

```bash
cd data-ocr-module
python server.py
```

The API will be available at `http://localhost:8000`

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

### 5. Start with Docker (Optional)

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint              | Description                                    |
|--------|-----------------------|------------------------------------------------|
| GET    | `/health`             | Health check                                   |
| GET    | `/api/pipeline/status`| Pipeline component status                      |
| POST   | `/api/upload`         | Upload document for OCR extraction             |
| GET    | `/api/documents`      | List processed documents                       |
| GET    | `/api/documents/{id}` | Get specific document                          |
| POST   | `/upload-contract`    | **Full pipeline**: Upload → OCR → NLP → Risk   |
| POST   | `/analyze-text`       | Analyze raw contract text (NLP + Risk)         |
| POST   | `/analyze-file`       | Analyze file with Legal-BERT + Named Entity Extraction |

### Response Schema (NLP + Risk)

```json
{
  "clause": "Termination",
  "confidence": 92.4,
  "risk_score": 78,
  "risk_level": "High"
}
```

---

## 🧪 Running Tests

### Unit Tests (Pytest)

```bash
cd data-ocr-module
# Run all unit tests (ignoring cuad dataset test if dependencies like pandas are missing)
python -m pytest src/tests/ --ignore=src/tests/test_dataset.py -v
```

### End-to-End & Browser Flow Verification

These scripts test end-to-end integration and API-level contract adherence:

```bash
cd data-ocr-module
# Run NLP API classification & risk scoring E2E tests
python e2e_test.py

# Run live frontend-to-backend browser flow simulation test
python browser_flow_test.py
```

---

## 🔬 OCR Engine Features

- **PyMuPDF** for 10–50x faster PDF rendering (replaces pdf2image/Poppler)
- **Self-healing OCR**: Automatically retries with handwriting preset if confidence < 65%
- **Adaptive binarization**: Otsu + local thresholding for degraded scans
- **Preset system**: `default`, `clean`, `noisy`, `handwriting` configurations
- **Multi-format**: PDF, DOCX, PNG, JPG, TIFF, BMP

---

## ⚠️ Risk Scoring Dimensions

| Dimension              | Weight | Examples                                      |
|-----------------------|--------|-----------------------------------------------|
| Unfavorable Obligations| 25%   | "sole discretion", "without notice"           |
| Liability Exposure     | 30%   | "unlimited liability", "no cap"               |
| Vague Language         | 15%   | "reasonable efforts", "as deemed appropriate" |
| Missing Protections    | 20%   | No indemnification cap, no termination clause |
| Renewal Risks          | 10%   | "auto-renewal", "evergreen"                   |

**Risk Levels**: Low (0–30) · Medium (31–70) · High (71–100)

---

## 🌿 Branch Strategy

| Branch             | Purpose                        |
|-------------------|--------------------------------|
| `main`            | Production-ready releases      |
| `develop`         | Integration branch             |
| `feature/ocr`     | OCR engine development         |
| `feature/nlp`     | NLP/ML model development       |
| `feature/backend` | Backend API development        |
| `feature/frontend`| Frontend UI development        |
| `feature/devops`  | Infrastructure & CI/CD         |

---

## 👥 Team

| Member              | Responsibility         |
|--------------------|------------------------|
| **Saniya**         | Frontend + DevOps      |
| **Prajwal**        | OCR + Data Processing  |
| **Dhruva**         | NLP / ML Engineering   |
| **Vishwas Chandra**| Backend / API          |

---

<div align="center">

**Built with ❤️ by the AI Contract Intelligence Team**

</div>
