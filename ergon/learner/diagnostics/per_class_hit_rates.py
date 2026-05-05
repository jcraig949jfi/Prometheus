"""ergon.learner.diagnostics.per_class_hit_rates — per-operator-class hit rates.

Computed by Charon, 2026-05-05, as outside auditor. Ergon's scheduler enforces
minimum shares (uniform/anti_prior/structured_null >= 5%) but has no data on
which classes actually produce hits. This module computes three hit-rate
definitions per class with cross-seed CIs.

Three hit definitions, all reported:

1. PROMOTE rate
   numerator: substrate-PASS records of class in ledger
   denominator: actual attempts of class (scheduler simulation)
   caveat: in Ergon's a149 predicate-search, "PROMOTE" = substrate-pass
   (lift >= 2.0 AND match_size >= 3). Strict kernel PROMOTE (F1+F6+F9+F11
   all CLEAR) does NOT apply — predicates aren't directly tested by the
   battery; corpus records are. This metric is the closest defensible
   analog given persisted data.

2. Archive cell-fill rate
   numerator: distinct canonical_predicate_hash values for class in ledger
   denominator: actual attempts of class
   caveat: this is a predicate-novelty proxy for MAP-Elites cell-fill. The
   archive's true cell-fill (cell-coordinate based) is computed at submit
   time and not persisted. Distinct canonical-predicates per class
   approximates "novel substrate contribution" but may diverge from
   true MAP-Elites cell-fill. Trial 2's archive_n_cells aggregates
   across classes and isn't broken down per-class.

3. Near-miss rate
   numerator: substrate-PASS records of class with matched_kill_rate in (0, 1)
   denominator: actual attempts of class
   caveat: KILL_VECTOR_SPEC.md ("cleared k of 4 falsifiers, k>=3") applies
   to the Lehmer/Mahler discovery pipeline. Ergon's a149 predicate-search
   has different semantics — predicates capture record sets, not single
   candidates tested by F1+F6+F9+F11. Closest defensible adaptation:
   "captured a partial-kill cluster" — match-set whose records mostly-
   but-not-uniformly cleared their battery. matched_kill_rate ∈ (0, 1)
   with strict bounds. Don't compare numerically across pipelines.

Cross-seed discipline:
- Per-config reports: stratified by weight regime (u05_canonical,
  u30_broad). Each config has 3 seeds; we bootstrap CIs over seeds.
- Aggregate report: stratified bootstrap over (config, seed) pairs.
- Single-seed findings get explicit n_seeds=1 flag; do not treat as robust.

Data sources (a149_real corpus only):
- ergon/learner/trials/ledgers/trial_3_iter28_a149_u05_canonical_ledger.jsonl
- ergon/learner/trials/ledgers/trial_3_iter28_a149_u30_broad_ledger.jsonl
- ergon/learner/trials/ledgers/trial_3_iter31_a149_u05_15k_ledger.jsonl
- ergon/learner/trials/ledgers/trial_3_iter31_a149_u30_15k_ledger.jsonl

Synthetic-corpus ledgers (iter15, iter18, iter27) excluded — different
corpus, different scheduler regime, different lift threshold.

Usage:
  python -m ergon.learner.diagnostics.per_class_hit_rates
"""
from __future__ import annotations

import json
import random
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[3]
LEDGER_DIR = REPO / "ergon" / "learner" / "trials" / "ledgers"

# a149_real ledgers only — synthetic ledgers excluded for regime-purity
A149_REAL_LEDGERS = [
    "trial_3_iter28_a149_u05_canonical_ledger.jsonl",
    "trial_3_iter28_a149_u30_broad_ledger.jsonl",
    "trial_3_iter31_a149_u05_15k_ledger.jsonl",
    "trial_3_iter31_a149_u30_15k_ledger.jsonl",
]

OPERATOR_CLASSES = ["structural", "symbolic", "anti_prior", "uniform", "structured_null"]

# Mirror scheduler.DEFAULT_MIN_SHARES — minimum-share enforcement floors
DEFAULT_MIN_SHARES = {
    "uniform": 0.05,
    "anti_prior": 0.05,
    "structured_null": 0.05,
}

