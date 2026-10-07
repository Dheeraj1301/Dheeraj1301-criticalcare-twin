# Dataset Audit

Generated from the downloaded files; no schemas were assumed in advance.

## Cross-dataset decision

The datasets are **not joined**. The ICU table has `patient_id`, but the symptom table has no identifier and the analytics table's independently generated `patient_id` belongs to another source. Matching similarly named demographic fields would create false patient linkage. Each source therefore has a separate role.

## Disease_symptom_and_patient_profile_dataset.csv

- Dataset source: `uom190346a/disease-symptoms-and-patient-profile-dataset`
- Local file: `data/raw/disease_symptoms_profile/Disease_symptom_and_patient_profile_dataset.csv`
- Rows: 349
- Columns: 10
- Duplicate rows: 49
- Longitudinal status: Cross-sectional disease/profile examples.

### Exact schema and missingness

| Column | Inferred dtype | Missing | Unique |
|---|---:|---:|---:|
| Disease | object | 0 | 116 |
| Fever | object | 0 | 2 |
| Cough | object | 0 | 2 |
| Fatigue | object | 0 | 2 |
| Difficulty Breathing | object | 0 | 2 |
| Age | int64 | 0 | 26 |
| Gender | object | 0 | 2 |
| Blood Pressure | object | 0 | 3 |
| Cholesterol Level | object | 0 | 3 |
| Outcome Variable | object | 0 | 2 |

### Inferred clinical/data roles

- Identifiers: none detected
- Timestamps: none detected
- Targets/outcomes: `Outcome Variable`
- Vital signs: none detected
- Laboratory variables: `Cholesterol Level`
- Demographics: `Age`, `Gender`
- Symptoms: `Fever`, `Cough`, `Fatigue`, `Difficulty Breathing`
- Diagnoses: `Disease`
- Medications/interventions: none detected

### Numerical distributions

Values are `count / mean / std / min / 25% / median / 75% / max`.

| Variable | Distribution |
|---|---|
| Age | 349 / 46.3 / 13.1 / 19 / 35 / 45 / 55 / 90 |

### Categorical distributions

Top values are shown as `value: count` (up to 10 per field).

| Variable | Top values |
|---|---|
| Disease | Asthma: 23; Stroke: 16; Osteoporosis: 14; Diabetes: 10; Hypertension: 10; Migraine: 10; Influenza: 8; Bronchitis: 8; Pneumonia: 8; Hyperthyroidism: 7 |
| Fever | Yes: 175; No: 174 |
| Cough | No: 182; Yes: 167 |
| Fatigue | Yes: 242; No: 107 |
| Difficulty Breathing | No: 261; Yes: 88 |
| Gender | Female: 176; Male: 173 |
| Blood Pressure | High: 167; Normal: 164; Low: 18 |
| Cholesterol Level | High: 166; Normal: 149; Low: 34 |
| Outcome Variable | Positive: 186; Negative: 163 |

### Clinical usefulness

Supplementary source for demonstrating categorical symptom/disease context and for discussing a separate positive/negative outcome task. It is not used to invent ICU physiology.

### Limitations

Small, duplicated, cross-sectional examples; no patient ID or timestamps; ambiguous meaning of the outcome; categorical blood pressure/cholesterol; cannot be linked to ICU encounters.

## healthcare_patient_analytics_seaborn.csv

- Dataset source: `abbas829/healthcare-patient-analytics-dataset`
- Local file: `data/raw/healthcare_analytics/healthcare_patient_analytics_seaborn.csv`
- Rows: 5,000
- Columns: 12
- Duplicate rows: 0
- Longitudinal status: Time-stamped administrative visits, but each patient ID occurs once; cross-sectional for this download.

### Exact schema and missingness

