"""Bounded, credential-isolated RunPod v2 and canary artifact transports.

No logging, shell, retries, or import-time credential reads. In particular, an
ambiguous create failure MUST be reconciled by the controller, not retried here.
An optional trusted urllib-compatible opener supports entirely offline tests;
injected stdlib OpenerDirectors also receive the no-redirect handler.

Elapsed monotonic deadlines (10s/request, 30s/inventory) are cooperative checks,
NOT hard real-time or billing limits. OS DNS resolution and blocking urllib,
TLS, socket, or close operations cannot be preempted here; timeout=10 remains
per I/O. read1 avoids read(n)'s repeated body receives where available, but even
it can block on protocol framing. Late results are rejected, not cancelled at
the provider; the controller must independently reconcile/terminate paid pods.
"""

import json
import os
import re
from time import monotonic
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, OpenerDirector, ProxyHandler, Request, build_opener


_API_URL = "https://api.runpod.io/v2/pods"
_API_LIMIT = 8 * 1024 * 1024
_ARTIFACT_LIMIT = 4 * 1024 * 1024
_REQUEST_SECONDS = 10
_LIST_SECONDS = 30
_LIST_LIMIT = 16 * 1024 * 1024
_POD_LIMIT = 10000
_ARTIFACT_NAMES = frozenset({"receipt.json", "canary.log", "result.json"})
_POD_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")


def _status(value):
    return value if type(value) is int and 100 <= value <= 599 else None


class ProviderError(Exception):
    """Only a numeric HTTP status escapes the transport; None means local failure.

    ``category`` is an optional, closed-vocabulary coarse hint distinguishing a
    malformed/unexpected provider response shape (SCHEMA_INVALID) from a plain
    transport/local failure. It carries no untrusted text.
    """

    def __init__(self, status=None, category=None):
        self.status = _status(status)
        self.category = category if category in ("SCHEMA_INVALID",) else None
        message = "Provider request failed"
        if self.status is not None:
            message += " (HTTP %d)" % self.status
        super().__init__(message)


class _NoRedirects(HTTPRedirectHandler):
    # Run before even an injected OpenerDirector's default redirect handler.
    handler_order = 0

    def http_error_302(self, req, fp, code, msg, headers):
        # The default handler can read a redirect body before following it.
        # Neither that body nor its Location is trusted here.
        fp.close()
        raise ProviderError(code) from None

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302


def _credential(variable):
    token = os.environ.get(variable, "")
    if not token or len(token) > 4096 or any(not 33 <= ord(c) <= 126 for c in token):
        raise ProviderError() from None
    return "Bearer " + token


def _pod_id(value):
    if not isinstance(value, str) or _POD_ID.fullmatch(value) is None:
        raise ProviderError() from None
    return value


def _check_deadline(deadline):
    if monotonic() >= deadline:
        raise ProviderError() from None


def _read_limited(response, limit, deadline):
    payload = bytearray()
    # HTTPResponse.read(n) can perform many receives before returning control.
    read = getattr(response, "read1", None)
    if not callable(read):
        read = response.read
    while True:
        _check_deadline(deadline)
        chunk = read(min(64 * 1024, limit + 1 - len(payload)))
        _check_deadline(deadline)
        if not isinstance(chunk, bytes) or len(payload) + len(chunk) > limit:
            raise ProviderError() from None
        if not chunk:
            return bytes(payload)
        payload.extend(chunk)


class _Client:
    def __init__(self, variable, opener):
        self._authorization = _credential(variable)
        failed = False
        try:
            if opener is None:
                # Ignore ambient proxy configuration: connect to the fixed HTTPS origin.
                opener = build_opener(ProxyHandler({}), _NoRedirects())
            elif isinstance(opener, OpenerDirector):
                opener.add_handler(_NoRedirects())
            self._opener = opener
        except Exception:
            failed = True
        if failed:
            raise ProviderError() from None

    def __repr__(self):
        return "%s()" % type(self).__name__

    def _request(self, url, method, expected, limit, data=None, missing=(),
                 accept="application/json", deadline=None, status_out=None):
        response = None
        payload = None
        status = None
        succeeded = False
        try:
            request_deadline = monotonic() + _REQUEST_SECONDS
            deadline = request_deadline if deadline is None else min(deadline, request_deadline)
            request = Request(url, data=data, method=method, headers={"Accept": accept})
            # Defense in depth: even a redirecting opener must not copy credentials.
            request.add_unredirected_header("Authorization", self._authorization)
            if data is not None:
                request.add_header("Content-Type", "application/json")
            _check_deadline(deadline)
            response = self._opener.open(request, timeout=10)
            _check_deadline(deadline)
            status = _status(response.getcode())
            if status in missing:
                succeeded = True
            elif status == expected:
                if limit is not None:
                    payload = _read_limited(response, limit, deadline)
                succeeded = True
        except HTTPError as error:
            response = error
            status = _status(error.code)
            succeeded = status in missing
        except ProviderError as error:
            status = error.status
        except Exception:
            # Includes network, TLS, timeout, and malformed response failures.
            status = None
        finally:
            try:
                if response is not None:
                    response.close()
                # Also reject late HTTPError/missing/bodyless responses and close.
                _check_deadline(deadline)
            except Exception:
                status = None
                succeeded = False
        # Raise OUTSIDE the except block: no secret-bearing exception context.
        if not succeeded:
            raise ProviderError(status) from None
        if status_out is not None:
            status_out.append(status)
        return payload


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError()
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError()


