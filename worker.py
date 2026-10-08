"""Dedicated CrewAI worker process.

Run separately from FastAPI:
    python worker.py
"""
from __future__ import annotations

import os
import threading
import time
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
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))


def _heartbeat_loop(job_id: str, stop: threading.Event) -> None:
    interval = max(5, min(30, RECOVERY_SECONDS // 3))
    while not stop.wait(interval):
        heartbeat(job_id)


def process_job(job: dict) -> None:
    job_id = job["job_id"]
    stop = threading.Event()
    heartbeat_thread = threading.Thread(target=_heartbeat_loop, args=(job_id, stop), daemon=True)
    heartbeat_thread.start()
    try:
        append_event(job_id, "log", {"message": f"Starting CrewAI pipeline for: {job['topic']}", "level": "info"})
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

        update_job(job_id, status="completed", finished_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), artifacts=artifacts)
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
    print(f"Worker started: concurrency={MAX_CONCURRENT_JOBS}, poll={POLL_SECONDS}s")
    while True:
        recover_stale_jobs(RECOVERY_SECONDS)
        active: list[threading.Thread] = []
        for _ in range(MAX_CONCURRENT_JOBS):
            job = claim_next_job()
            if not job:
                break
            thread = threading.Thread(target=process_job, args=(job,), daemon=False)
            thread.start()
            active.append(thread)
        for thread in active:
            thread.join()
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
