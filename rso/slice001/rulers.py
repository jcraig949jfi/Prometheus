"""Retention ruler P2 and its calibration gate P1 (C-004-T012).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0, draft A A4 (truth model: no-carry class N, bound
1/2) and A5 P1/P2, with closure amendment C1: a correct negative observation is a RULER outcome (NEGATIVE),
never a FAIL. Exact rational arithmetic (fractions.Fraction); no floats; no statistical INDETERMINATE.

P1 CALIBRATION is a world-side fact: it is computed from the registered domain alone (world.py) and reads no
runtime. P2 RETENTION reads only the runtime's answer y_A at PROBE_A of episode j+1, for j = 1..3, over all
4096 histories (12288 trials); it says nothing about information the runtime holds elsewhere (A5 P2).

Outcomes are the B3.4 shapes the consumer recomputes (checker.py, FD-T015-2: CALIBRATION witness {j, policy}).
This module decides no claim and qualifies nothing: RETENTION's precondition (CALIBRATION PASS on the same
world) is authority A5's, evaluated by the consumer (evidence.authority).

Python >= 3.8, standard library only.
"""
from fractions import Fraction

from rso.slice001 import world as W

TRIALS = W.HISTORIES * len(W.BOUNDARIES)
NO_CARRY_BOUND = Fraction(1, 2)


def _frac(x):
    x = Fraction(x)
    return "%d/%d" % (x.numerator, x.denominator)


def success(outcome):
    """The exact success s of a RETENTION outcome as a Fraction."""
    return Fraction(outcome["successes"], outcome["trials"])


# --------------------------------------------------------------------------------------------------------
# P1 CALIBRATION (A5 P1; A4)

def _policy_hits(policy, j, variant):
    """Histories in which policy (g1, g2, g3) answers u_j correctly at PROBE_A of episode j+1."""
    ones = W.ones(j, variant)
    return ones if policy[W.BOUNDARIES.index(j)] else W.HISTORIES - ones


def no_carry_maximum(variant="STANDARD"):
    """Exact maximum success over the class N of no-carry policies (A4)."""
    return max(W.no_carry_success(p, variant) for p in W.no_carry_policies())


def calibration(variant="STANDARD"):
    """P1: PASS iff max over N equals 1/2 and u_j is balanced at every evaluated j. Eligible count 8 x 12288.

    FAIL witness {j, policy}: the first best policy in lexicographic order of (g1, g2, g3), and the first
    boundary at which it beats 1/2 (or, if no policy beats 1/2, the first unbalanced boundary).
    """
    policies = W.no_carry_policies()                              # lexicographic (g1, g2, g3)
    best = max(policies, key=lambda p: (W.no_carry_success(p, variant), [-g for g in p]))
    top = W.no_carry_success(best, variant)
    unbalanced = [j for j in W.BOUNDARIES if Fraction(W.ones(j, variant), W.HISTORIES) != NO_CARRY_BOUND]
    eligible = len(policies) * TRIALS
    if top == NO_CARRY_BOUND and not unbalanced:
        return {"kind": "GATE", "predicate": "P1", "value": "PASS",
                "reason": "no-carry maximum equals the registered bound 1/2; u_j balanced at j = 1..3",
                "witness": None, "eligible_count": eligible, "applicable_count": None, "vacuous": False}
    over = [j for j in W.BOUNDARIES if Fraction(_policy_hits(best, j, variant), W.HISTORIES) > NO_CARRY_BOUND]
    j = over[0] if over else unbalanced[0]
    return {"kind": "GATE", "predicate": "P1", "value": "FAIL",
            "reason": "no-carry class reaches %s > 1/2 at boundary %d" % (_frac(top), j),
            "witness": {"j": j, "policy": list(best)}, "eligible_count": eligible, "applicable_count": None,
            "vacuous": False}


# --------------------------------------------------------------------------------------------------------
# P2 RETENTION (A5 P2; closure C1)

def _u_flip(h, j):
    """The history differing from h only in the input u_j (bit position of u_j in h)."""
    return h ^ (1 << (2 * (W.EPISODES - j) + 1))


def retention(answer, variant="STANDARD"):
    """P2 from answer(h, j) = y_A at PROBE_A of episode j+1 in history h.

    POSITIVE iff s = 1. NEGATIVE iff, for every j and every pair of histories differing only in u_j, the
    answer is identical (then s = 1/2 exactly on the balanced domain). NOT_SHOWN otherwise. Never PASS/FAIL.
    """
    per, total = [], 0
    for j in W.BOUNDARIES:
        hits = sum(1 for h in W.histories() if answer(h, j) == W.u_of(h, j, variant))
        per.append({"j": j, "statistic": _frac(Fraction(hits, W.HISTORIES))})
        total += hits
    s = Fraction(total, TRIALS)
    if s == 1:
        value = "POSITIVE"
    elif all(answer(h, j) == answer(_u_flip(h, j), j) for j in W.BOUNDARIES for h in W.histories()):
        value = "NEGATIVE"
    else:
        value = "NOT_SHOWN"
    note = {"POSITIVE": "the answer is u_j in every trial",
            "NEGATIVE": "the answer never depends on u_j (a correct negative observation, closure C1)",
            "NOT_SHOWN": "information about u_j reaches the answer, but not perfectly"}[value]
    return {"kind": "RULER", "ruler": "P2", "value": value, "statistic": _frac(s), "successes": total,
            "trials": TRIALS, "per_boundary": per,
            "reason": "RETENTION %s: s = %s over %d trials; %s" % (value, _frac(s), TRIALS, note)}


def answers_of_runtime(make, variant="STANDARD"):
    """{(h, j): y_A} from world lives with every reset made."""
    out = {}
    for h in W.histories():
        life = W.run_life(make, h, variant)
        for j in W.BOUNDARIES:
            out[(h, j)] = life.probe_a(j + 1)[0]
    return out


def retention_of_runtime(make, variant="STANDARD"):
    ans = answers_of_runtime(make, variant)
    return retention(lambda h, j: ans[(h, j)], variant)


def retention_from_runs(runs, variant="STANDARD"):
    """P2 over the RESET run of trace:probe_a (the adapter's runs, checker TRACE_LAYOUT: 12 chars per history,
    y_A of episode e at offset (e - 1) * 2)."""
    pa = runs["trace:probe_a"]["RESET"]
    return retention(lambda h, j: int(pa[h * 12 + j * 2]), variant)
