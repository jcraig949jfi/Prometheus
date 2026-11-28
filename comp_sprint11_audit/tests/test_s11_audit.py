"""Unit tests for Sprint 11 — Reference KM-2023 Reproduction (Stop Condition #1), Phase B Disjointness &
Tool-Less Isolation, Phase D Machine-Checked Counterexample & Theorem P1, and Frozen rso/ Integrity."""
from __future__ import annotations

import inspect

from comp_sprint10_alphatensor.s10_benchmarks import build_s10_benchmarks, make_matmul_tensor
from comp_sprint10_alphatensor.s10_core import verify_bilinear_decomp
from comp_sprint11_audit import phase_b_attribution
from comp_sprint11_audit.phase_a_km2023 import km2023_reference_search
from comp_sprint11_audit.phase_b_attribution import (
    build_s11_attribution_suite,
    s11_attr_manifest_sha256,
)
from comp_sprint11_audit.phase_d_theorem_loop import (
    cycle1_search_flip_completeness_counterexample,
    cycle2_verify_xor_triangle_theorem,
)


def test_stop_condition_1_km2023_reproduces_2x2x2_and_2x3x3():
    """Verify faithful fused KM-2023 reproduces Strassen 7 (2x2x2) and Hopcroft-Kerr 15 (2x3x3) cleanly."""
    t222 = make_matmul_tensor(2, 2, 2)
    sol7, _ = km2023_reference_search(t222, time_limit_sec=0.35, seed=0)
    assert verify_bilinear_decomp(t222, sol7) and len(sol7) == 7

    t233 = make_matmul_tensor(2, 3, 3)
    best15 = 99
    for sd in range(3):
        sol, _ = km2023_reference_search(t233, time_limit_sec=0.60, seed=sd)
        assert verify_bilinear_decomp(t233, sol)
        best15 = min(best15, len(sol))
        if best15 <= 15:
            break
    assert best15 == 15


def test_phase_b_disjoint_immutable_suite_and_toolless_guard():
    """Verify Phase B 40-task suite is deterministic, 100% disjoint from Sprint 10, and enforces `--tools ""`."""
    s10_shas = {t.sha256() for tasks in build_s10_benchmarks().values() for t in tasks}
    s11_tasks = build_s11_attribution_suite()
    assert len(s11_tasks) == 40
    assert s11_attr_manifest_sha256(s11_tasks) == s11_attr_manifest_sha256(build_s11_attribution_suite())
    assert all(t.sha256() not in s10_shas for t in s11_tasks)
    src = inspect.getsource(phase_b_attribution._call_claude_isolated)
    assert '"--tools", ""' in src
    assert "TemporaryDirectory" in src


def test_phase_d_machine_checked_counterexample_and_theorem_p1():
    """Verify Cycle 1 exact isolated BFS counterexample AND Cycle 2 machine-checked Theorem P1."""
    c1 = cycle1_search_flip_completeness_counterexample()
    assert c1["verdict"] == "REJECTED_BY_MACHINE_CHECKED_COUNTEREXAMPLE"
    assert c1["trapped_flip_degree"] == 0
    assert c1["exhaustive_bfs_proof"]["complete"] is True
    assert c1["exhaustive_bfs_proof"]["component_size"] == 1
    assert c1["true_rank_upper_bound"] < c1["trapped_rank"]
    assert c1["xor_triangle_plus_escape_check"]["deg_after_one_xor_triangle_plus"] >= 3

    c2 = cycle2_verify_xor_triangle_theorem()
    assert c2["verdict"] == "RETAINED_MACHINE_CHECKED_THEOREM"
    ev = c2["empirical_verification_trials"]
    assert ev["iso_violations"] == 0 and ev["tri_violations"] == 0
    assert ev["min_isolated_flip_deg_gain"] >= 3
