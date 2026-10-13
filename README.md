# 🌍 TerraPulse (CampTwin AI)
### Autonomous Multimodal Digital Twin & Compound Disaster Cascade Interceptor for Informal Settlements

> **Google Cloud AI Builder Cup 2026** — *Track: Sustainability & Social Impact*  
> **Grand Finale**: Singapore, December 4, 2026  
> **Primary Anchor**: Cox's Bazar, Bangladesh (*Kutupalong-Balukhali*, ~1M residents — world's largest refugee camp, Camp 4 Block G)  
> **Regional Scalability**: JAPAC climate-vulnerable informal settlements (Jakarta floodplains, Manila informal communities, Chittagong hill settlements).

---

## 📌 Executive Summary & Problem Statement

In informal settlements and refugee camps across the Asia-Pacific region, monsoon climate shocks trigger **non-linear, multi-stage compound disaster cascades**. Traditional early warning systems treat hazards in isolation — alerting on rainfall alone or waiting for landslides to be reported by radio. By then, the catastrophic chain reaction is already underway:

$$\text{Blocked Culvert} \xrightarrow{+15\text{m}} \text{Soil Surcharge} \xrightarrow{+45\text{m}} \text{Bamboo Wall Collapse} \xrightarrow{+1.5\text{h}} \text{Latrine Pit Breach} \xrightarrow{+2.5\text{h}} \text{Tubewell Contamination} \xrightarrow{+24\text{h}} \text{Cholera Outbreak}$$

**TerraPulse (CampTwin AI)** is an autonomous, multimodal digital twin and compound disaster interception platform. Anchored in Cox's Bazar Camp 4 (Block G), TerraPulse fuses **orbital remote sensing (NASA GPM IMERG 30-min precipitation, Sentinel-1 SAR soil saturation, Copernicus DEM)** with **ground-level multimodal inspections (volunteer phone photos, drone frames, Rohingya/Bengali voice notes analyzed via Gemini 2.0 Flash)**. 

When micro-defects align with extreme hydro-meteorological loads, TerraPulse models the cascading failure chain in real time and deploys an autonomous **Vertex AI Agent Swarm** to dispatch targeted interventions **before** the cascade becomes fatal.

---

## 🏛️ System Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │              ORBITAL & METEOROLOGICAL TELEMETRY        │
                  │  • NASA GPM IMERG 30-min Rain Rates (mm/hr)            │
                  │  • Sentinel-1 C-band SAR Soil Moisture Saturation      │
                  │  • Copernicus DEM 30m Topographic Slopes & Gradients   │
                  └───────────────────────────┬────────────────────────────┘
                                              │
 ┌────────────────────────────────────────┐   │
 │     MULTIMODAL GROUND INSPECTIONS      │   │
 │ • Volunteer Smartphone Photos / Video  │   │
 │ • Community Voice Transcripts (Audio)  │   │
 │ • Gemini 2.0 Flash Vision Engine       │   │
 │   - Bamboo Wall Deflection Angle (°)   │   │
 │   - Culvert Siltation % & Choke Size   │   │
 │   - Cracked Well Aprons & Bounding Box │   │
 └───────────────────┬────────────────────┘   │
                     │                        │
                     ▼                        ▼
        ┌────────────────────────────────────────────────────────┐
        │       CAMP DIGITAL TWIN & TOPOGRAPHIC HYDRO-GRAPH      │
        │   • Authentic HDX / OpenStreetMap Settlement Graph     │
        │   • Gravity-Driven Downhill Hydrological Routing       │
        │   • Topographic Wetness Index: TWI = ln(A / tan β)     │
        │   • UN Sphere WASH Standard Proximity Audit (<30m)     │
        └───────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │      COMPOUND DISASTER CASCADE REASONING ENGINE        │
        │   • Multi-Stage Domino Failure Propagation Simulator   │
        │   • Physics-Informed Time-to-Failure Countdown Timers  │
        │   • Interception Window & Population-at-Risk Forecast  │
        │   • Vibrio cholerae / Waterborne Epidemic Escalation   │
        └───────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │          VERTEX AI AUTONOMOUS AGENT SWARM              │
        │ ┌──────────────────────┐  ┌──────────────────────────┐ │
        │ │ Tactical Dispatch    │  │ WASH Protection          │ │
        │ │ • Priority CPP Tasks │  │ • Tubewell TW-04 Lock    │ │
        │ │ • GPS Shovel/Sandbag │  │ • AquaTabs (15L/pers/day)│ │
        │ └──────────────────────┘  └──────────────────────────┘ │
        │ ┌────────────────────────────────────────────────────┐ │
        │ │ Micro-Evacuation Pathfinding                       │ │
        │ │ • Turn-by-turn Escape Corridor avoiding Haz-Zones  │ │
        │ │ • Multilingual Audio Guidance (Rohingya/Bengali)   │ │
        │ └────────────────────────────────────────────────────┘ │
        └───────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │   INTERACTIVE COMMAND HUD & FASTAPI OPERATIONS CENTER  │
        │   • Live Leaflet Camp Map with Hazard Pulses & Routes  │
        │   • Real-Time Telemetry Ticker & Bounding Box Overlays │
        │   • 1-Click Autonomous Interception Execution          │
        └────────────────────────────────────────────────────────┘
