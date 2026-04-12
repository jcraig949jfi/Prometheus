#!/usr/bin/env python3
"""Novelty and complexity scoring for forged reasoning tools.

Computes two additional metrics for each tool in forge/:

1. Behavioral Novelty — NCD between this tool's score vector (outputs on
   the 15 traps) and every other tool's score vector. Tools that produce
   different answer patterns from the rest of the library are genuinely
   novel, not just accurate.

2. Trace Complexity — how many distinct reasoning steps contributed to the
   final score. A tool where 4 genes fire and modify ctx is structurally
   more interesting than one where NCD fallback does everything.

Usage:
    python novelty_scorer.py                  # Score all tools, save results
    python novelty_scorer.py --top 20         # Show top 20 by novelty
    python novelty_scorer.py --update-ledger  # Backfill novelty/complexity into ledger.jsonl
"""

import argparse
import json
import logging
import sys
import zlib
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HEPH_ROOT = Path(__file__).resolve().parent.parent
FORGE_DIR = HEPH_ROOT / "forge"
LEDGER_PATH = HEPH_ROOT / "ledger.jsonl"
SCORES_PATH = HEPH_ROOT / "novelty_scores.json"

sys.path.insert(0, str(HEPH_ROOT / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NOVELTY] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("novelty_scorer")

# ---------------------------------------------------------------------------
# Trap battery (same 15 used everywhere)
# ---------------------------------------------------------------------------

from test_harness import TRAPS, load_tool_from_file


# ---------------------------------------------------------------------------
# Score vector computation
# ---------------------------------------------------------------------------

def compute_score_vector(tool, traps: list[dict]) -> np.ndarray:
    """Run tool on all traps, return vector of top-candidate scores.

    Each element is the score assigned to the top-ranked candidate.
    This captures the tool's BEHAVIOR — two tools with similar score
    vectors behave similarly regardless of their internal structure.
    """
    scores = []
    for trap in traps:
        try:
            ranked = tool.evaluate(trap["prompt"], trap["candidates"])
            if ranked:
                scores.append(float(ranked[0].get("score", 0.0)))
            else:
                scores.append(0.0)
        except Exception:
            scores.append(0.0)
    return np.array(scores, dtype=np.float64)


def compute_answer_vector(tool, traps: list[dict]) -> list[str]:
    """Run tool on all traps, return which candidate it picks for each.

    Two tools with different answer vectors are behaviorally distinct
    even if their score magnitudes differ.
    """
    answers = []
    for trap in traps:
        try:
            ranked = tool.evaluate(trap["prompt"], trap["candidates"])
            if ranked:
                answers.append(ranked[0].get("candidate", ""))
            else:
                answers.append("")
        except Exception:
            answers.append("")
    return answers


# ---------------------------------------------------------------------------
# Trace complexity
# ---------------------------------------------------------------------------

def compute_trace_complexity(tool, traps: list[dict]) -> dict:
    """Measure how many distinct steps contribute to scoring.

    Returns:
        gene_count: average number of genes that fire per candidate
        key_writes: average number of distinct ctx keys written
        score_changes: average number of times ctx['score'] changes value
        uses_fallback_only: True if the tool never writes ctx['score']
            from a non-fallback gene
    """
    gene_counts = []
    key_write_counts = []
    score_change_counts = []
    fallback_only_flags = []

    for trap in traps[:5]:  # Use 5 traps for speed
        for cand in trap["candidates"][:2]:  # 2 candidates per trap
            try:
                # Build context manually to capture trace
                ctx = {
                    "prompt": trap["prompt"],
                    "candidate": cand,
                    "raw_text": trap["prompt"] + " " + cand,
                    "parsed": None,
                    "score": 0.0,
                    "fallback_score": 0.0,
                    "_gene_trace": [],
                }

                # Try calling _run_pipeline if it exists (compiled organisms)
                if hasattr(tool, "_run_pipeline"):
                    try:
                        tool._run_pipeline(ctx)
                        trace = ctx.get("_gene_trace", [])
                        gene_counts.append(len(trace))

                        keys_written = set()
                        score_values = [0.0]
                        has_non_fallback_scorer = False

                        for entry in trace:
                            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                                gene_id = str(entry[0])
                                key = str(entry[1])
                                keys_written.add(key)
                                if key == "score" and len(entry) >= 3:
                                    val = entry[2]
                                    if isinstance(val, (int, float)) and val != score_values[-1]:
                                        score_values.append(float(val))
                                if key == "score" and "fallback" not in gene_id.lower():
                                    has_non_fallback_scorer = True

                        key_write_counts.append(len(keys_written))
                        score_change_counts.append(len(score_values) - 1)
                        fallback_only_flags.append(not has_non_fallback_scorer)
                        continue
                    except Exception:
                        pass

                # Fallback: just measure whether evaluate produces varied scores
                ranked = tool.evaluate(trap["prompt"], trap["candidates"])
                if ranked and len(ranked) >= 2:
                    scores = [r.get("score", 0) for r in ranked]
                    reasoning = ranked[0].get("reasoning", "")

                    # Count unique non-zero scores as proxy for complexity
                    unique_scores = len(set(round(s, 6) for s in scores))
                    gene_counts.append(1)  # Can't tell, assume 1
                    key_write_counts.append(unique_scores)

                    # Check if reasoning mentions fallback/ncd
                    is_fallback = "fallback" in reasoning.lower() or "ncd" in reasoning.lower()
                    fallback_only_flags.append(is_fallback)
                    score_change_counts.append(0 if unique_scores <= 1 else 1)
                else:
                    gene_counts.append(0)
                    key_write_counts.append(0)
                    score_change_counts.append(0)
                    fallback_only_flags.append(True)

            except Exception:
                gene_counts.append(0)
                key_write_counts.append(0)
                score_change_counts.append(0)
                fallback_only_flags.append(True)

    return {
        "avg_gene_count": round(float(np.mean(gene_counts)) if gene_counts else 0, 2),
        "avg_key_writes": round(float(np.mean(key_write_counts)) if key_write_counts else 0, 2),
        "avg_score_changes": round(float(np.mean(score_change_counts)) if score_change_counts else 0, 2),
        "fallback_only_ratio": round(
            sum(fallback_only_flags) / len(fallback_only_flags) if fallback_only_flags else 1.0, 2
        ),
        "complexity_score": 0.0,  # Computed below
    }


# ---------------------------------------------------------------------------
# Behavioral novelty (NCD between score vectors)
# ---------------------------------------------------------------------------

def ncd(x: np.ndarray, y: np.ndarray) -> float:
    """Normalized Compression Distance between two score vectors."""
    sx = ",".join(f"{v:.6f}" for v in x).encode("utf-8")
    sy = ",".join(f"{v:.6f}" for v in y).encode("utf-8")
    cx = len(zlib.compress(sx))
    cy = len(zlib.compress(sy))
    cxy = len(zlib.compress(sx + b"|" + sy))
    denom = max(cx, cy)
    if denom == 0:
        return 1.0
    return (cxy - min(cx, cy)) / denom


def compute_novelty_scores(score_vectors: dict[str, np.ndarray],
                           k_nearest: int = 10) -> dict[str, float]:
    """Compute behavioral novelty for each tool.

    Novelty = mean NCD distance to k nearest neighbors in the library.
    Higher = more behaviorally distinct from the rest.
    """
    names = list(score_vectors.keys())
    n = len(names)
    novelty = {}

    if n < 2:
        return {name: 1.0 for name in names}

    # Compute pairwise NCD matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = ncd(score_vectors[names[i]], score_vectors[names[j]])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    k = min(k_nearest, n - 1)
    for i, name in enumerate(names):
        distances = sorted(dist_matrix[i])
        # Skip self (distance 0)
        nearest = distances[1:k + 1]
        novelty[name] = round(float(np.mean(nearest)), 4) if nearest else 0.0

    return novelty


def compute_answer_diversity(answer_vectors: dict[str, list[str]]) -> dict[str, float]:
    """How different is this tool's answer pattern from the majority?

    For each trap, compute the majority answer. A tool's diversity score
    is the fraction of traps where it disagrees with the majority.
    """
    names = list(answer_vectors.keys())
    if not names:
        return {}

    n_traps = len(next(iter(answer_vectors.values())))
    majority_answers = []
    for t in range(n_traps):
        from collections import Counter
        votes = Counter(answer_vectors[name][t] for name in names if t < len(answer_vectors[name]))
        majority = votes.most_common(1)[0][0] if votes else ""
        majority_answers.append(majority)

    diversity = {}
    for name in names:
        disagreements = sum(
            1 for t in range(n_traps)
            if t < len(answer_vectors[name]) and answer_vectors[name][t] != majority_answers[t]
        )
        diversity[name] = round(disagreements / n_traps, 4) if n_traps > 0 else 0.0

    return diversity


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def score_all_tools() -> dict:
    """Score all tools in forge/ for novelty and complexity.

    Returns dict: tool_name -> {novelty, answer_diversity, complexity, ...}
    """
    tools_dir = FORGE_DIR
    py_files = sorted(tools_dir.glob("*.py"))

    if not py_files:
        log.warning("No tools found in %s", tools_dir)
        return {}

    log.info("Scoring %d tools for novelty and complexity...", len(py_files))

    # Phase 1: Load all tools and compute score vectors
    score_vectors = {}
    answer_vectors = {}
    loaded_tools = {}

    for py in py_files:
        try:
            tool = load_tool_from_file(py)
            sv = compute_score_vector(tool, TRAPS)
            av = compute_answer_vector(tool, TRAPS)
            score_vectors[py.stem] = sv
            answer_vectors[py.stem] = av
            loaded_tools[py.stem] = tool
        except Exception as e:
            log.warning("  Skipping %s: %s", py.stem, e)

    log.info("Loaded %d tools, computing novelty...", len(score_vectors))

    # Phase 2: Compute novelty scores
    novelty_scores = compute_novelty_scores(score_vectors)
    diversity_scores = compute_answer_diversity(answer_vectors)

    # Phase 3: Compute trace complexity
    log.info("Computing trace complexity...")
    results = {}
    for name, tool in loaded_tools.items():
        complexity = compute_trace_complexity(tool, TRAPS)

        # Composite complexity score: weighted combination
        complexity["complexity_score"] = round(
            0.3 * min(complexity["avg_gene_count"] / 5.0, 1.0) +
            0.3 * min(complexity["avg_key_writes"] / 4.0, 1.0) +
            0.2 * min(complexity["avg_score_changes"] / 3.0, 1.0) +
            0.2 * (1.0 - complexity["fallback_only_ratio"]),
            4
        )

        results[name] = {
            "novelty": novelty_scores.get(name, 0.0),
            "answer_diversity": diversity_scores.get(name, 0.0),
            **complexity,
        }

    log.info("Scored %d tools", len(results))
    return results


def save_scores(results: dict):
    """Save novelty/complexity scores to JSON."""
    SCORES_PATH.write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8"
    )
    log.info("Saved scores to %s", SCORES_PATH)


