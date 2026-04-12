"""Round 3, M1 — EC/MF batch (7 tests).
Load DuckDB once, run all elliptic curve / modular form tests.

Tests:
  G.R2.d7   Div by 7: rank-0 vs rank-1          (Untested)
  G.R2.d11  Div by 11: rank-0 vs rank-1         (Untested)
  G.R2.d13  Div by 13: rank-0 vs rank-1         (Untested)
  G.R3.ec   EC per conductor is NOT Poisson      (SURVIVED z=0)
  G.R4.mod  Rank-2 conductor mod 12 != rank-0    (SURVIVED z=0)
  C89       Torsion -> root number (EC)           (Potential rediscovery)
  C51-f24   EC conductor M4/M² = 1.71 (classify) (WON)

Machine: M1 (Skullport), 2026-04-12
Battery: v6 (F1-F27, frozen)
"""
import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
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
    out = DATA / "shared/scripts/v2/r3_ecmf_batch_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nResults saved to v2/r3_ecmf_batch_results.json")


# ============================================================
# LOAD DATA
# ============================================================
print("Loading EC data from DuckDB...")
import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)

ec_df = con.execute("""
    SELECT conductor, rank, torsion, torsion_structure
    FROM elliptic_curves
    WHERE rank IS NOT NULL
""").fetchdf()
print(f"  {len(ec_df)} elliptic curves loaded")

# Load root numbers from l_functions table (joined via conductor/label)
lf_df = con.execute("""
    SELECT lf.root_number, lf.conductor, ec.rank, ec.torsion, ec.torsion_structure
    FROM l_functions lf
    JOIN elliptic_curves ec ON lf.object_id = ec.object_id
    WHERE lf.root_number IS NOT NULL AND ec.rank IS NOT NULL
""").fetchdf()
print(f"  {len(lf_df)} EC with root numbers from L-functions")

con.close()

# Parse conductors and ranks
conductors = ec_df["conductor"].values.astype(int)
ranks = ec_df["rank"].values.astype(int)
torsions = ec_df["torsion"].values.astype(int)

conds_r0 = conductors[ranks == 0]
conds_r1 = conductors[ranks == 1]
conds_r2 = conductors[ranks == 2]
print(f"  rank-0: {len(conds_r0)}, rank-1: {len(conds_r1)}, rank-2: {len(conds_r2)}")


# ============================================================
# TESTS 1-3: G.R2.d7, G.R2.d11, G.R2.d13 — Div by prime: rank-0 vs rank-1
# ============================================================
for p_val in [7, 11, 13]:
    tag = f"G.R2.d{p_val}"
    print(f"\n{'=' * 70}")
    print(f"TEST: {tag} — Div by {p_val}: rank-0 vs rank-1")
    print("=" * 70)

    d_r0 = np.array([1 if c % p_val == 0 else 0 for c in conds_r0])
    d_r1 = np.array([1 if c % p_val == 0 else 0 for c in conds_r1])

    rate_r0 = np.mean(d_r0)
    rate_r1 = np.mean(d_r1)
    real_d = abs(rate_r0 - rate_r1)
    print(f"  rank-0 div rate: {rate_r0:.4f} ({sum(d_r0)}/{len(d_r0)})")
    print(f"  rank-1 div rate: {rate_r1:.4f} ({sum(d_r1)}/{len(d_r1)})")
    print(f"  |diff| = {real_d:.4f}")

    combined = np.concatenate([d_r0, d_r1])
    null_d = []
    for _ in range(N_PERM):
        rng.shuffle(combined)
        null_d.append(abs(np.mean(combined[:len(d_r0)]) - np.mean(combined[len(d_r0):])))
    p, z = permutation_test(real_d, null_d)
    print(f"  p = {p:.6f}, z = {z:.1f}")

    # F24: rank -> divisibility
    all_div = np.concatenate([d_r0, d_r1])
    all_rank_labels = ["rank-0"] * len(d_r0) + ["rank-1"] * len(d_r1)
    v24, r24 = bv2.F24_variance_decomposition(all_div, all_rank_labels)
    print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.6f})")

    RESULTS[tag] = {
        "claim": f"Divisibility by {p_val} differs between rank-0 and rank-1 EC",
        "n_r0": len(d_r0), "n_r1": len(d_r1),
        "rate_r0": float(rate_r0), "rate_r1": float(rate_r1),
        "diff": real_d, "p": p, "z": z,
        "f24": {"verdict": v24, **r24},
        "verdict": "SURVIVES" if p < 0.01 else "KILLED",
    }


# ============================================================
# TEST 4: G.R3.ec — EC per conductor is NOT Poisson
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 4: G.R3.ec — EC per conductor is NOT Poisson")
print("=" * 70)

ec_per_cond = Counter(conductors)
counts = np.array(list(ec_per_cond.values()))
print(f"  Unique conductors: {len(ec_per_cond)}")
print(f"  Mean EC per conductor: {np.mean(counts):.3f}")
print(f"  Var/Mean ratio: {np.var(counts)/np.mean(counts):.3f} (Poisson expects 1.0)")

