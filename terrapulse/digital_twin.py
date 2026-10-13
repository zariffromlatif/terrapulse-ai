"""TerraPulse (CampTwin AI) - Settlement Digital Twin & Topographic Hydro-Graph.

Constructs an authentic spatial graph of Cox's Bazar Camp 4 (Block G), computes
hydrological flow routing, Topographic Wetness Index (TWI), elevation slopes,
and UN Sphere Humanitarian Standard proximity violations between sanitation and drinking water.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from terrapulse.models import (
    AssetStatus,
    AssetType,
    SettlementAsset,
    SphereStandardViolation,
)


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle ground distance between two points in meters."""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class CampDigitalTwin:
    """Autonomous Multimodal Digital Twin representing informal camp infrastructure & hydrology."""

    def __init__(self, block_name: str = "Camp 4 Block G"):
        self.block_name = block_name
        # Spatial infrastructure graph (undirected for physical pathways & adjacency)
        self.graph = nx.Graph()
        # Directed hydrological flow graph (downhill gravity routing)
        self.hydro_graph = nx.DiGraph()
        # Fast asset registry by ID
        self.assets: Dict[str, SettlementAsset] = {}
        # Prepopulate with authentic Cox's Bazar Camp 4 footprints
        self._build_authentic_coxs_bazar_camp4_topology()

    def _build_authentic_coxs_bazar_camp4_topology(self) -> None:
        """Loads authentic topographic and structural nodes based on HDX & OpenStreetMap footprints."""
        # Baseline reference: Camp 4 Block G, Kutupalong-Balukhali expansion
        # Elevation profile: Hill crest ~38m, slope terrace ~24-30m, ravine floor ~14-18m
        raw_assets = [
            # Culverts & Main Drainage
            SettlementAsset(
                id="CULVERT_C14",
                name="Culvert C-14 (Block G Main Drain)",
                asset_type=AssetType.CULVERT,
                latitude=21.19882,
                longitude=92.15340,
                elevation_m=16.5,
                capacity=150,
                condition_score=0.45,
                metadata={"catchment_m2": 4200, "lining": "brick_kacha", "nominal_flow_m3s": 3.8},
            ),
            SettlementAsset(
                id="CULVERT_C08",
                name="Culvert C-08 (Upper Gully Discharge)",
                asset_type=AssetType.CULVERT,
                latitude=21.19940,
                longitude=92.15280,
                elevation_m=22.0,
                capacity=100,
                condition_score=0.85,
                metadata={"catchment_m2": 2100, "lining": "pucca", "nominal_flow_m3s": 2.4},
            ),
            SettlementAsset(
                id="CULVERT_C22",
                name="Culvert C-22 (Canal Outfall)",
                asset_type=AssetType.CULVERT,
                latitude=21.19790,
                longitude=92.15410,
                elevation_m=13.2,
                capacity=220,
                condition_score=0.90,
                metadata={"catchment_m2": 8500, "lining": "reinforced_concrete", "nominal_flow_m3s": 5.2},
            ),
            # Bamboo Retaining Walls
            SettlementAsset(
                id="WALL_BW07",
                name="Bamboo Retaining Wall BW-07 (Terrace Cut)",
                asset_type=AssetType.RETAINING_WALL,
                latitude=21.19895,
                longitude=92.15320,
                elevation_m=24.5,
                capacity=0,
                condition_score=0.40,
                metadata={"height_m": 3.2, "length_m": 28.0, "deflection_angle_deg": 18.5, "soil_type": "sandy_clay"},
            ),
            SettlementAsset(
                id="WALL_BW03",
                name="Bamboo Retaining Wall BW-03 (Ridge Stabilizer)",
                asset_type=AssetType.RETAINING_WALL,
                latitude=21.19980,
                longitude=92.15250,
                elevation_m=34.0,
                capacity=0,
                condition_score=0.88,
                metadata={"height_m": 2.5, "length_m": 18.0, "deflection_angle_deg": 3.0, "soil_type": "clay_loam"},
            ),
            SettlementAsset(
                id="WALL_BW12",
                name="Bamboo Retaining Wall BW-12 (Slope Shoring)",
                asset_type=AssetType.RETAINING_WALL,
                latitude=21.19840,
                longitude=92.15370,
                elevation_m=19.8,
                capacity=0,
                condition_score=0.75,
                metadata={"height_m": 2.8, "length_m": 22.0, "deflection_angle_deg": 5.2, "soil_type": "sandy_loam"},
            ),
            # Latrine Pits (Sanitation)
            SettlementAsset(
                id="LATRINE_LP101",
                name="Community Latrine Pit LP-101",
                asset_type=AssetType.LATRINE_PIT,
                latitude=21.19888,
                longitude=92.15310,
                elevation_m=23.8,
                capacity=60,
                condition_score=0.50,
                metadata={"sludge_volume_liters": 2850, "pit_type": "twin_pit_pour_flush", "fill_level_pct": 82},
            ),
            SettlementAsset(
                id="LATRINE_LP102",
                name="Latrine Cluster LP-102",
                asset_type=AssetType.LATRINE_PIT,
                latitude=21.19950,
                longitude=92.15230,
                elevation_m=32.5,
                capacity=50,
                condition_score=0.82,
                metadata={"sludge_volume_liters": 1600, "pit_type": "twin_pit_pour_flush", "fill_level_pct": 45},
            ),
            SettlementAsset(
                id="LATRINE_LP108",
                name="Latrine Unit LP-108",
                asset_type=AssetType.LATRINE_PIT,
                latitude=21.19810,
                longitude=92.15450,
                elevation_m=15.0,
                capacity=40,
                condition_score=0.80,
                metadata={"sludge_volume_liters": 1200, "pit_type": "single_offset", "fill_level_pct": 50},
            ),
            # Drinking Water Points (Tubewells & Tapstands)
            SettlementAsset(
                id="TUBEWELL_TW04",
                name="Deep Tubewell TW-04 (Zone Central)",
                asset_type=AssetType.TUBEWELL,
                latitude=21.19875,
                longitude=92.15328,
                elevation_m=17.2,
                capacity=450,
                population_sheltered=450,
                condition_score=0.85,
                metadata={"depth_m": 125.0, "casing_status": "intact", "apron_cracked": True, "fecal_coliform_cfu_100ml": 0},
            ),
            SettlementAsset(
                id="TUBEWELL_TW09",
                name="Deep Tubewell TW-09 (Ridge Health Hub)",
                asset_type=AssetType.TUBEWELL,
                latitude=21.20010,
                longitude=92.15210,
                elevation_m=36.0,
                capacity=380,
                population_sheltered=380,
                condition_score=0.95,
                metadata={"depth_m": 140.0, "casing_status": "intact", "apron_cracked": False, "fecal_coliform_cfu_100ml": 0},
            ),
            SettlementAsset(
                id="TAPSTAND_TS12",
                name="Gravity Tapstand TS-12",
                asset_type=AssetType.TUBEWELL,
                latitude=21.19770,
                longitude=92.15430,
                elevation_m=14.0,
                capacity=300,
                population_sheltered=300,
                condition_score=0.90,
                metadata={"source": "chlorinated_network", "residual_chlorine_ppm": 0.5},
            ),
            # Safe Zones (Muster Points / High Elevation Centers)
            SettlementAsset(
                id="SAFEZONE_SZ01",
                name="Camp 4 Primary Community Safe Haven & CiC Complex",
                asset_type=AssetType.SAFE_ZONE,
                latitude=21.20040,
                longitude=92.15180,
                elevation_m=39.5,
                capacity=1800,
                population_sheltered=0,
                condition_score=1.0,
                metadata={"structure": "reinforced_masonry", "medical_kit": True, "emergency_water_m3": 45.0},
            ),
            SettlementAsset(
                id="SAFEZONE_SZ02",
                name="Learning Center North (Secondary Safe Point)",
                asset_type=AssetType.SAFE_ZONE,
                latitude=21.19990,
                longitude=92.15460,
                elevation_m=31.0,
                capacity=650,
                population_sheltered=0,
                condition_score=0.98,
                metadata={"structure": "semi_pucca", "solar_lighting": True},
            ),
            # Drainage Junctions
            SettlementAsset(
                id="DRAIN_J01",
                name="Ravine Confluence Junction DJ-01",
                asset_type=AssetType.DRAINAGE_JUNCTION,
                latitude=21.19870,
                longitude=92.15350,
                elevation_m=16.0,
                capacity=0,
                condition_score=0.70,
            ),
            SettlementAsset(
                id="DRAIN_J02",
                name="Mid-Slope Inflow Junction DJ-02",
                asset_type=AssetType.DRAINAGE_JUNCTION,
                latitude=21.19920,
                longitude=92.15300,
                elevation_m=20.5,
                capacity=0,
                condition_score=0.75,
            ),
            # Footpath Intersections
            SettlementAsset(
                id="PATH_P01",
                name="Main Access Ridge Trail Intersect",
                asset_type=AssetType.FOOTPATH,
                latitude=21.20020,
                longitude=92.15200,
                elevation_m=37.8,
                capacity=0,
            ),
            SettlementAsset(
                id="PATH_P02",
                name="Block G Upper Pathway",
                asset_type=AssetType.FOOTPATH,
                latitude=21.19960,
                longitude=92.15260,
                elevation_m=28.4,
                capacity=0,
            ),
            SettlementAsset(
                id="PATH_P03",
                name="Block G Mid Terraced Steps",
                asset_type=AssetType.FOOTPATH,
                latitude=21.19900,
                longitude=92.15300,
                elevation_m=23.0,
                capacity=0,
            ),
            SettlementAsset(
                id="PATH_P04",
                name="Ravine Crossing Plank Way",
                asset_type=AssetType.FOOTPATH,
                latitude=21.19860,
                longitude=92.15360,
                elevation_m=16.8,
                capacity=0,
            ),
            SettlementAsset(
                id="PATH_P05",
                name="East Ridge Bypass Trail",
                asset_type=AssetType.FOOTPATH,
                latitude=21.19970,
                longitude=92.15420,
                elevation_m=29.5,
                capacity=0,
            ),
        ]

        # Add Shelters S-401 through S-420 clustered along slopes
        shelter_configs = [
            ("SHELTER_S401", "Shelter S-401 (Family 12)", 21.20005, 92.15220, 35.5, 6),
            ("SHELTER_S402", "Shelter S-402 (Family 14)", 21.19985, 92.15235, 33.2, 7),
            ("SHELTER_S403", "Shelter S-403 (Family 19)", 21.19965, 92.15250, 30.1, 5),
            ("SHELTER_S404", "Shelter S-404 (Family 22)", 21.19945, 92.15265, 27.5, 8),
            ("SHELTER_S405", "Shelter S-405 (Family 25)", 21.19925, 92.15280, 25.0, 6),
            ("SHELTER_S406", "Shelter S-406 (Family 28)", 21.19910, 92.15290, 24.2, 5),
            ("SHELTER_S407", "Shelter S-407 (Family 31)", 21.19900, 92.15298, 23.5, 7),
            # Vulnerable cluster directly on slope below WALL_BW07 & LP101
            ("SHELTER_S408", "Shelter S-408 (Family 34)", 21.19890, 92.15312, 22.8, 6),
            ("SHELTER_S409", "Shelter S-409 (Family 38)", 21.19882, 92.15318, 21.5, 5),
            ("SHELTER_S410", "Shelter S-410 (Family 41)", 21.19875, 92.15322, 20.2, 8),
            ("SHELTER_S411", "Shelter S-411 (Family 45)", 21.19868, 92.15328, 19.1, 6),
            ("SHELTER_S412", "Shelter S-412 (Family 48)", 21.19860, 92.15335, 18.2, 7),
            ("SHELTER_S413", "Shelter S-413 (Family 52)", 21.19852, 92.15342, 17.6, 6),
            ("SHELTER_S414", "Shelter S-414 (Family 55)", 21.19845, 92.15350, 17.0, 5),
            ("SHELTER_S415", "Shelter S-415 (Family 59)", 21.19838, 92.15358, 16.5, 8),
            # Eastern terraced slope
            ("SHELTER_S416", "Shelter S-416 (Family 62)", 21.19920, 92.15380, 23.8, 6),
            ("SHELTER_S417", "Shelter S-417 (Family 66)", 21.19940, 92.15400, 26.5, 7),
            ("SHELTER_S418", "Shelter S-418 (Family 70)", 21.19960, 92.15420, 29.0, 5),
            ("SHELTER_S419", "Shelter S-419 (Family 73)", 21.19880, 92.15390, 21.0, 6),
            ("SHELTER_S420", "Shelter S-420 (Family 78)", 21.19850, 92.15410, 18.5, 7),
        ]

        for s_id, s_name, lat, lon, elev, pop in shelter_configs:
            raw_assets.append(
                SettlementAsset(
                    id=s_id,
                    name=s_name,
                    asset_type=AssetType.SHELTER,
                    latitude=lat,
                    longitude=lon,
                    elevation_m=elev,
                    capacity=pop,
                    population_sheltered=pop,
                    condition_score=0.90,
                    metadata={"family_members": pop, "bamboo_condition": "stable"},
                )
            )

        # Register nodes in graph
        for a in raw_assets:
            self.add_asset(a)

        # Build physical connectivity edges (pathways, stairways, channels)
        physical_edges: List[Tuple[str, str, str, float]] = [
            # Ridge Trail to Safe Haven
            ("SAFEZONE_SZ01", "PATH_P01", "reinforced_path", 1.0),
            ("PATH_P01", "TUBEWELL_TW09", "footpath", 1.0),
            ("PATH_P01", "SHELTER_S401", "footpath", 1.0),
            ("SHELTER_S401", "SHELTER_S402", "footpath", 1.0),
            ("SHELTER_S402", "WALL_BW03", "terraced_steps", 1.2),
            ("WALL_BW03", "LATRINE_LP102", "footpath", 1.1),
            ("SHELTER_S402", "PATH_P02", "footpath", 1.0),
            ("PATH_P02", "SHELTER_S403", "footpath", 1.0),
            ("SHELTER_S403", "SHELTER_S404", "footpath", 1.0),
            ("SHELTER_S404", "CULVERT_C08", "drainage_bank", 1.3),
            ("CULVERT_C08", "DRAIN_J02", "concrete_channel", 1.0),
            ("SHELTER_S404", "SHELTER_S405", "footpath", 1.0),
            ("SHELTER_S405", "PATH_P03", "footpath", 1.0),
            ("PATH_P03", "WALL_BW07", "bamboo_steps", 1.4),
            ("WALL_BW07", "LATRINE_LP101", "path", 1.1),
            ("PATH_P03", "SHELTER_S406", "footpath", 1.0),
            ("SHELTER_S406", "SHELTER_S407", "footpath", 1.0),
            ("SHELTER_S407", "SHELTER_S408", "footpath", 1.0),
            ("SHELTER_S408", "SHELTER_S409", "footpath", 1.0),
            ("SHELTER_S409", "SHELTER_S410", "footpath", 1.0),
            ("SHELTER_S410", "TUBEWELL_TW04", "access_path", 1.0),
            ("TUBEWELL_TW04", "DRAIN_J01", "drainage_apron", 1.1),
            ("DRAIN_J01", "CULVERT_C14", "culvert_entry", 1.2),
            ("CULVERT_C14", "PATH_P04", "footpath", 1.0),
            ("SHELTER_S410", "SHELTER_S411", "footpath", 1.0),
            ("SHELTER_S411", "SHELTER_S412", "footpath", 1.0),
            ("SHELTER_S412", "SHELTER_S413", "footpath", 1.0),
            ("SHELTER_S413", "SHELTER_S414", "footpath", 1.0),
            ("SHELTER_S414", "SHELTER_S415", "footpath", 1.0),
            ("SHELTER_S415", "WALL_BW12", "slope_edge", 1.3),
            ("PATH_P04", "DRAIN_J01", "drain_flank", 1.2),
            ("PATH_P04", "CULVERT_C22", "canal_path", 1.1),
            ("CULVERT_C22", "TAPSTAND_TS12", "piped_route", 1.0),
            ("TAPSTAND_TS12", "LATRINE_LP108", "footpath", 1.0),
            # East Ridge safe bypass
            ("PATH_P03", "PATH_P05", "cross_contour_path", 1.1),
            ("PATH_P05", "SAFEZONE_SZ02", "wide_paved_path", 1.0),
            ("SAFEZONE_SZ02", "SHELTER_S418", "footpath", 1.0),
            ("SHELTER_S418", "SHELTER_S417", "footpath", 1.0),
            ("SHELTER_S417", "SHELTER_S416", "footpath", 1.0),
            ("SHELTER_S416", "DRAIN_J02", "gully_steps", 1.2),
            ("SAFEZONE_SZ02", "SAFEZONE_SZ01", "ridge_connector_paved", 0.9),
        ]

        for u, v, edge_type, factor in physical_edges:
            if u in self.assets and v in self.assets:
                a1 = self.assets[u]
                a2 = self.assets[v]
                dist = haversine_distance_meters(a1.latitude, a1.longitude, a2.latitude, a2.longitude)
                elev_diff = abs(a1.elevation_m - a2.elevation_m)
                # 3D traversal weight
                weight = math.sqrt(dist**2 + elev_diff**2) * factor
                self.graph.add_edge(u, v, edge_type=edge_type, distance_m=dist, weight=weight)

        # Build gravity-driven hydraulic flow directed graph
        self._build_hydrological_routing()

    def add_asset(self, asset: SettlementAsset) -> None:
        """Inserts or updates an asset in the digital twin."""
        self.assets[asset.id] = asset
        self.graph.add_node(
            asset.id,
            name=asset.name,
            asset_type=asset.asset_type.value,
            latitude=asset.latitude,
            longitude=asset.longitude,
            elevation_m=asset.elevation_m,
            status=asset.status.value,
            condition_score=asset.condition_score,
            population_sheltered=asset.population_sheltered,
        )

    def _build_hydrological_routing(self) -> None:
        """Derives downhill hydraulic flow direction for surface runoff based on DEM gradients."""
        self.hydro_graph.clear()
        for node_id, data in self.graph.nodes(data=True):
            self.hydro_graph.add_node(node_id, **data)

        # Connect downhill edges between geographically adjacent assets (within 80m)
        all_ids = list(self.assets.keys())
        for i in range(len(all_ids)):
            u_id = all_ids[i]
            u = self.assets[u_id]
            for j in range(i + 1, len(all_ids)):
                v_id = all_ids[j]
                v = self.assets[v_id]
                dist = haversine_distance_meters(u.latitude, u.longitude, v.latitude, v.longitude)
                if dist <= 65.0:
                    elev_diff = u.elevation_m - v.elevation_m
                    # Gravity flow from higher elevation to lower elevation
                    if elev_diff > 0.5:
                        slope_pct = (elev_diff / dist) * 100.0
                        self.hydro_graph.add_edge(
                            u_id,
                            v_id,
                            distance_m=dist,
                            drop_m=elev_diff,
                            slope_gradient_pct=slope_pct,
                            flow_type="surface_runoff",
                        )
                    elif elev_diff < -0.5:
                        slope_pct = (abs(elev_diff) / dist) * 100.0
                        self.hydro_graph.add_edge(
                            v_id,
                            u_id,
                            distance_m=dist,
                            drop_m=abs(elev_diff),
                            slope_gradient_pct=slope_pct,
                            flow_type="surface_runoff",
                        )

    def calculate_topographic_wetness_index(self) -> Dict[str, float]:
        """Calculates Topographic Wetness Index (TWI = ln(A / tan(beta))) for each node.

        Nodes with high TWI accumulate high runoff and are prime flood/failure hotspots.
        """
        twi_scores: Dict[str, float] = {}

        for node_id in self.assets:
            # Catchment accumulation: number of upstream nodes draining into this node
            ancestors = nx.ancestors(self.hydro_graph, node_id) if node_id in self.hydro_graph else set()
            contributing_area = max(1.0, float(len(ancestors) * 350.0))  # approx m^2 per sub-catchment

            # Estimate local slope from outgoing edges
            outgoing = list(self.hydro_graph.out_edges(node_id, data=True))
            if outgoing:
                avg_slope_pct = sum(d.get("slope_gradient_pct", 10.0) for _, _, d in outgoing) / len(outgoing)
                slope_rad = max(0.05, math.atan(avg_slope_pct / 100.0))
            else:
                # Depression or base ravine
                slope_rad = 0.04

            tan_beta = math.tan(slope_rad)
            twi = math.log(contributing_area / tan_beta)
            twi_scores[node_id] = round(twi, 2)

        return twi_scores

    def detect_sphere_wash_violations(self) -> List[SphereStandardViolation]:
        """Audits settlement against UN Sphere Humanitarian Standard (WASH standard 1).

        Requirement: Minimum 30 meters horizontal separation between latrine pits
        and drinking water sources, with strict avoidance of uphill sanitation
        discharging towards water aprons.
        """
        violations: List[SphereStandardViolation] = []
        latrines = [a for a in self.assets.values() if a.asset_type == AssetType.LATRINE_PIT]
        tubewells = [a for a in self.assets.values() if a.asset_type == AssetType.TUBEWELL]

        for lp in latrines:
            for tw in tubewells:
                dist = haversine_distance_meters(lp.latitude, lp.longitude, tw.latitude, tw.longitude)
                # Sphere minimum separation is 30.0 meters
                elev_diff = lp.elevation_m - tw.elevation_m
                is_uphill = elev_diff > 1.0

                # Check if hydraulic path exists from latrine to tubewell
                has_downstream_path = False
                if lp.id in self.hydro_graph and tw.id in self.hydro_graph:
                    has_downstream_path = nx.has_path(self.hydro_graph, lp.id, tw.id)

                if dist < 30.0 or (has_downstream_path and is_uphill and dist < 45.0):
                    risk_level = "CRITICAL_FLOWPATH" if has_downstream_path else "HIGH_PROXIMITY"
                    violations.append(
                        SphereStandardViolation(
                            standard_id="UN-SPHERE-WASH-1.2",
                            description=(
                                f"Sanitation unit '{lp.name}' is within {dist:.1f}m of drinking source "
                                f"'{tw.name}' (UN Sphere min 30.0m requirement violated). "
                                f"Elevation drop: {elev_diff:.1f}m ({'Uphill contamination vector' if is_uphill else 'Horizontal'})."
                            ),
                            latrine_id=lp.id,
                            tubewell_id=tw.id,
                            distance_meters=round(dist, 1),
                            minimum_required_meters=30.0,
                            hydraulic_gradient_risk=risk_level,
                            status="VIOLATION",
                        )
                    )

        return violations

    def find_safe_evacuation_routes(
        self,
        origin_shelter_ids: List[str],
        hazardous_nodes: Set[str],
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    ) -> List[Dict[str, Any]]:
        """Computes dynamic escape corridors to nearest safe zone bypassing hazardous slopes & torrents."""
        if blocked_edges is None:
            blocked_edges = set()

        safe_zones = [a.id for a in self.assets.values() if a.asset_type == AssetType.SAFE_ZONE]
        routes: List[Dict[str, Any]] = []

        for shelter_id in origin_shelter_ids:
            if shelter_id not in self.assets:
                continue

            # Create safe traversal subgraph per origin, preserving origin shelter start node
            traversal_graph = self.graph.copy()
            for h in hazardous_nodes:
                if h != shelter_id and traversal_graph.has_node(h):
                    traversal_graph.remove_node(h)

            for u, v in blocked_edges:
                if traversal_graph.has_edge(u, v):
                    traversal_graph.remove_edge(u, v)

            best_path = None
            best_cost = float("inf")
            target_safe_zone = None

            for sz in safe_zones:
                if sz not in traversal_graph or shelter_id not in traversal_graph:
                    continue
                try:
                    path = nx.shortest_path(traversal_graph, source=shelter_id, target=sz, weight="weight")
                    cost = nx.shortest_path_length(traversal_graph, source=shelter_id, target=sz, weight="weight")
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path
                        target_safe_zone = sz
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

            if best_path and target_safe_zone:
                waypoints = [
                    {
                        "node_id": nid,
                        "latitude": self.assets[nid].latitude,
                        "longitude": self.assets[nid].longitude,
                        "elevation_m": self.assets[nid].elevation_m,
                    }
                    for nid in best_path
                ]
                routes.append(
                    {
                        "shelter_id": shelter_id,
                        "safe_zone_id": target_safe_zone,
                        "safe_zone_name": self.assets[target_safe_zone].name,
                        "waypoints": waypoints,
                        "path_node_ids": best_path,
                        "transit_distance_m": round(best_cost, 1),
                        "estimated_minutes": max(3, int(best_cost / 35.0)),  # avg camp walking pace ~35m/min on mud slopes
                    }
                )

        return routes

    def export_geojson(self) -> Dict[str, Any]:
        """Exports the full digital twin topology as a GeoJSON FeatureCollection."""
        features: List[Dict[str, Any]] = []

        # 1. Point Features for Assets
        for asset_id, asset in self.assets.items():
            color = "#3b82f6"  # blue default
            if asset.asset_type == AssetType.SHELTER:
                color = "#10b981"  # green
            elif asset.asset_type == AssetType.CULVERT:
                color = "#f59e0b"  # amber
            elif asset.asset_type == AssetType.RETAINING_WALL:
                color = "#8b5cf6"  # purple
            elif asset.asset_type == AssetType.LATRINE_PIT:
                color = "#ef4444"  # red
            elif asset.asset_type == AssetType.TUBEWELL:
                color = "#06b6d4"  # cyan
            elif asset.asset_type == AssetType.SAFE_ZONE:
                color = "#22c55e"  # emerald

            if asset.status == AssetStatus.CRITICAL or asset.status == AssetStatus.COMPROMISED:
                color = "#dc2626"

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [asset.longitude, asset.latitude],
                },
                "properties": {
                    "id": asset.id,
                    "name": asset.name,
                    "asset_type": asset.asset_type.value,
                    "elevation_m": asset.elevation_m,
                    "status": asset.status.value,
                    "capacity": asset.capacity,
                    "population": asset.population_sheltered,
                    "condition_score": asset.condition_score,
                    "marker_color": color,
                    **asset.metadata,
                },
            }
            features.append(feature)

        # 2. LineString Features for Physical Pathways & Infrastructure
        for u, v, data in self.graph.edges(data=True):
            a1 = self.assets[u]
            a2 = self.assets[v]
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [a1.longitude, a1.latitude],
                            [a2.longitude, a2.latitude],
                        ],
                    },
                    "properties": {
                        "source": u,
                        "target": v,
                        "edge_type": data.get("edge_type", "footpath"),
                        "distance_m": round(data.get("distance_m", 0.0), 1),
                        "line_color": "#64748b" if "path" in data.get("edge_type", "") else "#0284c7",
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "metadata": {
                "project": "TerraPulse CampTwin AI",
                "block": self.block_name,
                "node_count": len(self.assets),
                "edge_count": self.graph.number_of_edges(),
            },
            "features": features,
        }
