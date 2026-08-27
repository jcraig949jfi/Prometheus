"""BINDING Phase-1 run for one real substrate.

Usage: python substrates/run_phase1.py S1_REG

Frozen by PREREG-PHASE1.md. After this run begins, no repair, no threshold
movement, no rerun-to-positive. Fatal defects: preserve, mark invalid, stop.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from d4core.pipeline import run_pipeline, _san  # noqa: E402
from substrates.vm_substrates import SUBSTRATES  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

REAL_CFG = {
    "seed": 12000,
    "census_n": 10_000,
    "op_parents": 1200,
    "op_reps": 4,
    "n_cross": 500,
    "rev_sample": 400,
    "n_walks": 64,
    "walk_len": 150,
    "n_ref": 48,
    "k_low": 4,
    "k_high": 4,
    "nav_budget": 1200,
    "nav_plan": [["N1_RESTART_WALK", 3], ["N2_HILLCLIMB", 5],
                 ["N3_NOVELTY", 2], ["N4_RECOMBINER", 5]],
    "coverage_seeds": 2,
    "coverage_budget": 3000,
    "ablation_seeds": 2,
    "cf_seeds": 2,
}


def main(name: str):
    cls = SUBSTRATES[name]
    sub = cls()
    t0 = time.time()

    # G0 expressivity witness (pre-census, part of the frozen substrate def)
    from d4core.interface import Meter
    m = Meter()
    m.set_component("expressivity")
    sub.bind_meter(m)
    w = sub.witness_genome()
    fw = sub.evaluate(w)
    witness = {"viable": bool(sub.viable(fw)),
               "outputs": [list(r[0]) for r in fw.rows]}
    print(f"[{name}] witness viable={witness['viable']}")
    if not witness["viable"]:
        out = {"substrate": name, "witness": witness,
               "gates": {"primary": "PHENOTYPE_POVERTY", "flags": ["PHENOTYPE_POVERTY"],
                         "note": "expressivity witness not viable"}}
        with open(os.path.join(OUT, f"{name}_results.json"), "w") as fh:
            json.dump(_san(out), fh, indent=1)
        return

    res = run_pipeline(
        sub, REAL_CFG, OUT, is_real=True,
        encoding_variant_factory=lambda: cls(encoded=True),
        radius_variant_factory=lambda: cls(radius2=True),
    )
    res["witness"] = witness
    res["wall_seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, f"{name}_results.json"), "w") as fh:
        json.dump(_san(res), fh, indent=1)
    print(f"[{name}] DONE in {res['wall_seconds']}s primary={res['gates']['primary']}")


if __name__ == "__main__":
    main(sys.argv[1])
