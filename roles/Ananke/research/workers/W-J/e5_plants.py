"""E5 (PLAN.md): designed aggregation plant under the 4 operators."""
import dataclasses, json, pathlib, sys
import numpy as np, torch
torch.set_num_threads(2)
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import e2_evolve as E
from prometheus.ananke import assays, c1b_run, plants
from prometheus.ananke.rng import H_int
base, env0, _, _ = c1b_run.load("f6b623cdb23afd2c")
if len(sys.argv) > 1 and sys.argv[1] == "lossless":
    base = base.replace(loss=0.0, dup=0.0, noise=0, update_mode="sync", update_period=1)
def agg(ph):
    return plants.assemble(ph, [
        ("GT", "T0", "SENSE", "ZERO", 0),       # 256 if SENSE > 0
        ("GT", "T1", "ZERO", "SENSE", 0),       # 256 if SENSE < 0
        ("ADD", "EMIT", "T0", "T1", 0),         # emit iff SENSE != 0
        ("MOV", "PAY0", "SENSE", 0, 0),
        ("MOV", "S0", "IN0_0", 0, 0),
    ])
g1 = agg(base)
g = np.repeat(g1[None], base.rules, 0)          # same program in every rule slot
seeds = assays.world_seeds(H_int(E.NS, 0xE5), 64)
out = {}
for fam in ["MAJ", "RELAY"]:
    env = dataclasses.replace(env0, family=fam)
    out[fam] = {}
    for op in E.ARMS:
        ci, tel = E.held_eval(base, op, env, g, seeds, "cpu")
        out[fam][op] = {"acc": ci, "emit_rate": tel.get("emit_rate"), "collide_frac": tel.get("collide_frac")}
        print(fam, op, np.round(ci, 3), "emit", round(tel.get("emit_rate", 0), 4), "coll", round(tel.get("collide_frac", 0), 3), flush=True)
(pathlib.Path(__file__).parent / ("out/e5b.json" if len(sys.argv) > 1 else "out/e5.json")).write_text(json.dumps(out, indent=1, default=float))
