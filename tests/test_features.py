import pytest
from src.twin.feature_engine import FeatureEngine
from src.twin.state import DataClass, ParameterState, PhysiologicalState, utcnow


def p(value):
    return ParameterState(raw_value=value, filtered_value=value, rolling_mean=value, timestamp=utcnow(), source=DataClass.OBSERVED)


def test_transparent_derived_features():
    state = PhysiologicalState(parameters={"heart_rate":p(100),"systolic_bp":p(120),"diastolic_bp":p(60)})
    f = FeatureEngine().compute(state, {"heart_rate":80,"systolic_bp":120,"diastolic_bp":70}, expected_count=3)
    assert f["mean_arterial_pressure"] == pytest.approx(80)
    assert f["pulse_pressure"] == 60
    assert f["shock_index_proxy"] == pytest.approx(100/120)

