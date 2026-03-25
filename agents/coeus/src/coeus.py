#!/usr/bin/env python3
"""
Coeus — Causal Intelligence Layer.

Titan of rational inquiry. Sits between Nous (theory) and Hephaestus (forge),
using causal discovery to learn which concepts drive forge success, then
enriches each triplet with actionable context.

Usage:
    python coeus.py                     # full rebuild: graph + enrichments
    python coeus.py --graph-only        # rebuild causal graph only
    python coeus.py --enrich-only       # regenerate enrichments from existing graph
    python coeus.py --summary           # print concept rankings and graph stats
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "hephaestus" / "src"))

from hephaestus import (
    combo_key, load_ledger,
    HEPHAESTUS_ROOT, FORGE_DIR,
)
from causal_graph import build_causal_graph, CausalGraph
from enrichment import generate_all_enrichments

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [COEUS] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("coeus")

COEUS_ROOT = Path(__file__).resolve().parent.parent
NOUS_ROOT = COEUS_ROOT.parent / "nous"
NEMESIS_ROOT = COEUS_ROOT.parent / "nemesis"
GRAPHS_DIR = COEUS_ROOT / "graphs"
ENRICHMENTS_DIR = COEUS_ROOT / "enrichments"


def load_all_nous(deduplicate: bool = True) -> list[dict]:
    """Load all Nous results, optionally deduplicating by combo key (keep best score)."""
    runs_dir = NOUS_ROOT / "runs"
    if not runs_dir.exists():
        return []

    if not deduplicate:
        results = []
        for run_dir in sorted(runs_dir.iterdir()):
            jsonl = run_dir / "responses.jsonl"
            if not jsonl.exists():
                continue
            with open(jsonl, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        results.append(json.loads(line))
        return results

    best = {}
    for run_dir in sorted(runs_dir.iterdir()):
        jsonl = run_dir / "responses.jsonl"
        if not jsonl.exists():
            continue
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                key = combo_key(entry)
                existing = best.get(key)
                if existing is None:
                    best[key] = entry
                else:
                    new_score = entry.get("score", {}).get("composite_score") or 0.0
                    old_score = existing.get("score", {}).get("composite_score") or 0.0
                    if new_score > old_score:
                        best[key] = entry
    return list(best.values())


def load_forge_entries() -> list[dict]:
    """Load metadata for all successfully forged tools."""
    entries = []
    if not FORGE_DIR.exists():
        return entries
    for json_path in FORGE_DIR.glob("*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            entries.append(data)
        except Exception:
            continue
    return entries


def load_adversarial_results() -> list[dict]:
    """Load Nemesis adversarial results for dual causal graph analysis."""
    adv_path = NEMESIS_ROOT / "adversarial" / "adversarial_results.jsonl"
    if not adv_path.exists():
        return []
    results = []
    with open(adv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                # Enforce provenance check
                if entry.get("provenance") != "adversarial":
                    continue
                results.append(entry)
    return results


def compute_adversarial_survival(adversarial_results: list[dict]) -> dict:
    """Compute per-concept adversarial survival rates from Nemesis data.

    Returns dict: concept_name -> {survival_rate, n_tasks, n_survived}
    """
    from collections import defaultdict
    concept_tasks = defaultdict(lambda: {"total": 0, "survived": 0})

    for task in adversarial_results:
        tool_results = task.get("tool_results", {})
        if not tool_results:
            continue
        # For each tool, check if it survived this adversarial task
        for tool_name, result in tool_results.items():
            # Extract concept names from tool name (underscore_x_separated)
            parts = tool_name.split("_x_")
            concepts = [p.replace("_", " ").title() for p in parts]
            for concept in concepts:
                concept_tasks[concept]["total"] += 1
                if result.get("correct", False):
                    concept_tasks[concept]["survived"] += 1

    survival = {}
    for concept, stats in concept_tasks.items():
        if stats["total"] > 0:
            survival[concept] = {
                "survival_rate": round(stats["survived"] / stats["total"], 4),
                "n_tasks": stats["total"],
                "n_survived": stats["survived"],
            }
    return survival


def print_summary(graph: CausalGraph):
    """Print a human-readable summary of the causal graph."""
    print(f"\n{'='*70}")
    print("COEUS — CAUSAL GRAPH SUMMARY")
    print(f"{'='*70}")
    print(f"  Method:        {graph.method}")
    print(f"  Observations:  {graph.n_observations}")
    print(f"  Forged:        {graph.n_forged}")

    # Top concepts by forge effect
    forge_ranked = sorted(
        [(c, v.get("forge_effect", 0)) for c, v in graph.concept_influence.items()],
        key=lambda x: -x[1],
    )
    positive = [(c, e) for c, e in forge_ranked if e > 0.01]
    negative = [(c, e) for c, e in forge_ranked if e < -0.01]

    if positive:
        print(f"\n  Top forge drivers (positive causal effect):")
        for concept, effect in positive[:15]:
            rate = graph.forge_rate_by_concept.get(concept, 0)
            print(f"    {concept:40s} effect={effect:+.3f}  rate={rate:.0%}")

    if negative:
        print(f"\n  Forge inhibitors (negative causal effect):")
        for concept, effect in negative[:10]:
            rate = graph.forge_rate_by_concept.get(concept, 0)
            print(f"    {concept:40s} effect={effect:+.3f}  rate={rate:.0%}")

    # Pair synergies
    if graph.pair_synergy:
        synergies = sorted(graph.pair_synergy.items(), key=lambda x: -abs(x[1]))
        print(f"\n  Top pair synergies:")
        for pair, syn in synergies[:10]:
            label = "synergy" if syn > 0 else "conflict"
            print(f"    {pair:50s} {label}={syn:+.3f}")

    # Field effects
    if graph.field_effects:
        print(f"\n  Field effects on forge success:")
        for field, effect in sorted(graph.field_effects.items(), key=lambda x: -x[1]):
            direction = "+" if effect > 0 else ""
            print(f"    {field:30s} {direction}{effect:.3f}")

    # Score DAG
    if graph.score_dag:
        print(f"\n  Score dimension effects on forge success:")
        if isinstance(graph.score_dag, dict):
            for dim, weight in sorted(graph.score_dag.items(),
                                      key=lambda x: -abs(x[1]) if isinstance(x[1], (int, float)) else 0):
                if isinstance(weight, (int, float)):
                    print(f"    {dim:35s} weight={weight:+.3f}")

    print(f"\n{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Coeus — Causal Intelligence Layer")
    parser.add_argument("--graph-only", action="store_true",
                        help="Only rebuild causal graph, skip enrichments")
    parser.add_argument("--enrich-only", action="store_true",
                        help="Only regenerate enrichments from existing graph")
    parser.add_argument("--summary", action="store_true",
                        help="Print causal graph summary and exit")
    args = parser.parse_args()

    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    ENRICHMENTS_DIR.mkdir(parents=True, exist_ok=True)

    graph_path = GRAPHS_DIR / "causal_graph.json"

    # --- Summary mode ---
    if args.summary:
        if not graph_path.exists():
            print("No causal graph found. Run `python coeus.py` first.")
            sys.exit(1)
        graph = CausalGraph.load(graph_path)
        print_summary(graph)
        return

    # --- Enrich-only mode ---
    if args.enrich_only:
        if not graph_path.exists():
            print("No causal graph found. Run `python coeus.py` or `--graph-only` first.")
            sys.exit(1)
        graph = CausalGraph.load(graph_path)
        nous_entries = load_all_nous()
        forge_entries = load_forge_entries()
        log.info("Generating enrichments for %d entries...", len(nous_entries))
        count = generate_all_enrichments(nous_entries, graph, forge_entries,
                                         combo_key, ENRICHMENTS_DIR)
        log.info("Generated %d enrichment files in %s", count, ENRICHMENTS_DIR)
        return

    # --- Full rebuild ---
    print("=" * 70)
    print("COEUS — CAUSAL INTELLIGENCE LAYER")
    print("Building causal graph from Nous + Hephaestus data")
    print("=" * 70)

    # Load data
    nous_entries = load_all_nous()
    log.info("Loaded %d unique Nous entries", len(nous_entries))

    ledger = load_ledger()
    log.info("Loaded %d ledger entries", len(ledger))

    forge_entries = load_forge_entries()
    log.info("Loaded %d forge entries", len(forge_entries))

    if len(nous_entries) == 0:
        log.error("No Nous data found. Run Nous first.")
        sys.exit(1)

    # Build causal graph
    graph = build_causal_graph(nous_entries, ledger, combo_key)

    # Save graph
    graph.save(graph_path)
    log.info("Causal graph saved: %s", graph_path)

    # Load adversarial data from Nemesis (if available)
    adversarial_results = load_adversarial_results()
    adversarial_survival = {}
    if adversarial_results:
        log.info("Loaded %d adversarial results from Nemesis", len(adversarial_results))
        adversarial_survival = compute_adversarial_survival(adversarial_results)
        log.info("Computed adversarial survival for %d concepts", len(adversarial_survival))

        # Save adversarial graph alongside forge graph
        adv_graph_path = GRAPHS_DIR / "adversarial_graph.json"
        adv_graph_path.write_text(json.dumps({
            "adversarial_survival": adversarial_survival,
            "n_adversarial_tasks": len(adversarial_results),
            "updated_at": datetime.now().isoformat(),
        }, indent=2, default=str), encoding="utf-8")
        log.info("Adversarial graph saved: %s", adv_graph_path)

        # Compute Goodhart divergence: concepts that predict forge success
        # but NOT adversarial robustness
        goodhart_indicators = {}
        for concept, influence in graph.concept_influence.items():
            forge_eff = influence.get("forge_effect", 0)
            adv_data = adversarial_survival.get(concept, {})
            adv_rate = adv_data.get("survival_rate", 0.5)

            # High forge effect + low adversarial survival = Goodhart indicator
            if forge_eff > 0.1 and adv_rate < 0.4:
                goodhart_indicators[concept] = {
                    "forge_effect": forge_eff,
                    "adversarial_survival": adv_rate,
                    "divergence": round(forge_eff - adv_rate, 4),
                    "warning": "High forge success but low adversarial robustness — may be Goodharting",
                }
            # Low forge effect + high adversarial survival = genuine robustness
            elif forge_eff < 0.1 and adv_rate > 0.6:
                goodhart_indicators[concept] = {
                    "forge_effect": forge_eff,
                    "adversarial_survival": adv_rate,
                    "divergence": round(adv_rate - forge_eff, 4),
                    "note": "Low forge priority but high adversarial robustness — undervalued",
                }

        if goodhart_indicators:
            log.info("Goodhart indicators: %d concepts with forge/adversarial divergence",
                     len(goodhart_indicators))
    else:
        log.info("No Nemesis adversarial data found (run Nemesis to enable dual graph)")

    # Save concept scores for easy lookup
    scores_path = GRAPHS_DIR / "concept_scores.json"
    scores_data = {
        "concept_influence": graph.concept_influence,
        "forge_rate_by_concept": graph.forge_rate_by_concept,
        "pair_synergy": graph.pair_synergy,
        "field_effects": graph.field_effects,
        "updated_at": datetime.now().isoformat(),
    }
    if adversarial_survival:
        scores_data["adversarial_survival"] = adversarial_survival
    if goodhart_indicators:
        scores_data["goodhart_indicators"] = goodhart_indicators
    scores_path.write_text(json.dumps(scores_data, indent=2, default=str),
                           encoding="utf-8")

    # Print summary
    print_summary(graph)

    # Print adversarial summary if available
    if adversarial_survival:
        print("\n  Adversarial Survival (from Nemesis):")
        ranked = sorted(adversarial_survival.items(),
                        key=lambda x: -x[1]["survival_rate"])
        for concept, data in ranked[:10]:
            print(f"    {concept:40s} survival={data['survival_rate']:.0%} "
                  f"({data['n_survived']}/{data['n_tasks']})")
    if goodhart_indicators:
        warnings = {k: v for k, v in goodhart_indicators.items() if "warning" in v}
        undervalued = {k: v for k, v in goodhart_indicators.items() if "note" in v}
        if warnings:
            print("\n  GOODHART WARNINGS (high forge, low adversarial):")
            for concept, data in warnings.items():
                print(f"    {concept:40s} forge={data['forge_effect']:+.3f} "
                      f"adversarial={data['adversarial_survival']:.0%}")
        if undervalued:
            print("\n  UNDERVALUED (low forge priority, high adversarial robustness):")
            for concept, data in undervalued.items():
                print(f"    {concept:40s} forge={data['forge_effect']:+.3f} "
                      f"adversarial={data['adversarial_survival']:.0%}")

    # Generate enrichments
    if not args.graph_only:
        log.info("Generating enrichments for %d entries...", len(nous_entries))
        count = generate_all_enrichments(nous_entries, graph, forge_entries,
                                         combo_key, ENRICHMENTS_DIR)
        log.info("Generated %d enrichment files in %s", count, ENRICHMENTS_DIR)

    print(f"\n  Graph:       {graph_path}")
    print(f"  Scores:      {scores_path}")
    if not args.graph_only:
        print(f"  Enrichments: {ENRICHMENTS_DIR}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
