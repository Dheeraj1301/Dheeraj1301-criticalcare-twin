"""Offline-safe edge synchronization to FIWARE Orion-LD and MinIO."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.cloud.object_store import SnapshotObjectStore
from src.cloud.orion import OrionDigitalTwinClient


class EdgeGateway:
    def __init__(self, orion_url: str | None = None, outbox_path: str | Path = "data/edge_outbox.sqlite", site_id: str | None = None, salt: str | None = None, orion_client=None, object_store=None) -> None:
        self.orion_url = orion_url or os.getenv("CCT_ORION_URL", "http://127.0.0.1:1026")
        self.path = Path(outbox_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.site_id = site_id or os.getenv("CCT_SITE_ID", "EDGE-01")
        self.salt = salt or os.getenv("CCT_PATIENT_SALT", "change-this-local-salt")
        self.orion = orion_client or OrionDigitalTwinClient(self.orion_url)
        self.object_store = object_store or self._default_store()
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS outbox (
                message_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload_json TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT
            );
            CREATE TABLE IF NOT EXISTS sync_audit (
                message_id TEXT PRIMARY KEY, synced_at TEXT NOT NULL, framework TEXT NOT NULL, object_key TEXT
            );
            """)

    @staticmethod
    def _default_store():
        return SnapshotObjectStore(
            bucket=os.getenv("CCT_S3_BUCKET", "criticalcare-twin"),
            endpoint_url=os.getenv("CCT_S3_ENDPOINT", "http://127.0.0.1:9000"),
            access_key=os.getenv("CCT_S3_ACCESS_KEY", "criticalcare"),
            secret_key=os.getenv("CCT_S3_SECRET_KEY", "criticalcare-local"),
        )

    def connect(self):
        return sqlite3.connect(self.path)

    def patient_key(self, patient_id: str) -> str:
        return hashlib.sha256(f"{self.salt}:{patient_id}".encode()).hexdigest()[:20]

    def build_payload(self, twin, snapshot) -> dict:
        return {
            "message_id": str(uuid4()), "site_id": self.site_id,
            "patient_key": self.patient_key(twin.profile.patient_id), "twin_id": twin.twin_id,
            "twin_version": snapshot.twin_version, "timestamp": snapshot.timestamp.isoformat(),
            "state": snapshot.state.vector(), "derived_state": snapshot.derived_state,
            "risk": snapshot.risk_state.model_dump(mode="json"),
            "uncertainty": snapshot.uncertainty.model_dump(mode="json"),
            "provenance_class": "OBSERVED_OR_MODEL_ESTIMATED",
        }

    def publish(self, twin, snapshot) -> bool:
        payload = self.build_payload(twin, snapshot)
        try:
            self._send(payload)
            return True
        except Exception as exc:
            with self.connect() as db:
                db.execute("INSERT OR REPLACE INTO outbox(message_id,created_at,payload_json,attempts,last_error) VALUES (?,?,?,?,?)", (payload["message_id"], datetime.now(timezone.utc).isoformat(), json.dumps(payload), 1, str(exc)[:500]))
            return False

    def _send(self, payload: dict) -> None:
        entity_id = self.orion.upsert(payload)
        object_key = self.object_store.archive(payload["patient_key"], payload["twin_version"], payload)
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO sync_audit VALUES (?,?,?,?)", (payload["message_id"], datetime.now(timezone.utc).isoformat(), entity_id, object_key))

    def flush(self, limit: int = 100) -> dict[str, int]:
        with self.connect() as db:
            rows = db.execute("SELECT message_id,payload_json FROM outbox ORDER BY created_at LIMIT ?", (limit,)).fetchall()
        sent = 0
        for message_id, payload_json in rows:
            try:
                self._send(json.loads(payload_json))
            except Exception as exc:
                with self.connect() as db:
                    db.execute("UPDATE outbox SET attempts=attempts+1,last_error=? WHERE message_id=?", (str(exc)[:500], message_id))
                break
            with self.connect() as db:
                db.execute("DELETE FROM outbox WHERE message_id=?", (message_id,))
            sent += 1
        return {"sent": sent, "remaining": self.status()["queued"]}

    def status(self) -> dict:
        with self.connect() as db:
            queued = db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
            synced = db.execute("SELECT COUNT(*) FROM sync_audit").fetchone()[0]
        orion_online = self.orion.online()
        storage_online = self.object_store.online()
        return {"online": orion_online and storage_online, "orion_online": orion_online, "storage_online": storage_online, "queued": queued, "synced": synced, "site_id": self.site_id, "framework": "FIWARE Orion-LD / NGSI-LD", "storage": "MinIO / S3-compatible", "orion_url": self.orion_url}
