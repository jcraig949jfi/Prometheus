"""The conformance gate at Archaeon's boundaries: fail-closed against a fake
engine whose identity can be set per test. The FULL gate (Harmonia's script)
is exercised by the committed demonstration receipt against real engines
(archaeon/docs/h0h5/CONFORMANCE_WIRING_RECEIPT_2026-09-11.json); here the
identity tier, the retry policy, the cache and the halt plumbing are tested
without the network."""
from __future__ import annotations

import http.server
import json
import os
import threading

import pytest

from archaeon import conformance as C


class _Engine:
    def __init__(self, version: dict, fail: bool = False):
        self.version, self.fail = version, fail
        srv = self

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if srv.fail or self.path != "/v2/version":
                    self.send_response(500); self.end_headers(); return
                body = json.dumps(srv.version).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body)

            def log_message(self, *a):
                pass
        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), H)
        self.base = "http://127.0.0.1:{}/v2".format(self.httpd.server_address[1])
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def stop(self):
        self.httpd.shutdown()


CONTRACT_ENGINE = {"base_url": "http://unused/v2", "api": "v2", "schema_version": 8,
                   "engine_instance_id": "eng_contract", "engine_source_hash": "sha256:build-A",
                   "science_profile": "warn", "session_enforcement": "advisory"}


def _cfg(tmp_path, base, contract_engine=CONTRACT_ENGINE, **kw):
    cp = tmp_path / "contract.json"
    cp.write_text(json.dumps({"engine": contract_engine, "routes": [{"method": "GET", "path": "/v2/version", "requires_session_key": False}]}), encoding="utf-8")
    return C.ConformanceConfig(contract_path=str(cp), base_url=base, cacert="", retries=kw.pop("retries", 1), backoff_s=0.01,
                               timeout_s=2.0, cache_path=kw.pop("cache_path", str(tmp_path / "cache.json")), **kw)


@pytest.fixture(autouse=True)
def _not_production(monkeypatch):
    # the gate must run in these tests even though VIV_SCHEMA is the test schema
    monkeypatch.delenv("ARCHAEON_CONFORMANCE_MODE", raising=False)
    monkeypatch.setattr(C, "_production", lambda: False)


def test_matching_identity_runs_the_full_gate_once_then_caches(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(C, "full_gate", lambda cfg, contract, base, cacert: (calls.append(1) or
                        {"exit": 0, "state": "CONFORMANT", "at": "2026-09-11T00:00:00+00:00", "elapsed_s": 0.1, "stdout_tail": "CONFORMANT -- safe to proceed"}))
    e = _Engine(dict(CONTRACT_ENGINE))
    try:
        cfg = _cfg(tmp_path, e.base)
        r1 = C.require(cfg); r2 = C.require(cfg)
    finally:
        e.stop()
    assert r1["state"] == "CONFORMANT" and r1["halted"] is False and r1["gate"]["mode"] == "full"
    assert r2["gate"]["mode"] == "cached" and calls == [1]
    c = C.compact(r1)
    assert c["live"]["engine_instance_id"] == "eng_contract" and c["contract"]["hash"].startswith("sha256:")


def test_wrong_instance_halts_before_the_full_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "full_gate", lambda *a: pytest.fail("full gate must not run on a wrong instance"))
    e = _Engine(dict(CONTRACT_ENGINE, engine_instance_id="eng_other_ledger"))
    try:
        with pytest.raises(C.ConformanceHalt) as ex:
            C.require(_cfg(tmp_path, e.base))
    finally:
        e.stop()
    assert ex.value.record["state"] == "WRONG_INSTANCE" and ex.value.record["halted"] is True


def test_unreachable_retries_then_halts(tmp_path):
    e = _Engine(dict(CONTRACT_ENGINE), fail=True)
    try:
        with pytest.raises(C.ConformanceHalt) as ex:
            C.require(_cfg(tmp_path, e.base, retries=2))
    finally:
        e.stop()
    rec = ex.value.record
    assert rec["state"] == "UNREACHABLE" and len(rec["attempts"]) == 3 and not any(a["ok"] for a in rec["attempts"])


