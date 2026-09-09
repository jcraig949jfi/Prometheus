#!/usr/bin/env python3
"""H0-H5 iteration 1: the end-to-end receipt, run against a DEVELOPMENT engine.

    python deploy/h0h5_iteration1_receipt.py --db <dev.db> [--json]

Production is not touched and not restarted. This runs in-process against a
separate ledger with its own engine_instance_id, its own blobs directory and
its own budgets.

WHAT IT DEMONSTRATES, once, with real identifiers:
  a producer-created artifact, resolved by an authorized reader against its
  sealed digest, and charged exactly once.

Every identifier printed is read back out of the ledger. Nothing is asserted
that the engine did not return.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.errors import AccessDenied, ConflictError, ValidationError  # noqa: E402
from sfe.release import ENGINE_SOURCE_HASH                          # noqa: E402
from sfe.runtime import Foundry                                     # noqa: E402
from sfe.store import SCHEMA_VERSION                                # noqa: E402

PAYLOAD = b'{"interface_id":"boolean-inputs-v1","inputs":[[0,0],[0,1],[1,0],[1,1]]}'


def sha(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    f = Foundry(a.db)
    R = {"engine": {"engine_instance_id": f.engine_instance_id(),
                    "engine_source_hash": ENGINE_SOURCE_HASH,
                    "schema_version": SCHEMA_VERSION,
                    "max_artifact_bytes": f.max_artifact_bytes,
                    "db": os.path.abspath(a.db)},
         "steps": [], "checks": []}
    ok = [True]

    def step(name, **kw):
        R["steps"].append({"step": name, **kw})
        print("  %-34s %s" % (name, json.dumps(kw)[:120]))

    def check(name, cond, detail=""):
        R["checks"].append({"check": name, "pass": bool(cond),
                            "detail": str(detail)[:200]})
        if not cond:
            ok[0] = False
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                               "" if cond else "  <-- " + str(detail)))

    print("H0-H5 ITERATION 1 -- END-TO-END RECEIPT (development engine)")
    print("=" * 72)
    print("  engine_instance_id  %s" % R["engine"]["engine_instance_id"])
    print("  engine_source_hash  %s" % ENGINE_SOURCE_HASH)
    print("  schema_version      %s" % SCHEMA_VERSION)
    print()

    # -- the producer -----------------------------------------------------
    producer = f.create_client("h0h5-producer")
    sess = f.create_session(producer, "h0h5")
    world = f.create_world(sess, "h0h5-preflight", budget={
        "retrieval_calls": {"limit": 10, "enforcement": "enforceable"},
        "cpu_s": {"limit": 60, "enforcement": "enforceable"},
        "wall_s": {"limit": None, "enforcement": "unavailable"},
    })["world_id"]
    f.start_world(world, producer)
    step("world created", world_id=world, client_id=producer)

    digest = sha(PAYLOAD)
    art = f.create_artifact(world, "failure_input_set", PAYLOAD,
                            meta={"info_kind": "artifact",
                                  "artifact_type": "failure_input_set",
                                  "schema_version": "1",
                                  "codec": "canonical-json-v1",
                                  "interface_id": "boolean-inputs-v1"},
                            expected_blob_hash=digest, client_id=producer)
    step("artifact produced", artifact_id=art["artifact_id"],
         digest=art["blob_hash"], bytes=len(PAYLOAD))
    check("write-side digest gate held", art["blob_hash"] == digest)

    # -- reserve BEFORE the read -----------------------------------------
    res = f.reserve_budget(world, "retrieval_calls", 1, stage="retrieval",
                           attempt_id="attempt-1", idem_key="preflight-1",
                           client_id=producer)
    step("budget reserved", reservation_id=res["reservation_id"],
         state=res["state"], amount=res["amount"])
    check("reservation debited BEFORE the operation",
          f.budget_status(world)["consumed"]["retrieval_calls"] == 1,
          f.budget_status(world)["consumed"])

    # -- the authorized read ---------------------------------------------
    got = f.get_artifact_content(world, art["artifact_id"],
                                 client_id=producer, expected_digest=digest,
                                 expected_bytes=len(PAYLOAD))
    R["resolution"] = got["resolution"]
    step("artifact resolved", digest_verified=got["resolution"]["digest_verified"],
         authorization=got["resolution"]["authorization"],
         bytes=got["bytes"])
    check("bytes hash to the sealed digest",
          sha(__import__("base64").b64decode(got["content_b64"])) == digest)
    check("resolution receipt names the engine",
          got["resolution"]["engine_instance_id"] == f.engine_instance_id())

    # -- a digest alone authorizes nothing --------------------------------
    outsider = f.create_client("h0h5-outsider")
    denied = False
    try:
        f.get_artifact_content(world, art["artifact_id"], client_id=outsider,
                               expected_digest=digest)
    except AccessDenied:
        denied = True
    check("a correct digest does NOT authorize a foreign reader", denied)

    wrong = False
    try:
        f.get_artifact_content(world, art["artifact_id"], client_id=producer,
                               expected_digest=sha(b"other"))
    except ValidationError:
        wrong = True
    check("a wrong expected digest returns no bytes", wrong)

    # -- settle, once -----------------------------------------------------
    ce = f.record_cost_event(
        world, stage="retrieval", attempt_id="attempt-1",
        reservation_id=res["reservation_id"], source_artifacts=[digest],
        resources=[
            {"resource": "retrieval_calls", "quantity": 1, "unit": "calls",
             "method": "counter", "scope": "attempt"},
            {"resource": "cpu_s", "quantity": 0.004, "unit": "s",
             "method": "clock", "scope": "attempt"},
            {"resource": "wall_s", "quantity": None, "method": "declared",
             "scope": "attempt"},
        ],
        environment={"stratum": "cpu-only", "profile": "alpha",
                     "concurrent_jobs": 1}, client_id=producer)
    R["cost_event"] = {k: ce[k] for k in ("cost_event_id", "event_seq",
                                          "entry_hash", "stage",
                                          "attempt_id", "reservation_id")}
    R["cost_event"]["resources"] = ce["resources"]
    step("cost event sealed", cost_event_id=ce["cost_event_id"],
         event_seq=ce["event_seq"], entry_hash=ce["entry_hash"][:26] + "...")

    twice = False
    try:
        f.record_cost_event(world, stage="retrieval",
                            reservation_id=res["reservation_id"],
                            resources=[{"resource": "retrieval_calls",
                                        "quantity": 1}], client_id=producer)
    except ConflictError:
        twice = True
    check("double billing refused", twice)

    st = f.budget_status(world)
    check("charged exactly once", st["consumed"]["retrieval_calls"] == 1,
          st["consumed"])

    rep = f.cost_report(world, client_id=producer)
    R["cost_report"] = rep
    check("unavailable is not zero",
          "wall_s" not in rep["additive_totals"]
          and rep["unavailable_counts"].get("wall_s") == 1,
          {"totals": rep["additive_totals"],
           "unavailable": rep["unavailable_counts"]})
    check("no reservation left open", rep["open_reservations"] == [])

    back = f.get_cost_event(ce["cost_event_id"], client_id=producer)
    check("the source artifact is inside the seal",
          digest in back.get("artifacts", []), back.get("artifacts"))
    v = f.verify_world(world, client_id=producer)
    check("world ledger still verifies", v["ok"] is True, v)
    R["ledger"] = {"world_id": world, "verified": v["ok"],
                   "head_hash": f.get_world(world, producer)["head_hash"]}

    f.close()
    print()
    print("=" * 72)
    print("  RESULT: %s" % ("PASS" if ok[0] else "FAIL"))
    R["result"] = "PASS" if ok[0] else "FAIL"
    if a.json:
        print(json.dumps(R, indent=2, default=str))
    return 0 if ok[0] else 1


if __name__ == "__main__":
    sys.exit(main())
