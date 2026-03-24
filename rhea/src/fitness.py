"""
Rhea fitness function: reasoning gravity measurement.

Two components weighted to produce a single scalar fitness:

1. Ejection Suppression Score (weight: 0.6)
   - Logit lens backward pass on trap battery
   - Measures monotonicity of correct answer probability across layers
   - Higher monotonicity = stronger reasoning gravity
   - L* absent = maximum score

2. Correct Answer Survival Rate (weight: 0.4)
   - Is correct answer in top-5 logits at final layer?
   - Binary per trap, averaged across battery
   - Survival not winning — presence not dominance

This is fundamentally different from Ignis fitness (which scores
steered generation quality). Rhea never generates — it only
looks at the internal probability landscape.
"""

from dataclasses import dataclass
from logit_lens import batch_logit_lens, LogitLensResult


@dataclass
class FitnessResult:
    fitness: float
    ejection_suppression: float
    survival_rate: float
    per_trap: list[dict]


W_EJECTION = 0.6
W_SURVIVAL = 0.4


def evaluate_fitness(model, tokenizer, traps) -> FitnessResult:
    """
    Evaluate a single individual (model with LoRA applied) on the trap battery.

    Args:
        model: HuggingFace model with LoRA weights applied
        tokenizer: corresponding tokenizer
        traps: list of Trap objects

    Returns:
        FitnessResult with composite fitness and component scores
    """
    # Run logit lens on all traps
    results: list[LogitLensResult] = batch_logit_lens(model, tokenizer, traps)

    per_trap = []
    monotonicity_scores = []
    survival_count = 0

    for r in results:
        monotonicity_scores.append(r.monotonicity)
        if r.survival:
            survival_count += 1

        per_trap.append({
            "name": r.trap_name,
            "monotonicity": r.monotonicity,
            "survival": r.survival,
            "l_star": r.l_star,
            "p_correct_final": r.layer_probs[-1] if r.layer_probs else 0.0,
            "top5_final": r.top5_final,
        })

    # Aggregate
    ejection_suppression = (
        sum(monotonicity_scores) / len(monotonicity_scores)
        if monotonicity_scores else 0.0
    )
    survival_rate = survival_count / len(traps) if traps else 0.0

    fitness = W_EJECTION * ejection_suppression + W_SURVIVAL * survival_rate

    return FitnessResult(
        fitness=fitness,
        ejection_suppression=ejection_suppression,
        survival_rate=survival_rate,
        per_trap=per_trap,
    )


def check_graduation(fitness_history: list[float],
                      ejection_suppression: float,
                      survival_rate: float,
                      plateau_window: int = 20) -> dict:
    """
    Check if the current population meets graduation criteria.

    Graduation from 135M → 0.5B requires:
      - ejection_suppression > 0.75
      - survival_rate > 0.60
      - fitness plateau for `plateau_window` generations

    Returns dict with pass/fail for each criterion and overall.
    """
    # Plateau check: is the best fitness in the last N generations
    # within 1% of the current best?
    plateau = False
    if len(fitness_history) >= plateau_window:
        recent = fitness_history[-plateau_window:]
        best = max(recent)
        worst = min(recent)
        plateau = (best - worst) < 0.01 * best if best > 0 else True

    result = {
        "ejection_suppression_pass": ejection_suppression > 0.75,
        "survival_rate_pass": survival_rate > 0.60,
        "plateau": plateau,
        "ejection_suppression": ejection_suppression,
        "survival_rate": survival_rate,
    }
    result["graduated"] = (
        result["ejection_suppression_pass"]
        and result["survival_rate_pass"]
        and result["plateau"]
    )
    return result
