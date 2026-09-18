"""Run Campaign 0C exactly as preregistered; one row per experiment. TIER 2.

python run_c0c.py [--quick]
"""
from __future__ import annotations

import hashlib
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
import secondary as S  # noqa: E402

QUICK = "--quick" in sys.argv
R = 20 if QUICK else 400
LS = (32, 64)
L_DIR = HERE / ("ledgers_quick" if QUICK else "ledgers")


def seed(*parts) -> int:
    return int(hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:15], 16)


def job(args):
    wname, L, rep = args
    w = {x.name: x for x in S.worlds()}[wname]
    lins = S.simulate(w, L, random.Random(seed("0C", wname, L, rep)))
    r = S.procedure(lins)
    tr = [l["truth"] for l in lins]
    nom = r["nominated"]
    conf = r["confirmed"]
    return {
        "world": wname, "kind": w.kind, "pi": w.pi, "J": w.J, "L": L, "rep": rep,
        "n_planted": sum(t["planted"] for t in tr), "n_true_carriers": sum(t["true_carrier"] for t in tr),
        "n_qualified": len(r["qualified"]), "n_nominated": len(nom), "n_confirmed": len(conf),
        "n_confirmed_true": sum(tr[i]["true_carrier"] for i in conf),
        "discovery": r["discovery"], "discovery_nmin1": r["discovery_nmin1"],
        "nominated_screen_minus_true": [round(r["screen_d"][i] - tr[i]["true_effect"], 5) for i in nom],
        "nominated_true_carrier": [tr[i]["true_carrier"] for i in nom],
        "confirmed_est": [[round(x, 5) for x in r["estimates"][i]] for i in conf],
        "confirmed_true": [round(tr[i]["true_effect"], 5) for i in conf],
    }


def main():
    t0 = time.time()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True,
                                cwd=HERE).stdout.strip())
    jobs = [(w.name, L, r) for w in S.worlds() for L in LS for r in range(R)]
    L_DIR.mkdir(exist_ok=True)
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as p, \
            open(L_DIR / "c0c_rows.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for row in p.imap_unordered(job, jobs, chunksize=8):
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    meta = {"head_sha": sha, "dirty_tree": dirty, "quick": QUICK, "R": R, "Ls": LS, "jobs": len(jobs),
            "runtime_s": round(time.time() - t0, 1)}
    (L_DIR / "C0C_RUN_META.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
