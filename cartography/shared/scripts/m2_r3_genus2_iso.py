#!/usr/bin/env python3
"""
M2 Round 3 — Genus-2/Isogeny/F27 checks batch (8 tests)
C78, C71-f24, isogeny-knot overlap, isogeny-MF, C09-f27, C86-f27, C05-f27, crossing-polytope
"""
import sys, os, json
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
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

results = []
def record(name, classification, eta2=None, key_metric=""):
    results.append({"name": name, "classification": classification, "eta2": eta2, "key_metric": key_metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:20s} | {classification:20s} | {e:15s} | {key_metric}")

# Load G2
print("Loading genus-2...")
g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
print(f"  {len(valid_g2)} curves\n")

# ============================================================
print("=" * 90)
print("C78: G2 root number vs conductor")
print("=" * 90)
rn_cond = [(c["root_number"], c["conductor"]) for c in valid_g2 if c.get("root_number") is not None]
if rn_cond:
    rn_labels = [str(r) for r, c in rn_cond]
    cond_vals = [c for r, c in rn_cond]
    eta, n, k = eta_sq(cond_vals, rn_labels)
    v24, r24 = bv2.F24_variance_decomposition(cond_vals, rn_labels)
    record("C78", v24, eta, f"root_number->conductor n={n}")
    # Log transform
    log_cond = [np.log(c) for c in cond_vals if c > 0]
    log_labels = [rn_labels[i] for i in range(len(cond_vals)) if cond_vals[i] > 0]
    eta_log, _, _ = eta_sq(log_cond, log_labels)
    print(f"  log(conductor): eta2={eta_log:.4f}")

# ============================================================
print("\nC71-f24: G2 adelic obstruction density")
# Check for adelic obstruction data
has_adelic = sum(1 for c in g2 if c.get("has_square_sha") is not None or c.get("analytic_rank") is not None)
print(f"  Curves with analytic rank data: {has_adelic}")
ar_curves = [c for c in valid_g2 if c.get("analytic_rank") is not None]
if len(ar_curves) > 30:
    eta, n, k = eta_sq(
        [c["analytic_rank"] for c in ar_curves],
        [c["st_group"] for c in ar_curves])
    record("C71-f24", "LAW" if eta >= 0.14 else "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE",
           eta, f"ST->analytic_rank n={n}")
else:
    record("C71-f24", "SKIP", key_metric="No analytic rank data")

# ============================================================
print("\nIsogeny-knot overlap (G.R5.iso): primes that are knot determinants")
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 1)
print(f"  Unique knot determinants: {len(knot_dets)}")

# Load isogeny primes
iso_dir = DATA / "isogenies/data/graphs"
iso_primes = set()
if iso_dir.exists():
    for d in iso_dir.iterdir():
        if d.is_dir():
            try: iso_primes.add(int(d.name))
            except: pass
print(f"  Isogeny primes: {len(iso_primes)}")

overlap = knot_dets & iso_primes
print(f"  Overlap (primes that are knot dets): {len(overlap)}")
if iso_primes and knot_dets:
    # For overlapping primes, load node counts and compare to non-overlap
    overlap_nodes = []
    nonoverlap_nodes = []
    for d in iso_dir.iterdir():
        if d.is_dir():
            md_file = d / f"{d.name}_metadata.json"
            if md_file.exists():
                try:
                    md = json.load(open(md_file))
                    p = md["prime"]
                    nodes = md["nodes"]
                    if p in overlap:
                        overlap_nodes.append(nodes)
                    else:
                        nonoverlap_nodes.append(nodes)
                except:
                    pass

    if overlap_nodes and nonoverlap_nodes:
        vals = overlap_nodes + nonoverlap_nodes
        labs = ["knot_det"] * len(overlap_nodes) + ["not_knot_det"] * len(nonoverlap_nodes)
        eta, n, k = eta_sq(vals, labs)
        record("R5.iso-knot", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
               f"n_overlap={len(overlap_nodes)} n_other={len(nonoverlap_nodes)}")

# ============================================================
print("\nCrossing: det in polytope_verts vs not (G.R5.cross)")
poly_path = DATA / "polytopes/data/polytopes.json"
if poly_path.exists():
    polytopes = json.load(open(poly_path, encoding="utf-8"))
    poly_verts = set()
    for p in polytopes:
        if isinstance(p, dict) and p.get("f_vector"):
            poly_verts.add(p["f_vector"][0] if p["f_vector"] else 0)
    print(f"  Unique polytope vertex counts: {len(poly_verts)}")
    in_poly = [k["crossing_number"] for k in knots if k.get("crossing_number") and k.get("determinant") and k["determinant"] in poly_verts]
    not_poly = [k["crossing_number"] for k in knots if k.get("crossing_number") and k.get("determinant") and k["determinant"] not in poly_verts]
    if in_poly and not_poly:
        vals = in_poly + not_poly
        labs = ["in_poly"] * len(in_poly) + ["not_poly"] * len(not_poly)
        eta, n, k = eta_sq(vals, labs)
        record("R5.cross-poly", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
               f"n_in={len(in_poly)} n_out={len(not_poly)}")
else:
    record("R5.cross-poly", "SKIP", key_metric="Polytope data not found")

# ============================================================
print("\nIsogeny nodes ~ MF count at level p (G.R6.iso, F24)")
import duckdb
ROOT = Path(__file__).resolve().parents[3]
try:
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    mf_counts = dict(con.execute("SELECT level, COUNT(*) FROM modular_forms GROUP BY level").fetchall())
    con.close()
except:
    mf_counts = {}

if mf_counts and iso_primes:
    iso_nodes_list = []
    mf_at_p = []
    for d in iso_dir.iterdir():
        if d.is_dir():
            md_file = d / f"{d.name}_metadata.json"
            if md_file.exists():
                try:
                    md = json.load(open(md_file))
                    p = md["prime"]
                    nodes = md["nodes"]
                    mf_c = mf_counts.get(p, 0)
                    if mf_c > 0:
                        iso_nodes_list.append(nodes)
                        mf_at_p.append(mf_c)
                except:
                    pass
    if len(iso_nodes_list) > 10:
        r = np.corrcoef(iso_nodes_list, mf_at_p)[0, 1]
        record("R6.iso-MF", "CONSTRAINT" if r**2 >= 0.01 else "NEGLIGIBLE",
               r**2, f"r={r:.4f} n={len(iso_nodes_list)}")

# ============================================================
print("\nF27 consequence checks on Round 2 LAWs")
for gvar, ovar, name in [
    ("moonshine_class", "coefficient_scale", "C09-f27"),
    ("isogeny_prime", "diameter", "C86-f27"),
    ("maass_level", "spectral_parameter", "C05-f27"),
]:
    v27, r27 = bv2.F27_consequence_check(gvar, ovar)
    record(name, v27, key_metric=str(r27.get("explanation", r27.get("partial_matches", "none")))[:60])

# ============================================================
print("\n" + "=" * 90)
print("M2 R3 GENUS-2/ISOGENY BATCH SUMMARY")
print("=" * 90)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:20s} | {r['classification']:20s} | {e:15s} | {r['key_metric'][:50]}")
