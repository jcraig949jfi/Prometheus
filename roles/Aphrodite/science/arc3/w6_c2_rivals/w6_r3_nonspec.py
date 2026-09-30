"""R3 NON-SPECIFICITY (Archaeon). Pool of random CLEAN schemas (a18._random_schema,
seeded; clean() = engine/a20_c3.clean copied verbatim in logic: NEW_FINAL vs G1,
>= 20 accumulating instances, and neither EQUAL / COMPOSES / REFINES any
re-expression of G1). Size = number of leaves (atoms + hole); G1 has 2.
For CON1's two payoff families (qoda, qyba) and the 12 fresh G2 families
(CON1_FORENSICS.json), count the schemas S whose wrap (v - (S)) COVERS each
family (w6_common extensional cover), plus two secondary readings: S alone, and
ANY one-move composition of S (a18.compositions)."""
import json
import random
import re
import time
from w6_common import a18, T3D, I, Fam, c2_data, wr, HERE
import ruler_v2 as R

t0 = time.time()
roles, panel, donors, trans = c2_data()
con1 = json.load(open(HERE.parent / "con1" / "CON1_FORENSICS.json", encoding="utf-8"))
fams = []
for f in roles["CON/1"]["families"]:
    if f["name"] in con1["original"]:
        fams.append(Fam(f["name"], f["body"], f["final"], f["init"]))
for name, (b, fi, i), _sz in con1["fresh_families"]:
    fams.append(Fam(name, b, fi, i))
print("families", [F.name for F in fams], flush=True)


def clean(s, sp, tsp):
    v = R.verdict_full(s, a18.G1, sp, tsp)
    if not v["NEW_FINAL"] or v["accumulating"] < 20:
        return False
    for ref in R.reexpressions(a18.G1):
        rel = R.relations(s, ref)
        if rel["COMPOSES"] or rel["REFINES"] or rel["EQUAL"]:
            return False
    return True


def leaves(s):
    return len(re.findall(r"\{H\}|\b(?:acc|v|first|last|0|1)\b", s.replace("abs(", "(")))


a18.use_world("W5")
sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
rng = random.Random(I._seed("ARC3/W6/R3-POOL/v1"))
pool, seen, tries = [], set(), 0
while tries < 4000 and sum(1 for s in pool if leaves(s) <= 3) < 60:
    s = a18._random_schema(rng)
    if not s or s in seen:
        continue
    seen.add(s)
    tries += 1
    if clean(s, sp, tsp):
        pool.append(s)
print("pool", len(pool), "tries", tries, "leaf-hist", {k: sum(1 for s in pool if leaves(s) == k) for k in range(1, 8)},
      round(time.time() - t0), flush=True)
controls = {"G1": panel["G1"], "SHAM_0": panel["SHAM_0"], "SHAM_1": panel["SHAM_1"], "OFF_0": panel["OFF_0"]}
rows = []
for tag, s in [("CTRL:" + k, v) for k, v in controls.items()] + [("POOL", s) for s in pool]:
    wrap = "(v - (%s))" % s
    wi = T3D.instantiate(wrap)
    si = T3D.instantiate(s)
    row = {"tag": tag, "schema": s, "leaves": leaves(s), "wrap": wrap, "wrap_instances": len(wi),
           "wrap_covers": [F.name for F in fams if F.covered_by_bodies(wi)],
           "self_covers": [F.name for F in fams if F.covered_by_bodies(si)]}
    if tag.startswith("CTRL") or leaves(s) <= 3:
        comp_b = list(dict.fromkeys(b for w in a18.compositions(s) for b in T3D.instantiate(w)))
        row["anycomp_covers"] = [F.name for F in fams if F.covered_by_bodies(comp_b)]
    rows.append(row)
    print(tag, s, len(wi), len(row["wrap_covers"]), len(row.get("anycomp_covers", [])), round(time.time() - t0), flush=True)
    wr("W6_R3_NONSPEC.json", {"families": [F.name for F in fams], "pool_tries": tries, "rows": rows})
print("wrote", round(time.time() - t0), flush=True)
