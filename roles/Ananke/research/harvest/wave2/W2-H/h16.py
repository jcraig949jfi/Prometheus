"""(2) H16 on real arrays: swap_rel sd_floor scale, mirror-pair structure, verdict sensitivity.
Inputs: workers/W-Z/out/pairs/*.npz (per (pair, trial) pair-mean x4, 255 = unscored; 256 pairs) and
workers/W-Z/out/row_table.csv. Output: out/h16.json. numpy only (prometheus.ananke.swap_rel imported unchanged)."""
import csv
import json
import math
import pathlib
import sys
import warnings

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from prometheus.ananke import swap_rel as sr  # noqa: E402

PAIRS = ROOT / "roles/Ananke/research/workers/W-Z/out/pairs"


def floors(P, K):
    return {"current_SEscale": sr.sd_floor(P, K),                 # sqrt(1/4K)/sqrt(P)*.5, applied to a per-pair SD
            "intended_SD_K": math.sqrt(1 / (4 * K)) * 0.5,        # plan text: binomial-scale floor for a pair stat of K trials
            "intended_SD_2K": math.sqrt(1 / (8 * K)) * 0.5}       # same with the 2K world-trials a mirror pair averages


def interval_floor(x, floor, level=0.99, C=None):
    """swap_rel.interval('H2') with an explicit per-pair-SD floor (identical code path otherwise)."""
    x = np.asarray(x, float)
    P = x.shape[-1]
    q = (1 - level) / 2
    C = sr.boot_counts(P) if C is None else C
    X = x.reshape(-1, P)
    m = X.mean(1)
    sd = X.std(1, ddof=1)
    bm = (X @ C.T) / P
    bm2 = ((X * X) @ C.T) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
    bsd = np.maximum(bsd, floor)
    d = bm - m[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / math.sqrt(P))
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.sort(np.where(np.isnan(t), 0.0, t), 1)
    tlo, thi = sr._qsorted(t, q), sr._qsorted(t, 1 - q)
    se = sd / math.sqrt(P)
    deg = sd <= 1e-12
    lo = np.where(deg, m, m - thi * se)
    hi = np.where(deg, m, m - tlo * se)
    return m.reshape(x.shape[:-1]), lo.reshape(x.shape[:-1]), hi.reshape(x.shape[:-1])


def cert_floor(a, s, floor, C=None):
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    _, loF, hiF = interval_floor(DF, floor, C=C)
    _, loN, hiN = interval_floor(DN, floor, C=C)
    v = "INDETERMINATE"
    if loF > 0 and hiN < 0:
        v = "CHANCE_REL"
    if loN > 0:
        v = "NO_EFFECT_REL"
    if hiF < 0:
        v = "FLIP_REL"
    return v


def load_arms():
    out = []
    for f in sorted(PAIRS.glob("*.npz")):
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
            K = int(round(both[ok].sum() / max(1, ok.sum())))       # scored trials per world (= per pair-trial row)
            out.append({"gid": f.stem, "arm": arm, "a": a[ok], "s": s[ok], "At": np.where(both, A, np.nan)[ok],
                        "St": np.where(both, S, np.nan)[ok], "K": K})
    return out


if __name__ == "__main__":
    arms = [x for x in load_arms() if len(x["a"]) >= 32]
    res = {"n_arms": len(arms)}
    Cc = {}
    rows = []
    for x in arms:
        a, s, K = x["a"], x["s"], x["K"]
        P = len(a)
        C = Cc.setdefault(P, sr.boot_counts(P))
        DF = (s - 0.5) + (a - 0.5) / 2
        DN = (s - 0.5) - (a - 0.5) / 2
        fl = floors(P, K)
        # resample SDs (the quantity the floor acts on)
        minbsd = []
        for X in (DF, DN):
            bm = (X @ C.T) / P
            bm2 = ((X * X) @ C.T) / P
            minbsd.append(float(np.sqrt(np.maximum(bm2 - bm * bm, 0) * P / (P - 1)).min()))
        # mirror structure in the normal arm: per pair-trial value 0/.25/.5/.75/1
        At = x["At"]
        p = np.nanmean(At)
        half = np.nanmean(At == 0.5)
        ties = np.nanmean((At == 0.25) | (At == 0.75))
        rho_conc = 1 - half / max(2 * p * (1 - p), 1e-9) if 0 < p < 1 else float("nan")
        var_obs = float(np.var(a, ddof=1))
        r = {"gid": x["gid"], "arm": x["arm"], "P": P, "K": K, "a_mean": float(a.mean()),
             "sd_DF": float(DF.std(ddof=1)), "sd_DN": float(DN.std(ddof=1)),
             "minbsd_DF": minbsd[0], "minbsd_DN": minbsd[1], **{f"floor_{k}": v for k, v in fl.items()},
             "half_frac": float(half), "tie_frac": float(ties), "rho_concordance": float(rho_conc),
             "var_a": var_obs, "var_model_K": float(p * (1 - p) / K), "var_model_2K": float(p * (1 - p) / (2 * K))}
        r["v_REL3"] = str(sr.certificate(a, s, K, method="BOOTT", C=C)["verdict"])
        r["v_H2"] = str(sr.certificate(a, s, K, method="H2", C=C)["verdict"])
        for k, f in fl.items():
            r[f"v_{k}"] = cert_floor(a, s, f, C=C)
        rows.append(r)
    res["rows"] = rows
    R = rows
    res["summary"] = {
        "H2_ne_REL3": sum(r["v_H2"] != r["v_REL3"] for r in R),
        "intendedK_ne_REL3": sum(r["v_intended_SD_K"] != r["v_REL3"] for r in R),
        "intended2K_ne_REL3": sum(r["v_intended_SD_2K"] != r["v_REL3"] for r in R),
        "floor_binds_current": sum(min(r["minbsd_DF"], r["minbsd_DN"]) < r["floor_current_SEscale"] for r in R),
        "floor_binds_intendedK": sum(min(r["minbsd_DF"], r["minbsd_DN"]) < r["floor_intended_SD_K"] for r in R),
        "min_ratio_minbsd_over_current_floor": float(min(min(r["minbsd_DF"], r["minbsd_DN"]) / r["floor_current_SEscale"] for r in R)),
        "median_sd_DF": float(np.median([r["sd_DF"] for r in R])),
        "min_sd_DF": float(min(r["sd_DF"] for r in R)),
        "median_var_ratio_obs_over_modelK": float(np.median([r["var_a"] / r["var_model_K"] for r in R if r["var_model_K"] > 0])),
        "median_rho_concordance": float(np.nanmedian([r["rho_concordance"] for r in R])),
        "q_rho_concordance": np.nanquantile([r["rho_concordance"] for r in R], [.1, .25, .5, .75, .9]).tolist(),
        "K_values": sorted({r["K"] for r in R}), "P_values": sorted({r["P"] for r in R}),
    }
    ch = [(r["gid"], r["arm"], r["v_REL3"], r["v_intended_SD_K"], r["v_intended_SD_2K"]) for r in R
          if r["v_intended_SD_K"] != r["v_REL3"] or r["v_intended_SD_2K"] != r["v_REL3"]]
    res["changes"] = ch
    json.dump(res, open(HERE / "out" / "h16.json", "w"), indent=1)
    print(json.dumps(res["summary"], indent=1))
    for c in ch:
        print(c)
