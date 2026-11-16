from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics.explainability import contribution_note
from src.edge.gateway import EdgeGateway
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.repository import TwinRepository
from src.twin.state import DataClass, Observation, PatientProfile
from src.ui.charts import state_history
from src.ui.components import analytics_panel, event_console, live_pipeline, live_signal_panel, metric_card, patient_visual, twin_engine_visual
from src.ui.styles import CSS

ROOT = Path(__file__).resolve().parent
PAGES = ["Command Center", "Observation Ingestion", "State Explorer", "Risk & Explainability", "Digital Twin Platform", "Evidence Lab"]
MEASUREMENTS = ["heart_rate", "systolic_bp", "diastolic_bp", "respiratory_rate", "spo2", "temperature", "glucose", "potassium", "gcs"]

st.set_page_config(page_title="CRITICALCARE-TWIN", page_icon="T", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def load_profiles() -> list[PatientProfile]:
    path = ROOT / "data" / "metadata" / "observed_profiles.json"
    if not path.exists():
        st.error("Observed profiles are missing. Run `python scripts/download_data.py` and `python scripts/prepare_data.py`.")
        st.stop()
    return [PatientProfile.model_validate(x) for x in json.loads(path.read_text(encoding="utf-8"))]


def init_twin(profile: PatientProfile) -> None:
    repo = TwinRepository(ROOT / "data" / "criticalcare_twin.sqlite")
    repo.save_patient(profile)
    gateway = EdgeGateway(outbox_path=ROOT / "data" / "edge_outbox.sqlite")
    twin = PatientDigitalTwin(profile, repository=repo, edge_gateway=gateway)
    twin.ingest(Observation(patient_id=profile.patient_id, values=profile.baseline, quality={k: 0.82 for k in profile.baseline}, source=DataClass.OBSERVED))
    st.session_state.twin = twin
    st.session_state.ingestion_results = []


def ingest_frame(twin: PatientDigitalTwin, frame: pd.DataFrame) -> list[dict]:
    results = []
    for number, row in frame.iterrows():
        values = {name: float(row[name]) for name in MEASUREMENTS if name in row and pd.notna(row[name])}
        timestamp = pd.to_datetime(row.get("timestamp"), utc=True, errors="coerce")
        if pd.isna(timestamp):
            timestamp = datetime.now(timezone.utc)
        try:
            snapshot = twin.ingest(Observation(patient_id=twin.profile.patient_id, timestamp=timestamp.to_pydatetime() if hasattr(timestamp, "to_pydatetime") else timestamp, values=values, quality={k: 1.0 for k in values}, source=DataClass.OBSERVED))
            results.append({"row": int(number), "status": "accepted", "version": snapshot.twin_version, "timestamp": snapshot.timestamp})
        except ValueError as exc:
            results.append({"row": int(number), "status": "rejected", "reason": str(exc)})
    return results


profiles = load_profiles()
labels = [p.static_properties.get("display_label", f"Observed encounter {p.encounter_id or p.patient_id}") for p in profiles]
with st.sidebar:
    st.markdown('<div class="eyebrow">OBSERVED DATA / DIGITAL TWIN</div>', unsafe_allow_html=True)
    st.title("TWIN")
    selected = st.selectbox("Observed encounter", labels)
    profile = profiles[labels.index(selected)]
    if "twin" not in st.session_state or st.session_state.twin.profile.patient_id != profile.patient_id:
        init_twin(profile)
    page = st.radio("Workspace", PAGES)
    st.divider()
    st.caption("FIWARE ORION-LD · NGSI-LD · MINIO")
    st.caption("Outcome model: hospital_death")

twin = st.session_state.twin
st.markdown('<div class="eyebrow">PATIENT-SPECIFIC COMPUTATIONAL REPRESENTATION</div>', unsafe_allow_html=True)
st.title(page)
st.markdown(f'<div class="statusbar"><span class="statuspill">{twin.status}</span><span class="statuspill">{twin.twin_id}</span><span class="statuspill">VERSION {twin.twin_version}</span><span class="statuspill">SOURCE OBSERVED</span></div>', unsafe_allow_html=True)

if page == "Command Center":
    a, b, c, d = st.columns(4)
    a.metric("Hospital mortality estimate", f"{twin.risk_state.probability:.1%}", help="Dataset outcome estimate; not a diagnosis")
    b.metric("Anomaly state", twin.risk_state.anomaly_state.upper(), f"score {twin.risk_state.anomaly_score:.2f}")
    c.metric("State confidence", f"{twin.uncertainty.state_confidence:.0%}")
    d.metric("Data quality", f"{twin.uncertainty.data_quality_score:.0%}")
    left, right = st.columns([1.0, 1.8])
    with left:
        patient_visual(twin)
        st.info("This encounter baseline comes from the audited ICU dataset. No synthetic telemetry is generated.")
    with right:
        items = list(twin.current_state.parameters.items())
        for start in range(0, len(items), 3):
            cols = st.columns(3)
            for col, (name, parameter) in zip(cols, items[start:start + 3]):
                with col:
                    metric_card(name, parameter.raw_value, parameter.filtered_value, parameter.delta, parameter.trend, parameter.measurement_confidence, parameter.source.value)

elif page == "Observation Ingestion":
    st.subheader("Ingest observed measurements")
    st.write("Upload timestamped observations from a bedside export, device gateway, or EHR integration. Required measurement names are shown below; `timestamp` is recommended.")
    st.code("timestamp," + ",".join(MEASUREMENTS), language="text")
    uploaded = st.file_uploader("Observed CSV", type=["csv"])
    if uploaded is not None:
        frame = pd.read_csv(uploaded)
        st.dataframe(frame.head(20), width="stretch", hide_index=True)
        if st.button("Validate and synchronize observations", type="primary"):
            st.session_state.ingestion_results = ingest_frame(twin, frame)
    if st.session_state.ingestion_results:
        st.dataframe(pd.DataFrame(st.session_state.ingestion_results), width="stretch", hide_index=True)
    live_pipeline(twin)
    incoming, engine, outputs = st.columns([1.05, 0.9, 1.05])
    with incoming: live_signal_panel(twin)
    with engine: twin_engine_visual(twin)
    with outputs: analytics_panel(twin)
    event_console(twin.events.events, 10)

elif page == "State Explorer":
    variable = st.selectbox("State variable", list(twin.current_state.parameters))
    st.plotly_chart(state_history(twin, variable), width="stretch")
    previous = twin.previous_state.vector()
    rows = [{"Variable": name, "X(t-1)": previous.get(name), "Observation": p.raw_value, "X(t)": p.filtered_value, "Delta": p.delta, "Baseline": twin.profile.baseline.get(name), "Trend": p.trend, "Confidence": p.measurement_confidence, "Class": p.source.value} for name, p in twin.current_state.parameters.items()]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

elif page == "Risk & Explainability":
    a, b, c = st.columns(3)
    a.metric("Model-estimated hospital mortality", f"{twin.risk_state.probability:.1%}", twin.risk_state.label)
    b.metric("Patient-normalized anomaly", f"{twin.risk_state.anomaly_score:.2f}", twin.risk_state.anomaly_state)
    c.metric("Prediction confidence", f"{twin.risk_state.confidence:.0%}")
    contributions = pd.DataFrame(twin.model_outputs.get("contributions", []), columns=["Feature", "Relative contribution"])
    if not contributions.empty: st.bar_chart(contributions.set_index("Feature"))
    st.info(contribution_note())

elif page == "Digital Twin Platform":
    status = twin.edge_gateway.status()
    a, b, c, d = st.columns(4)
    a.metric("Orion-LD broker", "ONLINE" if status["orion_online"] else "OFFLINE")
    b.metric("MinIO object storage", "ONLINE" if status["storage_online"] else "OFFLINE")
    c.metric("Buffered at edge", status["queued"])
    d.metric("Platform-synced", status["synced"])
    if st.button("Flush edge buffer", disabled=not status["online"]):
        result = twin.edge_gateway.flush()
        st.success(f"Sent {result['sent']} messages; {result['remaining']} remain queued.")
    st.graphviz_chart('''digraph { rankdir=LR; node [shape=box style="rounded,filled" fillcolor="#10252c" color="#45d6c7" fontcolor="#e7f0f2"]; Source [label="Observed CSV / device / EHR"]; Edge [label="Edge validation + analytics"]; Queue [label="Offline outbox"]; Orion [label="FIWARE Orion-LD\nNGSI-LD entity graph"]; Mongo [label="MongoDB\ncurrent context"]; MinIO [label="MinIO\nimmutable JSON snapshots"]; Dashboard [label="Streamlit dashboard"]; Source -> Edge -> Queue -> Orion; Orion -> Mongo; Queue -> MinIO; Orion -> Dashboard; Edge -> Dashboard; }''', width="stretch")
    st.write(f"Framework: **{status['framework']}**  |  Storage: **{status['storage']}**  |  Broker: `{status['orion_url']}`")

elif page == "Evidence Lab":
    metadata = json.loads((ROOT / "models" / "hospital_mortality_metadata.json").read_text(encoding="utf-8"))
    results = [{"Model": name, "ROC-AUC": m["roc_auc"], "PR-AUC": m["pr_auc"], "Precision @ .25": m["precision_at_0.25"], "Recall @ .25": m["recall_at_0.25"], "Brier": m["brier"]} for name, m in metadata["candidates"].items()]
    st.dataframe(pd.DataFrame(results), width="stretch", hide_index=True)
    st.caption("Metrics are measured on the held-out encounter split. They are not edited or inflated.")
