"""Tests for stratify_source_report.stratify().

Covers Aporia Q5/Q6 adjudications:
- Each policy enum value (under_minimum_policy, over_target_policy).
- Determinism contract (same input + same rule → identical output bytes).
- 3 exception conditions per Q5.
- Q6 refinement: rule metadata in seed → different rule produces
  different seed for same candidate set.
"""
from __future__ import annotations

import dataclasses
import json
from typing import Any, Dict, List

import pytest

from ergon.learner.scripts.stratify_source_report import (
    StratificationRuleError,
    StratifiedDraw,
    _UNKNOWN_BUCKET,
    stratify,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_rule(**overrides: Any) -> Dict[str, Any]:
    """Default Tier-1 rule for KnotInfo-shaped tests."""
    base = {
        "_schema_version": "0.1.0",
        "strata_field": "knot_family",
        "strata_classifier": "inline",
        "strata_labels": ["torus", "hyperbolic", "satellite", "composite"],
        "draws_per_stratum": {"min": 5, "max": 15},
        "target_total": {"min": 50, "max": 100},
        "seed_basis": "input_hash",
        "tie_break": "first_after_seeded_shuffle",
        "under_minimum_policy": "include_all",
        "over_target_policy": "cap_proportional",
        "source_report_pointer": "test:knotinfo",
    }
    base.update(overrides)
    return base


def _make_candidates(
    counts: Dict[str, int], strata_field: str = "knot_family",
) -> List[Dict[str, Any]]:
    """Make N candidates per stratum with deterministic ids."""
    out: List[Dict[str, Any]] = []
    for label, count in counts.items():
        for i in range(count):
            out.append({
                "id": f"c-{label}-{i:04d}",
                strata_field: label,
                "payload": f"candidate {label} {i}",
            })
    return out


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_balanced_strata_within_range(self) -> None:
        """All strata >= min, total within target_total — clean draw."""
        candidates = _make_candidates(
            {"torus": 20, "hyperbolic": 20, "satellite": 20, "composite": 20},
        )
        result = stratify(candidates, _make_rule())
        assert isinstance(result, StratifiedDraw)
        # Each stratum should draw max=15 (within range; total 60).
        assert result.per_stratum_yield == {
            "torus": 15, "hyperbolic": 15, "satellite": 15, "composite": 15,
        }
        assert len(result.drawn) == 60
        assert result.target_total_status == "in_range"
        # No exceptions raised; warnings may exist but no error conditions.
        assert isinstance(result.warnings, list)

    def test_per_stratum_input_count_accurate(self) -> None:
        candidates = _make_candidates(
            {"torus": 47, "hyperbolic": 2731, "satellite": 184, "composite": 16},
        )
        result = stratify(candidates, _make_rule())
        assert result.per_stratum_input["torus"] == 47
        assert result.per_stratum_input["hyperbolic"] == 2731
        assert result.per_stratum_input["satellite"] == 184
        assert result.per_stratum_input["composite"] == 16
        assert result.per_stratum_input[_UNKNOWN_BUCKET] == 0


# ---------------------------------------------------------------------------
# under_minimum_policy
# ---------------------------------------------------------------------------


class TestUnderMinimumPolicy:
    def test_include_all_keeps_below_min_stratum(self) -> None:
        """include_all: stratum with 3 candidates (< min 5) → keep all 3."""
        candidates = _make_candidates(
            {"torus": 3, "hyperbolic": 20, "satellite": 20, "composite": 20},
        )
        result = stratify(candidates, _make_rule(under_minimum_policy="include_all"))
        assert result.per_stratum_yield["torus"] == 3
        # And warning surfaced.
        assert any("torus" in w and "include_all applied" in w
                   for w in result.warnings)

    def test_escalate_raises_on_below_min(self) -> None:
        """escalate: raises rather than including below-min stratum."""
        candidates = _make_candidates(
            {"torus": 3, "hyperbolic": 20, "satellite": 20, "composite": 20},
        )
        rule = _make_rule(under_minimum_policy="escalate")
        with pytest.raises(StratificationRuleError, match="under_minimum_policy=escalate"):
            stratify(candidates, rule)


# ---------------------------------------------------------------------------
# over_target_policy
# ---------------------------------------------------------------------------


class TestOverTargetPolicy:
    def test_cap_proportional_when_over_max(self) -> None:
        """8 strata × 15 = 120 > target_max 100 → proportional cap."""
        # Use a rule with 8 strata so the natural draw exceeds 100.
        rule = _make_rule(
            strata_labels=["a", "b", "c", "d", "e", "f", "g", "h"],
            strata_field="kind",
            over_target_policy="cap_proportional",
        )
        candidates = _make_candidates(
            {l: 30 for l in rule["strata_labels"]},
            strata_field="kind",
        )
        result = stratify(candidates, rule)
        # Each stratum naturally draws 15 → total 120; scale = 100/120 = 0.833...
        # int(15 * 0.833) = 12 per stratum → total 96. Status = over_capped.
        assert result.target_total_status == "over_capped"
        assert sum(result.per_stratum_yield.values()) <= 100
        assert any("cap_proportional applied" in w for w in result.warnings)

    def test_cap_uniform_when_over_max(self) -> None:
        rule = _make_rule(
            strata_labels=["a", "b", "c", "d", "e", "f", "g", "h"],
            strata_field="kind",
            over_target_policy="cap_uniform",
        )
        candidates = _make_candidates(
            {l: 30 for l in rule["strata_labels"]},
            strata_field="kind",
        )
        result = stratify(candidates, rule)
        # 8 strata, target_max 100 → per_stratum_cap = 12. Each stratum = 12.
        for label in rule["strata_labels"]:
            assert result.per_stratum_yield[label] == 12
        assert result.target_total_status == "over_capped"
        assert any("cap_uniform applied" in w for w in result.warnings)

    def test_over_target_escalate_raises(self) -> None:
        rule = _make_rule(
            strata_labels=["a", "b", "c", "d", "e", "f", "g", "h"],
            strata_field="kind",
            over_target_policy="escalate",
        )
        candidates = _make_candidates(
            {l: 30 for l in rule["strata_labels"]},
            strata_field="kind",
        )
        with pytest.raises(StratificationRuleError, match="over_target_policy=escalate"):
            stratify(candidates, rule)


# ---------------------------------------------------------------------------
# target_total status
# ---------------------------------------------------------------------------


class TestTargetTotalStatus:
    def test_under_target_status_when_total_below_min(self) -> None:
        """4 strata × 10 = 40 < target_min 50 → status=under, no cap."""
        candidates = _make_candidates(
            {"torus": 10, "hyperbolic": 10, "satellite": 10, "composite": 10},
        )
        result = stratify(candidates, _make_rule())
        # Each draws 10 (within min..max); total = 40 < 50.
        assert sum(result.per_stratum_yield.values()) == 40
        assert result.target_total_status == "under"
        assert any("< target_total.min" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Q5 exceptions
# ---------------------------------------------------------------------------


class TestQ5Exceptions:
    def test_empty_candidates_raises(self) -> None:
        with pytest.raises(StratificationRuleError, match="empty"):
            stratify([], _make_rule())

    def test_zero_strata_field_populated_raises(self) -> None:
        # Candidates missing the strata_field entirely.
        candidates = [
            {"id": f"c-{i}", "payload": "x"} for i in range(20)
        ]
        with pytest.raises(StratificationRuleError, match="zero candidates have strata_field"):
            stratify(candidates, _make_rule())

    def test_unknown_bucket_over_5pct_raises(self) -> None:
        # 95 valid + 6 unknown = 101 total; 6/101 = 5.94% > 5%.
        candidates = _make_candidates(
            {"torus": 30, "hyperbolic": 30, "satellite": 30, "composite": 5},
        )
        # Add 6 candidates with invalid stratum label.
        candidates.extend([
            {"id": f"c-bad-{i}", "knot_family": "bogus", "payload": "x"}
            for i in range(6)
        ])
        with pytest.raises(StratificationRuleError, match=r"_unknown bucket"):
            stratify(candidates, _make_rule())

    def test_unknown_bucket_under_5pct_is_warning_not_exception(self) -> None:
        # 100 valid + 3 unknown = 103 total; 3/103 = 2.9% < 5%.
        candidates = _make_candidates(
            {"torus": 25, "hyperbolic": 25, "satellite": 25, "composite": 25},
        )
        candidates.extend([
            {"id": f"c-bad-{i}", "knot_family": "bogus", "payload": "x"}
            for i in range(3)
        ])
        result = stratify(candidates, _make_rule())
        assert any("within 5% tolerance" in w for w in result.warnings)

    def test_single_stratum_raises(self) -> None:
        """All candidates in one stratum → cannot stratify."""
        candidates = _make_candidates({"torus": 50})
        with pytest.raises(StratificationRuleError, match="single stratum"):
            stratify(candidates, _make_rule())


# ---------------------------------------------------------------------------
# Determinism (Q6)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_rule_identical_output(self) -> None:
        """Determinism contract: identical drawn list bytes across runs."""
        candidates = _make_candidates(
            {"torus": 20, "hyperbolic": 20, "satellite": 20, "composite": 20},
        )
        rule = _make_rule()
        r1 = stratify(candidates, rule)
        r2 = stratify(candidates, rule)
        assert r1.seed_used == r2.seed_used
        # Compare drawn lists by serializing (lists of dicts).
        assert json.dumps(r1.drawn, sort_keys=True) == json.dumps(
            r2.drawn, sort_keys=True,
        )

    def test_candidate_order_does_not_change_seed(self) -> None:
        """Sorted-by-id seed input → insertion order irrelevant."""
        candidates_a = _make_candidates(
            {"torus": 10, "hyperbolic": 10, "satellite": 10, "composite": 10},
        )
        # Reverse insertion order.
        candidates_b = list(reversed(candidates_a))
        rule = _make_rule()
        r_a = stratify(candidates_a, rule)
        r_b = stratify(candidates_b, rule)
        assert r_a.seed_used == r_b.seed_used

    def test_q6_rule_metadata_changes_seed(self) -> None:
        """Q6 refinement: changing rule._schema_version produces a new seed."""
        candidates = _make_candidates(
            {"torus": 20, "hyperbolic": 20, "satellite": 20, "composite": 20},
        )
        rule_v1 = _make_rule(_schema_version="0.1.0")
        rule_v2 = _make_rule(_schema_version="0.2.0")
        r1 = stratify(candidates, rule_v1)
        r2 = stratify(candidates, rule_v2)
        assert r1.seed_used != r2.seed_used, (
            "Q6 refinement: schema_version must be in seed input"
        )

    def test_q6_strata_field_changes_seed(self) -> None:
        """Q6 refinement: changing rule.strata_field produces a new seed."""
        candidates = _make_candidates(
            {"a": 20, "b": 20, "c": 20, "d": 20}, strata_field="strataA",
        )
        # Same candidates also carry strataB.
        for c in candidates:
            c["strataB"] = c["strataA"]
        rule_a = _make_rule(
            strata_field="strataA", strata_labels=["a", "b", "c", "d"],
        )
        rule_b = _make_rule(
            strata_field="strataB", strata_labels=["a", "b", "c", "d"],
        )
        r_a = stratify(candidates, rule_a)
        r_b = stratify(candidates, rule_b)
        assert r_a.seed_used != r_b.seed_used


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


class TestDeduplication:
    def test_duplicate_ids_first_seen_wins(self) -> None:
        candidates = _make_candidates(
            {"torus": 10, "hyperbolic": 10, "satellite": 10, "composite": 10},
        )
        # Append a duplicate of the first candidate.
        candidates.append(candidates[0])
        result = stratify(candidates, _make_rule())
        assert any("de-duplicated" in w and "1" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Rule validation
# ---------------------------------------------------------------------------


class TestRuleValidation:
    def test_missing_required_key_raises(self) -> None:
        rule = _make_rule()
        del rule["strata_field"]
        with pytest.raises(StratificationRuleError, match="missing required keys"):
            stratify(_make_candidates({"torus": 10}), rule)

    def test_external_function_classifier_rejected_in_tier_1(self) -> None:
        rule = _make_rule(strata_classifier="external_function")
        with pytest.raises(StratificationRuleError, match="strata_classifier='inline'"):
            stratify(_make_candidates({"torus": 10}), rule)

    def test_invalid_under_min_policy_raises(self) -> None:
        rule = _make_rule(under_minimum_policy="bogus")
        with pytest.raises(StratificationRuleError, match="under_minimum_policy"):
            stratify(_make_candidates({"torus": 10}), rule)

    def test_invalid_over_target_policy_raises(self) -> None:
        rule = _make_rule(over_target_policy="bogus")
        with pytest.raises(StratificationRuleError, match="over_target_policy"):
            stratify(_make_candidates({"torus": 10}), rule)
