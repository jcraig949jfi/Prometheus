"""W2-6 check C8 (T6 vs T1/T2 on the cell axis): does the ITERATED single-interaction map (each cell's own write-back
and post-interaction mutation inside every call) reproduce BRIDGE's cell effect under carried registers
(observed S5, PERSIST: C7 4/32 = 0.125 vs CF 14/32 = 0.44), which the one-step map could not see?

Harness: forensics/map_common.py (run_rs ATOMIC runner + register policy CARRY, dense VM, cell C7 or CF; never run).
Process (ILLUSTRATIVE, not world.Runner): as c7c -- a lineage of members each carrying content + context; each step
every member meets a fresh uniform-random partner (fresh zero state) at a random side; a conversion adds the partner
half (content + leftover context) as a member; a member converted by its partner leaves. Established = CAP members.
Donors: the 16 BRIDGE donors (run_br.donors()). Output c8_cell_axis_iterated_map.json
"""
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))
import map_common as M  # noqa: E402

CAP, T, L = 40, 40, int(sys.argv[1]) if len(sys.argv) > 1 else 10
t0 = time.process_time()
D = M.run_br.donors()
out = {"cells": {}}
for cell in ("C7", "CF"):
    h = M.Harness("CARRY", 555, cell=cell)
    rng = random.Random(9090)
    per = []
    for di, dn in enumerate(D):
        g0 = bytes.fromhex(dn["hex"])
        est = 0
        for lin in range(L):
            mem = [(g0, (None, 0, 0))]
            for step in range(T):
                nxt = []
                for g, st in mem:
                    pg = M.rand_genome(rng)
                    r = h.interact(g, pg, rng.randrange(2), d_state=st, p_state=(None, 0, 0))
                    if r["d_kept"]:
                        nxt.append((r["gd"], r["d_state"]))
                    if r["p_conv"]:
                        nxt.append((r["gp"], r["p_state"]))
                mem = nxt
                if not mem or len(mem) >= CAP:
                    break
            est += len(mem) >= CAP
        per.append(round(est / L, 3))
        print(cell, di, dn["origin"], per[-1], round(time.process_time() - t0, 1), flush=True)
    out["cells"][cell] = {"per_donor": per, "mean": round(sum(per) / len(per), 3)}
out["observed_PERSIST_S5"] = {"C7": 0.125, "CF": 0.4375}
out["cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "c8_cell_axis_iterated_map.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
