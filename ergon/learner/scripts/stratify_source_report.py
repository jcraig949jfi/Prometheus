"""Deterministic stratified sampling for source_report calibration claims.

Authority: `ergon/learner/v1_0_plans/source_report_stratification_spec.md`
+ Aporia adjudication ticket
`T-2026-05-15-aporia-to-ergon-stratification-design-confirmed-7-questions-adjudicated-ship-stratify-source-report-py`
(P1, 2026-05-15, ship-greenlight explicit).

Implements Q1-Q7 adjudicated design:
- Q1 ACCEPTED: structured-object rule shape.
- Q2 ACCEPTED: Tier-1 strata_classifier="inline" only.
- Q3 ACCEPTED: under_minimum_policy="include_all" preserves source breadth.
- Q4 ACCEPTED: over_target_policy="cap_proportional" preserves relative
  representation.
- Q5 SELECTIVE ESCALATION: 3 conditions raise StratificationRuleError;
  everything else stays in warnings.
- Q6 ACCEPTED with optional refinement: seed input = sorted-candidate-IDs
  PLUS rule._schema_version + rule.strata_field, so same candidates with
  a different rule version yield a different seed.
- Q7 ACCEPTED: Tier-1 supports one rule per call; multi-rule composition
  is deferred to Tier-2.
"""
from __future__ import annotations

import dataclasses
import hashlib
import random
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


_UNKNOWN_BUCKET = "_unknown"
_UNKNOWN_FRACTION_LIMIT = 0.05  # Q5 exception threshold
_VALID_TARGET_STATUSES = frozenset(("in_range", "under", "over_capped"))


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class StratificationRuleError(ValueError):
    """Raised when a stratification rule cannot meaningfully apply.

    Per Aporia Q5 adjudication, raised on:
    - `_unknown` bucket > 5% of input (rule shape is wrong)
    - Zero candidates with strata_field populated (rule cannot apply)
    - All candidates fall into single stratum (no stratification possible)

    NOT raised on below-minimum strata or over-target caps — those stay in
    StratifiedDraw.warnings.
    """


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class StratifiedDraw:
    """Result of a single stratify() call. Frozen for downstream safety."""
    drawn: List[Dict[str, Any]]
    per_stratum_yield: Dict[str, int]
    per_stratum_input: Dict[str, int]
    target_total_status: str
    warnings: List[str]
    seed_used: int
    rule_applied: Dict[str, Any]


# ---------------------------------------------------------------------------
# Rule validation
# ---------------------------------------------------------------------------


_RULE_REQUIRED_KEYS = (
    "_schema_version", "strata_field", "strata_classifier",
    "strata_labels", "draws_per_stratum", "target_total",
    "seed_basis", "tie_break", "under_minimum_policy",
    "over_target_policy", "source_report_pointer",
)
_VALID_UNDER_MIN_POLICIES = frozenset(("include_all", "escalate"))
_VALID_OVER_TARGET_POLICIES = frozenset(
    ("cap_proportional", "cap_uniform", "escalate"),
)


def _validate_rule(rule: Dict[str, Any]) -> None:
    """Sanity-check the rule shape; raise on misconfiguration."""
    missing = [k for k in _RULE_REQUIRED_KEYS if k not in rule]
    if missing:
        raise StratificationRuleError(
            f"rule missing required keys: {sorted(missing)}",
        )
    if rule["strata_classifier"] != "inline":
        raise StratificationRuleError(
            f"Tier-1 supports only strata_classifier='inline'; got "
            f"{rule['strata_classifier']!r}. external_function and enum "
            f"classifiers are deferred to Tier-2 per Q2 adjudication.",
        )
    if rule["seed_basis"] != "input_hash":
        raise StratificationRuleError(
            f"Tier-1 supports only seed_basis='input_hash'; got "
            f"{rule['seed_basis']!r}.",
        )
    if rule["tie_break"] != "first_after_seeded_shuffle":
        raise StratificationRuleError(
            f"Tier-1 supports only tie_break='first_after_seeded_shuffle'; "
            f"got {rule['tie_break']!r}.",
        )
    if rule["under_minimum_policy"] not in _VALID_UNDER_MIN_POLICIES:
        raise StratificationRuleError(
            f"under_minimum_policy must be one of "
            f"{sorted(_VALID_UNDER_MIN_POLICIES)}; got "
            f"{rule['under_minimum_policy']!r}.",
        )
    if rule["over_target_policy"] not in _VALID_OVER_TARGET_POLICIES:
        raise StratificationRuleError(
            f"over_target_policy must be one of "
            f"{sorted(_VALID_OVER_TARGET_POLICIES)}; got "
            f"{rule['over_target_policy']!r}.",
        )


# ---------------------------------------------------------------------------
# Seed derivation (Q6 refinement: include rule metadata)
# ---------------------------------------------------------------------------


