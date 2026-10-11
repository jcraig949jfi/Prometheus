"""B78 -- does a NATURAL CURRICULUM cross the update wall? (review packet F3-S3)

B75-B77: RESET-like (update-on-condition) genomes in the relocating pulse world from:
- random gen 0: 0/12;
- a stateless forager: 4/6 (median 3.5 genomes);
- a hand-seeded write-once LATCH: 6/6 (median ~102).
B69c/B69e: from random gen 0, the write-once latch IS reached in about half of populations in the PLAIN pulse world.
Curriculum: random gen 0, SOLO.
- Stage 1: G1=200 in the plain pulse world (P-boom, 24 ticks, P=4, no relocation).
- Stage 2: G2=300 in the relocating pulse world (48 ticks, P=4, Q=16, random relocation).
Same CMP3 search (N=200, E=8). Seeds 7801-7812.
Readouts:
- at the switch: does the population's best genome use state (full dependence >= .02 in the plain pulse world)?
- at the end: the B77 readout (every unique genome above the hand LATCH; RESET-like = full dependence >= .02 AND
  re-find >= .31).
PREDICTION (committed before running), hypothesis 'the curriculum crosses the wall':
- populations with >= 5 RESET-like genomes at the end >= 4/12;
- among them, more come from populations that had a state-using best at the switch than not.
The memory law's defender predicts <= 1/12.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock, load as load24
from archaeon.beta.b68_pulse_state_controls import group_pulse
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B78_curriculum"


def cell(job):
    w24_, s, _ = load24(); w24 = NoClock(w24_)
    w48_, _, _ = B75.load(); w48 = NoClock(w48_)
    stage = {"w": w24, "fit": lambda m: group_pulse([m], w24, s, 8, 4)[0]}
    cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, stage["w"], s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b78", foundry=FOUNDRY_C2)
    G1, G2 = job["G1"], job["G2"]; switch_dep = None
    for g in range(G1 + G2):
        if g == G1:
            sc24 = lambda m: sum(group_pulse([m], w24, s + 1000 + k, 16, 4)[0] for k in range(4)) / 4
            best = max(({id(o["manifest"]): o["manifest"] for o in ev.pop}).values(), key=sc24)
            lk = copy.deepcopy(best); lk["code_writable"] = False; lk["persist"] = "none"
            switch_dep = round(sc24(best) - sc24(lk), 4)
            stage["w"] = w48; stage["fit"] = lambda m: group_reloc([m], w48, s, 8, P=4, Q=16, mode="random")[0]
        cache.clear()
        for o in ev.pop:
            if id(o["manifest"]) not in cache:
                cache[id(o["manifest"])] = stage["fit"](o["manifest"])
        ev.evaluate_generation(episodes=[], last=(g == G1 + G2 - 1))
        if g < G1 + G2 - 1:
            ev.reproduce()
    pop = [o["manifest"] for o in ev.pop]
    (OUT / ("pop_%d.json" % job["seed"])).write_text(json.dumps(pop), encoding="utf-8")
    sc48 = lambda m: sum(group_reloc([m], w48, s + 1000 + k, 16, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    uniq = list({json.dumps(m["genome"]): m for m in pop}.values()); n_reset = 0; best = 0.0
    for m in uniq:
        r = sc48(m); best = max(best, r)
        if r <= .040:
            continue
        lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
        if r - sc48(lk) >= .02:
            rf = B75.refind(m, w48, s, w48_.R); n_reset += bool(rf is not None and rf >= .31)
    return {"seed": job["seed"], "switch_best_state_dep": switch_dep, "reset_like": n_reset, "best_reward": round(best, 4)}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    G1 = int(argv[0]) if argv else 200; G2 = int(argv[1]) if len(argv) > 1 else 300
    n = int(argv[3]) if len(argv) > 3 else 12; rows = []
    with ProcessPoolExecutor(max_workers=int(argv[2]) if len(argv) > 2 else 12) as ex:
        futs = {ex.submit(cell, {"seed": 7801 + i, "G1": G1, "G2": G2}): i for i in range(n)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 7801 + futs[f], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B78_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {"pops_ge5_reset": sum(r.get("reset_like", 0) >= 5 for r in rows),
            "of_which_state_at_switch": sum(r.get("reset_like", 0) >= 5 and (r.get("switch_best_state_dep") or 0) >= .02 for r in rows),
            "state_at_switch": sum((r.get("switch_best_state_dep") or 0) >= .02 for r in rows)}
    print(json.dumps(summ))
    (OUT / "B78_result.json").write_text(json.dumps({"probe": "B78", "G1": G1, "G2": G2, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
