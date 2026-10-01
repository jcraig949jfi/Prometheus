"""SPIKE K9 (RB-3 follow-up to K8 + RB-1): does composition become a genuine,
G1-DEPENDENT source of novelty once the instantiation space is depth-3 (G5,
a17.g5_bodies, 465,954 bodies)?

For each of the 84 wrap(G1, op, atom) schemas (K6), in G4 vs G5:
  instantiations, accumulating instantiations, NEW_V2 vs G1's span
  (ruler v2), and whether the schema is derivable from PRISTINE coverage
  alone (in the K3 PRISTINE single-hole universe, compared modulo
  commutativity via ruler_v2._term).
Stages: representable -> derivable-with-G1-only (not PRISTINE) -> NEW_V2 ->
size (accumulating instances >= 10 counts as a real abstraction).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPK = HERE.parents[1] / "frontier" / "spikes"
ENG = HERE.parents[2] / "engine"
for p in (HERE.parent / "rb1", ENG, SPK):
    sys.path.insert(0, str(p))
import ruler_v2 as R      # noqa: E402
import a17                # noqa: E402
import basis_v4 as G      # noqa: E402
import fair as FR         # noqa: E402
import tier3d as T3D      # noqa: E402
import k3_derivable_universe as K3  # noqa: E402

G1 = "(acc + {H})"


def canon(s):
    return repr(R._term(s))


def measure(wraps, space_tag):
    sp = R.span_of_schema(G1)
    rows = []
    for w in wraps:
        inst = T3D.instantiate(w)
        r = R.verdict(w, G1, sp, inst)
        rows.append({"schema": w, "space": space_tag, "inst": len(inst), "accumulating": r["accumulating"],
                     "novel": r["novel"], "NEW_V2": r["NEW"], "classes": r["novel_classes"],
                     "REFINES": r["REFINES"], "COMPOSES": r["COMPOSES"]})
    return rows


if __name__ == "__main__":
    wraps = [r["schema"] for r in json.loads((SPK / "K6_COMPOUNDING.json").read_text())["rows"]]
    pr = list(dict.fromkeys(FR.pristine().entries[0]["bodies"]))
    pristine_universe = {canon(s) for s in K3.universe(pr)}
    g4 = measure(wraps, "G4")
    # switch the instantiation space to G5 (depth-3). Only in-process; no file is modified.
    G.BODY_SPACE = a17.g5_bodies()
    T3D._STRUCT_TO_BODY = None
    R.vec.cache_clear()
    g5 = measure(wraps, "G5")
    out = []
    for a, b in zip(g4, g5):
        out.append({"schema": a["schema"], "in_PRISTINE_universe": canon(a["schema"]) in pristine_universe,
                    "G4": {k: a[k] for k in ("inst", "accumulating", "novel", "NEW_V2")},
                    "G5": {k: b[k] for k in ("inst", "accumulating", "novel", "NEW_V2", "classes")}})
    stages = {
        "representable_G5": sum(o["G5"]["inst"] >= 2 for o in out),
        "G1_dependent (not PRISTINE-derivable)": sum(not o["in_PRISTINE_universe"] for o in out),
        "G1_dependent & NEW_V2 (G5)": sum((not o["in_PRISTINE_universe"]) and o["G5"]["NEW_V2"] for o in out),
        "... & accumulating>=10 (G5)": sum((not o["in_PRISTINE_universe"]) and o["G5"]["NEW_V2"]
                                          and o["G5"]["accumulating"] >= 10 for o in out),
        "same, in G4": sum((not o["in_PRISTINE_universe"]) and o["G4"]["NEW_V2"] and o["G4"]["accumulating"] >= 10
                           for o in out),
    }
    (HERE / "K9_COMPOSITION_DEPTH3.json").write_text(json.dumps({"stages": stages, "rows": out}, indent=1))
    print(json.dumps(stages, indent=1))
    for o in sorted(out, key=lambda o: -o["G5"]["accumulating"])[:30]:
        print("%-44s PRIST=%-5s G4 acc=%3d new=%-5s | G5 inst=%4d acc=%4d novel=%4d NEW=%-5s %s" % (
            o["schema"], o["in_PRISTINE_universe"], o["G4"]["accumulating"], o["G4"]["NEW_V2"],
            o["G5"]["inst"], o["G5"]["accumulating"], o["G5"]["novel"], o["G5"]["NEW_V2"], o["G5"]["classes"]))
