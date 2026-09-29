"""W-B X5e (added after X5d gave identical results for rules 1-3): are junk
rules simply silent? Emitters per world under uniform-k frozen, and whether
X5d traces for rules 1..3 are bit-identical."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from probe import run, freeze, set_r, pin
from prometheus.ananke import c1b, c1b_run
from m3 import pair_mask
res = {}
for cid in c1b.SPECIMENS["M3"]:
    ph, env, g, _ = c1b_run.load(cid)
    o = {}
    for k in range(ph.rules):
        tr = run(ph, g, env, pre=lambda w, k=k: (set_r(k)(w), freeze(w)))
        o[f"uniform{k}_emitters_per_world"] = float(tr.stats["emitters"].mean())
        o[f"uniform{k}_readout_S0_nonzero_frac"] = float((tr.trace != 0).mean())
    base = run(ph, g, env)
    B, N = 64, ph.n_sites
    ro = np.zeros((B, N), bool)
    ri = base.ep.schedule.read_idx.cpu().numpy()
    for b in range(B):
        ro[b, ri[b]] = True
    m = pair_mask(B, N, 0.25, 11, ro)
    ev = lambda f: (lambda w, t: f(w))
    trs = [run(ph, g, env, pre=lambda w, k=k: (set_r(0)(w), pin(m, k)(w)), every=ev(pin(m, k))).trace for k in range(1, ph.rules)]
    o["X5d_traces_identical_rules_1_2_3"] = bool(all((t == trs[0]).all() for t in trs))
    res[cid[:8]] = o
    print(cid[:8], o, flush=True)
(pathlib.Path(__file__).parent / "out" / "junk_check.json").write_text(json.dumps(res, indent=1))
