"""Offline-safe edge-to-cloud synchronization for de-identified twin summaries."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx


class EdgeGateway:
    def __init__(self, cloud_url: str = "http://127.0.0.1:8000", outbox_path: str | Path = "data/edge_outbox.sqlite", site_id: str = "DEMO-EDGE-01", salt: str = "criticalcare-twin-demo") -> None:
        self.cloud_url = cloud_url.rstrip("/")
        self.path = Path(outbox_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.site_id = site_id
        self.salt = salt
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS outbox (
                message_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload_json TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT
            );
            CREATE TABLE IF NOT EXISTS sync_audit (
                message_id TEXT PRIMARY KEY, synced_at TEXT NOT NULL, cloud_status INTEGER NOT NULL
            );
            """)

    def connect(self):
        return sqlite3.connect(self.path)

    def patient_key(self, patient_id: str) -> str:
        return hashlib.sha256(f"{self.salt}:{patient_id}".encode()).hexdigest()[:20]

    def build_payload(self, twin, snapshot) -> dict:
        return {
            "message_id": str(uuid4()),
            "site_id": self.site_id,
            "patient_key": self.patient_key(twin.profile.patient_id),
            "twin_id": twin.twin_id,
            "twin_version": snapshot.twin_version,
            "timestamp": snapshot.timestamp.isoformat(),
            "state": snapshot.state.vector(),
            "derived_state": snapshot.derived_state,
            "risk": snapshot.risk_state.model_dump(mode="json"),
            "uncertainty": snapshot.uncertainty.model_dump(mode="json"),
            "provenance_class": "SIMULATED" if snapshot.uncertainty.simulated_fraction else "OBSERVED_OR_ESTIMATED",
        }

    def publish(self, twin, snapshot) -> bool:
        payload = self.build_payload(twin, snapshot)
        if self._send(payload):
            return True
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO outbox(message_id,created_at,payload_json,attempts,last_error) VALUES (?,?,?,?,?)", (payload["message_id"], datetime.now(timezone.utc).isoformat(), json.dumps(payload), 1, "cloud unavailable"))
        return False

    def _send(self, payload: dict) -> bool:
        try:
            response = httpx.post(f"{self.cloud_url}/v1/twins/sync", json=payload, timeout=1.5)
            if response.is_success:
                with self.connect() as db:
                    db.execute("INSERT OR REPLACE INTO sync_audit VALUES (?,?,?)", (payload["message_id"], datetime.now(timezone.utc).isoformat(), response.status_code))
                return True
        except httpx.HTTPError:
            pass
        return False

    def flush(self, limit: int = 100) -> dict[str, int]:
        with self.connect() as db:
            rows = db.execute("SELECT message_id,payload_json FROM outbox ORDER BY created_at LIMIT ?", (limit,)).fetchall()
        sent = 0
        for message_id, payload_json in rows:
            payload = json.loads(payload_json)
            if self._send(payload):
                with self.connect() as db:
                    db.execute("DELETE FROM outbox WHERE message_id=?", (message_id,))
                sent += 1
            else:
                with self.connect() as db:
                    db.execute("UPDATE outbox SET attempts=attempts+1,last_error='cloud unavailable' WHERE message_id=?", (message_id,))
                break
        return {"sent": sent, "remaining": self.status()["queued"]}

    def status(self) -> dict:
        with self.connect() as db:
            queued = db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
            synced = db.execute("SELECT COUNT(*) FROM sync_audit").fetchone()[0]
        online = False
        try:
            online = httpx.get(f"{self.cloud_url}/health", timeout=.6).is_success
        except httpx.HTTPError:
            pass
        return {"online": online, "queued": queued, "synced": synced, "site_id": self.site_id, "cloud_url": self.cloud_url}

