# Architecture

CRITICALCARE-TWIN is an offline-capable edge application connected to FIWARE Orion-LD and MinIO.

1. An observed ICU encounter or uploaded timestamped CSV creates an `Observation`.
2. Validation enforces patient identity, chronological ordering, numeric types, quality bounds, and physiological ranges.
3. `TwinSynchronizer` updates the versioned `PatientDigitalTwin`, derived features, analytics, uncertainty, events, and SQLite audit state.
4. `EdgeGateway` replaces the source identifier with a salted SHA-256 key and builds a versioned envelope.
5. `OrionDigitalTwinClient` creates or updates the corresponding NGSI-LD `CriticalCareTwin` entity.
6. `SnapshotObjectStore` archives the same envelope at `twins/{patient_key}/{date}/v{version}.json` in MinIO.
7. If either platform boundary is unavailable, the immutable envelope remains in SQLite and can be flushed later.

Orion-LD owns current connected context. MinIO owns immutable snapshot history. SQLite owns the local audit and outage boundary.

The deployment is self-hosted and uses no paid cloud API. Shared or clinical environments still require TLS, authenticated identities, secret rotation, authorization, monitoring, backups, governance, and clinical validation.
