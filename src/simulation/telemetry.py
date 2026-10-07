from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import yaml
from src.twin.state import DataClass, Observation, PatientProfile
from src.data.validation import BOUNDS

NOISE = {"heart_rate": 1.8, "systolic_bp": 2.5, "diastolic_bp": 1.8, "respiratory_rate": .7, "spo2": .35, "temperature": .08, "glucose": 3, "potassium": .05, "gcs": .12}


class SyntheticTelemetryEngine:
    """Creates reproducible DEMO telemetry around a real encounter profile; never training labels."""

    def __init__(self, config: str | Path | None = None, seed: int = 42) -> None:
        path = Path(config or Path(__file__).resolve().parents[2] / "config" / "scenarios.yaml")
        self.config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.seed = seed

    def generate(self, profile: PatientProfile, scenario: str = "Stable", steps: int = 24, start: datetime | None = None) -> list[Observation]:
        rng = np.random.default_rng(self.seed + int(profile.patient_id) % 10000)
        drift = self.config["scenarios"][scenario]["drift"]
        interval = self.config.get("interval_minutes", 5)
        start = start or datetime.now(timezone.utc).replace(second=0, microsecond=0)
        current = profile.baseline.copy()
        observations = []
        for step in range(steps):
            values = {}
            for name, base in current.items():
                change = float(drift.get(name, 0)) + float(rng.normal(0, NOISE.get(name, .1)))
                current[name] = current[name] + change
                low, high = BOUNDS.get(name, (-np.inf, np.inf))
                values[name] = float(np.clip(current[name], low, high))
            observations.append(Observation(patient_id=profile.patient_id, timestamp=start + timedelta(minutes=step * interval), values=values, quality={k: .88 for k in values}, source=DataClass.SIMULATED, scenario=scenario))
        return observations

