"""W2-AC: C1 headline counts re-derived at the correct independence units.

CPU only, numpy only, no engine runs. Run from anywhere:
    python roles/Ananke/research/harvest/wave2/W2-AC/ac_c1_units.py
Writes out/c1_units.json and prints a summary.

Units:
  row        = one evolve search (its own search seed; held worlds keyed by that seed)
  condition  = sha1(physics, env): identical physics x task (B reps, D replicates share it)
  physics    = sha1(physics)
  lineage    = root A1 cell reached by following `parent` (B->A, B2->B, C->A/B, D->B/B2/C, E->B)
SIGNAL = held lo99 > .55 (PREREG s7), re-implemented here; no report.py import.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import math
import os
import pathlib

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
FAMS = ("RELAY", "MAJ", "HOLD", "XOR", "FLIP")
SIG_LO, COMM_LO = 0.55, 0.03
BOOTT_FLIPS = {"884a64df866756b0", "8ccf6c723ec57b3d"}            # W2-H F3
T_FLIPS = {"884a64df866756b0", "925caa3a48964717", "0f5451c3b3cdf250"}
RNG = np.random.default_rng(0xAC)
NBOOT = 20000

R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
BYID = {r["cell_id"]: r for r in R}
EV = [r for r in R if r["kind"] == "evolve"]


def h(o):
    return hashlib.sha1(json.dumps(o, sort_keys=True).encode()).hexdigest()[:10]


def cond(r):
    return h([r["physics"], r["env"]])


def phys(r):
    return h(r["physics"])


def root(r):
    seen = 0
    while r["wave"] != "A":
        r = BYID[r["parent"]]
        seen += 1
        assert seen < 10
    return r["cell_id"]


def sig(r, drop=()):
    return r["result"]["held"]["lo99"] > SIG_LO and r["cell_id"] not in drop


def cdep(r):
    return sig(r) and r["result"]["held"]["comm_delta_lo99"] > COMM_LO


def fam(r):
    return r["env"]["family"]


def hops(r):
    """Same rule as W2-G rederive_c1.hops: ring/torus ceil(d/r); smallworld/random d (BFS); global 1."""
    p, d = r["physics"], r["env"]["d"]
    t = p["topology"]
    if t == "global":
        return 1
    if t in ("ring", "torus"):
        return math.ceil(d / p["radius"])
    return d


# ------------------------------------------------------------------ statistics
def wilson(k, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(max(0, c - w), 4), round(min(1, c + w), 4))


def _betainc_inv(a, b, q):
    # bisection on the regularized incomplete beta via continued fraction (no scipy dependency)
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if _ibeta(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _cf(a, b, x) / a
    return 1 - math.exp(lbt) * _cf(b, a, 1 - x) / b


def _cf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    hh = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e-300
        hh *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e-300
        de = d * c
        hh *= de
        if abs(de - 1) < 1e-12:
            break
    return hh


def clopper(k, n, conf=0.95):
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else _betainc_inv(k, n - k + 1, a)
    hi = 1.0 if k == n else _betainc_inv(k + 1, n - k, 1 - a)
    return (round(lo, 4), round(hi, 4))


def cp_upper_one_sided(k, n, conf):
    return round(1.0 if k == n else _betainc_inv(k + 1, n - k, conf), 4)


def icc_anova(groups):
    """groups: list of 0/1 lists. ANOVA ICC for binary data (Fleiss)."""
    groups = [g for g in groups if len(g)]
    k = len(groups)
    N = sum(len(g) for g in groups)
    if k < 2 or N == k:
        return None
    p = sum(sum(g) for g in groups) / N
    msb = sum(len(g) * (np.mean(g) - p) ** 2 for g in groups) / (k - 1)
    msw = sum(len(g) * np.mean(g) * (1 - np.mean(g)) for g in groups) / (N - k)
    m0 = (N - sum(len(g) ** 2 for g in groups) / N) / (k - 1)
    den = msb + (m0 - 1) * msw
    return None if den == 0 else float((msb - msw) / den)


def deff(groups, icc):
    N = sum(len(g) for g in groups)
    mw = sum(len(g) ** 2 for g in groups) / N
    return 1 + (mw - 1) * max(icc or 0.0, 0.0), mw


def cluster_boot(groups, conf=0.95):
    k = np.array([sum(g) for g in groups], float)
    n = np.array([len(g) for g in groups], float)
    idx = RNG.integers(len(groups), size=(NBOOT, len(groups)))
    est = k[idx].sum(1) / n[idx].sum(1)
    a = (1 - conf) / 2
    p = k.sum() / n.sum()
    vb = p * (1 - p) / n.sum()
    de = float(est.var() / vb) if vb > 0 else None
    return (round(float(np.quantile(est, a)), 4), round(float(np.quantile(est, 1 - a)), 4),
            {"deff_boot": None if de is None else round(de, 2), "n_eff_boot": None if not de else round(n.sum() / de, 1)})


def unit_block(rows, key_fns, pred):
    out = {"rows": len(rows), "k_rows": sum(pred(r) for r in rows)}
    out["p_rows"] = round(out["k_rows"] / max(1, len(rows)), 4)
    out["wilson95_rows_naive"] = wilson(out["k_rows"], len(rows))
    for name, fn in key_fns.items():
        g = collections.defaultdict(list)
        for r in rows:
            g[fn(r)].append(int(pred(r)))
        groups = list(g.values())
        icc = icc_anova(groups)
        de, mw = deff(groups, icc)
        out[name] = {
            "n_units": len(groups),
            "units_with_any": sum(1 for x in groups if any(x)),
            "icc": None if icc is None else round(icc, 3),
            "m_weighted": round(mw, 2),
            "deff": round(de, 2),
            "n_eff": round(len(rows) / de, 1),
            "cluster_boot95_pooled_ratio": cluster_boot(groups) if len(groups) > 1 else None,
        }
    return out


KEYS = {"condition": cond, "physics": phys, "lineage": root}
res = {}

# ---------------------------------------------- (1) L3 pooled ratios, per family
res["L3"] = {}
for f in FAMS:
    rows = [r for r in EV if fam(r) == f]
    blk = unit_block(rows, KEYS, sig)
    blk["by_wave"] = {w: [sum(sig(r) for r in rows if r["wave"] == w), sum(1 for r in rows if r["wave"] == w)]
                      for w in ("A", "B", "B2", "C", "D", "E")}
    sig_rows = [r for r in rows if sig(r)]
    blk["signal_rows_by_lineage"] = collections.Counter(root(r)[:8] for r in sig_rows).most_common()
    blk["signal_rows_distinct_conditions"] = len({cond(r) for r in sig_rows})
    blk["signal_rows_distinct_physics"] = len({phys(r) for r in sig_rows})
    blk["signal_rows_distinct_lineages"] = len({root(r) for r in sig_rows})
    res["L3"][f] = blk

# ---------------------------------------------- (2) A1 rates (the only unselected frame)
A1 = [r for r in EV if r["wave"] == "A"]
assert len({phys(r) for r in A1}) == len(A1) == 352
assert len({r["search_seed"] for r in A1}) == 352
res["A1"] = {}
for f in FAMS:
    rows = [r for r in A1 if fam(r) == f]
    d = {}
    for frame in ("uniform", "from_living_A0", "all"):
        rr = rows if frame == "all" else [r for r in rows if frame in r["extra"]]
        k = sum(sig(r) for r in rr)
        d[frame] = {"k": k, "n": len(rr), "p": round(k / len(rr), 4), "wilson95": wilson(k, len(rr)),
                    "cp95": clopper(k, len(rr))}
    kb = sum(sig(r, BOOTT_FLIPS) for r in rows)
    kt = sum(sig(r, T_FLIPS) for r in rows)
    d["boott_k"], d["t_k"] = kb, kt
    d["boott_cp95"] = clopper(kb, len(rows))
    res["A1"][f] = d

# A1 COMM_DEPENDENT (P4: <= 5%)
k8 = sum(cdep(r) for r in A1)
by = collections.Counter(fam(r) for r in A1 if cdep(r))
res["P4"] = {"k": k8, "n": 352, "by_family": dict(by), "p": round(k8 / 352, 4),
             "cp95": clopper(k8, 352), "cp_upper95_one_sided": cp_upper_one_sided(k8, 352, .95),
             "cp_upper99_one_sided": cp_upper_one_sided(k8, 352, .99),
             "boott_k": sum(cdep(r) and r["cell_id"] not in BOOTT_FLIPS for r in A1),
             "comm_family_only": {"k": sum(cdep(r) for r in A1 if fam(r) in ("RELAY", "MAJ", "XOR", "FLIP")),
                                  "n": sum(1 for r in A1 if fam(r) in ("RELAY", "MAJ", "XOR", "FLIP"))},
             "alias_check_SIGNAL_eq_CDEP_in_RELAY_MAJ_XOR": all(sig(r) == cdep(r) for r in EV
                                                                if fam(r) in ("RELAY", "MAJ", "XOR"))}
kc = res["P4"]["comm_family_only"]
kc["cp95"] = clopper(kc["k"], kc["n"])
# pooled all-wave COMM_DEPENDENT per family
res["CDEP_pooled"] = {f: [sum(cdep(r) for r in EV if fam(r) == f), sum(sig(r) for r in EV if fam(r) == f)]
                      for f in FAMS}

# ---------------------------------------------- (3) replicate concordance: is SIGNAL a property of the condition?
conc = {}
for f in ("RELAY", "MAJ", "HOLD"):
    g = collections.defaultdict(list)
    for r in EV:
        if fam(r) == f:
            g[cond(r)].append(int(sig(r)))
    multi = [v for v in g.values() if len(v) >= 2]
    # pairwise concordance among searches at the same condition
    pp = pn = nn = 0
    for v in multi:
        s = sum(v); n = len(v)
        pp += s * (s - 1) / 2; nn += (n - s) * (n - s - 1) / 2; pn += s * (n - s)
    tot = pp + pn + nn
    p_given = pp * 2 / max(1, 2 * pp + pn)          # P(another search SIGNAL | one SIGNAL)
    conc[f] = {"conditions_with_reps": len(multi), "searches": sum(len(v) for v in multi),
               "pairs_SS": pp, "pairs_SN": pn, "pairs_NN": nn,
               "P_second_SIGNAL_given_first": round(p_given, 3),
               "icc_condition_reps_only": None if not multi else round(icc_anova(multi), 3)}
res["replicate_concordance"] = conc

# D wave specifically: source vs fresh replicates
dsum = []
for r in EV:
    if r["wave"] == "D":
        src = BYID[r["extra"]["replicates"]]
        dsum.append((fam(r), src["cell_id"][:8], round(src["result"]["held"]["acc"], 3),
                     round(r["result"]["held"]["acc"], 3), sig(src), sig(r)))
res["D_replicates"] = {"rows": dsum, "source_SIGNAL": sum(x[4] for x in dsum[::2]),
                       "replicates_SIGNAL": sum(x[5] for x in dsum), "n_rep": len(dsum)}

# ---------------------------------------------- (4) one-hop
rel_sig = [r for r in EV if fam(r) == "RELAY" and sig(r)]
oh = [hops(r) == 1 for r in rel_sig]
byc = collections.defaultdict(list)
byl = collections.defaultdict(list)
for r in rel_sig:
    byc[cond(r)].append(hops(r) == 1)
    byl[root(r)].append(hops(r) == 1)
res["one_hop"] = {
    "rows": [sum(oh), len(oh)],
    "conditions": [sum(all(v) for v in byc.values()), len(byc)],
    "lineages_all_one_hop": [sum(all(v) for v in byl.values()), len(byl)],
    "lineage_sizes": sorted((len(v) for v in byl.values()), reverse=True),
    "multi_hop_rows": [(r["cell_id"][:8], r["wave"], r["physics"]["topology"], r["env"]["d"],
                        r["physics"]["radius"], round(r["result"]["held"]["lo99"], 3)) for r in rel_sig if hops(r) != 1],
}
# A1 frame: one-hop vs multi-hop tasks
a1r = [r for r in A1 if fam(r) == "RELAY"]
one = [r for r in a1r if hops(r) == 1]
multi = [r for r in a1r if hops(r) != 1]
k1, n1, k2, n2 = sum(sig(r) for r in one), len(one), sum(sig(r) for r in multi), len(multi)


def newcombe(k1, n1, k2, n2):
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    p1, p2 = k1 / n1, k2 / n2
    d = p1 - p2
    return (round(d, 4), round(d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), 4),
            round(d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2), 4))


def fisher_two_sided(k1, n1, k2, n2):
    K, N = k1 + k2, n1 + n2
    def hp(x):
        return math.comb(n1, x) * math.comb(n2, K - x) / math.comb(N, K)
    p0 = hp(k1)
    return round(sum(hp(x) for x in range(max(0, K - n2), min(K, n1) + 1) if hp(x) <= p0 * (1 + 1e-9)), 4)


res["one_hop"]["A1_by_topology"] = {t: [sum(sig(r) for r in a1r if r["physics"]["topology"] == t and hops(r) == 1),
                                         sum(1 for r in a1r if r["physics"]["topology"] == t and hops(r) == 1),
                                         sum(sig(r) for r in a1r if r["physics"]["topology"] == t and hops(r) != 1),
                                         sum(1 for r in a1r if r["physics"]["topology"] == t and hops(r) != 1)]
                                     for t in ("ring", "torus", "global", "smallworld", "random")}
rt = [r for r in a1r if r["physics"]["topology"] in ("ring", "torus", "global")]
k1r, n1r = sum(sig(r) for r in rt if hops(r) == 1), sum(1 for r in rt if hops(r) == 1)
k2r, n2r = sum(sig(r) for r in rt if hops(r) != 1), sum(1 for r in rt if hops(r) != 1)
res["one_hop"]["A1_lattice_global_only"] = {"one": [k1r, n1r], "multi": [k2r, n2r],
                                            "fisher_p": fisher_two_sided(k1r, n1r, k2r, n2r)}
res["one_hop"]["A1"] = {"one_hop": [k1, n1, wilson(k1, n1)], "multi_hop": [k2, n2, wilson(k2, n2)],
                        "diff_newcombe95": newcombe(k1, n1, k2, n2), "fisher_p": fisher_two_sided(k1, n1, k2, n2),
                        "topologies_multi": collections.Counter(r["physics"]["topology"] for r in multi),
                        "A1_signal_hops": [(r["cell_id"][:8], r["physics"]["topology"], hops(r)) for r in a1r if sig(r)]}
# MAJ: hops not defined by d (E-W2: MAJ "d" is not distance); report rows only
# ---------------------------------------------- (5) HOLD composition
hold_sig = [r for r in EV if fam(r) == "HOLD" and sig(r)]
lott = [r for r in hold_sig if r["physics"]["setrule"] == 0 and r["physics"]["rules"] > 1]
latch = [r for r in hold_sig if r["result"]["held"]["acc"] >= 0.999]
res["HOLD_composition"] = {
    "signal": len(hold_sig),
    "setrule0_rules_gt1 (lottery-eligible)": len(lott),
    "held_acc_1.000": len(latch),
    "comm_delta_lo99_gt_.03": sum(cdep(r) for r in hold_sig),
    "distinct_conditions": len({cond(r) for r in hold_sig}),
    "distinct_lineages": len({root(r) for r in hold_sig}),
    "C_wave_HOLD_rows (env variants HOLD never reads)": sum(1 for r in EV if fam(r) == "HOLD" and r["wave"] == "C"),
}

# ---------------------------------------------- (6) design-effect sensitivity: SIGNAL rows per unit at A1 vs pooled
json.dump(res, open(OUT / "c1_units.json", "w"), indent=1, default=str)

# ---------------------------------------------- print
for f in ("RELAY", "MAJ", "HOLD"):
    b = res["L3"][f]
    print(f"\n== {f} pooled {b['k_rows']}/{b['rows']} by wave {b['by_wave']}")
    print(f"   SIGNAL rows: distinct cond {b['signal_rows_distinct_conditions']}, physics {b['signal_rows_distinct_physics']},"
          f" lineages {b['signal_rows_distinct_lineages']}; top lineages {b['signal_rows_by_lineage'][:4]}")
    for u in KEYS:
        print("  ", u, b[u])
print("\nA1:", json.dumps(res["A1"], default=str))
print("\nP4:", json.dumps(res["P4"], default=str))
print("\nCDEP pooled:", res["CDEP_pooled"])
print("\nreplicate concordance:", json.dumps(res["replicate_concordance"]))
print("\nD:", res["D_replicates"]["source_SIGNAL"], res["D_replicates"]["replicates_SIGNAL"], res["D_replicates"]["n_rep"])
for x in res["D_replicates"]["rows"]:
    print("  ", x)
print("\none-hop:", json.dumps(res["one_hop"], default=str))
print("\nHOLD:", json.dumps(res["HOLD_composition"]))
