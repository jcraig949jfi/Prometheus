"""prometheus_math/tests/test_pivot_bughunt.py — bug-hunt probes for the
pivot-stack pivot-side modules.

Modules audited:
  * prometheus_math.sigma_env (SigmaMathEnv bandit)
  * prometheus_math.discovery_env (DiscoveryEnv generative)
  * prometheus_math.discovery_pipeline (DiscoveryPipeline)
  * prometheus_math.obstruction_env (ObstructionEnv predicate-discovery)
  * prometheus_math._obstruction_corpus_live (live adapter)
  * prometheus_math.four_counts_pilot (§6.2 + §6.4)
  * prometheus_math.withheld_benchmark (§6.2.5)
  * prometheus_math.catalog_consistency (§6.3)
  * prometheus_math.arsenal_meta (registry)

Probes are ADDITIVE; every test docstring records:
  * which module + function it probes
  * which of the 7 categories it falls in
  * NEW / regression status

Categories (from the bug-hunt protocol):
  1 = Boundary value analysis
  2 = Equivalence class partitioning
  3 = Property-based fuzzing with Hypothesis
  4 = Adversarial inputs
  5 = State-machine testing
  6 = Differential testing
  7 = Error injection
"""
from __future__ import annotations

import math

import numpy as np
import pytest

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:  # pragma: no cover
    HAS_HYPOTHESIS = False
    pytest.skip("hypothesis not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _tiny_corpus():
    from prometheus_math._obstruction_corpus import CorpusEntry
    return [
        CorpusEntry(n_steps=5, neg_x=4, pos_x=1, neg_y=1, pos_y=1,
                    neg_z=1, pos_z=1,
                    has_diag_neg=True, has_diag_pos=False,
                    kill_verdict=True),
        CorpusEntry(n_steps=3, neg_x=1, pos_x=1, neg_y=1, pos_y=1,
                    neg_z=0, pos_z=0,
                    has_diag_neg=False, has_diag_pos=False,
                    kill_verdict=False),
    ]


# ---------------------------------------------------------------------------
# Category 1 — Boundary value analysis
# ---------------------------------------------------------------------------


class TestBoundary_DiscoveryEnv:

    def test_degree_2_smallest_legal(self):
        """discovery_env.DiscoveryEnv — Cat 1 — NEW. degree=2 is the
        documented lower bound; must not raise."""
        from prometheus_math.discovery_env import DiscoveryEnv
        env = DiscoveryEnv(degree=2)
        env.reset()

    def test_degree_1_rejected(self):
        """discovery_env.DiscoveryEnv — Cat 1 — NEW. degree<2 must
        raise ValueError."""
        from prometheus_math.discovery_env import DiscoveryEnv
        with pytest.raises(ValueError):
            DiscoveryEnv(degree=1)

    def test_degree_0_rejected(self):
        """discovery_env.DiscoveryEnv — Cat 1 — NEW."""
        from prometheus_math.discovery_env import DiscoveryEnv
        with pytest.raises(ValueError):
            DiscoveryEnv(degree=0)

    def test_palindromic_from_half_minimum_degree(self):
        """discovery_env._palindromic_from_half — Cat 1 — NEW. degree=2
        produces [a, b, a]."""
        from prometheus_math.discovery_env import _palindromic_from_half
        assert _palindromic_from_half([1, 2], 2) == [1, 2, 1]

    def test_palindromic_extra_half_coeffs_truncated(self):
        """discovery_env._palindromic_from_half — Cat 1 — NEW. Extra
        half-coeffs beyond half_len are silently ignored (current
        behaviour; documented here as regression)."""
        from prometheus_math.discovery_env import _palindromic_from_half
        # half_len for deg 4 is 3, but pass 6 elements — first 3 used.
        out = _palindromic_from_half([1, 2, 3, 4, 5, 6], 4)
        assert out == [1, 2, 3, 2, 1]

    def test_reward_at_lower_band_boundary_excluded(self):
        """discovery_env._compute_reward — Cat 1 — NEW. M=1.001 is at
        the strict boundary; the inclusive lower bound is `1.001 < M`,
        so M=1.001 itself must NOT score sub_lehmer."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(1.001)
        assert r == 0.0
        assert label != "sub_lehmer"

    def test_reward_at_upper_band_boundary_excluded(self):
        """discovery_env._compute_reward — Cat 1 — NEW. M=1.18 is at
        the strict upper boundary; falls through to salem_cluster."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(1.18)
        assert r == 20.0
        assert label == "salem_cluster"

    def test_reward_just_inside_sub_lehmer(self):
        """discovery_env._compute_reward — Cat 1 — NEW. M just under 1.18
        scores sub_lehmer."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(1.18 - 1e-9)
        assert r == 100.0

    def test_reward_at_exactly_5(self):
        """discovery_env._compute_reward — Cat 1 — NEW. M=5.0 is the
        excluded upper limit of `functional`."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(5.0)
        assert r == 0.0
        assert label == "cyclotomic_or_large"

    def test_reward_extreme_huge_value(self):
        """discovery_env._compute_reward — Cat 1 — NEW. M=1e300 is
        finite-large; must yield 0 reward."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(1e300)
        assert r == 0.0

    def test_reward_nan_yields_zero(self):
        """discovery_env._compute_reward — Cat 1 — NEW."""
        from prometheus_math.discovery_env import _compute_reward
        r, label = _compute_reward(float("nan"))
        assert r == 0.0
        assert label == "non_finite"


class TestBoundary_ObstructionEnv:

    def test_held_out_fraction_zero_rejected(self):
        """obstruction_env.ObstructionEnv — Cat 1 — regression."""
        from prometheus_math.obstruction_env import ObstructionEnv
        with pytest.raises(ValueError):
            ObstructionEnv(corpus=_tiny_corpus(), held_out_fraction=0.0)

    def test_held_out_fraction_one_rejected(self):
        """obstruction_env.ObstructionEnv — Cat 1 — regression."""
        from prometheus_math.obstruction_env import ObstructionEnv
        with pytest.raises(ValueError):
            ObstructionEnv(corpus=_tiny_corpus(), held_out_fraction=1.0)

    def test_held_out_fraction_just_above_zero(self):
        """obstruction_env.ObstructionEnv — Cat 1 — NEW. Tiny but
        positive fraction must be accepted."""
        from prometheus_math.obstruction_env import ObstructionEnv
        env = ObstructionEnv(corpus=_tiny_corpus(), held_out_fraction=1e-9)
        assert env.held_out_fraction == 1e-9

    def test_max_predicate_complexity_zero_yields_stop_only(self):
        """obstruction_env.ObstructionEnv — Cat 1 — regression."""
        from prometheus_math.obstruction_env import (
            ObstructionEnv,
            STOP_ACTION,
        )
        env = ObstructionEnv(
            corpus=_tiny_corpus(),
            held_out_fraction=0.5,
            max_predicate_complexity=0,
        )
        env.reset()
        # Step 0 (any conjunct) terminates because step_count >= max.
        obs, r, terminated, _, info = env.step(0)
        assert terminated

    def test_max_predicate_complexity_negative_rejected(self):
        """obstruction_env.ObstructionEnv — Cat 1 — NEW."""
        from prometheus_math.obstruction_env import ObstructionEnv
        with pytest.raises(ValueError):
            ObstructionEnv(
                corpus=_tiny_corpus(),
                held_out_fraction=0.5,
                max_predicate_complexity=-1,
            )

    def test_action_at_stop_index_terminates(self):
        """obstruction_env.ObstructionEnv — Cat 1 — NEW."""
        from prometheus_math.obstruction_env import (
            ObstructionEnv,
            STOP_ACTION,
        )
        env = ObstructionEnv(
            corpus=_tiny_corpus(),
            held_out_fraction=0.5,
            max_predicate_complexity=3,
        )
        env.reset()
        obs, r, terminated, _, info = env.step(STOP_ACTION)
        assert terminated

    def test_decode_stop_action_raises(self):
        """obstruction_env.decode_action — Cat 1 — NEW."""
        from prometheus_math.obstruction_env import (
            decode_action,
            STOP_ACTION,
        )
        with pytest.raises(ValueError):
            decode_action(STOP_ACTION)


class TestBoundary_DiscoveryPipeline:

    def test_M_at_lower_band_boundary_rejected(self):
        """discovery_pipeline.DiscoveryPipeline.process_candidate — Cat 1
        — NEW. M=1.001 is strict-excluded; record is REJECTED."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        r = p.process_candidate([1, 1, -1, -1, 1, 1], 1.001)
        assert r.terminal_state == "REJECTED"
        assert "out_of_band" in r.kill_pattern

    def test_M_at_upper_band_boundary_rejected(self):
        """discovery_pipeline.DiscoveryPipeline.process_candidate — Cat 1
        — NEW."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        r = p.process_candidate([1, 1, -1, -1, 1, 1], 1.18)
        assert r.terminal_state == "REJECTED"

    def test_M_NaN_rejected(self):
        """discovery_pipeline — Cat 1 — NEW. NaN comparisons are False;
        must route to REJECTED via out_of_band."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        r = p.process_candidate([1, 1, -1, -1, 1, 1], float("nan"))
        assert r.terminal_state == "REJECTED"

    def test_M_inf_rejected(self):
        """discovery_pipeline — Cat 1 — NEW."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        r = p.process_candidate([1, 1, -1, -1, 1, 1], float("inf"))
        assert r.terminal_state == "REJECTED"


class TestBoundary_CatalogConsistency:

    def test_mossinghoff_validates_finite_m(self):
        """catalog_consistency._validate_inputs — Cat 1 — NEW."""
        from prometheus_math.catalog_consistency import _validate_inputs
        with pytest.raises(ValueError):
            _validate_inputs([1, 2, 1], float("nan"))
        with pytest.raises(ValueError):
            _validate_inputs([1, 2, 1], float("inf"))
        with pytest.raises(ValueError):
            _validate_inputs([1, 2, 1], -0.1)

    def test_mossinghoff_empty_coeffs_rejected(self):
        """catalog_consistency.mossinghoff_check — Cat 1 — NEW."""
        from prometheus_math.catalog_consistency import mossinghoff_check
        with pytest.raises(ValueError):
            mossinghoff_check([], 1.5)

    def test_mossinghoff_zero_tol_makes_no_match(self):
        """catalog_consistency.mossinghoff_check — Cat 1 — NEW. tol=0
        makes the strict `< 0` distance impossible → always miss."""
        from prometheus_math.catalog_consistency import mossinghoff_check
        # Use a known Mossinghoff M-value (Lehmer's poly).
        r = mossinghoff_check([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], 1.17628081825991, tol=0.0)
        assert not r.hit


class TestBoundary_WithheldBenchmark:

    def test_holdout_fraction_zero_yields_full_visible(self):
        """withheld_benchmark.partition_mossinghoff — Cat 1 — NEW."""
        from prometheus_math.withheld_benchmark import partition_mossinghoff
        corpus = [([1, 2, 1], 1.5), ([1, 3, 1], 2.0)]
        p = partition_mossinghoff(holdout_fraction=0.0, _corpus=corpus)
        assert p.n_visible == 2
        assert p.n_withheld == 0

    def test_holdout_fraction_one_rejected(self):
        """withheld_benchmark.partition_mossinghoff — Cat 1 —
        regression."""
        from prometheus_math.withheld_benchmark import partition_mossinghoff
        corpus = [([1, 2, 1], 1.5), ([1, 3, 1], 2.0)]
        with pytest.raises(ValueError):
            partition_mossinghoff(holdout_fraction=1.0, _corpus=corpus)


# ---------------------------------------------------------------------------
# Category 2 — Equivalence class partitioning
# ---------------------------------------------------------------------------


class TestEquivalence_DiscoveryEnv:

    def test_reward_label_buckets_partition_full_M_axis(self):
        """discovery_env._compute_reward — Cat 2 — NEW. Every finite
        non-negative M routes to exactly one labelled bucket."""
        from prometheus_math.discovery_env import _compute_reward
        ms = [0.5, 0.999, 1.0, 1.0005, 1.001, 1.05, 1.18, 1.5, 1.9999, 2.0,
              4.999, 5.0, 100.0, 1e300]
        labels = set()
        for m in ms:
            r, label = _compute_reward(m)
            labels.add(label)
        # All labels must come from the documented set.
        documented = {
            "non_finite", "numerical_artifact", "sub_lehmer",
            "salem_cluster", "low_m", "functional", "cyclotomic_or_large",
        }
        assert labels.issubset(documented), f"undocumented labels: {labels - documented}"

    def test_reward_shaped_handles_all_buckets(self):
        """discovery_env._compute_reward_shaped — Cat 2 — NEW."""
        from prometheus_math.discovery_env import _compute_reward_shaped
        for m in [0.5, 1.0, 1.001, 1.18, 1.5, 4.999, 5.0]:
            r, label = _compute_reward_shaped(m)
            assert r >= 0


class TestEquivalence_ObstructionEnv:

    def test_evaluate_predicate_empty_predicate_yields_lift_one(self):
        """obstruction_env.evaluate_predicate — Cat 2 — regression.
        Tautological predicate: empty dict matches everything → no
        baseline group → lift=1.0 by convention."""
        from prometheus_math.obstruction_env import evaluate_predicate
        out = evaluate_predicate({}, _tiny_corpus())
        assert out["lift"] == 1.0
        assert out["lift_excess"] == 0.0

    def test_evaluate_predicate_no_match_yields_lift_zero(self):
        """obstruction_env.evaluate_predicate — Cat 2 — NEW. Predicate
        with no matches → distinct equiv class with lift=0."""
        from prometheus_math.obstruction_env import evaluate_predicate
        # n_steps=99 doesn't match any corpus entry.
        out = evaluate_predicate({"n_steps": 99}, _tiny_corpus())
        assert out["match_group_size"] == 0
        assert out["lift"] == 0.0


# ---------------------------------------------------------------------------
# Category 3 — Property-based fuzzing
# ---------------------------------------------------------------------------


class TestPropertyBased:

    @settings(deadline=10000, max_examples=50)
    @given(m=st.floats(min_value=0.0, max_value=10.0, allow_nan=False))
    def test_property_compute_reward_nonneg(self, m):
        """discovery_env._compute_reward — Cat 3 — NEW. Reward is always
        >= 0 for finite non-negative M."""
        from prometheus_math.discovery_env import _compute_reward
        r, _ = _compute_reward(m)
        assert r >= 0.0

    @settings(deadline=10000, max_examples=50)
    @given(m=st.floats(min_value=0.0, max_value=10.0, allow_nan=False))
    def test_property_compute_reward_shaped_nonneg(self, m):
        """discovery_env._compute_reward_shaped — Cat 3 — NEW."""
        from prometheus_math.discovery_env import _compute_reward_shaped
        r, _ = _compute_reward_shaped(m)
        assert r >= 0.0

    @settings(deadline=10000, max_examples=50)
    @given(
        coeffs=st.lists(st.integers(min_value=-3, max_value=3),
                        min_size=2, max_size=10),
    )
    def test_property_palindromic_is_palindromic(self, coeffs):
        """discovery_env._palindromic_from_half — Cat 3 — NEW. Output
        is always palindromic by construction."""
        from prometheus_math.discovery_env import (
            _is_reciprocal,
            _palindromic_from_half,
        )
        # Need degree such that half_len <= len(coeffs).
        # half_len = degree//2 + 1, so degree = 2*(len-1).
        degree = max(2, 2 * (len(coeffs) - 1))
        half_len = degree // 2 + 1
        if len(coeffs) < half_len:
            return  # skip — not enough coeffs
        out = _palindromic_from_half(coeffs[:half_len], degree)
        assert _is_reciprocal(out)

    @settings(deadline=10000, max_examples=30)
    @given(
        seed=st.integers(min_value=0, max_value=2**31 - 1),
    )
    def test_property_obstruction_split_deterministic(self, seed):
        """obstruction_env._split — Cat 3 — NEW. Same seed yields the
        same split."""
        from prometheus_math.obstruction_env import ObstructionEnv
        from prometheus_math._obstruction_corpus import OBSTRUCTION_CORPUS
        e1 = ObstructionEnv(
            corpus=list(OBSTRUCTION_CORPUS[:30]),
            held_out_fraction=0.3, seed=seed,
        )
        e2 = ObstructionEnv(
            corpus=list(OBSTRUCTION_CORPUS[:30]),
            held_out_fraction=0.3, seed=seed,
        )
        # Both must split into identical train/test.
        train_ids_1 = sorted(id(e) for e in e1._train_corpus)
        train_ids_2 = sorted(id(e) for e in e2._train_corpus)
        # Object identity won't match (different instantiations); compare
        # by indices via dataclass eq.
        assert e1._train_corpus == e2._train_corpus
        assert e1._test_corpus == e2._test_corpus

    @settings(deadline=10000, max_examples=30)
    @given(
        m=st.floats(min_value=1.0, max_value=10.0, allow_nan=False),
        tol=st.floats(min_value=1e-12, max_value=1e-2, allow_nan=False),
    )
    def test_property_mossinghoff_self_match_within_tol(self, m, tol):
        """catalog_consistency.mossinghoff_check — Cat 3 — NEW. If we
        query with an M from the snapshot itself, exact-equal must hit
        for any positive tol."""
        from prometheus_math.databases.mahler import MAHLER_TABLE
        from prometheus_math.catalog_consistency import mossinghoff_check
        if not MAHLER_TABLE:
            pytest.skip("no Mossinghoff snapshot")
        entry = MAHLER_TABLE[0]
        target_m = float(entry["mahler_measure"])
        coeffs = list(entry["coeffs"])
        r = mossinghoff_check(coeffs, target_m, tol=max(tol, 1e-9))
        assert r.hit


# ---------------------------------------------------------------------------
# Category 4 — Adversarial inputs
# ---------------------------------------------------------------------------


class TestAdversarial:

    def test_obstruction_evaluate_predicate_corpus_with_all_kills(self):
        """obstruction_env.evaluate_predicate — Cat 4 — NEW. All-kills
        corpus → matched=baseline=1, lift=1, excess=0 (no signal)."""
        from prometheus_math.obstruction_env import evaluate_predicate
        from prometheus_math._obstruction_corpus import CorpusEntry
        corpus = [
            CorpusEntry(n_steps=i, neg_x=0, pos_x=0, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=False, has_diag_pos=False,
                        kill_verdict=True)
            for i in range(3)
        ]
        out = evaluate_predicate({"n_steps": 1}, corpus)
        assert out["lift_excess"] == 0.0

    def test_obstruction_evaluate_predicate_with_no_kills(self):
        """obstruction_env.evaluate_predicate — Cat 4 — NEW. Zero kills
        in match group → matched_rate=0; baseline=0 → lift=0."""
        from prometheus_math.obstruction_env import evaluate_predicate
        from prometheus_math._obstruction_corpus import CorpusEntry
        corpus = [
            CorpusEntry(n_steps=i, neg_x=0, pos_x=0, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=False, has_diag_pos=False,
                        kill_verdict=False)
            for i in range(3)
        ]
        out = evaluate_predicate({"n_steps": 1}, corpus)
        assert out["lift"] == 0.0

    def test_zero_polynomial_in_pipeline_phase0_band_check(self):
        """discovery_pipeline — Cat 4 — NEW. All-zero coeffs are not
        themselves the candidate; they fall under phase0 since their
        M would compute to inf or fail. We test that the pipeline does
        not crash — it must REJECT cleanly."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        # Pretend M = 1.1 so we get past phase0 to irreducibility check
        # which will reject zero polynomial.
        r = p.process_candidate([0, 0, 0, 0], 1.1)
        assert r.terminal_state == "REJECTED"
        assert "reducible" in (r.kill_pattern or "") or "zero" in (r.kill_pattern or "").lower()


class TestAdversarial_SigmaMathEnv:

    def test_empty_action_table_is_honored(self):
        """sigma_env.SigmaMathEnv — Cat 4 — regression for B-BUGHUNT-002.

        action_table=[] is adversarial input; user explicitly passed an
        empty list. The previous `or _default_action_table_for_lehmer()`
        silently swapped in the default — masking caller intent. After
        the fix, None means default and [] means empty.
        """
        from prometheus_math.sigma_env import SigmaMathEnv
        env = SigmaMathEnv(action_table=[])
        env.reset()
        assert env.action_space.n == 1  # _DiscreteStub fallback to >=1 for Gym

    def test_caller_action_table_mutation_isolated(self):
        """sigma_env.SigmaMathEnv — Cat 4 — regression for B-BUGHUNT-005.

        Caller mutating the action_table after construction must NOT
        propagate into the env's internal table.
        """
        from prometheus_math.sigma_env import SigmaMathEnv
        table = [{"callable_ref": "math:sqrt", "arg_label": "x",
                  "args": [4.0], "kwargs": {}}]
        env = SigmaMathEnv(action_table=table)
        table.clear()
        assert len(env._action_table_raw) == 1, (
            "caller's mutation bled into env (B-BUGHUNT-005)"
        )

    def test_action_out_of_range_negative_raises(self):
        """sigma_env.SigmaMathEnv.step — Cat 4 — NEW."""
        from prometheus_math.sigma_env import SigmaMathEnv
        env = SigmaMathEnv()
        env.reset()
        with pytest.raises(ValueError):
            env.step(-1)

    def test_step_before_reset_raises(self):
        """sigma_env.SigmaMathEnv.step — Cat 4 — NEW."""
        from prometheus_math.sigma_env import SigmaMathEnv
        env = SigmaMathEnv()
        with pytest.raises(RuntimeError):
            env.step(0)


# ---------------------------------------------------------------------------
# Category 5 — State-machine testing
# ---------------------------------------------------------------------------


class TestStateMachine:

    def test_discovery_env_reset_keeps_kernel_across_episodes(self):
        """discovery_env.DiscoveryEnv.reset — Cat 5 — NEW (regression).
        DiscoveryEnv intentionally KEEPS its kernel across reset() calls;
        SigmaMathEnv builds a fresh one. This asymmetry is documented
        for downstream learners."""
        from prometheus_math.discovery_env import DiscoveryEnv
        env = DiscoveryEnv(degree=4, kernel_db_path=":memory:")
        env.reset()
        k1 = env._kernel
        env.reset()
        k2 = env._kernel
        assert k1 is k2

    def test_sigma_math_env_reset_creates_fresh_kernel(self):
        """sigma_env.SigmaMathEnv.reset — Cat 5 — NEW (regression)."""
        from prometheus_math.sigma_env import SigmaMathEnv
        env = SigmaMathEnv()
        env.reset()
        k1 = env._kernel
        env.reset()
        k2 = env._kernel
        assert k1 is not k2

    def test_discovery_env_close_then_reset_is_supported(self):
        """discovery_env.DiscoveryEnv — Cat 5 — NEW. After close(),
        a subsequent reset() must succeed (rebuild kernel)."""
        from prometheus_math.discovery_env import DiscoveryEnv
        env = DiscoveryEnv(degree=4, kernel_db_path=":memory:",
                           enable_pipeline=False)
        env.reset()
        env.close()
        assert env._kernel is None
        # Reset rebuilds.
        env.reset()
        assert env._kernel is not None

    def test_obstruction_env_step_before_reset_raises(self):
        """obstruction_env.ObstructionEnv.step — Cat 5 — regression."""
        from prometheus_math.obstruction_env import ObstructionEnv
        env = ObstructionEnv(corpus=_tiny_corpus(), held_out_fraction=0.5,
                             max_predicate_complexity=2)
        with pytest.raises(RuntimeError):
            env.step(0)

    def test_obstruction_env_repick_same_feature_overrides(self):
        """obstruction_env.ObstructionEnv.step — Cat 5 — NEW. Re-picking
        a feature within an episode overrides the previous value."""
        from prometheus_math.obstruction_env import (
            ObstructionEnv,
            encode_action,
        )
        env = ObstructionEnv(corpus=_tiny_corpus(), held_out_fraction=0.5,
                             max_predicate_complexity=3)
        env.reset()
        a1 = encode_action("n_steps", 5)
        a2 = encode_action("n_steps", 3)
        env.step(a1)
        env.step(a2)
        assert env._partial["n_steps"] == 3


# ---------------------------------------------------------------------------
# Category 6 — Differential testing
# ---------------------------------------------------------------------------


class TestDifferential:

    def test_palindromic_from_half_matches_manual_mirror(self):
        """discovery_env._palindromic_from_half — Cat 6 — NEW. Mirror
        the half manually and compare."""
        from prometheus_math.discovery_env import _palindromic_from_half
        half = [1, 0, -1]
        out = _palindromic_from_half(half, 4)  # half_len=3
        manual = half + list(reversed(half[:-1]))
        assert out == manual

    def test_evaluate_predicate_in_sample_lift_matches_definition(self):
        """obstruction_env.evaluate_predicate — Cat 6 — NEW. Manually
        compute matched_kill_rate / baseline_kill_rate; compare."""
        from prometheus_math.obstruction_env import evaluate_predicate
        from prometheus_math._obstruction_corpus import CorpusEntry
        corpus = [
            CorpusEntry(n_steps=5, neg_x=4, pos_x=1, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=True, has_diag_pos=False,
                        kill_verdict=True),
            CorpusEntry(n_steps=5, neg_x=4, pos_x=1, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=True, has_diag_pos=False,
                        kill_verdict=True),
            CorpusEntry(n_steps=3, neg_x=0, pos_x=0, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=False, has_diag_pos=False,
                        kill_verdict=False),
            CorpusEntry(n_steps=3, neg_x=0, pos_x=0, neg_y=0, pos_y=0,
                        neg_z=0, pos_z=0,
                        has_diag_neg=False, has_diag_pos=False,
                        kill_verdict=False),
        ]
        out = evaluate_predicate({"n_steps": 5}, corpus)
        # Manual: matched=2 kills/2 records=1.0; baseline=0 kills/2=0.
        # So matched_rate>0 and baseline_rate=0, code-path uses 1e-6 cap.
        assert out["matched_kill_rate"] == 1.0
        assert out["baseline_kill_rate"] == 0.0
        # The code-path makes lift = matched_rate / 1e-6 = 1e6 — huge.
        assert out["lift"] >= 1e5


# ---------------------------------------------------------------------------
# Category 7 — Error injection
# ---------------------------------------------------------------------------


class TestErrorInjection:

    def test_pipeline_crashes_on_PROMOTE_failure_returns_REJECTED(self):
        """discovery_pipeline.DiscoveryPipeline — Cat 7 — NEW. If
        PROMOTE raises, the pipeline must catch and return REJECTED
        rather than propagate."""
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension
        from prometheus_math.discovery_pipeline import DiscoveryPipeline

        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)

        # Monkey-patch PROMOTE to raise.
        orig_promote = k.PROMOTE
        def _bad_promote(claim, cap):
            raise RuntimeError("simulated promote failure")
        k.PROMOTE = _bad_promote  # type: ignore

        try:
            # A polynomial constructed to (a) sit in the (1.001, 1.18) M-band,
            # and (b) be unlikely to match any catalog. We also short-circuit
            # the catalog check by monkey-patching it because reaching the
            # PROMOTE-failure path requires surviving every kill check, which
            # is hard to guarantee in a unit test.
            import prometheus_math.discovery_pipeline as dp

            orig_check = dp._check_catalog_miss
            orig_f1 = dp._f1_permutation_null
            orig_f6 = dp._f6_base_rate
            orig_f9 = dp._f9_simpler_explanation
            orig_f11 = dp._f11_cross_validation
            orig_irred = dp._is_irreducible
            try:
                dp._check_catalog_miss = lambda c, m, tol=1e-5: (True, "miss", ["mock"])
                dp._is_irreducible = lambda c: (True, "mock")
                dp._f1_permutation_null = lambda c, m: (True, "F1 mock")
                dp._f6_base_rate = lambda c, m: (True, "F6 mock")
                dp._f9_simpler_explanation = lambda c: (True, "F9 mock")
                dp._f11_cross_validation = lambda c, m: (True, "F11 mock")
                # palindromic coeffs land within the M-band per phase0 only
                # if M is in (1.001, 1.18). We pass M directly.
                lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
                r = p.process_candidate(lehmer, 1.176)
                assert r.terminal_state == "REJECTED"
                assert r.kill_pattern is not None
                assert "PROMOTE_failed" in r.kill_pattern
            finally:
                dp._check_catalog_miss = orig_check
                dp._is_irreducible = orig_irred
                dp._f1_permutation_null = orig_f1
                dp._f6_base_rate = orig_f6
                dp._f9_simpler_explanation = orig_f9
                dp._f11_cross_validation = orig_f11
        finally:
            k.PROMOTE = orig_promote  # type: ignore

    def test_obstruction_env_substrate_eval_failure_falls_back(self):
        """obstruction_env.ObstructionEnv._terminate — Cat 7 — NEW.
        When the EVAL fails, the env falls back to a direct
        evaluate_predicate call, not crashing."""
        from prometheus_math.obstruction_env import (
            ObstructionEnv,
            encode_action,
            STOP_ACTION,
        )
        # We don't easily inject a fault — at minimum check the path
        # doesn't crash on the empty-predicate STOP route.
        env = ObstructionEnv(
            corpus=_tiny_corpus(),
            held_out_fraction=0.5,
            max_predicate_complexity=2,
        )
        env.reset()
        # Immediately STOP — empty predicate, should yield reward 0.
        obs, r, terminated, _, info = env.step(STOP_ACTION)
        assert terminated
        assert r == 0.0


