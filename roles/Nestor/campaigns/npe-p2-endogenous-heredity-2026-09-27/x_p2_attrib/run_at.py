"""X-P2-ATTRIB (EXPLORE, INSTRUMENT / success attribution for C-DENSE-COPY; P2 Block A, Thread T-ACQ-1(i)). Declared
before running. Theory-aware by date. Existing genomes only (LIGHT; no world runs).

Aphrodite slice 4's design attributed every success to the new coordinate; W1 did not. Question: do the competent
genomes that arose under the dense VM owe their competence to the one-byte copy alias -- does competence vanish when
the same genome is assayed on the stock VM, where 0xE5 / 0xE7 decode as NOP?
Sample: every DENSE-VM genome in the P2 corpus sample (delegates/corpus/q1_partial.jsonl) with rate_full >= 0.5
(fresh-start competent on the dense VM, 20 seeds), capped at 400 by a fixed-seed random draw.
Measurement: run_dd.assay_one, 20 seeds, same seeds and cell parameters, on (a) the dense VM and (b) the stock VM.
ATTRIBUTED iff rate_dense >= 0.5 and rate_stock < 0.1.
Classification: SIGNAL (success runs through the alias) if >= 90% of genomes are ATTRIBUTED; CLEAN_NULL (the alias is
not what makes them copy) if <= 20%; WEAK_SIGNAL otherwise. Reported separately: genomes that contain no alias byte
(expected to keep competence on the stock VM; a control that must not be ATTRIBUTED).
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))


def main():
    import world
    import z8 as plain
    import run_dc
    import run_dd
    import run_ds
    dense = run_dc.dense_z8()
    rows = [json.loads(l) for l in open(HERE.parent / "delegates" / "corpus" / "q1_partial.jsonl")]
    rows = [r for r in rows if r["vm"] == "DENSE" and r["rate_full"] >= 0.5]
    rng = random.Random(20260927)
    if len(rows) > 400:
        rows = rng.sample(rows, 400)
    runners = {}
    out = []
    for r in rows:
        if r["cell"] not in runners:
            a = run_ds.cells()[run_dd.CELLS[r["cell"]]]
            runners[r["cell"]] = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
        R = runners[r["cell"]]
        g = bytes.fromhex(r["hex"])
        rec = {"cell": r["cell"], "hex": r["hex"], "has_alias": any(b in (0xE5, 0xE7) for b in g)}
        for name, vm in (("dense", dense), ("stock", plain)):
            world.z8 = vm
            h, _ = run_dd.assay_one(world, R, g, ("X-P2-ATTRIB", r["hex"]), 20)
            rec["rate_" + name] = h / 20
        rec["attributed"] = rec["rate_dense"] >= 0.5 and rec["rate_stock"] < 0.1
        out.append(rec)
    world.z8 = plain
    test = [x for x in out if x["rate_dense"] >= 0.5]
    alias = [x for x in test if x["has_alias"]]
    noalias = [x for x in test if not x["has_alias"]]
    share = sum(x["attributed"] for x in test) / len(test) if test else 0.0
    cls = ("INVALID" if not test or any(x["attributed"] for x in noalias) else
           "SIGNAL" if share >= 0.9 else "CLEAN_NULL" if share <= 0.2 else "WEAK_SIGNAL")
    summ = {"classification": cls, "n": len(test), "attributed": sum(x["attributed"] for x in test),
            "attributed_share": round(share, 4), "with_alias": len(alias),
            "without_alias": len(noalias), "without_alias_attributed": sum(x["attributed"] for x in noalias),
            "mean_rate_dense": round(sum(x["rate_dense"] for x in test) / len(test), 4) if test else None,
            "mean_rate_stock": round(sum(x["rate_stock"] for x in test) / len(test), 4) if test else None}
    (HERE / "RESULTS.json").write_text(json.dumps(out))
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