| Column | Inferred dtype | Missing | Unique |
|---|---:|---:|---:|
| patient_id | int64 | 0 | 5,000 |
| visit_date | object | 0 | 5,000 |
| age_group | object | 0 | 4 |
| gender | object | 0 | 2 |
| region | object | 0 | 4 |
| department | object | 0 | 5 |
| treatment_type | object | 0 | 4 |
| visit_type | object | 0 | 2 |
| length_of_stay_days | float64 | 0 | 105 |
| treatment_cost | float64 | 0 | 4,841 |
| recovery_score | float64 | 0 | 66 |
| readmission_risk | float64 | 0 | 83 |

### Inferred clinical/data roles

- Identifiers: `patient_id`
- Timestamps: `visit_date`
- Targets/outcomes: `recovery_score`, `readmission_risk`
- Vital signs: none detected
- Laboratory variables: none detected
- Demographics: `age_group`, `gender`
- Symptoms: none detected
- Diagnoses: none detected
- Medications/interventions: `treatment_type`, `treatment_cost`

### Numerical distributions

Values are `count / mean / std / min / 25% / median / 75% / max`.

| Variable | Distribution |
|---|---|
| patient_id | 5e+03 / 2.5e+03 / 1.44e+03 / 1 / 1.25e+03 / 2.5e+03 / 3.75e+03 / 5e+03 |
| length_of_stay_days | 5e+03 / 4.06 / 1.93 / 0 / 2.7 / 4 / 5.4 / 11.9 |
| treatment_cost | 5e+03 / 5.49e+04 / 1.95e+04 / 746 / 4.12e+04 / 5.51e+04 / 6.8e+04 / 1.19e+05 |
| recovery_score | 5e+03 / 74.7 / 11.9 / 33 / 67 / 75 / 83 / 100 |
| readmission_risk | 5e+03 / 0.281 / 0.157 / 0.01 / 0.16 / 0.26 / 0.38 / 0.84 |

### Categorical distributions

Top values are shown as `value: count` (up to 10 per field).

| Variable | Top values |
|---|---|
| visit_date | 2022-01-01 00:00:00: 1; 2022-01-01 01:00:00: 1; 2022-01-01 02:00:00: 1; 2022-01-01 03:00:00: 1; 2022-01-01 04:00:00: 1; 2022-01-01 05:00:00: 1; 2022-01-01 06:00:00: 1; 2022-01-01 07:00:00: 1; 2022-01-01 08:00:00: 1; 2022-01-01 09:00:00: 1 |
| age_group | 31-45: 1716; 18-30: 1283; 46-60: 1271; 60+: 730 |
| gender | Male: 2508; Female: 2492 |
| region | West: 1290; North: 1282; East: 1217; South: 1211 |
| department | Orthopedics: 1058; Cardiology: 995; General Medicine: 991; Pediatrics: 989; Neurology: 967 |
| treatment_type | Observation: 1270; Surgery: 1262; Medication: 1236; Therapy: 1232 |
| visit_type | Routine: 3432; Emergency: 1568 |

### Clinical usefulness

Administrative/provenance demonstration only: visit attributes, recovery score, and supplied readmission-risk values.

### Limitations

Appears synthetic/curated, has one row per patient, no physiology or measured clinical outcome for training, and identifiers are source-local. Not linked to the ICU dataset.

## dataset.csv

- Dataset source: `mitishaagarwal/patient`
- Local file: `data/raw/patient/dataset.csv`
- Rows: 91,713
- Columns: 85
- Duplicate rows: 0
- Longitudinal status: Cross-sectional encounter-level table; min/max windows are not timestamped sequences.

### Exact schema and missingness

