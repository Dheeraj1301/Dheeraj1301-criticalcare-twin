# CRITICALCARE-TWIN — System Architecture

CRITICALCARE-TWIN is an **offline-capable research prototype** that maintains a versioned patient digital-twin state from **observed** ICU encounter summaries and subsequently uploaded timestamped observations. Its local edge state is distinct from the two external stores: **FIWARE Orion-LD** for current NGSI-LD context and **MinIO** for immutable historical envelopes.

> **Research only.** Not a validated clinical device or decision-support system. The source dataset contains cross-sectional encounter summaries, not a live bedside monitoring stream.

## Component architecture

```mermaid
flowchart TB
    subgraph Input["Observed inputs"]
        A["Audited ICU encounter summary"]
        B["Timestamped CSV / authorized EHR or device adapter"]
    end
    subgraph Edge["Local edge application"]
        C["Input adapter + quality/range validation"]
        D["TwinSynchronizer"]
        E["PatientDigitalTwin: versioned state + features"]
        F["Model inference, anomaly & forecast (research analytics)"]
        G[("SQLite: observations, audit, offline outbox")]
        H["EdgeGateway: pseudonymized versioned envelope"]
        U["Streamlit dashboard"]
    end
    subgraph Platform["Self-hosted platform"]
        I["FIWARE Orion-LD: current NGSI-LD entity"]
        J[("MongoDB: Orion-LD persistence")]
        K[("MinIO: immutable JSON versions")]
    end
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
    E --> U
    F --> U
    H --> G
    G -->|"sync/retry"| I
    G -->|"sync/retry"| K
    I --> J
    I -.->|"platform status / current context"| U
    K -.->|"snapshot evidence"| U
```

The arrows to Orion-LD and MinIO indicate **separate delivery attempts** using the same versioned envelope. A failure at either external destination does not block local twin updates.

## Observation and recovery sequence

```mermaid
sequenceDiagram
    actor Researcher
    participant UI as Streamlit
    participant Sync as TwinSynchronizer
    participant DB as SQLite / outbox
    participant GW as EdgeGateway
    participant Orion as Orion-LD
    participant Store as MinIO
    Researcher->>UI: Upload timestamped observations
    UI->>Sync: Validate and process in chronological order
    Sync->>DB: Persist observation, state, audit, events
    Sync->>GW: Build versioned pseudonymous envelope
    GW->>DB: Queue envelope durably
    opt Services are reachable
        GW->>Orion: Upsert NGSI-LD current context
        GW->>Store: Archive immutable JSON snapshot
        GW->>DB: Record delivery/flush status
    end
    Note over GW,DB: On outage, retain payload and retry later
    UI-->>Researcher: Show local state and platform status
```

## Ownership of data

| Component | Role | Important boundary |
| --- | --- | --- |
| `src/data/` | Observed-data adapters, preprocessing and validation | Reject malformed or implausible observations |
| `src/twin/` | State synchronization, derived features, versions, events | Local state is not proof of live bedside monitoring |
| `src/analytics/` | Trained risk model, forecasting and anomaly prototypes | Associations and research estimates, not clinical predictions |
| `src/edge/` | Pseudonymous envelopes, outage tolerance and resynchronization | Pseudonymization is **not** anonymization |
| SQLite | Local audit history, event persistence and durable outbox | Continues to work without Orion-LD or MinIO |
| FIWARE Orion-LD + MongoDB | Latest connected NGSI-LD context | Not an immutable audit archive |
| MinIO | Versioned JSON envelopes through an S3-compatible API | Not the authority for current twin state |
| Streamlit | Ingestion, investigation, evidence and platform visibility | Not an authenticated clinical dashboard |

## Reproducibility and evidence

- [README](README.md) — installation, run commands, observed CSV contract, held-out benchmark table.
- [Data provenance](reports/DATA_PROVENANCE.md), [dataset audit](reports/DATASET_AUDIT.md), and [data dictionary](DATA_DICTIONARY.md) — scope and source records.
- [Model evaluation](reports/MODEL_EVALUATION.md) — four-model 80/20 encounter-level comparison.
- [Test results](reports/TEST_RESULTS.md) and [project status](PROJECT_STATUS.md) — automated checks and outstanding workstation-dependent Docker verification.
- [Limitations](LIMITATIONS.md) and [model card](MODEL_CARD.md) — non-clinical boundaries.

## Deployment and validation status

The repository includes a Compose definition in `infra/compose.yaml` and a host verification script in `scripts/verify_platform.py`. The Python automated checks and local model evaluation are documented; **end-to-end verification against running platform containers has not been established on the original development workstation**. Before shared deployment, add TLS, identity/authorization, secret rotation, backups, monitoring, data governance and clinical validation.
