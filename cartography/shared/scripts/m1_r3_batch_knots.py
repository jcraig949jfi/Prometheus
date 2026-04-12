"""Round 3, M1 — Knot batch (9 tests).
Load knots.json once, run all knot tests through frozen battery F1-F27.

Tests:
  G.R1.3  det ~ max Alexander coeff           (SURVIVED z=83)
  G.R1.8  crossing: det-is-conductor vs not   (SURVIVED z=3.4)
  G.R4.6  Alexander(-1) ~ Jones(-1)           (SURVIVED z=24.8)
  G.R4.5  max Jones coeff ~ determinant       (SURVIVED z=23.9)
  C67     Alexander polynomial recurrence BM  (0% success)
  C84     Knot det -> Alexander enrichment     (ANALYZED)
  C94     Knot Jones mod-p fingerprint        (In progress)
  C17     Knot -> crystal enrichment           (PARKED/KILLED)
  G.alex  Alexander entropy by crossing       (SURVIVED z=6.8)

Machine: M1 (Skullport), 2026-04-12
Battery: v6 (F1-F27, frozen)
"""
import sys, json, time
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2
from battery_unified import UnifiedBattery

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()
ub = UnifiedBattery()

RESULTS = {}
N_PERM = 2000

def permutation_test(real_stat, null_stats):
    """Compute p-value and z-score from permutation null."""
    null_arr = np.array(null_stats)
    p = (np.sum(null_arr >= real_stat) + 1) / (len(null_arr) + 1)
    z = (real_stat - np.mean(null_arr)) / max(np.std(null_arr), 1e-12)
    return p, z

def save_results():
    out = DATA / "shared/scripts/v2/r3_knot_batch_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nResults saved to v2/r3_knot_batch_results.json")


# ============================================================
# LOAD DATA
# ============================================================
print("Loading knots.json...")
knots_data = json.loads((DATA / "knots/data/knots.json").read_text(encoding="utf-8"))
knots = knots_data["knots"]
print(f"  {len(knots)} knots loaded")

# Pre-filter useful subsets
knots_with_alex = [k for k in knots if k.get("alex_coeffs") and k.get("determinant") and k["determinant"] > 0]
knots_with_jones = [k for k in knots if k.get("jones_coeffs") and k.get("determinant") and k["determinant"] > 0]
knots_with_both = [k for k in knots if k.get("alex_coeffs") and k.get("jones_coeffs")]
knots_with_cross = [k for k in knots if k.get("crossing_number") and k["crossing_number"] > 0]
print(f"  alex+det: {len(knots_with_alex)}, jones+det: {len(knots_with_jones)}, "
      f"both: {len(knots_with_both)}, crossing: {len(knots_with_cross)}")

# Load EC conductors for G.R1.8
print("Loading EC conductors from DuckDB...")
import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)
ec_rows = con.execute("""
    SELECT conductor, rank FROM elliptic_curves WHERE rank IS NOT NULL AND conductor <= 50000
""").fetchall()
conds_r0 = [int(r[0]) for r in ec_rows if r[1] == 0]
conds_r1 = [int(r[0]) for r in ec_rows if r[1] == 1]
cond_set = set(conds_r0 + conds_r1)
con.close()
print(f"  EC conductors: {len(cond_set)} unique (rank-0: {len(conds_r0)}, rank-1: {len(conds_r1)})")

rng = np.random.default_rng(42)

# ============================================================
# TEST 1: G.R1.3 — det ~ max Alexander coeff
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: G.R1.3 — det ~ max Alexander coeff")
print("=" * 70)

det_for_alex = np.array([k["determinant"] for k in knots_with_alex])
max_alex = np.array([max(abs(c) for c in k["alex_coeffs"]) for k in knots_with_alex])

real_r = abs(stats.spearmanr(det_for_alex, max_alex)[0])
null_r = [abs(stats.spearmanr(det_for_alex, rng.permutation(max_alex))[0]) for _ in range(N_PERM)]
p, z = permutation_test(real_r, null_r)
print(f"  Spearman |r| = {real_r:.4f}, p = {p:.6f}, z = {z:.1f}")

# F24: variance decomposition (bin determinants)
det_bins = np.digitize(np.log1p(det_for_alex), bins=np.linspace(0, np.log1p(det_for_alex.max()), 8))
det_labels = [f"bin_{b}" for b in det_bins]
v24, r24 = bv2.F24_variance_decomposition(max_alex, det_labels)
v24b, r24b = bv2.F24b_metric_consistency(max_alex, det_labels)
print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
print(f"  F24b: {v24b} (M4/M²={r24b.get('m4m2_ratio', 'N/A')})")

