"""PTE-C3S runner (GPU): selector-resolution test on the C2C graded FLIP stones.

usage: python run_c3s.py PLAN.json OUTDIR WORKER [--deadline-utc ISO] [--max-jobs N] [--device cuda]

Arms (all: frozen operator OP0, 36 generations, pop 96, BASE settings; stone at gen-0 index 0; search_seed = the C2C
seed for (cell, idx), so every arm shares C2C's gen-0 population and training-world stream (prefix-consistent in M)):
  S8   M 8,  w_contrast .10, w_any .02   (= C2C OP0_STEP exactly; replay gate against the C2C row)
  S32  M 32, w_contrast .10, w_any .02
  W8   M 8,  w_contrast 0,   w_any 0
  W32  M 32, w_contrast 0,   w_any 0
Final evaluation on the C2C held worlds (128, H(search_seed, HELD_NS)) with the frozen FLIP ruler:
  champion (C2A rule), the injected stone, and BL = the final-population lineage member (share >= .5) with the highest
  MONITOR-world B (selection on monitor worlds only; held worlds never select).
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import os
import pathlib
import socket
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c3_common as K  # noqa: E402
C = K.C; X = K.X; B = K.B
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import HELD_NS, SearchSpec  # noqa: E402

BASE_SPEC = dict(pop=96, M=8, gens=36, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)
ARMS = {"S8": dict(M=8), "S32": dict(M=32), "W8": dict(M=8, w_contrast=0.0, w_any=0.0),
        "W32": dict(M=32, w_contrast=0.0, w_any=0.0)}


def c2c_reference(pte_dir):
    ref = {}
    for l in gzip.open(os.path.join(pte_dir, "c2c", "production", "rows_C2C.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r.get("arm") == "OP0_STEP":
            ref[(r["cell_id"], r["idx"])] = {"champion": r["champion"], "status": r["competence"]["status"]}
    return ref


def ev(ph, env, seeds, progs, device):
    pt, ep = C.eval_programs(ph, env, seeds, progs, device=device)
    return [C.competence("FLIP", pt[i], ep) for i in range(len(progs))]


def run_job(job, cell, device, ref):
    ph = C.Physics.from_dict(cell["physics"]).validate(); env = envs.EnvSpec(**cell["env"])
    idx = job["idx"]; arm = job["arm"]
    sseed = X.search_seed(cell["cell_key"], idx)
    sp = SearchSpec(**dict(BASE_SPEC, **ARMS[arm]))
    stone = np.asarray(cell["stones"][str(idx)]["genome"], dtype=np.int64)
    mon = K.monitor_seeds(cell["cell_key"])
    t0 = time.time()
    e = K.evolve_c3(ph, env, sseed, sp, device, init=stone, mon_seeds=mon)
    pop, tags = e["pop"], e["tags"]
    share = tags.mean((1, 2)); lin = np.flatnonzero(share >= B.LINEAGE_MIN_SHARE)
    bl = None
    if lin.size:
        uniq, first = np.unique(pop[lin].reshape(lin.size, -1), axis=0, return_index=True)
        cand = lin[first]
        res = ev(ph, env, mon, [pop[i] for i in cand], device)
        bl = int(cand[int(np.argmax([r_["B"]["mean"] for r_ in res]))])
    hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    ci = e["champ_index"]
    progs = [pop[ci], stone] + ([pop[bl]] if bl is not None else [])
    hr = ev(ph, env, hs, progs, device)
    row = {"kind": "c3s_search", "job_id": job["job_id"], "cell_id": cell["cell_id"], "idx": idx, "arm": arm,
           "search_seed": sseed, "search": sp.to_dict(),
           "champion": pop[ci].tolist(), "champ_share": float(share[ci]),
           "champ_held": C.slim(hr[0]), "stone_held": C.slim(hr[1]),
           "bl_index": bl, "bl_share": float(share[bl]) if bl is not None else None,
           "bl_genome": pop[bl].tolist() if bl is not None else None,
           "bl_held": C.slim(hr[2]) if bl is not None else None,
           "final_n_lineage": int(lin.size),
           "lineage_extinct_gen": next((c["gen"] for c in e["curve"] if c["n_lineage"] == 0), None),
           "curve": e["curve"], "wall_s": round(time.time() - t0, 2), "device": device, "host": socket.gethostname()}
    if arm == "S8":
        rf = ref.get((cell["cell_id"], idx))
        row["replay_gate"] = None if rf is None else {
            "champion_equal": bool(np.array_equal(pop[ci], np.asarray(rf["champion"]))),
            "status_equal": hr[0]["status"] == rf["status"]}
    trainw = set()
    for gen in range(sp.gens):
        trainw.update(assays.world_seeds(C.H_int(sseed, K.TRAIN_NS, gen), sp.M))
    row["held_train_overlap"] = len(set(hs) & trainw)
    row["held_monitor_overlap"] = len(set(hs) & set(mon))
    return row, {"pop": pop.astype(np.int16), "tags": tags}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("outdir"); ap.add_argument("worker", type=int)
    ap.add_argument("--deadline-utc", default=None); ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text())
    cells = {c["cell_id"]: c for c in plan["cells"]}
    ref = c2c_reference(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
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
        row, npz = run_job(job, cells[job["cell_id"]], a.device, ref)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(out / f"rows_w{a.worker}.jsonl", "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        print(job["job_id"], row["champ_held"]["status"], (row["bl_held"] or {}).get("status"), row.get("replay_gate"),
              row["wall_s"], flush=True)


if __name__ == "__main__":
    main()
