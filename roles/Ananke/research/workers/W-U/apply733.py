"""PLAN s7: re-apply REL3 to W-O's 733 verdicts from SAVED marginals (no pair arrays exist).
Bounding protocol over pair correlation rho in [-1,1] (41) x halfwidth multiplier {.9,1,1.1}; combos kept
only if the normal-approx PCT certificate reproduces the recorded certificate (`rel`).
Writes out/rel3_733.csv, out/apply733.json."""
import collections
import csv
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swap_rel3 as r3  # noqa: E402

TAB = r3.load_table()
METHOD = TAB["METHOD"]
P = 256
Z99 = 2.5758293035489
TQ = r3.t_ppf(0.995, P - 1) * math.sqrt(P / (P - 1))   # TINT/XPCT normal-approx multiplier on the plug-in SE
RHOS = np.linspace(-1, 1, 41)
MULTS = (0.9, 1.0, 1.1)
ORDER = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL", "INDETERMINATE", "NOT_ELIGIBLE")


def cert(dfm, dnm, seF, seN, k):
    loF, hiF, loN, hiN = dfm - k * seF, dfm + k * seF, dnm - k * seN, dnm + k * seN
    if hiF < 0:
        return "FLIP_REL"
    if loN > 0:
        return "NO_EFFECT_REL"
    if loF > 0 and hiN < 0:
        return "CHANCE_REL"
    return "INDETERMINATE"


rows = list(csv.DictReader(open(HERE.parent / "W-O" / "out" / "rerun_table.csv")))
rel2 = {r["vid"]: r for r in csv.DictReader(open(HERE.parent / "W-Q" / "out" / "rel2_table.csv"))}
assert len(rows) == 733
out = []
for r in rows:
    n = json.loads(r["n512"])
    s = json.loads(r["s512"])
    K = int(r["K"])
    dz = TAB["designs"][f"P{P}_K{K}"]
    sa, ss = (n[2] - n[1]) / (2 * Z99), (s[2] - s[1]) / (2 * Z99)
    dfm, dnm = (s[0] - .5) + (n[0] - .5) / 2, (s[0] - .5) - (n[0] - .5) / 2
    kept, labs, strs, certs = 0, set(), set(), set()
    zcls = set()
    for rho in RHOS:
        for mu in MULTS:
            seF = mu * math.sqrt(max(ss * ss + sa * sa / 4 + rho * ss * sa, 0))
            seN = mu * math.sqrt(max(ss * ss + sa * sa / 4 - rho * ss * sa, 0))
            g = n[0] - 0.5
            if g > 0:   # z class over ALL rho (not only the kept ones), PLAN s6/s7
                z = (s[0] - 0.5) / g
                sez = mu * math.sqrt(max(ss * ss - 2 * z * rho * ss * sa + z * z * sa * sa, 0)) / g
                zcls.add(r3.z_class(z - TQ * sez, z + TQ * sez))
            if cert(dfm, dnm, seF, seN, Z99) != r["rel"]:
                continue
            kept += 1
            c = cert(dfm, dnm, seF, seN, TQ)
            nlo = n[0] - TQ * mu * sa
            lab = r3.label(c, nlo, P, K, dz=dz)
            certs.add(c)
            labs.add(lab["label"])
            strs.add(lab["strict"])
    status = "INCONSISTENT" if kept == 0 else ("DETERMINED" if len(labs) == 1 else "AMBIGUOUS")
    q = rel2[r["vid"]]
    y = {k: r[k] for k in ("vid", "source", "specimen", "family", "arm", "timing", "offset", "single", "rel", "K", "z")}
    y.update(rel2=q["rel2"], rel2_strict=q["rel2_strict"], kept=kept, status=status,
             cert3="|".join(sorted(certs)), rel3="|".join(sorted(labs)), rel3_strict="|".join(sorted(strs)),
             zclass="|".join(sorted(zcls)), n_lo=n[1])
    out.append(y)
with open(HERE / "out" / "rel3_733.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)


def tab(key_a, key_b, sub=None):
    sub = out if sub is None else sub
    c = collections.Counter((x[key_a], x[key_b]) for x in sub)
    return {a: {b: n for (aa, b), n in sorted(c.items()) if aa == a} for a in sorted({x[key_a] for x in sub})}


S = {"method": METHOD, "status": dict(collections.Counter(x["status"] for x in out)),
     "rel2_x_rel3": tab("rel2", "rel3"), "strict2_x_strict3": tab("rel2_strict", "rel3_strict"),
     "rel3_marginal": dict(collections.Counter(x["rel3"] for x in out)),
     "rel3_strict_marginal": dict(collections.Counter(x["rel3_strict"] for x in out))}
fl = [x for x in out if x["rel3"] == "FLIP_REL"]
S["flip_zclass"] = dict(collections.Counter(x["zclass"] for x in fl))
S["flip_zclass_by_family"] = tab("family", "zclass", fl)
grp = collections.defaultdict(set)
for x in out:
    grp[(x["specimen"], x["source"], x["offset"])].add(x["rel3"])
S["n_groups"] = len(grp)
S["groups_with_verdict"] = {v: sum(v in g for g in grp.values()) for v in ORDER}
fgrp = collections.defaultdict(list)
for x in fl:
    fgrp[(x["specimen"], x["source"], x["offset"])].append(x)
S["flip_groups"] = len(fgrp)
S["flip_groups_by_zclass"] = dict(collections.Counter("|".join(sorted({y["zclass"] for y in v})) for v in fgrp.values()))
S["flip_specimens"] = len({x["specimen"] for x in fl})
ch = [x for x in out if x["single"] == "CHANCE"]
S["absCHANCE_x_rel3"] = dict(collections.Counter(x["rel3"] for x in ch))
S["absCHANCE_flip_groups"] = len({(x["specimen"], x["source"], x["offset"]) for x in ch if x["rel3"] == "FLIP_REL"})
S["changed_rows"] = [(x["vid"], x["specimen"][:8], x["arm"], x["offset"], x["rel2"], x["rel3"], x["status"])
                     for x in out if x["rel3"] != x["rel2"]]
json.dump(S, open(HERE / "out" / "apply733.json", "w"), indent=1)
for k, v in S.items():
    print(k, json.dumps(v))
