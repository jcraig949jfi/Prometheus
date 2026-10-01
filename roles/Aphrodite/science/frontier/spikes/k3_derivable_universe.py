"""SPIKE K3 -- the derivable-schema universe (Block F, representation ceiling
of the IMPROVEMENT MECHANISM rather than of the task grammar).

tier3d.derive_schemas keeps an LGG of two member bodies (from two DISTINCT
classes) iff it has exactly one hole and a non-hole root. Member bodies can
only come from the donor's library coverage. So the set of schemas that the
fixed mechanism could EVER derive is bounded by single-hole LGGs over pairs of
coverage bodies. We enumerate that universe for PRISTINE coverage (H2, 422
bodies over acc and v only) and for L1 coverage (+ the 161 derived_0 = G1
instantiations), keep schemas with >= 2 in-space instantiations, and label
each SEMANTICALLY_NEW (non-G1) or not. Pairs are not filtered by class
(a class split is necessary for derivation), so this is an UPPER bound.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import a17  # noqa: E402
import fair as FR  # noqa: E402
import identity as I  # noqa: E402
import tier3d as T3D  # noqa: E402
import tier3e as T3E  # noqa: E402


def universe(bodies):
    terms = [I.normalise(I.parse(b)) for b in bodies]
    found = Counter()
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            g, table = T3D.lgg(terms[i], terms[j])
            if len(table) != 1 or g[0].startswith("hole"):
                continue
            found[T3D.schema_src(g)] += 1
    return found


if __name__ == "__main__":
    L1 = a17.L1_entries()
    pr = list(dict.fromkeys(FR.pristine().entries[0]["bodies"]))
    g1b = [b for e in L1 if e["name"] == "derived_0" for b in e["bodies"]]
    out = {}
    for tag, bodies in (("PRISTINE", pr), ("L1", list(dict.fromkeys(g1b + pr)))):
        u = universe(bodies)
        rows = []
        for s, n in u.items():
            inst = T3D.instantiate(s)
            if len(inst) < 2:
                continue
            sn = T3E.semantically_new(s)
            rows.append({"schema": s, "pairs": n, "instantiations": len(inst),
                         "SEMANTICALLY_NEW": sn["SEMANTICALLY_NEW"], "n_new_bodies": sn["n_new_mechanism_bodies"]})
        new = [r for r in rows if r["SEMANTICALLY_NEW"]]
        top = Counter()
        for r in new:
            top[r["schema"].split("(")[0] + r["schema"][:12]] += 0
        out[tag] = {"coverage_bodies": len(bodies), "single_hole_schemas": len(u),
                    "with_2plus_instantiations": len(rows), "semantically_new": len(new),
                    "new_examples": sorted(new, key=lambda r: -r["pairs"])[:40],
                    "old_examples": sorted([r for r in rows if not r["SEMANTICALLY_NEW"]], key=lambda r: -r["pairs"])[:15]}
        print(tag, {k: v for k, v in out[tag].items() if not k.endswith("examples")})
        print("  NEW top:", [(r["schema"], r["pairs"]) for r in out[tag]["new_examples"][:25]])
    Path(__file__).with_name("K3_DERIVABLE_UNIVERSE.json").write_text(json.dumps(out, indent=1))
