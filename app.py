from __future__ import annotations

import json
import time
from datetime import timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

from src.analytics.explainability import contribution_note
from src.edge.gateway import EdgeGateway
from src.simulation.scenario_engine import ScenarioEngine
from src.simulation.telemetry import SyntheticTelemetryEngine
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.repository import TwinRepository
from src.twin.state import DataClass, Observation, PatientProfile, SimulationScenario
from src.ui.charts import scenario_comparison, state_history
from src.ui.components import analytics_panel, event_console, lifecycle, live_pipeline, live_signal_panel, metric_card, patient_visual, twin_engine_visual
from src.ui.styles import CSS

ROOT = Path(__file__).resolve().parent
PAGES = ["Command Center", "Live Twin", "State Explorer", "Risk & Explainability", "What-If Lab", "Cloud & Edge", "Evidence Lab"]

st.set_page_config(page_title="CRITICALCARE-TWIN", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def load_profiles():
    path = ROOT / "data" / "metadata" / "demo_profiles.json"
    if not path.exists():
        st.error("Demo profiles are missing. Run `python scripts/download_data.py` then `python scripts/prepare_data.py`.")
        st.stop()
    return [PatientProfile.model_validate(x) for x in json.loads(path.read_text(encoding="utf-8"))]


def init_twin(profile: PatientProfile):
    repo = TwinRepository(ROOT / "data" / "criticalcare_twin.sqlite")
    repo.save_patient(profile)
    model_meta = ROOT / "models" / "hospital_mortality_metadata.json"
    if model_meta.exists():
        repo.save_model_metadata("hospital_mortality", json.loads(model_meta.read_text(encoding="utf-8")))
    edge = EdgeGateway(outbox_path=ROOT / "data" / "edge_outbox.sqlite")
    twin = PatientDigitalTwin(profile, repository=repo, edge_gateway=edge)
    twin.ingest(Observation(patient_id=profile.patient_id, values=profile.baseline, quality={k: .82 for k in profile.baseline}, source=DataClass.OBSERVED))
    st.session_state.twin = twin
    st.session_state.replay = []
    st.session_state.replay_index = 0
    st.session_state.playing = False
    st.session_state.simulation = None


profiles = load_profiles()
labels = [p.static_properties.get("demo_label", p.patient_id) for p in profiles]
with st.sidebar:
    st.markdown('<div class="eyebrow">CRITICALCARE / RESEARCH</div>', unsafe_allow_html=True)
    st.title("◈ TWIN")
    selected_label = st.selectbox("Demonstration profile", labels)
    profile = profiles[labels.index(selected_label)]
    if "twin" not in st.session_state or st.session_state.twin.profile.patient_id != profile.patient_id:
        init_twin(profile)
    page = st.radio("Workspace", PAGES)
    st.divider()
    st.caption("LOCAL ENGINE · SQLITE · SEEDED REPLAY")
    st.caption("Outcome model: hospital_death")

twin = st.session_state.twin
st.markdown('<div class="eyebrow">PATIENT-SPECIFIC COMPUTATIONAL REPRESENTATION</div>', unsafe_allow_html=True)
st.title(f"{page}")
st.markdown(f'<div class="statusbar"><span class="statuspill">{twin.status}</span><span class="statuspill">{twin.twin_id}</span><span class="statuspill">PATIENT {twin.profile.patient_id}</span><span class="statuspill">VERSION {twin.twin_version}</span><span class="statuspill">LAST {twin.last_synchronization_time:%H:%M:%S}</span></div>', unsafe_allow_html=True)


def replay_controls():
    scenario = st.selectbox("Demonstration stream", ["Stable", "Respiratory deterioration", "Hemodynamic instability", "Fever/inflammatory stress"])
    speed = st.select_slider("Replay speed", options=[.5, 1, 2, 4], value=2, format_func=lambda x: f"{x}×")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("▶ Play", width="stretch"):
        if not st.session_state.replay:
            start = twin.last_synchronization_time + timedelta(minutes=5)
            st.session_state.replay = SyntheticTelemetryEngine().generate(twin.profile, scenario, 24, start)
        st.session_state.playing = True
    if c2.button("Ⅱ Pause", width="stretch"): st.session_state.playing = False
    if c3.button("Step →", width="stretch"):
        if not st.session_state.replay:
            start = twin.last_synchronization_time + timedelta(minutes=5)
            st.session_state.replay = SyntheticTelemetryEngine().generate(twin.profile, scenario, 24, start)
        idx = st.session_state.replay_index
        if idx < len(st.session_state.replay):
            twin.ingest(st.session_state.replay[idx]); st.session_state.replay_index += 1
    if c4.button("↺ Reset", width="stretch"): init_twin(twin.profile); st.rerun()
    total = max(len(st.session_state.replay), 1)
    st.progress(min(st.session_state.replay_index / total, 1), text=f"Observation {st.session_state.replay_index} / {len(st.session_state.replay)}")
    if st.session_state.playing and st.session_state.replay_index < len(st.session_state.replay):
        idx = st.session_state.replay_index
        twin.ingest(st.session_state.replay[idx]); st.session_state.replay_index += 1
        time.sleep(max(.12, .8 / speed)); st.rerun()
    elif st.session_state.playing:
        st.session_state.playing = False


if page == "Command Center":
    a,b,c,d = st.columns(4)
    a.metric("Hospital mortality model", f"{twin.risk_state.probability:.1%}", help="Dataset-defined encounter outcome; not a diagnosis")
    b.metric("Anomaly state", twin.risk_state.anomaly_state.upper(), f"score {twin.risk_state.anomaly_score:.2f}")
    c.metric("State confidence", f"{twin.uncertainty.state_confidence:.0%}")
    d.metric("Data quality", f"{twin.uncertainty.data_quality_score:.0%}")
    left, right = st.columns([1.05, 1.6])
    with left:
        patient_visual(twin)
        if twin.alerts:
            for alert in twin.alerts: st.warning(alert)
        else: st.success("No active prototype threshold alerts")
    with right:
        state_items = list(twin.current_state.parameters.items())
        derived_items = [(k,v) for k,v in twin.derived_state.items() if k in {"mean_arterial_pressure","pulse_pressure","shock_index_proxy"}]
        for start in range(0, len(state_items), 3):
            cols = st.columns(3)
            for col, (name, p) in zip(cols, state_items[start:start+3]):
                with col: metric_card(name, p.raw_value, p.filtered_value, p.delta, p.trend, p.measurement_confidence, p.source.value)
        cols = st.columns(3)
        for col, (name, value) in zip(cols, derived_items):
            with col: metric_card(name, value, value, source="DERIVED")

elif page == "Live Twin":
    replay_controls()
    live_pipeline(twin)
    incoming, engine, outputs = st.columns([1.05, .9, 1.05])
    with incoming: live_signal_panel(twin)
    with engine: twin_engine_visual(twin)
    with outputs: analytics_panel(twin)
    timeline, monitor = st.columns([1.05, 1.65])
    with timeline:
        st.subheader("Event timeline")
        event_console(twin.events.events, 10)
    with monitor:
        st.subheader("State motion")
        live_variable = st.selectbox("Monitor channel", ["heart_rate", "systolic_bp", "spo2", "respiratory_rate", "temperature"], label_visibility="collapsed")
        st.plotly_chart(state_history(twin, live_variable), width="stretch")
    st.caption("Replay values are SIMULATED DEMO TELEMETRY around an observed ICU encounter baseline.")

elif page == "State Explorer":
    variable = st.selectbox("State variable", list(twin.current_state.parameters))
    st.plotly_chart(state_history(twin, variable), width="stretch")
    rows = []
    previous = twin.previous_state.vector()
    for name, p in twin.current_state.parameters.items():
        rows.append({"Variable":name, "X(t-1)":previous.get(name), "Observation":p.raw_value, "X(t)":p.filtered_value, "Delta X":p.delta, "Patient baseline":twin.profile.baseline.get(name), "Rolling mean":p.rolling_mean, "Rolling SD":p.rolling_std, "Trend":p.trend, "Confidence":p.measurement_confidence, "Class":p.source.value})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption("RAW SENSOR VALUE → FILTERED TWIN VALUE → DERIVED TREND. Forecast is a prototype short-horizon extrapolation.")

elif page == "Risk & Explainability":
    a,b,c = st.columns(3)
    a.metric("Model-estimated hospital mortality", f"{twin.risk_state.probability:.1%}", twin.risk_state.label)
    b.metric("Patient-normalized anomaly", f"{twin.risk_state.anomaly_score:.2f}", twin.risk_state.anomaly_state)
    c.metric("Prediction confidence", f"{twin.risk_state.confidence:.0%}")
    left,right = st.columns(2)
    with left:
        st.subheader("Top model associations")
        contributions = pd.DataFrame(twin.model_outputs.get("contributions", []), columns=["Feature", "Relative contribution"])
        if not contributions.empty: st.bar_chart(contributions.set_index("Feature"))
        st.info(contribution_note())
    with right:
        st.subheader("Most patient-deviating variables")
        for index,name in enumerate(twin.risk_state.top_deviations,1): st.write(f"{index}. `{name}`")
        st.markdown("The anomaly detector is an independent transparent multivariate baseline-deviation method. It is a prototype metric, not a validated score.")

elif page == "What-If Lab":
    st.subheader("What-If Physiological Scenario Laboratory")
    st.warning("Research simulation only — not treatment guidance. Controls perturb a cloned computational state and do not recommend interventions.")
    controls = {}
    cols = st.columns(5)
    specs = [("heart_rate",-40.,40.),("systolic_bp",-40.,40.),("spo2",-15.,5.),("temperature",-3.,3.),("respiratory_rate",-10.,20.)]
    for col,(name,low,high) in zip(cols,specs):
        with col: controls[name] = st.slider(name.replace("_"," ").title(), low, high, 0., 1.)
    horizon = st.slider("Horizon (5-minute steps)", 2, 18, 8)
    if st.button("Run cloned scenario", type="primary"):
        scenario = SimulationScenario(name="User controlled physiology", perturbations={k:v for k,v in controls.items() if v}, horizon=horizon)
        st.session_state.simulation = ScenarioEngine().run(twin, scenario)
    result = st.session_state.simulation
    if result:
        a,b,c = st.columns(3)
        a.metric("Baseline clone risk", f"{result.baseline_risk:.1%}")
        b.metric("Scenario clone risk", f"{result.scenario_risk:.1%}", f"{result.scenario_risk-result.baseline_risk:+.1%}")
        c.metric("Actual twin isolation", "VERIFIED" if result.original_unchanged else "FAILED")
        variable = st.selectbox("Compare variable", [k for k in specs if k[0] in result.scenario_trajectory[0]], format_func=lambda x:x[0])[0]
        st.plotly_chart(scenario_comparison(result, variable), width="stretch")

elif page == "Cloud & Edge":
    status = twin.edge_gateway.status()
    a,b,c,d = st.columns(4)
    a.metric("Cloud service", "ONLINE" if status["online"] else "OFFLINE")
    b.metric("Buffered at edge", status["queued"])
    c.metric("Cloud-synced", status["synced"])
    d.metric("Edge site", status["site_id"])
    if st.button("Flush edge buffer", disabled=not status["online"]):
        result = twin.edge_gateway.flush()
        st.success(f"Sent {result['sent']} messages; {result['remaining']} remain queued.")
    st.graphviz_chart('''digraph { rankdir=LR; bgcolor="transparent"; node [shape=box style="rounded,filled" fillcolor="#10252c" color="#45d6c7" fontcolor="#e7f0f2" fontname="Arial"]; edge [color="#527780" fontcolor="#8fa5ad"]; Patient [label="Patient / demo source"]; Edge [label="EDGE NODE\nvalidation + twin sync\nstate estimation"]; Queue [label="Offline outbox\nSQLite"]; Cloud [label="CLOUD SERVICE API\npseudonymous snapshots"]; Store [label="Cloud twin store\nSQLite demo / managed DB ready"]; Fleet [label="Fleet summary API"]; Dash [label="Research dashboard"]; Patient -> Edge [label=" observation"]; Edge -> Queue [label=" durable message"]; Queue -> Cloud [label=" HTTPS sync"]; Cloud -> Store; Store -> Fleet; Edge -> Dash [label=" low latency"]; Cloud -> Dash [label=" cloud status"]; }''', width="stretch")
    left,right = st.columns(2)
    with left:
        st.subheader("Edge responsibilities")
        st.markdown("- Validate observations and update the patient twin with low latency\n- Continue while disconnected\n- Persist snapshots and queue outbound summaries\n- Hash the source patient ID before transmission")
    with right:
        st.subheader("Cloud responsibilities")
        st.markdown("- Accept idempotent versioned twin summaries\n- Store cross-session history by pseudonymous patient key\n- Expose latest-state and fleet-summary endpoints\n- Remain deployable without changing edge code")
    st.caption(f"Cloud endpoint: {status['cloud_url']} · Local service emulates the cloud boundary; no commercial cloud or paid API is required.")

elif page == "Evidence Lab":
    evidence_tab, model_tab = st.tabs(["Data provenance", "Model evaluation"])
    with evidence_tab:
        st.subheader("Source separation")
        st.dataframe(pd.DataFrame([
            ["mitishaagarwal/patient",91713,85,"ICU profile + hospital_death model","OBSERVED encounter summaries"],
            ["uom190346a/disease-symptoms-and-patient-profile-dataset",349,10,"Audited supplementary context","Not joined"],
            ["abbas829/healthcare-patient-analytics-dataset",5000,12,"Administrative provenance example","Not joined"],
        ], columns=["Dataset","Rows","Columns","Role","Linkage"]), width="stretch", hide_index=True)
        st.info("No cross-dataset join: identifiers are absent or source-local. Similar demographics are not a defensible linkage key.")
        lineage = [{"Field":k, "Classification":"SIMULATED" if p.source==DataClass.SIMULATED else p.source.value, "Origin":twin.profile.provenance.get(k,"runtime twin state")} for k,p in twin.current_state.parameters.items()]
        lineage += [{"Field":k,"Classification":"DERIVED","Origin":"FeatureEngine; transparent formula"} for k in ["mean_arterial_pressure","pulse_pressure","shock_index_proxy"]]
        st.dataframe(pd.DataFrame(lineage), width="stretch", hide_index=True)
    with model_tab:
        metadata = json.loads((ROOT / "models" / "hospital_mortality_metadata.json").read_text(encoding="utf-8"))
        results = [{"Model":name,"ROC-AUC":m["roc_auc"],"PR-AUC":m["pr_auc"],"Precision @ .25":m["precision_at_0.25"],"Recall @ .25":m["recall_at_0.25"],"Brier":m["brier"]} for name,m in metadata["candidates"].items()]
        st.dataframe(pd.DataFrame(results), width="stretch", hide_index=True)
        selected = metadata["candidates"][metadata["selected_model"]]
        x,y,z = st.columns(3)
        x.metric("Selected", metadata["selected_model"]); y.metric("ROC-AUC",f"{selected['roc_auc']:.3f}"); z.metric("PR-AUC",f"{selected['pr_auc']:.3f}")
        st.caption("Internal evaluation only; feature importance is associational, not causal.")