vm_ratio = np.var(counts) / np.mean(counts)

# Chi-squared test for Poisson fit
lam = np.mean(counts)
max_k = min(int(np.max(counts)), 50)
observed = np.bincount(np.clip(counts, 0, max_k), minlength=max_k + 1)
expected_poisson = np.array([stats.poisson.pmf(k, lam) * len(counts) for k in range(max_k + 1)])

# Lump cells with expected < 5
valid = expected_poisson > 5
if valid.sum() > 3:
    obs_v = observed[valid].astype(float)
    exp_v = expected_poisson[valid]
    exp_v = exp_v * obs_v.sum() / exp_v.sum()  # normalize
    chi2, p_chi = stats.chisquare(obs_v, exp_v)
    print(f"  Chi² = {chi2:.1f}, p = {p_chi:.2e}")
    survived = p_chi < 0.01
else:
    chi2, p_chi = 0, 1.0
    survived = False
    print("  Insufficient cells for chi² test")

# F24: bucket conductors by magnitude -> EC count per bucket
cond_magnitude = np.array([np.log10(c + 1) for c in ec_per_cond.keys()])
cond_counts = np.array(list(ec_per_cond.values()))
mag_bins = np.digitize(cond_magnitude, bins=np.linspace(0, cond_magnitude.max(), 6))
mag_labels = [f"mag_bin_{b}" for b in mag_bins]
v24, r24 = bv2.F24_variance_decomposition(cond_counts, mag_labels)
print(f"  F24 (conductor magnitude -> EC count): {v24} (eta²={r24.get('eta_squared', 0):.4f})")

RESULTS["G.R3.ec"] = {
    "claim": "EC count per conductor is NOT Poisson distributed",
    "n_conductors": len(ec_per_cond), "mean_per_cond": float(np.mean(counts)),
    "var_mean_ratio": float(vm_ratio),
    "chi2": float(chi2), "p_chi": float(p_chi),
    "f24": {"verdict": v24, **r24},
    "verdict": "SURVIVES" if survived else "KILLED",
}


# ============================================================
# TEST 5: G.R4.mod — Rank-2 conductor mod 12 differs from rank-0
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 5: G.R4.mod — Rank-2 conductor mod 12 != rank-0")
print("=" * 70)

if len(conds_r2) >= 20:
    mod12_r2 = np.bincount([c % 12 for c in conds_r2], minlength=12)
    # Sample proportionally from rank-0 for comparison
    sample_r0 = rng.choice(conds_r0, size=min(len(conds_r0), len(conds_r2) * 10), replace=False)
    mod12_r0 = np.bincount([c % 12 for c in sample_r0], minlength=12)

    print(f"  rank-2: n={len(conds_r2)}")
    print(f"  rank-0 sample: n={len(sample_r0)}")
    print(f"  mod-12 rank-2: {mod12_r2}")
    print(f"  mod-12 rank-0: {mod12_r0}")

    # Chi-squared contingency test
    contingency = np.array([mod12_r2, mod12_r0])
    # Remove columns where both are zero
    nonzero_cols = (contingency.sum(axis=0) > 0)
    contingency = contingency[:, nonzero_cols]

    if contingency.shape[1] >= 2:
        chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
        print(f"  Chi² = {chi2:.1f}, dof = {dof}, p = {p_chi:.2e}")

        # F24: rank -> conductor mod 12
        all_mods = np.array([c % 12 for c in np.concatenate([conds_r0[:5000], conds_r2])])
        all_rank_labels = ["rank-0"] * min(len(conds_r0), 5000) + ["rank-2"] * len(conds_r2)
        v24, r24 = bv2.F24_variance_decomposition(all_mods.astype(float), all_rank_labels)
        print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

        RESULTS["G.R4.mod"] = {
            "claim": "Rank-2 conductor mod 12 distribution differs from rank-0",
            "n_r2": len(conds_r2), "n_r0_sample": len(sample_r0),
            "chi2": float(chi2), "dof": int(dof), "p": float(p_chi),
            "f24": {"verdict": v24, **r24},
            "verdict": "SURVIVES" if p_chi < 0.01 else "KILLED",
        }
    else:
        RESULTS["G.R4.mod"] = {"verdict": "SKIP", "reason": "insufficient mod-12 variation"}
else:
    print(f"  SKIP: only {len(conds_r2)} rank-2 curves")
    RESULTS["G.R4.mod"] = {"verdict": "SKIP", "reason": f"only {len(conds_r2)} rank-2 curves"}


# ============================================================
# TEST 6: C89 — Torsion -> root number (EC)
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 6: C89 — Torsion -> root number (EC)")
print("=" * 70)

