"""Small dependency-free observability helpers for API and job execution."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def request_id() -> str:
    """Return a short correlation ID suitable for API logs and response headers."""
    return uuid4().hex


def duration_seconds(started_at: str | None, finished_at: str | None) -> float | None:
    """Calculate an elapsed duration from ISO-8601 timestamps."""
    if not started_at:
        return None
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(finished_at) if finished_at else datetime.now(timezone.utc)
    return round(max(0.0, (end - start).total_seconds()), 3)


def build_job_metrics(job: dict, events: list[dict]) -> dict:
    """Build a stable, JSON-safe operational summary for one job."""
    duration = duration_seconds(job.get("started_at"), job.get("finished_at"))
    status_counts: dict[str, int] = {}
    for event in events:
        if event.get("type") == "status":
            status = event.get("status")
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "retry_count": int(job.get("retry_count", 0)),
        "max_retries": int(job.get("max_retries", 0)),
        "duration_seconds": duration,
        "event_count": len(events),
        "status_transitions": status_counts,
        "worker_id": job.get("worker_id"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "updated_at": job.get("updated_at"),
    }
