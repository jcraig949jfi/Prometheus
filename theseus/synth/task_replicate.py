"""THESEUS-35: fresh-seed replication of DISTRIBUTED cue carriers (post hoc in THESEUS-33).

Prereg: roles/Theseus/prereg/2026-10-08_distributed_replication/PREREG.md.

Stages (each checkpointed to its own jsonl; a restart skips finished ids):
  S1  J at V 8, k 8 (mean over task seeds 0, 1) for up to 100 viable genomes per arm
      (D = DEEP+VERY_DEEP children, R, P, B, C) of the run --ref, plus gate controls.
  S2  single-rule knockouts (task seed 0) on capable genomes (J >= .5), up to 40 per arm.
  S3  pairwise knockouts on S2 genomes with no single essential rule.
Carrier classes (drop >= .2 = essential): ONE-POINT (some single essential), DEGENERATE (no
single, some pair), DISTRIBUTED (no single, no pair).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import task_census as tc  # noqa: E402
from . import task_degen as tdg  # noqa: E402
from . import task_hard as th  # noqa: E402

ARMS = ("D", "R", "P", "B", "C")


def load(ref, rng, n):
    arms = {a: [] for a in ARMS}
    for l in open(f"theseus/entities/{ref}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("viable") and e.get("kind") == "mechanism" and e.get("lane") in ("DEEP", "VERY_DEEP"):
            arms["D"].append((e["id"], e["executableRepresentation"]))
    for l in open(f"theseus/controls/arms_{ref}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["viable"] and r["arm"] in ("R", "P", "B", "C"):
            arms[r["arm"]].append((r["id"], r["genome"]))
    out = []
    for a in ARMS:
        rows = arms[a]
        idx = sorted(rng.choice(len(rows), size=min(n, len(rows)), replace=False)) if rows else []
        out += [(a, rows[i][0], rows[i][1]) for i in idx]
    return out


def _stage(pool, path, items, fn):
    done = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            x = json.loads(l)
            done[x["id"]] = x
    todo = [(i, arg) for i, arg in items if i not in done]
    with open(path, "a", encoding="utf-8") as f:
        for (i, _), x in zip(todo, pool.imap(fn, [arg for _, arg in todo])):
            rec = {"id": i, **x}
            f.write(json.dumps(rec, separators=(",", ":")) + chr(10))
            f.flush()
            done[i] = rec
    return done


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261008)
    ctl = tc.controls(rng) + tdg.gate(np.random.default_rng(33))
    jobs = ctl + load(a.ref, rng, 100)
    group = {i: g for g, i, _ in jobs}
    genome = {i: x for _, i, x in jobs}
    t0 = time.time()
    with Pool(a.workers) as pool:
        s1 = _stage(pool, f"{out}/S1.jsonl", [(i, genome[i]) for _, i, _ in jobs], th._j2)
        krng = np.random.default_rng(7)
        ko_ids = []
        for arm in ARMS:
            cand = [i for _, i, _ in jobs if group[i] == arm and s1[i]["J_hard"] >= th.J_MIN_FOR_KO]
            idx = sorted(krng.choice(len(cand), size=min(th.KO_PER_ARM, len(cand)), replace=False)) if cand else []
            ko_ids += [cand[k] for k in idx]
        ko_ids += [i for _, i, _ in ctl if group[i].startswith("CTL:") and ("rr-" in i or "sr-" in i)]
        s2 = _stage(pool, f"{out}/S2.jsonl", [(i, (genome[i], s1[i]["J_seeds"][0])) for i in ko_ids], th._ko)
        s3_ids = [i for i in ko_ids if s2[i]["carrier_size"] == 0]
        s3 = _stage(pool, f"{out}/S3.jsonl", [(i, genome[i]) for i in s3_ids], tdg.job)
    summ = {"ref": a.ref, "wall_s": round(time.time() - t0, 1), "groups": {}}
    for grp in sorted(set(group.values())):
        ids = [i for i in group if group[i] == grp]
        J = np.array([s1[i]["J_hard"] for i in ids])
        kos = [i for i in ko_ids if group[i] == grp]
        one = sum(s2[i]["carrier_size"] >= 1 for i in kos)
        deg = sum(1 for i in kos if s2[i]["carrier_size"] == 0 and s3[i]["critical_pairs"])
        dist = sum(1 for i in kos if s2[i]["carrier_size"] == 0 and not s3[i]["critical_pairs"])
        summ["groups"][grp] = {"n": len(ids), "mean_J": float(J.mean()), "median_J": float(np.median(J)),
                               "capable_ko_n": len(kos), "one_point": one, "degenerate": deg, "distributed": dist}
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
