"""W1 -- aggregate the recurrence probe (FORENSIC, NOT A DISPOSITION).
Reads W1_RECURRENCE_N96.json; writes W1_RECURRENCE_SUMMARY.json.
Adds, per supply and per panel schema S (A19 panel):
  P_class(S)    P(>= 2 of 8 random TRANSFER families instantiate SOME composition of S)
  P_specific(S) P(>= 2 of 8 random TRANSFER families instantiate the SAME composition of S)
and, per generator, the cross-seed Jaccard of recurring (>= 3 families) schema sets
(low Jaccard = the identity of what recurs is set by the seed, i.e. emergent).
"""
import json
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "0", "U:0"]
import w1_recurrence_probe as P  # noqa: E402

res = json.loads((HERE / "W1_RECURRENCE_N96.json").read_text())
P.T3D.in_space_body("(acc + v)")
pidx = P.panel_index()
out, rec_sets = {}, defaultdict(list)
for tag, r in sorted(res.items()):
    kind = tag.split(":")[0]
    bodies = [f[1] for f in r["families"]]
    rng = random.Random(P.I._seed("W1/ANALYSE/" + tag))
    cls, spec = Counter(), Counter()
    for _ in range(2000):
        tr = rng.sample(bodies, 8)
        for S, per in pidx.items():
            mem = [b for b in tr if b in per]
            cls[S] += len(mem) >= 2
            wc = Counter(w for b in mem for w in per[b])
            spec[S] += bool(wc) and max(wc.values()) >= 2
    sch = Counter(s for b in set(bodies) for s in P.schemas(b))
    rec_sets[kind].append({s for s, c in sch.items() if c >= 3})
    m = r["measure"]
    out[tag] = {"kind": kind, "admit_rate_per_proposal": round(r["stats"]["admitted"] / r["stats"]["proposals"], 4),
                "R3": m["R3"], "R3u": m["R3_unique_bodies"], "P_reuse": m["P_reuse"], "dup": m["dup_body_share"],
                "n_schemas_ge3": m["n_schemas_ge3"],
                "panel": {S: dict(m["panel"][S], P_class=round(cls[S] / 2000, 3), P_specific=round(spec[S] / 2000, 3))
                          for S in pidx}}


def jac(a, b):
    return len(a & b) / len(a | b) if (a | b) else float("nan")


agg = {}
for kind in sorted({v["kind"] for v in out.values()}):
    rows = [v for v in out.values() if v["kind"] == kind]
    ss = rec_sets[kind]
    js = [jac(ss[i], ss[j]) for i in range(len(ss)) for j in range(i + 1, len(ss))]
    agg[kind] = {"n_seeds": len(rows),
                 **{k: round(st.mean(r[k] for r in rows), 3) for k in ("R3", "R3u", "P_reuse", "dup", "n_schemas_ge3",
                                                                      "admit_rate_per_proposal")},
                 "cross_seed_jaccard_recurring": round(st.mean(js), 3) if js else None,
                 "panel": {S: {k: [r["panel"][S][k] for r in rows]
                               for k in ("share", "max_one_composition", "P_class", "P_specific")}
                           for S in pidx}}
(HERE / "W1_RECURRENCE_SUMMARY.json").write_text(json.dumps({"per_supply": out, "per_generator": agg}, indent=1))
for k, v in agg.items():
    print(k, {x: v[x] for x in ("R3", "R3u", "P_reuse", "dup", "cross_seed_jaccard_recurring", "admit_rate_per_proposal")})
    for S in pidx:
        print("   ", S, v["panel"][S])
