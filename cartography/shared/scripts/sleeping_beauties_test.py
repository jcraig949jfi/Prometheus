#!/usr/bin/env python3
"""
Sleeping Beauties: Test the top 3 immediately actionable untested datasets.

1. Moonshine McKay-Thompson sequences vs MF
2. Discovery candidates triage (top 100 by z-score)
3. Root probe results (knot polynomial root spacing)
"""
import sys, os, json, glob
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, ks_2samp

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("SLEEPING BEAUTIES: Testing untouched data")
print("=" * 100)


# ============================================================
# 1. MOONSHINE: McKay-Thompson sequences vs Modular Forms
# ============================================================
print("\n" + "=" * 100)
print("1. MOONSHINE ↔ MODULAR FORMS")
print("=" * 100)

moonshine_dir = DATA / "convergence/data/moonshine"
if moonshine_dir.exists():
    mckay_files = sorted(moonshine_dir.glob("mckay_*.json"))
    print(f"  McKay-Thompson files: {len(mckay_files)}")

    # Load the J-function (class 1A = the identity element of Monster)
    j_func = None
    for f in mckay_files:
        if "1A" in f.name or "A000521" in f.name:
            j_data = json.load(open(f, encoding="utf-8"))
            if isinstance(j_data, dict):
                j_func = j_data.get("coefficients", j_data.get("values", j_data.get("terms")))
            elif isinstance(j_data, list):
                j_func = j_data
            print(f"  J-function ({f.name}): {type(j_func)}, {len(j_func) if j_func else 0} terms")
            if j_func and len(j_func) > 5:
                print(f"  First terms: {j_func[:8]}")
            break

    if j_func is None:
        # Try summary
        summary_path = moonshine_dir / "mckay_thompson_summary.json"
        if summary_path.exists():
            summary = json.load(open(summary_path, encoding="utf-8"))
            print(f"  Summary keys: {list(summary.keys())[:5] if isinstance(summary, dict) else type(summary)}")
            if isinstance(summary, dict):
                for cls, data in list(summary.items())[:3]:
                    print(f"    Class {cls}: {type(data)}, {str(data)[:100]}")

    # Load MF data at level 1 (where J-function lives)
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    mf_level1 = con.execute("""
        SELECT lmfdb_label, ap_coeffs, weight FROM modular_forms
        WHERE level = 1 LIMIT 100
    """).fetchall()
    con.close()
    print(f"  MF at level 1: {len(mf_level1)}")
    for label, ap, weight in mf_level1[:3]:
        print(f"    {label}: weight={weight}, ap type={type(ap)}")

    # The J-function is weight 0, level 1. LMFDB might not have it as a "modular form"
    # since it's a modular function (weight 0), not a cusp form.
    print(f"\n  NOTE: J-function is weight 0 (modular function), not weight 2 (cusp form).")
    print(f"  LMFDB classical modular forms are weight ≥ 1. J may not be in the MF table.")
    print(f"  This is a KNOWN gap — the moonshine bridge operates at weight 0,")
    print(f"  while LMFDB focuses on weight ≥ 1.")

    # Alternative test: do moonshine coefficients correlate with EC/MF counts?
    # The coefficient c_n of the J-function counts the number of Monster representations
    # at grade n. These are related to EC conductors at level n.
    if j_func and isinstance(j_func, list) and len(j_func) > 10:
        # Try to load as integers
        j_coeffs = []
        for c in j_func[:200]:
            try: j_coeffs.append(int(float(c)))
            except: break

        if j_coeffs:
            con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
            ec_by_level = dict(con.execute("""
                SELECT conductor, COUNT(*) FROM elliptic_curves
                WHERE conductor > 0 AND conductor <= 200
                GROUP BY conductor
            """).fetchall())
            con.close()

            # Correlate J-function coefficients with EC count at matching conductor
            shared = sorted(set(range(1, len(j_coeffs))) & set(ec_by_level.keys()))
            if len(shared) >= 10:
                j_vals = [j_coeffs[n] for n in shared]
                ec_vals = [ec_by_level[n] for n in shared]
                rho, p = spearmanr(j_vals, ec_vals)
                print(f"\n  J-function coefficients vs EC count at conductor n:")
                print(f"  rho = {rho:.4f}, p = {p:.4e} (n={len(shared)} shared levels)")

                if abs(rho) > 0.1 and p < 0.01:
                    print(f"  SIGNAL: Moonshine coefficients correlate with EC density.")
                else:
                    print(f"  NO SIGNAL: No correlation between J coefficients and EC counts.")
