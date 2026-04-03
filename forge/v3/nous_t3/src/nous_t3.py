"""
Tier 3 Nous -- Tool Combination Miner

Generates hypotheses about how T1 and T2 forged tools can be combined
with computational science lenses to create stronger Tier 3 tools.

T3 triple: t1_or_t2_substrate + t1_or_t2_substrate + computational_science_lens
Cross-tier recombination (T1+T2 pair) is preferred and receives a bonus.
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
_HEPHAESTUS_T1 = _REPO / "agents" / "hephaestus"
_HEPHAESTUS_T2 = _REPO / "forge" / "v2" / "hephaestus_t2"

# T1 forge directories
_T1_FORGE_DIRS = [
    _HEPHAESTUS_T1 / "forge_v9",
    _HEPHAESTUS_T1 / "forge",
    _HEPHAESTUS_T1 / "forge_v7",
]

# T2 forge directory
_T2_FORGE_DIR = _HEPHAESTUS_T2 / "forge"

# All forge directories (T1 + T2)
_ALL_FORGE_DIRS = _T1_FORGE_DIRS + [_T2_FORGE_DIR]

# T1 ledger for forged tools and near-misses
_T1_LEDGER = _HEPHAESTUS_T1 / "ledger.jsonl"

_RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"

# ---------------------------------------------------------------------------
# Computational science lenses (same as T2)
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
# Hypothesis templates -- one per lens family for variety
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
        "structural invariants--categories where both tools agree despite "
        "different internal representations--which can anchor a shared "
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
        "their error patterns reveals correctable bit-flip categories--ones "
        "where a parity-check decoder can recover the correct label from the "
        "disagreement pattern."
    ),
    "Free Energy Principle": (
        "Model the combined system as minimising variational free energy: "
        "{t1} supplies a generative prior over category structure while {t2} "
        "provides the likelihood from reasoning traces. Categories where "
        "free energy is highest are the current frontier for Tier 3 gains."
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
        "targets for a combined Tier 3 tool."
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
        "complementary errors--prime candidates for a repair layer in the "
        "Tier 3 combination."
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
        "the combination is synergistic and Tier 3 gains are likely."
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
    "representations, yielding a Tier 3 tool with broader coverage than "
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


def _find_tool_path(concept_names: list[str],
                    forge_dirs: list[Path] | None = None) -> str | None:
    """Find the .py file for a tool across forge directories."""
    fname = _key_to_filename(concept_names)
    dirs = forge_dirs or _ALL_FORGE_DIRS
    for d in dirs:
        candidate = d / fname
        if candidate.exists():
            return str(candidate)
    return None


def _classify_tier(path: str | None) -> str:
    """Determine if a tool path belongs to T1 or T2."""
    if path is None:
        return "unknown"
    p = Path(path).resolve()
    for d in _T1_FORGE_DIRS:
        try:
            p.relative_to(d.resolve())
            return "t1"
        except ValueError:
            pass
    try:
        p.relative_to(_T2_FORGE_DIR.resolve())
        return "t2"
    except ValueError:
        return "unknown"


def scan_t1_substrate() -> list[dict[str, Any]]:
    """
    Read the T1 ledger and build the substrate pool of forged Tier 1 tools.
    Also includes near-misses (accuracy 20-41%).
    Returns list of dicts: {name, path, accuracy, calibration, concepts, status, tier}
    """
    if not _T1_LEDGER.exists():
        print(f"[WARN] T1 Ledger not found at {_T1_LEDGER}", file=sys.stderr)
        return []

    pool: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    with open(_T1_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            key = entry.get("key", "")

            # Keep latest entry per key (ledger is append-only)
            if key in seen_keys:
                pool = [p for p in pool if p["name"] != key]
            seen_keys.add(key)

            status = entry.get("status", "")
            accuracy = entry.get("accuracy", 0.0) or 0.0
            calibration = entry.get("calibration", 0.0) or 0.0
            concept_names = entry.get("concept_names", [])

            is_forged = status == "forged"
            is_near_miss = status == "scrap" and 0.20 <= accuracy <= 0.41

            if not (is_forged or is_near_miss):
                continue

            path = _find_tool_path(concept_names, _T1_FORGE_DIRS)

            pool.append({
                "name": key,
                "path": path,
                "accuracy": round(accuracy * 100, 1),
                "calibration": round(calibration * 100, 1),
                "concepts": concept_names,
                "status": "near_miss" if is_near_miss else "forged",
                "tier": "t1",
            })

    return pool


def scan_t2_substrate() -> list[dict[str, Any]]:
    """
    Scan the T2 forge directory for forged Tier 2 tools.
    Returns list of dicts: {name, path, accuracy, calibration, concepts, status, tier}
    """
    pool: list[dict[str, Any]] = []

    if not _T2_FORGE_DIR.exists():
        print(f"[WARN] T2 forge dir not found at {_T2_FORGE_DIR}", file=sys.stderr)
        return []

    for py_file in sorted(_T2_FORGE_DIR.glob("*.py")):
        name = py_file.stem
        pool.append({
            "name": name,
            "path": str(py_file),
            "accuracy": 0.0,   # T2 tools not yet benchmarked
            "calibration": 0.0,
            "concepts": name.replace("_x_", "|").split("|") if "_x_" in name
                        else [name],
            "status": "forged",
            "tier": "t2",
        })

    return pool


def scan_substrate() -> list[dict[str, Any]]:
    """
    Build the combined T1 + T2 substrate pool for Tier 3.
    """
    t1 = scan_t1_substrate()
    t2 = scan_t2_substrate()
    pool = t1 + t2
    return pool


def print_scan_report(pool: list[dict[str, Any]]) -> None:
    """Print summary statistics about the substrate pool."""
    t1_tools = [t for t in pool if t["tier"] == "t1"]
    t2_tools = [t for t in pool if t["tier"] == "t2"]
    forged = [t for t in pool if t["status"] == "forged"]
    near_miss = [t for t in pool if t["status"] == "near_miss"]

    print("=" * 60)
    print("  Tier 3 Nous -- Substrate Pool Scan")
    print("=" * 60)
    print(f"  T1 tools:        {len(t1_tools)}")
    print(f"  T2 tools:        {len(t2_tools)}")
    print(f"  Forged tools:    {len(forged)}")
    print(f"  Near-miss scraps:{len(near_miss)}")
    print(f"  Total substrate: {len(pool)}")
    print()

    if pool:
        accs = [t["accuracy"] for t in pool if t["accuracy"] > 0]
        if accs:
            print(f"  Accuracy range:  {min(accs):.1f}% -- {max(accs):.1f}%")
            print(f"  Median accuracy: {sorted(accs)[len(accs)//2]:.1f}%")
        else:
            print("  Accuracy range:  (no benchmarked tools)")
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
    for d in _T1_FORGE_DIRS:
        if d.exists():
            py_count = len(list(d.glob("*.py")))
            print(f"  {d.name}/: {py_count} .py files  (T1)")
    if _T2_FORGE_DIR.exists():
        py_count = len(list(_T2_FORGE_DIR.glob("*.py")))
        print(f"  {_T2_FORGE_DIR.name}/: {py_count} .py files  (T2)")

    print("=" * 60)


# ---------------------------------------------------------------------------
# Category analysis helpers
# ---------------------------------------------------------------------------

def _extract_categories(tool: dict[str, Any]) -> set[str]:
    """Approximate category coverage from concept names."""
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

    jaccard_complement = 1.0 - (overlap / union) if union else 0.0
    acc_diff = abs(t1["accuracy"] - t2["accuracy"]) / 100.0

    score = (jaccard_complement * 7.0) + (acc_diff * 3.0)
    return round(min(score, 10.0), 1)


def _novelty(t1: dict[str, Any], t2: dict[str, Any], lens: str,
             seen_triples: set[tuple[str, str, str]]) -> float:
    """Score 0-10: penalise already-generated triples."""
    triple = tuple(sorted([t1["name"], t2["name"]])) + (lens,)
    if triple in seen_triples:
        return 0.0
    return 7.0


def _near_miss_bonus(t1: dict[str, Any], t2: dict[str, Any]) -> float:
    """Bonus 0-3 if one or both tools are near-miss scraps."""
    bonus = 0.0
    if t1["status"] == "near_miss":
        bonus += 1.5
    if t2["status"] == "near_miss":
        bonus += 1.5
    return bonus


def _cross_tier_bonus(t1: dict[str, Any], t2: dict[str, Any]) -> float:
    """Bonus +1 if the pair is a cross-tier combination (T1+T2)."""
    tiers = {t1["tier"], t2["tier"]}
    if "t1" in tiers and "t2" in tiers:
        return 1.0
    return 0.0


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
    """Generate n T3 triples from the substrate pool.

    Prefers cross-tier (T1+T2) pairs. Scores by: cross-tier bonus,
    complementarity, and novelty.
    """
    if len(pool) < 2:
        print("[ERROR] Need at least 2 substrate tools to generate triples.",
              file=sys.stderr)
        return []

    # Partition by tier for cross-tier preference
    t1_pool = [t for t in pool if t["tier"] == "t1"]
    t2_pool = [t for t in pool if t["tier"] == "t2"]
    has_cross_tier = len(t1_pool) > 0 and len(t2_pool) > 0

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

    # Build per-tier weight lists
    t1_weights = [w for t, w in zip(pool, tool_weights) if t["tier"] == "t1"]
    t2_weights = [w for t, w in zip(pool, tool_weights) if t["tier"] == "t2"]

    attempts = 0
    max_attempts = n * 20

    while len(results) < n and attempts < max_attempts:
        attempts += 1

        # 70% chance of cross-tier pairing when both tiers available
        if has_cross_tier and rng.random() < 0.7:
            t1 = rng.choices(t1_pool, weights=t1_weights, k=1)[0]
            t2 = rng.choices(t2_pool, weights=t2_weights, k=1)[0]
        else:
            # Same-tier pairing (fallback)
            t1 = rng.choices(pool, weights=tool_weights, k=1)[0]
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

        # Score
        comp = _complementarity(t1, t2)
        nov = _novelty(t1, t2, lens, seen_triples)
        seen_triples.add(triple_key)
        nm_bonus = _near_miss_bonus(t1, t2)
        ct_bonus = _cross_tier_bonus(t1, t2)

        composite = round((comp + nov + nm_bonus + ct_bonus) / 2.0, 1)

        # Generate hypothesis
        hypothesis = _generate_hypothesis(t1, t2, lens)
        response_text = (
            f"Given {t1['name']} [T{1 if t1['tier']=='t1' else 2}] "
            f"(covers: {', '.join(t1['concepts'])}, "
            f"accuracy: {t1['accuracy']}%) and {t2['name']} "
            f"[T{1 if t2['tier']=='t1' else 2}] "
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
                    "cross_tier_bonus": ct_bonus,
                },
            },
            "substrate": {
                "tool_1": {
                    "name": t1["name"],
                    "accuracy": t1["accuracy"],
                    "calibration": t1["calibration"],
                    "concepts": t1["concepts"],
                    "status": t1["status"],
                    "tier": t1["tier"],
                    "path": t1["path"],
                },
                "tool_2": {
                    "name": t2["name"],
                    "accuracy": t2["accuracy"],
                    "calibration": t2["calibration"],
                    "concepts": t2["concepts"],
                    "status": t2["status"],
                    "tier": t2["tier"],
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
        description="Tier 3 Nous -- Tool Combination Miner"
    )
    parser.add_argument("--n", type=int, default=50,
                        help="Number of T3 triples to generate")
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
    print(f"Generating {args.n} T3 triples (seed={args.seed})...")

    results = generate_triples(pool, args.n, rng)

    if not results:
        print("[ERROR] No triples generated.", file=sys.stderr)
        sys.exit(1)

    out_path = save_results(results)
    print(f"Saved {len(results)} triples to {out_path}")
    print()

    # Summary
    scores = [r["score"]["composite_score"] for r in results]
    print(f"  Score range: {min(scores):.1f} -- {max(scores):.1f}")
    print(f"  Mean score:  {sum(scores)/len(scores):.1f}")
    print()

    # Cross-tier stats
    cross = sum(1 for r in results
                if r["substrate"]["tool_1"]["tier"] != r["substrate"]["tool_2"]["tier"])
    print(f"  Cross-tier pairs: {cross}/{len(results)}")
    print()

    # Print top 5
    for i, r in enumerate(results[:5], 1):
        t1_tier = r["substrate"]["tool_1"]["tier"].upper()
        t2_tier = r["substrate"]["tool_2"]["tier"].upper()
        print(f"  [{i}] score={r['score']['composite_score']:.1f}  "
              f"{r['concept_names'][0]} [{t1_tier}]  x  "
              f"{r['concept_names'][1]} [{t2_tier}]  "
              f"via {r['concept_names'][2]}")
        print(f"      comp={r['score']['ratings']['complementarity']:.1f}  "
              f"nov={r['score']['ratings']['novelty']:.1f}  "
              f"nm={r['score']['ratings']['near_miss_bonus']:.1f}  "
              f"ct={r['score']['ratings']['cross_tier_bonus']:.1f}")


if __name__ == "__main__":
    main()
