#!/usr/bin/env python3
"""
Harmonia Bridge — Sends Ergon MAP-Elites survivors into Harmonia's large tensor.

Two-stage scoring pipeline:
  Stage 1 (Ergon): Cheap evolutionary search, 57 hyp/sec, small tensor, kills 99.9%
  Stage 2 (Harmonia): Deep TT-Cross analysis on surviving domain pairs,
                       ungated exploration first, then falsification battery

Usage:
    # After an Ergon run:
    python harmonia_bridge.py results/archive_YYYYMMDD_HHMMSS.json

    # Or from Python:
    from harmonia_bridge import promote_to_harmonia
    results = promote_to_harmonia(archive, top_k=10)
"""
import sys
import json
import time
import argparse
from pathlib import Path
from collections import Counter, defaultdict

_root = Path(__file__).resolve().parent.parent  # Prometheus/
_forge_v3 = str(_root / "forge/v3")
_harmonia = str(_root)  # harmonia is imported as harmonia.src.*
if _forge_v3 not in sys.path:
    sys.path.insert(0, _forge_v3)
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
sys.path.insert(0, str(Path(__file__).parent))

from gene_schema import Hypothesis
from archive import Archive

# Domain name mapping: Ergon -> Harmonia
# Ergon uses gene_schema names, Harmonia uses its own registry names
DOMAIN_MAP = {
    "elliptic_curves": "elliptic_curves",
    "modular_forms": "modular_forms",
    "number_fields": "number_fields",
    "genus2_curves": "genus2",
    "maass_forms": "maass",
    "knots": "knots",
    "superconductors": "materials",  # closest match — Harmonia has materials not superconductors
    "lattices": "lattices",
    "isogenies": None,  # no Harmonia equivalent
    "oeis": "oeis",
    "polytopes": "polytopes",
    "space_groups": "space_groups",
    "dirichlet_zeros": "dirichlet_zeros",
    "ec_zeros": "ec_zeros",
    "materials": "materials",
    "chemistry_qm9": "chemistry",
    "metabolism": "metabolism",
}


def extract_domain_pairs(archive):
    """Extract domain pairs from Ergon archive, ranked by best survival depth and count.

    Returns list of:
        (domain_a, domain_b, best_depth, best_z, n_survivors, best_hypothesis)
    sorted by best_depth desc, then n_survivors desc.
    """
    pair_stats = defaultdict(lambda: {"best_depth": 0, "best_z": 0, "count": 0, "best_hyp": None})

    for cell_key, hyp in archive.grid.items():
        pair = tuple(sorted([hyp.domain_a, hyp.domain_b]))
        stats = pair_stats[pair]
        stats["count"] += 1
        if hyp.survival_depth > stats["best_depth"]:
            stats["best_depth"] = hyp.survival_depth
            stats["best_z"] = hyp.fitness
            stats["best_hyp"] = hyp
        elif hyp.survival_depth == stats["best_depth"] and abs(hyp.fitness) > abs(stats["best_z"]):
            stats["best_z"] = hyp.fitness
            stats["best_hyp"] = hyp

    results = []
    for (da, db), stats in pair_stats.items():
        results.append((da, db, stats["best_depth"], stats["best_z"], stats["count"], stats["best_hyp"]))

    results.sort(key=lambda x: (-x[2], -x[4], -abs(x[3])))
    return results


def map_to_harmonia(ergon_domain):
    """Map Ergon domain name to Harmonia domain name. Returns None if no mapping."""
    return DOMAIN_MAP.get(ergon_domain)


