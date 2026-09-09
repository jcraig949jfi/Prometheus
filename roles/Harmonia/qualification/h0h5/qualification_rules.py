"""Harmonia qualification rules for the H0-H5 lanes.  QR-1.0.0  2026-09-08.

Executable rules, not prose. Every gate here is mechanical: no LLM verdict is
consulted anywhere in this module, and none may be.

THE CYCLE (one lane, in order; a lane may not skip a stage)

    0 contract fixtures      the kind's own contract holds on known inputs
    1 positive control       a planted effect of DECLARED SIGN is recovered
    2 negative control       a no-effect dataset does NOT read as support
    3 paired pilot           DISJOINT from confirmation; calibrates the
                             threshold and sizes the blocks
    4 frozen confirmation    plan hashed and committed BEFORE the data opens
    5 effect + uncertainty   paired blocks, simultaneous across primaries
    6 scope-specific decision  SUPPORTED / UNSUPPORTED / INCONCLUSIVE, bounded
                             to the population actually run

TWO AXES, NEVER COLLAPSED (design s6, s8). The release ladder
(SCAFFOLD/ALPHA/BETA/ONE_POINT_ZERO/ONE_POINT_ONE) is a SOFTWARE fact. The
verdict (SUPPORTED/UNSUPPORTED/INCONCLUSIVE) is a SCIENTIFIC fact. A 1.0
implementation may be UNSUPPORTED and that is a completed result. This module
returns the scientific axis only and never blocks a release.

THE INDEPENDENT UNIT (non-negotiable, carried from the repeat-unit ruling)
The unit is the PAIRED (seed x task_block). Generations, mutations, candidates,
CEGIS rounds and oracle calls are WITHIN-unit repeats. They sharpen a block's
estimate and add no independent units. A plan whose declared_n exceeds its
block count is refused by validate_plan.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from itertools import combinations

RULES_VERSION = "QR-1.0.0"

# ---------------------------------------------------------------- decisions

SUPPORTED = "SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"          # evidence AGAINST a practical effect
INCONCLUSIVE = "INCONCLUSIVE"
INELIGIBLE = "INELIGIBLE"            # the design could not have decided

# release ladder, software axis only
LADDER = ["SCAFFOLD", "ALPHA", "BETA", "ONE_POINT_ZERO", "ONE_POINT_ONE"]


@dataclass
class LanePlan:
    """Everything declared BEFORE a lane's pilot. Missing fields are refused."""
    lane: str
    plan_version: str
    unit_definition: str                     # must name seed x task_block
    n_blocks: int                            # independent units, per arm
    assigned_tasks_per_block: int
    denominator_rule: str                    # must be all-assigned
    exclusion_rule: str                      # identical across arms
    retry_rule: str                          # identical across arms
    paired: bool
    primary_contrasts: list                  # names; multiplicity is over these
    practical_threshold: float               # on the solve-fraction scale
    threshold_status: str                    # PROPOSED | FROZEN_FROM_PILOT
    uncertainty_procedure: str               # e.g. paired-block t + Bonferroni
    multiplicity: str                        # NONE | BONFERRONI
    alpha: float = 0.05
    pilot_task_ids: tuple = ()
    confirmation_task_ids: tuple = ()
    notes: str = ""

    def digest(self) -> str:
        return "sha256:" + hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True, default=str).encode()
        ).hexdigest()


class PlanRefused(Exception):
    pass


def validate_plan(p: LanePlan) -> list:
    """Mechanical refusals. Returns the list of satisfied checks; raises on any
    violation. This runs BEFORE a pilot, so every check is knowable in advance."""
    ok = []
    if "seed" not in p.unit_definition or "task_block" not in p.unit_definition:
        raise PlanRefused(
            "unit_definition must name the paired (seed x task_block) unit; "
            "generations/mutations/candidates are never replicates")
    ok.append("unit_is_paired_seed_x_task_block")

    if p.denominator_rule != "all_assigned_tasks":
        raise PlanRefused("denominator_rule must be all_assigned_tasks")
    ok.append("denominator_is_all_assigned")

    if p.exclusion_rule != p.retry_rule.replace("retry", "exclusion") and (
            "identical_across_arms" not in p.exclusion_rule
            or "identical_across_arms" not in p.retry_rule):
        raise PlanRefused(
            "exclusion and retry rules must both be declared identical across arms")
    ok.append("exclusion_and_retry_identical_across_arms")

    if not p.paired:
        raise PlanRefused("H0-H5 lanes are paired designs; unpaired is refused")
    ok.append("paired_contrasts")

    if p.threshold_status not in ("PROPOSED", "FROZEN_FROM_PILOT"):
        raise PlanRefused("threshold_status must be PROPOSED or FROZEN_FROM_PILOT")
    ok.append("threshold_status_declared")

    if set(p.pilot_task_ids) & set(p.confirmation_task_ids):
        raise PlanRefused(
            "pilot and confirmation task sets must be DISJOINT; overlap = %d"
            % len(set(p.pilot_task_ids) & set(p.confirmation_task_ids)))
    ok.append("pilot_confirmation_disjoint")

    if len(p.primary_contrasts) > 1 and p.multiplicity == "NONE":
        raise PlanRefused(
            "%d primary contrasts declared with multiplicity NONE"
            % len(p.primary_contrasts))
    ok.append("multiplicity_handled")

    # HA-1.6: a design states the smallest p its own lattice can produce.
    mp = min_attainable_p_paired(p.n_blocks)
    if mp > p.alpha:
        raise PlanRefused(
            "INELIGIBLE by HA-1.6: %d paired blocks give a minimum attainable "
            "two-sided p of %.4f, above alpha %.3f. The gate cannot fire on any "
            "data. Resize or declare the lane descriptive." % (p.n_blocks, mp, p.alpha))
    ok.append("min_attainable_p_%.4f_le_alpha" % mp)
    return ok


