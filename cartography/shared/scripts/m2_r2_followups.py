#!/usr/bin/env python3
"""
M2 Round 2 — Follow-up tests (R2.1-R2.4)
R2.1: Random-prime ablation for C11 (kill or validate 3-prime fingerprint)
R2.2: Jaccard threshold sweep for C5 (kill or promote curvature)
R2.3: Class-balanced interaction resampling
R2.4: ICSD/AFLOW cross-validation for SC findings
"""
import sys, os, csv, io, re, json, glob
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)


def eta_sq(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


# Load SC data once
print("Loading superconductor data...")
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        formula = row.get("formula_sc", "").strip()
        if tc > 0 and sg and sc_class:
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            sc_rows.append({"tc": tc, "sg": sg, "sc_class": sc_class,
                           "formula": formula, "n_elements": len(elements)})
    except:
        pass
print(f"  {len(sc_rows)} superconductors\n")


# ============================================================
# R2.1: Random-prime ablation for C11
# ============================================================
print("=" * 100)
print("R2.1: RANDOM-PRIME ABLATION — Is (3,5,7) special or arbitrary?")
print("=" * 100)

def fingerprint_eta(primes, rows):
    labels = []
    tcs = []
    for r in rows:
        elems = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', r["formula"])
        counts = []
        for e, c in elems:
            if e:
                try: counts.append(float(c) if c else 1.0)
                except: counts.append(1.0)
        if counts:
            total = int(round(sum(counts)))
            fp = tuple(total % p for p in primes)
            labels.append(str(fp))
            tcs.append(r["tc"])
    if len(tcs) < 100:
        return float("nan"), 0, 0
    return eta_sq(tcs, labels)

prime_sets = [
    ("(3,5,7)", [3, 5, 7]),       # original
    ("(2,3,5)", [2, 3, 5]),       # smaller primes
    ("(5,7,11)", [5, 7, 11]),     # larger primes
    ("(2,5,11)", [2, 5, 11]),     # spread
    ("(7,11,13)", [7, 11, 13]),   # all large
    ("(3,7,13)", [3, 7, 13]),     # mixed
]

# Also random hash functions with same bucket count (~23 groups)
for trial in range(5):
    random_primes = sorted(rng.choice(range(2, 50), 3, replace=False))
    prime_sets.append((f"random_{trial} ({','.join(map(str,random_primes))})", list(random_primes)))

print(f"\n  {'Prime set':35s} | {'eta^2':>8s} | {'n':>6s} | {'groups':>6s}")
print("  " + "-" * 65)

results_r21 = []
for name, primes in prime_sets:
    eta, n, k = fingerprint_eta(primes, sc_rows)
    print(f"  {name:35s} | {eta:8.4f} | {n:6d} | {k:6d}")
    results_r21.append({"name": name, "primes": primes, "eta2": eta, "n": n, "k": k})

# Also test: element count as single variable (simplest possible)
eta_ne, n_ne, k_ne = eta_sq([r["tc"] for r in sc_rows], [r["n_elements"] for r in sc_rows])
print(f"  {'N_elements (no hashing)':35s} | {eta_ne:8.4f} | {n_ne:6d} | {k_ne:6d}")

# SC_class for comparison
eta_sc, n_sc, k_sc = eta_sq([r["tc"] for r in sc_rows], [r["sc_class"] for r in sc_rows])
print(f"  {'SC_class (baseline)':35s} | {eta_sc:8.4f} | {n_sc:6d} | {k_sc:6d}")

original_eta = results_r21[0]["eta2"]
other_etas = [r["eta2"] for r in results_r21[1:] if not np.isnan(r["eta2"])]
print(f"\n  Original (3,5,7) eta^2: {original_eta:.4f}")
print(f"  Other prime sets mean:  {np.mean(other_etas):.4f}")
print(f"  Other prime sets std:   {np.std(other_etas):.4f}")
print(f"  z-score of (3,5,7):     {(original_eta - np.mean(other_etas)) / np.std(other_etas):.1f}" if np.std(other_etas) > 0 else "")

if abs(original_eta - np.mean(other_etas)) < 2 * np.std(other_etas):
    print(f"\n  VERDICT: (3,5,7) is NOT special. Any prime set gives similar eta^2.")
    print(f"  C11 is a FEATURE ENGINEERING ARTIFACT — the hashing captures N_elements, not prime structure.")
    print(f"  KILL C11.")
else:
    print(f"\n  VERDICT: (3,5,7) stands out from other prime sets.")
    print(f"  C11 may carry genuine prime-arithmetic information.")


# ============================================================
# R2.2: Jaccard threshold sweep for C5
# ============================================================
print()
print("=" * 100)
print("R2.2: JACCARD THRESHOLD SWEEP — Is curvature stable across thresholds?")
print("=" * 100)

compositions = []
for r in sc_rows:
    elems = set(re.findall(r'[A-Z][a-z]?', r["formula"]))
    compositions.append(elems)

tc_arr = np.array([r["tc"] for r in sc_rows])
ne_arr = np.array([r["n_elements"] for r in sc_rows])

# Sample for speed
sample_size = min(1500, len(compositions))
sample_idx = rng.choice(len(compositions), sample_size, replace=False)
sample_tc = tc_arr[sample_idx]
sample_ne = ne_arr[sample_idx]

thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
print(f"\n  {'Threshold':>10s} | {'mean deg':>8s} | {'r(deg,Tc)':>10s} | {'partial r':>10s} | {'stable?'}")
print("  " + "-" * 60)

partial_rs = []
for thresh in thresholds:
    degrees = np.zeros(sample_size)
    for i in range(sample_size):
        count = 0
        for j in range(sample_size):
            if i != j:
                inter = len(compositions[sample_idx[i]] & compositions[sample_idx[j]])
                union = len(compositions[sample_idx[i]] | compositions[sample_idx[j]])
                if union > 0 and inter / union > thresh:
                    count += 1
        degrees[i] = count

    r_raw = np.corrcoef(degrees, sample_tc)[0, 1] if np.std(degrees) > 0 else 0

    # Partial after n_elements
    if np.std(degrees) > 0:
        X = np.column_stack([np.ones(sample_size), sample_ne])
        b_d = np.linalg.lstsq(X, degrees, rcond=None)[0]
        b_t = np.linalg.lstsq(X, sample_tc, rcond=None)[0]
        deg_r = degrees - X @ b_d
        tc_r = sample_tc - X @ b_t
        r_partial = np.corrcoef(deg_r, tc_r)[0, 1] if np.std(deg_r) > 0 else 0
    else:
        r_partial = 0

    partial_rs.append(r_partial)
    print(f"  {thresh:10.1f} | {np.mean(degrees):8.1f} | {r_raw:10.4f} | {r_partial:10.4f} |")

pr_arr = np.array(partial_rs)
cv = np.std(pr_arr) / np.mean(np.abs(pr_arr)) if np.mean(np.abs(pr_arr)) > 0 else float("inf")
print(f"\n  Partial r range: [{np.min(pr_arr):.4f}, {np.max(pr_arr):.4f}]")
print(f"  Partial r CV: {cv:.3f}")

if cv < 0.3 and np.min(np.abs(pr_arr)) > 0.1:
    print(f"  VERDICT: STABLE across thresholds. C5 curvature is REAL.")
elif np.max(np.abs(pr_arr)) > 0.3 and np.min(np.abs(pr_arr)) < 0.1:
    print(f"  VERDICT: THRESHOLD-DEPENDENT. C5 is an ARTIFACT of the 0.5 cutoff.")
    print(f"  KILL C5.")
else:
    print(f"  VERDICT: PARTIALLY STABLE. Effect persists but magnitude varies.")


# ============================================================
# R2.3: Class-balanced interaction resampling
# ============================================================
print()
print("=" * 100)
print("R2.3: CLASS-BALANCED INTERACTION — Is 8.5% inflated by imbalance?")
print("=" * 100)

tc_all = [r["tc"] for r in sc_rows]
sg_all = [r["sg"] for r in sc_rows]
sc_all = [r["sc_class"] for r in sc_rows]
n_total = len(tc_all)

# Find SGs that appear in >= 2 classes with >= 10 members each
sg_class_counts = defaultdict(lambda: defaultdict(int))
for r in sc_rows:
    sg_class_counts[r["sg"]][r["sc_class"]] += 1

balanced_sgs = []
for sg, class_dist in sg_class_counts.items():
    classes_with_10 = [c for c, n in class_dist.items() if n >= 10]
    if len(classes_with_10) >= 2:
        balanced_sgs.append(sg)

print(f"  SGs appearing in >= 2 classes with >= 10 each: {len(balanced_sgs)}")

if balanced_sgs:
    # Subsample: for each balanced SG, take equal n from each class
    balanced_rows = []
    for sg in balanced_sgs:
        class_pools = defaultdict(list)
        for r in sc_rows:
            if r["sg"] == sg:
                class_pools[r["sc_class"]].append(r)
        min_n = min(len(v) for v in class_pools.values() if len(v) >= 10)
        min_n = min(min_n, 50)  # cap per cell
        for cls, rows in class_pools.items():
            if len(rows) >= 10:
                sampled = rng.choice(len(rows), min(min_n, len(rows)), replace=False)
                for i in sampled:
                    balanced_rows.append(rows[i])

    print(f"  Balanced subsample: {len(balanced_rows)} rows, {len(balanced_sgs)} SGs")

    if len(balanced_rows) >= 100:
        b_tc = [r["tc"] for r in balanced_rows]
        b_sg = [r["sg"] for r in balanced_rows]
        b_sc = [r["sc_class"] for r in balanced_rows]

        # Additive model
        def one_hot(labels, n):
            unique = sorted(set(labels))
            mat = np.zeros((n, max(len(unique) - 1, 1)))
            for i, l in enumerate(labels):
                idx = unique.index(l)
                if idx > 0 and idx - 1 < mat.shape[1]:
                    mat[i, idx - 1] = 1
            return mat

        nb = len(b_tc)
        tc_b = np.array(b_tc)
        X_sc_b = one_hot(b_sc, nb)
        X_sg_b = one_hot(b_sg, nb)

        # SC only
        X1 = np.column_stack([np.ones(nb), X_sc_b])
        b1 = np.linalg.lstsq(X1, tc_b, rcond=None)[0]
        r2_sc = 1 - np.sum((tc_b - X1 @ b1)**2) / np.sum((tc_b - np.mean(tc_b))**2)

        # SC + SG (additive)
        X2 = np.column_stack([np.ones(nb), X_sc_b, X_sg_b])
        b2 = np.linalg.lstsq(X2, tc_b, rcond=None)[0]
        r2_add = 1 - np.sum((tc_b - X2 @ b2)**2) / np.sum((tc_b - np.mean(tc_b))**2)

        # Cell means (interaction)
        cell_labels = [f"{s}|{c}" for s, c in zip(b_sg, b_sc)]
        cell_groups = defaultdict(list)
        for v, cl in zip(tc_b, cell_labels):
            cell_groups[cl].append(v)
        cell_means = {cl: np.mean(v) for cl, v in cell_groups.items() if len(v) >= 2}
        pred_cell = np.array([cell_means.get(cl, np.mean(tc_b)) for cl in cell_labels])
        r2_cell = 1 - np.sum((tc_b - pred_cell)**2) / np.sum((tc_b - np.mean(tc_b))**2)

        r2_sg_incr = r2_add - r2_sc
        r2_inter = r2_cell - r2_add

        print(f"\n  BALANCED variance decomposition:")
        print(f"    SC_class:     {r2_sc:.4f}")
        print(f"    SG (incr):    {r2_sg_incr:.4f}")
        print(f"    Interaction:  {r2_inter:.4f}")
        print(f"    Residual:     {1 - r2_cell:.4f}")
        print(f"\n  UNBALANCED (from Round 1):")
        print(f"    SC_class:     0.5698")
        print(f"    SG (incr):    0.1409")
        print(f"    Interaction:  0.0853")

        if r2_inter < 0.03:
            print(f"\n  VERDICT: Interaction DEFLATES under balancing. Class imbalance was inflating it.")
        elif r2_inter > 0.06:
            print(f"\n  VERDICT: Interaction SURVIVES balancing. Real physics, not just imbalance.")
        else:
            print(f"\n  VERDICT: Interaction partially deflates. Some real signal, some artifact.")
else:
    print("  Insufficient multi-class SGs for balanced test")


# ============================================================
# R2.4: ICSD/AFLOW cross-validation
# ============================================================
print()
print("=" * 100)
print("R2.4: ICSD/AFLOW CROSS-VALIDATION — External replication")
print("=" * 100)

# Check for crossmatch data
sc_dir = DATA / "physics/data/superconductors"
crossmatch_files = list(sc_dir.glob("*crossmatch*")) + list(sc_dir.glob("*canonical*"))
print(f"\n  Cross-validation files found: {[f.name for f in crossmatch_files]}")

# Try to load COD crossmatch
cod_crossmatch = sc_dir / "cod_spacegroup_crossmatch.csv"
cod_canonical = sc_dir / "cod_canonical_superconductors.csv"
aflow_canonical = sc_dir / "aflow_canonical_superconductors.csv"

for fpath, label in [(cod_crossmatch, "COD crossmatch"), (cod_canonical, "COD canonical"), (aflow_canonical, "AFLOW canonical")]:
    if fpath.exists():
        print(f"\n  Loading {label}...")
        try:
            rows = []
            with open(fpath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cols = reader.fieldnames
                print(f"    Columns: {cols[:10]}")
                for row in reader:
                    rows.append(row)
            print(f"    Rows: {len(rows)}")

            # Check for Tc and SG columns
            tc_col = None
            sg_col = None
            sc_col = None
            for c in cols:
                cl = c.lower()
                if 'tc' in cl or 'critical' in cl:
                    tc_col = c
                if 'space' in cl or 'sg' in cl or 'spacegroup' in cl:
                    sg_col = c
                if 'class' in cl or 'family' in cl or 'sc_class' in cl:
                    sc_col = c

            print(f"    Tc column: {tc_col}")
            print(f"    SG column: {sg_col}")
            print(f"    SC_class column: {sc_col}")

            if tc_col and sg_col:
                valid = []
                for row in rows:
                    try:
                        tc = float(row[tc_col])
                        sg = row[sg_col].strip()
                        if tc > 0 and sg:
                            valid.append({"tc": tc, "sg": sg, "sc_class": row.get(sc_col, "").strip() if sc_col else ""})
                    except:
                        pass

                print(f"    Valid rows with Tc + SG: {len(valid)}")

                if len(valid) >= 30:
                    eta_rep, n_rep, k_rep = eta_sq([r["tc"] for r in valid], [r["sg"] for r in valid])
                    print(f"    eta^2(SG -> Tc): {eta_rep:.4f} (n={n_rep}, k={k_rep})")
                    print(f"    Main dataset:    0.4565")

                    if sc_col and any(r["sc_class"] for r in valid):
                        eta_sc_rep, _, _ = eta_sq([r["tc"] for r in valid if r["sc_class"]],
                                                   [r["sc_class"] for r in valid if r["sc_class"]])
                        print(f"    eta^2(SC_class -> Tc): {eta_sc_rep:.4f}")
                        print(f"    Main dataset:         0.5698")

                    v25, r25 = bv2.F25_transportability(
                        [r["tc"] for r in valid], [r["sg"] for r in valid],
                        [r.get("sc_class", "unknown") for r in valid] if sc_col else
                        ["group" + str(i % 3) for i in range(len(valid))])
                    print(f"    F25 transportability: {v25}")
                else:
                    print(f"    Insufficient data for replication")
        except Exception as e:
            print(f"    Error loading {label}: {e}")
    else:
        print(f"\n  {label}: file not found")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("R2 FOLLOW-UP SUMMARY")
print("=" * 100)
print(f"""
  R2.1 Random-prime ablation:
    (3,5,7) eta^2 = {original_eta:.4f}
    Other prime sets: mean = {np.mean(other_etas):.4f}, std = {np.std(other_etas):.4f}
    VERDICT: {'ARTIFACT — KILL C11' if abs(original_eta - np.mean(other_etas)) < 2 * np.std(other_etas) else 'SPECIAL — keep C11'}

  R2.2 Jaccard threshold sweep:
    Partial r range: [{np.min(pr_arr):.4f}, {np.max(pr_arr):.4f}]
    CV: {cv:.3f}

  R2.3 Class-balanced interaction:
    {'See balanced decomposition above' if balanced_sgs else 'Insufficient data'}

  R2.4 ICSD/AFLOW replication:
    {'See results above' if crossmatch_files else 'No crossmatch data found'}
""")
