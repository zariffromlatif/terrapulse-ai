"""TerraPulse (CampTwin AI) - Core Data Models.

Defines Pydantic schemas for settlement digital twin assets, multimodal inspection defects,
orbital hydro-telemetry, compound failure cascades, and autonomous agent swarm dispatches.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Infrastructure asset types across Cox's Bazar informal settlements."""
    SHELTER = "shelter"
    CULVERT = "culvert"
    RETAINING_WALL = "retaining_wall"
    LATRINE_PIT = "latrine_pit"
    TUBEWELL = "tubewell"
    SAFE_ZONE = "safe_zone"
    DRAINAGE_JUNCTION = "drainage_junction"
    FOOTPATH = "footpath"


class AssetStatus(str, Enum):
    """Operational health status of camp infrastructure."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPROMISED = "compromised"
    DESTROYED = "destroyed"


class DefectType(str, Enum):
    """Classes of physical structural and sanitation defects."""
    BAMBOO_WALL_DEFLECTION = "bamboo_wall_deflection"
    CULVERT_SILTATION = "culvert_siltation"
    CRACKED_DRAINAGE_APRON = "cracked_drainage_apron"
    LATRINE_PIT_OVERFLOW = "latrine_pit_overflow"
    EROSION_GULLY = "erosion_gully"
    STRUCTURAL_FRACTURE = "structural_fracture"


class DefectSeverity(str, Enum):
    """Severity classification based on disaster threshold triggers."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BoundingBox(BaseModel):
    """Normalized bounding box coordinates [ymin, xmin, ymax, xmax] (0-1000 scale)."""
    ymin: int = Field(..., ge=0, le=1000)
    xmin: int = Field(..., ge=0, le=1000)
    ymax: int = Field(..., ge=0, le=1000)
    xmax: int = Field(..., ge=0, le=1000)


class SettlementAsset(BaseModel):
    """A physical node in the settlement digital twin topology."""
    id: str
    name: str
    asset_type: AssetType
    block: str = "Camp 4 Block G"
    latitude: float
    longitude: float
    elevation_m: float
    status: AssetStatus = AssetStatus.NORMAL
    capacity: int = 0
    population_sheltered: int = 0
    condition_score: float = Field(1.0, ge=0.0, le=1.0, description="1.0 is pristine, 0.0 is total failure")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InspectionDefect(BaseModel):
    """Ground-level micro-defect detected from multimodal volunteer inputs."""
    defect_id: str
    defect_type: DefectType
    severity: DefectSeverity
    confidence: float = Field(..., ge=0.0, le=1.0)
    asset_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bounding_box: Optional[BoundingBox] = None
    deflection_angle_deg: Optional[float] = Field(None, description="Bamboo retaining wall tilt in degrees")
    siltation_pct: Optional[float] = Field(None, description="Culvert silt/debris blockage percentage 0-100")
    crack_width_cm: Optional[float] = Field(None, description="Fissure width in concrete or apron")
    volunteer_notes: str = ""
    timestamp: str = ""


class InspectionResult(BaseModel):
    """Aggregated output from Multimodal Inspection Engine."""
    inspection_id: str
    source_type: str = "multimodal_image"  # image, audio, sensor
    defects_detected: List[InspectionDefect] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    primary_hazard: str
    recommended_action: str
    processed_by: str = "Gemini 2.0 Flash + Deterministic Fusion"


class OrbitalTelemetry(BaseModel):
    """Remote sensing data fused with ground twin."""
    gpm_rain_rate_mm_hr: float = Field(..., description="NASA GPM IMERG 30-min rain rate in mm/hr")
    sentinel1_soil_saturation: float = Field(..., ge=0.0, le=1.0, description="Sentinel-1 SAR C-band moisture 0.0-1.0")
    copernicus_dem_slope_deg: float = Field(22.0, description="Local terrain slope gradient")
    timestamp: str = "2026-10-13T12:00:00Z"
    station_id: str = "CXB-CAMP4-HYDRO-01"


class CascadeStage(BaseModel):
    """Discrete progression step in compound disaster domino cascade."""
    stage_index: int
    stage_name: str
    time_offset_minutes: int
    description: str
    failure_probability: float
    triggered_assets: List[str]
    status: str = "PENDING"  # PENDING, IMMINENT, TRIGGERED, INTERCEPTED


class SphereStandardViolation(BaseModel):
    """UN Sphere Humanitarian Standard breach assessment."""
    standard_id: str = "SPHERE-WASH-1"
    description: str
    latrine_id: str
    tubewell_id: str
    distance_meters: float
    minimum_required_meters: float = 30.0
    hydraulic_gradient_risk: str
    status: str = "VIOLATION"


class CascadeSimulationResult(BaseModel):
    """Output of Compound Disaster Cascade Reasoning Engine."""
    scenario_id: str
    timestamp: str
    rain_rate_mm_hr: float
    soil_saturation: float
    cascade_probability: float
    time_to_slope_failure_min: int
    time_to_latrine_breach_min: int
    time_to_water_contamination_min: int
    stages: List[CascadeStage]
    compromised_assets: List[str]
    population_at_risk: int
    cholera_outbreak_risk_pct: float
    sphere_violations: List[SphereStandardViolation] = Field(default_factory=list)
    critical_interception_window_min: int = 25
    executive_summary: str


class TacticalMission(BaseModel):
    """Volunteer/CPP dispatch task order issued by Tactical Dispatch Agent."""
    mission_id: str
    priority: str = "P1_IMMEDIATE"  # P1_IMMEDIATE, P2_URGENT, P3_MONITOR
    target_asset_id: str
    assigned_team: str
    required_equipment: List[str]
    urgency_minutes: int
    objective_description: str
    target_gps: Dict[str, float]


class WASHAlert(BaseModel):
    """Drinking water protection directive issued by WASH Protection Agent."""
    alert_id: str
    affected_tubewells: List[str]
    shutoff_required: bool = True
    aquatab_strips_needed: int
    boil_advisory_languages: List[str] = Field(default_factory=lambda: ["Rohingya", "Bengali", "English"])
    population_warned: int
    chlorine_dosing_ppm: float = 2.0
    action_items: List[str]


class EvacuationPlan(BaseModel):
    """Turn-by-turn dynamic escape corridor issued by Micro-Evacuation Agent."""
    plan_id: str
    origin_shelters: List[str]
    safe_zone_id: str
    safe_zone_name: str
    waypoint_coordinates: List[Dict[str, float]]
    estimated_transit_minutes: int
    avoided_hazard_zones: List[str]
    instructions_multilingual: Dict[str, str]


class AgentSwarmDispatchResponse(BaseModel):
    """Synthesized command dispatch from Vertex AI Autonomous Agent Swarm."""
    timestamp: str
    scenario_id: str
    tactical_missions: List[TacticalMission]
    wash_alerts: List[WASHAlert]
    evacuation_plans: List[EvacuationPlan]
    dispatch_summary: str
    un_sphere_compliance_score: float = Field(100.0, ge=0.0, le=100.0)
    swarm_coordination_status: str = "ACTIVE_INTERCEPTION"
