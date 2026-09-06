"""The PEW link, end to end, against the live fossil service.

Double-gated on purpose: it needs VIV_PEW_TOKEN *and* VIV_LIVE_PEW=1. PEW is a
shared, append-only scientific record and a test suite must not write to it
just because it happened to run. The bring-up evidence from the one deliberate
execution is in roles/Vivarium/DELIVERABLE_V0_2026-09-05.md.
"""
from __future__ import annotations

import hashlib
import os
import ssl
import urllib.request
from pathlib import Path

import pytest

from conftest import make_spec
from viv import db as _db
from viv import pew as _pew
from viv import queue as _q
from viv.loop import Vivarium

REPO = Path(__file__).resolve().parent.parent.parent
CACERT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient" / "config" / "m1.crt"
CFG = _db.load_config()


def _reachable(url, **kw) -> bool:
    try:
        urllib.request.urlopen(url, timeout=5, **kw).read()
        return True
    except Exception:                               # noqa: BLE001
        return False


pytestmark = [
    pytest.mark.skipif(os.environ.get("VIV_LIVE_PEW") != "1",
                       reason="set VIV_LIVE_PEW=1 to write to the live PEW"),
    # The credential now lives in the gitignored config.local.json, not only
    # in the environment, so gate on the RESOLVED config -- otherwise this test
    # silently never runs on the very host that is configured for PEW.
    pytest.mark.skipif(not CFG.get("pew_token"),
                       reason="no PEW credential resolvable on this host"),
    pytest.mark.skipif(
        not _reachable(CFG["sfe_base_url"] + "/v2/version",
                       context=ssl.create_default_context(cafile=str(CACERT))),
        reason="SFE not reachable"),
]


def test_the_queue_item_is_traceable_all_the_way_into_pew(conn, schema):
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    spec = make_spec(hypothesis="live pew probe %s" % nonce,
                     kind="evaluate_bitstring",
                     outcome_rule={"field": "solved", "op": "==",
                                   "value": True, "if_true": "SURVIVED",
                                   "if_false": "FALSIFIED",
                                   "if_indeterminate": "INCONCLUSIVE"})
    spec["pew"] = {"encounter_id": "enc_viv_test_" + nonce,
                   "players": ["org_viv_test_" + nonce],
                   "world_binding_id": "vivarium-live-pew-%s" % nonce,
                   "required": True}
    eid = _q.enqueue(conn, created_by="vivarium-selftest",
                     source_reason="live PEW link proof",
                     experiment_spec=spec, schema=schema)
    conn.commit()

    v = Vivarium(worker_id="vivarium-selftest", schema=schema,
                 log=lambda *a: print(*a))
    assert v.cycle(conn) == eid
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed", row["error"]
    assert row["pew_reference"].startswith("pew:encounter/enc_viv_test_")

    client = v.pew()
    # ISOLATION: conftest forces VIV_PEW_NAMESPACE=test, so even a live PEW
    # test cannot deposit a fixture into the scientific record.
    assert client.namespace == "test",         "a test wrote to the %r namespace" % client.namespace
    status, body = client._req(                      # noqa: SLF001
        "GET", "/fossil/encounters/%s" % spec["pew"]["encounter_id"])
    assert status == 200 and body["n_runs"] == 1
    fossil = body["runs"][0]
    summary = row["result_summary"]
    assert fossil["run_id"] == summary["run_id"]
    assert fossil["sfe_entry_hash"] == summary["anchor"]["sfe_entry_hash"]
    assert fossil["outcome"] == summary["outcome"]
    assert fossil["producer"]["spec_hash"] == row["spec_hash"]

    # The auditable check the PEW contract names: the (event_id, entry_hash)
    # pair exists in SFE, and it BINDS this experiment and observation.
    verified = v.runner().c._req("POST", "/v2/audit/verify-anchor", {  # noqa: SLF001
        "world_id": fossil["sfe_world_id"],
        "event_id": fossil["sfe_event_id"],
        "entry_hash": fossil["sfe_entry_hash"],
        "exp_id": row["sfe_experiment_id"], "obs_id": summary["obs_id"]})
    assert verified["valid"] is True
    assert verified["checks"]["binds_exp_id"] is True
    assert verified["checks"]["binds_obs_id"] is True
