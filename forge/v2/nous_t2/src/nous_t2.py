"""
Tier 2 Nous — Tool Combination Miner

Generates hypotheses about how Tier 1 forged tools can be combined
with computational science lenses to create stronger Tier 2 tools.

T2 triple: substrate_1 + substrate_2 + computational_science_lens
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths (relative to repo root, resolved at runtime)
# ---------------------------------------------------------------------------

_REPO = Path(__file__).resolve().parents[4]  # F:\Prometheus
_HEPHAESTUS = _REPO / "agents" / "hephaestus"
_FORGE_DIRS = [
    _HEPHAESTUS / "forge_v9",
    _HEPHAESTUS / "forge",
    _HEPHAESTUS / "forge_v7",
]
_LEDGER = _HEPHAESTUS / "ledger.jsonl"
_RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"

# ---------------------------------------------------------------------------
# Computational science lenses (subset of 95 concepts suited for combination)
# ---------------------------------------------------------------------------

LENSES = [
    "Information Theory", "Ergodic Theory", "Category Theory",
    "Error Correcting Codes", "Kolmogorov Complexity", "Game Theory",
    "Optimal Control", "Bayesian Inference", "Causal Inference",
    "Free Energy Principle", "Chaos Theory", "Network Science",
    "Constraint Satisfaction", "Type Theory", "Model Checking",
    "Abstract Interpretation", "Sensitivity Analysis", "Metamorphic Testing",
    "Property-Based Testing", "Satisfiability", "Hoare Logic",
    "Program Synthesis", "Compositional Semantics", "Mechanism Design",
    "Multi-Armed Bandits", "Monte Carlo Tree Search", "Spectral Analysis",
    "Tensor Decomposition", "Topological Data Analysis", "Renormalization",
    "Maximum Entropy", "Sparse Coding",
]

# ---------------------------------------------------------------------------
# Hypothesis templates — one per lens family for variety
# ---------------------------------------------------------------------------

_HYPOTHESIS_TEMPLATES: dict[str, str] = {
    "Information Theory": (
        "Measure the mutual information between {t1}'s output distribution and "
        "{t2}'s output distribution across shared categories. Categories where "
        "MI is low indicate independent evidence streams that a merged tool can "
        "exploit via entropy-weighted voting, boosting coverage on the "
        "{gap_count} gap categories."
    ),
    "Category Theory": (
        "Construct a functor from {t1}'s category judgements into {t2}'s "
        "judgment space. Natural transformations between the two expose "
        "structural invariants—categories where both tools agree despite "
        "different internal representations—which can anchor a shared "
        "confidence calibration layer."
    ),
    "Causal Inference": (
        "Treat {t1} and {t2} as parallel interventions on the same input. "
        "Use do-calculus to identify categories where one tool's accuracy "
        "causally mediates the other's errors, enabling a selective routing "
        "policy that sends hard instances to the stronger tool per-category."
    ),
    "Error Correcting Codes": (
        "Encode {t1} and {t2} outputs as codewords in a binary block code "
        "where each bit is a category verdict. The Hamming distance between "
        "their error patterns reveals correctable bit-flip categories—ones "
        "where a parity-check decoder can recover the correct label from the "
        "disagreement pattern."
    ),
    "Free Energy Principle": (
        "Model the combined system as minimising variational free energy: "
        "{t1} supplies a generative prior over category structure while {t2} "
        "provides the likelihood from reasoning traces. Categories where "
        "free energy is highest are the current frontier for Tier 2 gains."
    ),
    "Game Theory": (
        "Frame {t1} and {t2} as strategic agents in a cooperative game over "
        "the 105-category space. Nash equilibria of the joint strategy reveal "
        "stable category assignments, while mixed strategies over the "
        "{gap_count} contested categories indicate where randomised "
        "ensembling outperforms fixed routing."
    ),
    "Network Science": (
        "Build a bipartite graph: {t1} and {t2} nodes connect to category "
        "nodes weighted by per-category accuracy. Community detection on "
        "this graph partitions categories into clusters best served by each "
        "tool, and bridge categories between clusters are the highest-value "
        "targets for a combined Tier 2 tool."
    ),
    "Bayesian Inference": (
        "Use {t1}'s category-level accuracy as a prior and update with "
        "{t2}'s independent evidence via Bayes' rule. The posterior "
        "probability per category yields a principled confidence score that "
        "calibrates better than either tool alone, especially on the "
        "{gap_count} categories where priors are weakest."
    ),
    "Maximum Entropy": (
        "Among all distributions over categories consistent with {t1} and "
        "{t2}'s accuracy constraints, select the maximum-entropy one. This "
        "avoids over-fitting to either tool's biases and produces the "
        "least-committed routing table, maximising expected information gain "
        "on unseen instances."
    ),
    "Metamorphic Testing": (
        "Define metamorphic relations between {t1} and {t2}: if {t1} judges "
        "category C correctly, then {t2}'s confidence on C should satisfy a "
        "monotonicity relation. Violations flag categories with systematic "
        "complementary errors—prime candidates for a repair layer in the "
        "Tier 2 combination."
    ),
    "Constraint Satisfaction": (
        "Express {t1}'s and {t2}'s per-category verdicts as Boolean "
        "constraints. A SAT solver over the joint constraint set identifies "
        "the maximal consistent subset of category assignments, resolving "
        "conflicts between tools with minimum information loss."
    ),
    "Optimal Control": (
        "Model the inference pipeline as a control system where {t1} and "
        "{t2} are actuators and category accuracy is the state variable. "
        "An LQR controller allocates reasoning depth between tools per "
        "category to minimise total error with bounded compute budget."
    ),
    "Sensitivity Analysis": (
        "Perturb {t1}'s and {t2}'s input prompts and measure Sobol indices "
        "per category. High first-order indices reveal categories dominated "
        "by a single tool; high interaction indices reveal categories where "
        "the combination is synergistic and Tier 2 gains are likely."
    ),
    "Type Theory": (
        "Assign dependent types to {t1}'s and {t2}'s reasoning traces. "
        "Type-checking the composition reveals categories where the proof "
        "terms are compatible (safe to merge) versus where type mismatches "
        "signal fundamentally different reasoning strategies that need "
        "explicit mediation."
    ),
}

_DEFAULT_TEMPLATE = (
    "Apply {lens} to the combination: use {t1}'s strength on "
    "{cats_1_short} and {t2}'s strength on {cats_2_short} as complementary "
    "evidence streams. The {lens} framework suggests that the "
    "{gap_count} non-overlapping categories can be recovered by "
    "exploiting the structural contrast between the two tools' internal "
    "representations, yielding a Tier 2 tool with broader coverage than "
    "either substrate alone."
)


# ---------------------------------------------------------------------------
# Substrate scanning
# ---------------------------------------------------------------------------

def _key_to_filename(concept_names: list[str]) -> str:
    """Derive the expected .py filename from sorted concept names."""
    return "_x_".join(
        c.lower().replace(" ", "_").replace("-", "_")
        for c in sorted(concept_names)
    ) + ".py"


def _find_tool_path(concept_names: list[str]) -> str | None:
    """Find the .py file for a tool across forge directories."""
    fname = _key_to_filename(concept_names)
    for d in _FORGE_DIRS:
        candidate = d / fname
        if candidate.exists():
            return str(candidate)
    return None


def scan_substrate() -> list[dict[str, Any]]:
    """
    Read the ledger and build the substrate pool of forged Tier 1 tools.
    Returns list of dicts: {name, path, accuracy, calibration, concepts, status}
    """
    if not _LEDGER.exists():
        print(f"[WARN] Ledger not found at {_LEDGER}", file=sys.stderr)
        return []

    pool: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    with open(_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            key = entry.get("key", "")

            # Keep latest entry per key (ledger is append-only)
            if key in seen_keys:
                # Replace existing
                pool = [p for p in pool if p["name"] != key]
            seen_keys.add(key)

            status = entry.get("status", "")
            accuracy = entry.get("accuracy", 0.0) or 0.0
            calibration = entry.get("calibration", 0.0) or 0.0
            concept_names = entry.get("concept_names", [])

            # Include forged tools and near-miss scraps (accuracy 20-41%)
            is_forged = status == "forged"
            is_near_miss = status == "scrap" and 0.20 <= accuracy <= 0.41

            if not (is_forged or is_near_miss):
                continue

            path = _find_tool_path(concept_names)

            pool.append({
                "name": key,
                "path": path,
                "accuracy": round(accuracy * 100, 1),
                "calibration": round(calibration * 100, 1),
                "concepts": concept_names,
                "status": "near_miss" if is_near_miss else "forged",
            })

    return pool


def print_scan_report(pool: list[dict[str, Any]]) -> None:
    """Print summary statistics about the substrate pool."""
    forged = [t for t in pool if t["status"] == "forged"]
    near_miss = [t for t in pool if t["status"] == "near_miss"]

    print("=" * 60)
    print("  Tier 2 Nous — Substrate Pool Scan")
    print("=" * 60)
    print(f"  Forged tools:    {len(forged)}")
    print(f"  Near-miss scraps:{len(near_miss)}")
    print(f"  Total substrate: {len(pool)}")
    print()

    if pool:
        accs = [t["accuracy"] for t in pool]
        print(f"  Accuracy range:  {min(accs):.1f}% — {max(accs):.1f}%")
        print(f"  Median accuracy: {sorted(accs)[len(accs)//2]:.1f}%")
        print()

        with_path = sum(1 for t in pool if t["path"])
        print(f"  Tools with file: {with_path}/{len(pool)}")
        print()

        # Concept frequency
        concept_counts: Counter[str] = Counter()
        for t in pool:
            for c in t["concepts"]:
                concept_counts[c] += 1
        print(f"  Unique concepts: {len(concept_counts)}")
        print("  Top 10 concepts:")
        for concept, count in concept_counts.most_common(10):
            print(f"    {concept}: {count}")

    # Forge directory breakdown
    print()
    for d in _FORGE_DIRS:
        if d.exists():
            py_count = len(list(d.glob("*.py")))
            print(f"  {d.name}/: {py_count} .py files")

    print("=" * 60)


# ---------------------------------------------------------------------------
# Category analysis helpers
# ---------------------------------------------------------------------------

def _extract_categories(tool: dict[str, Any]) -> set[str]:
    """
    Approximate category coverage from concept names.
    In a full implementation this would read the tool's eval results.
    For now, use the concept triple as a proxy for coverage domain.
    """
    return set(tool["concepts"])


def _complementarity(t1: dict[str, Any], t2: dict[str, Any]) -> float:
    """
    Score 0-10: how complementary are two tools?
    Higher when concepts don't overlap and accuracy profiles differ.
    """
    c1 = set(t1["concepts"])
    c2 = set(t2["concepts"])
    overlap = len(c1 & c2)
    union = len(c1 | c2)

    # Concept diversity: fewer shared concepts = more complementary
    jaccard_complement = 1.0 - (overlap / union) if union else 0.0

    # Accuracy spread: tools at different accuracy levels cover different
    # difficulty strata
    acc_diff = abs(t1["accuracy"] - t2["accuracy"]) / 100.0

    score = (jaccard_complement * 7.0) + (acc_diff * 3.0)
    return round(min(score, 10.0), 1)


def _novelty(t1: dict[str, Any], t2: dict[str, Any], lens: str,
             seen_triples: set[tuple[str, str, str]]) -> float:
    """Score 0-10: penalise already-generated triples."""
    triple = tuple(sorted([t1["name"], t2["name"]])) + (lens,)
    if triple in seen_triples:
        return 0.0
    return 7.0  # Base novelty; could be refined with embedding distance


def _near_miss_bonus(t1: dict[str, Any], t2: dict[str, Any]) -> float:
    """Bonus 0-3 if one or both tools are near-miss scraps."""
    bonus = 0.0
    if t1["status"] == "near_miss":
        bonus += 1.5
    if t2["status"] == "near_miss":
        bonus += 1.5
    return bonus


# ---------------------------------------------------------------------------
# Hypothesis generation
# ---------------------------------------------------------------------------

def _generate_hypothesis(t1: dict[str, Any], t2: dict[str, Any],
                         lens: str) -> str:
    """Build a concrete hypothesis for the triple."""
    cats_1 = ", ".join(t1["concepts"][:2])
    cats_2 = ", ".join(t2["concepts"][:2])
    gap_count = len(set(t1["concepts"]) ^ set(t2["concepts"]))

    template = _HYPOTHESIS_TEMPLATES.get(lens, _DEFAULT_TEMPLATE)

    return template.format(
        t1=t1["name"],
        t2=t2["name"],
        lens=lens,
        cats_1_short=cats_1,
        cats_2_short=cats_2,
        gap_count=gap_count,
    )


def generate_triples(
    pool: list[dict[str, Any]],
    n: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    """Generate n T2 triples from the substrate pool."""
    if len(pool) < 2:
        print("[ERROR] Need at least 2 substrate tools to generate triples.",
              file=sys.stderr)
        return []

    results: list[dict[str, Any]] = []
    seen_triples: set[tuple[str, str, str]] = set()

    # Weight tools by inverse frequency of their concepts (prefer diverse picks)
    concept_freq: Counter[str] = Counter()
    for t in pool:
        for c in t["concepts"]:
            concept_freq[c] += 1
    max_freq = max(concept_freq.values()) if concept_freq else 1

    tool_weights = []
    for t in pool:
        avg_rarity = sum(
            (max_freq - concept_freq[c] + 1) for c in t["concepts"]
        ) / max(len(t["concepts"]), 1)
        tool_weights.append(avg_rarity)

    attempts = 0
    max_attempts = n * 20

    while len(results) < n and attempts < max_attempts:
        attempts += 1

        # Pick two distinct tools (weighted by diversity)
        t1 = rng.choices(pool, weights=tool_weights, k=1)[0]
        # Exclude t1 for second pick
        pool2 = [t for t in pool if t["name"] != t1["name"]]
        weights2 = [w for t, w in zip(pool, tool_weights)
                     if t["name"] != t1["name"]]
        if not pool2:
            continue
        t2 = rng.choices(pool2, weights=weights2, k=1)[0]

        # Pick a lens
        lens = rng.choice(LENSES)

        # Deduplicate
        triple_key = tuple(sorted([t1["name"], t2["name"]])) + (lens,)
        if triple_key in seen_triples:
            continue

        # Score (check novelty before adding to seen set)
        comp = _complementarity(t1, t2)
        nov = _novelty(t1, t2, lens, seen_triples)

        seen_triples.add(triple_key)
        nm_bonus = _near_miss_bonus(t1, t2)
        composite = round((comp + nov + nm_bonus) / 2.0, 1)

        # Generate hypothesis
        hypothesis = _generate_hypothesis(t1, t2, lens)
        response_text = (
            f"Given {t1['name']} (covers: {', '.join(t1['concepts'])}, "
            f"accuracy: {t1['accuracy']}%) and {t2['name']} "
            f"(covers: {', '.join(t2['concepts'])}, accuracy: {t2['accuracy']}%), "
            f"applying {lens} suggests: {hypothesis}"
        )

        results.append({
            "concept_names": [t1["name"], t2["name"], lens],
            "response_text": response_text,
            "score": {
                "composite_score": composite,
                "ratings": {
                    "complementarity": comp,
                    "novelty": nov,
                    "near_miss_bonus": nm_bonus,
                },
            },
            "substrate": {
                "tool_1": {
                    "name": t1["name"],
                    "accuracy": t1["accuracy"],
                    "calibration": t1["calibration"],
                    "concepts": t1["concepts"],
                    "status": t1["status"],
                    "path": t1["path"],
                },
                "tool_2": {
                    "name": t2["name"],
                    "accuracy": t2["accuracy"],
                    "calibration": t2["calibration"],
                    "concepts": t2["concepts"],
                    "status": t2["status"],
                    "path": t2["path"],
                },
            },
        })

    # Sort by composite score descending
    results.sort(key=lambda x: x["score"]["composite_score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_results(results: list[dict[str, Any]]) -> Path:
    """Save results to a timestamped run directory."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = _RUNS_DIR / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / "responses.jsonl"

    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tier 2 Nous — Tool Combination Miner"
    )
    parser.add_argument("--n", type=int, default=50,
                        help="Number of T2 triples to generate")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--scan", action="store_true",
                        help="Just scan and report substrate pool stats")
    args = parser.parse_args()

    pool = scan_substrate()

    if args.scan:
        print_scan_report(pool)
        return

    if not pool:
        print("[ERROR] No substrate tools found. Run --scan to debug.",
              file=sys.stderr)
        sys.exit(1)

    rng = random.Random(args.seed)
    print(f"Generating {args.n} T2 triples (seed={args.seed})...")

    results = generate_triples(pool, args.n, rng)

    if not results:
        print("[ERROR] No triples generated.", file=sys.stderr)
        sys.exit(1)

    out_path = save_results(results)
    print(f"Saved {len(results)} triples to {out_path}")
    print()

    # Summary
    scores = [r["score"]["composite_score"] for r in results]
    print(f"  Score range: {min(scores):.1f} — {max(scores):.1f}")
    print(f"  Mean score:  {sum(scores)/len(scores):.1f}")
    print()

    # Print top 5
    for i, r in enumerate(results[:5], 1):
        print(f"  [{i}] score={r['score']['composite_score']:.1f}  "
              f"{r['concept_names'][0]}  x  {r['concept_names'][1]}  "
              f"via {r['concept_names'][2]}")
        print(f"      comp={r['score']['ratings']['complementarity']:.1f}  "
              f"nov={r['score']['ratings']['novelty']:.1f}  "
              f"nm={r['score']['ratings']['near_miss_bonus']:.1f}")


if __name__ == "__main__":
    main()
