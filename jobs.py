"""Persistent, request-scoped job manager for CrewAI generation."""
from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
JOB_ROOT = BASE_DIR / "artifacts"
JOB_ROOT.mkdir(exist_ok=True)

_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}
_queues: dict[str, asyncio.Queue] = {}
_loops: dict[str, asyncio.AbstractEventLoop] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persist(job: dict[str, Any]) -> None:
    path = JOB_ROOT / job["job_id"] / "job.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(job, indent=2), encoding="utf-8")


def get_job(job_id: str) -> dict[str, Any] | None:
    with _lock:
        if job_id in _jobs:
            return dict(_jobs[job_id])
    path = JOB_ROOT / job_id / "job.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _publish(job_id: str, event: dict[str, Any]) -> None:
    queue = _queues.get(job_id)
    loop = _loops.get(job_id)
    if queue and loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(queue.put(event), loop)


def update_job(job_id: str, **changes: Any) -> dict[str, Any]:
    with _lock:
        job = _jobs[job_id]
        job.update(changes)
        job["updated_at"] = _now()
        snapshot = dict(job)
        _persist(snapshot)
    if "status" in changes:
        _publish(job_id, {"type": "status", "status": changes["status"]})
    return snapshot


def log_job(job_id: str, message: str, level: str = "info") -> None:
    _publish(job_id, {"type": "log", "message": message, "level": level, "at": _now()})


def _run_job(job_id: str, topic: str, channel: str) -> None:
    artifact_dir = JOB_ROOT / job_id
    try:
        update_job(job_id, status="running", started_at=_now())
        log_job(job_id, f"Starting CrewAI pipeline for: {topic}")

        from crew import create_blog_crew
        crew = create_blog_crew()
        result = crew.kickoff(inputs={"topic": topic, "channel": channel})
        log_job(job_id, "Crew execution completed.")

        # Capture CrewAI task output in a request-scoped artifact directory.
        output_map = {
            "article": "new_blog_post.md",
            "social": "social_snippets.md",
            "podcast": "podcast_script.md",
            "newsletter": "newsletter.md",
        }
        artifacts = {}
        for name, filename in output_map.items():
            source = BASE_DIR / filename
            target = artifact_dir / filename
            if source.exists():
                target.write_text(source.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
                artifacts[name] = str(target.relative_to(BASE_DIR)).replace(os.sep, "/")

        result_path = artifact_dir / "crew_result.txt"
        result_path.write_text(str(result), encoding="utf-8")
        artifacts["crew_result"] = str(result_path.relative_to(BASE_DIR)).replace(os.sep, "/")

        update_job(job_id, status="completed", finished_at=_now(), artifacts=artifacts)
        log_job(job_id, "Job completed successfully.", "success")
    except Exception as exc:
        update_job(job_id, status="failed", finished_at=_now(), error=str(exc))
        log_job(job_id, f"Job failed: {exc}", "error")
    finally:
        _publish(job_id, {"type": "done", "job_id": job_id})


def create_job(topic: str, channel: str) -> dict[str, Any]:
    if not topic:
        raise ValueError("Topic is required")
    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "topic": topic,
        "channel": channel,
        "status": "queued",
        "created_at": _now(),
        "updated_at": _now(),
        "artifacts": {},
    }
    with _lock:
        _jobs[job_id] = job
    _persist(job)

    thread = threading.Thread(target=_run_job, args=(job_id, topic, channel), daemon=True)
    thread.start()
    return dict(job)


class _EventStream:
    async def exists(self, job_id: str) -> bool:
        return get_job(job_id) is not None

    async def iter(self, job_id: str):
        queue = asyncio.Queue()
        _queues[job_id] = queue
        _loops[job_id] = asyncio.get_running_loop()
        try:
            job = get_job(job_id)
            if job:
                yield f"data: {json.dumps({'type': 'status', 'status': job['status']})}\n\n"
                for key, value in job.get("artifacts", {}).items():
                    yield f"data: {json.dumps({'type': 'artifact', 'name': key, 'path': value})}\n\n"
                if job["status"] in {"completed", "failed"}:
                    yield f"data: {json.dumps({'type': 'done', 'job_id': job_id})}\n\n"
                    return
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "done":
                    return
        finally:
            _queues.pop(job_id, None)
            _loops.pop(job_id, None)


event_stream = _EventStream()
