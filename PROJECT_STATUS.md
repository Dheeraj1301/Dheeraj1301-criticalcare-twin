# Project Status

## Implemented

- FIWARE Orion-LD NGSI-LD digital-twin adapter.
- MongoDB-backed current platform context.
- MinIO S3-compatible immutable snapshot storage.
- Offline SQLite outbox and synchronization audit.
- Observed CSV ingestion; synthetic telemetry and scenario paths removed.
- Four-model comparison with histogram gradient boosting selected at ROC-AUC 0.8577 and PR-AUC 0.4467.
- Ten automated tests passing.

## Host-dependent remaining check

`python scripts/verify_platform.py` requires a running Docker-compatible daemon. This workstation currently has only the Docker CLI, so the real container integration check is correctly reported as not executed rather than passed.
