"""Phase 3.H — Permutation null for cross-cell primitive (ITER-63).

The single most discriminating test of today's architectural passes.

## The hypothesis being tested

Today's results claim the cross-cell motif primitive produces N
actionable routing deltas vs per-plugin counter on real data. If
this is REAL statistical structure, shuffling the input_signatures
(preserving plugin+kp marginals but breaking the per-signature
linkages) should produce ZERO or near-zero actionable deltas in
the null distribution.

If null permutations produce comparable numbers of deltas, the
primitive's "signal" was lift inflation from low expected counts,
not real cross-cell structure. The architectural pass collapses.

## Protocol (pre-committed)

1. Load combined ledger (production + Mahler-enriched + BSD-enriched).
2. Measure substrate's actionable deltas (= 3 from ITER-58).
3. Run N=200 permutation trials:
   - Each trial: shuffle input_signature column across all rows
     (preserves plugin x kp marginals exactly; breaks input
     linkages)
   - Re-run cross-cell extraction + counter comparison
   - Record actionable_deltas for that trial
4. Empirical p-value = (# trials with actionable_deltas >= 3) / 200
5. Pass if p < 0.05 (substrate's signal is significantly above
   the null distribution).

## Pre-committed pass threshold

p_value < 0.05. If the substrate fails this test, today's
architectural verdicts (ITER-58 through ITER-62) are downgraded
from PASS to STATISTICALLY UNDERDETERMINED.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from charon.agents.erebos._cross_cell_motif import (
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _load_real_rows,
)


N_PERMUTATIONS = 200
MIN_COOCCURRENCE = 3
MIN_LIFT = 1.5
SEED = 1789
ALPHA = 0.05


@dataclass(frozen=True)
class PermutationNullResult:
    observed_deltas: int
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


def _count_actionable_deltas(rows: list[dict]) -> int:
    counter_recs = per_plugin_majority(rows)
    motif_result = extract_cooccurrence_motifs(
        rows, min_cooccurrence=MIN_COOCCURRENCE, min_lift=MIN_LIFT,
    )
    cond_recs = conditional_kp_recommendations(rows, motif_result.motifs)
    n = 0
    for (plugin, _partner), cond_kp in cond_recs.items():
        unc = counter_recs.get(plugin)
        if unc is None:
            continue
        if cond_kp != unc:
            n += 1
    return n


def _shuffle_signatures(rows: list[dict], rng: random.Random) -> list[dict]:
    """Permute input_signature column across rows. Preserves
    plugin/kp marginals exactly; breaks per-signature linkages."""
    sigs = [r.get("input_signature") for r in rows]
    rng.shuffle(sigs)
    return [{**r, "input_signature": s} for r, s in zip(rows, sigs)]


def run_permutation_null() -> PermutationNullResult:
    rows = _load_real_rows(include_enriched=True)

    observed = _count_actionable_deltas(rows)

    rng = random.Random(SEED)
    null: list[int] = []
    for trial in range(N_PERMUTATIONS):
        shuffled = _shuffle_signatures(rows, rng)
        null.append(_count_actionable_deltas(shuffled))

    null_mean = sum(null) / len(null)
    null_var = sum((n - null_mean) ** 2 for n in null) / len(null)
    null_std = null_var ** 0.5
    sorted_null = sorted(null)
    null_p95 = sorted_null[int(0.95 * (len(sorted_null) - 1))]
    null_max = max(null)
    n_ge = sum(1 for n in null if n >= observed)
    p_value = n_ge / len(null)
    z = (observed - null_mean) / null_std if null_std > 0 else float("inf")

    if p_value < ALPHA:
        verdict = "REAL_SIGNAL"
        headline = (
            f"REAL SIGNAL: observed {observed} actionable deltas; "
            f"null distribution mean={null_mean:.2f}, p95={null_p95}; "
            f"empirical p-value = {p_value:.4f} < {ALPHA}. The "
            f"cross-cell primitive's structure survives the "
            f"permutation null. Today's architectural verdicts are "
            f"statistically supported."
        )
    else:
        verdict = "STATISTICALLY_UNDERDETERMINED"
        headline = (
            f"STATISTICALLY UNDERDETERMINED: observed {observed} "
            f"actionable deltas; null distribution mean="
            f"{null_mean:.2f}, p95={null_p95}; p-value = "
            f"{p_value:.4f} >= {ALPHA}. The substrate's signal is "
            f"NOT distinguishable from chance under permuted "
            f"signatures. Today's architectural passes downgraded."
        )

    return PermutationNullResult(
        observed_deltas=observed,
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
    r = run_permutation_null()
    print("=" * 72)
    print("Phase 3.H -- Permutation null for cross-cell primitive")
    print("=" * 72)
    print(r.headline)
    print()
    print(f"  observed_actionable_deltas       : {r.observed_deltas}")
    print(f"  n_null_permutations              : {len(r.null_distribution)}")
    print(f"  null mean (+/- std)              : {r.null_mean:.2f} (+/- {r.null_std:.2f})")
    print(f"  null max                         : {r.null_max}")
    print(f"  null p95                         : {r.null_p95}")
    print(f"  n_null >= observed               : {r.n_null_ge_observed}")
    print(f"  empirical p-value                : {r.p_value:.4f}")
    print(f"  z-score (obs vs null)            : {r.z_score:.2f}")
    print()
    print(f"VERDICT: {r.verdict}")
