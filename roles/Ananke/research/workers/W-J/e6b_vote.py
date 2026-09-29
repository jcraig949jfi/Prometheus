"""E6b: presence-vote / count-threshold plant under the 4 operators (lossless physics)."""
import dataclasses, json, pathlib, sys
import numpy as np, torch
torch.set_num_threads(2)
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import e2_evolve as E
from prometheus.ananke import assays, c1b_run, plants
from prometheus.ananke.rng import H_int
base, env, _, _ = c1b_run.load("f6b623cdb23afd2c")
base = base.replace(loss=0.0, dup=0.0, noise=0, update_mode="sync", update_period=1)
g1 = plants.assemble(base, [("GT", "EMIT", "SENSE", "ZERO", 0),      # only positive voters speak
                            ("CONST", "PAY0", 0, 0, 52),               # I << (b & 7): b = 0 -> 52
                            ("ADDI", "S0", "IN0_0", 0, -118)])         # >= 3 votes -> positive
g = np.repeat(g1[None], base.rules, 0)
seeds = assays.world_seeds(H_int(E.NS, 0xE6B), 64)
out = {}
for op in E.ARMS:
    ci, tel = E.held_eval(base, op, env, g, seeds, "cpu")
    out[op] = ci; print(op, np.round(ci, 3), flush=True)
(pathlib.Path(__file__).parent / "out/e6b.json").write_text(json.dumps(out, indent=1))