def min_attainable_p_paired(n_blocks: int) -> float:
    """Paired sign-flip permutation lattice: 2 / 2**n."""
    if n_blocks <= 0:
        return 1.0
    if n_blocks > 30:
        return 0.0
    return 2.0 / (2 ** n_blocks)


def min_attainable_p_unpaired(n_a: int, n_b: int) -> float:
    return 2.0 / math.comb(n_a + n_b, n_a)


# ------------------------------------------------------- effect + uncertainty

def _mean(v):
    return sum(v) / len(v)


def _sd(v):
    if len(v) < 2:
        return 0.0
    m = _mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


# two-sided t quantiles at 0.05 and at 0.025 (Bonferroni for 2 contrasts)
_T = {(1, .05): 12.706, (2, .05): 4.303, (3, .05): 3.182, (4, .05): 2.776,
      (5, .05): 2.571, (6, .05): 2.447, (7, .05): 2.365, (8, .05): 2.306,
      (9, .05): 2.262, (10, .05): 2.228, (12, .05): 2.179, (15, .05): 2.131,
      (20, .05): 2.086, (24, .05): 2.064, (30, .05): 2.042, (40, .05): 2.021,
      (60, .05): 2.000, (120, .05): 1.980, (999, .05): 1.960,
      (1, .025): 25.452, (2, .025): 6.205, (3, .025): 4.177, (4, .025): 3.495,
      (5, .025): 3.163, (6, .025): 2.969, (7, .025): 2.841, (8, .025): 2.752,
      (9, .025): 2.685, (10, .025): 2.634, (12, .025): 2.560, (15, .025): 2.490,
      (20, .025): 2.423, (24, .025): 2.391, (30, .025): 2.360, (40, .025): 2.329,
      (60, .025): 2.299, (120, .025): 2.270, (999, .025): 2.241}


def t_crit(df: int, two_sided_alpha: float) -> float:
    keys = sorted({k[0] for k in _T if abs(k[1] - two_sided_alpha) < 1e-9})
    for k in keys:
        if df <= k:
            return _T[(k, two_sided_alpha)]
    return _T[(999, two_sided_alpha)]


@dataclass
class Estimate:
    name: str
    point: float
    lo: float
    hi: float
    se: float
    n_blocks: int
    alpha_used: float
    min_attainable_p: float

    def decide(self, threshold: float) -> str:
        """Operator's rule: support = lower bound above threshold; evidence
        against = upper bound below; straddle = inconclusive."""
        if self.min_attainable_p > self.alpha_used:
            return INELIGIBLE
        if self.lo > threshold:
            return SUPPORTED
        if self.hi < threshold:
            return UNSUPPORTED
        return INCONCLUSIVE


def paired_contrast(name, per_block_values, alpha=0.05, n_primary=1) -> Estimate:
    """per_block_values: one signed difference per INDEPENDENT BLOCK.

    Simultaneous coverage across n_primary predeclared primary contrasts is
    Bonferroni: each interval is computed at alpha / n_primary."""
    n = len(per_block_values)
    a = alpha / max(1, n_primary)
    m, s = _mean(per_block_values), _sd(per_block_values)
    se = s / math.sqrt(n) if n else float("inf")
    tc = t_crit(max(1, n - 1), 0.05 if abs(a - 0.05) < 1e-9 else 0.025)
    return Estimate(name, m, m - tc * se, m + tc * se, se, n, a,
                    min_attainable_p_paired(n))


