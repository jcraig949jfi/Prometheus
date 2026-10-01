"""W1 -- NON-TRIVIAL composition recurrence (forensic). As w1_analyse, but for each
panel schema S a family counts only if its body is NOT an instance of S itself
(identity wraps such as (1 * S), (S // 1), (S - 0) collapse to S) and the matched
composition is not an identity wrap. Symmetric for every panel schema.
Writes W1_RECURRENCE_NONTRIVIAL.json."""
import json, random, statistics as stt, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "0", "U:0"]
import w1_recurrence_probe as P
res = json.loads((HERE / "W1_RECURRENCE_N96.json").read_text())
P.T3D.in_space_body("(acc + v)")
pidx = P.panel_index()
IDW = ["(1 * {S})", "({S} * 1)", "({S} // 1)", "({S} - 0)", "({S} + 0)", "(0 + {S})", "pow({S}, 1)"]
nt = {}
for S, per in pidx.items():
    own = set(P.T3D.instantiate(P.PANEL[S]))
    idw = {x.replace("{S}", P.PANEL[S]) for x in IDW}
    nt[S] = {b: {w for w in ws if w not in idw} for b, ws in per.items() if b not in own}
    nt[S] = {b: ws for b, ws in nt[S].items() if ws}
out = {}
for tag, r in sorted(res.items()):
    bodies = [f[1] for f in r["families"]]
    rng = random.Random(P.I._seed("W1/ANALYSE-NT/" + tag))
    cls, spec = Counter(), Counter()
    for _ in range(2000):
        tr = rng.sample(bodies, 8)
        for S, per in nt.items():
            mem = [b for b in tr if b in per]
            cls[S] += len(mem) >= 2
            wc = Counter(w for b in mem for w in per[b])
            spec[S] += bool(wc) and max(wc.values()) >= 2
    row = {}
    for S, per in nt.items():
        mem = [b for b in bodies if b in per]
        wc = Counter(w for b in mem for w in per[b])
        row[S] = {"share": round(len(mem) / len(bodies), 3), "max_one": max(wc.values()) if wc else 0,
                  "top": wc.most_common(2), "P_class": round(cls[S] / 2000, 3), "P_specific": round(spec[S] / 2000, 3)}
    out[tag] = row
agg = {}
for kind in sorted({t.split(":")[0] for t in out}):
    rows = [v for t, v in out.items() if t.split(":")[0] == kind]
    agg[kind] = {S: {k: [r[S][k] for r in rows] for k in ("share", "max_one", "P_class", "P_specific")} for S in nt}
(HERE / "W1_RECURRENCE_NONTRIVIAL.json").write_text(json.dumps({"per_supply": out, "per_generator": agg}, indent=1))
for k, v in agg.items():
    print(k)
    for S in nt:
        print("   ", S, v[S])
for t in ("U:0", "U:1", "U:2", "LIN:0", "LIN:2"):
    print(t, out[t]["G1"]["top"])
