"""W2-K: label-level stability of the C1b specimen labels. Resample the 32 mirror pairs (same indices in every
arm, so arm correlation is kept), recompute every near-cut reading with the frozen pct rule (c1b.ci), push
the booleans through the frozen decision lists (c1b_run.label_m2 / label_m3, recorded NOT_ELIGIBLE lists), count
labels. This is a PLUG-IN replicate model (the observed pairs are the population): it is more optimistic
than the predictive keep = Phi(d/sqrt2). Far readings (d > 8 SE) are held at their recorded values."""
import json, os, pathlib, sys
from collections import Counter
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
import numpy as np
from prometheus.ananke import c1b, c1b_run
B = 400
g = np.random.default_rng(20261001)
out = {}
a = np.load(HERE / "out" / "pairs_m2spec.npz")
labs = Counter()
for _ in range(B):
    i = g.integers(0, 32, 32)
    n = a["normal"][i]
    d_b = a["reset_all_nonpacket"][i] - n
    d_w = a["reset_w"][i] - n
    m_w, lo_w, _ = c1b.ci(d_w)
    b = {"A": True, "Z": True, "C": False, "I": False, "K_S": False, "K_Kp": False, "K_En": False,
         "B": c1b.ci(d_b)[1] >= c1b.INTACT_LO, "K_w": bool(m_w <= -c1b.DROP_PT and lo_w < c1b.DROP_LO)}
    labs[c1b_run.label_m2(b, ["Z"])] += 1
out["M2 4ab2ba01"] = {"recorded": "IN_FLIGHT_PLUS_JOINT_UNRESOLVED", "boot": dict(labs)}
for tag, cid in (("m3_0a23", "0a23398f20cc41a2"), ("m3_f6b6", "f6b623cdb23afd2c")):
    a = np.load(HERE / "out" / f"pairs_{tag}.npz")
    labs = Counter()
    for _ in range(B):
        i = g.integers(0, 32, 32)
        n = a["normal"][i]
        c1w = a["drop_window_c1"][i]
        d_r = a["freeze_rule"][i] - n
        m_r, lo_r, _ = c1b.ci(d_r)
        b = {"T": bool(c1b.ci(c1w)[1] >= c1b.C1_INTACT_LO), "X": bool(c1b.ci(c1w)[2] <= c1b.KILL_HI),
             "R": bool(m_r <= -c1b.DROP_PT and lo_r < c1b.DROP_LO), "M": False}
        labs[c1b_run.label_m3(b, ["T_c1_window"], True)] += 1
    out["M3 " + cid[:8]] = {"recorded": "TRANSPORT+RULE_SWITCH_UNRESOLVED", "boot": dict(labs)}
(HERE / "out" / "label_boot.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
