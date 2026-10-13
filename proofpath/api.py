"""FastAPI REST API and Web Application server for ProofPath AI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from proofpath.benchmark import run_fraud_response_benchmark
from proofpath.models import Jurisdiction
from proofpath.service import ProofPathService

app = FastAPI(
    title="ProofPath AI API",
    description="Turn financial-fraud evidence into an actionable, evidence-backed response package.",
    version="1.0.0",
)

# Enable CORS for local dev and Cloud Run environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ProofPathService()
WEB_DIR = Path(__file__).parent / "web"


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ProofPath AI",
        "version": "1.0.0",
        "genai_sdk_available": service.extractor._client is not None,
    }


@app.post("/api/cases/analyze")
async def analyze_case_endpoint(
    files: List[UploadFile] = File(...),
    jurisdiction: str = Form("BANGLADESH"),
    victim_name: str = Form("Confidential Victim"),
    victim_contact: str = Form("Confidential Contact"),
    case_id: Optional[str] = Form(None),
):
    """Ingest multimodal evidence files and run end-to-end reconstruction, verification, and procedural guidance."""
    if not files:
        raise HTTPException(status_code=400, detail="No evidence files uploaded")

    # Map jurisdiction
    jur = Jurisdiction.BANGLADESH
    if jurisdiction.upper() == "SINGAPORE":
        jur = Jurisdiction.SINGAPORE
    elif jurisdiction.upper() == "GENERAL":
        jur = Jurisdiction.GENERAL

    processed_files = []
    for f in files:
        content = await f.read()
        processed_files.append((f.filename, content, f.content_type))

    dossier = service.analyze_case(
        files=processed_files,
        jurisdiction=jur,
        victim_name=victim_name,
        victim_contact=victim_contact,
        case_id=case_id,
    )

    return dossier


@app.get("/api/cases/{case_id}")
def get_case_endpoint(case_id: str):
    dossier = service.get_case(case_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Case not found")
    return dossier


@app.get("/api/cases/{case_id}/pdf")
def get_case_pdf_endpoint(case_id: str):
    pdf_bytes = service.get_pdf(case_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Case or PDF not found")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=ProofPath_Dossier_{case_id}.pdf"},
    )


@app.get("/api/cases/{case_id}/zip")
def get_case_zip_endpoint(case_id: str):
    zip_bytes = service.get_zip(case_id)
    if not zip_bytes:
        raise HTTPException(status_code=404, detail="Case or ZIP not found")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=ProofPath_Package_{case_id}.zip"},
    )


@app.get("/api/intelligence/graph")
def get_intelligence_graph_endpoint():
    return service.get_graph_data()


@app.get("/api/benchmark/run")
def run_benchmark_endpoint():
    report = run_fraud_response_benchmark(service)
    return report


# Serve static web frontend
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Serve authentic demo samples for multimodal ingestion
SAMPLES_DIR = WEB_DIR / "samples"
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ProofPath AI API is running. Web UI directory not found.</h1>")
