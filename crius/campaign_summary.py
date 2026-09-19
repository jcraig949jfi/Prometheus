"""Cross-run summary for a campaign: one row per search run, plus a store-usage census.

Store usage per candidate is read from its CandidateReceipt (ws_cost_total,
blocks_created_total, artifacts_invoked_total, workspace_bytes_final over
the search seeds). "uses store" = any ws cost or any block created; "keeps
state" = workspace bytes at the end of a lifetime > 0 or blocks invoked > 0.

CLI: python -m crius.campaign_summary [--runs-dir crius/runs] [--out crius/runs/CAMPAIGN_SUMMARY.md]
"""

from __future__ import annotations

import argparse
import glob
import json
import os

from . import receipts


def census(run_dir: str) -> dict:
    n = uses = keeps = solvers = 0
    best = None
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            n += 1
            ps = list(r["per_seed"].values())
            ws = sum(p["ws_cost_total"] for p in ps)
            blk = sum(p["blocks_created_total"] for p in ps)
            inv = sum(p["artifacts_invoked_total"] for p in ps)
            wb = sum(p["workspace_bytes_final"] for p in ps)
            succ = sum(p["successes"] for p in ps) / len(ps)
            if ws > 0 or blk > 0:
                uses += 1
            if wb > 0 or inv > 0:
                keeps += 1
            if succ >= 40:
                solvers += 1
            if best is None or r["fitness"] > best["fitness"]:
                best = r
    bps = list(best["per_seed"].values())
    return {
        "candidates": n, "uses_store": uses, "keeps_state": keeps, "solvers_ge40": solvers,
        "best_fitness": best["fitness"], "best_id": best["candidate_id"], "best_iteration": best["iteration"],
        "best_successes": round(sum(p["successes"] for p in bps) / len(bps), 1),
        "best_interactions": round(sum(p["interactions_total"] for p in bps) / len(bps)),
        "best_ws_cost": sum(p["ws_cost_total"] for p in bps), "best_blocks": sum(p["blocks_created_total"] for p in bps),
        "best_invoked": sum(p["artifacts_invoked_total"] for p in bps), "best_len": best["length"],
    }


def qual_row(run_dir: str, suite: str = "heldout_v1") -> dict:
    p = os.path.join(run_dir, "qualify_%s" % suite, "SUMMARY.json")
    if not os.path.exists(p):
        return {}
    rows = receipts.read_json(p)["rows"]
    top = [r for r in rows if r["label"].startswith("top1_")]
    if not top:
        return {}
    m = lambda k: sum(r[k] for r in top) / len(top)
    return {
        "q_effA": round(sum(r["eff"]["ACCUMULATED"] for r in top) / len(top), 3),
        "q_effF": round(sum(r["eff"]["FRESH"] for r in top) / len(top), 3),
        "q_succA": round(sum(r["successes"]["ACCUMULATED"] for r in top) / len(top), 1),
        "q_reuse_gain": round(m("reuse_gain_total"), 1),
        "q_invoked": round(m("artifacts_invoked"), 1),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=os.path.join("crius", "runs"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    lines = []
    P = lines.append
    P("CAMPAIGN SUMMARY (one row per search run; census over every evaluated candidate)")
    P("%-24s %5s %6s %6s %6s %8s %5s %6s %6s %6s %5s %5s | %6s %6s %6s %8s" % (
        "run", "cands", "usesSt", "keepSt", "solv40", "bestFit", "it", "succ", "inter", "wsCost", "blk", "invk",
        "q_effA", "q_effF", "q_succ", "q_reuse"))
    for d in sorted(glob.glob(os.path.join(args.runs_dir, "search_*"))):
        if not os.path.exists(os.path.join(d, "best.json")):
            continue
        c = census(d)
        q = qual_row(d)
        P("%-24s %5d %6d %6d %6d %8.4f %5d %6.1f %6d %6d %5d %5d | %6s %6s %6s %8s" % (
            os.path.basename(d)[:24], c["candidates"], c["uses_store"], c["keeps_state"], c["solvers_ge40"],
            c["best_fitness"], c["best_iteration"], c["best_successes"], c["best_interactions"], c["best_ws_cost"],
            c["best_blocks"], c["best_invoked"], q.get("q_effA", "--"), q.get("q_effF", "--"), q.get("q_succA", "--"), q.get("q_reuse_gain", "--")))
    text = "\n".join(lines)
    print(text)
    out = args.out or os.path.join(args.runs_dir, "CAMPAIGN_SUMMARY.md")
    with open(out, "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
