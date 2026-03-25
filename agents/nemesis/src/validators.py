"""Validate adversarial task quality before admitting to the grid.

Prevents bad ground truth from polluting the adversarial set.
Uses the execution evaluator as a cross-check.
"""

import logging
import sys
from pathlib import Path

log = logging.getLogger("nemesis.validators")

HEPHAESTUS_ROOT = Path(__file__).resolve().parent.parent.parent / "hephaestus"


def _load_execution_evaluator():
    """Load the execution evaluator for ground truth cross-checking."""
    exec_eval_path = HEPHAESTUS_ROOT / "forge" / "execution_evaluator.py"
    if not exec_eval_path.exists():
        return None
    try:
        sys.path.insert(0, str(HEPHAESTUS_ROOT / "src"))
        from test_harness import load_tool_from_file
        return load_tool_from_file(exec_eval_path)
    except Exception as e:
        log.warning("Could not load execution evaluator: %s", e)
        return None


_exec_eval = None


def validate_task(prompt: str, candidates: list[str], correct: str) -> tuple[bool, str]:
    """Validate an adversarial task before grid admission.

    Returns (valid, reason).
    """
    # 1. Basic structural validity
    if not prompt or not prompt.strip():
        return False, "empty_prompt"
    if not candidates or len(candidates) < 2:
        return False, "too_few_candidates"
    if correct not in candidates:
        return False, "correct_not_in_candidates"
    if len(set(candidates)) < len(candidates):
        return False, "duplicate_candidates"

    # 2. Prompt must contain a question or assertion
    if "?" not in prompt and not any(
        prompt.lower().startswith(w) for w in ("is ", "are ", "which ", "who ", "what ", "how ")
    ):
        return False, "no_question_detected"

    # 3. Cross-check with execution evaluator (if available)
    global _exec_eval
    if _exec_eval is None:
        _exec_eval = _load_execution_evaluator()

    if _exec_eval is not None:
        try:
            ranked = _exec_eval.evaluate(prompt, candidates)
            if ranked:
                exec_answer = ranked[0]["candidate"]
                exec_reasoning = ranked[0].get("reasoning", "")
                # Only flag as suspect if the execution evaluator has high confidence
                # AND disagrees (i.e., it matched a computable pattern but got a different answer)
                if (exec_answer != correct
                        and "execution:" in exec_reasoning
                        and "fallback:" not in exec_reasoning):
                    log.warning("Execution evaluator disagrees: exec=%s, claimed=%s, prompt=%s",
                                exec_answer, correct, prompt[:80])
                    return False, f"exec_evaluator_disagrees: {exec_answer} != {correct}"
        except Exception:
            pass  # execution evaluator failed, don't block on it

    return True, "ok"
