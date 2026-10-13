# 🛡️ ProofPath AI

> **The AI agent that turns financial-fraud evidence into an actionable, evidence-backed response.**  
> *Google Cloud AI Builder Cup 2026 Submission*

[![Tests](https://img.shields.io/badge/Tests-27%20Passed-success)](#verification--testing)
[![Benchmark](https://img.shields.io/badge/Benchmark-100%25%20Composite%20Score-brightgreen)](#eval-benchmark)
[![Deployment](https://img.shields.io/badge/Google%20Cloud%20Run-Container%20Ready-blue)](#deployment)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://python.org)

---

## 📌 Executive Overview

When victims suffer financial cyber-fraud, they are left with fragmented artifacts: coercive WhatsApp/Telegram chats, payment receipts, voice call recordings, and phishing links. To stand any chance of recovering their funds, victims must act within the **Golden Window (0–2 hours)**, but are overwhelmed by complex statutory procedures across banks, telecom regulators, police stations, and central bank ombudsmen.

**ProofPath AI** solves this crisis by acting as an end-to-end autonomous forensic response agent:
1. **Ingests multimodal evidence** (screenshots, receipts, chat logs, audio notes).
2. **Reconstructs what happened** chronologically with cryptographic SHA-256 evidence indexing.
3. **Validates consistency & flags contradictions** (e.g., authority impersonation vs. personal P2P wallet, backdated receipts, escalated amounts).
4. **Correlates threats across a global scam intelligence graph** using NetworkX to map syndicate hubs, recurring phones, and scam domains.
5. **Generates jurisdiction-specific statutory response roadmaps** tailored to **Bangladesh** (Bangladesh Bank CIPC, MFS dispute cells, CID Cyber Police) and **Singapore** (MAS Shared Responsibility Framework, SPF Anti-Scam Centre, ScamShield).
6. **Assembles court-ready and bank-ready evidence packets**: official PDF dossiers, PII-redacted timeline reports, and pre-filled formal complaint applications.

---

## 🏛️ Architecture & Technical Layers

```
                          MULTIMODAL EVIDENCE INGESTION
          [Payment Receipts]  [Chat Logs]  [Audio Transcripts]  [Phishing URLs]
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │       Layer 1: Multimodal Reconstruction Engine         │
             │     Google GenAI SDK (Gemini) + Deterministic Fallback  │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │         Layer 2: Verification & Risk Engine             │
             │   Cross-Document Checks • Chronology • Contradictions   │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │      Layer 3: Cross-Case Scam Intelligence Graph        │
             │     NetworkX Knowledge Graph • Syndicate Clustering     │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │         Layer 4: Procedural Response Agent              │
             │   Bangladesh Bank CIPC / CID • Singapore MAS / SPF ASC  │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │         Layer 5: Actionable Case Dossier Package        │
             │    Official PDF (ReportLab) • Evidence ZIP • SHA-256    │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
     Interactive Web Application & REST API       Streamlit Dashboard
                 (FastAPI)                             (app.py)
```

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
To enable live Gemini multimodal extraction, set your API key in `.env`:
```bash
cp .env.example .env
# Set GEMINI_API_KEY=your_key_here
```
*(Note: ProofPath AI includes a robust deterministic forensic fallback engine that runs locally with 100% accuracy even without an API key).*

### 3. Run the Fraud-Response Benchmark
Execute the automated quantitative evaluation benchmark:
```bash
python eval_benchmark.py
```

### 4. Run the Full Test Suite
```bash
pytest -v tests/
```

### 5. Launch the Web Application
Start the high-performance FastAPI server with the interactive UI:
```bash
uvicorn proofpath.api:app --host 0.0.0.0 --port 8080 --reload
```
Open **`http://localhost:8080`** in your browser.

Alternatively, launch the Streamlit analyst dashboard:
```bash
streamlit run app.py
```

---

## 📊 Benchmark Results (`eval_benchmark.py`)

ProofPath AI features a standalone evaluation benchmark measuring 5 key quantitative performance metrics:

| Dimension | Measured Objective | Score |
|---|---|---|
| **Extraction Accuracy** | Precision/recall on amounts, currencies, transaction IDs, suspect indicators | **100.0%** |
| **Consistency & Anomalies** | Identification of backdated receipts, P2P disguise, and amount discrepancies | **100.0%** |
| **Scam Pattern Detection** | Typology classification (Impersonation, Task Scam, Advance-Fee) | **100.0%** |
| **Procedural Compliance** | Statutory authority citations (Bangladesh Bank CIPC, SPF ASC, FIDReC) | **100.0%** |
| **Syndicate Precision** | Correlation of threat indicators to known syndicated network clusters | **100.0%** |
| **OVERALL COMPOSITE** | **Weighted Multi-Scenario Benchmark Score** | **100.0%** |

---

## 🌐 API Endpoints

- `POST /api/cases/analyze`: Ingests multipart files or text evidence and generates the complete case dossier.
- `GET /api/cases/{case_id}`: Retrieves structured JSON case dossier.
- `GET /api/cases/{case_id}/pdf`: Downloads court-ready formatted PDF evidence dossier.
- `GET /api/cases/{case_id}/zip`: Downloads full evidence archive with PDF, markdown, JSON, and letters.
- `GET /api/intelligence/graph`: Returns NetworkX graph nodes and edges for visualizer.
- `GET /api/benchmark/run`: Executes the benchmark suite on demand.
- `GET /api/health`: Healthcheck endpoint for Google Cloud Run container liveness.

---

## 🐳 Deployment to Google Cloud Run

The application is containerized with a production-grade multi-stage Dockerfile adhering to Cloud Run standards:

```bash
# Build Docker image
docker build -t gcr.io/$PROJECT_ID/proofpath-ai .

# Run locally with Docker Compose
docker-compose up

# Deploy to Google Cloud Run
gcloud run deploy proofpath-ai \
  --image gcr.io/$PROJECT_ID/proofpath-ai \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

---

## 📁 Repository Structure

```
├── proofpath/
│   ├── __init__.py           # Package init
│   ├── models.py             # Pydantic schemas (EvidenceItem, RiskAssessment, CaseDossier)
│   ├── extractor.py          # Multimodal GenAI extraction + deterministic fallback parser
│   ├── verification.py       # Cross-document checks, contradictions, timeline chronology
│   ├── graph.py              # Scam Intelligence NetworkX graph and syndicate clustering
│   ├── response_agent.py     # Staged statutory roadmaps (Bangladesh Bank CIPC, SG MAS ASC)
│   ├── dossier.py            # PDF generation (ReportLab), ZIP packaging, PII redaction
│   ├── benchmark.py          # Benchmark evaluation logic
│   ├── service.py            # Central investigation service
│   ├── api.py                # FastAPI REST API
│   └── web/                  # Interactive Web UI
│       ├── index.html        # Modern forensic investigator dashboard
│       ├── app.js            # Frontend logic, dynamic graph renderer, demo loaders
│       └── style.css         # Responsive styling
├── sample_data/              # Realistic synthetic test cases (BD bKash & SG PayNow)
├── tests/                    # 27 unit and integration tests (100% pass)
├── app.py                    # Streamlit dashboard
├── eval_benchmark.py         # Quantitative CLI benchmark runner
├── Dockerfile                # Google Cloud Run containerfile
├── docker-compose.yml        # Docker compose config
├── cloudbuild.yaml           # Google Cloud Build pipeline
└── requirements.txt          # Python dependencies
```
