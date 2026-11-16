"""End-to-end verification against live Orion-LD and MinIO services."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.edge.gateway import EdgeGateway
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.state import Observation, PatientProfile


def main() -> int:
    gateway = EdgeGateway(outbox_path=ROOT / "data" / "platform_verification.sqlite")
    before = gateway.status()
    if not before["online"]:
        print(json.dumps({"passed": False, "reason": "platform offline", "status": before}, indent=2))
        return 1
    profile = PatientProfile(patient_id="PLATFORM-VERIFICATION", encounter_id="VERIFY-1", baseline={"heart_rate": 80, "systolic_bp": 120, "diastolic_bp": 70, "spo2": 98})
    twin = PatientDigitalTwin(profile, edge_gateway=gateway)
    snapshot = twin.ingest(Observation(patient_id=profile.patient_id, values=profile.baseline))
    patient_key = gateway.patient_key(profile.patient_id)
    entity = gateway.orion.get(patient_key)
    after = gateway.status()
    result = {"passed": entity["id"].endswith(patient_key) and after["synced"] >= 1, "entity_id": entity["id"], "twin_version": snapshot.twin_version, "orion_online": after["orion_online"], "storage_online": after["storage_online"], "synced": after["synced"]}
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
