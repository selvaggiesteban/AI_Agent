"""Thin Meta Graph API client for the Marketing API."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_API_VERSION = os.environ.get("META_GRAPH_VERSION", "v26.0")
GRAPH_URL = "https://graph.facebook.com"


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader (KEY=VALUE). Existing environment variables win."""
    env_path = path or (REPO_ROOT / ".env")
    if not env_path.is_file():
        return
    try:
        raw_text = env_path.read_text(encoding="utf-8-sig")
    except OSError:
        return
    for raw in raw_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


class GraphAPIError(RuntimeError):
    """Raised when the Graph API returns an error payload."""

    def __init__(self, payload: dict, context: str = ""):
        err = payload.get("error", {}) if isinstance(payload, dict) else {}
        self.code = err.get("code")
        self.error_subcode = err.get("error_subcode")
        self.is_transient = bool(err.get("is_transient"))
        self.fbtrace_id = err.get("fbtrace_id")
        self.user_title = err.get("error_user_title")
        self.user_message = err.get("error_user_msg")
        message = err.get("message") or str(payload)
        parts = []
        if context:
            parts.append(context)
        if self.code is not None:
            parts.append(f"{message} (code={self.code}, subcode={self.error_subcode})")
        else:
            parts.append(message)
        if self.user_message:
            parts.append(f"detail: {self.user_message}")
        if self.fbtrace_id:
            parts.append(f"fbtrace_id: {self.fbtrace_id}")
        super().__init__(" | ".join(parts))


def to_form_value(value) -> str:
    """Encode nested structures the way Graph API form posts expect (JSON strings)."""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(value, ensure_ascii=False)


class GraphClient:
    def __init__(self, token: str | None = None, version: str | None = None):
        load_dotenv()
        self.token = token if token is not None else os.environ.get("META_ACCESS_TOKEN", "")
        self.version = version or os.environ.get("META_GRAPH_VERSION", DEFAULT_API_VERSION)
        self.session = requests.Session()

    def require_token(self) -> None:
        if not self.token:
            raise GraphAPIError(
                {"error": {"message": "META_ACCESS_TOKEN is not set (see scripts/meta_ads/README.md)"}},
                "auth",
            )

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{GRAPH_URL}/{self.version}/{path.lstrip('/')}"

    def get(self, path: str, params: dict | None = None, retries: int = 3):
        self.require_token()
        params = dict(params or {})
        params["access_token"] = self.token
        return self._request("GET", path, params=params, retries=retries)

    def post(self, path: str, data: dict | None = None, files: dict | None = None, retries: int = 3):
        self.require_token()
        data = {key: to_form_value(value) for key, value in dict(data or {}).items()}
        data["access_token"] = self.token
        return self._request("POST", path, data=data, files=files, retries=retries)

    def _request(self, method: str, path: str, params=None, data=None, files=None, retries: int = 3):
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                if method == "GET":
                    resp = self.session.get(self._url(path), params=params, timeout=60)
                else:
                    resp = self.session.post(self._url(path), data=data, files=files, timeout=180)
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(2 ** attempt)
                continue
            if resp.status_code >= 500:
                last_error = RuntimeError(f"HTTP {resp.status_code} from Meta")
                time.sleep(2 ** attempt)
                continue
            try:
                payload = resp.json()
            except ValueError:
                raise RuntimeError(f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:500]}")
            if isinstance(payload, dict) and "error" in payload:
                error = GraphAPIError(payload, context=f"{method} {path}")
                if error.is_transient and attempt < retries - 1:
                    last_error = error
                    time.sleep(2 ** attempt)
                    continue
                raise error
            return payload
        raise last_error if last_error is not None else RuntimeError("request failed")

    def paginate(self, path: str, params: dict | None = None, limit: int = 200) -> list[dict]:
        params = dict(params or {})
        params.setdefault("limit", limit)
        page = self.get(path, params)
        items = list(page.get("data", []))
        while page.get("paging", {}).get("next"):
            resp = self.session.get(page["paging"]["next"], timeout=60)
            page = resp.json()
            if isinstance(page, dict) and "error" in page:
                raise GraphAPIError(page, context="paginate")
            items.extend(page.get("data", []))
        return items


def exchange_long_lived_token(app_id: str, app_secret: str, short_token: str) -> dict:
    """Exchange a short-lived user token for a long-lived one (no token in client state)."""
    resp = requests.get(
        f"{GRAPH_URL}/{DEFAULT_API_VERSION}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=60,
    )
    payload = resp.json()
    if "error" in payload:
        raise GraphAPIError(payload, context="oauth/access_token")
    return payload
