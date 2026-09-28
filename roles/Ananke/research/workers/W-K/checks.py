"""Stage 2: run every candidate check (PLAN.md K0..K9) on every fixture.
Writes out/matrix.json. Scoring is in score.py (rule frozen in PLAN.md)."""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
import wk  # noqa: E402
from prometheus.ananke import c1b, envs, lens  # noqa: E402
from prometheus.ananke.engine import Controls, World, Schedule  # noqa: E402

HERE = os.path.dirname(__file__)
PASS, FLAG, NA = "PASS", "FLAG", "NA"

PC_MAP = {("transport", "HOLD"): "echo_hold", ("transport", "RELAY"): "relay_flood",
          ("S", "HOLD"): "hold_latch", ("rule", "HOLD"): "rule_switch_hold",
          ("routing", "RELAY"): "route_relay", ("energy", "RELAY"): "relay_flood",
          ("energy", "HOLD"): "echo_hold"}
CP_MAP = {("transport", "HOLD"): "hold_latch", ("S", "HOLD"): "echo_hold",
          ("rule", "HOLD"): "hold_latch", ("routing", "RELAY"): "relay_flood",
          ("energy", "HOLD"): "hold_latch"}


def timed(fn):
    def wrap(*a, **k):
        r0, t0 = wk.COST["runs"], time.time()
        out = fn(*a, **k)
        out["runs"] = wk.COST["runs"] - r0
        out["wall"] = round(time.time() - t0, 2)
        return out
    return wrap


# ------------------------------------------------------------------ helpers
def plant_run(fx, name, harness):
    pph, gfn = wk.PLANTS[name]
    ph = c1b.at_specimen(pph(), fx.ph)
    g = gfn(ph)
    n = harness.run(ph, g, fx.env, wk.NORMAL)
    a = harness.run(ph, g, fx.env, fx.arm)
    return n, a


def twin_world(fx, g):
    ep = envs.build(fx.ph, fx.env, wk.SEEDS)
    sv = ep.schedule.sense_val.clone()
    Pd = fx.env.period()
    tk0 = 5 * Pd
    B = len(wk.SEEDS)
    for b in range(1, B, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + fx.env.cue_len, b] = -sv[tk0:tk0 + fx.env.cue_len, b - 1]
    sidx, ridx = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    for b in range(1, B, 2):
        sidx[b], ridx[b] = sidx[b - 1], ridx[b - 1]
    ws = [wk.SEEDS[m - (m % 2)] for m in range(B)]
    w = World(fx.ph, np.repeat(g[None], B, 0), ws, device=wk.DEV, schedule=Schedule(sidx, sv, ridx))
    return w, ep


def var_sites(w, var):
    """Declared variable with a leading [B, N] (post-tick unless 'delivered')."""
    if var == "delivered":
        slot = w.t % w.LM
        return torch.cat([w.Msum[slot].flatten(2), w.Mcnt[slot].flatten(2)], 2)
    x = wk.state_of(w, var)
    return x.reshape(x.shape[0], x.shape[1], -1)


# ------------------------------------------------------------------ checks
@timed
def k0(fx, base):
    return {"status": FLAG if base["reading"]["reading"] == "NULL" else PASS}


@timed
def k1(fx, base):
    if not fx.arm.window:
        return {"status": NA, "why": "not a windowed packet-drop arm"}
    g = wk.genome_of(fx)
    wk.COST["runs"] += 1
    prof = lens.cue_arrival_profile(fx.ph, g, fx.env, trial=5, M=wk.M, ns=wk.NS, device=wk.DEV)
    ep = base["n"].ep
    ro5 = int(ep.ro_tick[0, 5])
    ticks, _ = fx.arm.foot_fn(fx.env, ep, fx.ph)
    r = lens.reach(prof, [t - ro5 for t in ticks])
    return {"status": FLAG if (r is None or r < 0.5) else PASS, "reach": r,
            "lags": {str(k): v for k, v in prof["lags"].items()}}


@timed
def k1g(fx, base):
    g = wk.genome_of(fx)
    wk.COST["runs"] += 1
    w, ep = twin_world(fx, g)
    ticks, sm = fx.arm.foot_fn(fx.env, ep, fx.ph)
    cond_kind = sm if isinstance(sm, str) else None
    if cond_kind:
        hook = wk.CondFlush(cond_kind)
        sm = None
    tset = set(ticks) if ticks is not None else set()
    P = w.B // 2
    in_fp = np.zeros(P, bool)
    anywhere = False
    smt = torch.as_tensor(sm) if sm is not None else None
    for t in range(fx.env.T()):
        pre = var_sites(w, fx.arm.var) if fx.arm.var == "delivered" else None
        w.step()
        v = pre if pre is not None else var_sites(w, fx.arm.var)
        d = (v[0::2] != v[1::2]).any(-1)                     # [P, N]
        if bool(d.any()):
            anywhere = True
        if cond_kind:
            c = hook.cond(w, ep)
            wm = (c[0::2] | c[1::2]).numpy()
            in_fp |= (d.any(-1).numpy() & wm)
        elif t in tset:
            if smt is not None:
                d = d & smt[0::2]
            in_fp |= d.any(-1).numpy()
    if not anywhere:
        return {"status": NA, "why": "declared variable never differs between cue twins"}
    frac = float(in_fp.mean())
    return {"status": FLAG if frac < 0.5 else PASS, "frac_pairs": frac}


