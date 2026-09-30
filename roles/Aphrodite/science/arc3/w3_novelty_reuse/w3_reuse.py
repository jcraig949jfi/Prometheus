"""W3 PART 2 -- re-score the C2 (AMENDMENT 19) ladder REUSE / CAPABILITY / SOLVED rungs
under alternative, defensible reuse definitions. FORENSIC: historical results stand.
Reads engine/A19_C2/*.  Also computes, analytically (no search), whether a selected
schema's instance set contains a program EXTENSIONALLY equal to each transfer family's
generating program (same init/final, some instance body; equality on the RULER v2
trajectory battery plus the family's own length-4..9 lists).
Usage: python w3_reuse.py     (single core; ~minutes)
"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
C2 = ROOT / "engine" / "A19_C2"
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine" / "accel"))
ESCROW = 250000
ON_PATH = ["G1", "SHAM_0", "SHAM_1"]
HELD = {"G1": "G1", "G1_NC": "G1", "SHAM_0": "SHAM_0", "SHAM_1": "SHAM_1", "OFF_0": "OFF_0", "P": "P"}


def jl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def ladders(donors, trans, src):
    out = {}
    for d in donors:
        if not d["catalog"].startswith("CON"):
            continue
        rows = [t for t in trans if t["catalog"] == d["catalog"] and t["arm"] == d["arm"]]
        held = HELD[d["arm"]]
        grp = "CON:" + held if held in ON_PATH else None
        comp = bool(d["COMPOSES_held"])
        sel_any = d["selected_schema"] is not None

        def fams(pred, own_only):
            return sorted({t["family"] for t in rows if (not own_only or grp is None or src[t["family"]] == grp)
                           for c in t["cells"] if pred(c)})

        lit = lambda c: c["SELECTED"]["qualified"] and c["SELECTED"]["coord"] == "g2_new"   # noqa: E731
        newsolve = lambda c: c["SELECTED"]["qualified"] and not c["START"]["qualified"]    # noqa: E731
        cap = lambda c: (c["SELECTED"]["qualified"] and c["SELECTED"]["charge"] <= ESCROW  # noqa: E731
                         and "ladder_charge" in c["START"] and "ladder_charge" in c["PRISTINE"]
                         and not c["START"].get("ladder_qualified") and not c["PRISTINE"].get("ladder_qualified"))
        cheaper = lambda c: (c["SELECTED"]["qualified"] and (not c["START"]["qualified"]   # noqa: E731
                             or c["SELECTED"]["charge"] < c["START"]["charge"]))
        dearer = lambda c: (c["START"]["qualified"] and c["SELECTED"]["qualified"]         # noqa: E731
                            and c["SELECTED"]["charge"] > c["START"]["charge"])
        lost = lambda c: c["START"]["qualified"] and not c["SELECTED"]["qualified"]         # noqa: E731
        r = {"selected": d["selected_schema"], "COMPOSES_held": comp,
             # frozen definitions (reproduced)
             "SOLVED_frozen": bool(fams(newsolve, True)),
             "REUSABLE_frozen": comp and len(fams(lit, True)) >= 2,
             "CAP_frozen": comp and len(fams(cap, True)) >= 2,
             # alternatives
             "R_lit_anygroup_fams": fams(lit, False),
             "R_newsolve_anygroup_fams": fams(newsolve, False),
             "R_cap_anygroup_fams": fams(cap, False),
             "R_cheaper_anygroup_fams": fams(cheaper, False),
             "R_dearer_anygroup_fams": fams(dearer, False),
             "R_lost_anygroup_fams": fams(lost, False),
             "any_selection": sel_any}
        r["REUSABLE_anygroup"] = comp and len(r["R_lit_anygroup_fams"]) >= 2
        r["REUSABLE_anygroup_ge1"] = comp and len(r["R_lit_anygroup_fams"]) >= 1
        r["CAP_anygroup"] = comp and len(r["R_cap_anygroup_fams"]) >= 2
        r["SOLVED_anygroup"] = bool(r["R_newsolve_anygroup_fams"])
        r["NEWSOLVE_anyselection_ge1"] = sel_any and bool(r["R_newsolve_anygroup_fams"])
        out.setdefault(d["arm"], {})[d["catalog"]] = r
    return out


def extensional(donors, roles):
    import a18
    a18.use_world("W5")
    import tier3d as T3D
    import fasteval as FE
    rng = random.Random("W3/EXT/v1")
    bat = [[rng.randint(2, 30) for _ in range(rng.randint(2, 12))] + [rng.randint(3, 97)] for _ in range(60)]

    def run(init, body, final):
        return tuple(FE.run_program(("fold", init, body, final), x, True) for x in bat)
    res = {}
    for d in donors:
        s = d["selected_schema"]
        if not s or not d["catalog"].startswith("CON"):
            continue
        key = "CON/" + d["catalog"][3:]
        inst = T3D.instantiate(s)
        fam = [f for f in roles[key]["families"] if f["role"] in ("TRANSFER", "VALIDATE")]
        hits = []
        for f in fam:
            target = run(f["init"], f["body"], f["final"])
            lit = f["body"] in set(inst)
            ext = lit or any(run(f["init"], b, f["final"]) == target for b in inst)
            if ext:
                hits.append({"family": f["name"], "role": f["role"], "source": f["source"], "literal": lit})
        res["%s/%s" % (d["catalog"], d["arm"])] = {"selected": s, "n_inst": len(inst), "matches": hits}
        print(d["catalog"], d["arm"], s, [(h["family"], h["role"], h["source"], h["literal"]) for h in hits],
              flush=True)
    return res


if __name__ == "__main__":
    donors = jl(C2 / "A18_DONORS_2026-09-28.jsonl")
    trans = jl(C2 / "A18_TRANSFER_2026-09-28.jsonl")
    roles = json.loads((C2 / "A18_ROLES_2026-09-28.json").read_text())
    src = {f["name"]: f["source"] for v in roles.values() for f in v["families"]}
    lad = ladders(donors, trans, src)
    counts = {}
    for arm, reps in lad.items():
        counts[arm] = {k: sum(1 for r in reps.values() if r[k]) for k in
                       ("SOLVED_frozen", "REUSABLE_frozen", "CAP_frozen", "SOLVED_anygroup", "REUSABLE_anygroup",
                        "REUSABLE_anygroup_ge1", "CAP_anygroup", "NEWSOLVE_anyselection_ge1")}
    frozen = json.loads((C2 / "A18_C1_RESULT_2026-09-28.json").read_text())["per_supply"]["CON"]["ladder_counts"]
    check = {a: (frozen[a]["SOLVED"], frozen[a]["REUSABLE"], frozen[a]["CAPABILITY_EXPANDING"]) ==
             (counts[a]["SOLVED_frozen"], counts[a]["REUSABLE_frozen"], counts[a]["CAP_frozen"]) for a in counts}
    print("frozen counts reproduced:", check)
    print(json.dumps(counts, indent=1))
    ext = extensional(donors, roles)
    (HERE / "W3_REUSE_C2.json").write_text(json.dumps({"reproduces_frozen": check, "counts": counts,
                                                        "ladders": lad, "extensional_matches": ext},
                                                       indent=1, default=str))