def _compute_seed(candidates: List[Dict[str, Any]], rule: Dict[str, Any]) -> int:
    """Derive 64-bit seed from sorted candidate IDs plus rule metadata.

    Q6 refinement: same candidates with a different rule version or
    strata_field produce a different seed — `same input` is candidate-set
    AND rule-config, not just candidate-set.
    """
    sorted_ids = sorted(c["id"] for c in candidates)
    seed_input = "\n".join(sorted_ids)
    # Q6 refinement: include rule metadata in seed input.
    seed_input += f"|{rule['_schema_version']}|{rule['strata_field']}"
    input_hash = hashlib.sha256(seed_input.encode("ascii")).hexdigest()
    return int(input_hash[:16], 16)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def _dedupe(
    candidates: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], int]:
    """First-seen-wins de-dup by `id` field."""
    seen: set = set()
    deduped: List[Dict[str, Any]] = []
    dup_count = 0
    for c in candidates:
        cid = c["id"]
        if cid in seen:
            dup_count += 1
            continue
        seen.add(cid)
        deduped.append(c)
    return deduped, dup_count


# ---------------------------------------------------------------------------
# Classification into strata buckets
# ---------------------------------------------------------------------------


def _classify(
    candidates: List[Dict[str, Any]], rule: Dict[str, Any],
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Bucket candidates by rule.strata_field value against rule.strata_labels.

    Candidates missing the field OR with values not in strata_labels go to
    `_unknown`. Returns (buckets, missing_field_count).
    """
    strata_field = rule["strata_field"]
    strata_labels = set(rule["strata_labels"])
    buckets: Dict[str, List[Dict[str, Any]]] = {
        label: [] for label in rule["strata_labels"]
    }
    buckets[_UNKNOWN_BUCKET] = []
    missing_field = 0
    for c in candidates:
        v = c.get(strata_field)
        if v is None:
            missing_field += 1
            buckets[_UNKNOWN_BUCKET].append(c)
        elif v in strata_labels:
            buckets[v].append(c)
        else:
            buckets[_UNKNOWN_BUCKET].append(c)
    return buckets, missing_field


# ---------------------------------------------------------------------------
# Per-stratum draw
# ---------------------------------------------------------------------------


def _draw_per_stratum(
    buckets: Dict[str, List[Dict[str, Any]]],
    rule: Dict[str, Any],
    rng: random.Random,
) -> tuple[Dict[str, List[Dict[str, Any]]], List[str]]:
    """Apply per-stratum min/max draws; respect under_minimum_policy."""
    min_draws = rule["draws_per_stratum"]["min"]
    max_draws = rule["draws_per_stratum"]["max"]
    drawn_per_stratum: Dict[str, List[Dict[str, Any]]] = {}
    warnings: List[str] = []

    for label in rule["strata_labels"]:
        in_stratum = buckets.get(label, [])
        if len(in_stratum) == 0:
            drawn_per_stratum[label] = []
            warnings.append(f"stratum {label!r} has 0 candidates")
            continue
        if len(in_stratum) < min_draws:
            policy = rule["under_minimum_policy"]
            if policy == "include_all":
                drawn_per_stratum[label] = list(in_stratum)
                warnings.append(
                    f"stratum {label!r} has {len(in_stratum)} candidates "
                    f"(< min {min_draws}); include_all applied",
                )
                continue
            # policy == "escalate" — validated upstream
            raise StratificationRuleError(
                f"stratum {label!r} has {len(in_stratum)} candidates "
                f"(< min {min_draws}); under_minimum_policy=escalate",
            )
        # len >= min: shuffle (seeded) and take up to max
        shuffled = list(in_stratum)
        rng.shuffle(shuffled)
        target = min(len(shuffled), max_draws)
        drawn_per_stratum[label] = shuffled[:target]
    return drawn_per_stratum, warnings


# ---------------------------------------------------------------------------
# Target-total cap
# ---------------------------------------------------------------------------


def _apply_target_cap(
    drawn_per_stratum: Dict[str, List[Dict[str, Any]]],
    rule: Dict[str, Any],
) -> tuple[Dict[str, List[Dict[str, Any]]], List[str], str]:
    """Apply target_total cap per over_target_policy."""
    target_min = rule["target_total"]["min"]
    target_max = rule["target_total"]["max"]
    total = sum(len(picks) for picks in drawn_per_stratum.values())
    warnings: List[str] = []

    if target_min <= total <= target_max:
        return drawn_per_stratum, warnings, "in_range"
    if total < target_min:
        warnings.append(
            f"total draw {total} < target_total.min {target_min}; "
            f"not capped (under-target is informational, not corrected)",
        )
        return drawn_per_stratum, warnings, "under"

    # total > target_max
    policy = rule["over_target_policy"]
    if policy == "cap_proportional":
        scale = target_max / total
        capped: Dict[str, List[Dict[str, Any]]] = {}
        for label, picks in drawn_per_stratum.items():
            new_count = max(0, int(len(picks) * scale))
            capped[label] = picks[:new_count]
        warnings.append(
            f"total draw {total} > target_total.max {target_max}; "
            f"cap_proportional applied (scale={scale:.4f})",
        )
        return capped, warnings, "over_capped"
    if policy == "cap_uniform":
        num_strata = sum(1 for picks in drawn_per_stratum.values() if picks)
        if num_strata == 0:
            return drawn_per_stratum, warnings, "over_capped"
        per_stratum_cap = target_max // num_strata
        capped = {
            label: picks[:per_stratum_cap]
            for label, picks in drawn_per_stratum.items()
        }
        warnings.append(
            f"total draw {total} > target_total.max {target_max}; "
            f"cap_uniform applied (per_stratum_cap={per_stratum_cap})",
        )
        return capped, warnings, "over_capped"
    # policy == "escalate" — validated upstream
    raise StratificationRuleError(
        f"total draw {total} > target_total.max {target_max}; "
        f"over_target_policy=escalate",
    )


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def stratify(
    candidates: List[Dict[str, Any]],
    rule: Dict[str, Any],
) -> StratifiedDraw:
    """Apply a stratification rule to candidates; return deterministic draw.

    Args:
        candidates: list of candidate dicts. Each MUST have an `id` field
            (string, unique within the call). Each candidate's value of
            `rule["strata_field"]` is read inline (Tier-1).
        rule: stratification_rule object per spec §2.1.

    Returns:
        StratifiedDraw with selected subset, per-stratum yields,
        target-total status, warnings, seed_used, and rule echo.

    Raises:
        StratificationRuleError: when the rule cannot meaningfully apply
            (Q5 selective escalation): _unknown bucket > 5% of input;
            zero candidates with strata_field populated; all candidates
            fall into a single stratum.
    """
    _validate_rule(rule)

    if not candidates:
        raise StratificationRuleError(
            "candidates list is empty; rule cannot apply",
        )

    candidates_clean, dup_count = _dedupe(candidates)
    warnings: List[str] = []
    if dup_count > 0:
        warnings.append(
            f"de-duplicated {dup_count} candidates by id "
            f"(first-seen-wins)",
        )

    buckets, missing_field = _classify(candidates_clean, rule)

    # Q5 exception: zero candidates with strata_field populated.
    if missing_field == len(candidates_clean):
        raise StratificationRuleError(
            f"zero candidates have strata_field "
            f"{rule['strata_field']!r} populated; rule cannot apply",
        )

    # Q5 exception: _unknown > 5% of input.
    unknown_count = len(buckets[_UNKNOWN_BUCKET])
    unknown_fraction = unknown_count / len(candidates_clean)
    if unknown_fraction > _UNKNOWN_FRACTION_LIMIT:
        raise StratificationRuleError(
            f"_unknown bucket holds {unknown_count} of "
            f"{len(candidates_clean)} candidates "
            f"({unknown_fraction:.1%} > 5%); rule shape needs revision "
            f"(strata_field or strata_labels wrong)",
        )
    if unknown_count > 0:
        warnings.append(
            f"_unknown bucket holds {unknown_count} candidates "
            f"({unknown_fraction:.1%}); within 5% tolerance",
        )

    # Q5 exception: all candidates in single stratum.
    populated = [
        label for label in rule["strata_labels"]
        if buckets[label]
    ]
    if len(populated) == 1:
        raise StratificationRuleError(
            f"all candidates fall into single stratum "
            f"{populated[0]!r}; no stratification possible",
        )

    seed = _compute_seed(candidates_clean, rule)
    rng = random.Random(seed)

    drawn_per_stratum, draw_warnings = _draw_per_stratum(buckets, rule, rng)
    warnings.extend(draw_warnings)

    drawn_per_stratum, cap_warnings, target_status = _apply_target_cap(
        drawn_per_stratum, rule,
    )
    warnings.extend(cap_warnings)

    drawn: List[Dict[str, Any]] = []
    per_stratum_yield: Dict[str, int] = {}
    for label in rule["strata_labels"]:
        picks = drawn_per_stratum.get(label, [])
        drawn.extend(picks)
        per_stratum_yield[label] = len(picks)

    per_stratum_input: Dict[str, int] = {
        label: len(buckets.get(label, []))
        for label in rule["strata_labels"]
    }
    per_stratum_input[_UNKNOWN_BUCKET] = unknown_count

    return StratifiedDraw(
        drawn=drawn,
        per_stratum_yield=per_stratum_yield,
        per_stratum_input=per_stratum_input,
        target_total_status=target_status,
        warnings=warnings,
        seed_used=seed,
        rule_applied=dict(rule),
    )
