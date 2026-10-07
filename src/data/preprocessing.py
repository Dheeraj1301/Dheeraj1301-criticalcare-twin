from __future__ import annotations
import math


def midpoint(low, high, fallback=None):
    values = [float(v) for v in (low, high) if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return sum(values) / len(values) if values else fallback

