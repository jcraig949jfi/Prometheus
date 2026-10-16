"""B103 -- does signalling EVOLVE (be restored from one word away) when the mutation load is below the error threshold?

B99: at clone fraction c >= .8, SEEDED signallers sweep (error threshold removed). B95b/B97: from 200 x MUTE_OP
(one word from full communication), the signal is never restored at c=0.
Tension: lowering the load also cuts mutation SUPPLY.
- Break rate ~.31 x (1-c) < s ~ .046 needs c >~ .85.
- At c=.85, clean one-word restores ~0.6 per run, plus ~50 'decode-OUT' variants with collateral changes per run.
Arms: gen 0 = 200 x MUTE_OP, B97 high-headroom world, rotating scout, CMP3 N=200 G=300, c=0.85, seeds 10301-10306;
SHARED vs INDIVIDUAL reward.
Readout: the top 10's SIGNALS; restored = the best genome's SIGNALS > .05.
PREDICTION (committed before running): SHARED restores >= 2/6 AND SHARED >= INDIVIDUAL.
If SHARED is 0/6, mutation supply at a sub-threshold load is too low for the signal to re-arise within G=300.
B103 RESULT: SHARED 4/6, INDIVIDUAL 0/6 (MET). Best genomes were NOT saved (my omission).
B103b (argv[2] = 10311): REPLICATION on new seeds 10311-10316, best genomes dumped, plus SIGNAL CONTENT (share of
signal writes = richest index + 1; hand COMPLETE 1.0). SAME prediction, committed before the run; additionally the
content of restored signallers is >= .5.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import MUTE_OP
from archaeon.beta.b97_signal_headroom import sw
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B103_evolve_lowload"
C_ = 0.85


def cell(job):
    w, s = sw(); arm = job["arm"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rec["origins"] = ["gen0_MUTE_OP"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b103", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x MUTE_OP", "verified_common": True},
                      descend_fn=make_descend(C_, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b103.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8)
            vals = [sum(rew) / len(rew)] * len(rew) if arm == "SHARED" else rew
            for m, v in zip(grp, vals):
                cache[id(m)] = v
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    sigs = [readouts(m, w, s)[0] for m in tops]
    (OUT / ("best_%s_%d.json" % (arm, job["seed"]))).write_text(json.dumps(tops[0]), encoding="utf-8")
    return {"arm": arm, "seed": job["seed"], "best_signals": sigs[0], "top10_signalling": sum(x > .05 for x in sigs), "restored": sigs[0] > .05,
            "signal_content": content(tops[0], w, s)}


def content(m, w, s, E=32):
    """As a lone scout: share of signal writes equal to (index of the richest pool + 1). Hand COMPLETE = 1.0."""
    from proteus.foundry.prng import SplitMix64 as _S, seed_from as _sf
    from proteus.foundry.vm import Player as _P
    p = _P(m); hit = 0; n = 0
    for ep in range(E):
        st = w.w.reset(s + 1000 + ep % 4, ep, {}); vm = p.fresh_state(); rng = _S(_sf("wse.vmrng", 7, ep, 0))
        while not w.done(st):
            obs = w.observe(st); p.begin_tick(vm); outs, _ = p.run_tick(vm, obs, w.K, rng)
            if len(outs) > 3 and outs[3]:
                pools = st["pools"]; n += 1; hit += outs[3][0] == pools.index(max(pools)) + 1
            w.act(st, outs)
    return round(hit / n, 3) if n else None


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        base = int(argv[2]) if len(argv) > 2 else 10301
        futs = {ex.submit(cell, {"arm": a, "seed": base + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("SHARED", "INDIVIDUAL") for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 10301 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / ("B103_cells.jsonl" if base == 10301 else "B103b_cells.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("restored", False) for r in rows if r.get("arm") == a) for a in ("SHARED", "INDIVIDUAL")}
    summ["pred"] = summ["SHARED"] >= 2 and summ["SHARED"] >= summ["INDIVIDUAL"]
    print(json.dumps(summ))
    (OUT / ("B103_result.json" if base == 10301 else "B103b_result.json")).write_text(json.dumps({"probe": "B103", "c": C_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
