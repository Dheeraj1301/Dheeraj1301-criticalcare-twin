# Operational Pipeline

| Stage | Input | Output | Implementation |
|---|---|---|---|
| Observed ingestion | Audited encounter or timestamped CSV | `Observation` | `src/data`, `app.py` |
| Validation | Observation | Accepted or rejected values | `src/data/validation.py` |
| Synchronization | Previous state + observation | Versioned state | `src/twin/synchronizer.py` |
| Analytics | State + baseline + history | Risk, anomaly, forecast | `src/analytics` |
| Local audit | Snapshot and events | SQLite records | `src/twin/repository.py` |
| Edge privacy | Snapshot | Pseudonymous envelope | `src/edge/gateway.py` |
| Digital-twin platform | Envelope | NGSI-LD entity | `src/cloud/orion.py` |
| Object storage | Envelope | Versioned JSON object | `src/cloud/object_store.py` |
| Disconnection handling | Failed envelope | Durable outbox | `src/edge/gateway.py` |
