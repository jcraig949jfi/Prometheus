"""WTP-03 instrument validation (PREREG_WTP03 s10), run before Wave A on validation seeds
9,500,000+ (disjoint from dev seeds 9,1xx,xxx-9,4xx,xxx and campaign seeds). Fixed pass rules.

V1 TEETH        planted lowrank / cp / spectral worlds: X1 fires with SD >= .10 in >= 2 of 3
V2 NO FALSE +   planted ADDITIVE field: no structured substrate has XC >= .10 on any set
V3 SCALAR KILL  the WTP-02 specimen #10 genome (0e3e9ca1cb88f30c) through the collider (lifetime 300, an
                unkillable carrier): the constant substrate's XC <= 0 on every measured set (>= 1 set measured).
                Structured-substrate firings there are RECORDED, not failed (that world may hold real structure).
V4 DETERMINISM  same seed -> identical stream digest and identical collide() output
V5 SURROGATE    marginal surrogate preserves the mean (|d| < 1e-9), the variance (within 1%), every
                per-mode marginal mean (max |d| < 1e-9) and destroys planted structure (V1 worlds: XC_marg < .10)
V6 SUPPORT      ablate_half on a constant memory -> NOT_APPLICABLE; on a trained CP -> changed
V7 RECOMB TEETH planted spectral world: X6 fires (DCT recombines a never-seen pair block)"""
import json
import os

import numpy as np

from .autopsy import intervene
from .collider import experience, collide, additive_part, marginal_surrogate, train, test_sets, make
from .controls import planted, additive_hook
from .detect3 import completion
from .world3 import mem_cap, run_life

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03")


def _collide_world(g, seed, hook=None):
    import ensorain.wtp3.collider as C
    if hook is None:
        st, life = experience(g, seed)
        sm, _ = experience(g, seed, field="marg")
    else:
        tap = dict(t=[], c=[], y=[])
        run_life(C.carrier(g), seed, tap=tap, field_hook=hook, excursions=False)
        st = dict(t=np.concatenate(tap["t"]), c=np.concatenate(tap["c"]), y=np.concatenate(tap["y"]), x=tap["x_final"],
                  V0=tap["x_birth_var"], seen=tap["seen"], dims=tap["dims"], T=tap["T"])
        sm = None
    cap = mem_cap(g, st["x"].size)
    real = collide(st, cap, seed)
    marg = collide(sm, cap, seed) if sm is not None else None
    return st, real, marg


