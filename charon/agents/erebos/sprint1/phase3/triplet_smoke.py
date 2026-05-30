"""Phase 3.F — Triplet motif primitive smoke (ITER-60).

Run triplet co-occurrence motif extraction on combined real ledger.
Pre-committed PASS criterion: >= 1 triplet motif surfaces above
the lift threshold.

A triplet motif is structurally impossible to express as a
pair-aware counter (the pair counter's joint statistics top out
at 2 cells). If triplet motifs surface with high lift, the
substrate has access to higher-order structure that no pairwise
baseline can match.
"""
from __future__ import annotations

from dataclasses import dataclass

from charon.agents.erebos._cross_cell_motif import extract_triplet_motifs
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _load_real_rows,
)


MIN_COOCCURRENCE = 2
MIN_LIFT = 1.5
PASS_THRESHOLD = 1


@dataclass(frozen=True)
class TripletSmokeResult:
    n_rows: int
    n_signatures: int
    n_signatures_with_triple_emissions: int
    n_triplet_motifs: int
    top_lift: float
    sample_triplets: tuple
    verdict: str
    headline: str


def run_triplet_smoke() -> TripletSmokeResult:
    rows = _load_real_rows(include_enriched=True)
    result = extract_triplet_motifs(
        rows,
        min_cooccurrence=MIN_COOCCURRENCE,
        min_lift=MIN_LIFT,
    )

    n_motifs = len(result.motifs)
    top_lift = (
        result.motifs[0].lift_over_pair_independence
        if result.motifs else 0.0
    )

    if n_motifs >= PASS_THRESHOLD:
        verdict = "PASS"
        headline = (
            f"PASS: {n_motifs} triplet motif(s) surface above lift "
            f"{MIN_LIFT} (top lift={top_lift:.2f}). The substrate "
            f"detects higher-order structure no pair-aware counter "
            f"can express."
        )
    else:
        verdict = "FAIL"
        headline = (
            f"FAIL: zero triplet motifs above lift {MIN_LIFT}. "
            f"The substrate has no 3-cell structure to navigate "
            f"in the current ledger -- triplet primitive does not "
            f"extend ITER-58's pair-cell value on this data."
        )

    samples = tuple(
        (m.cells, m.cooccurrence_count, round(m.lift_over_pair_independence, 2))
        for m in result.motifs[:5]
    )

    return TripletSmokeResult(
        n_rows=len(rows),
        n_signatures=result.n_signatures_scanned,
        n_signatures_with_triple_emissions=result.n_signatures_with_triple_emissions,
        n_triplet_motifs=n_motifs,
        top_lift=top_lift,
        sample_triplets=samples,
        verdict=verdict,
        headline=headline,
    )


if __name__ == "__main__":
    r = run_triplet_smoke()
    print("=" * 72)
    print("Phase 3.F -- Triplet motif primitive smoke verdict")
    print("=" * 72)
    print(r.headline)
    print()
    print(f"  n_rows                                    : {r.n_rows}")
    print(f"  n_signatures                              : {r.n_signatures}")
    print(f"  n_signatures with >=3 emissions           : {r.n_signatures_with_triple_emissions}")
    print(f"  n_triplet_motifs above threshold          : {r.n_triplet_motifs}")
    print(f"  top lift                                  : {r.top_lift:.2f}")
    print()
    print(f"VERDICT: {r.verdict}")
    if r.sample_triplets:
        print()
        print("Sample triplets (cells, cooc, lift):")
        for cells, cooc, lift in r.sample_triplets:
            print(f"  lift={lift}  cooc={cooc}")
            for c in cells:
                print(f"    {c}")
