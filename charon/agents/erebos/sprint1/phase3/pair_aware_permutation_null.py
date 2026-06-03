"""Phase 3.K -- Permutation null for the PAIR-AWARE robustness claim (ITER-83).

## Why this harness exists (Charon adversarial audit, 2026-06-03)

The Phase 3 stress audit (ITER-63/64/66) ran a permutation null, a scale
stress, and a parent-child isolation -- but ALL THREE compared the cross-cell
primitive against `per_plugin_majority`, the UNCONDITIONAL counter (3 deltas).

The architecture's single strongest real-data validation, however, is a
DIFFERENT number: the **2 actionable deltas vs the PAIR-AWARE counter**
(Phase 3.E / ITER-59). That is the "ROBUST PASS -- robust against the
strongest counter baseline -- the lift filter is load-bearing" claim cited in
`PHASE3_EFG_VERDICT` §1 and §6 as the substrate's first genuine architectural
pass on real data against a discriminating baseline.

That load-bearing number was NEVER subjected to a permutation null.

Per `feedback_counter_baseline_discriminator`: the discriminating question is
whether Layer 2 beats typed-row + counters, not whether it beats a weak
counter. The pair-aware counter IS that discriminating baseline. So the
permutation null that matters is the one on the substrate-vs-pair-aware delta
count -- not the substrate-vs-per-plugin one the stress audit ran.

## The hypothesis being tested

The 2 substrate-vs-pair-aware deltas are cases where the lift filter makes the
substrate diverge from a counter that (for those cells) fell back to the global
majority kp. The claim is that this divergence reflects REAL cross-cell
structure the lift filter captures.

Null hypothesis: the divergence is just lift-vs-count disagreement at chance
level -- lift-max and count-max are different functions that disagree on noise
co-occurrences regardless of whether real structure exists. If shuffling
input_signatures (breaking per-signature linkage, preserving plugin x kp
marginals) produces a comparable number of substrate-vs-pair-aware deltas,
the lift filter's "advantage" is a measurement artifact, not signal.

## Protocol (pre-committed, mirrors permutation_null.py exactly)

1. Load combined ledger (production + Mahler-enriched + BSD-enriched) via the
   same `_load_real_rows(include_enriched=True)` the other harnesses use.
2. Measure observed substrate-vs-pair-aware deltas (expected = 2).
3. N=200 permutation trials: shuffle the input_signature column, recompute BOTH
   the substrate recommendations and the pair-aware counter recommendations on
   the shuffled data, count deltas.
4. Empirical p-value = (# trials with deltas >= observed) / N.
5. Pass iff p < 0.05.

Same SEED, N_PERMUTATIONS, thresholds, and shuffle function as the per-plugin
permutation null, so the only difference is the baseline being compared.

## Pre-committed pass threshold

p_value < 0.05. If this fails, the "ROBUST PASS / lift filter is load-bearing"
claim (Phase 3.E, the architecture's strongest real-data validation) is
downgraded to STATISTICALLY UNDERDETERMINED -- the same downgrade the per-plugin
null (p=0.075 on current ledger) already forces on the 3-delta claim.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from charon.agents.erebos._cross_cell_motif import (
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)
from charon.agents.erebos.sprint1.phase3.pair_aware_counter import (
    pair_aware_counter_recommendations,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _load_real_rows,
)

# Identical to permutation_null.py so the ONLY difference is the baseline.
N_PERMUTATIONS = 200
MIN_COOCCURRENCE = 3
MIN_LIFT = 1.5
SEED = 1789
ALPHA = 0.05


@dataclass(frozen=True)
class PairAwareNullResult:
    observed_deltas_vs_pair: int
    observed_deltas_vs_plugin: int
    null_distribution: tuple[int, ...]
    null_mean: float
    null_std: float
    null_max: int
    null_p95: int
    n_null_ge_observed: int
    p_value: float
    z_score: float
    verdict: str
    headline: str


def _substrate_recs(rows: list[dict]) -> dict:
    motif_result = extract_cooccurrence_motifs(
        rows, min_cooccurrence=MIN_COOCCURRENCE, min_lift=MIN_LIFT,
    )
    return conditional_kp_recommendations(rows, motif_result.motifs)


def _count_deltas_vs_pair(rows: list[dict]) -> int:
    """Substrate-vs-pair-aware-counter deltas. Mirrors the sub_vs_pair
    logic in pair_aware_counter.run_pair_aware_smoke()."""
    substrate = _substrate_recs(rows)
    pair_counter = pair_aware_counter_recommendations(rows)
    n = 0
    for (plugin, partner), sub_kp in substrate.items():
        pair_kp = pair_counter.get((plugin, partner))
        if pair_kp is None or pair_kp != sub_kp:
            n += 1
    return n


def _count_deltas_vs_plugin(rows: list[dict]) -> int:
    """Substrate-vs-per-plugin-counter deltas (cross-check vs ITER-63)."""
    substrate = _substrate_recs(rows)
    counter = per_plugin_majority(rows)
    n = 0
    for (plugin, _partner), sub_kp in substrate.items():
        unc = counter.get(plugin)
        if unc is None:
            continue
        if sub_kp != unc:
            n += 1
    return n


def _shuffle_signatures(rows: list[dict], rng: random.Random) -> list[dict]:
    sigs = [r.get("input_signature") for r in rows]
    rng.shuffle(sigs)
    return [{**r, "input_signature": s} for r, s in zip(rows, sigs)]


def run_pair_aware_permutation_null() -> PairAwareNullResult:
    rows = _load_real_rows(include_enriched=True)

    observed_pair = _count_deltas_vs_pair(rows)
    observed_plugin = _count_deltas_vs_plugin(rows)

    rng = random.Random(SEED)
    null: list[int] = []
    for _ in range(N_PERMUTATIONS):
        shuffled = _shuffle_signatures(rows, rng)
        null.append(_count_deltas_vs_pair(shuffled))

    null_mean = sum(null) / len(null)
    null_var = sum((n - null_mean) ** 2 for n in null) / len(null)
    null_std = null_var ** 0.5
    sorted_null = sorted(null)
    null_p95 = sorted_null[int(0.95 * (len(sorted_null) - 1))]
    null_max = max(null)
    n_ge = sum(1 for n in null if n >= observed_pair)
    p_value = n_ge / len(null)
    z = (observed_pair - null_mean) / null_std if null_std > 0 else float("inf")

    if p_value < ALPHA:
        verdict = "REAL_SIGNAL"
        headline = (
            f"REAL SIGNAL: observed {observed_pair} substrate-vs-pair-aware "
            f"deltas; null mean={null_mean:.2f}, p95={null_p95}; "
            f"p-value={p_value:.4f} < {ALPHA}. The lift filter's advantage "
            f"over the pair-aware counter survives the permutation null. "
            f"The ROBUST PASS claim is statistically supported."
        )
    else:
        verdict = "STATISTICALLY_UNDERDETERMINED"
        headline = (
            f"STATISTICALLY UNDERDETERMINED: observed {observed_pair} "
            f"substrate-vs-pair-aware deltas; null mean={null_mean:.2f}, "
            f"p95={null_p95}; p-value={p_value:.4f} >= {ALPHA}. The lift "
            f"filter's divergence from the pair-aware counter is NOT "
            f"distinguishable from chance lift-vs-count disagreement. "
            f"The ROBUST PASS / 'lift filter is load-bearing' claim "
            f"(Phase 3.E, the architecture's strongest real-data "
            f"validation) is downgraded."
        )

    return PairAwareNullResult(
        observed_deltas_vs_pair=observed_pair,
        observed_deltas_vs_plugin=observed_plugin,
        null_distribution=tuple(null),
        null_mean=null_mean,
        null_std=null_std,
        null_max=null_max,
        null_p95=null_p95,
        n_null_ge_observed=n_ge,
        p_value=p_value,
        z_score=z,
        verdict=verdict,
        headline=headline,
    )


if __name__ == "__main__":
    r = run_pair_aware_permutation_null()
    print("=" * 72)
    print("Phase 3.K -- Permutation null for the PAIR-AWARE robustness claim")
    print("=" * 72)
    print(r.headline)
    print()
    print(f"  observed deltas vs PAIR-AWARE counter : {r.observed_deltas_vs_pair}")
    print(f"  observed deltas vs per-plugin counter : {r.observed_deltas_vs_plugin}")
    print(f"  n_null_permutations                   : {len(r.null_distribution)}")
    print(f"  null mean (+/- std)                   : {r.null_mean:.2f} (+/- {r.null_std:.2f})")
    print(f"  null max                              : {r.null_max}")
    print(f"  null p95                              : {r.null_p95}")
    print(f"  n_null >= observed                    : {r.n_null_ge_observed}")
    print(f"  empirical p-value                     : {r.p_value:.4f}")
    print(f"  z-score (obs vs null)                 : {r.z_score:.2f}")
    print()
    print(f"VERDICT: {r.verdict}")
