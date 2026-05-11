"""Tier-0 substrate generator: Lehmer palindromic deg-N coef-bound ±B.

Per `pivot/substrate_generation_pipeline_2026-05-11.md` Tier 0:
single-generator throughput baseline; in-memory SigmaKernel (no
production writes) by default.

Composes with the existing `prometheus_math.discovery_pipeline`
infrastructure: enumerates palindromic polynomial candidates,
computes Mahler measure, hands each to
`DiscoveryPipeline.process_candidate()`, collects the resulting
DiscoveryRecord (which contains a KillVector v2), and reports
throughput + quality distribution.

CLI
---
::

    # Smoke test (30 candidates, single-process, in-memory)
    python -m prometheus_math.substrate_generation.tier_0_lehmer_palindromic \\
        --max-candidates 30 \\
        --coef-bound 2 \\
        --out prometheus_math/substrate_generation/_tier_0_smoke_results.json

    # Baseline (1000 candidates; still in-memory unless --writeable)
    python -m prometheus_math.substrate_generation.tier_0_lehmer_palindromic \\
        --max-candidates 1000 \\
        --coef-bound 5 \\
        --out prometheus_math/substrate_generation/_tier_0_baseline_results.json

NOTE: production substrate writes require the `--writeable` flag (NOT
implemented in Tier 0 — Aporia must greenlight per the design doc).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from itertools import product
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Candidate enumerator
# ---------------------------------------------------------------------------


def enumerate_palindromic_candidates(
    degree: int = 12,
    coef_bound: int = 5,
    require_leading_one: bool = True,
) -> Iterator[List[int]]:
    """Yield palindromic deg-N coefficient tuples within bound ±coef_bound.

    A palindromic polynomial of degree N has c_i = c_{N-i} for all i,
    so the free parameters are (c_0, c_1, ..., c_{floor(N/2)}).
    Total candidate count: (2*coef_bound+1)^(floor(N/2)+1).

    Parameters
    ----------
    degree : int
        Polynomial degree. Default 12 (Lehmer-relevant region).
    coef_bound : int
        Each free coefficient ranges in [-coef_bound, coef_bound].
    require_leading_one : bool
        If True (default), only emit candidates with c_0 = 1
        (Lehmer convention; eliminates equivalent rescalings).
    """
    if degree < 2 or degree % 2 != 0:
        raise ValueError(f"degree must be even >= 2; got {degree}")
    half = degree // 2  # number of free interior coefficients
    # Free parameters: (c_0, c_1, ..., c_half). c_half is the middle
    # coefficient (its own palindromic partner). c_{half+i} = c_{half-i}.
    if require_leading_one:
        c0_range = (1,)
    else:
        c0_range = tuple(range(-coef_bound, coef_bound + 1))
    interior_range = tuple(range(-coef_bound, coef_bound + 1))
    for free in product(c0_range, *([interior_range] * half)):
        # Rebuild full coefficient tuple [c_0, c_1, ..., c_N]
        coeffs = list(free)  # c_0 .. c_half
        # Mirror: c_{half+1}..c_N = reversed(c_0..c_{half-1})
        coeffs.extend(reversed(free[:half]))
        yield coeffs


# ---------------------------------------------------------------------------
# Mahler measure (lightweight)
# ---------------------------------------------------------------------------


def compute_mahler_measure(coeffs: List[int], dps: int = 60) -> Optional[float]:
    """Compute Mahler measure of a polynomial via mpmath polyroots.

    Returns None on numerical failure (not a substrate-grade evaluator;
    Tier-0's purpose is throughput baselining, not high-precision
    Mahler measurement). Production-grade callers should use
    `prometheus_math._lehmer_brute_force_path_b.mahler_measure_high_precision`
    via sympy factorization.
    """
    try:
        import mpmath
    except ImportError:
        return None
    try:
        # mpmath.polyroots expects coefficients high-degree-first
        mpmath.mp.dps = dps
        roots = mpmath.polyroots(list(coeffs), maxsteps=100)
        # M(p) = |c_lead| * prod over roots r: max(1, |r|)
        c_lead = abs(coeffs[0]) if coeffs[0] != 0 else 1
        M = mpmath.mpf(c_lead)
        for r in roots:
            mag = abs(r)
            if mag > 1:
                M *= mag
        return float(M)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Quality scoring (Tier-0 minimal: just classify outcome shape)
# ---------------------------------------------------------------------------


@dataclass
class CandidateOutcome:
    """Per-candidate outcome summary captured by the Tier-0 generator."""

    coeffs: Tuple[int, ...]
    mahler_measure: Optional[float]
    terminal_state: str  # SURVIVED / REJECTED / out_of_band / etc.
    kill_pattern: Optional[str]
    n_components_triggered: int
    n_components_total: int
    near_miss: bool  # any |margin| in (0, 0.05) on a triggered component
    catalog_disagreement: bool  # F-gates and catalog disagree
    elapsed_s: float


def _classify_outcome(record: Any, elapsed_s: float) -> CandidateOutcome:
    """Convert a DiscoveryRecord into a Tier-0 CandidateOutcome."""
    kv = getattr(record, "kill_vector", None)
    components = list(kv.components) if kv is not None else []
    n_total = len(components)
    triggered = [c for c in components if c.triggered]
    n_triggered = len(triggered)
    # Near-miss: any triggered component with small absolute margin
    near_miss = any(
        c.margin is not None and 0.0 < abs(c.margin) < 0.05
        for c in triggered
    )
    # Catalog disagreement: a catalog: prefix component triggered AND
    # at least one F-gate did NOT trigger
    catalog_triggered = any(
        c.triggered and c.falsifier_name.startswith("catalog:")
        for c in components
    )
    f_gate_survived = any(
        not c.triggered and c.falsifier_name in ("F1_permutation_null",
                                                  "F6_base_rate",
                                                  "F9_simpler_explanation",
                                                  "F11_cross_validation")
        for c in components
    )
    catalog_disagreement = catalog_triggered and f_gate_survived
    return CandidateOutcome(
        coeffs=tuple(record.coeffs),
        mahler_measure=record.mahler_measure,
        terminal_state=record.terminal_state,
        kill_pattern=record.kill_pattern,
        n_components_triggered=n_triggered,
        n_components_total=n_total,
        near_miss=near_miss,
        catalog_disagreement=catalog_disagreement,
        elapsed_s=elapsed_s,
    )


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


@dataclass
class Tier0Run:
    n_enumerated: int = 0
    n_processed: int = 0
    n_skipped_no_mahler: int = 0
    n_skipped_out_of_band: int = 0
    elapsed_total_s: float = 0.0
    outcomes: List[CandidateOutcome] = field(default_factory=list)

    @property
    def records_per_hour(self) -> float:
        if self.elapsed_total_s <= 0:
            return 0.0
        return (self.n_processed / self.elapsed_total_s) * 3600.0

    @property
    def near_miss_rate(self) -> float:
        if self.n_processed == 0:
            return 0.0
        return sum(1 for o in self.outcomes if o.near_miss) / self.n_processed

    @property
    def catalog_disagreement_rate(self) -> float:
        if self.n_processed == 0:
            return 0.0
        return sum(1 for o in self.outcomes if o.catalog_disagreement) / self.n_processed

    @property
    def survived_count(self) -> int:
        return sum(1 for o in self.outcomes if o.terminal_state == "PROMOTED"
                   or o.terminal_state == "SURVIVED")

    def kill_pattern_distribution(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for o in self.outcomes:
            key = o.kill_pattern or "(survived)"
            out[key] = out.get(key, 0) + 1
        return out

    def to_summary(self) -> Dict[str, Any]:
        return {
            "n_enumerated": self.n_enumerated,
            "n_processed": self.n_processed,
            "n_skipped_no_mahler": self.n_skipped_no_mahler,
            "n_skipped_out_of_band": self.n_skipped_out_of_band,
            "elapsed_total_s": round(self.elapsed_total_s, 3),
            "records_per_hour": round(self.records_per_hour, 1),
            "near_miss_rate": round(self.near_miss_rate, 4),
            "catalog_disagreement_rate": round(self.catalog_disagreement_rate, 4),
            "survived_count": self.survived_count,
            "kill_pattern_distribution_top": dict(
                sorted(self.kill_pattern_distribution().items(),
                       key=lambda kv: -kv[1])[:8]
            ),
        }


def run_tier_0(
    *,
    degree: int = 12,
    coef_bound: int = 5,
    max_candidates: int = 30,
    skip_out_of_band_early: bool = True,
    writeable: bool = False,
) -> Tier0Run:
    """Run Tier-0 generator end-to-end.

    Parameters
    ----------
    degree, coef_bound : int
        Enumeration parameters. Default deg-12 ±5 (Lehmer-relevant).
    max_candidates : int
        Stop after this many candidates. Tier-0 default 30 (smoke test);
        Tier-0 baseline run uses 1000-10000.
    skip_out_of_band_early : bool
        If True, drop candidates with Mahler measure outside (1.001, 1.18)
        BEFORE handing to DiscoveryPipeline (which would otherwise emit a
        REJECTED record with kill_pattern="out_of_band:..."). For
        throughput baselining we want to measure in-band probe cost.
    writeable : bool
        If True, write to production substrate. **Tier 0 does NOT
        support this** — Aporia greenlight required (see design doc).
    """
    if writeable:
        raise NotImplementedError(
            "Tier-0 production substrate writes require Aporia greenlight "
            "per pivot/substrate_generation_pipeline_2026-05-11.md. "
            "Run with writeable=False (default) for in-memory-only mode."
        )

    # Lazy import to keep enumerator standalone-importable
    from sigma_kernel.bind_eval import BindEvalExtension
    from sigma_kernel.sigma_kernel import SigmaKernel
    from prometheus_math.discovery_pipeline import DiscoveryPipeline

    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    pipeline = DiscoveryPipeline(kernel=kernel, ext=ext)

    run = Tier0Run()
    t_start = time.perf_counter()
    try:
        for coeffs in enumerate_palindromic_candidates(
            degree=degree, coef_bound=coef_bound,
        ):
            if run.n_processed >= max_candidates:
                break
            run.n_enumerated += 1
            mm = compute_mahler_measure(coeffs)
            if mm is None:
                run.n_skipped_no_mahler += 1
                continue
            if skip_out_of_band_early and not (1.001 < mm < 1.18):
                run.n_skipped_out_of_band += 1
                continue
            t_one = time.perf_counter()
            try:
                record = pipeline.process_candidate(coeffs, mm)
            except Exception as exc:  # noqa: BLE001
                # Capture failure as outcome (substrate-grade: the failure
                # IS the output; we record + continue rather than crash)
                run.n_processed += 1
                run.outcomes.append(CandidateOutcome(
                    coeffs=tuple(coeffs), mahler_measure=mm,
                    terminal_state="ERROR", kill_pattern=f"error:{type(exc).__name__}",
                    n_components_triggered=0, n_components_total=0,
                    near_miss=False, catalog_disagreement=False,
                    elapsed_s=time.perf_counter() - t_one,
                ))
                continue
            run.n_processed += 1
            run.outcomes.append(_classify_outcome(record, time.perf_counter() - t_one))
    finally:
        kernel.close()
    run.elapsed_total_s = time.perf_counter() - t_start
    return run


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="tier_0_lehmer_palindromic",
        description=(
            "Tier-0 substrate generator (Lehmer palindromic). "
            "Default in-memory; --writeable requires Aporia greenlight."
        ),
    )
    p.add_argument("--degree", type=int, default=12)
    p.add_argument("--coef-bound", type=int, default=5)
    p.add_argument("--max-candidates", type=int, default=30)
    p.add_argument("--out", type=str, default=None,
                   help="Write summary JSON to this path (default: stdout)")
    p.add_argument("--writeable", action="store_true",
                   help="Production substrate writes (REQUIRES APORIA GREENLIGHT)")
    args = p.parse_args(argv)

    run = run_tier_0(
        degree=args.degree,
        coef_bound=args.coef_bound,
        max_candidates=args.max_candidates,
        writeable=args.writeable,
    )
    summary = run.to_summary()
    summary["run_args"] = vars(args)
    payload = json.dumps(summary, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(payload)
    print(f"\nTier-0 throughput: {summary['records_per_hour']:.1f} records/hour "
          f"on {summary['n_processed']} candidates "
          f"({summary['elapsed_total_s']:.2f}s wall-clock)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
