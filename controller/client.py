"""Simulator HTTP client with bounded retries.

Only idempotent calls are retried automatically. `advance`, `post_approval`, `apply`,
`auto_apply`, `suggest_fixes` and `validate` have side effects: after an ambiguous failure the
caller reconciles against server state instead of blindly resending.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Iterator

import httpx

log = logging.getLogger("controller.client")


class SimError(Exception):
    def __init__(self, status: int, code: str, detail=None):
        super().__init__(f"{status} {code}: {detail}")
        self.status, self.code, self.detail = status, code, detail


class SimUnavailable(Exception):
    """Transport failure or 5xx after retries."""


class SimClient:
    def __init__(self, base_url: str, timeout: float = 120.0, retries: int = 5, backoff: float = 0.5):
        self.http = httpx.Client(base_url=base_url, timeout=timeout)
        self.retries, self.backoff = retries, backoff
        self.stats = {"requests": 0, "retries": 0, "errors": 0}

    def close(self):
        self.http.close()

    def _send(self, method: str, path: str, *, retry: bool, **kw) -> httpx.Response:
        attempts = self.retries if retry else 1
        last: Exception | None = None
        for i in range(attempts):
            self.stats["requests"] += 1
            try:
                r = self.http.request(method, path, **kw)
                if r.status_code >= 500:
                    last = SimUnavailable(f"{r.status_code} on {method} {path}")
                else:
                    return r
            except (httpx.TransportError, httpx.TimeoutException) as e:
                last = SimUnavailable(f"{type(e).__name__} on {method} {path}: {e}")
            self.stats["errors"] += 1
            if i + 1 < attempts:
                self.stats["retries"] += 1
                time.sleep(min(self.backoff * 2 ** i, 8.0))
        raise last  # type: ignore[misc]

    def _json(self, method: str, path: str, *, retry: bool, **kw):
        r = self._send(method, path, retry=retry, **kw)
        try:
            body = r.json()
        except ValueError:
            raise SimUnavailable(f"non-JSON response on {method} {path}: {r.text[:120]}")
        if r.status_code >= 400:
            code = body.get("error", "error") if isinstance(body, dict) else "error"
            detail = body.get("detail") if isinstance(body, dict) else body
            raise SimError(r.status_code, code, detail)
        return body

    # --- reads (safe to retry)
    def state(self) -> dict:
        return self._json("GET", "/sim/state", retry=True)

    def workflows(self) -> list[dict]:
        return self._json("GET", "/workflows", retry=True)

    def config(self, wid: str) -> dict:
        return self._json("GET", f"/workflows/{wid}/config", retry=True)

    def config_history(self, wid: str) -> list[dict]:
        return self._json("GET", f"/workflows/{wid}/config/history", retry=True)

    def chunks(self, kind: str, after: int = -1) -> list[dict]:
        return self._json("GET", "/events/chunks", retry=True, params={"kind": kind, "after": after})

    def approvals(self, workflow_id: str | None = None, status: str | None = None) -> list[dict]:
        params = {k: v for k, v in (("workflow_id", workflow_id), ("status", status)) if v}
        return self._json("GET", "/approvals", retry=True, params=params)

    def approval(self, aid: str) -> dict:
        return self._json("GET", f"/approvals/{aid}", retry=True)

    def stream_chunk(self, n: int) -> Iterator[str]:
        """Yield NDJSON lines of one chunk without holding the body in memory."""
        last: Exception | None = None
        for i in range(self.retries):
            try:
                with self.http.stream("GET", f"/events/chunks/{n}") as r:
                    if r.status_code >= 500:
                        raise SimUnavailable(f"{r.status_code} on chunk {n}")
                    if r.status_code >= 400:
                        raise SimError(r.status_code, "chunk_error", n)
                    # Fully consumed before the caller commits, so a broken stream raises before any state change
                    for line in r.iter_lines():
                        if line:
                            yield line
                    return
            except (httpx.TransportError, SimUnavailable) as e:
                last = e
                time.sleep(min(self.backoff * 2 ** i, 8.0))
        raise SimUnavailable(f"chunk {n}: {last}")

    # --- side effects (never auto-retried on ambiguity)
    def advance(self, minutes: int) -> dict:
        return self._json("POST", "/sim/advance", retry=False, json={"minutes": minutes})

    def post_approval(self, body: dict) -> dict:
        return self._json("POST", "/approvals", retry=False, json=body)

    def apply(self, wid: str, approval_id: str) -> dict:
        return self._json("POST", f"/workflows/{wid}/apply", retry=False, json={"approval_id": approval_id})

    def auto_apply(self, wid: str, body: dict) -> dict:
        return self._json("PUT", f"/workflows/{wid}/config", retry=False, json=body)

    def suggest_fixes(self, wid: str, problem: str) -> dict:
        return self._json("POST", "/llm/suggest-fixes", retry=False, json={"workflow_id": wid, "problem": problem})

    def validate(self, wid: str, prompt_version: str, n: int) -> dict:
        return self._json("POST", "/validation/runs", retry=False,
                          json={"workflow_id": wid, "prompt_version": prompt_version, "n": n})


def parse_lines(lines: Iterator[str]) -> Iterator[dict]:
    for ln in lines:
        try:
            yield json.loads(ln)
        except ValueError:
            log.warning("skipping malformed event line: %.80s", ln)
