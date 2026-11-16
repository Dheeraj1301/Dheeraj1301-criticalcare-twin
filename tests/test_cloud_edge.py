import json

from src.cloud.orion import OrionDigitalTwinClient
from src.edge.gateway import EdgeGateway
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import Observation, PatientProfile


class FakeOrion:
    def __init__(self, online=True): self.available = online; self.payloads = []
    def upsert(self, payload):
        if not self.available: raise ConnectionError("broker unavailable")
        self.payloads.append(payload)
        return OrionDigitalTwinClient.entity_id(payload["patient_key"])
    def online(self): return self.available


class FakeStore:
    def __init__(self, online=True): self.available = online; self.objects = []
    def archive(self, patient_key, version, payload):
        if not self.available: raise ConnectionError("storage unavailable")
        key = f"twins/{patient_key}/v{version:08d}.json"
        self.objects.append((key, payload))
        return key
    def online(self): return self.available


def snapshot():
    profile = PatientProfile(patient_id="REAL-PATIENT-ID", baseline={"heart_rate": 80})
    twin = PatientDigitalTwin(profile)
    snap = twin.ingest(Observation(patient_id=profile.patient_id, values={"heart_rate": 82}))
    return twin, snap


def test_gateway_sends_ngsi_entity_and_archives_without_patient_id(tmp_path):
    orion, store = FakeOrion(), FakeStore()
    gateway = EdgeGateway(outbox_path=tmp_path / "edge.sqlite", orion_client=orion, object_store=store)
    twin, snap = snapshot()
    assert gateway.publish(twin, snap) is True
    payload = orion.payloads[0]
    assert "REAL-PATIENT-ID" not in json.dumps(payload)
    assert payload["provenance_class"] == "OBSERVED_OR_MODEL_ESTIMATED"
    assert store.objects[0][0].startswith(f"twins/{gateway.patient_key('REAL-PATIENT-ID')}/")
    assert gateway.status()["synced"] == 1


def test_offline_buffer_flushes_when_platform_recovers(tmp_path):
    orion, store = FakeOrion(False), FakeStore()
    gateway = EdgeGateway(outbox_path=tmp_path / "edge.sqlite", orion_client=orion, object_store=store)
    twin, snap = snapshot()
    assert gateway.publish(twin, snap) is False
    assert gateway.status()["queued"] == 1
    orion.available = True
    assert gateway.flush() == {"sent": 1, "remaining": 0}


def test_orion_entity_is_valid_ngsi_ld_shape():
    payload = {"patient_key": "abc123", "twin_id": "TWIN-1", "twin_version": 3, "site_id": "EDGE-01", "timestamp": "2026-01-01T00:00:00Z", "state": {"heart_rate": 90}, "risk": {"probability": .2}, "uncertainty": {"state_confidence": .9}}
    entity = OrionDigitalTwinClient().entity(payload)
    assert entity["id"] == "urn:ngsi-ld:CriticalCareTwin:abc123"
    assert entity["heart_rate"]["type"] == "Property"
    assert entity["heart_rate"]["value"] == 90
