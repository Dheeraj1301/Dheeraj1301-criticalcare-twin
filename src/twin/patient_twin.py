from __future__ import annotations

import copy
from datetime import datetime
from uuid import uuid4

from .events import EventBus
from .state import Observation, PatientProfile, PhysiologicalState, RiskState, TwinEvent, TwinSnapshot, UncertaintyState


class PatientDigitalTwin:
    def __init__(self, profile: PatientProfile, twin_id: str | None = None, repository=None, edge_gateway=None) -> None:
        self.twin_id = twin_id or f"TWIN-{uuid4().hex[:8].upper()}"
        self.profile = profile
        self.identity = {"patient_id": profile.patient_id, "twin_id": self.twin_id}
        self.static_properties = profile.static_properties
        self.current_state = PhysiologicalState()
        self.previous_state = PhysiologicalState()
        self.observation_buffer: list[Observation] = []
        self.state_history: list[PhysiologicalState] = []
        self.derived_state: dict[str, float] = {}
        self.risk_state = RiskState()
        self.uncertainty = UncertaintyState()
        self.alerts: list[str] = []
        self.model_outputs: dict = {}
        self.forecast_outputs: list[dict] = []
        self.simulation_outputs: list[dict] = []
        self.provenance = profile.provenance
        self.last_synchronization_time: datetime | None = None
        self.twin_version = 0
        self.events = EventBus()
        self.repository = repository
        self.edge_gateway = edge_gateway
        self._persisted_event_count = 0

    def ingest(self, observation: Observation) -> TwinSnapshot:
        from .synchronizer import TwinSynchronizer
        return TwinSynchronizer().synchronize(self, observation)

    def validate(self, observation: Observation) -> None:
        from src.data.validation import validate_values
        if observation.patient_id != self.profile.patient_id:
            raise ValueError("Observation patient_id does not match twin patient")
        if self.last_synchronization_time and observation.timestamp < self.last_synchronization_time:
            raise ValueError("Observation timestamp precedes the latest synchronized observation")
        if not observation.values:
            raise ValueError("Observation contains no values")
        for name, quality in observation.quality.items():
            if not 0 <= quality <= 1: raise ValueError(f"Invalid measurement quality for {name}")
        errors = validate_values(observation.values)
        if errors:
            raise ValueError("; ".join(errors))

    def emit(self, event_type: str, payload: dict | None = None, severity: str = "info") -> None:
        self.events.publish(TwinEvent(patient_id=self.profile.patient_id, twin_id=self.twin_id, event_type=event_type, payload=payload or {}, severity=severity))

    def snapshot(self) -> TwinSnapshot:
        return TwinSnapshot(twin_id=self.twin_id, patient_id=self.profile.patient_id, twin_version=self.twin_version, state=self.current_state.model_copy(deep=True), derived_state=copy.deepcopy(self.derived_state), risk_state=self.risk_state.model_copy(deep=True), uncertainty=self.uncertainty.model_copy(deep=True))

    def clone(self) -> "PatientDigitalTwin":
        cloned = copy.deepcopy(self)
        cloned.twin_id = f"SIM-{uuid4().hex[:8].upper()}"
        cloned.identity["twin_id"] = cloned.twin_id
        cloned.repository = None
        cloned.edge_gateway = None
        return cloned

    @property
    def status(self) -> str:
        return "SYNCHRONIZED" if self.last_synchronization_time else "INITIALIZED"
