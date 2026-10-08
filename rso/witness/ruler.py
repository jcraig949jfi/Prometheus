"""Stochastic retention ruler P-RET and calibration gate P-CAL for the native witness (C-009-T014).

Specification: rso/witness/RULER.md (this packet). Design: rso/witness/DESIGN_DRAFT.md s4-s5 (Cadmus, C-009-T012),
SELECTION.md (Ares W15). Outcome typing: closure C1 (D02, D11) -- P-RET is a RULER with outcomes POSITIVE / NEGATIVE /
NOT_SHOWN / INDETERMINATE (INDETERMINATE: a registered statistical decision that meets neither threshold); P-CAL is a
GATE, PASS or FAIL with its reason. A correct negative observation is a ruler outcome, never a FAIL.

Unit of analysis: the EPISODE of the frozen subject. One episode gives one decision (episode_decision): the majority
non-abstain action over the steps after the episode's last interrupt; abstain-only or a tie is NO_ANSWER and counts
as incorrect. Episodes are independent given the frozen subject (the genome is restored at every B2 reset and each
episode draws its own world), and the design balances r exactly (n/2 episodes with r = 0, n/2 with r = 1).

Under no carry (the decision is independent of r) the number correct X has mean <= n/2 and variance <= n/4, so the
exact one-sided binomial test against p0 = 1/2 has size <= alpha (it is exact for a fair-coin subject, conservative
for a constant or abstaining one). Every threshold is an INTEGER computed here in exact rational arithmetic, so the
preregistration states them as numbers and the ruler reads no floating-point statistic.

No witness data is read or produced here: everything below is a pure function, tested on synthetic data only
(SELECTION.md gate). Python >= 3.8, standard library only.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb

# Registered values (RULER.md s3). Changing any of these is a preregistration change.
N_EPISODES = 2048                # 1024 with r = 0, 1024 with r = 1 (RULER.md s4: power of NEGATIVE and of P-CAL)
ALPHA = Fraction(1, 100)         # per decision (each one-sided test)
DELTA = Fraction(1, 20)          # smallest effect of interest above / around the bound
BOUND = Fraction(1, 2)           # registered no-carry bound: balanced binary r
NO_ANSWER = 0                    # Ares action 0 = abstain; 1 / 2 = the regime actions (good = r + 1)
RULER_VALUES = ("POSITIVE", "NEGATIVE", "NOT_SHOWN", "INDETERMINATE")


class RulerError(ValueError):
    pass


# --------------------------------------------------------------------------------------------------------
# Exact binomial tails

_CACHE = {}


def _cumulative(n, p):
    """(cdf numerators, denominator) of Binomial(n, p) in exact integers: P(X <= k) = cdf[k] / den."""
    p = Fraction(p)
    key = (n, p)
    if key not in _CACHE:
        a, b = p.numerator, p.denominator
        pmf = [comb(n, k) * a ** k * (b - a) ** (n - k) for k in range(n + 1)]
        cdf, acc = [], 0
        for v in pmf:
            acc += v
            cdf.append(acc)
        _CACHE[key] = (cdf, b ** n)
    return _CACHE[key]


def tail_le(n, k, p):
    """P(X <= k) for X ~ Binomial(n, p), exact (a Fraction)."""
    if k < 0:
        return Fraction(0)
    cdf, den = _cumulative(n, p)
    return Fraction(cdf[min(k, n)], den)


def tail_ge(n, k, p):
    """P(X >= k) for X ~ Binomial(n, p), exact."""
    return 1 - tail_le(n, k - 1, p)


def _le_ok(n, k, p, alpha):
    """P(X <= k | p) <= alpha, compared in integers."""
    if k < 0:
        return True
    cdf, den = _cumulative(n, p)
    return cdf[min(k, n)] * alpha.denominator <= alpha.numerator * den


def _ge_ok(n, k, p, alpha):
    """P(X >= k | p) <= alpha, compared in integers."""
    if k <= 0:
        return alpha >= 1
    cdf, den = _cumulative(n, p)
    return (den - cdf[min(k, n + 1) - 1]) * alpha.denominator <= alpha.numerator * den


@lru_cache(maxsize=None)
def thresholds(n=N_EPISODES, alpha=ALPHA, delta=DELTA, bound=BOUND):
    """The integer decision thresholds of P-RET for n episodes.

    k_pos  smallest k with P(X >= k | bound) <= alpha          POSITIVE iff correct >= k_pos;
                                                               NOT_SHOWN iff WRONG answers >= k_pos (inverted)
    k_neg  largest  k with P(X <= k | bound + delta) <= alpha  NEGATIVE iff correct <= k_neg (and not NOT_SHOWN)
    Wrong answers, not low accuracy, decide NOT_SHOWN: an abstaining no-carry subject is less often correct but
    never more often wrong than 1/2 in expectation, so abstention cannot produce NOT_SHOWN (FD-T014-2).
    """
    if n <= 0 or n % 2:
        raise RulerError("n must be a positive even number (balanced r)")
    alpha = Fraction(alpha)
    k_pos = next(k for k in range(n + 2) if k > n or _ge_ok(n, k, bound, alpha))
    k_neg = max(k for k in range(-1, n + 1) if _le_ok(n, k, bound + delta, alpha))
    return {"n": n, "k_pos": k_pos, "k_neg": k_neg}   # cached: callers copy before changing it


# --------------------------------------------------------------------------------------------------------
# Episodes -> decisions

def episode_decision(actions, last_interrupt):
    """The episode's answer: the majority non-abstain action at steps t > last_interrupt; NO_ANSWER on a tie or if
    every such step abstains. `actions` is the episode's action sequence (0 abstain, 1, 2)."""
    tail = [a for t, a in enumerate(actions) if t > last_interrupt and a != NO_ANSWER]
    if any(a not in (1, 2) for a in tail):
        raise RulerError("actions must be 0, 1 or 2")
    ones, twos = tail.count(1), tail.count(2)
    if ones == twos:
        return NO_ANSWER
    return 1 if ones > twos else 2


