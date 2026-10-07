from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from src.twin.state import PatientProfile
from .preprocessing import midpoint


class ICUEncounterAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.path)

    def profile_from_row(self, row: pd.Series) -> PatientProfile:
        gcs_parts = [row.get("gcs_eyes_apache"), row.get("gcs_motor_apache"), row.get("gcs_verbal_apache")]
        gcs = sum(float(v) for v in gcs_parts if pd.notna(v)) if all(pd.notna(v) for v in gcs_parts) else 15.0
        baseline = {
            "heart_rate": midpoint(row.get("h1_heartrate_min"), row.get("h1_heartrate_max"), row.get("heart_rate_apache")),
            "systolic_bp": midpoint(row.get("h1_sysbp_min"), row.get("h1_sysbp_max"), 120),
            "diastolic_bp": midpoint(row.get("h1_diasbp_min"), row.get("h1_diasbp_max"), 70),
            "respiratory_rate": midpoint(row.get("h1_resprate_min"), row.get("h1_resprate_max"), row.get("resprate_apache")),
            "spo2": midpoint(row.get("h1_spo2_min"), row.get("h1_spo2_max"), 97),
            "temperature": midpoint(row.get("d1_temp_min"), row.get("d1_temp_max"), row.get("temp_apache")),
            "glucose": midpoint(row.get("d1_glucose_min"), row.get("d1_glucose_max"), 110),
            "potassium": midpoint(row.get("d1_potassium_min"), row.get("d1_potassium_max"), 4),
            "gcs": gcs,
        }
        baseline = {k: float(v) for k, v in baseline.items() if v is not None and np.isfinite(v)}
        static = {k: row.get(k) for k in ["bmi", "elective_surgery", "ventilated_apache", "intubated_apache", "icu_type", "apache_3j_bodysystem"]}
        static = {k.replace("_apache", ""): (v.item() if hasattr(v, "item") else v) for k, v in static.items() if pd.notna(v)}
        return PatientProfile(
            patient_id=str(int(row.patient_id)), encounter_id=str(int(row.encounter_id)),
            age=float(row.age) if pd.notna(row.age) else None, gender=str(row.gender) if pd.notna(row.gender) else None,
            ethnicity=str(row.ethnicity) if pd.notna(row.ethnicity) else None, static_properties=static,
            baseline=baseline, provenance={k: "OBSERVED: patient/dataset.csv encounter summary" for k in baseline},
        )

    def demo_profiles(self) -> list[PatientProfile]:
        df = self.load()
        complete = df.dropna(subset=["h1_heartrate_min", "h1_sysbp_min", "h1_diasbp_min", "h1_resprate_min", "h1_spo2_min", "d1_temp_min"])
        candidates = [complete[complete.hospital_death == 0].iloc[0], complete[complete.hospital_death == 0].iloc[len(complete)//3], complete.iloc[-1]]
        profiles = [self.profile_from_row(r) for r in candidates]
        for profile, label in zip(profiles, ["PATIENT A — Stable", "PATIENT B — Gradual deterioration", "PATIENT C — Acute simulated instability"]):
            profile.static_properties["demo_label"] = label
        return profiles

