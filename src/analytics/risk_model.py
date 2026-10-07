from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np


class HospitalMortalityRiskModel:
    target = "hospital_death"

    def __init__(self, artifact: str | Path | None = None) -> None:
        artifact = Path(artifact or Path(__file__).resolve().parents[2] / "models" / "hospital_mortality.joblib")
        self.bundle = joblib.load(artifact) if artifact.exists() else None

    def _row(self, state: dict[str, float], static: dict) -> dict[str, float]:
        row = {
            "age": static.get("age", np.nan), "bmi": static.get("bmi", np.nan),
            "heart_rate": state.get("heart_rate", np.nan), "systolic_bp": state.get("systolic_bp", np.nan),
            "diastolic_bp": state.get("diastolic_bp", np.nan), "respiratory_rate": state.get("respiratory_rate", np.nan),
            "spo2": state.get("spo2", np.nan), "temperature": state.get("temperature", np.nan),
            "glucose": state.get("glucose", np.nan), "potassium": state.get("potassium", np.nan),
            "gcs": state.get("gcs", np.nan), "elective_surgery": static.get("elective_surgery", 0),
            "ventilated": static.get("ventilated", 0), "intubated": static.get("intubated", 0),
        }
        return {k: (np.nan if v is None else v) for k, v in row.items()}

    def predict(self, state: dict[str, float], static: dict) -> tuple[float, list[tuple[str, float]]]:
        row = self._row(state, static)
        if self.bundle is None:
            # Explicitly labelled fallback heuristic keeps the twin demonstrable before model training.
            terms = {
                "heart_rate": max(0, abs(row["heart_rate"] - 80) - 25) / 50 if np.isfinite(row["heart_rate"]) else 0,
                "spo2": max(0, 94 - row["spo2"]) / 20 if np.isfinite(row["spo2"]) else 0,
                "systolic_bp": max(0, 95 - row["systolic_bp"]) / 50 if np.isfinite(row["systolic_bp"]) else 0,
                "respiratory_rate": max(0, row["respiratory_rate"] - 22) / 25 if np.isfinite(row["respiratory_rate"]) else 0,
                "gcs": max(0, 15 - row["gcs"]) / 12 if np.isfinite(row["gcs"]) else 0,
            }
            probability = float(np.clip(0.03 + .22 * sum(terms.values()), .01, .95))
            return probability, sorted(terms.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        import pandas as pd
        frame = pd.DataFrame([row], columns=self.bundle["features"])
        probability = float(self.bundle["model"].predict_proba(frame)[0, 1])
        explanation = self.explain(frame.iloc[0].to_dict())
        return probability, explanation

    def explain(self, row: dict[str, float]) -> list[tuple[str, float]]:
        if not self.bundle:
            return []
        importance = self.bundle.get("feature_importance", {})
        medians = self.bundle.get("medians", {})
        contributions = []
        for name, value in row.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if np.isfinite(numeric):
                median = float(medians.get(name, numeric))
                contributions.append((name, float(importance.get(name, 0)) * abs(numeric - median) / max(abs(median), 1)))
        return sorted(contributions, key=lambda x: x[1], reverse=True)[:5]
