"""Round 3, M1 — Fungrim/mathlib/formal batch (7 tests).
Load fungrim_index.json, import_graph.json, findstat_enriched.json once.

Tests:
  G.R1.6   Symbol count: equations vs definitions      (SURVIVED z=3.9)
  G.R2.pi  Pi formulas have more symbols               (SURVIVED z=18.9)
  G.R2.zeta Zeta concentrated in fewer modules         (SURVIVED z=-12.3)
  G.R4.fung Later formulas have more symbols (within module) (SURVIVED z=13.7)
  C75      Fungrim symbol analysis                     (ANALYZED)
  C23      FindStat combinatorial statistics           (PARKED)
  C76      FindStat enriched data                      (PARKED)

Machine: M1 (Skullport), 2026-04-12
Battery: v6 (F1-F27, frozen)
"""
import sys, json, ast
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
    out = DATA / "shared/scripts/v2/r3_formal_batch_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nResults saved to v2/r3_formal_batch_results.json")


# ============================================================
# LOAD DATA
# ============================================================
print("Loading fungrim_index.json...")
fungrim = json.loads((DATA / "fungrim/data/fungrim_index.json").read_text(encoding="utf-8"))
formulas = fungrim["formulas"]
print(f"  {len(formulas)} formulas, {fungrim['n_modules']} modules")

# Parse n_symbols as int, symbols as list
for f in formulas:
    f["n_symbols"] = int(f["n_symbols"])
    if isinstance(f["symbols"], str):
        try:
            f["symbols"] = ast.literal_eval(f["symbols"])
        except (ValueError, SyntaxError):
            f["symbols"] = []

print("Loading findstat_enriched.json...")
findstat = json.loads((DATA / "findstat/data/findstat_enriched.json").read_text(encoding="utf-8"))
fs_stats = findstat.get("statistics", [])
print(f"  {len(fs_stats)} FindStat statistics")

print("Loading import_graph.json...")
mathlib = json.loads((DATA / "mathlib/data/import_graph.json").read_text(encoding="utf-8"))
print(f"  mathlib keys: {list(mathlib.keys())[:5]}")


# ============================================================
# TEST 1: G.R1.6 — Symbol count: equations vs definitions
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 1: G.R1.6 — Symbol count: equations vs definitions")
print("=" * 70)

eqs = np.array([f["n_symbols"] for f in formulas if f["type"] == "equation"])
defs = np.array([f["n_symbols"] for f in formulas if f["type"] == "definition"])
print(f"  equations: n={len(eqs)}, mean symbols={np.mean(eqs):.2f}")
print(f"  definitions: n={len(defs)}, mean symbols={np.mean(defs):.2f}")

real_d = abs(np.mean(eqs) - np.mean(defs))
combined = np.concatenate([eqs, defs])
null_d = []
for _ in range(N_PERM):
    rng.shuffle(combined)
    null_d.append(abs(np.mean(combined[:len(eqs)]) - np.mean(combined[len(eqs):])))
p, z = permutation_test(real_d, null_d)
print(f"  |diff| = {real_d:.3f}, p = {p:.6f}, z = {z:.1f}")

# F24
all_nsym = np.concatenate([eqs, defs])
all_type_labels = ["equation"] * len(eqs) + ["definition"] * len(defs)
v24, r24 = bv2.F24_variance_decomposition(all_nsym.astype(float), all_type_labels)
v24b, r24b = bv2.F24b_metric_consistency(all_nsym.astype(float), all_type_labels)
print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")
print(f"  F24b: {v24b}")

# F27: is type -> symbol count a known consequence?
v27, r27 = bv2.F27_consequence_check("formula_type", "symbol_count")
print(f"  F27: {v27}")

RESULTS["G.R1.6"] = {
    "claim": "Equations have different symbol counts than definitions",
    "n_eq": len(eqs), "n_def": len(defs),
    "mean_eq": float(np.mean(eqs)), "mean_def": float(np.mean(defs)),
    "diff": real_d, "p": p, "z": z,
    "f24": {"verdict": v24, **r24}, "f24b": {"verdict": v24b, **r24b},
    "f27": {"verdict": v27, **r27},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}


# ============================================================
# TEST 2: G.R2.pi — Pi formulas have more symbols
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 2: G.R2.pi — Pi formulas have more symbols")
print("=" * 70)

