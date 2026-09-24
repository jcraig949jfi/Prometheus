"""D-series Round 2 (PREREG_D2): confirmation grids for the six Round-1
nominations in a RANDOM and a COMPETENT background.
python -m ensorain.d1.round2 <run|score>"""
import json
import sys

import numpy as np

from .analyze import interaction_test, pattern, bins, col, load, CONT, LOGD
from .core import sample_dials, run

R1 = "ensorain/runs/d1_round1.jsonl"
OUT = "ensorain/runs/d1_round2.jsonl"
NOMS = [("N1", "world_family", "org_family", "r2c"), ("N2", "lam", "org_family", "r2c"),
        ("N3", "forget", "org_family", "r2c"), ("N4", "scratch", "surprise_alpha", "r2c"),
        ("N5", "sweeps", "kappa_mult", "EFF"), ("N6", "cap_actual", "org_family", "EFF")]
DIAL_KEY = {"cap_actual": "cap"}  # the dial that sets cap_actual
LEVELS_CAT = {"world_family": ["CP", "MAT", "NONE", "TT"], "org_family": ["CP", "LR", "TT"]}
COMPETENT = dict(lam=30.0, sweeps=10, scratch=128, cap=192, replay_frac=0.0, dream_ratio=0.0, surprise_alpha=0.0,
                 disturb=0.0, forget=0.0, err_frac=0.0, persist=5, p_restruct=0.0, drift=0.3, noise=0.1,
                 kappa_mult=1.0, org_family="TT", start="correct", world_family="TT")
N_CELL = {"RANDOM": 40, "COMPETENT": 16}


def levels(k, r1rows):
    """Continuous: Round-1 tercile midpoints (quantiles 1/6, 1/2, 5/6 of the
    sampled values, in dial units). Categorical: every level."""
    if k in LEVELS_CAT:
        return LEVELS_CAT[k]
    x = np.array([float(r[k]) for r in r1rows])
    q = np.quantile(x, [1 / 6, 1 / 2, 5 / 6])
    if k in ("sweeps", "scratch", "cap_actual"):
        return [int(round(v)) for v in q]
    return [float(v) for v in q]


def jobs():
    r1 = load(R1)
    out, life = [], 0
    rng = np.random.default_rng(924_002)
    for nid, ki, kj, ruler in NOMS:
        li, lj = levels(ki, r1), levels(kj, r1)
        for bg in ("RANDOM", "COMPETENT"):
            for a, vi in enumerate(li):
                for b, vj in enumerate(lj):
                    for rep in range(N_CELL[bg]):
                        d = sample_dials(rng) if bg == "RANDOM" else dict(COMPETENT)
                        d[DIAL_KEY.get(ki, ki)] = vi
                        d[DIAL_KEY.get(kj, kj)] = vj
                        out.append(dict(life=life, inst=70000 + life, seed=500000 + life, dials=d,
                                        nom=nid, bg=bg, cell=[a, b]))
                        life += 1
    return out


def score():
    r1 = load(R1)
    rows = [json.loads(l) for l in open(OUT)]
    ok = [r for r in rows if r.get("status") == "OK"]
    for r in ok:
        r["r2c"] = float(np.clip(r["r2_ho"], -1, 1))
    rep = dict(n=len(rows), n_ok=len(ok))
    alpha = 0.05 / 6
    for nid, ki, kj, ruler in NOMS:
        y1 = np.array([r[ruler] if ruler != "r2c" else r["r2c"] for r in r1], float)
        bi, na = bins(col(r1, ki), ki)
        bj, nb = bins(col(r1, kj), kj)
        P1, M1 = pattern(bi, na, bj, nb, y1)
        res = {}
        for bg in ("RANDOM", "COMPETENT"):
            v = [r for r in ok if r["nom"] == nid and r["bg"] == bg]
            ci = np.array([r["cell"][0] for r in v])
            cj = np.array([r["cell"][1] for r in v])
            y = np.array([r[ruler] for r in v], float)
            F, p = interaction_test(ci, na, cj, nb, y)
            P2, M2 = pattern(ci, na, cj, nb, y)
            m = ~np.isnan(P1) & ~np.isnan(P2)
            r_pat = float(np.corrcoef(P1[m], P2[m])[0, 1]) if m.sum() >= 3 else float("nan")
            res[bg] = dict(n=len(v), F=round(F, 2), p=p, pattern_r=round(r_pat, 3),
                           cell_means=np.round(M2, 3).tolist(),
                           replicated=bool(p < alpha and r_pat > 0.5))
        res["round1_cell_means"] = np.round(M1, 3).tolist()
        res["REPLICATED"] = res["RANDOM"]["replicated"]
        rep[nid] = dict(pair=[ki, kj], ruler=ruler, **res)
    rep["instrument_controls_pass"] = bool(rep["N1"]["RANDOM"]["replicated"] and rep["N5"]["RANDOM"]["replicated"])
    json.dump(rep, open("ensorain/runs/d1_round2_score.json", "w"), indent=1)
    for nid, *_ in NOMS:
        x = rep[nid]
        print(nid, x["pair"], x["ruler"], "| RANDOM F", x["RANDOM"]["F"], "p", f'{x["RANDOM"]["p"]:.1e}', "r", x["RANDOM"]["pattern_r"],
              "REP" if x["RANDOM"]["replicated"] else "--", "| COMPETENT F", x["COMPETENT"]["F"], "p", f'{x["COMPETENT"]["p"]:.1e}',
              "r", x["COMPETENT"]["pattern_r"], "YES" if x["COMPETENT"]["replicated"] else "--")
    print("instrument controls pass:", rep["instrument_controls_pass"])


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(jobs(), OUT)
    else:
        score()
