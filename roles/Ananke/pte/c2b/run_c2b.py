"""PTE-C2B search runner (GPU). One job = one search (cell, arm, seed index).

usage: python run_c2b.py PLAN.json OUTDIR WORKER_ID [--deadline-utc ISO] [--max-jobs N] [--device cuda]

Arms (all BASE settings of C2A: pop 96, M 8, elite 4, trunc .25, p_field .04, p_instr .15, p_swap .10,
p_cross .30, w_contrast .10, w_any .02, M_final 16; held 128 worlds):
  BRK1 / BRK2  the plan's pre-qualified broken start (exactly k edits, FALSE on C2B_BROKEN_QUAL) at gen-0 index 0
  STEP         the plan's pre-qualified stepping stone at gen-0 index 0
  B4X          no injection; gens 144; checkpoints at gen 36/72/108/144
search_seed = C2A's search_seed(cell_key, idx) for idx 0..7: every arm shares C2A BASE's gen-0 population and
training-world stream at that index (common random numbers); seeded arms differ only at index 0.
B4X prefix gate: the population after generation 36 (index 35) and its gen-36 champion (C2A's FINAL_NS
re-evaluation) must equal the C2A BASE search at the same (cell, idx) exactly; the comparison is recorded per job.
Per generation: max/mean accuracy, and for seeded arms the lineage counts and the best lineage member's training
accuracy. Saved per job: final population, line tags, champion index, parent indices per generation.
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
import c2b_common as B  # noqa: E402
C = B.C
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS, SearchSpec, random_genomes  # noqa: E402

BASE_SPEC = dict(pop=96, M=8, gens=36, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)


def arm_spec(arm):
    return SearchSpec(**dict(BASE_SPEC, gens=144 if arm == "B4X" else 36))


def champion_at(ph, env, pop, sseed, gi, sp, device):
    """C2A's champion rule: argmax final training accuracy on M_final worlds. Gen-36 uses C2A's exact key."""
    key = C.H_int(sseed, FINAL_NS) if gi == 35 else C.H_int(sseed, FINAL_NS, B.FINAL_CKPT_KEY, gi + 1)
    fs = assays.world_seeds(key, sp.M_final)
    rf = assays.evaluate(ph, pop, env, fs, device=device)
    return int(np.argmax(rf.mean())), rf.mean(), fs


def evolve_c2b(ph, env, sseed, sp, device, init=None, ckpts=(), held=None, role=None):
    g = np.random.default_rng(sseed)
    pop = random_genomes(g, sp.pop, ph)
    tags = np.zeros(pop.shape[:3], dtype=bool)
    if init is not None:
        pop[0] = init
        tags[0] = True
    curve, parents_log, checkpoints, snap35 = [], [], {}, None
    train_seeds = set()
    for gen in range(sp.gens):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        train_seeds.update(seeds)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any
        order = np.argsort(-f, kind="stable")
        share = tags.mean((1, 2))
        lin = share >= B.LINEAGE_MIN_SHARE
        rec = {"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]),
               "max_acc": float(acc.max()), "mean_acc": float(acc.mean())}
        if init is not None:
            rec.update(n_lineage=int(lin.sum()), n_any_tag=int((share > 0).sum()),
                       lineage_max_acc=float(acc[lin].max()) if lin.any() else None,
                       lineage_best_rank=int(np.flatnonzero(lin[order])[0]) if lin.any() else None)
        curve.append(rec)
        if gen in ckpts:
            ci, fa, fs = champion_at(ph, env, pop, sseed, gen, sp, device)
            pt, ep = C.eval_programs(ph, env, held, [pop[ci]], device=device)
            cc = C.competence(role, pt[0], ep)
            checkpoints[gen + 1] = {"champion": pop[ci].tolist(), "champ_index": ci, "status": cc["status"],
                                    "competence": C.slim(cc), "champ_train_final": float(fa[ci])}
            train_seeds.update(fs)
            if gen == 35:
                snap35 = pop.copy()
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        par, ptag = pop[order[:k]], tags[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        ntag = [tags[order[i]] for i in range(sp.elite)]
        plog = [[int(order[i]), -1, 1] for i in range(sp.elite)]           # [parent_a, parent_b, elite]
        while len(nxt) < sp.pop:
            ia = int(g.integers(k))
            a, ta, ib = par[ia], ptag[ia], -1
            if g.random() < sp.p_cross:
                ib = int(g.integers(k))
                a, ta = B.crossover_tagged(g, a, par[ib], ta, ptag[ib])
            c, t = B.mutate_tagged(g, a, ta, sp)
            nxt.append(c); ntag.append(t)
            plog.append([int(order[ia]), int(order[ib]) if ib >= 0 else -1, 0])
        parents_log.append(plog)
        pop, tags = np.stack(nxt), np.stack(ntag)
    return {"pop": pop, "tags": tags, "curve": curve, "parents": np.asarray(parents_log, dtype=np.int16),
            "checkpoints": checkpoints, "snap35": snap35, "train_seeds": train_seeds}


def run_job(job, cell, device, c2a_pops):
    ph = C.Physics.from_dict(cell["physics"]).validate()
    env = envs.EnvSpec(**cell["env"])
    role, arm, idx = cell["role"], job["arm"], job["idx"]
    plant = np.asarray(cell["plant_genome"], dtype=np.int64)
    sseed = C.search_seed(cell["cell_key"], idx)
    sp = arm_spec(arm)
    hseeds = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    init = None
    if arm in ("BRK1", "BRK2"):
        init = np.asarray(cell["brk"][arm][str(idx)]["genome"], dtype=np.int64)
    elif arm == "STEP":
        init = np.asarray(cell["step"]["genome"], dtype=np.int64)
    t0 = time.time()
    ck = B.B4X_CHECKPOINTS if arm == "B4X" else (sp.gens - 1,)
    ev = evolve_c2b(ph, env, sseed, sp, device, init=init, ckpts=ck, held=hseeds, role=role)
    final = ev["checkpoints"][sp.gens]
    ci = final["champ_index"]
    champ = ev["pop"][ci]
    # plant, injected start, and best lineage member on the same held worlds
    progs, names = [plant], ["plant"]
    if init is not None:
        progs.append(init); names.append("injected")
        sh = ev["tags"].mean((1, 2))
        lin = np.flatnonzero(sh >= B.LINEAGE_MIN_SHARE)
        best_lin = None
        if lin.size:
            # best lineage member by the final-training accuracy used for the champion
            rf_key = C.H_int(sseed, FINAL_NS) if sp.gens == 36 else C.H_int(sseed, FINAL_NS, B.FINAL_CKPT_KEY, sp.gens)
            rf = assays.evaluate(ph, ev["pop"][lin], env, assays.world_seeds(rf_key, sp.M_final), device=device)
            best_lin = int(lin[int(np.argmax(rf.mean()))])
            progs.append(ev["pop"][best_lin]); names.append("best_lineage_member")
    pt, ep = C.eval_programs(ph, env, hseeds, progs, device=device)
    ev_named = {n: C.slim(C.competence(role, pt[i], ep)) for i, n in enumerate(names)}
    share = float(ev["tags"][ci].mean())
    success = final["status"] == "TRUE"
    row = {"kind": "c2b_search", "job_id": job["job_id"], "cell_id": cell["cell_id"], "family": cell["family"],
           "role": role, "arm": arm, "idx": idx, "search_seed": sseed, "search": sp.to_dict(),
           "success": success, "competence": final["competence"], "champion": champ.tolist(),
           "champ_lineage_share": share if init is not None else None,
           "attribution": B.attribute(success, share if init is not None else None, arm),
           "held_eval": ev_named, "plant_acc": ev_named["plant"]["all"]["mean"],
           "champ_acc": final["competence"]["all"]["mean"],
           "checkpoints": {str(k): {kk: v for kk, v in c.items() if kk != "champion"} for k, c in ev["checkpoints"].items()},
           "checkpoint_champions": {str(k): c["champion"] for k, c in ev["checkpoints"].items()},
           "held_train_overlap": len(set(hseeds) & ev["train_seeds"]),
           "curve": ev["curve"], "wall_s": round(time.time() - t0, 2), "device": device,
           "host": socket.gethostname()}
    if init is not None:
        row["injected_id"] = f"{cell['cell_id']}|{arm}|{idx:02d}|init"
        row["injected_edits"] = cell["brk"][arm][str(idx)]["edits"] if arm.startswith("BRK") else None
        lin_curve = [c.get("lineage_max_acc") for c in ev["curve"]]
        row["lineage_extinct_gen"] = next((c["gen"] for c in ev["curve"] if c["n_lineage"] == 0), None)
        row["final_n_lineage"] = ev["curve"][-1]["n_lineage"]
        row["best_lineage_member_index"] = best_lin
    if arm == "B4X":
        cks = {k: ev["checkpoints"][k]["status"] for k in (36, 72, 108, 144)}
        row["checkpoint_status"] = cks
        row["first_competent_gen"] = next((k for k in (36, 72, 108, 144) if cks[k] == "TRUE"), None)
        row["new_after_36"] = cks[36] != "TRUE" and any(cks[k] == "TRUE" for k in (72, 108, 144))
        pref = c2a_pops.get((cell["cell_id"], idx))
        if pref is None:
            row["prefix_gate"] = {"status": "NO_C2A_REFERENCE"}
        else:
            pop_eq = bool(np.array_equal(ev["snap35"].astype(np.int16), pref["pop"]))
            ch_eq = bool(np.array_equal(np.asarray(ev["checkpoints"][36]["champion"]), np.asarray(pref["champion"])))
            curve_eq = all(abs(a["max_acc"] - b["max_acc"]) == 0 and abs(a["best_acc"] - b["best_acc"]) == 0
                           for a, b in zip(ev["curve"][:36], pref["curve"]))
            st36 = ev["checkpoints"][36]["status"] == pref["status"]
            row["prefix_gate"] = {"pop35_equal": pop_eq, "champion36_equal": ch_eq, "curve_acc_equal": curve_eq,
                                  "status36_equal": st36,
                                  "status": "PASS" if (pop_eq and ch_eq and curve_eq and st36) else "FAIL"}
    npz = {"pop": ev["pop"].astype(np.int16), "tags": ev["tags"], "champ_index": np.int32(ci),
           "parents": ev["parents"]}
    return row, npz


def load_c2a_reference(c2a_dir):
    """C2A BASE final populations (gen-36) and rows, keyed by (cell_id, idx)."""
    import glob
    import tarfile
    ref = {}
    rows = {}
    import gzip
    for l in gzip.open(os.path.join(c2a_dir, "production", "rows_C2A.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r["arm"] == "BASE":
            rows[(r["cell_id"], r["idx"])] = r
    tf = tarfile.open(os.path.join(c2a_dir, "production", "pops_C2A.tar"))
    import io
    for (cid, idx), r in rows.items():
        name = "pops/" + f"{cid}|BASE|{idx:02d}".replace("|", "__") + ".npz"
        z = np.load(io.BytesIO(tf.extractfile(name).read()))
        ref[(cid, idx)] = {"pop": z["pop"], "champion": r["champion"], "curve": r["curve"],
                           "status": r["competence"]["status"]}
    return ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("outdir"); ap.add_argument("worker", type=int)
    ap.add_argument("--deadline-utc", default=None); ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text())
    cells = {c["cell_id"]: c for c in plan["cells"]}
    c2a_pops = load_c2a_reference(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a"))
    out = pathlib.Path(a.outdir); (out / "claims").mkdir(parents=True, exist_ok=True); (out / "pops").mkdir(exist_ok=True)
    deadline = dt.datetime.fromisoformat(a.deadline_utc) if a.deadline_utc else None
    rows = out / f"rows_w{a.worker}.jsonl"
    hb = out / f"heartbeat_w{a.worker}.json"
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
        hb.write_text(json.dumps({"worker": a.worker, "job": job["job_id"], "done": n,
                                  "start_utc": dt.datetime.now(dt.timezone.utc).isoformat()}))
        row, npz = run_job(job, cells[job["cell_id"]], a.device, c2a_pops)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(rows, "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        print(job["job_id"], row["attribution"] or "fail", round(row["champ_acc"], 3),
              row.get("prefix_gate", {}).get("status", ""), row["wall_s"], flush=True)
    hb.write_text(json.dumps({"worker": a.worker, "finished": True, "done": n,
                              "utc": dt.datetime.now(dt.timezone.utc).isoformat()}))


if __name__ == "__main__":
    main()