pi_syms = np.array([f["n_symbols"] for f in formulas if "Pi" in f.get("symbols", [])])
non_pi = np.array([f["n_symbols"] for f in formulas if "Pi" not in f.get("symbols", [])])
print(f"  Pi formulas: n={len(pi_syms)}, mean={np.mean(pi_syms):.2f}")
print(f"  Non-Pi formulas: n={len(non_pi)}, mean={np.mean(non_pi):.2f}")

real_d = abs(np.mean(pi_syms) - np.mean(non_pi))
combined = np.concatenate([pi_syms, non_pi])
null_d = []
for _ in range(N_PERM):
    rng.shuffle(combined)
    null_d.append(abs(np.mean(combined[:len(pi_syms)]) - np.mean(combined[len(pi_syms):])))
p, z = permutation_test(real_d, null_d)
print(f"  |diff| = {real_d:.3f}, p = {p:.6f}, z = {z:.1f}")

# F24
all_sym = np.concatenate([pi_syms, non_pi]).astype(float)
labels = ["has_Pi"] * len(pi_syms) + ["no_Pi"] * len(non_pi)
v24, r24 = bv2.F24_variance_decomposition(all_sym, labels)
print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

RESULTS["G.R2.pi"] = {
    "claim": "Pi formulas have more symbols than non-Pi",
    "n_pi": len(pi_syms), "n_non_pi": len(non_pi),
    "mean_pi": float(np.mean(pi_syms)), "mean_non_pi": float(np.mean(non_pi)),
    "diff": real_d, "p": p, "z": z,
    "f24": {"verdict": v24, **r24},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}


# ============================================================
# TEST 3: G.R2.zeta — Zeta concentrated in fewer modules
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 3: G.R2.zeta — Zeta concentrated in fewer modules")
print("=" * 70)

zeta_forms = [f for f in formulas if any("Zeta" in s for s in f.get("symbols", []))]
zeta_mods = set(f["module"] for f in zeta_forms)
all_mods = [f["module"] for f in formulas]
print(f"  Zeta formulas: {len(zeta_forms)}")
print(f"  Zeta modules: {len(zeta_mods)} (out of {len(set(all_mods))} total)")

real_stat = len(zeta_mods)

# Null: randomly select same number of formulas, count unique modules
null_conc = []
for _ in range(N_PERM):
    sample_mods = rng.choice(all_mods, size=len(zeta_forms), replace=False)
    null_conc.append(len(set(sample_mods)))

# One-tailed: lower is more concentrated
p = (np.sum(np.array(null_conc) <= real_stat) + 1) / (len(null_conc) + 1)
z = (np.mean(null_conc) - real_stat) / max(np.std(null_conc), 1e-12)  # positive z = more concentrated
print(f"  Real: {real_stat} modules, Null mean: {np.mean(null_conc):.1f}")
print(f"  p (one-tailed, lower) = {p:.6f}, z = {z:.1f}")

RESULTS["G.R2.zeta"] = {
    "claim": "Zeta formulas concentrated in fewer modules than random",
    "n_zeta": len(zeta_forms), "n_zeta_modules": real_stat,
    "null_mean_modules": float(np.mean(null_conc)),
    "p": p, "z": z,
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}


# ============================================================
# TEST 4: G.R4.fung — Later formulas have more symbols (within module)
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 4: G.R4.fung — Later formulas have more symbols (within module)")
print("=" * 70)

mod_positions = defaultdict(list)
for i, f in enumerate(formulas):
    mod_positions[f["module"]].append((i, f["n_symbols"]))

within_mod_corr = []
for mod, items in mod_positions.items():
    if len(items) > 10:
        pos, syms = zip(*items)
        r_val = stats.spearmanr(pos, syms)[0]
        if not np.isnan(r_val):
            within_mod_corr.append(r_val)

real_stat = abs(np.mean(within_mod_corr))
print(f"  Modules with >10 formulas: {len(within_mod_corr)}")
print(f"  Mean within-module Spearman r: {np.mean(within_mod_corr):.4f}")
print(f"  |mean r| = {real_stat:.4f}")

