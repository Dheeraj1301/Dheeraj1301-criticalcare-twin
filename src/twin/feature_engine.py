from __future__ import annotations

import numpy as np
from .state import PhysiologicalState

EXPECTED_SD = {"heart_rate": 15, "systolic_bp": 20, "diastolic_bp": 12, "respiratory_rate": 5, "spo2": 3, "temperature": 0.8, "glucose": 40, "potassium": 0.6, "gcs": 2}


class FeatureEngine:
    def compute(self, state: PhysiologicalState, baseline: dict[str, float], expected_count: int = 9) -> dict[str, float]:
        x = state.vector()
        features: dict[str, float] = {}
        if "systolic_bp" in x and "diastolic_bp" in x:
            features["mean_arterial_pressure"] = (x["systolic_bp"] + 2 * x["diastolic_bp"]) / 3
            features["pulse_pressure"] = x["systolic_bp"] - x["diastolic_bp"]
        if x.get("systolic_bp", 0) > 0 and "heart_rate" in x:
            features["shock_index_proxy"] = x["heart_rate"] / x["systolic_bp"]
        deviations = []
        for name, value in x.items():
            features[f"current_{name}"] = value
            if name in baseline:
                delta = value - baseline[name]
                features[f"deviation_{name}"] = delta
                features[f"normalized_deviation_{name}"] = delta / EXPECTED_SD.get(name, max(abs(baseline[name]) * .1, 1))
                deviations.append(abs(features[f"normalized_deviation_{name}"]))
            parameter = state.parameters[name]
            features[f"slope_{name}"] = parameter.slope
            features[f"volatility_{name}"] = parameter.rolling_std
        features["missingness_score"] = max(0.0, 1 - len(x) / expected_count)
        features["physiological_instability_index"] = float(np.mean(deviations)) if deviations else 0.0
        return features

