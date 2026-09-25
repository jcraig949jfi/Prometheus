"""X-POSITION (EXPLORE, MEASUREMENT; localization after X-RUNAWAY-TRANSPLANT = CLEAN_NULL).
Declared before running.

Runaway heredity (C-RUNAWAY) occurred only for specimen 7ae3; with the splice off, none of the
other 7 RECOMBINATION-axis specimens ran away (0/112). Candidate mechanism: runaway needs every
COPY to be a working copier from its new position; a donor that copies correctly only from one
half of the tape (hard-coded addresses) makes copies that cannot copy.

Measure, for each of the 16 H2 panel donor genomes, the P-11 randomized-victim assay with the
genome as donor in half a (copying into b) and in half b (copying into a): fresh registers,
the cell's slice budget and world-op mask, copy-mutation off. A genome is POSITION_INDEPENDENT
if the assay passes (majority of 3 draws) in BOTH directions.
Prediction (declared): 7ae3 is position-independent; specimens that never exceeded depth 1-2
are not. The measurement is deterministic; no evolution is run.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def main():
    import grammar as G
    import p11
    import world
    import z8
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    seen, rows = set(), []
    for b in man["bundles"]:
        if b["hypothesis_id"] != "H2" or b["specimen"] in seen:
            continue
        seen.add(b["specimen"])
        arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
        g = bytes.fromhex(arm["kwargs"]["implant_hex"])
        r = world.Runner(arm["cell"], 1, tier=arm["tier"], max_epochs=1)
        n = r.L
        tape = world._pow2(2 * n)
        rand = bytes((i * 97 + 13) % 256 for i in range(n))            # the partner's own bytes
        out = {}
        for label, ga, gb, vs in (("donor_in_a", g, rand, 1), ("donor_in_b", rand, g, 0)):
            res = p11.assay(z8, n=n, tape_len=tape, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0),
                            budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=0.0, victim_side=vs,
                            seed=("X-POSITION", b["specimen"], label))
            out[label] = {"pass": res["pass"], "draws_passed": res["draws_passed"],
                          "fid_final": [d["fid_final"] for d in res["draws"]]}
        rows.append({"specimen": b["specimen"], "axis": arm["cell"]["atlas_axis"],
                     "genome_len": len(g), "L": n, **out,
                     "position_independent": out["donor_in_a"]["pass"] and out["donor_in_b"]["pass"]})
    (HERE / "RESULTS.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print("%-32s %-18s a->b %-5s b->a %-5s  PI=%s" % (r["specimen"], r["axis"], r["donor_in_a"]["pass"],
                                                        r["donor_in_b"]["pass"], r["position_independent"]))
    print("position-independent:", sum(r["position_independent"] for r in rows), "of", len(rows))


if __name__ == "__main__":
    main()
