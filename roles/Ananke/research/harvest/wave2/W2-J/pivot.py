"""XOR_PIVOT (W2-B per_sensor_pivotality, imported read-only from wave2/W2-B/rulers_extra.py) for W2-J plants
vs their NOR one-flag cheats at C1 rows, plus H-PLANT P-XOR vs its NOR readout at aa2b8d68 (strict) and
4eeca9f1 (H-PLANT at_c1 override). Fresh namespace W2JS+1, M worlds, trials (2,5,8).
usage: python pivot.py M 'json list of [cell8, fam, opts]' tag   (fam 'pxor_strict' / 'pxor_atc1' for H-PLANT)"""
import sys, time
from wj_common import *
sys.path.insert(0, str(HERE.parent / "W2-B"))
from rulers_extra import per_sensor_pivotality   # noqa: E402  (W2-B, read-only)
import plants_wj as pw
import hp_plants as hp
import run_xor as rx
from screen2 import build
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.physics import Physics


def pxor_nor(ph, Pd):
    """H-PLANT P-XOR lines 0-13 + NOR readout (+ iff no + flag): 16 lines."""
    g = hp.p_xor(ph, Pd)[0].copy()
    tail = plants.assemble(ph, [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)], L=2)
    g[14:16] = tail
    return np.broadcast_to(g, (ph.rules, *g.shape)).copy()


import numpy as np  # noqa: E402

t0 = time.process_time()
M = int(sys.argv[1]); todo = json.loads(sys.argv[2]); tag = sys.argv[3]
seeds = assays.world_seeds(WJ_NS + 1, M)
rows = {r["cell_id"][:8]: r for r in hc.rows() if r["env"]["family"] == "XOR"}
out = []
for c8, fam, o in todo:
    r = rows[c8]
    env = envs.EnvSpec(**r["env"])
    progs = {}
    if fam in ("pxor_strict", "pxor_atc1"):
        ph = Physics.from_dict(r["physics"]).validate() if fam == "pxor_strict" else rx.at_c1(r)[0]
        progs["xor"] = (ph, hp.p_xor(ph, env.period()))
        progs["nor"] = (ph, pxor_nor(ph, env.period()))
    else:
        ph0 = Physics.from_dict(r["physics"])
        for ro in ("xor", "nor"):
            lines, ev, f2 = build(ph0, env, fam, o, readout=ro)
            ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
            progs[ro] = (ph, pw.genome(ph, lines))
    rec = {"cell": r["cell_id"], "fam": fam, "opts": o, "M": M, "trials": [2, 5, 8]}
    for ro, (ph, g) in progs.items():
        acc = hc.evaluate(ph, g, env, seeds)
        piv, arr = per_sensor_pivotality(ph, g, env, seeds, (2, 5, 8))
        # conditional pivotality: split sensor j's flips by the OTHER sensor's cue sign in that trial.
        # parity: p_j(other=+) == p_j(other=-) (both ~ reach); NOR-type: one of them ~ 0.
        ep = envs.build(ph, env, seeds)
        cond = {}
        for j, a in arr.items():
            oth = 1 - j
            sg = np.stack([np.sign(ep.schedule.sense_val[k * env.period(), :, oth].numpy()) for k in (2, 5, 8)], 1)
            cond[j] = {"other+": float(a[sg > 0].mean()) if (sg > 0).any() else None,
                       "other-": float(a[sg < 0].mean()) if (sg < 0).any() else None}
        rec[ro] = {"acc": acc["acc"], "lo99": acc["lo99"], "pivot": piv, "min_pivot": float(min(piv.values())),
                   "cond_pivot": cond}
        print(c8, fam, ro, "acc %.3f lo %.3f" % (acc["acc"], acc["lo99"]), "pivot", {k: round(v, 3) for k, v in piv.items()},
              "cond", {j: {kk: (round(vv, 2) if vv is not None else None) for kk, vv in c.items()} for j, c in cond.items()},
              "cpu %.0f" % (time.process_time() - t0), flush=True)
    out.append(rec)
    save(f"pivot_{tag}.json", {"rows": out, "cpu_s": time.process_time() - t0})
print("cpu_s", time.process_time() - t0)