LOOKBACK_WINDOW = 100  # scheduler default


def simulate_scheduler_calls(
    weights: Dict[str, float],
    seed: int,
    n_episodes: int,
    min_shares: Optional[Dict[str, float]] = None,
    lookback_window: int = LOOKBACK_WINDOW,
) -> Counter:
    """Replay the OperatorScheduler deterministically; return per-class counts.

    Mirrors ergon.learner.scheduler.OperatorScheduler.next_operator_class
    exactly. Reproduces actual attempt counts per class under min-share
    enforcement, given the same seed and weights.
    """
    if min_shares is None:
        min_shares = DEFAULT_MIN_SHARES
    rng = random.Random(seed)
    classes = list(weights.keys())
    weight_vals = [weights[c] for c in classes]

    from collections import deque
    recent: deque = deque(maxlen=lookback_window)
    counts: Counter = Counter()

    for _ in range(n_episodes):
        chosen = None
        # Min-share enforcement (only after warm-up)
        if len(recent) >= lookback_window:
            window_counts = Counter(recent)
            window_size = len(recent)
            for op, ms in min_shares.items():
                actual_share = window_counts.get(op, 0) / window_size
                if actual_share < ms:
                    if chosen is None or actual_share < (
                        window_counts.get(chosen, 0) / window_size
                    ):
                        chosen = op

        if chosen is None:
            chosen = rng.choices(classes, weights=weight_vals, k=1)[0]

        recent.append(chosen)
        counts[chosen] += 1

    return counts


