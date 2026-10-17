"""B118d -- does a type check evolve FROM A WORKING FORAGER? (reward semantics, the precursor version)

B118b/B118c: from random gen 0 no forager reads the type words (0/4, 0/4 or <= 1/4). Even the PLAIN arm does not
reach the hand forager's lift, so basic foraging is itself rarely found at G=300 -- a semantic layer on top of it
is out of reach (as with communication from scratch, B104/B112-NL).
B118d (precursor version, like B103/B105 for communication): interleaved strong-Toxic worlds with EXACTLY R = 3,
so the hand forager GEN(3) is exact on every world. Gen 0 = 200 x GEN(3). A one-pool type check is ~3 coupled edits
away (route t_i to a register; insert JNZ; fix the shifted JZ offset).
Arms: TOXIC vs PLAIN (p = 0, same layout); seeds 11821-11824 each; B35 scheme (fresh world per gen); G=300; 8 procs.
Held-out: 12 R = 3 interleaved Toxic worlds, keys ('b118dho', i).
Type-reading = mean held-out lift >= GEN(3)'s + .02 AND mean type use >= .02.
CONTROLS (held-out, in the run log): GEN(3) and CHK(3) lift and type use.
PREDICTION (committed before running): TOXIC type-reading >= 2/4; PLAIN 0/4.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import lift
from archaeon.beta.b118c_interleaved import Blind, IToxic, chk, gen
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B118d_seeded_forager"


def world3(key, p):
    for t in range(60):
        w, s = echo_free_world(key + (t,))
        if w.w.R == 3:
            break
    assert w.w.R == 3, key
    return NoClock(IToxic(w.w, p, 2.0)), s


def heldout(n=12):
    return [world3(("b118dho", i), .5) for i in range(n)]


def hcontrols(ho):
    out = {}
    for nm, m in (("GEN3", gen(3)), ("CHK3", chk(3))):
        ls = [lift(m, w, s) for w, s in ho]; us = [lift(m, w, s) - lift(m, Blind(w), s) for w, s in ho]
        out[nm] = {"mean_lift": round(sum(ls) / len(ls), 4), "mean_type_use": round(sum(us) / len(us), 4)}
    return out


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world3(("b118dtrain", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    rec = G.organism_record(gen(3), None, 0); rec["origins"] = ["gen0_GEN3"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b118d", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x GEN(3)", "verified_common": True})
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    ho = heldout(); base = job["gen_lift"]
    lifts = [lift(m, w, s) for w, s in ho]; uses = [lift(m, w, s) - lift(m, Blind(w), s) for w, s in ho]
    ml, mu = sum(lifts) / len(lifts), sum(uses) / len(uses)
    return {"arm": job["arm"], "seed": job["seed"], "mean_lift": round(ml, 4), "mean_type_use": round(mu, 4),
            "type_reading": ml >= base + .02 and mu >= .02}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    hc = hcontrols(heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    if argv and argv[0] == "controls":
        (OUT / "B118d_heldout_controls.json").write_text(json.dumps(hc, indent=1), encoding="utf-8"); return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 11821 + i, "G": int(argv[0]) if argv else 300, "gen_lift": hc["GEN3"]["mean_lift"]}): (a, i)
                for a in ("TOXIC", "PLAIN") for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 11821 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B118d_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("type_reading", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["pred"] = summ["TOXIC"] >= 2 and summ["PLAIN"] == 0
    print(json.dumps(summ))
    (OUT / "B118d_result.json").write_text(json.dumps({"probe": "B118d", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
