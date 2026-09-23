"""E1 life loop (PREREG_E1 s1-s4). Scratch allowance S samples, charged
consolidation under a per-life compute ceiling, tight-tolerance locks."""
import numpy as np

from .mem import audit
from .world import NV, D

ECON = dict(
    energy0=60.0,
    metabolism=0.5,
    reward=10.0,
    tau=0.15,
    kappa=1e-5,
    budget=4e7,       # per-life compute ceiling (units)
    scratch=128,
    audit_every=200,
)


def live(world, mem, events, econ=None, stop_at=None, record=False):
    e = dict(ECON, **(econ or {}))
    energy = e["energy0"]
    S = int(e["scratch"])
    sA = np.zeros((S, D), dtype=np.int64)
    sy = np.zeros(S)
    fill = 0
    comp = 0.0
    comp_energy = 0.0
    refused = 0
    rew = {"L1": 0.0, "L2": 0.0, "L3s": 0.0, "L3h": 0.0}
    n = {"L1": 0, "L2": 0, "L3s": 0, "L3h": 0}
    ok = {"L1": 0, "L2": 0, "L3s": 0, "L3h": 0}
    used = mem.used()
    t = -1
    trace = []
    for t, ev in enumerate(events):
        if stop_at is not None and t >= stop_at:
            break
        energy -= e["metabolism"]
        if ev[0] == "obs":
            fa, noise = ev[1], ev[2]
            ys = world.x[tuple(fa.T)] + noise
            for a, v in zip(fa, ys):
                sA[fill], sy[fill] = a, v
                fill += 1
                if fill == S:
                    units = None
                    if comp < e["budget"]:
                        units = mem.consolidate(sA.copy(), sy.copy())
                        comp += units
                        comp_energy += e["kappa"] * units
                        energy -= e["kappa"] * units
                    else:
                        refused += 1
                    fill = 0
        else:
            kind = ev[0]
            if kind == "L3":
                a, w, truth, ho = ev[1], ev[2], ev[3], ev[4]
                key = "L3h" if ho else "L3s"
                fa = np.repeat(np.asarray(a)[None, :], NV, 0)
                fa[:, world.ax["D"]] = np.arange(NV)
                ans = float(sum(wi * mem.predict(x) for wi, x in zip(w, fa)))
                cost = NV * mem.eval_cost()
                sd = world.sd["L3"]
            else:
                a, truth = ev[1], ev[3]
                key = kind
                ans = mem.predict(a)
                cost = mem.eval_cost()
                sd = world.sd[kind]
            comp += cost
            comp_energy += e["kappa"] * cost
            energy -= e["kappa"] * cost
            n[key] += 1
            if abs(ans - truth) < e["tau"] * sd:
                ok[key] += 1
                rew[key] += e["reward"]
                energy += e["reward"]
            if record:
                trace.append((t, key, int(abs(ans - truth) < e["tau"] * sd)))
        if e["audit_every"] and t % e["audit_every"] == 0:
            used = mem.used()
        if energy <= 0:
            break
    used = mem.used()
    pred = mem.predict_many(world.addr)
    xf = world.x.reshape(-1)
    ho = world.heldout_cell

    def r2(msk):
        yv = xf[msk]
        return float(1 - ((yv - pred[msk]) ** 2).sum() / ((yv - yv.mean()) ** 2).sum())

    reward = sum(rew.values())
    out = dict(steps=t + 1, died=bool(energy <= 0), energy=float(energy), reward=reward,
               reward_transfer=rew["L2"] + rew["L3h"], reward_puzzle=rew["L1"] + rew["L3s"],
               comp_units=comp, comp_energy=comp_energy, U=reward - comp_energy, refused=refused,
               P_used=int(used), r2_ho=r2(ho), r2_seen=r2(~ho),
               **{f"n_{k}": n[k] for k in n}, **{f"ok_{k}": ok[k] for k in ok})
    if record:
        out["trace"] = trace
    return out
