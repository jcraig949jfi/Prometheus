"""Second genealogy: the first lineage member that is FULLY state-robust (FR):
  competent, and from every tested start state the copy rate is >= 0.25 x rate_0:
  own carried state after k = 1..6 blank-partner executions, CONST (0x5A) and RANDOM.
Pre-screen on CONST and RANDOM (cheap), then the k-curve. Chronological over versions.json (L members only).
Also records, for each competent L version before the first FR, its CONST/RANDOM rates, so the arrival of the
state-independence can be dated. Writes genealogy2.json."""
import json
import pathlib

import measure as M
from kcurve import kcurve

HERE = pathlib.Path(__file__).resolve().parent
V = json.loads((HERE / "versions.json").read_text())
cache = {}
first = None
n_tested = 0
for v in V:
    if not v["inL"]:
        continue
    g = bytes.fromhex(v["g"])
    if not M.competent(g):
        continue
    if v["g"] not in cache:
        o = M.state_rates(g, 20, ("FRESH", "CONST", "RANDOM"), tag="F16-G2")
        o["fr_pre"] = o["FRESH"] > 0 and o["CONST"] >= 0.25 * o["FRESH"] and o["RANDOM"] >= 0.25 * o["FRESH"]
        if o["fr_pre"]:
            o["k"] = kcurve(g)
            o["FR"] = o["k"][0] > 0 and all(x >= 0.25 * o["k"][0] for x in o["k"][1:])
        else:
            o["FR"] = False
        cache[v["g"]] = o
        n_tested += 1
    v["g2"] = cache[v["g"]]
    if v["g2"]["FR"]:
        first = v["vid"]
        break
path = []
x = first
while x is not None:
    path.append(x)
    x = V[x]["parent_vid"]
path.reverse()
rows = []
for vid in path:
    v = V[vid]
    g = bytes.fromhex(v["g"])
    if "g2" not in v:
        o = M.state_rates(g, 20, ("FRESH", "CONST", "RANDOM"), tag="F16-G2")
        o["k"] = kcurve(g)
        v["g2"] = o
    elif "k" not in v["g2"]:
        v["g2"]["k"] = kcurve(g)
    rows.append({k: v.get(k) for k in ("vid", "oid", "via", "e", "seq", "causal", "fid", "g", "victim_old",
                                        "donor_pre", "victim_vid", "parent_vid", "inL")} | {"meas": v["g2"],
                                                                                           "competent": M.competent(g)})
steps = []
for a, b in zip(rows, rows[1:]):
    ga, gb = bytes.fromhex(a["g"]), bytes.fromhex(b["g"])
    vo = bytes.fromhex(b["victim_old"]) if b.get("victim_old") else None
    steps.append({"to": b["vid"], "via": b["via"], "e": b["e"],
                  "diffs": [[i, "%02X" % ga[i], "%02X" % gb[i], ("%02X" % vo[i]) if vo else None]
                            for i in range(64) if ga[i] != gb[i]]})
out = {"first_FR_vid": first, "n_distinct_tested": n_tested, "path": rows, "steps": steps,
       "n_births": sum(r["via"] == "birth" for r in rows), "n_mut": sum(r["via"] == "mut" for r in rows)}
(HERE / "genealogy2.json").write_text(json.dumps(out, indent=1))
print(first, n_tested, out["n_births"], out["n_mut"])
for r, s in zip(rows[1:], steps):
    print(r["vid"], r["via"], r["e"], r["causal"], r["meas"], s["diffs"])
print(rows[0]["vid"], rows[0]["via"], rows[0]["meas"])
