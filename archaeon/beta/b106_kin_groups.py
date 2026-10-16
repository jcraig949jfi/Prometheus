"""B106 -- KIN STRUCTURE: clonal groups at NORMAL mutation load (alternative to group reward / lowered load).

B98: at normal load (c=0), seeded signallers go extinct (break rate .31 >> s .046 under random groups).
B99: lowering the load rescues them.
Kin alternative: each genome is evaluated in a group of 4 COPIES OF ITSELF (rotating scout). Its fitness is its own
reward, which is identical across the clones. A signal now benefits only copies of the signaller, so selection on a
working signaller is roughly the whole-group benefit (~.25: COMPLETE own group .995 vs MUTE_OP .754, B97 world). That
approaches the ~.31 break rate.
Arms (c = 0, CMP3 N=200, E=4 episodes per clonal group, G=100, B97 world), seeds 10601-10604:
  SEEDED  gen 0 = 20% COMPLETE + 80% MUTE_OP (B98 condition: 0/4 kept signalling under random groups)
  MUTE    gen 0 = 200 x MUTE_OP (B95b/B97 condition: 0/12 restored under random groups)
Readout: the top 10's SIGNALS (B94 readout, hand partners); 'signalling' = >= 5 of the top 10 with SIGNALS > .05.
PREDICTION (committed before running), kin-selection hypothesis:
- SEEDED keeps signalling in >= 3/4 (vs 0/4 in B98);
- MUTE restores in >= 1/4.
If SEEDED is 0/4, clonal structure does not lift communication above the error threshold at normal load.
B106 RESULT = INSTRUMENT FAILURE (mine): with E=4 the four training episodes on world seed s all have pool 0 richest,
so the listeners default is already right and signalling has ZERO value (clonal COMPLETE = MUTE = 1.000).
B106b (argv[2] = 8): E=8 (the B103-B105 setting; there COMPLETE .995 vs MUTE .777), seeds 10611-10614. SAME prediction,
committed before the run.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
from archaeon.beta.b97_signal_headroom import sw
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B106_kin"


def cell(job):
    w, s = sw(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, job.get("E", 4), rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rc = G.organism_record(B92.man(list(COMPLETE)), None, 0); rc["origins"] = ["gen0_COMPLETE"]
    rm = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rm["origins"] = ["gen0_MUTE_OP"]
    n_c = 40 if job["arm"] == "SEEDED" else 0
    pop = [copy.deepcopy(rc) for _ in range(n_c)] + [copy.deepcopy(rm) for _ in range(200 - n_c)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=job.get("E", 4), branch="b106", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "%d COMPLETE + %d MUTE_OP" % (n_c, 200 - n_c), "verified_common": True})
    for g in range(job["G"]):
        cache.clear()
        for o in ev.pop:
            m = o["manifest"]
            if id(m) not in cache:
                cache[id(m)] = sum(group_rot([m] * 4, w, s, job.get("E", 4))) / 4
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    sigs = [readouts(m, w, s)[0] for m in tops]
    return {"arm": job["arm"], "seed": job["seed"], "top10_signalling": sum(x > .05 for x in sigs), "best_signals": sigs[0],
            "signalling": sum(x > .05 for x in sigs) >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        E_ = int(argv[2]) if len(argv) > 2 else 4; base = 10601 if E_ == 4 else 10611
        futs = {ex.submit(cell, {"arm": a, "seed": base + i, "G": int(argv[0]) if argv else 100, "E": E_}): (a, i) for a in ("SEEDED", "MUTE") for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 10601 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / ("B106_cells.jsonl" if E_ == 4 else "B106b_cells.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("signalling", False) for r in rows if r.get("arm") == a) for a in ("SEEDED", "MUTE")}
    summ["pred"] = summ["SEEDED"] >= 3 and summ["MUTE"] >= 1
    print(json.dumps(summ))
    (OUT / ("B106_result.json" if E_ == 4 else "B106b_result.json")).write_text(json.dumps({"probe": "B106", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
