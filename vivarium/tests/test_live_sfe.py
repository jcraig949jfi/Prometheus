"""End-to-end against the real engine.

Skipped automatically when SFE is unreachable, so the suite still runs on a
host with no engine. When it does run, it proves the thing the fakes cannot:
that the hash the queue sealed is the hash the LEDGER holds, and that the
recorded sfe_experiment_id really resolves to a committed experiment whose
work item completed.
"""
from __future__ import annotations

import os
import ssl
import sys
import urllib.request
from pathlib import Path

import pytest

from conftest import make_spec
from viv import db as _db
from viv import spec as _spec_mod
from viv import queue as _q
from viv.loop import Vivarium

REPO = Path(__file__).resolve().parent.parent.parent
CACERT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient" / "config" / "m1.crt"


def _sfe_reachable(cfg) -> bool:
    try:
        ctx = ssl.create_default_context(cafile=str(CACERT))
        urllib.request.urlopen(cfg["sfe_base_url"] + "/v2/version",
                               context=ctx, timeout=5).read()
        return True
    except Exception:                               # noqa: BLE001
        return False


CFG = _db.load_config()
pytestmark = pytest.mark.skipif(
    not _sfe_reachable(CFG), reason="SFE engine not reachable from this host")


def test_a_real_experiment_runs_once_and_is_traceable(conn, schema):
    spec = make_spec(
        bits="0" * 24, hypothesis="live probe %s" % os.getpid(),
        kind="evaluate_bitstring",
        outcome_rule={"field": "solved", "op": "==", "value": True,
                      "if_true": "SURVIVED", "if_false": "FALSIFIED",
                      "if_indeterminate": "INCONCLUSIVE"})
    eid = _q.enqueue(conn, created_by="vivarium-selftest",
                     source_reason="live end-to-end proof",
                     source_evidence={"suite": "test_live_sfe"},
                     experiment_spec=spec, schema=schema)
    conn.commit()
    sealed = _q.get(conn, eid, schema=schema)["spec_hash"]

    v = Vivarium(worker_id="vivarium-selftest", schema=schema,
                 pew_client=None, log=lambda *a: print(*a))
    assert v.cycle(conn) == eid

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed", row["error"]
    assert row["sfe_experiment_id"].startswith("exp_")

    s = row["result_summary"]
    assert s["outcome"] in ("SURVIVED", "FALSIFIED")
    assert s["run_id"] == "%s:%s" % (s["exp_id"], s["work_id"])
    assert s["anchor"]["resolved"] is True
    assert s["anchor"]["sfe_entry_hash"].startswith("sha256:")
    assert s["anchor"]["event_type"] == "OBSERVATION_RECORDED"
    assert s["world_name"] == _spec_mod.world_name(sealed)
    assert s["audit_envelope"]["work_status"] == "COMPLETED"

    # The ledger, read back independently, holds the hash the queue sealed.
    env = v.runner().audit_envelope(s["world_id"], row["sfe_experiment_id"])
    assert env["sealed_spec_hash_in_ledger"] == sealed
    assert env["spec_hash_recomputed"] == sealed

    # And the anchor is a REAL event that BINDS this experiment, not merely a
    # sha256-shaped string: the engine's credential-free verifier says so.
    verified = v.runner().c._req("POST", "/v2/audit/verify-anchor", {
        "world_id": s["world_id"], "event_id": s["anchor"]["sfe_event_id"],
        "entry_hash": s["anchor"]["sfe_entry_hash"],
        "exp_id": row["sfe_experiment_id"], "obs_id": s["obs_id"]})
    assert verified["valid"] is True, verified

    assert v.cycle(conn) is None                 # never runs a second time