else:
    print(f"  Moonshine directory not found at {moonshine_dir}")


# ============================================================
# 2. DISCOVERY CANDIDATES: Triage top 100
# ============================================================
print("\n" + "=" * 100)
print("2. DISCOVERY CANDIDATES TRIAGE")
print("=" * 100)

disc_path = DATA / "convergence/data/discovery_candidates.jsonl"
if disc_path.exists():
    candidates = []
    with open(disc_path) as f:
        for line in f:
            try:
                c = json.loads(line.strip())
                if isinstance(c, dict):
                    candidates.append(c)
            except:
                pass
            if len(candidates) >= 10000:
                break

    print(f"  Discovery candidates loaded: {len(candidates)}")
    if candidates:
        # What fields do they have?
        print(f"  Sample keys: {list(candidates[0].keys())[:10]}")

        # Sort by z-score or significance
        scored = []
        for c in candidates:
            z = c.get("z_score", c.get("z", c.get("significance", 0)))
            try:
                z = float(z)
                scored.append((z, c))
            except:
                pass

        scored.sort(key=lambda x: -abs(x[0]))
        print(f"  With z-scores: {len(scored)}")

        if scored:
            print(f"\n  Top 20 by |z|:")
            print(f"  {'z':>8s} | {'type':15s} | description")
            print("  " + "-" * 70)
            domains_seen = Counter()
            for z, c in scored[:20]:
                desc = str(c.get("description", c.get("hypothesis", c.get("claim", "?"))))[:50]
                ctype = c.get("type", c.get("category", "?"))
                domains = c.get("domains", c.get("dataset_pair", "?"))
                print(f"  {z:8.1f} | {str(ctype):15s} | {desc}")
                if isinstance(domains, str):
                    domains_seen[domains] += 1

            # Distribution of candidate types
            type_dist = Counter(c.get("type", c.get("category", "?")) for _, c in scored)
            print(f"\n  Type distribution: {dict(type_dist.most_common(10))}")

            # How many would survive F24 permutation null?
            # Quick estimate: z > 3 is our threshold
            survive_z3 = sum(1 for z, _ in scored if abs(z) > 3)
            survive_z10 = sum(1 for z, _ in scored if abs(z) > 10)
            print(f"\n  Would survive z > 3: {survive_z3}/{len(scored)}")
            print(f"  Would survive z > 10: {survive_z10}/{len(scored)}")
else:
    print(f"  discovery_candidates.jsonl not found")


# ============================================================
# 3. ROOT PROBES: Knot polynomial root spacing
# ============================================================
print("\n" + "=" * 100)
print("3. ROOT PROBES: Knot polynomial root spacing statistics")
print("=" * 100)