```

---

## ⚡ Core Deliverables & Capabilities

### 1. Settlement Digital Twin & Topographic Hydro-Graph (`terrapulse/digital_twin.py`)
- **Authentic Settlement Anchoring**: Built on OpenStreetMap and Humanitarian Data Exchange (HDX) footprints for **Cox's Bazar Camp 4 (Block G)**, covering 27+ core infrastructure assets:
  - Culverts & Drainage (`CULVERT_C14`, `CULVERT_C08`, `CULVERT_C22`)
  - Bamboo Retaining Walls (`WALL_BW07`, `WALL_BW03`, `WALL_BW12`)
  - Latrine Sanitation Pits (`LATRINE_LP101`, `LATRINE_LP102`, `LATRINE_LP108`)
  - Deep Tubewells & Distribution (`TUBEWELL_TW04`, `TUBEWELL_TW09`, `TAPSTAND_TS12`)
  - Refugee Shelters (`SHELTER_S401` through `SHELTER_S420`)
  - Designated Safe Zones (`SAFEZONE_SZ01` CiC Complex, `SAFEZONE_SZ02` Learning Center)
- **Topographic Wetness Index (TWI)**:
  $$\text{TWI}_i = \ln\left(\frac{A_i}{\tan \beta_i}\right)$$
  Where $A_i$ represents the upstream contributing catchment accumulation and $\beta_i$ is local slope gradient in radians.
- **Gravity-Driven Hydro-Routing**: Derives directed flow vectors down elevation contours ($\Delta z > 0.5\text{m}$) to trace surface runoff accumulation paths.
- **UN Sphere WASH Audit**: Automatically flags any latrine pit within 30m horizontal separation of a drinking tubewell or positioned uphill in a surface runoff flowpath.

### 2. Multimodal Inspection Engine (`terrapulse/inspection.py`)
- **Multimodal Inputs**: Accepts volunteer smartphone photographs, drone video frames, and community audio notes translated from Rohingya, Bengali, and English.
- **Gemini 2.0 Flash Integration**: Formulates structured geotechnical prompts returning:
  - Bamboo Retaining Wall Deflection Angle (`deflection_angle_deg`, e.g., 18.5° tilt vs 15.0° critical shear threshold).
  - Culvert Siltation & Obstruction (`siltation_pct`, e.g., 75% throttle reducing hydraulic capacity from 3.8 m³/s to 0.9 m³/s).
  - Sanitary Apron Cracking (`crack_width_cm`, e.g., 4.2cm fissure allowing borehole casing infiltration).
  - Normalized Bounding Boxes (`[ymin, xmin, ymax, xmax]`, 0–1000 scale) for visual localization.
- **Deterministic Edge Fallback**: If offline or air-gapped without an API key, executes a calibrated physics and keyword heuristic engine that guarantees 100% operational uptime at field basecamps.

### 3. Compound Disaster Cascade Reasoning Engine (`terrapulse/cascade_engine.py`)
- **Orbital Fusion**: Synthesizes NASA GPM IMERG rain rate ($R = 65\text{ mm/hr}$), Sentinel-1 SAR soil moisture saturation ($S = 88\%$), and Copernicus DEM terrain slope ($22.5^\circ$).
- **5-Stage Domino Cascade Simulation**:
  1. *Stage 1 (T+15m)*: **Culvert Hydraulic Choking** — Silted Culvert C-14 causes channel overtopping into footpaths.
  2. *Stage 2 (T+45m)*: **Soil Surcharge & Pore-Pressure Spike** — Water infiltrates sandy terrace slope behind Wall BW-07, eliminating shear strength.
  3. *Stage 3 (T+1h10m)*: **Bamboo Wall Shear Collapse & Mudslide** — 450 m³ liquefied soil slides down 22° slope towards Shelters S-408 through S-415.
  4. *Stage 4 (T+1h55m)*: **Latrine Pit Scour & Bio-WASH Breach** — 2,850L fecal sludge washes downhill toward Tubewell TW-04.
  5. *Stage 5 (T+24h)*: **Aquifer Contamination & Cholera Outbreak** — Cracked apron allows pathogen infiltration, putting 1,450 residents at risk of acute watery diarrhea.
- **Interception Window**: Identifies the critical countdown time (e.g. 25 minutes) to clear the culvert before irreversible slope saturation begins.

### 4. Vertex AI Autonomous Agent Swarm (`terrapulse/agents.py`)
- **Tactical Dispatch Agent**:
  - Issues prioritized volunteer tasks to Cyclone Preparedness Programme (CPP) brigades.
  - Generates specific equipment lists: 4x trenching shovels, 2x 4m bamboo hooks, 25x sandbags for Culvert C-14; 12x Borak bamboo buttresses for Wall BW-07.
  - Specifies precise target GPS coordinates and urgency countdown.
- **WASH Protection Agent**:
  - Pushes automatic valve lock command to Deep Tubewell TW-04.
  - Calculates UN Sphere Standard water purification needs: 15L clean drinking water per person/day $\implies$ 320 AquaTab blister strips (3,200 tablets of NaDCC 33mg) for 7-day household reserve.
  - Broadcasts multilingual loudspeaker boil warnings in Rohingya, Bengali, and English.
- **Micro-Evacuation Agent**:
  - Dynamically computes shortest-path turn-by-turn escape corridors avoiding all active hazard zones (mudslide cones, collapsed walls, flooded ravines).
  - Routes 50+ residents along the East Ridge Bypass Trail directly to **Camp 4 Primary Safe Haven (CiC Complex)** in 6 minutes.

### 5. Interactive Web HUD & Operations Command Center (`terrapulse/api.py`, `terrapulse/web/`)
- **FastAPI Production Backend** serving a dark-mode command dashboard.
- **Live Leaflet Map**: Renders Camp 4 Block G with real terrain coordinates, color-coded infrastructure nodes, pulsing red hazard zones, and green animated evacuation corridor paths.
- **Live Telemetry Ticker**: Real-time readings from NASA GPM, Sentinel-1 SAR, Copernicus DEM, and compound cascade probability.
- **Multimodal Camera Feed Viewport**: Displays simulated drone/phone imagery with SVG bounding box overlays and volunteer audio notes.
- **1-Click Autonomous Interception**: Triggers the entire agent swarm with single-click command dispatch.

---

## 🇺🇳 UN Sphere Humanitarian Standards Compliance

TerraPulse is architected around the internationally recognized **Sphere Handbook for Humanitarian Response**:
- **WASH Standard 1.2 (Water Source Protection)**: Enforces a minimum **30-meter horizontal buffer** between latrine pits and drinking water sources. TerraPulse automatically flags the 22.1m separation between `LATRINE_LP101` and `TUBEWELL_TW04` as a critical biohazard vector.
- **WASH Standard 2.1 (Water Quantity & Quality)**: Guarantees access to **15 liters of safe water per person per day**, automatically calculating emergency NaDCC chlorine dosing and AquaTab distribution quotas.
- **Camp Coordination & Camp Management (CCCM) Evacuation Standard**: Ensures evacuation escape paths avoid slopes greater than 18° during active landslides and bypass submerged drainage channels.

---

## 📊 Verification & Quantitative Benchmark Results

The system includes an automated quantitative verification benchmark suite (`eval_benchmark.py`) and a comprehensive pytest suite (`tests/`):

```bash
$ python eval_benchmark.py
============================================================================
  TERRAPULSE (CAMPTWIN AI) - COMPOUND DISASTER INTERCEPTOR BENCHMARK
  Google Cloud AI Builder Cup 2026 // Sustainability & Social Impact Track
  Target: Cox's Bazar Informal Settlement (Kutupalong Camp 4 Block G)