def _k2(fx, harness):
    key = (fx.arm.pathway, fx.env.family)
    if key not in PC_MAP:
        return {"status": NA, "why": "no must-flip plant"}
    n, a = plant_run(fx, PC_MAP[key], harness)
    lo = c1b.ci(n.pairs)[1]
    hi_d = c1b.ci(a.pairs - n.pairs)[2]
    ok = lo > c1b.COMPETENT_LO and hi_d < c1b.FIRED_HI
    return {"status": PASS if ok else FLAG, "plant": PC_MAP[key], "competent_lo99": lo,
            "diff_hi99": hi_d}


@timed
def k2(fx, base):
    return _k2(fx, fx.harness)


@timed
def k2iso(fx, base):
    return _k2(fx, wk.Harness())


@timed
def k3(fx, base):
    same = np.array_equal(base["n"].trace, base["a"].trace)
    return {"status": FLAG if same else PASS}


@timed
def k3b(fx, base):
    same = base["n"].digests == base["a"].digests
    return {"status": FLAG if same else PASS}


@timed
def k3c(fx, base):
    tn, ta = base["n"].trace, base["a"].trace
    dw = (tn != ta).reshape(tn.shape[0], -1, 2, tn.shape[2]).any((0, 2, 3))
    frac = float(dw.mean())
    return {"status": FLAG if frac < 0.5 else PASS, "frac_pairs": frac}


@timed
def k4d(fx, base):
    h = base["a"].self_hits
    return {"status": FLAG if h == 0 else PASS, "self_hits": h}


@timed
def k4c(fx, base):
    g = wk.genome_of(fx)
    r = fx.harness.run(fx.ph, g, fx.env, fx.arm, shadow=True)
    return {"status": FLAG if r.applied == 0 else PASS, "applied_tick_worlds": r.applied,
            "worlds_touched": r.applied_worlds}


@timed
def k5(fx, base):
    rn, ra = base["n"].rec, base["a"].rec
    diff = any(not torch.equal(x, y) for x, y in zip(rn, ra))
    return {"status": PASS if diff else FLAG}


@timed
def k6a(fx, base):
    mn, ma = base["n"].manifest, base["a"].manifest
    dc = set(fx.arm.declared_ctrl(fx.env, base["n"].ep))
    dp = set(fx.arm.phys)
    extra = []
    for k in ("genome", "ws", "sense_idx", "sense_val", "read_idx", "y", "scored", "ro_tick"):
        if mn[k] != ma[k]:
            extra.append(k)
    for k, v in mn["physics"].items():
        if ma["physics"][k] != v and k not in dp:
            extra.append("physics." + k)
    for k, v in mn["ctrl"].items():
        if ma["ctrl"][k] != v and k not in dc:
            extra.append("ctrl." + k)
    return {"status": FLAG if extra else PASS, "undeclared_diffs": extra}


@timed
def k6b(fx, base):
    mn, ma = base["n"].manifest, base["a"].manifest
    missing = []
    for k in fx.arm.declared_ctrl(fx.env, base["n"].ep):
        if ma["ctrl"][k] == mn["ctrl"][k]:
            missing.append("ctrl." + k)
    for k in fx.arm.phys:
        if ma["physics"][k] == mn["physics"][k]:
            missing.append("physics." + k)
    if fx.arm.hook is not None and ma["hook"] is None:
        missing.append("hook")
    return {"status": FLAG if missing else PASS, "declared_absent": missing}


@timed
def k7(fx, base):
    key = (fx.arm.pathway, fx.env.family)
    if key not in CP_MAP:
        return {"status": NA, "why": "no must-not-flip plant for this env"}
    n, a = plant_run(fx, CP_MAP[key], fx.harness)
    lo = c1b.ci(n.pairs)[1]
    if lo <= c1b.COMPETENT_LO:
        return {"status": NA, "why": "counter-plant not competent", "competent_lo99": lo}
    dlo = c1b.ci(a.pairs - n.pairs)[1]
    return {"status": FLAG if dlo < c1b.INTACT_LO else PASS, "plant": CP_MAP[key],
            "diff_lo99": dlo}


