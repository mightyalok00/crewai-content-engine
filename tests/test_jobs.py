from datetime import datetime, timedelta, timezone

import pytest

from job_store import (
    append_event,
    claim_next_job,
    complete_job,
    get_events,
    get_job,
    mark_failure,
)


def test_job_lifecycle_is_persistent(monkeypatch, tmp_path):
    import job_store

    db = tmp_path / "jobs.sqlite3"
    monkeypatch.setattr(job_store, "DB_PATH", db)
    job_store.init_db()

    created = job_store.create_job("Test topic", "@test", max_retries=1)
    assert created["status"] == "queued"
    assert get_job(created["job_id"])["topic"] == "Test topic"

    claimed = claim_next_job("test-worker")
    assert claimed["job_id"] == created["job_id"]
    assert claimed["status"] == "running"
    assert claimed["worker_id"] == "test-worker"
    assert claimed["lease_token"]


def test_events_are_replayable(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "events.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Events", "@test")
    event_id = append_event(job["job_id"], "log", {"message": "hello", "level": "info"})
    events = get_events(job["job_id"], after_id=0)
    assert any(
        event["event_id"] == event_id and event["message"] == "hello"
        for event in events
    )


def test_failure_retries_then_fails(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "retry.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Retry me", "@test", max_retries=1)

    first = claim_next_job("test-worker-a")
    retrying = mark_failure(job["job_id"], "temporary", first["lease_token"])
    assert retrying["status"] == "queued"
    assert retrying["retry_count"] == 1
    assert retrying["lease_token"] is None

    second = claim_next_job("test-worker-b")
    failed = mark_failure(job["job_id"], "permanent", second["lease_token"])
    assert failed["status"] == "failed"
    assert failed["retry_count"] == 2
    assert failed["lease_token"] is None


def test_completion_persists_artifacts(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "artifacts.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Artifacts", "@test")
    claimed = claim_next_job("test-worker")

    updated = complete_job(
        job["job_id"],
        claimed["lease_token"],
        {"article": "artifacts/x/article.md"},
    )
    assert updated["status"] == "completed"
    assert updated["artifacts"]["article"].endswith("article.md")
    assert updated["worker_id"] is None
    assert updated["lease_token"] is None


def test_stale_worker_cannot_complete_after_recovery(monkeypatch, tmp_path):
    import job_store

    db = tmp_path / "lease.sqlite3"
    monkeypatch.setattr(job_store, "DB_PATH", db)
    job_store.init_db()
    job = job_store.create_job("Lease test", "@test", max_retries=1)
    claimed = job_store.claim_next_job("worker-a")
    old_lease = claimed["lease_token"]

    stale_at = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
    with job_store._connect() as conn:
        conn.execute(
            "UPDATE jobs SET heartbeat_at = ? WHERE job_id = ?",
            (stale_at, job["job_id"]),
        )

    assert job_store.recover_stale_jobs(10) == 1
    recovered = job_store.get_job(job["job_id"])
    assert recovered["status"] == "queued"
    assert recovered["lease_token"] is None
    assert recovered["worker_id"] is None

    replacement = job_store.claim_next_job("worker-b")
    assert replacement["lease_token"] != old_lease

    with pytest.raises(RuntimeError, match="lease"):
        job_store.complete_job(
            job["job_id"],
            old_lease,
            {"article": "stale.md"},
        )

    assert job_store.get_job(job["job_id"])["status"] == "running"


def test_stale_worker_cannot_fail_recovered_job(monkeypatch, tmp_path):
    import job_store

    db = tmp_path / "stale-failure.sqlite3"
    monkeypatch.setattr(job_store, "DB_PATH", db)
    job_store.init_db()
    job = job_store.create_job("Stale failure", "@test", max_retries=2)
    claimed = job_store.claim_next_job("worker-a")
    old_lease = claimed["lease_token"]

    stale_at = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
    with job_store._connect() as conn:
        conn.execute(
            "UPDATE jobs SET heartbeat_at = ? WHERE job_id = ?",
            (stale_at, job["job_id"]),
        )

    assert job_store.recover_stale_jobs(10) == 1
    replacement = job_store.claim_next_job("worker-b")

    with pytest.raises(RuntimeError, match="lease"):
        job_store.mark_failure(job["job_id"], "stale error", old_lease)

    current = job_store.get_job(job["job_id"])
    assert current["status"] == "running"
    assert current["lease_token"] == replacement["lease_token"]
