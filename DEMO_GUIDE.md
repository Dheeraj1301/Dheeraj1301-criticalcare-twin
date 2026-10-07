# Five-Minute Demo Guide

## 0:00–0:35 — Define the twin

Open **Cloud & Edge**. Say: “The patient is the physical entity. The edge twin owns baseline, dynamic state, uncertainty, history, events, and simulations. Pseudonymous versioned snapshots cross the cloud boundary through a durable store-and-forward queue.” Show cloud health, queue depth, sync count, and the deployment diagram.

## 0:35–1:05 — Select a patient

Choose **PATIENT B — Gradual deterioration** and open **Command Center**. Point out the twin ID, version, patient baseline, 9 dynamic variables, 3 derived values, provenance badges, quality, and confidence. Say that initialization comes from a real ICU encounter summary.

## 1:05–2:05 — Replay synchronization

Open **Live Twin**, select **Respiratory deterioration**, set 2×, and press Play. Say: “This is seeded simulated demo telemetry because the source is not longitudinal.” Show observations enter, version increments, values update, and the event console records validation, state transition, risk, forecast, latency, and snapshot.

## 2:05–2:45 — Inspect the state transition

Pause and open **State Explorer**. Select SpO₂ or heart rate. Say: “Gray is raw input, cyan is filtered twin state, amber is this patient's baseline, and dashed is the prototype forecast.” Show X(t−1), observation, X(t), ΔX, trend, and confidence.

## 2:45–3:20 — Analytics

Open **Risk & Explainability**. Say: “The supervised output is named for its actual target—hospital death—not renamed as deterioration. The independent anomaly metric compares state with this patient's baseline. Contributions are associations, not causes.”

## 3:20–4:15 — What-if clone

Open **What-If Lab**. Reduce SpO₂ by 5 points, choose 8 steps, and run. Say: “This is a computational scenario, not treatment advice. It runs on a deep clone.” Compare trajectories and point to **Actual twin isolation: VERIFIED**.

## 4:15–5:00 — Provenance and close

Open **Evidence Lab**. Use **Data & Provenance** to show why the sources were not joined, then **Model Evidence** for comparison and validation limits. Close with: “This demonstrates twin lifecycle, disconnected edge operation, cloud synchronization, and auditability. It does not demonstrate clinical safety or efficacy.”
