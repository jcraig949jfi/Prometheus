"""N4 exactness receipt: cuTensorNet tt_digits logits vs genomes.TTDigits.ref_logits.

Sweep: D (obs features; 4D cores) x rank r x genome seeds, B rows each, honest (stride 1) and the stride-2
cheat. Per cell: clear rows, argmax mismatches on clear rows, row-normalised max abs error (clear and all).
Correctness only: no timing fields (no GPU lease).

Runs in WSL (~/lab/nv-venv-t). Rows go to a JSONL outside F: (hot data); the Windows side copies it into
primordial/ledger/rows/T/ and commits it with `python -m primordial.fabric.rows commit`.

usage: python -m primordial.nv.tensornet.n4_oracle [--out ~/lab/hot/N4-oracle.jsonl] [--quick]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.nv.tensornet import tt_cutn as tn

EXP_ID = "N4-cutensornet-tt-digits-oracle"
STATUS = "record"


def cell(D: int, r: int, seed: int, B: int, stride: int) -> dict:
    fam = gm.TTDigits(D=D, A=8)
    fam.rank = r
    rng = np.random.default_rng(seed)
    g1 = fam.one(fam.init(rng, 1), 0)
    obs = rng.integers(0, 65536, size=(B, D), dtype=np.int64)
    res = tn.compare_to_oracle(fam, g1, obs, tn.contract_logits(g1, obs, stride=stride))
    return {"exp_id": EXP_ID, "status": "cheat" if stride == 2 else STATUS, "family": "tt_digits",
            "D": D, "cores": 4 * D, "r": r, "A": 8, "genome_seed": seed, "B": B, "stride": stride,
            "genome_bytes": fam.nbytes, **res}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/lab/hot/N4-oracle.jsonl"))
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--status", default="record", choices=["record", "dev"])
    ap.add_argument("--git", default="", help="HEAD sha (git cannot run from WSL on a Windows worktree)")
    a = ap.parse_args(argv)
    global STATUS
    STATUS = a.status
    Ds, rs, seeds, B = ([3, 5], [3], [0, 1], 256) if a.quick else ([3, 5, 8, 16], [3, 8], [0, 1, 2, 3], 1024)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    import cupy as cp
    import cuquantum
    git = a.git
    rows = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"exp_id": EXP_ID, "status": "record", "kind": "header", "git": git,
                             "ts": time.strftime("%Y%m%dT%H%M%S"), "cuquantum": cuquantum.__version__,
                             "cupy": cp.__version__, "device": cp.cuda.runtime.getDeviceProperties(0)["name"].decode(),
                             "pm_tag": os.environ.get("PM_TAG"), "dtype": "float64"}) + "\n")
        for D in Ds:
            for r in rs:
                for s in seeds:
                    for stride in (1, 2):
                        row = cell(D, r, 1000 * D + 10 * r + s, B, stride)
                        rows.append(row)
                        fh.write(json.dumps(row) + "\n")
                        fh.flush()
        honest = [x for x in rows if x["stride"] == 1]
        cheat = [x for x in rows if x["stride"] == 2]
        summ = {"exp_id": EXP_ID, "status": "record", "kind": "summary",
                "honest_cells": len(honest), "honest_argmax_mismatch_clear": sum(x["argmax_mismatch_clear"] for x in honest),
                "honest_clear_rows": sum(x["n_clear"] for x in honest),
                "honest_max_abs_err_rownorm_all": max(x["max_abs_err_rownorm_all"] for x in honest),
                "cheat_cells": len(cheat), "cheat_cells_caught": sum(x["argmax_mismatch_clear"] > 0 for x in cheat),
                "cheat_min_mismatch_clear": min(x["argmax_mismatch_clear"] for x in cheat)}
        fh.write(json.dumps(summ) + "\n")
    print(json.dumps(summ))
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
