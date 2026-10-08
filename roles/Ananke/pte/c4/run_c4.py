"""PTE-C4 runner (GPU): composition and reuse ladder.

usage: python run_c4.py PLAN.json OUTDIR WORKER [--deadline-utc ISO] [--max-jobs N] [--device cuda]

Job fields: cell_id, task in {RELAY1H, HOLD, GATE, FLIP}, rep (c3r REPS key), op in {OP0, OPD, OPDL}, idx, gens.
Task envs at the cell's physics: RELAY1H = RELAY with d = 1; HOLD = HOLD (gap 8, 12 trials); GATE = gated relay with
the cell's FLIP env fields; FLIP = the cell's env. Rulers: FLIP -> the frozen B ruler; all others -> RELAY-mh role
(SIGNAL on all trials + late-half liveness).
OPDL = OPD plus, with probability P_LIB = .15 per offspring (before duplication), insertion of a uniformly chosen
FROZEN library module (plan["library"]) into free capacity, INSTANTIATED with a uniformly random permutation of the
state registers (c4_common.rename_state) so separately evolved modules can coexist. Inserted lines carry a library tag
(module id + 1); module_integrity compares slots against the module's renamed-or-not lines.
Seeds: search_seed = H(C4_NS, task id, cell_key, idx): every arm of one task shares the gen-0 population (same rep
spec) and training worlds; arms differ only in the operator.
Per finished search, for the champion (C2 FINAL rule at the last generation), on held worlds:
  competence; live lines (line ablation on 16 held worlds); library-derived lines (count, live count, modified vs the
  module); dup-derived lines; ablation of ALL library-derived lines -> competence status (causal use of the module).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import pathlib
import socket
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_common as K  # noqa: E402
R = K.R; C = K.C; B = R.B
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS, SearchSpec  # noqa: E402

C4_NS = 0xC4001007
TASK_ID = {"RELAY1H": 1, "HOLD": 2, "GATE": 3, "FLIP": 4}
ROLE = {"RELAY1H": "RELAY-mh", "HOLD": "RELAY-mh", "GATE": "RELAY-mh", "FLIP": "FLIP"}
BASE_SPEC = dict(pop=96, M=8, gens=36, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)


def task_env(cell, task):
    e = envs.EnvSpec(**cell["env"])
    if task == "FLIP":
        return e
    if task == "GATE":
        return dataclasses.replace(e, family="GATE")
    if task == "RELAY1H":
        return dataclasses.replace(e, family="RELAY", d=1, trials=12)
    if task == "HOLD":
        return envs.EnvSpec(family="HOLD", gap=8, trials=12)
    raise KeyError(task)


def search_seed(cell_key, task, idx):
    return C.H_int(C4_NS, TASK_ID[task], cell_key, idx)


def evolve(ph, env, sseed, sp, device, rep, op, lib):
    rr = R.REPS[rep]
    g = np.random.default_rng(sseed)
    pop = R.init_population(g, sp.pop, ph, rr["free_lines"])
    shp = pop.shape[:3]
    tags = np.zeros(shp, bool); dup = np.zeros(shp, bool); lt = np.zeros(shp, np.int16)
    curve = []
    for gen in range(sp.gens):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any
        order = np.argsort(-f, kind="stable")
        curve.append({"gen": gen, "max_acc": float(acc.max()), "mean_acc": float(acc.mean()),
                      "lib_lines_best": int((lt[order[0]] > 0).sum()), "dup_lines_best": int(dup[order[0]].sum())})
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        sel = order[:k]
        nxt, nt, nd, nl = [], [], [], []
        for i in range(sp.elite):
            j = order[i]; nxt.append(pop[j]); nt.append(tags[j]); nd.append(dup[j]); nl.append(lt[j])
        while len(nxt) < sp.pop:
            ia = int(sel[int(g.integers(k))])
            a, ta, da, la = pop[ia], tags[ia], dup[ia], lt[ia]
            if g.random() < sp.p_cross:
                ib = int(sel[int(g.integers(k))])
                m = g.random(a.shape[:2]) < 0.5
                a = np.where(m[..., None], a, pop[ib]); ta = np.where(m, ta, tags[ib])
                da = np.where(m, da, dup[ib]); la = np.where(m, la, lt[ib])
            if op == "OPDL" and g.random() < K.P_LIB:
                a, ta, da, la, _ = K.insert_module(g, a, ta, da, lib, la, ph=ph)
            if op in ("OPD", "OPDL") and g.random() < R.P_DUP:
                a2, ta2, da2, info = R.duplicate(g, a, ta, da)
                r_, b_, s_, pos, _ = info
                la = la.copy(); la[r_, pos:pos + b_] = la[r_, s_:s_ + b_]
                a, ta, da = a2, ta2, da2
            c, t = B.mutate_tagged(g, a, ta, sp)
            # the library tag marks SLOT provenance (it survives later mutation); whether the slot still holds the
            # module's instruction is measured separately (module_integrity: unmodified vs modified)
            nxt.append(c); nt.append(t); nd.append(da); nl.append(la)
        pop, tags, dup, lt = np.stack(nxt), np.stack(nt), np.stack(nd), np.stack(nl)
    fs = assays.world_seeds(C.H_int(sseed, FINAL_NS), sp.M_final)
    rf = assays.evaluate(ph, pop, env, fs, device=device)
    ci = int(np.argmax(rf.mean()))
    return {"pop": pop, "tags": tags, "dup": dup, "lib": lt, "ci": ci, "curve": curve}


def run_job(job, cell, plan, device):
    task, rep, op, idx = job["task"], job["rep"], job["op"], job["idx"]
    ph = R.rep_physics(C.Physics.from_dict(cell["physics"]).validate(), rep)
    env = task_env(cell, task)
    sseed = search_seed(cell["cell_key"], task, idx)
    sp = SearchSpec(**dict(BASE_SPEC, gens=job.get("gens", 36), **plan["selector"]))
    lib = job.get("library") or plan.get("library") or []          # per-job library: s8 arm D (own-cell D-LIB)
    t0 = time.time()
    e = evolve(ph, env, sseed, sp, device, rep, op, lib)
    champ = e["pop"][e["ci"]]; lt = e["lib"][e["ci"]]; dp = e["dup"][e["ci"]]
    hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    role = ROLE[task]
    progs = [champ]
    abl = None
    if (lt > 0).any():
        abl = champ.copy(); abl[lt > 0] = 0; progs.append(abl)
    pt, ep = C.eval_programs(ph, env, hs, progs, device=device)
    comp = C.competence(role, pt[0], ep)
    row = {"kind": "c4_search", "job_id": job["job_id"], "cell_id": cell["cell_id"], "task": task, "arm": job.get("arm"),
           "rep": rep, "op": op,
           "idx": idx, "search_seed": sseed, "search": sp.to_dict(), "competence": C.slim(comp),
           "success": comp["status"] == "TRUE", "champion": champ.tolist(),
           "lib_lines": int((lt > 0).sum()), "lib_modules": sorted(set(int(x) for x in lt[lt > 0])),
           "dup_lines": int(dp.sum()), "curve": e["curve"], "wall_s": None, "device": device,
           "host": socket.gethostname()}
    if abl is not None:
        row["lib_ablation"] = C.slim(C.competence(role, pt[1], ep))
    if comp["status"] == "TRUE" or (lt > 0).any():
        live, _ = K.live_lines(ph, env, champ, hs[:16], role, device=device)
        row["live_lines"] = live
        row["live_lib_lines"] = [i for i in live if lt[0, i] > 0]
        mods = {}
        for mid in row["lib_modules"]:
            mod = np.asarray(lib[mid - 1]["lines"])
            pos = np.flatnonzero(lt[0] == mid)
            variants = [K.rename_state(mod, ph, pm) for pm in __import__("itertools").permutations(range(ph.state_dim))]
            mods[mid] = {"n": int(pos.size), "unmodified": int(sum(any((champ[0, p] == ml).all() for v in variants for ml in v)
                                                                    for p in pos))}
        row["module_integrity"] = mods
    trainw = set()
    for gen in range(sp.gens):
        trainw.update(assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M))
    row["held_train_overlap"] = len(set(hs) & trainw)
    row["wall_s"] = round(time.time() - t0, 2)
    return row, {"pop": e["pop"].astype(np.int16), "tags": e["tags"], "dup": e["dup"], "lib": e["lib"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("outdir"); ap.add_argument("worker", type=int)
    ap.add_argument("--deadline-utc", default=None); ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text())
    cells = {c["cell_id"]: c for c in plan["cells"]}
    out = pathlib.Path(a.outdir); (out / "claims").mkdir(parents=True, exist_ok=True); (out / "pops").mkdir(exist_ok=True)
    deadline = dt.datetime.fromisoformat(a.deadline_utc) if a.deadline_utc else None
    n = 0
    for job in plan["jobs"]:
        if deadline and dt.datetime.now(dt.timezone.utc) >= deadline:
            print("DEADLINE", flush=True); break
        if a.max_jobs is not None and n >= a.max_jobs:
            break
        fid = job["job_id"].replace("|", "__")
        try:
            fd = os.open(str(out / "claims" / (fid + ".claim")), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.write(fd, str(a.worker).encode()); os.close(fd)
        row, npz = run_job(job, cells[job["cell_id"]], plan, a.device)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(out / f"rows_w{a.worker}.jsonl", "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        print(job["job_id"], row["competence"]["status"], row["lib_lines"], row["wall_s"], flush=True)


if __name__ == "__main__":
    main()