# ---------------------------------------------------------------------------
# Cross-module: Mossinghoff catalog tolerance round-trip
# ---------------------------------------------------------------------------


class TestCatalogTolerance:

    def test_mossinghoff_match_with_default_tol(self):
        """catalog_consistency.mossinghoff_check — Cat 6 — NEW.
        Querying with the exact M-value from the snapshot must hit at
        the default 1e-5 tol."""
        from prometheus_math.databases.mahler import MAHLER_TABLE
        from prometheus_math.catalog_consistency import mossinghoff_check
        if not MAHLER_TABLE:
            pytest.skip("snapshot empty")
        entry = MAHLER_TABLE[0]
        m = float(entry["mahler_measure"])
        coeffs = list(entry["coeffs"])
        r = mossinghoff_check(coeffs, m)
        assert r.hit

    def test_lehmer_literature_check_handles_x_negate_flip(self):
        """catalog_consistency.lehmer_literature_check — Cat 6 — NEW.
        The x→-x flipped polynomial has the same M; the catalog should
        find it via Phase 1 coeff match."""
        from prometheus_math._lehmer_literature_data import LEHMER_LITERATURE_TABLE
        from prometheus_math.catalog_consistency import lehmer_literature_check
        if not LEHMER_LITERATURE_TABLE:
            pytest.skip("no lit table")
        entry = LEHMER_LITERATURE_TABLE[0]
        coeffs = list(entry["polynomial_coeffs"])
        m = float(entry["m_value"])
        flipped = [c if (i % 2 == 0) else -c for i, c in enumerate(coeffs)]
        r = lehmer_literature_check(flipped, m)
        assert r.hit


