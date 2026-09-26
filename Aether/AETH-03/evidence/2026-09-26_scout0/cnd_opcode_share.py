"""Share of 0x02 among active emitters at the end of cnd's scout0 warmup.

PHYSICS_DESIGN_01 s4/C4 preregistered this measurement, but the battery
in aeth03_scouts.py did not record it. The warmup is deterministic in
(variant, n, seed, rng_seed), so this replays it with the battery's own
`initial` and `step` and reads the share, rather than changing the
battery after it had run.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [AETHER, os.path.join(AETHER, "test", "reference")]
import numpy as np
from observatory import aeth03_scouts as S
out = {}
for s in (0, 1):
    seed, rng_seed = S.SEED0 + s, S.RNG0 + s
    par = S.params(seed, S.MUT_ON)
    f = S.initial("cnd", 128, rng_seed)
    em0 = S.emitters("cnd", f, 1)
    share0 = float((f[0][em0] == 2).mean())
    for t in range(1, 1501):
        f, _ = S.step("cnd", f, t, par)
    em = S.emitters("cnd", f, par["write_cost"])
    out[s] = {"share_0x02_initial": share0,
              "share_0x02_end_of_warmup": float((f[0][em] == 2).mean()),
              "emitters_end": int(em.sum()),
              "sites_opcode_0x02_end": int((f[0] == 2).sum())}
    print(s, out[s], flush=True)
with open(os.path.join(HERE, "cnd_opcode_share.json"), "w", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True); fh.write("\n")