def h0_estimands(blocks, alpha=0.05):
    """H0's two primary quantities as ANALYSES over paired blocks.

    blocks: list of dicts with keys S00, S10, S01, S11 -- each the solve
    FRACTION for that cell in that block, over all assigned tasks.

    Returns (additive_gain, interaction). They are DIFFERENT RESULTS and are
    reported separately; a supported additive gain never implies synergy.

    EXACT DESIGN FACT, independent of the block correlation. With four cells
    measured on the same block, coefficients (1,0,0,-1) for the main contrast
    and (1,-1,-1,1) for the interaction under an exchangeable within-block
    correlation rho:
        Var(S11-S00) = 2 s^2 (1-rho)
        Var(I)       = 4 s^2 (1-rho)
    so SE(I) = sqrt(2) * SE(main) ALWAYS -- rho cancels. The interaction needs
    TWICE the blocks of the main effect for equal precision, and H0's stronger
    claim is the interaction.
    """
    gain = [b["S11"] - b["S00"] for b in blocks]
    inter = [b["S11"] - b["S10"] - b["S01"] + b["S00"] for b in blocks]
    return (paired_contrast("additive_gain_S11_minus_S00", gain, alpha, 2),
            paired_contrast("interaction_I", inter, alpha, 2))


def required_blocks(sd_of_block_diff, threshold, alpha=0.05, n_primary=1,
                    true_effect=0.0, max_n=4000):
    """Smallest block count at which the operator's decision rule can return a
    CONCLUSIVE verdict for a given true effect. Needed because 'inconclusive'
    is this rule's default and silence is not a result."""
    for n in range(2, max_n + 1):
        a = alpha / max(1, n_primary)
        tc = t_crit(n - 1, 0.05 if abs(a - 0.05) < 1e-9 else 0.025)
        se = sd_of_block_diff / math.sqrt(n)
        lo, hi = true_effect - tc * se, true_effect + tc * se
        if (lo > threshold or hi < threshold) and min_attainable_p_paired(n) <= alpha:
            return n
    return None


# ------------------------------------------------------------- H4 protocol

H4_PROTOCOL_VERSION = "H4-ADAPTIVE-1.0.0"

H4_ADAPTIVE_PROTOCOL = {
    "version": H4_PROTOCOL_VERSION,
    "distinct_from_m_signal": {
        "m_signal": ("FROZEN corpus and FROZEN universe; both the directed and "
                     "the matched random order committed before any outcome is "
                     "revealed; endpoint is detector discrimination among "
                     "regions on that frozen corpus. The policy does not change "
                     "the universe while it runs."),
        "h4": ("The curriculum policy CHANGES THE TASK DISTRIBUTION while it "
               "runs -- that change IS the intervention. There is therefore no "
               "common universe during training, and no frozen candidate order "
               "to commit in advance."),
        "consequence": ("The two protocols cannot share an endpoint. H4 is not "
                        "admitted into M-SIGNAL and M-SIGNAL's frozen-universe "
                        "guarantees do not transfer to it."),
    },
    # the rule that does the most work
    "endpoint_surface": {
        "primary": "frozen final suite, identical for every arm, labels never "
                   "exposed to training",
        "secondary": "historical suite, for retention/forgetting, never fed back",
        "PROHIBITED": ("training-task solve rate as an endpoint, in any arm. An "
                       "adaptive arm generates its own tasks, so training solve "
                       "rate is confounded by the arm's own task generation: an "
                       "arm that proposes easier tasks scores higher while "
                       "learning less. 'Training challenges becoming harder does "
                       "not establish competence' -- this makes that mechanical."),
    },
    "precommitted": ["policy_id", "policy_version", "allowed_evidence",
                     "initial_state", "seed_streams", "budgets",
                     "tie_breaks", "stopping_rule", "censoring_rule"],
    "evaluator": ("fixed and independent of every arm; never updated during the "
                  "campaign; its own version pinned and hashed"),
    "design": "2x2, fixed/adaptive curriculum x transfer off/on",
    "reporting": ("combined effect and interaction reported SEPARATELY, with "
                  "simultaneous uncertainty across both; the interaction carries "
                  "sqrt(2) times the main effect's SE by construction"),
    "denominator": ("every ASSIGNED task in the frozen suite, including those "
                    "never attempted and those censored by budget exhaustion"),
    "censoring": ("budget exhaustion is CENSORED, not failure and not success; "
                  "censored runs stay in the denominator and their count is "
                  "reported beside the endpoint"),
    "void_conditions": [
        "any arm evaluated on tasks it generated",
        "evaluator updated mid-campaign",
        "historical suite fed back into training without an explicit licence",
        "confirmation opened before the plan hash was committed",
    ],
}
