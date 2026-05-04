"""ergon.learner.archive — MAP-Elites archive with per-operator-class tracking.

Per pivot/ergon_learner_proposal_v8.md §6.2 + ChatGPT's storage-discipline
recommendation:

The archive holds cell elites (the best genome seen for each cell) plus
per-operator-class lineage statistics. Storage discipline: archive holds
only `(cell_coordinate, content_hash, fitness)` pointers; heavy genome
data lives in Postgres `sigma_proto.genomes` (or in-memory dict at MVP).

Three-tier lexicographic comparison among cell-residents (per v8 §6.2):
  1. Battery-survival count (PROMOTE = highest tier)
  2. Residual signal-class flag — DEPRECATED at MVP (Trial 1 negative
     result; classifier in deep escrow). Replaced with proxy:
     band-concentration tier (does the genome land in a productive
     magnitude bucket?)
  3. Cost-amortized fitness (cheaper survivors win ties)

The third-best metric — cell-fill diversity / band-concentration per
operator class — is empirically motivated by Techne's Path B data:
REINFORCE (33% Salem-cluster concentration), PPO (9% cyclotomic),
random (0.1%). This signal exists even when PROMOTE rate is zero.

Per round-2 reviewer's MAP-Elites collapse concern, the archive
includes hot-swap support: rebin_all_elites() applies a new descriptor
to existing elites without losing them.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Iterator, List, Literal, Optional, Sequence, Tuple,
)

from ergon.learner.descriptor import CellCoordinate
from ergon.learner.genome import Genome, MutationOperatorClass


# ---------------------------------------------------------------------------
# Fitness — three-tier lexicographic comparison
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FitnessTuple:
    """Four-tier fitness for cell-elite competition.

    Original three-tier (v8 §6.2 + Trial 1 adjustment):
      Tier 0 (primary): battery_survival_count (PROMOTE = max value).
      Tier 1 (secondary): band_concentration_tier (replaces v7's residual
        signal-class flag since Trial 1 escrowed the classifier).
      Tier 2 (tertiary): cost_amortized_score (cheaper wins ties).

    Iter 11 addition (continuous_signal_score):
      Tier "1.5" — INSERTED between band_concentration_tier and
      cost_amortized_score. Continuous score in [0, +inf) representing
      signal-strength refinement above the substrate-pass threshold.

      Trial 3 production pilot exposed a local-maximum problem in the
      MVP fitness: a 3-conjunct predicate matching pos_x:1, has_diag_neg:
      True, neg_x:4 substrate-PASSes with lift=22.40 and match-size=10.
      Adding the 4th conjunct (n_steps:5) to complete OBSTRUCTION_
      SIGNATURE REDUCES match-size 10→8 without changing the binary
      battery_survival_count. The engine has no gradient to refine the
      passing predicate.

      continuous_signal_score is domain-specific; for Lehmer-Mahler:
      log10(1 + 1/M_excess); for Obstruction: log10(1 + lift). Domains
      that don't have a continuous signal can leave it at 0.0 — fitness
      reduces to the original three-tier order.

    Higher is better at every tier. Lexicographic comparison.
    """
    battery_survival_count: int
    band_concentration_tier: int
    continuous_signal_score: float = 0.0  # NEW Iter 11 — replaces "tier 1.5"
    cost_amortized_score: float = 0.0

    def to_tuple(self) -> Tuple[int, int, float, float]:
        return (
            self.battery_survival_count,
            self.band_concentration_tier,
            self.continuous_signal_score,
            self.cost_amortized_score,
        )

    def beats(self, other: "FitnessTuple") -> bool:
        """Lexicographic strict-greater-than comparison."""
        return self.to_tuple() > other.to_tuple()


# ---------------------------------------------------------------------------
# ArchiveEntry — pointer-storage discipline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArchiveEntry:
    """One cell elite, stored as a pointer.

    Per ChatGPT: archive stores `(cell_coordinate, content_hash,
    fitness)` only. Heavy genome data lives in `sigma_proto.genomes`
    Postgres table (or in-memory `genome_store` dict at MVP).
    """
    cell_coordinate: CellCoordinate
    content_hash: str
    fitness: FitnessTuple
    operator_class: MutationOperatorClass
    n_evaluations: int = 1  # how many genomes have ever competed for this cell


# ---------------------------------------------------------------------------
# The archive
# ---------------------------------------------------------------------------


class MAPElitesArchive:
    """Quality-diversity archive over typed-DAG genomes.

    Storage layout (pointer-storage discipline per ChatGPT recommendation):
      - cells: dict[tuple, ArchiveEntry] — the cell -> elite mapping
      - genome_store: dict[content_hash, Genome] — heavy data (in-memory at MVP;
        v0.5 swaps to sigma_proto.genomes Postgres table)
      - operator_class_lineage: dict[content_hash, MutationOperatorClass] —
        kept separately from genome.mutation_operator_class to support
        rebinning under hot-swap (genome's lineage is immutable; archive's
        lineage tracking can update for ablation studies)
      - per_operator_eval_count: how many evaluations each operator has had
      - per_operator_fill_count: how many cells each operator has filled
        (counted as "current elite from this operator class")

    The cells dict's keys are CellCoordinate tuples. ArchiveEntry holds
    the elite. Two genomes with the same cell coordinate compete for the
    elite slot via `fitness.beats(other.fitness)`.

    Hot-swap support: `rebin_all_elites(new_descriptor_fn)` applies a
    new descriptor to all genomes whose content_hash is in genome_store,
    rebuilding the cells dict. Used when descriptor audit (per
    descriptor.compute_fill_rates) flags axis collapse and the
    hot-swap protocol kicks in.
    """

    def __init__(self) -> None:
        self.cells: Dict[Tuple[int, ...], ArchiveEntry] = {}
        self.genome_store: Dict[str, Genome] = {}
        self.per_operator_eval_count: Counter = Counter()
        # Cells claimed-by-operator: cell_coordinate -> operator_class of current elite
        self._operator_cell_filled: Dict[Tuple[int, ...], MutationOperatorClass] = {}

    # ------------------------------------------------------------------
    # Submission
    # ------------------------------------------------------------------

    def submit(
        self,
        genome: Genome,
        cell_coordinate: CellCoordinate,
        fitness: FitnessTuple,
    ) -> bool:
        """Submit a genome for cell-elite competition.

        Returns True if the genome won the cell (became elite); False
        if an existing elite beat it.

        Always increments per_operator_eval_count (regardless of win),
        which tracks how many evaluations each operator class has spent.
        """
        operator = genome.mutation_operator_class
        self.per_operator_eval_count[operator] += 1

        cell_key = cell_coordinate.to_tuple()
        existing = self.cells.get(cell_key)

        if existing is None:
            # Cell empty: claim it
            self.cells[cell_key] = ArchiveEntry(
                cell_coordinate=cell_coordinate,
                content_hash=genome.content_hash(),
                fitness=fitness,
                operator_class=operator,
                n_evaluations=1,
            )
            self.genome_store[genome.content_hash()] = genome
            self._operator_cell_filled[cell_key] = operator
            return True

        # Cell occupied: lexicographic comparison
        existing_evals = existing.n_evaluations + 1
        if fitness.beats(existing.fitness):
            # New genome wins
            self.cells[cell_key] = ArchiveEntry(
                cell_coordinate=cell_coordinate,
                content_hash=genome.content_hash(),
                fitness=fitness,
                operator_class=operator,
                n_evaluations=existing_evals,
            )
            self.genome_store[genome.content_hash()] = genome
            self._operator_cell_filled[cell_key] = operator
            # NOTE: we don't delete the loser's genome from genome_store —
            # it may still be referenced by other archive entries / lineage.
            # Garbage collection is a v0.5 concern.
            return True

        # New genome lost; just bump evaluation count on existing entry
        self.cells[cell_key] = ArchiveEntry(
            cell_coordinate=existing.cell_coordinate,
            content_hash=existing.content_hash,
            fitness=existing.fitness,
            operator_class=existing.operator_class,
            n_evaluations=existing_evals,
        )
        return False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def n_cells_filled(self) -> int:
        """Number of cells with at least one elite."""
        return len(self.cells)

    def get_elite(self, cell_coordinate: CellCoordinate) -> Optional[ArchiveEntry]:
        """Return the elite at a given cell, or None if cell is empty."""
        return self.cells.get(cell_coordinate.to_tuple())

    def get_genome(self, content_hash: str) -> Optional[Genome]:
        """Return the Genome for a given content hash, or None if not stored."""
        return self.genome_store.get(content_hash)

    def all_elites(self) -> Iterator[ArchiveEntry]:
        """Iterate all cell elites in deterministic (sorted by cell_key) order."""
        for key in sorted(self.cells.keys()):
            yield self.cells[key]

    def all_coordinates(self) -> List[CellCoordinate]:
        """Return all occupied CellCoordinates."""
        return [self.cells[key].cell_coordinate for key in sorted(self.cells.keys())]

    # ------------------------------------------------------------------
    # Per-operator-class metrics — the load-bearing diagnostics
    # ------------------------------------------------------------------

    def operator_fill_count(self) -> Dict[MutationOperatorClass, int]:
        """Number of cells whose current elite came from each operator class.

        Per ChatGPT + round-2 review's lineage tagging: this is the per-
        operator measurement that distinguishes which operator class
        fills which territory.
        """
        out: Counter = Counter()
        for op in self._operator_cell_filled.values():
            out[op] += 1
        return dict(out)

    def operator_eval_count(self) -> Dict[MutationOperatorClass, int]:
        """Number of evaluations each operator class has spent."""
        return dict(self.per_operator_eval_count)

    def operator_fill_efficiency(self) -> Dict[MutationOperatorClass, float]:
        """Fills / evaluations ratio per operator class.

        High efficiency = operator finds new cells quickly. Low efficiency
        = operator wastes evaluations on already-occupied cells. The
        anti_prior operator's efficiency relative to neural's is a
        candidate substrate-grade metric per round-6 reviewer concern
        (whether anti_prior actually explores new territory or generates
        structured noise).
        """
        fills = self.operator_fill_count()
        evals = self.operator_eval_count()
        out: Dict[MutationOperatorClass, float] = {}
        for op, n_evals in evals.items():
            if n_evals > 0:
                out[op] = fills.get(op, 0) / n_evals
            else:
                out[op] = 0.0
        return out

    def coverage_divergence(
        self,
        op_a: MutationOperatorClass,
        op_b: MutationOperatorClass,
    ) -> float:
        """Symmetric set-divergence between cells filled by two operators.

        Returns Jaccard distance: 1 - |A ∩ B| / |A ∪ B|, where A and B
        are the cell-key sets each operator's elites currently occupy.

        High divergence (close to 1.0) = operators explore disjoint
        territory — what we want for `anti_prior` vs `neural` per v8 §3.5.
        Low divergence (close to 0) = operators converge on the same
        cells — failure mode round-6 reviewer flagged.
        """
        cells_a = {k for k, v in self._operator_cell_filled.items() if v == op_a}
        cells_b = {k for k, v in self._operator_cell_filled.items() if v == op_b}
        union = cells_a | cells_b
        if not union:
            return 0.0
        intersection = cells_a & cells_b
        jaccard_sim = len(intersection) / len(union)
        return 1.0 - jaccard_sim

    def band_concentration_per_operator(
        self,
        axis_index: int = 3,  # default: magnitude axis (per v8 §6.2)
    ) -> Dict[MutationOperatorClass, Dict[int, float]]:
        """Distribution of operator-class elites across one axis's bins.

        Per Techne's Path B finding: operators show significant band-
        concentration even when PROMOTE rate is zero (REINFORCE 33% Salem,
        PPO 9% cyclotomic, random 0.1%). This is the third-best metric
        Trial 2 should detect.

        Returns: operator -> {axis_value: fraction of operator's elites
        in that bin}
        """
        out: Dict[MutationOperatorClass, Counter] = defaultdict(Counter)
        operator_totals: Counter = Counter()
        for cell_key, entry in self.cells.items():
            axis_value = cell_key[axis_index]
            out[entry.operator_class][axis_value] += 1
            operator_totals[entry.operator_class] += 1
        return {
            op: {bin_val: count / operator_totals[op]
                 for bin_val, count in op_dist.items()}
            for op, op_dist in out.items()
        }

    # ------------------------------------------------------------------
    # Hot-swap support (v8 §6.2 / round-2 reviewer)
    # ------------------------------------------------------------------

    def rebin_all_elites(
        self,
        new_coordinate_fn: Callable[[Genome, ArchiveEntry], CellCoordinate],
    ) -> Dict[str, int]:
        """Rebin existing elites under a new descriptor.

        Used when per-axis fill-rate audit flags axis collapse and
        descriptor.hot_swap protocol activates. Walks all current elites,
        recomputes their cell coordinates via `new_coordinate_fn`,
        rebuilds the cells dict.

        Returns {n_elites_before, n_elites_after, n_collisions}. A
        collision means two pre-rebin elites mapped to the same post-rebin
        cell; the better fitness wins.
        """
        old_cells = list(self.cells.values())
        n_before = len(old_cells)

        new_cells: Dict[Tuple[int, ...], ArchiveEntry] = {}
        new_operator_cell_filled: Dict[Tuple[int, ...], MutationOperatorClass] = {}
        n_collisions = 0

        for old_entry in old_cells:
            genome = self.genome_store.get(old_entry.content_hash)
            if genome is None:
                continue  # stale entry; skip
            new_coord = new_coordinate_fn(genome, old_entry)
            new_key = new_coord.to_tuple()
            existing_new = new_cells.get(new_key)
            if existing_new is None:
                new_cells[new_key] = ArchiveEntry(
                    cell_coordinate=new_coord,
                    content_hash=old_entry.content_hash,
                    fitness=old_entry.fitness,
                    operator_class=old_entry.operator_class,
                    n_evaluations=old_entry.n_evaluations,
                )
                new_operator_cell_filled[new_key] = old_entry.operator_class
            else:
                n_collisions += 1
                # Resolve via fitness comparison
                if old_entry.fitness.beats(existing_new.fitness):
                    new_cells[new_key] = ArchiveEntry(
                        cell_coordinate=new_coord,
                        content_hash=old_entry.content_hash,
                        fitness=old_entry.fitness,
                        operator_class=old_entry.operator_class,
                        n_evaluations=existing_new.n_evaluations + old_entry.n_evaluations,
                    )
                    new_operator_cell_filled[new_key] = old_entry.operator_class

        self.cells = new_cells
        self._operator_cell_filled = new_operator_cell_filled

        return {
            "n_elites_before": n_before,
            "n_elites_after": len(new_cells),
            "n_collisions": n_collisions,
        }

    # ------------------------------------------------------------------
    # Snapshot / persistence (v0.5+ stub)
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a serializable snapshot of the archive (without the heavy
        genome_store; that lives in Postgres at production scale).

        Used for observability dashboards (per v7 §8 logging spec).
        """
        return {
            "n_cells_filled": self.n_cells_filled(),
            "operator_fill_count": self.operator_fill_count(),
            "operator_eval_count": self.operator_eval_count(),
            "operator_fill_efficiency": self.operator_fill_efficiency(),
            "elites": [
                {
                    "cell": e.cell_coordinate.to_tuple(),
                    "content_hash": e.content_hash,
                    "fitness": e.fitness.to_tuple(),
                    "operator": e.operator_class,
                    "n_evals": e.n_evaluations,
                }
                for e in self.all_elites()
            ],
        }
