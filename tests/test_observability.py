import asyncio

from app import get_generation_metrics, get_generation_timeline


def test_job_metrics_and_timeline_are_replayable(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "observability.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Observability", "@test")
    job_store.append_event(job["job_id"], "log", {"message": "started", "level": "info"})

    metrics = asyncio.run(get_generation_metrics(job["job_id"]))
    timeline = asyncio.run(get_generation_timeline(job["job_id"]))

    assert metrics["job_id"] == job["job_id"]
    assert metrics["status"] == "queued"
    assert metrics["event_count"] >= 2
    assert metrics["status_transitions"]["queued"] == 1
    assert timeline["job_id"] == job["job_id"]
    assert len(timeline["events"]) >= 2


def test_observability_uses_completed_duration(monkeypatch, tmp_path):
    import job_store
    from observability import build_job_metrics

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "duration.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Duration", "@test")
    claimed = job_store.claim_next_job("worker")
    completed = job_store.complete_job(
        job["job_id"], claimed["lease_token"], {"article": "article.md"}
    )

    metrics = build_job_metrics(completed, job_store.get_events(job["job_id"]))

    assert metrics["status"] == "completed"
    assert metrics["duration_seconds"] is not None
    assert metrics["duration_seconds"] >= 0
    assert metrics["status_transitions"]["completed"] == 1
