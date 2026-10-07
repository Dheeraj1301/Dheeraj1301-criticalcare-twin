# Changelog

## 1.1.0 — Cloud-edge architecture

- Added an edge gateway with pseudonymization, durable store-and-forward delivery, retry, and sync audit state.
- Added a FastAPI cloud service for twin snapshot ingestion, latest-state lookup, fleet summaries, and health monitoring.
- Connected twin synchronization to the edge gateway without allowing what-if clones to publish.
- Replaced redundant dashboard pages with a focused **Cloud & Edge** page and a consolidated **Evidence Lab**.
- Added a detailed architecture PDF containing diagrams and graphs derived from the actual ICU dataset and saved model evaluation.
- Expanded the automated suite to cover cloud endpoints, offline buffering, privacy boundaries, and all seven dashboard pages.

## 1.0.0 — Research prototype

- Audited all requested datasets and documented the no-join decision.
- Added patient-specific state, synchronization, filtering, derived features, uncertainty, events, persistence, and replay.
- Added hospital-mortality model comparison, transparent anomaly detection, forecasting, and clone-isolated what-if simulation.
- Added an eight-page Streamlit dashboard, deterministic demo profiles, tests, and research documentation.
