from datetime import datetime, timezone
from src.simulation.scenario_engine import ScenarioEngine
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import Observation, PatientProfile, SimulationScenario


def test_scenario_isolation_critical():
    profile = PatientProfile(patient_id="P2", baseline={"heart_rate":80,"systolic_bp":120,"diastolic_bp":70,"respiratory_rate":16,"spo2":97,"temperature":37,"glucose":110,"potassium":4,"gcs":15})
    twin = PatientDigitalTwin(profile)
    twin.ingest(Observation(patient_id="P2", timestamp=datetime(2026,1,1,tzinfo=timezone.utc), values=profile.baseline))
    before = twin.current_state.model_dump_json()
    result = ScenarioEngine().run(twin, SimulationScenario(name="oxygen drop", perturbations={"spo2":-5}, horizon=4))
    assert result.original_unchanged
    assert twin.current_state.model_dump_json() == before
    assert result.scenario_trajectory[-1]["spo2"] < result.baseline_trajectory[-1]["spo2"]

