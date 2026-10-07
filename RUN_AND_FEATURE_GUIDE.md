# Run and Feature Guide

## Run in VS Code

Open the project folder in VS Code, then open **Terminal > New Terminal**.

### First-time setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
```

If PowerShell blocks virtual-environment activation, run this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Start the complete cloud-edge system

Open two VS Code terminals.

Terminal 1 — cloud service:

```powershell
.venv\Scripts\Activate.ps1
python scripts/run_cloud.py
```

Terminal 2 — edge dashboard:

```powershell
.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Open `http://localhost:8501`. The cloud API runs at `http://127.0.0.1:8000`, and its health endpoint is `http://127.0.0.1:8000/health`.

### Optional data and model rebuild

These commands are only required when rebuilding the data and fitted model:

```powershell
python scripts/download_data.py
python scripts/inspect_data.py
python scripts/prepare_data.py
python scripts/train_models.py
```

## Features in Easy Words

### Command Center

This is the main summary screen. It shows the patient-specific **digital twin**, current **physiological state**, twin version, data quality, confidence, risk, and important events. It answers: “What does the system currently know about this patient?”

### Live Twin

This page demonstrates **real-time synchronization**. Time-indexed observations enter the system, pass through **validation**, and update the twin through a **state transition**. The version number and **event log** make every update auditable. Because the source dataset is not longitudinal, the replay data are clearly labelled **simulated telemetry**.

### State Explorer

This page explains how one measurement changes over time. It compares the **raw observation**, **filtered state estimate**, patient **baseline**, trend, and short-horizon **forecast**. This makes the twin update process visible instead of presenting only a final number.

### Risk & Explainability

The fitted **random-forest classifier** estimates the documented target, **hospital mortality risk**. **Feature contributions** show which variables influenced the prediction. A separate patient-normalized **anomaly score** measures how unusual the current state is compared with that patient's baseline. These are associations, not causes.

### What-If Lab

This page creates a **deep clone** of the twin and changes selected inputs across several simulated steps. It supports **counterfactual simulation** without modifying the real twin. Scenario clones are isolated and cannot publish data to the cloud.

### Cloud & Edge

The **edge layer** runs the patient twin, analytics, local persistence, and low-latency processing. The **cloud layer** receives pseudonymous, versioned snapshots and provides latest-state and fleet-summary APIs. If the network is unavailable, **store-and-forward** places snapshots in a durable SQLite **outbox** and retries them later. A salted **pseudonymous patient key** prevents the raw patient ID from crossing the cloud boundary.

### Evidence Lab

This page holds the scientific evidence. **Data & Provenance** records where the data came from and why unrelated datasets were not joined. **Model Evidence** presents model comparison, evaluation metrics, and validation limits. This keeps **data lineage**, assumptions, and limitations visible.

## Supporting Components

- **Patient baseline:** the individual's reference values used for personalization.
- **State estimator:** filters observations before storing the current state.
- **Derived features:** calculated values such as shock index, pulse pressure, and instability.
- **Uncertainty:** expresses how confident the prototype is in current estimates.
- **Persistence:** saves snapshots and events in SQLite so the twin has memory.
- **Event-driven architecture:** records validation, synchronization, risk, forecast, and cloud-delivery events.
- **FastAPI cloud service:** exposes health, synchronization, latest-state, and fleet-summary endpoints.
- **Streamlit dashboard:** provides the interactive visual interface.
- **Auditability:** versions, timestamps, provenance, and events make changes traceable.
- **Testing:** automated tests cover twin behavior, persistence, simulation isolation, dashboard rendering, cloud APIs, offline buffering, and privacy boundaries.

## Important Limitation

This is a research and educational prototype. It has not been clinically validated and must not be used for diagnosis, treatment, triage, or patient management.
