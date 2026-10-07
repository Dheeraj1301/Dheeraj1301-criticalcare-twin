from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from .state import Observation, TwinEvent, TwinSnapshot


class TwinRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, profile_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS twins (twin_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL, version INTEGER, updated_at TEXT);
            CREATE TABLE IF NOT EXISTS observations (observation_id TEXT PRIMARY KEY, twin_id TEXT, patient_id TEXT, timestamp TEXT, payload_json TEXT);
            CREATE TABLE IF NOT EXISTS twin_snapshots (snapshot_id TEXT PRIMARY KEY, twin_id TEXT, patient_id TEXT, timestamp TEXT, version INTEGER, payload_json TEXT);
            CREATE TABLE IF NOT EXISTS twin_events (event_id TEXT PRIMARY KEY, twin_id TEXT, patient_id TEXT, timestamp TEXT, event_type TEXT, severity TEXT, payload_json TEXT);
            CREATE TABLE IF NOT EXISTS risk_predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, twin_id TEXT, timestamp TEXT, target TEXT, probability REAL, confidence REAL);
            CREATE TABLE IF NOT EXISTS simulation_runs (id TEXT PRIMARY KEY, twin_id TEXT, timestamp TEXT, payload_json TEXT);
            CREATE TABLE IF NOT EXISTS model_metadata (name TEXT PRIMARY KEY, payload_json TEXT);
            """)

    def save_patient(self, profile) -> None:
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO patients VALUES (?, ?)", (profile.patient_id, profile.model_dump_json()))

    def save_observation(self, observation: Observation, twin_id: str) -> None:
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO observations VALUES (?, ?, ?, ?, ?)", (observation.observation_id, twin_id, observation.patient_id, observation.timestamp.isoformat(), observation.model_dump_json()))

    def save_snapshot(self, snapshot: TwinSnapshot) -> None:
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO twin_snapshots VALUES (?, ?, ?, ?, ?, ?)", (snapshot.snapshot_id, snapshot.twin_id, snapshot.patient_id, snapshot.timestamp.isoformat(), snapshot.twin_version, snapshot.model_dump_json()))
            db.execute("INSERT OR REPLACE INTO twins VALUES (?, ?, ?, ?)", (snapshot.twin_id, snapshot.patient_id, snapshot.twin_version, snapshot.timestamp.isoformat()))
            db.execute("INSERT INTO risk_predictions(twin_id,timestamp,target,probability,confidence) VALUES (?,?,?,?,?)", (snapshot.twin_id, snapshot.timestamp.isoformat(), snapshot.risk_state.target, snapshot.risk_state.probability, snapshot.risk_state.confidence))

    def save_event(self, event: TwinEvent) -> None:
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO twin_events VALUES (?, ?, ?, ?, ?, ?, ?)", (event.event_id, event.twin_id, event.patient_id, event.timestamp.isoformat(), event.event_type, event.severity, json.dumps(event.payload, default=str)))

    def save_simulation(self, twin_id: str, result) -> str:
        run_id = str(uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO simulation_runs VALUES (?, ?, datetime('now'), ?)", (run_id, twin_id, result.model_dump_json()))
        return run_id

    def save_model_metadata(self, name: str, metadata: dict) -> None:
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO model_metadata VALUES (?, ?)", (name, json.dumps(metadata, default=str)))

    def snapshots(self, twin_id: str) -> list[TwinSnapshot]:
        with self.connect() as db:
            rows = db.execute("SELECT payload_json FROM twin_snapshots WHERE twin_id=? ORDER BY timestamp", (twin_id,)).fetchall()
        return [TwinSnapshot.model_validate_json(r[0]) for r in rows]

    def counts(self) -> dict[str, int]:
        names = ["patients", "twins", "observations", "twin_snapshots", "twin_events", "risk_predictions", "simulation_runs", "model_metadata"]
        with self.connect() as db:
            return {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in names}
