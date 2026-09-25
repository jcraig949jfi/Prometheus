"""D-series Round 4 (PREREG_D3 s "Round 4", fixed before Round 3): a
fresh-seed grid for every Round-3 nomination except the planted control.
Background = Round-3 range midpoints (geometric for log dials); for the
categorical dial `start`, the background is BALANCED (half the lives
each), because a categorical has no midpoint. Committed before any
Round-4 row. python -m ensorain.d1.round4 <run|score>"""
import json
import sys

import numpy as np

from .analyze import interaction_test, pattern, bins, col, load, configure
from .core import run

R3 = "ensorain/runs/d3_round3.jsonl"
OUT = "ensorain/runs/d4_round4.jsonl"
DIALS3 = (["lam", "sweeps", "scratch", "cap_actual", "replay_frac_actual", "dream_ratio", "surprise_alpha",
           "disturb", "forget", "err_frac_actual", "persist", "p_restruct", "drift", "noise", "kappa_mult"], ["start"])
# every Round-3 nomination except the planted control, with the ruler it was first nominated on
NOMS = [("M1", "scratch", "start", "nlmse"), ("M2", "cap_actual", "replay_frac_actual", "nlmse"),
        ("M3", "sweeps", "kappa_mult", "EFF"), ("M4", "p_restruct", "kappa_mult", "EFF"),
        ("M5", "replay_frac_actual", "kappa_mult", "EFF"), ("M6", "scratch", "cap_actual", "EFF"),
        ("M7", "dream_ratio", "kappa_mult", "EFF"), ("M8", "scratch", "kappa_mult", "EFF"),
        ("M9", "drift", "kappa_mult", "EFF"), ("M10", "cap_actual", "kappa_mult", "EFF"),
        ("M11", "scratch", "drift", "EFF")]
DIAL_KEY = {"cap_actual": "cap", "replay_frac_actual": "replay_frac", "err_frac_actual": "err_frac"}
BG = dict(world_family="TT", org_family="TT", lam=float(np.sqrt(15 * 120)), sweeps=12, scratch=int(round(np.sqrt(64 * 512))),
          cap=int(round(np.sqrt(192 * 512))), replay_frac=0.15, err_frac=0.075, persist=10, dream_ratio=0.5,
          surprise_alpha=0.15, disturb=0.025, forget=0.05, p_restruct=0.5, drift=0.3, noise=0.15, kappa_mult=1.0)
N_CELL = 16


def levels(k, rows):
    if k == "start":
        return ["correct", "random"]
    x = np.array([float(r[k]) for r in rows])
    q = np.quantile(x, [1 / 6, 1 / 2, 5 / 6])
    return [int(round(v)) for v in q] if k in ("sweeps", "scratch", "cap_actual") else [float(v) for v in q]


def jobs():
    configure(*DIALS3, ["nlmse", "EFF"])
    r3 = load(R3)
    out, life = [], 0
    for nid, ki, kj, ruler in NOMS:
        li, lj = levels(ki, r3), levels(kj, r3)
        for a, vi in enumerate(li):
            for b, vj in enumerate(lj):
                for rep in range(N_CELL):
                    d = dict(BG, start=["correct", "random"][rep % 2])
                    d[DIAL_KEY.get(ki, ki)] = vi
                    d[DIAL_KEY.get(kj, kj)] = vj
                    out.append(dict(life=life, inst=90000 + life, seed=990000 + life, dials=d, nom=nid, cell=[a, b]))
                    life += 1
    return out


def score():
    configure(*DIALS3, ["nlmse", "EFF"])
    r3 = load(R3)
    rows = [json.loads(l) for l in open(OUT)]
    ok = [r for r in rows if r.get("status") == "OK"]
    for r in ok:
        r["nlmse"] = float(-np.log10(max(r["mse_ho"], 1e-12)))
    alpha = 0.05 / len(NOMS)
    rep = dict(n=len(rows), n_ok=len(ok), alpha=alpha)
    for nid, ki, kj, ruler in NOMS:
        y3 = np.array([r[ruler] for r in r3], float)
        bi, na = bins(col(r3, ki), ki)
        bj, nb = bins(col(r3, kj), kj)
        P3, M3 = pattern(bi, na, bj, nb, y3)
        v = [r for r in ok if r["nom"] == nid]
        ci, cj = np.array([r["cell"][0] for r in v]), np.array([r["cell"][1] for r in v])
        y = np.array([r[ruler] for r in v], float)
        F, p = interaction_test(ci, na, cj, nb, y)
        P4, M4 = pattern(ci, na, cj, nb, y)
        m = ~np.isnan(P3) & ~np.isnan(P4)
        r_pat = float(np.corrcoef(P3[m], P4[m])[0, 1]) if m.sum() >= 3 else float("nan")
        rep[nid] = dict(pair=[ki, kj], ruler=ruler, n=len(v), F=round(F, 2), p=p, pattern_r=round(r_pat, 3),
                        replicated=bool(p < alpha and r_pat > 0.5), round3_cells=np.round(M3, 3).tolist(),
                        round4_cells=np.round(M4, 3).tolist())
        print(nid, [ki, kj], ruler, "F", round(F, 2), "p", f"{p:.1e}", "r", round(r_pat, 2),
              "REPLICATED" if rep[nid]["replicated"] else "--")
    json.dump(rep, open("ensorain/runs/d4_round4_score.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(jobs(), OUT)
    else:
        score()
