"""FastAPI cloud service. Runs locally for demonstration and is deployable unchanged."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("CCT_CLOUD_DB", "data/cloud_twin.sqlite"))


class CloudTwinEnvelope(BaseModel):
    message_id: str
    site_id: str
    patient_key: str = Field(min_length=12)
    twin_id: str
    twin_version: int
    timestamp: str
    state: dict[str, float]
    derived_state: dict[str, float]
    risk: dict[str, Any]
    uncertainty: dict[str, Any]
    provenance_class: str


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS cloud_twin_snapshots (
      message_id TEXT PRIMARY KEY, site_id TEXT, patient_key TEXT, twin_id TEXT,
      twin_version INTEGER, observed_at TEXT, received_at TEXT, payload_json TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_cloud_patient_time ON cloud_twin_snapshots(patient_key, observed_at);
    """)
    return db


app = FastAPI(title="CRITICALCARE-TWIN Cloud Service", version="1.0.0")


@app.get("/health")
def health():
    with connect() as db:
        count = db.execute("SELECT COUNT(*) FROM cloud_twin_snapshots").fetchone()[0]
    return {"status": "online", "stored_snapshots": count, "mode": "local cloud-service emulator"}


@app.post("/v1/twins/sync", status_code=202)
def sync_twin(envelope: CloudTwinEnvelope):
    payload = envelope.model_dump(mode="json")
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO cloud_twin_snapshots VALUES (?,?,?,?,?,?,?,?)", (envelope.message_id, envelope.site_id, envelope.patient_key, envelope.twin_id, envelope.twin_version, envelope.timestamp, datetime.now(timezone.utc).isoformat(), json.dumps(payload)))
    return {"accepted": True, "message_id": envelope.message_id}


@app.get("/v1/twins/{patient_key}/latest")
def latest(patient_key: str):
    with connect() as db:
        row = db.execute("SELECT payload_json FROM cloud_twin_snapshots WHERE patient_key=? ORDER BY observed_at DESC LIMIT 1", (patient_key,)).fetchone()
    if not row:
        raise HTTPException(404, "No synchronized twin found")
    return json.loads(row[0])


@app.get("/v1/fleet/summary")
def fleet_summary():
    with connect() as db:
        total = db.execute("SELECT COUNT(*) FROM cloud_twin_snapshots").fetchone()[0]
        patients = db.execute("SELECT COUNT(DISTINCT patient_key) FROM cloud_twin_snapshots").fetchone()[0]
        sites = db.execute("SELECT COUNT(DISTINCT site_id) FROM cloud_twin_snapshots").fetchone()[0]
    return {"snapshots": total, "pseudonymous_patients": patients, "edge_sites": sites}

