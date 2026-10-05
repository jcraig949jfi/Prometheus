"""PTE-C2A search runner (GPU). One job = one search (cell, arm, seed index).

usage: python run.py PLAN.json OUTDIR WORKER_ID [--deadline-utc ISO] [--max-jobs N]

The loop is search.evolve's loop, line for line (random_genomes / mutate / crossover are imported from
prometheus.ananke.search, unchanged), with these declared additions:
  * init: a genome written at gen-0 index 0 AFTER the population is drawn (PSEED: the plant; KSEED: the plant
    perturbed at k fields). Every other member and every RNG draw is identical to BASE at the same seed index.
  * per-generation telemetry: max/mean/var accuracy, best fitness, shaping share of the top quartile, and
    (seeded arms and all arms, for the basin descriptor) the plant's exact-copy count, best rank and the
    minimum instruction distance of any member to the plant.
  * the final population (genomes + final training accuracy) is saved for audit.
  * held evaluation: 128 worlds (64 pairs) under H(search_seed, HELD_NS); champion AND plant are scored on the
    same held worlds with the competence-class ruler (c2a_common.competence).
Arms: BASE (C1 protocol), W0 (w_contrast = w_any = 0), M32 (M = 32), PSEED (plant at index 0),
      KSEED-k (plant with k distinct fields resampled from the GA's own field distribution, at index 0).
Jobs are claimed dynamically (O_EXCL claim files) in plan order; a worker starts no job after the deadline.
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
import c2a_common as C  # noqa: E402
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import (FINAL_NS, HELD_NS, TRAIN_NS, SearchSpec, crossover,  # noqa: E402
                                      mutate, random_genomes)

ROLE = {"RELAY-mh": "RELAY-mh", "FLIP": "FLIP", "RELAY-1h": "RELAY-1h"}
BASE_SPEC = dict(pop=96, M=8, gens=36, elite=4, trunc=0.25, p_field=0.04, p_instr=0.15, p_swap=0.10,
                 p_cross=0.30, M_final=16, M_held=64, w_contrast=0.10, w_any=0.02)   # C1 / C2 draft s6.1


def arm_spec(arm: str) -> SearchSpec:
    s = dict(BASE_SPEC)
    if arm == "W0":
        s.update(w_contrast=0.0, w_any=0.0)
    elif arm == "M32":
        s.update(M=32)
    return SearchSpec(**s)


def kseed_genome(plant: np.ndarray, k: int, cell_key: int, idx: int):
    """Resample k DISTINCT (rule, line, field) positions with search._rand_instr's per-field distribution
    (fields 0-3 uniform 0..255, field 4 uniform -128..127); a draw equal to the current value is redrawn."""
    g = np.random.default_rng(C.H_int(C.C2A_NS, C.KSEED_KEY, cell_key, k, idx))
    x = plant.copy()
    R, L, F = x.shape
    pos = g.choice(R * L * F, size=k, replace=False)
    out = []
    for p in pos:
        r, rem = divmod(int(p), L * F)
        line, f = divmod(rem, F)
        old = int(x[r, line, f])
        while True:
            v = int(g.integers(-128, 128)) if f == 4 else int(g.integers(0, 256))
            if v != old:
                break
        x[r, line, f] = v
        out.append([r, line, f, old, v])
    return x, out


def line_dist(pop: np.ndarray, plant: np.ndarray) -> np.ndarray:
    """Number of instructions (rule, line) that differ from the plant, per member."""
    return (pop != plant[None]).any(-1).sum((1, 2))


def evolve_c2a(ph, env, sseed: int, sp: SearchSpec, device: str, init=None, plant=None):
    t_start = time.time()
    g = np.random.default_rng(sseed)
    pop = random_genomes(g, sp.pop, ph)
    if init is not None:
        pop[0] = init
    curve = []
    all_train_seeds = set()
    for gen in range(sp.gens):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        all_train_seeds.update(seeds)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        acc = r.mean()
        bc = sp.w_contrast * np.maximum(r.sens_act, 0)
        ba = sp.w_any * r.sens_any
        f = acc + bc + ba
        order = np.argsort(-f, kind="stable")
        q = order[: max(1, sp.pop // 4)]
        rec = {"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]),
               "max_acc": float(acc.max()), "mean_acc": float(acc.mean()), "var_acc": float(acc.var()),
               "bonus_share_topq": float(np.mean((f[q] - acc[q]) / np.maximum(f[q], 1e-9))),
               "best_bonus_contrast": float(bc[order[0]]), "best_bonus_any": float(ba[order[0]])}
        if plant is not None:
            ld = line_dist(pop, plant)
            ex = np.flatnonzero(ld == 0)
            rank = np.empty(sp.pop, int); rank[order] = np.arange(sp.pop)
            rec.update(n_exact_plant=int(ex.size), plant_best_rank=int(rank[ex].min()) if ex.size else None,
                       plant_acc=float(acc[ex].max()) if ex.size else None, min_line_dist=int(ld.min()),
                       n_within_2=int((ld <= 2).sum()))
        curve.append(rec)
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        parents = pop[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        while len(nxt) < sp.pop:
            a = parents[g.integers(k)]
            if g.random() < sp.p_cross:
                a = crossover(g, a, parents[g.integers(k)])
            nxt.append(mutate(g, a, sp))
        pop = np.stack(nxt)
    fseeds = assays.world_seeds(C.H_int(sseed, FINAL_NS), sp.M_final)
    rf = assays.evaluate(ph, pop, env, fseeds, device=device)
    ci = int(np.argmax(rf.mean()))            # champion by training ACCURACY only (as search.evolve)
    champ = pop[ci]
    hseeds = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    overlap = sorted((set(hseeds) & (all_train_seeds | set(fseeds))))
    return {"pop": pop, "final_train_acc": rf.mean(), "champ_index": ci, "champion": champ,
            "curve": curve, "hseeds": hseeds, "fseeds": fseeds, "held_train_overlap": len(overlap),
            "search_wall_s": time.time() - t_start}


def run_job(job: dict, cell: dict, device: str) -> tuple[dict, dict]:
    ph = C.Physics.from_dict(cell["physics"]).validate()
    env = envs.EnvSpec(**cell["env"])
    plant = np.asarray(cell["plant_genome"], dtype=np.int64)
    sseed = C.search_seed(cell["cell_key"], job["idx"])
    arm = job["arm"]
    sp = arm_spec("BASE" if arm.startswith(("PSEED", "KSEED")) else arm)
    init, kinfo = None, None
    if arm == "PSEED":
        init = plant.copy()
    elif arm.startswith("KSEED"):
        init, kinfo = kseed_genome(plant, int(arm.split("-")[1]), cell["cell_key"], job["idx"])
    t0 = time.time()
    ev = evolve_c2a(ph, env, sseed, sp, device, init=init, plant=plant)
    th = time.time()
    pt, ep = C.eval_programs(ph, env, ev["hseeds"], [ev["champion"], plant], device=device)
    role = ROLE[cell["role"]]
    cc = C.competence(role, pt[0], ep)
    cp = C.competence(role, pt[1], ep)
    t_held = time.time() - th
    champ_acc = cc["all"]["mean"]
    plant_acc = cp["all"]["mean"]
    last = ev["curve"][-1]
    ld_final = line_dist(ev["pop"], plant)
    row = {
        "kind": "c2a_search", "job_id": job["job_id"], "cell_id": cell["cell_id"], "family": cell["family"],
        "role": cell["role"], "arm": arm, "idx": job["idx"], "search_seed": sseed,
        "namespaces": {"train": ["H(search_seed, TRAIN_NS=0x7A1, gen)", sp.M],
                       "final": ["H(search_seed, FINAL_NS=0xF1A)", sp.M_final],
                       "held": ["H(search_seed, HELD_NS=0x4E1D)", C.M_HELD],
                       "held_train_overlap": ev["held_train_overlap"]},
        "search": sp.to_dict(), "init": ("plant" if arm == "PSEED" else ("kseed" if kinfo else None)),
        "kseed_edits": kinfo,
        "success": cc["status"] == "TRUE", "competence": C.slim(cc), "plant_held": C.slim(cp),
        "champ_acc": champ_acc, "plant_acc": plant_acc,
        "champ_plant_ratio": (champ_acc - 0.5) / (plant_acc - 0.5) if plant_acc > 0.5 else None,
        "selector_max_over_gens": max(c["max_acc"] for c in ev["curve"]),
        "champ_train_final": float(ev["final_train_acc"][ev["champ_index"]]),
        "pop_final_mean": float(np.mean(ev["final_train_acc"])),
        "fitness_last_gen_best": {"fit": last["best_fit"], "acc": last["best_acc"],
                                  "bonus_contrast": last["best_bonus_contrast"], "bonus_any": last["best_bonus_any"]},
        "bonus_share_topq_last": last["bonus_share_topq"],
        "basin": {"champ_line_dist": int((ev["champion"] != plant).any(-1).sum()),
                  "final_min_line_dist": int(ld_final.min()), "final_n_exact_plant": int((ld_final == 0).sum()),
                  "final_n_within_2": int((ld_final <= 2).sum()),
                  "ever_within_2": any((c.get("min_line_dist") or 99) <= 2 for c in ev["curve"])},
        "curve": ev["curve"],
        "champion": ev["champion"].tolist(),
        "wall": {"search_s": round(ev["search_wall_s"], 2), "held_s": round(t_held, 2),
                 "job_s": round(time.time() - t0, 2)},
        "device": device, "host": socket.gethostname(),
    }
    npz = {"pop": ev["pop"].astype(np.int16), "final_train_acc": ev["final_train_acc"].astype(np.float32),
           "champ_index": np.int32(ev["champ_index"])}
    return row, npz


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
    rows = out / f"rows_w{a.worker}.jsonl"
    hb = out / f"heartbeat_w{a.worker}.json"
    n = 0
    for job in plan["jobs"]:
        if deadline and dt.datetime.now(dt.timezone.utc) >= deadline:
            print("DEADLINE: no new jobs", flush=True); break
        if a.max_jobs is not None and n >= a.max_jobs:
            break
        fid = job["job_id"].replace("|", "__")          # Windows: no "|" in file names
        claim = out / "claims" / (fid + ".claim")
        try:
            fd = os.open(str(claim), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.write(fd, json.dumps({"worker": a.worker, "utc": dt.datetime.now(dt.timezone.utc).isoformat()}).encode())
        os.close(fd)
        hb.write_text(json.dumps({"worker": a.worker, "job": job["job_id"], "start_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "done": n}))
        row, npz = run_job(job, cells[job["cell_id"]], a.device)
        np.savez_compressed(out / "pops" / (fid + ".npz"), **npz)
        row["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(rows, "a") as fh:
            fh.write(json.dumps(row, default=C._jd) + "\n")
        n += 1
        print(job["job_id"], "success" if row["success"] else "fail", round(row["champ_acc"], 3),
              row["wall"]["job_s"], flush=True)
    hb.write_text(json.dumps({"worker": a.worker, "job": None, "finished": True, "done": n,
                              "utc": dt.datetime.now(dt.timezone.utc).isoformat()}))


if __name__ == "__main__":
    main()
