"""W4.0 synthetic-null gate decision logic — H0 calibrated for class-imbalanced
held-out + strong-prior base models (E006).

The v0.5b W4.0 re-run under masked decode FIRED on Variant A all 3 seeds, but
investigation showed `lora_post_train ≡ base_zero_shot` bit-identical for every
firing — i.e. the LoRA training contributed nothing measurable. The gate's
binomial test against fixed H0=0.5 was mis-specified for this corpus shape:
class-imbalanced held-out (15:2 → after split, 7/7 cyclotomic for seeds 42 + 1234)
combined with the base model's strong prior toward `cyclotomic_noise` under
masked decode pushed accuracy above 0.5 trivially, with no learning involved.

The new decision function requires BOTH:
1. Accuracy beats max(0.5, empirical_held_out_majority_rate). A model that just
   echoes the majority class doesn't FIRE.
2. LoRA accuracy is at least `delta` higher than base zero-shot. The LoRA must
   contribute *something* beyond the base prior; pure base-prior firing is no
   longer flagged as memorization.

Gate FIRES (memorization suspected) only if BOTH hold:
  beats_majority_baseline AND lora_beats_base_by_delta

Otherwise PASS.

This is purely a decision function on per-run accuracy / count data; no contract
change to evaluate_model_with_label_mask, TrainingArgs, or any public API. The
v0_5b_rerun runner can adopt this without changing any other surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Counter, Dict, List, Optional, Sequence

from scipy.stats import binomtest


DEFAULT_ALPHA = 0.10
DEFAULT_DELTA = 0.05
DEFAULT_CHANCE = 0.5


@dataclass(frozen=True)
class GateDecision:
    """Per-run gate decision under the calibrated H0.

    - lora_acc / base_acc: accuracies on the same held-out
    - n_correct / n_total: lora's correct-count and held-out size
    - majority_rate: empirical held-out majority-class frequency
    - h0_rate: actual H0 used for the binomial test (= max(0.5, majority_rate))
    - p_value: one-sided binomial p (alternative='greater') against h0_rate
    - beats_baseline: p_value < alpha
    - lora_beats_base_by_delta: lora_acc - base_acc >= delta
    - decision: "FIRE" only when BOTH conditions hold; else "PASS"
    - reason: short explanation when PASS for clarity
    """
    lora_acc: float
    base_acc: float
    n_correct: int
    n_total: int
    majority_rate: float
    h0_rate: float
    p_value: float
    beats_baseline: bool
    lora_beats_base_by_delta: bool
    decision: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lora_acc": float(self.lora_acc),
            "base_acc": float(self.base_acc),
            "n_correct": int(self.n_correct),
            "n_total": int(self.n_total),
            "majority_rate": float(self.majority_rate),
            "h0_rate": float(self.h0_rate),
            "p_value": float(self.p_value),
            "beats_baseline": bool(self.beats_baseline),
            "lora_beats_base_by_delta": bool(self.lora_beats_base_by_delta),
            "decision": str(self.decision),
            "reason": str(self.reason),
        }


def synthetic_null_gate_decision(
    lora_acc: float,
    base_acc: float,
    n_correct: int,
    n_total: int,
    gold_label_counts: Dict[str, int] | Sequence[str],
    alpha: float = DEFAULT_ALPHA,
    delta: float = DEFAULT_DELTA,
    chance: float = DEFAULT_CHANCE,
) -> GateDecision:
    """Decide gate verdict under the calibrated H0.

    Args:
        lora_acc: LoRA-trained model accuracy on held-out
        base_acc: base zero-shot accuracy on the same held-out
        n_correct: LoRA correct count (= round(lora_acc * n_total))
        n_total: held-out size
        gold_label_counts: either a dict {label: count} OR a sequence of gold labels
        alpha: significance threshold for the binomial test
        delta: minimum required LoRA-over-base improvement
        chance: chance baseline (default 0.5)

    Returns: GateDecision with full decision telemetry.
    """
    if isinstance(gold_label_counts, dict):
        counts = dict(gold_label_counts)
    else:
        counts = {}
        for g in gold_label_counts:
            key = str(g)
            counts[key] = counts.get(key, 0) + 1

    if n_total <= 0:
        # Edge case: empty held-out. Decision is PASS (no signal, no gate).
        return GateDecision(
            lora_acc=lora_acc, base_acc=base_acc,
            n_correct=n_correct, n_total=n_total,
            majority_rate=chance, h0_rate=chance,
            p_value=1.0, beats_baseline=False,
            lora_beats_base_by_delta=False,
            decision="PASS", reason="empty held-out",
        )

    majority_rate = (max(counts.values()) / n_total) if counts else chance
    h0_rate = max(chance, float(majority_rate))

    bt = binomtest(n_correct, n_total, p=h0_rate, alternative="greater")
    p_value = float(bt.pvalue)
    beats_baseline = p_value < alpha
    delta_gap = float(lora_acc - base_acc)
    lora_beats_base_by_delta = delta_gap >= delta

    if beats_baseline and lora_beats_base_by_delta:
        decision = "FIRE"
        reason = (
            f"lora_acc={lora_acc:.3f} beats h0={h0_rate:.3f} (p={p_value:.4f}<alpha={alpha}) "
            f"AND lora-base={delta_gap:+.3f} >= delta={delta}"
        )
    elif beats_baseline and not lora_beats_base_by_delta:
        decision = "PASS"
        reason = (
            f"beats baseline but lora-base={delta_gap:+.3f} < delta={delta}: "
            "base-prior firing, not memorization"
        )
    elif not beats_baseline and lora_beats_base_by_delta:
        decision = "PASS"
        reason = (
            f"lora>base by {delta_gap:+.3f} but does not beat h0={h0_rate:.3f} "
            f"(p={p_value:.4f}>=alpha={alpha})"
        )
    else:
        decision = "PASS"
        reason = (
            f"neither condition met: p={p_value:.4f} vs alpha={alpha}, "
            f"lora-base={delta_gap:+.3f} vs delta={delta}"
        )

    return GateDecision(
        lora_acc=float(lora_acc),
        base_acc=float(base_acc),
        n_correct=int(n_correct),
        n_total=int(n_total),
        majority_rate=float(majority_rate),
        h0_rate=float(h0_rate),
        p_value=p_value,
        beats_baseline=beats_baseline,
        lora_beats_base_by_delta=lora_beats_base_by_delta,
        decision=decision,
        reason=reason,
    )


def redecide_v0_5b_w4_0(
    results_json_path: str,
    output_path: Optional[str] = None,
    alpha: float = DEFAULT_ALPHA,
    delta: float = DEFAULT_DELTA,
) -> Dict[str, Any]:
    """Re-decide v0.5b W4.0 verdicts using the calibrated H0 on existing run data.

    Loads `null_gate_results.json` produced by v0_5b_rerun (LoRA training
    completed; per-run accuracy + base zero-shot already recorded), applies the
    new gate decision logic to each (variant × seed) combination, and writes
    a recalibrated results doc to `output_path` (or alongside the input if not
    given). Returns the recalibrated dict.

    No re-training; this is a pure re-decision pass. The LoRA accuracies and
    base zero-shot accuracies don't change because the model is deterministic
    given training inputs.
    """
    import json
    from pathlib import Path

    src = Path(results_json_path)
    with src.open("r", encoding="utf-8") as f:
        original = json.load(f)

    out = {
        "source_results": str(src),
        "h0_protocol": "max(chance, empirical_held_out_majority_rate) AND lora-base>=delta",
        "alpha": alpha,
        "delta": delta,
        "decode_protocol": original.get("decode_protocol", "unknown"),
        "variant_a_boundary": {},
        "variant_b_synthetic": {},
        "config": original.get("config", {}),
    }
    fired: List[Dict[str, Any]] = []

    for variant_key in ("variant_a_boundary", "variant_b_synthetic"):
        variant = original.get(variant_key, {})
        for seed_key, block in variant.items():
            base_acc = float(block.get("base_zero_shot", {}).get("accuracy", 0.0))
            lora_block = block.get("lora_post_train", {})
            lora_acc = float(lora_block.get("accuracy", block.get("accuracy", 0.0)))
            n_total = int(lora_block.get("n", block.get("n_total", 0)))
            n_correct = int(round(lora_acc * n_total))

            # Held-out gold-label distribution: use the LoRA confusion matrix's
            # gold-label keys, summing each row.
            confusion = lora_block.get("confusion_matrix", {})
            counts: Dict[str, int] = {}
            for gold_label, pred_dict in confusion.items():
                counts[str(gold_label)] = sum(int(v) for v in pred_dict.values())
            if not counts:
                # Fall back to held_out_label_dist if recorded
                fallback = block.get("heldout_label_dist") or block.get("heldout_label_dist_post_fold")
                if fallback:
                    counts = {str(k): int(v) for k, v in fallback.items()}

            decision = synthetic_null_gate_decision(
                lora_acc=lora_acc, base_acc=base_acc,
                n_correct=n_correct, n_total=n_total,
                gold_label_counts=counts,
                alpha=alpha, delta=delta,
            )
            out[variant_key][seed_key] = decision.to_dict()
            if decision.decision == "FIRE":
                fired.append({"variant": variant_key, "seed": seed_key})

    out["overall_verdict"] = "FIRE" if fired else "PASS"
    out["gate_fired_on"] = fired

    # Persist
    target = Path(output_path) if output_path else src.with_name("null_gate_results_recalibrated.json")
    with target.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    out["written_to"] = str(target)
    return out


__all__ = [
    "GateDecision",
    "DEFAULT_ALPHA",
    "DEFAULT_DELTA",
    "DEFAULT_CHANCE",
    "synthetic_null_gate_decision",
    "redecide_v0_5b_w4_0",
]
