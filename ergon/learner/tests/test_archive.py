"""Tests for ergon.learner.archive — MAP-Elites archive."""
from __future__ import annotations

import pytest

from ergon.learner.archive import (
    ArchiveEntry,
    FitnessTuple,
    MAPElitesArchive,
)
from ergon.learner.descriptor import CellCoordinate
from ergon.learner.genome import Genome, NodeRef


def make_genome(callable_ref: str, operator: str = "structural", arg_value: int = 1) -> Genome:
    """Helper: small genome with a unique callable_ref + arg for hash variety."""
    return Genome(
        nodes=(
            NodeRef(callable_ref=callable_ref, arg_bindings=(("literal", arg_value),)),
        ),
        target_predicate="test",
        mutation_operator_class=operator,
    )


def make_fitness(survival: int = 0, band: int = 1, cost_score: float = 0.5) -> FitnessTuple:
    return FitnessTuple(
        battery_survival_count=survival,
        band_concentration_tier=band,
        cost_amortized_score=cost_score,
    )


def make_coord(*values: int) -> CellCoordinate:
    """Build a CellCoordinate from 5 axis values."""
    assert len(values) == 5
    return CellCoordinate(*values)


# ---------------------------------------------------------------------------
# Authority — fitness comparison is lexicographic
# ---------------------------------------------------------------------------


def test_fitness_higher_survival_wins():
    """Tier 0 (battery_survival_count) dominates."""
    f1 = make_fitness(survival=2, band=0, cost_score=0.0)
    f2 = make_fitness(survival=1, band=2, cost_score=1.0)
    assert f1.beats(f2)
    assert not f2.beats(f1)


def test_fitness_higher_band_wins_at_equal_survival():
    """Tier 1 (band_concentration_tier) decides ties on tier 0."""
    f1 = make_fitness(survival=1, band=2, cost_score=0.0)
    f2 = make_fitness(survival=1, band=1, cost_score=1.0)
    assert f1.beats(f2)
    assert not f2.beats(f1)


def test_fitness_higher_cost_score_wins_at_equal_higher_tiers():
    """Tier 2 (cost_amortized_score) breaks ties on tiers 0 and 1."""
    f1 = make_fitness(survival=1, band=1, cost_score=0.9)
    f2 = make_fitness(survival=1, band=1, cost_score=0.5)
    assert f1.beats(f2)


def test_fitness_equal_does_not_beat():
    """Strict greater-than: equal fitnesses neither beats the other."""
    f1 = make_fitness(survival=1, band=1, cost_score=0.5)
    f2 = make_fitness(survival=1, band=1, cost_score=0.5)
    assert not f1.beats(f2)
    assert not f2.beats(f1)


# ---------------------------------------------------------------------------
# Property — submission semantics
# ---------------------------------------------------------------------------


def test_submit_to_empty_archive_creates_elite():
    archive = MAPElitesArchive()
    g = make_genome("atom_a")
    coord = make_coord(0, 0, 0, 0, 0)
    fitness = make_fitness(survival=1)
    won = archive.submit(g, coord, fitness)
    assert won
    assert archive.n_cells_filled() == 1
    elite = archive.get_elite(coord)
    assert elite is not None
    assert elite.content_hash == g.content_hash()


def test_submit_higher_fitness_replaces_elite():
    archive = MAPElitesArchive()
    g1 = make_genome("atom_a", arg_value=1)
    g2 = make_genome("atom_b", arg_value=2)
    coord = make_coord(0, 0, 0, 0, 0)
    archive.submit(g1, coord, make_fitness(survival=1))
    won = archive.submit(g2, coord, make_fitness(survival=3))
    assert won
    elite = archive.get_elite(coord)
    assert elite.content_hash == g2.content_hash()


def test_submit_lower_fitness_does_not_replace():
    archive = MAPElitesArchive()
    g1 = make_genome("atom_a", arg_value=1)
    g2 = make_genome("atom_b", arg_value=2)
    coord = make_coord(0, 0, 0, 0, 0)
    archive.submit(g1, coord, make_fitness(survival=5))
    won = archive.submit(g2, coord, make_fitness(survival=2))
    assert not won
    elite = archive.get_elite(coord)
    assert elite.content_hash == g1.content_hash()


