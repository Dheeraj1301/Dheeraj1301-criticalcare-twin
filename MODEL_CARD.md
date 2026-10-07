# Model Card — Encounter-Level Hospital Mortality Model

## Objective and intended use

Estimate the documented binary `hospital_death` field for educational exploration of an analytical capability attached to a digital twin. It is not a diagnosis, deterioration forecast, or recommendation.

## Data and features

Source: `mitishaagarwal/patient`, 91,713 ICU encounters. Features are age, BMI, state-compatible vital summaries, glucose, potassium, GCS, elective-surgery status, ventilation, and intubation. APACHE death probabilities, identifiers, and outcome-adjacent fields are excluded. Missing values are median-imputed inside the training pipeline.

## Training and evaluation

Seed 42; stratified 80/20 random encounter split. Logistic regression and a class-balanced random forest are compared. The artifact, exact metrics, class balance, curves, confusion matrix, and timestamp are in `models/hospital_mortality_metadata.json` and `reports/MODEL_EVALUATION.md`.

Metrics include ROC-AUC, PR-AUC, precision, recall, F1, confusion matrix at a documented research threshold, and Brier score. These are internal metrics only.

## Limitations and prohibited use

- No external, temporal, geographic, or prospective validation.
- Encounter-window measurements may not reflect prediction-time availability.
- Missingness, treatment decisions, and site practice may introduce bias.
- Fairness across patient groups and sites has not been established.
- Feature contributions are associations, not causal effects.

Clinical diagnosis, prognosis, triage, treatment selection, dosage, resource allocation, autonomous alerts, or real-patient management are out of scope.

