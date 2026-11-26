"""Core unit tests for Track S7-CT: Fault-Tolerant Quantum Clifford+T T-Count vs Published T-par & TODD."""
from __future__ import annotations

import copy

import pytest

from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint7_clifford_t.s7_benchmarks import build_s7_benchmarks, s7_manifest_sha256
from comp_sprint7_clifford_t.s7_core import (
    build_s7_a3_artifact,
    build_s7_a5_sham_artifact,
    optimize_s7_with_artifact,
    simulate_clifford_t,
    todd_baseline_optimize,
    tpar_fold_baseline,
    verify_clifford_t_circuit,
)


def test_s7_140_manifest_and_exact_unitary_tpar_todd():
    s1 = build_s7_benchmarks()
    s2 = build_s7_benchmarks()
    assert s7_manifest_sha256(s1) == s7_manifest_sha256(s2)
    assert sum(len(v) for v in s1.values()) == 140

    todd_gains = 0
    for t in s1["s7_hold_struct"][:6] + s1["s7_hold_proc_ccz"][:4]:
        st, ph = simulate_clifford_t(t.n_qubits, t.circuit.gates)
        c_tpar = tpar_fold_baseline(t.circuit)
        c_todd = todd_baseline_optimize(t.circuit)
        assert verify_clifford_t_circuit(st, ph, c_tpar)
        assert verify_clifford_t_circuit(st, ph, c_todd)
        assert c_todd.t_count() <= c_tpar.t_count() <= t.circuit.t_count()
        todd_gains += (c_tpar.t_count() - c_todd.t_count())
    # Published TODD MUST genuinely reduce T-count below T-par on overlapping CCZ networks!
    assert todd_gains > 0, "Published TODD baseline failed to reduce T-count below T-par!"


def test_s7_law4b_determinism_cross_gen_and_rso_6of6():
    suites = build_s7_benchmarks()
    t = suites["s7_hold_struct"][0]
    m0 = LibModule.from_source(
        "ct_g0", 0,
        "def run_todd(circ):\n"
        "    c = todd_optimize(circ)\n"
        "    report_best(c)\n"
        "    return best_solution()\n",
    )
    m1 = LibModule.from_source(
        "ct_g1", 1,
        "def run_wrap(circ):\n"
        "    return lib.run_todd(circ)\n",
    )
    orch = LibModule.from_source(
        "ct_o1", 1,
        "def solve(circ, n_qubits, seed, api, lib, budget):\n"
        "    return lib.run_wrap(circ)\n",
        required_fn="solve",
    )
    art = CompositionalAlgoArtifact("G1", "S7_CLIFFORD_T", 1, (m0, m1), orch)
    c1, mt1 = optimize_s7_with_artifact(t.circuit, art, seed=0, v3_budget=250_000)
    c2, mt2 = optimize_s7_with_artifact(t.circuit, art, seed=0, v3_budget=250_000)
    assert c1.sha256() == c2.sha256() and mt1["ops_spent"] == mt2["ops_spent"]
    assert not mt1["fn_errors"]
    assert any(k.startswith("g1->g0:run_todd") for k in mt1["cross_gen_calls"])

    # A5_SHAM determinism
    a5 = build_s7_a5_sham_artifact()
    ca, ma = optimize_s7_with_artifact(t.circuit, a5, seed=1, v3_budget=100_000)
    cb, mb = optimize_s7_with_artifact(t.circuit, a5, seed=1, v3_budget=100_000)
    assert ca.sha256() == cb.sha256() and ma["ops_spent"] == mb["ops_spent"]

    # 6/6 RSO audit
    tasks = suites["s7_hold_struct"][:2]
    rows = []
    for arm, a in [("A0_BASE", None), ("G1", art)]:
        for tk in tasks:
            for sd in (0, 1, 2):
                c, _ = optimize_s7_with_artifact(tk.circuit, a, seed=sd, v3_budget=150_000)
                rows.append(make_row(
                    arm=arm, suite="s7_hold_struct", task_id=tk.task_id, stratum=tk.stratum,
                    split=tk.split, seed=sd, spec_sha256=tk.sha256(), cost=c.t_count(),
                    verified_exact=True, solution_sha256=c.sha256(),
                ))
    mini = {"s7_hold_struct": tasks}
    msha = s7_manifest_sha256(mini)
    pkt = {"track": "S7_CLIFFORD_T", "manifest_sha256": msha, "summary": compute_summary(rows), "rows": rows}
    kw = dict(canonical_suites=mini, canonical_manifest_sha256=msha, expected_arms=["A0_BASE", "G1"], expected_suites=["s7_hold_struct"], expected_seeds=[0, 1, 2])
    assert verify_and_reduce(pkt, **kw)["licenses_verdict"] is True
    for mut in [
        lambda p: p["rows"].pop(),
        lambda p: p["rows"].append(copy.deepcopy(p["rows"][0])),
        lambda p: p["summary"]["G1"]["s7_hold_struct"].__setitem__("mean_median_cost", 0.0),
        lambda p: p["rows"][-1].__setitem__("cost", 0),
        lambda p: p["rows"][0].__setitem__("spec_sha256", "0" * 64),
        lambda p: p.__setitem__("manifest_sha256", "f" * 64),
    ]:
        p2 = copy.deepcopy(pkt); mut(p2)
        with pytest.raises(ValueError):
            verify_and_reduce(p2, **kw)