# Null: shuffle symbols within each module
null_means = []
for _ in range(1000):
    shuffled_corrs = []
    for mod, items in mod_positions.items():
        if len(items) > 10:
            pos, syms = zip(*items)
            r_val = stats.spearmanr(pos, rng.permutation(list(syms)))[0]
            if not np.isnan(r_val):
                shuffled_corrs.append(r_val)
    null_means.append(abs(np.mean(shuffled_corrs)))

p, z = permutation_test(real_stat, null_means)
print(f"  p = {p:.6f}, z = {z:.1f}")

# F24: module -> mean symbol count
mod_labels = []
mod_nsyms = []
for f in formulas:
    mod_labels.append(f["module"])
    mod_nsyms.append(float(f["n_symbols"]))
v24, r24 = bv2.F24_variance_decomposition(np.array(mod_nsyms), mod_labels)
print(f"  F24 (module -> n_symbols): {v24} (eta²={r24.get('eta_squared', 0):.4f})")

RESULTS["G.R4.fung"] = {
    "claim": "Later formulas within a module use more symbols",
    "n_modules_tested": len(within_mod_corr),
    "mean_within_r": float(np.mean(within_mod_corr)),
    "abs_mean_r": real_stat, "p": p, "z": z,
    "f24_module_symbols": {"verdict": v24, **r24},
    "verdict": "SURVIVES" if p < 0.01 else "KILLED",
}


# ============================================================
# TEST 5: C75 — Fungrim symbol analysis (deeper)
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 5: C75 — Fungrim symbol analysis")
print("=" * 70)

# Compute per-symbol statistics: how many formulas use each symbol, mean n_symbols
symbol_stats = defaultdict(lambda: {"count": 0, "total_nsym": 0})
for f in formulas:
    for s in f.get("symbols", []):
        symbol_stats[s]["count"] += 1
        symbol_stats[s]["total_nsym"] += f["n_symbols"]

# Sort by frequency
sorted_symbols = sorted(symbol_stats.items(), key=lambda x: -x[1]["count"])
print(f"  Total unique symbols: {len(sorted_symbols)}")
print(f"  Top 10: {[(s, d['count']) for s, d in sorted_symbols[:10]]}")

# M4/M² of symbol frequency distribution
freqs = np.array([d["count"] for _, d in sorted_symbols])
if len(freqs) > 30:
    centered = freqs / np.mean(freqs)
    m2 = np.mean(centered ** 2)
    m4 = np.mean(centered ** 4)
    m4m2 = m4 / m2 ** 2
    print(f"  Symbol frequency M4/M² = {m4m2:.3f}")

    # F24: symbol type (common vs rare) -> mean formula complexity
    mean_complexity = np.array([d["total_nsym"] / max(d["count"], 1) for _, d in sorted_symbols])
    freq_labels = ["top50" if i < 50 else "mid" if i < 200 else "tail"
                   for i in range(len(sorted_symbols))]
    v24, r24 = bv2.F24_variance_decomposition(mean_complexity, freq_labels)
    print(f"  F24 (symbol rank -> formula complexity): {v24} (eta²={r24.get('eta_squared', 0):.4f})")

    RESULTS["C75"] = {
        "claim": "Fungrim symbol frequency distribution has non-trivial structure",
        "n_symbols": len(sorted_symbols), "m4m2_freq": m4m2,
        "top10": [(s, d["count"]) for s, d in sorted_symbols[:10]],
        "f24": {"verdict": v24, **r24},
        "verdict": "ANALYZED",
    }
else:
    RESULTS["C75"] = {"verdict": "INSUFFICIENT_DATA"}


# ============================================================
# TEST 6: C23 — FindStat combinatorial statistics
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 6: C23 — FindStat combinatorial statistics")
print("=" * 70)

