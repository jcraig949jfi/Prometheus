"""Core unit tests for Track S5-Q: Quantum GL(n, F_2) CNOT Synthesis under All Four Laws."""
from __future__ import annotations

import copy

import pytest

from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint4.ko_matched import knockout_generations_generic
from comp_sprint5_quantum.s5q_benchmarks import build_s5q_benchmarks, s5q_manifest_sha256
from comp_sprint5_quantum.s5q_core import (
    build_s5q_a3_artifact,
    build_s5q_a5_sham_artifact,
    gauss_elim_cnot,
    pmh_cnot_synth,
    synthesize_s5q_with_artifact,
    verify_cnot_circuit,
)


def test_s5q_140_manifest_gauss_and_pmh_exactness():
    s1 = build_s5q_benchmarks()
    s2 = build_s5q_benchmarks()
    assert s5q_manifest_sha256(s1) == s5q_manifest_sha256(s2)
    assert sum(len(v) for v in s1.values()) == 140
    # Verify Gauss and published Patel-Markov-Hayes (PMH 2008) on sample dense 16-18q matrices!
    for t in s1["s5q_hold_struct"][:4] + s1["s5q_hold_proc_dense"][:4]:
        cg = gauss_elim_cnot(t.target_rows)
        cp = pmh_cnot_synth(t.target_rows)
        assert verify_cnot_circuit(t.target_rows, cg)
        assert verify_cnot_circuit(t.target_rows, cp)
        # PMH should generally be <= Gauss on dense matrices
        assert cp.gate_count() <= cg.gate_count() + 10


def test_s5q_law4_determinism_cross_gen_knockout_and_rso_6of6():
    suites = build_s5q_benchmarks()
    t = suites["s5q_hold_proc_dense"][0]
    m0 = LibModule.from_source(
        "q_g0", 0,
        "def run_pmh_m(rows, m):\n"
        "    c = pmh_synth(rows, m=m)\n"
        "    report_best(c)\n"
        "    return best_solution()\n",
    )
    m1 = LibModule.from_source(
        "q_g1", 1,
        "def try_blocks(rows):\n"
        "    for m in (2, 3, 4):\n"
        "        lib.run_pmh_m(rows, m)\n"
        "    return best_solution()\n",
    )
    orch = LibModule.from_source(
        "q_o1", 1,
        "def solve(circ, target_rows, seed, api, lib, budget):\n"
        "    lib.run('try_blocks', target_rows, op_cap=15000)\n"
        "    return best_solution()\n",
        required_fn="solve",
    )
    g0 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", "S5Q_CNOT_COMP", 0, (m0,), LibModule.from_source("q_o0", 0, "def solve(circ, target_rows, seed, api, lib, budget):\n    return lib.run_pmh_m(target_rows, 3)\n", required_fn="solve"))
    g1 = CompositionalAlgoArtifact("G1", "S5Q_CNOT_COMP", 1, (m0, m1), orch)
    ko = knockout_generations_generic(g1, {1}, "CNOTCircuit", "KO_MATCHED_G1")

    c1, mt1 = synthesize_s5q_with_artifact(t.target_rows, g1, seed=0, word_budget=25_000)
    c2, mt2 = synthesize_s5q_with_artifact(t.target_rows, g1, seed=0, word_budget=25_000)
    assert c1.sha256() == c2.sha256() and mt1["ops_spent"] == mt2["ops_spent"]
    assert not mt1["fn_errors"]
    assert any(k.startswith("g1->g0:run_pmh_m") for k in mt1["cross_gen_calls"])

    # Matched-op knockout + A3/A5 determinism
    _, mko = synthesize_s5q_with_artifact(t.target_rows, ko, seed=0, word_budget=25_000, fallback_artifact=g0)
    assert mko["ops_spent"] > 0
    for art in (build_s5q_a3_artifact(), build_s5q_a5_sham_artifact()):
        ca, ma = synthesize_s5q_with_artifact(t.target_rows, art, seed=1, word_budget=15_000)
        cb, mb = synthesize_s5q_with_artifact(t.target_rows, art, seed=1, word_budget=15_000)
        assert ca.sha256() == cb.sha256() and ma["ops_spent"] == mb["ops_spent"]

    # 6/6 RSO audit on mini S5-Q packet
    tasks = suites["s5q_hold_proc_dense"][:2]
    rows = []
    for arm, a in [("A0_BASE", None), ("G1", g1)]:
        for tk in tasks:
            for sd in (0, 1, 2):
                c, _ = synthesize_s5q_with_artifact(tk.target_rows, a, seed=sd, word_budget=15_000)
                rows.append(make_row(
                    arm=arm, suite="s5q_hold_proc_dense", task_id=tk.task_id, stratum=tk.stratum,
                    split=tk.split, seed=sd, spec_sha256=tk.sha256(), cost=c.gate_count(),
                    verified_exact=True, solution_sha256=c.sha256(),
                ))
    mini = {"s5q_hold_proc_dense": tasks}
    msha = s5q_manifest_sha256(mini)
    pkt = {"track": "S5Q_CNOT_COMP", "manifest_sha256": msha, "summary": compute_summary(rows), "rows": rows}
    kw = dict(canonical_suites=mini, canonical_manifest_sha256=msha, expected_arms=["A0_BASE", "G1"], expected_suites=["s5q_hold_proc_dense"], expected_seeds=[0, 1, 2])
    assert verify_and_reduce(pkt, **kw)["licenses_verdict"] is True
    for mut in [
        lambda p: p["rows"].pop(),
        lambda p: p["rows"].append(copy.deepcopy(p["rows"][0])),
        lambda p: p["summary"]["G1"]["s5q_hold_proc_dense"].__setitem__("mean_median_cost", 0.0),
        lambda p: p["rows"][-1].__setitem__("cost", 0),
        lambda p: p["rows"][0].__setitem__("spec_sha256", "0" * 64),
        lambda p: p.__setitem__("manifest_sha256", "f" * 64),
    ]:
        p2 = copy.deepcopy(pkt); mut(p2)
        with pytest.raises(ValueError):
            verify_and_reduce(p2, **kw)
