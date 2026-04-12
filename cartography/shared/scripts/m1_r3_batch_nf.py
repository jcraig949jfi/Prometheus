"""Round 3, M1 — Number field batch (5 tests).
Load number_fields.json + DuckDB once, run all NF tests through frozen battery.

Tests:
  C72     NF hR/sqrt(D) moment ratio            (ANALYZED)
  C91     Galois -> disc within degree 4          (ANALYZED)
  G.R5.3  NF regulator ~ discriminant            (SURVIVED z=4.8)
  G.R5.nf NF disc: class# in knot_dets vs not   (SURVIVED z=3.5)
  G.R5.sg NF disc: class# in SG pg_orders vs not (SURVIVED z=35.7)

Machine: M1 (Skullport), 2026-04-12
Battery: v6 (F1-F27, frozen)
"""
import sys, json
import numpy as np
from pathlib import Path
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()
RESULTS = {}
N_PERM = 2000
rng = np.random.default_rng(42)

def permutation_test(real_stat, null_stats):
    null_arr = np.array(null_stats)
    p = (np.sum(null_arr >= real_stat) + 1) / (len(null_arr) + 1)
    z = (real_stat - np.mean(null_arr)) / max(np.std(null_arr), 1e-12)
    return p, z

def save_results():
    out = DATA / "shared/scripts/v2/r3_nf_batch_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nResults saved to v2/r3_nf_batch_results.json")


# ============================================================
# LOAD DATA
# ============================================================
print("Loading number_fields.json...")
nf_data = json.loads((DATA / "number_fields/data/number_fields.json").read_text(encoding="utf-8"))
print(f"  {len(nf_data)} number fields loaded")

# Parse numeric fields (stored as strings)
nf = []
for f in nf_data:
    try:
        entry = {
            "label": f.get("label", ""),
            "degree": int(f["degree"]),
            "disc_abs": abs(int(f["disc_abs"])),
            "class_number": int(f.get("class_number", 0)),
            "galois_label": f.get("galois_label", ""),
            "regulator": float(f.get("regulator", 0)),
        }
        if entry["disc_abs"] > 0:
            nf.append(entry)
    except (ValueError, TypeError):
        continue
print(f"  {len(nf)} valid entries after parsing")

# Load knot determinants for G.R5.nf
print("Loading knot determinants...")
knots_data = json.loads((DATA / "knots/data/knots.json").read_text(encoding="utf-8"))
knot_dets_small = set(k.get("determinant", 0) for k in knots_data["knots"]
                      if k.get("determinant") and 0 < k["determinant"] < 100)
print(f"  Small knot dets (0-100): {len(knot_dets_small)}")

# Load SG point group orders for G.R5.sg
print("Loading space group data...")
sg_data = json.loads((DATA / "v2/bilbao_sg_analysis_results.json").read_text(encoding="utf-8"))
pg_order_set = set(s["pg_order"] for s in sg_data["sg_table"])
print(f"  PG orders: {sorted(pg_order_set)}")

# Load EC conductors for G.R5.3
print("Loading EC conductors...")
import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)
ec_rows = con.execute("SELECT conductor FROM elliptic_curves WHERE conductor <= 50000").fetchall()
all_conds = set(int(r[0]) for r in ec_rows if r[0])
con.close()
print(f"  {len(all_conds)} unique EC conductors")


# ============================================================
# TEST 1: C72 — NF hR/sqrt(D) moment ratio
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: C72 — NF hR/sqrt(D) moment ratio (Brauer-Siegel)")
print("=" * 70)

bs_ratios = []
bs_degrees = []
for f in nf:
    if f["class_number"] > 0 and f["regulator"] > 0 and f["disc_abs"] > 1:
        ratio = f["class_number"] * f["regulator"] / np.sqrt(float(f["disc_abs"]))
        if np.isfinite(ratio) and ratio > 0:
            bs_ratios.append(ratio)
            bs_degrees.append(str(f["degree"]))

bs_ratios = np.array(bs_ratios)
print(f"  n = {len(bs_ratios)}")
print(f"  Mean hR/sqrt(D) = {np.mean(bs_ratios):.4f}")
print(f"  Median = {np.median(bs_ratios):.4f}")

