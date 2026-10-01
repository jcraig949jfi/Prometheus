"""(2b) False-certificate rate of REL3 / H2 / floor variants at the REL boundary truths, with the REAL mirror-pair
structure: the population of pairs is a real W-Z normal arm (per (pair, trial) mirror means), and the swap arm is
built per pair-trial by the W-Q 'realistic' mechanism (complement of normal w.p. t, copy w.p. u, else a fresh
mirror pair of two independent fair coins), so the population truth is EXACTLY on the boundary:
z = -1/2 (FLIP boundary: t = .5, u = 0) and z = +1/2 (NO_EFFECT boundary: t = 0, u = .5).
Samples P pairs with replacement from the 256 real pairs. Output out/fc_mirror.json. numpy only."""
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[5]))
import h16  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
PS = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else (32, 64, 256)
SKIP = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] != "-" else set()
TAG = sys.argv[4] if len(sys.argv) > 4 else ""


def verdict_floor(a, s, floor, C, method):
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    if method == "REL3":
        _, loF, hiF = sr.interval(DF, method="BOOTT", C=C)
        _, loN, hiN = sr.interval(DN, method="BOOTT", C=C)
    elif method == "T":
        from scipy import stats as st
        P = DF.shape[-1]
        q = st.t.ppf(0.995, P - 1)
        def ti(X):
            m = X.mean(-1); se = X.std(-1, ddof=1) / math.sqrt(P)
            return m, m - q * se, m + q * se
        _, loF, hiF = ti(DF)
        _, loN, hiN = ti(DN)
    else:
        _, loF, hiF = h16.interval_floor(DF, floor, C=C)
        _, loN, hiN = h16.interval_floor(DN, floor, C=C)
    return hiF < 0, loN > 0


if __name__ == "__main__":
    arms = [x for x in h16.load_arms() if len(x["a"]) >= 256]
    # selection: spread over normal accuracy and over per-pair SD (incl. the most degenerate arms)
    am = np.array([x["a"].mean() for x in arms])
    sd = np.array([((x["s"] - .5) + (x["a"] - .5) / 2).std(ddof=1) for x in arms])
    pick = set()
    for q in np.linspace(0.05, 0.95, 8):
        pick.add(int(np.argmin(np.abs(am - np.quantile(am, q)))))
    pick |= set(np.argsort(sd)[:6].tolist())
    pick |= set(np.argsort(-am)[:3].tolist())
    rng = np.random.default_rng(20261001)
    out = []
    for i in sorted(pick):
        x = arms[i]
        if f"{x['gid'][:8]}:{x['arm']}" in SKIP:
            continue
        At = x["At"]
        K = x["K"]
        for P in PS:
            C = sr.boot_counts(P)
            res = {"gid": x["gid"], "arm": x["arm"], "P": P, "K": K, "a_mean": float(am[i]), "sd_DF_obs": float(sd[i])}
            meths = {"REL3": None, "H2": sr.sd_floor(P, K), "floorK": math.sqrt(1 / (4 * K)) * .5,
                     "floor2K": math.sqrt(1 / (8 * K)) * .5, "T": None}
            cnt = {m: [0, 0] for m in meths}
            for zi, (t, u) in enumerate(((0.5, 0.0), (0.0, 0.5))):
                done = 0
                while done < N:
                    n = min(500, N - done)
                    idx = rng.integers(0, At.shape[0], size=(n, P))
                    A = At[idx]                                        # [n, P, ntr]
                    r = rng.random(A.shape)
                    fresh = (rng.integers(0, 2, A.shape) + rng.integers(0, 2, A.shape)) / 2
                    S = np.where(r < t, 1 - A, np.where(r < t + u, A, fresh))
                    S = np.where(np.isnan(A), np.nan, S)
                    a = np.nanmean(A, -1)
                    s = np.nanmean(S, -1)
                    for m, f in meths.items():
                        fl, ne = verdict_floor(a, s, f, C, m)
                        cnt[m][zi] += int(fl.sum() if zi == 0 else ne.sum())
                    done += n
            res["FC_FLIP"] = {m: c[0] / N for m, c in cnt.items()}
            res["FC_NOEFF"] = {m: c[1] / N for m, c in cnt.items()}
            out.append(res)
            print(x["gid"][:8], x["arm"], P, round(am[i], 3), round(sd[i], 3),
                  {m: (res["FC_FLIP"][m], res["FC_NOEFF"][m]) for m in meths}, flush=True)
    json.dump({"N": N, "rows": out}, open(HERE / "out" / f"fc_mirror{TAG}.json", "w"), indent=1)
