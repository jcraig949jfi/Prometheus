"""For the 8 most common live competent genomes at epoch 700 (all FULLY robust in kcurve.json): trace each back
to D0 through versions.json, screen every version on the path (CONST/RANDOM pre-screen, tag 'F16-G2' as
genealogy2), and record the step where CONST/RANDOM robustness first appears and whether vid 1005 (first FR) is
an ancestor. Also a positional consensus: bytes where >= 7/8 of these genomes agree with each other but differ
from every D0 genome. Writes paths700.json."""
import collections
import json
import pathlib

import measure as M

HERE = pathlib.Path(__file__).resolve().parent
V = json.loads((HERE / "versions.json").read_text())
D = json.loads((HERE / "replay_events.json").read_text())
G = json.loads((HERE / "genealogy.json").read_text())
live = D["snaps"]["700"]["live"]
seq700 = D["snaps"]["700"]["seq"]
# oid -> latest version with seq <= seq700
cur = {}
for v in V:
    if v["seq"] <= seq700:
        cur[v["oid"]] = v["vid"]
cnt = collections.Counter(g for _, g in live)
tops = []
for g, c in cnt.most_common():
    if M.competent(bytes.fromhex(g)):
        oid = next(o for o, gg in live if gg == g and o in cur and V[cur[o]]["g"] == g)
        tops.append((g, c, cur[oid]))
    if len(tops) == 8:
        break
cache = {}


def fr(g):
    if g not in cache:
        o = M.state_rates(bytes.fromhex(g), 20, ("FRESH", "SELF1", "CONST", "RANDOM"), tag="F16-G2")
        o["frc"] = o["FRESH"] > 0 and o["CONST"] >= 0.25 * o["FRESH"] and o["RANDOM"] >= 0.25 * o["FRESH"]
        cache[g] = o
    return cache[g]


out = []
for g, c, vid in tops:
    path = []
    x = vid
    while x is not None:
        path.append(x)
        x = V[x]["parent_vid"]
    path.reverse()
    meas = [fr(V[p]["g"]) for p in path]
    first = next((i for i, m in enumerate(meas) if m["frc"]), None)
    # does it stay robust after the first transition?
    stays = first is not None and all(m["frc"] for m in meas[first:])
    fv = path[first] if first is not None else None
    pv = path[first - 1] if first else None
    diffs = None
    if fv is not None and pv is not None:
        a, b = bytes.fromhex(V[pv]["g"]), bytes.fromhex(V[fv]["g"])
        vo = V[fv].get("victim_old")
        diffs = [[i, "%02X" % a[i], "%02X" % b[i], vo[2 * i:2 * i + 2].upper() if vo else None] for i in range(64) if a[i] != b[i]]
    out.append({"genome": g, "count700": c, "vid": vid, "root_vid": path[0], "root_via": V[path[0]]["via"],
                "n_births": sum(V[p]["via"] == "birth" for p in path), "n_mut": sum(V[p]["via"] == "mut" for p in path),
                "through_1005": 1005 in path, "first_frc_vid": fv, "first_frc_e": V[fv]["e"] if fv is not None else None,
                "frc_persists_along_path": stays, "transition_diffs": diffs,
                "path_frc": [[p, V[p]["e"], V[p]["via"], m["frc"], m["FRESH"], m["SELF1"], m["CONST"], m["RANDOM"]]
                             for p, m in zip(path, meas)]})
    print(vid, c, "root", path[0], "births", out[-1]["n_births"], "via1005", 1005 in path, "first", fv,
          out[-1]["first_frc_e"], "persists", stays, diffs, flush=True)
d0 = [bytes.fromhex(h) for h in G["d0_genomes"]]
T = [bytes.fromhex(t[0]) for t in tops]
cons = []
for i in range(64):
    vals = collections.Counter(t[i] for t in T)
    b, k = vals.most_common(1)[0]
    if k >= 7 and all(d[i] != b for d in d0):
        cons.append([i, "%02X" % b, k, ["%02X" % d[i] for d in d0]])
print("consensus diffs vs D0:", cons)
(HERE / "paths700.json").write_text(json.dumps({"paths": out, "consensus_vs_d0": cons}, indent=1))
