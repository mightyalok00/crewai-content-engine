"""Dedicated CrewAI worker process.

Run separately from FastAPI:
    python worker.py

For concurrency, run multiple worker processes with different WORKER_ID values.
Each worker executes one CrewAI job at a time. Job leases fence stale workers,
and each execution attempt receives an isolated artifact directory.
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
    complete_job,
    heartbeat,
    mark_failure,
    recover_stale_jobs,
)

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
POLL_SECONDS = float(os.getenv("JOB_POLL_SECONDS", "2"))
RECOVERY_SECONDS = int(os.getenv("JOB_RECOVERY_SECONDS", "300"))
WORKER_ID = os.getenv("WORKER_ID", "worker-1")


def _heartbeat_loop(
    job_id: str,
    lease_token: str,
    stop: threading.Event,
    lease_lost: threading.Event,
) -> None:
    interval = max(5, min(30, RECOVERY_SECONDS // 3))
    while not stop.wait(interval):
        try:
            heartbeat(job_id, lease_token)
        except RuntimeError:
            # Recovery may have reassigned this job. The running CrewAI call
            # cannot necessarily be cancelled safely, so mark the attempt stale
            # and let the lease-fenced completion path reject its result.
            lease_lost.set()
            stop.set()
            return


def _attempt_output_dir(job: dict) -> Path:
    lease_token = job["lease_token"]
    if not lease_token:
        raise RuntimeError("Claimed job is missing its worker lease")
    attempt = int(job["retry_count"])
    return BASE_DIR / "artifacts" / job["job_id"] / f"attempt-{attempt}-{lease_token[:12]}"


def process_job(job: dict) -> None:
    job_id = job["job_id"]
    lease_token = job.get("lease_token")
    if not lease_token:
        raise RuntimeError(f"Job {job_id} has no worker lease")

    stop = threading.Event()
    lease_lost = threading.Event()
    heartbeat_thread = threading.Thread(
        target=_heartbeat_loop,
        args=(job_id, lease_token, stop, lease_lost),
        daemon=True,
        name=f"heartbeat-{job_id[:8]}",
    )
    heartbeat_thread.start()

    try:
        append_event(
            job_id,
            "log",
            {
                "message": f"Worker {WORKER_ID} started the CrewAI pipeline.",
                "level": "info",
                "worker_id": WORKER_ID,
            },
        )

        output_dir = _attempt_output_dir(job)
        output_dir.mkdir(parents=True, exist_ok=True)

        from crew import configure_output_directory, create_blog_crew

        configure_output_directory(output_dir)
        crew = create_blog_crew()
        result = crew.kickoff(
            inputs={"topic": job["topic"], "channel": job["channel"]}
        )

        # Do not publish a result after another worker has recovered the job.
        if lease_lost.is_set():
            append_event(
                job_id,
                "log",
                {
                    "message": "Worker lost its lease; discarding stale attempt.",
                    "level": "warning",
                    "worker_id": WORKER_ID,
                },
            )
            return

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
        artifacts["crew_result"] = str(result_path.relative_to(BASE_DIR)).replace(
            os.sep, "/"
        )

        try:
            complete_job(job_id, lease_token, artifacts)
        except RuntimeError as exc:
            if "lease" not in str(exc).lower():
                raise
            append_event(
                job_id,
                "log",
                {
                    "message": "Worker lost its lease before completion; stale result ignored.",
                    "level": "warning",
                    "worker_id": WORKER_ID,
                },
            )
            return

        append_event(
            job_id,
            "log",
            {
                "message": "Job completed successfully.",
                "level": "success",
                "worker_id": WORKER_ID,
            },
        )
    except Exception as exc:
        try:
            job_after_failure = mark_failure(job_id, str(exc), lease_token)
        except RuntimeError as lease_error:
            if "lease" not in str(lease_error).lower():
                raise
            append_event(
                job_id,
                "log",
                {
                    "message": "Worker lost its lease; ignoring stale failure.",
                    "level": "warning",
                    "worker_id": WORKER_ID,
                },
            )
            return

        append_event(
            job_id,
            "log",
            {
                "message": f"Job attempt failed: {exc}",
                "level": "error",
                "retrying": job_after_failure["status"] == "queued",
                "worker_id": WORKER_ID,
            },
        )
    finally:
        stop.set()
        heartbeat_thread.join(timeout=1)


def main() -> None:
    print(f"Worker started: id={WORKER_ID}, poll={POLL_SECONDS}s")
    while True:
        recover_stale_jobs(RECOVERY_SECONDS)
        job = claim_next_job(WORKER_ID)
        if job:
            process_job(job)
        else:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
