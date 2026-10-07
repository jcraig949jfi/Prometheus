"""B32 -- make specificity unlearnable: a FRESH random world structure every generation (abstraction pressure).

B28/B29: evolved foragers are world-specific and multi-world training (2 fixed worlds) still yields specific mappings;
the invariant rule ("harvest the non-empty pool by position, else move") exists (hand generalist) and is not found.
B32 changes the WORLD DISTRIBUTION: each generation is scored on a world drawn fresh from a family -- the P-boom
NoClock params with R (pool count) in {2,3,4,5}, ring nodes in {6..16}, deplete/regen re-drawn, hazards and objects
kept -- so a mapping tied to one layout cannot persist.
Readout: test on 6 FIXED held-out worlds from the same family (never used in training) + the 3 named NOCLOCK worlds:
lift over each world's best constant, and the blind twin.
Positive control: the hand generalist on the held-out set. Negative: a B25 P-boom-specific elite on the held-out set.
PREDICTION (before running): >= 2/4 seeds reach mean held-out lift >= .05 with blind collapse (invariant sensing);
the P-boom-specific elite stays <= .02.
Heavy-ish: run under lease spectrex5:cpu12 (<= 12 procs) in the budget window.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.campaign6.worlds.runtime import ComposedWorld, evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"


_BASE = {}
_WCACHE = {}


def _base():
    """P-boom base world, loaded ONCE per process (run 1 re-read the checkpoint for every evaluation -- the hang)."""
    if "w" not in _BASE:
        _BASE["w"] = load()[0]
    return _BASE["w"]


def family_world(key):
    """v2 (2026-10-07 ~21:55Z): v1 varied only R / ring size / rates of the P-boom params and the P-boom-SPECIFIC elite
    transferred within it (negative control failed: lift .03-.37). v2 draws a WHOLE world from the C6 procedural
    generator (archaeon.campaign6.worlds.generator.sample_world) and forces only what foraging needs: resources ON,
    locality ON, >= 2 action channels (MOVE is channel 1), delayed OFF. Feature set, K and all ranges vary."""
    from archaeon.campaign6.worlds.generator import sample_world
    base = _base()
    rng = SplitMix64(seed_from("archaeon.beta.b32.world2", *key))
    rec = sample_world(rng.randbelow(10 ** 9))
    p = copy.deepcopy(rec["params"])
    if not p["resources"].get("on"):
        p["resources"] = copy.deepcopy(base.params["resources"])
    if not p["locality"].get("on"):
        p["locality"] = copy.deepcopy(base.params["locality"])
    p["delayed"] = {"on": False}
    if p["channels"].get("k", 1) < 2:
        p["channels"] = {"on": True, "k": 2}
    return NoClock(ComposedWorld(p)), 1000 + rng.randbelow(10 ** 6)


def heldout_worlds(n=6, scan=200):
    """Held-out worlds where the controls discriminate: hand generalist lift >= .05 AND P-boom-specific elite lift <= .02."""
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    spec = b25[2506]["elite_manifest"]
    out = []
    for i in range(scan):
        w, s = family_world(("heldout", i))
        if lift(generalist(), w, s) >= .05 and lift(spec, w, s) <= .02:
            out.append((w, s))
            if len(out) >= n:
                break
    return out


def lift(m, w, s):
    return score(m, w, s) - max(score(constant_manifest(c, w.K), w, s) for c in CONSTS)


def controls():
    ho = heldout_worlds()
    _, _, sweep = load()
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    spec = b25[2506]["elite_manifest"]
    return {"generalist_lift": [round(lift(generalist(), w, s), 4) for w, s in ho],
            "pboom_specific_lift": [round(lift(spec, w, s), 4) for w, s in ho],
            "Rs": [w.w.R for w, _ in ho], "features": [w.w.features for w, _ in ho], "n_heldout": len(ho)}


def cell(job):
    state = {"g": 0}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = ("train", job["seed"], state["g"])
        if k not in _WCACHE:
            _WCACHE.clear(); _WCACHE[k] = family_world(k)
        w, s = _WCACHE[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b32", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    ho = heldout_worlds()
    lifts = [round(lift(m, w, s), 4) for w, s in ho]
    blinds = [round(score(m, w, s) - score(m, Ablate(w, "all"), s), 4) for w, s in ho]
    return {"seed": job["seed"], "heldout_lifts": lifts, "mean_lift": round(sum(lifts) / len(lifts), 4),
            "input_use": blinds, "mean_input_use": round(sum(blinds) / len(blinds), 4), "elite_manifest": m}


def main(argv):
    if argv and argv[0] == "controls":
        r = controls(); print(json.dumps(r)); (OUT / "B32_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[0]) if argv else 300
    workers = int(argv[1]) if len(argv) > 1 else 12
    seeds = int(argv[2]) if len(argv) > 2 else 4
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(cell, {"seed": 3201 + s, "G": G_}): s for s in range(seeds)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 3201 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B32_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B32_result.json").write_text(json.dumps({"probe": "B32", "G": G_, "controls": controls(), "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
