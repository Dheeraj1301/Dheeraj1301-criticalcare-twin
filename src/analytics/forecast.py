from __future__ import annotations

from datetime import timedelta
import numpy as np
from src.twin.state import PhysiologicalState


BOUNDS = {"heart_rate": (20, 250), "systolic_bp": (40, 260), "diastolic_bp": (20, 180), "respiratory_rate": (4, 80), "spo2": (50, 100), "temperature": (30, 43), "glucose": (20, 700), "potassium": (1.5, 9), "gcs": (3, 15)}


class TrajectoryForecaster:
    """Transparent local-linear forecast for demonstration only."""

    def forecast(self, history: list[PhysiologicalState], current: PhysiologicalState, steps: int = 6, interval_minutes: int = 5) -> list[dict]:
        if not current.timestamp:
            return []
        output = []
        for step in range(1, steps + 1):
            row = {"timestamp": current.timestamp + timedelta(minutes=step * interval_minutes), "step": step}
            for name, param in current.parameters.items():
                vals = [s.parameters[name].filtered_value for s in history[-8:] if name in s.parameters] + [param.filtered_value]
                slope = float(np.polyfit(np.arange(len(vals)), vals, 1)[0]) if len(vals) > 1 else 0.0
                value = param.filtered_value + slope * step
                low_bound, high_bound = BOUNDS.get(name, (-np.inf, np.inf))
                value = float(np.clip(value, low_bound, high_bound))
                uncertainty = max(float(np.std(vals)), abs(slope), 0.01) * np.sqrt(step)
                row[name] = value
                row[f"{name}_lower"] = float(np.clip(value - 1.64 * uncertainty, low_bound, high_bound))
                row[f"{name}_upper"] = float(np.clip(value + 1.64 * uncertainty, low_bound, high_bound))
            output.append(row)
        return output

