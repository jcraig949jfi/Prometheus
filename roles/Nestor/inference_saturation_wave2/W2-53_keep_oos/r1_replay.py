"""W2-53 r1: bit-exact replay of the B >= 27 conditioned W2-37 runs (FIELD BANK + FREE BANK) with W2-22's run2 body
copied verbatim (mech = None, so the counterfactual branches are inert and crng/cmodel are never drawn) plus the
W2-29/W2-42 PASSIVE recorder: for every causal-lineage child counted in B, the child's genome is read with
r._genome(vic) after the interaction (no rng use, no world-state writes).
Per run: births = [epoch, child gid, victim_pre_anc, Bxk after this birth]; gid = genome hex list in first-birth order.
Gate: every output field of run2 (+ traj when W2-37 kept it) == W2-37 runs_<STRUCT>.jsonl row.
python -B r1_replay.py STRUCT  -> r1_<STRUCT>.jsonl, r1_gate_<STRUCT>.json"""
from __future__ import annotations
import json, pickle, random, sys, time, pathlib
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
W37 = W2 / "W2-37_fstar_k1"
sys.path.insert(0, str(W2 / "W2-22_second_regime"))
import w22  # noqa: E402
F = w22.F
from ffield import world, make_runner, set_org, Model, depth_from  # noqa: E402
BANKS = None


def run2r(rule, seed, struct="FIELD", partner="FULL", ctx="CARRY", mut=True, T=300, bank=None, pool=None,
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
    # ---- passive recorder (W2-29 record / W2-42 births) ----
    GID = {}
    births = []

    def gid(g):
        k = GID.get(g)
        if k is None:
            k = GID[g] = len(GID)
        return k

    def record(child, vic, vanc):
        if vic is None:
            vic = next((o for o in r.orgs if o.alive and o.oid == child), None)
        births.append([r.epoch, None if vic is None else gid(r._genome(vic)), vanc, cnt["Bxk"]])
    # ---------------------------------------------------------

    orig_lb = r._lin_birth
    anc0_oids = set()

    def lb(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None, victim_pre_anc=None, vic=None):
        if causal and parent in causal_set:
            causal_set.add(child)
            cnt["B"] += 1
            if victim_pre_anc is not None:
                if victim_pre_anc == 0:
                    cnt["kin"] += 1
                else:
                    cnt["Bxk"] += 1
            record(child, vic, victim_pre_anc)
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
                raise RuntimeError("mech is None in W2-53")
            lb(*args, victim_pre_anc=vanc, vic=vic)

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
    rec = {"gid": [g.hex() for g in sorted(GID, key=GID.get)], "births": births}
    return out, rec


def job(a):
    global BANKS
    struct, s, ref = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    out, rec = run2r("BASE", 9_998_000 + s, struct, "BANK", "CARRY", True, T=300, bank=BANKS["BASE"],
                     pool=BANKS["POOL"], traj=True, mech=None, stop="xk")
    cpu = round(time.process_time() - t0, 2)
    keys = [k for k in ref if k not in ("s", "cpu_s", "traj")]
    mism = {k: (out.get(k), ref[k]) for k in keys if out.get(k) != ref[k]}
    if "traj" in ref and [list(x) for x in out["traj"]] != ref["traj"]:
        mism["traj"] = "differs"
    out.pop("traj")
    return {"s": s, "struct": struct, "cpu_s": cpu, "mismatch": mism, "keys_checked": keys + (["traj"] if "traj" in ref else []),
            "out": out, **rec}


if __name__ == "__main__":
    struct = sys.argv[1]
    refs = [json.loads(l) for l in open(W37 / ("runs_%s.jsonl" % struct))]
    todo = [(struct, d["s"], d) for d in refs if d["B"] >= 27]
    t0 = time.time()
    res = []
    with mp.Pool(5) as p, open(HERE / ("r1_%s.jsonl" % struct), "w") as fh:
        for x in p.imap_unordered(job, sorted(todo, key=lambda t: -t[2]["cpu_s"]), chunksize=1):
            fh.write(json.dumps(x) + "\n"); fh.flush()
            res.append(x)
            print(struct, x["s"], "mism", x["mismatch"], "cpu", x["cpu_s"], flush=True)
    gate = {"struct": struct, "n": len(res), "n_mismatch": sum(bool(x["mismatch"]) for x in res),
            "cpu_s_total": round(sum(x["cpu_s"] for x in res), 1), "wall_s": round(time.time() - t0, 1),
            "runs": {x["s"]: {"mismatch": x["mismatch"], "B": x["out"]["B"], "Bxk": x["out"]["Bxk"],
                              "stop": x["out"]["stop"], "epochs": x["out"]["epochs"], "cpu_s": x["cpu_s"],
                              "n_keys": len(x["keys_checked"]), "traj_checked": "traj" in x["keys_checked"]}
                     for x in sorted(res, key=lambda x: x["s"])}}
    (HERE / ("r1_gate_%s.json" % struct)).write_text(json.dumps(gate, indent=1))
    print("DONE", struct, gate["n"], "mismatch", gate["n_mismatch"], "cpu", gate["cpu_s_total"], "wall", gate["wall_s"])
