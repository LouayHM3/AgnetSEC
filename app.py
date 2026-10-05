from __future__ import annotations

import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from database import Database
from scanner import DemoScanner, calculate_score, risk_level

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("AGENTSEC_DB", BASE_DIR / "data" / "agentsec.db"))

app = Flask(__name__)
database = Database(DB_PATH)
scanner = DemoScanner()
active_scans: dict[str, dict] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_demo_scan(scan_id: str, target: str, ports: str) -> None:
    try:
        for progress in scanner.run(target, ports):
            active_scans[scan_id].update(progress)
            time.sleep(0.45)
        result = active_scans[scan_id]["result"]
        database.save_scan(scan_id, target, result)
        active_scans[scan_id].update({"status": "completed", "progress": 100, "completed_at": now_iso()})
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        active_scans[scan_id].update({"status": "failed", "error": str(exc)})


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "mode": "demo", "service": "agentsec"})


@app.post("/api/scans")
def create_scan():
    payload = request.get_json(silent=True) or {}
    target = str(payload.get("target", "")).strip()
    ports = str(payload.get("ports", "22,80,443"))
    if not target or len(target) > 253:
        return jsonify({"error": "A valid target is required"}), 400

    scan_id = uuid.uuid4().hex[:12]
    active_scans[scan_id] = {
        "scan_id": scan_id,
        "target": target,
        "ports": ports,
        "status": "running",
        "progress": 0,
        "started_at": now_iso(),
        "logs": ["Scan queued", "Demo mode: using deterministic evidence fixtures"],
    }
    thread = threading.Thread(target=run_demo_scan, args=(scan_id, target, ports), daemon=True)
    thread.start()
    return jsonify({"scan_id": scan_id, "status": "running"}), 202


@app.get("/api/scans/<scan_id>")
def scan_status(scan_id: str):
    scan = active_scans.get(scan_id)
    if scan:
        return jsonify(scan)
    saved = database.get_scan(scan_id)
    if saved:
        return jsonify(saved)
    return jsonify({"error": "Scan not found"}), 404


@app.get("/api/history")
def history():
    return jsonify(database.history())


@app.get("/api/stats")
def stats():
    return jsonify(database.stats())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "3000")), debug=False)
