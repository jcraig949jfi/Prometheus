"""W2-35 a6: realized in-world causal m by FRAME (W2-17 a4's estimator: mean causal children of causal-born nodes born
<= stop-15), from r3_out birth logs; node frame = frame class of its genome at birth. Runaways vs deep controls.
python -B a6_realized_m.py -> a6_realized_m.json"""
import json, pathlib, collections
from frames import frame, W2, HERE
from s1_scan import fclass
from r2_replay import RUNS  # noqa (path set by s1_scan)
out, agg = {}, collections.defaultdict(lambda: [0, 0])
for label in RUNS:
    d = json.loads((W2 / "W2-17_runaway_departure" / "r3_out" / (label + ".json")).read_text())
    B = {int(k): v for k, v in d["births"].items()}
    stop = d["epochs_replayed"]
    kids = collections.Counter(v["p"] for v in B.values() if v["c"])
    grp = collections.defaultdict(lambda: [0, 0])
    for k, v in B.items():
        if not v["c"] or v["e"] > stop - 15:
            continue
        c = fclass(frame(bytes.fromhex(v["g"])))
        c = "F0" if c == "F0" else ("ROT" if c.startswith("ROT") else "none")
        grp[c][0] += 1
        grp[c][1] += kids[k]
        cls = "RUN" if d["recorded_final_depth"] >= 22 else "CTL"
        agg[(cls, c)][0] += 1
        agg[(cls, c)][1] += kids[k]
    out[label] = {c: {"n": n, "m": round(s / n, 3)} for c, (n, s) in grp.items()}
    print(label, out[label])
res = {"per_run": out, "pooled": {"%s|%s" % k: {"n": n, "m": round(s / n, 3)} for k, (n, s) in sorted(agg.items())}}
print(res["pooled"])
(HERE / "a6_realized_m.json").write_text(json.dumps(res, indent=1))
