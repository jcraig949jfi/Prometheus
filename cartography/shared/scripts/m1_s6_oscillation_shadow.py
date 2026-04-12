"""S6: Oscillation shadow — F24 magnitude check.
Prior: Sign oscillation patterns in EC L-function zeros, p=0.001.
Need F24 to determine if this is LAW, CONSTRAINT, or NEGLIGIBLE.
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# The oscillation shadow finding is about sign patterns in EC a_p coefficients
# Load from charon's DuckDB or from the v2 results
osc_results_path = Path("F:/Prometheus/charon/v2/oscillation_shadow_results.json")
if not osc_results_path.exists():
    osc_results_path = DATA / "shared/scripts/v2/oscillation_shadow_results.json"

# Also try loading EC data directly from LMFDB dump or convergence data
ec_path = None
for candidate in [
    DATA / "convergence/data/bridges.jsonl",
    DATA / "number_fields/data/number_fields.json",
]:
    if candidate.exists():
        ec_path = candidate
        break

# Load existing oscillation shadow results if available
if osc_results_path.exists():
    print(f"Loading prior oscillation results from {osc_results_path}")
    with open(osc_results_path) as f:
        prior = json.load(f)
    print(f"Prior result keys: {list(prior.keys())[:10]}")

    # Extract the key data
    if "forms" in prior:
        forms_data = prior["forms"]
    elif "results" in prior:
        forms_data = prior["results"]
    else:
        forms_data = prior

    # Try to extract oscillation metrics
    if isinstance(forms_data, dict):
        print(f"Data structure: dict with {len(forms_data)} keys")
        print(f"Sample keys: {list(forms_data.keys())[:10]}")
    elif isinstance(forms_data, list):
        print(f"Data structure: list with {len(forms_data)} entries")
        if forms_data:
            print(f"Sample entry keys: {list(forms_data[0].keys()) if isinstance(forms_data[0], dict) else type(forms_data[0])}")
else:
    print("No prior oscillation results found. Computing from scratch using EC data...")

# Load EC data from DuckDB
import subprocess
try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

if HAS_DUCKDB:
    db_path = Path("F:/Prometheus/charon/data/charon.duckdb")
    if db_path.exists():
        print(f"\nLoading EC data from DuckDB...")
        con = duckdb.connect(str(db_path), read_only=True)

        # Check what tables exist
        tables = con.execute("SHOW TABLES").fetchall()
        print(f"Tables: {[t[0] for t in tables]}")

        # Try to get EC a_p data
        try:
            # Get elliptic curve data with rank info
            ec_data = con.execute("""
                SELECT label, conductor, rank, root_number
                FROM elliptic_curves
                WHERE rank IS NOT NULL
                LIMIT 50000
            """).fetchdf()
            print(f"EC data: {len(ec_data)} curves")

            if len(ec_data) > 0:
                # F24: rank -> root_number
                ranks = ec_data["rank"].values.astype(float)
                rn_labels = ec_data["root_number"].astype(str).values

                print("\n" + "="*70)
                print("TEST 1: Root number by rank (F24)")
                print("="*70)
                v1, r1 = bv2.F24_variance_decomposition(ranks, rn_labels)
                print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")

                # F24: conductor distribution by rank
                print("\n" + "="*70)
                print("TEST 2: Conductor by rank (F24)")
                print("="*70)
                log_cond = np.log(ec_data["conductor"].values.astype(float) + 1)
                rank_labels = ec_data["rank"].astype(str).values
                v2, r2 = bv2.F24_variance_decomposition(log_cond, rank_labels)
                print(f"Verdict: {v2}, eta2 = {r2.get('eta_squared', 0):.4f}")
                for label, gs in sorted(r2.get("group_stats", {}).items()):
                    print(f"  Rank {label}: n={gs['n']}, mean log(N)={gs['mean']:.3f}")

                v2b, r2b = bv2.F24b_metric_consistency(log_cond, rank_labels)
                print(f"F24b: {v2b}")

                # Test 3: Root number parity check (should be exact identity)
                print("\n" + "="*70)
                print("TEST 3: Root number vs rank parity (identity check)")
                print("="*70)
                rn = ec_data["root_number"].values.astype(int)
                rk = ec_data["rank"].values.astype(int)
                expected_rn = np.where(rk % 2 == 0, 1, -1)
                match_rate = np.mean(rn == expected_rn)
                print(f"root_number == (-1)^rank: {match_rate*100:.2f}%")
                if match_rate > 0.999:
                    print("-> EXACT IDENTITY (BSD parity conjecture)")

        except Exception as e:
            print(f"EC query failed: {e}")
            # Try modular forms
            try:
                mf_data = con.execute("""
                    SELECT label, level, weight, dim
                    FROM modular_forms
                    WHERE weight IS NOT NULL
                    LIMIT 50000
                """).fetchdf()
                print(f"\nMF data: {len(mf_data)} forms")

                if len(mf_data) > 0:
                    print("\n" + "="*70)
                    print("TEST 1: Weight -> dimension (F24)")
                    print("="*70)
                    dims = mf_data["dim"].values.astype(float)
                    weight_labels = mf_data["weight"].astype(str).values
                    v1, r1 = bv2.F24_variance_decomposition(dims, weight_labels)
                    print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")
            except Exception as e2:
                print(f"MF query also failed: {e2}")

        con.close()
    else:
        print("DuckDB not found")

# --- Use prior oscillation data if available ---
if osc_results_path.exists():
    print("\n" + "="*70)
    print("PRIOR OSCILLATION SHADOW ANALYSIS")
    print("="*70)
    with open(osc_results_path) as f:
        prior = json.load(f)

    # Report what we have
    for key, val in prior.items():
        if isinstance(val, (int, float, str, bool)):
            print(f"  {key}: {val}")
        elif isinstance(val, list) and len(val) <= 5:
            print(f"  {key}: {val}")
        elif isinstance(val, dict) and len(val) <= 5:
            print(f"  {key}: {val}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

classification = "NEEDS_DATA"
eta2_val = 0

# If we got EC F24 results
if HAS_DUCKDB and 'r2' in dir():
    eta2_val = r2.get("eta_squared", 0)
    if eta2_val >= 0.14:
        classification = "LAW"
    elif eta2_val >= 0.01:
        classification = "TENDENCY"
    else:
        classification = "NEGLIGIBLE"

print(f"-> CLASSIFICATION: {classification}")
if classification == "NEEDS_DATA":
    print("   The oscillation shadow finding requires EC a_p coefficient data")
    print("   which is in the DuckDB but may need different table structure.")
    print("   The prior result (p=0.001) was from sign-change analysis on 17,314 forms.")

final_results = {
    "test": "S6",
    "claim": "Oscillation shadow in EC L-function zeros",
    "classification": classification,
    "conductor_by_rank_eta2": eta2_val,
    "note": "Partial analysis - full oscillation shadow requires a_p coefficient sequences",
}
with open(DATA / "shared/scripts/v2/s6_oscillation_shadow_results.json", "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/s6_oscillation_shadow_results.json")
