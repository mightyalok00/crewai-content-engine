"""SQLite-backed persistent job store with fenced worker leases."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("JOB_DB_PATH", str(BASE_DIR / "artifacts" / "jobs.sqlite3")))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY, topic TEXT NOT NULL, channel TEXT NOT NULL,
            status TEXT NOT NULL, retry_count INTEGER NOT NULL DEFAULT 0,
            max_retries INTEGER NOT NULL DEFAULT 2, error TEXT,
            artifacts_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
            heartbeat_at TEXT, worker_id TEXT, lease_token TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at);
        CREATE TABLE IF NOT EXISTS job_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
            event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_job_events_job ON job_events(job_id, event_id);
        """)
        columns = {r["name"] for r in conn.execute("PRAGMA table_info(jobs)").fetchall()}
        if "worker_id" not in columns:
            conn.execute("ALTER TABLE jobs ADD COLUMN worker_id TEXT")
        if "lease_token" not in columns:
            conn.execute("ALTER TABLE jobs ADD COLUMN lease_token TEXT")


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["artifacts"] = json.loads(data.pop("artifacts_json") or "{}")
    return data


def create_job(topic: str, channel: str, max_retries: int = 2) -> dict[str, Any]:
    init_db()
    now = _now()
    job_id = uuid4().hex
    with _connect() as conn:
        conn.execute(
            """INSERT INTO jobs
            (job_id, topic, channel, status, retry_count, max_retries, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', 0, ?, ?, ?)""",
            (job_id, topic, channel, max_retries, now, now),
        )
    append_event(job_id, "status", {"status": "queued"})
    return get_job(job_id)  # type: ignore[return-value]


def get_job(job_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        return _row(conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone())


def append_event(job_id: str, event_type: str, payload: dict[str, Any]) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO job_events(job_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (job_id, event_type, json.dumps(payload), _now()),
        )
        return int(cur.lastrowid)


def get_events(job_id: str, after_id: int = 0) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT event_id, event_type, payload_json, created_at FROM job_events "
            "WHERE job_id = ? AND event_id > ? ORDER BY event_id",
            (job_id, after_id),
        ).fetchall()
    return [{"event_id": r["event_id"], "type": r["event_type"],
             **json.loads(r["payload_json"]), "at": r["created_at"]} for r in rows]


def _update(job_id: str, expected_lease_token: str | None = None, **changes: Any) -> dict[str, Any]:
    allowed = {"status", "error", "artifacts", "started_at", "finished_at",
               "heartbeat_at", "retry_count", "max_retries", "worker_id", "lease_token"}
    fields = {k: v for k, v in changes.items() if k in allowed}
    if "artifacts" in fields:
        fields["artifacts_json"] = json.dumps(fields.pop("artifacts"))
    fields["updated_at"] = _now()
    assignments = ", ".join(f"{k} = ?" for k in fields)
    where = "job_id = ?" + (" AND lease_token = ?" if expected_lease_token else "")
    params = (*fields.values(), job_id) if not expected_lease_token else (*fields.values(), job_id, expected_lease_token)
    with _connect() as conn:
        cur = conn.execute(f"UPDATE jobs SET {assignments} WHERE {where}", params)
    if cur.rowcount != 1:
        raise RuntimeError("Worker lease was lost")
    if "status" in changes:
        append_event(job_id, "status", {"status": changes["status"]})
    return get_job(job_id)  # type: ignore[return-value]


def claim_next_job(worker_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at LIMIT 1"
        ).fetchone()
        if row is None:
            conn.commit()
            return None
        lease = uuid4().hex
        now = _now()
        conn.execute(
            """UPDATE jobs SET status='running', started_at=COALESCE(started_at, ?),
               heartbeat_at=?, updated_at=?, worker_id=?, lease_token=?
               WHERE job_id=? AND status='queued'""",
            (now, now, now, worker_id, lease, row["job_id"]),
        )
        conn.commit()
    append_event(row["job_id"], "status", {"status": "running", "worker_id": worker_id})
    return get_job(row["job_id"])


def heartbeat(job_id: str, lease_token: str) -> None:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE jobs SET heartbeat_at=?, updated_at=? "
            "WHERE job_id=? AND lease_token=? AND status='running'",
            (_now(), _now(), job_id, lease_token),
        )
    if cur.rowcount != 1:
        raise RuntimeError("Worker lease was lost")


def complete_job(job_id: str, lease_token: str, artifacts: dict[str, Any]) -> dict[str, Any]:
    return _update(job_id, lease_token, status="completed",
                   finished_at=_now(), artifacts=artifacts,
                   worker_id=None, lease_token=None)


def mark_failure(job_id: str, error: str, lease_token: str) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    if job.get("lease_token") != lease_token:
        raise RuntimeError("Worker lease was lost")
    next_retry = int(job["retry_count"]) + 1
    status = "queued" if next_retry <= int(job["max_retries"]) else "failed"
    return _update(
        job_id, lease_token, status=status, retry_count=next_retry, error=error,
        finished_at=None if status == "queued" else _now(),
        worker_id=None, lease_token=None,
    )


def recover_stale_jobs(timeout_seconds: int = 300) -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)).isoformat()
    recovered: list[tuple[str, str, int]] = []
    with _connect() as conn:
        rows = conn.execute(
            "SELECT job_id, retry_count, max_retries FROM jobs "
            "WHERE status='running' AND COALESCE(heartbeat_at, started_at) < ?",
            (cutoff,),
        ).fetchall()
        for row in rows:
            retry = int(row["retry_count"]) + 1
            status = "queued" if retry <= int(row["max_retries"]) else "failed"
            conn.execute(
                "UPDATE jobs SET status=?, retry_count=?, error=?, finished_at=?, "
                "updated_at=?, worker_id=NULL, lease_token=NULL WHERE job_id=? AND status='running'",
                (status, retry, "Recovered after worker heartbeat timeout",
                 None if status == "queued" else _now(),
                 _now(), row["job_id"]),
            )
            recovered.append((row["job_id"], status, retry))
    for job_id, status, retry in recovered:
        append_event(job_id, "status", {"status": status, "reason": "worker_recovery",
                                        "retry_count": retry})
    return len(recovered)


init_db()
