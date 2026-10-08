"""B43 -- an EVIDENCE-INTEGRATION world: does memory of past cues evolve when it pays? (design + controls)

Design analysis (2026-10-08 ~08:40Z): the C6 "hidden" feature does not test evidence integration -- the latent is the
index of the rich pool (3.0 vs <= 1.75), which visible pool words already reveal; with locality the hint names the
pool but not its place. Purpose-built world (wrapper over a C6 ComposedWorld with resources + hidden, NO locality):
  observation  ONE word: the noisy hint (true latent with prob 1 - noise, else uniform over R); pool words withheld
  action       channel 0 = harvest index; reward = the pool's amount (rich 3.0, others <= 1.75), C6 dynamics
A reactive hint-follower harvests the true rich pool with prob (1 - noise) + noise/R; an organism that accumulates
hints can approach 1.0 after a few ticks.
Controls: REACTIVE (harvest the current hint), STICKY (harvest the current hint only if it equals the previous hint,
else the previous choice -- one remembered word), ORACLE (harvest the true latent; reads hidden state, not an organism,
reported for headroom), CONSTANT best.
"""
import copy
import json
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import _prog
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b25_noclock_world import load
from archaeon.campaign6.worlds.runtime import ComposedWorld

OUT = Path(__file__).resolve().parent / "results"
IN, JZ, LDC, OUT_, HALT, MOV, EQ, JNZ = 21, 19, 3, 23, 1, 4, 16, 20


class HintOnly:
    """Observation = [hint] only. Everything else (dynamics, reward) is the wrapped world's."""
    def __init__(self, w):
        self.w = w; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        return [[self.w.observe(st)[0][-1]]]


def evidence_world(R=4, noise=0.45, key=0):
    base = load()[0]
    p = copy.deepcopy(base.params)
    for f in ("locality", "objects", "delayed", "hazards", "history", "coupling", "regime"):
        p[f] = {"on": False}
    # v2: no depletion / no regeneration -- v1 (C6 dynamics) rewarded ROTATING harvests (oracle .24 < reactive .44-.60),
    # so knowing the latent did not pay. With static pools the rich pool is always the best harvest.
    p["resources"] = dict(p["resources"], types=R, on=True, deplete=0.0, regen=0.0)
    p["hidden"] = {"on": True, "noise": noise}
    p["channels"] = {"on": True, "k": 1}
    return HintOnly(ComposedWorld(p)), 1000 + key


def _m(g, persist="regs", n_regs=6):
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": n_regs, "tape_words": max(16, len(g) + 16), "genome": g,
            "code_writable": False, "persist": persist, "tick_budget": 64, "out_cap": 1}


REACTIVE = _m(_prog([(IN, 1, 0), (OUT_, 1, 0), (HALT,)]), persist="none")
# STICKY: r2 = previous hint, r3 = current choice (persist regs). If hint == previous hint: choice = hint. Output choice.
STICKY = _m(_prog([(IN, 1, 0), (EQ, 4, 1, 2), (JZ, 4, 2), (MOV, 3, 1), (MOV, 2, 1), (OUT_, 3, 0), (HALT,)]))


def oracle_score(world, seed, E=8):
    total = mx = 0.0
    for ep in range(E):
        st = world.reset(seed, ep, None)
        while not world.done(st):
            world.act(st, [[st["hidden"]]])
        total += max(0.0, st["reward"]); mx += st["max_reward"]
    return min(1.0, total / max(1e-9, mx))


def controls(R=4, noise=0.45):
    w, s = evidence_world(R, noise)
    return {"R": R, "noise": noise, "reactive": round(score(REACTIVE, w, s), 4), "sticky": round(score(STICKY, w, s), 4),
            "oracle": round(oracle_score(w, s), 4), "constant": round(max(score(constant_manifest(c, w.K), w, s) for c in CONSTS), 4)}


if __name__ == "__main__" and not (len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "b44"):
    rows = [controls(R, nz) for R in (3, 4, 5) for nz in (0.3, 0.45, 0.6)]
    for r in rows:
        print(json.dumps(r))
    OUT.mkdir(exist_ok=True)
    (OUT / "B43_controls.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- B44: evolution on the evidence world (R=4, noise .6)
# Ladder (v2 controls): constant .656 < REACTIVE .754 < STICKY .900 < oracle 1.0 -> memory of one past cue is worth ~+.15.
# PREDICTION (before running): >= 3/8 elites beat REACTIVE by >= .05 AND lose >= .05 under persist=none (evolved
# evidence integration); the rest sit at the reactive hint-follower.
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET  # noqa: E402
from archaeon.campaign6.worlds.runtime import evaluate_world  # noqa: E402
from archaeon.wse import evolve as EV  # noqa: E402


def cell44(job):
    w, s = evidence_world(4, 0.6)
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, s, 16, rng_seed=7)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b44", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    hw, hs = evidence_world(4, 0.6, key=99)          # held-out world seed
    el = score(m, hw, hs); re = score(REACTIVE, hw, hs); st = score(STICKY, hw, hs)
    nop = score(dict(m, persist="none"), hw, hs)
    return {"seed": job["seed"], "elite": round(el, 4), "reactive": round(re, 4), "sticky": round(st, 4),
            "persist_none": round(nop, 4), "beats_reactive": el - re >= .05, "uses_memory": el - nop >= .05,
            "elite_manifest": m}


def main44(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell44, {"seed": 4401 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 4401 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B44_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B44_result.json").write_text(json.dumps({"probe": "B44", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "b44":
    sys.exit(main44(sys.argv[2:]))
