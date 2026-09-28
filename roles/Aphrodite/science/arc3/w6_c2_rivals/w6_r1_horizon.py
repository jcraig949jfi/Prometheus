"""R1 COMPOSITION HORIZON (Nestor). For every C2 VALIDATE and TRANSFER family,
the minimum number of composition moves (a18.compositions, applied
iteratively) from each panel schema to a schema that COVERS the family
(w6_common: extensional on a 100-input task-domain battery). W5 is depth 3, so
distances are 0, 1, 2 or INF (depth 4 has no in-space instances)."""
import time
from w6_common import a18, T3D, Fam, c2_data, wr

t0 = time.time()
roles, panel, donors, trans = c2_data()
fams = {}
for key, v in roles.items():
    if not v["ok"]:
        continue
    for f in v["families"]:
        if f["role"] in ("VALIDATE", "TRANSFER"):
            fams.setdefault(f["name"], {"f": f, "uses": []})["uses"].append([key, f["role"]])
print("families", len(fams), flush=True)
F = {n: Fam(n, d["f"]["body"], d["f"]["final"], d["f"]["init"]) for n, d in fams.items()}
out = {"families": {}, "levels": {}}
for sk in ("G1", "SHAM_0", "SHAM_1", "OFF_0"):
    S = panel[sk]
    D = [[S], a18.compositions(S)]
    d2 = []
    for w in D[1]:
        d2 += a18.compositions(w)
    D.append(list(dict.fromkeys(d2)))
    inst = [{s: T3D.instantiate(s) for s in lvl} for lvl in D]
    B = [list(dict.fromkeys(b for s in lvl for b in inst[k][s])) for k, lvl in enumerate(D)]
    out["levels"][sk] = {"schemas": [len(x) for x in D], "bodies": [len(x) for x in B]}
    print(sk, out["levels"][sk], round(time.time() - t0), flush=True)
    for n, fam in F.items():
        r = {"dist": None}
        for k in range(3):
            hit = fam.covered_by_bodies(B[k])
            if hit:
                wit = next(s for s in D[k] if hit[2] in inst[k][s])
                r = {"dist": k, "schema": wit, "program": list(hit)}
                break
        out["families"].setdefault(n, {"spec": fams[n]["f"], "uses": fams[n]["uses"]})[sk] = r
    print(sk, "done", round(time.time() - t0), flush=True)
wr("W6_R1_HORIZON.json", out)
print("wrote", round(time.time() - t0), flush=True)
