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


def run_trap_battery(tool, timeout_per_trap: float = 5.0) -> dict:
    """Run all traps against a tool. Compare against NCD baseline.

    A tool passes if it strictly beats NCD on accuracy OR calibration
    (and doesn't lose on either). Tying both = fail.
    """
    # Run the tool
    tool_results = _run_battery(tool, TRAPS)

    # Run NCD baseline
    ncd_results = _run_battery(_ncd_baseline, TRAPS)

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

    result = {
        "accuracy": tool_acc,
        "calibration": tool_cal,
        "correct_count": tool_results["correct_count"],
        "calibrated_count": tool_results["calibrated_count"],
        "n_traps": tool_results["n_traps"],
        "passed": passed,
        "trap_results": tool_results["trap_results"],
        "ncd_accuracy": ncd_acc,
        "ncd_calibration": ncd_cal,
        "margin_accuracy": round(tool_acc - ncd_acc, 4),
        "margin_calibration": round(tool_cal - ncd_cal, 4),
    }
    if adversarial_acc is not None:
        result["adversarial_accuracy"] = adversarial_acc
        result["adversarial_n"] = adversarial_n
    return result
