"""Residue eligibility gate — Layer-1 -> Seam -> Layer-2 contract.

Per Erebos Doctrine v1.0 (pivot/erebos_doctrine_v1_2026-05-27.md)
§"the seam — what crosses from Layer 1 to Layer 2" and
feedback_residue_must_be_navigable_not_logged.md:

> "every reasoning act leaves navigable residue" needs an
> eligibility gate. Failures meeting none of the criteria are
> exhaust, not residue. Logged != navigable.

Without this gate, every Layer-1 failure floods the kill_ledger
and drowns the navigable signal. Phase 1B ITER-35: the gate.

## The four eligibility criteria

A per-emission verdict is ELIGIBLE to cross the seam iff at least
one of these is true:

1. **changes_routing_distribution** — the verdict's kill_pattern
   maps (via kill_pattern_registry.routing_action_for) to a
   routing action different from the current dominant action, OR
   the kill_pattern is novel (never seen in the ledger). Effect:
   the substrate's next plugin choice will be different than it
   would have been without this entry.

2. **localizes_boundary** — the verdict carries a threshold / CI
   bound / posterior spike location / p-value that narrows or
   sharpens a known boundary. Effect: subsequent emissions can
   navigate by the localized boundary.

3. **falsifies_prior_signature** — a prior ledger entry (same
   canonical input_provenance) attested a different kill_pattern,
   OR a prior entry's expected_kill_pattern was unstable across
   re-runs. Effect: previously-trusted residue is downgraded.

4. **adds_tensor_rank** — the (plugin_id, domain, kill_pattern)
   triple is novel in the ledger. Effect: a new coordinate appears
   in the (generator x domain x invariant x confusion_class)
   tensor that Layer 2 will eventually navigate.

A verdict meeting ZERO criteria is **exhaust** — write to a
separate exhaust log, NOT the primary kill_ledger.

## Integration contract

The daemon (Phase 1B ITER-37/38, deferred) constructs a
LedgerContext snapshot BEFORE each eligibility check, populating
only what the four criteria need. The eligibility primitive is
storage-backend independent — it never reads the ledger directly.

## What this gate is NOT

- NOT a quality filter. A PROMOTED Layer-1 verdict can be exhaust
  if it adds no routing / boundary / falsification / rank signal.
- NOT a substitute for kill_pattern_registry routing — it decides
  whether to CROSS the seam, not where to ROUTE next.
- NOT a substitute for cost-instrumentation. A high-cost exhaust
  emission is still exhaust; cost-per-information is a separate
  metric.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from charon.agents.erebos._kill_pattern_registry import routing_action_for


# Criterion names — also the keys in EligibilityVerdict.criteria_met.
CRITERION_ROUTING_CHANGE = "changes_routing_distribution"
CRITERION_BOUNDARY_LOCALIZED = "localizes_boundary"
CRITERION_FALSIFIES_PRIOR = "falsifies_prior_signature"
CRITERION_ADDS_TENSOR_RANK = "adds_tensor_rank"

ALL_CRITERIA = (
    CRITERION_ROUTING_CHANGE,
    CRITERION_BOUNDARY_LOCALIZED,
    CRITERION_FALSIFIES_PRIOR,
    CRITERION_ADDS_TENSOR_RANK,
)


# Verdict-dict field names whose presence signals boundary localization.
# Kept explicit (no regex) so the audit set is auditable. Reflects the
# Phase 1A retrofit emission shapes (BOCPD interior spike, bootstrap CI,
# MC G-test p-value, etc.) and the pre-existing sweep-threshold shapes.
_BOUNDARY_LOCALIZING_FIELDS = frozenset({
    "interior_spike_threshold",
    "interior_spike_value",
    "most_likely_changepoint_threshold",
    "slope_ci_lower",
    "slope_ci_upper",
    "fwer_p_value",
    "p_value_mc",
    "p_value",
    "chi_squared_threshold",
    "posterior_threshold",
    "sweep_thresholds",
    "phase_transition_threshold",
    "boundary_M",
    "boundary_value",
    "ci_lower",
    "ci_upper",
})


@dataclass(frozen=True)
class LedgerContext:
    """Snapshot of ledger state required by the eligibility checks.

    Storage-backend independent: the daemon constructs this once per
    eligibility check by querying whatever the actual kill_ledger
    backend is. The eligibility primitive never touches storage.

    Fields:
        known_kill_patterns: every kp the ledger has seen.
        routing_distribution: kp -> fraction of recent ledger entries
            with that kp. Used to determine the "current dominant
            routing action". Empty dict => no prior entries => any
            kp counts as routing-changing.
        prior_kps_by_input_signature: canonical input signature ->
            list of kps previously observed for that input. The
            signature is daemon-constructed (e.g., sha256 of
            sorted input_provenance JSON, or claim.predicate_handle.
            canonical_form() if present).
        known_plugin_domain_kp_triples: set of (plugin_id, domain, kp)
            triples already present in the ledger. Novelty here
            satisfies adds_tensor_rank.
    """
    known_kill_patterns: frozenset[str] = frozenset()
    routing_distribution: dict[str, float] = field(default_factory=dict)
    prior_kps_by_input_signature: dict[str, list[str]] = field(default_factory=dict)
    known_plugin_domain_kp_triples: frozenset[tuple[str, str, str]] = frozenset()

    @staticmethod
    def empty() -> "LedgerContext":
        """Empty ledger context (first emission, cold-start)."""
        return LedgerContext()


@dataclass(frozen=True)
class EligibilityVerdict:
    """Result of an eligibility check.

    Attributes:
        eligible: True iff at least one criterion was met.
        criteria_met: tuple of criterion names that fired (subset of
            ALL_CRITERIA).
        routing_change_detail: dict describing the routing-change
            check (current action, new action, is_novel). Always
            populated for audit even when the criterion did not fire.
        boundary_detail: same, for boundary localization.
        prior_falsification_detail: same, for prior-signature check.
        tensor_rank_detail: same, for tensor-rank novelty.
        notes: human-readable summary suitable for the exhaust log
            when eligible == False.
    """
    eligible: bool
    criteria_met: tuple[str, ...]
    routing_change_detail: dict
    boundary_detail: dict
    prior_falsification_detail: dict
    tensor_rank_detail: dict
    notes: str = ""


def _check_routing_change(
    new_kp: Optional[str],
    ledger_context: LedgerContext,
) -> tuple[bool, dict]:
    """Did this verdict's kp change the routing distribution?"""
    if new_kp is None:
        # PROMOTED verdicts don't route to a "next plugin"; they're
        # routing-changing only if the substrate previously believed
        # this input always REJECTED with some kp. That check happens
        # in _check_prior_falsification; routing-change here is False.
        return False, {
            "new_kp": None,
            "new_routing_action": None,
            "is_novel_kp": False,
            "current_dominant_kp": None,
            "current_dominant_action": None,
            "fires": False,
            "reason": "PROMOTED verdict has no routing implication",
        }

    new_action = routing_action_for(new_kp)
    is_novel = new_kp not in ledger_context.known_kill_patterns

    if not ledger_context.routing_distribution:
        # Empty ledger: any kp is routing-changing by definition
        return True, {
            "new_kp": new_kp,
            "new_routing_action": new_action,
            "is_novel_kp": is_novel,
            "current_dominant_kp": None,
            "current_dominant_action": None,
            "fires": True,
            "reason": "ledger empty; this kp is the first routing signal",
        }

    current_dominant_kp = max(
        ledger_context.routing_distribution.items(),
        key=lambda kv: kv[1],
    )[0]
    current_dominant_action = routing_action_for(current_dominant_kp)

    action_changes = new_action != current_dominant_action
    fires = is_novel or action_changes

    return fires, {
        "new_kp": new_kp,
        "new_routing_action": new_action,
        "is_novel_kp": is_novel,
        "current_dominant_kp": current_dominant_kp,
        "current_dominant_action": current_dominant_action,
        "fires": fires,
        "reason": (
            "novel kp" if is_novel
            else "routing action differs from current dominant"
            if action_changes
            else "routing action matches current dominant — exhaust"
        ),
    }


