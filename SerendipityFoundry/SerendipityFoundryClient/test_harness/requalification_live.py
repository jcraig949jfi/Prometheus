"""Live requalification harness -- proves the GEN-2 repair invariants over REST.

Runs against a RUNNING Engine and demonstrates, on the wire, that the obvious
laundering paths are structurally unavailable. Named for the repair order's RQ
set. Prints a PASS/FAIL table; non-zero exit on any failure.

    python test_harness/requalification_live.py [--base-url URL] [--cafile PATH]

  RQ-A  late prediction AFTER commit is never prospective (409; retro-only)
  RQ-B  worker hindsight: late prediction after work claim cannot be prospective
  RQ-C  stale lease completion after reclaim is rejected
  RQ-D  ...even from the SAME worker_id (the claim ATTEMPT is fenced)
  DFX-2 experiment budget is consumed at COMMIT (register-only is free)
  DFX-3 the exact running release identity is on the wire and in the ledger
  H5    cross-client sharing needs a REGISTERED (unguessable) group capability
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfclient import EngineClient, EngineError

RESULTS = []


def check(name, fn):
    try:
        fn()
        RESULTS.append((name, "PASS", ""))
        print(f"[PASS] {name}")
    except Exception as e:                               # noqa: BLE001
        RESULTS.append((name, "FAIL", str(e)[:200]))
        print(f"[FAIL] {name}: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://192.168.1.202:8811")
    ap.add_argument("--cafile", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "m1.crt"))
    ap.add_argument("--insecure", action="store_true")
    args = ap.parse_args()

    c = EngineClient(args.base_url, cafile=args.cafile, insecure=args.insecure)
    c.register("requal-live")

    def world(budget=None):
        sid = c.create_session("requal")
        w = c.create_world(sid, "w", budget=budget or {
            "experiments": {"limit": 100, "enforcement": "enforceable"}})[
                "world_id"]
        c.start(w)
        return w

    # RQ-A: late prediction after commit
    def rq_a():
        w = world()
        h = c.hypothesis(w, "H")
        e = c.experiment(w, {"p": 1}, hyp_id=h)          # commit=True default
        p_late = c.prediction(w, h, {"x": 1})            # AFTER commit
        try:
            c.observation(w, e["exp_id"], {"r": 1}, "SURVIVED", pred_id=p_late)
            raise AssertionError("late prediction accepted as prospective")
        except EngineError as ex:
            assert ex.status == 409, ex
        # retrospective is allowed but never prospective
        c.observation(w, e["exp_id"], {"r": 1}, "SURVIVED", pred_id=p_late,
                      retrospective=True)
        st = c.status(w)
        assert st["epistemics"]["observations_prospectively_predicted"] == 0
        assert st["epistemics"]["observations_with_retrospective_binding"] >= 1
    check("RQ-A late prediction after commit is never prospective", rq_a)

    # RQ-B: worker hindsight
    def rq_b():
        w = world()
        h = c.hypothesis(w, "H")
        e = c.experiment(w, {"bits": "1"}, hyp_id=h, enqueue=True,
                         kind="evaluate")
        cl = c.claim("wk", world_id=w, lease_s=30)       # worker claims
        c.complete(e["work_id"], "wk", cl["claim_id"],
                   {"score": 1.0})                       # learns the outcome
        p_hind = c.prediction(w, h, {"x": 1})            # hindsight prediction
        try:
            c.observation(w, e["exp_id"], {"score": 1.0}, "SURVIVED",
                          pred_id=p_hind, work_id=e["work_id"])
            raise AssertionError("hindsight prediction laundered")
        except EngineError as ex:
            assert ex.status == 409, ex
    check("RQ-B worker hindsight cannot be laundered into foresight", rq_b)

    # RQ-C / RQ-D: stale lease fencing
    def rq_cd():
        w = world()
        e = c.experiment(w, {"bits": "1"}, enqueue=True, kind="evaluate")
        work_id = e["work_id"]
        a = c.claim("wk", world_id=w, lease_s=0.1)       # attempt A, short lease
        assert a["work_id"] == work_id
        time.sleep(0.4)
        b = c.claim("wk", world_id=w, lease_s=30)        # SAME worker_id, reclaim
        assert b["claim_id"] != a["claim_id"]
        try:
            c.complete(work_id, "wk", a["claim_id"], {"score": 0.0})  # stale
            raise AssertionError("stale-lease completion accepted")
        except EngineError as ex:
            assert ex.status == 409, ex
        c.complete(work_id, "wk", b["claim_id"], {"score": 1.0})      # current ok
    check("RQ-C/D stale lease completion rejected (same worker_id fenced)",
          rq_cd)

    # DFX-2: budget at commit
    def dfx2():
        w = world(budget={"experiments": {"limit": 2, "enforcement":
                                          "enforceable"}})
        c.experiment(w, {"i": 0}, commit=False)          # register only: free
        assert c.resources(w)["consumed"].get("experiments", 0) == 0
        c.experiment(w, {"i": 1})                        # commit -> charge 1
        c.experiment(w, {"i": 2})                        # commit -> charge 2
        try:
            c.experiment(w, {"i": 3})                    # commit -> exhausted
            raise AssertionError("over-budget commit allowed")
        except EngineError as ex:
            assert ex.status == 409 and ex.detail.get("error") == \
                "budget_exhausted", ex
        assert c.resources(w)["consumed"]["experiments"] == 2
    check("DFX-2 experiment budget consumed at commit (register is free)", dfx2)

    # DFX-3: release identity on the wire and in the ledger
    def dfx3():
        v = c.version()
        assert v["engine_source_hash"].startswith("sha256:"), v
        w = world()
        e = c.experiment(w, {"p": 1})
        evs = c.events(w, limit=50)
        committed = [x for x in evs if x["event_type"] == "EXPERIMENT_COMMITTED"]
        assert committed, "no EXPERIMENT_COMMITTED event"
        assert committed[0]["payload"]["engine_source_hash"] == \
            v["engine_source_hash"]
    check("DFX-3 exact release identity on /version and every commit", dfx3)

    # H5: cross-client sharing requires a registered group capability
    def h5():
        w = world()
        art = c.artifact(w, "k", b"A-secret", {"info_kind": "artifact"})[
            "artifact_id"]
        b = EngineClient(args.base_url, cafile=args.cafile,
                         insecure=args.insecure)
        b.register("requal-live-B")
        sidb = b.create_session("b")
        # B fabricates a group id and cannot self-enroll into A's sharing
        dst = b.create_world(sidb, "exfil", sharing_policy="FULLY_SHARED",
                             topology_group="grp_fabricated_deadbeef")[
                                 "world_id"]
        b.start(dst)
        try:
            b.import_artifact(dst, w, art)
            raise AssertionError("cross-client import without a registered "
                                 "group succeeded")
        except EngineError as ex:
            assert ex.status == 403, ex
    check("H5 cross-client sharing needs a registered group (no self-enroll)",
          h5)

    print("\n" + "=" * 64)
    npass = sum(1 for _n, v, _ in RESULTS if v == "PASS")
    for name, v, note in RESULTS:
        print(f"  {v:4s}  {name}" + (f"  -- {note}" if note else ""))
    print(f"  {npass}/{len(RESULTS)} requalification invariants proven live")
    print("=" * 64)
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
