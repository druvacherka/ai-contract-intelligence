<div align="center">

<img src="https://img.shields.io/badge/🧠_IntelliAnalyze_AI-Contract_Intelligence-blueviolet?style=for-the-badge&labelColor=1a1a2e&color=6C63FF" alt="IntelliAnalyze AI" />

# IntelliAnalyze AI

### 🔬 Autonomous Multi-Agent Contract Intelligence Platform

> *Transform legal contracts into actionable intelligence in seconds — powered by a 7-agent AI pipeline with OCR, NLP, Risk Scoring, and AI Summarization.*

[![React 19](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/Gemini_2.0-Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3-F55036?style=flat-square&logo=meta&logoColor=white)](https://groq.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

**[🚀 Live Demo](#quick-start)** · **[📖 Documentation](#-architecture)** · **[🧪 API Reference](#-api-endpoints)** · **[👥 Team](#-team)**

</div>

---

## ✨ Why IntelliAnalyze AI?

<table>
<tr>
<td width="50%">

### 🎯 The Problem
Legal teams spend **60% of their time** manually reviewing contracts. Critical risks get missed, clauses go unclassified, and compliance gaps grow. Traditional tools are rule-based, fragile, and can't handle scanned documents.

### 💡 Our Solution
IntelliAnalyze AI deploys a **7-agent autonomous pipeline** that processes any contract format — scanned PDFs, images, DOCX, or plain text — and delivers comprehensive intelligence reports with risk scores, clause classification, entity extraction, and AI-powered recommendations.

</td>
<td width="50%">

### 🏆 What Makes Us Different

| Feature | Traditional Tools | IntelliAnalyze AI |
|---------|:---:|:---:|
| Scanned PDF Support | ❌ | ✅ Dual-engine OCR |
| Multi-Agent Pipeline | ❌ | ✅ 7 Autonomous Agents |
| AI Summarization | ❌ | ✅ Gemini + Groq |
| Real-time Risk Scoring | ⚠️ Basic | ✅ 5-Dimensional |
| Fallback Architecture | ❌ | ✅ Triple Redundancy |
| Self-healing OCR | ❌ | ✅ Auto-retry Logic |
| Vector Search | ❌ | ✅ Semantic Search |

</td>
</tr>
</table>

---

## 🧬 The 7-Agent AI Pipeline

> Each contract passes through **7 specialized autonomous agents** in sequence. If one AI provider fails, the system automatically falls back to the next.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  🔍 Agent 1 │───▶│  🧹 Agent 2 │───▶│  🏷️ Agent 3 │───▶│  📋 Agent 4 │
│  OCR Agent  │    │ Text Cleaner│    │  NER Agent  │    │Clause Detect│
│             │    │             │    │             │    │             │
│ Tesseract + │    │ Normalize & │    │ Extract all │    │ Classify 15+│
│ PyMuPDF     │    │ Structure   │    │ entities    │    │ clause types│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                   ┌──────────────────────────────────────────────┘
                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  ⚠️ Agent 5 │───▶│  🤖 Agent 6 │───▶│  ✅ Agent 7 │
│Risk Analyzer│    │AI Summarizer│    │  Compiler   │
│             │    │             │    │             │
│ Score 0-100 │    │ Gemini/Groq │    │ Final Intel │
│ 5 dimensions│    │ Summaries   │    │ Report      │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Agent Details

| # | Agent | Technology | Function |
|---|-------|-----------|----------|
| 01 | **OCR Agent** | Tesseract + PyMuPDF + OpenCV | Extracts text from PDFs, scans, images with dual-engine OCR and self-healing retry |
| 02 | **Text Cleaner** | Custom NLP Pipeline | Normalizes encoding, removes noise, fixes OCR artifacts, structures raw text |
| 03 | **NER Agent** | SpaCy `en_core_web_lg` | Extracts organizations, persons, dates, monetary values, jurisdictions |
| 04 | **Clause Detector** | TF-IDF + Keyword Analysis | Classifies 15+ clause types: Termination, Confidentiality, Liability, IP, etc. |
| 05 | **Risk Analyzer** | Multi-dimensional Scoring | Scores each clause 0-100 across 5 risk dimensions with severity flagging |
| 06 | **AI Summarizer** | Google Gemini 2.0 Flash | Generates executive summaries, key findings, and actionable recommendations |
| 07 | **Report Compiler** | Aggregation Engine | Assembles final intelligence report with all scores, entities, and assessments |

### 🛡️ Triple Fallback Architecture

```
Primary: Google Gemini 2.0 Flash
    ↓ (if quota exceeded or error)
Fallback: Groq — Llama 3.3 70B  
    ↓ (if unavailable)  
Emergency: Rule-based Analysis Engine
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                               │
│  React 19 + Vite + TailwindCSS                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Dashboard│ │  Upload  │ │ Results  │ │ Semantic Search  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│  Auth: Supabase (Google OAuth + Email/Password)              │
└──────────────────────────┬───────────────────────────────────┘
                           │ REST API (JWT Auth)
┌──────────────────────────▼───────────────────────────────────┐
│                     BACKEND — FastAPI                         │
│  ┌───────────────────────────────────────────────────┐       │
│  │            7-Agent Pipeline (AgentPipeline)        │       │
│  │  OCR → Clean → NER → Clause → Risk → AI → Compile │       │
│  └───────────────────────────────────────────────────┘       │
│  ┌──────────┐ ┌──────────────┐ ┌────────────────────┐       │
│  │ Supabase │ │ PDF Report   │ │ Vector Search      │       │
│  │ Client   │ │ Generator    │ │ (Embeddings)       │       │
│  └──────────┘ └──────────────┘ └────────────────────┘       │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                     DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ MongoDB Atlas│  │   Supabase   │  │ File System      │   │
│  │ (Contracts,  │  │ (Auth Only)  │  │ (Uploads, PDFs)  │   │
│  │  Users,      │  │              │  │                  │   │
│  │  Embeddings) │  │              │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

<table>
<tr>
<td>

### Frontend
- **React 19** — Modern UI with hooks
- **Vite** — Lightning-fast HMR
- **TailwindCSS** — Utility-first styling
- **React Router v7** — Client-side routing
- **Supabase JS** — Auth + OAuth

</td>
<td>

### Backend
- **FastAPI** — High-performance async API
- **Uvicorn** — ASGI server
- **SpaCy** — NLP + NER engine
- **Tesseract OCR** — Text extraction
- **PyMuPDF** — PDF processing

</td>
<td>

### AI & Data
- **Google Gemini 2.0** — AI summarization
- **Groq (Llama 3.3)** — Fallback LLM
- **MongoDB Atlas** — Document database
- **Supabase** — Auth & OAuth
- **SentenceTransformers** — Vector embeddings

</td>
</tr>
</table>

---

## 📁 Project Structure

```
ai-contract-intelligence/
│
├── 📂 frontend/                        # React 19 + Vite Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Landing page with 7-agent showcase
│   │   │   ├── Dashboard.jsx          # Intelligence dashboard with stats
│   │   │   ├── Upload.jsx             # Drag & drop contract upload
│   │   │   ├── ContractResults.jsx    # Full analysis results view
│   │   │   ├── Search.jsx             # Semantic vector search
│   │   │   ├── Login.jsx              # Auth with Google OAuth
│   │   │   ├── Signup.jsx             # Registration page
│   │   │   ├── Analytics.jsx          # Portfolio analytics
│   │   │   ├── Settings.jsx           # User settings
│   │   │   ├── Help.jsx               # Documentation
│   │   │   └── Team.jsx               # Team page
│   │   ├── components/
│   │   │   ├── Navbar.jsx             # Navigation with theme toggle
│   │   │   ├── ProfileDropdown.jsx    # User profile menu
│   │   │   ├── ThemeToggle.jsx        # Dark/light mode
│   │   │   └── auth/
│   │   │       └── ProtectedRoute.jsx # Auth guard
│   │   ├── context/
│   │   │   ├── AuthContext.jsx        # Supabase auth state
│   │   │   └── NotificationContext.jsx # Toast notifications
│   │   ├── services/
│   │   │   ├── api.js                 # Backend API client
│   │   │   └── supabase.js            # Supabase client config
│   │   ├── App.jsx                    # Root app with routing
│   │   └── index.css                  # Design system + themes
│   └── package.json
│
├── 📂 data-ocr-module/                 # Python Backend (FastAPI)
│   ├── server.py                      # FastAPI server (all endpoints)
│   ├── requirements.txt               # Python dependencies
│   ├── src/
│   │   ├── agents/                    # 🤖 7-Agent Pipeline
│   │   │   ├── pipeline.py            # AgentPipeline orchestrator
│   │   │   ├── ocr_agent.py           # Agent 1: OCR extraction
│   │   │   ├── cleaner_agent.py       # Agent 2: Text cleaning
│   │   │   ├── ner_agent.py           # Agent 3: Entity recognition
│   │   │   ├── clause_agent.py        # Agent 4: Clause detection
│   │   │   ├── risk_agent.py          # Agent 5: Risk analysis
│   │   │   ├── summary_agent.py       # Agent 6: AI summarization
│   │   │   └── compile_agent.py       # Agent 7: Report compilation
│   │   ├── services/                  # Backend Services
│   │   │   ├── database.py            # MongoDB CRUD operations
│   │   │   ├── supabase_client.py     # Supabase auth verification
│   │   │   ├── vector_search.py       # Semantic vector search
│   │   │   └── pdf_report.py          # PDF report generation
│   │   ├── ocr/                       # OCR Engine
│   │   │   ├── document_loader.py     # File type detection
│   │   │   ├── pdf_parser.py          # PDF text extraction
│   │   │   ├── docx_parser.py         # DOCX text extraction
│   │   │   ├── scan_detector.py       # Scanned vs digital detection
│   │   │   ├── ocr_engine.py          # Tesseract OCR engine
│   │   │   └── image_preprocessor.py  # Image preprocessing
│   │   ├── nlp/                       # NLP Engine
│   │   │   ├── nlp_engine.py          # Clause classifier (TF-IDF)
│   │   │   └── risk_engine.py         # Multi-dimensional risk scorer
│   │   ├── preprocessing/
│   │   │   ├── clean_text.py          # Text normalization
│   │   │   └── json_formatter.py      # JSON output formatter
│   │   └── utils/
│   │       ├── config.py              # Centralized configuration
│   │       └── logger.py              # Structured logging
│   └── tests/                         # Test suite
│
├── 📂 infra/                           # DevOps & Infrastructure
│   ├── docker/
│   │   ├── backend.Dockerfile         # Backend container
│   │   └── nginx.conf                 # Reverse proxy config
│   ├── github_actions/                # CI/CD workflows
│   └── terraform/                     # Cloud infrastructure
│
├── docker-compose.yml                 # Full-stack orchestration
├── .env                               # Environment variables
├── supabase_schema.sql                # Auth schema
└── README.md                          # This file
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| Node.js | ≥ 20 | Frontend runtime |
| Tesseract OCR | Latest | Text extraction |
| MongoDB Atlas | Free tier | Data persistence |
| Git | Latest | Version control |

### 1️⃣ Clone & Configure

```bash
git clone https://github.com/druvacherka/ai-contract-intelligence.git
cd ai-contract-intelligence
```

Create a `.env` file in the project root:

```env
# MongoDB
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=contract_intelligence

# Supabase (Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# AI Providers
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### 2️⃣ Start Backend

```bash
cd data-ocr-module
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python server.py
```

> Backend API available at **http://localhost:8000**

### 3️⃣ Start Frontend

```bash
cd frontend
npm install
npm run dev
```

> Frontend available at **http://localhost:5173**

### 4️⃣ Docker (Optional)

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check with module status |
| `GET` | `/api/pipeline/status` | Pipeline component availability |
| `POST` | `/upload-contract` | **Full 7-agent pipeline**: Upload → OCR → NLP → Risk → AI → Report |
| `POST` | `/analyze-text` | Analyze raw contract text (NLP + Risk + AI) |

### Authenticated Endpoints (JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/contracts` | List all user contracts from MongoDB |
| `GET` | `/api/contracts/{id}` | Get specific contract analysis |
| `DELETE` | `/api/contracts/{id}` | Delete a contract |
| `POST` | `/api/search` | Semantic vector search across contracts |
| `GET` | `/api/report/{id}/pdf` | Download PDF intelligence report |

### Sample Response

```json
{
  "contract_id": "a1b2c3d4-...",
  "clause": "Termination",
  "confidence": 94.2,
  "risk_score": 78,
  "risk_level": "High",
  "ai_summary": "This contract contains high-risk termination clauses...",
  "key_findings": ["Unilateral termination rights", "30-day notice period"],
  "recommendations": ["Add mutual termination clause", "Extend notice to 90 days"],
  "entities": {
    "organizations": ["Acme Corp", "Widget Inc"],
    "dates": ["2025-01-01", "2025-12-31"],
    "monetary_values": ["$500,000"]
  },
  "clauses": [
    { "type": "Termination", "confidence": 94.2, "risk_score": 78 },
    { "type": "Confidentiality", "confidence": 88.1, "risk_score": 35 }
  ]
}
```

---

## ⚠️ Risk Scoring System

Contracts are evaluated across **5 risk dimensions** producing a composite score (0–100):

| Dimension | Weight | What It Detects |
|-----------|--------|-----------------|
| 🔴 **Unfavorable Obligations** | 25% | "sole discretion", "without notice", "irrevocable" |
| 🔴 **Liability Exposure** | 30% | "unlimited liability", "no cap on damages" |
| 🟡 **Vague Language** | 15% | "reasonable efforts", "as deemed appropriate" |
| 🟠 **Missing Protections** | 20% | No indemnification cap, no termination clause |
| 🟡 **Renewal Risks** | 10% | "auto-renewal", "evergreen", no opt-out |

### Risk Levels

```
🟢 Low Risk    :  0 — 30   →  Standard contract, minimal concerns
🟡 Medium Risk : 31 — 70   →  Review recommended, some flagged clauses  
🔴 High Risk   : 71 — 100  →  Immediate legal review required
```

---

## 🔍 OCR Engine Features

- **Dual-engine extraction** — PyMuPDF for native PDFs + Tesseract for scanned documents
- **Self-healing OCR** — Automatically retries with handwriting preset if confidence < 65%
- **Adaptive preprocessing** — Otsu + local thresholding for degraded scans
- **Preset system** — `default`, `clean`, `noisy`, `handwriting` configurations
- **Multi-format support** — PDF, DOCX, DOC, TXT, PNG, JPG, TIFF, BMP
- **Scan detection** — Automatically identifies scanned vs. digital-native documents

---

## 🔐 Authentication

IntelliAnalyze AI uses **Supabase** for authentication:

- **Email/Password** — Traditional signup and login
- **Google OAuth 2.0** — One-click Google sign-in
- **JWT Verification** — Backend verifies Supabase JWTs for API protection
- **Protected Routes** — Frontend guards dashboard routes with auth context

---

## 🧪 Testing

```bash
cd data-ocr-module

# Unit tests (pytest)
python -m pytest src/tests/ --ignore=src/tests/test_dataset.py -v

# End-to-end API tests
python e2e_test.py

# Browser flow simulation
python browser_flow_test.py
```

---

## 🌿 Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready releases |
| `develop` | Integration & staging |
| `feature/ocr` | OCR engine development |
| `feature/nlp` | NLP/ML model development |
| `feature/backend` | Backend API & services |
| `feature/frontend` | Frontend UI & UX |
| `feature/devops` | Infrastructure & CI/CD |

---

## 👥 Team

<table>
<tr>
<td align="center"><b>Saniya</b><br/><sub>Frontend + DevOps</sub></td>
<td align="center"><b>Prajwal</b><br/><sub>OCR + Data Processing</sub></td>
<td align="center"><b>Dhruva</b><br/><sub>NLP / ML Engineering</sub></td>
<td align="center"><b>Vishwas Chandra</b><br/><sub>Backend / API</sub></td>
</tr>
</table>

---

<div align="center">

### 🌟 Star this repo if you find it useful!

**Built with ❤️ by the IntelliAnalyze AI Team**

*Transforming legal document review from hours to seconds.*

</div>
