"""ARC3 pre-freeze SUPPLY feasibility for the corrected recurrence assay (C3R2).
Forensic, pre-donor, supply-only. For G1 and a pool of clean candidate schemas:
which compositions are GENUINE motifs, and how many have >= 8 T4-admissible
accumulating instance families?
GENUINE(w, S): not INERT (some accumulating instance's grid vector is outside
S's own instance vectors), not EQUAL/REFINES S or any re-expression of S
(relations closed over reexpressions -- W3's repair), NEW_V2 and NEW_TRAJ vs S's
span (ruler v2; G1 additionally excludes its ADDITIVE class).
"""
import json
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG.parent / "science" / "compounding" / "rb1"))
os.environ["A17_FASTEVAL"] = "1"
import a18  # noqa: E402

K_ADM = 8


def genuine(w, s):
    import ruler_v2 as R
    import tier3d as T3D
    inst = [b for b in T3D.instantiate(w) if R.accumulating(b)]
    held = {R.vec(b) for b in T3D.instantiate(s)}
    if not inst or all(R.vec(b) in held for b in inst):
        return False, inst
    for ref in R.reexpressions(s):
        rel = R.relations(w, ref)
        if rel["EQUAL"] or rel["REFINES"]:
            return False, inst
    sp = R.span_of_schema(s)
    tsp = R.traj_span(R.reexpression_bodies(s))
    ex = ("ADDITIVE",) if s == a18.G1 else ()
    v = R.new_v2(w, sp, inst, exclude_classes=ex)
    t = R.new_traj(w, tsp, inst)
    return bool(v["NEW_V2"] and t["NEW_TRAJ"]), inst


def job(args):
    a18.worker_init()
    import basis_v4 as G
    import tribunal_t4 as T4
    key, s = args
    rng = random.Random("APHRODITE/ARC3/C3R2-FEAS/" + s)
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    out = []
    for w in a18.compositions(s):
        ok, inst = genuine(w, s)
        if not ok:
            continue
        rng.shuffle(inst)
        adm = 0
        for b in inst[:40]:
            adm += T4.family_profile(("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals)))["admissible"]
            if adm >= K_ADM:
                break
        out.append({"motif": w, "admissible_found": adm, "instances": len(inst)})
    good = [m for m in out if m["admissible_found"] >= K_ADM]
    return {"key": key, "schema": s, "genuine": len(out), "genuine_usable": len(good),
            "usable": [m["motif"] for m in good]}


if __name__ == "__main__":
    import ruler_v2 as R
    import a20_c3 as B
    a18.use_world("W5")
    sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
    rng = random.Random("APHRODITE/ARC3/C3R2-FEAS/POOL/v1")
    pool, seen = {"G1": a18.G1}, {a18.G1}
    while len(pool) < 31:
        s = a18._random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        if B.clean(s, sp, tsp):
            pool["S%02d" % len(pool)] = s
    with ProcessPoolExecutor(5, initializer=a18.worker_init) as ex:
        rows = list(ex.map(job, list(pool.items())))
    rows.sort(key=lambda r: -r["genuine_usable"])
    (HERE / "GENUINE_MOTIFS.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r["key"], r["schema"], "genuine", r["genuine"], "usable(>=8 adm)", r["genuine_usable"])