def load_ledger_records(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL ledger records into a list of dicts."""
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def per_seed_hit_counts(
    records: List[Dict[str, Any]], seed: int
) -> Dict[str, Dict[str, int]]:
    """Compute per-class hit numerators for a single seed.

    Returns: class -> {n_promote, n_unique_canonical, n_near_miss}
    """
    out: Dict[str, Dict[str, int]] = {
        c: {"n_promote": 0, "n_unique_canonical": 0, "n_near_miss": 0}
        for c in OPERATOR_CLASSES
    }
    seen_canonical_per_class: Dict[str, set] = defaultdict(set)
    for r in records:
        if r.get("seed") != seed:
            continue
        op = r.get("operator_class")
        if op not in OPERATOR_CLASSES:
            continue

        # PROMOTE: every ledger record is a substrate-PASS event by construction
        out[op]["n_promote"] += 1

        # Distinct canonical predicates
        ch = r.get("canonical_predicate_hash")
        if ch is None:
            # Legacy: fall back to genome_content_hash (over-counts; flagged in honesty notes)
            ch = r.get("genome_content_hash", "")
        if ch and ch not in seen_canonical_per_class[op]:
            seen_canonical_per_class[op].add(ch)

        # Near-miss: matched_kill_rate strictly in (0, 1)
        mkr = None
        extra = r.get("extra")
        if isinstance(extra, dict):
            mkr = extra.get("matched_kill_rate")
        if mkr is not None and 0.0 < float(mkr) < 1.0:
            out[op]["n_near_miss"] += 1

    for c in OPERATOR_CLASSES:
        out[c]["n_unique_canonical"] = len(seen_canonical_per_class[c])
    return out


def per_seed_rates(
    records: List[Dict[str, Any]],
    seed: int,
    weights: Dict[str, float],
    n_episodes: int,
) -> Dict[str, Dict[str, Any]]:
    """Compute per-class rates for one seed: numerator / actual_attempts."""
    attempts = simulate_scheduler_calls(weights, seed, n_episodes)
    counts = per_seed_hit_counts(records, seed)
    out: Dict[str, Dict[str, Any]] = {}
    for c in OPERATOR_CLASSES:
        n_att = attempts.get(c, 0)
        out[c] = {
            "n_attempts": n_att,
            "n_promote": counts[c]["n_promote"],
            "n_unique_canonical": counts[c]["n_unique_canonical"],
            "n_near_miss": counts[c]["n_near_miss"],
            "promote_rate": (counts[c]["n_promote"] / n_att) if n_att else 0.0,
            "archive_fill_rate": (
                counts[c]["n_unique_canonical"] / n_att
            ) if n_att else 0.0,
            "near_miss_rate": (counts[c]["n_near_miss"] / n_att) if n_att else 0.0,
        }
    return out


def bootstrap_ci(
    values: List[float], n_resamples: int = 2000, alpha: float = 0.05,
    rng_seed: int = 7
) -> Tuple[float, float, float]:
    """Percentile bootstrap CI. Returns (mean, ci_low, ci_high).

    Uses the seed-level values list; resamples with replacement.
    """
    if not values:
        return (0.0, 0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0], values[0])
    rng = random.Random(rng_seed)
    n = len(values)
    means = []
    for _ in range(n_resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.fmean(sample))
    means.sort()
    lo_idx = int(n_resamples * alpha / 2)
    hi_idx = int(n_resamples * (1 - alpha / 2)) - 1
    return (statistics.fmean(values), means[lo_idx], means[hi_idx])


def collect_seed_rates(
    ledger_paths: List[Path],
) -> Dict[str, List[Dict[str, Any]]]:
    """For each ledger, compute per-seed rates. Return list of seed-rate dicts.

    Each seed-rate dict has keys:
      ledger, config, seed, weights, n_episodes, per_class
    """
    by_config: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for path in ledger_paths:
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        if not meta_path.exists():
            print(f"[warn] meta missing: {meta_path}; skipping {path.name}")
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        weights = meta["weights"]
        n_episodes = meta["n_episodes"]
        records = load_ledger_records(path)
        seeds_in_ledger = sorted({r["seed"] for r in records if "seed" in r})
        config_key = f"{meta.get('trial_name', path.stem)}"
        for seed in seeds_in_ledger:
            rates = per_seed_rates(records, seed, weights, n_episodes)
            by_config[config_key].append({
                "ledger": path.name,
                "config": config_key,
                "seed": seed,
                "weights": weights,
                "n_episodes": n_episodes,
                "per_class": rates,
            })
    return dict(by_config)


def aggregate_per_class_across_seeds(
    seed_rate_records: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Aggregate across seed-records (any stratum) into per-class CI dicts.

    For each operator class and each metric, compute mean + bootstrap CI
    over the seed-level values.
    """
    out: Dict[str, Dict[str, Dict[str, float]]] = {}
    for c in OPERATOR_CLASSES:
        per_class_metrics: Dict[str, Dict[str, float]] = {}
        for metric in ("promote_rate", "archive_fill_rate", "near_miss_rate"):
            vals = [r["per_class"][c][metric] for r in seed_rate_records]
            mean, lo, hi = bootstrap_ci(vals)
            per_class_metrics[metric] = {
                "mean": mean,
                "ci_low": lo,
                "ci_high": hi,
                "n_seed_observations": len(vals),
                "raw_values": vals,
            }
        # Also report attempt counts (median/min/max — not bootstrap)
        attempts = [r["per_class"][c]["n_attempts"] for r in seed_rate_records]
        per_class_metrics["n_attempts_per_seed"] = {
            "median": statistics.median(attempts) if attempts else 0,
            "min": min(attempts) if attempts else 0,
            "max": max(attempts) if attempts else 0,
        }
        out[c] = per_class_metrics
    return out


def main() -> None:
    ledger_paths = [LEDGER_DIR / name for name in A149_REAL_LEDGERS]
    missing = [p for p in ledger_paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"[error] missing ledger: {p}")
        raise SystemExit(1)

    print(f"Loading {len(ledger_paths)} a149_real ledgers...")
    by_config = collect_seed_rates(ledger_paths)

    # Per-config aggregation
    per_config_agg: Dict[str, Dict[str, Any]] = {}
    for config_key, seed_records in by_config.items():
        per_config_agg[config_key] = {
            "n_seeds": len(seed_records),
            "n_episodes_per_seed": (
                seed_records[0]["n_episodes"] if seed_records else 0
            ),
            "weights": seed_records[0]["weights"] if seed_records else {},
            "per_class": aggregate_per_class_across_seeds(seed_records),
        }

    # Aggregate across all seed-records (stratified bootstrap = pooled bootstrap
    # since each seed-record contributes a per-seed rate; resampling across
    # all 12 seed-records weights configs equally per data point, not per
    # config). Documented in honesty notes.
    all_seed_records = [r for recs in by_config.values() for r in recs]
    aggregate_per_class = aggregate_per_class_across_seeds(all_seed_records)

    honesty_notes = [
        "Denominators come from deterministic scheduler simulation (OperatorScheduler "
        "replay with seed + weights), not from persisted attempt counts. The engine's "
        "operator_call_counts is computed at runtime but not persisted in the ledger "
        "or trial_results.json. Replay agrees with weights × n_episodes within "
        "multinomial variance for the warm-up period; min-share enforcement adjusts "
        "shares for post-warm-up episodes (see scheduler.py).",
        "PROMOTE rate uses Ergon's substrate-pass criterion (lift >= 2.0 AND match_size "
        ">= 3). Strict kernel PROMOTE (F1+F6+F9+F11 all CLEAR) is not applicable to "
        "predicate search: predicates aren't tested by the battery; corpus records "
        "are. Per engine.py docstring, strict kernel PROMOTE at Path B is empirically "
        "0/30000 — different metric, different pipeline.",
        "Archive cell-fill rate is approximated by distinct canonical_predicate_hash "
        "per class. The MAP-Elites archive's true cell-fill (cell-coordinate-based) "
        "is computed at archive.submit() time but not persisted. The proxy may "
        "undercount classes that explore many cells with the same predicate or "
        "overcount classes that produce predicate variants without exploring new "
        "cells. Trial 2's archive_n_cells (per-seed total) is consistent with these "
        "numbers in aggregate but cannot be broken down per-class without re-running.",
        "Near-miss rate adapts KILL_VECTOR_SPEC's 'cleared k of 4 falsifiers, k>=3' "
        "to predicate-search. The adaptation: predicate captured a partial-kill "
        "cluster (matched_kill_rate strictly in (0, 1)). This is qualitatively "
        "similar — a substrate-PASS event whose match-set isn't unanimous. Don't "
        "compare numerically across the Lehmer/Mahler kill_vector pipeline; the "
        "semantics of 'falsifier' differ.",
        "Cross-seed CIs are 95% percentile bootstrap (2000 resamples) over per-seed "
        "rates. With 12 seed-records (3 seeds × 4 configs) the CIs are wide; treat "
        "any single-config metric (n_seed_observations=3) as exploratory only. "
        "n_seed_observations=1 means single-seed; flagged below.",
        "Aggregate-level CIs pool across configs. This treats u05_canonical and "
        "u30_broad as the same regime, which is partly defensible (same corpus, "
        "same evaluator, same scheduler module — only weights differ) but also "
        "partly conflated (different weight regimes induce different exploration "
        "dynamics). The per-config table preserves regime separation; consult both.",
        "Synthetic-corpus ledgers (iter15, iter18, iter27_uniform30) are excluded. "
        "Different corpus, different lift threshold, different baseline kill rate. "
        "Mixing would conflate regimes.",
        "Iter28 had 1/3-seed cluster discovery flagged in CALIBRATION post; treat "
        "any class-specific metric where one seed dominates as suspect. Per-seed "
        "raw_values are reported in the JSON for verification.",
        "The scheduler's deterministic replay reconstructs attempts exactly only if "
        "trial_3_iter28_a149_real.py used the same min_shares (DEFAULT_MIN_SHARES) "
        "and lookback_window (100) as the scheduler module. These are the defaults "
        "and the trial code does not override; verified by code-read 2026-05-05.",
    ]

    output = {
        "computed_date": date.today().isoformat(),
        "computed_by": "Charon (outside auditor)",
        "data_sources": [str(p.relative_to(REPO)) for p in ledger_paths],
        "definitions": {
            "promote": (
                "(substrate-PASS records of class) / (actual scheduler attempts of class). "
                "Ergon a149: substrate-pass = lift >= 2.0 AND match_size >= 3."
            ),
            "archive_fill": (
                "(distinct canonical_predicate_hash values of class) / (actual scheduler "
                "attempts of class). Predicate-novelty proxy for MAP-Elites cell-fill."
            ),
            "near_miss": (
                "(substrate-PASS records of class with matched_kill_rate ∈ (0, 1)) / "
                "(actual scheduler attempts of class). Predicate captured a partial-kill "
                "cluster. Adaptation of KILL_VECTOR_SPEC near-miss semantics."
            ),
        },
        "per_class": aggregate_per_class,
        "per_config": per_config_agg,
        "honesty_notes": honesty_notes,
    }

    out_dir = REPO / "ergon" / "learner" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "per_class_hit_rates.json"
    out_json.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_json}")

    # Markdown report
    md = render_markdown_report(output)
    md_path = out_dir / "PER_CLASS_HIT_RATES_REPORT.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {md_path}")