def promote_to_harmonia(archive, top_k=10, subsample=2000, max_rank=15, skip_battery=False):
    """Take Ergon archive survivors and run them through Harmonia's deep tensor.

    Stage 1: Ungated TT-Cross exploration (find bond dimensions)
    Stage 2: Falsification battery (only if bond_dim > 0 and not skip_battery)

    Args:
        archive: Ergon Archive object with populated grid
        top_k: How many domain pairs to promote
        subsample: Subsample size for Harmonia domains
        max_rank: Max TT bond dimension
        skip_battery: If True, only do ungated exploration (no falsification)

    Returns:
        List of result dicts with exploration and falsification reports
    """
    # Late imports — these are heavy (torch, tntorch)
    from harmonia.src.engine import HarmoniaEngine
    from harmonia.src.tensor_falsify import falsify_bond

    pairs = extract_domain_pairs(archive)

    if not pairs:
        print("No survivors in archive to promote.")
        return []

    print("=" * 80)
    print(f"HARMONIA BRIDGE — Promoting top {min(top_k, len(pairs))} domain pairs")
    print("=" * 80)
    print(f"\nErgon archive: {len(archive.grid)} cells filled")
    print(f"Domain pairs with survivors: {len(pairs)}")
    print()

    # Show the candidates
    print("Candidates (from Ergon):")
    for i, (da, db, depth, z, count, hyp) in enumerate(pairs[:top_k]):
        ha = map_to_harmonia(da)
        hb = map_to_harmonia(db)
        status = "OK" if (ha and hb) else "SKIP (no Harmonia mapping)"
        print(f"  {i+1}. {da} x {db} | depth={depth}, z={z:+.1f}, cells={count} | -> {status}")
    print()

    results = []
    for da, db, depth, z, count, hyp in pairs[:top_k]:
        ha = map_to_harmonia(da)
        hb = map_to_harmonia(db)

        if not ha or not hb:
            print(f"SKIP: {da} x {db} — no Harmonia domain mapping")
            results.append({
                "ergon_pair": (da, db),
                "harmonia_pair": None,
                "status": "skipped",
                "reason": "no Harmonia domain mapping",
            })
            continue

        if ha == hb:
            # Same domain — Harmonia needs at least 2 distinct domains for TT-Cross
            # Still useful: run as single-domain self-analysis
            print(f"\n--- {ha} (self-pair from {da} x {db}) ---")
            print(f"  Ergon: depth={depth}, z={z:+.1f}")
            print(f"  Skipping TT-Cross (same domain), running falsification only...")

            if not skip_battery:
                try:
                    report = falsify_bond(ha, ha, subsample=subsample, max_rank=max_rank,
                                         inference=f"Ergon survivor: {hyp.feature_a} x {hyp.feature_b}")
                    print(f"  {report.summary()}")
                    results.append({
                        "ergon_pair": (da, db),
                        "harmonia_pair": (ha, hb),
                        "status": "falsified",
                        "surviving_rank": report.surviving_rank,
                        "original_rank": report.original_rank,
                        "tests": [{"test": t.test, "verdict": t.verdict, "detail": t.detail}
                                  for t in report.tests],
                        "wall_time": report.wall_time,
                    })
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results.append({
                        "ergon_pair": (da, db),
                        "harmonia_pair": (ha, hb),
                        "status": "error",
                        "error": str(e)[:200],
                    })
            continue

        print(f"\n--- {ha} x {hb} (from {da} x {db}) ---")
        print(f"  Ergon: depth={depth}, z={z:+.1f}, feature_a={hyp.feature_a}, feature_b={hyp.feature_b}")

        # Stage 1: Ungated TT-Cross exploration
        print(f"  Stage 1: Ungated TT-Cross exploration (subsample={subsample})...")
        try:
            t0 = time.time()
            engine = HarmoniaEngine(
                domains=[ha, hb],
                max_rank=max_rank,
                subsample=subsample,
                scorer="distributional",
            )
            tt, report = engine.explore()
            explore_time = time.time() - t0

            bond_dim = report.bonds[0].bond_dim if report.bonds else 0
            svs = report.bonds[0].top_singular_values[:5] if report.bonds else []

            print(f"  Bond dimension: {bond_dim}")
            if svs:
                print(f"  Top singular values: {', '.join(f'{s:.3f}' for s in svs)}")
            print(f"  Wall time: {explore_time:.1f}s")

            result = {
                "ergon_pair": (da, db),
                "harmonia_pair": (ha, hb),
                "ergon_depth": depth,
                "ergon_z": z,
                "bond_dim": bond_dim,
                "top_svs": svs,
                "explore_time": explore_time,
            }

            # Stage 2: Falsification (only if bond_dim > 0)
            if bond_dim > 0 and not skip_battery:
                print(f"  Stage 2: Falsification battery (bond_dim={bond_dim})...")
                try:
                    f_report = falsify_bond(ha, hb, subsample=subsample, max_rank=max_rank,
                                           inference=f"Ergon survivor: {hyp.feature_a} x {hyp.feature_b}")
                    print(f"  {f_report.summary()}")
                    result["status"] = "falsified"
                    result["surviving_rank"] = f_report.surviving_rank
                    result["original_rank"] = f_report.original_rank
                    result["falsification_tests"] = [
                        {"test": t.test, "verdict": t.verdict, "detail": t.detail}
                        for t in f_report.tests
                    ]
                    result["falsification_time"] = f_report.wall_time

                    if f_report.surviving_rank > 0:
                        print(f"  >>> SURVIVES HARMONIA FALSIFICATION (rank {f_report.surviving_rank}) <<<")
                    else:
                        print(f"  Killed by Harmonia battery")
                except Exception as e:
                    print(f"  Falsification error: {e}")
                    result["status"] = "explore_only"
                    result["falsification_error"] = str(e)[:200]
            elif bond_dim == 0:
                print(f"  No bond structure found — skipping falsification")
                result["status"] = "no_bond"
            else:
                result["status"] = "explored"

            results.append(result)

        except Exception as e:
            print(f"  Exploration error: {e}")
            results.append({
                "ergon_pair": (da, db),
                "harmonia_pair": (ha, hb),
                "status": "error",
                "error": str(e)[:200],
            })

    # Summary
    print("\n" + "=" * 80)
    print("BRIDGE SUMMARY")
    print("=" * 80)
    explored = [r for r in results if r.get("bond_dim") is not None]
    with_bond = [r for r in explored if r.get("bond_dim", 0) > 0]
    survived = [r for r in results if r.get("surviving_rank", 0) > 0]

    print(f"  Pairs explored: {len(explored)}")
    print(f"  Pairs with bond structure: {len(with_bond)}")
    print(f"  Pairs surviving falsification: {len(survived)}")

    if survived:
        print(f"\n  SURVIVORS:")
        for r in survived:
            print(f"    {r['harmonia_pair'][0]} x {r['harmonia_pair'][1]}: "
                  f"bond={r.get('bond_dim', '?')}, surviving_rank={r['surviving_rank']}")

    # Save results
    out_path = Path(__file__).parent / "results" / f"bridge_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved: {out_path}")

    return results


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Harmonia Bridge — promote Ergon survivors to deep tensor analysis")
    parser.add_argument("archive", help="Path to Ergon archive JSON file")
    parser.add_argument("--top-k", type=int, default=10, help="Number of domain pairs to promote")
    parser.add_argument("--subsample", type=int, default=2000, help="Subsample size for Harmonia domains")
    parser.add_argument("--max-rank", type=int, default=15, help="Max TT bond dimension")
    parser.add_argument("--explore-only", action="store_true", help="Skip falsification, only do TT-Cross")
    args = parser.parse_args()

    # Load Ergon archive
    archive = Archive()
    archive.load(args.archive)
    print(f"Loaded Ergon archive: {len(archive.grid)} cells from {args.archive}")

    results = promote_to_harmonia(
        archive,
        top_k=args.top_k,
        subsample=args.subsample,
        max_rank=args.max_rank,
        skip_battery=args.explore_only,
    )


if __name__ == "__main__":
    main()
