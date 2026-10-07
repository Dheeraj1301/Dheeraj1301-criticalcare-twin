"""Launch the deployable cloud-service boundary locally."""
from __future__ import annotations
import sys
from pathlib import Path
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    uvicorn.run("src.cloud.service:app", host="127.0.0.1", port=8000, reload=False, app_dir=str(ROOT))
