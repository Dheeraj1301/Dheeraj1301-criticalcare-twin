from datetime import datetime, timedelta, timezone
import pytest
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import Observation, PatientProfile


@pytest.fixture
def profile():
    return PatientProfile(patient_id="P1", age=62, static_properties={"bmi":27}, baseline={"heart_rate":80,"systolic_bp":120,"diastolic_bp":70,"respiratory_rate":16,"spo2":97,"temperature":37,"glucose":110,"potassium":4,"gcs":15})


def obs(profile, minute=0, **changes):
    values = {**profile.baseline, **changes}
    return Observation(patient_id=profile.patient_id, timestamp=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=minute), values=values)


def test_initialization(profile):
    twin = PatientDigitalTwin(profile)
    assert twin.profile.patient_id == "P1" and twin.twin_version == 0


def test_observation_updates_state_and_history(profile):
    twin = PatientDigitalTwin(profile); twin.ingest(obs(profile))
    twin.ingest(obs(profile, 5, heart_rate=100))
    assert twin.twin_version == 2 and len(twin.state_history) == 2
    assert 80 < twin.current_state.parameters["heart_rate"].filtered_value < 100
    assert twin.previous_state.parameters["heart_rate"].filtered_value == 80


def test_invalid_observations(profile):
    twin = PatientDigitalTwin(profile)
    with pytest.raises(ValueError): twin.ingest(Observation(patient_id="wrong", values={"heart_rate":80}))
    with pytest.raises(ValueError): twin.ingest(Observation(patient_id="P1", values={"spo2":120}))


def test_events_generated(profile):
    twin = PatientDigitalTwin(profile); twin.ingest(obs(profile))
    types = {e.event_type for e in twin.events.events}
    assert {"OBSERVATION_RECEIVED","STATE_UPDATED","RISK_CHANGED","FORECAST_UPDATED","SNAPSHOT_CREATED"} <= types

