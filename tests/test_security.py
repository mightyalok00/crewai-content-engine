import pytest
from fastapi import HTTPException
from security import safe_webhook_url

@pytest.mark.parametrize("url", ["http://127.0.0.1:8000/hook","http://localhost/hook","http://10.0.0.10/hook","http://192.168.1.20/hook","http://169.254.169.254/latest/meta-data"])
def test_safe_webhook_rejects_private_targets(url):
    with pytest.raises(HTTPException):
        safe_webhook_url(url)

def test_safe_webhook_requires_http_scheme():
    with pytest.raises(HTTPException):
        safe_webhook_url("file:///etc/passwd")

def test_safe_webhook_accepts_public_hostname(monkeypatch):
    monkeypatch.setattr("security.socket.getaddrinfo", lambda *args, **kwargs: [(None,None,None,None,("93.184.216.34",0))])
    assert safe_webhook_url("https://example.com/webhook") == "https://example.com/webhook"