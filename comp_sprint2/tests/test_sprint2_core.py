"""Unit & RSO adversarial tests for Sprint 2 (AST sandbox, hardened 3-seed reducer, Track S2-A & S2-B)."""
from __future__ import annotations

import copy
import pytest

from rso.adversary import attacks as X, core as K

from comp_sprint.circuit import verify_truth_tables
from comp_sprint2.reducer_s2 import (
    compute_row_sha256,
    compute_summary,
    evaluate_claim2_detector,
    make_row,
    verify_and_reduce,
)
from comp_sprint2.s2a_benchmarks import build_s2a_benchmarks, s2a_manifest_sha256
from comp_sprint2.s2a_engine import (
    build_s2a_a3_artifact,
    build_s2a_a5_sham_artifact,
    synthesize_s2a_with_artifact,
)
from comp_sprint2.s2b_benchmarks import build_s2b_benchmarks, s2b_manifest_sha256
from comp_sprint2.s2b_bv import BVBuilder, simplify_bv_with_z3_industry, verify_bv_equiv_z3
from comp_sprint2.s2b_engine import (
    build_s2b_a3_artifact,
    build_s2b_a5_sham_artifact,
    optimize_s2b_with_artifact,
)
from comp_sprint2.sandbox_exec import AlgoArtifact, AlgoPass, validate_algo_source


def test_sandbox_blocks_unsafe_code_and_accepts_valid_pass():
    for bad in (
        "import os\ndef optimize(c, n, t, s, d): return c",
        "def optimize(c, n, t, s, d): return open('x')",
        "def optimize(c, n, t, s, d): return ().__class__.__bases__",
        "def optimize(c, n, t, s, d): return eval('1+1')",
        "def optimize(c, n, t, s, d): return getattr(c, 'gates')",
        "def wrong_name(c): return c",
    ):
        with pytest.raises(ValueError):
            validate_algo_source(bad)

    p = AlgoPass.from_source("noop", "S2A_XAG", "def optimize(circ, n, t, s, d):\n    return circ", origin="test")
    art = AlgoArtifact(arm="TEST", track="S2A_XAG", generation=1, passes=(p,))
    rt = AlgoArtifact.from_dict(art.to_dict())
    assert rt.sha256() == art.sha256()


def test_s2a_benchmarks_deterministic_and_engine_exact():
    s1 = build_s2a_benchmarks()
    s2 = build_s2a_benchmarks()
    assert s2a_manifest_sha256(s1) == s2a_manifest_sha256(s2)
    assert {k: len(v) for k, v in s1.items()} == {
        "s2a_dev_struct": 12,
        "s2a_dev_proc": 12,
        "s2a_hold_struct": 10,
        "s2a_hold_proc_shared": 10,
        "s2a_hold_proc_comp": 8,
    }
    # Verify A0, A3, A5 exactness and monotonicity on a dev task
    t = s1["s2a_dev_struct"][0]
    c0, _ = synthesize_s2a_with_artifact(t.n_inputs, t.targets, None, seed=0)
    c3, _ = synthesize_s2a_with_artifact(t.n_inputs, t.targets, build_s2a_a3_artifact(), seed=0, time_budget_sec=0.3)
    c5, _ = synthesize_s2a_with_artifact(t.n_inputs, t.targets, build_s2a_a5_sham_artifact(), seed=0, time_budget_sec=0.2)
    assert verify_truth_tables(c0, t.targets)
    assert verify_truth_tables(c3, t.targets) and c3.gate_count() <= c0.gate_count()
    assert verify_truth_tables(c5, t.targets) and c5.gate_count() <= c0.gate_count()


def test_s2b_benchmarks_z3_exact_and_engine_monotonic():
    s1 = build_s2b_benchmarks()
    s2 = build_s2b_benchmarks()
    assert s2b_manifest_sha256(s1) == s2b_manifest_sha256(s2)
    assert {k: len(v) for k, v in s1.items()} == {
        "s2b_dev_struct": 12,
        "s2b_dev_proc": 12,
        "s2b_hold_struct": 12,
        "s2b_hold_proc_mba": 10,
        "s2b_hold_proc_comp": 10,
    }
    # Verify MBA add task compresses cleanly with A3 CEGIS & Z3 proof
    t = s1["s2b_dev_struct"][0]  # MBA x+y -> 1 op!
    p0, _ = optimize_s2b_with_artifact(t.spec, None, seed=0)
    p1 = simplify_bv_with_z3_industry(t.spec)
    p3, _ = optimize_s2b_with_artifact(t.spec, build_s2b_a3_artifact(), seed=0, time_budget_sec=0.5)
    p5, _ = optimize_s2b_with_artifact(t.spec, build_s2b_a5_sham_artifact(), seed=0, time_budget_sec=0.2)
    assert verify_bv_equiv_z3(t.spec, p0)[0]
    assert verify_bv_equiv_z3(t.spec, p1)[0]
    assert verify_bv_equiv_z3(t.spec, p3)[0] and p3.op_count() == 1
    assert verify_bv_equiv_z3(t.spec, p5)[0] and p5.op_count() <= p0.op_count()

    # Unsound candidate MUST be rejected by Z3
    b_bad = BVBuilder(16, 2)
    bad_prog = b_bad.build(b_bad.op("XOR", 0, 1))
    ok, ce = verify_bv_equiv_z3(t.spec, bad_prog)
    assert ok is False and ce is not None


