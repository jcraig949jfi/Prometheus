"""
MP x Bilbao: Wyckoff Position Occupancy Patterns
Challenge 333 — Prometheus cartography v2

For each MP structure's space group, look up Bilbao Wyckoff data and compute:
  (a) Wyckoff count and max multiplicity per SG
  (b) nsites vs Wyckoff count correlation
  (c) Most Wyckoff-constrained SGs (fewest positions)
  (d) Wyckoff richness vs formation energy correlation
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import math

# ---------- paths (relative to repo root) ----------
REPO = Path(__file__).resolve().parents[2]
MP_PATH = REPO / "cartography" / "physics" / "data" / "materials_project_10k.json"
BILBAO_DIR = REPO / "cartography" / "physics" / "data" / "bilbao"
OUT_JSON = Path(__file__).resolve().parent / "mp_bilbao_wyckoff_results.json"


def load_bilbao():
    """Load all Bilbao SG files into {sg_number: data}."""
    sgs = {}
    for fn in os.listdir(BILBAO_DIR):
        if fn.startswith("sg_") and fn.endswith(".json"):
            sg_num = int(fn[3:-5])
            with open(BILBAO_DIR / fn) as f:
                sgs[sg_num] = json.load(f)
    return sgs


def wyckoff_multiplicities(sg_data):
    """Return list of (index, multiplicity) for each Wyckoff position."""
    pgo = sg_data["point_group_order"]
    result = []
    for wp in sg_data["wyckoff_positions"]:
        mult = pgo // wp["stabilizer_order"]
        result.append({"index": wp["index"], "multiplicity": mult,
                        "stabilizer_order": wp["stabilizer_order"]})
    return result


def pearson_r(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom = math.sqrt(sxx * syy)
    if denom == 0:
        return 0.0
    return sxy / denom


def main():
    # ---- Load data ----
    with open(MP_PATH) as f:
        mp_data = json.load(f)
    bilbao = load_bilbao()

    # ---- Per-SG Wyckoff analysis ----
    sg_wyckoff = {}  # sg_num -> {num_positions, max_mult, min_mult, multiplicities}
    for sg_num, sg_data in sorted(bilbao.items()):
        mults = wyckoff_multiplicities(sg_data)
        mult_vals = [m["multiplicity"] for m in mults]
        sg_wyckoff[sg_num] = {
            "num_positions": sg_data["num_wyckoff_positions"],
            "point_group_order": sg_data["point_group_order"],
            "max_multiplicity": max(mult_vals),
            "min_multiplicity": min(mult_vals),
            "multiplicities": mult_vals,
        }

    # ---- Match MP structures to Bilbao ----
    mp_matched = []
    for entry in mp_data:
        sg = entry["spacegroup_number"]
        if sg not in sg_wyckoff:
            continue
        sw = sg_wyckoff[sg]
        mp_matched.append({
            "material_id": entry["material_id"],
            "formula": entry["formula"],
            "spacegroup_number": sg,
            "nsites": entry["nsites"],
            "formation_energy_per_atom": entry["formation_energy_per_atom"],
            "band_gap": entry["band_gap"],
            "wyckoff_count": sw["num_positions"],
            "max_wyckoff_mult": sw["max_multiplicity"],
            "min_wyckoff_mult": sw["min_multiplicity"],
            "point_group_order": sw["point_group_order"],
        })

    print(f"Matched {len(mp_matched)}/{len(mp_data)} MP entries to Bilbao SGs")

    # ---- (a) Max Wyckoff multiplicity vs nsites ----
    xs_maxmult = [m["max_wyckoff_mult"] for m in mp_matched]
    ys_nsites = [m["nsites"] for m in mp_matched]
    r_maxmult_nsites = pearson_r(xs_maxmult, ys_nsites)
    print(f"\n(a) Pearson r(max_wyckoff_mult, nsites) = {r_maxmult_nsites:.4f}")

    # ---- (b) nsites vs wyckoff_count ----
    xs_wcount = [m["wyckoff_count"] for m in mp_matched]
    r_wcount_nsites = pearson_r(xs_wcount, ys_nsites)
    print(f"(b) Pearson r(wyckoff_count, nsites) = {r_wcount_nsites:.4f}")

    # ---- Per-SG aggregated stats ----
    sg_stats = defaultdict(lambda: {"nsites": [], "fe": [], "count": 0})
    for m in mp_matched:
        sg = m["spacegroup_number"]
        sg_stats[sg]["nsites"].append(m["nsites"])
        sg_stats[sg]["fe"].append(m["formation_energy_per_atom"])
        sg_stats[sg]["count"] += 1
        sg_stats[sg]["wyckoff_count"] = m["wyckoff_count"]
        sg_stats[sg]["max_mult"] = m["max_wyckoff_mult"]

    # ---- (c) Most Wyckoff-constrained SGs (fewest positions) ----
    # Among SGs that appear in MP data
    constrained = sorted(sg_stats.items(), key=lambda x: x[1]["wyckoff_count"])
    print("\n(c) Most Wyckoff-constrained SGs (fewest positions) in MP data:")
    print(f"{'SG':>5} {'Wyckoff#':>8} {'MaxMult':>8} {'MP count':>9} {'Avg nsites':>11}")
    for sg, st in constrained[:15]:
        avg_ns = sum(st["nsites"]) / len(st["nsites"])
        print(f"{sg:>5} {st['wyckoff_count']:>8} {st['max_mult']:>8} {st['count']:>9} {avg_ns:>11.1f}")

    # ---- Most Wyckoff-rich SGs ----
    rich = sorted(sg_stats.items(), key=lambda x: x[1]["wyckoff_count"], reverse=True)
    print("\nMost Wyckoff-rich SGs (most positions) in MP data:")
    print(f"{'SG':>5} {'Wyckoff#':>8} {'MaxMult':>8} {'MP count':>9} {'Avg nsites':>11}")
    for sg, st in rich[:15]:
        avg_ns = sum(st["nsites"]) / len(st["nsites"])
        print(f"{sg:>5} {st['wyckoff_count']:>8} {st['max_mult']:>8} {st['count']:>9} {avg_ns:>11.1f}")

    # ---- (d) Wyckoff richness vs formation energy ----
    xs_wcount_all = [m["wyckoff_count"] for m in mp_matched]
    ys_fe = [m["formation_energy_per_atom"] for m in mp_matched]
    r_wcount_fe = pearson_r(xs_wcount_all, ys_fe)
    print(f"\n(d) Pearson r(wyckoff_count, formation_energy) = {r_wcount_fe:.4f}")

    # Also per-SG median formation energy vs wyckoff_count
    sg_median_fe = []
    sg_wcount_list = []
    for sg, st in sg_stats.items():
        fes = sorted(st["fe"])
        median_fe = fes[len(fes) // 2]
        sg_median_fe.append(median_fe)
        sg_wcount_list.append(st["wyckoff_count"])
    r_sg_wcount_medfe = pearson_r(sg_wcount_list, sg_median_fe)
    print(f"    Per-SG Pearson r(wyckoff_count, median_fe) = {r_sg_wcount_medfe:.4f}")

    # ---- Additional: point_group_order vs formation energy ----
    xs_pgo = [m["point_group_order"] for m in mp_matched]
    r_pgo_fe = pearson_r(xs_pgo, ys_fe)
    print(f"    Pearson r(point_group_order, formation_energy) = {r_pgo_fe:.4f}")

    # ---- Global Wyckoff multiplicity distribution across all 230 SGs ----
    all_mults = []
    for sg_num in sorted(sg_wyckoff.keys()):
        all_mults.extend(sg_wyckoff[sg_num]["multiplicities"])
    mult_counter = Counter(all_mults)
    print(f"\nGlobal Wyckoff multiplicity distribution (all 230 SGs, {len(all_mults)} positions):")
    for mult, count in sorted(mult_counter.items()):
        print(f"  mult={mult:>3}: {count:>4} positions ({100*count/len(all_mults):.1f}%)")

    # ---- Most common Wyckoff position type (by multiplicity) in MP-used SGs ----
    mp_sg_mult_weighted = Counter()
    for m in mp_matched:
        sg = m["spacegroup_number"]
        for mult in sg_wyckoff[sg]["multiplicities"]:
            mp_sg_mult_weighted[mult] += 1
    print(f"\nMP-weighted Wyckoff multiplicity (each MP entry contributes its SG's full set):")
    for mult, count in mp_sg_mult_weighted.most_common(10):
        print(f"  mult={mult:>3}: {count:>6} (weighted)")

    # ---- Build results ----
    results = {
        "meta": {
            "description": "MP x Bilbao Wyckoff Position Occupancy Patterns",
            "challenge": 333,
            "mp_entries": len(mp_data),
            "matched": len(mp_matched),
            "unique_sgs_in_mp": len(sg_stats),
            "bilbao_sgs_total": len(bilbao),
        },
        "correlations": {
            "max_wyckoff_mult_vs_nsites": round(r_maxmult_nsites, 4),
            "wyckoff_count_vs_nsites": round(r_wcount_nsites, 4),
            "wyckoff_count_vs_formation_energy": round(r_wcount_fe, 4),
            "per_sg_wyckoff_count_vs_median_fe": round(r_sg_wcount_medfe, 4),
            "point_group_order_vs_formation_energy": round(r_pgo_fe, 4),
        },
        "most_constrained_sgs": [
            {
                "sg": sg,
                "wyckoff_count": st["wyckoff_count"],
                "max_multiplicity": st["max_mult"],
                "mp_count": st["count"],
                "avg_nsites": round(sum(st["nsites"]) / len(st["nsites"]), 1),
                "avg_formation_energy": round(sum(st["fe"]) / len(st["fe"]), 4),
            }
            for sg, st in constrained[:15]
        ],
        "most_rich_sgs": [
            {
                "sg": sg,
                "wyckoff_count": st["wyckoff_count"],
                "max_multiplicity": st["max_mult"],
                "mp_count": st["count"],
                "avg_nsites": round(sum(st["nsites"]) / len(st["nsites"]), 1),
                "avg_formation_energy": round(sum(st["fe"]) / len(st["fe"]), 4),
            }
            for sg, st in rich[:15]
        ],
        "wyckoff_multiplicity_distribution": {
            str(mult): count for mult, count in sorted(mult_counter.items())
        },
        "per_sg_wyckoff_summary": {
            str(sg): {
                "num_positions": sw["num_positions"],
                "point_group_order": sw["point_group_order"],
                "max_multiplicity": sw["max_multiplicity"],
                "min_multiplicity": sw["min_multiplicity"],
            }
            for sg, sw in sorted(sg_wyckoff.items())
            if sg in sg_stats
        },
    }

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")


if __name__ == "__main__":
    main()
