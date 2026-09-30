"""W1 -- transfer-breadth curve under the UNCONSTRUCTED supplies (forensic).
P(>= 2 of K random transfer families instantiate the SAME non-trivial composition of S),
K in {8, 16, 32, 64}, for U (A19 NAT rule), LIN and STAR. Writes W1_BREADTH.json.
Also COND: pick a random member family of S (a stand-in for the VALIDATE family on which
the composition was selected) and one of its compositions w at random; P(>= 2 of K OTHER
random families instantiate w). This is the reuse opportunity of a selected composition."""
import json, random, sys
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
    if tag.split(":")[0] not in ("U", "LIN", "STAR"):
        continue
    bodies = [f[1] for f in r["families"]]
    rng = random.Random(P.I._seed("W1/BREADTH/" + tag))
    out[tag] = {}
    for K in (8, 16, 32, 64):
        c = Counter()
        for _ in range(1000):
            tr = rng.sample(bodies, K)
            for S, per in nt.items():
                wc = Counter(w for b in tr if b in per for w in per[b])
                c[S] += bool(wc) and max(wc.values()) >= 2
        out[tag][K] = {S: round(c[S] / 1000, 3) for S in nt}
        cond = {}
        for S, per in nt.items():
            mem = [i for i, b in enumerate(bodies) if b in per]
            if not mem:
                cond[S] = None
                continue
            h = 0
            for _ in range(1000):
                i = rng.choice(mem)
                w = rng.choice(sorted(per[bodies[i]]))
                tr = rng.sample([j for j in range(len(bodies)) if j != i], K)
                h += sum(1 for j in tr if bodies[j] in per and w in per[bodies[j]]) >= 2
            cond[S] = round(h / 1000, 3)
        out[tag]["COND_%d" % K] = cond
    print(tag, out[tag])
(HERE / "W1_BREADTH.json").write_text(json.dumps(out, indent=1))
