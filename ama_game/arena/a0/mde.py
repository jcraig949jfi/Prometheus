#!/usr/bin/env python3
"""Simulation-based minimum detectable effect for the A0-vs-D comparison.

The primary outcome is expected verifier cost to a correct disposition, with an
incorrect disposition charged the full budget cap. That distribution is not
remotely normal: it is a small cluster of cheap correct answers plus a point
mass sitting exactly on the cap. Normal-theory power formulas do not apply to
it, and using one would produce a confident MDE that is simply wrong.

So the MDE is estimated by resampling the observed pilot distribution:

  1. take the pilot's per-claim (correct, verifier_calls) outcomes as the A arm;
  2. construct a hypothetical D arm by applying two levers, each of which
     preserves the observed structure rather than replacing it:
       g - the fraction of A's ERRORS that D converts to correct answers, each
           given a cost resampled from A's own observed correct-cost pool;
       f - the fraction by which D reduces verifier cost on answers A already
           got right;
  3. draw unpaired samples of size n from each arm, as the prereg's disjoint
     matched sets require;
  4. test the difference with a permutation test, which assumes nothing about
     the shape;
  5. repeat, and report the rejection rate as power.

Because the cap is large relative to a typical correct answer's cost, g moves
EVC far more than f does. That is a property of the metric as preregistered,
not a modelling choice, and it is worth seeing explicitly before A0 is read.

  python mde.py --pilot MDE_PILOT --n 30
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def arm_from_pilot(rows, cap):
    correct_costs = [r["verifier_calls"] for r in rows if r["correct"]]
    n_err = sum(1 for r in rows if not r["correct"])
    return {"correct_costs": correct_costs or [1], "n_correct": len(correct_costs),
            "n_error": n_err, "cap": cap, "n": len(rows)}


def draw(arm, rng, g=0.0, f=0.0, size=None):
    """One resampled cost vector under improvement levers (g, f)."""
    size = size or arm["n"]
    p_err = arm["n_error"] / arm["n"]
    out = []
    for _ in range(size):
        if rng.random() < p_err:
            if rng.random() < g:                    # D rescues this error
                out.append(max(1, round(rng.choice(arm["correct_costs"]) * (1 - f))))
            else:
                out.append(arm["cap"])
        else:
            out.append(max(1, round(rng.choice(arm["correct_costs"]) * (1 - f))))
    return out


def permutation_p(a, b, rng, draws=600):
    obs = abs(statistics.mean(a) - statistics.mean(b))
    pool = list(a) + list(b)
    na = len(a)
    hits = 0
    for _ in range(draws):
        rng.shuffle(pool)
        if abs(statistics.mean(pool[:na]) - statistics.mean(pool[na:])) >= obs:
            hits += 1
    return (hits + 1) / (draws + 1)


def power_at(arm, n, g, f, rng, reps=400, alpha=0.05):
    rej, deltas = 0, []
    for _ in range(reps):
        a = draw(arm, rng, 0.0, 0.0, n)
        d = draw(arm, rng, g, f, n)
        deltas.append(statistics.mean(a) - statistics.mean(d))
        if permutation_p(a, d, rng) < alpha:
            rej += 1
    return rej / reps, statistics.mean(deltas)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", required=True)
    p.add_argument("--n", type=int, action="append", default=[])
    p.add_argument("--reps", type=int, default=400)
    args = p.parse_args()

    res = json.loads((HERE / args.pilot / "RESULT.json").read_text(encoding="utf-8"))
    cap = res["budget_cap"]
    arm = arm_from_pilot(res["rows"], cap)
    ns = args.n or [30, 60, 120]
    rng = random.Random(20260825)

    L = []
    L.append("A0-vs-D MINIMUM DETECTABLE EFFECT (simulation, not normal theory)")
    L.append("=" * 68)
    L.append(f"pilot            : {args.pilot}, n = {arm['n']}")
    L.append(f"observed EVC     : {res['evc']:.2f}   accuracy {res['accuracy']:.0%}")
    L.append(f"budget cap       : {cap}")
    L.append(f"correct-cost pool: {sorted(arm['correct_costs'])}")
    L.append(f"error mass       : {arm['n_error']}/{arm['n']} "
             f"= {arm['n_error']/arm['n']:.0%} of items sit on the cap")
    L.append("")
    L.append("Power to detect a difference in EVC between two disjoint arms,")
    L.append("permutation test at alpha = 0.05, unpaired as preregistered.")
    L.append("")
    L.append(f"  {'n/arm':>6s} {'g (errors D fixes)':>20s} {'f (cost cut)':>13s} "
             f"{'dEVC':>8s} {'power':>7s}")

    grid = [(0.25, 0.0), (0.50, 0.0), (0.75, 0.0), (1.0, 0.0),
            (0.0, 0.30), (0.0, 0.60), (0.25, 0.50), (0.50, 0.50)]
    table = []
    for n in ns:
        for g, f in grid:
            pw, dv = power_at(arm, n, g, f, rng, reps=args.reps)
            table.append({"n": n, "g": g, "f": f, "delta_evc": dv, "power": pw})
            L.append(f"  {n:>6d} {g:>20.2f} {f:>13.2f} {dv:>8.2f} {pw:>7.0%}")
        L.append("")

    L.append("READING THIS")
    L.append("  g moves EVC far more than f, because a wrong answer is charged the")
    L.append("  full cap while a right one typically costs a few calls. Under this")
    L.append("  metric, D earns its keep mainly by being RIGHT more often, not by")
    L.append("  being cheaper. That is what the prereg chose, and it is worth")
    L.append("  knowing before the result is read rather than after.")
    L.append("")
    for n in ns:
        rows = [t for t in table if t["n"] == n and t["power"] >= 0.80]
        if rows:
            best = min(rows, key=lambda t: abs(t["delta_evc"]))
            L.append(f"  n = {n:<4d} MDE at 80% power: dEVC ~ {abs(best['delta_evc']):.1f} "
                     f"verifier calls (e.g. g={best['g']}, f={best['f']})")
        else:
            L.append(f"  n = {n:<4d} no tested effect reaches 80% power. At this n the")
            L.append(f"           comparison is UNPOWERED for the effects simulated.")

    text = "\n".join(L)
    print(text)
    out = HERE / args.pilot / "MDE.json"
    out.write_text(json.dumps({
        "pilot": args.pilot, "cap": cap, "arm": arm,
        "observed_evc": res["evc"], "observed_accuracy": res["accuracy"],
        "grid": table,
    }, indent=2) + "\n", encoding="utf-8")
    (HERE / args.pilot / "MDE.txt").write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
