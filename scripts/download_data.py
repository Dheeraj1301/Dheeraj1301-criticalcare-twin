"""Download the three required public Kaggle datasets without altering source files."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import kagglehub

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
DATASETS = {
    "patient": "mitishaagarwal/patient",
    "disease_symptoms_profile": "uom190346a/disease-symptoms-and-patient-profile-dataset",
    "healthcare_analytics": "abbas829/healthcare-patient-analytics-dataset",
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    manifest = {"downloaded_at": datetime.now(timezone.utc).isoformat(), "datasets": {}}
    for key, handle in DATASETS.items():
        cache_path = Path(kagglehub.dataset_download(handle))
        destination = RAW / key
        destination.mkdir(parents=True, exist_ok=True)
        copied = []
        for source in cache_path.rglob("*"):
            if source.is_file():
                target = destination / source.relative_to(cache_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                copied.append(str(target.relative_to(ROOT)))
        manifest["datasets"][key] = {"handle": handle, "cache_path": str(cache_path), "files": copied}
        print(f"{handle}: {cache_path}")
    (META / "download_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

