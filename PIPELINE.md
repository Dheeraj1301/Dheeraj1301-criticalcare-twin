# Operational Pipeline

| Stage | Input | Processing | Output | Responsible code |
|---|---|---|---|---|
| Ingestion | Kaggle files | Preserve raw files and record source | Raw datasets | `scripts/download_data.py` |
| Audit | Raw files | Schema, quality, distribution inspection | Dataset audit | `scripts/inspect_data.py` |
| Validation | Source records / telemetry | Range and type checks | Valid observations | `src/data/validation.py` |
| Preprocessing | Audited records | Source-specific normalization | Patient profiles | `src/data/adapters.py` |
| Initialization | Patient profile | Build identity, baseline, uncertainty | Persistent twin | `src/twin/patient_twin.py` |
| Synchronization | Timestamped observation | Validate, estimate, derive, analyze | New state and event | `src/twin/synchronizer.py` |
| State estimation | Observation + prior history | Confidence-weighted smoothing | **X_t**, delta, trends | `src/twin/state_estimator.py` |
| Features | State + baseline + history | Transparent formulas | **Z_t** | `src/twin/feature_engine.py` |
| Analytics | Twin features | Supervised risk + anomaly scoring | Model outputs | `src/analytics/` |
| Forecast | State history | Trend extrapolation | Short-horizon trajectory | `src/analytics/forecast.py` |
| Simulation | Cloned current twin | Controlled perturbation | Scenario comparison | `src/simulation/scenario_engine.py` |
| Persistence | Snapshots and events | SQLite serialization | Replayable history | `src/twin/repository.py` |
| Edge packaging | Persisted twin snapshot | Pseudonymize ID and build versioned envelope | Cloud sync message | `src/edge/gateway.py` |
| Offline buffering | Failed cloud request | Durable ordered outbox | Retryable messages | `src/edge/gateway.py` |
| Cloud synchronization | Pseudonymous envelope | Idempotent API acceptance | Cloud twin snapshot | `src/cloud/service.py` |
| Cloud query | Versioned cloud history | Latest-state and fleet aggregation | Cloud API response | `src/cloud/service.py` |
| Presentation | Twin lifecycle artifacts | Interactive research views | Dashboard | `app.py`, `src/ui/` |
