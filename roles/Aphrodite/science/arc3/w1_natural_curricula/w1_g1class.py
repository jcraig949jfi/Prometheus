"""W1 -- what are the G1-composition families in each supply? (forensic)
Splits G1-composition members by ruler v2 fclass (ADDITIVE = inside G1's own span)
and lists the most frequent specific compositions under U and LIN."""
import json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "0", "U:0"]
import w1_recurrence_probe as P
res = json.loads((HERE / "W1_RECURRENCE_N96.json").read_text())
P.T3D.in_space_body("(acc + v)")
per = P.panel_index()["G1"]
out = {}
for tag, r in sorted(res.items()):
    mem = [f[1] for f in r["families"] if f[1] in per]
    fc = Counter(P.R.fclass(b) for b in mem)
    wc = Counter(w for b in mem for w in per[b])
    out[tag] = {"members": len(mem), "fclass": dict(fc), "top_compositions": wc.most_common(4)}
    print(tag, len(mem), dict(fc), wc.most_common(3))
(HERE / "W1_G1CLASS.json").write_text(json.dumps(out, indent=1))
