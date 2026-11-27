"""Unit tests for Sprint 10 — 5th Independent Formal Domain: Exact Binary Bilinear 3-Tensor Rank over F_2."""
from __future__ import annotations

from comp_sprint10_alphatensor.s10_benchmarks import (
    build_s10_benchmarks,
    make_matmul_tensor,
    s10_manifest_sha256,
)
from comp_sprint10_alphatensor.s10_core import (
    build_s10_a1_flip_graph_artifact,
    run_s10_artifact,
    verify_bilinear_decomp,
)


def test_s10_strassen_2x2x2_rediscovery_and_exact_verifier():
    """Verify exact bilinear tensor verifier (positive + mutated negative) AND that published
    Kauers-Moosbauer Flip-Graph automatically rediscovers Strassen rank 7 (< 8) on 2x2x2 matmul!"""
    t222 = make_matmul_tensor(2, 2, 2)
    assert t222.base_rank() == 8
    assert verify_bilinear_decomp(t222, t222.init_terms)
    # Corrupted decomposition MUST fail exact verifier
    assert not verify_bilinear_decomp(t222, t222.init_terms[:-1])

    fg = build_s10_a1_flip_graph_artifact()
    sol, tel = run_s10_artifact(fg, t222, seed=0, v3_budget=600_000)
    assert verify_bilinear_decomp(t222, sol)
    assert not tel["verifier_fallback"]
    assert len(sol) == 7  # Strassen optimal rank 7 over F_2!


def test_s10_140_benchmarks_deterministic_manifest():
    suites = build_s10_benchmarks()
    assert len(suites["dev_diag"]) == 20
    assert all(len(suites[f"val_g{g}"]) == 20 for g in (1, 2, 3))
    assert len(suites["s10_hold_matmul"]) == 12
    assert len(suites["s10_hold_proc_planted"]) == 24
    assert len(suites["s10_hold_proc_rand"]) == 24
    assert sum(len(v) for v in suites.values()) == 140
    assert s10_manifest_sha256(suites) == s10_manifest_sha256(build_s10_benchmarks())
    # Every single benchmark initial decomposition verifies 100% exact
    for tasks in suites.values():
        for t in tasks:
            assert verify_bilinear_decomp(t.tensor, t.tensor.init_terms)


def test_s10_runner_enforces_toolless_isolation():
    import inspect
    from comp_sprint10_alphatensor import s10_runner
    src = inspect.getsource(s10_runner._call_claude_isolated)
    assert '"--tools", ""' in src
    assert "TemporaryDirectory" in src

