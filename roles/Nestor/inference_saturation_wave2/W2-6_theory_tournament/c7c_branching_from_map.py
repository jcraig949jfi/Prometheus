"""W2-6 check C7c (T6 vs T7, BASE miss; ILLUSTRATIVE, not world.Runner): a branching process built only from single
world interactions (same harness as c7). Each labelled member carries its own content + context; every step each member
meets one fresh uniform-random partner at a random side (naive, density-independent background); a recorded conversion
adds the partner half (content + leftover context) as a new member one generation deeper; a member that is overwritten
by its partner leaves the lineage. Runs until the lineage is extinct, reaches CAP members ("established"), or T steps.
Readouts per write-back rule: P(established), P(max generation >= 8), mean final size. Compared with the observed
7ae3 rates: ATOMIC ~0.52 (runaway ruler), BASE ~0.03. Output c7c_branching_from_map.json
"""
import json, random, sys, time
# c7 main() is guarded
import c7_t6_t7_base_closure as C  # noqa: E402

CAP, T, L = 40, 60, 120
t0 = time.process_time()
out = {}
for name, base in (("BASE", C.world.Runner), ("ATOMIC", C.run_ds.runner_cls(C.world))):
    h = C.harness(base, 1234)
    rng = random.Random(4321)
    est = gen8 = 0
    sizes, calls = [], 0
    for lin in range(L):
        mem = [(C.G7, (None, 0, 0), 0)]
        maxgen = 0
        for step in range(T):
            nxt = []
            for g, st, gen in mem:
                pg = bytes(rng.randrange(256) for _ in range(64))
                a = C.one(h, g, st, pg, rng.randrange(2)); calls += 1
                if not a["hijacked"]:
                    nxt.append((a["d_after"][0], a["d_after"][1], gen))
                if a["conv"]:
                    nxt.append((a["p_after"][0], a["p_after"][1], gen + 1))
                    maxgen = max(maxgen, gen + 1)
            mem = nxt
            if not mem or len(mem) >= CAP:
                break
        est += len(mem) >= CAP
        gen8 += maxgen >= 8
        sizes.append(len(mem))
    out[name] = {"lineages": L, "P_reach_cap": round(est / L, 3), "P_maxgen_ge8": round(gen8 / L, 3),
                 "mean_final_size": round(sum(sizes) / L, 1), "calls": calls}
    print(name, out[name], round(time.process_time() - t0, 1), flush=True)
out["observed_reference"] = {"ATOMIC_runaway": "109/208 = 0.52", "BASE": "about 0.03 (4/144)"}
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open(C.HERE / "c7c_branching_from_map.json", "w"), indent=1)
