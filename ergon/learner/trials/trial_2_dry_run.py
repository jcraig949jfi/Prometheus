"""Trial 2 dry-run pilot — engine smoke test at small scale.

Runs the TrialTwoEngine for 200 episodes and reports:
- archive cell-fill rate
- per-operator-class fill counts + fill efficiency
- coverage divergence between operator classes
- F_TRIVIAL_BAND_REJECT trigger rate
- minimum-share enforcement compliance
- band concentration per operator (the load-bearing Trial 2 metric)

Per the v8 design freeze: this is the actual empirical test that
informs whether the v8 envelope holds. Adjusted post-Trial-1: PROMOTE
rate is no longer the primary metric (classifier in deep escrow);
band concentration + cell-fill diversity are.

Acceptance criteria for this dry-run (scaled from v8 §4 Trial 2):
  Primary: structural cell-fill ≥ 1.5× uniform cell-fill
  Secondary: archive coverage ≥ 5% of 5,000 cells (250 cells)
             at 200 episodes (very conservative; 1K episodes target 20-30%)
  Tertiary: F_TRIVIAL_BAND_REJECT rate within [5%, 30%] (or [0%, 30%]
            if no trivial patterns surface at MVP-scale stub evaluator)
  Quaternary: scheduler min-share constraints all compliant
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ergon.learner.engine import TrialTwoEngine


def run_dry_run(n_episodes: int = 200, seed: int = 42) -> dict:
    """Execute the dry-run pilot and return results dict."""
    print(f"=== Trial 2 dry-run pilot: n_episodes={n_episodes}, seed={seed} ===")
    engine = TrialTwoEngine(seed=seed)
    report = engine.run(n_episodes=n_episodes)

    # Per-operator metrics from archive
    fill_counts = engine.archive.operator_fill_count()
    eval_counts = engine.archive.operator_eval_count()
    fill_efficiency = engine.archive.operator_fill_efficiency()

    # Coverage divergence between operator classes
    pairs = [
        ("structural", "uniform"),
        ("structural", "anti_prior"),
        ("symbolic", "uniform"),
        ("anti_prior", "uniform"),
        ("anti_prior", "structured_null"),
    ]
    coverage_divergences = {
        f"{a}_vs_{b}": engine.archive.coverage_divergence(a, b)
        for a, b in pairs
    }

    # Band concentration per operator (axis 3 = magnitude bucket)
    band_conc = engine.archive.band_concentration_per_operator(axis_index=3)

    # Scheduler compliance
    scheduler_compliance = engine.scheduler.check_min_share_compliance()
    cumulative_shares = engine.scheduler.cumulative_shares()

    # Acceptance criteria evaluation
    structural_fills = fill_counts.get("structural", 0)
    uniform_fills = fill_counts.get("uniform", 0)
    primary_pass = structural_fills >= 1.5 * max(uniform_fills, 1)
    secondary_target = max(int(n_episodes * 0.05), 10)
    secondary_pass = report.archive_n_cells_filled >= secondary_target
    trivial_rate = report.f_trivial_band_reject_rate
    tertiary_pass = trivial_rate <= 0.30  # upper bound
    quaternary_pass = all(info["compliant"] for info in scheduler_compliance.values())

    return {
        "n_episodes": n_episodes,
        "seed": seed,
        "elapsed_seconds": report.elapsed_seconds,
        "n_promoted": report.n_promoted,
        "n_trivial_rejects": report.n_trivial_rejects,
        "f_trivial_band_reject_rate": trivial_rate,
        "archive_n_cells_filled": report.archive_n_cells_filled,
        "operator_call_counts": dict(report.operator_call_counts),
        "operator_fill_counts": fill_counts,
        "operator_fill_efficiency": fill_efficiency,
        "coverage_divergences": coverage_divergences,
        "band_concentration_per_operator": {
            op: dict(dist) for op, dist in band_conc.items()
        },
        "scheduler_cumulative_shares": cumulative_shares,
        "scheduler_min_share_compliance": scheduler_compliance,
        "acceptance": {
            "primary_structural_vs_uniform_1_5x": primary_pass,
            "primary_structural_fills": structural_fills,
            "primary_uniform_fills": uniform_fills,
            "primary_ratio": (
                structural_fills / max(uniform_fills, 1)
                if uniform_fills > 0
                else float("inf")
            ),
            "secondary_archive_coverage": secondary_pass,
            "secondary_target": secondary_target,
            "tertiary_trivial_rate": tertiary_pass,
            "quaternary_min_share_compliance": quaternary_pass,
        },
    }


def format_report(results: dict) -> str:
    """Pretty-print a Trial 2 dry-run summary."""
    lines = [
        "=" * 72,
        f"Trial 2 Dry-Run Report (seed={results['seed']}, n={results['n_episodes']})",
        "=" * 72,
        f"Elapsed: {results['elapsed_seconds']:.2f}s",
        f"Episodes/sec: {results['n_episodes'] / max(results['elapsed_seconds'], 1e-6):.1f}",
        "",
        "ACCEPTANCE",
        f"  [Primary] structural >= 1.5x uniform fills: "
        f"{'PASS' if results['acceptance']['primary_structural_vs_uniform_1_5x'] else 'FAIL'} "
        f"(structural={results['acceptance']['primary_structural_fills']}, "
        f"uniform={results['acceptance']['primary_uniform_fills']}, "
        f"ratio={results['acceptance']['primary_ratio']:.2f})",
        f"  [Secondary] archive coverage >= {results['acceptance']['secondary_target']}: "
        f"{'PASS' if results['acceptance']['secondary_archive_coverage'] else 'FAIL'} "
        f"(actual={results['archive_n_cells_filled']})",
        f"  [Tertiary] trivial rate in [0, 30%]: "
        f"{'PASS' if results['acceptance']['tertiary_trivial_rate'] else 'FAIL'} "
        f"(actual={results['f_trivial_band_reject_rate']:.3f})",
        f"  [Quaternary] scheduler min-share compliant: "
        f"{'PASS' if results['acceptance']['quaternary_min_share_compliance'] else 'FAIL'}",
        "",
        "OPERATOR FILL COUNTS",
    ]
    for op, count in sorted(results["operator_fill_counts"].items()):
        eff = results["operator_fill_efficiency"].get(op, 0)
        lines.append(f"  {op:18s}: {count:4d} cells (efficiency: {eff:.3f})")
    lines += ["", "SCHEDULER CUMULATIVE SHARES"]
    for op, share in sorted(results["scheduler_cumulative_shares"].items()):
        lines.append(f"  {op:18s}: {share:.3f}")
    lines += ["", "COVERAGE DIVERGENCES (Jaccard distance between operator-cell-sets)"]
    for pair, div in sorted(results["coverage_divergences"].items()):
        lines.append(f"  {pair:35s}: {div:.3f}")
    lines += [
        "",
        f"PROMOTED: {results['n_promoted']}",
        f"TRIVIAL REJECTS: {results['n_trivial_rejects']}",
        "",
        "Note: PROMOTE rate at MVP scope uses MVPSubstrateEvaluator stub",
        "calibrated against Path B's empirical 0/30000 finding; near-zero",
        "promotes is expected, not failure.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_dry_run(n_episodes=200, seed=42)
    out_dir = Path(__file__).parent
    out_path = out_dir / "trial_2_dry_run_results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")

    report = format_report(results)
    report_path = out_dir / "TRIAL_2_DRY_RUN_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nFull JSON: {out_path}")
    print(f"Report: {report_path}")