def validate():
    os.makedirs(OUT, exist_ok=True)
    v = {}
    # V1 / V5 / V7
    teeth, surrogate_ok, recomb = [], [], None
    for i, (gen, dims, rank, band) in enumerate([("lowrank", (10, 10, 10), 2, 0.25), ("cp", (10, 10, 10), 2, 0.1),
                                                   ("spectral", (12, 12, 12), 3, 0.03)]):
        g = planted(gen, dims, rank, band)
        st, real, marg = _collide_world(g, 9_500_001 + i)
        fired = completion(real, marg, "interp")
        teeth.append(dict(gen=gen, fired=[(k, round(a, 3), round(sd, 3)) for k, a, sd in fired]))
        xm = max([v2["XC"]["interp"] for v2 in marg["subs"].values() if v2.get("status") == "OK" and v2["XC"]["interp"] is not None
                  and v2.get("n_floats", 0) >= 8 and v2 is not marg["subs"].get("constant")], default=None)
        surrogate_ok.append(xm is not None and xm < 0.10)
        if gen == "spectral":
            recomb = [(k, round(a, 3), round(sd, 3)) for k, a, sd in completion(real, marg, "recomb")]
    v["V1_teeth"] = teeth
    v["V1_pass"] = sum(bool(t["fired"]) for t in teeth) >= 2
    v["V7_recomb"] = recomb
    v["V7_pass"] = bool(recomb)
    # V5 surrogate statistics on a planted field
    rng = np.random.default_rng(9_500_050)
    x = np.random.default_rng(1).normal(size=(10, 10, 10))
    x = x + np.random.default_rng(2).normal(size=(10, 1, 1)) + np.random.default_rng(3).normal(size=(1, 10, 1))
    xs, _ = marginal_surrogate(rng)(x, x)
    marg_d = max(float(np.abs(x.mean(axis=tuple(k for k in range(3) if k != m)) - xs.mean(axis=tuple(k for k in range(3) if k != m))).max())
                 for m in range(3))
    v["V5_stats"] = dict(mean_diff=float(abs(x.mean() - xs.mean())), var_ratio=float(xs.var() / x.var()), marg_max_diff=marg_d)
    v["V5_pass"] = bool(v["V5_stats"]["mean_diff"] < 1e-9 and abs(v["V5_stats"]["var_ratio"] - 1) < 0.01 and marg_d < 1e-9
                        and all(surrogate_ok))
    v["V5_structure_destroyed"] = surrogate_ok
    # V2 additive negative
    g = planted("lowrank", (10, 10, 10), 2, 0.25)
    st, real, _ = _collide_world(g, 9_500_010, hook=additive_hook(9_500_010))
    worst = max([v2["XC"][s] for k, v2 in real["subs"].items() if v2.get("status") == "OK" and v2.get("n_floats", 0) >= 8
                 for s in ("interp", "recomb", "novel") if v2["XC"][s] is not None], default=None)
    v["V2_max_structured_XC"] = worst
    v["V2_pass"] = worst is not None and worst < 0.10
    # V3 WTP-02 specimen #10
    rows = json.load(open(os.path.join(os.path.dirname(__file__), "..", "runs", "wtp02", "waveA.json")))
    g10 = next(r["genome"] for r in rows if r["genome_hash"] == "0e3e9ca1cb88f30c")
    import copy as _copy
    g10 = _copy.deepcopy(g10)
    g10["memory"]["carrier"] = "additive"
    g10["resource"].update(energy0=1e9, metabolism=0.0)   # the organism must live so the specimen can be tested
    g10["time"].update(lifetime=300, lifetime2=300)        # short enough that unseen cells remain (220-cell world)
    st, life = experience(g10, 9_500_020)
    if st is None or len(st["y"]) < 50:
        v["V3"] = dict(note="specimen world yields no usable stream even with an unkillable carrier", life=life.get("status"))
        v["V3_pass"] = False
    else:
        sm, _ = experience(g10, 9_500_020, field="marg")
        cap = mem_cap(g10, st["x"].size)
        real = collide(st, cap, 9_500_020)
        marg = collide(sm, cap, 9_500_020) if sm is not None else None
        fired = completion(real, marg, "interp") + completion(real, marg, "recomb")
        cx = [real["subs"]["constant"]["XC"][s] for s in ("interp", "recomb", "novel") if real["subs"]["constant"]["XC"][s] is not None]
        v["V3"] = dict(fired=[(k, a, sd) for k, a, sd in fired], constant_XC=cx)
        v["V3"]["marg_XC"] = {k: marg["subs"][k].get("XC") for k, *_ in fired} if marg else None
        v["V3_pass"] = bool(cx) and all(c <= 1e-9 for c in cx)   # vacuous (no test cells) fails
    # V4 determinism
    g = planted("cp", (10, 10, 10), 2, 0.1)
    a, _ = experience(g, 9_500_030)
    b, _ = experience(g, 9_500_030)
    ca, cb = collide(a, 100, 9_500_030), collide(b, 100, 9_500_030)
    same = a["digest"] == b["digest"] and json.dumps(ca["subs"], sort_keys=True, default=str) == json.dumps(cb["subs"], sort_keys=True, default=str)
    v["V4_pass"] = bool(same)
    # V6 support
    const = make("constant", [10, 10, 10], 100, np.random.default_rng(0))
    T = np.arange(64)
    _, s1 = intervene("ablate_half", const, a, T, 100, 1, np.random.default_rng(0))
    trained, _ = train("cp", a, 100, 9_500_031)
    _, s2 = intervene("ablate_half", trained, a, T, 100, 1, np.random.default_rng(0))
    v["V6"] = dict(constant=s1, trained=s2)
    v["V6_pass"] = (not s1["changed"]) and s2["changed"]
    v["ALL_PASS"] = all(v[k] for k in v if k.endswith("_pass"))
    json.dump(v, open(os.path.join(OUT, "validation.json"), "w"), indent=1, default=str)
    print(json.dumps(v, indent=1, default=str), flush=True)
    return v
