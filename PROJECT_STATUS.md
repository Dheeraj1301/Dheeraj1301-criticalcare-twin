# Current Phase

Phase 19 — Cloud-edge digital twin and architecture report complete

# Completed

- Download and audit of all three specified Kaggle datasets and a defensible no-join decision.
- Processed-data provenance, data adapter, and reproducible patient profiles.
- PatientDigitalTwin core, state contracts, synchronization, estimation, history, baseline personalization, and generic state vector.
- Seeded synthetic demo telemetry with four bounded scenarios.
- Derived/temporal features, anomaly detection, uncertainty, and prototype forecasting.
- Logistic-regression vs random-forest comparison for documented `hospital_death`; fitted artifact and evaluation report.
- Clone-isolated what-if engine and SQLite persistence/event schema.
- Seven-page dark Streamlit dashboard, replay controls, event console, patient SVG, cloud status, and provenance labels.
- Edge gateway with pseudonymous identifiers, durable SQLite store-and-forward outbox, retry/audit state, and configurable cloud endpoint.
- Cloud twin API with health, versioned snapshot ingestion, latest-twin lookup, and fleet summary endpoints.
- Detailed architecture PDF with diagrams and graphs generated from the actual 91,713-row ICU dataset and saved model evidence.
- Academic documentation, model card, data dictionary, limitations, and five-minute demo guide.
- Unit, persistence, scenario-isolation, smoke, compilation, and dashboard render verification.

# In Progress

- None.

# Next Tasks

- Optional research: external/temporal validation, governed longitudinal adapter, subgroup fairness assessment, and clinician usability study.

# Known Problems

- No clinical or external validation; the system must remain an educational/research demonstration.
- Source ICU data are encounter summaries, not ordered telemetry. Replay is explicitly simulated.
- Forecasting and uncertainty are transparent prototype methods, not validated clinical models.

# Scientific Assumptions

- First-hour vital extrema and day-one lab/temperature extrema initialize a baseline via midpoints.
- No datasets are linked because there is no defensible common patient identity.
- Synthetic telemetry demonstrates synchronization only and never fabricates training outcomes.
- The supervised target remains `hospital_death`; it is not relabelled as deterioration.

# Decisions Made

- Random forest selected over logistic regression by internal ROC-AUC (0.849 vs 0.840).
- APACHE death probabilities and identifiers are excluded to reduce obvious leakage.
- Patient-normalized deviation is used for transparent anomaly detection.
- SQLite and in-process events are appropriate for the edge prototype; the cloud API is a replaceable service boundary backed by its own versioned store.
- Raw patient identifiers remain at the edge; cloud envelopes use a salted pseudonymous key.

# Tests Passing

- `python -m pytest -q`: 10 passed.
- `python scripts/run_demo.py`: lifecycle smoke test passed.
- `python -m compileall -q app.py src scripts`: passed.
- Streamlit AppTest: all seven pages render without exceptions; scenario isolation shows VERIFIED.
- Cloud-edge delivery test: offline snapshot queued, cloud started, retry delivered, fleet summary updated, and queue returned to zero.
- Browser smoke test: app loaded, state cards rendered, replay advanced twin version, state chart/table and architecture diagram rendered.

# Demo Readiness

**DEMO READY — RESEARCH / EDUCATIONAL USE ONLY**
