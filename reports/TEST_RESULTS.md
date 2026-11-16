# Verification Results

Run date: 2026-11-16 (Asia/Calcutta)

## Automated tests

Command: `python -m pytest -q`

| Suite boundary | Result |
|---|---:|
| Twin state, validation, transitions, features, persistence | Passed |
| FIWARE/MinIO gateway contract, pseudonymization, offline retry | Passed |
| Streamlit rendering across all six workspaces | Passed |
| Total | **10 passed in 19.49 seconds** |

The gateway tests use deterministic fake transport clients. They validate NGSI-LD entity shape, dual-write coordination, removal of raw patient identifiers, durable buffering, and recovery flushing without requiring an external service.

## Model evaluation

Command: `python scripts/train_models.py`

Dataset: 91,713 ICU encounter rows. Validation: fixed 80/20 stratified random split, seed 42.

| Model | ROC-AUC | PR-AUC | Precision @ 0.25 | Recall @ 0.25 | F1 @ 0.25 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Logistic regression | 0.8395 | 0.3988 | 0.1416 | 0.9375 | 0.2461 | 0.1626 |
| Random forest | 0.8486 | 0.4205 | 0.1544 | 0.9280 | 0.2648 | 0.1321 |
| Extra Trees | 0.8463 | 0.4212 | 0.1355 | 0.9596 | 0.2375 | 0.1497 |
| **Histogram gradient boosting** | **0.8577** | **0.4467** | **0.1611** | **0.9242** | **0.2743** | **0.1473** |

The selected model improved ROC-AUC by 0.0091 and PR-AUC by 0.0262 over the previous random forest. The values are measured outputs, not edited targets.

## Real platform execution boundary

The workstation has Docker CLI 29.1.4, but no running Docker or Podman daemon. WSL2 also reports that Virtual Machine Platform/virtualization is unavailable. Therefore the real `Orion-LD -> MongoDB` and `MinIO` container run could not execute on this host during this verification.

The exact end-to-end check is implemented in `scripts/verify_platform.py`. Once a container daemon is running, it:

1. checks Orion-LD and MinIO availability;
2. creates an observed patient twin update;
3. reads the resulting NGSI-LD entity back from Orion-LD;
4. verifies the synchronized audit row and MinIO archive path;
5. exits non-zero if any boundary fails.

No claim of a successful live cloud run is made until that command passes.