| Column | Inferred dtype | Missing | Unique |
|---|---:|---:|---:|
| encounter_id | int64 | 0 | 91,713 |
| patient_id | int64 | 0 | 91,713 |
| hospital_id | int64 | 0 | 147 |
| age | float64 | 4,228 | 74 |
| bmi | float64 | 3,429 | 34,888 |
| elective_surgery | int64 | 0 | 2 |
| ethnicity | object | 1,395 | 6 |
| gender | object | 25 | 2 |
| height | float64 | 1,334 | 401 |
| icu_admit_source | object | 112 | 5 |
| icu_id | int64 | 0 | 241 |
| icu_stay_type | object | 0 | 3 |
| icu_type | object | 0 | 8 |
| pre_icu_los_days | float64 | 0 | 9,757 |
| weight | float64 | 2,720 | 3,409 |
| apache_2_diagnosis | float64 | 1,662 | 44 |
| apache_3j_diagnosis | float64 | 1,101 | 399 |
| apache_post_operative | int64 | 0 | 2 |
| arf_apache | float64 | 715 | 2 |
| gcs_eyes_apache | float64 | 1,901 | 4 |
| gcs_motor_apache | float64 | 1,901 | 6 |
| gcs_unable_apache | float64 | 1,037 | 2 |
| gcs_verbal_apache | float64 | 1,901 | 5 |
| heart_rate_apache | float64 | 878 | 149 |
| intubated_apache | float64 | 715 | 2 |
| map_apache | float64 | 994 | 161 |
| resprate_apache | float64 | 1,234 | 74 |
| temp_apache | float64 | 4,108 | 191 |
| ventilated_apache | float64 | 715 | 2 |
| d1_diasbp_max | float64 | 165 | 120 |
| d1_diasbp_min | float64 | 165 | 78 |
| d1_diasbp_noninvasive_max | float64 | 1,040 | 120 |
| d1_diasbp_noninvasive_min | float64 | 1,040 | 78 |
| d1_heartrate_max | float64 | 145 | 120 |
| d1_heartrate_min | float64 | 145 | 154 |
| d1_mbp_max | float64 | 220 | 125 |
| d1_mbp_min | float64 | 220 | 91 |
| d1_mbp_noninvasive_max | float64 | 1,479 | 122 |
| d1_mbp_noninvasive_min | float64 | 1,479 | 91 |
| d1_resprate_max | float64 | 385 | 79 |
| d1_resprate_min | float64 | 385 | 55 |
| d1_spo2_max | float64 | 333 | 43 |
| d1_spo2_min | float64 | 333 | 101 |
| d1_sysbp_max | float64 | 159 | 143 |
| d1_sysbp_min | float64 | 159 | 120 |
| d1_sysbp_noninvasive_max | float64 | 1,027 | 143 |
| d1_sysbp_noninvasive_min | float64 | 1,027 | 120 |
| d1_temp_max | float64 | 2,324 | 186 |
| d1_temp_min | float64 | 2,324 | 209 |
| h1_diasbp_max | float64 | 3,619 | 107 |
| h1_diasbp_min | float64 | 3,619 | 92 |
| h1_diasbp_noninvasive_max | float64 | 7,350 | 108 |
| h1_diasbp_noninvasive_min | float64 | 7,350 | 93 |
| h1_heartrate_max | float64 | 2,790 | 119 |
| h1_heartrate_min | float64 | 2,790 | 109 |
| h1_mbp_max | float64 | 4,639 | 117 |
| h1_mbp_min | float64 | 4,639 | 107 |
| h1_mbp_noninvasive_max | float64 | 9,084 | 115 |
| h1_mbp_noninvasive_min | float64 | 9,084 | 107 |
| h1_resprate_max | float64 | 4,357 | 50 |
| h1_resprate_min | float64 | 4,357 | 91 |
| h1_spo2_max | float64 | 4,185 | 72 |
| h1_spo2_min | float64 | 4,185 | 100 |
| h1_sysbp_max | float64 | 3,611 | 149 |
| h1_sysbp_min | float64 | 3,611 | 142 |
| h1_sysbp_noninvasive_max | float64 | 7,341 | 149 |
| h1_sysbp_noninvasive_min | float64 | 7,341 | 143 |
| d1_glucose_max | float64 | 5,807 | 538 |
| d1_glucose_min | float64 | 5,807 | 256 |
| d1_potassium_max | float64 | 9,585 | 100 |
| d1_potassium_min | float64 | 9,585 | 116 |
| apache_4a_hospital_death_prob | float64 | 7,947 | 101 |
| apache_4a_icu_death_prob | float64 | 7,947 | 99 |
| aids | float64 | 715 | 2 |
| cirrhosis | float64 | 715 | 2 |
| diabetes_mellitus | float64 | 715 | 2 |
| hepatic_failure | float64 | 715 | 2 |
| immunosuppression | float64 | 715 | 2 |
| leukemia | float64 | 715 | 2 |
| lymphoma | float64 | 715 | 2 |
| solid_tumor_with_metastasis | float64 | 715 | 2 |
| apache_3j_bodysystem | object | 1,662 | 11 |
| apache_2_bodysystem | object | 1,662 | 10 |
| Unnamed: 83 | float64 | 91,713 | 0 |
| hospital_death | int64 | 0 | 2 |

