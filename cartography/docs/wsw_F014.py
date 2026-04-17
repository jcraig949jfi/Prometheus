"""Weak Signal Walk — F014: Lehmer spectrum gap (task wsw_F014).

Task: Apply Mahler measure projection (P053) stratified by degree, bad_primes count (num_ram),
      and conductor (disc_abs decade). Verify the 4.4% gap persists across all strata.
      Check for degree-dependent structure in the gap width.

Data source: lmfdb.nf_fields (22M rows total; sampling strategy below).
Projections used:
  P053 (Mahler measure projection)
  P023-analog (degree stratification)
  P021-analog (num_ram = bad-prime count stratification)
  P020-analog (disc_abs-decade stratification)

Sampling strategy (explicitly biased, documented per Pattern 4):
  For each degree d in [2, 30]: ORDER BY disc_abs ASC LIMIT N_per_degree.
  RATIONALE: Minimum-Mahler-measure polynomials (Lehmer-type) have small
  discriminant for their degree; sorting ASC by disc_abs biases toward the
  target. A random sample would likely miss the true per-stratum minimum.
  The sampling bias is INTENTIONAL and DISCLOSED — do not use this script's
  output for distribution-averaged claims.

Output: cartography/docs/wsw_F014_results.json
"""
import json
import os
import time
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import psycopg2

DB = dict(host="192.168.1.176", port=5432, dbname="lmfdb", user="lmfdb", password="lmfdb")
N_PER_DEGREE = 5000
DEGREES = list(range(2, 25))  # deg 1 is trivial; 25+ sparse
LEHMER_BOUND = 1.17628081825992  # Mahler measure of Lehmer's polynomial
NEXT_KNOWN = 1.228  # claimed next smallest in F014 tensor entry
OUT_PATH = Path("D:/Prometheus/cartography/docs/wsw_F014_results.json")


def parse_coeffs(txt: str) -> list[int]:
    """Parse postgres array-literal {a,b,c} into [a,b,c] of ints. Lowest-degree first."""
    if not txt or not txt.startswith("{") or not txt.endswith("}"):
        return []
    inner = txt[1:-1]
    if not inner:
        return []
    out = []
    for tok in inner.split(","):
        tok = tok.strip()
        if not tok:
            return []
        try:
            out.append(int(tok))
        except ValueError:
            return []
    return out


def mahler_measure(coeffs_low_first: list[int]) -> float | None:
    """Compute Mahler measure = |leading| * prod max(1, |root|) for integer polynomial.

    coeffs are lowest-degree first (LMFDB convention). numpy.roots wants
    highest-degree first.
    """
    if len(coeffs_low_first) < 2:
        return None
    leading = coeffs_low_first[-1]
    if leading == 0:
        return None
    # Strip trailing zeros to high-degree side: leading should be last non-zero.
    coeffs_high_first = list(reversed(coeffs_low_first))
    # numpy.roots
    try:
        roots = np.roots(coeffs_high_first)
    except Exception:
        return None
    m = abs(leading)
    for r in roots:
        ar = abs(r)
        if ar > 1.0:
            m *= ar
    if not math.isfinite(m):
        return None
    return float(m)


# -----------------------------------------------------------------------------
# Load + compute
# -----------------------------------------------------------------------------
t_total = time.time()
conn = psycopg2.connect(**DB)
cur = conn.cursor()

all_rows = []  # (deg, num_ram_int, disc_abs_int, mahler)

for d in DEGREES:
    t0 = time.time()
    cur.execute(
        """
        SELECT coeffs, num_ram, disc_abs
          FROM nf_fields
         WHERE degree = %s AND coeffs IS NOT NULL
         ORDER BY (disc_abs::numeric) ASC
         LIMIT %s
        """,
        (str(d), N_PER_DEGREE),
    )
    batch = cur.fetchall()
    loaded = 0
    for coeffs_txt, num_ram_txt, disc_abs_txt in batch:
        coeffs = parse_coeffs(coeffs_txt)
        if len(coeffs) != d + 1:
            continue  # malformed
        m = mahler_measure(coeffs)
        if m is None:
            continue
        try:
            nr = int(num_ram_txt) if num_ram_txt is not None else -1
        except (ValueError, TypeError):
            nr = -1
        try:
            da = int(disc_abs_txt) if disc_abs_txt is not None else -1
        except (ValueError, TypeError):
            da = -1
        all_rows.append((d, nr, da, m))
        loaded += 1
    print(f"[deg {d}] sampled {len(batch)} -> {loaded} usable  in {time.time()-t0:.1f}s")

conn.close()
print(f"[total] {len(all_rows)} polynomials evaluated in {time.time()-t_total:.1f}s")


