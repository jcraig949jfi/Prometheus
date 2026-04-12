#!/usr/bin/env python3
"""
M1 R3 — Number fields (5) + EC/MF (7) + Fungrim/formal (7) = 19 tests, run on M2
"""
import sys, os, json, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

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
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10: return float("nan")
    vn = arr / np.mean(arr)
    return np.mean(vn**4) / np.mean(vn**2)**2

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
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

results = []
def rec(name, cls, eta2=None, metric=""):
    results.append({"name": name, "cls": cls, "eta2": eta2, "metric": metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:30s} | {cls:20s} | {e:15s} | {metric}")

# ============================================================
# NUMBER FIELDS (5 tests)
# ============================================================
print("=" * 100)
print("NUMBER FIELD TESTS")
print("=" * 100)

nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
# Cast all numeric-looking fields to float
nf = []
for f in nf_raw:
    r = {}
    for k, v in f.items():
        if isinstance(v, str):
            try: r[k] = float(v)
            except: r[k] = v
        else:
            r[k] = v
    nf.append(r)
print(f"  {len(nf)} number fields\n")

# C72: NF hR/sqrt(D) moment ratio
valid_nf = [f for f in nf if f.get("regulator") and f.get("disc_abs")]
valid_nf = [f for f in valid_nf if float(f["disc_abs"]) > 0]
if valid_nf:
    ratios = [float(f["regulator"]) * float(f.get("class_number", 1)) / np.sqrt(float(f["disc_abs"])) for f in valid_nf if f.get("class_number")]
    ratios = [r for r in ratios if np.isfinite(r) and r > 0]
    if ratios:
        ratio_m4 = m4m2(ratios)
        # By degree
        deg_labels = [f["degree"] for f in valid_nf if f.get("class_number") and f.get("degree")][:len(ratios)]
        if len(deg_labels) == len(ratios):
            eta, n, k = eta_sq(ratios, deg_labels)
            rec("C72 hR/sqrt(D)", "LAW" if eta >= 0.14 else "TENDENCY", eta,
                f"M4/M2^2={ratio_m4:.2f} degree->ratio n={n}")

# C91: Galois -> disc within degree 4
deg4 = [f for f in nf if f.get("degree") == 4 and f.get("galois_label") and f.get("disc_abs")]
if deg4:
    eta, n, k = eta_sq([f["disc_abs"] for f in deg4], [f["galois_label"] for f in deg4])
    rec("C91 galois->disc_deg4", "LAW" if eta >= 0.14 else "TENDENCY", eta,
        f"n={n} k={k} (degree 4 only)")

# G.R5.3: NF regulator ~ discriminant
valid_reg = [f for f in nf if f.get("regulator") and f.get("disc_abs")]
if valid_reg:
    r = np.corrcoef([f["regulator"] for f in valid_reg], [f["disc_abs"] for f in valid_reg])[0, 1]
    rec("G.R5.3 reg~disc", "LAW" if r**2 >= 0.14 else "TENDENCY", r**2, f"r={r:.4f}")

# G.R5.nf: NF disc — class# in knot dets vs not
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 1)
nf_with_cn = [f for f in nf if f.get("class_number") and f.get("disc_abs")]
if nf_with_cn and knot_dets:
    in_knot = [f["disc_abs"] for f in nf_with_cn if f["class_number"] in knot_dets]
    not_knot = [f["disc_abs"] for f in nf_with_cn if f["class_number"] not in knot_dets]
    if in_knot and not_knot:
        vals = in_knot + not_knot
        labs = ["in_knot"] * len(in_knot) + ["not_knot"] * len(not_knot)
        eta, n, k = eta_sq(vals, labs)
        rec("G.R5.nf cn_in_knot_det", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
            f"n_in={len(in_knot)} n_out={len(not_knot)}")

# G.R5.sg: NF disc — class# in SG point group orders vs not
try:
    sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
    pg_orders = set(s.get("point_group_order", 0) for s in sg_data if s.get("point_group_order"))
    in_pg = [f["disc_abs"] for f in nf_with_cn if f["class_number"] in pg_orders]
    not_pg = [f["disc_abs"] for f in nf_with_cn if f["class_number"] not in pg_orders]
    if in_pg and not_pg:
        vals = in_pg + not_pg
        labs = ["in_pg"] * len(in_pg) + ["not_pg"] * len(not_pg)
        eta, n, k = eta_sq(vals, labs)
        rec("G.R5.sg cn_in_pg_order", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
            f"n_in={len(in_pg)} n_out={len(not_pg)}")
except:
    rec("G.R5.sg", "SKIP", metric="SG data not loaded")

# ============================================================
# EC/MF TESTS (7 tests)
# ============================================================
print("\n" + "=" * 100)
print("EC/MF TESTS")
print("=" * 100)

