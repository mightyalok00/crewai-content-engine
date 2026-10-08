from jobs import create_job, get_job

def test_create_job_persists_request_scoped_job(monkeypatch, tmp_path):
    import jobs
    monkeypatch.setattr(jobs, "JOB_ROOT", tmp_path)
    monkeypatch.setattr(jobs, "_run_job", lambda *args: None)
    job = create_job("Test topic", "@test")
    assert job["status"] == "queued"
    assert job["job_id"]
    assert get_job(job["job_id"])["topic"] == "Test topic"
    assert (tmp_path / job["job_id"] / "job.json").exists()
