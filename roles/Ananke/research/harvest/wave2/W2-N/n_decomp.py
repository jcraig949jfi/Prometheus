"""W2-N: decomposition of the AUDIT3 (W-Z vs W-U) between-namespace disagreement excess.

Pure numpy (no torch, no engine). Reads only:
  workers/W-Z/out/{row_table.csv, pairs/*.npz}   (second draw, namespace 0x680, exact pair arrays)
  workers/W-U/out/{rel3_733.csv, rel3_table.json} (first-draw labels, from W-O marginals)
  workers/W-O/out/rerun_table.csv                 (first draw, namespace 0x600, saved marginals only)

Parts
  D  measurement dedupe: arms of a group whose (a, s) pair arrays are identical or mirrored (s1 + s2 == 1)
     are ONE measurement (mirror => FLIP<->NO_EFFECT, CHANCE<->CHANCE exactly under BOOTT).
  E0 estimator check: W-U's marginal-bounding pipeline (apply733 semantics) applied to W-Z's OWN data
     (marginals = assays.pair_ci of W-Z pairs, rel = W-N PCT rule on W-Z pairs) vs the exact H2 label.
     Any disagreement here is pure estimator difference (same data).
  S  selection-aware predictive simulation, jointly per group (shared normal run = clustering, exactly):
     first draw D1 ~ N(W-Z means, k * Sigma_pairs / P), k = 2 (predictive) or 1 (plug-in);
     D1 is labelled through the full W-U pipeline (REL2 PCT cert -> rho/mu bounding -> status, REL3 label).
     Counterfactual columns: (i) no selection + exact label  (ii) selection + exact label  (iii) selection +
     W-U label (realistic). Expected counts are conditional on the row being DETERMINED in the simulated
     first draw, summed over the rows that were actually DETERMINED (the comparison AUDIT3 made).
Outputs out/decomp.json (+ printed tables)."""
from __future__ import annotations

import collections
import csv
import json
import math
import pathlib
import warnings

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
WK = HERE.parents[2] / "workers"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
Z99 = 2.5758293035489
CERTS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
TAB = json.loads((WK / "W-U" / "out" / "rel3_table.json").read_text())


def t_ppf995(df):
    from scipy import stats
    return float(stats.t.ppf(0.995, df))


P = 256
TQ = t_ppf995(P - 1) * math.sqrt(P / (P - 1))   # apply733's BOOTT normal-approx multiplier
RHOS = np.linspace(-1, 1, 41)
MULTS = np.array([0.9, 1.0, 1.1])


# ------------------------------------------------------------------ data
def load_arms():
    out = {}
    for f in sorted((WK / "W-Z" / "out" / "pairs").glob("*.npz")):
        z = np.load(f)
        arms = sorted({k.split("__", 1)[1] for k in z.files if "__" in k})
        for arm in arms:
            A = z[f"a__{arm}"].astype(float)
            S = z[f"s__{arm}"].astype(float)
            A[A == 255] = np.nan
            S[S == 255] = np.nan
            A /= 4
            S /= 4
            both = ~np.isnan(A) & ~np.isnan(S)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                a = np.nanmean(np.where(both, A, np.nan), 1)
                s = np.nanmean(np.where(both, S, np.nan), 1)
            ok = ~np.isnan(a) & ~np.isnan(s)
            K = int(round(both[ok].sum() / max(1, ok.sum())))
            out[(f.stem, arm)] = {"a": a, "s": s, "ok": ok, "K": K, "At": A, "St": S}
    return out


def pair_ci(v, level=0.99, n_boot=2000, seed=0):      # == assays.pair_ci (copied, numpy only)
    g = np.random.default_rng(seed)
    n = v.shape[-1]
    idx = g.integers(0, n, size=(n_boot, n))
    bs = v[..., idx].mean(-1)
    return v.mean(-1), np.quantile(bs, (1 - level) / 2, axis=-1), np.quantile(bs, 1 - (1 - level) / 2, axis=-1)


def wn_rule(a, s):                                     # == W-N swap_rel.rule (PCT, B=2000 seed 0)
    idx = np.random.default_rng(0).integers(0, len(a), size=(2000, len(a)))
    DF = (s - .5) + (a - .5) / 2
    DN = (s - .5) - (a - .5) / 2

    def ci(v):
        bs = v[idx].mean(-1)
        return v.mean(), np.quantile(bs, .005), np.quantile(bs, .995)
    _, loF, hiF = ci(DF)
    _, loN, hiN = ci(DN)
    if hiF < 0:
        return "FLIP_REL"
    if loN > 0:
        return "NO_EFFECT_REL"
    if loF > 0 and hiN < 0:
        return "CHANCE_REL"
    return "INDETERMINATE"


