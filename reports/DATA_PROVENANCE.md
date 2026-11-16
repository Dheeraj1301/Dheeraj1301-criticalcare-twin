# Data Provenance

Raw files are copied unchanged from the KaggleHub cache into `data/raw/<source>/`. `data/metadata/download_manifest.json` records handles and paths. Processed datasets have adjacent JSON provenance records containing source, timestamp, columns, transformations, missing-data policy, derived fields, synthetic fields, and limitations.

No synthetic telemetry is generated. The bundled source provides observed encounter summaries; later state transitions require explicitly uploaded timestamped observations from an authorized source.

