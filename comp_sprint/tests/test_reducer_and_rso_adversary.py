"""RSO Adversarial Kit integration test for comp_sprint.reducer (zero edits to frozen rso/).

Exercises ALL FIVE RSO attacks (DROP, DUPLICATE, REWRITE_DERIVED, CONSTANT, SCRUB_ANSWER)
through `rso.adversary.attacks` and `rso.adversary.core.run_variants`, asserting:
  0 SURVIVED, 0 VACUOUS, 0 ERROR.
"""
from __future__ import annotations

import copy

from rso.adversary import attacks as X, core as K

from comp_sprint.benchmarks import build_all_benchmarks, manifest_sha256
from comp_sprint.reducer import (
    compute_row_sha256,
    compute_summary,
    evaluate_claim2_detector,
    make_row,
    verify_and_reduce,
)
from comp_sprint.synth_base import synthesize_with_library

_TEST_SUITES = ("holdout_structured",)
_TEST_ARMS = ("A0_BASE", "A3_ZERO_LLM", "A5_SHAM")
_TEST_SEEDS = (0, 1, 2)


def _build_clean_mini_packet():
    suites = build_all_benchmarks()
    rows = []
    for arm in _TEST_ARMS:
        for task in suites["holdout_structured"]:
            for sd in _TEST_SEEDS:
                c = synthesize_with_library(task.n_inputs, task.targets, library=(), budget=400, seed=sd)
                rows.append(make_row(
                    arm=arm, suite="holdout_structured", task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=c.gate_count(),
                    and_count=c.and_count(), xor_count=c.xor_count(),
                    verified_exact=True, circuit_sha256=c.sha256(),
                ))
    return {
        "manifest_sha256": manifest_sha256(suites),
        "summary": compute_summary(rows),
        "rows": rows,
    }


def _judge_packet(attacked, original):
    changed = X.fingerprint(attacked) != X.fingerprint(original)
    try:
        res = verify_and_reduce(
            attacked,
            expected_arms=_TEST_ARMS,
            expected_suites=_TEST_SUITES,
            expected_seeds=_TEST_SEEDS,
        )
        return K.judge(res["licenses_verdict"], "accepted", changed)
    except ValueError as exc:
        return K.judge(False, f"raised ValueError: {exc}", changed)


def test_rso_adversarial_kit_all_five_attacks_rejected():
    clean = _build_clean_mini_packet()
    # Sanity: clean packet passes
    ok = verify_and_reduce(clean, _TEST_ARMS, _TEST_SUITES, _TEST_SEEDS)
    assert ok["licenses_verdict"] is True

    def v_drop():
        atk = copy.deepcopy(clean)
        atk["rows"] = X.drop(clean["rows"], 0)
        return _judge_packet(atk, clean)

    def v_duplicate():
        atk = copy.deepcopy(clean)
        atk["rows"] = X.duplicate(clean["rows"], src=0, dst=1)
        return _judge_packet(atk, clean)

    def v_rewrite_derived_summary():
        def rewrite(p):
            p["summary"]["A3_ZERO_LLM"]["holdout_structured"]["mean_median_gates"] = 1.0

        def rebind(p):
            # Attacker tampers summary without changing raw rows
            pass

        atk = X.rewrite_derived(clean, rewrite, rebind)
        return _judge_packet(atk, clean)

    def v_rewrite_derived_row_rebound():
        def rewrite(p):
            p["rows"][0]["gate_count"] = 1
            p["rows"][0]["and_count"] = 1
            p["rows"][0]["xor_count"] = 0

        def rebind(p):
            # Attacker even recomputes row_sha256! Reducer must catch summary mismatch OR
            # if attacker omits summary, check that re-binding row without summary still triggers mismatch
            p["rows"][0]["row_sha256"] = compute_row_sha256(p["rows"][0])

        atk = X.rewrite_derived(clean, rewrite, rebind)
        return _judge_packet(atk, clean)

    def v_scrub_answer():
        atk = copy.deepcopy(clean)
        atk["rows"][0] = X.scrub_answer(clean["rows"][0], ["targets_hex"], mode="corrupt")
        return _judge_packet(atk, clean)

    def v_constant_detector():
        # Verify our Claim-2 detector is NOT a constant always-True rule:
        # On a null summary (all arms equal), real detector MUST return False while constant(True) returns True.
        const_fn = X.constant_detector(True)
        real_on_null = evaluate_claim2_detector(clean["summary"], "A3_ZERO_LLM", "holdout_structured")
        const_on_null = const_fn(clean["summary"])
        # Rejected iff real detector says False on null while constant counterfeit says True
        refused_counterfeit = (real_on_null is False) and (const_on_null is True)
        return K.judge(not refused_counterfeit, f"real={real_on_null} const={const_on_null}", True)

    target_spec = {
        "campaign": "comp_sprint_phase2",
        "summary": "Track 3B-Boolean Phase 2/3 tamper-evident reducer",
        "source": "comp_sprint/reducer.py",
        "variants": [
            ("DROP", "drop_row_0", v_drop),
            ("DUPLICATE", "duplicate_row_0_over_1", v_duplicate),
            ("REWRITE_DERIVED", "tamper_summary", v_rewrite_derived_summary),
            ("REWRITE_DERIVED", "tamper_row_rebind_hash", v_rewrite_derived_row_rebound),
            ("SCRUB_ANSWER", "corrupt_targets_hex", v_scrub_answer),
            ("CONSTANT", "constant_claim2_detector_on_null", v_constant_detector),
        ],
        "not_applicable": {},
    }

    results = K.run_variants(
        "comp_sprint_phase2",
        target_spec["variants"],
        target_spec["not_applicable"],
    )
    assert len(results) == 6
    for r in results:
        assert r["verdict"] == "REJECTED", f"Attack {r['attack']}/{r['variant']} was {r['verdict']}: {r}"
