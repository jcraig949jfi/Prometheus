"""B47 -- punish the LATCH: an evidence world whose latent SWITCHES mid-episode. Does a conditional-update memory evolve?

Memory results so far: latching (store once, stop perceiving) is reachable (B16, B44/B45 first-hint latch); a
conditional update of stored state is not (two-value keyed memory B08J/B40; evidence filter B45). B47 makes latching
a liability: the B43 v2 evidence world, but at tick 12 the latent (rich pool) is re-drawn (different from the old one).
A first-hint latch is then wrong for half of every episode; REACTIVE is unaffected; STICKY (update when two
consecutive hints agree) re-tracks within a few ticks.
Controls (E=64 x 4 world seeds): LATCH (harvest the first hint forever), REACTIVE, STICKY, constant.
Evolution (8 seeds, G=300) under lease; scoring E=64 x 4 new world seeds (B45 standard).
PREDICTION (before evolving; criterion lowered to +.025 after the sweep showed a one-step filter gains only .042, SE ~.012 at E=64x4): 0/8 elites beat REACTIVE by >= .025 with a persist=none drop
(the conditional update is not reached even when the latch is punished).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET, _prog
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest
from archaeon.beta.b43_evidence_world import REACTIVE, STICKY, _m, evidence_world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
SWITCH_AT = 16          # chosen by a sweep: sticky margin .042 max (noise .6), latch .653 < reactive .744
IN, JNZ, MOV, OUT_, HALT, LDC = 21, 20, 4, 23, 1, 3


class Switching:
    def __init__(self, inner):
        self.w = inner; self.K = inner.K; self.features = getattr(inner, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def act(self, st, outs):
        self.w.act(st, outs)
        if st["tick"] == SWITCH_AT and st["pools"]:
            rng = SplitMix64(seed_from("archaeon.beta.b47.switch", st["hidden"], len(st["pools"]), st.get("reward", 0.0).__repr__()))
            old = st["hidden"]
            new = (old + 1 + rng.randbelow(len(st["pools"]) - 1)) % len(st["pools"])
            st["pools"][old] = 1.0
            st["pools"][new] = 3.0
            st["hidden"] = new


def world(key):
    w, s = evidence_world(4, 0.6, key=key)
    return Switching(w), s


# LATCH: r2 = flag, r3 = first hint (persist regs). If flag == 0: r3 = hint, flag = 1. Output r3.
LATCH = _m(_prog([(IN, 1, 0), (JNZ, 2, 3), (MOV, 3, 1), (LDC, 2, 1), (OUT_, 3, 0), (HALT,)]))


def sc(m, keys):
    return sum(evaluate_world(m, *world(k), 64, rng_seed=7)["reward"] for k in keys) / len(keys)


def controls():
    keys = [300, 301, 302, 303]
    return {"LATCH": round(sc(LATCH, keys), 4), "REACTIVE": round(sc(REACTIVE, keys), 4), "STICKY": round(sc(STICKY, keys), 4),
            "constant": round(max(sc(constant_manifest(c, 1), keys) for c in CONSTS), 4)}


def cell(job):
    w, s = world(0)
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, s, 16, rng_seed=7)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b47", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    keys = [310, 311, 312, 313]
    return {"seed": job["seed"], "elite": round(sc(m, keys), 4), "reactive": round(sc(REACTIVE, keys), 4),
            "sticky": round(sc(STICKY, keys), 4), "latch": round(sc(LATCH, keys), 4),
            "persist_none": round(sc(dict(m, persist="none"), keys), 4), "elite_manifest": m}


def main(argv):
    if argv and argv[0] == "controls":
        r = controls(); print(json.dumps(r)); (OUT / "B47_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"seed": 4701 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 4701 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B47_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B47_result.json").write_text(json.dumps({"probe": "B47", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
