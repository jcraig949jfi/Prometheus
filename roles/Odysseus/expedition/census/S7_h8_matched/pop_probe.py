"""S7 5b (EXPLORATORY): replay the C3-SFE-03 rung-0 hold for one seed exactly (ladder.run_ladder loop),
take the population entering generation ladder_start (before the first delay-1 battery) and evaluate every
member on W1_d8 / W1_d16 held-out (48 eps, rng 7). Usage: pop_probe.py SEED. Output: pop_probe_s<SEED>.json"""
import json, sys, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
from archaeon.campaign3.c3_sfe04 import TARGETS, HELDOUT_N
from archaeon.campaign3.ladder import RUNGS, battery, HOLD_MIN
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_SEED

seed = int(sys.argv[1]); p, N, E, rung0_max = 0.1, 200, 16, 100
t0c, t0w = time.process_time(), time.time()
hist = [r for r in json.loads((REPO / "archaeon/campaign3/C3-SFE-03/rows.json").read_text()) if r["seed"] == seed][0]
ev = Evolution(RUNGS[0], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-ladder-p%s" % p, foundry=FOUNDRY_C2)
sched, g, ladder_start = [], 0, None
while ladder_start is None:
    ev.spec = RUNGS[0]
    row = ev.evaluate_generation(episodes=battery(g, seed, 0, p, E), last=False)
    sched.append({"gen": g, "best": row["best_reward"], "mean": row["mean_reward"]})
    if row["best_reward"] >= HOLD_MIN or g + 1 >= rung0_max:
        ladder_start = g + 1
    ev.reproduce(); g += 1
hs = [{"gen": s["gen"], "best": s["best"], "mean": s["mean"]} for s in hist["schedule"][:ladder_start]]
match = hs == sched
res = {"status": "EXPLORATORY", "seed": seed, "ladder_start": ladder_start, "hist_hold_gens": hist["hold_gens"], "schedule_match_hist": match,
       "hist_general_heldout": hist["general_heldout"], "hist_general_gen": hist["general_gen"]}
per = {}
for sp in (TARGETS[0], TARGETS[1]):
    ho = episodes_for(sp, CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
    per[sp.name] = [round(evaluate(o["manifest"], ho, rng_seed=7)["reward"], 4) for o in ev.pop]
w0ho = episodes_for(RUNGS[0], CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
per["W0"] = [round(evaluate(o["manifest"], w0ho, rng_seed=7)["reward"], 4) for o in ev.pop]
d8, d16 = per["W1_d8"], per["W1_d16"]
res.update({"n_members": len(ev.pop), "d8_ge_0.9": sum(x >= 0.9 for x in d8), "d16_ge_0.9": sum(x >= 0.9 for x in d16),
            "both_ge_0.9": sum(a >= 0.9 and b >= 0.9 for a, b in zip(d8, d16)), "d8_max": max(d8), "d16_max": max(d16),
            "w0_ge_0.9": sum(x >= 0.9 for x in per["W0"]),
            "both_and_w0_ge_0.9": sum(a >= 0.9 and b >= 0.9 and c >= 0.9 for a, b, c in zip(d8, d16, per["W0"])),
            "per_member": per, "cpu_s": round(time.process_time() - t0c, 1), "wall_s": round(time.time() - t0w, 1)})
Path(__file__).with_name("pop_probe_s%d.json" % seed).write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "per_member"}))
