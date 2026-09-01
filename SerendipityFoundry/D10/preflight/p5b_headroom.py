"""P5b: headroom probe with bounded-output reference programs.

The 64-bit-output environment gave a gradient-free landscape (no partial
credit is ever earned, so seeded material is indistinguishable from noise
and is lost immediately). Constraining reference programs to outputs in
[0, OUT_HI] restores a graded signal through the instrument's own
cases_passed fitness -- no bespoke shaping function is introduced.
"""
import json, sys, time, random
sys.path.insert(0, "d10")
from lib import progtasks as P
from lib.acquire import acquire
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
K, N_FAM, N_MEM, N_SEEDS = 4, 5, 3, 4
OUT_HI = int(sys.argv[1]) if len(sys.argv) > 1 else 255
MIN_DISTINCT = int(sys.argv[2]) if len(sys.argv) > 2 else 16


def bounded_ok(prog, probe_seed):
    outs = []
    for ins in P._probe_inputs(probe_seed, P.PROBE_N):
        r = P._run(prog, ins, P.MAX_REF_STEPS + 1)
        if r.halt != "end" or not (0 <= r.output <= OUT_HI):
            return None
        outs.append(r.output)
    if len(set(outs)) < MIN_DISTINCT:
        return None
    return outs


def sample_root_b(seed, length, tries=3000):
    for i in range(tries):
        rng = random.Random(derive_seed(seed, "d10", "rootb", f"#{i}"))
        prog = bytes(rng.randrange(256) for _ in range(length))
        if bounded_ok(prog, derive_seed(seed, "d10", "probe")) is not None:
            return prog
    return None


def sample_member_b(root, seed, n_mut, tries=300):
    ps = derive_seed(seed, "d10", "probe")
    ro = bounded_ok(root, ps)
    for i in range(tries):
        g = root
        for j in range(n_mut):
            g = eng.mutate(g, derive_seed(seed, "d10", "memb", f"#{i}", f"m{j}"))
        o = bounded_ok(g, ps)
        if o is None or o == ro:
            continue
        return g
    return None


def build(root_len, n_mut, n_train, gen_seed, max_cand=200):
    fams, st = [], {"roots_tried":0,"roots_ok":0,"members_ok":0,"tasks_ok":0,"shortcut_rej":0}
    for f in range(max_cand):
        if len(fams) >= N_FAM: break
        st["roots_tried"] += 1
        root = sample_root_b(derive_seed(gen_seed, "rootb", f"#{f}"), root_len)
        if root is None: continue
        st["roots_ok"] += 1
        mems, tasks = [], []
        for m in range(N_MEM):
            g = sample_member_b(root, derive_seed(gen_seed, "memb", f"#{f}", f"#{m}"), n_mut)
            if g is None: continue
            st["members_ok"] += 1
            t = P.task_from_program(g, derive_seed(gen_seed, "case", f"#{f}", f"#{m}"),
                                    n_train, 20, f"f{f}", m)
            if t is None:
                st["shortcut_rej"] += 1; continue
            st["tasks_ok"] += 1
            mems.append(g); tasks.append(t)
        if len(tasks) >= 2:
            fams.append({"root": root, "members": mems, "tasks": tasks})
    return fams, st


out = {}
t0 = time.perf_counter()
for root_len in (12, 20):
    for n_mut in (1, 3):
        fams, st = build(root_len, n_mut, 6, 909)
        print(f"L{root_len}/m{n_mut}: fams={len(fams)} {st} [{time.perf_counter()-t0:.0f}s]", flush=True)
        if len(fams) < 3:
            out[f"L{root_len}/m{n_mut}"] = {"error": "insufficient", "gen": st}; continue
        for B in (600, 2000):
            acc = {"cold":[0,0], "sibling":[0,0], "foreign":[0,0]}
            accT = {"cold":0, "sibling":0, "foreign":0}
            for fi, fam in enumerate(fams):
                other_f = fams[(fi + 1) % len(fams)]
                for ti, pt in enumerate(fam["tasks"]):
                    sib = [fam["members"][j] for j in range(len(fam["members"])) if j != ti]
                    sib = (sib + [fam["root"]])[:K]
                    fo = (other_f["members"] + [other_f["root"]])[:K]
                    for s in range(N_SEEDS):
                        sd = derive_seed(31, "p5b", f"{fi}", f"{ti}", f"{s}")
                        for cond, seeds in (("cold", []), ("sibling", sib), ("foreign", fo)):
                            r = acquire(eng, pt.task, sd, B, seeds, LIM)
                            acc[cond][0] += r.solved_test; acc[cond][1] += 1
                            accT[cond] += r.solved_train
            key = f"L{root_len}/m{n_mut}/B{B}"
            out[key] = {c: round(v[0]/v[1],3) for c,v in acc.items()}
            out[key].update({c+"_train": round(accT[c]/acc[c][1],3) for c in accT})
            out[key]["n_per_cond"] = acc["cold"][1]; out[key]["gen"] = st
            print(f"{key}: {out[key]} [{time.perf_counter()-t0:.0f}s]", flush=True)
json.dump(out, open(f"d10/preflight/p5b_{OUT_HI}.json","w"), indent=1)
print("DONE")