# M4/M² signature
if len(bs_ratios) >= 30:
    centered = bs_ratios / np.mean(bs_ratios)
    m2 = np.mean(centered ** 2)
    m4 = np.mean(centered ** 4)
    m4m2 = m4 / m2 ** 2
    print(f"  M4/M² = {m4m2:.3f}")

    # F24 by degree
    v24, r24 = bv2.F24_variance_decomposition(bs_ratios, bs_degrees)
    v24b, r24b = bv2.F24b_metric_consistency(bs_ratios, bs_degrees)
    print(f"  F24 (degree -> ratio): {v24} (eta²={r24.get('eta_squared', 0):.4f})")
    print(f"  F24b: {v24b} (M4/M²={r24b.get('m4m2_ratio', 'N/A')})")

    # F25: transportability across degree
    # Use class_number parity as secondary
    cn_parity = ["odd" if nf[i]["class_number"] % 2 == 1 else "even"
                 for i, f in enumerate(nf) if f["class_number"] > 0 and f["regulator"] > 0 and f["disc_abs"] > 1
                 and f["class_number"] * f["regulator"] / np.sqrt(float(f["disc_abs"])) > 0][:len(bs_ratios)]
    if len(cn_parity) == len(bs_ratios):
        v25, r25 = bv2.F25_transportability(bs_ratios, bs_degrees, cn_parity)
        print(f"  F25: {v25}")
    else:
        v25, r25 = "SKIP", {}

    RESULTS["C72"] = {
        "claim": "hR/sqrt(D) (Brauer-Siegel ratio) has universal structure",
        "n": len(bs_ratios), "mean": float(np.mean(bs_ratios)), "median": float(np.median(bs_ratios)),
        "m4m2": m4m2,
        "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
        "f25": {"verdict": v25, **r25},
        "verdict": v24,
    }
else:
    RESULTS["C72"] = {"verdict": "INSUFFICIENT_DATA"}

# ============================================================
# TEST 2: C91 — Galois -> disc within degree <= 4
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: C91 — Galois -> disc within degree <= 4")
print("=" * 70)

