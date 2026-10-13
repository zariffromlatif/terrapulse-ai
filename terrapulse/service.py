"""TerraPulse (CampTwin AI) - Core Platform Orchestrator Service.

Coordinates the Settlement Digital Twin, Multimodal Inspection Engine,
Compound Disaster Cascade Reasoning Engine, and Vertex AI Autonomous Agent Swarm.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from terrapulse.agents import TerraPulseAgentSwarm
from terrapulse.cascade_engine import CompoundCascadeEngine
from terrapulse.digital_twin import CampDigitalTwin
from terrapulse.inspection import MultimodalInspectionEngine
from terrapulse.models import (
    AgentSwarmDispatchResponse,
    CascadeSimulationResult,
    InspectionDefect,
    InspectionResult,
    OrbitalTelemetry,
)


class TerraPulseService:
    """Unified service orchestrating all digital twin and disaster interception capabilities."""

    def __init__(self, api_key: Optional[str] = None):
        self.digital_twin = CampDigitalTwin(block_name="Camp 4 Block G (Kutupalong-Balukhali)")
        self.inspection_engine = MultimodalInspectionEngine(api_key=api_key)
        self.cascade_engine = CompoundCascadeEngine(digital_twin=self.digital_twin)
        self.agent_swarm = TerraPulseAgentSwarm(digital_twin=self.digital_twin)

    def get_preloaded_scenarios(self) -> List[Dict[str, Any]]:
        """Returns preconfigured benchmark & demo scenarios."""
        return [
            {
                "id": "monsoon_65mm_camp4",
                "name": "Monsoon Burst 65mm/hr in Camp 4 Block G (Compound Failure)",
                "description": "Torrential monsoon downpour over steep sand-cut slopes. Culvert C-14 choked by 75% silt, triggering retaining wall BW-07 blowout and latrine breach towards Tubewell TW-04.",
                "telemetry": {
                    "gpm_rain_rate_mm_hr": 65.0,
                    "sentinel1_soil_saturation": 0.88,
                    "copernicus_dem_slope_deg": 22.5,
                },
                "inspection_text": (
                    "Volunteer voice note (Rohingya translated): Culvert C-14 intake is 75% blocked by tree limbs and trash. "
                    "Bamboo retaining wall BW-07 is leaning heavily uphill of shelters, measured tilt is 18.5 degrees. "
                    "Deep tubewell TW-04 concrete apron has a 4.2cm fissure crack."
                ),
                "severity": "CRITICAL",
            },
            {
                "id": "cyclone_sitrang_surge",
                "name": "Cyclone Sitrang Severe Gale & Deluge (95mm/hr)",
                "description": "Extreme cyclone wind-shear and catastrophic rainfall causing widespread slope liquefaction and camp-wide drainage overflow.",
                "telemetry": {
                    "gpm_rain_rate_mm_hr": 95.0,
                    "sentinel1_soil_saturation": 0.95,
                    "copernicus_dem_slope_deg": 24.0,
                },
                "inspection_text": (
                    "CPP emergency radio: Severe flooding across Block G ravine. Multiple bamboo walls showing structural fracture. "
                    "Latrine pit LP-101 flooded and overflowing into footpaths."
                ),
                "severity": "CRITICAL",
            },
            {
                "id": "moderate_premonsoon_shower",
                "name": "Pre-Monsoon Convective Storm (35mm/hr)",
                "description": "Elevated rainfall with moderate culvert siltation (40%). Early warning allows proactive clearance without evacuation.",
                "telemetry": {
                    "gpm_rain_rate_mm_hr": 35.0,
                    "sentinel1_soil_saturation": 0.62,
                    "copernicus_dem_slope_deg": 18.0,
                },
                "inspection_text": (
                    "Field inspection report: Culvert C-14 has 40% silt buildup from road runoff. "
                    "Bamboo retaining wall BW-07 shows slight 6 degree deflection. No structural rupture."
                ),
                "severity": "MEDIUM",
            },
            {
                "id": "dry_season_baseline",
                "name": "Dry Season Baseline Survey (Clear Conditions)",
                "description": "Routine monitoring during dry winter months. Infrastructure stable, baseline Sphere audit active.",
                "telemetry": {
                    "gpm_rain_rate_mm_hr": 0.0,
                    "sentinel1_soil_saturation": 0.25,
                    "copernicus_dem_slope_deg": 20.0,
                },
                "inspection_text": "Routine check: Retaining walls intact. Drainage channels dry. Tubewell operational.",
                "severity": "LOW",
            },
        ]

    def run_full_pipeline(
        self,
        telemetry: Optional[OrbitalTelemetry] = None,
        inspection_text: str = "",
        image_bytes: Optional[bytes] = None,
        image_filename: str = "",
        scenario_id: str = "monsoon_65mm_camp4",
    ) -> Dict[str, Any]:
        """Executes the full end-to-end TerraPulse analysis pipeline."""
        # 1. Multimodal defect extraction
        inspection_result: InspectionResult = self.inspection_engine.analyze_inspection(
            text_transcript=inspection_text,
            image_bytes=image_bytes,
            image_filename=image_filename,
        )

        # 2. Telemetry resolution
        if telemetry is None:
            telemetry = OrbitalTelemetry(
                gpm_rain_rate_mm_hr=65.0,
                sentinel1_soil_saturation=0.88,
                copernicus_dem_slope_deg=22.5,
            )

        # 3. Compound cascade simulation
        cascade_result: CascadeSimulationResult = self.cascade_engine.simulate_cascade(
            telemetry=telemetry,
            defects=inspection_result.defects_detected,
            scenario_id=scenario_id,
        )

        # 4. Autonomous Agent Swarm coordination
        dispatch_response: AgentSwarmDispatchResponse = self.agent_swarm.coordinate_interception(
            cascade=cascade_result,
        )

        # 5. Topographic Wetness Index & Sphere Standards
        twi_map = self.digital_twin.calculate_topographic_wetness_index()
        sphere_violations = self.digital_twin.detect_sphere_wash_violations()
        geojson_data = self.digital_twin.export_geojson()

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scenario_id": scenario_id,
            "block_name": self.digital_twin.block_name,
            "telemetry": telemetry.model_dump(),
            "inspection": inspection_result.model_dump(),
            "cascade": cascade_result.model_dump(),
            "dispatch": dispatch_response.model_dump(),
            "twi_indices": twi_map,
            "sphere_violations": [v.model_dump() for v in sphere_violations],
            "geojson": geojson_data,
        }
