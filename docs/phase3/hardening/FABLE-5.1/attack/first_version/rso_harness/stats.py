"""G2 and G3. Exact binomial arithmetic: class exclusion against an exact bound, power, zero-hit bound."""
import hashlib
from math import comb

from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, Result

POWER_FLOOR = 0.99


def khash(*ints):
    """A deterministic 64-bit hash of a tuple of integers. The only source of randomness in the harness."""
    h = hashlib.blake2b(digest_size=8)
    for v in ints:
        h.update(int(v).to_bytes(8, "little", signed=True))
    return int.from_bytes(h.digest(), "little")


def tail_ge(n, k, p):
    """P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def critical_k(n, p0, alpha):
    """Smallest k with P(X >= k | p0) <= alpha, or None if even k = n is not rare enough."""
    for k in range(n + 1):
        if tail_ge(n, k, p0) <= alpha:
            return k
    return None


def exclusion_power(n, p0, alpha, p_true):
    """Probability that n trials at rate p_true exclude the class whose exact best rate is p0."""
    k = critical_k(n, p0, alpha)
    return 0.0 if k is None else tail_ge(n, k, p_true)


def preflight(n, p0, alpha, p_positive, floor=POWER_FLOOR):
    """G2. May this run start? Both registered answers must be attainable with probability >= floor.

    The positive must exclude the class (power), and a member of the class must not (1 - alpha).
    """
    k = critical_k(n, p0, alpha)
    if k is None:
        return Result("G2.preflight", BLOCKED,
                      "with n=%d the ruler cannot emit EXCLUDES at alpha=%g: the verdict is unreachable" % (n, alpha))
    power = tail_ge(n, k, p_positive)
    if power < floor:
        return Result("G2.preflight", BLOCKED, "power %.3f is below %.2f (n=%d, critical k=%d)" % (power, floor, n, k),
                      {"power": power, "critical_k": k})
    if 1 - alpha < floor:
        return Result("G2.preflight", BLOCKED, "alpha %g leaves the negative's answer below %.2f" % (alpha, floor))
    return Result("G2.preflight", PASS, "", {"power": power, "critical_k": k})


def class_exclusion(successes, n, p0, alpha):
    """G3. Does the score exclude the class whose exact best rate is p0? Returns EXCLUDES or NOT_EXCLUDED."""
    return "EXCLUDES" if tail_ge(n, successes, p0) <= alpha else "NOT_EXCLUDED"


def clopper_pearson(k, n, conf=0.95):
    """Two-sided exact interval for a binomial rate."""
    a = (1 - conf) / 2

    def solve(target, lo_side):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            value = tail_ge(n, k, mid) if lo_side else 1 - tail_ge(n, k + 1, mid)
            if (value < target) == lo_side:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(a, True)
    upper = 1.0 if k == n else solve(a, False)
    return lower, upper


def zero_hit_upper(n, conf=0.95):
    """One-sided upper bound on the hit rate after zero hits in n independent trials."""
    return 1 - (1 - conf) ** (1.0 / n)


def three_way(count, n, holds_at, fails_at):
    """A registered three-outcome rule on a count of replicates."""
    if not 0 <= fails_at < holds_at <= n:
        raise ValueError("thresholds must satisfy 0 <= fails_at < holds_at <= n")
    return PASS if count >= holds_at else FAIL if count <= fails_at else INDETERMINATE
