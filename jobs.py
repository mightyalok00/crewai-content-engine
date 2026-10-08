"""Compatibility API for persistent CrewAI jobs.

The API process only creates/reads jobs. Execution belongs to worker.py.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from job_store import (
    append_event,
    create_job as _create_job,
    get_events,
    get_job,
)


def create_job(topic: str, channel: str, max_retries: int = 2) -> dict[str, Any]:
    if not topic.strip():
        raise ValueError("Topic is required")
    return _create_job(topic.strip(), channel.strip(), max_retries=max_retries)


def log_job(job_id: str, message: str, level: str = "info") -> None:
    append_event(job_id, "log", {"message": message, "level": level})


class _EventStream:
    async def exists(self, job_id: str) -> bool:
        return get_job(job_id) is not None

    async def iter(self, job_id: str):
        last_event_id = 0
        while True:
            job = get_job(job_id)
            if job is None:
                return

            events = get_events(job_id, after_id=last_event_id)
            for event in events:
                last_event_id = event["event_id"]
                yield f"data: {json.dumps(event)}\n\n"

            if job["status"] in {"completed", "failed"} and not events:
                yield f"data: {json.dumps({'type': 'done', 'job_id': job_id})}\n\n"
                return

            await asyncio.sleep(0.75)


event_stream = _EventStream()
