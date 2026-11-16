# Run and Feature Guide

## Commands

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File infra\start-free-stack.ps1
python scripts/verify_platform.py
python -m pytest -q
python -m streamlit run app.py
```

## Dashboard features

- **Command Center:** current versioned patient state, measured model output, anomaly state, data quality, and observation provenance.
- **Observation Ingestion:** validates timestamped observed CSV rows and synchronizes accepted rows into the twin.
- **State Explorer:** displays previous state, raw observation, filtered state, delta, baseline, trend, and confidence.
- **Risk & Explainability:** shows the held-out model's probability and associational contributions with explicit limitations.
- **Digital Twin Platform:** displays Orion-LD, MinIO, outbox, and synchronization status and can flush buffered messages.
- **Evidence Lab:** displays the exact held-out metrics used to select the fitted model.

## Platform behavior

Orion-LD represents the live twin as an NGSI-LD entity. MongoDB persists current context. MinIO stores immutable JSON versions. If either service is offline, local synchronization continues and the exact platform envelope is retained in SQLite.
