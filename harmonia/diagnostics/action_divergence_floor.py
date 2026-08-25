"""Chance floor for the action-divergence statistic.

Charon's adjudicated headline (`charon/ADJUDICATION_2026-08-25_external_review.md`):

    "of 47,389 states where both actions were recorded, 27,370 (57.8%) have outcomes
     that differ by action. Regret is non-vacuous; the replacement experiment is live
     and well-powered."

That statistic has a floor nobody has published, and the floor is high.

Null: the action is IRRELEVANT and the outcome is an independent draw with the
population's marginal hold rate p. Then two recorded actions at the same state disagree
with probability

    P(differ | action irrelevant) = 2p(1-p)

which is 0.50 at p=0.5 and stays above 0.45 for any p in [0.35, 0.65]. So a divergence
rate near 50% is what a coin produces, not what a decision produces.

This is the same instrument as `shadow_catalog_chance_floor.py`, applied one level up:
there the survivors sat on their chance floor (45.9% observed vs 46.1% null); here the
question is how much of 57.8% is above the floor the same coin implies.

Reading:
  * The excess, not the raw rate, is the effect size. Power should be computed on it.
  * The excess is still highly significant at n=47,389 -- this does NOT kill the regret
    experiment. It rescales it by roughly 7x.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/action_divergence_floor.py
  ... --observed 0.578 --n 47389 --p 0.54

Harmonia C, 2026-08-25.
"""

from __future__ import annotations

import argparse
import math


def floor_for(p):
    return 2.0 * p * (1.0 - p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--observed", type=float, default=0.578,
                    help="observed fraction of states whose outcomes differ by action")
    ap.add_argument("--n", type=int, default=47389,
                    help="number of states with two recorded actions")
    ap.add_argument("--p", type=float, default=None,
                    help="marginal hold rate; if omitted, a sensitivity band is shown")
    a = ap.parse_args()

    print("Action-divergence chance floor")
    print("=" * 72)
    print(f"observed divergence : {a.observed:.4f}  on n={a.n:,} states")
    print()
    print("Null: action irrelevant, outcome ~ Bernoulli(p) independent across the two")
    print("      recorded actions  =>  P(differ) = 2p(1-p)")
    print()
    print(f"{'p':>8}{'floor 2p(1-p)':>16}{'excess':>10}{'z on excess':>14}")
    print("-" * 72)

    ps = [a.p] if a.p is not None else [0.35, 0.40, 0.45, 0.4770, 0.50, 0.5400, 0.60, 0.65]
    se = math.sqrt(0.25 / a.n)          # conservative SE for a proportion at p=0.5
    worst = None
    for p in ps:
        fl = floor_for(p)
        ex = a.observed - fl
        z = ex / se
        print(f"{p:>8.4f}{fl:>16.4f}{ex:>+10.4f}{z:>14.1f}")
        worst = fl if worst is None else max(worst, fl)

    print("-" * 72)
    ex_worst = a.observed - worst
    print(f"Worst-case floor over the band: {worst:.4f}  ->  excess {ex_worst:+.4f}")
    print(f"Ratio headline/excess: {a.observed / ex_worst:.1f}x")
    print()
    print("READING")
    print(f"  The headline reads as {a.observed:.1%}. The decision-relevant quantity is the")
    print(f"  excess over the floor, ~{ex_worst:.1%} -- roughly {a.observed/ex_worst:.0f}x smaller.")
    print("  At this n the excess is still many standard errors from zero, so regret is")
    print("  very likely non-vacuous. What changes is the EFFECT SIZE and therefore the")
    print("  power calculation, which should be run against the excess, not the raw rate.")
    print()
    print("  Note the floor is insensitive to p: 2p(1-p) >= 0.455 for all p in [0.35,0.65],")
    print("  so this conclusion does not depend on knowing c1's marginal rate precisely.")


if __name__ == "__main__":
    main()
