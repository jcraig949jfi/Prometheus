"""A remote Foundry client that keeps the network out of the science.

STANDARD LIBRARY ONLY. This file is deliberately self-contained so a research
console can copy just `remote.py` and drive a Foundry host with a stock Python
install — no donor dependencies, no package layout required.

Two invariants make it safe to treat a remote Foundry as the execution and
provenance authority:

1. RELEASE PIN. Construct with `expected_release_hash` and the client refuses
   to run against a host whose `source_tree_hash` differs. An experiment is
   thereby tied to exactly one instrument identity, not to "whatever version
   M1 happens to be running today."

2. THE NETWORK IS NEVER A SCIENTIFIC RESULT. A dropped connection, a timeout,
   or a 5xx never returns a fabricated result. It raises
   `TransportIndeterminate`, which carries the client-generated `trace_id`.
   The server's ledger is authoritative, so the caller reconciles that id via
   `reconcile()` and learns definitively whether the operation COMMITTED. A
   4xx is a definite rejection (auth/validation happen before any execution)
   and raises `FoundryHTTPError`. Only a fully received 2xx is a result.

Deterministic computation (VM step caps, seeds) stays authoritative on the
host; wall-clock and network time are operational only.
"""

from __future__ import annotations

import http.client
import json
import socket
import ssl
import urllib.parse
import uuid
from typing import Any, Optional


class FoundryClientError(Exception):
    """Base class for every client-raised error."""


class ReleaseMismatch(FoundryClientError):
    """The host's release identity is not the one the experiment expects."""

    def __init__(self, expected: str, actual: Optional[str]):
        self.expected, self.actual = expected, actual
        super().__init__(
            f"host source_tree_hash {actual!r} != expected {expected!r}; "
            f"refusing to run against a different instrument release")


class FoundryHTTPError(FoundryClientError):
    """The host returned a definite error status (4xx). The operation did not
    run: auth and validation are decided before any execution."""

    def __init__(self, status: int, detail: Any, trace_id: Optional[str]):
        self.status, self.detail, self.trace_id = status, detail, trace_id
        super().__init__(f"HTTP {status}: {detail}")


class TransportIndeterminate(FoundryClientError):
    """The outcome is UNKNOWN, not failed. A transport error or a 5xx means we
    cannot tell from the client whether the operation committed. NEVER treat
    this as a result. Reconcile `trace_id` against the host's ledger."""

    def __init__(self, trace_id: str, cause: str):
        self.trace_id, self.cause = trace_id, cause
        super().__init__(
            f"indeterminate outcome for trace_id={trace_id}: {cause}; "
            f"reconcile against the host ledger before assuming anything")


