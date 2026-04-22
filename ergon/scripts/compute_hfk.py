#!/usr/bin/env python3
"""
Batch-compute knot Floer homology (HFK) for all knots in knots.json.

Uses SnapPy for PD codes and knot_floer_homology for HFK computation.
Saves results to ergon/results/hfk_features.json.
"""
import json
import re
import signal
import sys
import time
from pathlib import Path

import snappy
import knot_floer_homology

ROOT = Path(__file__).resolve().parent.parent.parent
KNOTS_PATH = ROOT / "cartography" / "knots" / "data" / "knots.json"
OUTPUT_PATH = ROOT / "ergon" / "results" / "hfk_features.json"


def convert_name(name: str) -> str:
    """Convert knots.json name to SnapPy Link name.

    '11*a_367' -> '11a367'
    '12*n_121' -> '12n121'
    '3_1'      -> '3_1'  (no star = keep as-is)
    """
    if '*' in name:
        # Remove '*' and '_'
        return name.replace('*', '').replace('_', '')
    return name


def extract_crossing_number(name: str) -> int:
    """Extract crossing number from knot name."""
    m = re.match(r'^(\d+)', name)
    return int(m.group(1)) if m else 0


def compute_hfk_for_knot(name: str, snappy_name: str):
    """Compute HFK features for a single knot. Returns dict or None on failure."""
    L = snappy.Link(snappy_name)
    pd = L.PD_code()
    if not pd:
        return None

    result = knot_floer_homology.pd_to_hfk(pd)

    ranks = result.get('ranks', {})
    if ranks:
        i_vals = [k[0] for k in ranks]
        j_vals = [k[1] for k in ranks]
        rank_width = max(i_vals) - min(i_vals)
        rank_height = max(j_vals) - min(j_vals)
        max_betti = max(ranks.values())
    else:
        rank_width = 0
        rank_height = 0
        max_betti = 0

    crossing = extract_crossing_number(name)

    return {
        "name": name,
        "snappy_name": snappy_name,
        "f0_crossing_number": crossing,
        "f1_seifert_genus": result.get('seifert_genus', 0),
        "f2_tau": result.get('tau', 0),
        "f3_epsilon": result.get('epsilon', 0),
        "f4_total_rank": result.get('total_rank', 0),
        "f5_is_L_space": 1 if result.get('L_space_knot', False) else 0,
        "f6_is_fibered": 1 if result.get('fibered', False) else 0,
        "f7_rank_width": rank_width,
        "f8_rank_height": rank_height,
        "f9_max_betti": max_betti,
    }


def main():
    with open(KNOTS_PATH) as f:
        data = json.load(f)
    knots = data["knots"]

    print(f"Computing HFK for {len(knots)} knots...")
    results = []
    failures = []
    t0 = time.time()

    for i, k in enumerate(knots):
        name = k["name"]
        snappy_name = convert_name(name)

        try:
            feat = compute_hfk_for_knot(name, snappy_name)
            if feat is None:
                failures.append((name, "empty PD code"))
            else:
                results.append(feat)
        except Exception as e:
            failures.append((name, str(e)[:120]))

        if (i + 1) % 1000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1}/{len(knots)}] {len(results)} ok, {len(failures)} fail, "
                  f"{rate:.1f} knots/s, elapsed {elapsed:.0f}s")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Success: {len(results)}")
    print(f"  Failed:  {len(failures)}")

    if failures:
        print(f"\nFirst 20 failures:")
        for name, err in failures[:20]:
            print(f"  {name}: {err}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump({
            "n_knots": len(results),
            "n_failed": len(failures),
            "elapsed_seconds": round(elapsed, 1),
            "features": results,
        }, f, indent=1)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
