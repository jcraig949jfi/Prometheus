"""Cross-cell motif extraction (Phase 3.D / ITER-58).

Per `feedback_counter_baseline_discriminator` + the Phase 3 combined
verdict: the original motif extractor (ITER-40) groups rows by
(plugin, kp) and counts. A per-plugin majority counter groups rows
by plugin and counts. Their outputs match by construction when
there is one dominant kp per plugin -- which is the case on real
ledger data.

To produce signal counters cannot replicate, the new primitive must
consume MULTI-CELL patterns: structures that span TWO OR MORE
(plugin, kp) cells linked by a shared input_signature.

## What this primitive computes

A CO-OCCURRENCE MOTIF is a pair of cells (cell_A, cell_B) where
cell_X = (plugin_X, kp_X), such that both cells were emitted
against the same input_signature in the ledger, with frequency
significantly above the independence baseline.

```
  observed(A, B) = number of input_signatures where both A and B
                   were emitted
  expected(A, B) = N * P(A) * P(B)
                 = (count(A) * count(B)) / N_inputs   (independence)
  lift(A, B)     = observed(A, B) / expected(A, B)
```

A lift > 1.0 means A and B co-occur more often than independent
chance. A counter-based system cannot compute this because it
does not maintain joint statistics across cells; it only knows
marginal frequencies per plugin.

## Why this is by-construction richer than counters

Per-plugin counter outputs:
    recommend(plugin) = argmax_kp count(plugin, kp)

Counters cannot output:
    recommend(plugin | partner_observed) = argmax_kp
        count((plugin, kp) co-occurring with partner)

The conditional recommendation can DIFFER from the unconditional
when the partner-conditional distribution is skewed away from the
marginal. That difference IS the signal counters cannot see.

## What this primitive is NOT

- NOT a graph mining algorithm. It surfaces unordered cell PAIRS
  only. Triplets, paths, cycles are deferred.
- NOT a causal inference tool. Lift > 1 is correlation, not
  causation.
- NOT a substitute for the per-cell motif extractor (ITER-40);
  the two compose -- per-cell motifs identify dominant cells,
  cross-cell motifs identify how dominant cells link.
- NOT predictive without a downstream consumer. The primitive
  surfaces motifs; the recommendation logic lives in the
  routing-with-motifs harness.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional


# A cell is (plugin_id, kill_pattern_or_PROMOTED).
Cell = tuple[str, str]


@dataclass(frozen=True)
class CoOccurrenceMotif:
    """A pair of cells that co-occur across input_signatures
    more often than chance.

    Attributes:
        cell_a, cell_b: the two cells, sorted lexicographically
            so motifs are direction-agnostic.
        cooccurrence_count: number of input_signatures where
            both cells were emitted.
        marginal_a, marginal_b: number of signatures with cell_a
            (resp cell_b) emitted (regardless of partner).
        expected_under_independence: marginal_a * marginal_b /
            n_signatures.
        lift: cooccurrence_count / expected_under_independence.
            >1 means cells associate; <1 means they avoid.
        sample_signatures: up to N representative input_signatures
            where both cells co-occur.
    """
    cell_a: Cell
    cell_b: Cell
    cooccurrence_count: int
    marginal_a: int
    marginal_b: int
    expected_under_independence: float
    lift: float
    sample_signatures: tuple[str, ...]


@dataclass(frozen=True)
class CrossCellResult:
    """Output of one cross-cell motif extraction run."""
    n_signatures_scanned: int
    n_signatures_with_multiple_emissions: int
    motifs: tuple[CoOccurrenceMotif, ...]
    min_cooccurrence: int
    min_lift: float

    def top(self, k: int) -> tuple[CoOccurrenceMotif, ...]:
        return self.motifs[:k]


def _cell_of(row: dict) -> Optional[Cell]:
    """(plugin_id, kp_or_PROMOTED) for a row, or None if malformed."""
    pid = row.get("plugin_id")
    if not pid:
        return None
    kp = row.get("kill_pattern") or "PROMOTED"
    return (pid, kp)


def extract_cooccurrence_motifs(
    rows: Iterable[dict],
    *,
    min_cooccurrence: int = 2,
    min_lift: float = 1.5,
    sample_limit: int = 5,
) -> CrossCellResult:
    """Find (cell_a, cell_b) pairs that co-occur in input_signatures
    more often than independence predicts.

    Args:
        rows: iterable of ledger rows. Each must have plugin_id,
            kill_pattern (may be None for PROMOTED), input_signature.
        min_cooccurrence: minimum count to surface a motif.
        min_lift: minimum lift over independence to surface.
        sample_limit: cap on sample_signatures per motif.
    """
    # Group cells by input_signature
    cells_by_sig: dict[str, set[Cell]] = defaultdict(set)
    sigs_for_pair: dict[tuple[Cell, Cell], list[str]] = defaultdict(list)
    marginal: Counter = Counter()

    for row in rows:
        sig = row.get("input_signature")
        if not sig:
            continue
        cell = _cell_of(row)
        if cell is None:
            continue
        cells_by_sig[sig].add(cell)

    n_total_sigs = len(cells_by_sig)
    n_multi_emission = sum(1 for cells in cells_by_sig.values() if len(cells) > 1)

    # Marginal: count of signatures containing each cell
    for sig, cells in cells_by_sig.items():
        for c in cells:
            marginal[c] += 1

    if n_total_sigs == 0:
        return CrossCellResult(
            n_signatures_scanned=0,
            n_signatures_with_multiple_emissions=0,
            motifs=(),
            min_cooccurrence=min_cooccurrence,
            min_lift=min_lift,
        )

    # Pair counts: ordered tuples sorted lexicographically so the
    # motif is direction-agnostic
    pair_count: Counter = Counter()
    for sig, cells in cells_by_sig.items():
        if len(cells) < 2:
            continue
        cell_list = sorted(cells)
        for i in range(len(cell_list)):
            for j in range(i + 1, len(cell_list)):
                key = (cell_list[i], cell_list[j])
                pair_count[key] += 1
                sigs_for_pair[key].append(sig)

    # Build motifs above threshold
    motifs: list[CoOccurrenceMotif] = []
    for (a, b), cooc in pair_count.items():
        if cooc < min_cooccurrence:
            continue
        ma, mb = marginal[a], marginal[b]
        if n_total_sigs == 0 or ma == 0 or mb == 0:
            continue
        expected = (ma * mb) / n_total_sigs
        lift = cooc / expected if expected > 0 else float("inf")
        if lift < min_lift:
            continue
        samples = tuple(sigs_for_pair[(a, b)][:sample_limit])
        motifs.append(CoOccurrenceMotif(
            cell_a=a,
            cell_b=b,
            cooccurrence_count=cooc,
            marginal_a=ma,
            marginal_b=mb,
            expected_under_independence=expected,
            lift=lift,
            sample_signatures=samples,
        ))

    # Sort by lift desc, then cooccurrence_count desc, then cells asc
    motifs.sort(key=lambda m: (-m.lift, -m.cooccurrence_count, m.cell_a, m.cell_b))

    return CrossCellResult(
        n_signatures_scanned=n_total_sigs,
        n_signatures_with_multiple_emissions=n_multi_emission,
        motifs=tuple(motifs),
        min_cooccurrence=min_cooccurrence,
        min_lift=min_lift,
    )


def conditional_kp_recommendations(
    rows: list[dict],
    motifs: Iterable[CoOccurrenceMotif],
) -> dict[tuple[str, Cell], str]:
    """For each (plugin, partner_cell) pair where there's a motif
    linking (plugin, kp_X) to partner_cell, return the kp the
    substrate would recommend conditional on the partner being
    observed.

    Returns: {(plugin, partner_cell): recommended_kp_for_plugin}

    Counter baseline cannot produce this map — it has no notion of
    partner-conditional recommendation. Each (plugin, partner_cell)
    in this map is a potential actionable delta.
    """
    motif_list = list(motifs)
    # For each motif, both cells are candidates: given cell_B observed
    # as partner, the substrate believes cell_A is more likely to
    # co-occur than independence; that promotes A's kp for A's plugin.
    # Map (A.plugin, B) -> best kp for A.plugin given B observed
    # Score by lift
    scores: defaultdict[tuple[str, Cell], dict[str, float]] = defaultdict(dict)
    for m in motif_list:
        a_plugin, a_kp = m.cell_a
        b_cell = m.cell_b
        prior = scores[(a_plugin, b_cell)].get(a_kp, 0.0)
        scores[(a_plugin, b_cell)][a_kp] = max(prior, m.lift)
        # Symmetric direction
        b_plugin, b_kp = m.cell_b
        a_cell = m.cell_a
        prior2 = scores[(b_plugin, a_cell)].get(b_kp, 0.0)
        scores[(b_plugin, a_cell)][b_kp] = max(prior2, m.lift)

    recommendations: dict[tuple[str, Cell], str] = {}
    for (plugin, partner), kp_scores in scores.items():
        best_kp = max(kp_scores.items(), key=lambda kv: kv[1])[0]
        recommendations[(plugin, partner)] = best_kp
    return recommendations


def per_plugin_majority(rows: list[dict]) -> dict[str, str]:
    """Counter baseline: per-plugin most-common kp."""
    by_plugin: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        pid = r.get("plugin_id")
        if not pid:
            continue
        kp = r.get("kill_pattern") or "PROMOTED"
        by_plugin[pid][kp] += 1
    return {p: c.most_common(1)[0][0] for p, c in by_plugin.items()}
