"""e9_score.py -- rebuild of the missing E9 scoring harness (charter Task 1).

E9 (2026-08-25) killed 0.833 as a capability number: the known organism, scored on
42 tasks authored BLIND by Charon in Apollo's own seven categories, returned
mix-adjusted 0.0667 vs 0.6000 at home, with 40/42 abstentions and zero guesses.
The RESULT.json was committed; the SCRIPT that produced it was not. So the headline
falsification of the entire Apollo corpus was, until now, not reproducible from source.

This harness reconstructs it from the SAME evaluation path every historical Apollo
number used (`blackboard_evolve.run_pipeline`, `selected_answer == correct`, the
`KNOWN_0833` organism recorded in `replay_harness.py`). It re-derives the home
category mix from the home battery rather than hardcoding it, and asserts exact
reproduction of the two recorded numbers:

    raw_aggregate = 0.0476   (2/42; transitivity is the only non-zero category)
    mix_adjusted  = 0.0667   (home-weighted: only transitivity's 0.333 survives)

A discrepancy is a finding, not a nuisance -- the script exits non-zero and says so.

Usage:
    python apollo/scripts/e9_score.py            # score + reproduction check
    python apollo/scripts/e9_score.py --write     # also (re)write E9_RESULT.json
Exit: 0 reproduces within tolerance | 1 drift (investigate before trusting E9)
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
REPO = HERE.parents[1]
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

import blackboard_evolve as be  # noqa: E402
from blackboard import BlackboardState, run_pipeline  # noqa: E402

# The known 0.833 organism, verbatim from replay_harness.py (single source of truth).
from replay_harness import KNOWN_0833  # noqa: E402

CHARON = REPO / "roles" / "Charon" / "apollo_e9" / "charon_battery_E9.json"
HOME = SRC.parent / "data" / "clean_canary_v01.json"
RESULT = HERE.parent / "cycles" / "campaign_20260825" / "E9_RESULT.json"

# recorded endpoints (E9_FINDINGS.md / E9_RESULT.json), the reproduction targets
TARGET_RAW = 0.0476
TARGET_MIX = 0.0667
TOL = 0.0005  # the recorded numbers are rounded to 4 dp; this is rounding, not slack


def _ops(pipeline):
    return [be.REGISTRY[n][0] for n in pipeline if n in be.REGISTRY]


def _home_category_weights():
    """Home mix, derived not assumed: category size / total, from the home canary."""
    home = json.loads(HOME.read_text(encoding="utf-8"))["tasks"]
    counts = collections.Counter(t["category"] for t in home)
    total = sum(counts.values())
    return {c: n / total for c, n in counts.items()}, counts, total


def _home_per_category_acc(ops):
    """What the known organism scores per category AT HOME (for the delta column)."""
    home = json.loads(HOME.read_text(encoding="utf-8"))["tasks"]
    by = collections.defaultdict(list)
    for t in home:
        by[t["category"]].append(t)
    out = {}
    for c, tasks in by.items():
        n = 0
        for t in tasks:
            s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
            try:
                if run_pipeline(ops, s).selected_answer == t["correct"]:
                    n += 1
            except Exception:
                pass
        out[c] = n / len(tasks)
    return out


CHARON_META = REPO / "roles" / "Charon" / "apollo_e9" / "charon_battery_E9_metadata.json"


def _charon_floors():
    """Read Charon's AUTHORITATIVE trivial floors from its own metadata. These are
    tie-aware EXPECTED scores (a pick-longest with random tie-break scores 1/n_tied
    when the correct answer is among the longest), not a naive first-match heuristic.
    Recomputing them here with a different estimator would manufacture a false
    discrepancy and overwrite another seat's instrument calibration -- so we cite the
    source, we do not re-derive it."""
    m = json.loads(CHARON_META.read_text(encoding="utf-8"))["summary"]
    return {"longest": m["expected_pick_longest_score"],
            "shortest": m["expected_pick_shortest_score"],
            "chance": m["chance_floor"]}


def score(pipeline=KNOWN_0833):
    ops = _ops(pipeline)
    tasks = json.loads(CHARON.read_text(encoding="utf-8"))
    weights, _, _ = _home_category_weights()
    home_acc = _home_per_category_acc(ops)

    by = collections.defaultdict(lambda: {"correct": 0, "n": 0,
                                          "abstained": 0, "guessed": 0})
    total_correct = 0
    for t in tasks:
        c = t["category"]
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            sel = run_pipeline(ops, s).selected_answer
        except Exception:
            sel = None
        rec = by[c]
        rec["n"] += 1
        if sel == t["correct"]:
            rec["correct"] += 1
            total_correct += 1
        elif sel in (None, ""):
            # The organism's abstain sentinel is the EMPTY STRING, not None: every
            # guarded scorer skips, so selected_answer is never written away from its
            # "" default. Detecting only None would misreport 40 abstentions as guesses
            # and destroy the failure shape E9 exists to record (total non-recognition,
            # not wrong answers). This distinction was verified against source 2026-09-01.
            rec["abstained"] += 1
        else:
            rec["guessed"] += 1

    per_category = {}
    mix = 0.0
    for c, rec in by.items():
        acc = rec["correct"] / rec["n"]
        per_category[c] = {
            "correct": rec["correct"], "n": rec["n"], "acc": round(acc, 4),
            "home_acc": round(home_acc.get(c, 0.0), 4),
            "abstained": rec["abstained"], "guessed": rec["guessed"],
        }
        mix += weights.get(c, 0.0) * acc

    raw = total_correct / len(tasks)
    home_mix = sum(weights[c] * home_acc.get(c, 0.0) for c in weights)
    return {
        "experiment": "E9",
        "battery": "roles/Charon/apollo_e9/charon_battery_E9.json",
        "n": len(tasks),
        "organism": "KNOWN_0833",
        "per_category": per_category,
        "raw_aggregate": round(raw, 4),
        "mix_adjusted": round(mix, 4),
        "home_canary": round(home_mix, 4),
        "primary_verdict": "FAIL" if (0.6 - mix) > 0.15 else "PASS",
        "coprimary_verdict": "FAIL" if any(
            per_category[c]["home_acc"] >= 0.75 and per_category[c]["acc"] < 0.75
            for c in per_category) else "PASS",
        "charon_trivial_floor": _charon_floors(),
        "home_trivial_floor": 0.342,
        "home_trivial_floor_note": "recorded prior (2026-08-23 benchmark_attack); not "
                                   "recomputed here -- a different length estimator gives "
                                   "0.42, which is the estimator, not a drift in the data",
        "scored": "once, no tuning",
        "date": "2026-08-25",
        "regenerated_by": "apollo/scripts/e9_score.py (2026-09-01)",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="(re)write E9_RESULT.json from this run")
    args = ap.parse_args()

    r = score()
    raw, mix = r["raw_aggregate"], r["mix_adjusted"]
    print(f"raw_aggregate = {raw:.4f}   (target {TARGET_RAW})")
    print(f"mix_adjusted  = {mix:.4f}   (target {TARGET_MIX})")
    print(f"home_canary   = {r['home_canary']:.4f}   (target 0.6000)")
    for c, v in sorted(r["per_category"].items()):
        print(f"  {c:24s} {v['correct']}/{v['n']} = {v['acc']:.3f}"
              f"  home {v['home_acc']:.3f}  abst {v['abstained']} guess {v['guessed']}")

    ok = (abs(raw - TARGET_RAW) <= TOL and abs(mix - TARGET_MIX) <= TOL
          and abs(r["home_canary"] - 0.6) <= TOL)
    if args.write:
        RESULT.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {RESULT}")

    if ok:
        print("REPRODUCED: E9 is reproducible from source.")
        return 0
    print("DRIFT: E9 numbers do not reproduce. This is a finding -- investigate "
          "before citing E9 as reproducible.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
