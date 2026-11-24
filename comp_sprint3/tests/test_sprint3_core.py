"""Core unit tests for Sprint 3: Laws 1, 2, 3 + Hardened 3-Seed RSO 6/6 Audit."""
from __future__ import annotations

import copy

import pytest

from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.s3_benchmarks import build_s3_benchmarks, s3_manifest_sha256
from comp_sprint3.s3_engine import build_s3_a3_artifact, build_s3_a5_sham_artifact, synthesize_s3_with_artifact
from comp_sprint3.sandbox_s3 import (
    CompositionalAlgoArtifact,
    LibModule,
    knockout_generations,
    validate_module_source,
)
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats


def test_law1_sandbox_blocks_time_and_infinite_loops_deterministically():
    # 1. `time` is not allowed / not injected, imports & bare except blocked
    for bad in [
        "import time\ndef f(): return 1",
        "def f(x):\n    try:\n        return x\n    except:\n        return 0",
        "def f(x): return x.__class__",
        "def f(): return eval('1+1')",
    ]:
        with pytest.raises(ValueError):
            validate_module_source(bad)

    # 2. Infinite loop inside `except Exception:` MUST still terminate via BudgetExhausted(BaseException)!
    inf_mod = LibModule.from_source(
        "inf_mod", 0,
        "def burn(circ):\n"
        "    try:\n"
        "        while True:\n"
        "            x = 1 + 1\n"
        "    except Exception:\n"
        "        while True:\n"
        "            x = 2 + 2\n"
        "    return circ\n",
    )
    orch = LibModule.from_source(
        "orch", 0,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    return lib.burn(circ)\n",
        required_fn="solve",
    )
    art = CompositionalAlgoArtifact("TEST", "S3_XAG_COMP", 0, (inf_mod,), orch)
    suites = build_s3_benchmarks()
    t0 = suites["s3_train_g1"][0]
    c1, m1 = synthesize_s3_with_artifact(t0.n_inputs, t0.targets, art, seed=0, op_budget=500)
    c2, m2 = synthesize_s3_with_artifact(t0.n_inputs, t0.targets, art, seed=0, op_budget=500)
    assert m1["status"] == "budget_exhausted"
    assert m1["ops_spent"] == 500
    assert c1.sha256() == c2.sha256()
    assert m1["ops_spent"] == m2["ops_spent"]


def test_law1_zero_jitter_determinism_on_a3_and_a5():
    suites = build_s3_benchmarks()
    t = suites["s3_hold_struct"][0]
    a3 = build_s3_a3_artifact()
    a5 = build_s3_a5_sham_artifact()
    for art in (a3, a5):
        c1, m1 = synthesize_s3_with_artifact(t.n_inputs, t.targets, art, seed=1, op_budget=20_000)
        c2, m2 = synthesize_s3_with_artifact(t.n_inputs, t.targets, art, seed=1, op_budget=20_000)
        assert c1.gate_count() == c2.gate_count()
        assert c1.sha256() == c2.sha256()
        assert m1["ops_spent"] == m2["ops_spent"]


def test_law2_disjoint_170_task_manifest_and_exact_wilcoxon():
    s1 = build_s3_benchmarks()
    s2 = build_s3_benchmarks()
    assert s3_manifest_sha256(s1) == s3_manifest_sha256(s2)
    total = sum(len(v) for v in s1.values())
    assert total == 170
    assert len(s1["s3_val_g1"]) == 25
    assert len(s1["s3_val_g2"]) == 25
    assert len(s1["s3_val_g3"]) == 25
    assert len(s1["s3_hold_struct"]) + len(s1["s3_hold_proc_shared"]) + len(s1["s3_hold_proc_comp"]) == 50

    # Exact Wilcoxon sanity: 6 wins, 0 losses -> p_less = 1/64 = 0.015625, p_two = 0.03125
    st = paired_wilcoxon_stats([-1, -2, -3, -1, -2, -4, 0, 0])
    assert st["wins"] == 6 and st["losses"] == 0 and st["ties"] == 2
    assert abs(st["p_less"] - 0.015625) < 1e-6
    assert abs(st["p_two"] - 0.03125) < 1e-6