def update_ledger(results: dict):
    """Backfill novelty and complexity scores into ledger.jsonl."""
    if not LEDGER_PATH.exists():
        log.warning("Ledger not found at %s", LEDGER_PATH)
        return

    backup = Path(str(LEDGER_PATH) + ".bak")
    lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    backup.write_text("\n".join(lines), encoding="utf-8")

    updated = 0
    new_lines = []
    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            key = entry.get("key", "")
            # Convert combo key to filename format for lookup
            name = "_x_".join(
                c.replace(" ", "_") for c in sorted(key.split(" + "))
            ).lower()

            if name in results:
                entry["novelty"] = results[name]["novelty"]
                entry["answer_diversity"] = results[name]["answer_diversity"]
                entry["complexity_score"] = results[name]["complexity_score"]
                entry["fallback_only_ratio"] = results[name]["fallback_only_ratio"]
                updated += 1

            new_lines.append(json.dumps(entry, ensure_ascii=False))
        except (json.JSONDecodeError, KeyError):
            new_lines.append(line)

    LEDGER_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    log.info("Updated %d ledger entries (backup: %s)", updated, backup)


def print_rankings(results: dict, top_n: int = 20):
    """Print top tools by novelty, diversity, and complexity."""
    if not results:
        return

    # Load ledger for accuracy data
    acc_map = {}
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("status") == "forged":
                        key = e.get("key", "")
                        name = "_x_".join(
                            c.replace(" ", "_") for c in sorted(key.split(" + "))
                        ).lower()
                        acc_map[name] = (e.get("accuracy", 0), e.get("calibration", 0))
                except (json.JSONDecodeError, KeyError):
                    pass

    print()
    print("=" * 100)
    print("  TOP TOOLS BY NOVELTY (behavioral distinctness from library)")
    print("=" * 100)
    by_novelty = sorted(results.items(), key=lambda x: x[1]["novelty"], reverse=True)
    print(f"  {'Tool':55s} {'Nov':>5s} {'Div':>5s} {'Cplx':>5s} {'Acc':>5s} {'Cal':>5s}")
    print(f"  {'-'*55} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for name, scores in by_novelty[:top_n]:
        acc, cal = acc_map.get(name, (0, 0))
        print(f"  {name:55s} {scores['novelty']:5.3f} {scores['answer_diversity']:5.3f} "
              f"{scores['complexity_score']:5.3f} {acc*100:4.0f}% {cal*100:4.0f}%")

    print()
    print("=" * 100)
    print("  TOP TOOLS BY ANSWER DIVERSITY (disagrees with majority most often)")
    print("=" * 100)
    by_diversity = sorted(results.items(), key=lambda x: x[1]["answer_diversity"], reverse=True)
    print(f"  {'Tool':55s} {'Div':>5s} {'Nov':>5s} {'Cplx':>5s} {'Acc':>5s} {'Cal':>5s}")
    print(f"  {'-'*55} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for name, scores in by_diversity[:top_n]:
        acc, cal = acc_map.get(name, (0, 0))
        print(f"  {name:55s} {scores['answer_diversity']:5.3f} {scores['novelty']:5.3f} "
              f"{scores['complexity_score']:5.3f} {acc*100:4.0f}% {cal*100:4.0f}%")

    print()
    print("=" * 100)
    print("  TOP TOOLS BY COMPLEXITY (multi-step reasoning pipelines)")
    print("=" * 100)
    by_complexity = sorted(results.items(), key=lambda x: x[1]["complexity_score"], reverse=True)
    print(f"  {'Tool':55s} {'Cplx':>5s} {'Genes':>5s} {'Keys':>5s} {'FBOnly':>6s} {'Acc':>5s}")
    print(f"  {'-'*55} {'-'*5} {'-'*5} {'-'*5} {'-'*6} {'-'*5}")
    for name, scores in by_complexity[:top_n]:
        acc, _ = acc_map.get(name, (0, 0))
        print(f"  {name:55s} {scores['complexity_score']:5.3f} "
              f"{scores['avg_gene_count']:5.1f} {scores['avg_key_writes']:5.1f} "
              f"{scores['fallback_only_ratio']:5.0%} {acc*100:4.0f}%")

    # Summary stats
    all_novelty = [r["novelty"] for r in results.values()]
    all_diversity = [r["answer_diversity"] for r in results.values()]
    all_complexity = [r["complexity_score"] for r in results.values()]
    all_fallback = [r["fallback_only_ratio"] for r in results.values()]

    print()
    print("=" * 100)
    print("  LIBRARY SUMMARY")
    print("=" * 100)
    print(f"  Total tools:          {len(results)}")
    print(f"  Novelty:              median={np.median(all_novelty):.3f}  "
          f"min={min(all_novelty):.3f}  max={max(all_novelty):.3f}")
    print(f"  Answer diversity:     median={np.median(all_diversity):.3f}  "
          f"min={min(all_diversity):.3f}  max={max(all_diversity):.3f}")
    print(f"  Complexity:           median={np.median(all_complexity):.3f}  "
          f"min={min(all_complexity):.3f}  max={max(all_complexity):.3f}")
    print(f"  Fallback-only ratio:  median={np.median(all_fallback):.0%}  "
          f"({sum(1 for f in all_fallback if f >= 0.9)}/{len(all_fallback)} tools are NCD-dominated)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Novelty and complexity scoring for forge tools"
    )
    parser.add_argument("--top", type=int, default=20,
                        help="Show top N tools per category (default: 20)")
    parser.add_argument("--update-ledger", action="store_true",
                        help="Backfill novelty/complexity into ledger.jsonl")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress rankings output")
    args = parser.parse_args()

    results = score_all_tools()
    if not results:
        log.error("No tools scored")
        sys.exit(1)

    save_scores(results)

    if not args.quiet:
        print_rankings(results, top_n=args.top)

    if args.update_ledger:
        update_ledger(results)

    log.info("Done.")


if __name__ == "__main__":
    main()
