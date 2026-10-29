import json
import logging
import os

import psycopg2
from flask import Flask, jsonify, request


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        })


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
log = logging.getLogger("apex")
log.addHandler(handler)
log.setLevel(logging.INFO)

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "dev")
SEVERITIES = {"low", "medium", "high"}


def db():
    return psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=3)


@app.get("/health")
def health():
    return jsonify(status="ok", version=VERSION)


@app.get("/ready")
def ready():
    try:
        conn = db()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return jsonify(status="ready")
    except Exception as e:
        log.error("readiness check failed: %s", e)
        return jsonify(status="not ready"), 503


def ensure_table():
    conn = db()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS incidents ("
                "id SERIAL PRIMARY KEY, title TEXT NOT NULL, "
                "severity TEXT NOT NULL DEFAULT 'low', "
                "created_at TIMESTAMP DEFAULT now())"
            )
    finally:
        conn.close()


@app.get("/incidents")
def list_incidents():
    ensure_table()
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, severity FROM incidents ORDER BY id")
            rows = [{"id": r[0], "title": r[1], "severity": r[2]} for r in cur.fetchall()]
    finally:
        conn.close()
    return jsonify(rows)


@app.post("/incidents")
def create_incident():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    severity = data.get("severity", "low")
    if not title or severity not in SEVERITIES:
        return jsonify(error="title required; severity must be low/medium/high"), 400
    ensure_table()
    conn = db()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO incidents (title, severity) VALUES (%s, %s) RETURNING id",
                (title, severity),
            )
            new_id = cur.fetchone()[0]
    finally:
        conn.close()
    log.info("incident created id=%s severity=%s", new_id, severity)
    return jsonify(id=new_id, title=title, severity=severity), 201
