"""E0 lifetime simulator: one organism, one world, one life (PREREG_E0 s1-s4).

The policy skeleton is fixed and identical for every arm: predict each
exit's destination value from memory, take argmax with epsilon exploration,
avoid an 8-entry transient tabu (scratch, identical for all arms, not
persistent memory). Only the memory differs between arms.
"""
from collections import deque
import numpy as np
from .memories import audit
from .world import N

ECON_DEFAULT = dict(
    energy0=30.0,      # starting energy
    metabolism=1.0,    # per step
    gain=3.0,          # g
    theta=0.5,         # harvest threshold
    regrow=500,        # steps before a harvested cell yields again
    kappa=0.0005,      # energy per flop-proxy unit
    horizon=2000,      # L
    noise=0.1,         # observation sd
    epsilon=0.1,       # exploration
    tabu=8,
    audit_every=250,
)


def live(world, mem, cap, seed, econ=None, record_curve=False):
    e = dict(ECON_DEFAULT, **(econ or {}))
    rng = np.random.default_rng(seed)
    last_harv = np.full(N, -10**9)
    pos = int(rng.integers(N))
    energy = e["energy0"]
    tabu = deque(maxlen=e["tabu"])
    harvest = 0.0
    visited = np.zeros(N, dtype=bool)
    dec_n = dec_ok = 0
    flops_total = 0
    used = audit(mem, cap)
    t = 0
    curve = []
    x = world.x
    addr = world.addr
    for t in range(e["horizon"]):
        f0 = mem.flops
        a = addr[pos]
        y = x[pos] + rng.normal(0, e["noise"])
        visited[pos] = True
        mem.observe(a, y)
        if t - last_harv[pos] >= e["regrow"]:
            g = e["gain"] * max(0.0, x[pos] - e["theta"])
            harvest += g
            energy += g
            last_harv[pos] = t
        tabu.append(pos)
        ex = world.exits[pos]
        cand = [d for d in ex if d not in tabu] or list(ex)
        preds = [mem.predict(addr[d]) for d in cand]
        if rng.random() < e["epsilon"]:
            nxt = int(cand[int(rng.integers(len(cand)))])
        else:
            nxt = int(cand[int(np.argmax(np.asarray(preds) + rng.uniform(0, 1e-9, len(preds))))])  # random tie-break
        xv = x[np.array(cand)]
        if len(np.unique(xv)) >= 2:
            dec_n += 1
            dec_ok += int(x[nxt] == xv.max())
        df = mem.flops - f0
        flops_total += df
        energy -= e["metabolism"] + e["kappa"] * df
        pos = nxt
        if record_curve and t % 100 == 0:
            curve.append((t, harvest))
        if e["audit_every"] and t % e["audit_every"] == 0:
            used = audit(mem, cap)
        if energy <= 0:
            break
    used = audit(mem, cap)
    steps = t + 1
    # instrumentation (organism never sees this)
    pred = mem.predict_all(addr)
    r2_all = _r2(world.x, pred)
    unv = ~visited
    r2_unv = _r2(world.x[unv], pred[unv]) if unv.sum() > 10 else float("nan")
    out = dict(harvest=harvest, steps=steps, died=bool(energy <= 0), energy=energy,
               dec_n=dec_n, dec_acc=dec_ok / max(dec_n, 1), flops=flops_total,
               visited=int(visited.sum()), r2_all=r2_all, r2_unv=r2_unv, mem_used=used)
    if record_curve:
        out["curve"] = curve
    return out


def _r2(y, p):
    ss = ((y - y.mean()) ** 2).sum()
    return float(1 - ((y - p) ** 2).sum() / ss) if ss > 0 else float("nan")


def random_life(world, seed, econ=None):
    """RANDOM arm: uniform random exit, no memory, no predictions."""
    from .memories import NoMem
    return live(world, NoMem(0), 0, seed, dict(econ or {}, epsilon=1.0))
