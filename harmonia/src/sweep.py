"""
Parallel Sweep — Run TT-Cross explorations across all domain combinations concurrently.

Uses Python's concurrent.futures to run independent TT-Cross decompositions
in parallel. Each combination is fully independent — no shared state.
"""
import json
import time
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from harmonia.src.domain_index import DOMAIN_LOADERS


@dataclass
class SweepResult:
    """Result from one TT-Cross run in the sweep."""
    domains: list[str]
    domain_sizes: list[int]
    tt_ranks: list[int]
    bonds: list[dict]
    validated_bonds: list[dict]
    wall_time: float
    n_evals: int
    error: Optional[str] = None


def _run_single_exploration(domain_names, max_rank, eps, subsample, scorer, device='cpu'):
    """Worker function for parallel execution. Must be top-level for pickling."""
    try:
        from harmonia.src.engine import HarmoniaEngine
        from harmonia.src.validate import validate_bond

        engine = HarmoniaEngine(
            domains=list(domain_names),
            device=device,
            max_rank=max_rank,
            eps=eps,
            subsample=subsample,
            scorer=scorer,
        )

        tt, report = engine.explore()

        # Validate each bond
        validated = []
        for i in range(len(report.bonds)):
            vr = validate_bond(tt, i, engine._domain_list, run_battery=False)
            validated.append({
                "domain_a": vr.domain_a,
                "domain_b": vr.domain_b,
                "raw_rank": vr.raw_rank,
                "validated_rank": vr.validated_rank,
                "surviving_components": [
                    {"idx": c.component_idx, "sv": c.singular_value,
                     "energy": c.energy_fraction}
                    for c in vr.components if c.verdict == "SURVIVES"
                ],
                "killed_components": sum(
                    1 for c in vr.components if c.verdict == "KILLED"
                ),
            })

        return SweepResult(
            domains=list(domain_names),
            domain_sizes=report.domain_sizes,
            tt_ranks=report.tt_ranks,
            bonds=[asdict(b) for b in report.bonds],
            validated_bonds=validated,
            wall_time=report.wall_time_seconds,
            n_evals=report.n_function_evals,
        )
    except Exception as e:
        return SweepResult(
            domains=list(domain_names),
            domain_sizes=[],
            tt_ranks=[],
            bonds=[],
            validated_bonds=[],
            wall_time=0,
            n_evals=0,
            error=str(e),
        )


def sweep_pairs(
    domains: Optional[list[str]] = None,
    max_rank: int = 15,
    eps: float = 1e-3,
    subsample: Optional[int] = 2000,
    scorer: str = "distributional",
    max_workers: int = 4,
    device: str = "cpu",
) -> list[SweepResult]:
    """
    Run TT-Cross on all pairs of domains in parallel.

    Args:
        domains: Domain names to include. Default: all available.
        max_rank: Maximum TT bond dimension
        eps: Convergence threshold
        subsample: Subsample large domains for speed
        scorer: 'cosine' or 'distributional'
        max_workers: Number of parallel workers

    Returns:
        List of SweepResult for each domain pair
    """
    if domains is None:
        domains = list(DOMAIN_LOADERS.keys())

    pairs = list(combinations(domains, 2))
    print(f"Harmonia sweep: {len(pairs)} domain pairs, {max_workers} workers")

    results = []
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_single_exploration, pair, max_rank, eps, subsample, scorer, device
            ): pair
            for pair in pairs
        }

        for future in as_completed(futures):
            pair = futures[future]
            result = future.result()
            results.append(result)
            if result.error:
                print(f"  ERROR {result.domains}: {result.error}")
            else:
                bonds_summary = ", ".join(
                    f"{b['domain_a']}<->{b['domain_b']}=r{b['validated_rank']}"
                    for b in result.validated_bonds
                )
                print(f"  DONE {result.domains} ({result.wall_time:.2f}s): {bonds_summary}")

    total_time = time.time() - t0
    print(f"\nSweep complete: {len(results)} pairs in {total_time:.1f}s")
    return results