root_path = DATA / "convergence/data/root_probe_results.jsonl"
if root_path.exists():
    roots = []
    with open(root_path) as f:
        for line in f:
            try:
                r = json.loads(line.strip())
                if isinstance(r, dict):
                    roots.append(r)
            except:
                pass
            if len(roots) >= 5000:
                break

    print(f"  Root probes loaded: {len(roots)}")
    if roots:
        print(f"  Sample keys: {list(roots[0].keys())[:10]}")

        # Extract angle spacing statistics
        all_spacings = []
        all_angles = []
        for r in roots:
            angles = r.get("root_angles", r.get("angles", []))
            if isinstance(angles, list) and len(angles) >= 3:
                angles = sorted([float(a) for a in angles])
                gaps = np.diff(angles)
                if len(gaps) > 0:
                    mean_gap = np.mean(gaps)
                    if mean_gap > 0:
                        normalized = gaps / mean_gap
                        all_spacings.extend(normalized.tolist())
                all_angles.extend(angles)

        print(f"  Normalized angle spacings: {len(all_spacings)}")
        print(f"  Total root angles: {len(all_angles)}")

        if all_spacings:
            spacings = np.array(all_spacings)
            mean_s = np.mean(spacings)
            var_s = np.var(spacings)
            skew_s = np.mean(((spacings - mean_s) / np.std(spacings))**3) if np.std(spacings) > 0 else 0
            kurt_s = np.mean(((spacings - mean_s) / np.std(spacings))**4) if np.std(spacings) > 0 else 0

            print(f"\n  Root angle spacing statistics:")
            print(f"    Mean: {mean_s:.4f} (normalized to 1)")
            print(f"    Var:  {var_s:.4f} (GUE≈0.18, Poisson≈1.0, CUE≈0.18)")
            print(f"    Skew: {skew_s:.4f} (GUE≈0.66, Poisson≈2.0)")
            print(f"    Kurt: {kurt_s:.4f} (GUE≈3.27, Poisson≈9.0)")

            gue_dist = abs(var_s - 0.178) + abs(skew_s - 0.66)
            poi_dist = abs(var_s - 1.0) + abs(skew_s - 2.0)
            print(f"\n    Distance to GUE: {gue_dist:.3f}")
            print(f"    Distance to Poisson: {poi_dist:.3f}")
            print(f"    Better fit: {'GUE (LEVEL REPULSION)' if gue_dist < poi_dist else 'POISSON (INDEPENDENT)'}")

            frac_small = np.mean(spacings < 0.1)
            print(f"    Fraction s < 0.1: {frac_small:.4f} (GUE≈0.004, Poisson≈0.095)")

            if gue_dist < poi_dist:
                print(f"\n  FINDING: Knot polynomial roots show GUE-like level repulsion!")
                print(f"  This would connect topology to random matrix theory —")
                print(f"  the same universality class as L-function zeros (Montgomery-Odlyzko).")
            else:
                print(f"\n  Knot roots show Poisson spacing (independent, no repulsion).")
else:
    print(f"  root_probe_results.jsonl not found")


# ============================================================
# BONUS: Check g2c_endomorphisms (genus-2 endomorphism data)
# ============================================================
print("\n" + "=" * 100)
print("BONUS: Genus-2 endomorphism rings (lmfdb_dump)")
print("=" * 100)

endo_path = DATA / "lmfdb_dump/g2c_endomorphisms.json"
if endo_path.exists():
    size = os.path.getsize(endo_path)
    print(f"  File size: {size / 1e6:.1f} MB")

    # Sample the first few records
    with open(endo_path) as f:
        content = f.read(5000)
    try:
        sample = json.loads(content) if content.startswith("[") else json.loads("[" + content.split("\n")[0] + "]")
        if isinstance(sample, list) and sample:
            print(f"  First record keys: {list(sample[0].keys())[:10]}")
            print(f"  Sample: {json.dumps(sample[0], indent=2)[:300]}")
    except:
        print(f"  Format: {content[:200]}")
else:
    print(f"  g2c_endomorphisms.json not found in lmfdb_dump/")

# Check smf_fc (Siegel modular form Fourier coefficients)
smf_path = DATA / "lmfdb_dump/smf_fc.json"
if smf_path.exists():
    size = os.path.getsize(smf_path)
    print(f"\n  Siegel MF Fourier coeffs: {size / 1e6:.1f} MB")
    with open(smf_path) as f:
        line = f.readline()
    print(f"  First line: {line[:200]}")
else:
    print(f"\n  smf_fc.json not found")


print("\n" + "=" * 100)
print("SLEEPING BEAUTIES SUMMARY")
print("=" * 100)
