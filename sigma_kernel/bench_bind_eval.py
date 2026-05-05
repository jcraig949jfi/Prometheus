"""sigma_kernel/bench_bind_eval.py — measure the MVP's perf claims.

Three benchmarks the MVP doc claimed and one new one:

  1. BIND overhead vs raw import + call (claimed <50ms; expected ~1ms)
  2. EVAL overhead per call vs the raw callable (per-EVAL latency)
  3. Substrate growth per N evaluations (Postgres rows / SQLite rows)
  4. Cost-model accuracy: declared elapsed vs actual elapsed across the
     bootstrapped arsenal ops (over-/under-promise ratio per op)

Run::

    python sigma_kernel/bench_bind_eval.py

Reports a table to stdout. Designed for human eyeballing during MVP
acceptance review; no pytest assertions because perf depends on host
hardware.
"""
from __future__ import annotations

import importlib
import statistics
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel
from sigma_kernel.bind_eval_v2 import BindEvalKernelV2


def _percentile(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = int(len(xs) * p / 100)
    return xs[min(k, len(xs) - 1)]


def _bench_bind(n: int = 200, ext_factory=BindEvalExtension) -> dict:
    """How long does BIND take per call? Compares against raw import+call.

    ``ext_factory`` selects v1 (BindEvalExtension) or v2 (BindEvalKernelV2)
    so the same harness can be reused for both implementations.
    """
    kernel = SigmaKernel(":memory:")
    ext = ext_factory(kernel)
    ref = "techne.lib.mahler_measure:mahler_measure"

    bind_times = []
    for i in range(n):
        cap = kernel.mint_capability("BindCap")
        t0 = time.perf_counter()
        ext.BIND(
            callable_ref=ref,
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
            name=f"bench_bind_{i}",
            version=1,
        )
        bind_times.append(time.perf_counter() - t0)

    # Raw baseline: import + lookup time per call.
    raw_times = []
    for _ in range(n):
        t0 = time.perf_counter()
        mod = importlib.import_module("techne.lib.mahler_measure")
        _ = mod.mahler_measure
        raw_times.append(time.perf_counter() - t0)

    return {
        "n": n,
        "bind_p50_ms": 1000 * _percentile(bind_times, 50),
        "bind_p95_ms": 1000 * _percentile(bind_times, 95),
        "raw_p50_ms": 1000 * _percentile(raw_times, 50),
        "overhead_p50_ms": 1000 * (_percentile(bind_times, 50) - _percentile(raw_times, 50)),
    }


def _bench_eval(n: int = 200, ext_factory=BindEvalExtension) -> dict:
    """How long does EVAL take per call vs raw callable invocation?

    ``ext_factory`` selects v1 vs v2 (see ``_bench_bind``).
    """
    kernel = SigmaKernel(":memory:")
    ext = ext_factory(kernel)
    ref = "techne.lib.mahler_measure:mahler_measure"
    cap = kernel.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=ref,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )

    # Raw baseline.
    from techne.lib.mahler_measure import mahler_measure

    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]

    raw_times = []
    for _ in range(n):
        t0 = time.perf_counter()
        _ = mahler_measure(lehmer)
        raw_times.append(time.perf_counter() - t0)

    eval_times = []
    for i in range(n):
        c = kernel.mint_capability("EvalCap")
        t0 = time.perf_counter()
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[lehmer],
            cap=c,
            eval_version=i + 1,
        )
        eval_times.append(time.perf_counter() - t0)

    return {
        "n": n,
        "eval_p50_ms": 1000 * _percentile(eval_times, 50),
        "eval_p95_ms": 1000 * _percentile(eval_times, 95),
        "raw_p50_ms": 1000 * _percentile(raw_times, 50),
        "overhead_p50_ms": 1000 * (_percentile(eval_times, 50) - _percentile(raw_times, 50)),
    }


