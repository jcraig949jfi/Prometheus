"""
decision_gate.py — Auto-analyzes refinement chain outputs and writes a decision report.

Reads JSON outputs from controlled_cot_test.py and sae_decompose.py, applies
decision logic, and produces a decision_report.md with next-step recommendations.

Usage:
    python decision_gate.py --results-dir results/refinement/
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.decision_gate")


# ---------------------------------------------------------------------------
# JSON discovery
# ---------------------------------------------------------------------------

def find_latest_json(results_dir: Path, prefix: str) -> dict | None:
    """Find the most recent JSON file matching the given prefix."""
    candidates = sorted(results_dir.glob(f"{prefix}_*.json"), reverse=True)
    if not candidates:
        log.warning(f"No {prefix}_*.json found in {results_dir}")
        return None
    path = candidates[0]
    log.info(f"Loading {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Decision logic
# ---------------------------------------------------------------------------

def analyze(cot_data: dict | None, sae_data: dict | None) -> dict:
    """Apply decision tree and return recommendation."""
    cot_verdict = cot_data.get("verdict", "MISSING") if cot_data else "MISSING"
    sae_verdict = sae_data.get("verdict", "MISSING") if sae_data else "MISSING"

    recommendation = ""
    config_suggestion = None
    estimated_gpu_hours = "Unknown"
    next_command = ""

    # ------------------------------------------------------------------
    # Decision matrix
    # ------------------------------------------------------------------
    if cot_verdict == "CONFIRMED" and sae_verdict == "SUPPRESSOR":
        recommendation = (
            "Evolve for CoT-alignment. The current vector suppresses heuristics "
            "and the anti-CoT signal is confirmed real (not a prompt-length artifact). "
            "CoT-aligned evolution may find genuine precipitation vectors that "
            "activate reasoning pathways rather than suppressing shortcuts."
        )
        config_suggestion = {
            "experiment": "cot_aligned_cmaes",
            "description": "CMA-ES with CoT-alignment bonus in fitness",
            "fitness_modifications": [
                "Add cosine(vector, CoT_direction) bonus term",
                "Weight CoT-alignment at 0.3x logit margin weight",
                "Use embedded-CoT directions as alignment targets",
            ],
            "population_size": 64,
            "n_generations": 200,
            "notes": "Start from current best genome as initial mean",
        }
        estimated_gpu_hours = "4-8 hours (1x A100 or 2x RTX 3090)"
        next_command = (
            "python ignis_orchestrator.py "
            "--config configs/cot_aligned_cmaes.yaml "
            "--device cuda"
        )

    elif cot_verdict == "CONFIRMED" and sae_verdict == "AMPLIFIER":
        recommendation = (
            "Surprising: vector activates reasoning features despite confirmed "
            "anti-CoT correlation. This suggests the vector amplifies a different "
            "reasoning mode than chain-of-thought. Run cross-architecture comparison "
            "on Gemma-2-2B (which has Gemma Scope SAE weights) to validate whether "
            "this pattern generalizes."
        )
        config_suggestion = {
            "experiment": "cross_architecture_comparison",
            "description": "Replicate on Gemma-2-2B with Gemma Scope SAE",
            "target_model": "google/gemma-2-2b",
            "sae_release": "gemma-scope-2b-pt-res",
            "notes": "Use Gemma Scope for ground-truth feature decomposition",
        }
        estimated_gpu_hours = "2-4 hours (model + SAE analysis)"
        next_command = (
            "python sae_decompose.py "
            "--genome best_genome.pt "
            "--model google/gemma-2-2b "
            "--device cuda "
            "--output-dir results/gemma_comparison/"
        )

    elif cot_verdict == "CONFIRMED" and sae_verdict == "MIXED":
        recommendation = (
            "Anti-CoT confirmed, but vector has mixed SAE feature profile. "
            "The vector may be targeting a specific reasoning sub-circuit. "
            "Recommend layerwise probing to isolate which layers contribute "
            "most to the anti-CoT signal, then re-run SAE at those specific layers."
        )
        estimated_gpu_hours = "1-2 hours"
        next_command = (
            "python layerwise_probe.py "
            "--genome best_genome.pt "
            "--device cuda "
            "--output-dir results/layerwise/"
        )

    elif cot_verdict == "ARTIFACT":
        recommendation = (
            "Anti-CoT was a prompt-length artifact. The steering vector does not "
            "genuinely oppose chain-of-thought reasoning. Focus on held-out trap "
            "expansion and SAE feature analysis instead. The vector may still be "
            "useful — it just works through a different mechanism than CoT suppression."
        )
        config_suggestion = {
            "experiment": "expanded_trap_battery",
            "description": "Expand held-out traps and re-evaluate generalization",
            "new_traps": [
                "Base rate neglect",
                "Conjunction fallacy (Linda problem)",
                "Anchoring bias",
                "Survivorship bias",
            ],
            "notes": "If vector generalizes to new traps, mechanism is bypass not precipitation",
        }
        estimated_gpu_hours = "1-2 hours"
        next_command = (
            "python titan_generalization.py "
            "--genome best_genome.pt "
            "--device cuda "
            "--output-dir results/generalization/"
        )

    elif cot_verdict == "AMBIGUOUS":
        recommendation = (
            "CoT confound test was ambiguous — not enough signal to determine "
            "if anti-CoT is real or artifact. Recommend collecting more data: "
            "add more trap variants with embedded reasoning, and try multiple "
            "injection layers."
        )
        estimated_gpu_hours = "2-3 hours"
        next_command = (
            "python controlled_cot_test.py "
            "--genome best_genome.pt "
            "--device cuda "
            "--output-dir results/cot_extended/"
        )

    elif sae_verdict == "UNKNOWN":
        recommendation = (
            "SAE analysis unavailable (no pre-trained SAE weights for this model). "
            "Two options: (1) Train SAE weights for this model using SAELens "
            "(expensive, ~24 GPU hours), or (2) Switch to Gemma-2-2B which has "
            "Gemma Scope SAE weights available for immediate decomposition."
        )
        config_suggestion = {
            "experiment": "switch_to_gemma",
            "description": "Replicate Ignis pipeline on Gemma-2-2B for SAE access",
            "target_model": "google/gemma-2-2b",
            "sae_release": "gemma-scope-2b-pt-res",
            "notes": "Gemma Scope provides pre-trained SAE for all residual stream layers",
        }
        estimated_gpu_hours = "6-12 hours (full CMA-ES + analysis on new model)"
        next_command = (
            "python ignis_orchestrator.py "
            "--config configs/gemma_2b_replication.yaml "
            "--device cuda"
        )

    else:
        recommendation = (
            f"Unhandled combination: CoT={cot_verdict}, SAE={sae_verdict}. "
            f"Review raw JSON outputs manually."
        )
        estimated_gpu_hours = "N/A"
        next_command = "# Review results manually"

    return {
        "cot_verdict": cot_verdict,
        "sae_verdict": sae_verdict,
        "recommendation": recommendation,
        "config_suggestion": config_suggestion,
        "estimated_gpu_hours": estimated_gpu_hours,
        "next_command": next_command,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(
    decision: dict,
    cot_data: dict | None,
    sae_data: dict | None,
) -> str:
    """Build Markdown decision report."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append(f"# Ignis Refinement Chain — Decision Report")
    lines.append(f"")
    lines.append(f"Generated: {ts}")
    lines.append(f"")

    # ------------------------------------------------------------------
    # Step 1 summary
    # ------------------------------------------------------------------
    lines.append(f"## Step 1: Controlled CoT Test")
    lines.append(f"")
    if cot_data:
        lines.append(f"- **Verdict:** {cot_data.get('verdict', 'N/A')}")
        lines.append(f"- **Model:** {cot_data.get('model', 'N/A')}")
        lines.append(f"- **Layer:** {cot_data.get('layer', 'N/A')}")
        lines.append(f"- **Traps tested:** {cot_data.get('n_traps', 'N/A')}")
        agg = cot_data.get("aggregate", {})
        lines.append(f"- **Mean cos(v, embedded CoT):** {agg.get('mean_cos_v_embedded', 'N/A')}")
        lines.append(f"- **Negative/Positive/Ambiguous:** "
                      f"{agg.get('num_negative', '?')}/"
                      f"{agg.get('num_positive', '?')}/"
                      f"{agg.get('num_ambiguous', '?')}")
        lines.append(f"- **Explanation:** {cot_data.get('explanation', 'N/A')}")
    else:
        lines.append(f"- **Status:** NOT RUN (no controlled_cot_test JSON found)")
    lines.append(f"")

    # ------------------------------------------------------------------
    # Step 2 summary
    # ------------------------------------------------------------------
    lines.append(f"## Step 2: SAE / PCA Decomposition")
    lines.append(f"")
    if sae_data:
        lines.append(f"- **Verdict:** {sae_data.get('verdict', 'N/A')}")
        lines.append(f"- **Model:** {sae_data.get('model', 'N/A')}")
        lines.append(f"- **Layer:** {sae_data.get('layer', 'N/A')}")

        sae_result = sae_data.get("sae_result")
        if sae_result:
            lines.append(f"- **SAE approach:** Available (release: {sae_result.get('release_id')})")
            lines.append(f"- **Active features:** {sae_result.get('n_active')}/{sae_result.get('n_features_total')}")
            lines.append(f"- **Reconstruction cosine:** {sae_result.get('reconstruction_cosine')}")
        else:
            lines.append(f"- **SAE approach:** Not available (no pre-trained weights)")

        pca = sae_data.get("pca_result", {})
        centroid = pca.get("centroid_analysis", {})
        cos_corr = centroid.get("cos_vec_to_correction_direction")
        if cos_corr is not None:
            lines.append(f"- **PCA cos(vec, correction dir):** {cos_corr}")
            lines.append(f"- **Baseline correct/incorrect:** "
                          f"{centroid.get('n_correct_baseline', '?')}/"
                          f"{centroid.get('n_incorrect_baseline', '?')}")
        lines.append(f"- **Explanation:** {sae_data.get('explanation', 'N/A')}")
    else:
        lines.append(f"- **Status:** NOT RUN (no sae_decompose JSON found)")
    lines.append(f"")

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------
    lines.append(f"## Decision")
    lines.append(f"")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| CoT Verdict | {decision['cot_verdict']} |")
    lines.append(f"| SAE Verdict | {decision['sae_verdict']} |")
    lines.append(f"| Est. GPU Time | {decision['estimated_gpu_hours']} |")
    lines.append(f"")
    lines.append(f"### Recommendation")
    lines.append(f"")
    lines.append(decision["recommendation"])
    lines.append(f"")

    if decision["config_suggestion"]:
        lines.append(f"### Suggested Configuration")
        lines.append(f"")
        lines.append(f"```json")
        lines.append(json.dumps(decision["config_suggestion"], indent=2))
        lines.append(f"```")
        lines.append(f"")

    lines.append(f"### Next Command")
    lines.append(f"")
    lines.append(f"```bash")
    lines.append(decision["next_command"])
    lines.append(f"```")
    lines.append(f"")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Decision gate for Ignis refinement chain",
    )
    parser.add_argument(
        "--results-dir", type=str, required=True,
        help="Directory containing controlled_cot_test and sae_decompose JSON outputs",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        log.error(f"Results directory does not exist: {results_dir}")
        sys.exit(1)

    # Load latest results
    cot_data = find_latest_json(results_dir, "controlled_cot_test")
    sae_data = find_latest_json(results_dir, "sae_decompose")

    if cot_data is None and sae_data is None:
        log.error("No results found. Run controlled_cot_test.py and/or sae_decompose.py first.")
        sys.exit(1)

    # Analyze
    decision = analyze(cot_data, sae_data)

    # Build report
    report = build_report(decision, cot_data, sae_data)

    # Write report
    report_path = results_dir / "decision_report.md"
    report_path.write_text(report, encoding="utf-8")
    log.info(f"Decision report written to {report_path}")

    # Also write decision JSON for machine consumption
    decision_json = {
        "analysis": "decision_gate",
        "cot_verdict": decision["cot_verdict"],
        "sae_verdict": decision["sae_verdict"],
        "recommendation": decision["recommendation"],
        "config_suggestion": decision["config_suggestion"],
        "estimated_gpu_hours": decision["estimated_gpu_hours"],
        "next_command": decision["next_command"],
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }
    json_path = results_dir / "decision_gate.json"
    json_path.write_text(json.dumps(decision_json, indent=2), encoding="utf-8")
    log.info(f"Decision JSON written to {json_path}")

    # Print summary to console
    print("\n" + "=" * 60)
    print("DECISION GATE — RESULT")
    print("=" * 60)
    print(f"CoT Verdict:  {decision['cot_verdict']}")
    print(f"SAE Verdict:  {decision['sae_verdict']}")
    print(f"GPU Estimate: {decision['estimated_gpu_hours']}")
    print(f"")
    print(f"RECOMMENDATION:")
    print(f"  {decision['recommendation']}")
    print(f"")
    print(f"NEXT COMMAND:")
    print(f"  {decision['next_command']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
