"""TASK 2: the 35 C1 RELAY NULL cells of W2-W F1 where neither relay_refresh nor decay-0 relay_flood scores at
SIGNAL level (refresh_check.json rows that are not rescued).
modes:
  ka       variants on a clean synthetic physics (+ zero_comm), and one loss physics; batch vs W2-W exactness
  dials A B   single-dial neutralisation with P-2's relay_refresh at prog_len max(L,16) (W2-W's setting), on the
           first 16 of campaign.plant_viability's 32 worlds (H(seed,0x9147)); plus ALL dials off and the
           actual physics on the same 16 worlds. Dials: update->sync p1; loss->0; cap->0/collision none;
           jitter->0; noise->0; economy off; dest_mode->all (global: fanout N-1); dup->0 (extra).
           A dial is evaluated only where it is active at the cell.
  lio A B  leave-one-in (all dials off except one) for cells where no single removal rescues but ALL does.
  var A B  plant variants (relay_variants.menu) at the cell's ACTUAL physics: dev-select on the same 16
           worlds, then score the selected variant on the row's own 64 HELD worlds (32 pairs) with zero_comm.
  conf     re-score each cell's best rescuing single dial on all 32 plant-viability worlds."""
import sys, json
import af_common as c
import numpy as np
from prometheus.ananke import envs, plants, assays
from prometheus.ananke.physics import Physics
from prometheus.ananke.engine import Controls
from prometheus.ananke.rng import H_int
import relay_variants as rv

src = open(c.HERE.parent / "P-1/decay_plant.py").read().split("N_PER =")[0]
ns = {}; exec(compile(src, "decay_plant_head", "exec"), ns)
relay_refresh = ns["relay_refresh"]

def cells():
    d = json.load(open(c.HERE.parent / "W2-W/out/refresh_check.json"))["rows"]
    return [o for o in d if not (o["refresh"] >= .6 and o["refresh_lo99"] > .55)]

R = None
def row(cid):
    global R
    if R is None: R = {r["cell_id"]: r for r in c.hc.rows()}
    return R[cid]

def pv_seeds(r, M=32):
    return assays.world_seeds(H_int(r["search_seed"], 0x9147), M)

def dials(ph):
    D = {}
    if ph.update_mode == "async" or ph.update_period > 1: D["update"] = dict(update_mode="sync", update_period=1)
    if ph.loss > 0: D["loss"] = dict(loss=0.0)
    if ph.cap > 0 and ph.collision != "none": D["cap"] = dict(cap=0, collision="none")
    if ph.lat_jitter > 0: D["jitter"] = dict(lat_jitter=0)
    if ph.noise > 0: D["noise"] = dict(noise=0)
    if ph.economy_on: D["economy"] = dict(e_income=0, c_emit=0, c_op=0, c_mem=0)
    if ph.dest_mode == "sample":
        D["dest"] = dict(fanout=ph.n_sites - 1) if ph.topology == "global" else dict(dest_mode="all")
    if ph.dup > 0: D["dup"] = dict(dup=0.0)
    return D

def refresh_eval(ph, env, seeds):
    p16 = ph.replace(prog_len=max(ph.prog_len, 16)).validate()
    return c.batch_eval(p16, env, [(c.hc.bc(p16, relay_refresh(p16)), seeds, False)])[0]

def jl(fn, o):
    with open(c.OUT / fn, "a") as f: f.write(json.dumps(o) + "\n")

def done(fn):
    p = c.OUT / fn
    return {json.loads(l)["cell"] for l in open(p)} if p.exists() else set()

