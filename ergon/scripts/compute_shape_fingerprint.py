#!/usr/bin/env python3
"""
Compute high-precision SnapPy shape fingerprints for the knots.json corpus.

Full trace-field recovery (invariant_trace_field_gens.find_field) requires Sage
or cypari2, neither of which is installed on M1. This script delivers the
prerequisite data — high-precision tetrahedra shapes + volume + Chern-Simons +
cusp_shape — sufficient for downstream LLL-based trace-field recovery.

Output: ergon/results/shape_fingerprints.json
  {
    n_knots, n_failed, bits_prec, elapsed_seconds,
    fingerprints: [
      { name, snappy_name, num_tetrahedra, solution_type, volume,
        chern_simons, cusp_shape_real, cusp_shape_imag, shapes: [[re, im], ...] }
    ]
  }
"""
import json
import re
import time
from pathlib import Path

import snappy

ROOT = Path(__file__).resolve().parent.parent.parent
KNOTS_PATH = ROOT / "cartography" / "knots" / "data" / "knots.json"
OUT_PATH = ROOT / "ergon" / "results" / "shape_fingerprints.json"

BITS_PREC = 200


def convert_name(name: str) -> str:
    if '*' in name:
        return name.replace('*', '').replace('_', '')
    return name


def extract_crossing_number(name: str) -> int:
    m = re.match(r'^(\d+)', name)
    return int(m.group(1)) if m else 0


def _to_float_pair(z):
    """Convert snappy.Number complex to (real, imag) Python floats, preserving
    precision via str(). We keep the *string form* so LLL downstream can reparse
    to arbitrary precision if needed."""
    s = str(z)
    return s


def fingerprint(name: str, snappy_name: str):
    M = snappy.Manifold(snappy_name)
    sol = M.solution_type()
    n_tet = M.num_tetrahedra()

    try:
        vol = str(M.volume(bits_prec=BITS_PREC))
    except Exception:
        vol = None
    try:
        cs = str(M.chern_simons())
    except Exception:
        cs = None
    try:
        shapes = M.tetrahedra_shapes(bits_prec=BITS_PREC, part='rect')
        shapes_str = [str(s) for s in shapes]
    except Exception:
        shapes_str = None
    try:
        cs_shape = M.cusp_info(0).get('shape') if M.num_cusps() > 0 else None
        cs_shape_str = str(cs_shape) if cs_shape is not None else None
    except Exception:
        cs_shape_str = None

    return {
        "name": name,
        "snappy_name": snappy_name,
        "crossing_number": extract_crossing_number(name),
        "num_tetrahedra": n_tet,
        "solution_type": sol,
        "volume": vol,
        "chern_simons": cs,
        "cusp_shape": cs_shape_str,
        "shapes": shapes_str,
        "bits_prec": BITS_PREC,
    }


def main():
    with open(KNOTS_PATH) as f:
        data = json.load(f)
    knots = data["knots"]

    print(f"Computing shape fingerprints for {len(knots)} knots @ {BITS_PREC} bits")
    results = []
    failures = []
    t0 = time.time()

    for i, k in enumerate(knots):
        name = k["name"]
        snappy_name = convert_name(name)
        try:
            results.append(fingerprint(name, snappy_name))
        except Exception as e:
            failures.append((name, str(e)[:150]))

        if (i + 1) % 500 == 0:
            el = time.time() - t0
            rate = (i + 1) / el
            print(f"  [{i+1}/{len(knots)}] {len(results)} ok, {len(failures)} fail, "
                  f"{rate:.1f}/s, elapsed {el:.0f}s")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s: {len(results)} ok, {len(failures)} fail")
    if failures:
        print("First 10 failures:")
        for name, err in failures[:10]:
            print(f"  {name}: {err}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump({
            "n_knots": len(results),
            "n_failed": len(failures),
            "bits_prec": BITS_PREC,
            "elapsed_seconds": round(elapsed, 1),
            "fingerprints": results,
        }, f, indent=1)
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