def _bench_substrate_growth(n: int = 200) -> dict:
    """How many rows per EVAL? Measures pollution risk."""
    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    ref = "techne.lib.mahler_measure:mahler_measure"
    cap = kernel.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref=ref,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]

    for i in range(n):
        c = kernel.mint_capability("EvalCap")
        ext.EVAL(
            binding_name=b.symbol.name,
            binding_version=b.symbol.version,
            args=[lehmer],
            cap=c,
            eval_version=i + 1,
        )

    n_symbols = kernel.conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    n_evals = kernel.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    n_caps = kernel.conn.execute(
        "SELECT COUNT(*) FROM capabilities"
    ).fetchone()[0]
    return {
        "n_evals_run": n,
        "rows_symbols": n_symbols,
        "rows_evaluations": n_evals,
        "rows_capabilities": n_caps,
        "rows_per_eval": (n_symbols + n_evals + n_caps) / max(n, 1),
    }


def _bench_cost_accuracy() -> dict:
    """Run each registered arsenal op once with curated representative
    args. Compare declared ``cost_model.max_seconds`` against actual
    elapsed; aggregate ratio statistics so we can see how many ops sit
    inside the 2x-50x calibration band.

    Ops without curated args are skipped (not counted as overshoots).
    """
    from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
    # Reuse the test-suite's representative-args dict so the bench and
    # the calibration test agree on inputs.
    from prometheus_math.tests.test_arsenal_metadata import REPRESENTATIVE_ARGS

    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    rows = []
    for ref, meta in ARSENAL_REGISTRY.items():
        if ref not in REPRESENTATIVE_ARGS:
            continue
        args, kwargs = REPRESENTATIVE_ARGS[ref]
        cm = CostModel(**meta.cost) if meta.cost else CostModel()
        try:
            cap = kernel.mint_capability("BindCap")
            b = ext.BIND(
                callable_ref=ref,
                cost_model=cm,
                cap=cap,
                name=f"bench_{ref.split(':')[-1].replace('.', '_')}",
                version=1,
            )
            cap2 = kernel.mint_capability("EvalCap")
            ev = ext.EVAL(
                binding_name=b.symbol.name,
                binding_version=b.symbol.version,
                args=list(args),
                kwargs=dict(kwargs),
                cap=cap2,
            )
            actual = ev.actual_cost["elapsed_seconds"]
            declared = cm.max_seconds
            ratio_declared_over_actual = (
                declared / max(actual, 1e-7) if declared > 0 else float("nan")
            )
            rows.append(
                {
                    "ref": ref.split(":")[-1],
                    "category": meta.category or "unknown",
                    "declared_max_s": declared,
                    "actual_s": actual,
                    "ratio_declared_over_actual": ratio_declared_over_actual,
                    "success": ev.success,
                }
            )
        except Exception as e:
            rows.append(
                {
                    "ref": ref.split(":")[-1],
                    "category": meta.category or "unknown",
                    "declared_max_s": cm.max_seconds,
                    "actual_s": float("nan"),
                    "ratio_declared_over_actual": float("nan"),
                    "success": False,
                    "error": str(e)[:120],
                }
            )

    n_ops = len(rows)
    n_success = sum(1 for r in rows if r["success"])
    n_within_2x = sum(
        1 for r in rows
        if r["success"] and 2.0 <= r["ratio_declared_over_actual"] <= 50.0
    )
    n_within_10x = sum(
        1 for r in rows
        if r["success"] and 1.0 <= r["ratio_declared_over_actual"] <= 100.0
    )
    n_overshoots = sum(
        1 for r in rows
        if r["success"] and r["ratio_declared_over_actual"] < 1.0
    )
    n_too_loose = sum(
        1 for r in rows
        if r["success"] and r["ratio_declared_over_actual"] > 50.0
    )
    return {
        "per_op": rows,
        "summary": {
            "n_ops": n_ops,
            "n_success": n_success,
            "n_within_2x_50x_band": n_within_2x,
            "n_within_1x_100x_band": n_within_10x,
            "n_overshoots": n_overshoots,
            "n_too_loose_over_50x": n_too_loose,
        },
    }