def sweep_triples(
    domains: Optional[list[str]] = None,
    max_rank: int = 15,
    eps: float = 1e-3,
    subsample: Optional[int] = 2000,
    scorer: str = "distributional",
    max_workers: int = 4,
    device: str = "cpu",
) -> list[SweepResult]:
    """Run TT-Cross on all triples of domains in parallel."""
    if domains is None:
        domains = list(DOMAIN_LOADERS.keys())

    triples = list(combinations(domains, 3))
    print(f"Harmonia sweep: {len(triples)} domain triples, {max_workers} workers")

    results = []
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_single_exploration, triple, max_rank, eps, subsample, scorer, device
            ): triple
            for triple in triples
        }

        for future in as_completed(futures):
            triple = futures[future]
            result = future.result()
            results.append(result)
            if result.error:
                print(f"  ERROR {result.domains}: {result.error}")
            else:
                bonds_summary = ", ".join(
                    f"{b['domain_a']}<->{b['domain_b']}=r{b['validated_rank']}"
                    for b in result.validated_bonds
                )
                print(f"  DONE {result.domains} ({result.wall_time:.2f}s): {bonds_summary}")

    total_time = time.time() - t0
    print(f"\nSweep complete: {len(results)} triples in {total_time:.1f}s")
    return results


def sweep_all(
    domains: Optional[list[str]] = None,
    max_rank: int = 15,
    eps: float = 1e-3,
    subsample: Optional[int] = 2000,
    scorer: str = "distributional",
    max_workers: int = 4,
    device: str = "cpu",
) -> list[SweepResult]:
    """Run pairs + triples + the full N-domain tensor."""
    if domains is None:
        domains = list(DOMAIN_LOADERS.keys())

    # Pairs, triples, and the full combination
    combos = []
    for r in range(2, len(domains) + 1):
        combos.extend(combinations(domains, r))

    print(f"Harmonia full sweep: {len(combos)} combinations across "
          f"{len(domains)} domains, {max_workers} workers")

    results = []
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_single_exploration, combo, max_rank, eps, subsample, scorer, device
            ): combo
            for combo in combos
        }

        for future in as_completed(futures):
            combo = futures[future]
            result = future.result()
            results.append(result)
            if result.error:
                print(f"  ERROR {list(combo)}: {result.error}")
            else:
                bonds_summary = ", ".join(
                    f"{b['domain_a']}<->{b['domain_b']}=r{b['validated_rank']}"
                    for b in result.validated_bonds
                )
                print(f"  DONE {list(combo)} ({result.wall_time:.2f}s): {bonds_summary}")

    total_time = time.time() - t0
    print(f"\nFull sweep complete: {len(results)} combinations in {total_time:.1f}s")
    return results


def save_sweep(results: list[SweepResult], path: Optional[Path] = None):
    """Save sweep results to JSON."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "results" / "sweep_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "n_combinations": len(results),
        "results": [asdict(r) for r in results],
        "summary": {
            "total_evals": sum(r.n_evals for r in results),
            "total_time": sum(r.wall_time for r in results),
            "errors": sum(1 for r in results if r.error),
            "nonzero_bonds": [
                {"domains": r.domains, "bond": b["domain_a"] + "<->" + b["domain_b"],
                 "validated_rank": b["validated_rank"]}
                for r in results
                for b in r.validated_bonds
                if b["validated_rank"] > 0
            ],
        },
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Sweep results saved to {path}")


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "pairs"
    subsample = int(sys.argv[2]) if len(sys.argv) > 2 else 2000

    if mode == "pairs":
        results = sweep_pairs(subsample=subsample)
    elif mode == "triples":
        results = sweep_triples(subsample=subsample)
    elif mode == "all":
        results = sweep_all(subsample=subsample)
    else:
        print(f"Usage: python sweep.py [pairs|triples|all] [subsample]")
        sys.exit(1)

    save_sweep(results)
