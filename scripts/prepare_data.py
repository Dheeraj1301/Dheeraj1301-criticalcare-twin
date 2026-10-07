"""Create the audited ICU modeling table and demo profile metadata."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.adapters import ICUEncounterAdapter
SOURCE = ROOT / "data" / "raw" / "patient" / "dataset.csv"
OUT = ROOT / "data" / "processed" / "icu_model_table.csv"
META = ROOT / "data" / "metadata"


def average(df, low, high, fallback=None):
    result = df[[low, high]].mean(axis=1)
    return result.fillna(df[fallback]) if fallback else result


def main() -> None:
    df = pd.read_csv(SOURCE)
    model = pd.DataFrame({
        "age": df.age, "bmi": df.bmi,
        "heart_rate": average(df, "h1_heartrate_min", "h1_heartrate_max", "heart_rate_apache"),
        "systolic_bp": average(df, "h1_sysbp_min", "h1_sysbp_max"),
        "diastolic_bp": average(df, "h1_diasbp_min", "h1_diasbp_max"),
        "respiratory_rate": average(df, "h1_resprate_min", "h1_resprate_max", "resprate_apache"),
        "spo2": average(df, "h1_spo2_min", "h1_spo2_max"),
        "temperature": average(df, "d1_temp_min", "d1_temp_max", "temp_apache"),
        "glucose": average(df, "d1_glucose_min", "d1_glucose_max"),
        "potassium": average(df, "d1_potassium_min", "d1_potassium_max"),
        "gcs": df[["gcs_eyes_apache", "gcs_motor_apache", "gcs_verbal_apache"]].sum(axis=1, min_count=3),
        "elective_surgery": df.elective_surgery,
        "ventilated": df.ventilated_apache,
        "intubated": df.intubated_apache,
        "hospital_death": df.hospital_death,
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    model.to_csv(OUT, index=False)
    adapter = ICUEncounterAdapter(SOURCE)
    profiles = [p.model_dump(mode="json") for p in adapter.demo_profiles()]
    META.mkdir(parents=True, exist_ok=True)
    (META / "demo_profiles.json").write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    provenance = {
        "source_dataset": "mitishaagarwal/patient", "source_file": "data/raw/patient/dataset.csv",
        "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        "original_columns": list(df.columns), "renamed_columns": {},
        "transformations": "First-hour min/max midpoints; first-day lab/temperature midpoints; GCS component sum.",
        "missing_value_strategy": "Values remain missing in the processed table; model pipelines median-impute within training folds.",
        "derived_features": ["heart_rate", "systolic_bp", "diastolic_bp", "respiratory_rate", "spo2", "temperature", "glucose", "potassium", "gcs"],
        "synthetic_fields": [], "limitations": "Encounter-level summaries are not a timestamped physiological sequence."
    }
    (META / "icu_model_table.provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}: {model.shape}")


if __name__ == "__main__": main()