def _json_object(payload):
    result = None
    try:
        result = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=_reject_constant)
    except Exception:
        pass
    if not isinstance(result, dict):
        raise ProviderError(category="SCHEMA_INVALID") from None
    return result


def _pod(value):
    if not isinstance(value, dict):
        raise ProviderError(category="SCHEMA_INVALID") from None
    valid_id = True
    try:
        _pod_id(value.get("id"))
    except ProviderError:
        valid_id = False
    # Raise OUTSIDE the except block: no secret-bearing exception context.
    if not valid_id:
        raise ProviderError(category="SCHEMA_INVALID") from None
    return value


class RunPodAPI(_Client):
    """RunPod v2 pods API; capture RUNPOD_API_KEY only at construction."""

    def __init__(self, opener=None):
        super().__init__("RUNPOD_API_KEY", opener)

    def create_pod(self, body):
        if not isinstance(body, dict):
            raise ProviderError() from None
        data = None
        try:
            data = json.dumps(body, allow_nan=False, separators=(",", ":")).encode("utf-8")
        except Exception:
            pass
        if data is None:
            raise ProviderError() from None
        return _pod(_json_object(self._request(_API_URL, "POST", 201, _API_LIMIT, data)))

    def get_pod(self, pod_id):
        pod_id = _pod_id(pod_id)
        payload = self._request(_API_URL + "/" + pod_id, "GET", 200, _API_LIMIT,
                                missing=(404,))
        if payload is None:
            return None
        pod = _pod(_json_object(payload))
        if pod["id"] != pod_id:
            raise ProviderError(category="SCHEMA_INVALID") from None
        return pod

    def list_pods(self):
        return self._inventory()

    def visit_pods(self, visitor):
        """Stream validated positive records to a trusted cleanup consumer.

        Later failures still raise: visited records NEVER prove inventory
        completeness. They can establish exact ownership for prompt deletion.
        The visitor must not log or persist raw pods (env can contain secrets).
        """
        self._inventory(visitor)

    def _inventory(self, visitor=None):
        deadline = monotonic() + _LIST_SECONDS
        remaining = _LIST_LIMIT
        pods = []
        url = _API_URL
        seen = set()
        for _ in range(100):
            _check_deadline(deadline)
            if remaining <= 0:
                raise ProviderError() from None
            # Limit aggregate response-body bytes as well as retained pod count.
            # JSON's in-memory representation can be larger than its encoded body.
            payload = self._request(url, "GET", 200, min(_API_LIMIT, remaining),
                                    deadline=deadline)
            remaining -= len(payload)
            page = _json_object(payload)
            items = page.get("pods")
            pagination = page.get("pagination")
            if not isinstance(items, list) or not isinstance(pagination, dict):
                raise ProviderError(category="SCHEMA_INVALID") from None
            if "nextCursor" not in pagination or type(pagination.get("hasNextPage")) is not bool:
                raise ProviderError(category="SCHEMA_INVALID") from None
            cursor = pagination["nextCursor"]
            if cursor is not None and not isinstance(cursor, str):
                raise ProviderError(category="SCHEMA_INVALID") from None
            if len(pods) + len(items) > _POD_LIMIT:
                raise ProviderError(category="SCHEMA_INVALID") from None
            for item in items:
                pod = _pod(item)
                pods.append(pod)
                if visitor is not None:
                    visitor(pod)
            _check_deadline(deadline)
            if not pagination["hasNextPage"]:
                return pods
            if not cursor or cursor in seen:
                raise ProviderError(category="SCHEMA_INVALID") from None
            seen.add(cursor)
            query = None
            try:
                query = urlencode({"cursor": cursor})
            except Exception:
                pass
            if query is None:
                raise ProviderError() from None
            url = _API_URL + "?" + query
        # Never return a silently truncated inventory to the controller.
        raise ProviderError() from None

    def terminate_pod(self, pod_id):
        """Return "ACK_204" or "NOT_FOUND_404"; never collapse the two.

        NOT_FOUND_404 means not found OR not accessible to the caller [W1];
        it is NOT proof of termination. Any other outcome raises ProviderError,
        with .status carrying the HTTP status (HTTP_OTHER) or None (transport
        failure, no reliable status) -- the caller must classify accordingly
        and must never invent a termination result from an exception.
        """
        status_out = []
        self._request(_API_URL + "/" + _pod_id(pod_id), "DELETE", 204, None,
                      missing=(404,), status_out=status_out)
        return "ACK_204" if status_out[0] == 204 else "NOT_FOUND_404"


class ArtifactClient(_Client):
    """Canary proxy downloads; only AGE_ARTIFACT_TOKEN is read or forwarded."""

    def __init__(self, opener=None):
        super().__init__("AGE_ARTIFACT_TOKEN", opener)

    def fetch(self, pod_id, name):
        pod_id = _pod_id(pod_id)
        if not isinstance(name, str) or name not in _ARTIFACT_NAMES:
            raise ProviderError() from None
        url = "https://%s-8080.proxy.runpod.net/%s" % (pod_id, name)
        return self._request(url, "GET", 200, _ARTIFACT_LIMIT,
                             missing=(404, 502, 503, 504), accept="*/*")