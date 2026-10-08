from job_store import (
    append_event,
    claim_next_job,
    get_events,
    get_job,
    mark_failure,
    update_job,
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
    assert get_job(created["job_id"])["status"] == "running"


def test_events_are_replayable(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "events.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Events", "@test")
    event_id = append_event(job["job_id"], "log", {"message": "hello", "level": "info"})
    events = get_events(job["job_id"], after_id=0)
    assert any(event["event_id"] == event_id and event["message"] == "hello" for event in events)


def test_failure_retries_then_fails(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "retry.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Retry me", "@test", max_retries=1)
    claim_next_job()

    retrying = mark_failure(job["job_id"], "temporary")
    assert retrying["status"] == "queued"
    assert retrying["retry_count"] == 1

    claim_next_job()
    failed = mark_failure(job["job_id"], "permanent")
    assert failed["status"] == "failed"
    assert failed["retry_count"] == 2


def test_update_job_persists_artifacts(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "artifacts.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Artifacts", "@test")
    updated = update_job(job["job_id"], artifacts={"article": "artifacts/x/article.md"})
    assert updated["artifacts"]["article"].endswith("article.md")


def test_stale_worker_cannot_complete_after_recovery(monkeypatch, tmp_path):
    import job_store

    monkeypatch.setattr(job_store, "DB_PATH", tmp_path / "lease.sqlite3")
    job_store.init_db()
    job = job_store.create_job("Lease test", "@test", max_retries=1)
    claimed = job_store.claim_next_job("worker-a")
    old_lease = claimed["lease_token"]

    assert job_store.recover_stale_jobs(0) == 1
    recovered = job_store.get_job(job["job_id"])
    assert recovered["status"] == "queued"
    assert recovered["lease_token"] is None

    replacement = job_store.claim_next_job("worker-b")
    assert replacement["lease_token"] != old_lease

    try:
        job_store.complete_job(job["job_id"], old_lease, {"article": "stale.md"})
    except RuntimeError:
        pass
    else:
        raise AssertionError("stale worker was allowed to complete a recovered job")

    assert job_store.get_job(job["job_id"])["status"] == "running"
