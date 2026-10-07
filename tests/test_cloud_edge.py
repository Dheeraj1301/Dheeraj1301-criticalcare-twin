from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.cloud import service
from src.edge.gateway import EdgeGateway
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import Observation, PatientProfile


def test_cloud_accepts_pseudonymous_twin_and_reports_fleet(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "DB_PATH", tmp_path / "cloud.sqlite")
    client = TestClient(service.app)
    payload = {
        "message_id": "M1", "site_id": "EDGE-1", "patient_key": "abcdef1234567890",
        "twin_id": "T1", "twin_version": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": {"heart_rate": 88}, "derived_state": {}, "risk": {"probability": .1},
        "uncertainty": {"state_confidence": .9}, "provenance_class": "SIMULATED",
    }
    assert client.post("/v1/twins/sync", json=payload).status_code == 202
    assert client.get("/v1/twins/abcdef1234567890/latest").json()["twin_version"] == 1
    assert client.get("/v1/fleet/summary").json() == {"snapshots": 1, "pseudonymous_patients": 1, "edge_sites": 1}


def test_edge_buffers_offline_without_raw_patient_id(tmp_path, monkeypatch):
    gateway = EdgeGateway(cloud_url="http://127.0.0.1:1", outbox_path=tmp_path / "edge.sqlite")
    profile = PatientProfile(patient_id="REAL-PATIENT-ID", baseline={"heart_rate": 80})
    twin = PatientDigitalTwin(profile)
    twin.ingest(Observation(patient_id=profile.patient_id, values={"heart_rate": 82}))
    snapshot = twin.snapshot()
    assert gateway.publish(twin, snapshot) is False
    assert gateway.status()["queued"] == 1
    with gateway.connect() as db:
        payload_json = db.execute("SELECT payload_json FROM outbox").fetchone()[0]
    assert "REAL-PATIENT-ID" not in payload_json
    assert gateway.patient_key("REAL-PATIENT-ID") in payload_json

