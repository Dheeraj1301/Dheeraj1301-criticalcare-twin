"""Train and compare reproducible models for the documented hospital_death outcome."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score, roc_curve, precision_recall_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data" / "processed" / "icu_model_table.csv"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
SEED = 42


def metrics(model, X, y):
    p = model.predict_proba(X)[:, 1]
    pred = (p >= .25).astype(int)
    fpr, tpr, _ = roc_curve(y, p)
    pr, rc, _ = precision_recall_curve(y, p)
    return {"roc_auc": roc_auc_score(y, p), "pr_auc": average_precision_score(y, p), "precision_at_0.25": precision_score(y, pred, zero_division=0), "recall_at_0.25": recall_score(y, pred), "f1_at_0.25": f1_score(y, pred), "brier": brier_score_loss(y, p), "confusion_matrix_at_0.25": confusion_matrix(y, pred).tolist(), "roc_curve": {"fpr": fpr[::max(1, len(fpr)//100)].tolist(), "tpr": tpr[::max(1, len(tpr)//100)].tolist()}, "pr_curve": {"precision": pr[::max(1, len(pr)//100)].tolist(), "recall": rc[::max(1, len(rc)//100)].tolist()}}


def main() -> None:
    df = pd.read_csv(TABLE)
    features = [c for c in df.columns if c != "hospital_death"]
    X, y = df[features], df.hospital_death
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, stratify=y, random_state=SEED)
    candidates = {
        "logistic_regression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED)),
        "random_forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=180, max_depth=10, min_samples_leaf=8, class_weight="balanced", n_jobs=-1, random_state=SEED)),
    }
    results = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        results[name] = metrics(model, X_test, y_test)
        print(name, {k: round(v, 4) for k, v in results[name].items() if isinstance(v, float)})
    selected_name = max(results, key=lambda n: results[n]["roc_auc"])
    selected = candidates[selected_name]
    sample = X_test.sample(min(3000, len(X_test)), random_state=SEED)
    perm = permutation_importance(selected, sample, y_test.loc[sample.index], n_repeats=3, scoring="roc_auc", random_state=SEED, n_jobs=-1)
    importance = dict(zip(features, np.maximum(perm.importances_mean, 0).tolist()))
    medians = X_train.median(numeric_only=True).to_dict()
    metadata = {
        "objective": "Estimate the documented encounter-level hospital_death outcome; not critical-care deterioration forecasting.",
        "selected_model": selected_name, "features": features, "target": "hospital_death", "seed": SEED,
        "split": "80/20 stratified random encounter split", "train_rows": len(X_train), "test_rows": len(X_test),
        "positive_rate": float(y.mean()), "trained_at": datetime.now(timezone.utc).isoformat(), "candidates": results,
        "limitations": ["No external or temporal validation", "Encounter summaries may occur after admission", "Not clinically validated", "Feature importance is associational"],
    }
    MODELS.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)
    joblib.dump({"model": selected, "features": features, "feature_importance": importance, "medians": medians, "metadata": metadata}, MODELS / "hospital_mortality.joblib")
    (MODELS / "hospital_mortality_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    report = ["# Model Evaluation", "", "The supervised task is the dataset's documented `hospital_death` outcome. It is not relabelled as deterioration.", "", f"- Selected model: **{selected_name}**", f"- Rows: {len(df):,}; positive rate: {y.mean():.3f}", "- Validation: 80/20 stratified random encounter split (seed 42)", "- Leakage controls: APACHE mortality probabilities, encounter/patient IDs, and target-adjacent death fields excluded.", "", "| Model | ROC-AUC | PR-AUC | Precision@0.25 | Recall@0.25 | F1@0.25 | Brier |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, m in results.items(): report.append(f"| {name} | {m['roc_auc']:.3f} | {m['pr_auc']:.3f} | {m['precision_at_0.25']:.3f} | {m['recall_at_0.25']:.3f} | {m['f1_at_0.25']:.3f} | {m['brier']:.3f} |")
    report += ["", "## Limitations", "", "This internally validated educational model is not calibrated or validated for clinical use. Random encounter splitting does not measure future-site generalization. Feature importance reflects association, not causality."]
    (REPORTS / "MODEL_EVALUATION.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__": main()

