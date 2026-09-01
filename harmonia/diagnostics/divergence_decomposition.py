"""Exact decomposition of the action-divergence statistic -- and the correction of my own
2026-08-25 filing, which had the bound pointing the wrong way.

WHAT I FILED ON 2026-08-25 (pivot/NOTE_2026-08-25_action_divergence_chance_floor.md):

    "Null: the action is irrelevant and the outcome is an independent draw at the
     population's marginal hold rate p.  Then P(differ | action irrelevant) = 2p(1-p),
     which is 0.50 at p=0.5.  Observed 0.578 => excess +0.078 => THE EXCESS IS THE
     EFFECT SIZE.  Regret is very likely non-vacuous; the experiment should run."

Two things are wrong with that, and they are independent of each other.

(1) 2p(1-p) IS NOT A FLOOR.  It is a CEILING on the action-irrelevant divergence.
    If the action is irrelevant and each parent state s has its own success probability
    q_s, divergence is E[2 q_s (1-q_s)], and by Jensen (concavity of q -> 2q(1-q)):

        E[2 q_s (1-q_s)]  <=  2 E[q_s] (1 - E[q_s])  =  2p(1-p)

    State heterogeneity pushes divergence BELOW 2p(1-p), always.  So an observation
    below it is exactly what an irrelevant action produces.  Calling it a floor and
    reading the excess as effect size inverts the inference.

(2) WHAT D CAN AND CANNOT SUPPORT -- stated precisely, because the obvious
    overcorrection is also wrong.  D IS a valid one-sided test: exceeding 2p(1-p)
    implies E[d_s^2] > Var(q_s) >= 0, so the actions do differ.  It is conservative --
    it makes the action effect clear the state heterogeneity -- and it is silent in the
    other direction: falling below licenses nothing.  Three further limits:

      * D is symmetric under swapping the action labels (test 3), so it can bear on
        WHETHER the actions differ but never on WHICH is better, and never on whether
        the difference is predictable from the state.  Non-vacuity is not navigability.
      * D is MAXIMISED by a fair coin at every state (test 4) -- the least navigable
        world scores highest.  A large D is not good news.
      * the magnitude of the excess is E[d^2] - Var(q), a difference of two unknowns,
        NOT the effect size.  Power keyed to it is keyed to the wrong quantity.

THE EXACT IDENTITY (test 1 verifies it to Monte-Carlo error).  Write the per-state
success probabilities as alpha_s = q_s + d_s (action a) and beta_s = q_s - d_s (action
b), with Y_a and Y_b conditionally independent given s.  Then p = E[q_s] and

        D  =  2 p (1-p)  -  2 Var(q_s)  +  2 E[d_s^2]
    =>  D - 2 p (1-p)  =  2 ( E[d_s^2] - Var(q_s) )

The excess over 2p(1-p) is a DIFFERENCE of the action-effect term and the
state-heterogeneity term.  Neither is identified without the other.  My filing set
Var(q_s) = 0 by assumption and read the whole excess as action effect.

WHAT THIS DOES TO THE TWO PUBLISHED NUMBERS:

  * the 47,389-state sample (D = 0.5776) needs E[d^2] - Var(q) = +0.0405, i.e. an RMS
    action effect of at least 0.20 -- a very large claimed effect;
  * Charon's exact corpus scan (D = 0.4114 over 932,852 both-action parents) needs
    E[d^2] - Var(q) = -0.0426, which is what an irrelevant action over heterogeneous
    states produces and places NO lower bound on E[d^2] above zero.

So the corpus-scale statistic gives no evidence that the action matters, and the
sample-scale statistic was above the ceiling -- the direction that a selection effect
in which parents get both actions logged would manufacture.  That is the exchangeability
worry from my own section 3, now the load-bearing one rather than a footnote.

WHAT WOULD IDENTIFY IT.  Var(q_s) must be estimated separately, which needs repeated
observations at the SAME (state, action).  Charon measured that those exist for (P, A):
1,251,927 groups with >= 2 rows, 38.55% carrying multiple outcomes.  Those repeats vary
the replacement object, so they estimate replacement-induced variance rather than pure
noise -- which is the same UNDER-SPECIFIED ACTION finding from a second direction.

  PYTHONPATH=. python harmonia/diagnostics/divergence_decomposition.py --test
  PYTHONPATH=. python harmonia/diagnostics/divergence_decomposition.py

Harmonia C, M2, 2026-08-31.  Supersedes the reading in
harmonia/diagnostics/action_divergence_floor.py.
"""

from __future__ import annotations

import argparse
import math
import random

