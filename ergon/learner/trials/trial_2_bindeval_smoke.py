"""Trial 2 BindEvalKernelV2 smoke test.

Per Iteration 2 of MVP build (queued from Trial 2 production pilot
that passed all 4 acceptance criteria with the stub evaluator):

This smoke test runs a small pilot (200 episodes, 1 seed) using the
real BindEvalKernelV2 via BindEvalEvaluator. Goals:
  1. Verify the BIND/EVAL pipeline survives 200 round-trips
  2. Compare archive size + selection-pressure ratio against the stub
  3. Measure per-EVAL latency (the substrate-discipline tradeoff)

Acceptance:
  - 200 EVALs complete without error
  - structural fills > uniform fills (selection pressure works)
  - p50 EVAL latency < 50ms (well above the 5ms hot-path budget; we're
    counting cache miss overhead)
"""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from ergon.learner.engine import TrialTwoEngine
from ergon.learner.genome_evaluator import BindEvalEvaluator
from ergon.learner.scheduler import OperatorScheduler


def run_smoke_test(n_episodes: int = 200, seed: int = 42) -> dict:
    """Run engine with real BindEvalEvaluator instead of MVP stub."""
    print(f"=== BindEvalKernelV2 smoke test: n={n_episodes}, seed={seed} ===")
    t_init_start = time.time()
    evaluator = BindEvalEvaluator(promote_rate=0.0001)
    t_init = time.time() - t_init_start
    print(f"  BindEvalIntegration init: {t_init*1000:.1f}ms")

    scheduler = OperatorScheduler(seed=seed)
    engine = TrialTwoEngine(seed=seed, scheduler=scheduler, evaluator=evaluator)

    t_start = time.time()
    report = engine.run(n_episodes=n_episodes)
    elapsed = time.time() - t_start

    fill_counts = engine.archive.operator_fill_count()
    structural = fill_counts.get("structural", 0)
    uniform = fill_counts.get("uniform", 0)
    ratio = structural / max(uniform, 1)

    # Per-episode latency stats
    ep_latencies = [ep.elapsed_seconds * 1000 for ep in engine.episodes]
    p50 = statistics.median(ep_latencies)
    p95 = statistics.quantiles(ep_latencies, n=20)[18] if len(ep_latencies) >= 20 else max(ep_latencies)

    return {
        "n_episodes": n_episodes,
        "seed": seed,
        "init_ms": t_init * 1000,
        "total_elapsed_s": elapsed,
        "ms_per_episode_avg": (elapsed / n_episodes) * 1000,
        "ep_latency_p50_ms": p50,
        "ep_latency_p95_ms": p95,
        "n_substrate_passed": report.n_substrate_passed,
        "n_won_cell": report.n_won_cell,
        "n_trivial_rejects": report.n_trivial_rejects,
        "archive_n_cells_filled": report.archive_n_cells_filled,
        "fill_counts": fill_counts,
        "structural_uniform_ratio": ratio,
        "evaluator_cache_size": len(evaluator._cache),
        "acceptance": {
            "completed_without_error": True,
            "structural_beats_uniform": structural > uniform,
            "p50_latency_under_50ms": p50 < 50.0,
        },
    }


def format_report(results: dict) -> str:
    a = results["acceptance"]
    lines = [
        "=" * 72,
        f"BindEvalKernelV2 Smoke Test ({results['n_episodes']} episodes)",
        "=" * 72,
        "",
        "ACCEPTANCE",
        f"  [Completed without error]: {'PASS' if a['completed_without_error'] else 'FAIL'}",
        f"  [structural > uniform]:    {'PASS' if a['structural_beats_uniform'] else 'FAIL'}",
        f"  [p50 latency < 50ms]:      {'PASS' if a['p50_latency_under_50ms'] else 'FAIL'}",
        "",
        "TIMING",
        f"  Init:                {results['init_ms']:.1f} ms",
        f"  Total elapsed:       {results['total_elapsed_s']:.2f} s",
        f"  Per-episode avg:     {results['ms_per_episode_avg']:.2f} ms",
        f"  Per-episode p50:     {results['ep_latency_p50_ms']:.2f} ms",
        f"  Per-episode p95:     {results['ep_latency_p95_ms']:.2f} ms",
        "",
        "RESULTS",
        f"  Archive cells filled:    {results['archive_n_cells_filled']}",
        f"  Substrate-PASSED:        {results['n_substrate_passed']}",
        f"  Won-cell (archive elite): {results['n_won_cell']}",
        f"  Trivial rejects:         {results['n_trivial_rejects']}",
        f"  structural / uniform:    {results['structural_uniform_ratio']:.2f}x",
        "",
        "FILL COUNTS",
    ]
    for op, count in sorted(results["fill_counts"].items()):
        lines.append(f"  {op:18s}: {count:4d}")
    lines.append("")
    lines.append(f"BindEvalEvaluator cache size: {results['evaluator_cache_size']} entries")
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_smoke_test(n_episodes=200, seed=42)
    out_dir = Path(__file__).parent
    (out_dir / "trial_2_bindeval_smoke_results.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8"
    )
    report = format_report(results)
    (out_dir / "TRIAL_2_BINDEVAL_SMOKE_REPORT.md").write_text(report, encoding="utf-8")
    print()
    print(report)
