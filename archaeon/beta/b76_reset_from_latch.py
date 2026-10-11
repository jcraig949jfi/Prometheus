"""B76 -- is RESET reachable ONE STEP CLOSER? Start evolution from the write-once LATCH (attack on B75).

B75: in the relocating pulse world (ticks 48, P=4, Q=16, random relocation) search reaches write-once state (8/12) but
never the update-on-condition RESET (0/12), although RESET is the best hand strategy (1.66x LATCH). Here gen 0 is
100 x LATCH_1 + 100 x LATCH_2 (the hand latch, already the second-best strategy). Reaching RESET then needs only
the counter + unlatch additions (~9 instructions inserted, coupled through registers r5/r6/r8/r9).
SOLO, CMP3 N=200, E=8, G=300, seeds 7601-7606 (6 cells; window budget). Readout = the B75 census (top 10:
RESET-like = full state dependence >= .02 AND re-find >= the LATCH/RESET midpoint (.31) AND reward > hand LATCH).
Also: does the LATCH survive (best reward >= .9 x hand LATCH)?
PREDICTION (committed before running; from the wiring-chain mechanism, B55-B57):
- RESET-like in <= 1/6 populations, even from a LATCH start;
- the latch survives (best >= .036) in >= 4/6.
If RESET-like >= 3/6, the B75 wall was distance from a reachable start, not the update class itself.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b68_pulse_state_controls import latch, man
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B76_from_latch"


def latch_gen0():
    out = []
    for i in (1, 2):
        rec = G.organism_record(man(latch(i), "regs"), None, 0); rec["origins"] = ["gen0_latch%d" % i]
        out += [copy.deepcopy(rec) for _ in range(100)]
    return out


def cell(job):
    world, s, _ = B75.load(); w = NoClock(world); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b76", foundry=FOUNDRY_C2,
                      init_pop=latch_gen0(), gen0_provenance={"fill": "100 x LATCH_1 + 100 x LATCH_2", "verified_common": True})
    for g in range(job["G"]):
        cache.clear()
        for o in ev.pop:
            if id(o["manifest"]) not in cache:
                cache[id(o["manifest"])] = group_reloc([o["manifest"]], w, s, 8, P=B75.P_, Q=B75.Q_, mode="random")[0]
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    pop = [o["manifest"] for o in ev.pop]
    (OUT / ("pop_%d.json" % job["seed"])).write_text(json.dumps(pop), encoding="utf-8")
    n, best = B75.census_pop(pop, w, s, world.R, job["refs"])
    return {"seed": job["seed"], "reset_like_top10": n, "best_reward": best}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); print("refs", json.dumps(refs), flush=True)
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"seed": 7601 + i, "G": G_, "refs": refs}): i for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 7601 + futs[f], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B76_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {"pops_with_reset_like": sum(r.get("reset_like_top10", 0) > 0 for r in rows), "latch_survives": sum(r.get("best_reward", 0) >= .036 for r in rows)}
    print(json.dumps(summ))
    (OUT / "B76_result.json").write_text(json.dumps({"probe": "B76", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
