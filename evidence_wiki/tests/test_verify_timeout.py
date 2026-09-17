"""Anchor verification under an engine stall (pre-Campaign-4 repair,
2026-09-17; Daedalus #345: 0.13% of engine calls stall 5-13 s).

A fake verify-anchor endpoint stalls for a configurable time, then answers
valid with both bindings true. Controls:

    positive   stall 2 s under a 30 s timeout -> verified True, attempts 1
    defect     the OLD behaviour (6 s timeout, no retry) against an 8 s
               stall -> verify_call_failed: the fossil would have landed
               unverified with no alarm. Reproduced with timeout=1 here
               (the class, not the seconds).
    retry      first call times out, the second answers -> verified True,
               attempts 2 (the call is read-only; one retry is bounded)
    cheat      a non-timeout failure (HTTP 500) is NOT retried and is
               recorded as verify_call_failed with the error name
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

import pytest

from ew import closure


class _Fake:
    def __init__(self, stalls, status=200):
        self.stalls = list(stalls)     # per-call stall seconds, consumed in order
        self.status = status
        self.calls = 0
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                outer.calls += 1
                n = self.headers.get("Content-Length")
                self.rfile.read(int(n) if n else 0)
                stall = outer.stalls.pop(0) if outer.stalls else 0
                time.sleep(stall)
                body = json.dumps({"valid": True, "checks": {"binds_exp_id": True, "binds_obs_id": True,
                                                              "entry_hash_matches": True},
                                   "engine": {"engine_instance_id": "eng_test"}}).encode()
                try:
                    self.send_response(outer.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except (ConnectionAbortedError, BrokenPipeError):
                    pass

        self.srv = HTTPServer(("127.0.0.1", 0), H)
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def stop(self):
        self.srv.shutdown()


def _enc():
    return SimpleNamespace(sfe_world_id="wld_1", sfe_event_id="evt_" + "a" * 16,
                           sfe_entry_hash="sha256:" + "b" * 64,
                           producer={"exp_id": "exp_1", "obs_id": "obs_1"},
                           sfe_engine_instance_id="eng_test")


@pytest.fixture
def cfg(monkeypatch):
    def _set(port, timeout):
        monkeypatch.setattr(closure, "_SFE_CFG", {"url": f"http://127.0.0.1:{port}", "ca": None, "token": "t"})
        monkeypatch.setenv("EW_SFE_VERIFY_TIMEOUT", str(timeout))
    return _set


def test_positive_stall_inside_timeout_verifies(cfg):
    f = _Fake([2])
    try:
        cfg(f.port, 30)
        ok, checks = closure.verify_sfe_anchor(_enc())
        assert ok is True and f.calls == 1, checks
    finally:
        f.stop()


def test_defect_reproduced_short_timeout_records_failure(cfg):
    f = _Fake([3, 3])
    try:
        cfg(f.port, 1)
        ok, checks = closure.verify_sfe_anchor(_enc())
        assert ok is False and checks["reason"] == "verify_call_failed" and checks["timed_out"] is True
        assert checks["attempts"] == 2 and checks["timeout_s"] == 1.0
    finally:
        f.stop()


def test_retry_after_one_timeout_verifies(cfg):
    f = _Fake([3, 0])
    try:
        cfg(f.port, 1.5)
        ok, checks = closure.verify_sfe_anchor(_enc())
        assert ok is True and f.calls == 2, checks
    finally:
        f.stop()


def test_cheat_non_timeout_failure_is_not_retried(cfg):
    f = _Fake([0, 0], status=500)
    try:
        cfg(f.port, 30)
        ok, checks = closure.verify_sfe_anchor(_enc())
        assert ok is False and checks["reason"] == "verify_call_failed" and checks["attempts"] == 1
        assert checks["timed_out"] is False and f.calls == 1
    finally:
        f.stop()
