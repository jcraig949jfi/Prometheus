"""S7 5a (EXPLORATORY): replay C3-SFE-04 baseline W1_d16 seed 2 and probe its first held-out d16 reader
on d0/1/2/4/8/16. Imports the harness from git unchanged. Output: seed2_probe.json"""
import json, sys, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
from archaeon.campaign3.c3_sfe04 import TARGETS, HELDOUT_N
from archaeon.campaign3.ladder import RUNGS
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_SEED

t0c, t0w = time.process_time(), time.time()
spec, seed = TARGETS[1], 2
hist = [r for r in json.loads((REPO / "archaeon/campaign3/C3-SFE-04/rows.json").read_text()) if r["arm"] == "baseline" and r["target"] == "W1_d16" and r["seed"] == 2][0]
ev = Evolution(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="c3-sfe04-" + spec.name + "-baseline", foundry=FOUNDRY_C2)
ho = episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
tb, found, checks = [], None, []
for g in range(71):
    row = ev.evaluate_generation(last=False); tb.append(row["best_reward"])
    if g >= 52:
        m = ev.scored[0][1]["manifest"]
        h = evaluate(m, ho, rng_seed=7)["reward"]; checks.append({"gen": g, "d16_heldout": round(h, 4)})
        print("gen", g, "best", row["best_reward"], "d16_ho", round(h, 4), flush=True)
        if h >= 0.9:
            found = {"gen": g, "manifest": m}; break
    ev.reproduce()
out = {"status": "EXPLORATORY", "trace_best_replay": tb, "trace_best_match_hist": tb == hist["trace_best"][:len(tb)],
       "hist_first_foothold_gen": hist["first_foothold_gen"], "hist_competence_heldout": hist["competence_heldout"], "elite_checks": checks}
if found:
    probe = {}
    specs = RUNGS + [TARGETS[0], TARGETS[1]]
    for sp in specs:
        a = evaluate(found["manifest"], episodes_for(sp, CAMPAIGN_SEED, "heldout", 2, HELDOUT_N), rng_seed=7)["reward"]
        b = evaluate(found["manifest"], episodes_for(sp, CAMPAIGN_SEED, "heldout", 1, HELDOUT_N), rng_seed=7)["reward"]
        probe[sp.name] = {"heldout_seed2": round(a, 4), "heldout_seed1_directprobe_set": round(b, 4)}
    out.update({"reader_gen": found["gen"], "probe": probe, "reader_manifest": found["manifest"]})
out.update({"cpu_s": round(time.process_time() - t0c, 1), "wall_s": round(time.time() - t0w, 1)})
Path(__file__).with_name("seed2_probe.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v for k, v in out.items() if k not in ("reader_manifest", "trace_best_replay")}, default=str))
