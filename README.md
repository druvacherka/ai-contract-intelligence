<div align="center">

# 🔍 AI Contract Intelligence & Risk Scoring System

**Enterprise-grade NLP + OCR + Semantic Search platform for legal and compliance teams**

[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/DevOps-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
[![Tailwind](https://img.shields.io/badge/CSS-Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

</div>

---

## 📋 Project Overview

The **AI Contract Intelligence** platform is an enterprise-grade system designed to help legal and compliance teams analyze contracts at scale. The platform will combine OCR, NLP, and semantic search to extract, analyze, and score legal documents with AI precision.

This repository is the **monorepo foundation** — currently initialized with the frontend and DevOps architecture.

---

## 🏗️ Current Repository Structure

```
ai-contract-intelligence/
│
├── frontend/                # React + Vite + Tailwind CSS
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Route-level page components
│   │   ├── services/        # API service layer
│   │   ├── hooks/           # Custom React hooks
│   │   ├── styles/          # Additional stylesheets
│   │   ├── App.jsx          # Root app with routing
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── infra/                   # DevOps & Infrastructure
│   ├── docker/
│   │   ├── frontend.Dockerfile
│   │   └── nginx.conf
│   ├── github_actions/
│   └── terraform/
│
├── docker-compose.yml       # Frontend + Nginx services
├── .env.example             # Environment variable template
├── .gitignore               # Professional gitignore
└── README.md
```

---

## ⚙️ Tech Stack (Current)

| Layer          | Technology                    |
|---------------|-------------------------------|
| **Frontend**  | React 19, Vite, Tailwind CSS 4 |
| **Routing**   | React Router DOM              |
| **DevOps**    | Docker, Docker Compose, Nginx |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 20
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/druvacherka/ai-contract-intelligence.git
cd ai-contract-intelligence
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Start with Docker

```bash
docker-compose up --build
```

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
