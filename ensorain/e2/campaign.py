"""E2 campaign steps. python -m ensorain.e2.campaign <calibrate|devcheck|outer|confirm>"""
import collections
import json
import sys

import numpy as np

from .core import run, H, FAMILIES

OUT = "ensorain/runs/"
ECON = dict(energy0=400.0, metabolism=0.5, reward=10.0, tau=0.15, kappa=5e-6, budget=3e7, scratch=128)
SET_A, SET_B = range(40000, 40030), range(40100, 40130)
ARMS = ("NOMEM", "ORACLE_H", "BLIND1", "RANDPERM", "OUTER", "EXHAUSTIVE", "GREEDY", "MI", "LRSEL", "SD")
FAM_OF = {"TT": "TT", "MAT": "LR", "CP": "CP"}


def load_part2():
    return json.load(open(OUT + "e2_part2.json"))


def calibrate():
    grid = [dict(lam=l, sweeps=s, init_scale=0.5) for l in (3, 10, 30, 100) for s in (5, 10, 20)]
    base = {"TT": dict(lam=30, sweeps=20, init_scale=0.5), "LR": dict(lam=30, sweeps=10, init_scale=0.5),
            "CP": dict(lam=30, sweeps=10, init_scale=0.5)}
    jobs = []
    for fam, key in FAM_OF.items():
        for gi, g in enumerate(grid):
            c = dict(base)
            c[key] = g
            for i in range(500, 506):
                jobs.append(dict(family=fam, inst_seed=i, arm="ORACLE_H", org_seed=0, consts=c, econ=ECON, Dmax=0, gi=gi))
    rows = run(jobs, OUT + "e2_calibrate.jsonl")
    out = {}
    for fam, key in FAM_OF.items():
        agg = collections.defaultdict(list)
        for r in rows:
            if r["family"] == fam and r["status"] == "OK":
                agg[r["gi"]].append(r["r2_ho"])
        best = max(agg, key=lambda gi: np.median(agg[gi]))
        out[key] = dict(cfg=grid[best], dev_median_r2_ho=float(np.median(agg[best])))
        print(fam, out[key], {gi: round(float(np.median(v)), 3) for gi, v in sorted(agg.items())})
    json.dump(out, open(OUT + "e2_constants.json", "w"), indent=1)


def consts():
    c = json.load(open(OUT + "e2_constants.json"))
    out = {k: v["cfg"] for k, v in c.items()}
    out["disc_lam"] = load_part2()["disc_lam"]
    return out


def outer():
    p2 = load_part2()
    cs = consts()
    jobs = []
    for hi, h in enumerate(H):
        for fam in FAMILIES:
            for i in range(4000 + 16 * FAMILIES.index(fam), 4016 + 16 * FAMILIES.index(fam)):
                jobs.append(dict(family=fam, inst_seed=i, arm="OUTER", org_seed=0, consts=cs, econ=ECON,
                                 Dmax=p2["Dmax"], outer_h=list(h), hi=hi))
    for fam in FAMILIES:
        for i in range(4000 + 16 * FAMILIES.index(fam), 4016 + 16 * FAMILIES.index(fam)):
            jobs.append(dict(family=fam, inst_seed=i, arm="NOMEM", org_seed=0, consts=cs, econ=ECON, Dmax=0, hi=-1))
    rows = run(jobs, OUT + "e2_outer.jsonl")
    nom = {(r["family"], r["inst_seed"]): r["U"] for r in rows if r["arm"] == "NOMEM"}
    eff = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == "OUTER":
            eff[r["hi"]].append((r["U"] - nom[(r["family"], r["inst_seed"])]) / max(r["P_used"], 1))
    best = max(eff, key=lambda k: np.mean(eff[k]))
    for k in sorted(eff, key=lambda k: -np.mean(eff[k]))[:5]:
        print(H[k], round(float(np.mean(eff[k])), 3))
    p2["outer_h"] = list(H[best])
    json.dump(p2, open(OUT + "e2_part2.json", "w"), indent=1)
    print("OUTER =", H[best])


def confirm():
    p2 = load_part2()
    cs = consts()
    jobs = []
    for set_name, insts in (("A", SET_A), ("B", SET_B)):
        for fam in FAMILIES:
            for arm in ARMS:
                for i in insts:
                    for o in (0, 1):
                        jobs.append(dict(family=fam, inst_seed=i, arm=arm, org_seed=o, consts=cs, econ=ECON,
                                         Dmax=p2["Dmax"], outer_h=p2["outer_h"], set=set_name))
    run(jobs, OUT + "e2_confirm.jsonl")



def calibrate_disc():
    """Discovery-fit ridge: the CORRECT hypothesis fitted from scratch on the
    discovery buffer, family sweeps; objective median held-out R^2 of the
    world. Mechanism-independent (no identification rate consulted)."""
    from .core import World2, discovery_buffer, build, fit
    cs = consts()
    rows = []
    for lam in (0.01, 0.1, 1.0, 3.0, 10.0):
        cs2 = dict(cs, disc_lam=lam)
        for fam in ("TT", "MAT", "CP"):
            r2s = []
            for i in range(500, 506):
                w = World2(fam, i)
                ev = w.events()
                A, y, _, _ = discovery_buffer(w, ev, np.random.default_rng(i))
                h = w.correct_h()
                m = build(h, cs2, disc=True)
                fit(m, A, y, cs[h[0]]["sweeps"])
                p = m.predict_many(w.addr)
                xf, ho = w.x.reshape(-1), w.heldout_cell
                r2s.append(float(1 - ((xf[ho] - p[ho]) ** 2).sum() / ((xf[ho] - xf[ho].mean()) ** 2).sum()))
            rows.append(dict(lam=lam, family=fam, median_r2_ho=float(np.median(r2s))))
            print(lam, fam, round(float(np.median(r2s)), 3))
    json.dump(rows, open(OUT + "e2_calibrate_disc.json", "w"), indent=1)


if __name__ == "__main__":
    {"calibrate": calibrate, "calibrate_disc": calibrate_disc, "outer": outer, "confirm": confirm}[sys.argv[1]]()