# Charon's exact scan, charon/SESSION_2026-08-25_post_reset.md, c1 x equal_mod_2.
CORPUS = dict(
    name="corpus scan (Charon, exact, 369.5 GB)",
    divergent=383_800, both_actions=932_852,
    holds_true=3_823_296, holds_false=3_238_748,
)
# The adjudicated headline my 08-25 note was written against.
SAMPLE = dict(
    name="47,389-state sample (adjudicated headline)",
    divergent=27_370, both_actions=47_389,
    holds_true=None, holds_false=None,   # marginal imported from the corpus row
)


def ceiling(p):
    """Max divergence achievable when the action is irrelevant (homogeneous states)."""
    return 2.0 * p * (1.0 - p)


def excess_decomposition(D, p):
    """Return (excess, implied E[d^2]-Var(q)).  The identity is exact."""
    exc = D - ceiling(p)
    return exc, exc / 2.0


def bound_on_action_effect(D, p):
    """What the statistic alone licenses about the RMS action effect sqrt(E[d^2]).

    E[d^2] = Var(q) + (D - 2p(1-p))/2, and Var(q) is unknown in [0, p(1-p)].
    """
    _, half = excess_decomposition(D, p)
    lo = max(0.0, half)                 # Var(q) >= 0
    hi = min(p * (1.0 - p) + half, 1.0)  # Var(q) <= p(1-p)
    return lo, hi


# --------------------------------------------------------------------------- tests

def _simulate(n_states, q_draw, d_draw, rng):
    """One draw of the two-action world; returns (D, p_hat, Var(q), E[d^2], qbar)."""
    div = 0
    ysum = 0
    qs, ds = [], []
    for _ in range(n_states):
        q = q_draw(rng)
        d = d_draw(rng)
        a_p = min(1.0, max(0.0, q + d))
        b_p = min(1.0, max(0.0, q - d))
        qs.append((a_p + b_p) / 2.0)
        ds.append((a_p - b_p) / 2.0)
        ya = 1 if rng.random() < a_p else 0
        yb = 1 if rng.random() < b_p else 0
        div += (ya != yb)
        ysum += ya + yb
    n = float(n_states)
    qbar = sum(qs) / n
    varq = sum((q - qbar) ** 2 for q in qs) / n
    ed2 = sum(d * d for d in ds) / n
    return div / n, ysum / (2 * n), varq, ed2, qbar


def test_identity(rng):
    """D - 2p(1-p) == 2(E[d^2]-Var(q)), to Monte-Carlo error."""
    regimes = [
        ("homogeneous, no action effect", lambda r: 0.5, lambda r: 0.0),
        ("heterogeneous, no action effect", lambda r: r.choice([0.15, 0.5, 0.85]), lambda r: 0.0),
        ("homogeneous, strong action effect", lambda r: 0.5, lambda r: 0.35),
        ("heterogeneous + action effect", lambda r: r.uniform(0.2, 0.8), lambda r: r.choice([0.0, 0.2])),
    ]
    ok = True
    print("%-34s%9s%10s%10s%13s%9s" % ("regime", "D", "2p(1-p)", "excess", "2(Ed2-Varq)", "gap"))
    print("-" * 85)
    for label, qd, dd in regimes:
        D, p, varq, ed2, qbar = _simulate(400_000, qd, dd, rng)
        # p is estimated from realised outcomes; use qbar for the identity's p (they agree).
        exc = D - ceiling(qbar)
        pred = 2.0 * (ed2 - varq)
        gap = abs(exc - pred)
        ok &= gap < 0.005
        print("%-34s%9.4f%10.4f%+10.4f%+13.4f%9.4f" % (label, D, ceiling(qbar), exc, pred, gap))
    print()
    return ok


def test_jensen(rng):
    """Action irrelevant => D <= 2p(1-p), for every heterogeneity profile."""
    ok = True
    print("%-34s%9s%10s%12s" % ("action-irrelevant world", "D", "2p(1-p)", "D<=ceiling"))
    print("-" * 65)
    worlds = [
        ("q == 0.50 (no heterogeneity)", lambda r: 0.50),
        ("q ~ U(0.3,0.7)", lambda r: r.uniform(0.3, 0.7)),
        ("q ~ {0.05,0.95}", lambda r: r.choice([0.05, 0.95])),
        ("q ~ {0.0,1.0} (deterministic)", lambda r: r.choice([0.0, 1.0])),
    ]
    for label, qd in worlds:
        D, p, _, _, qbar = _simulate(200_000, qd, lambda r: 0.0, rng)
        held = D <= ceiling(qbar) + 0.005
        ok &= held
        print("%-34s%9.4f%10.4f%12s" % (label, D, ceiling(qbar), str(held)))
    print()
    return ok


