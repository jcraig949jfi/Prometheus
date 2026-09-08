#!/usr/bin/env python
"""DEMONSTRATION: a prospectively declared comparison family, uncontaminated.

Answers one question with live systems rather than with a fake:

    Can two arms of a comparison be DECLARED BEFORE EXECUTION, run through
    the same execution path, and end up in SFE and PEW with the arm label
    recorded as provenance and absent from the sealed science?

Three parts:

  A  a two-arm family, both arms carrying a BYTE-IDENTICAL spec, declared
     before either runs;
  B  a candidate set registered through ARCHAEON's own writer, one selected,
     the rest cancelled -- the class-A conversion, counted by the register
     rather than attested;
  C  both arms executed live, then SFE and PEW read back and searched for the
     arm label.

This is NOT Archaeon's scientific family and runs no science: the execution
kind is `noop_v0`, which takes no parameters and measures nothing. It exercises
the representation, which is what was asked for.

    python demo_family.py            # writes to the production viv schema
"""
from __future__ import annotations

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from viv import db as _db          # noqa: E402
from viv import queue as _q        # noqa: E402
from viv import spec as _spec      # noqa: E402
from viv.loop import Vivarium      # noqa: E402

NONCE = uuid.uuid4().hex[:8]
FAMILY = "demo-family-" + NONCE
ARMS = ("A_random", "C_frozen_S17")


def banner(t):
    print("\n" + "=" * 72 + "\n" + t + "\n" + "=" * 72)


def arm_spec():
    """One spec. Both arms get this object, byte for byte."""
    return {
        "spec_version": 2,
        "world": {"seed_root": 424242},
        "hypothesis": "representation demo: an arm label is not an execution "
                      "input",
        "prediction": None,
        "work": {"kind": "noop_v0", "payload": {}},
        "outcome_rule": {"field": "executed", "op": "==", "value": True,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE"},
        "pew": {"encounter_id": "enc_demo_family_" + NONCE,
                "players": [], "required": True},
    }


def part_a(conn):
    banner("A. A two-arm family, declared BEFORE either arm runs")
    spec = arm_spec()
    ids = {}
    for arm in ARMS:
        ids[arm] = _q.enqueue(
            conn, created_by="vivarium-demo",
            source_reason="tier1 representation demonstration",
            source_evidence={"policy": arm, "note": "provenance, not science"},
            experiment_spec=spec, family_id=FAMILY, arm_id=arm,
            request_key="demo-%s-%s" % (NONCE, arm),
            priority=10 if arm == ARMS[0] else 20)
    conn.commit()

    rows = _q.family(conn, FAMILY)
    hashes = {r["spec_hash"] for r in rows}
    print("family        : %s" % FAMILY)
    print("arms          : %s" % sorted(r["arm_id"] for r in rows))
    print("distinct spec_hash across arms : %d  <- 1 means uncontaminated"
          % len(hashes))
    print("sealed hash   : %s" % hashes.pop())
    print("derived world : %s   (same in both arms, by construction)"
          % _spec.world_name(rows[0]["spec_hash"]))
    blob = json.dumps(rows[0]["experiment_spec"])
    for arm in ARMS:
        assert arm not in blob, "the arm label reached the sealed spec"
    print("arm label inside experiment_spec : NO")
    return ids


def part_b(conn):
    banner("B. A candidate set through ARCHAEON's writer: register, select, "
           "cancel")
    from archaeon import vivqueue as vq

    cands = []
    for i in range(4):
        s = arm_spec()
        s["world"]["seed_root"] = 900000 + i        # genuinely different specs
        s["pew"] = None
        cands.append(vq.make_candidate(
            s, request_key="demo-cand-%s-%d" % (NONCE, i),
            source_evidence={"rank": i}))
    csid = "cs-demo-" + NONCE
    out = vq.submit(conn, candidates=cands, selected_index=1,
                    source_reason="human",          # does not consume quota
                    created_by="vivarium-demo", candidate_set_id=csid)
    print("registered    : %d" % out["registered"])
    print("selected      : %s" % out["selected_experiment_id"])
    print("cancelled     : %d" % len(out["cancelled_experiment_ids"]))
    derived = _q.candidate_set(conn, csid)
    print("DERIVED count : %s" % json.dumps(
        {k: v for k, v in derived.items()
         if k in ("registered", "cancelled", "retained", "executed",
                  "count_source")}, default=str))
    # The unchosen are permanent, not deleted: the only class-A trace of a
    # selection decision anywhere in the architecture.
    for eid in out["cancelled_experiment_ids"]:
        assert _q.get(conn, eid)["status"] == "cancelled"
    print("unchosen candidates still readable : YES (cancelled, not deleted)")
    return csid, out


def part_c(conn, ids):
    banner("C. Execute both arms live, then look for the arm label in SFE")
    v = Vivarium(worker_id="vivarium-demo-%s" % NONCE, log=print)
    ran = []
    for _ in range(6):
        got = v.cycle(conn)
        if got is None:
            break
        ran.append(got)
    print("\nexecuted      : %d rows" % len(ran))

    rows = _q.family(conn, FAMILY)
    runner = v.runner()
    print("")
    for r in sorted(rows, key=lambda x: x["arm_id"]):
        print("arm %-14s status=%-9s sfe=%s"
              % (r["arm_id"], r["status"], r["sfe_experiment_id"]))
        if r["status"] != "completed":
            print("   error: %s" % (r["error"] or "")[:200])
            continue
        s = r["result_summary"]
        env = runner.audit_envelope(s["world_id"], s["exp_id"])
        sealed = env["sealed_spec_hash_in_ledger"]
        assert sealed == r["spec_hash"]
        ledger = json.dumps(env)
        leaked = [a for a in ARMS if a in ledger] + \
                 ([FAMILY] if FAMILY in ledger else [])
        print("   world       : %s (%s)" % (s["world_id"], s["world_name"]))
        print("   sealed hash : %s  == queue: %s" % (sealed[:26],
                                                     sealed == r["spec_hash"]))
        print("   arm/family in the SFE audit envelope : %s"
              % (leaked or "ABSENT"))
        print("   pew         : %s" % r["pew_reference"])
        assert not leaked, "the arm label reached the scientific record"

    done = [r for r in rows if r["status"] == "completed"]
    if len(done) == 2:
        a, b = done
        print("\nBOTH ARMS: identical sealed hash = %s"
              % (a["spec_hash"] == b["spec_hash"]))
        print("           identical world NAME  = %s"
              % (a["result_summary"]["world_name"]
                 == b["result_summary"]["world_name"]))
        print("           DIFFERENT world ids   = %s   (two real executions)"
              % (a["result_summary"]["world_id"]
                 != b["result_summary"]["world_id"]))


def main():
    conn = _db.connect()
    try:
        ids = part_a(conn)
        part_b(conn)
        part_c(conn, ids)
        banner("DONE. family=%s" % FAMILY)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
