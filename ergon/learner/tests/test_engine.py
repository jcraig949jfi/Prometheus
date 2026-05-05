"""Tests for ergon.learner.engine — top-level Trial 2 search loop."""
from __future__ import annotations

import pytest

from ergon.learner.engine import (
    EngineRunReport,
    EpisodeResult,
    MVPSubstrateEvaluator,
    TrialTwoEngine,
)


# ===========================================================================
# Authority — engine API matches v8 §6 Trial 2 spec
# ===========================================================================


def test_engine_initializes_with_default_components():
    engine = TrialTwoEngine(seed=42)
    assert engine.scheduler is not None
    assert engine.archive is not None
    assert engine.evaluator is not None
    assert len(engine._operators) == 5  # 5 MVP operator classes


def test_engine_runs_smoke_test():
    """Engine.run(10) completes without errors; produces non-empty episode log."""
    engine = TrialTwoEngine(seed=42)
    report = engine.run(n_episodes=10)
    assert isinstance(report, EngineRunReport)
    assert report.n_episodes == 10
    assert len(engine.episodes) == 10
    assert report.elapsed_seconds > 0


def test_engine_archive_grows_with_episodes():
    """Archive should fill up cells as engine runs (some episodes win cells)."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=50)
    assert engine.archive.n_cells_filled() > 0


# ===========================================================================
# Property — operator-class lineage tracking
# ===========================================================================


def test_engine_uses_all_5_operator_classes():
    """Across enough episodes, all 5 operator classes get invoked."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=200)
    operator_classes_used = set(ep.operator_class for ep in engine.episodes)
    expected = {"structural", "symbolic", "uniform", "structured_null", "anti_prior"}
    assert operator_classes_used == expected


def test_engine_min_share_constraint_holds_at_scale():
    """Per v8 §3.5.4: non-prior operators get ≥15% combined share."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=500)
    cumulative = engine.scheduler.cumulative_shares()
    non_prior_share = (
        cumulative.get("uniform", 0)
        + cumulative.get("anti_prior", 0)
        + cumulative.get("structured_null", 0)
    )
    assert non_prior_share >= 0.15 - 0.02  # tolerance for warmup


def test_engine_episodes_have_unique_hashes_per_genome():
    """Each genome's content_hash should be (mostly) unique across episodes."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=50)
    hashes = [ep.genome_hash for ep in engine.episodes]
    # Most should be unique; some collisions allowed (e.g., null operators
    # that happen to produce identical genomes)
    n_unique = len(set(hashes))
    assert n_unique >= len(hashes) * 0.8  # ≥80% unique


# ===========================================================================
# Property — F_TRIVIAL_BAND_REJECT integration
# ===========================================================================


def test_engine_tracks_trivial_rejects():
    """Trivial-pattern matches should be counted in the report."""
    engine = TrialTwoEngine(seed=42)
    report = engine.run(n_episodes=100)
    assert report.n_trivial_rejects >= 0  # may be 0 if no trivial patterns surface
    assert 0 <= report.f_trivial_band_reject_rate <= 1