def test_label_invariance(rng):
    """Swapping the action labels leaves D unchanged => D cannot detect action effect."""
    pairs = [(1 if rng.random() < 0.7 else 0, 1 if rng.random() < 0.2 else 0)
             for _ in range(200_000)]
    d_fwd = sum(a != b for a, b in pairs) / len(pairs)
    d_swp = sum(b != a for a, b in pairs) / len(pairs)
    mean_a = sum(a for a, _ in pairs) / len(pairs)
    mean_b = sum(b for _, b in pairs) / len(pairs)
    ok = d_fwd == d_swp
    print("label invariance (world where action a is MUCH better than b)")
    print("-" * 65)
    print("  P(Y_a=1) = %.4f   P(Y_b=1) = %.4f   (a is better by %+.4f)"
          % (mean_a, mean_b, mean_a - mean_b))
    print("  D as recorded = %.4f   D with labels swapped = %.4f   identical: %s"
          % (d_fwd, d_swp, ok))
    print("  => D is the same number in the mirrored world where b is better.")
    print()
    return ok


def test_coin_maximises(rng):
    """The statistic is MAXIMISED by the least navigable world."""
    D_coin, _, _, _, _ = _simulate(200_000, lambda r: 0.5, lambda r: 0.0, rng)
    D_det, _, _, _, _ = _simulate(200_000, lambda r: r.choice([0.0, 1.0]), lambda r: 0.0, rng)
    ok = D_coin > D_det
    print("does a high D mean the corpus is navigable?")
    print("-" * 65)
    print("  fair coin at every state (nothing is learnable)   D = %.4f" % D_coin)
    print("  outcome fully determined by state (no choice)     D = %.4f" % D_det)
    print("  the UNLEARNABLE world scores higher: %s" % ok)
    print("  => D measures outcome entropy at the state, not decision value.")
    print()
    return ok


def run_tests():
    rng = random.Random(20260831)
    results = [
        ("identity D-2p(1-p) = 2(E[d^2]-Var(q))", test_identity(rng)),
        ("Jensen: action-irrelevant D <= 2p(1-p)", test_jensen(rng)),
        ("label invariance of D", test_label_invariance(rng)),
        ("coin maximises D", test_coin_maximises(rng)),
    ]
    print("=" * 85)
    for name, ok in results:
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
    n_ok = sum(1 for _, ok in results if ok)
    print("  %d/%d" % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 1


# --------------------------------------------------------------------------- report

def report():
    p = CORPUS["holds_true"] / (CORPUS["holds_true"] + CORPUS["holds_false"])
    print("Action-divergence decomposition -- correction of the 2026-08-25 filing")
    print("=" * 85)
    print("marginal hold rate p (exact corpus scan) = %.6f" % p)
    print("ceiling 2p(1-p) [NOT a floor]            = %.6f" % ceiling(p))
    print()
    print("%-44s%10s%9s%10s%11s" % ("population", "n", "D", "excess", "Ed2-Varq"))
    print("-" * 84)
    for src in (SAMPLE, CORPUS):
        D = src["divergent"] / src["both_actions"]
        exc, half = excess_decomposition(D, p)
        print("%-44s%10s%9.4f%+10.4f%+11.4f"
              % (src["name"], "{:,}".format(src["both_actions"]), D, exc, half))
    print()

    print("what each licenses about the action effect, from D alone")
    print("-" * 84)
    for src in (SAMPLE, CORPUS):
        D = src["divergent"] / src["both_actions"]
        lo, hi = bound_on_action_effect(D, p)
        print("  %s" % src["name"])
        print("    E[d^2] in [%.4f, %.4f]  ->  RMS action effect >= %.4f" % (lo, hi, math.sqrt(lo)))
        if lo <= 0.0:
            print("    LOWER BOUND IS ZERO: consistent with the action being wholly irrelevant.")
        else:
            print("    requires a large action effect -- or a selection effect in what got logged.")
    print()
    print("RULING")
    print("-" * 84)
    print("  The +0.081 'excess' I filed on 2026-08-25 was measured against a bound that")
    print("  points the other way, on a sample Charon has since shown to be unrepresentative.")
    print("  At corpus scale the same statistic sits 0.085 BELOW the ceiling, which is what")
    print("  an irrelevant action over heterogeneous states produces.  My section 2 conclusion")
    print("  -- 'regret is very likely non-vacuous, ~34 SE from zero' -- is WITHDRAWN.")
    print("  It is NOT replaced by the opposite claim.  Exceeding the ceiling would have")
    print("  been a valid one-sided test; the corpus does not exceed it, and falling below")
    print("  licenses nothing.  D is silent here, in both directions.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="run the four self-tests")
    a = ap.parse_args()
    raise SystemExit(run_tests() if a.test else report())


if __name__ == "__main__":
    main()
