"""CONFIRMATION batch generation straight into the vault (A5). Run ONLY after a candidate is frozen in the vault.

Worlds come from the CONFIRMATION seed namespace. For every world the labels (Certificate A at two seeds -- the v0.3
seed-stability rule -- Certificate B-linear, T3-DOWN) are written to a vault batch file and nowhere else. The public
side keeps only the world SPECS (family, knobs, k, stratum), which a frozen predictor needs to compute its
prediction. Nothing in this module prints or returns a label.

Strata (DESIGN v0.2 s3 / v0.3): S0-A = challenge proposal Q, kept only if T3-DOWN registers (REGISTERED filter;
T3-DOWN uses no label); S0-B = natural proposal P, unfiltered. Every Q draw and its filter outcome is recorded
(A7: Z_A per family).

    python -m prometheus.cosmos.c4.confirm <vault_dir> <batch> <n_A_per_family> <n_B_per_family> [workers]
"""
from __future__ import annotations

import json
import sys
from multiprocessing import get_context
from pathlib import Path

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c4 import exp01 as E
from prometheus.cosmos.c4 import firewall as FW
from prometheus.cosmos.c4.baselines import t3_down
from prometheus.cosmos.c4.cert_b import b_use
from prometheus.cosmos.hashing import h


def _label(spec):
    sys_, task = E.build(spec["family"], spec["knobs"], spec["k"])
    wid = spec["world_id"]
    a1 = certify(sys_, task, seed=int(wid[8:16], 16))["class"]
    a2 = certify(sys_, task, seed=int(wid[24:32], 16))["class"]
    a = a1 if a1 == a2 else "INDETERMINATE"
    b = b_use(sys_, task, "linear", seed=int(wid[16:24], 16))["functional"]
    return {"world_id": wid, "A": a, "A_seeds": [a1, a2], "B": bool(b)}


def _t3(spec):
    sys_, task = E.build(spec["family"], spec["knobs"], spec["k"])
    return t3_down(sys_, task)


def specs(batch: int, n_a: int, n_b: int, max_draws: int = 20):
    """S0-B: n_b natural worlds per family; S0-A: draw from Q until n_a REGISTERED worlds per family (or the draw
    budget runs out). Returns (specs, q_draw_log)."""
    out, qlog = [], []
    for fi, fam in enumerate(E.FAMILIES):
        for i in range(n_b):
            s = E.sample_world(fam, FW.split_seed("CONFIRMATION", batch, fi * 100000 + i), "P")
            s.update({"stratum": "S0-B", "world_id": h({"C": batch, "S": "B", "f": fam, "i": i, "w": s})})
            out.append(s)
        got, i = 0, 0
        while got < n_a and i < n_a * max_draws:
            s = E.sample_world(fam, FW.split_seed("CONFIRMATION", batch, 50000 + fi * 100000 + i), "Q")
            reg = _t3(s) == "FUNCTIONAL"
            qlog.append({"family": fam, "i": i, "registered": reg})
            if reg:
                s.update({"stratum": "S0-A", "world_id": h({"C": batch, "S": "A", "f": fam, "i": i, "w": s})})
                out.append(s)
                got += 1
            i += 1
    return out, qlog


def main(vault_dir: str, batch: int, n_a: int, n_b: int, workers: int = 3):
    v = FW.Vault(Path(vault_dir))
    sp, qlog = specs(batch, n_a, n_b)
    pub = Path(vault_dir) / f"SPECS_batch_{batch:03d}.json"
    pub.write_text(json.dumps({"specs": sp, "q_draws": qlog}, default=float))
    with get_context("spawn").Pool(workers, maxtasksperchild=4) as pool:
        labs = pool.map(_label, sp)
    by = {r["world_id"]: r for r in labs}
    ids = [s["world_id"] for s in sp]
    y = [int(by[i]["A"] == "FUNCTIONAL") if by[i]["A"] in ("FUNCTIONAL", "PASSIVE", "NONE") else -1 for i in ids]
    v.deposit(batch, ids, y, meta={"B": [int(by[i]["B"]) for i in ids], "A_raw": [by[i]["A"] for i in ids],
                                   "stratum": [s["stratum"] for s in sp], "family": [s["family"] for s in sp]})
    print(json.dumps({"deposited": len(ids), "batch": batch}))


if __name__ == "__main__":
    a = sys.argv
    main(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]) if len(a) > 5 else 3)
