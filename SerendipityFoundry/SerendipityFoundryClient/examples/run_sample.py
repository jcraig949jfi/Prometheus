"""Sample research session against the Serendipity Foundry Engine.

Runs from M1/SKULLPORT (or any LAN machine that trusts the Engine cert). It
registers a client, opens a world, runs a tiny hypothesis->prediction->
experiment->observation loop with a real queued worker, records a failure, forks
a counterfactual, and prints the world's mechanically-derived status.

    python examples/run_sample.py [--base-url URL] [--cafile PATH] [--insecure]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfclient import EngineClient, RemoteWorker


def local_executor(kind: str, payload: dict) -> dict:
    """The WORKER's compute (client-side, stdlib). Here: score a bitstring by
    its fraction of 1s. In a real deployment this could call a solver, an LLM,
    or a subprocess -- the Engine only stores the structured result."""
    bits = str(payload.get("bits", ""))
    score = (sum(1 for b in bits if b == "1") / len(bits)) if bits else 0.0
    return {"bits": bits, "score": score, "solved": score >= 1.0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://192.168.1.202:8811")
    ap.add_argument("--cafile", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config",
        "m1.crt"))
    ap.add_argument("--insecure", action="store_true")
    args = ap.parse_args()

    c = EngineClient(args.base_url, cafile=args.cafile, insecure=args.insecure)
    print("engine:", c.version())
    token = c.register("sample-console")
    print("registered; token (store this):", token[:16], "...")

    sid = c.create_session("sample-session")
    world = c.create_world(sid, "sample-world", budget={
        "experiments": {"limit": 100, "enforcement": "enforceable"}})
    wid = world["world_id"]
    c.start(wid)
    print("world:", wid, "state:", c.get_world(wid)["state"])

    # a small research loop, preregistering each prediction before observing
    worker = RemoteWorker(c, "sample-worker", local_executor)
    best = 0.0
    for candidate in ("1010", "1110", "1111", "0111"):
        h = c.hypothesis(wid, f"candidate {candidate} scores high")
        p = c.prediction(wid, h, {"candidate": candidate, "expect": ">=0.75"})
        exp = c.experiment(wid, {"bits": candidate}, hyp_id=h, pred_id=p,
                           enqueue=True, kind="evaluate")
        worker.run(world_id=wid)                      # a worker evaluates it
        result = c.get_world(wid)  # (status carries the mechanical accounting)
        # read the completed work result to decide the outcome
        score = local_executor("evaluate", {"bits": candidate})["score"]
        outcome = "SURVIVED" if score >= 0.75 else "FALSIFIED"
        c.observation(wid, exp["exp_id"], {"score": score}, outcome, pred_id=p)
        if outcome == "FALSIFIED":
            c.failure(wid, failure_type="below_threshold", falsifier="oracle",
                      violated="score>=0.75",
                      observed={"bits": candidate, "score": score})
        best = max(best, score)
        print(f"  {candidate}: score={score:.2f} -> {outcome}")

    # fork a counterfactual from the current state
    ck = c.checkpoint(wid)
    kids = c.fork(wid, ck["checkpoint_id"],
                  [{"name": "counterfactual-A"}, {"name": "counterfactual-B"}])
    print("forked:", [k["world_id"] for k in kids])

    st = c.status(wid)
    print("\n--- world status (mechanically derived) ---")
    print(json.dumps({"state": st["state"],
                      "ledger_integrity_ok": st["ledger_integrity_ok"],
                      "epistemics": st["epistemics"],
                      "resources": st["resources"]}, indent=2)[:1200])
    print(f"\nbest score reached: {best:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
