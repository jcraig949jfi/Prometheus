"""
Landscape Explorer — MAP-Elites style exploration of tensor space.

Generates random domain subsets, feature subsets, and scorer configurations.
Runs TT-Cross + battery on each. Builds a landscape of what structure
exists where. Everything is disposable — only battery verdicts persist.

Also includes known-truth calibration: run the tensor framework against
mathematically proven relationships to measure false-positive/negative rates.
"""
import torch
import numpy as np
import json
import time
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from harmonia.src.domain_index import DomainIndex, DOMAIN_LOADERS, load_domains
from harmonia.src.engine import HarmoniaEngine
from harmonia.src.validate import validate_bond, extract_bond_components
from harmonia.src.tensor_falsify import falsify_bond, FalsificationReport


# ── Known truths for calibration ──────────────────────────────────────

KNOWN_TRUTHS = [
    {
        "d1": "modular_forms", "d2": "dirichlet_zeros",
        "claim": "Level of modular form ~ conductor of L-function (modularity theorem)",
        "expected": "SURVIVES",
        "features": {"d1": "log_level", "d2": "log_conductor"},
    },
    {
        "d1": "modular_forms", "d2": "elliptic_curves",
        "claim": "Modular forms of weight 2 correspond to elliptic curves (Wiles/Taylor)",
        "expected": "SURVIVES",
        "features": {"d1": "weight", "d2": "conductor"},
    },
    {
        "d1": "elliptic_curves", "d2": "dirichlet_zeros",
        "claim": "EC conductor = L-function conductor (by definition)",
        "expected": "SURVIVES",
        "features": {"d1": "log_conductor", "d2": "log_conductor"},
    },
    {
        "d1": "number_fields", "d2": "lattices",
        "claim": "Number field discriminant ~ lattice determinant for ring of integers",
        "expected": "SURVIVES",
        "features": {"d1": "log_disc_abs", "d2": "log_determinant"},
    },
    {
        "d1": "space_groups", "d2": "materials",
        "claim": "Space group constrains material properties (crystal physics)",
        "expected": "SURVIVES",
        "features": {"d1": "crystal_system", "d2": "band_gap"},
    },
]

KNOWN_FALSEHOODS = [
    {
        "d1": "knots", "d2": "materials",
        "claim": "Knot invariants predict material band gaps (no known relationship)",
        "expected": "KILLED",
    },
    {
        "d1": "knots", "d2": "modular_forms",
        "claim": "Knot polynomials ~ modular form coefficients (no known relationship)",
        "expected": "KILLED",
    },
    {
        "d1": "fungrim", "d2": "polytopes",
        "claim": "Formula syntax predicts polytope geometry (no known relationship)",
        "expected": "KILLED",
    },
]


@dataclass
class CalibrationResult:
    claim: str
    expected: str
    actual: str
    correct: bool
    score: int  # out of 5
    details: str