def _check_boundary_localized(verdict: dict) -> tuple[bool, dict]:
    """Does the verdict carry a localized boundary signal?"""
    if not isinstance(verdict, dict):
        return False, {
            "verdict_is_dict": False,
            "fields_present": [],
            "fires": False,
            "reason": "verdict not a dict",
        }
    fields_present = sorted(
        f for f in _BOUNDARY_LOCALIZING_FIELDS
        if f in verdict and verdict[f] is not None
    )
    fires = bool(fields_present)
    return fires, {
        "verdict_is_dict": True,
        "fields_present": fields_present,
        "fires": fires,
        "reason": (
            f"boundary fields detected: {fields_present}" if fires
            else f"no fields in {sorted(_BOUNDARY_LOCALIZING_FIELDS)} "
                 f"present in verdict"
        ),
    }


def _check_prior_falsification(
    new_kp: Optional[str],
    input_signature: Optional[str],
    ledger_context: LedgerContext,
) -> tuple[bool, dict]:
    """Does this verdict contradict prior ledger entries on the same input?"""
    if input_signature is None:
        return False, {
            "input_signature": None,
            "prior_kps": [],
            "new_kp": new_kp,
            "fires": False,
            "reason": "no input_signature provided; cannot check prior",
        }
    prior_kps = ledger_context.prior_kps_by_input_signature.get(
        input_signature, []
    )
    if not prior_kps:
        return False, {
            "input_signature": input_signature,
            "prior_kps": [],
            "new_kp": new_kp,
            "fires": False,
            "reason": "no prior entries for this input signature",
        }
    # Prior falsification fires if the new kp is NOT in the set of
    # priors observed for this input. (Includes case where prior was
    # PROMOTED [None] and new is some kp, or vice versa.)
    prior_set = set(prior_kps)
    fires = new_kp not in prior_set
    return fires, {
        "input_signature": input_signature,
        "prior_kps": prior_kps,
        "new_kp": new_kp,
        "fires": fires,
        "reason": (
            f"new kp {new_kp!r} not in prior set {prior_set!r}"
            if fires
            else f"new kp {new_kp!r} matches prior set; no falsification"
        ),
    }


