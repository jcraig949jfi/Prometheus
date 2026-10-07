"""B06 -- when slots stop scaling, does search find INDEXED memory (a loop over a table)? (Phase 2-B Beta)

B05's ruler separates SLOT2 (fixed register slots; K3 ~ .69) from GENERAL (a tag/value table on the tape with a
search loop; K3 = K4 = 1.0). A reasoning-primitive question: under pressure where every K in {2,3,4} occurs, does
the population discover the general mechanism (loop + indirect addressing = abstraction over slot count), or
accumulate slots? Training episodes per generation: E=18, six each of K=2, K=3, K=4 (D=1, 4-bit values), fresh
identities per generation (the CMP3 episode family). Readout on held-out K=2..6: GENERAL needs K5/K6 >= .90
(slots cannot reach unseen K5/K6 at all).

Arms (equal compute N=200, G=G_ (default 400), 12 seeds): BASE (grammar v0.4 descend) and RELOC (B03's
relocation-aware structural edits at .30). Generation 0: the CMP3 random population.

PREDICTION (before running): no GENERAL organism in either arm (0/24); best held-out K4 <= .80; RELOC's best
K-mixed reward >= BASE's in at least 8/12 paired seeds.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES
from archaeon.beta.b03_search_arms import make_descend
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
SPECS = {k: WorldSpec("W%d_K%d" % (k, k), K=k, value_bits=4) for k in (2, 3, 4, 5, 6)}


def train_eps(g, seed):
    eps = []
    for k in (2, 3, 4):
        eps += episodes_for(SPECS[k], CAMPAIGN_SEED, "train", g * 100003 + seed, 6)
    return eps


def heldout_profile(m):
    return {"K%d" % k: round(evaluate(m, episodes_for(SPECS[k], CAMPAIGN_SEED, "heldout", 7, 48), rng_seed=7)["reward"], 4)
            for k in SPECS}


def cell(job):
    arm, seed, G_ = job["arm"], job["seed"], job["G"]
    t0 = time.time()
    ev = Evolution(SPECS[3], REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=18, branch="b06",
                   foundry=FOUNDRY_C2, descend_fn=make_descend(arm))
    best, checkpoints = [], {}
    for g in range(G_):
        row = ev.evaluate_generation(episodes=train_eps(g, seed), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if g in (99, 199, 299, G_ - 1):
            checkpoints[str(g)] = heldout_profile(ev.scored[0][1]["manifest"])
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    prof = heldout_profile(elite)
    general = prof["K5"] >= .90 and prof["K6"] >= .90
    return {"arm": arm, "seed": seed, "final_profile": prof, "general": general, "checkpoints": checkpoints,
            "trace_best": best, "elite_manifest": elite, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 400
    jobs = [{"arm": a, "seed": s, "G": G_} for s in range(601, 613) for a in ("BASE", "RELOC")]
    rows = []
    with ProcessPoolExecutor(max_workers=24) as ex:
        futs = [ex.submit(cell, j) for j in jobs]
        for f in futs:
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("arm", "seed", "final_profile", "general", "wall_s")}), flush=True)
    summ = {a: {"general": sum(r["general"] for r in rows if r["arm"] == a),
                "mean_K4": round(sum(r["final_profile"]["K4"] for r in rows if r["arm"] == a) / 12, 4)} for a in ("BASE", "RELOC")}
    print(json.dumps(summ), flush=True)
    (OUT / "B06_result.json").write_text(json.dumps({"probe": "B06", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
