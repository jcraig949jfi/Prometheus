"""ARC3 Block G -- can G2 (a composition of G1) itself be composed into a G3, in the
current representation? Analytic, 1 core. For G2 = (v - (acc + {H})) and the other
K9b G1 compositions: count compositions wrap(G2, op, atom) with >= 2 in-space W5
instances, their accumulating instances, and the NEW verdict vs G2's own span."""
import json, sys
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG)); sys.path.insert(0, str(ENG.parent / "science" / "compounding" / "rb1"))
import a18, tier3d as T3D, engine as E, basis_v4 as G  # noqa: E401,E402
import ruler_v2 as R  # noqa: E402
a18.use_world("W5")
G2S = ["(v - (acc + {H}))", "math.gcd(abs((acc + {H})), abs(first))", "(last % (acc + {H}))",
       "(first - (acc + {H}))", "((acc + {H}) * v)"]
out = {}
for g2 in G2S:
    raw = []
    for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        for a in G.BODY_ATOMS:
            for w in (tmpl.format(g2, a), tmpl.format(a, g2)):
                inst = T3D.instantiate(w)
                raw.append((w, len(inst), sum(R.accumulating(b) for b in inst)))
    sp = R.span_of_schema(g2)
    usable = [(w, n, acc) for w, n, acc in raw if n >= 2]
    new = []
    for w, n, acc in usable:
        v = R.new_v2(w, sp, exclude_classes=())
        if v["NEW_V2"]:
            new.append((w, n, acc))
    out[g2] = {"wraps": len(raw), "with_ge2_instances": len(usable), "max_instances": max((n for _, n, _ in raw), default=0),
               "atom_filler_only": sum(1 for w, n, acc in usable if n <= 6), "NEW_vs_G2": len(new), "examples": new[:5]}
    print(g2, {k: v for k, v in out[g2].items() if k != "examples"}, new[:3])
Path(__file__).with_name("G3_REACH.json").write_text(json.dumps(out, indent=1))
