"""C02: Mod-p residue starvation — deeper analysis.
Prior: 43.6% of modular forms show starvation. Which primes, which weights?
Battery v6 (F24+F25). Machine: M1 (Skullport), 2026-04-12
"""
import sys, json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)

# Get modular forms with traces (a_p coefficients)
print("Loading modular forms from DuckDB...")
df = con.execute("""
    SELECT lmfdb_label, level, weight, dim, char_order, char_parity,
           fricke_eigenval, sato_tate_group, is_cm, traces
    FROM modular_forms
    WHERE weight >= 2 AND traces IS NOT NULL
    LIMIT 50000
""").fetchdf()
print(f"Loaded {len(df)} modular forms")

# --- Test 1: Mod-p residue starvation by prime ---
print("\n" + "="*70)
print("TEST 1: Mod-p residue starvation across primes p=2,3,5,7,11,13")
print("="*70)

primes_to_test = [2, 3, 5, 7, 11, 13]
starvation_results = {}

for p in primes_to_test:
    starved_count = 0
    total_count = 0
    for _, row in df.iterrows():
        traces = row["traces"]
        if traces is None or not isinstance(traces, (list, np.ndarray)):
            continue
        if len(traces) < 20:
            continue
        # Get first 100 traces (a_p values)
        t = np.array(traces[:100], dtype=float)
        residues = t % p
        unique_residues = len(set(residues.astype(int)))
        expected = p
        if unique_residues < expected * 0.5:  # less than half the residues present
            starved_count += 1
        total_count += 1

    rate = starved_count / max(total_count, 1)
    starvation_results[p] = {"starved": starved_count, "total": total_count, "rate": rate}
    print(f"  p={p:2d}: {starved_count}/{total_count} starved ({rate*100:.1f}%)")

# --- Test 2: Starvation by weight ---
print("\n" + "="*70)
print("TEST 2: Starvation rate by weight (mod-3)")
print("="*70)

weight_starvation = defaultdict(lambda: {"starved": 0, "total": 0})
for _, row in df.iterrows():
    traces = row["traces"]
    if traces is None or not isinstance(traces, (list, np.ndarray)) or len(traces) < 20:
        continue
    t = np.array(traces[:100], dtype=float)
    residues = set((t % 3).astype(int))
    starved = len(residues) < 2  # only 0 or 1 residue class present
    w = int(row["weight"])
    weight_starvation[w]["total"] += 1
    if starved:
        weight_starvation[w]["starved"] += 1

for w in sorted(weight_starvation.keys()):
    s = weight_starvation[w]
    if s["total"] >= 10:
        rate = s["starved"] / s["total"]
        print(f"  Weight {w:3d}: {s['starved']}/{s['total']} ({rate*100:.1f}%)")

# --- Test 3: F24 on starvation grouped by weight ---
print("\n" + "="*70)
print("TEST 3: F24 - starvation intensity by weight")
print("="*70)

starvation_scores = []
weight_labels = []
for _, row in df.iterrows():
    traces = row["traces"]
    if traces is None or not isinstance(traces, (list, np.ndarray)) or len(traces) < 20:
        continue
    t = np.array(traces[:100], dtype=float)
    # Starvation score = fraction of prime residues that are empty (averaged over p=2,3,5,7)
    score = 0
    for p in [2, 3, 5, 7]:
        residues = set((t % p).astype(int))
        score += (p - len(residues)) / p
    score /= 4
    starvation_scores.append(score)
    weight_labels.append(str(int(row["weight"])))

starvation_scores = np.array(starvation_scores)
weight_labels = np.array(weight_labels)

v1, r1 = bv2.F24_variance_decomposition(starvation_scores, weight_labels)
print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")

# --- Test 4: F24 on starvation by level ---
print("\n" + "="*70)
print("TEST 4: F24 - starvation by level (prime vs composite)")
print("="*70)

level_labels = []
for _, row in df.iterrows():
    traces = row["traces"]
    if traces is None or not isinstance(traces, (list, np.ndarray)) or len(traces) < 20:
        continue
    lev = int(row["level"])
    # Classify: prime level vs composite
    from sympy import isprime
    level_labels.append("prime" if isprime(lev) else "composite")

level_labels = np.array(level_labels)
v2, r2 = bv2.F24_variance_decomposition(starvation_scores, level_labels)
print(f"Verdict: {v2}, eta2 = {r2.get('eta_squared', 0):.4f}")
for label, gs in sorted(r2.get("group_stats", {}).items()):
    print(f"  {label}: n={gs['n']}, mean starvation={gs['mean']:.4f}")

# --- Test 5: F25 transportability (starvation across weight strata) ---
print("\n" + "="*70)
print("TEST 5: F25 - does starvation pattern transfer across weights?")
print("="*70)

v5, r5 = bv2.F25_transportability(starvation_scores, level_labels, weight_labels)
print(f"Verdict: {v5}")
if "weighted_oos_r2" in r5:
    print(f"Weighted OOS R2: {r5['weighted_oos_r2']:.4f}")
if "per_partition" in r5:
    for p in r5["per_partition"][:5]:
        print(f"  Held-out weight {p['held_out']}: n={p['n_test']}, OOS R2={p['r2_oos']:.4f}")

# --- Test 6: Which primes show the most starvation? ---
print("\n" + "="*70)
print("TEST 6: Starvation signature by Sato-Tate group")
print("="*70)

st_starvation = defaultdict(list)
for _, row in df.iterrows():
    traces = row["traces"]
    st = row["sato_tate_group"]
    if traces is None or not isinstance(traces, (list, np.ndarray)) or len(traces) < 20:
        continue
    if not st or st == "":
        continue
    t = np.array(traces[:100], dtype=float)
    score = 0
    for p in [2, 3, 5, 7]:
        residues = set((t % p).astype(int))
        score += (p - len(residues)) / p
    score /= 4
    st_starvation[st].append(score)

st_labels_all = []
st_scores_all = []
for st, scores in st_starvation.items():
    if len(scores) >= 5:
        print(f"  ST={st}: n={len(scores)}, mean starvation={np.mean(scores):.4f}")
        for s in scores:
            st_labels_all.append(st)
            st_scores_all.append(s)

if len(set(st_labels_all)) >= 2:
    v6, r6 = bv2.F24_variance_decomposition(np.array(st_scores_all), np.array(st_labels_all))
    print(f"F24 ST->starvation: {v6}, eta2={r6.get('eta_squared', 0):.4f}")

con.close()

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
weight_eta2 = r1.get("eta_squared", 0)
level_eta2 = r2.get("eta_squared", 0)
print(f"Weight->starvation eta2: {weight_eta2:.4f}")
print(f"Level->starvation eta2: {level_eta2:.4f}")

if weight_eta2 >= 0.14:
    print("-> Weight->starvation: LAW")
elif weight_eta2 >= 0.01:
    print("-> Weight->starvation: TENDENCY")
else:
    print("-> Weight->starvation: NEGLIGIBLE")

results = {
    "test": "C02",
    "claim": "Mod-p residue starvation in modular forms",
    "starvation_by_prime": starvation_results,
    "weight_eta2": weight_eta2,
    "level_eta2": level_eta2,
    "f25_verdict": v5 if 'v5' in dir() else "NOT_RUN",
}
with open(DATA / "shared/scripts/v2/r2_c02_starvation_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/r2_c02_starvation_results.json")
