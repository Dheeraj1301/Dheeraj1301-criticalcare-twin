# Limitations

- The ICU source contains encounter summaries, not ordered bedside telemetry. Live state changes require an authorized external observation feed.
- The model has only an internal random held-out evaluation; it has no temporal, external, prospective, subgroup, or clinical validation.
- A higher ROC-AUC does not establish clinical usefulness, calibration, safety, or causality.
- The local free stack lacks production TLS, identity management, authorization, managed secrets, monitoring, backups, disaster recovery, and governance.
- Pseudonymization reduces exposure but is not anonymization.
- Forecasts, anomaly scores, and feature contributions are prototype analytics and cannot support patient management.
