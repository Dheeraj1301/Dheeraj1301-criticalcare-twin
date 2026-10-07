# Model Evaluation

The supervised task is the dataset's documented `hospital_death` outcome. It is not relabelled as deterioration.

- Selected model: **random_forest**
- Rows: 91,713; positive rate: 0.086
- Validation: 80/20 stratified random encounter split (seed 42)
- Leakage controls: APACHE mortality probabilities, encounter/patient IDs, and target-adjacent death fields excluded.

| Model | ROC-AUC | PR-AUC | Precision@0.25 | Recall@0.25 | F1@0.25 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.839 | 0.399 | 0.142 | 0.937 | 0.246 | 0.163 |
| random_forest | 0.849 | 0.420 | 0.154 | 0.928 | 0.265 | 0.132 |

## Limitations

This internally validated educational model is not calibrated or validated for clinical use. Random encounter splitting does not measure future-site generalization. Feature importance reflects association, not causality.