============================================================================
Initializing benchmark test scenarios across hydro-meteorological regimes...

--- BENCHMARK SCORECARD ---
Total Evaluated Scenarios     : 4
Passed Scenarios              : 4 / 4
----------------------------------------------------------------------------
1. Multimodal Defect Extraction Accuracy  : 100.0%
2. Compound Cascade Prediction Accuracy   : 100.0%
3. UN Sphere WASH 30m Audit Sensitivity   : 100.0%
4. Micro-Evacuation Route Safety Score    : 100.0%
5. Agent Swarm Dispatch Coherence Score   : 100.0%
----------------------------------------------------------------------------
OVERALL COMPOSITE BENCHMARK SCORE         : 100.0%
============================================================================
>>> BENCHMARK STATUS: ALL EVALUATION GATES PASSED (EXCELLENT)
```

### Pytest Unit Test Suite (31 Tests Passing)
```bash
$ pytest tests/ -v
tests/test_agents.py::test_tactical_dispatch_agent PASSED                [  3%]
tests/test_agents.py::test_wash_protection_agent PASSED                  [  6%]
tests/test_agents.py::test_micro_evacuation_agent PASSED                 [  9%]
tests/test_agents.py::test_agent_swarm_consensus PASSED                  [ 12%]
tests/test_api.py::test_command_hud_endpoint PASSED                      [ 16%]
tests/test_api.py::test_health_check_endpoint PASSED                     [ 19%]
tests/test_api.py::test_digital_twin_endpoints PASSED                    [ 22%]
tests/test_api.py::test_inspect_endpoint PASSED                          [ 25%]
tests/test_api.py::test_cascade_simulate_endpoint PASSED                 [ 29%]
tests/test_api.py::test_scenarios_and_benchmark_endpoints PASSED         [ 32%]
tests/test_api.py::test_inspect_upload_endpoint PASSED                   [ 35%]
tests/test_api.py::test_inspect_base64_endpoint PASSED                   [ 38%]
tests/test_api.py::test_cascade_simulate_custom_defects PASSED           [ 41%]
tests/test_cascade_engine.py::test_cascade_monsoon_simulation PASSED     [ 45%]
tests/test_cascade_engine.py::test_cascade_dry_baseline_simulation PASSED [ 48%]
tests/test_cascade_engine.py::test_cascade_with_empty_defects PASSED     [ 51%]
tests/test_cascade_engine.py::test_hydrological_rational_formula_runoff PASSED [ 54%]
tests/test_digital_twin.py::test_distance_calculation PASSED             [ 58%]
tests/test_digital_twin.py::test_digital_twin_topology PASSED            [ 61%]
tests/test_digital_twin.py::test_hydrological_gravity_flow PASSED        [ 64%]
tests/test_digital_twin.py::test_topographic_wetness_index PASSED        [ 67%]
tests/test_digital_twin.py::test_sphere_wash_violations_detection PASSED [ 70%]
tests/test_digital_twin.py::test_safe_evacuation_routing PASSED          [ 74%]
tests/test_digital_twin.py::test_geojson_export PASSED                   [ 77%]
tests/test_digital_twin.py::test_safe_evacuation_routing_when_origin_in_hazards PASSED [ 80%]
tests/test_inspection.py::test_inspection_engine_init PASSED             [ 83%]
tests/test_inspection.py::test_inspection_fallback_extraction PASSED     [ 87%]
tests/test_inspection.py::test_inspection_empty_input_defaults PASSED    [ 90%]
tests/test_inspection.py::test_inspection_routine_survey_no_critical_false_positives PASSED [ 93%]
tests/test_inspection.py::test_inspection_medium_defects_calibration PASSED [ 96%]
tests/test_inspection.py::test_inspection_base64_decoding PASSED         [100%]
======================== 31 passed in 1.48s ========================
```

---

## 🚀 Quickstart & Installation

### 1. Local Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/terrapulse.git
cd terrapulse

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your Gemini API key for live multimodal vision extraction
cp .env.example .env
# Edit .env and supply GEMINI_API_KEY if available (system has 100% offline fallback)
```

