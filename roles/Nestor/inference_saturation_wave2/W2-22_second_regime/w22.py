"""W2-22: run2() = W2-14 ffield.run (copied, imported helpers unchanged) + extra readouts + COUNTERFACTUAL mechanism
switches. World code is not modified; counterfactuals act on the outcome of the world's own _pair_interact.

Extra readouts: B_xk (causal-lineage births whose victim was NOT a founder-label member before the interaction),
kin (causal-lineage births onto founder-label victims), n_mech (counterfactual events applied).
mech: None | "KIN_COSTLY" (M1) | "NO_REPAIR" (M2)   -- see PREREG.md
stop: "orig" (W2-14's stops exactly) | "xk" (runaway stop also needs B_xk >= 163)
"""
from __future__ import annotations

import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-14_F_calibration"))
import ffield as F  # noqa: E402
from ffield import world, make_runner, set_org, Model, depth_from  # noqa: E402


def run2(rule, seed, struct="FIELD", partner="FULL", ctx="CARRY", mut=True, T=300, bank=None, pool=None,
         traj=False, stop_runaway=True, mech=None, stop="orig", eroded_fid=0.9):
    r = make_runner(rule, seed, mut=mut)
    mrng = random.Random(repr(("W2-14", rule, seed, struct, partner, ctx, mut)))
    model = Model(partner, mrng, bank, pool, r.L)
    crng = random.Random(repr(("W2-22-cf", rule, seed, mech)))          # counterfactual draws only
    cmodel = Model("BANK", crng, bank, pool, r.L) if mech else None
    founder = next(o for o in r.orgs if o.anc == 0)
    f0 = founder.oid
    causal_set = {f0}
    cnt = {"B": 0, "Ball": 0, "last_birth": 0, "calls": 0, "Bxk": 0, "kin": 0, "n_mech": 0}

    orig_lb = r._lin_birth
    anc0_oids = set()

    def lb(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None, victim_pre_anc=None):
        if causal and parent in causal_set:
            causal_set.add(child)
            cnt["B"] += 1
            if victim_pre_anc is not None:
                if victim_pre_anc == 0:
                    cnt["kin"] += 1
                else:
                    cnt["Bxk"] += 1
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
        pre = {id(o): (r._genome(o), o.oid, o.pid, o.anc) for o in (a, b)}
        buf = []

        def collect(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            src = a if a.oid == parent else b
            vic = b if src is a else a
            buf.append(((child, parent, niche, fid, span, causal, causal_pred), vic, src, vic.anc, src.anc))
        r._lin_birth = collect
        try:
            r._pair_interact(i, a, b)
        finally:
            r._lin_birth = lb
        for args, vic, src, vanc, sanc in buf:
            if mech and vanc == 0 and sanc == 0:
                g_v, oid_v, pid_v, _ = pre[id(vic)]
                g_s = pre[id(src)][0]
                if mech == "KIN_COSTLY":
                    g, st = cmodel.draw(r.epoch)
                    set_org(r, vic, g, st)
                    vic.anc = 1
                    cnt["n_mech"] += 1
                    continue
                if mech == "NO_REPAIR" and world._fidelity(g_v, g_s) < eroded_fid:
                    r.mem[vic.slot:vic.slot + r.slot_size] = bytes(r.slot_size)
                    r.mem[vic.slot:vic.slot + len(g_v)] = g_v
                    vic.length = len(g_v)
                    vic.oid, vic.pid, vic.anc = oid_v, pid_v, 0
                    cnt["n_mech"] += 1
                    continue
            lb(*args, victim_pre_anc=vanc)

    r._lin_birth = lb
    tr, maxA, stopr = [], 1, "horizon"
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
            mem = [o for o in alive if o.anc == 0]
            mrng.shuffle(mem)
            for k, o in enumerate(mem):
                if not o.alive or o.anc != 0:
                    continue
                if len(r.free_slots) < 2:
                    break
                g, st = model.draw(ep)
                p = r._place(g, 1)
                p.regs, p.fz, p.fc = (None if st[0] is None else list(st[0])), st[1], st[2]
                a, b = (o, p) if mrng.randrange(2) == 0 else (p, o)
                interact(a, b, 2 * k)
                for x in (o, p):
                    if x.anc != 0:
                        r._kill(x, "free_bg")
            if len(r.orgs) > 4 * r.pop_cap:
                r.orgs = [o for o in r.orgs if o.alive]
        for o in r.orgs:
            if o.alive:
                o.age += 1
        live = [o for o in r.orgs if o.alive]
        A = sum(o.anc == 0 for o in live)
        N = sum(o.oid in causal_set for o in live)
        maxA = max(maxA, A)
        if traj:
            tr.append((N, A, cnt["B"], cnt["Bxk"]))
        if A == 0:
            stopr = "extinct"
            break
        if ep >= 100 and ep - cnt["last_birth"] >= 100:
            stopr = "frozen"
            break
        if struct == "FREE" and A >= 256:
            stopr = "free_cap256"
            break
        xk_ok = stop == "orig" or cnt["Bxk"] >= 163
        if stop_runaway and maxA >= 40 and cnt["B"] >= 163 and xk_ok and ep % 10 == 9 and \
                depth_from(r.lineage, [f0]) >= 20:
            stopr = "runaway_decided"
            break
    out = {"rule": rule, "seed": seed, "struct": struct, "partner": partner, "ctx": ctx, "mut": mut,
           "epochs": ep + 1, "stop": stopr, "B": cnt["B"], "Ball": cnt["Ball"], "maxA": maxA,
           "A_end": A, "N_end": N, "depth_f": depth_from(r.lineage, [f0]),
           "depth_world": depth_from(r.lineage), "calls": cnt["calls"],
           "Bxk": cnt["Bxk"], "kin": cnt["kin"], "n_mech": cnt["n_mech"], "mech": mech}
    if traj:
        out["traj"] = tr
    return out
