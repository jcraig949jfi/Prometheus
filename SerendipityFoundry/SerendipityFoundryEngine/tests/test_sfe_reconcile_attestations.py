"""A6 reconciler: the separate witness, against a real ledger.

Controls:
  positive   an intent with an Idempotency-Key whose write LANDED (the
             idempotency_keys row exists) reconciles to CONFIRMED_EFFECT
  negative   a keyed intent whose write never landed reconciles to
             CONFIRMED_NO_EFFECT
  unknown    an intent without a key stays UNKNOWN_UNRECONCILABLE; an
             intent younger than the window is not touched at all
  cheat      the journal's own in-memory view is irrelevant: the reconciler
             reads the FILES of a dead process (a fresh Journal) and the
             ledger, nothing else
  durable    verdicts land in reconciled.jsonl, not in the journal files
"""
from __future__ import annotations

import json
import os
import sys
import time

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ENGINE_ROOT)
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))

import reconcile_attestations as ra   # noqa: E402
from sfe import attestation           # noqa: E402
from sfe.runtime import Foundry       # noqa: E402


def test_reconciler_settles_keyed_intents_and_leaves_unkeyed_unknown(tmp_path):
    db = str(tmp_path / "r.db")
    inc = str(tmp_path / "inc")
    f = Foundry(db)
    cid = f.create_client("c")
    s = f.create_session(cid, "s")
    # a write that LANDED under an idempotency key: the row the engine writes
    # in the same transaction as the effect (runtime.py), inserted here the
    # way the engine does it
    with f.store.write() as cx:
        cx.execute("INSERT INTO idempotency_keys(client_id,idem_key,world_id,route,request_hash,response,created_ts) "
                   "VALUES (?,?,?,?,?,?,?)", (cid, "k-landed", None, "POST /v2/worlds", "sha256:h", "{}", time.time()))
    f.close()
    # a dead process's journal: intents only
    j = attestation.Journal(inc)
    old = time.time() - 600
    r_landed = j.intent(route="POST /v2/worlds", idem_key="k-landed")
    r_lost = j.intent(route="POST /v2/worlds", idem_key="k-never")
    r_nokey = j.intent(route="POST /v2/worlds")
    r_young = j.intent(route="POST /v2/worlds", idem_key="k-young")
    # age the first three by rewriting their ts on disk (the tool reads files)
    p = [os.path.join(inc, n) for n in os.listdir(inc) if n.endswith(".jsonl")][0]
    lines = [json.loads(x) for x in open(p, encoding="ascii")]
    for rec in lines:
        if rec["rid"] in (r_landed, r_lost, r_nokey):
            rec["ts"] = old
    with open(p, "w", encoding="ascii") as fh:
        for rec in lines:
            fh.write(json.dumps(rec) + "\n")
    del j                                             # the process is gone
    out = ra.reconcile(inc, db, older_than_s=120.0)
    by = {v["rid"]: v["state"] for v in out}
    assert by[r_landed] == "CONFIRMED_EFFECT"
    assert by[r_lost] == "CONFIRMED_NO_EFFECT"
    assert by[r_nokey] == "UNKNOWN_UNRECONCILABLE"
    assert r_young not in by
    for v in out:
        assert v["witness"].startswith("deploy/reconcile_attestations.py")
    rec = [json.loads(x) for x in open(os.path.join(inc, "reconciled.jsonl"), encoding="ascii")]
    assert {x["rid"] for x in rec} == {r_landed, r_lost, r_nokey}
    # the journal files themselves are untouched by the witness
    assert all(json.loads(x)["kind"] == "intent" for x in open(p, encoding="ascii"))


def test_ambiguous_key_used_by_two_clients_stays_unknown(tmp_path):
    db = str(tmp_path / "r.db")
    inc = str(tmp_path / "inc")
    f = Foundry(db)
    a = f.create_client("a")
    b = f.create_client("b")
    with f.store.write() as cx:
        for c in (a, b):
            cx.execute("INSERT INTO idempotency_keys(client_id,idem_key,world_id,route,request_hash,response,created_ts) "
                       "VALUES (?,?,?,?,?,?,?)", (c, "shared", None, "POST /v2/worlds", "h", "{}", time.time()))
    f.close()
    j = attestation.Journal(inc)
    rid = j.intent(route="POST /v2/worlds", idem_key="shared")
    p = [os.path.join(inc, n) for n in os.listdir(inc) if n.endswith(".jsonl")][0]
    rec = json.loads(open(p, encoding="ascii").read())
    rec["ts"] = time.time() - 600
    open(p, "w", encoding="ascii").write(json.dumps(rec) + "\n")
    out = ra.reconcile(inc, db, older_than_s=120.0)
    assert out[0]["rid"] == rid and out[0]["state"] == "UNKNOWN_UNRECONCILABLE"
