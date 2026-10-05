from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY, target TEXT NOT NULL, created_at TEXT NOT NULL,
                score INTEGER NOT NULL, risk TEXT NOT NULL, findings TEXT NOT NULL
            )""")

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save_scan(self, scan_id: str, target: str, result: dict) -> None:
        with self.connect() as connection:
            connection.execute("INSERT OR REPLACE INTO scans VALUES (?, ?, datetime('now'), ?, ?, ?)", (scan_id, target, result["score"], result["risk"], json.dumps(result)))

    def get_scan(self, scan_id: str) -> dict | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
        if not row:
            return None
        result = json.loads(row["findings"])
        return {"scan_id": row["scan_id"], "target": row["target"], "status": "completed", "progress": 100, "created_at": row["created_at"], "result": result}

    def history(self) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute("SELECT scan_id, target, created_at, score, risk FROM scans ORDER BY created_at DESC LIMIT 20").fetchall()
        return [dict(row) for row in rows]

    def stats(self) -> dict:
        with self.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS total, COALESCE(AVG(score), 0) AS average_score FROM scans").fetchone()
            counts = connection.execute("SELECT risk, COUNT(*) AS count FROM scans GROUP BY risk").fetchall()
        return {"total_scans": row["total"], "average_score": round(row["average_score"], 1), "risk_distribution": {item["risk"]: item["count"] for item in counts}}