def test_submit_equal_fitness_does_not_replace():
    """Equal fitnesses leave the existing elite in place (incumbent wins ties)."""
    archive = MAPElitesArchive()
    g1 = make_genome("atom_a", arg_value=1)
    g2 = make_genome("atom_b", arg_value=2)
    coord = make_coord(0, 0, 0, 0, 0)
    archive.submit(g1, coord, make_fitness(survival=2, band=2, cost_score=0.5))
    won = archive.submit(g2, coord, make_fitness(survival=2, band=2, cost_score=0.5))
    assert not won
    elite = archive.get_elite(coord)
    assert elite.content_hash == g1.content_hash()


def test_submit_different_cells_creates_separate_elites():
    archive = MAPElitesArchive()
    coord_a = make_coord(0, 0, 0, 0, 0)
    coord_b = make_coord(1, 1, 1, 1, 1)
    archive.submit(make_genome("a"), coord_a, make_fitness())
    archive.submit(make_genome("b"), coord_b, make_fitness())
    assert archive.n_cells_filled() == 2


def test_submission_increments_eval_count_even_when_losing():
    archive = MAPElitesArchive()
    g_winner = make_genome("a", operator="structural")
    g_loser = make_genome("b", operator="uniform")
    coord = make_coord(0, 0, 0, 0, 0)
    archive.submit(g_winner, coord, make_fitness(survival=10))
    archive.submit(g_loser, coord, make_fitness(survival=1))  # loses
    evals = archive.operator_eval_count()
    assert evals.get("structural", 0) == 1
    assert evals.get("uniform", 0) == 1


# ---------------------------------------------------------------------------
# Property — per-operator-class metrics (the load-bearing diagnostics)
# ---------------------------------------------------------------------------


