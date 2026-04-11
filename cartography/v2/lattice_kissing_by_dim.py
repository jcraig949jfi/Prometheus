"""
Lattice Kissing Number Distribution by Dimension
=================================================
The kissing number of a lattice counts how many non-overlapping unit spheres
can simultaneously touch a central unit sphere (equivalently, the number of
shortest vectors). This analysis measures the distribution of kissing numbers
across dimensions in the LMFDB lattice database.

Key questions:
  1. Distribution of kissing numbers by dimension
  2. Does LMFDB contain the known record holders (dim 2: 6, dim 3: 12,
     dim 8: 240, dim 24: 196560)?
  3. Mean and median kissing by dimension
  4. Growth rate of kissing number with dimension

Data: cartography/lmfdb_dump/lat_lattices.json (39,293 lattices)

Output: lattice_kissing_by_dim_results.json

Usage:
    python lattice_kissing_by_dim.py
"""

import json
import time
import math
import numpy as np
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).resolve().parent / "lattice_kissing_by_dim_results.json"

# Known optimal lattice kissing numbers (proven tight)
KNOWN_RECORDS = {
    1: 2,
    2: 6,        # hexagonal lattice A2
    3: 12,       # FCC / D3
    4: 24,       # D4
    5: 40,       # D5
    6: 72,       # E6
    7: 126,      # E7
    8: 240,      # E8
    24: 196560,  # Leech lattice
}


def load_data():
    """Load lattice records, filter to those with dim and kissing."""
    with open(DATA_PATH, "r") as f:
        blob = json.load(f)
    records = blob["records"]
    valid = []
    for r in records:
        dim = r.get("dim")
        kiss = r.get("kissing")
        if dim is not None and kiss is not None:
            valid.append({"dim": int(dim), "kissing": int(kiss),
                          "label": r.get("label", ""), "name": r.get("name", "")})
    return valid