import duckdb
ROOT = Path(__file__).resolve().parents[3]
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_rows = con.execute("SELECT conductor, rank, torsion, cm FROM elliptic_curves WHERE conductor > 0").fetchall()
try:
    mf_counts = dict(con.execute("SELECT level, COUNT(*) FROM modular_forms GROUP BY level").fetchall())
except:
    mf_counts = {}
con.close()
print(f"  {len(ec_rows)} EC, {len(mf_counts)} MF levels\n")

# G.R2.d7/d11/d13: Div by 7,11,13 rank-0 vs rank-1
for div in [7, 11, 13]:
    r0r1 = [(1 if r[0] % div == 0 else 0, r[1]) for r in ec_rows if r[1] in (0, 1)]
    if r0r1:
        vals = [x[0] for x in r0r1]
        labs = [x[1] for x in r0r1]
        eta, n, k = eta_sq(vals, labs)
        rec(f"G.R2.d{div} div_rank", "NEGLIGIBLE" if eta < 0.01 else "TENDENCY", eta,
            f"n={n}")

# G.R3.ec: EC per conductor is NOT Poisson
cond_counts = Counter(r[0] for r in ec_rows)
counts = list(cond_counts.values())
if counts:
    from scipy.stats import kstest, poisson
    mean_c = np.mean(counts)
    ks = kstest(counts, poisson(mean_c).cdf)
    rec("G.R3.ec not_poisson", "CONSTRAINT" if ks.pvalue < 0.001 else "NEGLIGIBLE",
        metric=f"KS={ks.statistic:.4f} p={ks.pvalue:.4e} mean={mean_c:.2f}")

# G.R4.mod: Rank-2 conductor mod 12 vs rank-0
r0_mod12 = Counter(r[0] % 12 for r in ec_rows if r[1] == 0)
r2_mod12 = Counter(r[0] % 12 for r in ec_rows if r[1] == 2)
if r0_mod12 and r2_mod12:
    # Chi-squared test
    all_residues = sorted(set(r0_mod12.keys()) | set(r2_mod12.keys()))
    obs_r0 = [r0_mod12.get(r, 0) for r in all_residues]
    obs_r2 = [r2_mod12.get(r, 0) for r in all_residues]
    from scipy.stats import chi2_contingency
    table = np.array([obs_r0, obs_r2])
    if table.sum() > 0:
        chi2, p, dof, expected = chi2_contingency(table)
        rec("G.R4.mod r2_mod12", "CONSTRAINT" if p < 0.001 else "NEGLIGIBLE",
            metric=f"chi2={chi2:.1f} p={p:.4e} dof={dof}")

# C89: Torsion -> root number
# Need root number — check if available
torsion_rn = [(r[2], 1 if r[0] % 2 == 0 else -1) for r in ec_rows if r[2] is not None and r[2] > 0]
if torsion_rn:
    vals = [x[1] for x in torsion_rn]
    labs = [str(x[0]) for x in torsion_rn]
    eta, n, k = eta_sq(vals, labs)
    rec("C89 torsion->rn_proxy", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
        f"n={n} k={k} (rn approximated by conductor parity)")

# C51-f24: EC conductor M4/M^2
ec_conds = [r[0] for r in ec_rows if r[0] > 0]
if ec_conds:
    ratio = m4m2(ec_conds)
    # By rank
    rank_labels = [r[1] for r in ec_rows if r[0] > 0 and r[1] is not None]
    conds_with_rank = [r[0] for r in ec_rows if r[0] > 0 and r[1] is not None]
    eta, n, k = eta_sq(conds_with_rank, rank_labels)
    rec("C51 ec_cond_f24", "TENDENCY" if eta >= 0.01 else "NEGLIGIBLE", eta,
        f"M4/M2^2={ratio:.2f} rank->cond n={n}")

# ============================================================
# FUNGRIM/FORMAL TESTS (7 tests)
# ============================================================
print("\n" + "=" * 100)
print("FUNGRIM/FORMAL TESTS")
print("=" * 100)

fungrim = json.load(open(DATA / "fungrim/data/fungrim_formulas.json", encoding="utf-8"))
print(f"  {len(fungrim)} formulas\n")

# G.R1.6: Symbol count — equations vs definitions (already done in unblocked, confirm)
types = defaultdict(list)
for f in fungrim:
    t = f.get("type", "unknown")
    syms = f.get("symbols", [])
    types[t].append(len(syms) if isinstance(syms, list) else 0)

