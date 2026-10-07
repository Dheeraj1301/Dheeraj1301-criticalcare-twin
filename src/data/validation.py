BOUNDS = {"heart_rate": (20, 250), "systolic_bp": (40, 260), "diastolic_bp": (20, 180), "respiratory_rate": (4, 80), "spo2": (50, 100), "temperature": (30, 43), "glucose": (20, 700), "potassium": (1.5, 9), "gcs": (3, 15)}


def validate_values(values: dict[str, float | None]) -> list[str]:
    errors = []
    for name, value in values.items():
        if value is not None and name in BOUNDS and not BOUNDS[name][0] <= value <= BOUNDS[name][1]:
            errors.append(f"{name}={value} outside configured demo bounds {BOUNDS[name]}")
    return errors

