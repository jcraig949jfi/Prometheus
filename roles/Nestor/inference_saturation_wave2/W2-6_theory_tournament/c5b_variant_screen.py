"""W2-6 check C5b: finish C5's variant screen with adequate counts.

Reads c5_context_variation_supply.json (children recorded by C5; no new interactions). Screens with the frozen
COMPETENT and STATE_FREE screens (s3_common fast-exact versions of run_de.competent / run_fair.fair_assay):
  forward: ALL distinct variant children of state-dependent (SD) donors in arm R, and up to MAXZ in arm Z;
           parents flagged BORDERLINE if max(R1, R2) fair rate >= 0.3 (a new seed tag alone can flip the call);
  reverse: up to MAXSF distinct variant children of state-free (SF) donors per arm (loss of state-freedom per birth).
Output c5b_variant_screen.json.  python -B c5b_variant_screen.py
"""
import json
import math
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))
import s3_common as S  # noqa: E402

CELL = "ffa6"
MAXZ, MAXSF = 700, 250
t0 = time.process_time()
d = json.load(open(HERE / "c5_context_variation_supply.json"))
rows = json.load(open(FOR / "core_map.json"))["rows"]
rng = random.Random(5)


def collect(sf, arm):
    out = []
    for r in d["donors"]:
        if r["sf"] != sf:
            continue
        par = rows[r["idx"]]
        border = max(par["fair"]["R1"], par["fair"]["R2"]) >= 0.3
        for x in r["arms"][arm]["kids_hex"]:
            out.append((r["idx"], border, x))
    return out


res = {}
for lab, sf, arm, cap in (("SD_R", False, "R", 10 ** 6), ("SD_Z", False, "Z", MAXZ),
                          ("SF_R", True, "R", MAXSF), ("SF_Z", True, "Z", MAXSF)):
    kids = collect(sf, arm)
    if len(kids) > cap:
        kids = rng.sample(kids, cap)
    n = comp = free = free_nb = n_nb = 0
    hits = []
    for idx, border, x in kids:
        g = bytes.fromhex(x)
        c = S.competent(CELL, g, True)
        f = c and S.state_free(CELL, g, True)
        n += 1; comp += c; free += f
        if not border:
            n_nb += 1; free_nb += f
        if f != sf:
            hits.append([idx, border, x])
    res[lab] = {"screened": n, "competent": comp, "state_free": free,
                "state_free_nonborderline_parents": [free_nb, n_nb],
                "changed_state": hits[:40]}
    print(lab, n, comp, free, free_nb, n_nb, round(time.process_time() - t0, 1), flush=True)


def fisher(a, b, c, d_):
    n1, n2, k = a + b, c + d_, a + c
    lf = lambda n: math.lgamma(n + 1)
    lp = lambda x: lf(n1) - lf(x) - lf(n1 - x) + lf(n2) - lf(k - x) - lf(n2 - k + x) - (lf(n1 + n2) - lf(k) - lf(n1 + n2 - k))
    p0 = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(max(0, k - n2), min(k, n1) + 1) if lp(x) <= p0 + 1e-9))


a, n1 = res["SD_Z"]["state_free"], res["SD_Z"]["screened"]
c, n2 = res["SD_R"]["state_free"], res["SD_R"]["screened"]
res["forward_Z_vs_R_fisher_p"] = fisher(a, n1 - a, c, n2 - c)
# per-conversion forward rate = (variant share) x (state-free share among screened variants)
s = d["summary"]
for arm in ("Z", "R"):
    vs = 1 - s["SD_%s" % arm]["exact_copy_share"]
    res["forward_rate_per_conversion_" + arm] = round(vs * res["SD_" + arm]["state_free"] / res["SD_" + arm]["screened"], 4)
    res["conversions_per_SD_donor_per_partner_" + arm] = round(s["SD_%s" % arm]["conversions"] / (s["SD_%s" % arm]["donors"] * d["partners"]), 3)
    vs2 = 1 - s["SF_%s" % arm]["exact_copy_share"]
    res["reverse_loss_rate_per_conversion_" + arm] = round(vs2 * (1 - res["SF_" + arm]["state_free"] / res["SF_" + arm]["screened"]), 4)
res["cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "c5b_variant_screen.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if not isinstance(v, dict)}, indent=1))
for k in ("SD_Z", "SD_R", "SF_Z", "SF_R"):
    print(k, {kk: vv for kk, vv in res[k].items() if kk != "changed_state"})