# ------------------------------------------------------------------ vectorised W-U pipeline
def cert_v(dfm, dnm, seF, seN, k):
    """broadcast arrays -> int code 0 FLIP, 1 NO_EFFECT, 2 CHANCE, 3 INDET (apply733.cert precedence)."""
    loF, hiF, loN, hiN = dfm - k * seF, dfm + k * seF, dnm - k * seN, dnm + k * seN
    c = np.full(np.broadcast(dfm, seF).shape, 3, np.int8)
    c = np.where((loF > 0) & (hiN < 0), 2, c)
    c = np.where(loN > 0, 1, c)
    c = np.where(hiF < 0, 0, c)
    return c


def label_v(c, nlo, K):
    """REL3 label code (0 F, 1 N, 2 C, 3 INDET, 4 NOT_ELIGIBLE) at P=256 (P >= floor; cert_ok from table)."""
    dz = TAB["designs"][f"P{P}_K{K}"]
    cok = np.array([bool(dz["cert_ok"][v]) for v in CERTS])
    pm = np.array([dz["p_min"][v] for v in CERTS])
    ident = nlo > 0.5
    attain_any = ident & np.any(cok[None] & (nlo[..., None] >= pm), axis=-1) if np.ndim(nlo) else \
        ident and bool(np.any(cok & (nlo >= pm)))
    lab = np.where(c < 3, np.where(cok[np.minimum(c, 2)], c, 4), np.where(attain_any, 3, 4))
    return np.where(ident, lab, 4).astype(np.int8)


NAMES = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL", "INDETERMINATE", "NOT_ELIGIBLE")
CODE = {n: i for i, n in enumerate(NAMES)}


def wu_pipeline(ma, ms, sa, ss, rel, K):
    """apply733 semantics, vectorised over leading axis of ma/ms/rel (rel = REL2 cert code of the draw).
    Returns status code (0 DET, 1 AMBIG, 2 INCONSISTENT) and label code (DET only; else -1)."""
    ma = np.asarray(ma, float)[..., None, None]
    ms = np.asarray(ms, float)[..., None, None]
    rel = np.asarray(rel)[..., None, None]
    rho = RHOS[:, None]
    mu = MULTS[None, :]
    seF = mu * np.sqrt(np.maximum(ss * ss + sa * sa / 4 + rho * ss * sa, 0))
    seN = mu * np.sqrt(np.maximum(ss * ss + sa * sa / 4 - rho * ss * sa, 0))
    dfm = (ms - .5) + (ma - .5) / 2
    dnm = (ms - .5) - (ma - .5) / 2
    keep = cert_v(dfm, dnm, seF, seN, Z99) == rel
    c = cert_v(dfm, dnm, seF, seN, TQ)
    nlo = np.broadcast_to(ma - TQ * mu * sa, c.shape)
    lab = label_v(c, nlo, K)
    big = 9
    lmin = np.where(keep, lab, big).reshape(lab.shape[:-2] + (-1,)).min(-1)
    lmax = np.where(keep, lab, -1).reshape(lab.shape[:-2] + (-1,)).max(-1)
    anyk = keep.reshape(keep.shape[:-2] + (-1,)).any(-1)
    status = np.where(~anyk, 2, np.where(lmin == lmax, 0, 1))
    return status, np.where(status == 0, lmin, -1)


