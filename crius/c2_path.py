"""Path evidence for a search run (CRIUS_C2_TERMINAL_PREREG s V): did incomplete machinery get a foothold?

From candidates.jsonl (every evaluated candidate with ancestry, store trace,
per-stream metrics), iterations.jsonl and takeovers.jsonl:
  - PARTS-operation frequencies per iteration window: candidates executing
    PREC_END (recorder), PINVOKE (invoker), PSIM/PMATCH (planner), and the
    conjunctions recorder+invoker, recorder+invoker+planner
  - time to first COMPLETE mechanism: first candidate whose lifetime shows
    PREC_END > 0 and PINVOKE > 0 and a chain task solved inside an invoked
    block (proxy: artifacts_invoked > 0 with blocks created by itself and
    solved > seed on its stream) -- the strict version is read from the
    qualification receipts (success_in_block on depth >= 2)
  - survival of partial structures: for each typed op, how many consecutive
    iterations at least one ELITE member (top mu of the iteration by
    fitness) executed it, and the longest such run
  - selectable foothold: fitness of children carrying a typed op versus
    their parent (delta), split by op; the fraction of children that
    improved on their parent while carrying the op vs. without it
  - recombination events producing functional descendants: splice children
    whose fitness exceeds both the parent's and the donor's (donor known
    from the modification string)

CLI: python -m crius.c2_path --run RUN_ID    (writes crius/runs/RUN_ID/PATH.md)
"""

from __future__ import annotations

import argparse
import json
import os

from . import receipts

OPS = {"recorder": ("PREC_END",), "invoker": ("PINVOKE",), "planner": ("PSIM", "PMATCH")}


def _trace(rec):
    t = {}
    for p in rec["per_seed"].values():
        for k, v in p.get("store_trace", {}).items():
            t[k] = t.get(k, 0) + v
    return t


def _has(t, names):
    return any(t.get(n, 0) > 0 for n in names)


def analyse(run_dir: str, mu: int = 8) -> str:
    cands = {}
    by_it = {}
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            cands[r["candidate_id"]] = r
            by_it.setdefault(r["iteration"], []).append(r)
    best = receipts.read_json(os.path.join(run_dir, "best.json"))
    its = sorted(by_it)
    L = []
    P = L.append
    P("PATH EVIDENCE run=%s arm=%s" % (best["run_id"], best["arm"]))
    # ---- frequencies per window of 50 iterations
    P("PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)")
    P("  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)")
    seed_solved = None
    for w0 in range(0, max(its) + 1, 50):
        rows = [r for it in its if w0 <= it < w0 + 50 for r in by_it[it]]
        if not rows:
            continue
        c = {"rec": 0, "inv": 0, "plan": 0, "ri": 0, "rip": 0, "own": 0}
        for r in rows:
            t = _trace(r)
            rec, inv, plan = _has(t, OPS["recorder"]), _has(t, OPS["invoker"]), _has(t, OPS["planner"])
            c["rec"] += rec
            c["inv"] += inv
            c["plan"] += plan
            c["ri"] += rec and inv
            c["rip"] += rec and inv and plan
            ps = list(r["per_seed"].values())
            if rec and inv and sum(p["artifacts_invoked_total"] for p in ps) > 0:
                c["own"] += 1
        P("  %4d-%3d %4d %5d %5d %5d %8d %13d %8d" % (w0, min(w0 + 49, max(its)), len(rows), c["rec"], c["inv"], c["plan"], c["ri"], c["rip"], c["own"]))
    # ---- survival in the elite
    P("Survival of typed ops in the ELITE (top %d by fitness per iteration): iterations present / longest consecutive run" % mu)
    for name, ops in OPS.items():
        present = []
        for it in its:
            elite = sorted(by_it[it], key=lambda r: -r["fitness"])[:mu]
            present.append(any(_has(_trace(r), ops) for r in elite))
        longest = cur = 0
        for p in present:
            cur = cur + 1 if p else 0
            longest = max(longest, cur)
        P("  %-9s present in %d/%d iterations; longest consecutive run %d" % (name, sum(present), len(present), longest))
    # ---- selectable foothold: child vs parent delta by op carried
    P("Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not")
    P("  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)")
    for name, ops in OPS.items():
        with_op, without = [], []
        for r in cands.values():
            par = cands.get(r["parent_id"]) if r["parent_id"] else None
            if par is None:
                continue
            d = r["fitness"] - par["fitness"]
            (with_op if _has(_trace(r), ops) and not _has(_trace(par), ops) else without).append(d)
        if with_op:
            P("  %-9s newly carried by %5d children: mean delta %+.3f, improved %4d (%.1f pct) | others: mean %+.3f, improved %.1f pct" % (
                name, len(with_op), sum(with_op) / len(with_op), sum(1 for d in with_op if d > 0), 100.0 * sum(1 for d in with_op if d > 0) / len(with_op),
                sum(without) / max(1, len(without)), 100.0 * sum(1 for d in without if d > 0) / max(1, len(without))))
        else:
            P("  %-9s never newly carried" % name)
    # ---- first complete mechanism (proxy), strict check deferred to qualification receipts
    first = None
    for it in its:
        for r in by_it[it]:
            t = _trace(r)
            ps = list(r["per_seed"].values())
            if _has(t, OPS["recorder"]) and _has(t, OPS["invoker"]) and sum(p["artifacts_invoked_total"] for p in ps) > 0 \
                    and sum(p["successes"] for p in ps) / len(ps) > 22:
                first = (it, r["candidate_id"], round(sum(p["successes"] for p in ps) / len(ps), 1), r["fitness"])
                break
        if first:
            break
    P("First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): %s" % (first,))
    # ---- recombination events
    n_spl = n_func = 0
    for r in cands.values():
        if "splice@" in r["modification"] and ":" in r["modification"]:
            n_spl += 1
            donor_id = r["modification"].rsplit(":", 1)[-1]
            par = cands.get(r["parent_id"])
            donor = cands.get(donor_id)
            if par and (donor is None or donor_id.startswith("PART")) and r["fitness"] > par["fitness"]:
                n_func += 1
            elif par and donor and r["fitness"] > max(par["fitness"], donor["fitness"]):
                n_func += 1
    P("Recombination: %d splice children; %d exceeded both parent and donor (or parent, when the donor is a PART)" % (n_spl, n_func))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    run_dir = args.run if os.path.isdir(args.run) else os.path.join("crius", "runs", args.run)
    text = analyse(run_dir)
    with open(os.path.join(run_dir, "PATH.md"), "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