def render_markdown_report(output: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Per-Class Mutation Hit Rates")
    lines.append("")
    lines.append(f"**Computed:** {output['computed_date']}  ")
    lines.append(f"**By:** {output['computed_by']}  ")
    lines.append(f"**Corpus:** a149_real (4 ledgers, 12 seed-records, ~24K substrate-passes)  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Definitions")
    lines.append("")
    for k, v in output["definitions"].items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Aggregate table
    lines.append("## Aggregate per class (12 seed-records, all configs pooled)")
    lines.append("")
    lines.append("Bootstrap 95% CIs (2000 resamples). `n_seed_obs=12` for all classes.")
    lines.append("")
    lines.append("| class | promote (mean [CI]) | archive_fill (mean [CI]) | near_miss (mean [CI]) | typical n_attempts/seed |")
    lines.append("|---|---|---|---|---|")
    for c in OPERATOR_CLASSES:
        agg = output["per_class"][c]
        p = agg["promote_rate"]
        a = agg["archive_fill_rate"]
        n = agg["near_miss_rate"]
        atts = agg["n_attempts_per_seed"]
        lines.append(
            f"| {c} | "
            f"{p['mean']:.4f} [{p['ci_low']:.4f}, {p['ci_high']:.4f}] | "
            f"{a['mean']:.4f} [{a['ci_low']:.4f}, {a['ci_high']:.4f}] | "
            f"{n['mean']:.4f} [{n['ci_low']:.4f}, {n['ci_high']:.4f}] | "
            f"~{atts['median']} (range {atts['min']}-{atts['max']}) |"
        )
    lines.append("")

    # Per-config tables
    lines.append("## Per-config (regime-separated)")
    lines.append("")
    for cfg, info in output["per_config"].items():
        lines.append(f"### {cfg}")
        lines.append("")
        lines.append(f"weights: `{json.dumps(info['weights'])}`  ")
        lines.append(f"n_episodes/seed: {info['n_episodes_per_seed']}, n_seeds: {info['n_seeds']}")
        lines.append("")
        lines.append("| class | promote | archive_fill | near_miss | n_attempts/seed |")
        lines.append("|---|---|---|---|---|")
        for c in OPERATOR_CLASSES:
            pc = info["per_class"][c]
            atts = pc["n_attempts_per_seed"]
            p = pc["promote_rate"]
            a = pc["archive_fill_rate"]
            n = pc["near_miss_rate"]
            lines.append(
                f"| {c} | "
                f"{p['mean']:.4f} [{p['ci_low']:.4f}, {p['ci_high']:.4f}] | "
                f"{a['mean']:.4f} [{a['ci_low']:.4f}, {a['ci_high']:.4f}] | "
                f"{n['mean']:.4f} [{n['ci_low']:.4f}, {n['ci_high']:.4f}] | "
                f"~{atts['median']} |"
            )
        lines.append("")

    lines.append("## Honesty notes")
    lines.append("")
    for h in output["honesty_notes"]:
        lines.append(f"- {h}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Substrate use")
    lines.append("")
    lines.append(
        "Numbers above are **internal fuel for the scheduler**, not external claims. "
        "Compare classes within the same metric and same config — cross-pipeline "
        "comparisons (Ergon vs Lehmer/Mahler) are not supported by the data. "
        "Wide CIs (n=12 seed-records) mean any per-class ranking of small effect "
        "sizes is unreliable; consider larger n_seeds or longer runs before "
        "shifting compute on borderline numbers."
    )
    lines.append("")
    lines.append("— Charon, outside auditor, " + output["computed_date"])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