def analyse(records):
    """Run kissing-number-by-dimension analysis."""
    t0 = time.time()

    # Group by dimension
    by_dim = defaultdict(list)
    for r in records:
        by_dim[r["dim"]].append(r)

    dims_sorted = sorted(by_dim.keys())

    # --- Per-dimension statistics ---
    dim_stats = {}
    for d in dims_sorted:
        kisses = [r["kissing"] for r in by_dim[d]]
        arr = np.array(kisses)
        max_kiss = int(arr.max())
        max_label = [r["label"] for r in by_dim[d] if r["kissing"] == max_kiss][:5]
        max_name = [r["name"] for r in by_dim[d] if r["kissing"] == max_kiss and r["name"]][:5]
        dim_stats[str(d)] = {
            "count": len(kisses),
            "min": int(arr.min()),
            "max": max_kiss,
            "mean": round(float(arr.mean()), 4),
            "median": float(np.median(arr)),
            "std": round(float(arr.std()), 4),
            "max_labels": max_label,
            "max_names": max_name if max_name else None,
        }

    # --- Distribution histograms (top kissing values per dim) ---
    distributions = {}
    for d in dims_sorted:
        kisses = [r["kissing"] for r in by_dim[d]]
        counts = defaultdict(int)
        for k in kisses:
            counts[k] += 1
        # Top 15 most common
        top = sorted(counts.items(), key=lambda x: -x[1])[:15]
        distributions[str(d)] = [{"kissing": k, "count": c} for k, c in top]

    # --- Record holder comparison ---
    record_comparison = {}
    for d, known in sorted(KNOWN_RECORDS.items()):
        d_str = str(d)
        if d in by_dim:
            stats = dim_stats[d_str]
            lmfdb_max = stats["max"]
            has_record = lmfdb_max >= known
            record_comparison[d_str] = {
                "known_record": known,
                "lmfdb_max": lmfdb_max,
                "has_record_holder": has_record,
                "ratio_to_record": round(lmfdb_max / known, 6) if known > 0 else None,
                "lmfdb_count": stats["count"],
                "max_labels": stats["max_labels"],
                "max_names": stats["max_names"],
            }
        else:
            record_comparison[d_str] = {
                "known_record": known,
                "lmfdb_max": None,
                "has_record_holder": False,
                "note": f"dim {d} not present in LMFDB lattice data",
            }

    # --- Growth rate analysis ---
    # Fit log(max_kissing) vs log(dim) for dims with at least 1 lattice
    dims_for_fit = []
    max_kisses_for_fit = []
    mean_kisses_for_fit = []
    for d in dims_sorted:
        if d >= 1:
            stats = dim_stats[str(d)]
            dims_for_fit.append(d)
            max_kisses_for_fit.append(stats["max"])
            mean_kisses_for_fit.append(stats["mean"])

    growth_rate = {}
    if len(dims_for_fit) >= 3:
        log_d = np.log(np.array(dims_for_fit, dtype=float))
        log_max_k = np.log(np.array(max_kisses_for_fit, dtype=float))
        log_mean_k = np.log(np.array(mean_kisses_for_fit, dtype=float))

        # Power law: kissing ~ dim^alpha
        coeff_max = np.polyfit(log_d, log_max_k, 1)
        coeff_mean = np.polyfit(log_d, log_mean_k, 1)

        # Exponential: kissing ~ exp(beta * dim)
        d_arr = np.array(dims_for_fit, dtype=float)
        coeff_exp_max = np.polyfit(d_arr, log_max_k, 1)
        coeff_exp_mean = np.polyfit(d_arr, log_mean_k, 1)

        # R^2 for each fit
        def r_squared(y, y_pred):
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return round(1 - ss_res / ss_tot, 6) if ss_tot > 0 else None

        r2_power_max = r_squared(log_max_k, coeff_max[0] * log_d + coeff_max[1])
        r2_power_mean = r_squared(log_mean_k, coeff_mean[0] * log_d + coeff_mean[1])
        r2_exp_max = r_squared(log_max_k, coeff_exp_max[0] * d_arr + coeff_exp_max[1])
        r2_exp_mean = r_squared(log_mean_k, coeff_exp_mean[0] * d_arr + coeff_exp_mean[1])

        growth_rate = {
            "dims_used": dims_for_fit,
            "power_law_max": {
                "alpha": round(float(coeff_max[0]), 4),
                "log_prefactor": round(float(coeff_max[1]), 4),
                "interpretation": f"max_kissing ~ dim^{round(float(coeff_max[0]), 2)}",
                "R2": r2_power_max,
            },
            "power_law_mean": {
                "alpha": round(float(coeff_mean[0]), 4),
                "log_prefactor": round(float(coeff_mean[1]), 4),
                "interpretation": f"mean_kissing ~ dim^{round(float(coeff_mean[0]), 2)}",
                "R2": r2_power_mean,
            },
            "exponential_max": {
                "beta": round(float(coeff_exp_max[0]), 6),
                "log_prefactor": round(float(coeff_exp_max[1]), 4),
                "interpretation": f"max_kissing ~ exp({round(float(coeff_exp_max[0]), 4)} * dim)",
                "R2": r2_exp_max,
            },
            "exponential_mean": {
                "beta": round(float(coeff_exp_mean[0]), 6),
                "log_prefactor": round(float(coeff_exp_mean[1]), 4),
                "interpretation": f"mean_kissing ~ exp({round(float(coeff_exp_mean[0]), 4)} * dim)",
                "R2": r2_exp_mean,
            },
            "note": "Power law fits log(kissing) vs log(dim); exponential fits log(kissing) vs dim. Higher R2 = better fit."
        }

    elapsed = round(time.time() - t0, 2)

    # --- Summary ---
    total_lattices = len(records)
    dims_covered = len(dims_sorted)
    overall_max = max(r["kissing"] for r in records)
    overall_max_rec = [r for r in records if r["kissing"] == overall_max][:3]

    summary = {
        "total_lattices": total_lattices,
        "dimensions_covered": dims_covered,
        "dim_range": [dims_sorted[0], dims_sorted[-1]],
        "overall_max_kissing": overall_max,
        "overall_max_records": [{"label": r["label"], "name": r["name"], "dim": r["dim"]}
                                for r in overall_max_rec],
        "elapsed_seconds": elapsed,
    }

    return {
        "title": "Lattice Kissing Number Distribution by Dimension",
        "source": "LMFDB lat_lattices",
        "date": "2026-04-10",
        "summary": summary,
        "dim_stats": dim_stats,
        "distributions_top15_per_dim": distributions,
        "record_comparison": record_comparison,
        "growth_rate": growth_rate,
    }


def main():
    print("Loading lattice data...")
    records = load_data()
    print(f"  {len(records)} lattices with dim + kissing")

    print("Analysing kissing number distributions...")
    results = analyse(records)

    print(f"\nSummary:")
    s = results["summary"]
    print(f"  Lattices: {s['total_lattices']}")
    print(f"  Dimensions: {s['dimensions_covered']} (range {s['dim_range']})")
    print(f"  Overall max kissing: {s['overall_max_kissing']}")
    for r in s["overall_max_records"]:
        print(f"    {r['label']} (dim {r['dim']}) name={r['name']}")

    print(f"\nRecord comparison:")
    for d, info in sorted(results["record_comparison"].items(), key=lambda x: int(x[0])):
        known = info["known_record"]
        lmax = info.get("lmfdb_max")
        has = info.get("has_record_holder", False)
        tag = "YES" if has else "NO"
        if lmax is not None:
            print(f"  dim {d:>2}: known={known:>6}, LMFDB max={lmax:>6}  [{tag}]")
        else:
            print(f"  dim {d:>2}: known={known:>6}, LMFDB max=  N/A   [{tag}]")

    print(f"\nGrowth rate:")
    gr = results["growth_rate"]
    if gr:
        pm = gr["power_law_max"]
        em = gr["exponential_max"]
        print(f"  Power law (max):  {pm['interpretation']}  R2={pm['R2']}")
        print(f"  Exponential (max): {em['interpretation']}  R2={em['R2']}")
        pmn = gr["power_law_mean"]
        emn = gr["exponential_mean"]
        print(f"  Power law (mean): {pmn['interpretation']}  R2={pmn['R2']}")
        print(f"  Exponential (mean): {emn['interpretation']}  R2={emn['R2']}")

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {s['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
