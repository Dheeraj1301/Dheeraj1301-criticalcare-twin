from __future__ import annotations

import numpy as np
from .state import DataClass, PhysiologicalState, UncertaintyState


def estimate_uncertainty(state: PhysiologicalState, expected_count: int = 9, forecast_horizon: int = 6) -> UncertaintyState:
    params = list(state.parameters.values())
    missing = max(0.0, 1 - len(params) / expected_count)
    simulated = sum(p.source == DataClass.SIMULATED for p in params) / max(len(params), 1)
    confidence = float(np.mean([p.measurement_confidence for p in params])) if params else 0.0
    data_quality = float(np.clip(confidence * (1 - 0.7 * missing) * (1 - 0.2 * simulated), 0, 1))
    return UncertaintyState(
        data_quality_score=data_quality,
        state_confidence=float(np.clip(confidence * (1 - missing), 0, 1)),
        prediction_confidence=float(np.clip(data_quality * 0.9, 0, 1)),
        forecast_uncertainty=float(np.clip((1 - confidence) + 0.025 * forecast_horizon + 0.2 * simulated, 0, 1)),
        missing_fraction=missing, simulated_fraction=simulated,
    )

