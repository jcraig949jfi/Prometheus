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

    # Save concept scores for easy lookup
    scores_path = GRAPHS_DIR / "concept_scores.json"
    scores_path.write_text(json.dumps({
        "concept_influence": graph.concept_influence,
        "forge_rate_by_concept": graph.forge_rate_by_concept,
        "pair_synergy": graph.pair_synergy,
        "field_effects": graph.field_effects,
        "updated_at": datetime.now().isoformat(),
    }, indent=2, default=str), encoding="utf-8")

    # Print summary
    print_summary(graph)

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