def mode_dials(a, b):
    ck = c.Clock(); fin = done("task2_dials.jsonl")
    for o in cells()[a:b]:
        if o["cell"] in fin: continue
        r = row(o["cell"]); ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        s16 = pv_seeds(r)[:16]
        D = dials(ph); res = {}
        e = refresh_eval(ph, env, s16); res["actual"] = [e["acc"], e["lo99"]]
        allk = {}
        for k, kw in D.items():
            allk.update(kw)
            e = refresh_eval(ph.replace(**kw), env, s16); res[k] = [e["acc"], e["lo99"]]
        e = refresh_eval(ph.replace(**allk), env, s16); res["ALL"] = [e["acc"], e["lo99"]]
        rec = {"cell": o["cell"], "active": list(D), "res": res, "cpu_s_cum": ck.done()["cpu_s"]}
        jl("task2_dials.jsonl", rec)
        print(o["cell"][:8], {k: round(v[0], 3) for k, v in res.items()}, flush=True)
    print(ck.done())

def mode_lio(a, b):
    ck = c.Clock(); fin = done("task2_lio.jsonl")
    Dl = {json.loads(l)["cell"]: json.loads(l) for l in open(c.OUT / "task2_dials.jsonl")}
    for o in cells()[a:b]:
        x = Dl.get(o["cell"])
        if not x or o["cell"] in fin: continue
        single = max(v[0] for k, v in x["res"].items() if k not in ("actual", "ALL"))
        if single >= .60 or x["res"]["ALL"][0] < .60 or len(x["active"]) < 2: continue
        r = row(o["cell"]); ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        s16 = pv_seeds(r)[:16]; D = dials(ph); res = {}
        for keep in D:
            kw = {}
            for k, v in D.items():
                if k != keep: kw.update(v)
            e = refresh_eval(ph.replace(**kw), env, s16); res["only_" + keep] = [e["acc"], e["lo99"]]
        # pairs removal: which 2-dial removal rescues (only the dials that lower ALL the most)
        kill = sorted(res, key=lambda k: res[k][0])[:3]
        names = [k[5:] for k in kill]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                kw = {**D[names[i]], **D[names[j]]}
                e = refresh_eval(ph.replace(**kw), env, s16); res[f"rm_{names[i]}+{names[j]}"] = [e["acc"], e["lo99"]]
        rec = {"cell": o["cell"], "res": res, "cpu_s_cum": ck.done()["cpu_s"]}
        jl("task2_lio.jsonl", rec); print(o["cell"][:8], {k: round(v[0], 3) for k, v in res.items()}, flush=True)
    print(ck.done())

def mode_var(a, b):
    ck = c.Clock(); fin = done("task2_var.jsonl")
    for o in cells()[a:b]:
        if o["cell"] in fin: continue
        r = row(o["cell"]); ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
        s16 = pv_seeds(r)[:16]; held = c.held_seeds(r)
        M = rv.menu(env); jobs = []; info = {}
        for k, L in M.items():
            ph2, g, ins, n = rv.genome(ph, L)
            jobs.append((g, s16, False)); info[k] = {"in_space": ins, "lines": n}
        res = c.batch_eval(ph2.validate(), env, jobs)
        for k, e in zip(M, res): info[k]["dev"] = e["acc"]
        best = max(M, key=lambda k: info[k]["dev"])
        ph2, g, ins, n = rv.genome(ph, M[best])
        h = c.batch_eval(ph2.validate(), env, [(g, held, False)])[0]
        z = c.batch_eval(ph2.validate(), env, [(g, held, False)], ctrl=Controls(zero_comm=True))[0]
        rec = {"cell": o["cell"], "menu": info, "selected": best, "held": [h["acc"], h["lo99"], h["hi99"]],
               "zero_comm": z["acc"], "in_space": ins, "lines": n,
               "genome_space": [ph.prog_len, ph.state_dim], "cpu_s_cum": ck.done()["cpu_s"]}
        # second-best in-space member on held too if the best is an override
        ins_k = [k for k in M if info[k]["in_space"]]
        if not ins and ins_k:
            b2 = max(ins_k, key=lambda k: info[k]["dev"])
            ph3, g3, _, _ = rv.genome(ph, M[b2])
            h3 = c.batch_eval(ph3.validate(), env, [(g3, held, False)])[0]
            rec["best_in_space"] = {"member": b2, "held": [h3["acc"], h3["lo99"], h3["hi99"]]}
        jl("task2_var.jsonl", rec)
        print(o["cell"][:8], {k: round(v["dev"], 3) for k, v in info.items()}, "sel", best, "held %.3f lo %.3f" % (h["acc"], h["lo99"]),
              "zc %.3f" % z["acc"], "in_space", ins, rec.get("best_in_space", ""), flush=True)
    print(ck.done())