### Inferred clinical/data roles

- Identifiers: `encounter_id`, `patient_id`
- Timestamps: none detected
- Targets/outcomes: `apache_4a_hospital_death_prob`, `apache_4a_icu_death_prob`, `hospital_death`
- Vital signs: `heart_rate_apache`, `map_apache`, `resprate_apache`, `temp_apache`, `d1_diasbp_max`, `d1_diasbp_min`, `d1_diasbp_noninvasive_max`, `d1_diasbp_noninvasive_min`, `d1_heartrate_max`, `d1_heartrate_min`, `d1_mbp_max`, `d1_mbp_min`, `d1_mbp_noninvasive_max`, `d1_mbp_noninvasive_min`, `d1_resprate_max`, `d1_resprate_min`, `d1_spo2_max`, `d1_spo2_min`, `d1_sysbp_max`, `d1_sysbp_min`, `d1_sysbp_noninvasive_max`, `d1_sysbp_noninvasive_min`, `d1_temp_max`, `d1_temp_min`, `h1_diasbp_max`, `h1_diasbp_min`, `h1_diasbp_noninvasive_max`, `h1_diasbp_noninvasive_min`, `h1_heartrate_max`, `h1_heartrate_min`, `h1_mbp_max`, `h1_mbp_min`, `h1_mbp_noninvasive_max`, `h1_mbp_noninvasive_min`, `h1_resprate_max`, `h1_resprate_min`, `h1_spo2_max`, `h1_spo2_min`, `h1_sysbp_max`, `h1_sysbp_min`, `h1_sysbp_noninvasive_max`, `h1_sysbp_noninvasive_min`
- Laboratory variables: `d1_glucose_max`, `d1_glucose_min`, `d1_potassium_max`, `d1_potassium_min`
- Demographics: `age`, `bmi`, `ethnicity`, `gender`, `height`, `weight`
- Symptoms: none detected
- Diagnoses: `apache_2_diagnosis`, `apache_3j_diagnosis`, `apache_3j_bodysystem`, `apache_2_bodysystem`
- Medications/interventions: `elective_surgery`, `intubated_apache`, `ventilated_apache`

### Numerical distributions

Values are `count / mean / std / min / 25% / median / 75% / max`.

