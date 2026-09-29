"""Descriptive: what the persisting twin difference looks like (end of trial k+6)."""
import sys, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import ret_census as rc
from prometheus.ananke.engine import World
want = {"D_f7e62fe3": "w", "M2_fresh3": "w", "D_6a47bd68": "S", "D_0ad7dc00": "Kp", "D_e79e72df": "Kp", "D_9e72f9b6": "Kp"}
for sp in rc.specimens():
    if sp["name"] not in want: continue
    tw = rc.twin_setup(sp["ph"], sp["env"]); Pd = tw["Pd"]
    w = World(sp["ph"], np.repeat(sp["g"][None], 64, 0), tw["ws"], device="cpu", schedule=tw["sch"])
    snaps = {}
    for t in range(sp["env"].T()):
        w.step()
        for j in (1, 6):
            if t == (rc.K + j + 1) * Pd - 1:
                snaps[j] = getattr(w, want[sp["name"]]).clone().to(__import__("torch").int64).numpy()
    c = tw["ylead"][:, rc.K]
    for j, a in snaps.items():
        d = a[0::2] - a[1::2]                     # [32, ...]
        d = d.reshape(32, -1)
        nz = (d != 0).sum(1); s = d.sum(1)
        print(sp["name"], want[sp["name"]], f"j={j}", "pairs_diff", int((nz > 0).sum()), "med_elems", float(np.median(nz)),
              "sum_diff*c>0:", int((s * c > 0).sum()), "<0:", int((s * c < 0).sum()), "=0:", int((s == 0).sum()),
              "|diff| vals", np.unique(np.abs(d[d != 0]))[:8].tolist(), "median|sum|", float(np.median(np.abs(s))))