if fs_stats:
    # Analyze by collection (permutations, binary trees, etc.)
    collections = Counter(s.get("collection", "unknown") for s in fs_stats)
    print(f"  Statistics: {len(fs_stats)}")
    print(f"  Collections: {collections.most_common(10)}")

    # Test: do some collections have more statistics than expected?
    coll_counts = np.array([c for _, c in collections.most_common()])
    if len(coll_counts) > 5:
        centered = coll_counts / np.mean(coll_counts)
        m2 = np.mean(centered ** 2)
        m4 = np.mean(centered ** 4)
        m4m2 = m4 / m2 ** 2
        print(f"  Collection size M4/M² = {m4m2:.3f}")

        # F24: collection -> statistic count (per-stat level)
        stat_collections = [s.get("collection", "unknown") for s in fs_stats]
        # Use a proxy: count of references per statistic
        ref_counts = np.array([len(s.get("references", [])) for s in fs_stats], dtype=float)
        v24, r24 = bv2.F24_variance_decomposition(ref_counts, stat_collections)
        print(f"  F24 (collection -> reference count): {v24} (eta²={r24.get('eta_squared', 0):.4f})")

        RESULTS["C23"] = {
            "claim": "FindStat statistics cluster non-uniformly by collection",
            "n_stats": len(fs_stats), "n_collections": len(collections),
            "m4m2_collection": m4m2,
            "top_collections": collections.most_common(5),
            "f24": {"verdict": v24, **r24},
            "verdict": "ANALYZED",
        }
    else:
        RESULTS["C23"] = {"verdict": "SKIP", "reason": "too few collections"}
else:
    RESULTS["C23"] = {"verdict": "SKIP", "reason": "no FindStat data loaded"}


# ============================================================
# TEST 7: C76 — FindStat enriched data
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 7: C76 — FindStat enriched data")
print("=" * 70)

if fs_stats:
    # Compute per-statistic features
    has_sage = [s for s in fs_stats if s.get("sage_code")]
    has_refs = [s for s in fs_stats if s.get("references")]
    print(f"  With Sage code: {len(has_sage)}/{len(fs_stats)}")
    print(f"  With references: {len(has_refs)}/{len(fs_stats)}")

    # Test: do statistics with Sage code have different reference counts?
    sage_refcount = np.array([len(s.get("references", [])) for s in fs_stats if s.get("sage_code")])
    nosage_refcount = np.array([len(s.get("references", [])) for s in fs_stats if not s.get("sage_code")])

    if len(sage_refcount) >= 10 and len(nosage_refcount) >= 10:
        real_d = abs(np.mean(sage_refcount) - np.mean(nosage_refcount))
        combined = np.concatenate([sage_refcount, nosage_refcount])
        null_d = []
        for _ in range(N_PERM):
            rng.shuffle(combined)
            null_d.append(abs(np.mean(combined[:len(sage_refcount)]) - np.mean(combined[len(sage_refcount):])))
        p, z = permutation_test(real_d, null_d)
        print(f"  Sage vs no-Sage ref count: {np.mean(sage_refcount):.2f} vs {np.mean(nosage_refcount):.2f}")
        print(f"  |diff| = {real_d:.3f}, p = {p:.6f}, z = {z:.1f}")

        # F24
        all_refs = np.concatenate([sage_refcount, nosage_refcount]).astype(float)
        labels = ["has_sage"] * len(sage_refcount) + ["no_sage"] * len(nosage_refcount)
        v24, r24 = bv2.F24_variance_decomposition(all_refs, labels)
        print(f"  F24: {v24} (eta²={r24.get('eta_squared', 0):.4f})")

        RESULTS["C76"] = {
            "claim": "FindStat: Sage-equipped statistics have different reference patterns",
            "n_sage": len(sage_refcount), "n_nosage": len(nosage_refcount),
            "mean_refs_sage": float(np.mean(sage_refcount)),
            "mean_refs_nosage": float(np.mean(nosage_refcount)),
            "diff": real_d, "p": p, "z": z,
            "f24": {"verdict": v24, **r24},
            "verdict": "SURVIVES" if p < 0.01 else "KILLED",
        }
    else:
        RESULTS["C76"] = {"verdict": "SKIP", "reason": "insufficient Sage/no-Sage split"}
else:
    RESULTS["C76"] = {"verdict": "SKIP", "reason": "no FindStat data"}


# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 70}")
print("FORMAL BATCH SUMMARY")
print("=" * 70)

for test_id, result in RESULTS.items():
    v = result.get("verdict", "?")
    claim = result.get("claim", "")
    eta = result.get("f24", {}).get("eta_squared", "")
    eta_str = f" eta²={eta:.4f}" if isinstance(eta, (int, float)) else ""
    print(f"  {test_id:12s} {v:20s} {claim}{eta_str}")

save_results()
print(f"\nFormal batch complete: {len(RESULTS)} tests")
