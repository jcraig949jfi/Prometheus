#!/usr/bin/env python3
"""
M2 Round 3 — Previously blocked tests, now unblocked by data parsing.
Knot Alexander/Conway tests, Polytope F24, Space group cross-domain,
Fungrim symbol tests, Maass Fricke, NIST config enrichment.
"""
import sys, os, json
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
    m2 = np.mean(vn**2); m4 = np.mean(vn**4)
    return m4 / m2**2 if m2 > 0 else float("nan")

results = []
def record(name, classification, eta2=None, key_metric=""):
    results.append({"name": name, "cls": classification, "eta2": eta2, "metric": key_metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:25s} | {classification:20s} | {e:15s} | {key_metric}")

# ============================================================
# KNOT TESTS (with parsed coefficients)
# ============================================================
print("=" * 100)
print("KNOT TESTS — Alexander/Conway coefficients now populated")
print("=" * 100)

knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
has_alex = [k for k in knots if k.get("alex_coeffs")]
has_conway = [k for k in knots if k.get("conway_coeffs")]
print(f"  Knots with alex_coeffs: {len(has_alex)}")
print(f"  Knots with conway_coeffs: {len(has_conway)}\n")

# C35 revisit: crossing -> determinant with Alexander control
print("C35 revisit: crossing -> det with Alexander degree control")
valid = [k for k in has_alex if k.get("determinant") and k.get("crossing_number")]
if valid:
    cn = np.array([k["crossing_number"] for k in valid], dtype=float)
    det = np.array([k["determinant"] for k in valid], dtype=float)
    alex_deg = np.array([len(k["alex_coeffs"]) for k in valid], dtype=float)

    # Verify identity: det = |Alexander(-1)|
    matches = 0
    for k in valid:
        coeffs = k["alex_coeffs"]
        alex_neg1 = sum(c * (-1)**i for i, c in enumerate(coeffs))
        if abs(abs(alex_neg1) - k["determinant"]) < 0.5:
            matches += 1
    print(f"  det = |Alexander(-1)| verification: {matches}/{len(valid)} ({matches/len(valid)*100:.1f}%)")

    # Partial: crossing -> det after Alexander degree
    X = np.column_stack([np.ones(len(cn)), alex_deg])
    b_d = np.linalg.lstsq(X, det, rcond=None)[0]
    b_c = np.linalg.lstsq(X, cn, rcond=None)[0]
    det_r = det - X @ b_d
    cn_r = cn - X @ b_c
    r_partial = np.corrcoef(cn_r, det_r)[0, 1]
    record("C35-alex-ctrl", "IDENTITY-MEDIATED", r_partial**2,
           f"partial r={r_partial:.4f} after alex_deg, identity={matches}/{len(valid)}")

# Alexander entropy by crossing number
print("\nAlexander entropy by crossing number")
for cn_val in [7, 8, 9, 10]:
    cn_knots = [k for k in has_alex if k.get("crossing_number") == cn_val]
    if len(cn_knots) >= 5:
        entropies = []
        for k in cn_knots:
            coeffs = np.array(k["alex_coeffs"], dtype=float)
            coeffs = np.abs(coeffs)
            total = np.sum(coeffs)
            if total > 0:
                p = coeffs / total
                p = p[p > 0]
                entropies.append(-np.sum(p * np.log2(p)))
        if entropies:
            print(f"  CN={cn_val}: n={len(entropies)}, mean entropy={np.mean(entropies):.3f}, std={np.std(entropies):.3f}")

# Conway moments (C54 with real data)
print("\nC54: Conway polynomial moments (with parsed coefficients)")
if has_conway:
    all_conway_coeffs = []
    for k in has_conway:
        all_conway_coeffs.extend([abs(c) for c in k["conway_coeffs"] if c != 0])
    if all_conway_coeffs:
        ratio = m4m2(all_conway_coeffs)
        record("C54-conway", "MEASURED", key_metric=f"M4/M2^2={ratio:.2f} n={len(all_conway_coeffs)}")

    # Per-crossing M4/M2^2
    cn_conway_m4 = []
    cn_labels = []
    for k in has_conway:
        if k.get("crossing_number"):
            coeffs = [abs(c) for c in k["conway_coeffs"] if c != 0]
            if len(coeffs) >= 3:
                r = m4m2(coeffs)
                if np.isfinite(r):
                    cn_conway_m4.append(r)
                    cn_labels.append(k["crossing_number"])
    if cn_conway_m4:
        eta, n, kg = eta_sq(cn_conway_m4, cn_labels)
        record("C54-crossing", "LAW" if eta >= 0.14 else "TENDENCY", eta,
               f"crossing->conway_M4 n={n}")

# ============================================================
# POLYTOPE TESTS (normalized data)
# ============================================================
print("\n" + "=" * 100)
print("POLYTOPE TESTS — 980 polytopes with normalized keys")
print("=" * 100)

polytopes = json.load(open(DATA / "polytopes/data/polytopes.json", encoding="utf-8"))
print(f"  {len(polytopes)} polytopes\n")

# C27: dim -> f-vector sum
fv_data = [(p["dimension"], sum(p["f_vector"])) for p in polytopes if p.get("f_vector") and p.get("dimension")]
if fv_data:
    dims = [d for d, _ in fv_data]
    fv_sums = [s for _, s in fv_data]
    eta, n, k = eta_sq(fv_sums, dims)
    v24, r24 = bv2.F24_variance_decomposition(fv_sums, dims)
    record("C27-fvec", v24, eta, f"dim->fvec_sum n={n} k={k}")

# Euler characteristic
chi_data = []
for p in polytopes:
    if p.get("f_vector"):
        fv = p["f_vector"]
        chi = sum((-1)**i * f for i, f in enumerate(fv))
        chi_data.append(chi)
if chi_data:
    vals = Counter(chi_data)
    print(f"  Euler chi distribution: {dict(vals.most_common(5))}")
    n_standard = sum(1 for c in chi_data if c in (0, 1, 2))
    record("R5.poly-euler", "REDISCOVERY" if n_standard/len(chi_data) > 0.8 else "TENDENCY",
           key_metric=f"chi standard: {n_standard}/{len(chi_data)} ({n_standard/len(chi_data)*100:.0f}%)")

# ============================================================
# SPACE GROUP CROSS-DOMAIN
# ============================================================
print("\n" + "=" * 100)
print("SPACE GROUP CROSS-DOMAIN — 230 SGs")
print("=" * 100)

sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
print(f"  {len(sg_data)} space groups")
if sg_data:
    sample = sg_data[0]
    print(f"  Keys: {list(sample.keys())}")

# SG number ~ Wyckoff count
wyckoff_data = [(s.get("number"), s.get("n_wyckoff", len(s.get("wyckoff_positions", s.get("wyckoff", [])))))
                for s in sg_data if isinstance(s, dict) and s.get("number")]
wyckoff_data = [(n, w) for n, w in wyckoff_data if w > 0]
if wyckoff_data:
    sg_nums = [n for n, _ in wyckoff_data]
    wy_counts = [w for _, w in wyckoff_data]
    r = np.corrcoef(sg_nums, wy_counts)[0, 1]
    record("R5.sg-wyckoff", "TENDENCY" if r**2 >= 0.01 else "NEGLIGIBLE", r**2,
           f"r(SG#, Wyckoff)={r:.4f} n={len(wyckoff_data)}")

# SG point group order ~ NF degree overlap
pg_orders = set()
for s in sg_data:
    pgo = s.get("point_group_order", s.get("pg_order"))
    if pgo: pg_orders.add(int(pgo))

nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf_degrees = set(f.get("degree") for f in nf if f.get("degree"))
overlap = pg_orders & nf_degrees
record("R5.nfsg-overlap", "TENDENCY" if len(overlap) >= 3 else "NEGLIGIBLE",
       key_metric=f"PG orders: {sorted(pg_orders)[:8]}, NF degrees: {sorted(nf_degrees)}, overlap: {sorted(overlap)}")

# ============================================================
# FUNGRIM TESTS
# ============================================================
print("\n" + "=" * 100)
print("FUNGRIM TESTS — 3,130 formulas")
print("=" * 100)

fungrim = json.load(open(DATA / "fungrim/data/fungrim_formulas.json", encoding="utf-8"))
print(f"  {len(fungrim)} formulas")
if fungrim:
    print(f"  Keys: {list(fungrim[0].keys())[:8]}")

# Symbol count: equations vs definitions
types = Counter(f.get("type", "unknown") for f in fungrim)
print(f"  Types: {dict(types.most_common(5))}")

sym_by_type = defaultdict(list)
for f in fungrim:
    t = f.get("type", "unknown")
    syms = f.get("symbols", f.get("variables", []))
    if isinstance(syms, list):
        sym_by_type[t].append(len(syms))

if len(sym_by_type) >= 2:
    all_vals = []
    all_labels = []
    for t, counts in sym_by_type.items():
        all_vals.extend(counts)
        all_labels.extend([t] * len(counts))
    eta, n, k = eta_sq(all_vals, all_labels)
    record("Fungrim-type-sym", "LAW" if eta >= 0.14 else "TENDENCY", eta,
           f"type->n_symbols n={n} k={k}")

# Module structure
modules = Counter(f.get("module", f.get("topic", "unknown")) for f in fungrim)
print(f"  Modules: {len(modules)} unique")
if len(modules) >= 2:
    mod_vals = [len(f.get("symbols", f.get("variables", []))) for f in fungrim if f.get("module") or f.get("topic")]
    mod_labels = [f.get("module", f.get("topic")) for f in fungrim if f.get("module") or f.get("topic")]
    if mod_vals:
        eta, n, k = eta_sq(mod_vals, mod_labels)
        record("Fungrim-mod-sym", "LAW" if eta >= 0.14 else "TENDENCY", eta,
               f"module->n_symbols n={n} k={k}")

# ============================================================
# NIST CONFIG ENRICHMENT (C1)
# ============================================================
print("\n" + "=" * 100)
print("C1: NIST spectral config enrichment (42,981 lines)")
print("=" * 100)

nist = json.load(open(DATA / "physics/data/nist_asd/nist_spectral_with_config.json", encoding="utf-8"))
print(f"  {len(nist)} spectral lines with config")
if nist:
    print(f"  Keys: {list(nist[0].keys())}")

    # eta^2: config -> wavelength
    configs = [r.get("configuration", r.get("conf", "")) for r in nist]
    wavelengths = []
    config_labels = []
    for r in nist:
        wl = r.get("wavelength", r.get("obs_wl"))
        conf = r.get("configuration", r.get("conf", ""))
        if wl and conf:
            try:
                wavelengths.append(float(wl))
                config_labels.append(conf)
            except:
                pass

    if len(wavelengths) > 100:
        eta, n, k = eta_sq(wavelengths, config_labels)
        v24, r24 = bv2.F24_variance_decomposition(wavelengths, config_labels)
        record("C1-config", v24, eta, f"config->wavelength n={n} k={k}")

        # Partial after element (Z)
        z_vals = []
        wl_clean = []
        conf_clean = []
        for r in nist:
            wl = r.get("wavelength", r.get("obs_wl"))
            conf = r.get("configuration", r.get("conf", ""))
            z = r.get("Z", r.get("atomic_number"))
            if wl and conf and z:
                try:
                    z_vals.append(float(z))
                    wl_clean.append(float(wl))
                    conf_clean.append(conf)
                except:
                    pass

        if len(z_vals) > 100:
            z_arr = np.array(z_vals)
            wl_arr = np.array(wl_clean)
            X = np.column_stack([np.ones(len(z_arr)), z_arr])
            beta = np.linalg.lstsq(X, wl_arr, rcond=None)[0]
            wl_resid = wl_arr - X @ beta
            eta_partial, n_p, k_p = eta_sq(wl_resid, conf_clean)
            record("C1-config|Z", "LAW" if eta_partial >= 0.14 else "TENDENCY", eta_partial,
                   f"config->wavelength|Z n={n_p} k={k_p}")
    else:
        record("C1", "SKIP", key_metric="Insufficient lines with config+wavelength")

# ============================================================
# MAASS FRICKE (with joined data)
# ============================================================
print("\n" + "=" * 100)
print("MAASS FRICKE — joined dataset")
print("=" * 100)

fricke_path = DATA / "maass/data/maass_with_fricke.json"
if fricke_path.exists():
    maass_f = json.load(open(fricke_path, encoding="utf-8"))
    has_fricke = [m for m in maass_f if m.get("fricke_eigenvalue") is not None]
    print(f"  Total forms: {len(maass_f)}")
    print(f"  With Fricke: {len(has_fricke)}")

    if len(has_fricke) > 50:
        # Fricke -> coefficient M4/M2^2
        fricke_plus = []
        fricke_minus = []
        for m in has_fricke:
            coeffs = m.get("coefficients", [])
            if len(coeffs) >= 50:
                arr = np.array(coeffs[:200], dtype=float)
                arr = arr[arr != 0]
                if len(arr) >= 10:
                    ratio = m4m2(np.abs(arr))
                    if np.isfinite(ratio):
                        if m["fricke_eigenvalue"] > 0:
                            fricke_plus.append(ratio)
                        else:
                            fricke_minus.append(ratio)

        if fricke_plus and fricke_minus:
            from scipy.stats import ttest_ind
            t, p = ttest_ind(fricke_plus, fricke_minus)
            vals = fricke_plus + fricke_minus
            labs = ["+1"]*len(fricke_plus) + ["-1"]*len(fricke_minus)
            eta, n, k = eta_sq(vals, labs)
            print(f"  Fricke +1: n={len(fricke_plus)}, mean M4/M2^2={np.mean(fricke_plus):.3f}")
            print(f"  Fricke -1: n={len(fricke_minus)}, mean M4/M2^2={np.mean(fricke_minus):.3f}")
            print(f"  t={t:.2f}, p={p:.4f}")
            record("Maass.fricke", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
                   f"fricke->coeff_shape p={p:.4f}")
        else:
            record("Maass.fricke", "SKIP", key_metric=f"+1:{len(fricke_plus)} -1:{len(fricke_minus)}")
else:
    record("Maass.fricke", "SKIP", key_metric="maass_with_fricke.json not found")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("M2 R3 UNBLOCKED TESTS — SUMMARY")
print("=" * 100)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:25s} | {r['cls']:20s} | {e:15s} | {r['metric'][:50]}")

print(f"\n  Total tests: {len(results)}")
print(f"  Results: {sum(1 for r in results if r['cls'] != 'SKIP')}")
print(f"  Skipped: {sum(1 for r in results if r['cls'] == 'SKIP')}")
