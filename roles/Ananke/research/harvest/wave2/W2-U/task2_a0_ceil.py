"""TASK 2 compute: RELAY joint ceilings for every A0 RELAY census row, on the EXACT plant_viability seeds
(world_seeds(H_int(search_seed, 0x9147), 32), campaign.py:299) and on 256 fresh worlds.
Plant runs at prog_len=max(L,12); prog_len does not enter the ceiling (topology/positions/timing only).
python task2_a0_ceil.py -> out/task2_a0_ceil.json"""
from w2u_ceil import *            # noqa
from w2p_common import Clock
NS = 0x57325541   # "W2UA"
ck = Clock()
A0 = [r for r in hc.rows() if r["wave"] == "A0" and r["env"]["family"] == "RELAY"]
out = []
for i, r in enumerate(A0):
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    cp = ceilings(ph, env, assays.world_seeds(H_int(r["search_seed"], 0x9147), 32))
    cb = ceilings(ph, env, assays.world_seeds(H_int(NS, int(r["cell_id"][:8], 16)), 256))
    out.append({"cell": r["cell_id"], "plant": cp, "big": cb})
    if i % 200 == 0:
        print(i, len(A0), ck.done(), flush=True)
save("task2_a0_ceil.json", {"rows": out, "compute": ck.done()})
print(ck.done())
