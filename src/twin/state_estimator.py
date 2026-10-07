from __future__ import annotations

import numpy as np
from .state import DataClass, Observation, ParameterState, PhysiologicalState


class StateEstimator:
    """Interpretable confidence-weighted exponential state estimator."""

    def __init__(self, history_window: int = 8) -> None:
        self.history_window = history_window

    def estimate(self, observation: Observation, previous: PhysiologicalState, history: list[PhysiologicalState]) -> PhysiologicalState:
        parameters: dict[str, ParameterState] = {}
        for name, raw in observation.values.items():
            if raw is None or not np.isfinite(raw):
                continue
            raw = float(raw)
            old = previous.parameters.get(name)
            confidence = float(np.clip(observation.quality.get(name, 0.9), 0.05, 1.0))
            alpha = 0.25 + 0.55 * confidence
            filtered = raw if old is None else alpha * raw + (1 - alpha) * old.filtered_value
            series = [s.parameters[name].filtered_value for s in history[-self.history_window:] if name in s.parameters] + [filtered]
            slope = float(np.polyfit(np.arange(len(series)), series, 1)[0]) if len(series) > 1 else 0.0
            scale = max(abs(float(np.mean(series))), 1.0)
            trend = "rising" if slope > 0.01 * scale else "falling" if slope < -0.01 * scale else "stable"
            parameters[name] = ParameterState(
                raw_value=raw, filtered_value=filtered,
                delta=0.0 if old is None else filtered - old.filtered_value,
                rolling_mean=float(np.mean(series)), rolling_std=float(np.std(series)),
                trend=trend, slope=slope, measurement_confidence=confidence,
                timestamp=observation.timestamp, source=observation.source,
            )
        for name, old in previous.parameters.items():
            if name not in parameters:
                retained = old.model_copy(deep=True)
                retained.measurement_confidence *= 0.92
                retained.source = DataClass.MODEL_ESTIMATED
                parameters[name] = retained
        return PhysiologicalState(timestamp=observation.timestamp, parameters=parameters)

