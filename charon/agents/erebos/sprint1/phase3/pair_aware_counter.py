"""Phase 3.E — Pair-aware counter baseline (ITER-59).

ITER-58 verdict's strongest caveat:

> The cross-cell primitive itself is a generalized counter (pair-
> counts instead of singleton-counts); a sophisticated pair-aware
> counter baseline could close the gap.

This module ships that sophisticated baseline and tests it.

## The pair-aware counter

For each row R with `input_signature = sig`, find all OTHER rows
with the same signature; each of their (plugin, kp) cells is a
"partner" of R. Build a counter:

  pair_count[(R.plugin, partner_cell, R.kp)] += 1

The pair-aware counter's recommendation for `(plugin, partner_cell)`
is `argmax_kp pair_count[(plugin, partner_cell, kp)]` -- the
most-common kp for `plugin` GIVEN `partner_cell` is observed.

This is structurally what the cross-cell motif primitive does, MINUS
the lift-over-independence filter. The pair-aware counter recommends
whatever co-occurs most; the substrate primitive recommends only if
the co-occurrence beats chance.

## Three baselines now

  per-plugin counter:    recommend(plugin) = argmax kp_marginal
  pair-aware counter:    recommend(plugin, partner) = argmax co-occurrence
  cross-cell primitive:  recommend(plugin, partner) = argmax lift over independence

If pair-aware counter == substrate, the lift filter adds nothing.
If pair-aware counter differs from substrate, the lift filter is
the load-bearing component (the substrate suppresses high-volume
but chance-level pairs that pair-aware counter promotes).

## Pass criterion for ITER-58 robustness

Substrate produces ≥1 actionable delta vs pair-aware counter on
the same combined real ledger. If so, ITER-58's architectural pass
is robust. If 0, the substrate's gains over per-plugin counter
were just "track pairs not singletons" and a counter-based system
matches.
"""
from __future__ import annotations

from collections import Counter, defaultdict
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


@dataclass(frozen=True)
class PairAwareSmokeResult:
    n_rows: int
    n_signatures: int
    n_pair_aware_recommendations: int
    n_substrate_recommendations: int
    deltas_substrate_vs_pair_counter: int
    deltas_substrate_vs_plugin_counter: int
    deltas_pair_counter_vs_plugin_counter: int
    sample_substrate_vs_pair_deltas: tuple
    verdict: str
    headline: str
    notes: str


def pair_aware_counter_recommendations(
    rows: list[dict],
) -> dict[tuple[str, Cell], str]:
    """Per-(plugin, partner_cell) most-common kp.

    For each input_signature, every pair of (cell_i, cell_j) with
    i != j contributes:
      pair_count[(plugin_i, cell_j, kp_i)] += 1
    The recommendation for `(plugin, partner)` is the argmax kp.

    NO lift filter. Pure pair-occurrence counter.
    """
    by_sig: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sig = r.get("input_signature")
        if sig and r.get("plugin_id"):
            by_sig[sig].append(r)

    pair_count: defaultdict[tuple[str, Cell], Counter] = defaultdict(Counter)
    for sig, sig_rows in by_sig.items():
        if len(sig_rows) < 2:
            continue
        for i, ri in enumerate(sig_rows):
            ri_plugin = ri["plugin_id"]
            ri_kp = ri.get("kill_pattern") or "PROMOTED"
            for j, rj in enumerate(sig_rows):
                if i == j:
                    continue
                rj_cell = (
                    rj["plugin_id"],
                    rj.get("kill_pattern") or "PROMOTED",
                )
                pair_count[(ri_plugin, rj_cell)][ri_kp] += 1

    return {
        key: counts.most_common(1)[0][0]
        for key, counts in pair_count.items()
    }


