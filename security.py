"""Security helpers for the local CrewAI Studio API."""
from __future__ import annotations
import ipaddress
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from fastapi import HTTPException, Request

def require_local_admin(request: Request) -> None:
    expected = os.getenv("APP_API_TOKEN", "").strip()
    if expected and request.headers.get("Authorization") == f"Bearer {expected}":
        return
    host = request.client.host if request.client else ""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is None or not address.is_loopback:
        raise HTTPException(status_code=403, detail="Admin API is restricted to localhost unless APP_API_TOKEN is configured.")

def _assert_public_host(hostname: str) -> None:
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise HTTPException(status_code=400, detail="Webhook host cannot be resolved.") from exc
    addresses = {item[4][0] for item in infos}
    if not addresses:
        raise HTTPException(status_code=400, detail="Webhook host cannot be resolved.")
    for raw_address in addresses:
        address = ipaddress.ip_address(raw_address)
        if address.is_private or address.is_loopback or address.is_link_local or address.is_multicast or address.is_reserved or address.is_unspecified:
            raise HTTPException(status_code=400, detail="Webhook targets must resolve to a public IP address.")

def safe_webhook_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid webhook URL. Only http:// and https:// URLs are allowed.")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise HTTPException(status_code=400, detail="Local webhook targets are not allowed.")
    _assert_public_host(hostname)
    return parsed.geturl()

class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Webhook redirects are disabled for SSRF protection.", headers, fp)

def post_json(url: str, payload: dict[str, Any], timeout: float = 15):
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json","User-Agent":"CrewAI-Studio-Publisher/4.0"}, method="POST")
    return urllib.request.build_opener(_NoRedirectHandler).open(request, timeout=timeout)
