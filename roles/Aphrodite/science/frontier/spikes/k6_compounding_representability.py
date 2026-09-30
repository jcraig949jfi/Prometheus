"""SPIKE K6 -- can a schema that CONTAINS G1 = (acc + {H}) exist in G4?
For every primitive op and every atom position, wrap (acc + {H}) one level
deeper (the smallest DreamCoder-style 'abstraction on top of an abstraction')
and count in-space instantiations, split by filler depth (atom vs depth-1).
Instantiations with only ATOM fillers are specialisations of depth-1 bodies,
not uses of G1's hole."""
import json, sys
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import basis_v4 as G, engine as E, fair as FR, tier3d as T3D, tier3e as T3E  # noqa: E401,E402
rows = []
for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
    for atom in G.BODY_ATOMS:
        for s in (tmpl.format("(acc + {H})", atom), tmpl.format(atom, "(acc + {H})")):
            atom_f = [f for f in FR.LEVEL1 if f in G.BODY_ATOMS and T3D.in_space_body(s.replace("{H}", f))]
            deep_f = [f for f in FR.LEVEL1 if f not in G.BODY_ATOMS and T3D.in_space_body(s.replace("{H}", f))]
            rows.append({"schema": s, "atom_filler_inst": len(atom_f), "depth1_filler_inst": len(deep_f)})
tot = {k: sum(r[k] for r in rows) for k in ("atom_filler_inst", "depth1_filler_inst")}
g1 = T3D.instantiate("(acc + {H})")
print("G1-wrapping schemas:", len(rows), tot, "| G1 itself instantiations:", len(g1))
print("body depth limit: max depth over BODY_SPACE =", max(len(__import__('re').findall(r'\(', b)) for b in G.BODY_SPACE[:2000]))
Path(__file__).with_name("K6_COMPOUNDING.json").write_text(json.dumps({"rows": rows, "totals": tot, "g1_inst": len(g1)}, indent=1))
