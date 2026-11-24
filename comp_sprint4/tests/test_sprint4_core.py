"""Core unit tests for Sprint 4: Track S4-A (Deterministic Z3 rlimit BV) & Track S4-B (9-11in 4-Gen XAG) + Matched-Op KO."""
from __future__ import annotations

import copy

import pytest

from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint4.ko_matched import knockout_generations_generic
from comp_sprint4.s4a_bv_benchmarks import build_s4a_bv_benchmarks, s4a_manifest_sha256
from comp_sprint4.s4a_bv_engine import (
    build_s4a_a3_artifact,
    build_s4a_a5_sham_artifact,
    optimize_s4a_with_artifact,
    verify_bv_equiv_z3_det,
)
from comp_sprint4.s4b_xag_benchmarks import build_s4b_xag_benchmarks, s4b_manifest_sha256
from comp_sprint4.s4b_xag_engine import (
    build_s4b_a3_artifact,
    build_s4b_a5_sham_artifact,
    synthesize_s4b_with_artifact,
)


def test_s4a_bv_140_manifest_and_zero_jitter_z3_rlimit_and_metered_builder():
    s1 = build_s4a_bv_benchmarks()
    s2 = build_s4a_bv_benchmarks()
    assert s4a_manifest_sha256(s1) == s4a_manifest_sha256(s2)
    assert sum(len(v) for v in s1.values()) == 140
    assert len(s1["s4a_hold_struct"]) == 18 and len(s1["s4a_hold_proc"]) == 26

    # Compositional BV artifact exercising MeteredBVBuilder + verify_equiv_z3 + cross-gen call -> ZERO fn_errors!
    m0 = LibModule.from_source(
        "bv_g0", 0,
        "def make_xor_probe(prog):\n"
        "    b = BVBuilder(prog.width, prog.n_inputs)\n"
        "    out = b.op('XOR', b.inp(0), b.inp(1)) if prog.n_inputs >= 2 else b.inp(0)\n"
        "    return b.build(out)\n",
    )
    m1 = LibModule.from_source(
        "bv_g1", 1,
        "def run_check(prog, spec):\n"
        "    cand = lib.make_xor_probe(prog)\n"
        "    ok, _ = verify_equiv_z3(spec, cand)\n"
        "    if ok:\n"
        "        report_best(cand)\n"
        "    return best_solution()\n",
    )
    orch = LibModule.from_source(
        "bv_orch", 1,
        "def solve(prog, spec, seed, api, lib, budget):\n"
        "    lib.run('run_check', prog, spec, op_cap=10000)\n"
        "    return best_solution()\n",
        required_fn="solve",
    )
    art = CompositionalAlgoArtifact("G1", "S4A_BV_COMP", 1, (m0, m1), orch)
    t = s1["s4a_hold_struct"][0]
    p1, meta1 = optimize_s4a_with_artifact(t.spec, art, seed=0, op_budget=15_000)
    p2, meta2 = optimize_s4a_with_artifact(t.spec, art, seed=0, op_budget=15_000)
    assert p1.sha256() == p2.sha256()
    assert meta1["ops_spent"] == meta2["ops_spent"]
    assert not meta1["fn_errors"], f"Unexpected BV fn_errors: {meta1['fn_error_msgs']}"
    assert any(k.startswith("g1->g0:make_xor_probe") for k in meta1["cross_gen_calls"])
    assert verify_bv_equiv_z3_det(t.spec, p1)[0] is True

    # Determinism on A3 and A5_SHAM
    for base_art in (build_s4a_a3_artifact(), build_s4a_a5_sham_artifact()):
        c1, m_a = optimize_s4a_with_artifact(t.spec, base_art, seed=1, op_budget=12_000)
        c2, m_b = optimize_s4a_with_artifact(t.spec, base_art, seed=1, op_budget=12_000)
        assert c1.sha256() == c2.sha256() and m_a["ops_spent"] == m_b["ops_spent"]


