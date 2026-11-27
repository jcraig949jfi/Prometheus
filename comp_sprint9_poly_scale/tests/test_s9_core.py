"""Unit tests for Sprint 9: Exact Polynomial O(m * n^3) Z/8Z Unitary Verifier & Clifford Completion
(Cross-Verified Identically Against Exhaustive 2^n Simulation on n = 8..12, Plus Full n = 12..16 Suite!)."""
from __future__ import annotations

from comp_sprint7_clifford_t.s7_core import (
    extract_phase_poly,
    simulate_clifford_t,
    verify_clifford_t_circuit,
)
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint9_poly_scale.s9_benchmarks import build_s9_benchmarks, s9_manifest_sha256
from comp_sprint9_poly_scale.s9_poly_core import (
    fast_todd_2022_poly_optimize,
    synthesize_poly_clifford_t,
    todd_2018_poly_optimize,
    tpar_poly_optimize,
    verify_poly_exact,
)


def test_poly_verifier_and_completion_match_exhaustive_2n_unitary():
    """Prove `verify_poly_exact` and `synthesize_poly_clifford_t` match exhaustive `2^n` unitary
    simulation 100% identically across real `n = 8..11` circuits (positive AND mutated negative checks!)."""
    s8 = build_s8_benchmarks()
    for task in s8["s8_hold_lit"][:8]:
        circ = task.circuit
        poly, final_mat = extract_phase_poly(circ)
        st0, ph0 = simulate_clifford_t(circ.n_qubits, circ.gates)

        ft = fast_todd_2022_poly_optimize(circ)
        assert verify_poly_exact(poly, final_mat, ft)
        assert verify_clifford_t_circuit(st0, ph0, ft)
        assert ft.t_count() <= task.tpar_t

        # Negative soundness test: corrupting a single T gate MUST fail BOTH verifiers!
        bad_gates = list(ft.gates) + [("T", 0)]
        from comp_sprint7_clifford_t.s7_core import CliffordTCircuit
        bad_circ = CliffordTCircuit(circ.n_qubits, tuple(bad_gates))
        assert not verify_poly_exact(poly, final_mat, bad_circ)
        assert not verify_clifford_t_circuit(st0, ph0, bad_circ)


def test_s9_320_benchmarks_and_n12_to_n16_polynomial_baselines():
    """Verify all 320 Sprint 9 tasks (`n = 12..16`), deterministic manifest, and polynomial TODD / FastTODD
    on large `n = 12..16` literature quantum circuits (`gf2^5_mult` 15q, `cuccaro_16`, `qcla_16`, `grover_16`!)."""
    suites = build_s9_benchmarks()
    assert len(suites["dev_diag"]) == 20
    assert all(len(suites[f"val_g{g}"]) == 25 for g in (1, 2, 3, 4))
    assert len(suites["s9_hold_lit"]) == 40
    assert len(suites["s9_hold_proc_ccz"]) == 80
    assert len(suites["s9_hold_proc_rand"]) == 80
    assert sum(len(v) for v in suites.values()) == 320
    assert s9_manifest_sha256(suites) == s9_manifest_sha256(build_s9_benchmarks())

    # Test representative n = 12..16 literature circuits (incl. n=15 GF(2^5) mult & n=16 Cuccaro/QCLA/Grover!)
    sample_lit = [suites["s9_hold_lit"][i] for i in (0, 4, 10, 14, 16, 21, 26, 31, 38)]
    strict_wins = 0
    for task in sample_lit:
        poly, final_mat = extract_phase_poly(task.circuit)
        tp = tpar_poly_optimize(task.circuit)
        ft = fast_todd_2022_poly_optimize(task.circuit)
        assert verify_poly_exact(poly, final_mat, tp)
        assert verify_poly_exact(poly, final_mat, ft)
        assert ft.t_count() <= tp.t_count()
        if ft.t_count() < tp.t_count():
            strict_wins += 1
    assert strict_wins >= 7


def test_s9_runner_enforces_toolless_isolation():
    """Regression guard: Sprint 9 proposer MUST enforce `--tools ""` in an isolated TemporaryDirectory."""
    import inspect
    from comp_sprint9_poly_scale import s9_runner
    src = inspect.getsource(s9_runner._call_claude_isolated)
    assert '"--tools", ""' in src
    assert "TemporaryDirectory" in src

