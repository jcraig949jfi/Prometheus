#!/usr/bin/env python3
"""
Batch-compute invariant trace / shape fields for the knots.json corpus
using Techne's knot_shape_field (PARI via cypari, no Sage required).

Output: ergon/results/knot_shape_fields.json
Format per knot:
  {knot_name, snappy_name, poly, degree, disc, bits_prec, error?,
   is_hyperbolic, caveat}

Handles torus / non-hyperbolic knots gracefully (error record, no crash).
"""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from techne.lib.knot_shape_field import knot_shape_field_batch
KNOTS_PATH = ROOT / "cartography" / "knots" / "data" / "knots.json"
OUT_PATH = ROOT / "ergon" / "results" / "knot_shape_fields.json"

BITS_PREC = 400
MAX_DEG = 10
CHECKPOINT_EVERY = 100


def convert_name(name: str) -> str:
    if '*' in name:
        return name.replace('*', '').replace('_', '')
    return name


def checkpoint(results, elapsed):
    n_ok = sum(1 for r in results if 'error' not in r)
    n_err = len(results) - n_ok
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump({
            "n_knots": len(results),
            "n_ok": n_ok,
            "n_error": n_err,
            "bits_prec": BITS_PREC,
            "max_deg": MAX_DEG,
            "elapsed_seconds": round(elapsed, 1),
            "complete": False,
            "results": results,
        }, f, default=str)
    import sys as _s
    print(f"  [checkpoint] saved {len(results)} at {elapsed:.0f}s ({n_ok} ok, {n_err} err)", flush=True)


def main():
    import sys
    from techne.lib.knot_shape_field import knot_shape_field
    with open(KNOTS_PATH) as f:
        data = json.load(f)
    knots = data["knots"]
    names = [(k["name"], convert_name(k["name"])) for k in knots]

    print(f"Computing shape fields for {len(names)} knots @ {BITS_PREC} bits, max_deg={MAX_DEG}", flush=True)
    print(f"Checkpointing every {CHECKPOINT_EVERY} knots to {OUT_PATH}", flush=True)
    t0 = time.time()

    results = []
    PROGRESS_PATH = OUT_PATH.parent / (OUT_PATH.stem + "_progress.txt")
    for i, (orig, sn) in enumerate(names):
        try:
            r = knot_shape_field(sn, bits_prec=BITS_PREC, max_deg=MAX_DEG)
            r['knot_name'] = sn
        except Exception as e:
            r = {
                'knot_name': sn,
                'error': str(e)[:200],
                'poly': None,
                'degree': None,
                'disc': None,
            }
        r['original_name'] = orig
        results.append(r)
        # Write one-line progress always so log shows activity
        if (i + 1) % 20 == 0:
            dt = time.time() - t0
            rate = (i + 1) / dt if dt > 0 else 0
            with open(PROGRESS_PATH, 'a') as pf:
                pf.write(f"{i+1}/{len(names)} rate={rate:.2f} knots/s elapsed={dt:.0f}s\n")
            print(f"  [progress] {i+1}/{len(names)}  {rate:.2f} knots/s  elapsed {dt:.0f}s", flush=True)
        if (i + 1) % CHECKPOINT_EVERY == 0:
            checkpoint(results, time.time() - t0)

    elapsed = time.time() - t0
    n_ok = sum(1 for r in results if 'error' not in r)
    n_err = len(results) - n_ok
    print(f"\nDone in {elapsed:.1f}s: {n_ok}/{len(results)} ok, {n_err} errors")

    # First 5 errors for diagnosis
    if n_err:
        print("First 5 errors:")
        errs = [r for r in results if 'error' in r][:5]
        for r in errs:
            print(f"  {r['original_name']} ({r['knot_name']}): {r['error']}")

    # Degree histogram of successes
    from collections import Counter
    deg_hist = Counter(r.get('degree') for r in results if 'error' not in r)
    print(f"\nDegree histogram: {dict(sorted(deg_hist.items(), key=lambda x: (x[0] is None, x[0])))}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump({
            "n_knots": len(results),
            "n_ok": n_ok,
            "n_error": n_err,
            "bits_prec": BITS_PREC,
            "max_deg": MAX_DEG,
            "elapsed_seconds": round(elapsed, 1),
            "complete": True,
            "results": results,
        }, f, indent=1, default=str)
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