c91_results = {}
for deg in [2, 3, 4]:
    subset = [f for f in nf if f["degree"] == deg and f["galois_label"]]
    if len(subset) < 30:
        print(f"  degree={deg}: SKIP (n={len(subset)})")
        continue

    log_disc = np.array([np.log(float(f["disc_abs"])) for f in subset])
    galois_labels = [f["galois_label"] for f in subset]
    unique_galois = set(galois_labels)
    print(f"  degree={deg}: n={len(subset)}, {len(unique_galois)} Galois groups")

    if len(unique_galois) >= 2:
        v24, r24 = bv2.F24_variance_decomposition(log_disc, galois_labels)
        v24b, r24b = bv2.F24b_metric_consistency(log_disc, galois_labels)
        print(f"    F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
        print(f"    F24b: {v24b}")

        c91_results[f"degree_{deg}"] = {
            "n": len(subset), "n_galois_groups": len(unique_galois),
            "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
        }

# Cross-degree F25
all_logdisc = np.array([np.log(float(f["disc_abs"])) for f in nf if f["degree"] <= 4 and f["galois_label"]])
all_galois = [f["galois_label"] for f in nf if f["degree"] <= 4 and f["galois_label"]]
all_deg_labels = [str(f["degree"]) for f in nf if f["degree"] <= 4 and f["galois_label"]]

if len(all_logdisc) >= 30 and len(set(all_galois)) >= 2:
    v25, r25 = bv2.F25_transportability(all_logdisc, all_galois, all_deg_labels)
    print(f"  F25 (transport across degree): {v25}")
else:
    v25, r25 = "SKIP", {}

RESULTS["C91"] = {
    "claim": "Galois group predicts discriminant within fixed degree",
    "per_degree": c91_results,
    "f25": {"verdict": v25, **r25},
    "verdict": "ANALYZED",
}

# ============================================================
# TEST 3: G.R5.3 — NF regulator ~ EC conductor density
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: G.R5.3 — NF regulator ~ EC conductor density")
print("=" * 70)

regs = [(f["regulator"], f["disc_abs"]) for f in nf
        if f["regulator"] > 0 and f["disc_abs"] <= 5000]
print(f"  NF with regulator + disc <= 5000: {len(regs)}")

if len(regs) >= 30:
    reg_vals = np.array([r[0] for r in regs])
    disc_vals = np.array([r[1] for r in regs])

    # EC conductor density: count of conductors within ±50
    ec_density = np.array([sum(1 for c in all_conds if abs(c - d) < 50) for d in disc_vals])

    real_r = abs(stats.spearmanr(reg_vals, ec_density)[0])
    null_r = [abs(stats.spearmanr(reg_vals, rng.permutation(ec_density))[0]) for _ in range(N_PERM)]
    p, z = permutation_test(real_r, null_r)
    print(f"  Spearman |r|(regulator, EC density) = {real_r:.4f}, p = {p:.6f}, z = {z:.1f}")

    # F24: bin regulators
    reg_bins = np.digitize(np.log1p(reg_vals), bins=np.linspace(0, np.log1p(reg_vals.max()), 6))
    reg_labels = [f"reg_bin_{b}" for b in reg_bins]
    v24, r24 = bv2.F24_variance_decomposition(ec_density, reg_labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

    RESULTS["G.R5.3"] = {
        "claim": "NF regulator ~ EC conductor density",
        "n": len(regs), "spearman_r": real_r, "p": p, "z": z,
        "f24": {"verdict": v24, **r24},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }
else:
    RESULTS["G.R5.3"] = {"verdict": "SKIP", "reason": "insufficient NF with small disc"}

# ============================================================
# TEST 4: G.R5.nf — NF disc: class# in knot_dets vs not
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: G.R5.nf — NF disc: class# in knot_dets vs not")
print("=" * 70)

nf_cn_is_det = [np.log1p(f["disc_abs"]) for f in nf if f["class_number"] in knot_dets_small]
nf_cn_not_det = [np.log1p(f["disc_abs"]) for f in nf if f["class_number"] not in knot_dets_small and f["class_number"] > 0]
print(f"  class#  in  knot dets: {len(nf_cn_is_det)}, class#  not in  knot dets: {len(nf_cn_not_det)}")

if len(nf_cn_is_det) >= 10 and len(nf_cn_not_det) >= 10:
    # Cap at 2000 per group for speed
    a = np.array(nf_cn_is_det[:2000])
    b = np.array(nf_cn_not_det[:2000])
    real_d = abs(np.mean(a) - np.mean(b))
    combined = np.concatenate([a, b])
    null_d = []
    for _ in range(N_PERM):
        rng.shuffle(combined)
        null_d.append(abs(np.mean(combined[:len(a)]) - np.mean(combined[len(a):])))
    p, z = permutation_test(real_d, null_d)
    print(f"  log(disc): in={np.mean(a):.3f}, not={np.mean(b):.3f}, |diff|={real_d:.3f}")
    print(f"  p = {p:.6f}, z = {z:.1f}")

    # F24
    labels = ["in_knot_det"] * len(a) + ["not_in_knot_det"] * len(b)
    vals = np.concatenate([a, b])
    v24, r24 = bv2.F24_variance_decomposition(vals, labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

    RESULTS["G.R5.nf"] = {
        "claim": "NF disc differs when class#  in  small knot determinants",
        "n_in": len(a), "n_not": len(b),
        "mean_in": float(np.mean(a)), "mean_not": float(np.mean(b)),
        "diff": real_d, "p": p, "z": z,
        "f24": {"verdict": v24, **r24},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }
else:
    RESULTS["G.R5.nf"] = {"verdict": "SKIP"}

# ============================================================
# TEST 5: G.R5.sg — NF disc: class# in SG point_group_orders vs not
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: G.R5.sg — NF disc: class# in SG pg_orders vs not")
print("=" * 70)

nf_cn_in_pg = [np.log1p(f["disc_abs"]) for f in nf if f["class_number"] in pg_order_set]
nf_cn_not_pg = [np.log1p(f["disc_abs"]) for f in nf if f["class_number"] not in pg_order_set and f["class_number"] > 0]
print(f"  class#  in  PG orders: {len(nf_cn_in_pg)}, class#  not in  PG orders: {len(nf_cn_not_pg)}")

if len(nf_cn_in_pg) >= 10 and len(nf_cn_not_pg) >= 10:
    a = np.array(nf_cn_in_pg[:2000])
    b = np.array(nf_cn_not_pg[:2000])
    real_d = abs(np.mean(a) - np.mean(b))
    combined = np.concatenate([a, b])
    null_d = []
    for _ in range(N_PERM):
        rng.shuffle(combined)
        null_d.append(abs(np.mean(combined[:len(a)]) - np.mean(combined[len(a):])))
    p, z = permutation_test(real_d, null_d)
    print(f"  log(disc): in_pg={np.mean(a):.3f}, not_pg={np.mean(b):.3f}, |diff|={real_d:.3f}")
    print(f"  p = {p:.6f}, z = {z:.1f}")

    labels = ["in_pg_order"] * len(a) + ["not_in_pg_order"] * len(b)
    vals = np.concatenate([a, b])
    v24, r24 = bv2.F24_variance_decomposition(vals, labels)
    v24b, r24b = bv2.F24b_metric_consistency(vals, labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
    print(f"  F24b: {v24b}")

    RESULTS["G.R5.sg"] = {
        "claim": "NF disc differs when class#  in  SG point group orders",
        "n_in": len(a), "n_not": len(b),
        "mean_in": float(np.mean(a)), "mean_not": float(np.mean(b)),
        "diff": real_d, "p": p, "z": z,
        "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }
else:
    RESULTS["G.R5.sg"] = {"verdict": "SKIP"}


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("NUMBER FIELD BATCH SUMMARY")
print("=" * 70)

for test_id, result in RESULTS.items():
    v = result.get("verdict", "?")
    claim = result.get("claim", "")
    eta = result.get("f24", {}).get("eta_squared", "")
    eta_str = f" eta²={eta:.4f}" if isinstance(eta, (int, float)) else ""
    print(f"  {test_id:12s} {v:20s} {claim}{eta_str}")

save_results()
print(f"\nNumber field batch complete: {len(RESULTS)} tests")
