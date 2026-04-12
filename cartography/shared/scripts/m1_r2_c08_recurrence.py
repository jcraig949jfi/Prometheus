"""C08/R2: Recurrence operator duality -- OEIS vs elliptic curve traces.
Test if consecutive differences satisfy a linear recurrence of order k.
EC traces should be depleted (0.25x prior) vs OEIS (22% baseline).
Battery v2 (F24/F24b/F25/F27). Machine: M1 (Skullport), 2026-04-12
"""
import sys, json, re
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# ============================================================
# Recurrence detection utility
# ============================================================
def test_linear_recurrence(seq, max_order=5, residual_threshold=0.01):
    """Test if a sequence satisfies a linear recurrence of order <= max_order.
    Returns (is_recurrence, best_order, best_residual).
    """
    seq = np.array(seq, dtype=float)
    if len(seq) < max_order + 10:
        return False, 0, 1.0

    best_order = 0
    best_residual = 1.0

    for k in range(1, max_order + 1):
        # Build Toeplitz-like system: seq[k:] = c_0*seq[k-1:...] + ... + c_{k-1}*seq[0:...]
        n = len(seq) - k
        if n < k + 5:
            continue

        # Design matrix
        X = np.column_stack([seq[k - j - 1: k - j - 1 + n] for j in range(k)])
        y = seq[k: k + n]

        # Least squares
        try:
            coeffs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
        except np.linalg.LinAlgError:
            continue

        predicted = X @ coeffs
        ss_res = np.sum((y - predicted) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        if ss_tot == 0:
            # Constant sequence -- trivially recurrent
            return True, 1, 0.0

        relative_residual = ss_res / ss_tot

        if relative_residual < best_residual:
            best_residual = relative_residual
            best_order = k

    is_recurrence = best_residual < residual_threshold
    return is_recurrence, best_order, best_residual


# ============================================================
# Load OEIS data
# ============================================================
print("Loading OEIS sequences from stripped_new.txt...")
oeis_path = DATA / "oeis/data/stripped_new.txt"

oeis_sequences = []
MAX_OEIS = 20000  # Sample for speed
count = 0

with open(oeis_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Format: A-number ,term1,term2,...
        # Split on first space to get A-number, rest is comma-separated
        parts = line.split(" ", 1)
        if len(parts) < 2:
            # Try comma split: A000001 ,0,1,1,...
            idx = line.find(",")
            if idx < 0:
                continue
            a_num = line[:idx].strip()
            terms_str = line[idx:]
        else:
            a_num = parts[0].strip()
            terms_str = parts[1]

        # Parse terms -- strip leading/trailing commas
        terms_str = terms_str.strip().strip(",")
        if not terms_str:
            continue

        try:
            terms = [int(t.strip()) for t in terms_str.split(",") if t.strip()]
        except ValueError:
            continue

        if len(terms) >= 20:
            oeis_sequences.append({
                "id": a_num,
                "terms": terms[:100],  # cap at 100 terms
            })
            count += 1
            if count >= MAX_OEIS:
                break

print(f"Loaded {len(oeis_sequences)} OEIS sequences with >= 20 terms")

# ============================================================
# Load EC trace data from DuckDB
# ============================================================
print("Loading elliptic curve traces from DuckDB...")
import duckdb
con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)

ec_df = con.execute("""
    SELECT lmfdb_label, conductor, rank
    FROM elliptic_curves
    WHERE rank IS NOT NULL
    LIMIT 20000
""").fetchdf()

mf_df = con.execute("""
    SELECT lmfdb_label, level, weight, traces
    FROM modular_forms
    WHERE traces IS NOT NULL AND weight = 2
    LIMIT 10000
""").fetchdf()
print(f"Loaded {len(ec_df)} elliptic curves, {len(mf_df)} weight-2 modular forms")

# Extract trace sequences from modular forms (these are the a_p values)
ec_trace_sequences = []
for _, row in mf_df.iterrows():
    traces = row.get("traces")
    if traces is None or not isinstance(traces, (list, np.ndarray)):
        continue
    t = []
    for x in traces[:100]:
        if x is not None:
            try:
                t.append(int(x))
            except (ValueError, TypeError):
                continue
    if len(t) >= 20:
        ec_trace_sequences.append({
            "label": row.get("lmfdb_label", "?"),
            "level": int(row.get("level") or 0),
            "traces": t,
        })

print(f"  {len(ec_trace_sequences)} trace sequences with >= 20 terms")

# ============================================================
# TEST 1: Recurrence rates -- OEIS
# ============================================================
print("\n" + "="*70)
print("TEST 1: Recurrence rate in OEIS sequences")
print("="*70)

oeis_recurrence_count = 0
oeis_orders = []
oeis_residuals = []

for seq in oeis_sequences:
    diffs = np.diff(seq["terms"])
    if len(diffs) < 15:
        continue
    is_rec, order, resid = test_linear_recurrence(diffs, max_order=5)
    oeis_residuals.append(resid)
    if is_rec:
        oeis_recurrence_count += 1
        oeis_orders.append(order)

oeis_rate = oeis_recurrence_count / max(len(oeis_sequences), 1)
print(f"  Tested: {len(oeis_sequences)} sequences")
print(f"  Recurrent (diff satisfies linear recurrence): {oeis_recurrence_count}")
print(f"  Rate: {oeis_rate*100:.1f}%")
print(f"  Prior baseline: ~22%")
if oeis_orders:
    order_counts = defaultdict(int)
    for o in oeis_orders:
        order_counts[o] += 1
    print(f"  Order distribution: {dict(sorted(order_counts.items()))}")

# ============================================================
# TEST 2: Recurrence rates -- EC traces
# ============================================================
print("\n" + "="*70)
print("TEST 2: Recurrence rate in EC trace sequences")
print("="*70)

ec_recurrence_count = 0
ec_orders = []
ec_residuals = []
ec_levels_rec = []
ec_levels_nonrec = []

for seq in ec_trace_sequences:
    diffs = np.diff(seq["traces"])
    if len(diffs) < 15:
        continue
    is_rec, order, resid = test_linear_recurrence(diffs, max_order=5)
    ec_residuals.append(resid)
    if is_rec:
        ec_recurrence_count += 1
        ec_orders.append(order)
        ec_levels_rec.append(seq["level"])
    else:
        ec_levels_nonrec.append(seq["level"])

ec_rate = ec_recurrence_count / max(len(ec_trace_sequences), 1)
print(f"  Tested: {len(ec_trace_sequences)} trace sequences")
print(f"  Recurrent: {ec_recurrence_count}")
print(f"  Rate: {ec_rate*100:.1f}%")
print(f"  Prior expectation: ~{22*0.25:.0f}% (0.25x depletion of 22% baseline)")
if ec_orders:
    order_counts = defaultdict(int)
    for o in ec_orders:
        order_counts[o] += 1
    print(f"  Order distribution: {dict(sorted(order_counts.items()))}")

ratio = ec_rate / max(oeis_rate, 1e-6)
print(f"\n  EC/OEIS ratio: {ratio:.3f}x (prior: 0.25x)")

# ============================================================
# TEST 3: F24 -- recurrence by domain (OEIS vs EC)
# ============================================================
print("\n" + "="*70)
print("TEST 3: F24 -- residual quality by domain")
print("="*70)

all_residuals = []
all_domain_labels = []
for r in oeis_residuals:
    all_residuals.append(r)
    all_domain_labels.append("OEIS")
for r in ec_residuals:
    all_residuals.append(r)
    all_domain_labels.append("EC")

if len(all_residuals) >= 30 and len(set(all_domain_labels)) >= 2:
    v24, r24 = bv2.F24_variance_decomposition(
        np.array(all_residuals), all_domain_labels
    )
    print(f"F24 verdict: {v24}")
    print(f"  eta^2 = {r24.get('eta_squared', 0):.4f}")
    for gname, gstat in r24.get("group_stats", {}).items():
        print(f"  Domain '{gname}': n={gstat['n']}, mean_residual={gstat['mean']:.4f}")
else:
    v24, r24 = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24")

# ============================================================
# TEST 4: F24 -- recurrence rate by EC rank
# ============================================================
print("\n" + "="*70)
print("TEST 4: F24 -- recurrence residual by EC level bracket")
print("="*70)

ec_level_labels = []
ec_resid_vals = []
for i, seq in enumerate(ec_trace_sequences):
    if i >= len(ec_residuals):
        break
    lev = seq["level"]
    if lev <= 50:
        bracket = "<=50"
    elif lev <= 200:
        bracket = "51-200"
    elif lev <= 1000:
        bracket = "201-1000"
    else:
        bracket = ">1000"
    ec_level_labels.append(bracket)
    ec_resid_vals.append(ec_residuals[i])

if len(ec_resid_vals) >= 30 and len(set(ec_level_labels)) >= 2:
    v24_ec, r24_ec = bv2.F24_variance_decomposition(
        np.array(ec_resid_vals), ec_level_labels
    )
    print(f"F24 verdict: {v24_ec}")
    print(f"  eta^2 = {r24_ec.get('eta_squared', 0):.4f}")
    for gname, gstat in r24_ec.get("group_stats", {}).items():
        print(f"  Level bracket '{gname}': n={gstat['n']}, mean={gstat['mean']:.4f}")
else:
    v24_ec, r24_ec = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24 by level")

# ============================================================
# TEST 5: F24b -- metric consistency
# ============================================================
print("\n" + "="*70)
print("TEST 5: F24b -- metric consistency (domain comparison)")
print("="*70)

if len(all_residuals) >= 40 and len(set(all_domain_labels)) >= 2:
    v24b, r24b = bv2.F24b_metric_consistency(
        np.array(all_residuals), all_domain_labels
    )
    print(f"F24b verdict: {v24b}")
    print(f"  M4/M2 ratio = {r24b.get('m4m2_ratio', 'N/A')}")
else:
    v24b, r24b = "INSUFFICIENT_DATA", {}
    print("Insufficient data for F24b")

# ============================================================
# TEST 6: F25 -- transportability
# ============================================================
print("\n" + "="*70)
print("TEST 6: F25 -- transportability across level brackets")
print("="*70)

# Primary: domain (OEIS vs EC), secondary: level bracket or OEIS id prefix
prim_labels = []
sec_labels = []
transport_vals = []

for i, r in enumerate(oeis_residuals):
    prim_labels.append("OEIS")
    # Use first digit of A-number as secondary grouping
    a_id = oeis_sequences[i]["id"] if i < len(oeis_sequences) else "A0"
    digit = a_id[1] if len(a_id) > 1 else "0"
    sec_labels.append(f"A{digit}xxxxx")
    transport_vals.append(r)

for i, r in enumerate(ec_residuals):
    prim_labels.append("EC")
    bracket = ec_level_labels[i] if i < len(ec_level_labels) else "?"
    sec_labels.append(f"EC_{bracket}")
    transport_vals.append(r)

if len(set(sec_labels)) >= 2:
    v25, r25 = bv2.F25_transportability(
        np.array(transport_vals), prim_labels, sec_labels
    )
    print(f"F25 verdict: {v25}")
    print(f"  Weighted OOS R^2 = {r25.get('weighted_oos_r2', 'N/A')}")
else:
    v25, r25 = "INSUFFICIENT_DATA", {}
    print("Insufficient secondary groups for F25")

# ============================================================
# TEST 7: F27 -- consequence check
# ============================================================
print("\n" + "="*70)
print("TEST 7: F27 -- tautology check")
print("="*70)

v27, r27 = bv2.F27_consequence_check("sequence_domain", "recurrence_rate")
print(f"F27 verdict: {v27}")
if r27:
    print(f"  Details: {r27}")

# ============================================================
# CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

print(f"OEIS recurrence rate: {oeis_rate*100:.1f}% (prior: ~22%)")
print(f"EC recurrence rate: {ec_rate*100:.1f}% (prior: ~5.5% = 0.25 x 22%)")
print(f"EC/OEIS ratio: {ratio:.3f}x (prior: 0.25x)")
print(f"F24 domain effect: {v24} (eta^2={r24.get('eta_squared','N/A')})")
print(f"F24b: {v24b}")
print(f"F25: {v25}")
print(f"F27: {v27}")

if ratio < 0.5 and r24.get("eta_squared", 0) > 0.01:
    classification = "EC_DEPLETED"
    print(f"\n--> EC trace sequences are depleted in recurrence ({ratio:.2f}x of OEIS)")
elif ratio < 0.5:
    classification = "WEAK_DEPLETION"
    print(f"\n--> Weak depletion signal ({ratio:.2f}x) but small F24 effect")
else:
    classification = "NO_DEPLETION"
    print(f"\n--> No significant depletion: EC rate comparable to OEIS")

# ============================================================
# Save results
# ============================================================
final_results = {
    "test": "C08/R2",
    "claim": "EC traces depleted in recurrence vs OEIS (0.25x prior)",
    "oeis_recurrence_rate": oeis_rate,
    "ec_recurrence_rate": ec_rate,
    "ec_oeis_ratio": ratio,
    "oeis_n_tested": len(oeis_sequences),
    "ec_n_tested": len(ec_trace_sequences),
    "f24_domain": {"verdict": v24, "result": r24},
    "f24_ec_level": {"verdict": v24_ec, "result": r24_ec},
    "f24b": {"verdict": v24b, "result": r24b},
    "f25": {"verdict": v25, "result": r25},
    "f27": {"verdict": v27, "result": r27},
    "classification": classification,
}

out_path = Path(__file__).resolve().parent / "v2" / "c08_recurrence_results.json"
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c08_recurrence_results.json")
