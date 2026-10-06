"""C2BX + PTE-C2C runner (GPU). One job = one search. Shared 3-worker queue (plan order, O_EXCL claims).

usage: python run_c2c.py PLAN.json OUTDIR WORKER_ID [--deadline-utc ISO] [--max-jobs N] [--device cuda]

C2BX job (RELAY-mh cell, idx 0..7): the C2B B4X search continued unchanged. Same search_seed (C2A
search_seed(cell_key, idx)), same BASE settings and frozen operator, run to 576 generations (16x the C2A budget of
36). Checkpoint champions every 36 generations (gen 36, 72, ..., 576) with C2B's rule: gen 36 uses C2A's FINAL key,
later ones H(search_seed, FINAL_NS, 0xC4E7, gen). Prefix gate: the population after generation 144 (index 143)
equals C2B's saved B4X final population and the checkpoint statuses at 36/72/108/144 equal C2B's row.
C2C job (FLIP cell, idx 0..7, arm in OP0_BASE / OPB_BASE / OP0_STEP / OPB_STEP): 36 generations, BASE settings;
search_seed = c2c_common.search_seed (fresh); OPB = c2c_common.mutate_opb; STEP arms inject the cell's graded stone
for that idx at gen-0 index 0 (the same stone in OP0_STEP and OPB_STEP).
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import json
import os
import pathlib
import socket
import sys
import tarfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c2c_common as X  # noqa: E402
B = X.B
C = X.C
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS, SearchSpec, random_genomes  # noqa: E402

BASE_SPEC = dict(pop=96, M=8, gens=36, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)
C2BX_CKPTS = tuple(36 * j - 1 for j in range(1, 17))      # 35, 71, ..., 575


def champion_at(ph, env, pop, sseed, gi, sp, device):
    key = C.H_int(sseed, FINAL_NS) if gi == 35 else C.H_int(sseed, FINAL_NS, B.FINAL_CKPT_KEY, gi + 1)
    rf = assays.evaluate(ph, pop, env, assays.world_seeds(key, sp.M_final), device=device)
    return int(np.argmax(rf.mean())), rf.mean()


def evolve(ph, env, sseed, sp, device, mutate, init=None, ckpts=(), snaps=(), held=None, role=None):
    g = np.random.default_rng(sseed)
    pop = random_genomes(g, sp.pop, ph)
    tags = np.zeros(pop.shape[:3], dtype=bool)
    if init is not None:
        pop[0] = init; tags[0] = True
    curve, plog_all, cks, snap = [], [], {}, {}
    for gen in range(sp.gens):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any
        order = np.argsort(-f, kind="stable")
        share = tags.mean((1, 2)); lin = share >= B.LINEAGE_MIN_SHARE
        rec = {"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]),
               "max_acc": float(acc.max()), "mean_acc": float(acc.mean())}
        if init is not None:
            rec.update(n_lineage=int(lin.sum()), lineage_max_acc=float(acc[lin].max()) if lin.any() else None)
        curve.append(rec)
        if gen in ckpts:
            ci, fa = champion_at(ph, env, pop, sseed, gen, sp, device)
            pt, ep = C.eval_programs(ph, env, held, [pop[ci]], device=device)
            cc = C.competence(role, pt[0], ep)
            cks[gen + 1] = {"champion": pop[ci].tolist(), "champ_index": ci, "status": cc["status"],
                            "competence": C.slim(cc), "champ_train_final": float(fa[ci]),
                            "lineage_share": float(share[ci])}
        if gen in snaps:
            snap[gen] = pop.copy()
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        par, ptag = pop[order[:k]], tags[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        ntag = [tags[order[i]] for i in range(sp.elite)]
        plog = [[int(order[i]), -1, 1] for i in range(sp.elite)]
        while len(nxt) < sp.pop:
            ia = int(g.integers(k))
            a, ta, ib = par[ia], ptag[ia], -1
            if g.random() < sp.p_cross:
                ib = int(g.integers(k))
                a, ta = B.crossover_tagged(g, a, par[ib], ta, ptag[ib])
            c, t = mutate(g, a, ta, sp)
            nxt.append(c); ntag.append(t)
            plog.append([int(order[ia]), int(order[ib]) if ib >= 0 else -1, 0])
        plog_all.append(plog)
        pop, tags = np.stack(nxt), np.stack(ntag)
    return {"pop": pop, "tags": tags, "curve": curve, "checkpoints": cks, "snap": snap,
            "parents": np.asarray(plog_all, dtype=np.int16)}


def load_c2b_b4x(c2b_dir):
    rows = {}
    for l in gzip.open(os.path.join(c2b_dir, "production", "rows_C2B.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r["arm"] == "B4X":
            rows[(r["cell_id"], r["idx"])] = r
    tf = tarfile.open(os.path.join(c2b_dir, "production", "pops_C2B.tar"))
    ref = {}
    for (cid, idx), r in rows.items():
        name = "pops/" + f"{cid}|B4X|{idx:02d}".replace("|", "__") + ".npz"
        z = np.load(io.BytesIO(tf.extractfile(name).read()))
        ref[(cid, idx)] = {"pop": z["pop"], "checkpoint_status": r["checkpoint_status"], "row_success": r["success"]}
    return ref


def run_job(job, cell, device, c2b_ref):
    ph = C.Physics.from_dict(cell["physics"]).validate()
    env = envs.EnvSpec(**cell["env"])
    role, idx = cell["role"], job["idx"]
    plant = np.asarray(cell["plant_genome"], dtype=np.int64)
    t0 = time.time()
    row = {"job_id": job["job_id"], "cell_id": cell["cell_id"], "role": role, "idx": idx, "campaign": job["campaign"],
           "arm": job["arm"], "device": device, "host": socket.gethostname()}
    if job["campaign"] == "C2BX":
        sseed = C.search_seed(cell["cell_key"], idx)
        sp = SearchSpec(**dict(BASE_SPEC, gens=int(job.get("gens", 576))))   # flights only may shorten
        hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
        ev = evolve(ph, env, sseed, sp, device, B.mutate_tagged, ckpts=C2BX_CKPTS, snaps=(143,), held=hs, role=role)
        st = {g: ev["checkpoints"][g]["status"] for g in sorted(ev["checkpoints"])}
        ref = c2b_ref[(cell["cell_id"], idx)]
        pop_eq = bool(np.array_equal(ev["snap"][143].astype(np.int16), ref["pop"]))
        ck_eq = all(st[g] == ref["checkpoint_status"][str(g)] for g in (36, 72, 108, 144))
        first = next((g for g in sorted(st) if st[g] == "TRUE"), None)
        row.update(kind="c2bx_search", search_seed=sseed, checkpoint_status={str(g): s for g, s in st.items()},
                   first_competent_gen=first,
                   success_by={str(b): any(st[g] == "TRUE" for g in st if g <= b) for b in (144, 288, 576) if b <= sp.gens},
                   final_status_at={str(b): st[b] for b in (144, 288, 576) if b in st},
                   prefix_gate={"pop143_equal": pop_eq, "checkpoints_36_144_equal": ck_eq,
                                "status": "PASS" if (pop_eq and ck_eq) else "FAIL"},
                   checkpoints={str(g): {k: v for k, v in c.items() if k != "champion"} for g, c in ev["checkpoints"].items()},
                   checkpoint_champions={str(g): c["champion"] for g, c in ev["checkpoints"].items()},
                   plant_held=C.slim(C.competence(role, *_pt(ph, env, hs, plant, device))),
                   curve_summary=[{k: c[k] for k in ("gen", "max_acc", "mean_acc", "best_acc")} for c in ev["curve"]])
        npz = {"pop": ev["pop"].astype(np.int16)}
    else:
        sseed = X.search_seed(cell["cell_key"], idx)
        sp = SearchSpec(**BASE_SPEC)
        hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
        op, start = job["arm"].split("_")
        init = np.asarray(cell["stones"][str(idx)]["genome"], dtype=np.int64) if start == "STEP" else None
        mut = X.mutate_opb if op == "OPB" else B.mutate_tagged
        ev = evolve(ph, env, sseed, sp, device, mut, init=init, ckpts=(35,), held=hs, role=role)
        ck = ev["checkpoints"][36]
        progs = [plant] + ([init] if init is not None else [])
        pt, ep = C.eval_programs(ph, env, hs, progs, device=device)
        he = {"plant": C.slim(C.competence(role, pt[0], ep))}
        if init is not None:
            he["injected"] = C.slim(C.competence(role, pt[1], ep))
        success = ck["status"] == "TRUE"
        share = ck["lineage_share"] if init is not None else None
        attribution = None if not success else ("BACKGROUND_SUCCESS" if share is None or share < B.LINEAGE_MIN_SHARE
                                                 else "STEP_LINEAGE_SUCCESS")
        row.update(kind="c2c_search", operator=op, start=start, search_seed=sseed, success=success,
                   attribution=attribution, champ_lineage_share=share, competence=ck["competence"],
                   champion=ck["champion"], champ_acc=ck["competence"]["all"]["mean"], held_eval=he,
                   curve=ev["curve"], final_n_lineage=ev["curve"][-1].get("n_lineage"),
                   lineage_extinct_gen=next((c["gen"] for c in ev["curve"] if c.get("n_lineage") == 0), None))
        npz = {"pop": ev["pop"].astype(np.int16), "tags": ev["tags"], "parents": ev["parents"]}
    trainw = set()
    for gen in range(sp.gens):
        trainw.update(assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M))
    row["held_train_overlap"] = len(set(hs) & trainw)
    row["wall_s"] = round(time.time() - t0, 2)
    return row, npz


def _pt(ph, env, hs, g, device):
    pt, ep = C.eval_programs(ph, env, hs, [g], device=device)
    return pt[0], ep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("outdir"); ap.add_argument("worker", type=int)
    ap.add_argument("--deadline-utc", default=None); ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text())
    cells = {c["cell_id"]: c for c in plan["cells"]}
    c2b_ref = load_c2b_b4x(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2b"))
    out = pathlib.Path(a.outdir); (out / "claims").mkdir(parents=True, exist_ok=True); (out / "pops").mkdir(exist_ok=True)
    deadline = dt.datetime.fromisoformat(a.deadline_utc) if a.deadline_utc else None
    rows = out / f"rows_w{a.worker}.jsonl"
    n = 0
    for job in plan["jobs"]:
        if deadline and dt.datetime.now(dt.timezone.utc) >= deadline:
            print("DEADLINE: no new jobs", flush=True); break
        if a.max_jobs is not None and n >= a.max_jobs:
            break
        fid = job["job_id"].replace("|", "__")
        try:
            fd = os.open(str(out / "claims" / (fid + ".claim")), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.write(fd, json.dumps({"worker": a.worker, "utc": dt.datetime.now(dt.timezone.utc).isoformat()}).encode())
        os.close(fd)
        row, npz = run_job(job, cells[job["cell_id"]], a.device, c2b_ref)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(rows, "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        tag = row.get("attribution") or row.get("first_competent_gen") or ("ok" if row.get("prefix_gate", {}).get("status") == "PASS" else "fail")
        print(job["job_id"], tag, row.get("prefix_gate", {}).get("status", ""), row["wall_s"], flush=True)


if __name__ == "__main__":
    main()
