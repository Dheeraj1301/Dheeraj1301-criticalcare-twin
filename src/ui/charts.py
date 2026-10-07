from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go

COLORS = {"raw":"#8ea6ad", "filtered":"#45d6c7", "baseline":"#ffbd59", "scenario":"#ff6376"}


def state_history(twin, variable):
    rows = []
    for state in twin.state_history:
        if variable in state.parameters:
            p = state.parameters[variable]
            rows.append({"timestamp": state.timestamp, "raw": p.raw_value, "filtered": p.filtered_value})
    fig = go.Figure()
    if rows:
        df = pd.DataFrame(rows)
        fig.add_trace(go.Scatter(x=df.timestamp, y=df.raw, name="Raw sensor", line=dict(color=COLORS["raw"], dash="dot")))
        fig.add_trace(go.Scatter(x=df.timestamp, y=df.filtered, name="Filtered twin", line=dict(color=COLORS["filtered"], width=3)))
        fig.add_hline(y=twin.profile.baseline.get(variable, 0), line_color=COLORS["baseline"], annotation_text="Patient baseline")
    forecast = twin.forecast_outputs
    if forecast and variable in forecast[0]:
        fig.add_trace(go.Scatter(x=[r["timestamp"] for r in forecast], y=[r[variable] for r in forecast], name="Prototype forecast", line=dict(color="#68a5ff", dash="dash")))
        fig.add_trace(go.Scatter(x=[r["timestamp"] for r in forecast] + [r["timestamp"] for r in forecast][::-1], y=[r[f"{variable}_upper"] for r in forecast] + [r[f"{variable}_lower"] for r in forecast][::-1], fill="toself", fillcolor="rgba(104,165,255,.12)", line=dict(color="rgba(0,0,0,0)"), name="Forecast band"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a171d", plot_bgcolor="#0a171d", margin=dict(l=20,r=20,t=35,b=20), height=360, legend=dict(orientation="h"))
    return fig


def scenario_comparison(result, variable):
    base, scen = pd.DataFrame(result.baseline_trajectory), pd.DataFrame(result.scenario_trajectory)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=base.step, y=base[variable], name="Baseline clone", line=dict(color=COLORS["filtered"], width=3)))
    fig.add_trace(go.Scatter(x=scen.step, y=scen[variable], name="Scenario clone", line=dict(color=COLORS["scenario"], width=3)))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a171d", plot_bgcolor="#0a171d", xaxis_title="Simulation step", height=370, margin=dict(l=20,r=20,t=30,b=20))
    return fig

