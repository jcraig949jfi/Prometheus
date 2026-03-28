"""Test runner for v2 rebuilt tools + Tier 2 wrappers against the trap battery.

Tests:
  Tier 1 (standalone):  IBAI v2, EFME v2, Bandit v2
  Tier 2 (wrappers):    PerturbationCalibrator(IBAI v2), CriticalityRegularizer(IBAI v2)
  Baseline:             NCD

Also re-tests the original v1 tools for comparison, and retires Tier 3.
"""

import sys
from pathlib import Path

# Ensure we can import from src/
sys.path.insert(0, str(Path(__file__).parent / "src"))

from test_harness import TRAPS, _run_battery, _NCDBaseline, load_tool_from_file

FORGE = Path(__file__).parent / "forge"


def load_tool(name: str):
    """Load a ReasoningTool from forge/ by filename."""
    path = FORGE / name
    return load_tool_from_file(path)


def run_and_report(label: str, tool, traps=None):
    """Run trap battery and print results."""
    if traps is None:
        traps = TRAPS
    results = _run_battery(tool, traps)
    acc = results["accuracy"]
    cal = results["calibration"]
    cc = results["correct_count"]
    calcount = results["calibrated_count"]
    n = results["n_traps"]

    print(f"  {label:50s}  acc={acc:.1%} ({cc}/{n})  cal={cal:.1%} ({calcount}/{n})")

    # Print per-trap detail for failures
    for tr in results["trap_results"]:
        correct = tr.get("is_correct", False)
        calibrated = tr.get("is_calibrated", False)
        if not correct or not calibrated:
            prompt_short = tr["prompt"][:60]
            top = tr.get("top_candidate", "?")
            marks = ("X" if not correct else "ok") + "/" + ("X" if not calibrated else "ok")
            print(f"    [{marks}] {prompt_short}... -> {top}")

    return results


def main():
    print("=" * 80)
    print("TRAP BATTERY: v2 Tool Evaluation")
    print(f"Traps: {len(TRAPS)} ({10} original + {len(TRAPS)-10} compositional)")
    print("=" * 80)

    # -- NCD Baseline --
    print("\n--- BASELINE ---")
    ncd = _NCDBaseline()
    ncd_results = run_and_report("NCD Baseline", ncd)
    ncd_acc = ncd_results["accuracy"]
    ncd_cal = ncd_results["calibration"]
    print(f"\n  NCD floor: acc={ncd_acc:.1%}, cal={ncd_cal:.1%}")

    # -- Tier 1: v2 Rebuilds --
    print("\n--- TIER 1: v2 REBUILDS ---")
    tier1_tools = {
        "IBAI v2": "ibai_v2.py",
        "EFME v2": "efme_v2.py",
        "Bandit v2": "bandit_v2.py",
    }
    tier1_results = {}
    for label, fname in tier1_tools.items():
        try:
            tool = load_tool(fname)
            r = run_and_report(label, tool)
            tier1_results[label] = r
        except Exception as e:
            print(f"  {label:50s}  LOAD ERROR: {e}")

    # -- Tier 2: Wrappers on best Tier 1 tool --
    print("\n--- TIER 2: UTILITY WRAPPERS (on IBAI v2) ---")
    try:
        ibai = load_tool("ibai_v2.py")

        # PerturbationCalibrator
        sys.path.insert(0, str(FORGE))
        from perturbation_calibrator import PerturbationCalibrator
        from criticality_regularizer import CriticalityRegularizer

        # Wrap IBAI v2 with perturbation calibrator
        class PerturbWrapped:
            def __init__(self):
                self._cal = PerturbationCalibrator(ibai)
            def evaluate(self, prompt, candidates):
                return self._cal.calibrated_evaluate(prompt, candidates)
            def confidence(self, prompt, answer):
                return self._cal.calibrated_confidence(prompt, answer)

        run_and_report("PerturbationCalibrator(IBAI v2)", PerturbWrapped())

        # Wrap IBAI v2 with criticality regularizer
        class CritWrapped:
            def __init__(self):
                self._reg = CriticalityRegularizer(ibai)
            def evaluate(self, prompt, candidates):
                return self._reg.regularized_evaluate(prompt, candidates)
            def confidence(self, prompt, answer):
                return ibai.confidence(prompt, answer)

        run_and_report("CriticalityRegularizer(IBAI v2)", CritWrapped())

        # Landscape quality report
        print("\n  Landscape quality (IBAI v2 raw):")
        reg = CriticalityRegularizer(ibai)
        for trap in TRAPS[:5]:
            q = reg.landscape_quality(trap["prompt"], trap["candidates"])
            p_short = trap["prompt"][:50]
            print(f"    {p_short:52s} crit={q['criticality']:.3f} var={q['variance']:.4f} {'FLAT' if q['is_flat'] else ''}")

    except Exception as e:
        print(f"  Tier 2 wrapper error: {e}")
        import traceback
        traceback.print_exc()

    # -- Original v1 tools (for comparison) --
    print("\n--- ORIGINAL v1 TOOLS (for comparison) ---")
    v1_tools = {
        "IBAI v1 (hash)": "information_theory_x_active_inference_x_free_energy_principle.py",
        "EFME v1 (keyword)": "ergodic_theory_x_falsificationism_x_maximum_entropy.py",
        "Bandit v1 (hash)": "information_theory_x_sparse_autoencoders_x_multi-armed_bandits.py",
        "EATM-S v1": "ergodic_theory_x_theory_of_mind_x_abductive_reasoning.py",
        "ME-CGA v1": "information_theory_x_genetic_algorithms_x_criticality.py",
    }
    for label, fname in v1_tools.items():
        try:
            tool = load_tool(fname)
            run_and_report(label, tool)
        except Exception as e:
            print(f"  {label:50s}  LOAD ERROR: {e}")

    # -- Tier 3: Retired --
    print("\n--- TIER 3: RETIRED ---")
    retired = {
        "EGSAE-MC (retired)": "ergodic_theory_x_sparse_autoencoders_x_model_checking.py",
        "CPCTTN (retired)": "tensor_decomposition_x_criticality_x_free_energy_principle.py",
    }
    for label, fname in retired.items():
        try:
            tool = load_tool(fname)
            run_and_report(label, tool)
        except Exception as e:
            print(f"  {label:50s}  LOAD ERROR: {e}")

    # -- Summary --
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nNCD baseline: acc={ncd_acc:.1%}, cal={ncd_cal:.1%}")
    print("\nTier 1 vs NCD:")
    for label, r in tier1_results.items():
        margin_acc = r["accuracy"] - ncd_acc
        margin_cal = r["calibration"] - ncd_cal
        beats = (margin_acc > 0 or margin_cal > 0) and margin_acc >= 0 and margin_cal >= 0
        status = "BEATS NCD" if beats else "FAILS"
        print(f"  {label:30s}  margin_acc={margin_acc:+.1%}  margin_cal={margin_cal:+.1%}  [{status}]")


if __name__ == "__main__":
    main()