def _check_adds_tensor_rank(
    plugin_id: str,
    domain: str,
    new_kp: Optional[str],
    ledger_context: LedgerContext,
) -> tuple[bool, dict]:
    """Is the (plugin, domain, kp) triple a new tensor coordinate?"""
    # Use string "PROMOTED" as the kp slot for PROMOTED verdicts so
    # PROMOTED on a new (plugin, domain) is still rank-adding.
    triple = (plugin_id, domain, new_kp if new_kp is not None else "PROMOTED")
    is_novel = triple not in ledger_context.known_plugin_domain_kp_triples
    return is_novel, {
        "triple": triple,
        "is_novel": is_novel,
        "fires": is_novel,
        "reason": (
            "novel (plugin, domain, kp) triple"
            if is_novel
            else "triple already present in ledger"
        ),
    }


def assess_residue_eligibility(
    *,
    plugin_id: str,
    new_kill_pattern: Optional[str],
    verdict: dict,
    domain: str,
    ledger_context: LedgerContext,
    input_signature: Optional[str] = None,
) -> EligibilityVerdict:
    """Apply the four eligibility criteria; return per-criterion detail.

    Args:
        plugin_id: id of the generator/loader producing the verdict
            (e.g. 'g11_exception_miner').
        new_kill_pattern: the verdict's kill_pattern (None for
            PROMOTED).
        verdict: the loader's full result dict. Inspected for
            boundary-localizing fields.
        domain: substrate domain label (e.g. 'mahler_non_cyclotomic',
            'BSD', 'OEIS_sleeping_beauties'). The (plugin, domain, kp)
            triple is the tensor-rank coordinate.
        ledger_context: snapshot of ledger state needed by the four
            criteria. Storage-backend independent.
        input_signature: optional canonical signature of the input
            (e.g. predicate_handle.canonical_form() or
            sha256(input_provenance)). Required for the prior-
            falsification check; without it that check returns False.

    Returns:
        EligibilityVerdict. .eligible is True iff >=1 criterion fires.
    """
    routing_fires, routing_detail = _check_routing_change(
        new_kill_pattern, ledger_context
    )
    boundary_fires, boundary_detail = _check_boundary_localized(verdict)
    prior_fires, prior_detail = _check_prior_falsification(
        new_kill_pattern, input_signature, ledger_context
    )
    rank_fires, rank_detail = _check_adds_tensor_rank(
        plugin_id, domain, new_kill_pattern, ledger_context
    )

    criteria_met = []
    if routing_fires:
        criteria_met.append(CRITERION_ROUTING_CHANGE)
    if boundary_fires:
        criteria_met.append(CRITERION_BOUNDARY_LOCALIZED)
    if prior_fires:
        criteria_met.append(CRITERION_FALSIFIES_PRIOR)
    if rank_fires:
        criteria_met.append(CRITERION_ADDS_TENSOR_RANK)

    eligible = bool(criteria_met)
    if eligible:
        notes = (
            f"eligible: {len(criteria_met)} of 4 criteria fired "
            f"({', '.join(criteria_met)})"
        )
    else:
        notes = (
            "exhaust: zero criteria fired — verdict adds no routing "
            "change, no boundary localization, no prior falsification, "
            "no tensor-rank novelty. Write to exhaust log, not "
            "kill_ledger."
        )

    return EligibilityVerdict(
        eligible=eligible,
        criteria_met=tuple(criteria_met),
        routing_change_detail=routing_detail,
        boundary_detail=boundary_detail,
        prior_falsification_detail=prior_detail,
        tensor_rank_detail=rank_detail,
        notes=notes,
    )
