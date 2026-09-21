"""Offline stdlib regression tests; no sockets, real credentials, or paid calls.

Run with python -B Aether/test/test_aeth01_runpod_api.py (or via pytest).
"""

from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import importlib.util
import io
import json
import os
from pathlib import Path
import traceback
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import BaseHandler, HTTPRedirectHandler, ProxyHandler, build_opener
from urllib.response import addinfourl


MODULE_PATH = (Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
               / "runpod_api.py")
SPEC = importlib.util.spec_from_file_location("_aeth01_runpod_api_test", MODULE_PATH)
api = importlib.util.module_from_spec(SPEC)
# These are deliberately synthetic fixtures, not actual credentials.
ENV = {"RUNPOD_API_KEY": "offline-api-fixture", "AGE_ARTIFACT_TOKEN": "offline-artifact-fixture"}
with patch.dict(os.environ, {}, clear=True):
    SPEC.loader.exec_module(api)


class Clock:
    """Deterministic elapsed time, independent of wall time and scheduling."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class Response:
    def __init__(self, status=200, payload=b"", forbid_read=False, short_reads=False,
                 clock=None, delay=0):
        self.status = status
        self.stream = io.BytesIO(payload)
        self.forbid_read = forbid_read
        self.short_reads = short_reads
        self.clock = clock
        self.delay = delay
        self.read_sizes = []
        self.closed = False

    def getcode(self):
        return self.status

    def read(self, size):
        self.read_sizes.append(size)
        if self.forbid_read:
            raise AssertionError("Error bodies must never be read")
        if size <= 0 or size > 64 * 1024:
            raise AssertionError("Unbounded read")
        if self.clock is not None:
            self.clock.advance(self.delay)
        return self.stream.read(min(size, 3) if self.short_reads else size)

    def close(self):
        self.closed = True
        self.stream.close()


class Read1Response(Response):
    def read1(self, size):
        return super().read(size)

    def read(self, size):
        raise AssertionError("read1 must be preferred over read")


class Opener:
    def __init__(self, *outcomes, clock=None, delay=0):
        self.outcomes = list(outcomes)
        self.calls = []
        self.clock = clock
        self.delay = delay

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if self.clock is not None:
            self.clock.advance(self.delay)
        if not self.outcomes:
            raise AssertionError("Unexpected additional request")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def json_response(value, status=200):
    return Response(status, json.dumps(value).encode("utf-8"))


def page(pods=(), cursor=None, more=False):
    return {"pods": list(pods), "pagination": {"nextCursor": cursor, "hasNextPage": more}}


class MemoryHTTPS(BaseHandler):
    """Feed real urllib error/redirect processing without reaching a socket."""

    handler_order = 100

    def __init__(self, status, location):
        self.status = status
        self.location = location
        self.calls = []
        self.body = Response(forbid_read=True)

    def https_open(self, request):
        self.calls.append(request)
        headers = Message()
        headers["Location"] = self.location
        result = addinfourl(self.body, headers, request.full_url, self.status)
        result.msg = "offline redirect"
        return result


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, ENV, clear=True))
        self.enterContext(patch("socket.create_connection", side_effect=AssertionError("No network")))
        self.enterContext(patch("socket.socket", side_effect=AssertionError("No sockets")))
        self.clock = Clock()
        self.enterContext(patch.object(api, "monotonic", self.clock))

    def assert_error(self, status, operation):
        error = None
        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                operation()
        except api.ProviderError as caught:
            error = caught
            rendered = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if error is None:
            self.fail("Expected ProviderError")
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(error.status, status)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        for marker in ENV.values():
            self.assertNotIn(marker, rendered)
            self.assertNotIn(marker, repr(error))
        self.assertNotIn("untrusted-body", rendered)
        return error

    def test_import_and_construction_do_not_connect_and_repr_is_safe(self):
        with patch.object(api, "build_opener", wraps=api.build_opener) as factory:
            provider = api.RunPodAPI()
            artifact = api.ArtifactClient()
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(repr(provider), "RunPodAPI()")
        self.assertEqual(repr(artifact), "ArtifactClient()")
        for client in (provider, artifact):
            handlers = client._opener.handlers
            self.assertEqual(sum(isinstance(h, HTTPRedirectHandler) for h in handlers), 1)

    def test_opener_construction_errors_and_exception_status_are_sanitized(self):
        with patch.object(api, "build_opener", side_effect=OSError(ENV["RUNPOD_API_KEY"])):
            self.assert_error(None, api.RunPodAPI)
        for status in (ENV["RUNPOD_API_KEY"], True, {}, -1):
            error = api.ProviderError(status)
            self.assertIsNone(error.status)
            self.assertNotIn(ENV["RUNPOD_API_KEY"], repr(error))

    def test_credentials_required_and_header_injection_rejected(self):
        for variable, cls in (("RUNPOD_API_KEY", api.RunPodAPI),
                              ("AGE_ARTIFACT_TOKEN", api.ArtifactClient)):
            for value in (None, "", "space token", "bad\r\nHeader:value", "nonascii\u00e9", "x" * 4097):
                with self.subTest(variable=variable, invalid_length=0 if value is None else len(value)):
                    with patch.dict(os.environ, {}, clear=True):
                        if value is not None:
                            os.environ[variable] = value
                        self.assert_error(None, lambda: cls(Opener()))

    def test_credentials_captured_at_construction_and_isolated(self):
        pod = {"id": "pod_1"}
        provider_opener = Opener(json_response(pod))
        artifact_opener = Opener(Response(payload=b"artifact"))
        provider = api.RunPodAPI(provider_opener)
        artifact = api.ArtifactClient(artifact_opener)
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(provider.get_pod("pod_1"), pod)
            self.assertEqual(artifact.fetch("pod_1", "receipt.json"), b"artifact")
        for opener, key, other in ((provider_opener, "RUNPOD_API_KEY", "AGE_ARTIFACT_TOKEN"),
                                   (artifact_opener, "AGE_ARTIFACT_TOKEN", "RUNPOD_API_KEY")):
            request, timeout = opener.calls[0]
            self.assertEqual(timeout, 10)
            self.assertEqual(request.get_header("Authorization"), "Bearer " + ENV[key])
            self.assertNotIn("Authorization", request.headers)
            self.assertNotIn(ENV[other], repr(request.header_items()))
            self.assertNotIn(ENV[key], request.full_url)
        with patch.dict(os.environ, {"AGE_ARTIFACT_TOKEN": ENV["AGE_ARTIFACT_TOKEN"]}, clear=True):
            api.ArtifactClient(Opener())  # No API key needed or read.

    def test_create_get_delete_contracts(self):
        body = {"name": "canary", "image": "registry/image:tag", "env": {"LABEL": "value"}}
        pod = dict(body, id="pod_1", status="RUNNING", cost=0.2)
        deleted = Response(204, forbid_read=True)
        created = json_response(pod, 201)
        fetched = json_response(pod)
        opener = Opener(created, fetched, deleted)
        provider = api.RunPodAPI(opener)
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            self.assertEqual(provider.create_pod(body), pod)
            self.assertEqual(provider.get_pod("pod_1"), pod)
            self.assertEqual(provider.terminate_pod("pod_1"), "ACK_204")
        self.assertEqual(output.getvalue(), "")
        requests = [call[0] for call in opener.calls]
        self.assertEqual([r.get_method() for r in requests], ["POST", "GET", "DELETE"])
        self.assertEqual(requests[0].full_url, "https://api.runpod.io/v2/pods")
        self.assertEqual(requests[1].full_url, "https://api.runpod.io/v2/pods/pod_1")
        self.assertEqual(requests[2].full_url, requests[1].full_url)
        self.assertEqual(json.loads(requests[0].data), body)
        self.assertEqual(requests[0].get_header("Content-type"), "application/json")
        self.assertEqual(deleted.read_sizes, [])
        self.assertTrue(all(response.closed for response in (created, fetched, deleted)))

    def test_id_validation_precedes_any_request(self):
        opener = Opener()
        provider = api.RunPodAPI(opener)
        artifact = api.ArtifactClient(opener)
        for value in (None, 12, [], "", "x" * 129, "../pod", "pod/other", "pod?x", "pod#x",
                      "pod@example.com", "https://other", "pod\n", "pod%2f", "\u00e9", "pod.name"):
            for operation in (lambda: provider.get_pod(value), lambda: provider.terminate_pod(value),
                              lambda: artifact.fetch(value, "receipt.json")):
                self.assert_error(None, operation)
        self.assertEqual(opener.calls, [])
        for value in ("A", "x" * 128, "a_Z-09"):
            opener.outcomes.append(json_response({"id": value}))
            self.assertEqual(provider.get_pod(value), {"id": value})

    def test_invalid_create_body_never_sends(self):
        opener = Opener()
        provider = api.RunPodAPI(opener)
        cyclic = {}
        cyclic["self"] = cyclic
        for body in (None, [], "text", {"not_json": object()}, {"x": float("nan")}, cyclic):
            self.assert_error(None, lambda: provider.create_pod(body))
        self.assertEqual(opener.calls, [])

    def test_http_errors_never_read_bodies_and_only_expose_status(self):
        for status in (301, 302, 303, 307, 308, 400, 401, 403, 404, 429, 500, 502, 503, 504):
            for raised in (False, True):
                with self.subTest(status=status, raised=raised):
                    response = Response(status, b"untrusted-body", forbid_read=True)
                    outcome = HTTPError("https://api.runpod.io/v2/pods", status,
                                        ENV["RUNPOD_API_KEY"], {}, response) if raised else response
                    opener = Opener(outcome)
                    self.assert_error(status, lambda: api.RunPodAPI(opener).create_pod({}))
                    self.assertEqual(response.read_sizes, [])
                    self.assertTrue(response.closed)
                    self.assertEqual(len(opener.calls), 1)

    def test_404_get_and_delete_are_idempotent_but_not_create(self):
        for raised in (False, True):
            for method, expected in (("get_pod", None), ("terminate_pod", "NOT_FOUND_404")):
                response = Response(404, forbid_read=True)
                outcome = HTTPError("https://api.runpod.io/v2/pods/p", 404, "offline", {}, response) if raised else response
                provider = api.RunPodAPI(Opener(outcome))
                self.assertEqual(getattr(provider, method)("p"), expected)
                self.assertEqual(response.read_sizes, [])
                self.assertTrue(response.closed)

    def test_unexpected_success_statuses_fail_without_reading(self):
        for method, argument, status in (("create_pod", {}, 200), ("get_pod", "p", 201),
                                         ("terminate_pod", "p", 200), ("get_pod", "p", 204)):
            response = Response(status, forbid_read=True)
            provider = api.RunPodAPI(Opener(response))
            self.assert_error(status, lambda: getattr(provider, method)(argument))
            self.assertEqual(response.read_sizes, [])
            self.assertTrue(response.closed)

    def test_network_failures_are_sanitized_and_create_is_never_retried(self):
        for failure in (URLError(ENV["RUNPOD_API_KEY"]), TimeoutError(ENV["RUNPOD_API_KEY"]),
                        OSError(ENV["RUNPOD_API_KEY"]), ValueError(ENV["RUNPOD_API_KEY"])):
            opener = Opener(failure, json_response({"id": "must_not_retry"}, 201))
            self.assert_error(None, lambda: api.RunPodAPI(opener).create_pod({}))
            self.assertEqual(len(opener.calls), 1)

    def test_read_and_close_failures_are_sanitized(self):
        for method in ("read", "read1", "close"):
            response_cls = Read1Response if method == "read1" else Response
            response = response_cls(payload=b'{"id":"p"}')
            with patch.object(response, method, side_effect=OSError(ENV["RUNPOD_API_KEY"])):
                self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
            if method != "close":
                self.assertTrue(response.closed)

    def test_invalid_json_and_pod_shapes_fail_closed(self):
        for payload in (b"", b"untrusted-body", b"\xff", b"[]", b"null", b"1", b"{}",
                        b'{"id":false}', b'{"id":"../p"}', b'{"id":"other"}',
                        b'{"id":"p","id":"p"}', b'{"id":"p","cost":NaN}',
                        b'{"id":"p","cost":Infinity}', b'{"id":"p"} trailing'):
            response = Response(payload=payload)
            self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
            self.assertTrue(response.closed)
        opener = Opener(Response(201, b"untrusted-body"), json_response({"id": "retry"}, 201))
        self.assert_error(None, lambda: api.RunPodAPI(opener).create_pod({}))
        self.assertEqual(len(opener.calls), 1)

    def test_api_body_limit_and_short_reads(self):
        limit = 8 * 1024 * 1024
        prefix, suffix = b'{"id":"p","padding":"', b'"}'
        payload = prefix + b"x" * (limit - len(prefix) - len(suffix)) + suffix
        response = Response(payload=payload)
        self.assertEqual(api.RunPodAPI(Opener(response)).get_pod("p")["id"], "p")
        oversized = Response(payload=payload + b" ")
        self.assert_error(None, lambda: api.RunPodAPI(Opener(oversized)).get_pod("p"))
        self.assertTrue(oversized.closed)
        short = Response(payload=b'{"id":"p"}', short_reads=True)
        self.assertEqual(api.RunPodAPI(Opener(short)).get_pod("p"), {"id": "p"})

    def test_read1_is_preferred_and_short_reads_complete(self):
        response = Read1Response(payload=b'{"id":"p"}', short_reads=True)
        self.assertEqual(api.RunPodAPI(Opener(response)).get_pod("p"), {"id": "p"})
        self.assertGreater(len(response.read_sizes), 1)
        self.assertTrue(response.closed)
        self.assertTrue(response.stream.closed)

    def test_request_deadline_spans_open_and_reads_including_eof(self):
        cases = ((api.RunPodAPI, "create_pod", ({},), 201),
                 (api.RunPodAPI, "get_pod", ("p",), 200),
                 (api.ArtifactClient, "fetch", ("p", "receipt.json"), 200))
        for cls, method, args, status in cases:
            for response_cls in (Response, Read1Response):
                with self.subTest(method=method, reader=response_cls.__name__):
                    response = response_cls(status, b'{"id":"p"}', clock=self.clock, delay=2)
                    opener = Opener(response, clock=self.clock, delay=7)
                    # Open + data = 9s; EOF arrives at 11s and must not succeed.
                    self.assert_error(None, lambda: getattr(cls(opener), method)(*args))
                    self.assertEqual(len(response.read_sizes), 2)
                    self.assertEqual(len(opener.calls), 1)
                    self.assertEqual(opener.calls[0][1], 10)
                    self.assertTrue(response.closed)
                    self.assertTrue(response.stream.closed)

    def test_trickle_response_stops_at_deadline_without_draining(self):
        for cls, method, args in ((api.RunPodAPI, "get_pod", ("p",)),
                                  (api.ArtifactClient, "fetch", ("p", "canary.log"))):
            for response_cls in (Response, Read1Response):
                with self.subTest(method=method, reader=response_cls.__name__):
                    response = response_cls(payload=b'{"id":"p","padding":"' + b"x" * 100 + b'"}',
                                            short_reads=True, clock=self.clock, delay=2)
                    opener = Opener(response)
                    self.assert_error(None, lambda: getattr(cls(opener), method)(*args))
                    self.assertEqual(len(response.read_sizes), 5)
                    self.assertEqual(len(opener.calls), 1)
                    self.assertTrue(response.closed)
                    self.assertTrue(response.stream.closed)

    def test_slow_open_rejects_success_missing_and_http_errors_without_reading(self):
        cases = ((api.RunPodAPI, "create_pod", ({},), 201),
                 (api.RunPodAPI, "get_pod", ("p",), 200),
                 (api.RunPodAPI, "terminate_pod", ("p",), 204),
                 (api.RunPodAPI, "get_pod", ("p",), 404),
                 (api.RunPodAPI, "terminate_pod", ("p",), 404),
                 (api.ArtifactClient, "fetch", ("p", "receipt.json"), 200),
                 (api.ArtifactClient, "fetch", ("p", "receipt.json"), 503))
        for cls, method, args, status in cases:
            for raised in ((False, True) if status >= 400 else (False,)):
                for delay in (10, 11):
                    with self.subTest(method=method, status=status, raised=raised, delay=delay):
                        response = Response(status, forbid_read=True)
                        outcome = HTTPError("https://offline.invalid/", status,
                                            ENV["RUNPOD_API_KEY"], {}, response) if raised else response
                        opener = Opener(outcome, clock=self.clock, delay=delay)
                        self.assert_error(None, lambda: getattr(cls(opener), method)(*args))
                        self.assertEqual(len(opener.calls), 1)
                        self.assertEqual(opener.calls[0][1], 10)
                        self.assertEqual(response.read_sizes, [])
                        self.assertTrue(response.closed)
                        self.assertTrue(response.stream.closed)

    def test_expired_request_does_not_start_open_or_read(self):
        request_factory = api.Request

        def slow_request(*args, **kwargs):
            self.clock.advance(10)
            return request_factory(*args, **kwargs)

        opener = Opener()
        with patch.object(api, "Request", side_effect=slow_request):
            self.assert_error(None, lambda: api.RunPodAPI(opener).get_pod("p"))
        self.assertEqual(opener.calls, [])

        response = Response(forbid_read=True)

        def slow_status():
            self.clock.advance(10)
            return 200

        with patch.object(response, "getcode", side_effect=slow_status):
            self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
        self.assertEqual(response.read_sizes, [])
        self.assertTrue(response.closed)

    def test_late_close_cannot_turn_expired_request_into_success(self):
        response = json_response({"id": "p"})
        close = response.close

        def slow_close():
            close()
            self.clock.advance(10)

        with patch.object(response, "close", side_effect=slow_close):
            self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
        self.assertTrue(response.closed)
        self.assertTrue(response.stream.closed)

    def test_pagination_follows_empty_pages_and_encodes_cursor(self):
        cursor = "next &/?#=\u00e9"
        opener = Opener(json_response(page([{"id": "a"}], cursor, True)),
                        json_response(page([], "last", True)),
                        json_response(page([{"id": "b"}])))
        self.assertEqual(api.RunPodAPI(opener).list_pods(), [{"id": "a"}, {"id": "b"}])
        self.assertEqual(len(opener.calls), 3)
        self.assertEqual(opener.calls[0][0].full_url, "https://api.runpod.io/v2/pods")
        parsed = urlsplit(opener.calls[1][0].full_url)
        self.assertEqual((parsed.scheme, parsed.netloc, parsed.path),
                         ("https", "api.runpod.io", "/v2/pods"))
        self.assertEqual(parse_qs(parsed.query), {"cursor": [cursor]})
        self.assertEqual(parsed.fragment, "")
        self.assertEqual(api.RunPodAPI(Opener(json_response(page()))).list_pods(), [])

    def test_inventory_visitor_retains_positive_records_but_raises_on_later_failure(self):
        opener = Opener(json_response(page([{"id": "owned"}], "next", True)),
                        Response(503, forbid_read=True))
        visited = []
        self.assert_error(503, lambda: api.RunPodAPI(opener).visit_pods(visited.append))
        self.assertEqual(visited, [{"id": "owned"}])
        self.assertEqual(len(opener.calls), 2)

    def test_pagination_shapes_and_cycles_fail_closed(self):
        invalid_pages = [[], {}, {"pods": [], "pagination": None},
                         {"pods": {}, "pagination": {"nextCursor": None, "hasNextPage": False}},
                         {"pods": [], "pagination": {"hasNextPage": False}},
                         {"pods": [], "pagination": {"nextCursor": None}},
                         page([None]), page([{}]), page([{"id": "../p"}]),
                         page(cursor=12), page(cursor=[], more=True), page(more=True),
                         page(cursor="", more=True), page(cursor="\ud800", more=True),
                         page(more=1), page(more="false")]
        for invalid in invalid_pages:
            opener = Opener(json_response(page([{"id": "valid"}], "next", True)), json_response(invalid))
            self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
        opener = Opener(json_response(page(cursor="loop", more=True)),
                        json_response(page(cursor="loop", more=True)))
        self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
        self.assertEqual(len(opener.calls), 2)

    def test_pagination_limit_includes_exactly_100_pages(self):
        first_99 = [json_response(page(cursor=str(i), more=True)) for i in range(99)]
        opener = Opener(*first_99, json_response(page([{"id": "last"}])))
        self.assertEqual(api.RunPodAPI(opener).list_pods(), [{"id": "last"}])
        self.assertEqual(len(opener.calls), 100)
        opener = Opener(*(json_response(page(cursor=str(i), more=True)) for i in range(101)))
        self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
        self.assertEqual(len(opener.calls), 100)

    def test_pagination_deadline_is_shared_by_page_opens_and_reads(self):
        for phase in ("open", "read"):
            for more in (False, True):
                with self.subTest(phase=phase, more=more):
                    responses = []
                    for i in range(4):
                        payload = json.dumps(page([{"id": "p%d" % i}], str(i), i < 3 or more)).encode()
                        responses.append(Response(payload=payload, clock=self.clock,
                                                  delay=4.5 if phase == "read" else 0))
                    unused = json_response(page())
                    opener = Opener(*responses, unused, clock=self.clock,
                                    delay=9 if phase == "open" else 0)
                    # Each page takes <10s, but page four exceeds the shared 30s.
                    self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
                    self.assertEqual(len(opener.calls), 4)
                    self.assertTrue(all(timeout == 10 for _, timeout in opener.calls))
                    self.assertEqual(len(responses[-1].read_sizes), 0 if phase == "open" else 1)
                    self.assertTrue(all(response.closed and response.stream.closed
                                        for response in responses))
                    self.assertFalse(unused.closed)
                    self.assertEqual(unused.read_sizes, [])

    def test_pagination_deadline_includes_parsing_before_return_or_next_page(self):
        decode = api._json_object

        def slow_decode(payload):
            result = decode(payload)
            self.clock.advance(15)
            return result

        for more in (False, True):
            responses = [json_response(page([{"id": "a"}], "next", True)),
                         json_response(page([{"id": "b"}], "last", more))]
            opener = Opener(*responses)
            with patch.object(api, "_json_object", side_effect=slow_decode):
                self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
            self.assertEqual(len(opener.calls), 2)
            self.assertTrue(all(response.closed for response in responses))

    def test_pagination_aggregate_byte_limit_accepts_exact_and_rejects_overflow(self):
        self.assertEqual(api._LIST_LIMIT, 16 * 1024 * 1024)
        first = json.dumps(page([{"id": "a"}], "next", True)).encode()
        last = json.dumps(page([{"id": "b"}])).encode()
        # Scale only the aggregate cap; neither page reaches the per-page limit.
        for excess in (0, 1):
            responses = [Response(payload=first), Response(payload=last + b" " * excess)]
            opener = Opener(*responses)
            with patch.object(api, "_LIST_LIMIT", len(first) + len(last)):
                if excess:
                    self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
                else:
                    self.assertEqual(api.RunPodAPI(opener).list_pods(), [{"id": "a"}, {"id": "b"}])
            self.assertEqual(len(opener.calls), 2)
            self.assertLessEqual(max(responses[-1].read_sizes), len(last) + 1)
            self.assertTrue(all(response.closed for response in responses))

    def test_pagination_exhausted_byte_budget_does_not_open_another_page(self):
        payload = json.dumps(page([{"id": "a"}], "next", True)).encode()
        response, unused = Response(payload=payload), json_response(page())
        opener = Opener(response, unused)
        with patch.object(api, "_LIST_LIMIT", len(payload)):
            self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
        self.assertEqual(len(opener.calls), 1)
        self.assertTrue(response.closed)
        self.assertFalse(unused.closed)

    def test_pagination_pod_count_is_bounded_across_pages(self):
        for count in (10000, 10001):
            first = [{"id": "p%d" % i} for i in range(9999)]
            last = [{"id": "last%d" % i} for i in range(count - len(first))]
            responses = [json_response(page(first, "next", True)), json_response(page(last))]
            opener = Opener(*responses)
            if count == 10000:
                self.assertEqual(api.RunPodAPI(opener).list_pods(), first + last)
            else:
                self.assert_error(None, lambda: api.RunPodAPI(opener).list_pods())
            self.assertEqual(len(opener.calls), 2)
            self.assertTrue(all(response.closed for response in responses))

    def test_artifact_names_fixed_origin_and_binary_payload(self):
        payload = b"\x00\xffprivate artifact\n"
        for name in ("receipt.json", "canary.log", "result.json"):
            opener = Opener(Response(payload=payload, short_reads=True))
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                self.assertEqual(api.ArtifactClient(opener).fetch("pod_1", name), payload)
            self.assertEqual(output.getvalue(), "")
            request, timeout = opener.calls[0]
            self.assertEqual(request.full_url, "https://pod_1-8080.proxy.runpod.net/" + name)
            self.assertEqual(request.get_method(), "GET")
            self.assertIsNone(request.data)
            self.assertEqual(timeout, 10)
        opener = Opener()
        for name in (None, [], "", "../receipt.json", "/receipt.json", "receipt.json?x", "other", "RESULT.JSON"):
            self.assert_error(None, lambda: api.ArtifactClient(opener).fetch("p", name))
        self.assertEqual(opener.calls, [])

    def test_artifact_transients_only_and_no_error_body_reads(self):
        for status in (404, 502, 503, 504, 401, 403, 429, 500, 302):
            for raised in (False, True):
                response = Response(status, forbid_read=True)
                outcome = HTTPError("https://p-8080.proxy.runpod.net/result.json", status,
                                    ENV["AGE_ARTIFACT_TOKEN"], {}, response) if raised else response
                opener = Opener(outcome)
                client = api.ArtifactClient(opener)
                if status in (404, 502, 503, 504):
                    self.assertIsNone(client.fetch("p", "result.json"))
                else:
                    self.assert_error(status, lambda: client.fetch("p", "result.json"))
                self.assertEqual(response.read_sizes, [])
                self.assertTrue(response.closed)
                self.assertEqual(len(opener.calls), 1)
        client = api.ArtifactClient(Opener(URLError(ENV["AGE_ARTIFACT_TOKEN"])))
        self.assert_error(None, lambda: client.fetch("p", "result.json"))

    def test_artifact_byte_limit_and_empty_payload(self):
        for size in (0, 4 * 1024 * 1024, 4 * 1024 * 1024 + 1):
            response = Response(payload=b"x" * size)
            client = api.ArtifactClient(Opener(response))
            if size <= 4 * 1024 * 1024:
                self.assertEqual(client.fetch("p", "canary.log"), b"x" * size)
            else:
                self.assert_error(None, lambda: client.fetch("p", "canary.log"))
            self.assertTrue(response.closed)

    def test_real_urllib_redirects_are_rejected_before_read_or_follow(self):
        for status in (301, 302, 303, 307, 308):
            for location in ("https://untrusted.invalid/", "http://untrusted.invalid/",
                             "https://api.runpod.io/v2/pods/other", "/relative"):
                for cls in (api.RunPodAPI, api.ArtifactClient):
                    handler = MemoryHTTPS(status, location)
                    # Starts with urllib's normal redirect handler; the client must disable it.
                    opener = build_opener(ProxyHandler({}), handler)
                    client = cls(opener)
                    operation = (lambda: client.get_pod("p")) if cls is api.RunPodAPI else (
                        lambda: client.fetch("p", "receipt.json"))
                    self.assert_error(status, operation)
                    self.assertEqual(len(handler.calls), 1)
                    self.assertEqual(handler.body.read_sizes, [])
                    self.assertTrue(handler.body.closed)

    def test_delete_ack_and_not_found_are_never_collapsed(self):
        # B1: DELETE outcomes must remain distinguishable to the controller.
        ack = Response(204, forbid_read=True)
        self.assertEqual(api.RunPodAPI(Opener(ack)).terminate_pod("p"), "ACK_204")
        not_found = Response(404, forbid_read=True)
        self.assertEqual(api.RunPodAPI(Opener(not_found)).terminate_pod("p"), "NOT_FOUND_404")
        for status in (401, 403, 429, 500, 502, 503):
            response = Response(status, forbid_read=True)
            error = self.assert_error(status, lambda: api.RunPodAPI(Opener(response)).terminate_pod("p"))
            self.assertIsNone(error.category)
        transport_failure = Opener(URLError("offline"))
        error = self.assert_error(None, lambda: api.RunPodAPI(transport_failure).terminate_pod("p"))
        self.assertIsNone(error.category)

    def test_schema_invalid_category_distinguishes_decode_from_transport(self):
        # B4: coarsely distinguish a malformed provider response from a transport failure.
        for payload in (b"not json", b"[]", b'{"id":"../p"}', b'{"id":false}'):
            error = self.assert_error(None, lambda: api.RunPodAPI(
                Opener(Response(payload=payload))).get_pod("p"))
            self.assertEqual(error.category, "SCHEMA_INVALID")
        error = self.assert_error(None, lambda: api.RunPodAPI(
            Opener(URLError("offline"))).get_pod("p"))
        self.assertIsNone(error.category)
        error = self.assert_error(500, lambda: api.RunPodAPI(
            Opener(Response(500, forbid_read=True))).get_pod("p"))
        self.assertIsNone(error.category)
        for value in (ENV["RUNPOD_API_KEY"], True, {}, -1, "OTHER_CATEGORY"):
            self.assertIsNone(api.ProviderError(status=None, category=value).category)
        self.assertEqual(api.ProviderError(category="SCHEMA_INVALID").category, "SCHEMA_INVALID")

    def test_malformed_transport_responses_fail_safely(self):
        for status in (None, "200", True, -1):
            response = Response(status, forbid_read=True)
            self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
            self.assertEqual(response.read_sizes, [])
            self.assertTrue(response.closed)
        response = Response()
        with patch.object(response, "read", return_value="not bytes"):
            self.assert_error(None, lambda: api.RunPodAPI(Opener(response)).get_pod("p"))
        self.assertTrue(response.closed)


if __name__ == "__main__":
    unittest.main()