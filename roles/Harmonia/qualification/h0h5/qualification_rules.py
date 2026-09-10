"""Harmonia qualification rules for the H0-H5 lanes.  QR-1.1.0  2026-09-10.

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

RULES_VERSION = "QR-1.1.0"

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
