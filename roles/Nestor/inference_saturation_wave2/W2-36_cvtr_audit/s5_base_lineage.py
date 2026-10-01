"""Step 5: base lineages only (no variants), 128 panel copiers x certified side x 9 seeds: classify each seed's
base lineage as EXACT (fid >= 0.9 at g1-3 in >= 2/3 draws), PARTIAL (fid >= 0.5 at g1-3, no decay > 0.1, >= 2/3
draws, not EXACT) or COLLAPSE. Joined with s1's CVT-R accepts -> how many accepts sit on a collapsed base."""
import json, pathlib
from collections import Counter
from _cvtx import A, ROWS, make_step, fid
S1 = {r["key"]: r for r in json.loads(pathlib.Path(__file__).with_name("s1_multiseed.json").read_text())["rows"]}
OUT = pathlib.Path(__file__).with_suffix(".json")
panel = [r for r in ROWS if r["vm"] == "DENSE" and r["P11"]["certified"] and len(r["P11"]["certified_sides"]) == 1]
C = Counter(); per = []
for r in panel:
    G = bytes.fromhex(r["hex"]); s = r["P11"]["certified_sides"][0]
    P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
    seeds = [r["hex"]] + [r["hex"] + ":reseed%d" % j for j in range(8)]
    cls = []
    for sid in seeds:
        st = make_step(z, P, s, sid)
        F = []
        for k in range(3):
            g_, f = G, []
            for g in range(1, 5):
                g_ = st(g_, g, k); f.append(fid(g_, G))
            F.append(f)
        ex = sum(all(f[g] >= 0.9 for g in range(3)) for f in F) >= 2
        pa = sum(all(f[g] >= 0.5 for g in range(3)) and f[2] >= f[0] - 0.1 for f in F) >= 2
        cls.append("EXACT" if ex else "PARTIAL" if pa else "COLLAPSE")
    acc = [p["CVTR_accept"] for p in S1[r["key"]]["sides"][str(s)]]
    for c, a in zip(cls[1:], acc[1:]):
        C[(c, a)] += 1
    per.append({"key": r["key"], "side": s, "classes": cls, "cvtr": acc})
    C["genomes_any_accept_on_COLLAPSE"] += any(a and c == "COLLAPSE" for c, a in zip(cls[1:], acc[1:]))
    C["genomes_majority_accept_and_majority_COLLAPSE"] += sum(acc[1:]) >= 5 and cls[1:].count("COLLAPSE") >= 5
    C["genomes_any_PARTIAL"] += "PARTIAL" in cls[1:]
OUT.write_text(json.dumps({"counts": {str(k): v for k, v in C.items()}, "rows": per}, indent=0))
print({str(k): v for k, v in C.items()})
for p in per:
    if sum(p["cvtr"][1:]) >= 5 and p["classes"][1:].count("COLLAPSE") >= 5 or "PARTIAL" in p["classes"][1:]:
        print(p["key"], p["side"], "".join(c[0] for c in p["classes"]), "".join("1" if a else "0" for a in p["cvtr"]))