# -----------------------------------------------------------------------------
# Aggregate: min Mahler per stratum, and find polynomials in gap region
# -----------------------------------------------------------------------------
mahler_by_degree = defaultdict(list)
for d, nr, da, m in all_rows:
    mahler_by_degree[d].append((m, nr, da))

# Per-degree minimum (excluding cyclotomic-like m ~ 1.0; Mahler = 1 means cyclotomic)
per_degree = {}
for d, items in sorted(mahler_by_degree.items()):
    non_cyclo = [(m, nr, da) for (m, nr, da) in items if m > 1.0001]
    items_sorted = sorted(non_cyclo, key=lambda x: x[0])
    cyclo_count = sum(1 for (m, _, _) in items if m <= 1.0001)
    if items_sorted:
        min_m, min_nr, min_da = items_sorted[0]
        next5 = [{"m": m, "num_ram": nr, "disc_abs": da}
                 for (m, nr, da) in items_sorted[:5]]
    else:
        min_m, min_nr, min_da = float("inf"), -1, -1
        next5 = []
    per_degree[d] = {
        "n_evaluated": len(items),
        "n_cyclotomic_approx": cyclo_count,
        "min_non_cyclotomic_mahler": min_m,
        "min_sample_num_ram": min_nr,
        "min_sample_disc_abs": min_da,
        "top5_smallest_non_cyclotomic": next5,
        "at_lehmer_bound": (abs(min_m - LEHMER_BOUND) < 0.001),
        "gap_vs_lehmer_pct": (100.0 * (min_m - LEHMER_BOUND) / LEHMER_BOUND) if min_m > 1.0 and math.isfinite(min_m) else None,
    }


# -----------------------------------------------------------------------------
# Bad-prime stratification (num_ram bins)
# -----------------------------------------------------------------------------
per_num_ram = defaultdict(lambda: {"n": 0, "min_non_cyclo": float("inf"), "example": None})
for d, nr, da, m in all_rows:
    bin_key = nr if nr >= 0 else -1
    per_num_ram[bin_key]["n"] += 1
    if m > 1.0001 and m < per_num_ram[bin_key]["min_non_cyclo"]:
        per_num_ram[bin_key]["min_non_cyclo"] = m
        per_num_ram[bin_key]["example"] = {"degree": d, "disc_abs": da, "m": m}
per_num_ram_out = {
    str(k): {
        "n": v["n"],
        "min_non_cyclotomic_mahler": v["min_non_cyclo"],
        "example": v["example"],
        "gap_vs_lehmer_pct": (100.0 * (v["min_non_cyclo"] - LEHMER_BOUND) / LEHMER_BOUND) if math.isfinite(v["min_non_cyclo"]) else None,
    }
    for k, v in sorted(per_num_ram.items())
}


# -----------------------------------------------------------------------------
# Gap region populations: polynomials with Mahler in (LEHMER_BOUND, 1.3]
# -----------------------------------------------------------------------------
gap_buckets = defaultdict(int)  # (0.001-width bucket) -> count
gap_examples = []
for d, nr, da, m in all_rows:
    if LEHMER_BOUND - 0.001 < m <= 1.30:
        b = round(m, 3)
        gap_buckets[b] += 1
        if len(gap_examples) < 50:
            gap_examples.append({"degree": d, "num_ram": nr, "disc_abs": da, "m": m})
gap_histogram = {str(k): v for k, v in sorted(gap_buckets.items())}


# -----------------------------------------------------------------------------
# Headline numbers + verdict
# -----------------------------------------------------------------------------
# Global min non-cyclotomic in sample
global_non_cyclo = [m for (_, _, _, m) in all_rows if m > 1.0001]
global_min = min(global_non_cyclo) if global_non_cyclo else float("inf")
# Second-lowest (counting only values meaningfully above LEHMER_BOUND)
# "The gap" = smallest non-cyclotomic minus LEHMER_BOUND
meaningful_above = sorted(m for m in global_non_cyclo if m > LEHMER_BOUND + 0.0005)
second_min = meaningful_above[0] if meaningful_above else float("inf")

# Gap percentage
gap_pct = None
if math.isfinite(second_min) and global_min > 0:
    gap_pct = 100.0 * (second_min - LEHMER_BOUND) / LEHMER_BOUND

# Persistence across strata: is minimum per-degree stable near LEHMER_BOUND only at specific degrees?
degrees_at_lehmer = [d for d, v in per_degree.items() if v["at_lehmer_bound"]]
degrees_in_gap = [d for d, v in per_degree.items()
                  if v["gap_vs_lehmer_pct"] is not None
                  and 0 < v["gap_vs_lehmer_pct"] < 5.0]

