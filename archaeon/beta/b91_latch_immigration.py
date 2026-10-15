"""B91 -- is the genome-specific RESET conversion (stepping-stone puzzle) BASIN CAPTURE? Latch immigration.

RESET lane (B80/B81/B83-B85): conversion to update-on-condition is genome-specific -- H_6913 5/6, H_6923 1/6,
L_6916 0/6 -- and is not predicted by quality, length, persist mode, one-step density or short neutral reach.
Keyed lane (B89): keeping the precursor basin occupied by immigration lifts d4 from 4/16 to 6/8. Here the same
intervention is applied in the relocating pulse world (ticks 48, P=4, Q=16).
- Gen 0 = 200 x the latch.
- After each reproduce(), 20 random non-elite members are replaced by fresh latch copies.
- SOLO, G=300, seeds 9101-9106. Readout = B77 parity: a population converts with >= 5 RESET-like genomes.
Arms: H_6923_IMM (baseline 1/6), L_6916_IMM (baseline 0/6).
PREDICTION (committed before running):
- H_6923_IMM converts >= 3/6 -- its low rate was basin capture;
- L_6916_IMM <= 1/6 -- a latch with no route is not rescued by an occupied basin.
If H_6923_IMM stays <= 1/6, its failure is not basin capture.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.beta.b79_evolved_latch_start import parity
from archaeon.beta.b80_latch_quality import latch_genome
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B91_latch_imm"
IMM = 20


def cell(job):
    key = job["arm"].replace("_IMM", "")
    m0, _ = latch_genome(key); rec = G.organism_record(copy.deepcopy(m0), None, 0); rec["origins"] = ["gen0_" + key]
    world, s, _ = B75.load(); w = NoClock(world); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b91", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x " + key, "verified_common": True})
    rng = SplitMix64(seed_from("b91.imm", job["seed"]))
    for g in range(job["G"]):
        cache.clear()
        for o in ev.pop:
            if id(o["manifest"]) not in cache:
                cache[id(o["manifest"])] = group_reloc([o["manifest"]], w, s, 8, P=B75.P_, Q=B75.Q_, mode="random")[0]
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
            idx = list(range(ev.elitism, len(ev.pop)))
            for _ in range(IMM):
                k = idx.pop(rng.randbelow(len(idx))); im = copy.deepcopy(rec); im["origins"] = ["immigrant_" + key]; ev.pop[k] = im
    pop = [o["manifest"] for o in ev.pop]
    (OUT / ("pop_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(pop), encoding="utf-8")
    n, best = parity(pop)
    return {"arm": job["arm"], "seed": job["seed"], "parity_reset_like": n, "parity_best": best, "converts": n >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 9101 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("H_6923_IMM", "L_6916_IMM") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 9101 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B91_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("converts", False) for r in rows if r.get("arm") == a) for a in ("H_6923_IMM", "L_6916_IMM")}
    summ["pred"] = summ["H_6923_IMM"] >= 3 and summ["L_6916_IMM"] <= 1
    print(json.dumps(summ))
    (OUT / "B91_result.json").write_text(json.dumps({"probe": "B91", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
