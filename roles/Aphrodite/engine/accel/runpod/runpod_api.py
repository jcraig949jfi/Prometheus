"""Bounded, credential-isolated RunPod REST client (stdlib only).

Pattern reused (read-only reference, not imported) from
Aether/runpod/aeth01_canary/runpod_api.py: no redirects, bounded reads, a fixed
non-default User-Agent (Cloudflare rule 1010 blocks urllib's default UA with a
403), the key read from RUNPOD_API_KEY only at construction, never logged, never
placed on argv, and NO retries inside the transport (an ambiguous create must be
reconciled by the controller via list, never blindly retried).

Two endpoint dialects are supported because the CPU-pod path has NOT been
smoke-tested on this account:
  v2  https://api.runpod.io/v2/pods    -- smoke-tested 2026-09-22 (GPU pod body)
  v1  https://rest.runpod.io/v1/pods   -- RunPod REST API; CPU pods
         (computeType=CPU). UNVERIFIED on this account: the operator must
         confirm the body with a dry-run (--print-body) against current docs.
"""
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

API_BASES = {"v2": "https://api.runpod.io/v2/pods",
             "v1": "https://rest.runpod.io/v1/pods"}
USER_AGENT = "APHRODITE-ACCEL-RUNPOD-canary/1.0"
_LIMIT = 8 * 1024 * 1024
_POD_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")


class ProviderError(Exception):
    def __init__(self, status=None):
        self.status = status if isinstance(status, int) else None
        super().__init__("provider request failed" + (" (HTTP %d)" % self.status
                                                      if self.status else ""))


class _NoRedirects(HTTPRedirectHandler):
    handler_order = 0

    def http_error_302(self, req, fp, code, msg, headers):
        fp.close()
        raise ProviderError(code)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def pod_id_ok(pid):
    return isinstance(pid, str) and _POD_ID.fullmatch(pid) is not None


class RunPodAPI:
    def __init__(self, dialect="v1"):
        token = os.environ.get("RUNPOD_API_KEY", "")
        if not token or any(not 33 <= ord(c) <= 126 for c in token):
            raise ProviderError()
        self._auth = "Bearer " + token
        self.base = API_BASES[dialect]
        self.dialect = dialect
        self._opener = build_opener(ProxyHandler({}), _NoRedirects())

    def __repr__(self):
        return "RunPodAPI(%s)" % self.dialect

    def _req(self, url, method, expected, data=None, missing=()):
        req = Request(url, data=data, method=method,
                      headers={"Accept": "application/json", "User-Agent": USER_AGENT})
        req.add_unredirected_header("Authorization", self._auth)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        status, payload = None, None
        try:
            with self._opener.open(req, timeout=15) as r:
                status = r.getcode()
                if status in expected:
                    payload = r.read(_LIMIT + 1)
                    if len(payload) > _LIMIT:
                        raise ProviderError(status)
        except HTTPError as e:
            status = e.code
            e.close()
            if status in missing:
                return status, None
            raise ProviderError(status) from None
        except ProviderError:
            raise
        except Exception:      # noqa: BLE001  network / TLS / timeout
            raise ProviderError() from None
        if status not in expected:
            raise ProviderError(status)
        return status, payload

    @staticmethod
    def _obj(payload):
        try:
            return json.loads(payload.decode("utf-8")) if payload else None
        except Exception:      # noqa: BLE001
            raise ProviderError() from None

    def create_pod(self, body):
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        _s, p = self._req(self.base, "POST", (200, 201), data)
        pod = self._obj(p)
        if not isinstance(pod, dict) or not pod_id_ok(pod.get("id")):
            raise ProviderError()
        return pod

    def get_pod(self, pid):
        if not pod_id_ok(pid):
            raise ProviderError()
        s, p = self._req(self.base + "/" + pid, "GET", (200,), missing=(404,))
        return None if s == 404 else self._obj(p)

    def list_pods(self):
        """Full inventory; handles the v1 (bare list) and v2 (paginated) shapes.
        Never returns a silently truncated list."""
        pods, url, seen = [], self.base, set()
        for _ in range(100):
            _s, p = self._req(url, "GET", (200,))
            page = self._obj(p)
            if isinstance(page, list):
                return pods + page
            if not isinstance(page, dict) or not isinstance(page.get("pods"), list):
                raise ProviderError()
            pods += page["pods"]
            pg = page.get("pagination") or {}
            if not pg.get("hasNextPage"):
                return pods
            cur = pg.get("nextCursor")
            if not cur or cur in seen:
                raise ProviderError()
            seen.add(cur)
            url = self.base + "?cursor=" + str(cur)
        raise ProviderError()

    def terminate_pod(self, pid):
        """'ACK' or 'NOT_FOUND' (404 is NOT proof of termination)."""
        if not pod_id_ok(pid):
            raise ProviderError()
        s, _p = self._req(self.base + "/" + pid, "DELETE", (200, 204), missing=(404,))
        return "NOT_FOUND" if s == 404 else "ACK"


def fetch_artifact(pod_id, port, name, token, timeout=20):
    """GET https://<pod>-<port>.proxy.runpod.net/<name> with the artifact bearer
    token (a per-run random token, NOT the RunPod key). Returns bytes or None."""
    if not pod_id_ok(pod_id) or name not in ("status.json", "ACCEL_EQUIVALENCE.json",
                                             "canary.log"):
        return None
    url = "https://%s-%d.proxy.runpod.net/%s" % (pod_id, port, name)
    opener = build_opener(ProxyHandler({}), _NoRedirects())
    req = Request(url, method="GET", headers={"Accept": "*/*", "User-Agent": USER_AGENT})
    req.add_unredirected_header("Authorization", "Bearer " + token)
    try:
        with opener.open(req, timeout=timeout) as r:
            if r.getcode() == 200:
                data = r.read(_LIMIT + 1)
                return data if len(data) <= _LIMIT else None
    except Exception:          # noqa: BLE001
        return None
    return None
