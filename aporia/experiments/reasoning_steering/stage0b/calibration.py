"""Relational positive control / calibration (Stage 0b).

The relational H-R1 pipeline was missing a positive control: Stage-0a's control #6
(planted-cycle) validated the DECOMPOSER, but nothing validated the full relational
flow + null battery at H-R1 scale. Every real verdict so far was NULL, so we must
confirm the instrument FIRES on genuine curl at the SAME scale (n~30) before trusting
those NULLs.

Two anchors:
  (1) cyclic_profile(n, m): the canonical maximal Condorcet cycle -- m rotational
      evaluators over n states on a cycle; majority comparison is non-transitive by
      construction. Powered (n~30); must PASS the screen and BEAT_NULL.
  (2) Efron's intransitive dice: a FAMOUS, independent real non-transitive system;
      flow = computed win-probability margins (not hand-set). Confirms the decomposer
      recovers known curl (small n=4, not null-powered -- curl_mass only).
"""
from __future__ import annotations

import itertools

# Efron's intransitive dice: A>B>C>D>A, each with probability 2/3.
EFRON_DICE = {
    "A": [4, 4, 4, 4, 0, 0],
    "B": [3, 3, 3, 3, 3, 3],
    "C": [6, 6, 2, 2, 2, 2],
    "D": [5, 5, 5, 1, 1, 1],
}

__all__ = ["EFRON_DICE", "dice_win_prob", "intransitive_dice_flow", "cyclic_profile"]


def dice_win_prob(d1, d2) -> float:
    """P(d1 rolls strictly higher than d2) + 0.5 * P(tie)."""
    wins = ties = 0
    for a, b in itertools.product(d1, d2):
        if a > b:
            wins += 1
        elif a == b:
            ties += 1
    total = len(d1) * len(d2)
    return (wins + 0.5 * ties) / total


def intransitive_dice_flow(dice=EFRON_DICE):
    """Build (nodes, flow) over the dice; flow(i,j) = P(j beats i) - P(i beats j),
    antisymmetric, in canonical (sorted-label) orientation."""
    labels = sorted(dice)
    idx = {lab: i for i, lab in enumerate(labels)}
    flow = {}
    for a, b in itertools.combinations(labels, 2):       # a < b
        p = dice_win_prob(dice[b], dice[a])              # P(b beats a)
        flow[(idx[a], idx[b])] = float(2 * p - 1.0)      # in [-1, 1]
    return labels, flow


def cyclic_profile(n: int = 30, m: int = 0):
    """Maximal Condorcet cycle: states 0..n-1 on a ring; m rotational evaluators
    (default m=n). Evaluator k scores state i by -((i-k) mod n) (most prefers k,
    least prefers k-1). Majority pairwise comparison is non-transitive by construction.

    Returns records [{margins: {"e<k>": score}}] -- feeds the relational pipeline.
    """
    if n < 3:
        raise ValueError("need n >= 3 states")
    m = m or n
    offsets = [round(k * n / m) % n for k in range(m)]
    records = []
    for i in range(n):
        margins = {f"e{k}": float(-((i - off) % n)) for k, off in enumerate(offsets)}
        records.append({"label": f"s{i}", "margins": margins})
    return records
