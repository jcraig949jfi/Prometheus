"""Two-experimenter isolation test against a LIVE Serendipity Foundry Engine.

Proves that two experimenters (two distinct client tokens) sharing one Engine and
one database CANNOT stomp on each other: their worlds, event ledgers, work
queues, transactions, budgets, and artifacts stay separate under CONCURRENT load.

It drives experimenters A and B in parallel threads (so their writes genuinely
interleave at the server), then asserts, over the REST API:

  1. world listing isolation   -- each sees only its own worlds
  2. cross-access denied (403)  -- A cannot touch B's world knowing its id
  3. ledger separation+integrity-- every world's hash chain verifies; no event
                                   from A ever lands in B's world (and vice versa)
  4. work-queue isolation       -- an UNSCOPED worker drains ONLY its owner's
                                   work; neither steals nor observes the other's
  5. transaction integrity      -- no lost / duplicated / mixed writes: each
                                   world's event count and epistemic counts add up
  6. budget separation          -- A exhausting a world's budget leaves B's intact
  7. artifact confidentiality   -- B cannot import A's artifact by id, and learns
                                   nothing about which artifact ids A holds

    python test_harness/isolation_two_experimenters.py \\
        [--base-url URL] [--cafile PATH] [--insecure] [--worlds N] [--rounds N]

Exit code is non-zero if any isolation property fails.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfclient import EngineClient, EngineError, RemoteWorker

RESULTS = []


def check(name, fn):
    try:
        fn()
        RESULTS.append((name, "PASS", ""))
        print(f"[PASS] {name}")
    except Exception as e:                               # noqa: BLE001
        RESULTS.append((name, "FAIL", str(e)[:300]))
        print(f"[FAIL] {name}: {e}")


def _score(kind, payload):
    bits = str(payload.get("bits", ""))
    s = sum(1 for b in bits if b == "1") / len(bits) if bits else 0.0
    return {"bits": bits, "score": s}


def build(base_url, cafile, insecure, name, n_worlds, n_rounds):
    """One experimenter's whole burst: register, create/start N worlds, and in
    each world register hypotheses + experiments, enqueuing one work item per
    round. Returns (client, [world_ids], enqueued_count). Runs in its own thread
    so A and B hit the Engine concurrently."""
    c = EngineClient(base_url, cafile=cafile, insecure=insecure)
    c.register(f"iso-{name}")
    sid = c.create_session(f"iso-{name}-session")
    worlds, enq = [], 0
    for w in range(n_worlds):
        # identical world NAMES across A and B on purpose: names must not collide.
        # experiments budget is generous (commit now debits it); a separate
        # "compute" resource is used for the budget-separation isolation check.
        world = c.create_world(sid, f"world-{w}", budget={
            "experiments": {"limit": 1000, "enforcement": "enforceable"},
            "compute": {"limit": 3, "enforcement": "enforceable"}})
        wid = world["world_id"]
        c.start(wid)
        worlds.append(wid)
    for _ in range(n_rounds):
        for wid in worlds:
            h = c.hypothesis(wid, f"{name}: bits trend high")
            p = c.prediction(wid, h, {"by": name})
            e = c.experiment(wid, {"bits": "1011", "owner": name},
                             hyp_id=h, pred_id=p, enqueue=True, kind="evaluate")
            enq += 1
            c.observation(wid, e["exp_id"], {"score": 0.75}, "SURVIVED",
                          pred_id=p)
    return c, worlds, enq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://192.168.1.202:8811")
    ap.add_argument("--cafile", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "m1.crt"))
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--worlds", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=4)
    args = ap.parse_args()

    # ---- CONCURRENT phase: A and B build simultaneously -------------------
    out = {}

    def run(tag):
        out[tag] = build(args.base_url, args.cafile, args.insecure, tag,
                         args.worlds, args.rounds)

    ta = threading.Thread(target=run, args=("A",))
    tb = threading.Thread(target=run, args=("B",))
    ta.start(); tb.start(); ta.join(); tb.join()

    (A, wa, enq_a) = out["A"]
    (B, wb, enq_b) = out["B"]
    set_a, set_b = set(wa), set(wb)
    print(f"A: {len(wa)} worlds, {enq_a} work enqueued | "
          f"B: {len(wb)} worlds, {enq_b} work enqueued  (concurrent)")

    # 1. world listing isolation
    def cap_listing():
        la = {w["world_id"] for w in A.list_worlds()}
        lb = {w["world_id"] for w in B.list_worlds()}
        assert la == set_a, f"A sees {la ^ set_a} unexpected"
        assert lb == set_b, f"B sees {lb ^ set_b} unexpected"
        assert la.isdisjoint(lb), "world id overlap between experimenters"
    check("world listing isolation (each sees only its own)", cap_listing)

    # 2. cross-access denied even knowing the id
    def cap_cross():
        victim = wb[0]
        for label, call in (
                ("get", lambda: A.get_world(victim)),
                ("start", lambda: A.start(victim)),
                ("status", lambda: A.status(victim)),
                ("events", lambda: A.events(victim)),
                ("resources", lambda: A.resources(victim)),
                ("hypothesis", lambda: A.hypothesis(victim, "intrude")),
                ("experiment", lambda: A.experiment(victim, {"x": 1}))):
            try:
                call(); raise AssertionError(f"A reached B via {label}")
            except EngineError as e:
                assert e.status == 403, f"{label}: expected 403, got {e.status}"
    check("cross-access denied knowing the id (403 on every route)", cap_cross)

    # 3. ledger separation + integrity after concurrent load
    def cap_ledger():
        for owner, worlds in ((A, wa), (B, wb)):
            for wid in worlds:
                st = owner.status(wid)
                assert st["ledger_integrity_ok"] is True, f"{wid} chain broken"
                evs = owner.events(wid, limit=1000)
                assert evs, f"{wid} has no events"
                # NOT ONE event in this world may belong to another world
                assert all(e["world_id"] == wid for e in evs), \
                    f"{wid} ledger contains foreign world_id"
    check("ledger separation + hash-chain integrity (concurrent)", cap_ledger)

    # 4. work-queue isolation: an UNSCOPED worker drains ONLY its own work
    def cap_workqueue():
        # explicit cross-claim is refused outright
        try:
            A.claim("A-thief", world_id=wb[0]); raise AssertionError(
                "A claimed into B's world")
        except EngineError as e:
            assert e.status == 403
        # unscoped drains: if either stole from the other, a count comes up short
        na = RemoteWorker(A, "A-worker", _score).run(world_id=None)
        nb = RemoteWorker(B, "B-worker", _score).run(world_id=None)
        assert na == enq_a, f"A drained {na}, enqueued {enq_a} (cross-claim?)"
        assert nb == enq_b, f"B drained {nb}, enqueued {enq_b} (cross-claim?)"
    check("work-queue isolation (unscoped worker drains only its own)",
          cap_workqueue)

    # 5. transaction integrity: counts add up, nothing lost or mixed
    def cap_txn():
        for owner, worlds, tag in ((A, wa, "A"), (B, wb, "B")):
            for wid in worlds:
                st = owner.status(wid)
                ep = st["epistemics"]
                # each world saw exactly `rounds` hypotheses/experiments from its
                # OWN experimenter and none from the other
                assert ep["hypotheses_proposed"] == args.rounds, \
                    f"{tag} {wid}: {ep['hypotheses_proposed']} hyps != {args.rounds}"
                assert ep["experiments_created"] == args.rounds, \
                    f"{tag} {wid}: experiments miscount"
                assert ep["observations_recorded"] == args.rounds
    check("transaction integrity (per-world counts add up, no mixed writes)",
          cap_txn)

    # 6. budget separation
    def cap_budget():
        # A drives world wa[0]'s "compute" budget (limit 3) to exhaustion
        for _ in range(3):
            A.consume_budget(wa[0], "compute", 1)
        try:
            A.consume_budget(wa[0], "compute", 1)
            raise AssertionError("A over-budget consume allowed")
        except EngineError as e:
            assert e.status == 409
        # B's same-named world must be completely unaffected
        rb = B.resources(wb[0])
        assert rb["consumed"].get("compute", 0) == 0, \
            "B's budget moved when A consumed"
        assert rb["exhausted"] is False, "B's world exhausted by A's consumption"
    check("budget separation (A's exhaustion does not touch B)", cap_budget)

    # 7. artifact confidentiality across experimenters
    def cap_artifact():
        art = A.artifact(wa[0], "secret", b"A-private-bytes",
                         {"info_kind": "artifact"})["artifact_id"]
        # B, with a FULLY_SHARED destination, still cannot pull A's artifact
        sidb = B.create_session("iso-B-exfil")
        dst = B.create_world(sidb, "exfil", sharing_policy="FULLY_SHARED")[
            "world_id"]
        B.start(dst)
        for label, aid in (("real id", art), ("guessed id", "art_deadbeef")):
            try:
                B.import_artifact(dst, wa[0], aid)
                raise AssertionError(f"B imported A's artifact ({label})")
            except EngineError as e:
                assert e.status == 403, f"{label}: expected 403, got {e.status}"
    check("artifact confidentiality (no cross-experimenter import / id oracle)",
          cap_artifact)

    # ---- summary ----
    print("\n" + "=" * 64)
    npass = sum(1 for _n, v, _ in RESULTS if v == "PASS")
    for name, v, note in RESULTS:
        print(f"  {v:4s}  {name}" + (f"  -- {note}" if note else ""))
    print(f"  {npass}/{len(RESULTS)} isolation properties hold")
    print("=" * 64)
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
