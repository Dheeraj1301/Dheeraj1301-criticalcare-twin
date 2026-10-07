from __future__ import annotations
import html
import streamlit as st

UNITS = {"heart_rate":"bpm", "systolic_bp":"mmHg", "diastolic_bp":"mmHg", "respiratory_rate":"/min", "spo2":"%", "temperature":"°C", "glucose":"mg/dL", "potassium":"mmol/L", "gcs":"points", "mean_arterial_pressure":"mmHg", "pulse_pressure":"mmHg", "shock_index_proxy":"ratio"}


def metric_card(name, observed, estimated, delta=0, trend="stable", confidence=0, source="ESTIMATED"):
    unit = UNITS.get(name, "")
    st.markdown(f"""<div class="metric-card"><div class="metric-name">{html.escape(name.replace('_',' '))}</div><div class="metric-value">{estimated:.1f} <small>{unit}</small></div><div class="metric-meta">Observed {observed:.1f} · Δ {delta:+.2f}<br>{trend.upper()} · conf {confidence:.0%}<br><span class="badge">{source}</span></div></div>""", unsafe_allow_html=True)


def lifecycle():
    stages = ["PATIENT / SOURCE", "OBSERVATION", "VALIDATION", "SYNCHRONIZER", "STATE ESTIMATOR", "STATE VECTOR", "RISK + ANOMALY", "FORECAST", "SNAPSHOT"]
    st.markdown('<div class="flow">' + '<span class="flow-arrow">→</span>'.join(f'<span class="flow-node">{x}</span>' for x in stages) + '</div>', unsafe_allow_html=True)


def live_pipeline(twin):
    """Compact lifecycle indicator driven by the latest emitted event."""
    stages = [
        ("OBSERVATION", {"OBSERVATION_RECEIVED"}),
        ("VALIDATION", {"OBSERVATION_VALIDATED"}),
        ("STATE ESTIMATE", {"STATE_UPDATED"}),
        ("RISK + ANOMALY", {"RISK_CHANGED", "ANOMALY_DETECTED"}),
        ("FORECAST", {"FORECAST_UPDATED"}),
        ("SNAPSHOT", {"SNAPSHOT_CREATED"}),
    ]
    latest = twin.events.events[-1].event_type if twin.events.events else ""
    active = next((i for i, (_, event_types) in enumerate(stages) if latest in event_types), len(stages) - 1)
    blocks = []
    for i, (label, _) in enumerate(stages):
        cls = "active" if i == active else "done" if i < active else ""
        blocks.append(f'<div class="live-stage {cls}"><span class="stage-num">0{i+1}</span>{label}</div>')
    st.markdown('<div class="live-flow">' + ''.join(blocks) + '</div>', unsafe_allow_html=True)


def live_signal_panel(twin):
    params = list(twin.current_state.parameters.items())[:6]
    rows = ''.join(
        f'<div class="signal-row"><span>{name.replace("_", " ").upper()}</span><span class="signal-value">{p.raw_value:.1f}</span><span class="signal-delta">{p.delta:+.2f}</span></div>'
        for name, p in params
    )
    st.markdown(f'<div class="signal-panel"><div class="signal-title">INCOMING DATA PACKET · {len(params)} CHANNELS</div>{rows}</div>', unsafe_allow_html=True)


def twin_engine_visual(twin):
    st.markdown(f'''<div class="signal-panel"><div class="signal-title">DIGITAL TWIN ENGINE</div>
    <div class="engine-core"><div class="label">SYNCHRONIZED STATE</div><div class="version">X<sub>{twin.twin_version}</sub></div><div class="label">CONF {twin.uncertainty.state_confidence:.0%}</div></div>
    <div style="text-align:center;color:#789098;font:.65rem monospace">X(t−1) → FILTER → X(t) → ΔX</div></div>''', unsafe_allow_html=True)


def analytics_panel(twin):
    st.markdown(f'''<div class="signal-panel"><div class="signal-title">ATTACHED ANALYTICS</div>
    <div class="output-chip"><span>HOSPITAL-DEATH MODEL</span><strong>{twin.risk_state.probability:.1%}</strong></div>
    <div class="output-chip"><span>ANOMALY</span><strong>{twin.risk_state.anomaly_state.upper()} · {twin.risk_state.anomaly_score:.2f}</strong></div>
    <div class="output-chip"><span>FORECAST</span><strong>{len(twin.forecast_outputs)} STEPS</strong></div>
    <div class="output-chip"><span>DATA QUALITY</span><strong>{twin.uncertainty.data_quality_score:.0%}</strong></div></div>''', unsafe_allow_html=True)


def event_console(events, limit=16):
    for event in events[-limit:][::-1]:
        latency = event.payload.get("latency_ms")
        extra = f" · {latency:.1f} ms" if latency else ""
        st.markdown(f'<div class="event">{event.timestamp:%H:%M:%S} &nbsp; {event.event_type}{extra}</div>', unsafe_allow_html=True)


def patient_visual(twin):
    x = twin.current_state.vector()
    def v(k): return f"{x.get(k, 0):.1f}"
    st.markdown(f"""<svg viewBox="0 0 700 430" style="width:100%;background:#0a171d;border:1px solid #20343d;border-radius:12px">
    <defs><filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <g stroke="#244854" stroke-width="2" fill="none"><line x1="260" y1="90" x2="105" y2="70"/><line x1="235" y1="170" x2="100" y2="185"/><line x1="250" y1="280" x2="110" y2="330"/><line x1="440" y1="90" x2="590" y2="70"/><line x1="465" y1="170" x2="600" y2="185"/><line x1="450" y1="280" x2="590" y2="330"/></g>
    <g fill="#12313a" stroke="#45d6c7" stroke-width="2"><circle cx="350" cy="65" r="38"/><path d="M300 120 Q350 95 400 120 L425 250 L395 260 L390 400 L345 400 L350 270 L340 270 L305 400 L260 400 L280 250 Z"/></g>
    <g fill="#45d6c7" filter="url(#glow)"><circle cx="350" cy="150" r="8"/><circle cx="350" cy="210" r="7"/><circle cx="350" cy="320" r="6"/></g>
    <g font-family="monospace"><g fill="#91a7ae" font-size="13"><text x="35" y="55">HEART RATE</text><text x="35" y="170">PRESSURE</text><text x="35" y="315">TEMPERATURE</text><text x="555" y="55">SpO₂</text><text x="555" y="170">RESP RATE</text><text x="555" y="315">GCS</text></g>
    <g fill="#e7f0f2" font-size="22" font-weight="700"><text x="35" y="82">{v('heart_rate')}</text><text x="35" y="197">{v('systolic_bp')}/{v('diastolic_bp')}</text><text x="35" y="342">{v('temperature')}</text><text x="555" y="82">{v('spo2')}%</text><text x="555" y="197">{v('respiratory_rate')}</text><text x="555" y="342">{v('gcs')}</text></g></g></svg>""", unsafe_allow_html=True)
