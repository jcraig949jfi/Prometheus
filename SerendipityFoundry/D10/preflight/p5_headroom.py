"""P5: does memory have headroom at all?

Three conditions at matched budget, matched population size and matched
number of injected genotypes (k):
  cold     - k fresh random genotypes (the no-memory arm N)
  sibling  - k genotypes from the SAME family as the eval task (an oracle
             upper bound on what perfect retrieval could deliver)
  foreign  - k genotypes from OTHER families (a matched-material control)

If sibling does not beat cold and foreign, no organization of any kind can
show an effect in this environment and the assay is not viable.
"""
import json, sys, time
sys.path.insert(0, "d10")
from lib.acquire import acquire
from lib.progtasks import sample_root, sample_member, task_from_program
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
K = 4
N_FAM, N_MEM, N_SEEDS = 5, 3, 4

def build(root_len, n_mut, n_train, gen_seed, max_cand=60):
    fams = []
    stats = {"roots_tried": 0, "roots_ok": 0, "members_ok": 0,
             "tasks_ok": 0, "tasks_shortcut_rejected": 0}
    for f in range(max_cand):
        if len(fams) >= N_FAM:
            break
        stats["roots_tried"] += 1
        root = sample_root(derive_seed(gen_seed, "root", f"#{f}"), root_len)
        if root is None: continue
        stats["roots_ok"] += 1
        mems, tasks = [], []
        for m in range(N_MEM):
            g = sample_member(root, derive_seed(gen_seed, "mem", f"#{f}", f"#{m}"), n_mut)
            if g is None: continue
            stats["members_ok"] += 1
            t = task_from_program(g, derive_seed(gen_seed, "case", f"#{f}", f"#{m}"),
                                  n_train, 20, f"f{f}", m)
            if t is None:
                stats["tasks_shortcut_rejected"] += 1
                continue
            stats["tasks_ok"] += 1
            mems.append(g); tasks.append(t)
        if len(tasks) >= 2:
            fams.append({"root": root, "members": mems, "tasks": tasks})
    return fams, stats

out = {}
t0 = time.perf_counter()
for root_len in (16, 24, 32):
    for n_mut in (2, 4):
        for n_train in (6,):
            fams, gstats = build(root_len, n_mut, n_train, 777)
            print(f"L{root_len}/m{n_mut}: families={len(fams)} {gstats}", flush=True)
            if len(fams) < 3:
                out[f"L{root_len}/m{n_mut}/n{n_train}"] = {"error": "insufficient families"}
                continue
            for B in (600, 2000):
                acc = {"cold": [0,0], "sibling": [0,0], "foreign": [0,0]}
                for fi, fam in enumerate(fams):
                    for ti, pt in enumerate(fam["tasks"]):
                        sib = [fam["members"][j] for j in range(len(fam["members"])) if j != ti]
                        sib = (sib + [fam["root"]])[:K]
                        other = [fams[(fi+1) % len(fams)]["members"][j % len(fams[(fi+1)%len(fams)]["members"])]
                                 for j in range(K)]
                        for s in range(N_SEEDS):
                            sd = derive_seed(31, "p5", f"{fi}", f"{ti}", f"{s}")
                            for cond, seeds in (("cold", []), ("sibling", sib), ("foreign", other)):
                                r = acquire(eng, pt.task, sd, B, seeds, LIM)
                                acc[cond][0] += r.solved_test; acc[cond][1] += 1
                key = f"L{root_len}/m{n_mut}/n{n_train}/B{B}"
                out[key] = {c: round(v[0]/v[1], 3) for c, v in acc.items()}
                out[key]["n_per_cond"] = acc["cold"][1]
                out[key]["n_families"] = len(fams)
                out[key]["gen_stats"] = gstats
                print(f"{key}: {out[key]}  [{time.perf_counter()-t0:.0f}s]", flush=True)
json.dump(out, open("d10/preflight/p5.json","w"), indent=1)
print("DONE")