class FoundryClient:
    """Minimal, safe HTTP client for one Foundry host."""

    def __init__(self, base_url: str, token: str,
                 expected_release_hash: Optional[str] = None,
                 timeout_s: float = 30.0,
                 tls_context: Optional[ssl.SSLContext] = None):
        self._url = urllib.parse.urlsplit(base_url.rstrip("/"))
        if self._url.scheme not in ("http", "https"):
            raise ValueError(f"base_url must be http(s), got {base_url!r}")
        self._token = token
        self._timeout = float(timeout_s)
        self._tls = tls_context
        self.expected_release_hash = expected_release_hash
        self._release_checked = False

    # -- release pin -------------------------------------------------------
    def version(self) -> dict:
        return self._request("GET", "/v0/version")[1]

    def check_release(self) -> dict:
        """Fetch /v0/version and enforce the pin. Raises ReleaseMismatch on a
        mismatch. Called automatically before the first operation."""
        info = self.version()
        actual = info.get("source_tree_hash")
        if (self.expected_release_hash is not None
                and actual != self.expected_release_hash):
            raise ReleaseMismatch(self.expected_release_hash, actual)
        self._release_checked = True
        return info

    def _ensure_release(self) -> None:
        if self.expected_release_hash is not None and not self._release_checked:
            self.check_release()

    # -- operations --------------------------------------------------------
    def post(self, path: str, body: dict,
             trace_id: Optional[str] = None) -> dict:
        self._ensure_release()
        return self._request("POST", path, body, trace_id=trace_id)[1]

    def get(self, path: str) -> dict:
        self._ensure_release()
        return self._request("GET", path)[1]

    # convenience wrappers over the operational endpoints. `trace_id` is a
    # transport concern (it becomes the correlation header), never part of the
    # operation body, so it is a named parameter and is forwarded, not folded
    # into the request payload.
    def create_artifact(self, engine_id: str, op: str = "create_random",
                        trace_id: Optional[str] = None, **kw) -> dict:
        return self.post("/v0/artifacts",
                         {"engine_id": engine_id, "op": op, **kw},
                         trace_id=trace_id)

    def evaluate(self, trace_id: Optional[str] = None, **body) -> dict:
        return self.post("/v0/evaluate", body, trace_id=trace_id)

    def search(self, trace_id: Optional[str] = None, **body) -> dict:
        return self.post("/v0/search", body, trace_id=trace_id)

    # -- reconciliation ----------------------------------------------------
    def reconcile(self, trace_id: str) -> dict:
        """Definitive outcome of a possibly-indeterminate request.

        Requires an admin-scope token (trace inspection is operator-only).
        Returns {found, committed, ...}. `committed=True` means the operation
        reached the ledger; a client that got TransportIndeterminate can now
        decide safely — retry only if not committed. For content-addressed
        single operations (create/evaluate) a retry is idempotent regardless;
        for a budget-consuming search, reconcile before retrying so the run is
        not doubled.
        """
        return self.get(f"/admin/trace/{urllib.parse.quote(trace_id)}")

    # -- transport ---------------------------------------------------------
    def _request(self, method: str, path: str, body: Optional[dict] = None,
                 trace_id: Optional[str] = None) -> tuple[int, dict]:
        tid = trace_id or f"m2-{uuid.uuid4().hex}"
        payload = None
        headers = {"authorization": f"Bearer {self._token}",
                   "x-foundry-trace": tid, "accept": "application/json"}
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            headers["content-type"] = "application/json"

        conn = self._connect()
        try:
            conn.request(method, self._full(path), body=payload,
                         headers=headers)
            resp = conn.getresponse()
            raw = resp.read()                    # may raise mid-stream
            status = resp.status
        except (socket.timeout, TimeoutError) as e:
            raise TransportIndeterminate(tid, f"timeout: {e}")
        except (ConnectionError, http.client.HTTPException, OSError) as e:
            # Connection dropped/refused/reset, or an incomplete read: we do
            # NOT know whether the server ran the operation.
            raise TransportIndeterminate(tid, f"{type(e).__name__}: {e}")
        finally:
            conn.close()

        detail = _parse_json(raw)
        if 200 <= status < 300:
            # The ONLY case that is a result: a fully received success.
            result = detail if isinstance(detail, dict) else {"raw": detail}
            result.setdefault("trace_id", tid)
            return status, result
        if status >= 500:
            # Reached the server but the outcome is ambiguous: it may have
            # partially committed before failing. Treat as indeterminate.
            raise TransportIndeterminate(
                tid, f"server error {status}: {_err(detail)}")
        if status >= 400:
            # Definite rejection decided BEFORE any execution.
            raise FoundryHTTPError(status, _err(detail), tid)
        # A 3xx (or a 1xx) is NOT a received result: a redirect means the
        # endpoint did not run and the body is not the operation's output.
        # http.client does not follow redirects, and a 308 even preserves the
        # POST — so folding 3xx into success would let a non-executed
        # operation masquerade as a result. Outcome unknown => reconcile.
        location = ""
        try:
            location = resp.getheader("location") or ""
        except Exception:                           # noqa: BLE001
            pass
        raise TransportIndeterminate(
            tid, f"unexpected {status} (redirect/other) to {location!r}; "
                 f"not a received result")

    def _connect(self):
        host, port = self._url.hostname, self._url.port
        if self._url.scheme == "https":
            ctx = self._tls or ssl.create_default_context()
            return http.client.HTTPSConnection(
                host, port, timeout=self._timeout, context=ctx)
        return http.client.HTTPConnection(host, port, timeout=self._timeout)

    def _full(self, path: str) -> str:
        base = self._url.path or ""
        return base + path if base else path


def _parse_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:                               # noqa: BLE001
        return raw.decode("utf-8", "replace")


def _err(detail) -> str:
    if isinstance(detail, dict) and "detail" in detail:
        d = detail["detail"]
        if isinstance(d, dict):
            return d.get("message") or d.get("error") or json.dumps(d)
        return str(d)
    return str(detail)
