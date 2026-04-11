"""
Jones Polynomial Span and Breadth as Knot Complexity Measures
=============================================================
For ~13K knots, compute:
  - span = max_degree - min_degree of Jones polynomial
  - deficit = crossing_number - span (0 for alternating by KMT theorem)
  - breadth = number of nonzero coefficients
  - breadth/span ratio
  - correlations with determinant, Alexander polynomial degree

The Kauffman-Murasugi-Thistlethwaite theorem says span = crossing_number
for alternating knots. We verify this and measure the non-alternating penalty.
"""

import json
import os
import re
from collections import defaultdict

import numpy as np
from scipy import stats

# ── paths ────────────────────────────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO, "knots", "data", "knots.json")
OUT_PATH = os.path.join(REPO, "v2", "knot_jones_span_results.json")


def parse_name(name: str):
    """Parse knot name -> (crossing_number, is_alternating, index).

    Patterns:
      '3_1' -> (3, True, 1)         — small knots
      '11*a_1' -> (11, True, 1)     — alternating
      '11*n_1' -> (11, False, 1)    — non-alternating

    For knots <=10 crossings (Rolfsen table, no a/n flag), the non-alternating
    knots are at known indices:
      8_19, 8_20, 8_21
      9_42 through 9_49
      10_124 through 10_165
    """
    # Non-alternating cutoffs in Rolfsen table (first non-alt index for each cn)
    ROLFSEN_NONALT_START = {8: 19, 9: 42, 10: 124}

    m = re.match(r'^(\d+)\*?([an]?)_(\d+)$', name)
    if not m:
        return None, None, None
    cn = int(m.group(1))
    flag = m.group(2)
    idx = int(m.group(3))

    if flag == 'n':
        is_alt = False
    elif flag == 'a':
        is_alt = True
    else:
        # Small knots: use Rolfsen non-alternating cutoffs
        cutoff = ROLFSEN_NONALT_START.get(cn)
        is_alt = (cutoff is None) or (idx < cutoff)

    return cn, is_alt, idx


