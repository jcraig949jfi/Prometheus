"""W-H Part 0: observation of normal runs (no interventions)."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
torch.set_num_threads(2)
from harness import run, acc, seen_inbox, REPO
from prometheus.ananke import c1b_run, lens

OUT = pathlib.Path(__file__).parent / "out"

def observe(cid):
    ph, env, g, row = c1b_run.load(cid)
    rec = {k: [] for k in ("r_pre", "r", "S", "cnt", "insum", "awake", "E", "emit")}
    def pre(w, t):
        rec["r_pre"].append(w.r.cpu().numpy().astype(np.int8).copy())
        c, s = seen_inbox(w)
        rec["cnt"].append(c.astype(np.int32)); rec["insum"].append(s[..., 0].astype(np.int32))
    def post(w, t):
        rec["r"].append(w.r.cpu().numpy().astype(np.int8).copy())
        rec["S"].append(w.S.cpu().numpy().copy())
        rec["awake"].append(w.last_awake.cpu().numpy().copy())
        rec["E"].append(w.E.cpu().numpy().copy())
        rec["emit"].append(w.last_emit.cpu().numpy().copy())
    tr = run(ph, g, env, pre=pre, post=post)
    ep = tr.ep
    arrs = {k: np.stack(v) for k, v in rec.items()}
    np.savez_compressed(OUT / f"obs_{cid[:8]}.npz", sense=ep.schedule.sense_val.numpy(),
                        sidx=ep.schedule.sense_idx.numpy(), ridx=ep.schedule.read_idx.numpy(),
                        ro_tick=ep.ro_tick, y=ep.y, scored=ep.scored, trace=tr.trace, per_trial=tr.per_trial, **arrs)
    print(cid[:8], "normal", lens.ci(acc(tr)))

if __name__ == "__main__":
    for c in sys.argv[1:]:
        observe(c)
