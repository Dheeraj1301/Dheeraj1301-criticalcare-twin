# Data Provenance

Raw files are copied unchanged from the KaggleHub cache into `data/raw/<source>/`. `data/metadata/download_manifest.json` records handles and paths. Processed datasets have adjacent JSON provenance records containing source, timestamp, columns, transformations, missing-data policy, derived fields, synthetic fields, and limitations.

Synthetic telemetry is generated only at runtime or under `data/synthetic/`; it is labelled **SIMULATED DEMO TELEMETRY** and is never presented as a measured Kaggle time series or used to fabricate training labels.

