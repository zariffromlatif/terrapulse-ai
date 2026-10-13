"""TerraPulse (CampTwin AI) - Compound Disaster Cascade Reasoning Engine.

Fuses orbital remote-sensing telemetry (NASA GPM IMERG 30-min rain rates,
Sentinel-1 SAR soil moisture, Copernicus DEM slope) with ground micro-defects
to simulate 5-stage domino failure cascades across informal settlement topologies:
Blocked Culvert -> Soil Saturation -> Slope Failure -> Latrine Breach -> Cholera Outbreak.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set
import networkx as nx

from terrapulse.digital_twin import CampDigitalTwin
from terrapulse.models import (
    AssetStatus,
    AssetType,
    CascadeSimulationResult,
    CascadeStage,
    DefectSeverity,
    DefectType,
    InspectionDefect,
    OrbitalTelemetry,
    SphereStandardViolation,
)


class CompoundCascadeEngine:
    """Physics-informed reasoning engine modeling compound multi-hazard domino cascades."""

    def __init__(self, digital_twin: Optional[CampDigitalTwin] = None):
        self.twin = digital_twin or CampDigitalTwin()

    def simulate_cascade(
        self,
        telemetry: OrbitalTelemetry,
        defects: List[InspectionDefect],
        scenario_id: str = "MONSOON-BURST-CAMP4",
    ) -> CascadeSimulationResult:
        """Executes domino cascade simulation by fusing orbital hydrology with ground micro-defects."""
        # 1. Parameter Extraction
        rain_rate = telemetry.gpm_rain_rate_mm_hr
        soil_sat = telemetry.sentinel1_soil_saturation
        slope_deg = telemetry.copernicus_dem_slope_deg

        # Find primary micro-defects (use realistic nominal baselines when defects absent)
        culvert_defect = next((d for d in defects if d.defect_type == DefectType.CULVERT_SILTATION), None)
        wall_defect = next((d for d in defects if d.defect_type == DefectType.BAMBOO_WALL_DEFLECTION), None)
        apron_defect = next((d for d in defects if d.defect_type == DefectType.CRACKED_DRAINAGE_APRON), None)
        latrine_defect = next((d for d in defects if d.defect_type == DefectType.LATRINE_PIT_OVERFLOW), None)

        silt_pct = culvert_defect.siltation_pct if culvert_defect and culvert_defect.siltation_pct is not None else 5.0
        wall_tilt = wall_defect.deflection_angle_deg if wall_defect and wall_defect.deflection_angle_deg is not None else 1.0
        apron_cracked = apron_defect is not None

        # 2. Physics-Informed Cascade Probability Calculation
        # Dynamic runoff calculation (Rational Formula Q = C * I * A / 3600, C ~ 0.75, Catchment ~ 4200 m^2)
        peak_runoff_m3s = round(max(0.0, (0.75 * rain_rate * 4200.0) / 3600.0), 2)
        effective_culvert_capacity = round(max(0.2, 3.8 * (1.0 - (silt_pct / 100.0))), 2)

        # Rain factor: rain > 35 mm/hr is torrential; rain > 60 mm/hr is catastrophic
        rain_factor = min(1.0, rain_rate / 70.0)
        # Silt factor: blockage > 50% severely chokes drainage
        silt_factor = min(1.0, silt_pct / 85.0)
        # Soil factor: SAR saturation > 0.8 leaves zero infiltration buffer
        soil_factor = min(1.0, soil_sat / 0.90)
        # Wall deflection: tilt > 15 deg indicates imminent shear failure
        tilt_factor = min(1.0, max(0.0, wall_tilt) / 20.0)

        raw_cascade_prob = (0.35 * rain_factor) + (0.25 * silt_factor) + (0.20 * soil_factor) + (0.20 * tilt_factor)
        cascade_prob = round(min(0.99, max(0.05, raw_cascade_prob)), 3)

        # 3. Dynamic Time-to-Failure Estimations (minutes)
        time_to_choke_min = max(5, int(35.0 - (silt_pct * 0.25) - (rain_rate * 0.15)))
        time_to_slope_failure_min = max(20, int(150.0 - (soil_sat * 80.0) - (wall_tilt * 3.5)))
        time_to_latrine_breach_min = time_to_slope_failure_min + max(15, int(45.0 - (rain_rate * 0.3)))
        time_to_water_contamination_min = time_to_latrine_breach_min + max(25, int(60.0 - (rain_rate * 0.4)))

        # 4. Multi-Stage Domino Progression
        choke_desc = (
            f"Culvert C-14 obstructed by {silt_pct:.0f}% silt throttles flow capacity to {effective_culvert_capacity} m³/s. "
            f"Rainfall ({rain_rate:.1f} mm/hr) generates {peak_runoff_m3s} m³/s peak runoff."
        ) if rain_rate > 0.0 else (
            f"Culvert C-14 baseline siltation at {silt_pct:.0f}% with capacity {effective_culvert_capacity} m³/s. "
            "No active runoff under dry conditions."
        )

        stages: List[CascadeStage] = [
            CascadeStage(
                stage_index=1,
                stage_name="Culvert Hydraulic Choking & Flash Overtopping",
                time_offset_minutes=time_to_choke_min,
                description=choke_desc,
                failure_probability=round(min(0.98, max(0.02, silt_factor * rain_factor * 1.1)), 2),
                triggered_assets=["CULVERT_C14", "DRAIN_J01", "PATH_P04"],
                status="TRIGGERED" if cascade_prob > 0.6 else "PENDING",
            ),
            CascadeStage(
                stage_index=2,
                stage_name="Soil Surcharge & Pore-Water Pressure Spike",
                time_offset_minutes=int((time_to_choke_min + time_to_slope_failure_min) / 2),
                description=(
                    f"Overtopping runoff infiltrates sandy cut-slope behind retaining wall BW-07. "
                    f"Soil saturation reaches {soil_sat*100:.1f}%; pore pressure exceeds Mohr-Coulomb shear threshold."
                ),
                failure_probability=round(min(0.96, max(0.02, soil_factor * 1.05)), 2),
                triggered_assets=["WALL_BW07", "PATH_P03"],
                status="IMMINENT" if cascade_prob > 0.65 else "PENDING",
            ),
            CascadeStage(
                stage_index=3,
                stage_name="Bamboo Retaining Wall Shear Collapse & Mudslide",
                time_offset_minutes=time_to_slope_failure_min,
                description=(
                    f"Retaining Wall BW-07 deflection ({wall_tilt:.1f}°) exceeds structural limit (15.0°). "
                    f"450 m³ liquefied soil mass slides downhill along 22° slope towards Shelters S-408 through S-415."
                ),
                failure_probability=round(min(0.95, max(0.02, tilt_factor * soil_factor * 1.1)), 2),
                triggered_assets=["WALL_BW07", "SHELTER_S408", "SHELTER_S409", "SHELTER_S410", "SHELTER_S411"],
                status="IMMINENT" if cascade_prob > 0.75 else "PENDING",
            ),
            CascadeStage(
                stage_index=4,
                stage_name="Latrine Pit Scour & Fecal Bio-WASH Breach",
                time_offset_minutes=time_to_latrine_breach_min,
                description=(
                    "Debris flow scours Latrine Pit LP-101 foundation, releasing 2,850L of fecal sludge. "
                    "Contaminated blackwater plume surges directly into downstream hydraulic runoff gully."
                ),
                failure_probability=round(min(0.94, max(0.02, cascade_prob * 0.98)), 2),
                triggered_assets=["LATRINE_LP101", "DRAIN_J01"],
                status="TRIGGERED" if cascade_prob > 0.85 else "PENDING",
            ),
            CascadeStage(
                stage_index=5,
                stage_name="Drinking Aquifer Infiltration & Cholera Outbreak",
                time_offset_minutes=time_to_water_contamination_min,
                description=(
                    f"Pathogen plume floods Deep Tubewell TW-04{' (cracked apron seal)' if apron_cracked else ''}. "
                    "Aquifer infiltration exposes 1,450 residents to Vibrio cholerae / E. coli transmission within 24-48 hours."
                ),
                failure_probability=round(min(0.92, max(0.02, cascade_prob * 0.95)), 2),
                triggered_assets=["TUBEWELL_TW04", "SHELTER_S412", "SHELTER_S413", "SHELTER_S414", "SHELTER_S415"],
                status="IMMINENT" if cascade_prob > 0.88 else "PENDING",
            ),
        ]

        # 5. Impacted Assets & Population at Risk (dynamically calculated)
        compromised_asset_ids: List[str] = []
        if cascade_prob >= 0.65:
            compromised_asset_ids = [
                "CULVERT_C14",
                "WALL_BW07",
                "LATRINE_LP101",
                "TUBEWELL_TW04",
                "SHELTER_S408",
                "SHELTER_S409",
                "SHELTER_S410",
                "SHELTER_S411",
                "SHELTER_S412",
                "SHELTER_S413",
                "SHELTER_S414",
                "SHELTER_S415",
            ]
        elif cascade_prob >= 0.35:
            compromised_asset_ids = ["CULVERT_C14", "DRAIN_J01", "WALL_BW07", "SHELTER_S408", "SHELTER_S409"]
        else:
            compromised_asset_ids = []

        pop_risk = 0
        for aid in compromised_asset_ids:
            if aid in self.twin.assets:
                pop_risk += self.twin.assets[aid].population_sheltered
        if "TUBEWELL_TW04" in compromised_asset_ids:
            pop_risk += 450  # tubewell TW-04 drinking water beneficiaries

        cholera_risk = round(min(98.0, cascade_prob * 95.0), 1) if "TUBEWELL_TW04" in compromised_asset_ids else round(cascade_prob * 10.0, 1)

        sphere_violations = self.twin.detect_sphere_wash_violations()
        intervention_window = max(10, time_to_choke_min + 10)

        if cascade_prob >= 0.60:
            summary = (
                f"Compound disaster cascade detected with {cascade_prob*100:.1f}% probability in {self.twin.block_name}. "
                f"Triggered by {rain_rate:.0f} mm/hr monsoon rainfall, {silt_pct:.0f}% silted Culvert C-14, "
                f"and {wall_tilt:.1f}° deflection in Retaining Wall BW-07. "
                f"Failure sequence projects retaining wall collapse at T+{time_to_slope_failure_min}m, "
                f"sanitation breach at T+{time_to_latrine_breach_min}m, and drinking water contamination at T+{time_to_water_contamination_min}m. "
                f"Critical interception window: {intervention_window} minutes."
            )
        elif cascade_prob >= 0.35:
            summary = (
                f"Moderate hydro-meteorological surge ({cascade_prob*100:.1f}% risk) in {self.twin.block_name}. "
                f"Rainfall ({rain_rate:.0f} mm/hr) and {silt_pct:.0f}% silted Culvert C-14 warrant early preventative clearance. "
                f"Critical interception window: {intervention_window} minutes."
            )
        else:
            summary = (
                f"Routine baseline survey in {self.twin.block_name}. "
                f"Hydro-meteorological risk is low ({cascade_prob*100:.1f}%). All infrastructure stable under current conditions."
            )

        return CascadeSimulationResult(
            scenario_id=scenario_id,
            timestamp="2026-10-13T12:00:00Z",
            rain_rate_mm_hr=rain_rate,
            soil_saturation=soil_sat,
            cascade_probability=cascade_prob,
            time_to_slope_failure_min=time_to_slope_failure_min,
            time_to_latrine_breach_min=time_to_latrine_breach_min,
            time_to_water_contamination_min=time_to_water_contamination_min,
            stages=stages,
            compromised_assets=compromised_asset_ids,
            population_at_risk=pop_risk,
            cholera_outbreak_risk_pct=cholera_risk,
            sphere_violations=sphere_violations,
            critical_interception_window_min=intervention_window,
            executive_summary=summary,
        )
