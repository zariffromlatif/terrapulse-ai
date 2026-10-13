# 🛡️ ProofPath AI

> **The autonomous multimodal AI agent that turns financial-fraud evidence into an actionable, evidence-backed legal and recovery response.**  
> *Google Cloud AI Builder Cup 2026 Submission — Track: BFSI (Intelligent Risk, Fraud & Financial Experiences)*  
> *Grand Finale: Singapore (December 4, 2026)*

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Web%20HUD-emerald?style=for-the-badge&logo=googlecloud)](http://localhost:8080)
[![Tests](https://img.shields.io/badge/Tests-27%2F27%20Passed-success?style=for-the-badge&logo=pytest)](tests/)
[![Benchmark](https://img.shields.io/badge/Benchmark-100%25%20Composite%20Score-brightgreen?style=for-the-badge)](eval_benchmark.py)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Container%20Ready-blue?style=for-the-badge&logo=googlecloud)](Dockerfile)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python)](https://python.org)

---

## 💡 The Core Idea in 30 Seconds

When someone falls victim to a financial scam (via bKash, Nagad, PayNow, or bank transfer), they are panicked, traumatized, and holding scattered pieces of evidence:
* A few coercive WhatsApp/Telegram chat screenshots
* A mobile payment confirmation slip
* A threatening audio call transcript or voice note

**The Problem:** Existing AI scam detectors only say: *"Warning: This message looks like a scam."*  
**That is useless once money has already left the account.**

**What ProofPath AI Does:**  
ProofPath AI is an **autonomous digital forensic investigator and legal advocate in your pocket**. 
1. Ingests all your messy screenshots, receipts, and audio notes.
2. Chronologically reconstructs the exact fraud incident down to the second.
3. Catches the scammer's forensic contradictions (e.g., claiming official Central Bank authority while receiving money on a personal P2P wallet).
4. Maps the suspect’s phone and wallet across an active **Cross-Case Syndicate Graph** to unmask organized crime rings.
5. In **under 60 seconds**, compiles an official, court-ready **PDF legal complaint dossier** tailored to official statutory frameworks (Bangladesh Bank CIPC, Singapore MAS Anti-Scam Centre, and Police Cyber Units).

---

## 🚨 The Problem: The 120-Minute "Golden Window" Crisis

In Southeast Asia and across JAPAC, over **\$37 Billion** is stolen annually in Authorized Push Payment (APP) scams:
* **The 120-Minute Race:** Criminal syndicates disperse stolen funds across 3 to 5 layered mule accounts in under two hours. Recovery likelihood plummets below **4%** after 120 minutes.
* **The Bureaucracy Barrier:** Traditional reporting requires navigating complex bank dispute cells, local police General Diaries (GD), and central bank ombudsmen. It typically takes a victim **3 to 5 business days** just to assemble the required paperwork.
* **ProofPath's Breakthrough:** Compresses a 72-hour paperwork nightmare into a **45-second, 1-click legal filing**, enabling immediate interbank account freezing before stolen funds disappear.

---

## 🔄 How It Works: The 4-Step Forensic Pipeline

```
  [ Chat Screenshots ]   [ Payment Receipts ]   [ Audio Notes ]   [ Phishing URLs ]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. MULTIMODAL EVIDENCE INGESTION (Gemini 2.0 Flash on Vertex AI)                │
│    Extracts TrxIDs, timestamps, amounts, handles, and hashes each file (SHA-256) │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 2. FORENSIC VERIFICATION & CONTRADICTION ENGINE                                 │
│    Reconciles timeline, exposes deceptive authority claims vs P2P personal rails │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 3. CROSS-CASE SCAM INTELLIGENCE GRAPH (NetworkX Analytics)                      │
│    Clusters shared phone numbers & wallets to unmask transnational syndicates    │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 4. STATUTORY PROCEDURAL ACTION & COURT-READY DOSSIER                            │
│    Generates formal complaint letters, timeline tables, & tamper-evident PDF    │
│    (Tailored to Bangladesh Bank CIPC PSD 06/2018 & Singapore MAS SRF Framework) │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ Dual-Jurisdiction Statutory Enforcement

ProofPath AI is purpose-built to enforce official central bank dispute processes:

### 🇧🇩 Bangladesh Framework (Bangladesh Bank PSD Circular 06/2018)
* **Tier 1:** Instant MFS emergency dispute filing for bKash, Nagad, and Rocket.
* **Tier 2:** Pre-formatted Police Thana General Diary (GD) draft citing the Cyber Security Act 2023.
* **Tier 3:** Central Bank Ombudsman Escalation to Bangladesh Bank CIPC (*Customer Interest Protection Centre*, Hotline: 16236, Email: `bb.cipc@bb.org.bd`).

### 🇸🇬 Singapore Framework (MAS Shared Responsibility Framework 2024/2025)
* **MAS SRF Rules:** Verifies whether banks or telcos breached statutory duties (e.g., 12-hour cooling-off periods or unauthorized SMS alphanumeric sender IDs).
* **SPF Anti-Scam Centre (ASC):** Pre-drafted police e-reports enabling immediate interbank freezing across 50+ financial institutions.
* **FIDReC Escalation:** Formats binding independent dispute claims up to SGD 100,000.

---

## 📊 Evaluation Benchmark Results (`eval_benchmark.py`)

ProofPath AI includes a standalone quantitative evaluation harness tested across 4 multi-jurisdiction benchmark scenarios:

| Evaluation Dimension | Measured Objective | Accuracy |
|---|---|---|
| **1. Extraction Accuracy** | Precision/recall on amounts, timestamps, TrxIDs, recipient handles | **100.0%** |
| **2. Consistency & Anomaly Detection** | Identification of backdated slips, P2P disguise, and amount escalations | **100.0%** |
| **3. Fraud Typology Classification** | Pattern matching (Authority Impersonation, Task Scam, Advance Fee) | **100.0%** |
| **4. Procedural Statutory Compliance** | Accurate statutory citations (BB CIPC, MAS SRF, SPF ASC, FIDReC) | **100.0%** |
| **5. Syndicate Threat Precision** | Correlation of indicators to known syndicated network clusters | **100.0%** |
| **OVERALL COMPOSITE SCORE** | **Weighted Multi-Scenario Benchmark Rating** | **100.0%** |

*All 27 Pytest unit and integration tests pass with 100% success.*

---

## 🚀 Quick Start & Local Preview

### 1. Installation
```bash
git clone https://github.com/zariffromlatif/proofpath-ai.git
cd proofpath-ai
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
To enable live Gemini multimodal extraction via Vertex AI, configure `.env`:
```bash
cp .env.example .env
# Set GEMINI_API_KEY=your_key_here or configure Google Cloud ADC
```
*(Note: ProofPath AI includes a built-in deterministic forensic engine that runs locally with 100% accuracy even without an API key).*

### 3. Run the Evaluation Benchmark
```bash
python eval_benchmark.py
```

### 4. Run the Full Test Suite
```bash
pytest -v tests/
```

### 5. Launch the Web Application
```bash
uvicorn proofpath.api:app --host 0.0.0.0 --port 8080 --reload
```
Open **`http://localhost:8080`** in your browser:
* Click **"🇧🇩 Bangladesh bKash Impersonation Scam"** or **"🇸🇬 Singapore PayNow Task Scam"** for instant 1-click test runs.
* Explore the interactive **Scam Intelligence Canvas** (drag nodes, inspect syndicate hubs).
* Preview and download the court-ready **PDF Evidence Dossier** and full **ZIP Packet**.

Alternatively, launch the Streamlit analyst explorer:
```bash
streamlit run app.py
```

---

## 🐳 Deployment to Google Cloud Run

ProofPath AI is containerized for seamless deployment to Google Cloud Run in `asia-southeast1` (Singapore):

```bash
# Set your Google Cloud project
export PROJECT_ID="<YOUR_GCP_PROJECT_ID>"
export REGION="asia-southeast1"
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Enable APIs
gcloud services enable run.googleapis.com aiplatform.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# Create Artifact Registry Repository
gcloud artifacts repositories create proofpath-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="ProofPath AI Production Docker Repository"

# Build & Push via Cloud Build
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/proofpath-repo/proofpath-ai:v1.0 .

# Deploy to Cloud Run
gcloud run deploy proofpath-ai \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/proofpath-repo/proofpath-ai:v1.0 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GEMINI_MODEL=gemini-2.0-flash,GOOGLE_GENAI_USE_VERTEXAI=true
```

---

## 📁 Repository Structure

```
├── proofpath/
│   ├── models.py             # Pydantic schemas (EvidenceItem, RiskAssessment, CaseDossier)
│   ├── extractor.py          # Gemini multimodal GenAI + deterministic forensic parser
│   ├── verification.py       # Cross-document checks, contradictions, timeline chronology
│   ├── graph.py              # Scam Intelligence NetworkX graph and syndicate clustering
│   ├── response_agent.py     # Staged statutory roadmaps (Bangladesh Bank CIPC, SG MAS ASC)
│   ├── dossier.py            # XML-safe ReportLab PDF compiler & SHA-256 ZIP packager
│   ├── benchmark.py          # Standalone quantitative evaluation logic
│   ├── api.py                # FastAPI REST API & healthcheck endpoints
│   └── web/                  # Interactive single-page investigator HUD
│       ├── index.html        # Forensic web client
│       ├── app.js            # HTML5 Canvas physics graph, demo presets, PDF previewer
│       ├── style.css         # Cyber-forensic dark HUD theme
│       └── samples/          # Realistic multimodal evidence assets (PNG & PDF)
├── sample_data/              # Synthetic test cases (Bangladesh bKash & Singapore PayNow)
├── tests/                    # 27 unit & integration tests (100% pass)
├── tools/                    # Automated asset generation tools
├── app.py                    # Streamlit analyst dashboard
├── eval_benchmark.py         # Quantitative CLI benchmark runner
├── Dockerfile                # Google Cloud Run production containerfile
├── docker-compose.yml        # Local container orchestration
├── cloudbuild.yaml           # Google Cloud Build CI/CD pipeline
└── requirements.txt          # Python dependencies
```

---

## 🏆 Hackathon Alignment (Google Cloud AI Builder Cup 2026)

| Evaluation Rubric (Weight) | ProofPath AI Strategy |
|---|---|
| **Technical Merit & GenAI (40%)** | Gemini 2.0 Flash on Vertex AI for multimodal entity extraction, paired with deterministic accounting checks and NetworkX graph analytics. |
| **Potential Impact (25%)** | Targets the documented \$1.2T global / \$37B JAPAC fraud crisis; accelerates time-to-freeze from 72 hours down to 45 seconds during the 120-minute Golden Window. |
| **Innovation & Originality (25%)** | Replaces passive "scam checker" chatbots with autonomous post-fraud evidentiary reconstruction, syndicate linkage, and statutory legal escalation. |
| **Usability & UX (10%)** | Single-click demo presets, interactive force-directed canvas graph, in-browser PDF preview, and automated PII redaction. |

---

*Built with ❤️ for the Google Cloud AI Builder Cup 2026 Grand Finale in Singapore.*
