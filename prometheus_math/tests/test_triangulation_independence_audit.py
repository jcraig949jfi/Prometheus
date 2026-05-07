"""Tests for prometheus_math.triangulation_independence_audit (T-2026-05-07-T009)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from prometheus_math.kill_vector import KillComponent, KillVector
from prometheus_math.triangulation_independence_audit import (
    DEFAULT_FLAG_THRESHOLD_BITS,
    DEFAULT_N_NULL_SHUFFLES,
    AuditResult,
    PairMI,
    load_kill_vectors_from_pilot_store,
    render_report,
    run_audit,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _kv(triggered_names: List[str], hash_: str = "h") -> KillVector:
    """Build a KillVector with the given falsifier names triggered."""
    comps = tuple(
        KillComponent(falsifier_name=n, triggered=True)
        for n in triggered_names
    )
    return KillVector(components=comps, candidate_hash=hash_)


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------


class TestEmptyInput:
    def test_empty_corpus_returns_empty_audit(self):
        result = run_audit([])
        assert result.n_records == 0
        assert result.n_active_components == 0
        assert result.pair_results == ()
        assert result.top_10 == ()
        assert result.flagged == ()


# ---------------------------------------------------------------------------
# Independence: independent components should give corrected MI ~0
# ---------------------------------------------------------------------------


class TestIndependenceProduces0BitsAfterCorrection:
    def test_independent_components_corrected_mi_near_zero(self):
        """Build a corpus where two components are exactly independent
        (each fires with marginal 0.5 by separate random sampling).
        Bias-corrected MI should be ~0."""
        import random
        rng = random.Random(123)
        N = 2000
        vectors: List[KillVector] = []
        for i in range(N):
            triggered = []
            if rng.random() < 0.5:
                triggered.append("F1_permutation_null")
            if rng.random() < 0.5:
                triggered.append("F6_base_rate")
            vectors.append(_kv(triggered, hash_=f"h{i}"))
        result = run_audit(vectors, n_null_shuffles=20, seed=42)
        # Find the F1 <-> F6 pair
        target_pair = None
        for row in result.pair_results:
            if {row.component_a, row.component_b} == {
                "F1_permutation_null", "F6_base_rate"
            }:
                target_pair = row
                break
        assert target_pair is not None, (
            "F1<->F6 pair not in result; active: "
            f"{[(r.component_a, r.component_b) for r in result.pair_results]}"
        )
        # The bias-corrected MI should be small in magnitude (within ~0.05
        # bits with N=2000).
        assert abs(target_pair.bias_corrected_mi_bits) < 0.05, (
            f"independent components have non-trivial corrected MI: "
            f"{target_pair.bias_corrected_mi_bits:.4f} bits"
        )
        assert not target_pair.flagged


# ---------------------------------------------------------------------------
# Dependence: perfectly co-occurring components should be flagged
# ---------------------------------------------------------------------------


class TestPerfectCoOccurrenceIsFlagged:
    def test_perfectly_correlated_components_flagged_above_threshold(self):
        """Two components that always co-fire OR always co-don't-fire
        across the corpus have MI ~ 1 bit (when each fires with marginal
        ~0.5). Should be flagged with default threshold = 0.3 bits."""
        N = 1000
        vectors: List[KillVector] = []
        for i in range(N):
            if i % 2 == 0:
                # Both fire
                vectors.append(_kv(["F1_permutation_null", "F6_base_rate"], hash_=f"h{i}"))
            else:
                # Neither fires
                vectors.append(_kv([], hash_=f"h{i}"))
        result = run_audit(vectors, n_null_shuffles=20, seed=42)
        target_pair = None
        for row in result.pair_results:
            if {row.component_a, row.component_b} == {
                "F1_permutation_null", "F6_base_rate"
            }:
                target_pair = row
                break
        assert target_pair is not None
        # Perfect correlation => corrected MI close to 1 bit (since each
        # fires marginal 0.5).
        assert target_pair.bias_corrected_mi_bits > 0.5, (
            f"perfectly correlated pair has corrected MI "
            f"{target_pair.bias_corrected_mi_bits:.4f} bits; expected > 0.5"
        )
        assert target_pair.flagged
        assert target_pair.n_both_triggered == N // 2


# ---------------------------------------------------------------------------
# Threshold behavior
# ---------------------------------------------------------------------------


class TestThresholdRespected:
    def test_high_threshold_unflags_all(self):
        """A 10-bit threshold should unflag everything (MI is bounded by
        log2(2)=1 bit for boolean pairs)."""
        N = 500
        vectors: List[KillVector] = []
        for i in range(N):
            triggered = []
            if i % 3 == 0:
                triggered.append("F1_permutation_null")
            if i % 3 == 1:
                triggered.append("F6_base_rate")
            vectors.append(_kv(triggered, hash_=f"h{i}"))
        result = run_audit(vectors, threshold_bits=10.0, n_null_shuffles=10, seed=0)
        assert all(not r.flagged for r in result.pair_results)
        assert result.flagged == ()

    def test_zero_threshold_flags_everything_with_positive_corrected_mi(self):
        """Threshold 0 flags any pair whose corrected MI > 0."""
        N = 200
        vectors = [_kv(["F1_permutation_null", "F6_base_rate"], hash_=f"h{i}") for i in range(N)]
        # Both always fire => marginals are 1.0 (degenerate), so MI = 0 by
        # construction. Mix in some non-firing records so marginals are
        # non-degenerate.
        vectors.extend([_kv([], hash_=f"hb{i}") for i in range(N)])
        result = run_audit(vectors, threshold_bits=0.0, n_null_shuffles=10, seed=0)
        # The F1<->F6 pair has perfect coupling.
        flagged_names = {(r.component_a, r.component_b) for r in result.flagged}
        assert any(
            {"F1_permutation_null", "F6_base_rate"} == set(pair)
            for pair in flagged_names
        )


# ---------------------------------------------------------------------------
# Top-10 ordering
# ---------------------------------------------------------------------------


class TestTop10OrderedDescending:
    def test_top_10_sorted_by_bias_corrected_mi_descending(self):
        """top_10 must be sorted by bias_corrected_mi_bits descending."""
        N = 500
        vectors: List[KillVector] = []
        # Mix some independent + some correlated pairs.
        import random
        rng = random.Random(7)
        for i in range(N):
            triggered = []
            # Strong correlation: F1 and F6 co-fire most of the time
            if rng.random() < 0.5:
                triggered.append("F1_permutation_null")
                triggered.append("F6_base_rate")
            # Independent: F9 has independent marginal
            if rng.random() < 0.3:
                triggered.append("F9_simpler_explanation")
            # Mix in v2 components
            if rng.random() < 0.2:
                triggered.append("relativizes")
            vectors.append(_kv(triggered, hash_=f"h{i}"))
        result = run_audit(vectors, n_null_shuffles=15, seed=42)
        scores = [r.bias_corrected_mi_bits for r in result.top_10]
        assert scores == sorted(scores, reverse=True), (
            f"top_10 not sorted descending: {scores}"
        )
        assert len(result.top_10) <= 10


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_seed_same_result(self):
        """Two runs with the same seed must produce identical results."""
        N = 300
        import random
        rng = random.Random(99)
        vectors = []
        for i in range(N):
            triggered = []
            if rng.random() < 0.4:
                triggered.append("F1_permutation_null")
            if rng.random() < 0.6:
                triggered.append("F6_base_rate")
            vectors.append(_kv(triggered, hash_=f"h{i}"))
        result_a = run_audit(vectors, n_null_shuffles=15, seed=12345)
        result_b = run_audit(vectors, n_null_shuffles=15, seed=12345)
        assert result_a.n_records == result_b.n_records
        # Compare pair-by-pair
        rows_a = sorted(result_a.pair_results, key=lambda r: (r.component_a, r.component_b))
        rows_b = sorted(result_b.pair_results, key=lambda r: (r.component_a, r.component_b))
        assert len(rows_a) == len(rows_b)
        for a, b in zip(rows_a, rows_b):
            assert a.component_a == b.component_a
            assert a.component_b == b.component_b
            assert a.observed_mi_bits == b.observed_mi_bits
            assert a.null_mi_mean_bits == b.null_mi_mean_bits


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class TestPilotStoreLoader:
    def test_loader_reconstructs_kill_vectors(self, tmp_path: Path):
        """Build a tiny pilot-store-shaped JSON, load it, verify shapes."""
        kv_a = _kv(["F1_permutation_null"], hash_="ha")
        kv_b = _kv(["F6_base_rate", "F9_simpler_explanation"], hash_="hb")
        store = {
            "pilot": {
                "episodes": [
                    {"episode_idx": 0, "kill_vector": kv_a.to_dict()},
                    {"episode_idx": 1, "kill_vector": kv_b.to_dict()},
                    # Episode without kill_vector should be silently skipped
                    {"episode_idx": 2},
                ]
            }
        }
        path = tmp_path / "synth_store.json"
        path.write_text(json.dumps(store), encoding="utf-8")
        loaded = load_kill_vectors_from_pilot_store(path)
        assert len(loaded) == 2
        names_a = {c.falsifier_name for c in loaded[0].components if c.triggered}
        names_b = {c.falsifier_name for c in loaded[1].components if c.triggered}
        assert names_a == {"F1_permutation_null"}
        assert names_b == {"F6_base_rate", "F9_simpler_explanation"}

    def test_loader_rejects_unknown_schema(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"unexpected": "shape"}), encoding="utf-8")
        with pytest.raises(ValueError, match="unexpected store schema"):
            load_kill_vectors_from_pilot_store(path)

    def test_loader_rejects_non_list_episodes(self, tmp_path: Path):
        path = tmp_path / "bad2.json"
        path.write_text(
            json.dumps({"pilot": {"episodes": "not a list"}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="pilot.episodes shape"):
            load_kill_vectors_from_pilot_store(path)


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


class TestReportRendering:
    def test_empty_audit_renders_no_active_pairs_message(self):
        empty = AuditResult(
            n_records=0,
            n_active_components=0,
            threshold_bits=0.3,
            n_null_shuffles=50,
            pair_results=(),
            top_10=(),
            flagged=(),
            elapsed_s=0.0,
        )
        md = render_report(empty)
        assert "TriangulationProtocol Independence Audit Results" in md
        assert "No Active Pairs" in md
        assert "Audit cannot proceed without input data" in md

    def test_populated_audit_renders_top_10_table(self):
        rows = (
            PairMI(
                component_a="F1_permutation_null",
                component_b="F6_base_rate",
                observed_mi_bits=0.8,
                null_mi_mean_bits=0.05,
                null_mi_std_bits=0.01,
                bias_corrected_mi_bits=0.75,
                n_a_triggered=100,
                n_b_triggered=120,
                n_both_triggered=80,
                flagged=True,
            ),
        )
        ar = AuditResult(
            n_records=200,
            n_active_components=2,
            threshold_bits=0.3,
            n_null_shuffles=50,
            pair_results=rows,
            top_10=rows,
            flagged=rows,
            elapsed_s=1.23,
        )
        md = render_report(ar)
        assert "Top-10 Highest Bias-Corrected MI" in md
        assert "F1_permutation_null" in md
        assert "F6_base_rate" in md
        assert "0.7500" in md  # bias-corrected
        assert "FLAG" in md
        assert "Flagged Pairs" in md
        assert "1 pair(s) exceed" in md
        assert "Caveats" in md

    def test_no_flagged_pairs_message_correct(self):
        rows = (
            PairMI(
                component_a="a", component_b="b",
                observed_mi_bits=0.1, null_mi_mean_bits=0.05,
                null_mi_std_bits=0.01, bias_corrected_mi_bits=0.05,
                n_a_triggered=10, n_b_triggered=10, n_both_triggered=2,
                flagged=False,
            ),
        )
        ar = AuditResult(
            n_records=50, n_active_components=2,
            threshold_bits=0.3, n_null_shuffles=50,
            pair_results=rows, top_10=rows, flagged=(),
            elapsed_s=0.5,
        )
        md = render_report(ar)
        assert "No component pairs exceeded" in md
        assert "consistent with the observed corpus" in md


# ---------------------------------------------------------------------------
# Acceptance #4 — top-10 limit is respected
# ---------------------------------------------------------------------------


class TestTop10Limit:
    def test_top_10_capped_at_10_entries(self):
        """Even with more than 10 active pairs, top_10 has at most 10 entries."""
        N = 500
        import random
        rng = random.Random(13)
        vectors: List[KillVector] = []
        # Trigger 6 different components with varied marginals -> 15 pairs.
        names = [
            "F1_permutation_null", "F6_base_rate", "F9_simpler_explanation",
            "F11_cross_validation", "out_of_band", "reciprocity",
        ]
        for i in range(N):
            triggered = [n for n in names if rng.random() < 0.4]
            vectors.append(_kv(triggered, hash_=f"h{i}"))
        result = run_audit(vectors, n_null_shuffles=10, seed=0)
        assert len(result.top_10) <= 10
        assert len(result.pair_results) >= len(result.top_10)
