from datetime import datetime, timezone
from src.twin.patient_twin import PatientDigitalTwin
from src.twin.repository import TwinRepository
from src.twin.state import Observation, PatientProfile


def test_sqlite_persistence(tmp_path):
    repo = TwinRepository(tmp_path / "twin.sqlite")
    profile = PatientProfile(patient_id="PX", baseline={"heart_rate":80})
    repo.save_patient(profile)
    twin = PatientDigitalTwin(profile, repository=repo)
    twin.ingest(Observation(patient_id="PX", timestamp=datetime(2026,1,1,tzinfo=timezone.utc), values={"heart_rate":82}))
    counts = repo.counts()
    assert counts["patients"] == 1 and counts["observations"] == 1 and counts["twin_snapshots"] == 1
    assert repo.snapshots(twin.twin_id)[0].state.parameters["heart_rate"].filtered_value == 82

