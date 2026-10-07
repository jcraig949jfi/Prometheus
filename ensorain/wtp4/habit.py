"""WTP-04 habitability unit (PREREG_WTP04 s4): one (perturbed genome, seed) -> in-life earning rates of
  trivial twins (random policy without memory; frozen memory), the oracle twin, CHEAP carriers
  (constant, table, additive) and STRUCTURED carriers (lowrank, cp, tt, dct).
Rates are U/steps on immortal twins (metabolism 0, energy 1e9), exactly the WTP-03 G3 measurement, so
death never confounds the comparison. Each carrier is the world's own physics with organism 0's memory
replaced (collider.carrier). Cheap competitors are always run first and always reported."""
import copy
import time

import numpy as np

from ensorain.wtp3.collider import carrier, make
from ensorain.wtp3.world3 import build, mem_cap, run_life, streams

CHEAP = ("constant", "table", "additive")
LIFE_KIND = {"constant": "none"}          # the in-life memory registry calls the constant predictor "none"
STRUCT = ("lowrank", "cp", "tt", "dct")


def immortal(g):
    g = copy.deepcopy(g)
    g["resource"]["metabolism"], g["resource"]["energy0"] = 0.0, 1e9
    return g


def _rate(r, trivial=False):
    if r.get("status") == "OK" or (trivial and r.get("degenerate_reason") == "topology"):
        return float(r["U"] / r["steps"]) if r.get("steps") else None
    return None


def fits(g, seed):
    S, _ = streams(seed)
    x, _, dims, _, _, _ = build(g, S)
    cap = mem_cap(g, x.size)
    ok = []
    for kind in CHEAP + STRUCT:
        try:
            m = make(kind, dims, cap, np.random.default_rng(0))
        except ValueError:
            continue
        if kind == "constant" or m.n_floats() <= cap:
            ok.append(kind)
    return ok, dict(cells=int(x.size), cap=int(cap), dims=list(map(int, dims)))


def unit(g, seed):
    t0 = time.time()
    out = dict(seed=int(seed))
    try:
        kinds, info = fits(g, seed)
    except Exception as ex:
        return dict(out, status="ILLEGAL", reason=f"{type(ex).__name__}: {ex}"[:300], secs=round(time.time() - t0, 1))
    out.update(info)
    gz = immortal(g)
    base = carrier(gz, LIFE_KIND.get(kinds[0], kinds[0]) if kinds else "none")
    rates, lives = {}, {}
    jobs = [(tw, base, tw) for tw in ("random", "frozen", "oracle")] + [(k, carrier(gz, LIFE_KIND.get(k, k)), None) for k in kinds]
    for name, gc, tw in jobs:
        r = run_life(gc, seed, twin=tw, excursions=False)
        rates[name] = _rate(r, trivial=tw in ("random", "frozen"))
        lives[name] = dict(status=r.get("status"), why=r.get("degenerate_reason") or r.get("reason"), U=r.get("U"),
                           steps=r.get("steps"), n_seen=r.get("n_seen"), updates=r.get("updates"),
                           digest=r.get("event_digest"))
    out.update(status="OK", kinds=kinds, rates=rates, lives=lives, secs=round(time.time() - t0, 1))
    return out


def classify(u):
    """Per-unit labels (PREREG_WTP04 s5). TRAPPED = the oracle life ends DEGENERATE/topology. margin(gap) = max(0.01, 0.1 * gap)."""
    if u.get("status") != "OK":
        return dict(label="ILLEGAL")
    R = u["rates"]
    triv = [R[k] for k in ("random", "frozen") if R.get(k) is not None]
    orc = R.get("oracle")
    if orc is None and (u.get("lives") or {}).get("oracle", {}).get("why") == "topology":
        return dict(label="TRAPPED")      # even the oracle is confined: geometry/irreversibility kills exploration
    if not triv or orc is None:
        return dict(label="ILLEGAL")
    tmax = max(triv)
    gap = orc - tmax
    if gap <= 0.02 or gap <= 0.2 * abs(tmax):
        return dict(label="INFO_VALUELESS", tmax=tmax, orc=orc)
    m = max(0.01, 0.1 * gap)
    cheap = {k: R[k] for k in CHEAP if R.get(k) is not None}
    struct = {k: R[k] for k in STRUCT if R.get(k) is not None}
    bc = max(cheap.values()) if cheap else None
    bs = max(struct.values()) if struct else None
    best = max([v for v in (bc, bs) if v is not None], default=None)
    d = dict(tmax=tmax, orc=orc, gap=gap, margin=m, best_cheap=bc, best_struct=bs,
             H=(None if best is None else (best - tmax) / gap),
             winner=(max({**cheap, **struct}, key={**cheap, **struct}.get) if (cheap or struct) else None))
    if best is None or best - tmax < m:
        d["label"] = "DEAD"
    elif bs is not None and (bc is None or bs - bc >= m):
        d["label"] = "STRUCT_PAYS"
    else:
        d["label"] = "CHEAP_PAYS"
    return d
