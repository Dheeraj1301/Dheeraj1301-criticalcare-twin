# Digital Twin Specification

## Entities

The physical entity is a patient represented by the available clinical observations. The digital entity is `PatientDigitalTwin`, a persistent, versioned object with patient identity, static context, baseline, dynamic state, history, uncertainty, events, analytical outputs, and simulations.

## Formal state

Let **Y_t** be a timestamped observation vector at time *t*, including measurement-quality estimates. It is evidence entering the system; it is not automatically the twin state.

Let **B** be the patient baseline initialized from the selected ICU encounter. Let **X_(t−1)** be the preceding filtered state and **X_t** the new state:

**X_t = F(X_(t−1), Y_t, q_t)**

Here **F** is confidence-weighted exponential smoothing and **q_t** is measurement quality. A received value has weight **α = 0.25 + 0.55q_t**. Missing parameters retain the prior estimate with reduced confidence and a `MODEL_ESTIMATED` label. **ΔX_t = X_t − X_(t−1)** is stored per parameter.

Baseline deviation is **D_t = X_t − B**. Normalized deviations use configured transparent scale factors, not learned clinical cutoffs.

**Z_t = G(X_t, B, history)** contains MAP, pulse pressure, an HR/SBP proxy, rolling slopes, volatility, baseline distance, normalized deviations, missingness, and a prototype instability metric.

Attached analytics compute **R_t = M(Z_t, static context)**. Here **R_t** is specifically the model-estimated probability of the source field `hospital_death`. Independent function **A(X_t, B)** produces a patient-normalized anomaly score.

The short-horizon forecast **X̂_(t+k)** extrapolates recent local trends with widening empirical uncertainty bands. It is explicitly a prototype forecast.

For scenario perturbation **u**, a deep clone evolves as **X_(t+k)^scenario = S(clone(X_t), u, k)**. The actual twin is never passed to the scenario transition. Hash equality before and after simulation is asserted and tested.

## Semantic distinctions

- **Observation** — received timestamped measurement (`OBSERVED` or `SIMULATED`).
- **State** — filtered patient-specific computational estimate.
- **Derived value** — transparent calculation from state, `DERIVED`.
- **Prediction** — attached model output, `MODEL_ESTIMATED`.
- **Simulation** — cloned and perturbed twin output, `SIMULATED`.

## Lifecycle contract

`ingest → validate → synchronize → estimate state → compute features → evaluate risk and anomaly → forecast → emit events → persist snapshot` is executed by `TwinSynchronizer.synchronize`. Each state-update event records old/new hashes, changed parameters, risk before/after, alerts, and latency.

After local persistence, the edge creates cloud envelope **C_t = P(snapshot_t)**, where **P** removes the source patient identifier and replaces it with a salted one-way pseudonymous key. Delivery follows store-and-forward semantics: local state advancement never depends on cloud availability. Message ID provides idempotency and twin version preserves ordering context. Simulation clones do not carry an edge gateway and cannot publish scenario state to the cloud record.
