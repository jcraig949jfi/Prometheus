"""G2 and the arithmetic every statistical gate uses. Exact binomial tails, computed in logs.

Nothing here is asymptotic. A decision is taken only where an exact tail is at most alpha; where
neither registered answer can be given the outcome is UNDECIDED, and a gate turns that into
INDETERMINATE. An underpowered run is refused before it starts (preflight).
"""
import hashlib
from functools import lru_cache
from math import exp, lgamma, log, log1p

from .verdict import BLOCKED, PASS, Result

POWER_FLOOR = 0.99          # every registered answer must be attainable with at least this probability
DESIGN_CONFIDENCE = 0.99    # a rate seen in design runs is used at its one-sided lower bound


def khash(*ints):
    """A deterministic 64-bit hash of a tuple of integers. The only source of randomness in the harness."""
    h = hashlib.blake2b(digest_size=8)
    for v in ints:
        h.update(int(v).to_bytes(8, "little", signed=True))
    return int.from_bytes(h.digest(), "little")


@lru_cache(maxsize=256)
def pmf(n, p):
    """P(X = i) for i in 0..n, X ~ Binomial(n, p)."""
    if p <= 0.0:
        return (1.0,) + (0.0,) * n
    if p >= 1.0:
        return (0.0,) * n + (1.0,)
    lp, lq, top = log(p), log1p(-p), lgamma(n + 1)
    return tuple(exp(top - lgamma(i + 1) - lgamma(n - i + 1) + i * lp + (n - i) * lq) for i in range(n + 1))


def tail_ge(n, k, p):
    """P(X >= k)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return min(1.0, sum(pmf(n, p)[k:]))


def tail_le(n, k, p):
    """P(X <= k)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return min(1.0, sum(pmf(n, p)[:k + 1]))


def critical_k(n, p0, alpha):
    """Smallest k with P(X >= k | p0) <= alpha, or None if even k = n is not rare enough."""
    for k in range(n + 1):
        if tail_ge(n, k, p0) <= alpha:
            return k
    return None


def lower_critical(n, p, alpha):
    """Largest k with P(X <= k | p) <= alpha, or None if even k = 0 is not rare enough."""
    best = None
    for k in range(n + 1):
        if tail_le(n, k, p) > alpha:
            break
        best = k
    return best


def lower_bound(k, n, conf=DESIGN_CONFIDENCE):
    """One-sided exact lower bound on a rate after k successes in n trials."""
    if n <= 0 or k <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if tail_ge(n, k, mid) < 1 - conf:
            lo = mid
        else:
            hi = mid
    return lo


def upper_bound(k, n, conf=DESIGN_CONFIDENCE):
    """One-sided exact upper bound on a rate after k successes in n trials."""
    if n <= 0 or k >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if tail_le(n, k, mid) < 1 - conf:
            hi = mid
        else:
            lo = mid
    return hi


def is_count(v):
    """A non-negative integer that is not a boolean."""
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


# Words that stand where a registered choice should be. A field holding one of them is not registered.
PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")


def is_placeholder(v):
    return v is None or (isinstance(v, str) and v.strip().lower() in PLACEHOLDERS)