def main():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    knots = data["knots"]
    print(f"Loaded {len(knots)} knots")

    # ── Compute span, deficit, breadth for each knot ──────────────────
    records = []
    skipped = 0
    for k in knots:
        cn, is_alt, idx = parse_name(k["name"])
        if cn is None or cn == 0:
            skipped += 1
            continue

        jones = k.get("jones")
        if not jones or "min_power" not in jones:
            skipped += 1
            continue

        min_pow = jones["min_power"]
        max_pow = jones["max_power"]
        coeffs = jones["coefficients"]

        span = max_pow - min_pow
        deficit = cn - span
        breadth = sum(1 for c in coeffs if c != 0)
        breadth_span_ratio = breadth / span if span > 0 else float('nan')

        # Alexander degree (half-span, since it's symmetric)
        alex = k.get("alexander")
        alex_degree = None
        if alex and "min_power" in alex and "max_power" in alex:
            alex_degree = alex["max_power"] - alex["min_power"]

        det = k.get("determinant")

        records.append({
            "name": k["name"],
            "crossing_number": cn,
            "is_alternating": is_alt,
            "jones_span": span,
            "deficit": deficit,
            "breadth": breadth,
            "breadth_span_ratio": breadth_span_ratio,
            "alex_degree": alex_degree,
            "determinant": det,
        })

    print(f"Processed {len(records)} knots, skipped {skipped}")

    # ── 1. Alternating fraction and KMT verification ─────────────────
    alt_knots = [r for r in records if r["is_alternating"]]
    nonalt_knots = [r for r in records if not r["is_alternating"]]

    alt_fraction = len(alt_knots) / len(records) if records else 0
    print(f"\nAlternating: {len(alt_knots)} ({alt_fraction:.3f})")
    print(f"Non-alternating: {len(nonalt_knots)} ({1 - alt_fraction:.3f})")

    # KMT: for alternating knots, deficit should be 0
    alt_deficits = [r["deficit"] for r in alt_knots]
    alt_deficit_zero = sum(1 for d in alt_deficits if d == 0)
    alt_kmt_fraction = alt_deficit_zero / len(alt_knots) if alt_knots else 0
    print(f"\nKMT verification: {alt_deficit_zero}/{len(alt_knots)} alternating "
          f"knots have deficit=0 ({alt_kmt_fraction:.4f})")
    if alt_deficits:
        print(f"  Alt deficit stats: mean={np.mean(alt_deficits):.4f}, "
              f"max={max(alt_deficits)}, min={min(alt_deficits)}")

    # ── 2. Non-alternating deficit analysis ──────────────────────────
    nonalt_deficits = [r["deficit"] for r in nonalt_knots]
    if nonalt_deficits:
        mean_deficit = float(np.mean(nonalt_deficits))
        median_deficit = float(np.median(nonalt_deficits))
        std_deficit = float(np.std(nonalt_deficits))
        print(f"\nNon-alternating deficit: mean={mean_deficit:.3f}, "
              f"median={median_deficit:.1f}, std={std_deficit:.3f}")

        # Deficit distribution
        deficit_counts = defaultdict(int)
        for d in nonalt_deficits:
            deficit_counts[d] += 1
        print("  Deficit distribution:", dict(sorted(deficit_counts.items())))
    else:
        mean_deficit = median_deficit = std_deficit = 0

    # ── 3. Deficit vs crossing number (does penalty grow?) ───────────
    cn_deficit = defaultdict(list)
    for r in nonalt_knots:
        cn_deficit[r["crossing_number"]].append(r["deficit"])

    deficit_by_cn = {}
    for cn in sorted(cn_deficit.keys()):
        vals = cn_deficit[cn]
        deficit_by_cn[cn] = {
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "std": float(np.std(vals)),
            "n": len(vals),
        }
    print("\nDeficit by crossing number (non-alternating):")
    for cn, s in deficit_by_cn.items():
        print(f"  cn={cn}: mean={s['mean']:.2f}, median={s['median']:.1f}, n={s['n']}")

    # Regression: deficit vs crossing number
    if len(deficit_by_cn) >= 3:
        cns = np.array(sorted(deficit_by_cn.keys()), dtype=float)
        means = np.array([deficit_by_cn[int(c)]["mean"] for c in cns])
        slope, intercept, r, p, se = stats.linregress(cns, means)
        deficit_growth = {
            "slope": float(slope),
            "intercept": float(intercept),
            "R2": float(r ** 2),
            "p_value": float(p),
        }
        print(f"  Linear fit: deficit ~ {slope:.4f} * cn + {intercept:.3f}, "
              f"R²={r**2:.4f}, p={p:.4e}")
    else:
        deficit_growth = None

    # ── 4. Breadth/span ratio ────────────────────────────────────────
    alt_bsr = [r["breadth_span_ratio"] for r in alt_knots
               if not np.isnan(r["breadth_span_ratio"])]
    nonalt_bsr = [r["breadth_span_ratio"] for r in nonalt_knots
                  if not np.isnan(r["breadth_span_ratio"])]

    print(f"\nBreadth/span ratio:")
    if alt_bsr:
        print(f"  Alternating: mean={np.mean(alt_bsr):.4f}, std={np.std(alt_bsr):.4f}")
    if nonalt_bsr:
        print(f"  Non-alternating: mean={np.mean(nonalt_bsr):.4f}, std={np.std(nonalt_bsr):.4f}")

    # T-test between alternating and non-alternating breadth/span
    if alt_bsr and nonalt_bsr:
        t_stat, t_p = stats.ttest_ind(alt_bsr, nonalt_bsr)
        bsr_test = {"t_stat": float(t_stat), "p_value": float(t_p)}
        print(f"  t-test: t={t_stat:.3f}, p={t_p:.3e}")
    else:
        bsr_test = None

    # ── 5. Breadth/span by crossing number ───────────────────────────
    cn_bsr_alt = defaultdict(list)
    cn_bsr_nonalt = defaultdict(list)
    for r in records:
        if np.isnan(r["breadth_span_ratio"]):
            continue
        cn = r["crossing_number"]
        if r["is_alternating"]:
            cn_bsr_alt[cn].append(r["breadth_span_ratio"])
        else:
            cn_bsr_nonalt[cn].append(r["breadth_span_ratio"])

    # ── 6. Correlations with other invariants ────────────────────────
    print("\nCorrelations:")

    # Span vs determinant
    spans = np.array([r["jones_span"] for r in records], dtype=float)
    dets = np.array([r["determinant"] for r in records if r["determinant"] is not None],
                    dtype=float)
    if len(dets) == len(records):
        r_span_det, p_span_det = stats.spearmanr(spans, dets)
        print(f"  Span vs determinant: rho={r_span_det:.4f}, p={p_span_det:.3e}")
    else:
        # Filter to records with determinant
        paired = [(r["jones_span"], r["determinant"]) for r in records
                  if r["determinant"] is not None]
        if len(paired) > 10:
            s, d = zip(*paired)
            r_span_det, p_span_det = stats.spearmanr(s, d)
            print(f"  Span vs determinant: rho={r_span_det:.4f}, p={p_span_det:.3e}")
        else:
            r_span_det = p_span_det = None
            print("  Span vs determinant: insufficient data")

    # Span vs Alexander degree
    paired_alex = [(r["jones_span"], r["alex_degree"]) for r in records
                   if r["alex_degree"] is not None]
    if len(paired_alex) > 10:
        s, a = zip(*paired_alex)
        r_span_alex, p_span_alex = stats.spearmanr(s, a)
        print(f"  Span vs Alexander degree: rho={r_span_alex:.4f}, p={p_span_alex:.3e}")
    else:
        r_span_alex = p_span_alex = None

    # Deficit vs log(determinant) for non-alternating knots
    paired_def_det = [(r["deficit"], np.log(r["determinant"])) for r in nonalt_knots
                      if r["determinant"] is not None and r["determinant"] > 0]
    if len(paired_def_det) > 10:
        dd, ld = zip(*paired_def_det)
        r_def_det, p_def_det = stats.spearmanr(dd, ld)
        print(f"  Deficit vs log(det) [non-alt]: rho={r_def_det:.4f}, p={p_def_det:.3e}")
    else:
        r_def_det = p_def_det = None

    # Breadth vs crossing number
    brs = np.array([r["breadth"] for r in records], dtype=float)
    cns_all = np.array([r["crossing_number"] for r in records], dtype=float)
    r_br_cn, p_br_cn = stats.spearmanr(brs, cns_all)
    print(f"  Breadth vs crossing number: rho={r_br_cn:.4f}, p={p_br_cn:.3e}")

    # ── 7. "Non-alternating penalty constant" ────────────────────────
    # For non-alternating: deficit/crossing_number
    penalty_ratios = [r["deficit"] / r["crossing_number"]
                      for r in nonalt_knots if r["crossing_number"] > 0]
    if penalty_ratios:
        mean_penalty = float(np.mean(penalty_ratios))
        std_penalty = float(np.std(penalty_ratios))
        print(f"\nNon-alternating penalty constant (deficit/cn):")
        print(f"  mean={mean_penalty:.4f}, std={std_penalty:.4f}")
    else:
        mean_penalty = std_penalty = None

    # ── 8. Alternating knots: all maximal-span? ──────────────────────
    # For alternating knots, the Jones polynomial should have full span
    # meaning every power from min to max has a nonzero coefficient
    alt_full_breadth = sum(1 for r in alt_knots
                          if r["breadth"] == r["jones_span"] + 1)
    alt_full_frac = alt_full_breadth / len(alt_knots) if alt_knots else 0
    print(f"\nAlternating knots with full breadth (no gaps): "
          f"{alt_full_breadth}/{len(alt_knots)} ({alt_full_frac:.4f})")

    nonalt_full_breadth = sum(1 for r in nonalt_knots
                              if r["breadth"] == r["jones_span"] + 1)
    nonalt_full_frac = nonalt_full_breadth / len(nonalt_knots) if nonalt_knots else 0
    print(f"Non-alternating knots with full breadth: "
          f"{nonalt_full_breadth}/{len(nonalt_knots)} ({nonalt_full_frac:.4f})")

    # ── Build output ─────────────────────────────────────────────────
    results = {
        "title": "Jones Polynomial Span and Breadth as Knot Complexity Measures",
        "n_knots": len(records),
        "n_alternating": len(alt_knots),
        "n_non_alternating": len(nonalt_knots),
        "alternating_fraction": float(alt_fraction),
        "kmt_verification": {
            "alt_deficit_zero_count": alt_deficit_zero,
            "alt_total": len(alt_knots),
            "alt_deficit_zero_fraction": float(alt_kmt_fraction),
            "alt_deficit_mean": float(np.mean(alt_deficits)) if alt_deficits else None,
            "alt_deficit_max": int(max(alt_deficits)) if alt_deficits else None,
        },
        "non_alternating_deficit": {
            "mean": mean_deficit,
            "median": median_deficit,
            "std": std_deficit,
            "distribution": {str(k): v for k, v in sorted(deficit_counts.items())}
                            if nonalt_deficits else {},
        },
        "deficit_growth_with_cn": deficit_growth,
        "deficit_by_crossing_number": {str(k): v for k, v in deficit_by_cn.items()},
        "non_alternating_penalty_constant": {
            "mean_deficit_over_cn": mean_penalty,
            "std": std_penalty,
        },
        "breadth_span_ratio": {
            "alternating_mean": float(np.mean(alt_bsr)) if alt_bsr else None,
            "alternating_std": float(np.std(alt_bsr)) if alt_bsr else None,
            "non_alternating_mean": float(np.mean(nonalt_bsr)) if nonalt_bsr else None,
            "non_alternating_std": float(np.std(nonalt_bsr)) if nonalt_bsr else None,
            "ttest": bsr_test,
        },
        "full_breadth_fraction": {
            "alternating": float(alt_full_frac),
            "non_alternating": float(nonalt_full_frac),
        },
        "correlations": {
            "span_vs_determinant": {
                "spearman_rho": float(r_span_det) if r_span_det is not None else None,
                "p_value": float(p_span_det) if p_span_det is not None else None,
            },
            "span_vs_alexander_degree": {
                "spearman_rho": float(r_span_alex) if r_span_alex is not None else None,
                "p_value": float(p_span_alex) if p_span_alex is not None else None,
            },
            "deficit_vs_log_determinant": {
                "spearman_rho": float(r_def_det) if r_def_det is not None else None,
                "p_value": float(p_def_det) if p_def_det is not None else None,
            },
            "breadth_vs_crossing_number": {
                "spearman_rho": float(r_br_cn),
                "p_value": float(p_br_cn),
            },
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
