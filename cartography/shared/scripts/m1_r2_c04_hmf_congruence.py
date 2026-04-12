"""C04/R2: Hilbert modular form congruence scan.
Scan for mod-p congruences among modular forms using DuckDB traces data
(integer a_p values). The HMF catalog provides label/level/dimension context.
For primes l = 2,3,5,7,11: find pairs with a_p == a_p' (mod l) for many primes p.
Battery v2 (F24/F24b/F25/F27). Machine: M1 (Skullport), 2026-04-12
"""
import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# ============================================================
# Load modular forms from DuckDB (integer traces = a_p values)
# ============================================================
print("Loading modular forms from DuckDB...")
import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)

df = con.execute("""
    SELECT lmfdb_label, level, weight, dim, char_order, fricke_eigenval,
           is_cm, traces
    FROM modular_forms
    WHERE weight >= 2 AND traces IS NOT NULL AND dim = 1
    LIMIT 10000
""").fetchdf()
print(f"Loaded {len(df)} dimension-1 modular forms")

# Also load HMF metadata for context
print("Loading HMF catalog for level/dimension context...")
try:
    with open(DATA / "convergence/data/hmf_forms_full.json", "r") as f:
        hmf_raw = json.load(f)
    hmf_records = hmf_raw.get("records", hmf_raw)
    if isinstance(hmf_records, dict):
        hmf_records = list(hmf_records.values())
    print(f"Loaded {len(hmf_records)} HMF records")
except Exception as e:
    print(f"HMF load failed ({e}), continuing with DuckDB data only")
    hmf_records = []

# ============================================================
# Prepare trace vectors
# ============================================================
print("\nPreparing trace vectors...")

forms = []
for _, row in df.iterrows():
    traces = row.get("traces")
    if traces is None or not isinstance(traces, (list, np.ndarray)):
        continue
    t = [int(x) for x in traces[:50] if x is not None]
    if len(t) < 20:
        continue
    forms.append({
        "label": row.get("lmfdb_label", "?"),
        "level": int(row.get("level") or 0),
        "weight": int(row.get("weight") or 0),
        "dim": int(row.get("dim") or 0),
        "is_cm": int(row.get("is_cm") or 0),
        "fricke": int(row.get("fricke_eigenval") or 0),
        "traces": t,
    })

print(f"  {len(forms)} forms with >= 20 integer traces")

# ============================================================
# TEST 1: Mod-p congruence scan
# ============================================================
print("\n" + "="*70)
print("TEST 1: Mod-l congruence density for l = 2, 3, 5, 7, 11")
print("="*70)

congruence_primes = [2, 3, 5, 7, 11]
congruence_results = {}

# For efficiency, limit pairwise scan
MAX_PAIRS = 5000
n_forms = len(forms)

