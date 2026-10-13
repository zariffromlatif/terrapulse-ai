"""TerraPulse (CampTwin AI) - FastAPI REST API & Command Center Server.

Exposes endpoints for the settlement digital twin, multimodal inspection engine,
compound cascade simulation, autonomous agent swarm dispatch, and serves the Web HUD.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from terrapulse.benchmark import run_terrapulse_benchmark
from terrapulse.models import (
    AgentSwarmDispatchResponse,
    CascadeSimulationResult,
    InspectionDefect,
    InspectionResult,
    OrbitalTelemetry,
)
from terrapulse.service import TerraPulseService

app = FastAPI(
    title="TerraPulse (CampTwin AI) API",
    description="Autonomous Multimodal Digital Twin & Compound Disaster Cascade Interceptor for Cox's Bazar Informal Settlements.",
    version="2.6.0",
)

# Enable CORS for cross-origin frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared orchestrator service instance
service = TerraPulseService()
WEB_DIR = Path(__file__).parent / "web"


@app.get("/", response_class=HTMLResponse)
async def serve_command_hud():
    """Serves the interactive TerraPulse Mission Operations Command HUD."""
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>TerraPulse API is running. Web HUD template not found.</h1>")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health_check():
    """Health status and Google Cloud Run deployment metadata."""
    return {
        "status": "healthy",
        "service": "TerraPulse (CampTwin AI)",
        "track": "Sustainability & Social Impact",
        "target_settlement": "Cox's Bazar, Kutupalong-Balukhali (Camp 4 Block G)",
        "google_cloud_region": "asia-southeast1",
        "gemini_active": service.inspection_engine._client is not None,
        "version": "2.6.0",
    }


@app.get("/api/twin/graph")
async def get_digital_twin_graph():
    """Returns infrastructure topology graph metadata and assets."""
    assets = [a.model_dump() for a in service.digital_twin.assets.values()]
    return {
        "block": service.digital_twin.block_name,
        "node_count": len(assets),
        "edge_count": service.digital_twin.graph.number_of_edges(),
        "hydro_edge_count": service.digital_twin.hydro_graph.number_of_edges(),
        "assets": assets,
    }


@app.get("/api/twin/geojson")
async def get_digital_twin_geojson():
    """Returns authentic GeoJSON FeatureCollection of Camp 4 Block G."""
    return service.digital_twin.export_geojson()


@app.get("/api/twin/twi")
async def get_topographic_wetness_index():
    """Returns computed Topographic Wetness Index (TWI) values across the settlement."""
    return {
        "block": service.digital_twin.block_name,
        "method": "TWI = ln(A / tan(beta))",
        "twi_indices": service.digital_twin.calculate_topographic_wetness_index(),
    }


@app.get("/api/twin/wash-risk")
async def get_wash_proximity_violations():
    """Returns UN Sphere Humanitarian Standards audit between sanitation and drinking water."""
    violations = service.digital_twin.detect_sphere_wash_violations()
    return {
        "standard": "UN Sphere WASH Standard 1.2 (30m separation)",
        "total_violations": len(violations),
        "violations": [v.model_dump() for v in violations],
    }


class InspectionRequestPayload(BaseModel):
    transcript: str = ""
    asset_hint: Optional[str] = None
    image_base64: Optional[str] = None
    image_filename: Optional[str] = None


@app.post("/api/inspect")
async def inspect_media(payload: InspectionRequestPayload):
    """Processes multimodal volunteer inspection text or base64 photo/sensor telemetry."""
    res = service.inspection_engine.analyze_inspection(
        text_transcript=payload.transcript,
        image_base64=payload.image_base64,
        image_filename=payload.image_filename or "",
        asset_hint=payload.asset_hint,
    )
    return res.model_dump()


@app.post("/api/inspect/upload")
async def inspect_upload(
    file: UploadFile = File(...),
    transcript: str = Form(""),
    asset_hint: Optional[str] = Form(None),
):
    """Uploads inspection media (phone photo, video frame) from field volunteer."""
    image_bytes = await file.read()
    res = service.inspection_engine.analyze_inspection(
        text_transcript=transcript,
        image_bytes=image_bytes,
        image_filename=file.filename or "upload.jpg",
        asset_hint=asset_hint,
    )
    return res.model_dump()


class CascadeSimulatePayload(BaseModel):
    gpm_rain_rate_mm_hr: float = 65.0
    sentinel1_soil_saturation: float = 0.88
    copernicus_dem_slope_deg: float = 22.5
    scenario_id: str = "custom_monsoon_sim"
    defects: Optional[List[Dict[str, Any]]] = None


@app.post("/api/cascade/simulate")
async def simulate_cascade(payload: CascadeSimulatePayload):
    """Runs physics-informed 5-stage compound disaster cascade simulation."""
    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=payload.gpm_rain_rate_mm_hr,
        sentinel1_soil_saturation=payload.sentinel1_soil_saturation,
        copernicus_dem_slope_deg=payload.copernicus_dem_slope_deg,
    )
    if payload.defects:
        from terrapulse.models import InspectionDefect
        defects = [InspectionDefect.model_validate(d) for d in payload.defects]
    else:
        baseline_inspection = service.inspection_engine.analyze_inspection()
        defects = baseline_inspection.defects_detected

    cascade = service.cascade_engine.simulate_cascade(
        telemetry=telemetry,
        defects=defects,
        scenario_id=payload.scenario_id,
    )
    return cascade.model_dump()


@app.post("/api/agents/dispatch")
async def dispatch_agents(cascade_id: str = Query("monsoon_65mm_camp4")):
    """Coordinates Vertex AI Autonomous Agent Swarm (Tactical, WASH, Micro-Evacuation)."""
    # Run pipeline to obtain cascade result and dispatch
    result = service.run_full_pipeline(scenario_id=cascade_id)
    return result["dispatch"]


@app.get("/api/scenarios")
async def list_scenarios():
    """Lists preconfigured disaster scenarios for demonstration."""
    return service.get_preloaded_scenarios()


@app.post("/api/scenarios/{scenario_id}/run")
async def run_scenario(scenario_id: str):
    """Executes full end-to-end digital twin pipeline for a specific scenario."""
    scenarios = {s["id"]: s for s in service.get_preloaded_scenarios()}
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    sc = scenarios[scenario_id]
    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=sc["telemetry"]["gpm_rain_rate_mm_hr"],
        sentinel1_soil_saturation=sc["telemetry"]["sentinel1_soil_saturation"],
        copernicus_dem_slope_deg=sc["telemetry"]["copernicus_dem_slope_deg"],
    )

    result = service.run_full_pipeline(
        telemetry=telemetry,
        inspection_text=sc["inspection_text"],
        scenario_id=scenario_id,
    )
    return result


@app.get("/api/benchmark")
async def run_benchmark_endpoint():
    """Runs quantitative verification benchmark and returns scorecard."""
    report = run_terrapulse_benchmark(service)
    return report.model_dump()
