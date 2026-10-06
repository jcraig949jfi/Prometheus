"""B01b -- one edit from the summit: does the CMP3 GA get back, and does a waiting-time model predict when?

B01-D (2026-10-07) failed its prediction: from k=1-damaged solver copies the GA re-summited in 1/3 cells, and 0/12
for k >= 2. Defect in B01-D: the four k=1 copies were 3 lethal + 1 shelf-level child, so cells effectively started
from ONE plateau organism. B01b conditions on the plateau directly.

Design:
  1. Sample single-operator children of the solver; keep up to 12 distinct ones whose held-out score is
     shelf-level, [.45, .62) ("plateau neighbours": one edit away, behaviourally on the shelf).
  2. For each, the REVERSAL RATE r = share of 5,000 single-operator children that score >= .90 held-out.
  3. For each, one GA cell (CMP3 config: N=200, E=16, E0, FOUNDRY_C2), gen 0 = 4 copies + the common fill,
     G = 60. Record first confirmed summit.
  Waiting-time model (written before running): a plateau lineage holding share s of the population produces about
  s*N*r summit children per generation; if they are kept (elitism 4 keeps any train-best child), P(summit by G) =
  1 - exp(-sum_g s_g N r). With s ~ 4/200 decaying, cells with r >= 1e-3 should summit early and cells with
  r < 1e-4 should mostly not. PREDICTION: Spearman(r, summit indicator) > 0.5 across the 12 cells.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SOLVER, SUMMIT, TARGET, heldout, manifest
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"


def neighbours(max_n=12, scan=3000):
    parent = G.organism_record(manifest(SOLVER), None, 0)
    seen, out = set(), []
    for s in range(scan):
        child, rec = descend(parent, 9_000_000 + s)
        g = tuple(child["manifest"]["genome"])
        if g in seen:
            continue
        seen.add(g)
        r = heldout(child["manifest"])["reward"]
        if .45 <= r < .62:
            out.append({"seed": 9_000_000 + s, "op": rec["operators"][0].get("operator"), "heldout": round(r, 4),
                        "manifest": child["manifest"]})
            if len(out) >= max_n:
                break
    return out


def reversal_rate(m, n=5000):
    org = G.organism_record(m, None, 0)
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 7, 48)
    hit = 0
    for s in range(n):
        child, _ = descend(org, 5_000_000 + s)
        if evaluate(child["manifest"], eps, rng_seed=7)["reward"] >= SUMMIT:
            hit += 1
    return hit / n


def cell(job):
    t0 = time.time()
    m = job["manifest"]
    r = reversal_rate(m)
    init, prov = common_fill(CAMPAIGN_SEED, job["cell_seed"], 200, [m] * 4, tag="plateau", foundry=FOUNDRY_C2)
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["cell_seed"], N=200, E=16, branch="b01b",
                   foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", job["cell_seed"], 48)
    first, share = None, []
    for g in range(60):
        row = ev.evaluate_generation(last=(g == 59))
        share.append(row.get("origin_shares", {}).get("plateau", 0.0))
        if first is None and row["best_reward"] >= SUMMIT and evaluate(ev.scored[0][1]["manifest"], eps, rng_seed=7)["reward"] >= SUMMIT:
            first = g
            break
        if g < 59:
            ev.reproduce()
    return {"i": job["i"], "op": job["op"], "neighbour_heldout": job["heldout"], "reversal_rate": r,
            "first_summit_gen": first, "plateau_share_trace": share[:20], "wall_s": round(time.time() - t0, 1)}


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); rk = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                rk[o[k]] = (i + j) / 2
            i = j + 1
        return rk
    rx, ry = rank(x), rank(y); n = len(x); mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** .5
    return num / den if den else float("nan")


def main(argv):
    OUT.mkdir(exist_ok=True)
    nb = neighbours()
    print("neighbours", len(nb), [(x["op"], x["heldout"]) for x in nb], flush=True)
    jobs = [{"i": i, "op": x["op"], "heldout": x["heldout"], "manifest": x["manifest"], "cell_seed": 201 + i} for i, x in enumerate(nb)]
    with ProcessPoolExecutor(max_workers=12) as ex:
        rows = list(ex.map(cell, jobs))
    for r in rows:
        print(json.dumps({k: r[k] for k in ("i", "op", "neighbour_heldout", "reversal_rate", "first_summit_gen", "wall_s")}), flush=True)
    rho = spearman([r["reversal_rate"] for r in rows], [1 if r["first_summit_gen"] is not None else 0 for r in rows])
    out = {"probe": "B01b", "n_cells": len(rows), "summited": sum(r["first_summit_gen"] is not None for r in rows),
           "spearman_r_vs_summit": rho, "rows": rows, "neighbour_manifests": [x["manifest"] for x in nb]}
    print("summited %d/%d spearman %.3f" % (out["summited"], len(rows), rho), flush=True)
    (OUT / "B01b_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