| Variable | Distribution |
|---|---|
| encounter_id | 9.17e+04 / 6.56e+04 / 3.78e+04 / 1 / 3.29e+04 / 6.57e+04 / 9.83e+04 / 1.31e+05 |
| patient_id | 9.17e+04 / 6.55e+04 / 3.78e+04 / 1 / 3.28e+04 / 6.54e+04 / 9.83e+04 / 1.31e+05 |
| hospital_id | 9.17e+04 / 106 / 62.9 / 2 / 47 / 109 / 161 / 204 |
| age | 8.75e+04 / 62.3 / 16.8 / 16 / 52 / 65 / 75 / 89 |
| bmi | 8.83e+04 / 29.2 / 8.28 / 14.8 / 23.6 / 27.7 / 32.9 / 67.8 |
| elective_surgery | 9.17e+04 / 0.184 / 0.387 / 0 / 0 / 0 / 0 / 1 |
| height | 9.04e+04 / 170 / 10.8 / 137 / 162 / 170 / 178 / 196 |
| icu_id | 9.17e+04 / 508 / 229 / 82 / 369 / 504 / 679 / 927 |
| pre_icu_los_days | 9.17e+04 / 0.836 / 2.49 / -24.9 / 0.0354 / 0.139 / 0.409 / 159 |
| weight | 8.9e+04 / 84 / 25 / 38.6 / 66.8 / 80.3 / 97.1 / 186 |
| apache_2_diagnosis | 9.01e+04 / 185 / 86.1 / 101 / 113 / 122 / 301 / 308 |
| apache_3j_diagnosis | 9.06e+04 / 558 / 463 / 0.01 / 203 / 409 / 703 / 2.2e+03 |
| apache_post_operative | 9.17e+04 / 0.201 / 0.401 / 0 / 0 / 0 / 0 / 1 |
| arf_apache | 9.1e+04 / 0.028 / 0.165 / 0 / 0 / 0 / 0 / 1 |
| gcs_eyes_apache | 8.98e+04 / 3.47 / 0.952 / 1 / 3 / 4 / 4 / 4 |
| gcs_motor_apache | 8.98e+04 / 5.47 / 1.29 / 1 / 6 / 6 / 6 / 6 |
| gcs_unable_apache | 9.07e+04 / 0.00953 / 0.0971 / 0 / 0 / 0 / 0 / 1 |
| gcs_verbal_apache | 8.98e+04 / 3.99 / 1.56 / 1 / 4 / 5 / 5 / 5 |
| heart_rate_apache | 9.08e+04 / 99.7 / 30.9 / 30 / 86 / 104 / 120 / 178 |
| intubated_apache | 9.1e+04 / 0.151 / 0.358 / 0 / 0 / 0 / 0 / 1 |
| map_apache | 9.07e+04 / 88 / 42 / 40 / 54 / 67 / 125 / 200 |
| resprate_apache | 9.05e+04 / 25.8 / 15.1 / 4 / 11 / 28 / 36 / 60 |
| temp_apache | 8.76e+04 / 36.4 / 0.833 / 32.1 / 36.2 / 36.5 / 36.7 / 39.7 |
| ventilated_apache | 9.1e+04 / 0.326 / 0.469 / 0 / 0 / 0 / 1 / 1 |
| d1_diasbp_max | 9.15e+04 / 88.5 / 19.8 / 46 / 75 / 86 / 99 / 165 |
| d1_diasbp_min | 9.15e+04 / 50.2 / 13.3 / 13 / 42 / 50 / 58 / 90 |
| d1_diasbp_noninvasive_max | 9.07e+04 / 88.6 / 19.8 / 46 / 75 / 87 / 99 / 165 |
| d1_diasbp_noninvasive_min | 9.07e+04 / 50.2 / 13.3 / 13 / 42 / 50 / 58 / 90 |
| d1_heartrate_max | 9.16e+04 / 103 / 22 / 58 / 87 / 101 / 116 / 177 |
| d1_heartrate_min | 9.16e+04 / 70.3 / 17.1 / 0 / 60 / 69 / 81 / 175 |
| d1_mbp_max | 9.15e+04 / 105 / 20.8 / 60 / 90 / 102 / 116 / 184 |
| d1_mbp_min | 9.15e+04 / 64.9 / 15.7 / 22 / 55 / 64 / 75 / 112 |
| d1_mbp_noninvasive_max | 9.02e+04 / 105 / 20.7 / 60 / 90 / 102 / 116 / 181 |
| d1_mbp_noninvasive_min | 9.02e+04 / 64.9 / 15.7 / 22 / 55 / 64 / 75 / 112 |
| d1_resprate_max | 9.13e+04 / 28.9 / 10.7 / 14 / 22 / 26 / 32 / 92 |
| d1_resprate_min | 9.13e+04 / 12.8 / 5.06 / 0 / 10 / 13 / 16 / 100 |
| d1_spo2_max | 9.14e+04 / 99.2 / 1.79 / 0 / 99 / 100 / 100 / 100 |
| d1_spo2_min | 9.14e+04 / 90.5 / 10 / 0 / 89 / 92 / 95 / 100 |
| d1_sysbp_max | 9.16e+04 / 148 / 25.7 / 90 / 130 / 146 / 164 / 232 |
| d1_sysbp_min | 9.16e+04 / 96.9 / 20.7 / 41 / 83 / 96 / 110 / 160 |
| d1_sysbp_noninvasive_max | 9.07e+04 / 148 / 25.8 / 90 / 130 / 146 / 164 / 232 |
| d1_sysbp_noninvasive_min | 9.07e+04 / 97 / 20.7 / 41 / 84 / 96 / 110 / 160 |
| d1_temp_max | 8.94e+04 / 37.3 / 0.693 / 35.1 / 36.9 / 37.1 / 37.6 / 39.9 |
| d1_temp_min | 8.94e+04 / 36.3 / 0.745 / 31.9 / 36.1 / 36.4 / 36.7 / 37.8 |
| h1_diasbp_max | 8.81e+04 / 75.4 / 18.4 / 37 / 62 / 74 / 86 / 143 |
| h1_diasbp_min | 8.81e+04 / 62.8 / 16.4 / 22 / 52 / 62 / 73 / 113 |
| h1_diasbp_noninvasive_max | 8.44e+04 / 75.8 / 18.5 / 37 / 63 / 74 / 87 / 144 |
| h1_diasbp_noninvasive_min | 8.44e+04 / 63.3 / 16.4 / 22 / 52 / 62 / 74 / 114 |
| h1_heartrate_max | 8.89e+04 / 92.2 / 21.8 / 46 / 77 / 90 / 106 / 164 |
| h1_heartrate_min | 8.89e+04 / 83.7 / 20.3 / 36 / 69 / 82 / 97 / 144 |
| h1_mbp_max | 8.71e+04 / 91.6 / 20.5 / 49 / 77 / 90 / 104 / 165 |
| h1_mbp_min | 8.71e+04 / 79.4 / 19.1 / 32 / 66 / 78 / 92 / 138 |
| h1_mbp_noninvasive_max | 8.26e+04 / 91.6 / 20.6 / 49 / 77 / 90 / 104 / 163 |
| h1_mbp_noninvasive_min | 8.26e+04 / 79.7 / 19.2 / 32 / 66 / 79 / 92 / 138 |
| h1_resprate_max | 8.74e+04 / 22.6 / 7.52 / 10 / 18 / 21 / 26 / 59 |
| h1_resprate_min | 8.74e+04 / 17.2 / 6.07 / 0 / 14 / 16 / 20 / 189 |
| h1_spo2_max | 8.75e+04 / 98 / 3.21 / 0 / 97 / 99 / 100 / 100 |
| h1_spo2_min | 8.75e+04 / 95.2 / 6.63 / 0 / 94 / 96 / 99 / 100 |
| h1_sysbp_max | 8.81e+04 / 133 / 27.6 / 75 / 113 / 131 / 150 / 223 |
| h1_sysbp_min | 8.81e+04 / 116 / 26.5 / 53 / 98 / 115 / 134 / 194 |
| h1_sysbp_noninvasive_max | 8.44e+04 / 133 / 27.7 / 75 / 113 / 130 / 150 / 223 |
| h1_sysbp_noninvasive_min | 8.44e+04 / 117 / 26.6 / 53 / 98 / 115 / 134 / 195 |
| d1_glucose_max | 8.59e+04 / 175 / 86.7 / 73 / 117 / 150 / 201 / 611 |
| d1_glucose_min | 8.59e+04 / 114 / 38.3 / 33 / 91 / 107 / 131 / 288 |
| d1_potassium_max | 8.21e+04 / 4.25 / 0.667 / 2.8 / 3.8 / 4.2 / 4.6 / 7 |
| d1_potassium_min | 8.21e+04 / 3.93 / 0.58 / 2.4 / 3.6 / 3.9 / 4.3 / 5.8 |
| apache_4a_hospital_death_prob | 8.38e+04 / 0.0868 / 0.248 / -1 / 0.02 / 0.05 / 0.13 / 0.99 |
| apache_4a_icu_death_prob | 8.38e+04 / 0.044 / 0.217 / -1 / 0.01 / 0.02 / 0.06 / 0.97 |
| aids | 9.1e+04 / 0.000857 / 0.0293 / 0 / 0 / 0 / 0 / 1 |
| cirrhosis | 9.1e+04 / 0.0157 / 0.124 / 0 / 0 / 0 / 0 / 1 |
| diabetes_mellitus | 9.1e+04 / 0.225 / 0.418 / 0 / 0 / 0 / 0 / 1 |
| hepatic_failure | 9.1e+04 / 0.013 / 0.113 / 0 / 0 / 0 / 0 / 1 |
| immunosuppression | 9.1e+04 / 0.0262 / 0.16 / 0 / 0 / 0 / 0 / 1 |
| leukemia | 9.1e+04 / 0.00707 / 0.0838 / 0 / 0 / 0 / 0 / 1 |
| lymphoma | 9.1e+04 / 0.00413 / 0.0641 / 0 / 0 / 0 / 0 / 1 |
| solid_tumor_with_metastasis | 9.1e+04 / 0.0206 / 0.142 / 0 / 0 / 0 / 0 / 1 |
| Unnamed: 83 | 0 / nan / nan / nan / nan / nan / nan / nan |
| hospital_death | 9.17e+04 / 0.0863 / 0.281 / 0 / 0 / 0 / 0 / 1 |

