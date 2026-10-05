"""PTE-C2A Flight 1 GPU known-answer gates (operator order s14 items 6-8).

G6  reproduce historical C1 results bit-exactly: C1 champions' held accuracy recomputed on GPU and CPU equals
    the recorded value (6f82f9c7 FLIP@d9cc .4791666667 plus 3 RELAY-1h d9cc d3 delta8 SIGNAL champions).
G7  CPU/GPU agreement: assays.evaluate accuracy arrays (training path) and c2a eval_programs per-trial arrays
    are EQUAL on CPU and GPU for the same programs and worlds (integer engine; float telemetry excluded).
G8  PSEED pilot on a cell that never enters production (C1 FLIP@d9cc, 6f82f9c7, P-FLIP): the plant is present
    intact at gen 0 index 0, it scores as the plant on the gen-0 worlds, and after 2 generations it is still
    present at rank 0 (W2-D F4 pattern).
usage: python flight1_gates.py OUT.json
"""
import gzip
import json
import sys
import time

import numpy as np

import c2a_common as C
import run as R
from prometheus.ananke import assays, envs, search

ROWS = C.ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def c1_rows():
    return [json.loads(l) for l in gzip.open(ROWS, "rt")]


def held_acc(r, device):
    ph = C.Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    hs = assays.world_seeds(C.H_int(r["search_seed"], search.HELD_NS), sp.M_held)
    g = np.asarray(r["result"]["champion"])
    res = assays.evaluate(ph, g[None], env, hs, device=device)
    return float(res.pair_acc()[0].mean()), res.acc


def main(out):
    t0 = time.time()
    R1 = c1_rows()
    E = [r for r in R1 if r["kind"] == "evolve"]
    flip = next(r for r in E if r["cell_id"] == "6f82f9c7d51bcef1")
    relay = [r for r in E if r["env"]["family"] == "RELAY" and r["env"]["d"] == 3 and r["env"]["delta"] == 8
             and C.Physics.from_dict(r["physics"]).digest().startswith("d9cc") and r["labels"].get("SIGNAL")][:3]
    rep = {"G6": [], "G7": {}, "G8": {}}
    for r in [flip] + relay:
        a_gpu, acc_gpu = held_acc(r, "cuda")
        a_cpu, acc_cpu = held_acc(r, "cpu")
        rec = r["result"]["held"]["acc"]
        rep["G6"].append({"cell_id": r["cell_id"], "recorded": rec, "gpu": a_gpu, "cpu": a_cpu,
                          "exact": bool(a_gpu == rec and a_cpu == rec), "cpu_gpu_equal": bool(np.array_equal(acc_gpu, acc_cpu))})
    # G7: training-path evaluate on a mixed population (random + champions), and per-trial eval_programs
    ph = C.Physics.from_dict(flip["physics"]).validate()
    env = envs.EnvSpec(**flip["env"])
    g = np.random.default_rng(7)
    pop = search.random_genomes(g, 16, ph)
    pop[0] = C.p_flip(ph); pop[1] = np.asarray(flip["result"]["champion"])
    seeds = assays.world_seeds(C.H_int(C.C2A_NS, C.PILOT_KEY, 7), 8)
    rg = assays.evaluate(ph, pop, env, seeds, device="cuda")
    rc = assays.evaluate(ph, pop, env, seeds, device="cpu")
    pg, _ = C.eval_programs(ph, env, seeds, [pop[0], pop[1], pop[2]], device="cuda")
    pc, _ = C.eval_programs(ph, env, seeds, [pop[0], pop[1], pop[2]], device="cpu")
    rep["G7"] = {"evaluate_acc_equal": bool(np.array_equal(rg.acc, rc.acc)),
                 "sens_act_maxabs": float(np.abs(rg.sens_act - rc.sens_act).max()),
                 "sens_any_maxabs": float(np.abs(rg.sens_any - rc.sens_any).max()),
                 "eval_programs_equal": bool(np.array_equal(pg, pc)),
                 "plant_acc_evaluate_vs_eval_programs": [float(rg.acc[0].mean()), float(pg[0].mean())]}
    # G8: PSEED pilot, 2 generations on GPU
    plant = C.p_flip(ph)
    sp = R.arm_spec("BASE")
    import dataclasses
    sp2 = dataclasses.replace(sp, gens=3)          # gens 0,1,2 evaluated = 2 generations of selection
    sseed = C.H_int(C.C2A_NS, C.PILOT_KEY, 1)
    gq = np.random.default_rng(sseed)
    pop0 = search.random_genomes(gq, sp.pop, ph); pop0[0] = plant
    s0 = assays.world_seeds(C.H_int(sseed, search.TRAIN_NS, 0), sp.M)
    r0 = assays.evaluate(ph, pop0, env, s0, device="cuda")
    rp = assays.evaluate(ph, plant[None], env, s0, device="cuda")
    ev = R.evolve_c2a(ph, env, sseed, sp2, "cuda", init=plant, plant=plant)
    rep["G8"] = {"plant_intact_at_gen0_idx0": bool(np.array_equal(pop0[0], plant)),
                 "gen0_idx0_acc_equals_plant_alone": bool(np.array_equal(r0.acc[0], rp.acc[0])),
                 "gen0_plant_acc": float(r0.acc[0].mean()), "gen0_pop_max_acc": float(r0.mean().max()),
                 "curve": ev["curve"],
                 "rank0_after_2_generations": ev["curve"][-1]["plant_best_rank"] == 0,
                 "n_exact_plant_final_gen": ev["curve"][-1]["n_exact_plant"]}
    rep["pass"] = {"G6": all(x["exact"] and x["cpu_gpu_equal"] for x in rep["G6"]),
                   "G7": rep["G7"]["evaluate_acc_equal"] and rep["G7"]["eval_programs_equal"],
                   "G8": rep["G8"]["plant_intact_at_gen0_idx0"] and rep["G8"]["gen0_idx0_acc_equals_plant_alone"]
                   and rep["G8"]["rank0_after_2_generations"]}
    rep["wall_s"] = round(time.time() - t0, 1)
    C.jdump(out, rep)
    print(json.dumps(rep["pass"]), rep["wall_s"])
    for x in rep["G6"]:
        print(x)
    print({k: v for k, v in rep["G7"].items()})
    print({k: v for k, v in rep["G8"].items() if k != "curve"})


if __name__ == "__main__":
    main(sys.argv[1])
