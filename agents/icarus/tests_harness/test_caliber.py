"""
Icarus harness caliber suite -- meta-TDD for the instrumentation itself.

Two kinds of tests:
  - REGRESSION GUARDS (must pass now): lock in the anti-Goodhart machinery we
    have shipped. If one of these goes red, we broke a load-bearing instrument.
  - BUILD TARGETS (xfail now): encode the higher-caliber behavior the roadmap
    commits to. They are RED on purpose. When the corresponding roadmap item
    ships, the xfail becomes xpass -- that flip is the signal to convert it
    into a hard assertion.

This file is the executable form of the roadmap
(D:\\Prometheus\\pivot\\prometheus_swarm_roadmap_2026-05-28.md). Deterministic
only -- no LLM calls, so it runs fast and free.

Run: python -m pytest agents/icarus/tests_harness/test_caliber.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ICARUS = Path(r"D:\Prometheus\agents\icarus")
if str(ICARUS) not in sys.path:
    sys.path.insert(0, str(ICARUS))

FIX = ICARUS / "tests_harness" / "fixtures"
GENUINE = FIX / "genuine_r1"
GOODHART = FIX / "goodhart_r1"
BREAKER = FIX / "contract_breaker"
BOOTSTRAP = ICARUS / "cycles" / "cycle_000" / "code"


# ===========================================================================
# REGRESSION GUARDS -- must pass now (lock in shipped instrumentation)
# ===========================================================================

class TestAntiGoodhartShipped:

    def test_contract_lens_catches_cardinality_break(self):
        """Contract Lens must deterministically flag the apply_batch cardinality
        break (the Cycle 14 failure) -- candidate (breaker) vs a genuine parent."""
        from lenses.contract import run_contract_check
        r = run_contract_check(candidate_dir=BREAKER, stable_dir=GENUINE)
        assert r["contract_violation"] is True
        assert r["violation_subclass"] == "input_output_alignment_lost"

    def test_ablation_labels_goodhart_as_non_capability(self):
        """A Goodhart reasoner (visible-pass, blind-fail) must NOT be labeled a
        capability gain over a genuine parent."""
        from ablation import check_decorative
        r = check_decorative(candidate_dir=GOODHART, parent_dir=GENUINE,
                             tier_target="R1")
        assert r["improvement_kind"] != "capability"
        assert r["capability_gain"] is False

    def test_ablation_rewards_genuine_capability(self):
        """A genuine R1 reasoner must beat the bootstrap on the blind holdout."""
        from ablation import check_decorative
        r = check_decorative(candidate_dir=GENUINE, parent_dir=BOOTSTRAP,
                             tier_target="R1")
        assert r["capability_gain"] is True
        assert r["improvement_kind"] == "capability"
        assert r["delta"] > 0

    def test_holdout_distinguishes_goodhart_from_genuine(self):
        """The blind oracle must pass the genuine reasoner more than the Goodhart
        one -- the whole anti-Goodhart premise."""
        from ablation import _holdout_passed
        genuine = _holdout_passed(GENUINE, "R1")["passed"]
        goodhart = _holdout_passed(GOODHART, "R1")["passed"]
        assert genuine > goodhart, (
            f"blind oracle failed to distinguish: genuine={genuine} goodhart={goodhart}"
        )

    def test_taxonomy_classifies_diff_apply_failure(self):
        """A failed apply must classify as diff_apply_failed, detected_by patcher."""
        from taxonomy import classify_deterministic_spine
        spine = classify_deterministic_spine(
            cycle_n=99, tier_target="R1", strategy="minimal", decision="park",
            apply_result={"applied": False, "reason": "corrupt patch at line 7"},
            tdd_result={}, skeptic_report=None, contract_report=None,
            load_bearing_lens="patcher",
        )
        assert spine["failure_class"] == "diff_apply_failed"
        assert spine["detected_by"] == "patcher"

    def test_taxonomy_flags_goodhart_via_holdout(self):
        """A cycle that passes visible TDD but fails the blind holdout
        (goodhart_flag) must be classified metric_shaped / test_passes_by_construction."""
        from taxonomy import classify_deterministic_spine
        spine = classify_deterministic_spine(
            cycle_n=99, tier_target="R1", strategy="minimal", decision="park",
            apply_result={"applied": True, "files_changed": ["reasoner.py"]},
            tdd_result={"all_passed": False, "goodhart_flag": True,
                        "per_source": {"tier_falsification": {"passed": 2, "failed": 0, "errors": 0}}},
            skeptic_report=None, contract_report=None, load_bearing_lens="holdout",
        )
        assert spine["failure_class"] == "metric_shaped"
        assert spine["failure_subclass"] == "test_passes_by_construction"
        assert spine["detected_by"] == "holdout"

    def test_blind_R1_oracle_is_satisfiable(self):
        """Sanity floor: the blind R1 holdout is not impossibly strict -- a
        genuinely-correct reasoner passes all of it. Confirms the bar is
        reachable, so Generator failures are real capability gaps, not an
        unsatisfiable oracle. (Was an xfail build-target; flipped to guard
        after the genuine fixture demonstrated reachability.)"""
        from ablation import _holdout_passed
        r = _holdout_passed(GENUINE, "R1")
        assert r["failed"] == 0 and r["passed"] >= 3, (
            f"genuine reasoner blind R1: passed={r['passed']} failed={r['failed']}"
        )

    def test_debt_ledger_records_and_closes(self):
        """A recorded debt must be retrievable as open, then closable."""
        import debt_ledger, json, tempfile, os
        # Use an isolated ledger path
        orig = debt_ledger.LEDGER
        tmp = Path(tempfile.mkdtemp()) / "debt_ledger.json"
        debt_ledger.LEDGER = tmp
        try:
            d = debt_ledger.record_debt(
                cycle=1, concern="apply_batch drops entries",
                regression_test_to_write="assert len(out)==len(in)",
                source="contract",
            )
            assert d is not None
            assert len(debt_ledger.open_debts()) == 1
            debt_ledger.close_debt(d["debt_id"], cycle=2, how="regression_test_written")
            assert len(debt_ledger.open_debts()) == 0
        finally:
            debt_ledger.LEDGER = orig


# ===========================================================================
# BUILD TARGETS -- xfail now; flip to xpass when the roadmap item ships.
# Each cites its roadmap ID. These are RED on purpose (TDD red state).
# ===========================================================================

class TestHigherCaliberBuildTargets:

    @pytest.mark.xfail(reason="BUILD TARGET IC-9: tier tests must discriminate; "
                              "visible R1 test currently passes on the bootstrap (R0)")
    def test_tier_R1_test_fails_on_bootstrap(self):
        """A valid R1 falsification test must FAIL on the R0 bootstrap reasoner.
        Currently the visible R1 test is too weak and passes on bootstrap."""
        from tier_calibration import _run_test_against
        tier_R1 = BOOTSTRAP / "tests" / "test_tier_R1_falsification.py"
        res = _run_test_against(BOOTSTRAP, tier_R1, holdout=False)
        # caliber bar: bootstrap (R0) must FAIL the R1 test
        assert res["failed"] > 0, "R1 test does not discriminate R1 from R0 baseline"

    @pytest.mark.xfail(reason="BUILD TARGET IC-9 / Q9: the Generator-produced stable "
                              "reasoner must pass the full blind R1 holdout; no promoted "
                              "cycle has cleared it yet")
    def test_current_stable_passes_blind_R1(self):
        """The caliber bar: the CURRENT stable reasoner (what the Generator
        actually produced) passes the blind R1 holdout. Distinct from the
        fixture floor -- this tests the live evolved reasoner, not a hand-written
        one."""
        from ablation import _holdout_passed
        import lineage
        stable_code = Path(lineage.cycle_path(lineage.last_stable_cycle_n())) / "code"
        r = _holdout_passed(stable_code, "R1")
        assert r["failed"] == 0 and r["passed"] >= 3, (
            f"current stable blind R1: passed={r['passed']} failed={r['failed']}"
        )

    @pytest.mark.xfail(reason="BUILD TARGET IC-6: deterministic contract violation "
                              "should HARD-VETO promotion; currently promote-with-debt")
    def test_contract_violation_hard_vetoes_promotion(self):
        """A deterministic contract violation must force decision=park, not
        promote-with-debt. Encodes the IC-6 hard-veto policy."""
        from lenses import _panel
        # The policy hook does not exist yet; this is the red target.
        assert hasattr(_panel, "CONTRACT_HARD_VETO") and _panel.CONTRACT_HARD_VETO is True

    @pytest.mark.xfail(reason="BUILD TARGET IC-13: a revert policy must exist that "
                              "fires on M consecutive metric_shaped promotions")
    def test_revert_policy_exists(self):
        """A quantitative revert trigger must be implemented (consumes the debt/
        kill-cluster/improvement_kind signals that already ship)."""
        import lineage
        assert hasattr(lineage, "should_revert"), "no revert policy implemented yet"

    @pytest.mark.xfail(reason="BUILD TARGET IC-5: high-consensus cycles must trigger "
                              "escalation to a hardened Skeptic")
    def test_consensus_escalation_exists(self):
        from lenses import _panel
        assert hasattr(_panel, "consensus_escalation_triggered")

    @pytest.mark.xfail(reason="BUILD TARGET IC-11 / capability monotonicity: the stable "
                              "lineage's blind-holdout pass count must be non-decreasing")
    def test_stable_lineage_holdout_monotonic(self):
        """Each stable promotion must not regress the blind-holdout pass count.
        Cycle 14 violated this (distractor filtering broke cardinality). The
        caliber bar: monotone non-decreasing holdout over the stable chain."""
        from ablation import _holdout_passed
        import lineage
        stables = lineage.list_stable_cycles(limit=50)
        stables = sorted(stables, key=lambda s: s["cycle_n"])
        counts = [_holdout_passed(Path(s["cycle_path"]) / "code", "R2")["passed"]
                  for s in stables]
        # monotone non-decreasing
        assert all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1)), (
            f"blind-holdout pass count regressed across stable lineage: {counts}"
        )

    @pytest.mark.xfail(reason="BUILD TARGET SW-3: lens panel must be importable from "
                              "the shared library so other agents can reuse it")
    def test_lens_panel_in_shared_library(self):
        import importlib
        importlib.import_module("agents._shared.lenses._panel")
