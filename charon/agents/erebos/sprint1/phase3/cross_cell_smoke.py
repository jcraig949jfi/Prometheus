"""Phase 3.D smoke test — cross-cell motif primitive vs counter baseline.

Per Phase 3 combined verdict + Option 2 stand: the original motif
extractor (ITER-40) is structurally a per-plugin counter. ITER-58
ships a cross-cell motif primitive that, by construction, consumes
multi-cell patterns counters cannot compute. This smoke test asks:

  Does the cross-cell primitive produce conditional recommendations
  that DIFFER from per-plugin counter recommendations on real
  combined ledger data?

Pass criterion (pre-committed):
  >= 1 actionable delta where:
    (a) substrate's conditional recommendation for (plugin, partner)
        differs from the counter's unconditional recommendation for
        the same plugin
    (b) the underlying motif has lift >= MIN_LIFT and cooccurrence
        count >= MIN_COOCCURRENCE

If pass: Option 2 is empirically supported. Layer 2 redesign is on
the right track.
If fail: even the cross-cell primitive cannot produce actionable
deltas on real data. Escalate to Option 3 (pause + doctrine
reopening).
"""
from __future__ import annotations

from dataclasses import dataclass

from charon.agents.erebos._cross_cell_motif import (
    Cell,
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _load_real_rows,
)


MIN_COOCCURRENCE = 3
MIN_LIFT = 1.5
PASS_THRESHOLD_ACTIONABLE_DELTAS = 1


@dataclass(frozen=True)
class CrossCellSmokeResult:
    n_rows: int
    n_signatures_scanned: int
    n_multi_emission_signatures: int
    n_motifs_surfaced: int
    n_conditional_recommendations: int
    actionable_deltas: int
    sample_deltas: tuple
    verdict: str
    headline: str
    notes: str


def run_cross_cell_smoke() -> CrossCellSmokeResult:
    rows = _load_real_rows(include_enriched=True)
    n_rows = len(rows)

    # Counter baseline: per-plugin majority kp (no context-awareness)
    counter_recs = per_plugin_majority(rows)

    # Cross-cell motifs
    motif_result = extract_cooccurrence_motifs(
        rows,
        min_cooccurrence=MIN_COOCCURRENCE,
        min_lift=MIN_LIFT,
    )

    # Conditional recommendations from motifs
    cond_recs = conditional_kp_recommendations(rows, motif_result.motifs)

    # Actionable deltas: (plugin, partner) where conditional != unconditional
    actionable: list[tuple[str, Cell, str, str]] = []
    for (plugin, partner_cell), cond_kp in cond_recs.items():
        unconditional_kp = counter_recs.get(plugin)
        if unconditional_kp is None:
            continue
        if cond_kp != unconditional_kp:
            actionable.append((plugin, partner_cell, unconditional_kp, cond_kp))

    n_actionable = len(actionable)

    if n_actionable >= PASS_THRESHOLD_ACTIONABLE_DELTAS:
        verdict = "PASS"
        headline = (
            f"PASS: cross-cell motif primitive produces "
            f"{n_actionable} actionable routing delta(s) vs per-"
            f"plugin counter baseline. Option 2 architectural "
            f"redesign is empirically supported on real data."
        )
    else:
        verdict = "FAIL"
        headline = (
            f"FAIL: even the cross-cell motif primitive produces "
            f"zero actionable deltas vs counters on the real "
            f"combined ledger. Option 2 does not rescue the "
            f"architecture. Escalate to Option 3 (pause + reopen "
            f"doctrine)."
        )

    return CrossCellSmokeResult(
        n_rows=n_rows,
        n_signatures_scanned=motif_result.n_signatures_scanned,
        n_multi_emission_signatures=motif_result.n_signatures_with_multiple_emissions,
        n_motifs_surfaced=len(motif_result.motifs),
        n_conditional_recommendations=len(cond_recs),
        actionable_deltas=n_actionable,
        sample_deltas=tuple(actionable[:8]),
        verdict=verdict,
        headline=headline,
        notes=(
            f"min_cooccurrence={MIN_COOCCURRENCE}; min_lift={MIN_LIFT}; "
            f"n_distinct_plugins_in_counter={len(counter_recs)}; "
            f"top motif lift = "
            f"{motif_result.motifs[0].lift if motif_result.motifs else 'N/A'}"
        ),
    )


if __name__ == "__main__":
    r = run_cross_cell_smoke()
    print("=" * 72)
    print("Phase 3.D -- Cross-cell motif primitive smoke verdict")
    print("=" * 72)
    print(r.headline)
    print()
    print(f"  n_rows                      : {r.n_rows}")
    print(f"  n_signatures_scanned        : {r.n_signatures_scanned}")
    print(f"  n_multi_emission_signatures : {r.n_multi_emission_signatures}")
    print(f"  n_motifs_surfaced           : {r.n_motifs_surfaced}")
    print(f"  n_conditional_recs          : {r.n_conditional_recommendations}")
    print(f"  actionable_deltas           : {r.actionable_deltas}")
    print(f"  pass threshold              : >= {PASS_THRESHOLD_ACTIONABLE_DELTAS}")
    print()
    print(f"VERDICT: {r.verdict}")
    print()
    print("Notes:", r.notes)
    if r.sample_deltas:
        print()
        print("Sample actionable deltas (plugin | partner | counter -> substrate):")
        for plugin, partner, ckp, scond in r.sample_deltas:
            print(f"  {plugin:25s} | {str(partner):50s} | {ckp} -> {scond}")