def calibrate(subsample: int = 2000) -> dict:
    """
    Run known truths and known falsehoods through the tensor battery.
    Returns calibration metrics: sensitivity, specificity, accuracy.
    """
    print("CALIBRATION: Known truths")
    print("=" * 50)

    results = []

    for truth in KNOWN_TRUTHS:
        report = falsify_bond(truth["d1"], truth["d2"], subsample=subsample,
                              inference=truth["claim"])
        actual = "SURVIVES" if report.surviving_rank > 0 else "KILLED"
        correct = actual == truth["expected"]
        results.append(CalibrationResult(
            claim=truth["claim"], expected=truth["expected"], actual=actual,
            correct=correct, score=sum(1 for t in report.tests if t.verdict == "SURVIVES"),
            details=f"rank {report.original_rank}->{report.surviving_rank}, "
                    f"{report.wall_time:.1f}s"
        ))
        icon = "OK" if correct else "!!"
        print(f"  [{icon}] {truth['claim'][:60]}: {actual} ({results[-1].score}/5)")

    print("\nCALIBRATION: Known falsehoods")
    print("=" * 50)

    for false in KNOWN_FALSEHOODS:
        report = falsify_bond(false["d1"], false["d2"], subsample=subsample,
                              inference=false["claim"])
        actual = "SURVIVES" if report.surviving_rank > 0 else "KILLED"
        correct = actual == false["expected"]
        results.append(CalibrationResult(
            claim=false["claim"], expected=false["expected"], actual=actual,
            correct=correct, score=sum(1 for t in report.tests if t.verdict == "SURVIVES"),
            details=f"rank {report.original_rank}->{report.surviving_rank}, "
                    f"{report.wall_time:.1f}s"
        ))
        icon = "OK" if correct else "!!"
        print(f"  [{icon}] {false['claim'][:60]}: {actual} ({results[-1].score}/5)")

    # Metrics
    truths = [r for r in results if r.expected == "SURVIVES"]
    falses = [r for r in results if r.expected == "KILLED"]
    tp = sum(1 for r in truths if r.actual == "SURVIVES")
    fn = sum(1 for r in truths if r.actual == "KILLED")
    tn = sum(1 for r in falses if r.actual == "KILLED")
    fp = sum(1 for r in falses if r.actual == "SURVIVES")

    sensitivity = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    accuracy = (tp + tn) / max(len(results), 1)

    metrics = {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "accuracy": accuracy,
        "tp": tp, "fn": fn, "tn": tn, "fp": fp,
        "results": [asdict(r) for r in results],
    }

    print(f"\n  Sensitivity: {sensitivity:.0%} ({tp}/{tp+fn} truths detected)")
    print(f"  Specificity: {specificity:.0%} ({tn}/{tn+fp} falsehoods rejected)")
    print(f"  Accuracy:    {accuracy:.0%}")

    return metrics


# ── MAP-Elites Landscape Explorer ─────────────────────────────────────

@dataclass
class LandscapeCell:
    """One cell in the MAP-Elites grid."""
    domains: tuple
    scorer: str
    subsample: int
    max_rank: int
    # Results
    bond_dims: list[int] = field(default_factory=list)
    max_validated_rank: int = 0
    n_tests_passed: int = 0
    wall_time: float = 0.0
    inference: str = ""