def correct(decision, r):
    """1 iff the decision is the regime's action (good = r + 1); NO_ANSWER is incorrect."""
    if r not in (0, 1):
        raise RulerError("r must be 0 or 1")
    return 1 if decision == r + 1 else 0


def wrong(decision, r):
    """1 iff the decision is the OTHER regime action; NO_ANSWER is neither correct nor wrong."""
    return 1 if decision in (1, 2) and decision != r + 1 else 0


def _count(episodes, n):
    """episodes: [(r, decision)]. Checks the registered balanced design; returns (correct, wrong)."""
    eps = list(episodes)
    if len(eps) != n:
        raise RulerError("expected %d episodes, got %d" % (n, len(eps)))
    r1 = sum(1 for r, _ in eps if r == 1)
    if r1 * 2 != n:
        raise RulerError("unbalanced design: %d of %d episodes have r = 1" % (r1, n))
    return sum(correct(d, r) for r, d in eps), sum(wrong(d, r) for r, d in eps)


def _frac(x):
    x = Fraction(x)
    return "%d/%d" % (x.numerator, x.denominator)


# --------------------------------------------------------------------------------------------------------
# P-RET (ruler) and P-CAL (gate)

def p_ret(episodes, n=N_EPISODES, alpha=ALPHA, delta=DELTA, bound=BOUND):
    """Retention ruler on the subject's W15 episodes. Outcome shape: kind RULER, value, successes (correct), wrong,
    trials, statistic (exact fraction correct), thresholds, reason. NOT_SHOWN and POSITIVE are exclusive
    (correct + wrong <= n < 2 k_pos); then NEGATIVE; else INDETERMINATE."""
    x, w = _count(episodes, n)
    th = thresholds(n, alpha, delta, bound)
    if w >= th["k_pos"]:
        value, why = "NOT_SHOWN", "wrong answers significantly above %s: r reaches the answer, inverted" % _frac(bound)
    elif x >= th["k_pos"]:
        value, why = "POSITIVE", "accuracy significantly above the no-carry bound %s" % _frac(bound)
    elif x <= th["k_neg"]:
        value, why = "NEGATIVE", "accuracy shown below bound + delta = %s (no retention of that size)" % _frac(bound + delta)
    else:
        value, why = "INDETERMINATE", "neither threshold met at the registered n"
    return {"kind": "RULER", "ruler": "P-RET", "value": value, "successes": x, "wrong": w, "trials": n,
            "statistic": _frac(Fraction(x, n)), "bound": _frac(bound), "delta": _frac(delta), "alpha": _frac(alpha),
            "thresholds": dict(th), "reason": "P-RET %s: %d/%d correct, %d wrong; %s" % (value, x, n, w, why)}


def p_cal(null_episodes, shuf_episodes, pos_episodes, n=N_EPISODES, alpha=ALPHA, delta=DELTA, bound=BOUND):
    """Calibration gate. PASS iff the NULL arm on W15 and the subject on SHUF are each shown below bound + delta
    (correct <= k_neg: no-carry arms do not beat the registered bound by delta or more) AND the POS carrier is P-RET
    POSITIVE. The margin is one-sided because the bound is an upper bound and abstention lowers accuracy without
    breaking it (FD-T014-3). FAIL names the first failing arm; an arm that cannot be shown below the margin at the
    registered n FAILS -- the gate never passes by default. eligible_count = 3 arms."""
    th = thresholds(n, alpha, delta, bound)
    counts = {"NULL": _count(null_episodes, n)[0], "SHUF": _count(shuf_episodes, n)[0]}
    pos = p_ret(pos_episodes, n, alpha, delta, bound)
    witness, reason = None, None
    for arm in ("NULL", "SHUF"):
        x = counts[arm]
        if x > th["k_neg"]:
            witness = {"arm": arm, "successes": x, "trials": n, "k_neg": th["k_neg"]}
            reason = "calibration arm %s not shown below bound + delta: %d/%d > %d" % (arm, x, n, th["k_neg"])
            break
    if witness is None and pos["value"] != "POSITIVE":
        witness = {"arm": "POS", "successes": pos["successes"], "trials": n, "value": pos["value"]}
        reason = "positive control not detected: POS is %s (%d/%d)" % (pos["value"], pos["successes"], n)
    value = "FAIL" if witness else "PASS"
    return {"kind": "GATE", "predicate": "P-CAL", "value": value,
            "reason": reason or "NULL and SHUF below bound + %s; POS detected" % _frac(delta),
            "witness": witness, "eligible_count": 3, "applicable_count": None, "vacuous": False,
            "counts": dict(counts, POS=pos["successes"]), "thresholds": dict(th)}