def test_sprint2_rso_adversarial_kit_all_6_attacks_rejected():
    suites = build_s2b_benchmarks()
    sub_suites = {"s2b_dev_struct": suites["s2b_dev_struct"][:4]}
    man = s2b_manifest_sha256(sub_suites)
    arms = ("A0_BASE", "A2_PRIOR_ONLY", "A4_MG_UNPLUGGED", "A5_SHAM")
    seeds = (0, 1, 2)
    rows = []
    for arm in arms:
        for t in sub_suites["s2b_dev_struct"]:
            for sd in seeds:
                rows.append(make_row(
                    arm=arm, suite="s2b_dev_struct", task_id=t.task_id,
                    stratum=t.stratum, split=t.split, seed=sd,
                    spec_sha256=t.sha256(), cost=t.spec.op_count(),
                    verified_exact=True, solution_sha256=t.spec.sha256(),
                ))
    clean = {"manifest_sha256": man, "summary": compute_summary(rows), "rows": rows}
    ok = verify_and_reduce(
        clean, canonical_suites=sub_suites, canonical_manifest_sha256=man,
        expected_arms=arms, expected_suites=("s2b_dev_struct",), expected_seeds=seeds,
    )
    assert ok["licenses_verdict"] is True

    def _judge(atk):
        changed = X.fingerprint(atk) != X.fingerprint(clean)
        try:
            r = verify_and_reduce(
                atk, canonical_suites=sub_suites, canonical_manifest_sha256=man,
                expected_arms=arms, expected_suites=("s2b_dev_struct",), expected_seeds=seeds,
            )
            return K.judge(r["licenses_verdict"], "accepted", changed)
        except ValueError as exc:
            return K.judge(False, f"raised ValueError: {exc}", changed)

    def v_drop():
        a = copy.deepcopy(clean); a["rows"] = X.drop(clean["rows"], 0); return _judge(a)
    def v_dup():
        a = copy.deepcopy(clean); a["rows"] = X.duplicate(clean["rows"], 0, 1); return _judge(a)
    def v_rw_sum():
        return _judge(X.rewrite_derived(clean, lambda p: p["summary"]["A4_MG_UNPLUGGED"]["s2b_dev_struct"].__setitem__("mean_median_cost", 0.5), lambda p: None))
    def v_rw_single_seed():
        def rw(p): p["rows"][0]["cost"] = 1
        def rb(p): p["rows"][0]["row_sha256"] = compute_row_sha256(p["rows"][0])
        return _judge(X.rewrite_derived(clean, rw, rb))
    def v_scrub():
        a = copy.deepcopy(clean); a["rows"][0] = X.scrub_answer(clean["rows"][0], ["spec_sha256"], mode="corrupt"); return _judge(a)
    def v_const():
        c_fn = X.constant_detector(True)
        real = evaluate_claim2_detector(clean["summary"], "A4_MG_UNPLUGGED", "s2b_dev_struct")
        return K.judge(not ((real is False) and (c_fn(clean["summary"]) is True)), f"real={real}", True)

    res = K.run_variants(
        "comp_sprint2_hardened_3seed",
        [
            ("DROP", "drop_row_0", v_drop),
            ("DUPLICATE", "dup_row_0_over_1", v_dup),
            ("REWRITE_DERIVED", "tamper_summary", v_rw_sum),
            ("REWRITE_DERIVED", "tamper_single_seed_rebind_hash", v_rw_single_seed),
            ("SCRUB_ANSWER", "corrupt_spec_sha256", v_scrub),
            ("CONSTANT", "constant_claim2_detector", v_const),
        ],
        {},
    )
    assert len(res) == 6
    for r in res:
        assert r["verdict"] == "REJECTED", f"Attack {r['attack']}/{r['variant']} was {r['verdict']}: {r}"
