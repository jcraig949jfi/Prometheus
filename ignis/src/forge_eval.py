"""
forge_eval.py — Bridge between Hephaestus forge tools and Ignis trap batteries.

Runs the top N forge tools against the Ignis trap battery and produces:
1. Per-tool accuracy on the trap set
2. Consensus scores (majority vote across tools)
3. Tool-trap correlation matrix (which tools get which traps right)
4. A ranked list of tools most useful for evolution fitness augmentation

Can also score a specific genome's output against forge tool consensus,
providing a non-neural fitness signal for CMA-ES.

Usage:
    python forge_eval.py                           # Full eval of top 20 tools
    python forge_eval.py --top-n 50                # Top 50 tools
    python forge_eval.py --output-dir results/forge_eval
"""

import argparse
import importlib.util
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import LOGIT_TRAPS, HELD_OUT_TRAPS
from phase_transition_study import ORDINAL_TRAPS

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FORGE_EVAL] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("forge_eval")

FORGE_DIR = Path(__file__).resolve().parent.parent.parent / "agents" / "hephaestus" / "forge"
ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


# ---------------------------------------------------------------------------
# Load forge tools
# ---------------------------------------------------------------------------

def load_forge_metadata():
    """Load all forge tool JSON metadata, sorted by test_accuracy descending."""
    tools = []
    for jf in sorted(FORGE_DIR.glob("*.json")):
        # Skip utils directory metadata if any
        if "utils" in str(jf):
            continue
        with open(jf) as f:
            meta = json.load(f)
        meta["name"] = jf.stem
        meta["json_path"] = str(jf)
        meta["py_path"] = str(jf.with_suffix(".py"))
        tools.append(meta)
    tools.sort(key=lambda t: t.get("test_accuracy", 0) or 0, reverse=True)
    return tools