def run_pair_aware_smoke() -> PairAwareSmokeResult:
    rows = _load_real_rows(include_enriched=True)

    # Three recommendation maps
    plugin_counter = per_plugin_majority(rows)
    pair_counter = pair_aware_counter_recommendations(rows)
    motif_result = extract_cooccurrence_motifs(
        rows,
        min_cooccurrence=MIN_COOCCURRENCE,
        min_lift=MIN_LIFT,
    )
    substrate = conditional_kp_recommendations(rows, motif_result.motifs)

    # Compute pairwise deltas
    sub_vs_pair: list[tuple[str, Cell, str, str]] = []
    for (plugin, partner), sub_kp in substrate.items():
        pair_kp = pair_counter.get((plugin, partner))
        if pair_kp is None or pair_kp != sub_kp:
            sub_vs_pair.append((plugin, partner,
                                pair_kp or "NONE", sub_kp))

    sub_vs_plugin: list[tuple[str, Cell, str, str]] = []
    for (plugin, partner), sub_kp in substrate.items():
        plug_kp = plugin_counter.get(plugin)
        if plug_kp is None or plug_kp != sub_kp:
            sub_vs_plugin.append((plugin, partner,
                                  plug_kp or "NONE", sub_kp))

    pair_vs_plugin: list[tuple[str, Cell, str, str]] = []
    for (plugin, partner), pair_kp in pair_counter.items():
        plug_kp = plugin_counter.get(plugin)
        if plug_kp is None or plug_kp != pair_kp:
            pair_vs_plugin.append((plugin, partner,
                                   plug_kp or "NONE", pair_kp))

    n_sub_pair = len(sub_vs_pair)
    n_sub_plugin = len(sub_vs_plugin)
    n_pair_plugin = len(pair_vs_plugin)

    if n_sub_pair >= 1:
        verdict = "ROBUST_PASS"
        headline = (
            f"ROBUST PASS: substrate produces {n_sub_pair} "
            f"actionable delta(s) vs PAIR-AWARE counter (not just "
            f"per-plugin counter). The lift filter is load-bearing. "
            f"ITER-58's architectural pass is robust against the "
            f"strongest counter baseline."
        )
    elif n_pair_plugin > 0:
        verdict = "PAIR_COUNTER_MATCHES_SUBSTRATE"
        headline = (
            f"WEAK PASS: substrate ties pair-aware counter "
            f"(0 deltas), but pair-aware counter produces "
            f"{n_pair_plugin} deltas vs per-plugin counter. The "
            f"'cross-cell' value claim collapses to 'track pairs "
            f"not singletons.' Substrate primitive offers no "
            f"signal beyond a sophisticated counter."
        )
    else:
        verdict = "COUNTERS_TIE"
        headline = (
            f"NO LIFT: pair-aware counter also ties per-plugin "
            f"counter on this data (no multi-cell structure to "
            f"navigate). Substrate's ITER-58 pass may have been "
            f"a measurement artifact."
        )

    return PairAwareSmokeResult(
        n_rows=len(rows),
        n_signatures=len(set(r.get("input_signature") for r in rows
                              if r.get("input_signature"))),
        n_pair_aware_recommendations=len(pair_counter),
        n_substrate_recommendations=len(substrate),
        deltas_substrate_vs_pair_counter=n_sub_pair,
        deltas_substrate_vs_plugin_counter=n_sub_plugin,
        deltas_pair_counter_vs_plugin_counter=n_pair_plugin,
        sample_substrate_vs_pair_deltas=tuple(sub_vs_pair[:8]),
        verdict=verdict,
        headline=headline,
        notes=(
            f"min_cooccurrence={MIN_COOCCURRENCE}; "
            f"min_lift={MIN_LIFT}; "
            f"n_motifs_above_threshold={len(motif_result.motifs)}; "
            f"top_motif_lift = "
            f"{motif_result.motifs[0].lift if motif_result.motifs else 'N/A'}"
        ),
    )


if __name__ == "__main__":
    r = run_pair_aware_smoke()
    print("=" * 72)
    print("Phase 3.E -- Pair-aware counter baseline verdict")
    print("=" * 72)
    print(r.headline)
    print()
    print(f"  n_rows                                      : {r.n_rows}")
    print(f"  n_signatures                                : {r.n_signatures}")
    print(f"  n_pair_aware_recommendations                : {r.n_pair_aware_recommendations}")
    print(f"  n_substrate_recommendations                 : {r.n_substrate_recommendations}")
    print(f"  deltas: substrate vs PAIR-AWARE counter     : {r.deltas_substrate_vs_pair_counter}")
    print(f"  deltas: substrate vs per-plugin counter     : {r.deltas_substrate_vs_plugin_counter}")
    print(f"  deltas: pair-aware vs per-plugin counter    : {r.deltas_pair_counter_vs_plugin_counter}")
    print()
    print(f"VERDICT: {r.verdict}")
    print()
    print("Notes:", r.notes)
    if r.sample_substrate_vs_pair_deltas:
        print()
        print("Sample substrate-vs-pair-counter deltas:")
        for plugin, partner, pkp, skp in r.sample_substrate_vs_pair_deltas:
            print(f"  {plugin:25s} | partner={str(partner):50s}")
            print(f"      pair-counter: {pkp}")
            print(f"      substrate:    {skp}")