@timed
def k8s(fx, base):
    gen = torch.Generator().manual_seed(wk.NS)
    ph = fx.ph.replace(**fx.arm.phys) if fx.arm.phys else fx.ph
    ep = base["n"].ep
    ticks, sm = fx.arm.foot_fn(fx.env, ep, fx.ph)
    var = fx.arm.var
    B = len(wk.SEEDS)

    def scramble(w, wmask=None):
        if var == "S":
            x = torch.randint(-256, 257, w.S.shape, generator=gen, dtype=torch.int32)
            m = torch.ones(w.S.shape[:2], dtype=torch.bool) if sm is None or isinstance(sm, str) \
                else torch.as_tensor(sm)
            w.S.copy_(torch.where(m[..., None], x, w.S))
        elif var == "r":
            w.r.copy_(torch.randint(0, ph.rules, w.r.shape, generator=gen))
        elif var == "w":
            w.w.copy_(torch.randint(0, 1024, w.w.shape, generator=gen, dtype=torch.int32))
        elif var == "E":
            w.E.copy_(torch.randint(0, ph.e_max + 1, w.E.shape, generator=gen, dtype=torch.int32))
        elif var == "inflight":
            xs = torch.randint(-256, 257, w.Msum.shape, generator=gen, dtype=torch.int32)
            xc = torch.randint(0, 3, w.Mcnt.shape, generator=gen, dtype=torch.int32)
            m = wmask if wmask is not None else torch.ones(B, dtype=torch.bool)
            w.Msum.copy_(torch.where(m[None, :, None, None, None], xs, w.Msum))
            w.Mcnt.copy_(torch.where(m[None, :, None, None], xc, w.Mcnt))
        elif var == "delivered":
            slot = (w.t) % w.LM                      # arrives at the next tick
            w.Msum[slot].copy_(torch.randint(-256, 257, w.Msum[slot].shape, generator=gen,
                                             dtype=torch.int32))
            w.Mcnt[slot].copy_(torch.randint(0, 3, w.Mcnt[slot].shape, generator=gen,
                                             dtype=torch.int32))
    hooks = {}
    if isinstance(sm, str):
        cf = wk.CondFlush(sm)

        def hk(w):
            c = cf.cond(w, ep)
            if bool(c.any()):
                scramble(w, c)
        hooks = {t: hk for t in range(fx.env.T())}
    elif var == "delivered":
        hooks = {t - 1: scramble for t in ticks if t >= 1}
    else:
        hooks = {t: scramble for t in ticks}
    g = wk.genome_of(fx)
    r = fx.harness.run(ph, g, fx.env, wk.NORMAL, extra_hooks=hooks)
    same = np.array_equal(r.trace, base["n"].trace) if not fx.arm.phys else None
    if fx.arm.phys:      # scramble under the arm physics: compare with the arm run
        same = np.array_equal(r.trace, base["a"].trace)
    return {"status": FLAG if same else PASS}


@timed
def k9(fx, base):
    g = wk.genome_of(fx)
    s = fx.harness.run(fx.ph, g, fx.env, fx.arm.sham(), is_normal=False)
    same = np.array_equal(s.trace, base["n"].trace) and np.array_equal(s.acc, base["n"].acc)
    return {"status": PASS if same else FLAG}


CHECKS = {"K0": k0, "K1": k1, "K1g": k1g, "K2": k2, "K2iso": k2iso, "K3": k3, "K3b": k3b,
          "K3c": k3c, "K4d": k4d, "K4c": k4c, "K5": k5, "K6a": k6a, "K6b": k6b, "K7": k7,
          "K8s": k8s, "K9": k9}


def main(only=None):
    out = {}
    for fx in wk.fixtures():
        if only and fx.fid not in only:
            continue
        t0, r0 = time.time(), wk.COST["runs"]
        g = wk.genome_of(fx)
        n = fx.harness.run(fx.ph, g, fx.env, wk.NORMAL, record=fx.arm.var)
        a = fx.harness.run(fx.ph, g, fx.env, fx.arm, record=fx.arm.var)
        base = {"n": n, "a": a, "reading": wk.reading(n, a)}
        row = {"truth": fx.truth, "shape": fx.shape, "twin": fx.twin, "claim": fx.claim,
               "harness": fx.harness.label, "arm": fx.arm.name,
               "reading": base["reading"], "reading_cost": {"runs": wk.COST["runs"] - r0,
                                                            "wall": round(time.time() - t0, 2)},
               "checks": {}}
        for k, fn in CHECKS.items():
            try:
                row["checks"][k] = fn(fx, base)
            except Exception as e:          # a crashed check is NOT a pass
                row["checks"][k] = {"status": "ERROR", "why": repr(e), "runs": 0, "wall": 0}
        print(fx.fid, fx.truth, base["reading"]["reading"],
              " ".join(f"{k}:{v['status'][0]}" for k, v in row["checks"].items()), flush=True)
        out[fx.fid] = row
    name = "matrix.json" if not only else "matrix_partial.json"
    with open(os.path.join(HERE, "out", name), "w") as f:
        json.dump(out, f, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