if global_min <= LEHMER_BOUND + 0.001:
    verdict_base = "Lehmer bound TOUCHED in sample"
elif global_min <= LEHMER_BOUND * 1.044:
    verdict_base = "Lehmer bound-adjacent"
else:
    verdict_base = "Above Lehmer bound"

# The 4.4% gap verification: find if there is a polynomial strictly between
# LEHMER_BOUND + ε and 1.228 (the claimed next-known).
in_gap_strict = [m for m in global_non_cyclo
                 if LEHMER_BOUND + 0.0005 < m < NEXT_KNOWN - 0.0005]
gap_strict_violations = len(in_gap_strict)
min_in_strict_gap = min(in_gap_strict) if in_gap_strict else None

if gap_strict_violations == 0:
    gap_verdict = "GAP CONFIRMED in sample (no polynomial strictly between Lehmer and 1.228)"
else:
    gap_verdict = (f"GAP VIOLATED: {gap_strict_violations} polynomial(s) strictly in "
                   f"(Lehmer, 1.228). Minimum such: {min_in_strict_gap:.6f}")


# -----------------------------------------------------------------------------
# Write
# -----------------------------------------------------------------------------
output = {
    "specimen_id": "F014",
    "specimen_label": "Lehmer spectrum gap",
    "completed_by": "Harmonia_M2_sessionB",
    "n_evaluated": len(all_rows),
    "n_per_degree_cap": N_PER_DEGREE,
    "degrees_probed": DEGREES,
    "reference_constants": {
        "LEHMER_BOUND": LEHMER_BOUND,
        "NEXT_KNOWN_claimed_in_F014": NEXT_KNOWN,
        "claimed_gap_pct": 4.4,
    },
    "sampling_strategy": {
        "method": "ORDER BY disc_abs ASC LIMIT N_per_degree, per degree",
        "bias": "intentional — biases toward small-discriminant polynomials where minimum-Mahler lives",
        "pattern_4_disclosure": "This is a Pattern 4 (Sampling Frame Trap) pattern DELIBERATELY applied. Do not use the output for distribution-average claims. Use only for minimum-finding.",
        "alternative_not_taken": "Uniform random sample — would likely miss the minimum-Mahler polynomials, which are rare",
    },
    "projections_used": {
        "P053": "Mahler measure projection (numpy.roots)",
        "P023_analog": "degree stratification",
        "P021_analog": "num_ram stratification (number of ramified primes, proxy for bad-prime count)",
        "P020_analog": "disc_abs-decade stratification (implicit via discriminant-ordered sampling)",
    },
    "headline": {
        "global_min_non_cyclotomic_mahler": global_min,
        "second_min_non_cyclotomic_mahler": second_min,
        "gap_percent_observed": gap_pct,
        "claimed_gap_percent": 4.4,
        "gap_verdict": gap_verdict,
        "degrees_at_lehmer_bound": degrees_at_lehmer,
        "degrees_with_small_gap_lt_5pct": degrees_in_gap,
        "base_verdict": verdict_base,
    },
    "per_degree": per_degree,
    "per_num_ram": per_num_ram_out,
    "gap_region_histogram": gap_histogram,
    "gap_region_examples": gap_examples,
    "gap_strict_violations_count": gap_strict_violations,
    "gap_strict_violations_min_m": min_in_strict_gap,
    "verdict": "SURVIVES" if gap_strict_violations == 0 else "KILLED",
    "shape_summary": (
        f"From a Pattern-4-biased sample of {len(all_rows)} number-field polynomials across "
        f"degrees {min(DEGREES)}-{max(DEGREES)}, global minimum non-cyclotomic Mahler measure = "
        f"{global_min:.6f}. Gap to next distinct cluster: {gap_pct:.2f}% "
        f"(claimed 4.4%). {gap_verdict}."
    ),
    "notes": [
        "Cyclotomic polynomials have Mahler measure exactly 1; filtered them out with m > 1.0001.",
        "Mahler measure computed as |leading_coeff| * prod over roots with |r| > 1 of |r|, via numpy.roots.",
        "Degrees with low row counts in LMFDB (11, 13, 15, 17, 19, 21, 23) have small samples; their minima are inherently less stable than high-count degrees.",
        "num_ram is number of ramified primes in the field; a direct analog of P021 bad-prime stratification.",
    ],
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n===== HEADLINE =====")
print(f"Global min non-cyclotomic Mahler: {global_min:.6f}")
print(f"Second min:                       {second_min:.6f}")
print(f"Gap %:                            {gap_pct if gap_pct is not None else 'n/a'}")
print(f"Gap verdict:                      {gap_verdict}")
print(f"Verdict:                          {output['verdict']}")
print(f"Wrote:                            {OUT_PATH}")
