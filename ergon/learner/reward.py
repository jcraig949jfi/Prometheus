"""ergon.learner.reward — agreement-weighted reward (PROMOTE-only at MVP).

Per pivot/ergon_learner_proposal_v8.md S5.3 + Trial 1 outcome:

V8's reward formula:
  reward = w_S * substrate_pass            # 0.40
         + w_X * cross_model_logical       # 0.15 (DAG-consistency only)
         + w_H * holdout_battery_pass      # 0.20
         + w_NL * non_llm_evaluator_pass   # 0.10
         + w_R * signal_class_residual     # 0.15 CONDITIONAL on classifier

Trial 1 fired: classifier in deep escrow → w_R = 0. Total weights: 0.85.
v8 specifies renormalization to maintain reward scale.

MVP scope: at this version we ship PROMOTE-only because:
  - cross_model evaluator is v0.5+ (LiteLLM not wired yet)
  - held_out battery audit is v0.5+
  - non_llm_evaluator is v0.5+ (numeric perturbation harness)

So the MVP reward function reduces to:
  reward = substrate_pass

Where substrate_pass is the binary {kill, no-kill} outcome of running
F1+F6+F9+F11. This is the simplest possible reward; v0.5 layers in the
agreement-weighted form once those evaluators are wired.

The function structure is designed to accept v0.5's evaluator-result
inputs without architectural change — just per-component weights start
at 0 and get raised when the evaluator ships.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# Per v8 §5.3 default weights (with w_R conditional)
V8_REWARD_WEIGHTS_FULL = {
    "w_S": 0.40,
    "w_X": 0.15,
    "w_H": 0.20,
    "w_NL": 0.10,
    "w_R": 0.15,
}

# Per Trial 1 outcome: w_R = 0; renormalize remaining weights
V8_REWARD_WEIGHTS_POST_TRIAL_1 = {
    "w_S": 0.40 / 0.85,   # ≈ 0.471
    "w_X": 0.15 / 0.85,   # ≈ 0.176
    "w_H": 0.20 / 0.85,   # ≈ 0.235
    "w_NL": 0.10 / 0.85,  # ≈ 0.118
    "w_R": 0.0,
}

# At MVP scope, only w_S is active (other evaluators not wired yet)
MVP_REWARD_WEIGHTS = {
    "w_S": 1.0,
    "w_X": 0.0,
    "w_H": 0.0,
    "w_NL": 0.0,
    "w_R": 0.0,
}


@dataclass
class RewardComponents:
    """Per-component evaluation results for one CLAIM.

    Each component is a {0.0, 1.0} pass-indicator at MVP. v0.5+ may
    introduce continuous values (e.g., cross_model_logical = inter-
    evaluator agreement fraction in [0, 1]).
    """
    substrate_pass: float = 0.0          # F1+F6+F9+F11 pass indicator (or weighted)
    cross_model_logical: float = 0.0     # 1.0 if N≥2 LLMs all agree DAG is consistent
    holdout_battery_pass: float = 0.0    # 1.0 if held-out battery accepts
    non_llm_evaluator_pass: float = 0.0  # 1.0 if numeric perturbation/symbolic check accepts
    signal_class_residual: float = 0.0   # 1.0 if classifier confidence ≥0.85 + signal class

    # Diagnostic metadata (optional)
    metadata: Dict[str, Any] = field(default_factory=dict)


def compute_reward(
    components: RewardComponents,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Agreement-weighted reward computation.

    weights defaults to MVP_REWARD_WEIGHTS (PROMOTE-only at MVP per
    Trial 1 outcome). Pass V8_REWARD_WEIGHTS_POST_TRIAL_1 once v0.5
    evaluators are wired.
    """
    w = weights or MVP_REWARD_WEIGHTS

    return (
        w["w_S"] * components.substrate_pass
        + w["w_X"] * components.cross_model_logical
        + w["w_H"] * components.holdout_battery_pass
        + w["w_NL"] * components.non_llm_evaluator_pass
        + w["w_R"] * components.signal_class_residual
    )


def is_promotable(
    components: RewardComponents,
    promote_threshold: float = 0.5,
    weights: Optional[Dict[str, float]] = None,
) -> bool:
    """Decide whether a CLAIM with these reward components is PROMOTEd.

    At MVP: substrate_pass alone determines promotion (since other weights
    are zero). At v0.5+: agreement-weighted score must exceed threshold.
    """
    score = compute_reward(components, weights)
    return score >= promote_threshold


# ---------------------------------------------------------------------------
# Substrate-pass helper — runs the kernel discipline
# ---------------------------------------------------------------------------


def evaluate_substrate_pass(
    kill_path_verdicts: Dict[str, str],
) -> float:
    """Compute substrate_pass from a dict of kill-test → verdict strings.

    Per v8 unanimous battery: PROMOTE only if F1+F6+F9+F11 all return
    CLEAR or WARN; any BLOCK kills the CLAIM.

    kill_path_verdicts: {test_id: "CLEAR"|"WARN"|"BLOCK"}
    Returns: 1.0 if substrate-pass; 0.0 otherwise
    """
    UNANIMOUS_BATTERY = {"F1", "F6", "F9", "F11"}
    for test_id in UNANIMOUS_BATTERY:
        verdict = kill_path_verdicts.get(test_id, "BLOCK")  # missing = BLOCK by default
        if verdict == "BLOCK":
            return 0.0
    return 1.0