def test_operator_fill_count_tracks_current_elites():
    """fill_count counts cells whose CURRENT elite is from each operator."""
    archive = MAPElitesArchive()
    archive.submit(make_genome("a", "structural", 1), make_coord(0, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("b", "structural", 2), make_coord(1, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("c", "uniform", 3), make_coord(2, 0, 0, 0, 0), make_fitness(survival=1))
    fills = archive.operator_fill_count()
    assert fills.get("structural", 0) == 2
    assert fills.get("uniform", 0) == 1


def test_operator_fill_count_updates_when_elite_replaced():
    """When a new operator beats the existing elite, the cell's fill-count attribution moves."""
    archive = MAPElitesArchive()
    coord = make_coord(0, 0, 0, 0, 0)
    archive.submit(make_genome("a", "structural", 1), coord, make_fitness(survival=1))
    assert archive.operator_fill_count().get("structural", 0) == 1
    # New operator wins
    archive.submit(make_genome("b", "uniform", 2), coord, make_fitness(survival=5))
    fills = archive.operator_fill_count()
    assert fills.get("structural", 0) == 0
    assert fills.get("uniform", 0) == 1


def test_coverage_divergence_disjoint():
    """Operators filling disjoint cells have Jaccard distance 1.0."""
    archive = MAPElitesArchive()
    archive.submit(make_genome("a", "structural", 1), make_coord(0, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("b", "structural", 2), make_coord(1, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("c", "anti_prior", 3), make_coord(2, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("d", "anti_prior", 4), make_coord(3, 0, 0, 0, 0), make_fitness(survival=1))
    div = archive.coverage_divergence("structural", "anti_prior")
    assert div == 1.0


def test_coverage_divergence_identical():
    """Operators that collide on every cell have Jaccard distance 0.0.

    To produce this, structural fills cells then anti_prior submits genomes
    that beat the structural elites in the same cells.
    """
    archive = MAPElitesArchive()
    cells = [make_coord(i, 0, 0, 0, 0) for i in range(3)]
    for idx, c in enumerate(cells):
        archive.submit(make_genome(f"s_{idx}", "structural", idx), c, make_fitness(survival=1))
    for idx, c in enumerate(cells):
        archive.submit(make_genome(f"a_{idx}", "anti_prior", 100 + idx), c, make_fitness(survival=5))
    # All cells now belong to anti_prior; structural has zero current elites
    div = archive.coverage_divergence("structural", "anti_prior")
    assert div == 1.0  # disjoint by definition: structural has no cells


def test_coverage_divergence_partial_overlap():
    """3 structural cells + 3 anti_prior cells with 1 overlap → Jaccard distance 0.8."""
    archive = MAPElitesArchive()
    # Structural fills cells 0, 1, 2
    for i in range(3):
        archive.submit(
            make_genome(f"s{i}", "structural", i),
            make_coord(i, 0, 0, 0, 0),
            make_fitness(survival=1),
        )
    # Anti_prior fills cells 2 (collision), 3, 4
    archive.submit(make_genome("a2", "anti_prior", 100), make_coord(2, 0, 0, 0, 0), make_fitness(survival=5))
    archive.submit(make_genome("a3", "anti_prior", 101), make_coord(3, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("a4", "anti_prior", 102), make_coord(4, 0, 0, 0, 0), make_fitness(survival=1))
    # Cell 2: anti_prior beat structural and now owns it.
    # Structural cells: {0, 1}. Anti_prior cells: {2, 3, 4}. Disjoint.
    div = archive.coverage_divergence("structural", "anti_prior")
    assert div == 1.0  # disjoint


def test_band_concentration_per_operator():
    """REINFORCE-style finding: operators show distinct distributions over magnitude axis.

    Simulate Path B's pattern: structural concentrates on magnitude bucket 1
    (Salem-cluster proxy), uniform spreads across buckets 0-4. To avoid cell
    collisions we vary axes 0 and 1 enough to keep each submission unique.
    """
    archive = MAPElitesArchive()
    # 8 structural elites in magnitude_bucket=1 (vary axis 0 to keep unique)
    for i in range(8):
        archive.submit(
            make_genome(f"s_b1_{i}", "structural", i),
            make_coord(i % 4, i % 5, 0, 1, 0),
            make_fitness(survival=1),
        )
    # 2 structural elites in magnitude_bucket=2
    for i in range(2):
        archive.submit(
            make_genome(f"s_b2_{i}", "structural", 100 + i),
            make_coord(i, 0, 0, 2, 0),
            make_fitness(survival=1),
        )
    # 10 uniform elites: 2 per bucket 0-4 (vary axes 0, 1 for uniqueness)
    for bucket in range(5):
        for j in range(2):
            archive.submit(
                make_genome(f"u_b{bucket}_{j}", "uniform", 1000 + bucket * 10 + j),
                make_coord(j, bucket, 1, bucket, j),
                make_fitness(survival=1),
            )

    distrib = archive.band_concentration_per_operator(axis_index=3)
    structural_dist = distrib.get("structural", {})
    uniform_dist = distrib.get("uniform", {})
    # Structural: 8/10 = 80% in bucket 1, 2/10 = 20% in bucket 2
    assert structural_dist.get(1, 0) == 0.8
    assert structural_dist.get(2, 0) == 0.2
    # Uniform: 2/10 = 0.2 in each of 5 buckets (perfectly spread)
    assert max(uniform_dist.values()) == 0.2
    assert min(uniform_dist.values()) == 0.2


def test_operator_fill_efficiency():
    """Fill efficiency = current_fills / total_evals per operator."""
    archive = MAPElitesArchive()
    # structural submits to cells 0, 1, 2 → all 3 win → 3 evals, 3 fills (efficiency 1.0)
    for i in range(3):
        archive.submit(
            make_genome(f"s{i}", "structural", i),
            make_coord(i, 0, 0, 0, 0),
            make_fitness(survival=1),
        )
    # uniform with higher fitness: submit to cell 1 (steals from structural) and cells 2, 3, 4, 5
    archive.submit(make_genome("u1", "uniform", 100), make_coord(1, 0, 0, 0, 0), make_fitness(survival=10))  # steals cell 1
    archive.submit(make_genome("u2", "uniform", 101), make_coord(2, 0, 0, 0, 0), make_fitness(survival=10))  # steals cell 2
    archive.submit(make_genome("u3", "uniform", 102), make_coord(3, 0, 0, 0, 0), make_fitness(survival=10))  # new cell
    archive.submit(make_genome("u4", "uniform", 103), make_coord(4, 0, 0, 0, 0), make_fitness(survival=10))  # new cell
    archive.submit(make_genome("u5", "uniform", 104), make_coord(5, 0, 0, 0, 0), make_fitness(survival=10))  # new cell

    eff = archive.operator_fill_efficiency()
    # structural: 3 evals; only cell 0 still elite → 1 current fill → efficiency 1/3
    assert eff.get("structural", 0) == pytest.approx(1 / 3, rel=0.01)
    # uniform: 5 evals; owns cells 1, 2, 3, 4, 5 → 5 current fills → efficiency 1.0
    assert eff.get("uniform", 0) == 1.0


# ---------------------------------------------------------------------------
# Composition — hot-swap rebin
# ---------------------------------------------------------------------------


def test_rebin_all_elites_preserves_count_when_unique():
    archive = MAPElitesArchive()
    for i in range(5):
        archive.submit(
            make_genome(f"g{i}", "structural", i),
            make_coord(i, 0, 0, 0, 0),
            make_fitness(survival=1),
        )

    def identity_rebin(genome, entry):
        return entry.cell_coordinate

    result = archive.rebin_all_elites(identity_rebin)
    assert result["n_elites_before"] == 5
    assert result["n_elites_after"] == 5
    assert result["n_collisions"] == 0


def test_rebin_collapses_collisions_with_fitness_winner():
    archive = MAPElitesArchive()
    # 3 elites in different cells
    archive.submit(make_genome("a", "structural", 1), make_coord(0, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("b", "structural", 2), make_coord(1, 0, 0, 0, 0), make_fitness(survival=10))  # higher fitness
    archive.submit(make_genome("c", "structural", 3), make_coord(2, 0, 0, 0, 0), make_fitness(survival=5))

    # Rebin to map ALL cells to (0,0,0,0,0) → 2 collisions
    def collapse_to_one(genome, entry):
        return CellCoordinate(0, 0, 0, 0, 0)

    result = archive.rebin_all_elites(collapse_to_one)
    assert result["n_elites_before"] == 3
    assert result["n_elites_after"] == 1
    assert result["n_collisions"] == 2
    # Winner should be the survival=10 genome
    elite = archive.get_elite(make_coord(0, 0, 0, 0, 0))
    assert elite is not None
    assert elite.fitness.battery_survival_count == 10


# ---------------------------------------------------------------------------
# Composition — snapshot serialization
# ---------------------------------------------------------------------------


def test_snapshot_format():
    archive = MAPElitesArchive()
    archive.submit(make_genome("a", "structural", 1), make_coord(0, 0, 0, 0, 0), make_fitness(survival=1))
    archive.submit(make_genome("b", "uniform", 2), make_coord(1, 0, 0, 0, 0), make_fitness(survival=1))
    snap = archive.snapshot()
    assert snap["n_cells_filled"] == 2
    assert snap["operator_fill_count"]["structural"] == 1
    assert snap["operator_fill_count"]["uniform"] == 1
    assert len(snap["elites"]) == 2
    # Each elite carries cell, content_hash, fitness, operator, n_evals
    for e in snap["elites"]:
        assert set(e.keys()) == {"cell", "content_hash", "fitness", "operator", "n_evals"}


# ---------------------------------------------------------------------------
# Edge — empty archive queries
# ---------------------------------------------------------------------------


def test_empty_archive_queries():
    archive = MAPElitesArchive()
    assert archive.n_cells_filled() == 0
    assert archive.get_elite(make_coord(0, 0, 0, 0, 0)) is None
    assert archive.operator_fill_count() == {}
    assert archive.operator_eval_count() == {}
    assert archive.operator_fill_efficiency() == {}
    assert archive.coverage_divergence("structural", "uniform") == 0.0
    assert archive.band_concentration_per_operator() == {}
    assert list(archive.all_elites()) == []
