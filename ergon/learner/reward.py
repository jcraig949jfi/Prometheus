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

W1.7 (v0.5): per-domain π₀ weighting with CI propagation. Charon's
beta-binomial estimates of P(false null) per domain weight PROMOTE
confidence so that the same substrate-pass in genus2 (π₀=0.669, wide CI)
vs Lehmer (π₀=0.999, tight CI) carries ~500× different posterior weight.
Without CI propagation, low-data domains amplify noise into the gradient.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


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
# Per-domain π₀ weighting (W1.7) — Charon's beta-binomial calibration
# ---------------------------------------------------------------------------

DEFAULT_PI0_PATH = (
    Path(__file__).resolve().parents[2]
    / "charon" / "diagnostics" / "per_domain_pi0.json"
)


@dataclass
class Pi0Weight:
    """Per-domain π₀ point estimate + 95% CI.

    Used by `compute_reward_with_pi0` to weight PROMOTE confidence by the
    domain's null-rate posterior. Same PROMOTE in low-π₀ domain (genus2
    0.669) carries far less posterior weight than in a near-unity domain
    (Lehmer 0.999). CI carries through so wide-CI domains (thin data)
    don't spuriously amplify the gradient.
    """
    domain: str
    pi0_mean: float
    pi0_ci_lower: float
    pi0_ci_upper: float


@lru_cache(maxsize=4)
def _load_pi0_table(path_str: str) -> Dict[str, Pi0Weight]:
    p = Path(path_str)
    if not p.exists():
        return {}
    raw = json.loads(p.read_text(encoding="utf-8"))
    out: Dict[str, Pi0Weight] = {}
    for domain, entry in raw.get("per_domain", {}).items():
        ci = entry.get("pi0_ci") or [entry.get("pi0_mean", 0.0)] * 2
        out[domain] = Pi0Weight(
            domain=domain,
            pi0_mean=float(entry.get("pi0_mean", 0.0)),
            pi0_ci_lower=float(ci[0]),
            pi0_ci_upper=float(ci[1]),
        )
    return out


def get_pi0_weight(
    domain: Optional[str],
    pi0_path: Optional[Path] = None,
) -> Pi0Weight:
    """Return Pi0Weight for `domain`; fallback to neutral (1.0, 1.0, 1.0).

    A neutral fallback means the new code is a no-op for trial scripts
    that don't pass a domain — preserves backwards compatibility.
    """
    if domain is None:
        return Pi0Weight("__neutral__", 1.0, 1.0, 1.0)
    table = _load_pi0_table(str(pi0_path or DEFAULT_PI0_PATH))
    weight = table.get(domain)
    if weight is None:
        return Pi0Weight(domain, 1.0, 1.0, 1.0)
    return weight


def compute_reward_with_pi0(
    components: RewardComponents,
    weights: Optional[Dict[str, float]] = None,
    domain: Optional[str] = None,
    pi0_path: Optional[Path] = None,
) -> Tuple[float, Pi0Weight]:
    """Reward weighted by per-domain π₀ point estimate; CI returned alongside.

    Returns (pi0_weighted_reward, pi0_weight). Caller should log
    `pi0_weight.pi0_ci_lower` / `pi0_ci_upper` into the ledger so that
    downstream cross-corpus comparisons (W5.3) can apply CI-conditioned
    rate ratios rather than naive point-estimate ratios.

    Multiplicative weighting: a PROMOTE in a high-π₀ domain (most random
    candidates would be wrong under null) is strong evidence and earns
    near-full reward; a PROMOTE in a low-π₀ domain is weaker.
    """
    base = compute_reward(components, weights)
    pi0 = get_pi0_weight(domain, pi0_path=pi0_path)
    return base * pi0.pi0_mean, pi0


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