def mode_conf():
    ck = c.Clock(); fin = done("task2_conf.jsonl")
    for l in open(c.OUT / "task2_dials.jsonl"):
        x = json.loads(l)
        if x["cell"] in fin: continue
        sd = {k: v for k, v in x["res"].items() if k not in ("actual", "ALL")}
        if not sd: continue
        k = max(sd, key=lambda k: sd[k][0])
        if sd[k][0] < .60: continue
        r = row(x["cell"]); ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        e = refresh_eval(ph.replace(**dials(ph)[k]), env, pv_seeds(r))
        rec = {"cell": x["cell"], "dial": k, "acc32": e["acc"], "lo99_32": e["lo99"]}
        jl("task2_conf.jsonl", rec); print(rec, flush=True)
    print(ck.done())

def mode_ka():
    ck = c.Clock(); out = {}
    env = envs.EnvSpec(family="RELAY", d=3, delta=8, trials=16)
    seeds = assays.world_seeds(0xAF2, 32)
    base = Physics(topology="ring", n_sites=64, radius=1, dest_mode="all", lat_base=1, lat_hop=0, loss=0.0,
                   payload_width=1, channels=1, update_mode="sync", update_period=1, decay_shift=0, state_dim=2,
                   prog_len=16).validate()
    for name, ph in {"clean": base, "decay1": base.replace(decay_shift=1),
                     "loss.6_sample2": base.replace(loss=0.6, dest_mode="sample", fanout=2),
                     "async.5": base.replace(update_mode="async", update_p=0.5),
                     "aloha_cap1_r3": base.replace(radius=3, cap=1, collision="aloha")}.items():
        M = rv.menu(env); jobs = [(rv.genome(ph, L)[1], seeds, False) for L in M.values()]
        jobs.append((c.hc.bc(ph, relay_refresh(ph)), seeds, False))
        jobs.append((plants.plant("relay_flood", ph), seeds, False))
        res = c.batch_eval(ph, env, jobs)
        z = c.batch_eval(ph, env, jobs[:len(M)], ctrl=Controls(zero_comm=True))
        out[name] = {k: round(e["acc"], 3) for k, e in zip(list(M) + ["relay_refresh", "relay_flood"], res)}
        out[name]["zero_comm_max"] = max(e["acc"] for e in z)
        print(name, out[name], flush=True)
    # exactness vs W2-W refresh_check on 2 cells (32 worlds, refresh at p16)
    ex = []
    for o in cells()[:2]:
        r = row(o["cell"]); ph = Physics.from_dict(r["physics"]); env2 = envs.EnvSpec(**r["env"])
        e = refresh_eval(ph, env2, pv_seeds(r)); ex.append([o["cell"], e["acc"], o["refresh"], abs(e["acc"] - o["refresh"]) < 1e-12])
    out["w2w_exact"] = ex; print(ex)
    out["compute"] = ck.done(); c.save("task2_ka.json", out); print(ck.done())

if __name__ == "__main__":
    m = sys.argv[1]
    if m == "ka": mode_ka()
    elif m == "dials": mode_dials(int(sys.argv[2]), int(sys.argv[3]))
    elif m == "lio": mode_lio(int(sys.argv[2]), int(sys.argv[3]))
    elif m == "var": mode_var(int(sys.argv[2]), int(sys.argv[3]))
    elif m == "conf": mode_conf()
