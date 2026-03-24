"""Trap battery for testing forged reasoning tools."""

import importlib.util
import sys
import tempfile
from pathlib import Path

TRAPS = [
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
]

ACCURACY_THRESHOLD = 0.6
CALIBRATION_THRESHOLD = 0.5


def load_tool_from_code(code: str):
    """Load a ReasoningTool from source code string."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        spec = importlib.util.spec_from_file_location("_harness_test", tmp_path)
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
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool = mod.ReasoningTool()
    sys.modules.pop("_harness_file", None)
    return tool


def run_trap_battery(tool, timeout_per_trap: float = 5.0) -> dict:
    """Run all traps against a tool. Returns results dict."""
    correct_count = 0
    calibrated_count = 0
    trap_results = []

    for trap in TRAPS:
        prompt = trap["prompt"]
        candidates = trap["candidates"]
        correct = trap["correct"]
        wrong = [c for c in candidates if c != correct][0]

        result = {"prompt": prompt, "correct": correct}

        try:
            # Test evaluate()
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
            # Test calibration
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

    n_traps = len(TRAPS)
    accuracy = correct_count / n_traps
    calibration = calibrated_count / n_traps

    passed = accuracy >= ACCURACY_THRESHOLD and calibration >= CALIBRATION_THRESHOLD

    return {
        "accuracy": accuracy,
        "calibration": calibration,
        "correct_count": correct_count,
        "calibrated_count": calibrated_count,
        "n_traps": n_traps,
        "passed": passed,
        "trap_results": trap_results,
    }