### Categorical distributions

Top values are shown as `value: count` (up to 10 per field).

| Variable | Top values |
|---|---|
| ethnicity | Caucasian: 70684; African American: 9547; Other/Unknown: 4374; Hispanic: 3796; <MISSING>: 1395; Asian: 1129; Native American: 788 |
| gender | M: 49469; F: 42219; <MISSING>: 25 |
| icu_admit_source | Accident & Emergency: 54060; Operating Room / Recovery: 18713; Floor: 15611; Other Hospital: 2358; Other ICU: 859; <MISSING>: 112 |
| icu_stay_type | admit: 86183; transfer: 4970; readmit: 560 |
| icu_type | Med-Surg ICU: 50586; MICU: 7695; Neuro ICU: 7675; CCU-CTICU: 7156; SICU: 5209; Cardiac ICU: 4776; CSICU: 4613; CTICU: 4003 |
| apache_3j_bodysystem | Cardiovascular: 29999; Neurological: 11896; Sepsis: 11740; Respiratory: 11609; Gastrointestinal: 9026; Metabolic: 7650; Trauma: 3842; Genitourinary: 2172; <MISSING>: 1662; Musculoskeletal/Skin: 1166 |
| apache_2_bodysystem | Cardiovascular: 38816; Neurologic: 11896; Respiratory: 11609; Gastrointestinal: 9026; Metabolic: 7650; Trauma: 3842; Undefined diagnoses: 3768; Renal/Genitourinary: 2460; <MISSING>: 1662; Haematologic: 638 |

### Clinical usefulness

Primary source. Supplies real ICU encounter demographics, first-hour/day physiological summaries, neurological proxies, comorbidities, and the documented `hospital_death` outcome. Suitable for profile initialization and an encounter-level mortality model.

### Limitations

No timestamped bedside waveform/telemetry; extrema summarize windows and do not define ordering. Missing values are substantial for some variables. Data provenance/licensing and representativeness require review before any use beyond education. Patient IDs must not be linked outside this table.
