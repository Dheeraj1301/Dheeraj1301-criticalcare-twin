from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DataClass(StrEnum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    MODEL_ESTIMATED = "MODEL_ESTIMATED"
    SIMULATED = "SIMULATED"


class PatientProfile(BaseModel):
    patient_id: str
    encounter_id: str | None = None
    age: float | None = None
    gender: str | None = None
    ethnicity: str | None = None
    static_properties: dict[str, Any] = Field(default_factory=dict)
    baseline: dict[str, float] = Field(default_factory=dict)
    provenance: dict[str, str] = Field(default_factory=dict)


class Observation(BaseModel):
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    patient_id: str
    timestamp: datetime = Field(default_factory=utcnow)
    values: dict[str, float | None]
    quality: dict[str, float] = Field(default_factory=dict)
    source: DataClass = DataClass.OBSERVED
    scenario: str | None = None


class ParameterState(BaseModel):
    raw_value: float
    filtered_value: float
    delta: float = 0.0
    rolling_mean: float
    rolling_std: float = 0.0
    trend: str = "stable"
    slope: float = 0.0
    measurement_confidence: float = 1.0
    timestamp: datetime
    source: DataClass


class PhysiologicalState(BaseModel):
    timestamp: datetime | None = None
    parameters: dict[str, ParameterState] = Field(default_factory=dict)

    def vector(self) -> dict[str, float]:
        return {k: v.filtered_value for k, v in self.parameters.items()}


class RiskState(BaseModel):
    probability: float = 0.0
    label: str = "not evaluated"
    target: str = "hospital_death"
    anomaly_score: float = 0.0
    anomaly_state: str = "not evaluated"
    top_deviations: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class UncertaintyState(BaseModel):
    data_quality_score: float = 0.0
    state_confidence: float = 0.0
    prediction_confidence: float = 0.0
    forecast_uncertainty: float = 0.0
    missing_fraction: float = 0.0
    simulated_fraction: float = 0.0


class TwinEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    patient_id: str
    twin_id: str
    timestamp: datetime = Field(default_factory=utcnow)
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    severity: str = "info"
    source: str = "twin"


class TwinSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid4()))
    twin_id: str
    patient_id: str
    timestamp: datetime = Field(default_factory=utcnow)
    twin_version: int
    state: PhysiologicalState
    derived_state: dict[str, float]
    risk_state: RiskState
    uncertainty: UncertaintyState


class SimulationScenario(BaseModel):
    name: str
    perturbations: dict[str, float]
    horizon: int = Field(default=6, ge=1, le=48)


class SimulationResult(BaseModel):
    scenario: SimulationScenario
    baseline_trajectory: list[dict[str, float]]
    scenario_trajectory: list[dict[str, float]]
    baseline_risk: float
    scenario_risk: float
    baseline_anomaly: float
    scenario_anomaly: float
    original_state_hash: str
    original_unchanged: bool

