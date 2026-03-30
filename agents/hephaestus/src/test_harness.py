"""Trap battery for testing forged reasoning tools.

Tools must beat the NCD baseline on accuracy or calibration to pass.
"""

import importlib.util
import logging
import sys
import tempfile
import zlib
from pathlib import Path

import numpy as np

log = logging.getLogger("hephaestus.harness")

# ---------------------------------------------------------------------------
# Trap Battery
# ---------------------------------------------------------------------------

TRAPS = [
    # --- Original 10: cognitive biases, math, logic ---
    {
        "prompt": "Is 9.11 larger than 9.9?",
        "candidates": ["Yes", "No"],
        "correct": "No",
    },
    {
        "prompt": "Which is heavier: a pound of gold or a pound of feathers?",
        "candidates": ["Gold", "Same"],
        "correct": "Same",
    },
    {
        "prompt": "You overtake 2nd place in a race. What place are you in?",
        "candidates": ["First", "Second"],
        "correct": "Second",
    },
    {
        "prompt": "A bat and ball cost $1.10. Bat costs $1 more. Ball costs?",
        "candidates": ["$0.10", "$0.05"],
        "correct": "$0.05",
    },
    {
        "prompt": "If all cats are animals, are all animals cats?",
        "candidates": ["Yes", "No"],
        "correct": "No",
    },
    {
        "prompt": "0.999 repeating equals 1?",
        "candidates": ["Yes", "No"],
        "correct": "Yes",
    },
    {
        "prompt": "13 people, 12 months. Must two share a birth month?",
        "candidates": ["Yes", "No"],
        "correct": "Yes",
    },
    {
        "prompt": "Coin flipped heads 5 times. Next flip probability of heads?",
        "candidates": ["Higher than 50%", "50%"],
        "correct": "50%",
    },
    {
        "prompt": "Sum of two odd numbers is always odd?",
        "candidates": ["True", "False"],
        "correct": "False",
    },
    {
        "prompt": "A farmer has 15 sheep. All but 8 die. How many left?",
        "candidates": ["7", "8"],
        "correct": "8",
    },
    # --- Compositional / logical reasoning traps (11-15) ---
    {
        "prompt": "If Alice is taller than Bob, and Bob is taller than Carol, who is tallest?",
        "candidates": ["Carol", "Alice", "Bob", "They are the same height"],
        "correct": "Alice",
    },
    {
        "prompt": "It is not the case that all birds can fly. Can penguins fly?",
        "candidates": [
            "Yes, all birds can fly",
            "No, some birds cannot fly",
            "The question cannot be answered from the given information",
            "Yes, penguins are birds",
        ],
        "correct": "The question cannot be answered from the given information",
    },
    {
        "prompt": "9.11 is less than 9.9. Which number is larger?",
        "candidates": ["9.11", "9.9", "They are equal", "Cannot be determined"],
        "correct": "9.9",
    },
    {
        "prompt": "The dog chased the cat. Who was being chased?",
        "candidates": ["The dog", "The cat", "Both", "Neither"],
        "correct": "The cat",
    },
    {
        "prompt": "If it is raining, the ground is wet. The ground is not wet. Is it raining?",
        "candidates": ["Yes", "No", "Maybe", "Not enough information"],
        "correct": "No",
    },
]


# ---------------------------------------------------------------------------
# NCD Baseline
# ---------------------------------------------------------------------------

class _NCDBaseline:
    """Built-in NCD baseline for comparison. Tools must beat this to pass."""

    def __init__(self, level=6):
        self._level = level

    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        denom = max(cx, cy)
        return (cxy - min(cx, cy)) / denom if denom > 0 else 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            ncd_val = self._ncd(prompt, cand)
            score = 1.0 / (1.0 + ncd_val)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"NCD={ncd_val:.4f}",
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ncd_val = self._ncd(prompt, answer)
        conf = 1.0 - float(np.clip(ncd_val, 0.0, 1.0))
        return float(conf ** 2)


_ncd_baseline = _NCDBaseline()