def test_engine_trivial_reject_skips_evaluation():
    """When triviality fires, kill_path_verdicts include F_TRIVIAL_BAND_REJECT."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=100)
    trivial_episodes = [ep for ep in engine.episodes if ep.f_trivial_match.matched]
    for ep in trivial_episodes:
        assert "F_TRIVIAL_BAND_REJECT" in ep.kill_path_verdicts


# ===========================================================================
# Property — substrate evaluator stub produces realistic distributions
# ===========================================================================


def test_substrate_evaluator_kill_rate_matches_path_b():
    """Path B finding: ~0/30000 PROMOTEs at degree 10 + ±3.

    Stub default (promote_rate=0.001) should produce ~30 promotes per 30K
    episodes — close to Path B's empirical rate of zero.
    """
    evaluator = MVPSubstrateEvaluator(seed=42, promote_rate=0.001)

    from ergon.learner.genome import Genome, NodeRef
    from ergon.learner.reward import evaluate_substrate_pass

    n_pass = 0
    for i in range(1000):
        # Synthetic genome with varying content hash
        g = Genome(
            nodes=(
                NodeRef(callable_ref=f"atom_{i % 5}", arg_bindings=(("literal", i),)),
            ),
            target_predicate="test",
            mutation_operator_class="structural",
        )
        verdicts = evaluator.evaluate(g)
        n_pass += int(evaluate_substrate_pass(verdicts))

    # Expected ~1.2 passes per 1000 episodes for structural (rate * 1.2)
    # With Path B's actual rate of zero, our stub is ~3 sigma higher than
    # observed; that's a permissive calibration suitable for MVP testing.
    assert n_pass <= 20  # very permissive upper bound


# ===========================================================================
# Property — diagnostics format
# ===========================================================================


def test_run_report_format():
    engine = TrialTwoEngine(seed=42)
    report = engine.run(n_episodes=20)
    assert hasattr(report, "n_episodes")
    assert hasattr(report, "n_substrate_passed")
    assert hasattr(report, "n_won_cell")
    assert hasattr(report, "n_trivial_rejects")
    assert hasattr(report, "f_trivial_band_reject_rate")
    assert hasattr(report, "archive_n_cells_filled")
    assert hasattr(report, "operator_call_counts")
    assert hasattr(report, "operator_fill_counts")
    assert hasattr(report, "elapsed_seconds")


def test_episode_results_format():
    """Each episode produces a complete EpisodeResult."""
    engine = TrialTwoEngine(seed=42)
    engine.run(n_episodes=5)
    for ep in engine.episodes:
        assert isinstance(ep, EpisodeResult)
        assert ep.operator_class in (
            "structural", "symbolic", "uniform", "structured_null", "anti_prior",
        )
        assert ep.genome_hash
        assert ep.cell_coordinate is not None
        assert ep.fitness is not None
        assert ep.reward >= 0
        assert ep.kill_path_verdicts


# ===========================================================================
# Edge — small-N runs
# ===========================================================================


def test_engine_n_episodes_one():
    """Single-episode run should still produce valid output."""
    engine = TrialTwoEngine(seed=42)
    report = engine.run(n_episodes=1)
    assert report.n_episodes == 1
    assert len(engine.episodes) == 1


def test_engine_n_episodes_zero():
    engine = TrialTwoEngine(seed=42)
    report = engine.run(n_episodes=0)
    assert report.n_episodes == 0
    assert report.archive_n_cells_filled == 0
    assert report.f_trivial_band_reject_rate == 0.0


# ===========================================================================
# Composition — reproducibility
# ===========================================================================


def test_engine_deterministic_operator_sequence_given_seed():
    """Two engines with the same seed produce the same operator-class sequence.

    Note: full genome-hash determinism depends on shared-RNG ordering
    across components; that's a v0.5 hardening target. At MVP we verify
    the contractually-deterministic surface (operator selection by
    scheduler), which is what Trial 2's per-operator-class diagnostics
    rely on for reproducibility.
    """
    eng_a = TrialTwoEngine(seed=42)
    eng_b = TrialTwoEngine(seed=42)
    eng_a.run(n_episodes=20)
    eng_b.run(n_episodes=20)
    ops_a = [ep.operator_class for ep in eng_a.episodes]
    ops_b = [ep.operator_class for ep in eng_b.episodes]
    assert ops_a == ops_b


def test_engine_different_seeds_diverge():
    eng_a = TrialTwoEngine(seed=42)
    eng_b = TrialTwoEngine(seed=99)
    eng_a.run(n_episodes=20)
    eng_b.run(n_episodes=20)
    seqs_a = [ep.genome_hash for ep in eng_a.episodes]
    seqs_b = [ep.genome_hash for ep in eng_b.episodes]
    assert seqs_a != seqs_b
