from __future__ import annotations

import hashlib
import json
import time

from src.analytics.anomaly import TransparentAnomalyDetector
from src.analytics.forecast import TrajectoryForecaster
from src.analytics.risk_model import HospitalMortalityRiskModel
from .feature_engine import FeatureEngine
from .state import Observation, RiskState, TwinEvent, TwinSnapshot
from .state_estimator import StateEstimator
from .uncertainty import estimate_uncertainty


def state_hash(vector: dict[str, float]) -> str:
    return hashlib.sha256(json.dumps(vector, sort_keys=True).encode()).hexdigest()[:12]


class TwinSynchronizer:
    def __init__(self) -> None:
        self.estimator = StateEstimator()
        self.features = FeatureEngine()
        self.risk_model = HospitalMortalityRiskModel()
        self.anomaly = TransparentAnomalyDetector()
        self.forecaster = TrajectoryForecaster()

    def synchronize(self, twin, observation: Observation) -> TwinSnapshot:
        started = time.perf_counter()
        old_vector = twin.current_state.vector()
        risk_before = twin.risk_state.probability
        twin.emit("OBSERVATION_RECEIVED", {"observation_id": observation.observation_id, "source": observation.source.value})
        twin.validate(observation)
        twin.emit("OBSERVATION_VALIDATED", {"observation_id": observation.observation_id})
        twin.previous_state = twin.current_state.model_copy(deep=True)
        new_state = self.estimator.estimate(observation, twin.current_state, twin.state_history)
        twin.current_state = new_state
        twin.state_history.append(new_state.model_copy(deep=True))
        twin.state_history = twin.state_history[-500:]
        twin.derived_state = self.features.compute(new_state, twin.profile.baseline)
        probability, explanation = self.risk_model.predict(new_state.vector(), {**twin.profile.static_properties, "age": twin.profile.age})
        anomaly_score, anomaly_state, deviations = self.anomaly.score(new_state.vector(), twin.profile.baseline)
        twin.risk_state = RiskState(
            probability=probability, label="elevated" if probability >= .35 else "watch" if probability >= .15 else "low",
            anomaly_score=anomaly_score, anomaly_state=anomaly_state, top_deviations=deviations,
            confidence=twin.uncertainty.prediction_confidence,
        )
        twin.model_outputs = {"target": "hospital_death", "probability": probability, "contributions": explanation}
        twin.forecast_outputs = self.forecaster.forecast(twin.state_history[:-1], new_state)
        twin.uncertainty = estimate_uncertainty(new_state)
        twin.risk_state.confidence = twin.uncertainty.prediction_confidence
        twin.last_synchronization_time = observation.timestamp
        twin.twin_version += 1
        twin.observation_buffer.append(observation)
        changed = [k for k, v in new_state.vector().items() if old_vector.get(k) != v]
        alerts = []
        if anomaly_state == "abnormal": alerts.append("Prototype anomaly threshold crossed")
        if probability >= .35: alerts.append("Model-estimated hospital mortality risk elevated")
        twin.alerts = alerts
        latency = (time.perf_counter() - started) * 1000
        twin.emit("STATE_UPDATED", {"old_state_hash": state_hash(old_vector), "new_state_hash": state_hash(new_state.vector()), "changed_parameters": changed, "risk_before": risk_before, "risk_after": probability, "alerts": alerts, "latency_ms": latency})
        if anomaly_state == "abnormal": twin.emit("ANOMALY_DETECTED", {"score": anomaly_score, "variables": deviations}, "warning")
        twin.emit("RISK_CHANGED", {"before": risk_before, "after": probability, "target": "hospital_death"})
        twin.emit("FORECAST_UPDATED", {"steps": len(twin.forecast_outputs)})
        snapshot = twin.snapshot()
        twin.emit("SNAPSHOT_CREATED", {"snapshot_id": snapshot.snapshot_id})
        if twin.repository:
            twin.repository.save_observation(observation, twin.twin_id)
            twin.repository.save_snapshot(snapshot)
            for event in twin.events.events[twin._persisted_event_count:]: twin.repository.save_event(event)
            twin._persisted_event_count = len(twin.events.events)
        if twin.edge_gateway:
            synced = twin.edge_gateway.publish(twin, snapshot)
            twin.emit("CLOUD_SYNCED" if synced else "EDGE_SYNC_QUEUED", {"twin_version": twin.twin_version, "deidentified": True}, "info" if synced else "warning")
            if twin.repository:
                twin.repository.save_event(twin.events.events[-1])
                twin._persisted_event_count = len(twin.events.events)
        return snapshot
