# Digital Twin Specification

The physical entity is a patient represented only by available observed measurements. The digital entity is a persistent, versioned `PatientDigitalTwin` mirrored into a FIWARE Orion-LD NGSI-LD entity.

At timestamp `t`, validation accepts observation `Y_t`. The state estimator updates `X_t = F(X_(t-1), Y_t, q_t)`, where `q_t` is measurement quality. Derived features `Z_t = G(X_t, baseline, history)` feed the fitted hospital-death model, anomaly method, and short-horizon forecast. The output is persisted before platform synchronization.

Provenance classes are `OBSERVED`, `DERIVED`, and `MODEL_ESTIMATED`. The runtime contains no synthetic telemetry generator or counterfactual scenario engine.

The NGSI-LD entity ID is `urn:ngsi-ld:CriticalCareTwin:{patient_key}`. Each physiological attribute is an NGSI-LD Property with an `observedAt` timestamp. Risk and uncertainty are explicit properties. The raw patient identifier never crosses the edge gateway.
