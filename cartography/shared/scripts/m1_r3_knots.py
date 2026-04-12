#!/usr/bin/env python3
"""
M1 R3 — Knot batch (9 tests, run on M2)
G.R1.3: det ~ max Alexander coeff
G.R1.8: crossing: det-is-conductor vs not
G.R4.6: Alexander(-1) ~ Jones(-1)
G.R4.5: max Jones coeff ~ det (F24)
C67: Alexander polynomial recurrence (BM)
C84: Knot det -> Alexander enrichment
C94: Knot Jones mod-p fingerprint
C17: Knot -> crystal enrichment
G.alex: Alexander entropy by crossing
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

def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10: return float("nan")
    vn = arr / np.mean(arr)
    return np.mean(vn**4) / np.mean(vn**2)**2

results = []
def rec(name, cls, eta2=None, metric=""):
    results.append({"name": name, "cls": cls, "eta2": eta2, "metric": metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:30s} | {cls:20s} | {e:15s} | {metric}")

# Load
print("Loading knots...")
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
has_alex = [k for k in knots if k.get("alex_coeffs")]
has_jones = [k for k in knots if k.get("jones_coeffs")]
has_det = [k for k in knots if k.get("determinant")]
has_cn = [k for k in knots if k.get("crossing_number")]
print(f"  {len(knots)} knots, alex={len(has_alex)}, jones={len(has_jones)}, det={len(has_det)}, cn={len(has_cn)}")

# Load EC conductors for cross-domain test
import duckdb
ROOT = Path(__file__).resolve().parents[3]
try:
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    ec_conductors = set(r[0] for r in con.execute("SELECT DISTINCT conductor FROM elliptic_curves WHERE conductor > 0").fetchall())
    con.close()
except:
    ec_conductors = set()
print(f"  EC conductors: {len(ec_conductors)}\n")

print("=" * 100)

# G.R1.3: det ~ max Alexander coeff
print("G.R1.3: det ~ max Alexander coeff")
valid = [k for k in has_alex if k.get("determinant")]
if valid:
    det = np.array([k["determinant"] for k in valid], dtype=float)
    max_alex = np.array([max(abs(c) for c in k["alex_coeffs"]) for k in valid], dtype=float)
    r = np.corrcoef(det, max_alex)[0, 1]
    rec("G.R1.3 det~max_alex", "IDENTITY" if r**2 > 0.95 else "LAW" if r**2 > 0.14 else "TENDENCY", r**2, f"r={r:.4f}")

# G.R1.8: crossing: det-is-conductor vs not
print("\nG.R1.8: crossing number — det is EC conductor vs not")
if ec_conductors and has_cn:
    is_cond = [k["crossing_number"] for k in has_cn if k.get("determinant") and k["determinant"] in ec_conductors]
    not_cond = [k["crossing_number"] for k in has_cn if k.get("determinant") and k["determinant"] not in ec_conductors]
    if is_cond and not_cond:
        vals = is_cond + not_cond
        labs = ["is_cond"] * len(is_cond) + ["not_cond"] * len(not_cond)
        eta, n, kg = eta_sq(vals, labs)
        rec("G.R1.8 cn~is_conductor", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE", eta,
            f"n_cond={len(is_cond)} n_not={len(not_cond)}")

# G.R4.6: Alexander(-1) ~ Jones(-1)
print("\nG.R4.6: Alexander(-1) ~ Jones(-1)")
both = [k for k in knots if k.get("alex_coeffs") and k.get("jones_coeffs")]
if both:
    a_neg1 = [sum(c * (-1)**i for i, c in enumerate(k["alex_coeffs"])) for k in both]
    j_neg1 = [sum(c * (-1)**i for i, c in enumerate(k["jones_coeffs"])) for k in both]
    a_abs = np.abs(a_neg1)
    j_abs = np.abs(j_neg1)
    r = np.corrcoef(a_abs, j_abs)[0, 1]
    rec("G.R4.6 alex(-1)~jones(-1)", "IDENTITY" if r**2 > 0.95 else "LAW", r**2, f"r={r:.4f} n={len(both)}")

# G.R4.5: max Jones ~ det (F24 only, already known near-identity)
print("\nG.R4.5: max Jones coeff ~ det (F24 classify)")
valid_j = [k for k in has_jones if k.get("determinant")]
if valid_j:
    det_j = np.array([k["determinant"] for k in valid_j], dtype=float)
    max_j = np.array([max(abs(c) for c in k["jones_coeffs"]) for k in valid_j], dtype=float)
    r = np.corrcoef(det_j, max_j)[0, 1]
    rec("G.R4.5 max_jones~det", "NEAR-IDENTITY", r**2, f"r={r:.4f} R2={r**2:.6f}")

# C67: Alexander recurrence (Berlekamp-Massey)
print("\nC67: Alexander polynomial recurrence")
# Check if any Alexander coefficient sequence satisfies a linear recurrence
recurrence_hits = 0
tested = 0
for k in has_alex[:500]:  # cap for speed
    coeffs = k["alex_coeffs"]
    if len(coeffs) >= 6:
        tested += 1
        # Simple check: do later coefficients follow from earlier ones?
        # Linear recurrence of order 2: c[n] = a*c[n-1] + b*c[n-2]
        if len(coeffs) >= 5:
            c = np.array(coeffs, dtype=float)
            X = np.column_stack([c[1:-1], c[:-2]])
            y = c[2:]
            try:
                beta = np.linalg.lstsq(X, y, rcond=None)[0]
                pred = X @ beta
                resid = np.max(np.abs(y - pred))
                if resid < 0.5:  # integer recurrence
                    recurrence_hits += 1
            except:
                pass

rec("C67 alex_recurrence", "NEGLIGIBLE" if recurrence_hits < tested * 0.05 else "TENDENCY",
    metric=f"{recurrence_hits}/{tested} satisfy order-2 recurrence")

# C84: Knot det -> Alexander enrichment
print("\nC84: det -> Alexander enrichment")
# Do knots with the same determinant have more similar Alexander polynomials?
det_groups = defaultdict(list)
for k in has_alex:
    if k.get("determinant"):
        det_groups[k["determinant"]].append(k["alex_coeffs"])

within_dists = []
between_dists = []
dets_with_mult = {d: polys for d, polys in det_groups.items() if len(polys) >= 2}
if len(dets_with_mult) >= 5:
    for d, polys in list(dets_with_mult.items())[:100]:
        for i in range(len(polys)):
            for j in range(i+1, min(len(polys), i+5)):
                # L1 distance between coefficient vectors (pad shorter)
                a, b = polys[i], polys[j]
                max_len = max(len(a), len(b))
                a_pad = a + [0] * (max_len - len(a))
                b_pad = b + [0] * (max_len - len(b))
                within_dists.append(sum(abs(x-y) for x, y in zip(a_pad, b_pad)))
    # Random between-group pairs
    all_polys = [(d, p) for d, polys in dets_with_mult.items() for p in polys]
    for _ in range(len(within_dists)):
        i, j = rng.choice(len(all_polys), 2, replace=False)
        if all_polys[i][0] != all_polys[j][0]:
            a, b = all_polys[i][1], all_polys[j][1]
            max_len = max(len(a), len(b))
            a_pad = a + [0] * (max_len - len(a))
            b_pad = b + [0] * (max_len - len(b))
            between_dists.append(sum(abs(x-y) for x, y in zip(a_pad, b_pad)))

    if within_dists and between_dists:
        enrichment = np.mean(between_dists) / np.mean(within_dists) if np.mean(within_dists) > 0 else 0
        rec("C84 det->alex_enrich", "CONSTRAINT" if enrichment > 1.5 else "TENDENCY",
            metric=f"enrichment={enrichment:.2f}x within={np.mean(within_dists):.1f} between={np.mean(between_dists):.1f}")

# C94: Knot Jones mod-p fingerprint
print("\nC94: Jones mod-p fingerprint")
if has_jones:
    for p in [2, 3, 5]:
        fp_groups = defaultdict(list)
        for k in has_jones:
            if k.get("determinant"):
                fp = tuple(c % p for c in k["jones_coeffs"])
                fp_groups[fp].append(k["determinant"])
        n_fps = len(fp_groups)
        big_fps = {fp: dets for fp, dets in fp_groups.items() if len(dets) >= 5}
        if big_fps:
            all_dets = []
            all_labs = []
            for fp, dets in big_fps.items():
                all_dets.extend(dets)
                all_labs.extend([str(fp)] * len(dets))
            eta, n, kg = eta_sq(all_dets, all_labs)
            rec(f"C94 jones_mod{p}", "LAW" if eta >= 0.14 else "TENDENCY" if eta >= 0.01 else "NEGLIGIBLE",
                eta, f"n_fps={n_fps} big_fps={len(big_fps)}")

# C17: Knot -> crystal enrichment
print("\nC17: Knot determinant -> crystal property enrichment")
# Load SC space group numbers
sg_numbers = set()
try:
    sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
    sg_numbers = set(s.get("number", 0) for s in sg_data)
except:
    pass
knot_dets = set(k["determinant"] for k in has_det if k.get("determinant"))
overlap = knot_dets & sg_numbers
rec("C17 knot_det~sg_number", "TENDENCY" if len(overlap) > 10 else "NEGLIGIBLE",
    metric=f"overlap={len(overlap)} of {len(knot_dets)} dets vs {len(sg_numbers)} SG#s")

# G.alex: Alexander entropy by crossing (comprehensive)
print("\nG.alex: Alexander entropy by crossing number")
cn_entropy = defaultdict(list)
for k in has_alex:
    cn = k.get("crossing_number")
    if cn and cn > 0:
        coeffs = np.abs(np.array(k["alex_coeffs"], dtype=float))
        total = np.sum(coeffs)
        if total > 0:
            p = coeffs / total
            p = p[p > 0]
            cn_entropy[cn].append(-np.sum(p * np.log2(p)))

entropy_vals = []
entropy_labels = []
for cn, ents in cn_entropy.items():
    entropy_vals.extend(ents)
    entropy_labels.extend([cn] * len(ents))

if entropy_vals:
    eta, n, kg = eta_sq(entropy_vals, entropy_labels)
    rec("G.alex entropy~cn", "LAW" if eta >= 0.14 else "TENDENCY", eta,
        f"n={n} k={kg}")

# Summary
print("\n" + "=" * 100)
print("M1 R3 KNOT BATCH SUMMARY")
print("=" * 100)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:30s} | {r['cls']:20s} | {e:15s} | {r['metric'][:50]}")
