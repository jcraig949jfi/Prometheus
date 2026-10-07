"""B29 -- abstraction across worlds: leave-one-world-out training on the NOCLOCK worlds.

B28: evolved foragers are world-specific (home lift +.23, off-home -.02). A layout-invariant rule exists in principle
-- "harvest the pool whose (local) word is non-empty, by its position; else move" -- because in every NOCLOCK world
the pool words come first. B29 trains on the MEAN reward of TWO worlds and tests on the THIRD (never seen).
Worlds: P-boom_K_D_persist_s3 (R=3), B-scatter.T000.d_horizon (R=5), C6-unable.T3 (R=4).
Positive control: ONE fixed hand policy (reads 5 words, harvests the first non-empty by position, else moves) on all
three worlds -- the generalist exists only if it beats each world's constant.
Arms per held-out world: MULTI (train on the other two). Comparison: B27/B25 single-world elites' off-home lift (B28).
Readout: held-out lift = held-out reward - held-out world's best constant; blind twin on the held-out world.
PREDICTION (before running): MULTI held-out lift > B28's mean off-home lift (-.022) by >= .05 in >= 2 of 3 held-out
worlds, and held-out blind twin collapses (the rule senses content).
Heavy: run under lease spectrex5:cpu12 (<= 12 procs) in the budget window.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b27_noclock_generality import load_world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
WORLDS = {"P-boom": "P-boom_K_D_persist_s3", "B-scatter": "B-scatter.T000.d_horizon", "C6-unable": "C6-unable.T3"}
IN, JZ, LDC, OUT_, HALT = 21, 19, 3, 23, 1


def generalist(R=5):
    ins = [(IN, i + 1, 0) for i in range(R)]
    blocks = []
    for i in range(R):
        blocks += [(JZ, i + 1, 4), (LDC, 9, i), (OUT_, 9, 0), (HALT,)]
    tail = [(LDC, 10, 1), (OUT_, 0, 10), (HALT,)]
    g = []
    for t in ins + blocks + tail:
        g += (list(t) + [0, 0, 0])[:4]
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 12, "tape_words": max(16, len(g) + 16), "genome": g,
            "code_writable": False, "persist": "none", "tick_budget": 128, "out_cap": 1}


def worlds():
    return {k: (NoClock(load_world(v)[0]), load_world(v)[1]) for k, v in WORLDS.items()}


def baselines(ws):
    return {k: max(score(constant_manifest(c, w.K), w, s) for c in CONSTS) for k, (w, s) in ws.items()}


def controls():
    ws = worlds(); base = baselines(ws); g = generalist()
    return {k: {"generalist": round(score(g, w, s), 4), "constant": round(base[k], 4), "lift": round(score(g, w, s) - base[k], 4)}
            for k, (w, s) in ws.items()}


def cell(job):
    ws = worlds(); base = baselines(ws)
    train = [k for k in WORLDS if k != job["held_out"]]
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": _mean_eval(m, [ws[k] for k in train])
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b29", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    hw, hs = ws[job["held_out"]]
    held = score(m, hw, hs)
    return {"held_out": job["held_out"], "train": train, "seed": job["seed"],
            "train_lifts": {k: round(score(m, ws[k][0], ws[k][1]) - base[k], 4) for k in train},
            "held_out_lift": round(held - base[job["held_out"]], 4), "held_out_blind": round(score(m, Ablate(hw, "all"), hs), 4),
            "held_out_reward": round(held, 4), "elite_manifest": m}


def _mean_eval(m, pairs):
    rs = [evaluate_world(m, w, s, 8, rng_seed=7) for w, s in pairs]
    r = dict(rs[0]); r["reward"] = sum(x["reward"] for x in rs) / len(rs)
    return r


def main(argv):
    if argv and argv[0] == "controls":
        r = controls(); print(json.dumps(r)); (OUT / "B29_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[0]) if argv else 200
    workers = int(argv[1]) if len(argv) > 1 else 12
    seeds = int(argv[2]) if len(argv) > 2 else 4
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(cell, {"held_out": h, "seed": 2901 + s, "G": G_}): (h, s) for s in range(seeds) for h in WORLDS}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                h, s = futs[f]; r = {"held_out": h, "seed": 2901 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B29_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B29_result.json").write_text(json.dumps({"probe": "B29", "G": G_, "controls": controls(), "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
