"""ergon.learner.tools.stability_analysis — cross-seed stability analyzer.

Per ChatGPT frontier review (iter 36 / Task #99). Highest-priority question:
"Is Ergon discovering structure or sampling noise attractors?"

Three metrics to answer this from existing ledgers:

1. **Predicate recurrence across seeds**: for each unique content_hash, how
   many seeds independently produced it? High recurrence (most predicates
   found by 3/3 seeds) → discovering structure. Low recurrence (most
   predicates seed-specific) → noise attractors.

2. **Match-set overlap across seeds**: for each unique match-set on the
   corpus, how many seeds independently found at least one predicate
   matching that match-set? High overlap → cluster identity is robust.

3. **Description-length variance per cluster**: within a match-set-
   equivalent cluster, what's the distribution of conjunct counts? Low
   variance with a stable minimum → engine reliably identifies the
   parsimonious form. High variance → engine is exploring redundancy
   without converging.

Usage:
    python -m ergon.learner.tools.stability_analysis \
      <ledger.jsonl> [--corpus a149_real|obstruction_synthetic]
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


def _load_a149_real():
    from ergon.learner.trials._a149_real_corpus import load_a149_real_corpus
    return load_a149_real_corpus()


def _load_obstruction_synthetic():
    from prometheus_math._obstruction_corpus import OBSTRUCTION_CORPUS
    return OBSTRUCTION_CORPUS


CORPUS_LOADERS: Dict[str, Callable[[], Any]] = {
    "a149_real": _load_a149_real,
    "obstruction_synthetic": _load_obstruction_synthetic,
}


def _matches(features: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    return all(features.get(k) == v for k, v in pred.items())


def analyze_stability(
    records: List[Dict[str, Any]],
    corpus: List[Any],
    min_lift: float = 5.0,
) -> Dict[str, Any]:
    """Compute the three stability metrics from a ledger + corpus."""
    seeds = sorted(set(r["seed"] for r in records))

    # --- Metric 1: predicate recurrence by content_hash ---
    seeds_per_hash: Dict[str, Set[int]] = defaultdict(set)
    pred_by_hash: Dict[str, Dict[str, Any]] = {}
    for r in records:
        if r["lift"] < min_lift:
            continue
        ch = r["genome_content_hash"]
        seeds_per_hash[ch].add(r["seed"])
        if ch not in pred_by_hash:
            pred_by_hash[ch] = r["predicate"]

    recurrence_dist = Counter()
    for ch, sset in seeds_per_hash.items():
        recurrence_dist[len(sset)] += 1

    # --- Metric 2: match-set overlap across seeds ---
    # For each (seed, content_hash) pair, compute its match-set on corpus.
    # Then for each unique match-set, count seeds that produced any
    # predicate with that match-set.
    matchset_per_hash: Dict[str, frozenset] = {}
    for ch, pred in pred_by_hash.items():
        if not pred:
            continue
        match_ids = frozenset(
            id(e) for e in corpus if _matches(e.features(), pred)
        )
        matchset_per_hash[ch] = match_ids

    seeds_per_matchset: Dict[frozenset, Set[int]] = defaultdict(set)
    for ch, ms in matchset_per_hash.items():
        for seed in seeds_per_hash[ch]:
            seeds_per_matchset[ms].add(seed)

    matchset_recurrence_dist = Counter()
    high_quality_matchsets = []  # match=>=3 records, kr=1.0
    for ms, sset in seeds_per_matchset.items():
        matchset_recurrence_dist[len(sset)] += 1
        if len(ms) >= 3:
            # Check kill rate
            recs = [e for e in corpus if id(e) in ms]
            kr = sum(1 for e in recs if e.kill_verdict) / len(recs)
            if kr >= 0.999:
                high_quality_matchsets.append({
                    "match_size": len(ms),
                    "n_seeds": len(sset),
                    "n_predicate_variants": sum(
                        1 for h in matchset_per_hash if matchset_per_hash[h] == ms
                    ),
                })

    # --- Metric 3: description-length variance per cluster ---
    # For each unique match-set, what's the conjunct-count distribution
    # of predicates that produce it?
    dl_per_matchset: Dict[frozenset, List[int]] = defaultdict(list)
    for ch, ms in matchset_per_hash.items():
        dl = len(pred_by_hash[ch])
        dl_per_matchset[ms].append(dl)

    dl_summary = []
    for ms, dls in dl_per_matchset.items():
        if len(dls) < 2:
            continue  # need >=2 variants to measure variance
        if len(ms) < 3:
            continue  # focus on real clusters
        recs = [e for e in corpus if id(e) in ms]
        kr = sum(1 for e in recs if e.kill_verdict) / len(recs) if recs else 0.0
        if kr < 0.999:
            continue
        dl_summary.append({
            "match_size": len(ms),
            "n_variants": len(dls),
            "min_dl": min(dls),
            "max_dl": max(dls),
            "median_dl": statistics.median(dls),
            "stdev_dl": statistics.stdev(dls) if len(dls) > 1 else 0.0,
        })

    return {
        "n_records": len(records),
        "n_seeds": len(seeds),
        "n_unique_predicates": len(pred_by_hash),
        "predicate_recurrence_dist": dict(recurrence_dist),
        "n_unique_matchsets": len(matchset_per_hash) if matchset_per_hash else 0,
        "matchset_recurrence_dist": dict(matchset_recurrence_dist),
        "high_quality_matchsets": sorted(
            high_quality_matchsets, key=lambda x: -x["match_size"]
        ),
        "description_length_summary": sorted(
            dl_summary, key=lambda x: -x["match_size"]
        ),
    }


def render_stability_report(
    analysis: Dict[str, Any], ledger_label: str
) -> str:
    n_seeds = analysis["n_seeds"]
    rec = analysis["predicate_recurrence_dist"]
    ms_rec = analysis["matchset_recurrence_dist"]
    n_uniq = analysis["n_unique_predicates"]
    n_ms = analysis["n_unique_matchsets"]

    # Compute summary scores
    full_seed_preds = rec.get(n_seeds, 0)
    pred_recurrence_pct = 100 * full_seed_preds / n_uniq if n_uniq else 0.0

    full_seed_ms = ms_rec.get(n_seeds, 0)
    ms_recurrence_pct = 100 * full_seed_ms / n_ms if n_ms else 0.0

    lines = [
        f"# Stability analysis: {ledger_label}",
        "",
        f"- Records: {analysis['n_records']}",
        f"- Unique seeds: {n_seeds}",
        f"- Unique predicates (lift>=5): {n_uniq}",
        f"- Unique match-sets: {n_ms}",
        "",
        "## Metric 1 — predicate recurrence by content_hash",
        "",
        f"How many seeds independently produced each predicate?",
        "",
        "| seeds | predicates | % |",
        "|---|---|---|",
    ]
    for n in range(1, n_seeds + 1):
        c = rec.get(n, 0)
        pct = 100 * c / n_uniq if n_uniq else 0.0
        lines.append(f"| {n}/{n_seeds} | {c} | {pct:.1f}% |")

    lines += [
        "",
        f"**{full_seed_preds} of {n_uniq} unique predicates** "
        f"({pred_recurrence_pct:.1f}%) appeared in ALL {n_seeds} seeds.",
        "",
        "## Metric 2 — match-set overlap across seeds",
        "",
        f"How many seeds found at least one predicate with each match-set?",
        "",
        "| seeds | match-sets | % |",
        "|---|---|---|",
    ]
    for n in range(1, n_seeds + 1):
        c = ms_rec.get(n, 0)
        pct = 100 * c / n_ms if n_ms else 0.0
        lines.append(f"| {n}/{n_seeds} | {c} | {pct:.1f}% |")

    lines += [
        "",
        f"**{full_seed_ms} of {n_ms} unique match-sets** "
        f"({ms_recurrence_pct:.1f}%) were independently found by all "
        f"{n_seeds} seeds.",
        "",
    ]

    hq = analysis["high_quality_matchsets"]
    if hq:
        lines += [
            "### High-quality clusters (match>=3, kill_rate=1.0)",
            "",
            "| match_size | seeds | predicate variants |",
            "|---|---|---|",
        ]
        for h in hq:
            lines.append(
                f"| {h['match_size']} | {h['n_seeds']}/{n_seeds} | {h['n_predicate_variants']} |"
            )
        lines.append("")

    dl = analysis["description_length_summary"]
    if dl:
        lines += [
            "## Metric 3 — description-length variance per cluster",
            "",
            "Within each match-set-equivalent cluster, what conjunct counts does the engine produce?",
            "",
            "| match_size | n_variants | min_dl | max_dl | median_dl | stdev |",
            "|---|---|---|---|---|---|",
        ]
        for d in dl:
            lines.append(
                f"| {d['match_size']} | {d['n_variants']} | "
                f"{d['min_dl']} | {d['max_dl']} | {d['median_dl']:.1f} | "
                f"{d['stdev_dl']:.2f} |"
            )
        lines.append("")

    # Verdict — focus on HIGH-QUALITY cluster recurrence, not bulk predicate count
    lines.append("## Verdict")
    lines.append("")
    if hq:
        n_hq = len(hq)
        n_robust_hq = sum(1 for h in hq if h["n_seeds"] == n_seeds)
        hq_robust_pct = 100 * n_robust_hq / n_hq if n_hq else 0.0
        if n_hq == 0:
            verdict = (
                "**NO HIGH-QUALITY CLUSTERS** — engine produced no predicates with "
                "match>=3 and kill_rate=1.0. Either corpus is too noisy or "
                "substrate-pass criteria are too strict."
            )
        elif hq_robust_pct >= 80:
            verdict = (
                f"**HIGH STABILITY** — {n_robust_hq}/{n_hq} high-quality clusters "
                f"({hq_robust_pct:.0f}%) reproduced by all {n_seeds} seeds. "
                "Strong signals are robust; engine is discovering structure."
            )
        elif hq_robust_pct >= 50:
            verdict = (
                f"**MIXED STABILITY** — {n_robust_hq}/{n_hq} high-quality clusters "
                f"({hq_robust_pct:.0f}%) reproduced by all {n_seeds} seeds. "
                "Strongest signals are robust; weaker ones are seed-specific. "
                "**Treat single-seed findings as low-confidence hypotheses, not discoveries.**"
            )
        else:
            verdict = (
                f"**LOW STABILITY** — only {n_robust_hq}/{n_hq} high-quality clusters "
                f"({hq_robust_pct:.0f}%) reproduced by all {n_seeds} seeds. "
                "Most discoveries are seed-specific. Either run more seeds or "
                "tighten substrate-pass criteria before claiming structural findings."
            )
    else:
        verdict = (
            "**NO HIGH-QUALITY CLUSTERS** — engine produced no predicates with "
            "match>=3 and kill_rate=1.0. Either corpus is too noisy or "
            "substrate-pass criteria are too strict."
        )
    lines.append(verdict)
    lines.append("")
    lines.append(
        "Note: bulk predicate recurrence (Metric 1) is naturally low because "
        "the engine's stochastic search produces many seed-specific predicate "
        "variants. The substrate-grade question is whether the HIGH-QUALITY "
        "clusters (Metric 2's match-set overlap) are reproducible — not "
        "whether every predicate is."
    )

    return "\n".join(lines)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m ergon.learner.tools.stability_analysis "
              "<ledger.jsonl> [--corpus a149_real|obstruction_synthetic] "
              "[--min-lift FLOAT]")
        return 2

    paths = []
    corpus_id = "a149_real"
    min_lift = 5.0
    i = 1
    while i < len(argv):
        if argv[i] == "--corpus":
            corpus_id = argv[i + 1]
            i += 2
        elif argv[i] == "--min-lift":
            min_lift = float(argv[i + 1])
            i += 2
        else:
            paths.append(Path(argv[i]))
            i += 1

    if not paths:
        print("No ledger paths provided.")
        return 2
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"Ledger not found: {p}")
        return 1
    if corpus_id not in CORPUS_LOADERS:
        print(f"Unknown corpus '{corpus_id}'")
        return 1

    print(f"Loading {corpus_id} corpus...", file=sys.stderr)
    corpus = CORPUS_LOADERS[corpus_id]()

    seen = set()
    records = []
    for p in paths:
        print(f"Loading ledger {p}...", file=sys.stderr)
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    key = (r.get("genome_content_hash"), r.get("seed"),
                           r.get("episode"), r.get("trial_name"))
                    if key not in seen:
                        seen.add(key)
                        records.append(r)

    print(f"Analyzing stability across {len(records)} records "
          f"(min_lift={min_lift})...", file=sys.stderr)
    analysis = analyze_stability(records, corpus, min_lift=min_lift)
    label = paths[0].name if len(paths) == 1 else f"{len(paths)} merged ledgers"
    print(render_stability_report(analysis, label))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
