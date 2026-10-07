# Limitations

CRITICALCARE-TWIN is an educational software prototype, not a medical device.

- The ICU source is encounter-level and has no ordered bedside telemetry. Replay data are synthetic demonstrations around a real encounter baseline.
- The generator adds bounded drift and noise; it is not a validated physiological or pharmacokinetic model.
- The hospital-mortality model has only internal random-split evaluation and cannot establish clinical generalization.
- Anomaly, instability, confidence, and forecast uncertainty are transparent prototype metrics, not validated scores.
- No causal or treatment claims can be inferred from feature contributions or scenario perturbations.
- Dataset collection, representativeness, site effects, coding practices, licensing, and subgroup fairness require independent review.
- SQLite and in-process events suit a local demo, not a high-availability clinical system.