def test_changed_build_forces_the_full_gate_and_drift_halts(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "full_gate", lambda cfg, contract, base, cacert:
                        {"exit": 1, "state": "DRIFT", "at": "2026-09-11T00:00:00+00:00", "elapsed_s": 0.1, "stdout_tail": "DRIFT -- STOP THE LOOP."})
    e = _Engine(dict(CONTRACT_ENGINE, engine_source_hash="sha256:build-B"))
    try:
        with pytest.raises(C.ConformanceHalt) as ex:
            C.require(_cfg(tmp_path, e.base))
    finally:
        e.stop()
    assert ex.value.record["state"] == "DRIFT" and ex.value.record["gate"]["mode"] == "full"


def test_incomplete_proceeds_only_when_routes_are_covered(tmp_path, monkeypatch):
    e = _Engine(dict(CONTRACT_ENGINE, engine_source_hash="sha256:build-B"))
    try:
        monkeypatch.setattr(C, "full_gate", lambda *a: {"exit": 0, "state": "CONFORMANT", "at": "2026-09-11T00:00:00+00:00", "elapsed_s": 0.1,
                                                          "stdout_tail": "Every route you declared IS in the contract, so its claims"})
        r = C.require(_cfg(tmp_path, e.base))
        assert r["state"] == "INCOMPLETE_PROCEED" and r["halted"] is False
        monkeypatch.setattr(C, "full_gate", lambda *a: {"exit": 3, "state": "INCOMPLETE", "at": "2026-09-11T00:00:00+00:00", "elapsed_s": 0.1,
                                                          "stdout_tail": "HALT: 1 route(s) you will call are NOT in the contract"})
        with pytest.raises(C.ConformanceHalt) as ex:
            C.require(_cfg(tmp_path, e.base, cache_path=str(tmp_path / "cache2.json")))
        assert ex.value.record["state"] == "INCOMPLETE_HALT"
    finally:
        e.stop()


def test_the_gate_cannot_be_switched_off_in_production(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "_production", lambda: True)
    monkeypatch.setenv("ARCHAEON_CONFORMANCE_MODE", "off")
    e = _Engine(dict(CONTRACT_ENGINE, engine_instance_id="eng_other_ledger"))
    try:
        with pytest.raises(C.ConformanceHalt):
            C.require(_cfg(tmp_path, e.base, enabled=False))
    finally:
        e.stop()


def test_default_config_is_enabled_and_declares_the_consumer_routes():
    from archaeon import config as cfg
    assert cfg.DEFAULT.conformance.enabled is True
    assert cfg.DEFAULT.conformance.consumer_routes == ("GET /v2/version",)
    assert cfg.DEFAULT.conformance.retries >= 1


def test_submit_stamps_the_record_and_halts_before_writing(monkeypatch):
    """The queue write boundary: a halt writes nothing; a pass stamps every candidate."""
    from archaeon import vivqueue as vq
    halted = {"state": "WRONG_INSTANCE", "halted": True, "reason": "test"}
    monkeypatch.setattr(C, "require", lambda cfg=None: (_ for _ in ()).throw(C.ConformanceHalt(halted)))
    monkeypatch.setattr(vq, "assert_queue_ready", lambda conn: None)

    class Conn:
        def cursor(self):
            pytest.fail("no cursor must be opened when the gate halts")
    with pytest.raises(C.ConformanceHalt):
        vq.submit(Conn(), candidates=[{"spec": {"spec_version": 3, "work": {"kind": "x", "payload": {}}}, "spec_hash": "h", "family_id": None,
                                       "arm_id": None, "replication_of": None, "request_key": "rk", "source_evidence": {}}],
                  selected_index=0, source_reason="human")
