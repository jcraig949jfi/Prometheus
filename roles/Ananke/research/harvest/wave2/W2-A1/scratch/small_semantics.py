"""Small [V] checks: (a) routing write floor asymmetry; (b) stats.delivered counts aloha-collided packets;
(c) shuffle_time widens the delay range; (d) count C1 rows where cap>0 is inert (collision none)."""
from common import *
import gzip, json, numpy as np, torch
from prometheus.ananke import plants
from prometheus.ananke.engine import World, Schedule, Controls
from prometheus.ananke.physics import Physics
# (a)
rv = torch.tensor([-33, -32, -31, -1, 0, 1, 31, 32, 33], dtype=torch.int32)
print("(a) rval        ", rv.tolist()); print("    rval >> 5   ", (rv >> 5).tolist())
# (b) ring r1 dest all, cap 1 aloha: every site receives 2 copies -> all collide, yet 'delivered' > 0
ph = Physics(topology="ring", n_sites=8, dest_mode="all", cap=1, collision="aloha", prog_len=2, payload_width=1, channels=1)
G = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1)])[None]
idx = torch.arange(8)[None]; sch = Schedule(idx, torch.zeros(10, 1, 8, dtype=torch.int32), idx.clone())
w = World(ph, G[None], [1], device="cpu", schedule=sch); w.run(10, graph=False)
print("(b) attempted", int(w.stats["attempted"]), "delivered", int(w.stats["delivered"]), "collided", int(w.stats["collided"]), "Acc_cnt sum", int(w.Acc_cnt.sum()))
# (c) M1-like physics: ring r3, lat 1+1*hop, jitter 1 -> normal delay 2..5, LM
ph = Physics(topology="ring", n_sites=144, radius=3, lat_base=1, lat_hop=1, lat_jitter=1)
print("(c) LM", ph.lm(), " normal delay range [", 1 + 1 * 1 + 0, ",", 1 + 1 * 3 + 1, "]  shuffle_time range [1,", ph.lm() - 1, "]")
# (d)
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
n = sum(1 for r in R if r["physics"]["cap"] > 0 and r["physics"]["collision"] == "none")
m = sum(1 for r in R if r["physics"]["cap"] > 0)
print(f"(d) rows with cap>0: {m}; of these collision=none (cap inert): {n}")
