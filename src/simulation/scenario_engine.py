from __future__ import annotations

from datetime import timedelta
from src.twin.state import DataClass, Observation, SimulationResult, SimulationScenario
from src.twin.synchronizer import state_hash


class ScenarioEngine:
    def run(self, twin, scenario: SimulationScenario) -> SimulationResult:
        original_hash = state_hash(twin.current_state.vector())
        scenario_twin = twin.clone()
        baseline_twin = twin.clone()
        baseline_trajectory, scenario_trajectory = [], []
        timestamp = twin.last_synchronization_time
        if timestamp is None: raise ValueError("Synchronize the twin before simulation")
        for step in range(1, scenario.horizon + 1):
            base_values = baseline_twin.current_state.vector()
            scenario_values = scenario_twin.current_state.vector()
            for name, change in scenario.perturbations.items():
                if name in scenario_values: scenario_values[name] += change / scenario.horizon
            ts = timestamp + timedelta(minutes=step * 5)
            baseline_twin.ingest(Observation(patient_id=twin.profile.patient_id, timestamp=ts, values=base_values, quality={k: .7 for k in base_values}, source=DataClass.MODEL_ESTIMATED, scenario="baseline projection"))
            scenario_twin.ingest(Observation(patient_id=twin.profile.patient_id, timestamp=ts, values=scenario_values, quality={k: .65 for k in scenario_values}, source=DataClass.SIMULATED, scenario=scenario.name))
            baseline_trajectory.append({"step": step, **baseline_twin.current_state.vector(), "risk": baseline_twin.risk_state.probability, "anomaly": baseline_twin.risk_state.anomaly_score})
            scenario_trajectory.append({"step": step, **scenario_twin.current_state.vector(), "risk": scenario_twin.risk_state.probability, "anomaly": scenario_twin.risk_state.anomaly_score})
        unchanged = state_hash(twin.current_state.vector()) == original_hash
        twin.emit("SCENARIO_STARTED", {"name": scenario.name, "perturbations": scenario.perturbations})
        twin.emit("SCENARIO_COMPLETED", {"name": scenario.name, "original_unchanged": unchanged})
        result = SimulationResult(scenario=scenario, baseline_trajectory=baseline_trajectory, scenario_trajectory=scenario_trajectory, baseline_risk=baseline_twin.risk_state.probability, scenario_risk=scenario_twin.risk_state.probability, baseline_anomaly=baseline_twin.risk_state.anomaly_score, scenario_anomaly=scenario_twin.risk_state.anomaly_score, original_state_hash=original_hash, original_unchanged=unchanged)
        if twin.repository:
            twin.repository.save_simulation(twin.twin_id, result)
            for event in twin.events.events[twin._persisted_event_count:]:
                twin.repository.save_event(event)
            twin._persisted_event_count = len(twin.events.events)
        return result
