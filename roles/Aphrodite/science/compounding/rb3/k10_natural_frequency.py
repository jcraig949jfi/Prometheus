"""SPIKE K10 -- natural frequency, in the depth-3 body space (G5), of bodies
that are instances of the 26 G1-dependent NEW composed schemas (K9), vs
instances of G1 itself, and vs compositions of 8 random SHAM schemas (the
symmetric control). Body-level only (a lower bound on the task-level
question, which also needs the successor tribunal)."""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
for p in (HERE.parent / "rb1", ENG): sys.path.insert(0, str(p))
import a17, basis_v4 as G, tier3d as T3D, fair as FR, engine as E  # noqa: E401,E402
k9 = json.loads((HERE / "K9_COMPOSITION_DEPTH3.json").read_text())["rows"]
dep = [r["schema"] for r in k9 if not r["in_PRISTINE_universe"] and r["G5"]["NEW_V2"] and r["G5"]["accumulating"] >= 10]
print("G1-dependent NEW composed schemas:", len(dep)); print(dep)
G.BODY_SPACE = a17.g5_bodies(); T3D._STRUCT_TO_BODY = None
g5 = set(G.BODY_SPACE)
inst_dep = set(b for s in dep for b in T3D.instantiate(s))
inst_g1 = set(T3D.instantiate("(acc + {H})"))
# symmetric control: wraps of 8 sham schemas (a16/a17 sham construction, G4 bodies)
shams = [s["schema"] for s in json.loads((ENG / "A17_E1_RESULT_2026-09-26.json").read_text())["shams"]]
wrap_sham = set()
for s in shams:
    for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        for a in G.BODY_ATOMS:
            for w in (tmpl.format(s, a), tmpl.format(a, s)):
                wrap_sham |= set(T3D.instantiate(w))
n = len(g5)
res = {"G5_bodies": n, "G1_dependent_composed_instances": len(inst_dep), "frac": len(inst_dep) / n,
       "G1_instances": len(inst_g1), "sham_wrap_instances": len(wrap_sham), "sham_frac": len(wrap_sham) / n,
       "dep_schemas": dep}
print(json.dumps({k: v for k, v in res.items() if k != "dep_schemas"}, indent=1))
(HERE / "K10_NATURAL_FREQUENCY.json").write_text(json.dumps(res, indent=1))