# --------------------------------------------------------------------------------------------------------
# P-CHAN (gate; C-009-T017): does the advantage vanish when the allowed channel (plastic W1) is ablated?

@lru_cache(maxsize=None)
def mcnemar_threshold(m, alpha=ALPHA):
    """Smallest b with P(B >= b | B ~ Binomial(m, 1/2)) <= alpha: the one-sided exact McNemar threshold for m
    discordant pairs. m = 0 gives 1 (no discordant pair can never pass)."""
    alpha = Fraction(alpha)
    return next(b for b in range(m + 2) if b > m or _ge_ok(m, b, BOUND, alpha))


def p_chan(pairs, n=N_EPISODES, alpha=ALPHA, delta=DELTA, bound=BOUND):
    """Channel gate on PAIRED episodes: pairs = [(r, decision of X, decision of X-NOPL)], X and X-NOPL run on the
    SAME episode seeds (so the same r and world per pair). Applies only when X is P-RET POSITIVE (PREREG_DRAFT s5);
    otherwise RulerError -- the gate is not evaluated.

    PASS iff (1) X-NOPL is P-RET NEGATIVE (the advantage VANISHES under the ablation: accuracy shown below bound +
    delta; INDETERMINATE or POSITIVE is not enough) AND (2) the exact one-sided McNemar test on the discordant pairs
    favours X: b >= mcnemar_threshold(b + c) with b = X correct & X-NOPL not correct, c = the reverse. Under H0 of
    equal accuracy (exchangeable discordant outcomes) part (2) passes with probability <= alpha, conditionally on
    b + c and therefore unconditionally. Replaces the draft difference-of-totals rule (RULER.md s5, FD-T017-1).
    """
    ps = list(pairs)
    if any(len(t) != 3 for t in ps):
        raise RulerError("P-CHAN needs paired episodes (r, decision X, decision X-NOPL)")
    x = p_ret([(r, dx) for r, dx, _ in ps], n, alpha, delta, bound)
    if x["value"] != "POSITIVE":
        raise RulerError("P-CHAN applies only when X is P-RET POSITIVE (X is %s)" % x["value"])
    nopl = p_ret([(r, dn) for r, _, dn in ps], n, alpha, delta, bound)
    b = sum(1 for r, dx, dn in ps if correct(dx, r) and not correct(dn, r))
    c = sum(1 for r, dx, dn in ps if correct(dn, r) and not correct(dx, r))
    need = mcnemar_threshold(b + c, alpha)
    witness = None
    if nopl["value"] != "NEGATIVE":
        witness = {"why": "NOPL_NOT_NEGATIVE", "nopl": nopl["value"], "nopl_correct": nopl["successes"]}
        reason = "advantage not shown to vanish: X-NOPL is %s (%d/%d correct)" % (nopl["value"], nopl["successes"], n)
    elif b < need:
        witness = {"why": "NO_PAIRED_ADVANTAGE", "b": b, "c": c, "needed": need}
        reason = "paired advantage not significant: X wins %d, X-NOPL wins %d of %d discordant pairs (need %d)" % (
            b, c, b + c, need)
    else:
        reason = "X-NOPL NEGATIVE and X wins %d of %d discordant pairs (>= %d)" % (b, b + c, need)
    return {"kind": "GATE", "predicate": "P-CHAN", "value": "FAIL" if witness else "PASS", "reason": reason,
            "witness": witness, "eligible_count": n, "applicable_count": b + c, "vacuous": b + c == 0,
            "x_correct": x["successes"], "nopl": nopl["value"], "nopl_correct": nopl["successes"],
            "discordant": {"b": b, "c": c, "needed": need}}


# --------------------------------------------------------------------------------------------------------
# Operating characteristics (synthetic, exact)

def outcome_probabilities(p, n=N_EPISODES, alpha=ALPHA, delta=DELTA, bound=BOUND):
    """Exact probability of each P-RET outcome when the subject always answers and is correct with probability p
    per episode, independently (X ~ Binomial(n, p), wrong = n - X). The design's size and power, before any data.
    Abstention moves mass from correct to NO_ANSWER and can only lower POSITIVE and NOT_SHOWN."""
    th = thresholds(n, alpha, delta, bound)
    p = Fraction(p)
    ns = tail_le(n, n - th["k_pos"], p)                    # wrong = n - correct when the subject always answers
    pos = tail_ge(n, th["k_pos"], p)
    neg = tail_le(n, th["k_neg"], p) - ns
    return {"NOT_SHOWN": ns, "POSITIVE": pos, "NEGATIVE": neg, "INDETERMINATE": 1 - ns - pos - neg}
