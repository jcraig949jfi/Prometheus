"""On global topology every copy already goes to a uniform random other site (engine.py:493-496).
shuffle_dest (engine.py:522) re-draws the recipient uniformly over all N sites from the CTRL stream.
Prediction: on global, shuffle_dest = a re-drawn routing realisation (+ self-delivery w.p. 1/N), so its
effect is the same size as re-drawing the ROUTE stream. Re-draw = monkeypatch rng.ROUTE to an unused id
(the engine reads rng.ROUTE at call time); no file is modified."""
from common import *
import gzip, json, numpy as np
from prometheus.ananke import assays, envs, rng
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
for cid in ("613162a306938de7",):
    r = next(x for x in R if x["cell_id"] == cid)
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); G = np.asarray(r["result"]["champion"])[None]
    print(cid, ph.topology, ph.dest_mode, "fanout", ph.fanout, "N", ph.n_sites)
    for ns in (0x4E1D, 0xD0D0, 0x1234):
        seeds = assays.world_seeds(H_int(r["search_seed"], ns), 64)
        base = assays.evaluate(ph, G, env, seeds, device="cpu", graph=False).pair_acc()[0]
        sh = assays.evaluate(ph, G, env, seeds, ctrl=Controls(shuffle_dest=True), device="cpu", graph=False).pair_acc()[0]
        out = []
        for alt in (21, 22, 23):
            old = rng.ROUTE; rng.ROUTE = alt
            try:
                out.append(assays.evaluate(ph, G, env, seeds, device="cpu", graph=False).pair_acc()[0].mean())
            finally:
                rng.ROUTE = old
        print(f"  ns {ns:#x}: normal {base.mean():.3f}  shuffle_dest {sh.mean():.3f} (d={sh.mean()-base.mean():+.3f})  "
              f"route re-drawn x3: {[round(x,3) for x in out]} (d={[round(x-base.mean(),3) for x in out]})", flush=True)