def main() -> int:
    print("=" * 72)
    print("BIND/EVAL benchmarks — sigma_kernel MVP perf check (v1 vs v2)")
    print("=" * 72)

    print("\n[1] BIND overhead (n=200) -- v1 (BindEvalExtension)")
    r1 = _bench_bind(200, ext_factory=BindEvalExtension)
    print(f"  v1 bind p50:    {r1['bind_p50_ms']:7.3f} ms")
    print(f"  v1 bind p95:    {r1['bind_p95_ms']:7.3f} ms")
    print(f"  raw import p50: {r1['raw_p50_ms']:7.3f} ms")
    print(f"  overhead p50:   {r1['overhead_p50_ms']:7.3f} ms")

    print("\n[1b] BIND overhead (n=200) -- v2 (BindEvalKernelV2)")
    r1v2 = _bench_bind(200, ext_factory=BindEvalKernelV2)
    print(f"  v2 bind p50:    {r1v2['bind_p50_ms']:7.3f} ms")
    print(f"  v2 bind p95:    {r1v2['bind_p95_ms']:7.3f} ms")
    print(f"  v2 overhead p50:{r1v2['overhead_p50_ms']:7.3f} ms")
    pass1 = r1["bind_p50_ms"] < 50.0 and r1v2["bind_p50_ms"] < 50.0
    print(f"  claim v1+v2 < 50ms p50:  {'PASS' if pass1 else 'FAIL'}")
    print(
        f"  v2/v1 ratio: {r1v2['bind_p50_ms'] / max(r1['bind_p50_ms'], 1e-6):.2f}x"
    )

    print("\n[2] EVAL overhead per call (n=200) -- v1")
    r2 = _bench_eval(200, ext_factory=BindEvalExtension)
    print(f"  v1 eval p50:    {r2['eval_p50_ms']:7.3f} ms")
    print(f"  v1 eval p95:    {r2['eval_p95_ms']:7.3f} ms")
    print(f"  raw call p50:   {r2['raw_p50_ms']:7.3f} ms")
    print(f"  overhead p50:   {r2['overhead_p50_ms']:7.3f} ms")

    print("\n[2b] EVAL overhead per call (n=200) -- v2")
    r2v2 = _bench_eval(200, ext_factory=BindEvalKernelV2)
    print(f"  v2 eval p50:    {r2v2['eval_p50_ms']:7.3f} ms")
    print(f"  v2 eval p95:    {r2v2['eval_p95_ms']:7.3f} ms")
    print(f"  v2 overhead p50:{r2v2['overhead_p50_ms']:7.3f} ms")
    pass2 = r2["eval_p50_ms"] < 50.0 and r2v2["eval_p50_ms"] < 50.0
    print(f"  claim v1+v2 < 50ms p50:  {'PASS' if pass2 else 'FAIL'}")
    print(
        f"  v2/v1 ratio: {r2v2['eval_p50_ms'] / max(r2['eval_p50_ms'], 1e-6):.2f}x"
    )

    print("\n[3] Substrate growth (n=200 evals)")
    r = _bench_substrate_growth(200)
    print(f"  symbols rows:        {r['rows_symbols']}")
    print(f"  evaluations rows:    {r['rows_evaluations']}")
    print(f"  capabilities rows:   {r['rows_capabilities']}")
    print(f"  rows-per-EVAL:       {r['rows_per_eval']:.2f}")
    pass3 = r["rows_per_eval"] < 5.0
    print(f"  claim <5/eval:       {'PASS' if pass3 else 'FAIL'}")

    print("\n[4] Cost-model accuracy across all registered ops with curated args")
    r = _bench_cost_accuracy()
    print(
        f"  {'op':<48} {'category':<18} "
        f"{'declared(ms)':>12} {'actual(ms)':>12} {'D/A':>8} {'ok':>5}"
    )
    for row in sorted(r["per_op"], key=lambda x: x.get("category", "")):
        ok = row["success"]
        ratio = row.get("ratio_declared_over_actual", float("nan"))
        ratio_str = f"{ratio:7.2f}x" if ratio == ratio else "    nan"
        print(
            f"  {row['ref'][:47]:<48} {row['category'][:17]:<18} "
            f"{row['declared_max_s']*1000:>12.3f} "
            f"{row['actual_s']*1000:>12.4f} {ratio_str:>8} "
            f"{'PASS' if ok else 'FAIL':>5}"
        )
    s = r["summary"]
    print(f"\n  summary: {s}")
    overshoot = s["n_overshoots"]
    pass4 = overshoot == 0
    print(f"  no overshoots:       {'PASS' if pass4 else f'FAIL ({overshoot})'}")

    print("\n" + "=" * 72)
    overall = pass1 and pass2 and pass3 and pass4
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