# G.R2.pi: Pi formulas have more symbols
pi_syms = [len(f.get("symbols", [])) for f in fungrim if "pi" in str(f.get("symbols", [])).lower() or "Pi" in str(f.get("formula_text", ""))]
non_pi_syms = [len(f.get("symbols", [])) for f in fungrim if "pi" not in str(f.get("symbols", [])).lower() and "Pi" not in str(f.get("formula_text", ""))]
if pi_syms and non_pi_syms:
    vals = pi_syms + non_pi_syms
    labs = ["pi"] * len(pi_syms) + ["non_pi"] * len(non_pi_syms)
    eta, n, k = eta_sq(vals, labs)
    rec("G.R2.pi has_pi->n_sym", "TENDENCY" if eta >= 0.01 else "NEGLIGIBLE", eta,
        f"pi={len(pi_syms)} non_pi={len(non_pi_syms)} mean_pi={np.mean(pi_syms):.1f} mean_other={np.mean(non_pi_syms):.1f}")

# G.R2.zeta: Zeta concentrated in fewer modules
zeta_mods = set(f.get("module") for f in fungrim if "zeta" in str(f.get("symbols", [])).lower() or "Zeta" in str(f.get("formula_text", "")))
all_mods = set(f.get("module") for f in fungrim if f.get("module"))
rec("G.R2.zeta module_conc", "TENDENCY" if len(zeta_mods) < len(all_mods) * 0.3 else "NEGLIGIBLE",
    metric=f"zeta in {len(zeta_mods)}/{len(all_mods)} modules")

# G.R4.fung: Later formulas have more symbols (within module)
# Check: is there a position effect within modules?
mod_formulas = defaultdict(list)
for i, f in enumerate(fungrim):
    m = f.get("module")
    if m:
        mod_formulas[m].append(len(f.get("symbols", [])))

growth_rs = []
for m, sym_counts in mod_formulas.items():
    if len(sym_counts) >= 10:
        positions = np.arange(len(sym_counts), dtype=float)
        r = np.corrcoef(positions, sym_counts)[0, 1]
        if np.isfinite(r):
            growth_rs.append(r)

if growth_rs:
    mean_r = np.mean(growth_rs)
    rec("G.R4.fung within_mod_growth", "TENDENCY" if abs(mean_r) > 0.1 else "NEGLIGIBLE",
        metric=f"mean within-module r(position, n_sym)={mean_r:.4f} across {len(growth_rs)} modules")

# C75: Fungrim symbol usage analysis
all_symbols = []
for f in fungrim:
    syms = f.get("symbols", [])
    if isinstance(syms, list):
        all_symbols.extend(syms)
sym_counts = Counter(all_symbols)
top_10 = sym_counts.most_common(10)
rec("C75 symbol_usage", "MEASURED", metric=f"top: {', '.join(f'{s}({c})' for s,c in top_10[:5])}")

# C23: FindStat combinatorial statistics
findstat_path = DATA / "findstat/data/findstat_index.json"
if findstat_path.exists():
    fs = json.load(open(findstat_path, encoding="utf-8"))
    if isinstance(fs, list):
        print(f"\n  FindStat: {len(fs)} statistics")
        if fs and isinstance(fs[0], dict):
            print(f"  Keys: {list(fs[0].keys())[:6]}")
            # Check for any categorical grouping
            collections = [s.get("collection", s.get("domain", "unknown")) for s in fs]
            values_available = [s.get("n_values", s.get("size", 0)) for s in fs]
            if any(v > 0 for v in values_available):
                eta, n, k = eta_sq(values_available, collections)
                rec("C23 findstat coll->size", "LAW" if eta >= 0.14 else "TENDENCY", eta,
                    f"n={n} k={k}")
            else:
                rec("C23 findstat", "MEASURED", metric=f"{len(fs)} stats, {len(set(collections))} collections")
    else:
        rec("C23", "SKIP", metric="FindStat format unexpected")
else:
    findstat_enriched = DATA / "findstat/data/findstat_enriched.json"
    if findstat_enriched.exists():
        fs = json.load(open(findstat_enriched, encoding="utf-8"))
        rec("C23 findstat", "MEASURED", metric=f"{len(fs)} entries (enriched)")
    else:
        rec("C23", "SKIP", metric="FindStat not found")

# C76: FindStat enriched data
if findstat_enriched.exists() if 'findstat_enriched' in dir() else (DATA / "findstat/data/findstat_enriched.json").exists():
    try:
        fs_e = json.load(open(DATA / "findstat/data/findstat_enriched.json", encoding="utf-8"))
        rec("C76 findstat_enriched", "MEASURED", metric=f"{len(fs_e)} enriched entries")
    except:
        rec("C76", "SKIP", metric="Load error")
else:
    rec("C76", "SKIP", metric="Not found")

# Summary
print("\n" + "=" * 100)
print("M1 R3 NF/EC/FUNGRIM BATCH SUMMARY")
print("=" * 100)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:30s} | {r['cls']:20s} | {e:15s} | {r['metric'][:50]}")
