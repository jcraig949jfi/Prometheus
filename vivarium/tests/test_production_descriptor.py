"""viv/production.py -- the production descriptor consumers gate on
(PRODUCTION_DESCRIPTOR.md; operator s9/s12).

    POSITIVE  a descriptor whose engine answers with its instance id, whose
              store is the live environment and whose credential keys are
              present verifies ok; the daemon writes a restart receipt
    NEGATIVE  a live HOLD refuses; an expired HOLD does not; a wrong engine
              id refuses WRONG_ENGINE; a missing credential key refuses by
              NAME (no value is read)
    CHEAT     a descriptor edited to another engine id is refused by the
              live probe; the credential check reads key names only (a
              file holding the right keys with any values passes -- the
              descriptor is not a secret store)
"""
from __future__ import annotations

import datetime
import json

import pytest

from viv import production as _prod


def _desc(tmp_path, **over):
    d = {"descriptor_version": "prometheus.production.v1", "ruled_by": "test", "ruled_at": "2026-09-17T00:00:00Z",
         "hold": None,
         "engine": {"endpoint": "https://127.0.0.1:1", "engine_instance_id": "eng_test", "schema_floor": 8},
         "store": {"environment": "prometheus-canonical"},
         "consumers": {"vivarium": {"credential_file": str(tmp_path / "cred.json"), "keys": ["sfe_token", "pew_token"]}}}
    d.update(over)
    p = tmp_path / "PRODUCTION.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def test_hold_live_and_expired(tmp_path):
    now = datetime.datetime(2026, 9, 17, 12, 0, tzinfo=datetime.timezone.utc)
    live = _prod.load(_desc(tmp_path, hold={"since": "2026-09-17T11:00:00Z", "expires": "2026-09-17T13:00:00Z", "reason": "x", "by": "op"}))
    assert _prod.hold_live(live, now) is not None
    expired = _prod.load(_desc(tmp_path, hold={"since": "2026-09-17T10:00:00Z", "expires": "2026-09-17T11:00:00Z", "reason": "x", "by": "op"}))
    assert _prod.hold_live(expired, now) is None
    none = _prod.load(_desc(tmp_path))
    assert _prod.hold_live(none, now) is None


def test_credential_presence_reads_key_names_only(tmp_path):
    p = _desc(tmp_path)
    d = _prod.load(p)
    assert _prod.credential_presence(d)["ok"] is False
    (tmp_path / "cred.json").write_text(json.dumps({"sfe_token": "not-a-real-token", "pew_token": "x"}), encoding="utf-8")
    c = _prod.credential_presence(d)
    assert c["ok"] is True and c["present"] == {"sfe_token": True, "pew_token": True}
    assert "not-a-real-token" not in json.dumps(c)                 # values never surface
    (tmp_path / "cred.json").write_text(json.dumps({"sfe_token": "x"}), encoding="utf-8")
    assert _prod.credential_presence(d)["present"]["pew_token"] is False
    # an OPTIONAL key is recorded, never refused (the PEW writer token gates the deliverer, not the consumer)
    d2 = _prod.load(_desc(tmp_path, consumers={"vivarium": {"credential_file": str(tmp_path / "cred.json"),
                                                            "keys": ["sfe_token"], "optional_keys": ["pew_token"]}}))
    c2 = _prod.credential_presence(d2)
    assert c2["ok"] is True and c2["optional_present"] == {"pew_token": False}


def test_probe_refuses_wrong_engine(monkeypatch, tmp_path):
    import io
    import urllib.request

    class R(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: R(json.dumps({"engine_instance_id": "eng_other", "schema_version": 9}).encode()))
    d = _prod.load(_desc(tmp_path))
    v = _prod.probe_engine(d)
    assert v == {"ok": False, "reason": "WRONG_ENGINE", "url": "https://127.0.0.1:1/v2/version", "expected": "eng_test", "observed": "eng_other"}
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: R(json.dumps({"engine_instance_id": "eng_test", "schema_version": 7}).encode()))
    assert _prod.probe_engine(d)["reason"] == "SCHEMA_BELOW_FLOOR"
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: R(json.dumps({"engine_instance_id": "eng_test", "schema_version": 9, "engine_source_hash": "sha256:z"}).encode()))
    ok = _prod.probe_engine(d)
    assert ok["ok"] and ok["source_hash_matches"] is False        # informational, not a refusal


def test_verify_lists_every_reason(monkeypatch, tmp_path):
    import io
    import urllib.request

    class R(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: R(json.dumps({"engine_instance_id": "eng_other", "schema_version": 9}).encode()))
    d = _prod.load(_desc(tmp_path, hold={"since": "2026-09-17T00:00:00Z", "expires": "2999-01-01T00:00:00Z", "reason": "window", "by": "op"}))
    v = _prod.verify(d)
    assert v["ok"] is False
    assert any("HOLD" in r for r in v["refuse"]) and any("WRONG_ENGINE" in r for r in v["refuse"]) \
        and any("credential" in r for r in v["refuse"])
    assert v["store"]["ok"] is True                                  # the throwaway test schema is on the canonical cluster


def test_the_daemon_writes_a_restart_receipt_and_a_test_schema_proceeds(conn, schema, tmp_path, monkeypatch):
    from viv import daemon as _daemon
    from tests.test_loop import FakeRunner
    monkeypatch.setenv("VIV_VAR_DIR", str(tmp_path))
    monkeypatch.setenv("VIV_PRODUCTION_DESCRIPTOR", str(_desc(tmp_path)))
    d = _daemon.Daemon(worker_id="restart-w", schema=schema, runner=FakeRunner(), pew_client=None,
                       log=lambda *_a: None, idle_interval_s=0.01)
    code = d.run(max_ticks=1, install_signals=False)
    assert code == 0
    rec = json.loads((tmp_path / "restart-restart-w.json").read_text(encoding="utf-8"))
    assert rec["schema"] == schema and rec["process"]["worker_id"] == "restart-w"
    assert rec["code"]["base_sha"] and rec["store"]["environment"] == "prometheus-canonical"
    assert rec["credential"]["ok"] is False                         # recorded, not refused (test schema)
    assert rec["engine"]["reason"] == "NOT_PROBED"
    assert "point_release_tables" in rec["migrations"]
