#!/usr/bin/env python3
"""
H101 (Aporia void prediction): Do any of Charon's 11 small-Salem LMFDB NFs
(M < 1.3, deg 8-14) appear as a knot trace field in the 12,965-knot corpus?

Charon's small-Salem catalog (Mahler measure < 1.3):
  deg  M                  LMFDB label                 disc_abs
   8   1.28063816         8.2.11489547.1              1.15e7
  10   1.17628082         10.2.1332031009.1           1.33e9    (LEHMER)
  10   1.21639166         10.2.1487567761.1           1.49e9
  10   1.23039143         10.2.2932315445.1           2.93e9
  10   1.26123096         10.2.6656764921.1           6.66e9
  10   1.26723386         10.0.379908823.1            3.80e8
  10   1.28358236         10.0.1035983667.1           1.04e9
  10   1.29348595         10.2.7995399889.1           7.99e9
  12   1.22778556         12.0.201018619201.1         2.01e11
  12   1.24072642         12.2.2458729426447.1        2.46e12
  12   1.27281837         12.0.184052780197.1         1.84e11

Primary match fields: discriminant (signed), degree, polredabs polynomial string.
The LMFDB label encodes degree.signature.disc_abs.k, so disc_abs is a strong
indicator (candidate NF) and the polredabs-canonical polynomial is definitive.

Match logic:
  For each knot with a shape_field result, compare (degree, disc) against the
  Salem list. If match, flag candidate. Verify by checking polynomials agree after
  polredabs (already applied in Techne's tool).

Output: ergon/results/h101_salem_matches.json + stdout table.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOT_FIELDS = ROOT / "ergon" / "results" / "knot_shape_fields.json"
OUT = ROOT / "ergon" / "results" / "h101_salem_matches.json"

SALEM_NFS = [
    {"deg": 8,  "M": 1.28063816, "label": "8.2.11489547.1",       "disc_abs": 11489547},
    {"deg": 10, "M": 1.17628082, "label": "10.2.1332031009.1",    "disc_abs": 1332031009,  "name": "Lehmer decic"},
    {"deg": 10, "M": 1.21639166, "label": "10.2.1487567761.1",    "disc_abs": 1487567761},
    {"deg": 10, "M": 1.23039143, "label": "10.2.2932315445.1",    "disc_abs": 2932315445},
    {"deg": 10, "M": 1.26123096, "label": "10.2.6656764921.1",    "disc_abs": 6656764921},
    {"deg": 10, "M": 1.26723386, "label": "10.0.379908823.1",     "disc_abs": 379908823},
    {"deg": 10, "M": 1.28358236, "label": "10.0.1035983667.1",    "disc_abs": 1035983667},
    {"deg": 10, "M": 1.29348595, "label": "10.2.7995399889.1",    "disc_abs": 7995399889},
    {"deg": 12, "M": 1.22778556, "label": "12.0.201018619201.1",  "disc_abs": 201018619201},
    {"deg": 12, "M": 1.24072642, "label": "12.2.2458729426447.1", "disc_abs": 2458729426447},
    {"deg": 12, "M": 1.27281837, "label": "12.0.184052780197.1",  "disc_abs": 184052780197},
]


def main():
    if not KNOT_FIELDS.exists():
        print(f"ERROR: {KNOT_FIELDS} not found. Wait for knot_shape_field batch to complete.")
        sys.exit(1)

    data = json.load(open(KNOT_FIELDS))
    results = data.get("results", [])
    n_ok = sum(1 for r in results if 'error' not in r)
    print(f"Loaded {len(results)} knot records ({n_ok} with shape field).")

    salem_by_disc = {abs(s["disc_abs"]): s for s in SALEM_NFS}
    salem_by_deg = {}
    for s in SALEM_NFS:
        salem_by_deg.setdefault(s["deg"], []).append(s)

    # Pre-compute degree histogram of knots
    from collections import Counter
    knot_deg_hist = Counter(r.get("degree") for r in results if "error" not in r)
    print(f"Knot shape-field degree histogram: {dict(sorted(knot_deg_hist.items(), key=lambda x:(x[0] is None, x[0])))}")

    # Candidate matches: same degree AND |disc| in salem list
    candidates = []
    deg_bucket = {}  # deg -> list of (knot_name, disc) for neighbours
    for r in results:
        if "error" in r: continue
        d = r.get("degree")
        disc = r.get("disc")
        if d is None or disc is None: continue
        deg_bucket.setdefault(d, []).append((r.get("original_name") or r.get("knot_name"), disc, r.get("poly")))
        if abs(disc) in salem_by_disc:
            s = salem_by_disc[abs(disc)]
            if s["deg"] == d:
                candidates.append({
                    "knot": r.get("original_name") or r.get("knot_name"),
                    "knot_poly": r.get("poly"),
                    "knot_disc": disc,
                    "salem_label": s["label"],
                    "salem_M": s["M"],
                    "salem_name": s.get("name", ""),
                })

    print(f"\n{'='*80}")
    print(f"H101 VERDICT — exact (degree, |disc|) matches: {len(candidates)}")
    print(f"{'='*80}")
    if candidates:
        for c in candidates:
            print(f"  KNOT: {c['knot']}   poly: {c['knot_poly']}   disc={c['knot_disc']}")
            print(f"    -> MATCHES Salem NF {c['salem_label']}  M={c['salem_M']}  {c.get('salem_name','')}")
    else:
        print("  No (degree, |disc|) matches. H101 NOT CONFIRMED.")

    # For each target salem degree, print nearest discriminants observed in knot corpus
    print(f"\n{'='*80}")
    print("Nearest-disc knots per Salem target (diagnostic)")
    print(f"{'='*80}")
    near_report = []
    for s in SALEM_NFS:
        target = abs(s["disc_abs"])
        knots_at_deg = deg_bucket.get(s["deg"], [])
        if not knots_at_deg:
            print(f"  {s['label']} (deg={s['deg']}): NO KNOTS at this degree")
            continue
        ranked = sorted(knots_at_deg, key=lambda kd: abs(abs(kd[1]) - target))
        nearest = ranked[:3]
        print(f"  {s['label']} (deg={s['deg']}, |disc|={target}):")
        for name, d, poly in nearest:
            print(f"    nearest: {name}  |disc|={abs(d)}  poly={poly}  (delta={abs(abs(d)-target)})")
        near_report.append({
            "salem_label": s["label"],
            "target_disc_abs": target,
            "nearest_knots": [{"knot": name, "disc": d, "poly": poly} for name, d, poly in nearest],
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            "salem_targets": SALEM_NFS,
            "n_knots_loaded": len(results),
            "n_knots_with_shape_field": n_ok,
            "knot_degree_histogram": {str(k): v for k, v in knot_deg_hist.items()},
            "candidates_h101": candidates,
            "nearest_report": near_report,
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
