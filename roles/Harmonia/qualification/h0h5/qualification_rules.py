"""Harmonia qualification rules for the H0-H5 lanes.  QR-1.2.0  2026-09-18.

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

RULES_VERSION = "QR-1.2.1"

# QR-1.2.0 (2026-09-18, Harmonia[m2-ca1148a0]) ADDS, without changing any QR-1.1.0
# number or refusal:
#   lane_gate(lane)            HARM-05..10: the beta and 1.0 gate per lane, each naming
#                              WHICH of the three quantities it promises, its attainable
#                              range, and its eligibility count; H3 refuses diversity as
#                              an endpoint, H4 refuses any endpoint on training tasks,
#                              H5 carries the analytic reach bounds 8 / 12 as constants
#   freeze_plan / validate_plan(frozen=, data_opened=)
#                              HARM-34: a DIAGNOSTIC plan cannot be relabelled
#                              CONFIRMATORY after its data is read
#   contrast_correlation, paired_contrasts_shared_arm
#                              HARM-30: contrasts sharing a baseline arm carry their
#                              induced correlation; the fresh/S00 case is 0.5 under
#                              exchangeable equal variances
#   validate_cell_payloads     HARM-01: one payload hash under two CELL labels is refused;
#                              a declared alias (fresh == S00) is one baseline, two labels
#   replay_attestation / refuse_replay_as_replicate
#                              HARM-28: a bit-identical replay is an ATTESTATION and never
#                              a replicate
#   MULTIPLICITY.md, SIZING_RULE.md beside this module (HARM-11, HARM-12)
# QR-1.2.1 (2026-09-18, self-attack on 1.2.0, review packet Q1/Q2): refuse_relabel admits a
#   NEW confirmatory plan whose confirmation set is DISJOINT from the diagnostic's tasks
#   (freeze_plan records task_ids); validate_cell_payloads resolves alias chains and refuses
#   cycles; h5_reach_bounds_computed() derives 8 / 12 over the 4,096-entry map.

# QR-1.1.0 amends QR-1.0.0 in three places, after Archaeon reproduced
# Appendix A (SE(I)/SE(G) = sqrt(6) with equal marginal variances 0.005079)
# and confirmed sqrt(2) under exchangeable correlation at rho = 0, 0.3, 0.7.
# Both are right in their own domains. My QR-1.0.0 wording was universal and
# should not have been.
#
#   1. THE sqrt(2) RESULT IS CONDITIONAL, not general. It holds when the four
#      cells have EQUAL marginal variances AND an EXCHANGEABLE within-block
#      correlation. For a general four-cell covariance, each contrast has
#      variance c' Sigma c and the ratio is whatever that gives -- sqrt(6) is
#      one such case. Estimate the two contrasts SEPARATELY on the pilot.
#   2. G = S11 - S00 IS A JOINT-TREATMENT CONTRAST, NOT A MARGINAL MAIN
#      EFFECT. In a 2x2, G = (main 1) + (main 2) + (interaction); it is the
#      both-on-vs-both-off path, and calling it a main effect misattributes
#      the interaction into it.
#   3. required_blocks() COMPUTES INTERVAL CLEARANCE (precision), NOT POWER.
#      Renamed. A separate function estimates power when a probability of a
#      conclusive verdict is actually promised.
#
# THREE DISTINCT QUANTITIES, never substituted for one another:
#   MEANINGFUL EFFECT  a scientific / resource decision. Fixable BEFORE a
#                      pilot and not a function of the observed noise.
#   PRECISION          interval half-width at a given n. Arithmetic.
#   POWER              P(conclusive verdict) under an assumed truth. Requires
#                      the actual contrasts, multiplicity and decision rule.
# If the budget cannot resolve a fixed meaningful effect, REPORT THE
# LIMITATION or version a revised question. Never redefine the threshold to
# match the noise -- that is fitting the gate to the data.

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
    purpose: str = "CONFIRMATORY"      # CONFIRMATORY | DIAGNOSTIC
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

    # HA-1.6, SCOPED IN QR-1.1.0. The eligibility gate governs CONFIRMATORY
    # inference only. A DIAGNOSTIC run -- a two-seed instrument alpha, a
    # plumbing check, a contract fixture -- makes no inferential claim, so a
    # gate about the attainability of a p-value does not apply to it and must
    # not block it. Diagnostic alphas proceed while confirmation sizing is
    # being repaired; they simply may not be quoted as evidence for or against
    # an effect.
    mp = min_attainable_p_paired(p.n_blocks)
    if p.purpose == "CONFIRMATORY":
        if mp > p.alpha:
            raise PlanRefused(
                "INELIGIBLE by HA-1.6: %d paired blocks give a minimum "
                "attainable two-sided p of %.4f, above alpha %.3f. The gate "
                "cannot fire on any data. Resize or declare the lane "
                "descriptive." % (p.n_blocks, mp, p.alpha))
        ok.append("min_attainable_p_%.4f_le_alpha" % mp)
    elif p.purpose == "DIAGNOSTIC":
        ok.append("diagnostic_purpose_eligibility_gate_not_applied"
                  "_min_attainable_p_%.4f" % mp)
    else:
        raise PlanRefused("purpose must be CONFIRMATORY or DIAGNOSTIC")
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


CELLS = ("S11", "S10", "S01", "S00")
C_G = {"S11": 1.0, "S10": 0.0, "S01": 0.0, "S00": -1.0}   # joint treatment
C_I = {"S11": 1.0, "S10": -1.0, "S01": -1.0, "S00": 1.0}  # interaction
C_M1 = {"S11": .5, "S10": .5, "S01": -.5, "S00": -.5}     # marginal main, f1
C_M2 = {"S11": .5, "S10": -.5, "S01": .5, "S00": -.5}     # marginal main, f2


def contrast_variance(c: dict, sigma: dict) -> float:
    """c' Sigma c. THE general rule. sigma is {(cell_i, cell_j): cov}.

    Every special case -- sqrt(2), sqrt(6), anything else -- is this formula
    evaluated at a particular Sigma. Do not quote a ratio without the Sigma
    it was computed under.
    """
    tot = 0.0
    for i in CELLS:
        for j in CELLS:
            tot += c.get(i, 0.0) * c.get(j, 0.0) * sigma[(i, j)]
    return tot


def sigma_exchangeable(s2: float, rho: float) -> dict:
    """The SPECIAL CASE in which SE(I)/SE(G) = sqrt(2): equal marginal
    variances s2 and a single exchangeable within-block correlation rho.
    Under it Var(G) = 2 s2 (1-rho) and Var(I) = 4 s2 (1-rho), so rho cancels.
    Outside it the ratio is not sqrt(2) and must be computed, not assumed."""
    return {(i, j): (s2 if i == j else s2 * rho) for i in CELLS for j in CELLS}


def sigma_from_blocks(blocks) -> dict:
    """Estimate Sigma EMPIRICALLY from disjoint pilot blocks. This is what a
    lane must do rather than assume a structure: the two contrasts' variability
    is estimated SEPARATELY and the ratio is reported as measured."""
    n = len(blocks)
    mu = {c: _mean([b[c] for b in blocks]) for c in CELLS}
    sig = {}
    for i in CELLS:
        for j in CELLS:
            sig[(i, j)] = sum((b[i] - mu[i]) * (b[j] - mu[j])
                              for b in blocks) / (n - 1)
    return sig


def se_ratio_report(blocks) -> dict:
    """The honest object: the measured ratio, with the Sigma it came from and
    the sqrt(2) reference beside it, never instead of it."""
    sig = sigma_from_blocks(blocks)
    vG, vI = contrast_variance(C_G, sig), contrast_variance(C_I, sig)
    return {
        "var_G_joint_treatment": vG,
        "var_I_interaction": vI,
        "se_ratio_measured": math.sqrt(vI / vG) if vG > 0 else float("inf"),
        "se_ratio_if_exchangeable_equal_var": math.sqrt(2.0),
        "marginal_variances": {c: sig[(c, c)] for c in CELLS},
        "equal_marginal_variances": (
            max(sig[(c, c)] for c in CELLS) - min(sig[(c, c)] for c in CELLS)
            < 1e-9 * max(1e-12, max(sig[(c, c)] for c in CELLS))),
        "note": ("sqrt(2) is CONDITIONAL on equal marginal variances and an "
                 "exchangeable within-block correlation. Report the measured "
                 "ratio and the Sigma; the reference is context, not a result."),
    }


def h0_estimands(blocks, alpha=0.05):
    """H0's two primary quantities as ANALYSES over paired blocks.

    blocks: list of dicts with keys S00, S10, S01, S11 -- each the solve
    FRACTION for that cell in that block, over ALL ASSIGNED TASKS.

    Returns (G, I). They are DIFFERENT RESULTS, reported separately; a
    supported G never implies synergy.

    G = S11 - S00 IS A JOINT-TREATMENT CONTRAST, NOT A MARGINAL MAIN EFFECT.
    In a 2x2, G = (marginal main 1) + (marginal main 2) + I: it is the
    both-on-versus-both-off path through the design. Reporting it as a main
    effect silently attributes the interaction to it. The marginal main
    effects, if wanted, are C_M1 and C_M2 and are separate analyses.

    The variance of either contrast is c' Sigma c (contrast_variance). The
    sqrt(2) ratio holds ONLY under sigma_exchangeable; estimate Sigma on the
    disjoint pilot and report se_ratio_report beside the estimands.
    """
    gain = [b["S11"] - b["S00"] for b in blocks]
    inter = [b["S11"] - b["S10"] - b["S01"] + b["S00"] for b in blocks]
    return (paired_contrast("G_joint_treatment_S11_minus_S00", gain, alpha, 2),
            paired_contrast("interaction_I", inter, alpha, 2))


def blocks_for_interval_clearance(sd_of_block_diff, threshold, alpha=0.05,
                                  n_primary=1, assumed_effect=0.0, max_n=4000):
    """PRECISION, not power. Renamed in QR-1.1.0.

    Smallest n at which an interval CENTRED ON assumed_effect would clear the
    threshold. It assumes the point estimate lands exactly on assumed_effect,
    so it answers "how wide is the interval", not "how often would a real run
    reach a verdict". A real run's estimate scatters, so at this n roughly half
    of runs return INCONCLUSIVE. Use blocks_for_power when a probability of a
    conclusive verdict is promised.
    """
    for n in range(2, max_n + 1):
        a = alpha / max(1, n_primary)
        tc = t_crit(n - 1, 0.05 if abs(a - 0.05) < 1e-9 else 0.025)
        se = sd_of_block_diff / math.sqrt(n)
        lo, hi = assumed_effect - tc * se, assumed_effect + tc * se
        if (lo > threshold or hi < threshold) and min_attainable_p_paired(n) <= alpha:
            return n
    return None


# back-compat alias; the old name promised power and delivered precision
required_blocks = blocks_for_interval_clearance


def blocks_for_power(sd_of_block_diff, threshold, true_effect, target_power=0.80,
                     alpha=0.05, n_primary=1, trials=2000, max_n=2000, seed=7):
    """POWER: the smallest n at which P(CONCLUSIVE verdict) >= target_power,
    under the ACTUAL decision rule, multiplicity and contrast.

    Simulated rather than derived, because the decision rule is an interval
    clearance and not a standard test, so no closed form applies to it.
    Returns (n, achieved_power) or (None, best).
    """
    import random as _r
    best = 0.0
    n = 2
    while n <= max_n:
        if min_attainable_p_paired(n) > alpha:
            n += 1
            continue
        rng = _r.Random(seed + n)
        a = alpha / max(1, n_primary)
        tc = t_crit(n - 1, 0.05 if abs(a - 0.05) < 1e-9 else 0.025)
        hit = 0
        for _ in range(trials):
            d = [rng.gauss(true_effect, sd_of_block_diff) for _ in range(n)]
            m, s = _mean(d), _sd(d)
            se = s / math.sqrt(n)
            lo, hi = m - tc * se, m + tc * se
            if lo > threshold or hi < threshold:
                hit += 1
        p = hit / trials
        best = max(best, p)
        if p >= target_power:
            return n, p
        n += 1 if n < 40 else 4
    return None, best


# ------------------------------------------------------------- H4 protocol

H4_PROTOCOL_VERSION = "H4-ADAPTIVE-1.0.1"   # 1.0.1 (2026-09-18, HARM-32): the "reporting" sentence
                                            # made CONDITIONAL; no rule, endpoint or void condition changed;
                                            # H4 is at SCAFFOLD and no campaign ran under 1.0.0

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
                  "simultaneous uncertainty across both; the interaction's SE is "
                  "c_I' Sigma c_I over the pilot Sigma (sqrt(2) times the combined "
                  "effect's SE ONLY under equal marginal variances and exchangeable "
                  "within-block correlation; QR-1.1.0)"),
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


# =========================================================================
# QR-1.2.0 additions (2026-09-18). Nothing above this line changed.
# =========================================================================

# --------------------------------------------- the three quantities (HARM-12)

MEANINGFUL_EFFECT = "MEANINGFUL_EFFECT"   # a scientific / resource decision, fixed BEFORE the pilot
PRECISION = "PRECISION"                   # interval half-width at n; arithmetic (blocks_for_interval_clearance)
POWER = "POWER"                           # P(conclusive verdict) under an assumed truth (blocks_for_power)
THREE_QUANTITIES = (MEANINGFUL_EFFECT, PRECISION, POWER)


# ---------------------------------------------------- HARM-34: no relabelling

def freeze_plan(p: LanePlan, frozen_at: str = "") -> dict:
    """The record committed BEFORE a pilot opens. It carries the purpose the plan
    was frozen under and a digest of everything else, so a later plan can be
    recognised as 'the same plan with the purpose changed'."""
    body = asdict(p)
    purpose = body.pop("purpose")
    return {"digest_without_purpose": "sha256:" + hashlib.sha256(
                json.dumps(body, sort_keys=True, default=str).encode()).hexdigest(),
            "purpose": purpose, "plan_version": p.plan_version, "lane": p.lane,
            "frozen_at": frozen_at, "digest": p.digest(),
            # QR-1.2.1: the task ids the frozen plan touched, so a later CONFIRMATORY plan can
            # be admitted when, and only when, its confirmation set is disjoint from them
            "task_ids": sorted(set(p.pilot_task_ids) | set(p.confirmation_task_ids))}


def refuse_relabel(p: LanePlan, frozen: dict, data_opened: bool) -> None:
    """A DIAGNOSTIC plan whose data has been read may not become CONFIRMATORY.
    The eligibility gate (HA-1.6) was NOT applied to it, its rows were seen, and
    'the same plan, now confirmatory' is selection after the fact. The route is
    a NEW plan version with a DISJOINT confirmation set, frozen before that set
    is opened."""
    if frozen.get("purpose") == "DIAGNOSTIC" and p.purpose == "CONFIRMATORY" and data_opened:
        same = freeze_plan(p)["digest_without_purpose"] == frozen.get("digest_without_purpose")
        seen = set(frozen.get("task_ids") or [])
        overlap = seen & set(p.confirmation_task_ids)
        # QR-1.2.1 (self-attack 2026-09-18): a NEW plan whose confirmation set is DISJOINT from
        # every task the diagnostic touched is the route the refusal itself prescribes, so it is
        # admitted; the refusal fires on the same body, or on any confirmation task the
        # diagnostic already read. A frozen record without task_ids (pre-1.2.1) refuses as before.
        if same or overlap or not frozen.get("task_ids"):
            raise PlanRefused(
                "a DIAGNOSTIC plan (%s, frozen %s) may not be relabelled CONFIRMATORY after its "
                "data was read%s; version a new plan with a disjoint confirmation set"
                % (frozen.get("plan_version"), frozen.get("frozen_at") or "?",
                   " (same plan body)" if same else
                   (" (%d confirmation task(s) were read by the diagnostic)" % len(overlap) if overlap
                    else " (frozen record carries no task ids)")))


_validate_plan_1_1_0 = validate_plan


def validate_plan(p: LanePlan, frozen: dict = None, data_opened: bool = False) -> list:  # noqa: F811
    """QR-1.2.0: the QR-1.1.0 checks, then the relabel refusal when a frozen
    record is supplied. Without `frozen` the behaviour is exactly QR-1.1.0."""
    ok = _validate_plan_1_1_0(p)
    if frozen is not None:
        refuse_relabel(p, frozen, data_opened)
        ok.append("no_relabel_after_data_opened")
    return ok


# ------------------------------------------ HARM-30: shared-arm correlation

def contrast_correlation(c1: dict, c2: dict, sigma: dict) -> float:
    """corr(c1'y, c2'y) = c1' Sigma c2 / sqrt(c1' Sigma c1 * c2' Sigma c2). THE general
    rule; every special case is this at a particular Sigma."""
    cov = 0.0
    for i in CELLS:
        for j in CELLS:
            cov += c1.get(i, 0.0) * c2.get(j, 0.0) * sigma[(i, j)]
    v1, v2 = contrast_variance(c1, sigma), contrast_variance(c2, sigma)
    return cov / math.sqrt(v1 * v2) if v1 > 0 and v2 > 0 else float("nan")


C_TRANSPORT = {"S11": 0.0, "S10": 1.0, "S01": 0.0, "S00": -1.0}   # failures-only vs baseline
C_LIBRARY = {"S11": 0.0, "S10": 0.0, "S01": 1.0, "S00": -1.0}     # library-only vs baseline


def paired_contrasts_shared_arm(blocks, contrasts: dict, alpha=0.05) -> dict:
    """Several contrasts over the SAME paired blocks, reported WITH the correlation
    they inherit from shared arms. Two contrasts that both subtract S00 are not
    independent results, and a reader who sees two 'supported' rows must see
    the correlation beside them. contrasts: {name: coefficient dict}."""
    sig = sigma_from_blocks(blocks)
    names = list(contrasts)
    est = {}
    for nm in names:
        vals = [sum(contrasts[nm].get(c, 0.0) * b[c] for c in CELLS) for b in blocks]
        est[nm] = paired_contrast(nm, vals, alpha, len(names))
    corr = {}
    for a, b in combinations(names, 2):
        corr["%s|%s" % (a, b)] = contrast_correlation(contrasts[a], contrasts[b], sig)
    return {"estimates": est, "induced_correlation": corr, "sigma": sig,
            "note": ("contrasts sharing an arm are correlated; Bonferroni over %d is "
                     "conservative under positive correlation, never anti-conservative"
                     % len(names))}


def shared_arm_correlation_exchangeable(c1: dict, c2: dict, rho: float = 0.0) -> float:
    """The special case a reader can check by hand: equal marginal variances and
    exchangeable within-block correlation rho. For two simple differences that
    share one arm (transport = S10 - S00, G = S11 - S00) the value is 0.5 for
    every rho."""
    return contrast_correlation(c1, c2, sigma_exchangeable(1.0, rho))


# ------------------------------------------- HARM-01: cell payload identity

def validate_cell_payloads(plan: dict) -> dict:
    """plan: {"cells": {label: {"payload_hash": ...}}, "aliases": {alias: cell_label}}.
    Two CELL labels with one payload hash are ONE measurement under two labels and
    are refused (charter s3). A declared alias is allowed and recorded as such:
    'fresh' == 'S00' is one baseline that two lanes name differently."""
    cells = plan["cells"]
    by_hash, by_payload = {}, {}
    for label, cell in cells.items():
        by_hash.setdefault(cell["payload_hash"], []).append(label)
        if "declared_payload" in cell:       # Charon A1: one payload can carry two hashes when a
            key = json.dumps(cell["declared_payload"], sort_keys=True)   # label leaks into the hash;
            by_payload.setdefault(key, []).append(label)                 # compare the content too
    dup = {h: ls for h, ls in by_hash.items() if len(ls) > 1}
    if dup:
        raise PlanRefused("one payload hash under two cell labels: %s -- one measurement, "
                          "two labels; declare an alias or remove a cell"
                          % "; ".join("%s -> %s" % (h[:19], ls) for h, ls in dup.items()))
    dup_p = {k: ls for k, ls in by_payload.items() if len(ls) > 1}
    if dup_p:
        raise PlanRefused("identical declared payload under two cell labels (hashes differ, so a "
                          "label leaked into the hash): %s" % "; ".join(str(ls) for ls in dup_p.values()))
    aliases = plan.get("aliases", {})
    resolved = {}
    for alias in aliases:                    # QR-1.2.1: an alias may name an alias; chains resolve,
        if alias in cells:                   # cycles, dangling targets and alias/cell double-use refused
            raise PlanRefused("%s is both an alias and a cell label" % alias)
        target, hops = alias, []
        while target in aliases:
            hops.append(target)
            target = aliases[target]
            if target in hops:
                raise PlanRefused("alias cycle %s -> %s" % (" -> ".join(hops), target))
        if target not in cells:
            raise PlanRefused("alias %s -> %s names no cell" % (alias, target))
        resolved[alias] = target
    return {"distinct_payloads": len(by_hash), "cell_labels": len(cells),
            "aliases": {a: {"cell": t, "payload_hash": cells[t]["payload_hash"]} for a, t in resolved.items()},
            "baselines_under_two_labels": [(a, t) for a, t in resolved.items()]}


# ------------------------------------- HARM-28: replay is an attestation

def replay_attestation(rows, payload_key="spec_hash", output_key="output_digest") -> list:
    """Rows sharing a payload hash are ONE measurement. Returns one attestation per
    payload hash with more than one row: were the outputs bit-identical? A replay
    that reproduces its bytes ATTESTS determinism; it adds no unit."""
    groups = {}
    for r in rows:
        groups.setdefault(r[payload_key], []).append(r)
    out = []
    for h, rs in groups.items():
        if len(rs) < 2:
            continue
        outs = {r.get(output_key) for r in rs}
        out.append({"payload_hash": h, "n_rows": len(rs), "n_distinct_outputs": len(outs),
                    "attests_determinism": len(outs) == 1,
                    "counts_as_units": 1})
    return out


def refuse_replay_as_replicate(rows, payload_key="spec_hash") -> int:
    """Returns the number of INDEPENDENT units in rows. Raises when a payload hash
    appears more than once, because an analysis that received these rows as
    replicates would count one measurement several times."""
    seen = {}
    for r in rows:
        seen[r[payload_key]] = seen.get(r[payload_key], 0) + 1
    dup = {h: n for h, n in seen.items() if n > 1}
    if dup:
        raise PlanRefused("replay rows offered as replicates: %s; a bit-identical replay is an "
                          "attestation (replay_attestation) and contributes one unit"
                          % ", ".join("%s x%d" % (h[:19], n) for h, n in dup.items()))
    return len(seen)


# ---------------------------------------------- HARM-05..10: lane gates

# H5's analytic construction facts (archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md):
# the four high bits of the direct 12-bit genome are inert, so a direct decoder
# reaches at most 8 distinct rules from a genome's 12 single-bit neighbours; a
# permutation of the map cannot create more than 12 distinct neighbours. Only the
# EXCESS over these bounds is evidence about a learned encoding.
H5_DIRECT_REACH_BOUND = 8
H5_PERMUTED_REACH_BOUND = 12
H5_GENOME_BITS = 12
H5_RULES = 256
H5_ENCODINGS_PER_RULE = 16

H1_POOL_RULE = "pool >= 2K"   # RULING_H1H0_FAIRNESS_C3_2_ANALYSIS_2026-09-10.md s2c: packs differ substantially only then


@dataclass
class Gate:
    stage: str                      # BETA | ONE_POINT_ZERO
    endpoint: str
    primary_contrasts: tuple
    promised_quantity: str          # one of THREE_QUANTITIES (SIZING_RULE.md)
    attainable_range: tuple         # of the endpoint statistic
    unit: str
    min_blocks: int                 # smallest eligible n under HA-1.6 at alpha 0.05
    multiplicity: str
    preconditions: tuple            # measured facts that must be printed before the gate
    refusals: tuple                 # what this gate refuses mechanically
    secondary: tuple = ()
    constants: dict = field(default_factory=dict)

    def eligibility(self, n_blocks: int, alpha: float = 0.05) -> dict:
        """Printed BEFORE any gate is applied (charter s1)."""
        mp = min_attainable_p_paired(n_blocks)
        return {"n_blocks": n_blocks, "min_attainable_p": mp, "alpha": alpha,
                "label": "ELIGIBLE" if mp <= alpha else "NOTHING_COULD_FIRE"}


@dataclass
class LaneGate:
    lane: str
    claim: str
    beta: Gate
    one_point_zero: Gate

    def as_dict(self):
        return asdict(self)


_MIN_ELIGIBLE = 6      # 2/2^6 = 0.031 <= 0.05; five blocks give 0.0625

_COMMON_REFUSALS = (
    "unit other than paired (seed x task_block)",
    "denominator other than all assigned tasks",
    "pilot/confirmation overlap",
    "primary contrasts > 1 with multiplicity NONE",
    "n_blocks below the HA-1.6 minimum",
    "threshold moved after the pilot SD is seen",
)


def _h0():
    beta = Gate("BETA", "solve fraction over all assigned held-out tasks, four cells",
                ("G_joint_treatment_S11_minus_S00", "interaction_I"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("pilot Sigma estimated on DISJOINT blocks (sigma_from_blocks)",
                 "se_ratio_report printed beside both estimands",
                 "shared-arm correlation printed for any contrast pair sharing S00 (paired_contrasts_shared_arm)",
                 "cell payload hashes distinct (validate_cell_payloads)"),
                _COMMON_REFUSALS + ("G reported as a marginal main effect",
                                    "a supported G read as synergy"),
                secondary=("C_M1", "C_M2"))
    one = Gate("ONE_POINT_ZERO", beta.endpoint, beta.primary_contrasts, POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "BONFERRONI",
               beta.preconditions + ("block count from blocks_for_power at the pilot Sigma, "
                                     "SEPARATELY for G and for I (I needs ~2x)",
                                     "threshold FROZEN_FROM_PILOT"),
               beta.refusals + ("confirmation opened before the plan hash was committed",),
               secondary=beta.secondary)
    return LaneGate("H0", "failure transport + component reuse improve held-out solving; "
                          "interaction is a separate, stronger claim", beta, one)


def _h1():
    beta = Gate("BETA", "solve fraction over all assigned target tasks, three arms",
                ("relevant_minus_random", "random_minus_fresh"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("realised pool size P and K printed; %s measured BEFORE a relevance arm is licensed" % H1_POOL_RULE,
                 "mean inter-arm pack overlap printed",
                 "input width >= 4 bits, or K <= 2 at 3 bits (fairness ruling s2c)",
                 "every retrieved input queried against the target oracle; fresh arm's probe allowance equal"),
                _COMMON_REFUSALS + ("relevance arm at 3 bits with K = 4 (pool cannot reach 2K)",
                                    "witness == null read as solved",
                                    "extra oracle access or source/target solution overlap"))
    one = Gate("ONE_POINT_ZERO", beta.endpoint, ("relevant_minus_random",), POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "NONE",
               beta.preconditions + ("threshold FROZEN_FROM_PILOT on a disjoint pilot",
                                     "block count from blocks_for_power"),
               beta.refusals + ("retrospective search for favourable task partitions",),
               secondary=("resource_to_solve including unsolved cases",))
    return LaneGate("H1", "relevant compatible source failures improve later CEGIS over "
                          "random-compatible retrieval and fresh search", beta, one)


def _h2():
    # three SEPARATE results; a gate that merges them is refused by construction
    beta = Gate("BETA", "(a) computation: task accuracy on the frozen catalogue; "
                        "(b) causal contribution: targeted vs matched-random intervention delta; "
                        "(c) frozen reuse: new-composition accuracy with vs without the component",
                ("a_computation", "b_causal_contribution", "c_frozen_reuse"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("readout-only / direct-input baseline printed beside (a)",
                 "matched random rules, matched intervention magnitude, matched state size and readout capacity",
                 "confirmation labels inaccessible to rule search and readout fitting"),
                _COMMON_REFUSALS + ("(a) reported as (b) or (c)",
                                    "a readout-explained gain attributed to the substrate",
                                    "criticality measures used as a gate"))
    one = Gate("ONE_POINT_ZERO", beta.endpoint, beta.primary_contrasts, POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "BONFERRONI",
               beta.preconditions + ("untouched finite task manifests for each of (a), (b), (c)",),
               beta.refusals + ("a null on (b) or (c) discarding the CA runner",))
    return LaneGate("H2", "bounded CA dynamics contribute causally to computation and become "
                          "reusable stateful components", beta, one)


DIVERSITY_ENDPOINTS = ("archive_diversity", "qd_score", "coverage", "descriptor_spread", "novelty")


def _h3():
    beta = Gate("BETA", "prospective utility: solve fraction on the sealed future-task manifest, four policies",
                ("hybrid_minus_topk", "behavioral_minus_topk", "uniform_minus_topk"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("identical ordered stream across the four policies (digest)",
                 "byte cap and item cap parity across policies",
                 "future queries frozen and sealed before any archive is replayed",
                 "descriptor, bins, tie order and capacity frozen"),
                _COMMON_REFUSALS + ("any diversity measure as an endpoint (%s)" % ", ".join(DIVERSITY_ENDPOINTS),
                                    "retrospective descriptor change",
                                    "cherry-picked query subset"),
                secondary=("archive diversity, reported and never a gate",))
    one = Gate("ONE_POINT_ZERO", beta.endpoint, beta.primary_contrasts, POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "BONFERRONI",
               beta.preconditions + ("policy cost receipts complete; costs charged in every arm",),
               beta.refusals, secondary=beta.secondary)
    return LaneGate("H3", "bounded behavioral/random retention improves future utility over "
                          "top-K, uniform and behavioral-only", beta, one)


def _h4():
    beta = Gate("BETA", "competence on the FROZEN final suite, identical for every arm; "
                        "retention on the historical suite as secondary",
                ("combined_effect_adaptive_x_transfer", "interaction"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("protocol version %s pinned and hashed" % H4_PROTOCOL_VERSION,
                 "evaluator fixed, independent of every arm, never updated mid-campaign",
                 "denominator: every ASSIGNED frozen-suite task, censored runs counted",
                 "policy_id, policy_version, seed streams, budgets, stopping and censoring rules precommitted"),
                _COMMON_REFUSALS + tuple(H4_ADAPTIVE_PROTOCOL["void_conditions"])
                + ("training-task solve rate as an endpoint in ANY arm",),
                secondary=("historical-suite retention/forgetting, never fed back",))
    one = Gate("ONE_POINT_ZERO", beta.endpoint, beta.primary_contrasts, POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "BONFERRONI",
               beta.preconditions + ("interaction sized at sqrt(2) worse precision than the combined effect, by construction",),
               beta.refusals, secondary=beta.secondary)
    return LaneGate("H4", "adaptive challenges and transfer improve independently evaluated competence", beta, one)


def _h5():
    consts = {"H5_DIRECT_REACH_BOUND": H5_DIRECT_REACH_BOUND, "H5_PERMUTED_REACH_BOUND": H5_PERMUTED_REACH_BOUND,
              "H5_GENOME_BITS": H5_GENOME_BITS, "H5_RULES": H5_RULES, "H5_ENCODINGS_PER_RULE": H5_ENCODINGS_PER_RULE}
    beta = Gate("BETA", "held-out solve fraction AND functional offspring yield, "
                        "learned-balanced vs direct vs scrambled-learned decoders",
                ("learned_minus_scrambled_solve", "learned_minus_scrambled_yield"),
                PRECISION, (-1.0, 1.0), "paired (seed x task_block)", _MIN_ELIGIBLE, "BONFERRONI",
                ("phenotype multiplicities EXACTLY preserved (16 per rule, 4096 entries)",
                 "initial phenotype distribution, mutation operator and target budget matched",
                 "training and decoding costs charged; total-cost result before any amortisation",
                 "mean class-reach reported as EXCESS over the analytic bound for the decoder's construction "
                 "(direct <= %d, any permutation <= %d)" % (H5_DIRECT_REACH_BOUND, H5_PERMUTED_REACH_BOUND)),
                _COMMON_REFUSALS + ("reach at or under the construction bound quoted as evolvability evidence",
                                    "a hand-designed or scrambled decoder read as a learned effect",
                                    "benefit that disappears after frequency / initial-phenotype / cost controls"),
                constants=consts)
    one = Gate("ONE_POINT_ZERO", beta.endpoint, beta.primary_contrasts, POWER, (-1.0, 1.0),
               beta.unit, _MIN_ELIGIBLE, "BONFERRONI",
               beta.preconditions + ("decoder frozen and hashed before target evaluation",),
               beta.refusals, constants=consts)
    return LaneGate("H5", "a learned balanced decoder improves access to useful variation after "
                          "phenotype frequencies and total costs are controlled", beta, one)


_LANES = {"H0": _h0, "H1": _h1, "H2": _h2, "H3": _h3, "H4": _h4, "H5": _h5}


def lane_gate(lane: str) -> LaneGate:
    if lane not in _LANES:
        raise PlanRefused("no gate for lane %r; lanes are %s" % (lane, sorted(_LANES)))
    return _LANES[lane]()


def refuse_endpoint(lane: str, endpoint_name: str, computed_on: str = "held_out") -> None:
    """Mechanical endpoint refusals: H3 refuses diversity; H4 refuses anything
    computed on training tasks."""
    e = endpoint_name.lower()
    if lane == "H3" and any(d in e for d in DIVERSITY_ENDPOINTS):
        raise PlanRefused("H3: %r is a diversity measure; prospective utility is the endpoint and "
                          "diversity is secondary (design: 'more measured diversity without later "
                          "solving benefit is a negative result')" % endpoint_name)
    if lane == "H4" and computed_on == "training":
        raise PlanRefused("H4: endpoint %r computed on TRAINING tasks; an adaptive arm generates its own "
                          "tasks, so training solve rate is confounded by task generation "
                          "(%s endpoint_surface.PROHIBITED)" % (endpoint_name, H4_PROTOCOL_VERSION))


def h5_excess_over_construction(mean_reach: float, decoder_kind: str) -> dict:
    """Only the excess over the analytic bound counts. decoder_kind: direct | permuted |
    scrambled | learned. A learned decoder is a permutation of the map (swaps preserve
    multiplicities), so its bound is the permuted one."""
    bound = {"direct": H5_DIRECT_REACH_BOUND, "permuted": H5_PERMUTED_REACH_BOUND,
             "scrambled": H5_PERMUTED_REACH_BOUND, "learned": H5_PERMUTED_REACH_BOUND}[decoder_kind]
    excess = mean_reach - bound
    return {"mean_reach": mean_reach, "decoder_kind": decoder_kind, "analytic_bound": bound,
            "excess_over_construction": excess,
            "label": "AT_OR_UNDER_BOUND_NO_EVIDENCE" if excess <= 0 else "EXCESS_%.4f" % excess}


def h0_worked_sizing(pilot_blocks, threshold=0.05, alpha=0.05, target_power=0.80):
    """HARM-06: the H0 sizing at a PILOT Sigma, G and I sized SEPARATELY.
    Returns the measured SE ratio, and for each contrast the interval-clearance
    n (PRECISION) at the null and the power n (POWER) at 2x the threshold."""
    rep = se_ratio_report(pilot_blocks)
    n = len(pilot_blocks)
    sdG = math.sqrt(rep["var_G_joint_treatment"])
    sdI = math.sqrt(rep["var_I_interaction"])
    out = {"pilot_n_blocks": n, "se_ratio_measured": rep["se_ratio_measured"],
           "se_ratio_if_exchangeable_equal_var": rep["se_ratio_if_exchangeable_equal_var"]}
    for nm, sd in (("G", sdG), ("I", sdI)):
        prec = blocks_for_interval_clearance(sd, threshold, alpha, 2, assumed_effect=0.0)
        pw, achieved = blocks_for_power(sd, threshold, true_effect=2 * threshold, target_power=target_power,
                                        alpha=alpha, n_primary=2, trials=400)
        out[nm] = {"block_sd": sd, "blocks_for_interval_clearance_at_null": prec,
                   "blocks_for_power_at_2x_threshold": pw, "achieved_power": achieved,
                   "quantities": {PRECISION: prec, POWER: pw, MEANINGFUL_EFFECT: threshold}}
    return out


# ----------------------------------------------- HARM-11: multiplicity ACROSS lanes

PROGRAM_LANES = ("H0", "H1", "H2", "H3", "H4", "H5")


def program_family(alpha: float = 0.05, lanes=PROGRAM_LANES) -> dict:
    """MULTIPLICITY.md, mechanical. Two families, never one:
    LANE family      each lane's declared primaries, Bonferroni within the lane at
                     alpha (what validate_plan enforces). A lane's own verdict is
                     read at this level.
    PROGRAM family   any claim that AGGREGATES lanes ('the ecosystem works',
                     'k of 6 supported'). Under a global null the probability that
                     at least one of n independent lane families returns a false
                     SUPPORTED is 1 - (1-alpha)^n; a program-level claim uses
                     alpha / n per lane. Both numbers are printed with any
                     cross-lane sentence."""
    n = len(lanes)
    return {"lanes": list(lanes), "n_lanes": n, "lane_alpha": alpha,
            "program_fwer_if_uncorrected": 1.0 - (1.0 - alpha) ** n,
            "expected_false_supports_if_uncorrected": n * alpha,
            "program_level_alpha_per_lane": alpha / n,
            "rule": "lane verdicts at lane_alpha (within-lane Bonferroni); cross-lane claims at alpha/n"}


# ------------------------------------ QR-1.2.1: the H5 bounds COMPUTED, not quoted

def h5_reach_bounds_computed(seed: int = 7, n_permutations: int = 3) -> dict:
    """Self-attack 2026-09-18 (review packet Q2): the constants 8 / 12 were quoted
    from Archaeon's readout. Compute them over the full map instead.
    Genome: 12 bits; direct decoder = the low 8 bits (rule 0..255); a genome's
    neighbours are its 12 single-bit flips. Reach = number of DISTINCT rules among
    the neighbours' decodings. For the direct decoder every genome reaches
    exactly 8 non-parent rules (each low-bit flip changes exactly one rule bit; the
    4 high bits are inert and give 4 NEUTRAL neighbours). For ANY decoder the reach
    is at most the neighbour count, 12, attained only when no neighbour is neutral. A
    balanced random permutation (16 genomes per rule preserved) is sampled to show
    where a permuted map lands (the live balanced_7 read 11.7305)."""
    import random as _r
    N, BITS = 4096, 12
    direct = [g & 0xFF for g in range(N)]

    # DEFINITION FOUND BY THIS CHECK: the readout's "reach" counts distinct rules among
    # the neighbours EXCLUDING the parent's own rule; neutral neighbours (same rule as the
    # parent) are counted separately as mean_neutral (4.0000 for direct). Counting the
    # parent's rule as well gives 9 for the direct decoder, not 8. Both are computed;
    # the constants 8 / 12 are the non-parent definition and the file says so.
    def reach_excl(dec):
        return [len({dec[g ^ (1 << b)] for b in range(BITS)} - {dec[g]}) for g in range(N)]

    def reach_incl(dec):
        return [len({dec[g ^ (1 << b)] for b in range(BITS)}) for g in range(N)]

    def neutral(dec):
        return [sum(1 for b in range(BITS) if dec[g ^ (1 << b)] == dec[g]) for g in range(N)]
    de, di, dn = reach_excl(direct), reach_incl(direct), neutral(direct)
    rng = _r.Random(seed)
    perm_means = []
    for _ in range(n_permutations):
        table = list(range(256)) * 16                # exactly 16 genomes per rule
        rng.shuffle(table)
        perm_means.append(sum(reach_excl(table)) / N)
    return {"genomes": N, "neighbours_per_genome": BITS,
            "definition": "reach = distinct rules among the 12 neighbours EXCLUDING the parent's rule; "
                          "neutral = neighbours decoding to the parent's rule",
            "direct_reach_excl_parent": {"min": min(de), "max": max(de), "mean": sum(de) / N},
            "direct_reach_incl_parent": {"min": min(di), "max": max(di), "mean": sum(di) / N},
            "direct_neutral_mean": sum(dn) / N,
            "H5_DIRECT_REACH_BOUND": H5_DIRECT_REACH_BOUND, "direct_bound_holds": max(de) == H5_DIRECT_REACH_BOUND,
            "H5_PERMUTED_REACH_BOUND": H5_PERMUTED_REACH_BOUND,
            "permuted_bound_is_neighbour_count": H5_PERMUTED_REACH_BOUND == BITS,
            "balanced_random_permutation_mean_reach_excl_parent": perm_means,
            "multiplicity_preserved": True}
