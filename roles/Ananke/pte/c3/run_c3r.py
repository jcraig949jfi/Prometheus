"""PTE-C3R runner (GPU): FLIP representation factorial, staged budget.

usage: python run_c3r.py PLAN.json OUTDIR WORKER [--deadline-utc ISO] [--max-jobs N] [--device cuda]

Job kinds:
  stage 1 (job["stage"] == 1): fresh search to generation 36 (1x); checkpoint champion at gen 36 scored on held worlds;
          the full GA state (population, lineage/dup tags, numpy bit-generator state, curve, checkpoints) is saved to
          OUTDIR/state/<fid>.npz + .json so that stage 2 continues the SAME trajectory.
  stage 2 (job["stage"] == 2): load the stage-1 state from job["state_dir"] and continue to generation 144 (4x);
          checkpoint champions at gens 72, 108, 144.
Selector: the plan's "selector" block (M and shaping) applies to every arm (C3S decision rule).
Held worlds: 128, H(search_seed, HELD_NS); monitor: c3_common monitor worlds, the generation best every 6 gens.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import socket
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c3r_common as R  # noqa: E402
C = R.C; K = R.K
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import HELD_NS, TRAIN_NS, SearchSpec  # noqa: E402

BASE_SPEC = dict(pop=96, M=8, gens=144, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)


def save_state(path, st):
    np.savez_compressed(path + ".npz", pop=st["pop"].astype(np.int16), tags=st["tags"], dup=st["dup"])
    json.dump({"rng_state": st["rng_state"], "next_gen": st["next_gen"], "curve": st["curve"],
               "checkpoints": {str(k): v for k, v in st["checkpoints"].items()}}, open(path + ".json", "w"),
              default=C._jd)


def load_state(path):
    z = np.load(path + ".npz"); j = json.load(open(path + ".json"))
    return {"pop": z["pop"].astype(np.int64), "tags": z["tags"], "dup": z["dup"], "rng_state": j["rng_state"],
            "next_gen": j["next_gen"], "curve": j["curve"], "checkpoints": {int(k): v for k, v in j["checkpoints"].items()}}


def run_job(job, cell, sel, device, out):
    ph0 = C.Physics.from_dict(cell["physics"]).validate(); env = envs.EnvSpec(**cell["env"])
    rep, idx = job["rep"], job["idx"]
    ph = R.rep_physics(ph0, rep)
    sseed = R.search_seed(cell["cell_key"], rep, idx)
    sp = SearchSpec(**dict(BASE_SPEC, **sel))
    hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    mon = K.monitor_seeds(cell["cell_key"])
    fid = f"{cell['cell_id']}__{rep}__{idx:02d}"
    t0 = time.time()
    if job["stage"] == 1:
        st = R.evolve_staged(ph, env, sseed, sp, device, rep, gens_to=36, ckpts=(35,), held=hs, mon_seeds=mon)
        os.makedirs(out / "state", exist_ok=True)
        save_state(str(out / "state" / fid), st)
    else:
        prev = load_state(os.path.join(job["state_dir"], fid))
        assert prev["next_gen"] == 36
        st = R.evolve_staged(ph, env, sseed, sp, device, rep, gens_to=144, state=prev, ckpts=(71, 107, 143), held=hs,
                             mon_seeds=mon)
    cks = {g: st["checkpoints"][g]["status"] for g in sorted(st["checkpoints"])}
    plant = np.asarray(cell["rep_plants"][rep], dtype=np.int64)
    pt, ep = C.eval_programs(ph, env, hs, [plant], device=device)
    trainw = set()
    for gen in range(st["next_gen"]):
        trainw.update(assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M))
    row = {"kind": "c3r_search", "job_id": job["job_id"], "cell_id": cell["cell_id"], "rep": rep, "idx": idx,
           "stage": job["stage"], "search_seed": sseed, "search": sp.to_dict(), "rep_spec": R.REPS[rep],
           "checkpoint_status": {str(g): s for g, s in cks.items()},
           "checkpoints": {str(g): {k: v for k, v in c.items() if k != "champion"} for g, c in st["checkpoints"].items()},
           "checkpoint_champions": {str(g): c["champion"] for g, c in st["checkpoints"].items()},
           "first_competent_gen": next((g for g in sorted(cks) if cks[g] == "TRUE"), None),
           "plant_held": C.slim(C.competence("FLIP", pt[0], ep)),
           "held_train_overlap": len(set(hs) & trainw), "held_monitor_overlap": len(set(hs) & set(mon)),
           "curve": st["curve"][-36:] if job["stage"] == 2 else st["curve"],
           "wall_s": round(time.time() - t0, 2), "device": device, "host": socket.gethostname()}
    return row, {"pop": st["pop"].astype(np.int16), "tags": st["tags"], "dup": st["dup"]}


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
        row, npz = run_job(job, cells[job["cell_id"]], plan["selector"], a.device, out)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(out / f"rows_w{a.worker}.jsonl", "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        print(job["job_id"], row["checkpoint_status"], row["wall_s"], flush=True)


if __name__ == "__main__":
    main()
