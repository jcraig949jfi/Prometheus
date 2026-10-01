"""W2-14 v0: does FIELD+FULL (the top rung) reproduce X-TICKET's world trajectories bit-for-bit over the first E epochs?
If yes, the harness is the world's pair epoch for this cell (and that rung is circular by construction).
python -B v0_bitexact.py [E] [seeds...] -> v0_bitexact.json"""
import json, sys, time
import ffield as F
E = int(sys.argv[1]) if len(sys.argv) > 1 else 25
S = [int(x) for x in sys.argv[2:]] or [14, 0]
t0 = time.process_time()
out = {"E": E, "rows": []}
for s in S:
    tk = json.load(open(F.CAMP / "c9x-explore-2026-09-24" / "x_ticket" / "results" / ("%03d.json" % s)))
    res = F.run("BASE", 9_998_000 + s, "FIELD", "FULL", T=E, traj=True, stop_runaway=False)
    mine = [list(x) for x in res["traj"]]
    world_ = [list(x) for x in tk["traj"][:len(mine)]]
    row = {"s": s, "match": mine == world_, "first_diff": next((i for i, (a, b) in enumerate(zip(mine, world_)) if a != b), None),
           "mine_last": mine[-1], "world_at_same": world_[-1], "cpu_s": round(time.process_time() - t0, 1)}
    out["rows"].append(row); print(row, flush=True)
json.dump(out, open(F.HERE / "v0_bitexact.json", "w"), indent=1)
