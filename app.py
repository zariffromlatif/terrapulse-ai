"""TerraPulse (CampTwin AI) - Application Entrypoint.

Supports direct execution via:
1. `python app.py` -> Starts FastAPI production server with interactive Web HUD on port 8080.
2. `streamlit run app.py` -> Starts Streamlit analytical operations dashboard.
"""

import os
import sys

# Detect if running under Streamlit
is_streamlit = "streamlit" in sys.modules or any("streamlit" in arg for arg in sys.argv)

if is_streamlit:
    import streamlit as st
    from terrapulse.service import TerraPulseService

    st.set_page_config(
        page_title="TerraPulse // CampTwin AI",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "service" not in st.session_state:
        st.session_state.service = TerraPulseService()
    service = st.session_state.service

    st.title("🌍 TerraPulse (CampTwin AI)")
    st.markdown(
        "**Autonomous Multimodal Digital Twin & Compound Disaster Cascade Interceptor for Informal Settlements**  \n"
        "*Google Cloud AI Builder Cup 2026 // Sustainability & Social Impact Track // Cox's Bazar Anchor*"
    )

    st.sidebar.header("Scenario Operations")
    scenarios = service.get_preloaded_scenarios()
    sc_names = [s["name"] for s in scenarios]
    selected_name = st.sidebar.selectbox("Choose Hydro-Meteorological Scenario", sc_names)
    selected_sc = next(s for s in scenarios if s["name"] == selected_name)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Telemetry Override")
    rain = st.sidebar.slider("NASA GPM Rain Rate (mm/hr)", 0.0, 120.0, float(selected_sc["telemetry"]["gpm_rain_rate_mm_hr"]))
    soil = st.sidebar.slider("Sentinel-1 SAR Soil Moisture", 0.0, 1.0, float(selected_sc["telemetry"]["sentinel1_soil_saturation"]))

    if st.sidebar.button("⚡ Run Interception Simulation", type="primary"):
        from terrapulse.models import OrbitalTelemetry
        tel = OrbitalTelemetry(
            gpm_rain_rate_mm_hr=rain,
            sentinel1_soil_saturation=soil,
            copernicus_dem_slope_deg=selected_sc["telemetry"]["copernicus_dem_slope_deg"],
        )
        res = service.run_full_pipeline(
            telemetry=tel,
            inspection_text=selected_sc["inspection_text"],
            scenario_id=selected_sc["id"],
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cascade Risk", f"{res['cascade']['cascade_probability']*100:.1f}%")
        col2.metric("Interception Window", f"{res['cascade']['critical_interception_window_min']} min")
        col3.metric("Pop at Risk", f"{res['cascade']['population_at_risk']} people")
        col4.metric("Cholera Risk", f"{res['cascade']['cholera_outbreak_risk_pct']}%")

        st.subheader("⏱️ 5-Stage Domino Cascade Sequence")
        for stage in res["cascade"]["stages"]:
            st.info(f"**Stage {stage['stage_index']}: {stage['stage_name']} (T+{stage['time_offset_minutes']}m)**: {stage['description']}")

        st.subheader("🤖 Vertex AI Autonomous Agent Swarm Interception")
        t1, t2, t3 = st.tabs(["Tactical Dispatch", "WASH Protection", "Micro-Evacuation"])
        with t1:
            for m in res["dispatch"]["tactical_missions"]:
                st.write(f"**{m['priority']} - {m['assigned_team']}**: {m['objective_description']}")
                st.caption(f"Required Tools: {', '.join(m['required_equipment'])}")
        with t2:
            for w in res["dispatch"]["wash_alerts"]:
                st.warning(f"Lock Tubewells: {', '.join(w['affected_tubewells'])} | AquaTabs: {w['aquatab_strips_needed']} strips")
                for item in w["action_items"]:
                    st.write(f"- {item}")
        with t3:
            for ep in res["dispatch"]["evacuation_plans"]:
                st.success(f"Corridor: {ep['safe_zone_name']} (Est. {ep['estimated_transit_minutes']} min)")
                st.json(ep["instructions_multilingual"])
    else:
        st.info("Select a scenario from the sidebar and click 'Run Interception Simulation' to view the digital twin analysis.")

else:
    # Direct execution: Start FastAPI server
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting TerraPulse API & Command HUD on http://0.0.0.0:{port} ...")
    uvicorn.run("terrapulse.api:app", host="0.0.0.0", port=port, reload=False)