def test_s4b_xag_172_manifest_cofactor_and_matched_op_knockout_and_rso_6of6():
    s1 = build_s4b_xag_benchmarks()
    s2 = build_s4b_xag_benchmarks()
    assert s4b_manifest_sha256(s1) == s4b_manifest_sha256(s2)
    assert sum(len(v) for v in s1.values()) == 172
    assert len(s1["s4b_hold_struct"]) == 16 and len(s1["s4b_hold_proc_shared"]) == 14 and len(s1["s4b_hold_proc_comp"]) == 14

    # Build a 2-gen artifact where G1 burns budget, and verify KO_MATCHED re-routes unspent budget to G0 fallback!
    m0 = LibModule.from_source(
        "xag_g0", 0,
        "def burn_davio(circ, n_in, targets, seed):\n"
        "    rng = random.Random(seed)\n"
        "    _cf = cofactor(targets[0], 0, 1)\n"
        "    while budget.remaining() > 300:\n"
        "        o = list(range(n_in)); rng.shuffle(o)\n"
        "        report_best(davio_synth(n_in, targets, o, greedy=False))\n"
        "    return best_solution()\n",
    )
    orch0 = LibModule.from_source(
        "o0", 0,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    return lib.burn_davio(circ, n_inputs, targets, seed)\n",
        required_fn="solve",
    )
    m1 = LibModule.from_source(
        "xag_g1", 1,
        "def extra_pass(circ, n_in, targets, seed):\n"
        "    return lib.burn_davio(circ, n_in, targets, seed + 5)\n",
    )
    orch1 = LibModule.from_source(
        "o1", 1,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    lib.run('extra_pass', circ, n_inputs, targets, seed, op_cap=18000)\n"
        "    return best_solution()\n",
        required_fn="solve",
    )
    g0 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", "S4B_XAG_4GEN", 0, (m0,), orch0)
    g1 = CompositionalAlgoArtifact("G1", "S4B_XAG_4GEN", 1, (m0, m1), orch1)
    ko_stub = knockout_generations_generic(g1, {1}, "XAGCircuit", "KO_MATCHED_G1")

    t = s1["s4b_hold_struct"][0]
    c_full, m_full = synthesize_s4b_with_artifact(t.n_inputs, t.targets, g1, seed=0, op_budget=20_000)
    c_ko_m, m_ko_m = synthesize_s4b_with_artifact(t.n_inputs, t.targets, ko_stub, seed=0, op_budget=20_000, fallback_artifact=g0)
    assert not m_full["fn_errors"]
    # Matched-op knockout MUST spend nearly the full 20,000 op budget via fallback routing!
    assert m_ko_m["ops_spent"] >= 18_000
    assert m_full["ops_spent"] >= 17_500

    # 6/6 RSO attack check on mini S4-B packet
    tasks = s1["s4b_hold_struct"][:2]
    rows = []
    for arm, a in [("A0_BASE", None), ("A3_ZERO_LLM", build_s4b_a3_artifact())]:
        for tk in tasks:
            for sd in (0, 1, 2):
                c, _ = synthesize_s4b_with_artifact(tk.n_inputs, tk.targets, a, seed=sd, op_budget=15_000)
                rows.append(make_row(
                    arm=arm, suite="s4b_hold_struct", task_id=tk.task_id, stratum=tk.stratum,
                    split=tk.split, seed=sd, spec_sha256=tk.sha256(), cost=c.gate_count(),
                    verified_exact=True, solution_sha256=c.sha256(),
                ))
    mini = {"s4b_hold_struct": tasks}
    msha = s4b_manifest_sha256(mini)
    pkt = {"track": "S4B_XAG_4GEN", "manifest_sha256": msha, "summary": compute_summary(rows), "rows": rows}
    kw = dict(canonical_suites=mini, canonical_manifest_sha256=msha, expected_arms=["A0_BASE", "A3_ZERO_LLM"], expected_suites=["s4b_hold_struct"], expected_seeds=[0, 1, 2])
    assert verify_and_reduce(pkt, **kw)["licenses_verdict"] is True
    for mut in [
        lambda p: p["rows"].pop(),
        lambda p: p["rows"].append(copy.deepcopy(p["rows"][0])),
        lambda p: p["summary"]["A3_ZERO_LLM"]["s4b_hold_struct"].__setitem__("mean_median_cost", 0.0),
        lambda p: p["rows"][-1].__setitem__("cost", 0),
        lambda p: p["rows"][0].__setitem__("spec_sha256", "0" * 64),
        lambda p: p.__setitem__("manifest_sha256", "f" * 64),
    ]:
        p2 = copy.deepcopy(pkt); mut(p2)
        with pytest.raises(ValueError):
            verify_and_reduce(p2, **kw)
