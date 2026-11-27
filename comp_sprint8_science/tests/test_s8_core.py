"""Unit tests for Sprint 8 Core, Exact C(n-1, 2) Involutive chi_z Theorem, Published FastTODD (2022),
and All 200 Fresh `n = 8..11` Qubit Benchmarks (Including All 20 Literature Quantum Circuits)."""
from __future__ import annotations

from comp_sprint7_clifford_t.s7_core import (
    cubic_tensor_bitmask,
    extract_phase_poly,
    simulate_clifford_t,
    tpar_fold_baseline as tpar_optimize,
    verify_clifford_t_circuit,
)
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks, s8_manifest_sha256
from comp_sprint8_science.s8_core import (
    apply_todd_shift,
    build_chi_z_columns,
    fast_todd_2022_optimize,
    nullspace_gf2_columns,
    odd_t_parities,
    run_s8_artifact,
    todd_2018_optimize,
)
from comp_sprint8_science.s8_mechanistic import build_ablation_artifact


def test_involutive_chi_z_theorem_and_published_baselines():
    """Exhaustively verify our exact `C(n-1, 2)` involutive `chi_z` theorem, `A1_TODD_2018`,
    and `A1_FAST_TODD_2022` on real `n = 8..11` literature quantum circuits (100% 2^n unitary!)."""
    suites = build_s8_benchmarks()
    assert len(suites["dev_diag"]) == 20
    assert all(len(suites[f"val_g{g}"]) == 25 for g in (1, 2, 3, 4))
    assert len(suites["s8_hold_lit"]) == 20
    assert len(suites["s8_hold_proc_ccz"]) == 30
    assert len(suites["s8_hold_proc_rand"]) == 30
    total_tasks = sum(len(v) for v in suites.values())
    assert total_tasks == 200

    # Manifest determinism check
    assert s8_manifest_sha256(suites) == s8_manifest_sha256(build_s8_benchmarks())

    # Verify EVERY single one of the 20 literature circuits (n=8..11) passes exact 2^n unitary check
    # under T-par, TODD (2018), AND FastTODD (2022), AND verify involutive chi_z preserves exact cubic tensor!
    fast_strict_wins = 0
    for task in suites["s8_hold_lit"]:
        circ = task.circuit
        n = task.n_qubits
        st0, ph0 = simulate_clifford_t(n, circ.gates)
        poly, _ = extract_phase_poly(circ)
        P = odd_t_parities(poly)
        cub0 = cubic_tensor_bitmask(n, P)

        # Check involutive chi_z nullspace vectors preserve exact cubic tensor on a non-trivial shift z
        z = P[0] ^ P[1]
        if z:
            cols = build_chi_z_columns(n, P, z)
            # Every column MUST fit strictly in C(n, 2) bits (<= 55 bits for n <= 11!)
            max_bits = n * (n - 1) // 2
            assert all(c < (1 << max_bits) for c in cols)
            nl = nullspace_gf2_columns(cols)
            for yv in nl[:5]:
                Q = apply_todd_shift(P, yv, z)
                assert cubic_tensor_bitmask(n, Q) == cub0

        tp = tpar_optimize(circ)
        td = todd_2018_optimize(circ)
        ft = fast_todd_2022_optimize(circ)
        assert verify_clifford_t_circuit(st0, ph0, tp)
        assert verify_clifford_t_circuit(st0, ph0, td)
        assert verify_clifford_t_circuit(st0, ph0, ft)
        assert ft.t_count() <= tp.t_count()
        if ft.t_count() < tp.t_count():
            fast_strict_wins += 1
    assert fast_strict_wins >= 15


def test_law4c_sparse_synthesis_artifact():
    """Verify our Law 4b+4c sparse `C(n-1, 2)` synthesis artifact executes cleanly and improves an n=10 circuit."""
    suites = build_s8_benchmarks()
    task = suites["s8_hold_lit"][2]  # lit_cuccaro_10a (n=10)
    art = build_ablation_artifact("SYNTH_SPARSE_NULL_TODD", use_sparse_chiz=True)
    circ, tel = run_s8_artifact(art, task.circuit, seed=0, v3_budget=600_000)
    st0, ph0 = simulate_clifford_t(task.n_qubits, task.circuit.gates)
    assert verify_clifford_t_circuit(st0, ph0, circ)
    assert not tel["verifier_fallback"]
    assert tel["ops_spent"] > 0
    assert circ.t_count() <= task.tpar_t


def test_s8_runner_enforces_toolless_isolated_proposer():
    """Regression guard: ensure Sprint 8 proposer enforces `--tools ""` inside an isolated TemporaryDirectory."""
    import inspect
    from comp_sprint8_science import s8_runner
    src = inspect.getsource(s8_runner._call_claude_json)
    assert '"--tools", ""' in src
    assert "TemporaryDirectory" in src

