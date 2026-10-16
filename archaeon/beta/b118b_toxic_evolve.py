"""B118b EVOLUTION -- does training on randomised reward SEMANTICS evolve a forager that reads the type word?

Controls (b118_toxic.py, B118b, prereg met): on strong-Toxic worlds (R >= 2, P_TOXIC 1/2, toxic harvest costs 2x)
the hand generalist's lift drops .067 -> .032 and a hand type-checker reaches .119 (gain +.087, 12/12 worlds).
Arms (B35 scheme: a FRESH echo-free family world each generation, R >= 2; CMP3 N=200 E=8 G=300):
  TOXIC  training worlds wrapped in strong Toxic
  PLAIN  the same worlds wrapped in Toxic with p = 0 (identical observation layout, type words always 0)
Seeds 11801-11804 per arm (8 procs).
Held-out: 12 strong-Toxic worlds, keys ('b118bho', i), never used in training; lift vs best constant.
TYPE USE = lift(m, Toxic) - lift(m, TypeBlind(Toxic)), where TypeBlind zeroes the R type words.
A type-reading forager = mean held-out lift >= .03 AND mean type use >= .02.
PREDICTION (committed before running): TOXIC type-reading >= 2/4; PLAIN 0/4.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import Toxic, lift, plain_and_toxic
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B118b_toxic_evolve"


class TypeBlind:
    def __init__(self, w):
        self.w = w; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.w.w.R              # NoClock -> Toxic -> ComposedWorld
        return [obs[0][:-R] + [0] * R] + obs[1:]


def train_world(key, toxic):
    for t in range(20):
        w, s = echo_free_world(key + (t,))
        if w.w.R >= 2:
            break
    return (NoClock(Toxic(w.w, .5, 2.0)) if toxic else NoClock(Toxic(w.w, 0.0, 2.0))), s


def heldout(n=12):
    return [plain_and_toxic(("b118bho", i), True)[1:] for i in range(n)]


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = train_world(("b118btrain", job["seed"], state["g"]), job["arm"] == "TOXIC")
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b118b", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    ho = heldout()
    lifts = [lift(m, w, s) for w, s in ho]; uses = [lift(m, w, s) - lift(m, TypeBlind(w), s) for w, s in ho]
    ml, mu = sum(lifts) / len(lifts), sum(uses) / len(uses)
    return {"arm": job["arm"], "seed": job["seed"], "mean_lift": round(ml, 4), "mean_type_use": round(mu, 4),
            "type_reading": ml >= .03 and mu >= .02}


def controls():
    from archaeon.beta.b29_leave_one_world_out import generalist
    from archaeon.beta.b118_toxic import checker
    ho = heldout(); out = {}
    for name, f in (("generalist", lambda w, s: generalist(w.w.w.R)), ("checker", checker)):
        ls = [lift(f(w, s), w, s) for w, s in ho]; us = [lift(f(w, s), w, s) - lift(f(w, s), TypeBlind(w), s) for w, s in ho]
        out[name] = {"mean_lift": round(sum(ls) / len(ls), 4), "mean_type_use": round(sum(us) / len(us), 4)}
    return out


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    if argv and argv[0] == "controls":
        (OUT / "B118b_heldout_controls.json").write_text(json.dumps(ctl, indent=1), encoding="utf-8"); return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 11801 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("TOXIC", "PLAIN") for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 11801 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B118b_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("type_reading", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["pred"] = summ["TOXIC"] >= 2 and summ["PLAIN"] == 0
    print(json.dumps(summ))
    (OUT / "B118b_result.json").write_text(json.dumps({"probe": "B118b", "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