for ell in congruence_primes:
    print(f"\n  Scanning mod {ell}...")

    # Compute mod-l reductions
    mod_traces = []
    for form in forms:
        mod_traces.append([t % ell for t in form["traces"]])

    # Sample pairs for congruence check
    rng = np.random.default_rng(42)
    n_check = min(MAX_PAIRS, n_forms * (n_forms - 1) // 2)

    congruent_counts = []  # fraction of matching a_p for each pair
    strong_congruences = []  # pairs with >= 80% match

    pairs_checked = 0
    for _ in range(n_check):
        i, j = rng.choice(n_forms, 2, replace=False)
        t_i = mod_traces[i]
        t_j = mod_traces[j]
        n_compare = min(len(t_i), len(t_j))
        if n_compare < 10:
            continue

        matches = sum(1 for a, b in zip(t_i[:n_compare], t_j[:n_compare]) if a == b)
        frac = matches / n_compare
        congruent_counts.append(frac)
        pairs_checked += 1

        if frac >= 0.8:
            strong_congruences.append({
                "i_label": forms[i]["label"],
                "j_label": forms[j]["label"],
                "i_level": forms[i]["level"],
                "j_level": forms[j]["level"],
                "match_frac": frac,
                "n_compared": n_compare,
            })

    if not congruent_counts:
        print(f"    No valid pairs")
        congruence_results[ell] = {"density": 0, "n_pairs": 0}
        continue

    arr = np.array(congruent_counts)
    expected_random = 1.0 / ell  # random baseline for mod-l match
    mean_density = float(np.mean(arr))
    enrichment = mean_density / expected_random if expected_random > 0 else 0

    congruence_results[ell] = {
        "n_pairs_checked": pairs_checked,
        "mean_match_density": mean_density,
        "expected_random": expected_random,
        "enrichment": enrichment,
        "n_strong_congruences": len(strong_congruences),
        "median_density": float(np.median(arr)),
        "std_density": float(np.std(arr)),
    }

    print(f"    Pairs checked: {pairs_checked}")
    print(f"    Mean match density: {mean_density:.4f} (random baseline: {expected_random:.4f})")
    print(f"    Enrichment: {enrichment:.2f}x")
    print(f"    Strong congruences (>=80%): {len(strong_congruences)}")

# ============================================================
# TEST 2: F24 -- congruence rate by weight
# ============================================================
print("\n" + "="*70)
print("TEST 2: F24 -- congruence rate varies by weight?")
print("="*70)

# For each form, compute its average mod-3 match rate against 20 random peers
ell_test = 3
form_match_rates = []
form_weights = []

rng = np.random.default_rng(123)
for i, form in enumerate(forms):
    t_i = [t % ell_test for t in form["traces"]]
    peers = rng.choice(n_forms, min(20, n_forms - 1), replace=False)
    peers = [p for p in peers if p != i]
    if not peers:
        continue
    rates = []
    for j in peers:
        t_j = [t % ell_test for t in forms[j]["traces"]]
        n_comp = min(len(t_i), len(t_j))
        if n_comp < 10:
            continue
        matches = sum(1 for a, b in zip(t_i[:n_comp], t_j[:n_comp]) if a == b)
        rates.append(matches / n_comp)
    if rates:
        form_match_rates.append(float(np.mean(rates)))
        form_weights.append(str(form["weight"]))

if len(form_match_rates) >= 30 and len(set(form_weights)) >= 2:
    v24, r24 = bv2.F24_variance_decomposition(
        np.array(form_match_rates), form_weights
    )
    print(f"F24 verdict: {v24}")
    print(f"  eta^2 = {r24.get('eta_squared', 0):.4f}")
    for gname, gstat in r24.get("group_stats", {}).items():
        print(f"  Weight {gname}: n={gstat['n']}, mean={gstat['mean']:.4f}")
else:
    v24, r24 = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24 by weight")

# ============================================================
# TEST 3: F24 -- congruence rate by level bracket
# ============================================================
print("\n" + "="*70)
print("TEST 3: F24 -- congruence rate varies by level?")
print("="*70)

form_level_brackets = []
for form in forms:
    lev = form["level"]
    if lev <= 100:
        form_level_brackets.append("<=100")
    elif lev <= 500:
        form_level_brackets.append("101-500")
    elif lev <= 1000:
        form_level_brackets.append("501-1000")
    else:
        form_level_brackets.append(">1000")

# Reuse form_match_rates from above (same length as forms if all got rates)
if len(form_match_rates) >= 30 and len(form_level_brackets) >= len(form_match_rates):
    brackets = form_level_brackets[:len(form_match_rates)]
    if len(set(brackets)) >= 2:
        v24_lev, r24_lev = bv2.F24_variance_decomposition(
            np.array(form_match_rates), brackets
        )
        print(f"F24 verdict: {v24_lev}")
        print(f"  eta^2 = {r24_lev.get('eta_squared', 0):.4f}")
        for gname, gstat in r24_lev.get("group_stats", {}).items():
            print(f"  Level bracket {gname}: n={gstat['n']}, mean={gstat['mean']:.4f}")
    else:
        v24_lev, r24_lev = "INSUFFICIENT_DATA", {}
        print("Only one level bracket, cannot run F24")
else:
    v24_lev, r24_lev = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24 by level")

# ============================================================
# TEST 4: F24b -- metric consistency on congruence rates
# ============================================================
print("\n" + "="*70)
print("TEST 4: F24b -- metric consistency")
print("="*70)

if len(form_match_rates) >= 40 and len(set(form_weights)) >= 2:
    v24b, r24b = bv2.F24b_metric_consistency(
        np.array(form_match_rates), form_weights[:len(form_match_rates)]
    )
    print(f"F24b verdict: {v24b}")
    print(f"  M4/M2 ratio = {r24b.get('m4m2_ratio', 'N/A')}")
    print(f"  eta^2 = {r24b.get('eta_squared', 'N/A')}")
else:
    v24b, r24b = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24b")

# ============================================================
# TEST 5: F25 -- transportability across weight classes
# ============================================================
print("\n" + "="*70)
print("TEST 5: F25 -- transportability across weight classes")
print("="*70)

# Primary: level bracket, secondary: weight
if len(form_match_rates) >= 30:
    prim = form_level_brackets[:len(form_match_rates)]
    sec = form_weights[:len(form_match_rates)]
    if len(set(sec)) >= 2:
        v25, r25 = bv2.F25_transportability(
            np.array(form_match_rates), prim, sec
        )
        print(f"F25 verdict: {v25}")
        print(f"  Weighted OOS R^2 = {r25.get('weighted_oos_r2', 'N/A')}")
    else:
        v25, r25 = "INSUFFICIENT_DATA", {}
        print("Only one weight class, cannot run F25")
else:
    v25, r25 = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F25")

# ============================================================
# TEST 6: F27 -- consequence check
# ============================================================
print("\n" + "="*70)
print("TEST 6: F27 -- tautology check")
print("="*70)

v27, r27 = bv2.F27_consequence_check("hecke_eigenvalue_mod_p", "congruence_rate")
print(f"F27 verdict: {v27}")
if r27:
    print(f"  Details: {r27}")

# ============================================================
# HMF dimension distribution (context from catalog)
# ============================================================
print("\n" + "="*70)
print("CONTEXT: HMF dimension distribution")
print("="*70)

if hmf_records:
    dims = [r.get("dimension", 0) or 0 for r in hmf_records]
    dim_counts = defaultdict(int)
    for d in dims:
        dim_counts[d] += 1
    for d in sorted(dim_counts.keys())[:10]:
        print(f"  dim={d}: {dim_counts[d]} forms ({100*dim_counts[d]/len(dims):.1f}%)")

# ============================================================
# CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

# Check if congruences are above random
any_enriched = any(
    v.get("enrichment", 0) > 1.5 for v in congruence_results.values()
)
all_enriched = all(
    v.get("enrichment", 0) > 1.2 for v in congruence_results.values()
    if v.get("n_pairs_checked", 0) > 0
)

print(f"Any prime with >1.5x enrichment: {any_enriched}")
print(f"All primes with >1.2x enrichment: {all_enriched}")
print(f"F24 by weight: {v24} (eta^2={r24.get('eta_squared','N/A')})")
print(f"F24 by level: {v24_lev} (eta^2={r24_lev.get('eta_squared','N/A')})")
print(f"F24b: {v24b}")
print(f"F25: {v25}")
print(f"F27: {v27}")

if any_enriched:
    classification = "CONGRUENCE_ENRICHED"
    print("\n--> Congruence rates exceed random baseline at some primes")
else:
    classification = "RANDOM_BASELINE"
    print("\n--> Congruence rates consistent with random mod-l matching")

# ============================================================
# Save results
# ============================================================
final_results = {
    "test": "C04/R2",
    "claim": "Hilbert modular form congruences reveal structural patterns by weight/level",
    "n_forms": len(forms),
    "congruence_by_prime": {str(k): v for k, v in congruence_results.items()},
    "f24_by_weight": {"verdict": v24, "result": r24},
    "f24_by_level": {"verdict": v24_lev, "result": r24_lev},
    "f24b": {"verdict": v24b, "result": r24b},
    "f25": {"verdict": v25, "result": r25},
    "f27": {"verdict": v27, "result": r27},
    "classification": classification,
}

out_path = Path(__file__).resolve().parent / "v2" / "c04_hmf_congruence_results.json"
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c04_hmf_congruence_results.json")
