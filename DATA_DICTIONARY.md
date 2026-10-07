# Data Dictionary

| Variable | Meaning | Unit | Dataset / engine | Class | Twin? | ML? | Notes |
|---|---|---|---|---|---:|---:|---|
| heart_rate | Heart rate | bpm | ICU / telemetry | Observed or Simulated | Yes | Yes | Filtered and trended |
| systolic_bp | Systolic pressure | mmHg | ICU / telemetry | Observed or Simulated | Yes | Yes | Baseline normalized |
| diastolic_bp | Diastolic pressure | mmHg | ICU / telemetry | Observed or Simulated | Yes | Yes | Baseline normalized |
| respiratory_rate | Respiratory rate | breaths/min | ICU / telemetry | Observed or Simulated | Yes | Yes | Bounded demo stream |
| spo2 | Peripheral oxygen saturation | % | ICU / telemetry | Observed or Simulated | Yes | Yes | Not a waveform |
| temperature | Temperature | °C | ICU / telemetry | Observed or Simulated | Yes | Yes | Day-one midpoint initially |
| glucose | Blood glucose | mg/dL | ICU / telemetry | Observed or Simulated | Yes | Yes | Day-one midpoint initially |
| potassium | Serum potassium | mmol/L | ICU / telemetry | Observed or Simulated | Yes | Yes | Day-one midpoint initially |
| gcs | GCS component-sum proxy | points | ICU / telemetry | Observed or Simulated | Yes | Yes | 3–15 |
| mean_arterial_pressure | (SBP + 2×DBP)/3 | mmHg | Feature engine | Derived | Yes | No | Prototype-derived metric |
| pulse_pressure | SBP − DBP | mmHg | Feature engine | Derived | Yes | No | Prototype-derived metric |
| shock_index_proxy | HR / SBP | ratio | Feature engine | Derived | Yes | No | Not a validated score here |
| physiological_instability_index | Mean normalized deviation | unitless | Feature engine | Derived | Yes | No | Custom prototype metric |
| hospital_death_probability | Supervised outcome estimate | probability | Risk model | Model Estimated | Yes | Output | Not a diagnosis |
| anomaly_score | Patient deviation | 0–1 | Anomaly engine | Model Estimated | Yes | No | Independent prototype method |
| forecast_* | Local trend projections | source unit | Forecast engine | Model Estimated | Yes | No | Prototype forecast |
| readmission_risk | Supplied source field | score | Healthcare analytics | Observed | No | No | Separate source; not joined |
| Outcome Variable | Source outcome label | category | Disease profile | Observed | No | No | Ambiguous; unused by ICU model |