def test_law3_compositional_cross_gen_calls_and_knockout_and_rso_6of6():
    mod_g0 = LibModule.from_source(
        "mod_g0_davio", 0,
        "def try_rev_davio(circ, n_inputs, targets):\n"
        "    b = StrashBuilder(n_inputs)\n"
        "    g = b.add_gate('XOR', 0, False, 1, False)\n"
        "    _tmp = b.build([g], prune_dead=True)\n"
        "    cand = davio_synth(n_inputs, targets, list(reversed(range(n_inputs))), greedy=True)\n"
        "    report_best(cand)\n"
        "    return best_solution()\n",
    )
    mod_g1 = LibModule.from_source(
        "mod_g1_caller", 1,
        "def refined_search(circ, n_inputs, targets, seed):\n"
        "    cur = lib.try_rev_davio(circ, n_inputs, targets)\n"
        "    rng = random.Random(seed + 7)\n"
        "    for _ in range(4):\n"
        "        o = list(range(n_inputs))\n"
        "        rng.shuffle(o)\n"
        "        cand = davio_synth(n_inputs, targets, o, greedy=False)\n"
        "        if report_best(cand):\n"
        "            cur = cand\n"
        "    return cur\n",
    )
    orch = LibModule.from_source(
        "orch_g1", 1,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    lib.run('refined_search', circ, n_inputs, targets, seed, op_cap=15000)\n"
        "    return best_solution()\n",
        required_fn="solve",
    )
    art = CompositionalAlgoArtifact("G1", "S3_XAG_COMP", 1, (mod_g0, mod_g1), orch)
    ko = knockout_generations(art, {1}, arm_name="G1_KO_G1")

    suites = build_s3_benchmarks()
    tasks = suites["s3_hold_struct"][:2]
    _, m_full = synthesize_s3_with_artifact(tasks[0].n_inputs, tasks[0].targets, art, seed=0, op_budget=25_000)
    _, m_ko = synthesize_s3_with_artifact(tasks[0].n_inputs, tasks[0].targets, ko, seed=0, op_budget=25_000)
    assert any(k.startswith("g1->g0:try_rev_davio") for k in m_full["cross_gen_calls"])
    assert not m_ko["cross_gen_calls"]
    assert not m_full["fn_errors"], f"Unexpected fn_errors: {m_full['fn_error_msgs']}"

    # Hardened 3-seed RSO 6/6 attack audit on a live mini Sprint 3 packet
    rows = []
    for arm_name, a in [("A0_BASE", None), ("G1", art)]:
        for t in tasks:
            for sd in (0, 1, 2):
                c, _ = synthesize_s3_with_artifact(t.n_inputs, t.targets, a, seed=sd, op_budget=15_000)
                rows.append(make_row(
                    arm=arm_name, suite="s3_hold_struct", task_id=t.task_id, stratum=t.stratum,
                    split=t.split, seed=sd, spec_sha256=t.sha256(), cost=c.gate_count(),
                    verified_exact=True, solution_sha256=c.sha256(),
                ))
    mini_suites = {"s3_hold_struct": tasks}
    msha = s3_manifest_sha256(mini_suites)
    pkt = {"track": "S3_XAG_COMP", "manifest_sha256": msha, "summary": compute_summary(rows), "rows": rows}
    kw = dict(canonical_suites=mini_suites, canonical_manifest_sha256=msha, expected_arms=["A0_BASE", "G1"], expected_suites=["s3_hold_struct"], expected_seeds=[0, 1, 2])
    assert verify_and_reduce(pkt, **kw)["licenses_verdict"] is True

    # All 6 RSO attacks MUST be REJECTED
    # 1. DROP
    p_drop = copy.deepcopy(pkt); p_drop["rows"].pop()
    with pytest.raises(ValueError): verify_and_reduce(p_drop, **kw)
    # 2. DUPLICATE
    p_dup = copy.deepcopy(pkt); p_dup["rows"].append(copy.deepcopy(p_dup["rows"][0]))
    with pytest.raises(ValueError): verify_and_reduce(p_dup, **kw)
    # 3. REWRITE_DERIVED (claimed summary edit)
    p_rew = copy.deepcopy(pkt); p_rew["summary"]["G1"]["s3_hold_struct"]["mean_median_cost"] -= 1.0
    with pytest.raises(ValueError): verify_and_reduce(p_rew, **kw)
    # 4. SINGLE-SEED TAMPER behind median
    p_s1 = copy.deepcopy(pkt); p_s1["rows"][-1]["cost"] = 0
    with pytest.raises(ValueError): verify_and_reduce(p_s1, **kw)
    # 5. SCRUB spec_sha256
    p_sc = copy.deepcopy(pkt); p_sc["rows"][0]["spec_sha256"] = "0" * 64
    with pytest.raises(ValueError): verify_and_reduce(p_sc, **kw)
    # 6. MANIFEST SHA mismatch
    p_mf = copy.deepcopy(pkt); p_mf["manifest_sha256"] = "f" * 64
    with pytest.raises(ValueError): verify_and_reduce(p_mf, **kw)
