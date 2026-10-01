"""W2-49 copy of W2-29 w29.py; ONLY change: passive per-epoch TRAJ (N, A, B, Bxk) returned as 4th value.
W2-29: run3() = W2-22 w22.run2 (copied; mech switches dropped) + a PASSIVE genome recorder for every child counted in B,
+ stop rule 'xk163' (stop as soon as B_xk >= 163). World code is not modified. See PREREG.md."""
from __future__ import annotations

import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent.parent / "W2-29_residue"  # W2-49: resolve world imports as W2-29 did
sys.path.insert(0, str(HERE.parent / "W2-22_second_regime"))
sys.path.insert(0, str(HERE.parent / "W2-14_F_calibration"))
import w22  # noqa: E402
import ffield as F  # noqa: E402
from ffield import make_runner, set_org, Model, depth_from  # noqa: E402


def run3(rule, seed, struct="FIELD", partner="FULL", ctx="CARRY", mut=True, T=300, bank=None, pool=None,
         stop="xk163", rec=True, stop_runaway=True):
    r = make_runner(rule, seed, mut=mut)
    mrng = random.Random(repr(("W2-14", rule, seed, struct, partner, ctx, mut)))
    model = Model(partner, mrng, bank, pool, r.L)
    founder = next(o for o in r.orgs if o.anc == 0)
    f0 = founder.oid
    g_founder = r._genome(founder)
    causal_set = {f0}
    cnt = {"B": 0, "Ball": 0, "last_birth": 0, "calls": 0, "Bxk": 0, "kin": 0}
    G = {}            # genome bytes -> [first_epoch, B_at_first, count]
    orig_lb = r._lin_birth
    anc0_oids = set()

    def record(child, vic):
        if vic is None:
            vic = next((o for o in r.orgs if o.alive and o.oid == child), None)
            if vic is None:
                return
        g = r._genome(vic)
        e = G.get(g)
        if e is None:
            G[g] = [r.epoch, cnt["B"], 1]
        else:
            e[2] += 1

    def lb(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None, victim_pre_anc=None, vic=None):
        if causal and parent in causal_set:
            causal_set.add(child)
            cnt["B"] += 1
            if victim_pre_anc is not None:
                if victim_pre_anc == 0:
                    cnt["kin"] += 1
                else:
                    cnt["Bxk"] += 1
            if rec:
                record(child, vic)
        if parent in anc0_oids:
            cnt["Ball"] += 1
            cnt["last_birth"] = r.epoch
        orig_lb(child, parent, niche, fid, span, causal, causal_pred, None)

    def interact(a, b, i):
        for o in (a, b):
            if ctx == "ZERO" and o.anc == 0:
                o.regs, o.fz, o.fc = None, 0, 0
        cnt["calls"] += 1
        anc0_oids.clear()
        anc0_oids.update(o.oid for o in (a, b) if o.anc == 0)
        buf = []

        def collect(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            src = a if a.oid == parent else b
            vic = b if src is a else a
            buf.append(((child, parent, niche, fid, span, causal, causal_pred), vic, vic.anc))
        r._lin_birth = collect
        try:
            r._pair_interact(i, a, b)
        finally:
            r._lin_birth = lb
        for args, vic, vanc in buf:
            lb(*args, victim_pre_anc=vanc, vic=vic)

    r._lin_birth = lb
    TRAJ = []  # W2-49
    maxA, stopr, A, N = 1, "horizon", 1, 1
    for ep in range(T):
        r.epoch = ep
        r._env_epoch()
        alive = [o for o in r.orgs if o.alive]
        if struct == "FIELD":
            r.rng.shuffle(alive)
            for i in range(0, len(alive) - 1, 2):
                a, b = alive[i], alive[i + 1]
                lin = a.anc == 0 or b.anc == 0
                if not lin:
                    if partner == "FULL":
                        r._pair_interact(i, a, b)
                        cnt["calls"] += 1
                    continue
                if partner != "FULL":
                    for o in (a, b):
                        if o.anc != 0:
                            g, st = model.draw(ep)
                            set_org(r, o, g, st)
                interact(a, b, i)
        else:
            raise ValueError("FIELD only")
        for o in r.orgs:
            if o.alive:
                o.age += 1
        live = [o for o in r.orgs if o.alive]
        A = sum(o.anc == 0 for o in live)
        N = sum(o.oid in causal_set for o in live)
        maxA = max(maxA, A)
        TRAJ.append((N, A, cnt["B"], cnt["Bxk"]))  # W2-49: passive per-epoch log, end of epoch ep+1
        if A == 0:
            stopr = "extinct"
            break
        if ep >= 100 and ep - cnt["last_birth"] >= 100:
            stopr = "frozen"
            break
        if stop == "xk163" and cnt["Bxk"] >= 163:
            stopr = "xk163"
            break
        if stop in ("orig", "xk") and stop_runaway:
            xk_ok = stop == "orig" or cnt["Bxk"] >= 163
            if maxA >= 40 and cnt["B"] >= 163 and xk_ok and ep % 10 == 9 and depth_from(r.lineage, [f0]) >= 20:
                stopr = "runaway_decided"
                break
    out = {"rule": rule, "seed": seed, "struct": struct, "partner": partner, "ctx": ctx, "mut": mut,
           "epochs": ep + 1, "stop": stopr, "B": cnt["B"], "Ball": cnt["Ball"], "maxA": maxA,
           "A_end": A, "N_end": N, "depth_f": depth_from(r.lineage, [f0]),
           "depth_world": depth_from(r.lineage), "calls": cnt["calls"],
           "Bxk": cnt["Bxk"], "kin": cnt["kin"]}
    return out, G, g_founder, TRAJ  # W2-49