# ------------------------------------------------------------------ main
def main(nsim=4000, seed=11):
    rows = list(csv.DictReader(open(WK / "W-Z" / "out" / "row_table.csv")))
    wu = {r["vid"]: r for r in csv.DictReader(open(WK / "W-U" / "out" / "rel3_733.csv"))}
    wo = {r["vid"]: r for r in csv.DictReader(open(WK / "W-O" / "out" / "rerun_table.csv"))}
    arms = load_arms()
    res = {}

    # ---- sanity: vectorised W-U pipeline reproduces rel3_733 on W-O marginals (all 733)
    mism = 0
    for v, r in wu.items():
        o = wo[v]
        n, s = json.loads(o["n512"]), json.loads(o["s512"])
        sa, ss = (n[2] - n[1]) / (2 * Z99), (s[2] - s[1]) / (2 * Z99)
        st, lb = wu_pipeline(n[0], s[0], sa, ss, CODE[o["rel"]], int(o["K"]))
        got = ("DETERMINED", "AMBIGUOUS", "INCONSISTENT")[int(st)]
        want = r["status"]
        if got != want or (got == "DETERMINED" and NAMES[int(lb)] != r["rel3"]):
            mism += 1
    res["sanity_vectorised_wu_vs_rel3_733_mismatches"] = mism
    print("sanity: vectorised W-U pipeline vs rel3_733 mismatches:", mism, "/ 733")

    # ---- D: measurement dedupe inside each group
    bygid = collections.defaultdict(list)
    for (g, a) in arms:
        bygid[g].append(a)
    meas = {}
    mirror_of = {}
    for g, al in bygid.items():
        al = sorted(al)
        rep = {}
        for a in al:
            x = arms[(g, a)]
            found = None
            for b, (rb, sign) in rep.items():
                y = arms[(g, b)]
                if rb != b:
                    continue
                if not np.array_equal(x["ok"], y["ok"]) or not np.allclose(x["a"][x["ok"]], y["a"][y["ok"]]):
                    continue
                if np.allclose(x["s"][x["ok"]], y["s"][y["ok"]]):
                    found = (b, +1)
                    break
                if np.allclose(x["s"][x["ok"]], 1 - y["s"][y["ok"]]):
                    found = (b, -1)
                    break
            rep[a] = (a, +1) if found is None else found
        for a, (b, sign) in rep.items():
            meas[(g, a)] = f"{g}:{b}"
            mirror_of[(g, a)] = sign
    det = [r for r in rows if r["WU_status"] == "DETERMINED"]
    dis = [r for r in det if r["new"] != r["WU_rel3"]]
    m_det = {meas[(r["gid"], r["arm"])] for r in det}
    m_dis = {meas[(r["gid"], r["arm"])] for r in dis}
    g_det = {r["gid"] for r in det}
    g_dis = {r["gid"] for r in dis}
    # a measurement "disagrees" if any of its DETERMINED rows disagree; check rows of one measurement agree
    incoh = 0
    for m in m_det:
        rs = [r for r in det if meas[(r["gid"], r["arm"])] == m]
        if len({r["new"] != r["WU_rel3"] for r in rs}) > 1:
            incoh += 1
    res["dedupe"] = {"rows_det": len(det), "rows_dis": len(dis), "measurements_det": len(m_det),
                     "measurements_dis": len(m_dis), "groups_det": len(g_det), "groups_dis": len(g_dis),
                     "measurements_with_mixed_row_outcomes": incoh,
                     "mirror_classes": sum(1 for k, v in mirror_of.items() if v == -1)}
    print("dedupe:", res["dedupe"])

    # ---- E0: W-U pipeline on W-Z's own data vs exact H2 label (same data)
    e0 = collections.Counter()
    e0_rows = []
    for r in rows:
        x = arms[(r["gid"], r["arm"])]
        a, s = x["a"][x["ok"]], x["s"][x["ok"]]
        n = pair_ci(a)
        sv = pair_ci(s)
        sa, ss = (n[2] - n[1]) / (2 * Z99), (sv[2] - sv[1]) / (2 * Z99)
        rel = wn_rule(a, s)
        st, lb = wu_pipeline(n[0], sv[0], sa, ss, CODE[rel], x["K"])
        st = ("DETERMINED", "AMBIGUOUS", "INCONSISTENT")[int(st)]
        lab = NAMES[int(lb)] if st == "DETERMINED" else ""
        e0[(st, lab == r["new"]) if st == "DETERMINED" else (st, None)] += 1
        if st == "DETERMINED" and lab != r["new"]:
            e0_rows.append((r["gid"], r["arm"], lab, r["new"]))
    res["E0_wu_pipeline_on_WZ_data"] = {str(k): v for k, v in e0.items()}
    res["E0_mismatch_rows"] = e0_rows
    print("E0 (W-U pipeline on W-Z data vs exact):", dict(e0), "mismatches:", e0_rows[:10])

    # ---- S: selection-aware predictive simulation, joint per group
    rng = np.random.default_rng(seed)
    rows_by_gid = collections.defaultdict(list)
    for r in rows:
        rows_by_gid[r["gid"]].append(r)
    acc = {k: collections.defaultdict(float) for k in ("k2", "k1")}
    per_row = []
    for g, rs in rows_by_gid.items():
        al = sorted({r["arm"] for r in rs})
        ok = np.logical_and.reduce([arms[(g, a)]["ok"] for a in al])
        A = arms[(g, al[0])]["a"][ok]
        Ss = np.stack([arms[(g, a)]["s"][ok] for a in al])
        X = np.vstack([A[None], Ss])                       # [1+k, P]
        Pg = X.shape[1]
        mu0 = X.mean(1)
        C = np.cov(X) / Pg
        sa = math.sqrt(C[0, 0])
        for kname, kk in (("k2", 2.0), ("k1", 1.0)):
            L = np.linalg.cholesky(kk * C + 1e-14 * np.eye(len(mu0)))
            D = mu0[None] + rng.standard_normal((nsim, len(mu0))) @ L.T     # first-draw means
            out_arm = {}
            for j, a in enumerate(al):
                ss = math.sqrt(C[1 + j, 1 + j])
                cov = C[0, 1 + j]
                seF_t = math.sqrt(max(ss * ss + sa * sa / 4 + cov, 0))
                seN_t = math.sqrt(max(ss * ss + sa * sa / 4 - cov, 0))
                ma, ms = D[:, 0], D[:, 1 + j]
                dfm, dnm = (ms - .5) + (ma - .5) / 2, (ms - .5) - (ma - .5) / 2
                rel = cert_v(dfm, dnm, seF_t, seN_t, Z99)                     # REL2 cert of the draw
                K = arms[(g, a)]["K"]
                st, lb = wu_pipeline(ma, ms, sa, ss, rel, K)
                exact = label_v(cert_v(dfm, dnm, seF_t, seN_t, TQ), ma - TQ * sa, K)
                out_arm[a] = (st, lb, exact)
            # rows
            sim_any_dis_sel = np.zeros(nsim, bool)
            sim_any_dis_exact = np.zeros(nsim, bool)
            sim_all_det = np.ones(nsim, bool)
            obs_row_det = []
            for r in rs:
                if r["WU_status"] != "DETERMINED":
                    continue
                st, lb, exact = out_arm[r["arm"]]
                obs = CODE[r["new"]]
                d = st == 0
                pdet = d.mean()
                p_sel_wu = ((lb != obs) & d).mean() / max(pdet, 1e-12)
                p_sel_ex = ((exact != obs) & d).mean() / max(pdet, 1e-12)
                p_nosel = (exact != obs).mean()
                acc[kname]["rows_noselect_exact"] += p_nosel
                acc[kname]["rows_select_exact"] += p_sel_ex
                acc[kname]["rows_select_WU"] += p_sel_wu
                sim_any_dis_sel |= (lb != obs) & d
                sim_any_dis_exact |= (exact != obs)
                sim_all_det &= d
                obs_row_det.append(r)
                if kname == "k2":
                    per_row.append({"gid": g, "arm": r["arm"], "obs_WZ": r["new"], "WU": r["WU_rel3"],
                                    "dis": r["new"] != r["WU_rel3"], "p_det": round(float(pdet), 4),
                                    "p_noselect_exact": round(float(p_nosel), 4),
                                    "p_select_exact": round(float(p_sel_ex), 4),
                                    "p_select_WU": round(float(p_sel_wu), 4)})
            # ambiguity calibration: P(row ambiguous) over all covered rows of the group
            for r in rs:
                st, _, _ = out_arm[r["arm"]]
                acc[kname]["ambig_expected"] += (st == 1).mean()
                acc[kname]["ambig_observed"] += r["WU_status"] == "AMBIGUOUS"
            if obs_row_det:
                # group-level: P(any DETERMINED row of the group disagrees | those rows determined)
                pdet_g = sim_all_det.mean()
                acc[kname]["groups_noselect_exact"] += sim_any_dis_exact.mean()
                acc[kname]["groups_select_WU"] += (sim_any_dis_sel & sim_all_det).mean() / max(pdet_g, 1e-12) \
                    if pdet_g > 0.02 else sim_any_dis_sel.mean()
                acc[kname]["groups_n"] += 1
    res["S"] = {k: dict(v) for k, v in acc.items()}
    for k, v in acc.items():
        print(k, {a: round(b, 2) for a, b in v.items()})
    # distance bands for the k2 model
    res["S_rows_k2"] = per_row
    json.dump(res, open(OUT / "decomp.json", "w"), indent=1, default=str)
    return res


if __name__ == "__main__":
    main()
