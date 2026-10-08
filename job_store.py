"""SQLite-backed persistent job store used by API and workers."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

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
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 2,
                error TEXT,
                artifacts_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                heartbeat_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_jobs_status_created
                ON jobs(status, created_at);
            CREATE TABLE IF NOT EXISTS job_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_job_events_job
                ON job_events(job_id, event_id);
            """
        )


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["artifacts"] = json.loads(data.pop("artifacts_json") or "{}")
    return data


def create_job(topic: str, channel: str, max_retries: int = 2) -> dict[str, Any]:
    init_db()
    from uuid import uuid4
    now = _now()
    job_id = uuid4().hex
    with _connect() as conn:
        conn.execute(
            """INSERT INTO jobs
            (job_id, topic, channel, status, retry_count, max_retries,
             created_at, updated_at)
            VALUES (?, ?, ?, 'queued', 0, ?, ?, ?)""",
            (job_id, topic, channel, max_retries, now, now),
        )
    append_event(job_id, "status", {"status": "queued"})
    return get_job(job_id)  # type: ignore[return-value]


def get_job(job_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        return _row(conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone())


def update_job(job_id: str, **changes: Any) -> dict[str, Any]:
    init_db()
    allowed = {
        "status", "error", "artifacts", "started_at", "finished_at",
        "heartbeat_at", "retry_count", "max_retries",
    }
    fields = {k: v for k, v in changes.items() if k in allowed}
    if not fields:
        job = get_job(job_id)
        if job is None:
            raise KeyError(job_id)
        return job
    if "artifacts" in fields:
        fields["artifacts"] = json.dumps(fields["artifacts"])
    fields["updated_at"] = _now()
    assignments = ", ".join(f"{k} = ?" for k in fields)
    with _connect() as conn:
        conn.execute(
            f"UPDATE jobs SET {assignments} WHERE job_id = ?",
            (*fields.values(), job_id),
        )
    if "status" in changes:
        append_event(job_id, "status", {"status": changes["status"]})
    return get_job(job_id)  # type: ignore[return-value]


def heartbeat(job_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET heartbeat_at = ?, updated_at = ? WHERE job_id = ?",
            (_now(), _now(), job_id),
        )


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
            """SELECT event_id, event_type, payload_json, created_at
               FROM job_events
               WHERE job_id = ? AND event_id > ?
               ORDER BY event_id""",
            (job_id, after_id),
        ).fetchall()
    return [
        {
            "event_id": row["event_id"],
            "type": row["event_type"],
            **json.loads(row["payload_json"]),
            "at": row["created_at"],
        }
        for row in rows
    ]


def claim_next_job() -> dict[str, Any] | None:
    """Atomically claim the oldest queued job across multiple worker processes."""
    init_db()
    with _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at LIMIT 1"
        ).fetchone()
        if row is None:
            conn.commit()
            return None
        now = _now()
        conn.execute(
            """UPDATE jobs
               SET status = 'running', started_at = COALESCE(started_at, ?),
                   heartbeat_at = ?, updated_at = ?
               WHERE job_id = ? AND status = 'queued'""",
            (now, now, now, row["job_id"]),
        )
        conn.commit()
    append_event(row["job_id"], "status", {"status": "running"})
    return get_job(row["job_id"])


def recover_stale_jobs(timeout_seconds: int = 300) -> int:
    """Requeue jobs abandoned by a crashed worker."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
    cutoff_iso = cutoff.isoformat()
    recovered_events: list[tuple[str, str, int]] = []
    with _connect() as conn:
        rows = conn.execute(
            """SELECT job_id FROM jobs
               WHERE status = 'running'
               AND COALESCE(heartbeat_at, started_at) < ?""",
            (cutoff_iso,),
        ).fetchall()
        for row in rows:
            job = conn.execute(
                "SELECT retry_count, max_retries FROM jobs WHERE job_id = ?",
                (row["job_id"],),
            ).fetchone()
            next_retry = int(job["retry_count"]) + 1
            status = "queued" if next_retry <= int(job["max_retries"]) else "failed"
            finished_at = None if status == "queued" else _now()
            conn.execute(
                """UPDATE jobs
                   SET status=?, retry_count=?, error=?,
                       finished_at=?, updated_at=?
                   WHERE job_id=? AND status='running'""",
                (
                    status,
                    next_retry,
                    "Recovered after worker heartbeat timeout",
                    finished_at,
                    _now(),
                    row["job_id"],
                ),
            )
            recovered_events.append((row["job_id"], status, next_retry))
    for job_id, status, retry_count in recovered_events:
        append_event(
            job_id,
            "status",
            {"status": status, "reason": "worker_recovery", "retry_count": retry_count},
        )
    return len(recovered_events)

def mark_failure(job_id: str, error: str) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    next_retry = int(job["retry_count"]) + 1
    if next_retry <= int(job["max_retries"]):
        return update_job(
            job_id,
            status="queued",
            retry_count=next_retry,
            error=error,
            finished_at=None,
        )
    return update_job(
        job_id,
        status="failed",
        retry_count=next_retry,
        error=error,
        finished_at=_now(),
    )


init_db()
