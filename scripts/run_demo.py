"""Prepare deterministic demo assets, execute a headless lifecycle smoke test, then optionally launch Streamlit."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulation.scenario_engine import ScenarioEngine
from src.simulation.telemetry import SyntheticTelemetryEngine
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import PatientProfile, SimulationScenario


def smoke() -> None:
    profiles_path = ROOT / "data" / "metadata" / "demo_profiles.json"
    if not profiles_path.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "prepare_data.py")], check=True, cwd=ROOT)
    profile = PatientProfile.model_validate(json.loads(profiles_path.read_text(encoding="utf-8"))[1])
    twin = PatientDigitalTwin(profile)
    stream = SyntheticTelemetryEngine().generate(profile, "Respiratory deterioration", 6)
    for obs in stream: twin.ingest(obs)
    before = twin.current_state.model_dump_json()
    result = ScenarioEngine().run(twin, SimulationScenario(name="smoke", perturbations={"spo2": -5}, horizon=3))
    assert result.original_unchanged and before == twin.current_state.model_dump_json()
    assert twin.twin_version == 6 and twin.forecast_outputs and twin.events.events
    print(f"Smoke test passed: {twin.twin_id}, version={twin.twin_version}, events={len(twin.events.events)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--launch", action="store_true", help="Launch Streamlit after the smoke test")
    args = parser.parse_args()
    smoke()
    if args.launch:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py")], check=True, cwd=ROOT)

