"""W2-N: AUDIT3 disagreement prediction with the first draw's observed STATUS PATTERN conditioned on.

Model (per W-Z group, joint over all its arms, so the shared normal run = clustering is exact):
  first draw D1 means ~ N(W-Z means, k * Sigma / P), k = 2 f^2  (flat-prior predictive with SE inflation f;
  k = 1 is the plug-in "W-Z is the truth" model).
Labels of D1:
  L_boott : certificate with BOOTT-equivalent asymmetric multipliers measured on the W-Z arm itself
            (what an exact REL3 label on D1 would be; pure noise, no estimator difference);
  L_wu    : apply733's marginal-bounding pipeline (status DET/AMBIG/INCONS + REL3 label), the actual W-U path.
Scenarios (expected number of disagreements with the OBSERVED W-Z label, over the 301 rows / 110 groups that
were W-U DETERMINED):
  A  noise only          : L_boott, no conditioning
  B  + estimator         : L_wu label at true rho/mu=1 (= normal TQ), no conditioning
  C  + row selection     : L_wu, conditional on that row being DETERMINED in D1
  D  + group selection   : L_wu, conditional on the group's full observed status pattern (each covered row's
                           DET/AMBIG status in D1 equals what W-U observed) -- the AMBIG-priority groups were
                           chosen BECAUSE their first draw sat near a threshold.
Output out/sim.json."""
from __future__ import annotations

import collections
import csv
import json
import math
import sys

import numpy as np

import n_decomp as N

sys.path.insert(0, str(N.WK / "W-U"))
import swap_rel3 as r3  # noqa: E402  (pure numpy; BOOTT interval)


def boott_mult(x):
    """BOOTT 99% interval of x as (k_lo, k_hi) multiples of se = sd/sqrt(P)."""
    m, lo, hi = r3.interval(x, "BOOTT")
    se = x.std(ddof=1) / math.sqrt(len(x))
    if se <= 0:
        return N.TQ, N.TQ
    return float((m - lo) / se), float((hi - m) / se)


def run(ks=(1.0, 2.0, 3.125, 4.5, 8.0), nsim=20000, seed=5, min_hits=200):
    rows = list(csv.DictReader(open(N.WK / "W-Z" / "out" / "row_table.csv")))
    arms = N.load_arms()
    rows_by_gid = collections.defaultdict(list)
    for r in rows:
        rows_by_gid[r["gid"]].append(r)
    prio = {r["gid"]: r["priority"] for r in csv.DictReader(open(N.WK / "W-Z" / "out" / "group_table.csv"))}
    rng = np.random.default_rng(seed)
    res = {}
    for k in ks:
        acc = collections.defaultdict(float)
        lowhit = 0
        grp_detail = []
        for g, rs in rows_by_gid.items():
            al = sorted({r["arm"] for r in rs})
            ok = np.logical_and.reduce([arms[(g, a)]["ok"] for a in al])
            A = arms[(g, al[0])]["a"][ok]
            X = np.vstack([A[None]] + [arms[(g, a)]["s"][ok][None] for a in al])
            Pg = X.shape[1]
            mu0 = X.mean(1)
            C = np.cov(X) / Pg
            sa = math.sqrt(C[0, 0])
            ka_lo, _ = boott_mult(A)
            L = np.linalg.cholesky(k * C + 1e-14 * np.eye(len(mu0)))
            D = mu0[None] + rng.standard_normal((nsim, len(mu0))) @ L.T
            arm_out = {}
            for j, a in enumerate(al):
                s = X[1 + j]
                ss = math.sqrt(C[1 + j, 1 + j])
                cov = C[0, 1 + j]
                seF = math.sqrt(max(ss * ss + sa * sa / 4 + cov, 0))
                seN = math.sqrt(max(ss * ss + sa * sa / 4 - cov, 0))
                DFv, DNv = (s - .5) + (A - .5) / 2, (s - .5) - (A - .5) / 2
                kFl, kFh = boott_mult(DFv)
                kNl, kNh = boott_mult(DNv)
                ma, ms = D[:, 0], D[:, 1 + j]
                dfm, dnm = (ms - .5) + (ma - .5) / 2, (ms - .5) - (ma - .5) / 2
                K = arms[(g, a)]["K"]
                # exact-like (BOOTT multipliers) label
                loF, hiF, loN, hiN = dfm - kFl * seF, dfm + kFh * seF, dnm - kNl * seN, dnm + kNh * seN
                c = np.full(nsim, 3, np.int8)
                c = np.where((loF > 0) & (hiN < 0), 2, c)
                c = np.where(loN > 0, 1, c)
                c = np.where(hiF < 0, 0, c)
                L_b = N.label_v(c, ma - ka_lo * sa, K)
                rel = N.cert_v(dfm, dnm, seF, seN, N.Z99)
                st, L_w = N.wu_pipeline(ma, ms, sa, ss, rel, K)
                L_t = N.label_v(N.cert_v(dfm, dnm, seF, seN, N.TQ), ma - N.TQ * sa, K)
                arm_out[a] = (L_b, L_t, st, L_w)
            obs_st = np.ones(nsim, bool)
            for r in rs:
                want = 0 if r["WU_status"] == "DETERMINED" else 1
                obs_st &= arm_out[r["arm"]][2] == want
            hits = int(obs_st.sum())
            if hits < min_hits:
                lowhit += 1
            det_rows = [r for r in rs if r["WU_status"] == "DETERMINED"]
            if not det_rows:
                continue
            anyA = np.zeros(nsim, bool)
            anyB = np.zeros(nsim, bool)
            anyC = np.zeros(nsim, bool)
            allC = np.ones(nsim, bool)
            for r in det_rows:
                L_b, L_t, st, L_w = arm_out[r["arm"]]
                obs = N.CODE[r["new"]]
                d = st == 0
                acc["A_rows"] += (L_b != obs).mean()
                acc["B_rows"] += (L_t != obs).mean()
                acc["C_rows"] += ((L_w != obs) & d).mean() / max(d.mean(), 1e-12)
                acc["D_rows"] += ((L_w != obs) & obs_st).sum() / max(hits, 1)
                anyA |= L_b != obs
                anyB |= L_t != obs
                anyC |= (L_w != obs) & d
                allC &= d
            pA, pB = anyA.mean(), anyB.mean()
            pC = (anyC & allC).sum() / max(allC.sum(), 1)
            pD = (anyC & obs_st).sum() / max(hits, 1)
            acc["A_groups"] += pA
            acc["B_groups"] += pB
            acc["C_groups"] += pC
            acc["D_groups"] += pD
            acc["D_groups_var"] += pD * (1 - pD)
            acc[f"D_groups_{prio[g]}"] += pD
            acc[f"A_groups_{prio[g]}"] += pA
            grp_detail.append({"gid": g, "prio": prio[g], "hits": hits, "pA": round(float(pA), 4),
                               "pB": round(float(pB), 4), "pC": round(float(pC), 4), "pD": round(float(pD), 4)})
        acc["groups_low_hits"] = lowhit
        res[f"k={k}"] = {"f": round(math.sqrt(k / 2), 3), **{a: round(float(b), 3) for a, b in acc.items()},
                         "groups": grp_detail}
        print(f"k={k} f={math.sqrt(k / 2):.3f}", {a: round(float(b), 2) for a, b in acc.items()}, flush=True)
    json.dump(res, open(N.OUT / "sim.json", "w"), indent=1)
    return res


if __name__ == "__main__":
    run()