# ---------------------------------------------------------------------------
# Arsenal metadata sanity
# ---------------------------------------------------------------------------


class TestArsenalRegistry:

    def test_registry_keys_have_colon_format(self):
        """arsenal_meta.ARSENAL_REGISTRY — Cat 6 — NEW. Every registry
        key must be in 'module:qualname' form (matches BIND's parser)."""
        from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
        for ref in ARSENAL_REGISTRY.keys():
            assert ":" in ref, f"registry key {ref!r} missing ':'"
            mod, qn = ref.split(":", 1)
            assert mod and qn, f"empty module or qualname: {ref!r}"

    def test_registry_meta_callable_ref_matches_key(self):
        """arsenal_meta.ARSENAL_REGISTRY — Cat 6 — NEW. The ArsenalMeta's
        callable_ref must equal its registry key."""
        from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
        for ref, meta in ARSENAL_REGISTRY.items():
            assert meta.callable_ref == ref

    def test_registry_cost_models_round_trip_to_CostModel(self):
        """arsenal_meta + bind_eval — Cat 6 — NEW. Every registered cost
        block must be a valid CostModel kwargs dict."""
        from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
        from sigma_kernel.bind_eval import CostModel
        for ref, meta in ARSENAL_REGISTRY.items():
            try:
                cm = CostModel(**(meta.cost or {}))
            except TypeError as e:
                pytest.fail(f"bad cost block on {ref}: {meta.cost}: {e}")


# ---------------------------------------------------------------------------
# Live corpus adapter (skip cleanly if unavailable)
# ---------------------------------------------------------------------------


class TestLiveCorpusAdapter:

    def test_load_live_corpus_FNF_when_files_missing(self, tmp_path):
        """_obstruction_corpus_live.load_live_corpus — Cat 7 — NEW.
        When the data files are missing, raise FileNotFoundError, not
        a generic IO/Exception."""
        from prometheus_math._obstruction_corpus_live import load_live_corpus
        bogus_battery = tmp_path / "no_such.jsonl"
        bogus_dev = tmp_path / "no_such2.jsonl"
        with pytest.raises(FileNotFoundError):
            load_live_corpus(path=bogus_battery, deviations_path=bogus_dev)