if len(lf_df) >= 30:
    # Parse root numbers
    root_nums = []
    torsion_labels = []
    for _, row in lf_df.iterrows():
        rn = row.get("root_number")
        tor = row.get("torsion")
        if rn is not None and tor is not None:
            try:
                rn_val = float(rn)
                tor_val = int(tor)
                root_nums.append(rn_val)
                torsion_labels.append(f"Z/{tor_val}Z" if tor_val > 1 else "trivial")
            except (ValueError, TypeError):
                continue

    root_nums = np.array(root_nums)
    print(f"  n = {len(root_nums)} EC with root number + torsion")
    print(f"  Torsion groups: {Counter(torsion_labels).most_common(10)}")
    print(f"  Root number distribution: +1={np.sum(root_nums > 0)}, -1={np.sum(root_nums < 0)}")

    if len(set(torsion_labels)) >= 2:
        # F24: torsion -> root number
        v24, r24 = bv2.F24_variance_decomposition(root_nums, torsion_labels)
        v24b, r24b = bv2.F24b_metric_consistency(root_nums, torsion_labels)
        print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
        print(f"  F24b: {v24b}")

        # Per-torsion root number rates
        tor_rn_rates = {}
        for tl in set(torsion_labels):
            mask = [i for i, t in enumerate(torsion_labels) if t == tl]
            rn_sub = root_nums[mask]
            pos_rate = np.mean(rn_sub > 0)
            tor_rn_rates[tl] = {"n": len(mask), "rn_plus1_rate": float(pos_rate)}
            print(f"    {tl}: n={len(mask)}, RN=+1 rate={pos_rate:.3f}")

        # F27: is torsion -> root number a known consequence?
        v27, r27 = bv2.F27_consequence_check("torsion_structure", "root_number")
        print(f"  F27: {v27}")

        RESULTS["C89"] = {
            "claim": "EC torsion group predicts root number sign",
            "n": len(root_nums), "per_torsion": tor_rn_rates,
            "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
            "f27": {"verdict": v27, **r27},
            "verdict": v24,
        }
    else:
        RESULTS["C89"] = {"verdict": "SKIP", "reason": "insufficient torsion variation"}
else:
    RESULTS["C89"] = {"verdict": "SKIP", "reason": "no root number data in L-functions table"}


# ============================================================
# TEST 7: C51-f24 — EC conductor M4/M² = 1.71 (classify)
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 7: C51-f24 — EC conductor M4/M² = 1.71 (classify)")
print("=" * 70)

log_cond = np.log(conductors[conductors > 0].astype(float))
centered = log_cond / np.mean(log_cond)
m2 = np.mean(centered ** 2)
m4 = np.mean(centered ** 4)
m4m2 = m4 / m2 ** 2
print(f"  n = {len(log_cond)}")
print(f"  M4/M² (log conductor) = {m4m2:.3f}")

# F24 by rank
rank_labels = [f"rank-{r}" for r in ranks[conductors > 0]]
v24_rank, r24_rank = bv2.F24_variance_decomposition(log_cond, rank_labels)
print(f"  F24 (rank -> log conductor): {v24_rank} (eta²={r24_rank.get('eta_squared', 0):.4f})")

# F24 by torsion
tor_labels = [f"tor-{t}" for t in torsions[conductors > 0]]
v24_tor, r24_tor = bv2.F24_variance_decomposition(log_cond, tor_labels)
print(f"  F24 (torsion -> log conductor): {v24_tor} (eta²={r24_tor.get('eta_squared', 0):.4f})")

# F24b
v24b, r24b = bv2.F24b_metric_consistency(log_cond, rank_labels)
print(f"  F24b: {v24b} (M4/M²={r24b.get('m4m2_ratio', 'N/A')})")

# F25: transport across rank
tor_sec = [f"tor-{t}" for t in torsions[conductors > 0]]
v25, r25 = bv2.F25_transportability(log_cond, rank_labels, tor_sec)
print(f"  F25: {v25}")

RESULTS["C51-f24"] = {
    "claim": "EC conductor distribution M4/M² = 1.71",
    "n": len(log_cond), "m4m2": m4m2,
    "f24_by_rank": {"verdict": v24_rank, **r24_rank},
    "f24_by_torsion": {"verdict": v24_tor, **r24_tor},
    "f24b": {"verdict": v24b, **r24b},
    "f25": {"verdict": v25, **r25},
    "verdict": "ANALYZED",
}


# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 70}")
print("EC/MF BATCH SUMMARY")
print("=" * 70)

for test_id, result in RESULTS.items():
    v = result.get("verdict", "?")
    claim = result.get("claim", "")
    eta = result.get("f24", result.get("f24_by_rank", {})).get("eta_squared", "")
    eta_str = f" eta²={eta:.4f}" if isinstance(eta, (int, float)) else ""
    print(f"  {test_id:12s} {v:20s} {claim}{eta_str}")

save_results()
print(f"\nEC/MF batch complete: {len(RESULTS)} tests")
