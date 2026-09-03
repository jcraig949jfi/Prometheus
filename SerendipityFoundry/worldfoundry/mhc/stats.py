"""Statistical core -- REBUILT around the red team's fatal findings.

THE PRIMARY INFERENTIAL OBJECT (revised): a wealth process on PER-BLOCK
CONDITIONAL RANKS, not a sign-flip permutation p-value.

Why (red-team FATALs, preserved in the packet):
  * Sign-symmetry is FALSE under the no-structure null: perturbing a selected,
    functional player generically degrades outcome-coupled coordinates in
    almost every block ("fragility of a tuned point") -- coherent direction
    with zero microstructure. The null must be CONSTRUCTED, not assumed.
  * Scale heterogeneity: chaotic blocks dominate sums; few-df studentization
    is heavy-tailed. Ranks are uniform under the null regardless of scale.
  * The bridge from permutation p-values to anytime-valid accumulation was
    asserted, not constructed. Betting on conditional ranks IS the anytime-
    valid construction, from block one; optional stopping is safe by Ville.

CONSTRUCTION. Per block b (one world x seed unit):
  * one CANDIDATE contrast   Delta_cand  (e.g. plant twin minus control twin)
  * m REFERENCE contrasts    Delta_ref_i (identically constructed pairs that
    differ only by irrelevant seeds -- OR other draws from the same frozen
    perturbation distribution, for operator-floor nulls)
  Under H0 the candidate is exchangeable with the references WITHIN the
  block, so its rank among them is uniform on {1..m+1} EXACTLY -- by
  construction, for any block scale, any world chaos, any fragility common
  to candidate and references.
  * Wealth update: bet a preregistered fraction on "candidate ranks top".
    e_b = 1 - lam + lam * (m+1) * 1{top rank}   (mixture over a lam grid)
  Ties (all contrasts exactly zero) bet nothing: e_b = 1. Exactly-zero
  blocks are uninformative, never evidence.

Product over independent blocks = e-process; wealth >= 1/alpha gives an
anytime-valid level-alpha test (Ville). Mixture over lam preserves validity.
"""
from __future__ import annotations

from fractions import Fraction

LAM_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))


def block_rank(cand: int, refs: list) -> tuple:
    """Rank of candidate among references, one-sided (large = interesting).
    Returns (is_top, is_tie_all_zero, n_refs)."""
    if cand == 0 and all(r == 0 for r in refs):
        return (False, True, len(refs))
    return (all(cand > r for r in refs), False, len(refs))


def wealth_process(blocks: list) -> Fraction:
    """blocks: list of (cand, refs). Returns final mixture wealth (exact
    rational arithmetic -- no float drift in the inferential object)."""
    wealths = [Fraction(1)] * len(LAM_GRID)
    for cand, refs in blocks:
        top, tie, m = block_rank(cand, refs)
        if tie:
            continue
        payoff = m + 1
        for i, lam in enumerate(LAM_GRID):
            wealths[i] *= (1 - lam) + (lam * payoff if top else Fraction(0))
    return sum(wealths) / len(wealths)


def crossed(blocks: list, threshold: int) -> bool:
    """Anytime-valid: did the mixture wealth EVER cross the threshold along
    the block sequence? (Optional stopping is what field use looks like.)"""
    wealths = [Fraction(1)] * len(LAM_GRID)
    for cand, refs in blocks:
        top, tie, m = block_rank(cand, refs)
        if tie:
            continue
        payoff = m + 1
        for i, lam in enumerate(LAM_GRID):
            wealths[i] *= (1 - lam) + (lam * payoff if top else Fraction(0))
        if sum(wealths) / len(wealths) >= threshold:
            return True
    return False


def naive_sign_test_p(deltas: list) -> Fraction:
    """The REJECTED primary statistic, retained for demonstration: exact
    binomial sign test against sign-symmetry. Shown in qualification to fire
    on pure fragility artifacts that the rank construction correctly ignores."""
    nz = [d for d in deltas if d != 0]
    n = len(nz)
    if n == 0:
        return Fraction(1)
    k = sum(1 for d in nz if d > 0)
    k = max(k, n - k)
    total = Fraction(0)
    for j in range(k, n + 1):
        c = 1
        for x in range(j):
            c = c * (n - x) // (x + 1)
        total += Fraction(c)
    p = Fraction(2) * total / Fraction(2 ** n)
    return min(p, Fraction(1))


def trend_consistency(levels: list, perm_stream, n_perm: int = 300) -> Fraction:
    """Genealogical trend on PER-GENERATION INCREMENTS (red team: never on
    levels -- random-walk drift makes level-trends spurious). Statistic:
    net signed increment consistency. Null: generation-label permutation.
    (Production adds cohort-centering and founder-disjoint blocks; the
    prototype lineage has one founder by construction and says so.)"""
    incs = [levels[i + 1] - levels[i] for i in range(len(levels) - 1)]
    if not any(incs):
        return Fraction(1)

    def stat(seq):
        return abs(sum((1 if x > 0 else -1 if x < 0 else 0) for x in seq))

    obs = stat(incs)
    ge = 0
    labels = list(levels)
    for _ in range(n_perm):
        for i in range(len(labels) - 1, 0, -1):
            j = perm_stream.below(i + 1)
            labels[i], labels[j] = labels[j], labels[i]
        pincs = [labels[i + 1] - labels[i] for i in range(len(labels) - 1)]
        if stat(pincs) >= obs:
            ge += 1
    return Fraction(ge + 1, n_perm + 1)
