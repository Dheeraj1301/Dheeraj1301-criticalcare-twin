"""Generate a reproducible, schema-first audit of every downloaded table."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "reports" / "DATASET_AUDIT.md"

SOURCES = {
    "patient": "mitishaagarwal/patient",
    "disease_symptoms_profile": "uom190346a/disease-symptoms-and-patient-profile-dataset",
    "healthcare_analytics": "abbas829/healthcare-patient-analytics-dataset",
}


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def inferred_roles(columns: list[str]) -> dict[str, list[str]]:
    lowered = {c: c.lower() for c in columns}
    pick = lambda words: [c for c, x in lowered.items() if any(w in x for w in words)]
    return {
        "Identifiers": pick(["patient_id", "encounter_id"]),
        "Timestamps": pick(["date", "time", "timestamp"]),
        "Targets/outcomes": pick(["death", "outcome", "readmission", "recovery"]),
        "Vital signs": pick(["heart", "heartrate", "sysbp", "diasbp", "mbp", "map_", "resprate", "spo2", "temp"]),
        "Laboratory variables": pick(["glucose", "potassium", "cholesterol"]),
        "Demographics": pick(["age", "gender", "ethnicity", "height", "weight", "bmi"]),
        "Symptoms": pick(["fever", "cough", "fatigue", "difficulty"]),
        "Diagnoses": pick(["diagnosis", "disease", "bodysystem"]),
        "Medications/interventions": pick(["treatment", "intubat", "ventilat", "surgery"]),
    }


def main() -> None:
    files = [p for p in RAW.rglob("*") if p.suffix.lower() in {".csv", ".xlsx", ".xls"}]
    lines = [
        "# Dataset Audit",
        "",
        "Generated from the downloaded files; no schemas were assumed in advance.",
        "",
        "## Cross-dataset decision",
        "",
        "The datasets are **not joined**. The ICU table has `patient_id`, but the symptom table has no identifier and the analytics table's independently generated `patient_id` belongs to another source. Matching similarly named demographic fields would create false patient linkage. Each source therefore has a separate role.",
        "",
    ]
    for path in files:
        key = path.relative_to(RAW).parts[0]
        df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
        lines += [
            f"## {path.name}", "",
            f"- Dataset source: `{SOURCES.get(key, key)}`",
            f"- Local file: `{path.relative_to(ROOT).as_posix()}`",
            f"- Rows: {len(df):,}",
            f"- Columns: {len(df.columns)}",
            f"- Duplicate rows: {int(df.duplicated().sum()):,}",
            f"- Longitudinal status: {'Time-stamped administrative visits, but each patient ID occurs once; cross-sectional for this download.' if 'visit_date' in df else 'Cross-sectional encounter-level table; min/max windows are not timestamped sequences.' if 'encounter_id' in df else 'Cross-sectional disease/profile examples.'}",
            "",
            "### Exact schema and missingness", "",
            "| Column | Inferred dtype | Missing | Unique |", "|---|---:|---:|---:|",
        ]
        for col in df.columns:
            lines.append(f"| {esc(col)} | {df[col].dtype} | {int(df[col].isna().sum()):,} | {df[col].nunique(dropna=True):,} |")
        lines += ["", "### Inferred clinical/data roles", ""]
        for label, values in inferred_roles(list(df.columns)).items():
            lines.append(f"- {label}: {', '.join(f'`{v}`' for v in values) if values else 'none detected'}")
        numeric = df.select_dtypes(include="number")
        lines += ["", "### Numerical distributions", "", "Values are `count / mean / std / min / 25% / median / 75% / max`.", "", "| Variable | Distribution |", "|---|---|"]
        for col in numeric.columns:
            s = numeric[col].describe(percentiles=[.25, .5, .75])
            vals = [s.get(x, float("nan")) for x in ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
            lines.append(f"| {esc(col)} | {' / '.join(f'{v:.3g}' for v in vals)} |")
        categoricals = df.select_dtypes(exclude="number")
        lines += ["", "### Categorical distributions", "", "Top values are shown as `value: count` (up to 10 per field).", "", "| Variable | Top values |", "|---|---|"]
        for col in categoricals.columns:
            counts = df[col].fillna("<MISSING>").astype(str).value_counts().head(10)
            lines.append(f"| {esc(col)} | {esc('; '.join(f'{k}: {v}' for k, v in counts.items()))} |")
        if key == "patient":
            usefulness = "Primary source. Supplies real ICU encounter demographics, first-hour/day physiological summaries, neurological proxies, comorbidities, and the documented `hospital_death` outcome. Suitable for profile initialization and an encounter-level mortality model."
            limitations = "No timestamped bedside waveform/telemetry; extrema summarize windows and do not define ordering. Missing values are substantial for some variables. Data provenance/licensing and representativeness require review before any use beyond education. Patient IDs must not be linked outside this table."
        elif key == "disease_symptoms_profile":
            usefulness = "Supplementary source for demonstrating categorical symptom/disease context and for discussing a separate positive/negative outcome task. It is not used to invent ICU physiology."
            limitations = "Small, duplicated, cross-sectional examples; no patient ID or timestamps; ambiguous meaning of the outcome; categorical blood pressure/cholesterol; cannot be linked to ICU encounters."
        else:
            usefulness = "Administrative/provenance demonstration only: visit attributes, recovery score, and supplied readmission-risk values."
            limitations = "Appears synthetic/curated, has one row per patient, no physiology or measured clinical outcome for training, and identifiers are source-local. Not linked to the ICU dataset."
        lines += ["", "### Clinical usefulness", "", usefulness, "", "### Limitations", "", limitations, ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT} ({len(lines):,} lines)")


if __name__ == "__main__":
    main()