def preflight(n, p0, alpha, p_positive, floor=POWER_FLOOR):
    """The arithmetic of G2. Both answers of the world-side ruler must be attainable with probability >= floor.

    The weakest registered positive (rate p_positive) must come out POSITIVE, and a member of the class
    (rate p0) must come out NEGATIVE: not excluded, and too low for the weakest positive. p_positive is
    taken on trust here; the gate proper is preflight_from_design.
    """
    gate = "G2.preflight"
    if not (is_count(n) and n > 0 and 0 < p0 < 1 and 0 < alpha < 1 and 0 < p_positive <= 1):
        return Result(gate, BLOCKED, "n, bound, alpha and the positive's rate must be registered as numbers in range")
    k = critical_k(n, p0, alpha)
    if k is None:
        return Result(gate, BLOCKED, "with n=%d the ruler cannot say yes at alpha=%g: the verdict is unreachable"
                      % (n, alpha))
    power = tail_ge(n, k, p_positive)
    if power < floor:
        return Result(gate, BLOCKED, "power %.3f is below %.2f (n=%d, critical count %d, positive at %.4f)"
                      % (power, floor, n, k, p_positive), {"power": power, "critical_k": k})
    if 1 - alpha < floor:
        return Result(gate, BLOCKED, "alpha %g leaves the class member's not-yes below %.2f" % (alpha, floor))
    no = lower_critical(n, p_positive, alpha)
    said_no = 0.0 if no is None else tail_le(n, min(no, k - 1), p0)
    if said_no < floor:
        return Result(gate, BLOCKED, "a member of the class is called NEGATIVE with probability %.3f, below %.2f"
                      % (said_no, floor), {"power": power, "critical_k": k, "negative": said_no})
    return Result(gate, PASS, "", {"power": power, "critical_k": k, "negative": said_no})


def preflight_from_design(n, p0, alpha, design_hits, design_n, floor=POWER_FLOOR):
    """G2. The positive's rate is taken from design runs at its lower bound, not from a declaration.

    The counts are still a declaration: the gate cannot see whether the design runs were made.
    """
    if not (is_count(design_n) and design_n > 0 and is_count(design_hits) and design_hits <= design_n):
        return Result("G2.preflight", BLOCKED, "the positive's rate has no design runs behind it")
    return preflight(n, p0, alpha, max(lower_bound(design_hits, design_n), 1e-12), floor)


def classify(successes, n, p0, alpha, p_positive, exact_rate=True):
    """Where a score stands against a class whose best rate is p0 and a weakest registered positive.

    EXCLUDES      too high for any member of the class
    INVERTED      too low for a class whose rate is exactly p0: the cue is carried and its complement
                  answered. Only where the class rate is exact (exact_rate), as in RETAIN-1.
    AT_BOUND      too low for the weakest registered positive, and the class is not excluded
    UNDECIDED     neither answer can be given at this alpha. A registered outcome
    UNDERPOWERED  no count of n can exclude the class at this alpha
    """
    hi = critical_k(n, p0, alpha)
    if hi is None:
        return "UNDERPOWERED"
    if successes >= hi:
        return "EXCLUDES"
    if exact_rate:
        low = lower_critical(n, p0, alpha)
        if low is not None and successes <= low:
            return "INVERTED"
    weak = lower_critical(n, p_positive, alpha)
    if weak is not None and successes <= weak:
        return "AT_BOUND"
    return "UNDECIDED"


def equivalence(k, n, center, margin, alpha):
    """Is a rate shown to lie inside center +- margin (WITHIN), shown to differ from center (OUTSIDE), or neither?

    Two one-sided exact tests each way at alpha/2. Not finding a difference is not WITHIN.
    """
    if tail_ge(n, k, center) <= alpha / 2 or tail_le(n, k, center) <= alpha / 2:
        return "OUTSIDE"
    above = tail_ge(n, k, max(center - margin, 0.0)) <= alpha / 2       # the rate exceeds center - margin
    below = tail_le(n, k, min(center + margin, 1.0)) <= alpha / 2       # the rate is under center + margin
    return "WITHIN" if above and below else "UNDECIDED"


def consistent(k, n, p, alpha):
    """Is a count of k in n compatible with rate p at level alpha (two-sided, exact)?"""
    return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2


def outcome_probability(table, rate):
    """Probability of each outcome of a verdict table when every unit passes with probability `rate`."""
    out, mass = {}, pmf(table["n"], rate)
    for count in range(table["n"] + 1):
        for lo, hi, outcome in table["rule"]:
            if lo <= count <= hi:
                out[outcome] = out.get(outcome, 0.0) + mass[count]
    return out


def zero_hit_upper(n, conf=0.95):
    """One-sided upper bound on a hit rate after zero hits in n independent trials."""
    return 1 - (1 - conf) ** (1.0 / n)
