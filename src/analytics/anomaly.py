from __future__ import annotations

import numpy as np

SCALES = {"heart_rate": 15, "systolic_bp": 20, "diastolic_bp": 12, "respiratory_rate": 5, "spo2": 3, "temperature": .8, "glucose": 40, "potassium": .6, "gcs": 2}


class TransparentAnomalyDetector:
    """Patient-normalized multivariate deviation detector; prototype metric, not clinical score."""

    def score(self, current: dict[str, float], baseline: dict[str, float]) -> tuple[float, str, list[str]]:
        deviations = {k: abs(current[k] - baseline[k]) / SCALES.get(k, max(abs(baseline[k]) * .1, 1)) for k in current.keys() & baseline.keys()}
        if not deviations:
            return 0.0, "insufficient data", []
        ordered = sorted(deviations, key=deviations.get, reverse=True)
        raw = .6 * max(deviations.values()) + .4 * float(np.mean(list(deviations.values())))
        score = float(1 - np.exp(-raw / 2))
        return score, "abnormal" if score >= .55 else "watch" if score >= .35 else "normal", ordered[:3]

