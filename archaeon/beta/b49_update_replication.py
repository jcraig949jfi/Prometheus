"""B49 -- head-to-head replication: does the SEL primitive raise the rate of evolved UPDATE-ON-CONDITION memory?

B47 (stock VM): 0/8 above reactive. B48 (SEL VM): 0/8 by the +.025 criterion, but seed 4807 showed a genuine
filter + re-track profile. B49: stock vs SEL VM, 12 seeds each, same switching-evidence world (noise .6, switch at 16),
CMP3 search, G=300. Per elite: score (E=64 x 4 new world keys, on its own VM) and the switch-recovery profile
(accuracy = output == latent, ticks 0-15 / 20-23, 2 keys x 64 episodes).
UPDATE = pre-switch accuracy >= REACTIVE's + .03 (it filters) AND post-late accuracy >= .45 (it re-tracks; latch .20).
PREDICTION (before running): UPDATE rate SEL > stock; SEL >= 2/12, stock <= 1/12.
"""
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b10_select_primitive import SELVM
from archaeon.beta.b43_evidence_world import REACTIVE
from archaeon.beta.b47_switching_evidence import world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"


def P(vm):
    return SELVM.Player if vm == "sel" else stockvm.Player


def sc(m, vm, keys):
    return sum(evaluate_world(m, *world(k), 64, rng_seed=7, player_factory=P(vm))["reward"] for k in keys) / len(keys)


def recovery(m, vm, keys=(360, 361)):
    p = P(vm)(m); acc = Counter(); n = Counter()
    for k in keys:
        w, s = world(k)
        for ep in range(64):
            st = w.reset(s, ep, None); vmst = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep)); t = 0
            while not w.done(st):
                obs = w.observe(st); outs, _ = p.run_tick(vmst, obs, w.K, rng)
                a = outs[0][0] % 4 if outs and outs[0] else None
                ph = "pre" if t < 16 else ("early" if t < 20 else "late")
                n[ph] += 1; acc[ph] += a == st["hidden"]; w.act(st, outs); t += 1
    return {k: round(acc[k] / n[k], 4) for k in ("pre", "early", "late")}


def cell(job):
    vm = job["vm"]
    EV.Player = P(vm)
    w, s = world(0)
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, s, 16, rng_seed=7, player_factory=P(vm))
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b49", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    keys = [350, 351, 352, 353]
    rec = recovery(m, vm); react = recovery(REACTIVE, vm)
    return {"vm": vm, "seed": job["seed"], "score": round(sc(m, vm, keys), 4), "reactive": round(sc(REACTIVE, vm, keys), 4),
            "recovery": rec, "reactive_recovery": react,
            "UPDATE": rec["pre"] >= react["pre"] + .03 and rec["late"] >= .45, "elite_manifest": m}


def main(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"vm": v, "seed": 4901 + s, "G": G_}): (v, s) for s in range(12) for v in ("sel", "stock")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                v, s = futs[f]; r = {"vm": v, "seed": 4901 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B49_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {v: {"n": sum(r.get("vm") == v for r in rows), "UPDATE": sum(r.get("vm") == v and r.get("UPDATE", False) for r in rows),
                "beats_reactive_.025": sum(r.get("vm") == v and r.get("score", 0) - r.get("reactive", 1) >= .025 for r in rows)}
            for v in ("sel", "stock")}
    print(json.dumps(summ), flush=True)
    (OUT / "B49_result.json").write_text(json.dumps({"probe": "B49", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
