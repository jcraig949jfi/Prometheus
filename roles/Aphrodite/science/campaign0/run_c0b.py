"""Campaign 0B run (PREREG_C0B): frozen assay under three pathologies + the delta table. TIER 2.

python run_c0b.py [--quick]
Rows -> ledgers/c0b_rows.jsonl (pathologies) and ledgers/c0b_delta_rows.jsonl.
Verdict -> summarize_c0b.py.
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import assay as A  # noqa: E402  -- FROZEN (6195af410)
import worlds as W  # noqa: E402
import worlds_0b as W0B  # noqa: E402
from run_c0 import MDE_SHIFTS, seed  # noqa: E402

QUICK = "--quick" in sys.argv
R = 10 if QUICK else 200
LS_0B = (32, 64)
LS_DELTA = (16, 32, 64)
DELTAS = (0.02, 0.03, 0.05)
L_DIR = HERE / ("ledgers_quick" if QUICK else "ledgers")


def job_path(args):
    path, key, L, rep = args
    obs = W0B.simulate_0b(W.WORLDS[key], L, random.Random(seed("0B", path, key, L, rep)), path)
    r = A.analyse(obs)
    return {"pathology": path, "world": key, "L": L, "rep": rep, "flags": sorted(r["flags"]),
            "ambiguous": r["ambiguous"], "modules": sorted(r["modules"]), "recovered": A.recovered(key, r),
            "d_vault_verdict": r["verdicts"]["D_VAULT"], "d_vault_mean": round(r["means"]["D_VAULT"], 5)}


def job_delta(args):
    kind, key, L, rep = args
    if kind == "mde":
        obs = W.simulate(W.mde_world(float(key)), L, random.Random(seed("dT", kind, key, L, rep)))
        wk = "W1"
    else:
        obs = W.simulate(W.WORLDS[key], L, random.Random(seed("dT", kind, key, L, rep)))
        wk = key
    out = []
    for d in DELTAS:
        r = A.analyse(obs, delta=d)
        out.append({"kind": kind, "world": key, "L": L, "rep": rep, "delta": d, "recovered": A.recovered(wk, r),
                    "d_vault_verdict": r["verdicts"]["D_VAULT"]})
    return out


def main():
    t0 = time.time()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True,
                                cwd=HERE).stdout.strip())
    L_DIR.mkdir(exist_ok=True)
    pj = [(p, k, L, r) for p in W0B.PATHOLOGIES for k in W.WORLDS for L in LS_0B for r in range(R)]
    dj = [("mde", str(s), L, r) for s in MDE_SHIFTS if s > 0 for L in LS_DELTA for r in range(R)]
    dj += [("world", k, L, r) for k in ("W4", "W6") for L in LS_DELTA for r in range(R)]
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        with open(L_DIR / "c0b_rows.jsonl", "w", encoding="utf-8", newline="\n") as fh:
            for row in pool.imap_unordered(job_path, pj, chunksize=4):
                fh.write(json.dumps(row, sort_keys=True) + "\n")
        with open(L_DIR / "c0b_delta_rows.jsonl", "w", encoding="utf-8", newline="\n") as fh:
            for rows in pool.imap_unordered(job_delta, dj, chunksize=4):
                for row in rows:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
    meta = {"head_sha": sha, "dirty_tree": dirty, "quick": QUICK, "R": R, "pathology_jobs": len(pj),
            "delta_jobs": len(dj), "runtime_s": round(time.time() - t0, 1)}
    (L_DIR / "C0B_RUN_META.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
