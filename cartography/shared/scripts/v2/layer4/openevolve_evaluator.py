"""OpenEvolve Evaluator — bridges OpenEvolve's evaluation interface to our
falsification battery.

OpenEvolve evaluators are Python files with an ``evaluate(program_path)``
function that returns ``dict[str, float]``.  This module reads the candidate
program file written by OpenEvolve, extracts the search function, runs it
through the sandbox on test dataset pairs, then feeds results into the
falsification battery.

Usage (standalone test):
    python openevolve_evaluator.py path/to/candidate.py

Usage (via OpenEvolve):
    openevolve run openevolve_problem.py openevolve_evaluator.py --config config.yaml
"""

import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Path setup — make our pipeline importable
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent          # layer4/
_V2_DIR   = _THIS_DIR.parent                         # v2/
_SS_DIR   = _V2_DIR.parent                           # shared/scripts/

for p in [str(_V2_DIR), str(_SS_DIR), str(_THIS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from sandbox import Sandbox, validate_code, complexity_score, extract_function_name

# Import battery with a fallback — it depends on cycle_logger
try:
    from falsification_battery import run_battery
    _BATTERY_AVAILABLE = True
except Exception:
    _BATTERY_AVAILABLE = False


# ---------------------------------------------------------------------------
# Synthetic test pairs (deterministic, no external data needed)
# ---------------------------------------------------------------------------

def _make_test_pairs(seed: int = 42) -> list[tuple]:
    """Five dataset pairs covering different correlation regimes."""
    rng = np.random.RandomState(seed)
    pairs = []

    # 1. Moderate linear correlation (r ~ 0.5)
    a = rng.randn(120)
    b = 0.5 * a + 0.5 * rng.randn(120)
    pairs.append((a, b, "linear_r05"))

    # 2. Independent exponentials (null — no relationship)
    a = rng.exponential(2.0, 100)
    b = rng.exponential(2.0, 100)
    pairs.append((a, b, "indep_exp"))

    # 3. Different distribution families
    a = rng.randn(100)
    b = rng.exponential(1.0, 100)
    pairs.append((a, b, "normal_vs_exp"))

    # 4. Nonlinear (quadratic) relationship
    a = rng.uniform(-3, 3, 150)
    b = a ** 2 + 0.3 * rng.randn(150)
    pairs.append((a, b, "quadratic"))

    # 5. Integer sequences with modular structure
    a = np.arange(2, 102, dtype=float)
    b = np.array([float(x ** 2 % 97) for x in range(2, 102)])
    pairs.append((a, b, "modular_quad"))

    return pairs


_TEST_PAIRS = _make_test_pairs()


# ---------------------------------------------------------------------------
# Core evaluation logic
# ---------------------------------------------------------------------------

_sandbox = Sandbox(timeout_s=10, max_memory_mb=256)


def _score_candidate(code_str: str) -> dict:
    """Score a candidate search function.

    Returns dict with:
        fitness            — primary objective (0-1, higher is better)
        battery_pass_rate  — fraction of test pairs that survive the battery
        novel_kills        — count of test pairs where function produces novel kill patterns
        complexity         — AST node count (lower is better)
        executes           — 1.0 if the function runs on all pairs, 0.0 otherwise
        mean_p_value       — geometric mean of reported p-values (lower = stronger signal)
    """
    # Defaults for failure
    FAIL = {
        "fitness": 0.0,
        "battery_pass_rate": 0.0,
        "novel_kills": 0,
        "complexity": 999,
        "executes": 0.0,
        "mean_p_value": 1.0,
    }

    # 1. Validate code safety
    safe, reason = validate_code(code_str)
    if not safe:
        return FAIL

    # 2. Find the search function name
    func_name = extract_function_name(code_str)
    if func_name is None:
        return FAIL

    # 3. Complexity / parsimony
    cx = complexity_score(code_str)
    if cx > 500:
        return FAIL

    # 4. Execute on each test pair, collect results
    exec_ok = 0
    battery_survived = 0
    battery_tested = 0
    p_values = []
    novel_kills = 0

    for values_a, values_b, label in _TEST_PAIRS:
        try:
            result = _sandbox.execute(code_str, func_name, values_a.tolist(), values_b.tolist())
        except Exception:
            continue

        if not result.get("success"):
            continue

        ret = result.get("result")
        if not isinstance(ret, dict):
            continue
        if "statistic" not in ret or "p_value" not in ret:
            continue

        exec_ok += 1
        p_val = float(ret.get("p_value", 1.0))
        p_values.append(max(p_val, 1e-300))  # clamp for log

        # 5. Run battery if available
        if _BATTERY_AVAILABLE:
            try:
                n = min(len(values_a), len(values_b))
                if n >= 10:
                    verdict, batt_results = run_battery(
                        np.asarray(values_a[:n], dtype=float),
                        np.asarray(values_b[:n], dtype=float),
                        claim=f"openevolve_{label}",
                    )
                    battery_tested += 1
                    if verdict == "SURVIVES":
                        battery_survived += 1
                    else:
                        # Count kill patterns as novelty signal
                        kills = [r.get("test", "?") for r in batt_results
                                 if isinstance(r, dict) and r.get("verdict") == "FAIL"]
                        if kills:
                            novel_kills += 1
            except Exception:
                pass  # battery failure doesn't sink the candidate

    # 6. Compute metrics
    n_pairs = len(_TEST_PAIRS)
    exec_rate = exec_ok / n_pairs if n_pairs > 0 else 0.0

    if not p_values:
        return FAIL

    # Geometric mean of p-values (log-space)
    mean_log_p = float(np.mean(np.log10(p_values)))
    mean_p = 10 ** mean_log_p

    battery_rate = battery_survived / battery_tested if battery_tested > 0 else 0.0

    # Parsimony: reward shorter code (AST nodes), cap at 200
    parsimony = max(0.0, 1.0 - cx / 200.0)

    # Fitness: multi-objective blend
    #   - execution (must run)           : 20%
    #   - battery pass rate              : 30%
    #   - signal strength (-log10 p)     : 25%
    #   - parsimony                      : 15%
    #   - novel kill patterns            : 10%
    signal_strength = min(1.0, max(0.0, -mean_log_p / 5.0))  # 0..1 scaled
    novel_score = min(1.0, novel_kills / max(1, n_pairs))

    fitness = (
        0.20 * exec_rate
        + 0.30 * battery_rate
        + 0.25 * signal_strength
        + 0.15 * parsimony
        + 0.10 * novel_score
    )

    return {
        "fitness": round(float(fitness), 6),
        "battery_pass_rate": round(float(battery_rate), 4),
        "novel_kills": int(novel_kills),
        "complexity": int(cx),
        "executes": round(float(exec_rate), 4),
        "mean_p_value": round(float(mean_p), 8),
    }


# ---------------------------------------------------------------------------
# OpenEvolve interface: evaluate(program_path) -> dict[str, float]
# ---------------------------------------------------------------------------

def evaluate(program_path: str) -> dict:
    """OpenEvolve entry point.

    Args:
        program_path: Path to a .py file written by OpenEvolve containing a
            search function inside an EVOLVE-BLOCK.

    Returns:
        dict of metric name -> float.  The first key ("fitness") is the
        primary optimization objective.
    """
    try:
        code_str = Path(program_path).read_text(encoding="utf-8")
    except Exception as e:
        return {"fitness": 0.0, "battery_pass_rate": 0.0, "novel_kills": 0,
                "complexity": 999, "executes": 0.0, "mean_p_value": 1.0,
                "error": str(e)}

    try:
        metrics = _score_candidate(code_str)
    except Exception as e:
        metrics = {"fitness": 0.0, "battery_pass_rate": 0.0, "novel_kills": 0,
                   "complexity": 999, "executes": 0.0, "mean_p_value": 1.0,
                   "error": f"{type(e).__name__}: {e}"}

    return metrics


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Evaluating: {path}")
        result = evaluate(path)
        print(json.dumps(result, indent=2))
    else:
        # Self-test with inline code
        test_code = '''
import numpy as np
from scipy import stats

def search_function(values_a, values_b):
    """Search for structural connection between two datasets."""
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    r, p = stats.pearsonr(values_a[:n], values_b[:n])
    return {"statistic": float(r), "p_value": float(p), "description": f"Pearson r={r:.4f}"}
'''
        print("Self-test: scoring inline Pearson function")
        result = _score_candidate(test_code)
        print(json.dumps(result, indent=2))

        # Also test via file path (the OpenEvolve interface)
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,
                                          encoding="utf-8") as f:
            f.write(test_code)
            tmp_path = f.name

        print(f"\nFile-based test: {tmp_path}")
        result2 = evaluate(tmp_path)
        print(json.dumps(result2, indent=2))

        import os
        os.unlink(tmp_path)