def _run_battery(tool, traps: list[dict]) -> dict:
    """Run a set of traps against a tool. Returns raw results."""
    correct_count = 0
    calibrated_count = 0
    trap_results = []

    for trap in traps:
        prompt = trap["prompt"]
        candidates = trap["candidates"]
        correct = trap["correct"]
        wrong_candidates = [c for c in candidates if c != correct]
        wrong = wrong_candidates[0] if wrong_candidates else candidates[-1]

        result = {"prompt": prompt, "correct": correct}

        try:
            ranked = tool.evaluate(prompt, candidates)
            top_candidate = ranked[0]["candidate"] if ranked else None
            is_correct = top_candidate == correct
            if is_correct:
                correct_count += 1
            result["top_candidate"] = top_candidate
            result["is_correct"] = is_correct
            result["rankings"] = ranked
        except Exception as e:
            result["evaluate_error"] = f"{type(e).__name__}: {e}"
            result["is_correct"] = False

        try:
            conf_correct = tool.confidence(prompt, correct)
            conf_wrong = tool.confidence(prompt, wrong)
            is_calibrated = conf_correct > conf_wrong
            if is_calibrated:
                calibrated_count += 1
            result["conf_correct"] = conf_correct
            result["conf_wrong"] = conf_wrong
            result["is_calibrated"] = is_calibrated
        except Exception as e:
            result["confidence_error"] = f"{type(e).__name__}: {e}"
            result["is_calibrated"] = False

        trap_results.append(result)

    n = len(traps)
    return {
        "accuracy": correct_count / n if n else 0,
        "calibration": calibrated_count / n if n else 0,
        "correct_count": correct_count,
        "calibrated_count": calibrated_count,
        "n_traps": n,
        "trap_results": trap_results,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_tool_from_code(code: str):
    """Load a ReasoningTool from source code string."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir(),
        encoding="utf-8",
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        spec = importlib.util.spec_from_file_location("_harness_test", tmp_path)
        if spec is None or spec.loader is None:
            raise ImportError("Failed to create module spec for harness test")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ReasoningTool()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        sys.modules.pop("_harness_test", None)


def load_tool_from_file(path: str | Path):
    """Load a ReasoningTool from a .py file."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location("_harness_file", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool = mod.ReasoningTool()
    sys.modules.pop("_harness_file", None)
    return tool


def run_ncd_baseline() -> dict:
    """Run the NCD baseline against all traps. Returns results dict."""
    return _run_battery(_ncd_baseline, TRAPS)


def run_dynamic_battery(tool, seed: int | None = None) -> dict | None:
    """Run dynamically generated traps (prevents overfitting to static battery).

    Returns results dict or None if trap generator unavailable.
    """
    try:
        from trap_generator import generate_trap_battery
        traps = generate_trap_battery(n_per_category=2, seed=seed)
        if not traps:
            return None
        return _run_battery(tool, traps)
    except ImportError:
        return None


def _load_expanded_battery(seed=42):
    """Try to load the 58-category expanded battery. Falls back to static 15."""
    try:
        from trap_generator_extended import generate_full_battery
        battery = generate_full_battery(n_per_category=2, seed=seed)
        if battery and len(set(t["category"] for t in battery)) > 20:
            return battery
    except ImportError:
        pass
    return None


def run_trap_battery(tool, timeout_per_trap: float = 5.0) -> dict:
    """Run all traps against a tool. Compare against NCD baseline.

    Uses the 58-category expanded battery if available, otherwise falls
    back to the static 15-trap battery. A tool passes if it strictly
    beats NCD on accuracy OR calibration (and doesn't lose on either).
    """
    # Try expanded battery first (58 categories)
    expanded = _load_expanded_battery()
    if expanded:
        traps = expanded
        log.debug("Using 58-category expanded battery (%d traps)", len(traps))
    else:
        traps = TRAPS
        log.debug("Using static 15-trap battery")

    # Run the tool
    tool_results = _run_battery(tool, traps)

    # Run NCD baseline
    ncd_results = _run_battery(_ncd_baseline, traps)

    tool_acc = tool_results["accuracy"]
    tool_cal = tool_results["calibration"]
    ncd_acc = ncd_results["accuracy"]
    ncd_cal = ncd_results["calibration"]

    # Must strictly beat NCD on at least one metric, not lose on either
    beats_acc = tool_acc > ncd_acc
    beats_cal = tool_cal > ncd_cal
    loses_acc = tool_acc < ncd_acc
    loses_cal = tool_cal < ncd_cal

    passed = (beats_acc or beats_cal) and not loses_acc and not loses_cal

    # Gate 6: Nemesis adversarial set (if available)
    adversarial_acc = None
    adversarial_n = 0
    nemesis_grid_path = Path(__file__).resolve().parent.parent.parent / "nemesis" / "grid" / "grid.json"
    if nemesis_grid_path.exists():
        try:
            import json
            grid_data = json.loads(nemesis_grid_path.read_text(encoding="utf-8"))
            adv_traps = []
            for cell in grid_data.get("cells", []):
                t = cell.get("task", {})
                if t.get("prompt") and t.get("candidates") and t.get("correct"):
                    adv_traps.append({
                        "prompt": t["prompt"],
                        "candidates": t["candidates"],
                        "correct": t["correct"],
                    })
            if adv_traps:
                adv_results = _run_battery(tool, adv_traps)
                adversarial_acc = adv_results["accuracy"]
                adversarial_n = adv_results["n_traps"]
                # Gate 6: must survive >= 50% of adversarial set
                if adversarial_acc < 0.5:
                    passed = False
        except Exception:
            log.debug("Gate 6 (Nemesis adversarial) unavailable, skipping")

    # Tier A/B breakdown (if traps have tier tags)
    tier_a_results = [tr for tr, trap in zip(tool_results["trap_results"], traps)
                      if trap.get("tier") == "A"]
    tier_b_results = [tr for tr, trap in zip(tool_results["trap_results"], traps)
                      if trap.get("tier") == "B"]
    tier_a_acc = (sum(1 for t in tier_a_results if t.get("is_correct")) / len(tier_a_results)
                  if tier_a_results else None)
    tier_b_acc = (sum(1 for t in tier_b_results if t.get("is_correct")) / len(tier_b_results)
                  if tier_b_results else None)

    result = {
        "accuracy": tool_acc,
        "calibration": tool_cal,
        "correct_count": tool_results["correct_count"],
        "calibrated_count": tool_results["calibrated_count"],
        "n_traps": tool_results["n_traps"],
        "n_categories": len(set(t.get("category", "") for t in traps)),
        "passed": passed,
        "trap_results": tool_results["trap_results"],
        "ncd_accuracy": ncd_acc,
        "ncd_calibration": ncd_cal,
        "margin_accuracy": round(tool_acc - ncd_acc, 4),
        "margin_calibration": round(tool_cal - ncd_cal, 4),
    }
    if tier_a_acc is not None:
        result["tier_a_accuracy"] = round(tier_a_acc, 4)
    if tier_b_acc is not None:
        result["tier_b_accuracy"] = round(tier_b_acc, 4)
    if adversarial_acc is not None:
        result["adversarial_accuracy"] = adversarial_acc
        result["adversarial_n"] = adversarial_n

    # Difficulty-weighted score (Tier 2 design)
    weighted = compute_weighted_score(tool_results["trap_results"], traps)
    if weighted is not None:
        result["weighted_score"] = weighted

    return result


# ---------------------------------------------------------------------------
# Difficulty-Weighted Scoring (Tier 2)
# ---------------------------------------------------------------------------
# Categories classified by best-existing-tool accuracy on 2026-03-29:
#   Easy (>80%): weight 0.3 — regex tools ace these
#   Medium (40-80%): weight 0.3 — partial regex coverage
#   Hard (<40%): weight 0.4 — require computation, not regex

CATEGORY_DIFFICULTY = {
    # === Easy (>80% for best regex tool) ===
    "validity_vs_truth": "easy", "vacuous_truth": "easy", "survivorship_bias": "easy",
    "sunk_cost": "easy", "subject_object": "easy", "second_order_belief": "easy",
    "regression_to_mean": "easy", "presupposition": "easy",
    "percentage_change_asymmetry": "easy", "numeric_stated_premise": "easy",
    "numeric_comparison": "easy", "denying_antecedent": "easy",
    "containment": "easy", "conditional_probability_asymmetry": "easy",
    "composition_fallacy": "easy", "all_but_n": "easy",
    "affirming_consequent": "easy", "tom_group_knowledge": "easy",
    "scope_ambiguity": "easy", "pronoun_ambiguity": "easy",
    "transitivity": "easy", "causal_necessary_sufficient_extended": "easy",
    "intention_vs_outcome": "easy", "tom_second_order_belief": "easy",
    "post_hoc": "easy", "order_of_operations": "easy",
    "necessary_vs_sufficient": "easy", "fencepost": "easy",
    "direction_composition": "easy",
    # === Medium (40-80% for best regex tool) ===
    "temporal_causal_ordering": "medium", "quantifier_inversion": "medium",
    "parallel_vs_sequential": "medium", "modus_tollens": "medium",
    "knowledge_attribution": "medium", "false_dichotomy": "medium",
    "empty_set": "medium", "demorgan": "medium", "chained_conditional": "medium",
    "inclusion_exclusion": "medium", "garden_path": "medium",
    "modular_arithmetic": "medium", "irrelevant_premise": "medium",
    "expected_value": "medium", "double_negation": "medium",
    "temporal_ordering": "medium", "self_referential_consistency": "medium",
    "rate_inverse_proportion": "medium", "premise_contradiction": "medium",
    "base_rate_neglect": "medium", "negation_scope": "medium",
    "multi_hop_deduction": "medium", "liar_detection": "medium",
    "left_right_reversal": "medium", "information_sufficiency": "medium",
    "false_belief_task": "medium", "causal_chain_length": "medium",
    "affirming_consequent_numeric": "medium", "framing_effect": "medium",
    "compositional_logic_arithmetic": "medium",
    "correlation_not_causation": "medium",
    "compositional_nested_tom_logic": "medium",
    "conjunction_fallacy": "medium", "temporal_concurrent_events": "medium",
    "argument_strength": "medium",
    # === Hard (<40% for best regex tool) ===
    "temporal_frequency_coincidence": "hard", "subset_inversion": "hard",
    "confidence_calibration": "hard", "causal_simpson_paradox": "hard",
    "temporal_scheduling_conflict": "hard", "temporal_rate_of_change": "hard",
    "temporal_duration_across_midnight": "hard",
    "compositional_depth_scaling": "hard",
    "compositional_temporal_causal": "hard", "tom_intention_reading": "hard",
    "compositional_logic_tom": "hard", "tom_mistaken_belief_chain": "hard",
    "temporal_sequence_reconstruction": "hard", "causal_confounding": "hard",
    "causal_common_cause": "hard", "tom_information_asymmetry": "hard",
    "temporal_age_reasoning": "hard", "tom_perspective_shift": "hard",
    "compositional_causal_statistical": "hard",
    "tom_strategic_deception": "hard",
    "compositional_arithmetic_temporal": "hard",
    "temporal_relative_day": "hard",
    "compositional_multi_hop_with_distractor": "hard",
    "causal_intervention": "hard", "causal_counterfactual": "hard",
    # === All Tier 2 categories are Hard by definition ===
    "stateful_register_machine": "hard", "epistemic_belief_tracking": "hard",
    "constraint_satisfaction": "hard", "recursive_evaluation": "hard",
    "counterfactual_dependency": "hard", "multi_step_arithmetic_carried": "hard",
    "bayesian_update": "hard", "information_sufficiency_t2": "hard",
    "defeasible_reasoning": "hard", "logical_consistency_checking": "hard",
    "temporal_interval_algebra": "hard", "stable_model_finding": "hard",
    "conditional_graph_traversal": "hard", "rule_application_order": "hard",
    "compositional_instruction_following": "hard",
    "referent_tracking_anaphora": "hard", "closed_world_negation": "hard",
    "argument_structure_analysis": "hard",
    "implicit_constraint_inference": "hard",
}

DIFFICULTY_WEIGHTS = {"easy": 0.3, "medium": 0.3, "hard": 0.4}


def compute_weighted_score(trap_results, traps):
    """Compute difficulty-weighted accuracy.

    Returns weighted score or None if categories can't be classified.
    """
    from collections import defaultdict

    # Group results by difficulty tier
    tier_correct = defaultdict(int)
    tier_total = defaultdict(int)

    for result, trap in zip(trap_results, traps):
        cat = trap.get("category", "")
        difficulty = CATEGORY_DIFFICULTY.get(cat, "medium")  # default medium for unknown
        tier_total[difficulty] += 1
        if result.get("is_correct"):
            tier_correct[difficulty] += 1

    if not tier_total:
        return None

    weighted = 0.0
    total_weight = 0.0
    for tier, weight in DIFFICULTY_WEIGHTS.items():
        if tier_total[tier] > 0:
            acc = tier_correct[tier] / tier_total[tier]
            weighted += weight * acc
            total_weight += weight

    return round(weighted / total_weight, 4) if total_weight > 0 else None
