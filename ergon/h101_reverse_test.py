#!/usr/bin/env python3
"""
H101 reverse-direction test.

Forward direction (discovering every knot's trace field then matching Salem NFs)
is too slow on Windows cypari without batching infrastructure (observed >3 min
per difficult knot at max_deg=10).

Reverse direction: for each Salem polynomial p(x) and each knot shape z, compute
p(z) at high precision. If |p(z)| < threshold, the shape is a root of p, i.e. the
knot's trace field contains a root of that Salem poly.

This is fast: O(deg) arithmetic per (poly, shape) pair, no algdep / polredabs.
For 5 polys × ~12K hyperbolic knots × ~10 shapes each = 600K evaluations.

We piggyback on the existing shape_fingerprints.json (bits_prec=200 SnapPy shapes
for all 12,965 knots, computed earlier this session). Upgrade precision on
matches.

Output: ergon/results/h101_reverse.json
"""
import json
import sys
import time
from pathlib import Path

from mpmath import mp, mpf, mpc

# -- Paths ----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FP_JSON = ROOT / "ergon" / "results" / "shape_fingerprints.json"
OUT = ROOT / "ergon" / "results" / "h101_reverse.json"

# -- Salem targets from Charon's deg-8-14 LMFDB exhaustive Lehmer scan --
# Each: (label, canonical poly coefficients [a0..an] -> poly = a_n*x^n + ... + a_0)
# Charon's canonical-form polynomials (from charon/data/small_salem_canonical_polys.json)
SALEM_POLYS = [
    # 10.2.1332031009.1 — Lehmer's decic
    ("10.2.1332031009.1", [1, -1, 0, 1, -1, 1, -1, 1, 0, -1, 1], 10, 1332031009, 1.17628),
    # 10.2.1487567761.1
    ("10.2.1487567761.1", [1, 0, 0, 0, -1, -1, -1, 0, 0, 0, 1], 10, 1487567761, 1.21639),
    # 10.2.2932315445.1
    ("10.2.2932315445.1", [1, 0, 0, -1, 0, -1, 0, -1, 0, 0, 1], 10, 2932315445, 1.23039),
    # 10.2.6656764921.1
    ("10.2.6656764921.1", [1, 0, -1, 0, 0, -1, 0, 0, -1, 0, 1], 10, 6656764921, 1.26123),
    # 8.2.11489547.1
    ("8.2.11489547.1",    [1, 0, 0, -1, -1, -1, 0, 0, 1], 8, 11489547, 1.28064),
]


def eval_poly_at(coeffs, z):
    """Evaluate sum_k c_k * z^k at complex z. coeffs[k] is the coefficient of x^k.
    Supports mpc / complex / anything with +, *."""
    # Horner's rule (from high degree down)
    n = len(coeffs) - 1
    acc = mpf(coeffs[n])
    for k in range(n - 1, -1, -1):
        acc = acc * z + mpf(coeffs[k])
    return acc


def parse_complex_str(s):
    """Parse a snappy shape string like '0.5 + 0.866...*I'."""
    # Replace *I with j for python complex or build mpc
    s = s.replace(" ", "")
    s = s.replace("*I", "j")
    s = s.replace("E", "e")
    # mpmath accepts 'a+bj' when using mpc(a, b) -- simpler: regex
    import re
    m = re.match(r"^(?P<re>[+-]?(\d+\.?\d*|\.\d+)(e[+-]?\d+)?)(?P<im>[+-](\d+\.?\d*|\.\d+)(e[+-]?\d+)?)j?$", s)
    if m:
        re_part = mpf(m.group('re'))
        im_part = mpf(m.group('im'))
        return mpc(re_part, im_part)
    # fallback: Python complex
    try:
        c = complex(s)
        return mpc(c.real, c.imag)
    except Exception:
        return None


def main():
    print("H101 reverse test: Salem polys vs knot shapes", flush=True)
    t0 = time.time()

    with open(FP_JSON) as f:
        data = json.load(f)
    fingerprints = data["fingerprints"]
    print(f"Loaded {len(fingerprints)} shape fingerprints", flush=True)

    mp.prec = 250  # mpf precision in bits (>= shape fingerprint prec 200)

    # Threshold: shape fingerprints are at 200 bits, so eval residue should be < 10^-50
    THRESH = mpf('1e-40')

    hits = []
    evaluated = 0
    hyper = 0
    for i, fp in enumerate(fingerprints):
        if not fp.get("shapes"):
            continue
        hyper += 1
        name = fp["name"]
        shapes = fp["shapes"]
        # For each shape, for each Salem poly, compute p(z). Record minimum residue.
        for shape_str in shapes:
            z = parse_complex_str(shape_str)
            if z is None:
                continue
            evaluated += 1
            for label, coeffs, deg, disc_abs, M in SALEM_POLYS:
                val = eval_poly_at(coeffs, z)
                absval = abs(val)
                if absval < THRESH:
                    hits.append({
                        "knot": name,
                        "shape": shape_str[:80],
                        "salem_label": label,
                        "salem_M": M,
                        "salem_disc_abs": disc_abs,
                        "residue": str(absval),
                    })
        if (i + 1) % 1000 == 0:
            print(f"  [{i+1}/{len(fingerprints)}] {hyper} hyperbolic  "
                  f"{evaluated} shapes eval'd  {len(hits)} hits  "
                  f"{(time.time()-t0):.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s.  {evaluated} shapes evaluated.", flush=True)
    print(f"HITS: {len(hits)}", flush=True)
    for h in hits[:20]:
        print(f"  {h['knot']}  ~=  {h['salem_label']}  (M={h['salem_M']})  residue={h['residue']}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            "salem_targets": [
                {"label": p[0], "coeffs": p[1], "deg": p[2], "disc_abs": p[3], "M": p[4]}
                for p in SALEM_POLYS
            ],
            "n_fingerprints": len(fingerprints),
            "n_hyperbolic": hyper,
            "n_shapes_evaluated": evaluated,
            "threshold": str(THRESH),
            "mp_prec_bits": mp.prec,
            "hits": hits,
            "elapsed_seconds": round(elapsed, 1),
        }, f, indent=1, default=str)
    print(f"Saved {OUT}", flush=True)


if __name__ == "__main__":
    main()
