#!/usr/bin/env python3
"""
Priority 1: Re-audit ALL genocide survivors (R1-R7) through F24 + F24b.

For each survivor, compute:
- eta^2 (categorical->continuous) or R^2 (continuous->continuous)
- Tail contribution from F24b
- Classify as LAW / CONSTRAINT / TENDENCY / NEGLIGIBLE

The genocide tests proved these effects are REAL (permutation p < 0.01).
F24 now asks: how BIG are they? And are they tail-driven?
"""

import sys, os, json, math, re as re_mod
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent  # cartography/
rng = np.random.default_rng(42)


def load_json(relpath):
    with open(DATA / relpath, "r", encoding="utf-8") as f:
        return json.load(f)


def r_squared(x, y):
    """Simple linear R^2."""
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 10:
        return float("nan"), len(x)
    r = np.corrcoef(x, y)[0, 1]
    return r**2, len(x)


def eta_sq(values, labels, min_group=5):
    """Compute eta^2."""
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm) ** 2)
    ss_between = sum(len(v) * (np.mean(v) - gm) ** 2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


def classify(eta, tail_contrib, is_tail_driven=False):
    if np.isnan(eta):
        return "SKIP"
    if is_tail_driven and eta < 0.14:
        return "CONSTRAINT"
    elif eta >= 0.14:
        return "LAW"
    elif eta >= 0.01:
        return "TENDENCY"
    else:
        return "NEGLIGIBLE"


def omega(n):
    if n <= 1: return 0
    count, d = 0, 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0: n //= d
        d += 1
    if n > 1: count += 1
    return count


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


# ============================================================
# Load all datasets
# ============================================================
print("Loading datasets...")

# Knots
knots_data = load_json("knots/data/knots.json")
knots = knots_data["knots"]

# Elliptic curves
import duckdb
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_rows = con.execute("""
    SELECT conductor, cm, rank, torsion, faltings_height, bad_primes, semistable
    FROM elliptic_curves WHERE conductor > 0
""").fetchall()
# Also get modular form counts per level
try:
    mf_counts = dict(con.execute("SELECT level, COUNT(*) FROM modular_forms GROUP BY level").fetchall())
except:
    mf_counts = {}
con.close()

# Number fields
nf = load_json("number_fields/data/number_fields.json")

# Genus-2
g2 = load_json("genus2/data/genus2_curves_full.json")

# Isogenies
iso_path = DATA / "isogenies/data"
iso_data = {}
if iso_path.exists():
    for f in iso_path.glob("*.json"):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if isinstance(d, dict) and "prime" in d:
                iso_data[d["prime"]] = d
        except:
            pass

# Space groups
sg_data = []
sg_path = DATA / "spacegroups/data/space_groups.json"
if sg_path.exists():
    sg_data = load_json("spacegroups/data/space_groups.json")

# Polytopes
poly_data = []
poly_path = DATA / "polytopes/data/polytopes.json"
if poly_path.exists():
    poly_data = load_json("polytopes/data/polytopes.json")

# Fungrim
fungrim = []
fungrim_path = DATA / "fungrim/data/fungrim_formulas.json"
if fungrim_path.exists():
    fungrim = load_json("fungrim/data/fungrim_formulas.json")

# mathlib
mathlib = []
mathlib_path = DATA / "mathlib/data/mathlib_imports.json"
if mathlib_path.exists():
    mathlib = load_json("mathlib/data/mathlib_imports.json")

# MMLKG
mmlkg = []
mmlkg_path = DATA / "mmlkg/data/mmlkg_articles.json"
if mmlkg_path.exists():
    mmlkg = load_json("mmlkg/data/mmlkg_articles.json")

# Superconductors
import csv, io
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
        if tc > 0 and sg:
            r = {"tc": tc, "sg": sg, "sc_class": sc_class, "formula": formula}
            for key, col in [("vol", "cell_volume_2"), ("density", "density_2"),
                             ("fe", "formation_energy_per_atom_2"), ("bg", "band_gap_2")]:
                try: r[key] = float(row.get(col, ""))
                except: r[key] = None
            elements = set(re_mod.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
    except:
        pass

print(f"  knots={len(knots)}, ec={len(ec_rows)}, nf={len(nf)}, g2={len(g2)}, sc={len(sc_rows)}")
print(f"  iso_primes={len(iso_data)}, sg={len(sg_data)}, poly={len(poly_data)}")
print(f"  fungrim={len(fungrim)}, mathlib={len(mathlib)}, mmlkg={len(mmlkg)}")
print()

# ============================================================
# Build the re-audit tests
# ============================================================
results = []


def audit(name, test_type, values=None, labels=None, x=None, y=None, source="", claim=""):
    """Run F24 on a finding. test_type: 'categorical' or 'correlation'."""
    if test_type == "categorical" and values is not None and labels is not None:
        v24, r24 = bv2.F24_variance_decomposition(values, labels)
        v24b, r24b = bv2.F24b_metric_consistency(values, labels)
        eta = r24.get("eta_squared", float("nan"))
        tail_c = r24b.get("tail_contribution", float("nan"))
        n = r24.get("n_total", len(values))
        k = r24.get("n_groups", 0)
        is_td = "TAIL_DRIVEN" in v24b
        ftype = classify(eta, tail_c, is_td)
    elif test_type == "correlation" and x is not None and y is not None:
        r2, n = r_squared(x, y)
        eta = r2
        tail_c = float("nan")
        k = 0
        ftype = classify(eta, 0)
        v24b = "R2"
    else:
        return

    print(f"  {name:6s} | {ftype:11s} | eta2={eta:.4f} | n={n:6d} | g={k:3d} | {source:8s} | {claim[:55]}")
    results.append({"name": name, "type": ftype, "eta2": eta, "n": n, "source": source, "claim": claim})


# ============================================================
# RE-AUDIT: R1 survivors
# ============================================================
print("=" * 110)
print("GENOCIDE SURVIVOR RE-AUDIT through F24 + F24b")
print(f"{'ID':>6s} | {'TYPE':11s} | {'eta2/R2':>10s} | {'n':>6s} | {'g':>3s} | {'source':8s} | claim")
print("-" * 110)

# --- KNOT DOMAIN ---
# H1: Determinant ~ Alexander polynomial length
det = [k["determinant"] for k in knots if k.get("determinant") and k.get("alexander_coeffs")]
alex_len = [len(k["alexander_coeffs"]) for k in knots if k.get("determinant") and k.get("alexander_coeffs")]
audit("R1.1", "correlation", x=det, y=alex_len, source="R1", claim="Determinant ~ Alexander polynomial length")

# H2: Jones sum: even vs odd crossing
even_jones = [sum(abs(c) for c in k.get("jones_coeffs", [])) for k in knots
              if k.get("jones_coeffs") and k.get("crossing_number") and k["crossing_number"] % 2 == 0]
odd_jones = [sum(abs(c) for c in k.get("jones_coeffs", [])) for k in knots
             if k.get("jones_coeffs") and k.get("crossing_number") and k["crossing_number"] % 2 == 1]
jones_vals = even_jones + odd_jones
jones_labels = ["even"] * len(even_jones) + ["odd"] * len(odd_jones)
audit("R1.2", "categorical", values=jones_vals, labels=jones_labels, source="R1",
      claim="Jones sum: even vs odd crossing")

# H3: Determinant ~ max Alexander coefficient
det3 = [k["determinant"] for k in knots if k.get("determinant") and k.get("alexander_coeffs")]
max_alex = [max(abs(c) for c in k["alexander_coeffs"]) for k in knots if k.get("determinant") and k.get("alexander_coeffs")]
audit("R1.3", "correlation", x=det3, y=max_alex, source="R1", claim="Determinant ~ max Alexander coeff")

# H6: Symbol count: equations vs definitions (Fungrim)
if fungrim:
    eq_syms = [len(f.get("symbols", [])) for f in fungrim if f.get("type") == "equation"]
    def_syms = [len(f.get("symbols", [])) for f in fungrim if f.get("type") == "definition"]
    if eq_syms and def_syms:
        vals = eq_syms + def_syms
        labs = ["equation"] * len(eq_syms) + ["definition"] * len(def_syms)
        audit("R1.6", "categorical", values=vals, labels=labs, source="R1",
              claim="Symbol count: equations vs definitions")

# H7: Module size ~ bridge symbol count (mathlib)
if mathlib:
    m_sizes = []
    m_imports = []
    for m in mathlib:
        if isinstance(m, dict) and m.get("n_imports") is not None:
            m_sizes.append(m.get("n_imports", 0))
            m_imports.append(len(m.get("imports", [])))
    if len(m_sizes) > 10:
        audit("R1.7", "correlation", x=m_sizes, y=m_imports, source="R1",
              claim="Module size ~ bridge symbol count")

# H8: Crossing number: det-is-conductor vs det-is-not
ec_conductors = set(r[0] for r in ec_rows)
knot_is_cond = [k["crossing_number"] for k in knots if k.get("crossing_number") and k.get("determinant") and k["determinant"] in ec_conductors]
knot_not_cond = [k["crossing_number"] for k in knots if k.get("crossing_number") and k.get("determinant") and k["determinant"] not in ec_conductors]
if knot_is_cond and knot_not_cond:
    vals = knot_is_cond + knot_not_cond
    labs = ["is_cond"] * len(knot_is_cond) + ["not_cond"] * len(knot_not_cond)
    audit("R1.8", "categorical", values=vals, labels=labs, source="R1",
          claim="Crossing: det-is-conductor vs not")

# --- R2 survivors ---
# Jones length ~ crossing number
j_len = [len(k.get("jones_coeffs", [])) for k in knots if k.get("jones_coeffs") and k.get("crossing_number")]
cn = [k["crossing_number"] for k in knots if k.get("jones_coeffs") and k.get("crossing_number")]
audit("R2.1", "correlation", x=cn, y=j_len, source="R2", claim="Jones length ~ crossing number")

# Alexander variance ~ crossing number
a_var = [float(np.var(k["alexander_coeffs"])) for k in knots if k.get("alexander_coeffs") and k.get("crossing_number")]
cn2 = [k["crossing_number"] for k in knots if k.get("alexander_coeffs") and k.get("crossing_number")]
audit("R2.2", "correlation", x=cn2, y=a_var, source="R2", claim="Alexander variance ~ crossing number")

# Div by 2,3,5: rank-0 vs rank-1 (BSD small-prime)
for div in [2, 3, 5]:
    r0 = [r[0] for r in ec_rows if r[2] == 0]
    r1 = [r[0] for r in ec_rows if r[2] == 1]
    r0_frac = sum(1 for c in r0 if c % div == 0) / len(r0) if r0 else 0
    r1_frac = sum(1 for c in r1 if c % div == 0) / len(r1) if r1 else 0
    # This is a proportion test, not directly eta^2. Use categorical.
    vals = [1 if c % div == 0 else 0 for c in [r[0] for r in ec_rows if r[2] in (0, 1)]]
    labs = [r[2] for r in ec_rows if r[2] in (0, 1)]
    audit(f"R2.d{div}", "categorical", values=vals, labels=labs, source="R2",
          claim=f"Div by {div}: rank-0 vs rank-1 conductor")

# --- R3 survivors ---
# EC count per N ~ MF count per N (modularity)
if mf_counts:
    shared_levels = [n for n in mf_counts if any(r[0] == n for r in ec_rows)]
    if shared_levels:
        ec_counts_per = []
        mf_counts_per = []
        for n in shared_levels[:5000]:
            ec_c = sum(1 for r in ec_rows if r[0] == n)
            mf_c = mf_counts.get(n, 0)
            ec_counts_per.append(ec_c)
            mf_counts_per.append(mf_c)
        audit("R3.5", "correlation", x=ec_counts_per, y=mf_counts_per, source="R3",
              claim="EC count per N ~ MF count per N (modularity)")

# Conductor digit entropy: rank-0 vs rank-1
def digit_entropy(n):
    s = str(abs(n))
    from collections import Counter
    c = Counter(s)
    total = len(s)
    return -sum((v/total) * math.log2(v/total) for v in c.values())

r0_ent = [digit_entropy(r[0]) for r in ec_rows if r[2] == 0 and r[0] > 99]
r1_ent = [digit_entropy(r[0]) for r in ec_rows if r[2] == 1 and r[0] > 99]
if r0_ent and r1_ent:
    vals = r0_ent + r1_ent
    labs = ["rank0"] * len(r0_ent) + ["rank1"] * len(r1_ent)
    audit("R3.3", "categorical", values=vals, labels=labs, source="R3",
          claim="Conductor digit entropy: rank-0 vs rank-1")

# --- R4 survivors ---
# Alexander(-1) ~ Jones(-1)
a_at_neg1 = []
j_at_neg1 = []
for k in knots:
    ac = k.get("alexander_coeffs", [])
    jc = k.get("jones_coeffs", [])
    if ac and jc:
        # Evaluate at t=-1
        a_val = sum(c * (-1)**i for i, c in enumerate(ac))
        j_val = sum(c * (-1)**i for i, c in enumerate(jc))
        a_at_neg1.append(abs(a_val))
        j_at_neg1.append(abs(j_val))
audit("R4.6", "correlation", x=a_at_neg1, y=j_at_neg1, source="R4",
      claim="Alexander(-1) ~ Jones(-1)")

# max Jones coeff ~ determinant
max_jones = [max(abs(c) for c in k["jones_coeffs"]) for k in knots if k.get("jones_coeffs") and k.get("determinant")]
det4 = [k["determinant"] for k in knots if k.get("jones_coeffs") and k.get("determinant")]
audit("R4.5", "correlation", x=det4, y=max_jones, source="R4", claim="max Jones coeff ~ determinant")

# omega: rank-0 vs rank-2
r0_om = [omega(r[0]) for r in ec_rows if r[2] == 0 and r[0] > 1]
r2_om = [omega(r[0]) for r in ec_rows if r[2] == 2 and r[0] > 1]
if r0_om and r2_om:
    vals = r0_om + r2_om
    labs = ["rank0"] * len(r0_om) + ["rank2"] * len(r2_om)
    audit("R4.7", "categorical", values=vals, labels=labs, source="R4",
          claim="omega: rank-0 vs rank-2 conductors")

# Mean conductor: rank-0 vs rank-2
r0_cond = [r[0] for r in ec_rows if r[2] == 0]
r2_cond = [r[0] for r in ec_rows if r[2] == 2]
if r0_cond and r2_cond:
    vals = r0_cond + r2_cond
    labs = ["rank0"] * len(r0_cond) + ["rank2"] * len(r2_cond)
    audit("R4.8", "categorical", values=vals, labels=labs, source="R4",
          claim="Mean conductor: rank-0 vs rank-2")

# EC per prime conductor vs composite
prime_ec = [r[0] for r in ec_rows if is_prime(r[0])]
comp_ec = [r[0] for r in ec_rows if not is_prime(r[0]) and r[0] > 1]
# Not quite right - this was about count of EC per conductor.
# Use: is the conductor prime or composite as a grouping on some EC property
# Actually the test was about HOW MANY EC share the same conductor level
from collections import Counter
cond_counts = Counter(r[0] for r in ec_rows)
prime_counts = [cond_counts[c] for c in cond_counts if is_prime(c)]
comp_counts = [cond_counts[c] for c in cond_counts if not is_prime(c) and c > 1]
if prime_counts and comp_counts:
    vals = prime_counts + comp_counts
    labs = ["prime"] * len(prime_counts) + ["composite"] * len(comp_counts)
    audit("R4.10", "categorical", values=vals, labels=labs, source="R4",
          claim="EC per prime vs composite conductor level")

# MF/EC ratio ~ conductor
if mf_counts:
    ratios = []
    conds = []
    for c in sorted(cond_counts.keys()):
        if c in mf_counts and cond_counts[c] > 0:
            ratios.append(mf_counts[c] / cond_counts[c])
            conds.append(c)
    if len(ratios) > 10:
        audit("R4.13", "correlation", x=conds, y=ratios, source="R4",
              claim="MF/EC ratio ~ conductor value")

# --- R5 survivors ---
# Class number: degree-2 vs degree-3
d2_cn = [f["class_number"] for f in nf if f.get("class_number") and f.get("degree") == 2]
d3_cn = [f["class_number"] for f in nf if f.get("class_number") and f.get("degree") == 3]
if d2_cn and d3_cn:
    vals = d2_cn + d3_cn
    labs = ["deg2"] * len(d2_cn) + ["deg3"] * len(d3_cn)
    audit("R5.1", "categorical", values=vals, labels=labs, source="R5",
          claim="Class number: degree-2 vs degree-3 fields")

# Class number: Galois groups
valid_nf_gal = [f for f in nf if f.get("class_number") and f.get("galois_label")]
if valid_nf_gal:
    vals = [f["class_number"] for f in valid_nf_gal]
    labs = [f["galois_label"] for f in valid_nf_gal]
    audit("R5.2", "categorical", values=vals, labels=labs, source="R5",
          claim="Class number by Galois group")

# NF regulator ~ EC conductor density
# This was z=4.8, weak cross-domain
valid_nf_reg = [f for f in nf if f.get("regulator") and f.get("disc_abs")]
if valid_nf_reg:
    regs = [f["regulator"] for f in valid_nf_reg]
    discs = [f["disc_abs"] for f in valid_nf_reg]
    audit("R5.3", "correlation", x=discs, y=regs, source="R5",
          claim="NF regulator ~ discriminant (proxy for conductor density)")

# Isogeny Deuring mass: nodes ~ (p-1)/12
if iso_data:
    primes = sorted(iso_data.keys())
    nodes = []
    deuring = []
    for p in primes:
        d = iso_data[p]
        n = d.get("n_vertices", d.get("nodes", 0))
        if n > 0 and p > 2:
            nodes.append(n)
            deuring.append((p - 1) / 12)
    if len(nodes) > 5:
        audit("R5.4", "correlation", x=deuring, y=nodes, source="R5",
              claim="Isogeny nodes ~ (p-1)/12 (Deuring mass)")

# Polytope dim ~ f-vector sum
if poly_data:
    dims = [p["dimension"] for p in poly_data if isinstance(p, dict) and p.get("dimension") and p.get("f_vector")]
    fv_sums = [sum(p["f_vector"]) for p in poly_data if isinstance(p, dict) and p.get("dimension") and p.get("f_vector")]
    if dims:
        audit("R5.8", "correlation", x=dims, y=fv_sums, source="R5",
              claim="Polytope dimension ~ f-vector sum")

# MMLKG hub vs leaf reference density
if mmlkg:
    hub_refs = [m.get("n_references", 0) for m in mmlkg if isinstance(m, dict) and m.get("n_references", 0) > 10]
    leaf_refs = [m.get("n_references", 0) for m in mmlkg if isinstance(m, dict) and m.get("n_references", 0) <= 10 and m.get("n_references", 0) > 0]
    if hub_refs and leaf_refs:
        vals = hub_refs + leaf_refs
        labs = ["hub"] * len(hub_refs) + ["leaf"] * len(leaf_refs)
        audit("R5.13", "categorical", values=vals, labels=labs, source="R5",
              claim="MMLKG hub vs leaf reference density")

# --- R6 survivors ---
# S3a: L(1,chi) proxy ~ isogeny nodes
# S4a: isogeny nodes ~ MF count at level p
if iso_data and mf_counts:
    primes6 = sorted(iso_data.keys())
    iso_nodes = []
    mf_at_p = []
    for p in primes6:
        d = iso_data[p]
        n = d.get("n_vertices", d.get("nodes", 0))
        mf_c = mf_counts.get(p, 0)
        if n > 0 and mf_c > 0:
            iso_nodes.append(n)
            mf_at_p.append(mf_c)
    if len(iso_nodes) > 5:
        audit("R6.4", "correlation", x=iso_nodes, y=mf_at_p, source="R6",
              claim="Isogeny nodes ~ MF count at level p")

# --- SUPERCONDUCTOR LAWS (from reaudit_20) ---
# Include for completeness - these are the benchmarks
audit("SC.1", "categorical",
      values=[r["tc"] for r in sc_rows if r["sc_class"]],
      labels=[r["sc_class"] for r in sc_rows if r["sc_class"]],
      source="reaudit", claim="SC class -> Tc (BASELINE LAW)")

audit("SC.2", "categorical",
      values=[r["tc"] for r in sc_rows],
      labels=[r["sg"] for r in sc_rows],
      source="reaudit", claim="SG -> Tc (BASELINE LAW)")

# --- GENUS-2 tests ---
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
audit("G2.1", "categorical",
      values=[c["conductor"] for c in valid_g2],
      labels=[c["st_group"] for c in valid_g2],
      source="G2", claim="ST group -> conductor")

audit("G2.2", "categorical",
      values=[abs(c["discriminant"]) for c in valid_g2 if c.get("discriminant", 0) != 0],
      labels=[c["st_group"] for c in valid_g2 if c.get("discriminant", 0) != 0],
      source="G2", claim="ST group -> |discriminant|")

# Crossing number -> determinant
valid_knots = [k for k in knots if k.get("determinant") and k.get("crossing_number")]
audit("KN.1", "categorical",
      values=[k["determinant"] for k in valid_knots],
      labels=[k["crossing_number"] for k in valid_knots],
      source="knots", claim="Crossing number -> determinant (LAW candidate)")


# ============================================================
# META-ANALYSIS
# ============================================================
print()
print("=" * 110)
print("META-ANALYSIS: Full re-audit classification")
print("=" * 110)

types = defaultdict(list)
for r in results:
    types[r["type"]].append(r)

print(f"\n  Total re-audited: {len(results)}")
for t in ["LAW", "CONSTRAINT", "TENDENCY", "NEGLIGIBLE", "SKIP"]:
    items = types.get(t, [])
    print(f"\n  {t} ({len(items)}):")
    for r in sorted(items, key=lambda x: -x["eta2"] if not np.isnan(x["eta2"]) else 0):
        print(f"    {r['name']:8s}: eta2={r['eta2']:.4f} | [{r['source']:8s}] {r['claim'][:60]}")

# Detection bias analysis
print()
print("=" * 110)
print("DETECTION BIAS ANALYSIS")
print("=" * 110)

laws = types.get("LAW", [])
constraints = types.get("CONSTRAINT", [])
tendencies = types.get("TENDENCY", [])
negligible = types.get("NEGLIGIBLE", [])

print(f"\n  Previously high-z survivors now reclassified:")
for r in results:
    if r["type"] in ("NEGLIGIBLE", "TENDENCY") and r["source"] in ("R1", "R2", "R3", "R4", "R5", "R6"):
        print(f"    {r['name']:8s}: {r['type']:11s} eta2={r['eta2']:.4f} | {r['claim'][:55]}")

print(f"\n  LAWs from genocide that were always strong:")
for r in results:
    if r["type"] == "LAW" and r["source"] in ("R1", "R2", "R3", "R4", "R5", "R6"):
        print(f"    {r['name']:8s}: LAW          eta2={r['eta2']:.4f} | {r['claim'][:55]}")