class LandscapeExplorer:
    """
    MAP-Elites style exploration of the cross-domain tensor space.

    Grid dimensions:
    - domain_pair (or triple/quad): which domains to combine
    - scorer: which coupling function to use
    - subsample: resolution (more objects = slower but more precise)

    Fitness: battery pass rate (0-5)
    Genome: (domains, scorer, subsample, max_rank)

    Everything is disposable. Only the landscape (battery verdicts) persists.
    """

    SCORERS = ["cosine", "distributional", "alignment"]
    SUBSAMPLES = [500, 1000, 2000]
    MAX_RANKS = [5, 10, 15]

    def __init__(self, domains: Optional[list[str]] = None, max_order: int = 3):
        self.dead = {"knots", "maass"}
        if domains is None:
            domains = [d for d in DOMAIN_LOADERS.keys() if d not in self.dead]
        self.domains = domains
        self.max_order = max_order
        self.grid: dict[tuple, LandscapeCell] = {}

    def _random_genome(self) -> dict:
        """Generate a random exploration configuration."""
        order = np.random.randint(2, self.max_order + 1)
        doms = tuple(sorted(np.random.choice(self.domains, order, replace=False)))
        scorer = np.random.choice(self.SCORERS)
        subsample = np.random.choice(self.SUBSAMPLES)
        max_rank = np.random.choice(self.MAX_RANKS)
        return {"domains": doms, "scorer": scorer, "subsample": subsample,
                "max_rank": max_rank}

    def _evaluate(self, genome: dict) -> LandscapeCell:
        """Evaluate one genome: run TT-Cross + heuristic validation."""
        doms = genome["domains"]
        try:
            engine = HarmoniaEngine(
                domains=list(doms), device="cpu",
                max_rank=genome["max_rank"], eps=1e-3,
                subsample=genome["subsample"],
                scorer=genome["scorer"],
            )
            tt, report = engine.explore()

            bond_dims = []
            max_vr = 0
            for i in range(len(report.bonds)):
                vr = validate_bond(tt, i, engine._domain_list, run_battery=False)
                bond_dims.append(vr.validated_rank)
                max_vr = max(max_vr, vr.validated_rank)

            return LandscapeCell(
                domains=doms, scorer=genome["scorer"],
                subsample=genome["subsample"], max_rank=genome["max_rank"],
                bond_dims=bond_dims, max_validated_rank=max_vr,
                wall_time=report.wall_time_seconds,
            )
        except Exception as e:
            return LandscapeCell(
                domains=doms, scorer=genome["scorer"],
                subsample=genome["subsample"], max_rank=genome["max_rank"],
                wall_time=0, inference=f"ERROR: {e}",
            )

    def explore(self, n_iterations: int = 100, n_workers: int = 8) -> dict:
        """
        Run MAP-Elites exploration.

        Returns landscape summary with best cells per domain combo.
        """
        print(f"MAP-Elites: {n_iterations} iterations, {len(self.domains)} domains, "
              f"max order {self.max_order}")

        t0 = time.time()
        n_done = 0

        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            # Submit all at once
            genomes = [self._random_genome() for _ in range(n_iterations)]
            futs = {ex.submit(self._evaluate, g): g for g in genomes}

            for f in as_completed(futs):
                cell = f.result()
                n_done += 1
                key = cell.domains

                # MAP-Elites: keep best cell per domain combo
                if key not in self.grid or cell.max_validated_rank > self.grid[key].max_validated_rank:
                    self.grid[key] = cell

                if n_done % 20 == 0:
                    elapsed = time.time() - t0
                    print(f"  [{n_done}/{n_iterations}] {elapsed:.0f}s, "
                          f"{len(self.grid)} unique cells")

        total = time.time() - t0
        print(f"\nDone: {n_iterations} evals in {total:.1f}s, "
              f"{len(self.grid)} unique domain combos explored")

        return self._summarize()

    def _summarize(self) -> dict:
        """Summarize the landscape."""
        cells = sorted(self.grid.values(), key=lambda c: -c.max_validated_rank)

        # Top discoveries
        top = [asdict(c) for c in cells[:20]]

        # By scorer
        by_scorer = {}
        for c in cells:
            by_scorer.setdefault(c.scorer, []).append(c.max_validated_rank)
        scorer_stats = {s: {"mean": np.mean(v), "max": max(v), "n": len(v)}
                        for s, v in by_scorer.items()}

        # By order
        by_order = {}
        for c in cells:
            by_order.setdefault(len(c.domains), []).append(c.max_validated_rank)
        order_stats = {o: {"mean": np.mean(v), "max": max(v), "n": len(v)}
                       for o, v in by_order.items()}

        # Heatmap data: domain -> avg max rank when included
        domain_scores = {d: [] for d in self.domains}
        for c in cells:
            for d in c.domains:
                domain_scores[d].append(c.max_validated_rank)
        domain_heat = {d: {"mean": np.mean(v), "n": len(v)}
                       for d, v in domain_scores.items() if v}

        summary = {
            "n_cells": len(self.grid),
            "top_20": top,
            "scorer_stats": scorer_stats,
            "order_stats": order_stats,
            "domain_heatmap": domain_heat,
        }

        print("\nTop 10 discoveries:")
        for c in cells[:10]:
            print(f"  {'+'.join(d[:5] for d in c.domains):>35} "
                  f"[{c.scorer[:5]}] rank={c.max_validated_rank} "
                  f"bonds={c.bond_dims}")

        print(f"\nScorer comparison:")
        for s, stats in sorted(scorer_stats.items()):
            print(f"  {s:>15}: mean={stats['mean']:.1f}, max={stats['max']}, n={stats['n']}")

        print(f"\nOrder effect:")
        for o, stats in sorted(order_stats.items()):
            print(f"  {o}-tuples: mean={stats['mean']:.1f}, max={stats['max']}, n={stats['n']}")

        print(f"\nDomain heatmap (avg rank when included):")
        for d, stats in sorted(domain_heat.items(), key=lambda x: -x[1]["mean"]):
            print(f"  {d:>18}: {stats['mean']:.1f} (n={stats['n']})")

        return summary


def run_landscape(n_iterations=200, max_order=3, save=True):
    """One-liner to run a landscape exploration and save results."""
    explorer = LandscapeExplorer(max_order=max_order)
    summary = explorer.explore(n_iterations=n_iterations)

    if save:
        path = Path(__file__).resolve().parent.parent / "results" / "landscape.json"
        with open(path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\nSaved to {path}")

    return summary