RESULTS["G.R1.3"] = {
    "claim": "det ~ max Alexander coeff",
    "n": len(det_for_alex), "spearman_r": real_r, "p": p, "z": z,
    "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}

# ============================================================
# TEST 2: G.R1.8 — crossing: det-is-conductor vs not
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: G.R1.8 — crossing: det-is-conductor vs not")
print("=" * 70)

knots_cross_det = [k for k in knots if k.get("crossing_number") and k["crossing_number"] > 0 and k.get("determinant")]
cross_in = np.array([k["crossing_number"] for k in knots_cross_det if k["determinant"] in cond_set])
cross_out = np.array([k["crossing_number"] for k in knots_cross_det if k["determinant"] not in cond_set])
print(f"  det in conductors: {len(cross_in)}, det not in conductors: {len(cross_out)}")

if len(cross_in) >= 10 and len(cross_out) >= 10:
    real_d = abs(np.mean(cross_in) - np.mean(cross_out))
    combined = np.concatenate([cross_in, cross_out])
    null_d = []
    for _ in range(N_PERM):
        rng.shuffle(combined)
        null_d.append(abs(np.mean(combined[:len(cross_in)]) - np.mean(combined[len(cross_in):])))
    p, z = permutation_test(real_d, null_d)
    print(f"  Mean crossing: in={np.mean(cross_in):.2f}, out={np.mean(cross_out):.2f}")
    print(f"  |diff| = {real_d:.3f}, p = {p:.6f}, z = {z:.1f}")

    labels = ["in_cond"] * len(cross_in) + ["not_cond"] * len(cross_out)
    all_cross = np.concatenate([cross_in, cross_out])
    v24, r24 = bv2.F24_variance_decomposition(all_cross, labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

    RESULTS["G.R1.8"] = {
        "claim": "crossing differs: det-is-conductor vs not",
        "n_in": len(cross_in), "n_out": len(cross_out),
        "mean_in": float(np.mean(cross_in)), "mean_out": float(np.mean(cross_out)),
        "diff": real_d, "p": p, "z": z,
        "f24": {"verdict": v24, **r24},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }
else:
    print("  SKIP: insufficient data")
    RESULTS["G.R1.8"] = {"verdict": "SKIP", "reason": "insufficient crossing+det data"}

# ============================================================
# TEST 3: G.R4.6 — Alexander(-1) ~ Jones(-1)
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: G.R4.6 — Alexander(-1) ~ Jones(-1)")
print("=" * 70)

alex_neg1 = []
jones_neg1 = []
for k in knots_with_both:
    ac = k["alex_coeffs"]
    jc = k["jones_coeffs"]
    if ac and jc:
        a_val = abs(sum(c * ((-1) ** i) for i, c in enumerate(ac)))
        j_val = abs(sum(c * ((-1) ** i) for i, c in enumerate(jc)))
        alex_neg1.append(a_val)
        jones_neg1.append(j_val)

alex_neg1 = np.array(alex_neg1)
jones_neg1 = np.array(jones_neg1)
print(f"  n = {len(alex_neg1)}")

if len(alex_neg1) >= 30:
    real_r = abs(stats.spearmanr(alex_neg1, jones_neg1)[0])
    null_r = [abs(stats.spearmanr(alex_neg1, rng.permutation(jones_neg1))[0]) for _ in range(N_PERM)]
    p, z = permutation_test(real_r, null_r)
    print(f"  Spearman |r| = {real_r:.4f}, p = {p:.6f}, z = {z:.1f}")

    # F24: bin Alexander(-1) values, test if Jones(-1) varies
    a_bins = np.digitize(np.log1p(alex_neg1), bins=np.linspace(0, np.log1p(alex_neg1.max()), 6))
    a_labels = [f"alex_bin_{b}" for b in a_bins]
    v24, r24 = bv2.F24_variance_decomposition(jones_neg1, a_labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

    RESULTS["G.R4.6"] = {
        "claim": "Alexander(-1) ~ Jones(-1)",
        "n": len(alex_neg1), "spearman_r": real_r, "p": p, "z": z,
        "f24": {"verdict": v24, **r24},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }
else:
    RESULTS["G.R4.6"] = {"verdict": "SKIP", "reason": "insufficient data with both polys"}

# ============================================================
# TEST 4: G.R4.5 — max Jones coeff ~ determinant
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: G.R4.5 — max Jones coeff ~ determinant")
print("=" * 70)

dets_j = np.array([k["determinant"] for k in knots_with_jones])
max_jones = np.array([max(abs(c) for c in k["jones_coeffs"]) for k in knots_with_jones])
print(f"  n = {len(dets_j)}")

real_r = abs(stats.spearmanr(dets_j, max_jones)[0])
null_r = [abs(stats.spearmanr(dets_j, rng.permutation(max_jones))[0]) for _ in range(N_PERM)]
p, z = permutation_test(real_r, null_r)
print(f"  Spearman |r| = {real_r:.4f}, p = {p:.6f}, z = {z:.1f}")

# F24
det_bins = np.digitize(np.log1p(dets_j), bins=np.linspace(0, np.log1p(dets_j.max()), 8))
det_labels = [f"bin_{b}" for b in det_bins]
v24, r24 = bv2.F24_variance_decomposition(max_jones, det_labels)
v24b, r24b = bv2.F24b_metric_consistency(max_jones, det_labels)
print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
print(f"  F24b: {v24b}")

RESULTS["G.R4.5"] = {
    "claim": "max Jones coeff ~ determinant",
    "n": len(dets_j), "spearman_r": real_r, "p": p, "z": z,
    "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}

# ============================================================
# TEST 5: C67 — Alexander polynomial recurrence (BM)
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: C67 — Alexander polynomial recurrence (BM)")
print("=" * 70)

def test_linear_recurrence(seq, max_order=5, residual_threshold=0.01):
    seq = np.array(seq, dtype=float)
    if len(seq) < max_order + 10:
        return False, 0, 1.0
    best_order, best_residual = 0, 1.0
    for k in range(1, max_order + 1):
        n = len(seq) - k
        if n < k + 5:
            continue
        X = np.column_stack([seq[k - j - 1: k - j - 1 + n] for j in range(k)])
        y = seq[k: k + n]
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        except np.linalg.LinAlgError:
            continue
        predicted = X @ coeffs
        ss_res = np.sum((y - predicted) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        if ss_tot == 0:
            return True, 1, 0.0
        relative_residual = ss_res / ss_tot
        if relative_residual < best_residual:
            best_residual = relative_residual
            best_order = k
    return best_residual < residual_threshold, best_order, best_residual

rec_count = 0
rec_orders = []
residuals = []
n_tested = 0

for k in knots:
    ac = k.get("alex_coeffs")
    if not ac or len(ac) < 15:
        continue
    n_tested += 1
    is_rec, order, resid = test_linear_recurrence(ac, max_order=5)
    residuals.append(resid)
    if is_rec:
        rec_count += 1
        rec_orders.append(order)

rec_rate = rec_count / max(n_tested, 1)
print(f"  Tested: {n_tested} knots with >=15 Alexander coefficients")
print(f"  Recurrent: {rec_count} ({rec_rate*100:.1f}%)")
print(f"  Prior: 0% success")
if rec_orders:
    order_dist = defaultdict(int)
    for o in rec_orders:
        order_dist[o] += 1
    print(f"  Order distribution: {dict(sorted(order_dist.items()))}")

RESULTS["C67"] = {
    "claim": "Alexander polynomial satisfies linear recurrence (BM)",
    "n_tested": n_tested, "n_recurrent": rec_count, "rate": rec_rate,
    "order_distribution": dict(sorted(defaultdict(int, {o: rec_orders.count(o) for o in set(rec_orders)}).items())) if rec_orders else {},
    "verdict": "KILLED" if rec_rate < 0.05 else "TENDENCY" if rec_rate < 0.2 else "LAW",
}

# ============================================================
# TEST 6: C84 — Knot det -> Alexander enrichment
# ============================================================
print("\n" + "=" * 70)
print("TEST 6: C84 — Knot det -> Alexander enrichment")
print("=" * 70)

mean_alex_mag = np.array([np.mean(np.abs(k["alex_coeffs"])) for k in knots_with_alex])
det_vals = np.array([k["determinant"] for k in knots_with_alex])

# Correlation
real_r = abs(stats.spearmanr(det_vals, mean_alex_mag)[0])
null_r = [abs(stats.spearmanr(det_vals, rng.permutation(mean_alex_mag))[0]) for _ in range(N_PERM)]
p, z = permutation_test(real_r, null_r)
print(f"  n = {len(det_vals)}")
print(f"  Spearman |r| = {real_r:.4f}, p = {p:.6f}, z = {z:.1f}")

# F24: bin by det quartiles
det_quartiles = np.digitize(det_vals, bins=np.quantile(det_vals, [0.25, 0.5, 0.75]))
det_q_labels = [f"Q{q}" for q in det_quartiles]
v24, r24 = bv2.F24_variance_decomposition(mean_alex_mag, det_q_labels)
v24b, r24b = bv2.F24b_metric_consistency(mean_alex_mag, det_q_labels)
print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
print(f"  F24b: {v24b}")

RESULTS["C84"] = {
    "claim": "Knot det -> Alexander coefficient magnitude",
    "n": len(det_vals), "spearman_r": real_r, "p": p, "z": z,
    "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}

# ============================================================
# TEST 7: C94 — Knot Jones mod-p fingerprint
# ============================================================
print("\n" + "=" * 70)
print("TEST 7: C94 — Knot Jones mod-p fingerprint")
print("=" * 70)

primes_to_test = [2, 3, 5, 7, 11, 13, 17, 19, 23]
jones_knots = [k for k in knots if k.get("jones_coeffs") and len(k["jones_coeffs"]) >= 3]
print(f"  Knots with Jones coeffs: {len(jones_knots)}")

fingerprint_results = {}
for p_val in primes_to_test:
    # For each knot: count how many residue classes mod p appear in Jones coefficients
    coverages = []
    for k in jones_knots:
        residues = set(c % p_val for c in k["jones_coeffs"] if c != 0)
        coverage = len(residues) / p_val  # fraction of residue classes hit
        coverages.append(coverage)

    coverages = np.array(coverages)
    starvation_rate = np.mean(coverages < 0.5)  # fraction with <50% coverage
    print(f"  p={p_val}: mean coverage={np.mean(coverages):.3f}, starvation rate={starvation_rate:.3f}")

    # F24: does crossing number predict coverage?
    jones_cross = [k.get("crossing_number", 0) for k in jones_knots]
    has_cross = [i for i, c in enumerate(jones_cross) if c > 0]
    if len(has_cross) > 30:
        cross_labels = [f"cn_{jones_cross[i]}" for i in has_cross]
        cov_subset = coverages[has_cross]
        v24_p, r24_p = bv2.F24_variance_decomposition(cov_subset, cross_labels)
        fingerprint_results[f"p={p_val}"] = {
            "mean_coverage": float(np.mean(coverages)),
            "starvation_rate": float(starvation_rate),
            "f24_crossing": {"verdict": v24_p, "eta_squared": r24_p.get("eta_squared", 0)},
        }
    else:
        fingerprint_results[f"p={p_val}"] = {
            "mean_coverage": float(np.mean(coverages)),
            "starvation_rate": float(starvation_rate),
        }

# F24: does determinant predict mod-p coverage (aggregate across primes)?
agg_coverage = []
det_labels_fp = []
for k in jones_knots:
    if k.get("determinant") and k["determinant"] > 0:
        total_cov = np.mean([len(set(c % p for c in k["jones_coeffs"] if c != 0)) / p for p in [2, 3, 5, 7]])
        agg_coverage.append(total_cov)
        d = k["determinant"]
        det_labels_fp.append("small" if d < 50 else "medium" if d < 500 else "large")

if len(agg_coverage) >= 30:
    v24, r24 = bv2.F24_variance_decomposition(np.array(agg_coverage), det_labels_fp)
    print(f"  F24 (det -> aggregate coverage): {v24} (eta²={r24.get('eta_squared', 0):.4f})")
    fingerprint_results["f24_det_aggregate"] = {"verdict": v24, **r24}

RESULTS["C94"] = {
    "claim": "Jones mod-p fingerprint encodes knot structure",
    "n": len(jones_knots), "primes_tested": primes_to_test,
    "per_prime": fingerprint_results,
    "verdict": "ANALYZED",
}

# ============================================================
# TEST 8: C17 — Knot -> crystal enrichment (PARKED/KILLED)
# ============================================================
print("\n" + "=" * 70)
print("TEST 8: C17 — Knot -> crystal enrichment (PARKED)")
print("=" * 70)

# Prior: KILLED — Collatz connection was false. Test if knot determinants
# appear as space group numbers at enriched rate.
sg_numbers = set(range(1, 231))  # 230 space groups
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 0)
overlap = knot_dets & sg_numbers
print(f"  Knot determinants: {len(knot_dets)}, SG numbers: {len(sg_numbers)}")
print(f"  Overlap: {len(overlap)} (knot dets that are also SG numbers)")

# Expected overlap by chance: how many integers 1-230 appear as knot dets?
expected = len([d for d in range(1, 231) if d in knot_dets])
# Test enrichment
det_list = sorted(knot_dets)
max_det = max(det_list)
random_overlaps = []
for _ in range(N_PERM):
    random_set = set(rng.choice(range(1, max_det + 1), size=len(sg_numbers), replace=False))
    random_overlaps.append(len(knot_dets & random_set))

real_overlap = len(overlap)
p, z = permutation_test(real_overlap, random_overlaps)
print(f"  Enrichment: {real_overlap}/{len(sg_numbers)} ({real_overlap/len(sg_numbers)*100:.1f}%)")
print(f"  Null mean: {np.mean(random_overlaps):.1f}, p = {p:.4f}, z = {z:.1f}")

RESULTS["C17"] = {
    "claim": "Knot determinants enriched in space group numbers",
    "overlap": real_overlap, "n_sg": len(sg_numbers), "n_knot_dets": len(knot_dets),
    "p": p, "z": z,
    "verdict": "KILLED" if p > 0.05 else "TENDENCY",
    "note": "Originally PARKED/KILLED (Collatz connection false). Reframed as SG overlap test.",
}

# ============================================================
# TEST 9: G.alex — Alexander entropy by crossing (7,8,9,10)
# ============================================================
print("\n" + "=" * 70)
print("TEST 9: G.alex — Alexander entropy by crossing (7,8,9,10)")
print("=" * 70)

def shannon_entropy(coeffs):
    ac = np.abs(np.array(coeffs, dtype=float)) + 0.01
    p_dist = ac / ac.sum()
    return -np.sum(p_dist * np.log2(p_dist))

# Compute entropy for all knots with alex_coeffs and crossing_number
entropy_by_crossing = defaultdict(list)
all_entropies = []
all_crossing_labels = []

for k in knots:
    if k.get("alex_coeffs") and k.get("crossing_number") and k["crossing_number"] > 0:
        ent = shannon_entropy(k["alex_coeffs"])
        entropy_by_crossing[k["crossing_number"]].append(ent)
        all_entropies.append(ent)
        all_crossing_labels.append(str(k["crossing_number"]))

print(f"  Total knots with entropy+crossing: {len(all_entropies)}")
for cn in [7, 8, 9, 10]:
    vals = entropy_by_crossing.get(cn, [])
    if vals:
        print(f"  cn={cn}: n={len(vals)}, mean entropy={np.mean(vals):.3f}")

# Per-crossing test against rest
alex_results = {}
for cn in [7, 8, 9, 10]:
    this_cn = np.array(entropy_by_crossing.get(cn, []))
    other_cn = np.array([e for c, ents in entropy_by_crossing.items() if c != cn for e in ents])

    if len(this_cn) >= 5 and len(other_cn) >= 5:
        real_d = abs(np.mean(this_cn) - np.mean(other_cn))
        combined = np.concatenate([this_cn, other_cn])
        null_d = []
        for _ in range(N_PERM):
            rng.shuffle(combined)
            null_d.append(abs(np.mean(combined[:len(this_cn)]) - np.mean(combined[len(this_cn):])))
        p, z = permutation_test(real_d, null_d)
        print(f"  cn={cn} vs rest: |diff|={real_d:.4f}, p={p:.4f}, z={z:.1f}")
        alex_results[f"cn={cn}"] = {"n": len(this_cn), "diff": real_d, "p": p, "z": z}

# F24: crossing number -> entropy
if len(all_entropies) >= 30:
    v24, r24 = bv2.F24_variance_decomposition(np.array(all_entropies), all_crossing_labels)
    v25, r25 = bv2.F25_transportability(np.array(all_entropies), all_crossing_labels,
                                         ["odd" if int(c) % 2 == 1 else "even" for c in all_crossing_labels])
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
    print(f"  F25: {v25}")
else:
    v24, r24 = "INSUFFICIENT", {}
    v25, r25 = "INSUFFICIENT", {}

RESULTS["G.alex"] = {
    "claim": "Alexander entropy varies by crossing number",
    "n": len(all_entropies), "per_crossing": alex_results,
    "f24": {"verdict": v24, **r24},
    "f25": {"verdict": v25, **r25},
    "verdict": "SURVIVES" if any(r.get("p", 1) < 0.01 for r in alex_results.values()) else "KILLED",
}

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("KNOT BATCH SUMMARY")
print("=" * 70)

for test_id, result in RESULTS.items():
    v = result.get("verdict", "?")
    claim = result.get("claim", "")
    eta = result.get("f24", {}).get("eta_squared", "")
    eta_str = f" eta²={eta:.4f}" if isinstance(eta, (int, float)) else ""
    print(f"  {test_id:12s} {v:12s} {claim}{eta_str}")

save_results()
print(f"\nKnot batch complete: {len(RESULTS)} tests")
