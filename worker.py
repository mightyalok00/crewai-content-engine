"""Dedicated CrewAI worker process.

Run separately from FastAPI:
    python worker.py

For concurrency, run multiple worker processes with different WORKER_ID values.
Each worker executes one CrewAI job at a time, preventing shared task state from
colliding inside a Python process.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from job_store import (
    append_event,
    claim_next_job,
    heartbeat,
    mark_failure,
    recover_stale_jobs,
    update_job,
)

load_dotenv(override=True)
BASE_DIR = Path(__file__).resolve().parent
POLL_SECONDS = float(os.getenv("JOB_POLL_SECONDS", "2"))
RECOVERY_SECONDS = int(os.getenv("JOB_RECOVERY_SECONDS", "300"))
WORKER_ID = os.getenv("WORKER_ID", "worker-1")


def _heartbeat_loop(job_id: str, stop: threading.Event) -> None:
    interval = max(5, min(30, RECOVERY_SECONDS // 3))
    while not stop.wait(interval):
        heartbeat(job_id)


def process_job(job: dict) -> None:
    job_id = job["job_id"]
    stop = threading.Event()
    heartbeat_thread = threading.Thread(
        target=_heartbeat_loop, args=(job_id, stop), daemon=True
    )
    heartbeat_thread.start()
    try:
        append_event(
            job_id,
            "log",
            {"message": f"Worker {WORKER_ID} started the CrewAI pipeline.", "level": "info"},
        )
        output_dir = BASE_DIR / "artifacts" / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        from crew import configure_output_directory, create_blog_crew

        configure_output_directory(output_dir)
        crew = create_blog_crew()
        result = crew.kickoff(inputs={"topic": job["topic"], "channel": job["channel"]})

        artifacts = {}
        for name, filename in {
            "article": "new_blog_post.md",
            "social": "social_snippets.md",
            "podcast": "podcast_script.md",
            "newsletter": "newsletter.md",
        }.items():
            path = output_dir / filename
            if path.exists():
                artifacts[name] = str(path.relative_to(BASE_DIR)).replace(os.sep, "/")

        result_path = output_dir / "crew_result.txt"
        result_path.write_text(str(result), encoding="utf-8")
        artifacts["crew_result"] = str(result_path.relative_to(BASE_DIR)).replace(os.sep, "/")

        update_job(
            job_id,
            status="completed",
            finished_at=datetime.now(timezone.utc).isoformat(),
            artifacts=artifacts,
        )
        append_event(job_id, "log", {"message": "Job completed successfully.", "level": "success"})
    except Exception as exc:
        job_after_failure = mark_failure(job_id, str(exc))
        append_event(
            job_id,
            "log",
            {
                "message": f"Job attempt failed: {exc}",
                "level": "error",
                "retrying": job_after_failure["status"] == "queued",
            },
        )
    finally:
        stop.set()


def main() -> None:
    print(f"Worker started: id={WORKER_ID}, poll={POLL_SECONDS}s")
    while True:
        recover_stale_jobs(RECOVERY_SECONDS)
        job = claim_next_job()
        if job:
            process_job(job)
        else:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