def load_tool_class(py_path):
    """Dynamically import a forge tool's ReasoningTool class."""
    spec = importlib.util.spec_from_file_location("forge_tool", py_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ReasoningTool()


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def eval_tool_on_traps(tool_instance, traps):
    """
    Run a single forge tool against all traps.
    Returns list of {trap_name, correct, score_target, score_anti, margin}.
    """
    results = []
    for trap in traps:
        prompt = trap["prompt"]
        target = trap["target_token"]
        anti = trap["anti_token"]

        try:
            # Run the forge tool
            scored = tool_instance.evaluate(prompt, [target, anti])
            if not scored or len(scored) < 2:
                results.append({
                    "trap_name": trap["name"],
                    "correct": False,
                    "score_target": 0.0,
                    "score_anti": 0.0,
                    "margin": 0.0,
                    "error": "insufficient results",
                })
                continue

            # Find scores for target and anti
            score_map = {s["candidate"]: s["score"] for s in scored}
            s_target = score_map.get(target, 0.0)
            s_anti = score_map.get(anti, 0.0)
            margin = s_target - s_anti
            correct = margin > 0

            results.append({
                "trap_name": trap["name"],
                "correct": correct,
                "score_target": s_target,
                "score_anti": s_anti,
                "margin": margin,
            })
        except Exception as e:
            results.append({
                "trap_name": trap["name"],
                "correct": False,
                "score_target": 0.0,
                "score_anti": 0.0,
                "margin": 0.0,
                "error": str(e),
            })

    return results


def compute_consensus(all_tool_results, traps):
    """
    Compute majority-vote consensus across all tools for each trap.
    Returns dict: trap_name -> {n_correct, n_total, consensus_correct, avg_margin}.
    """
    consensus = {}
    trap_names = [t["name"] for t in traps]

    for trap_name in trap_names:
        votes = []
        margins = []
        for tool_name, results in all_tool_results.items():
            for r in results:
                if r["trap_name"] == trap_name:
                    votes.append(r["correct"])
                    margins.append(r["margin"])
                    break

        n_correct = sum(votes)
        n_total = len(votes)
        consensus[trap_name] = {
            "n_correct": int(n_correct),
            "n_total": int(n_total),
            "consensus_correct": bool(n_correct > n_total / 2),
            "consensus_ratio": float(n_correct / max(n_total, 1)),
            "avg_margin": float(np.mean(margins)) if margins else 0.0,
        }
    return consensus


def compute_tool_trap_matrix(all_tool_results, traps):
    """
    Build a binary matrix: tools x traps, 1=correct, 0=wrong.
    Returns (matrix, tool_names, trap_names).
    """
    tool_names = sorted(all_tool_results.keys())
    trap_names = [t["name"] for t in traps]

    matrix = np.zeros((len(tool_names), len(trap_names)), dtype=int)
    for i, tn in enumerate(tool_names):
        results = all_tool_results[tn]
        result_map = {r["trap_name"]: r["correct"] for r in results}
        for j, trap_name in enumerate(trap_names):
            matrix[i, j] = int(result_map.get(trap_name, False))

    return matrix, tool_names, trap_names


# ---------------------------------------------------------------------------
# Fitness augmentation: score a genome's performance using forge consensus
# ---------------------------------------------------------------------------

def forge_fitness_signal(steered_margins, traps, consensus):
    """
    Given steered logit margins from a candidate genome, compute a forge-weighted
    fitness bonus. Traps where forge consensus is strong get higher weight.

    Args:
        steered_margins: dict {trap_name: float} — logit margins under steering
        traps: list of trap dicts
        consensus: dict from compute_consensus()

    Returns:
        float — forge fitness bonus to add to CMA-ES fitness
    """
    bonus = 0.0
    for trap in traps:
        name = trap["name"]
        margin = steered_margins.get(name, 0.0)
        if name not in consensus:
            continue

        cons = consensus[name]
        weight = cons["consensus_ratio"]  # 0.0 to 1.0

        if cons["consensus_correct"]:
            # Forge tools agree this should be correct — reward positive margin
            bonus += weight * max(0.0, margin)
        else:
            # Forge tools disagree or think it's wrong — no penalty, just skip
            pass

    return bonus


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Forge tool evaluation on Ignis traps")
    parser.add_argument("--top-n", type=int, default=20,
                        help="Number of top tools to evaluate")
    parser.add_argument("--output-dir", type=str,
                        default=str(Path(__file__).parent.parent / "results" / "forge_eval"))
    parser.add_argument("--save-consensus", action="store_true", default=True,
                        help="Save consensus file for evolution integration")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load metadata and select top tools
    all_meta = load_forge_metadata()
    selected = all_meta[:args.top_n]

    log.info(f"Loaded {len(all_meta)} forge tools, evaluating top {len(selected)}")
    log.info(f"Trap battery: {len(ALL_TRAPS)} traps")

    # Evaluate each tool
    all_results = {}
    tool_summaries = []

    for i, meta in enumerate(selected):
        name = meta["name"]
        py_path = meta["py_path"]

        if not Path(py_path).exists():
            log.warning(f"  [{i+1}/{len(selected)}] SKIP {name} — no .py file")
            continue

        log.info(f"  [{i+1}/{len(selected)}] {name} (test_acc={meta.get('test_accuracy', '?')})")

        try:
            tool = load_tool_class(py_path)
            results = eval_tool_on_traps(tool, ALL_TRAPS)
            all_results[name] = results

            n_correct = sum(r["correct"] for r in results)
            accuracy = n_correct / len(results)
            tool_summaries.append({
                "name": name,
                "test_accuracy": meta.get("test_accuracy", 0),
                "trap_accuracy": accuracy,
                "n_correct": n_correct,
                "n_total": len(results),
            })
            log.info(f"    Trap accuracy: {n_correct}/{len(results)} = {accuracy:.3f}")
        except Exception as e:
            log.error(f"    FAILED: {e}")

    # Compute consensus
    consensus = compute_consensus(all_results, ALL_TRAPS)

    # Compute tool-trap matrix
    matrix, tool_names, trap_names = compute_tool_trap_matrix(all_results, ALL_TRAPS)

    # Find traps where consensus is strongest
    log.info("\nConsensus results:")
    consensus_correct = 0
    for trap_name, cons in consensus.items():
        correct_str = "YES" if cons["consensus_correct"] else "no"
        log.info(f"  {correct_str}  {cons['n_correct']}/{cons['n_total']}  {trap_name}")
        if cons["consensus_correct"]:
            consensus_correct += 1

    log.info(f"\nConsensus accuracy: {consensus_correct}/{len(ALL_TRAPS)}")

    # Find most complementary tools (get different traps right)
    log.info("\nTool complementarity (unique correct traps):")
    for i, tn in enumerate(tool_names):
        unique = 0
        for j in range(matrix.shape[1]):
            if matrix[i, j] == 1 and matrix[:, j].sum() == 1:
                unique += 1
        if unique > 0:
            log.info(f"  {tn}: {unique} unique solves")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Full results
    full_output = {
        "timestamp": timestamp,
        "n_tools": len(all_results),
        "n_traps": len(ALL_TRAPS),
        "tool_summaries": sorted(tool_summaries, key=lambda x: x["trap_accuracy"], reverse=True),
        "consensus": consensus,
        "consensus_accuracy": consensus_correct / len(ALL_TRAPS),
        "per_tool_results": {k: v for k, v in all_results.items()},
    }

    def numpy_safe(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    with open(output_dir / f"forge_eval_{timestamp}.json", "w") as f:
        json.dump(full_output, f, indent=2, default=numpy_safe)

    # Save consensus file (for evolution integration)
    if args.save_consensus:
        consensus_file = output_dir / "forge_consensus.json"
        with open(consensus_file, "w") as f:
            json.dump({
                "consensus": consensus,
                "n_tools": len(all_results),
                "timestamp": timestamp,
            }, f, indent=2, default=numpy_safe)
        log.info(f"Consensus saved to {consensus_file}")

    # Save tool-trap matrix as CSV for analysis
    with open(output_dir / f"tool_trap_matrix_{timestamp}.csv", "w") as f:
        f.write("tool," + ",".join(trap_names) + ",accuracy\n")
        for i, tn in enumerate(tool_names):
            row = matrix[i]
            acc = row.sum() / len(row)
            f.write(tn + "," + ",".join(str(x) for x in row) + f",{acc:.3f}\n")

    log.info(f"\nResults saved to {output_dir}")
    log.info("Done.")


if __name__ == "__main__":
    main()