### 2. Run the Verification Tests & Benchmark
```bash
# Run unit test suite
pytest tests/ -v

# Run quantitative benchmark evaluation
python eval_benchmark.py
```

### 3. Launch the Interactive Operations Command HUD
```bash
# Start FastAPI production server with Command HUD on port 8080
python app.py
```
Open **`http://localhost:8080`** in any web browser to view the Command Center HUD.

Alternatively, launch the analytical Streamlit interface:
```bash
streamlit run app.py
```

---

## ☁️ Google Cloud Packaging & Cloud Run Deployment

TerraPulse is packaged for production on **Google Cloud Run** in the `asia-southeast1` (Singapore) region.

### 1. Local Docker Execution
```bash
# Build the container
docker build -t terrapulse-ai .

# Run locally on port 8080
docker run -p 8080:8080 terrapulse-ai
```
Or via Docker Compose:
```bash
docker-compose up --build
```

### 2. Google Cloud Build & Cloud Run Pipeline
```bash
# Submit automated build and deployment via Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

This pipeline automatically:
1. Validates all tests (`pytest tests/`) and passes benchmark gates (`python eval_benchmark.py`).
2. Builds the container image and pushes to Google Artifact Registry:
   `asia-southeast1-docker.pkg.dev/$PROJECT_ID/terrapulse-repo/terrapulse-ai:$COMMIT_SHA`
3. Deploys to Google Cloud Run in `asia-southeast1` with automatic HTTPS, non-root user security, and dynamic scaling.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive Operations Command HUD |
| `GET` | `/api/health` | Health status and Google Cloud region metadata |
| `GET` | `/api/twin/graph` | Digital twin nodes, edges, and asset details |
| `GET` | `/api/twin/geojson` | Authentic GeoJSON FeatureCollection of Camp 4 Block G |
| `GET` | `/api/twin/twi` | Computed Topographic Wetness Index (TWI) values |
| `GET` | `/api/twin/wash-risk` | UN Sphere Standard sanitation vs drinking water violations |
| `POST` | `/api/inspect` | Multimodal volunteer inspection text or base64 analysis |
| `POST` | `/api/inspect/upload` | Multipart file upload for field volunteer smartphone photos |
| `POST` | `/api/cascade/simulate`| Fuses rainfall, SAR moisture, and defects for domino simulation |
| `POST` | `/api/agents/dispatch` | Coordinates Vertex AI Tactical, WASH, and Evac agents |
| `GET` | `/api/scenarios` | Lists preconfigured demonstration scenarios |
| `POST` | `/api/scenarios/{id}/run`| Runs end-to-end digital twin pipeline for a scenario |
| `GET` | `/api/benchmark` | Runs quantitative benchmark and returns scorecard |

---

## 💡 Scalability Across JAPAC Climate-Vulnerable Communities

While demonstrated in Cox's Bazar (Kutupalong-Balukhali), TerraPulse's graph topology and orbital-ground fusion architecture are built to generalize across informal communities in the Asia-Pacific region:
- **Jakarta Kampungs (Indonesia)**: Ciliwung River flash overtopping and subsidence-driven drainage choking.
- **Metro Manila Informal Settlements (Philippines)**: Typhoon-induced mudflows and corrugated shanty slope failures.
- **Chittagong Hill Tracts (Bangladesh)**: Deforested steep sand-clay hill landslide intercepting community wells.

---

## 📜 License
Distributed under the Apache 2.0 License. Built for the Google Cloud AI Builder Cup 2026.
