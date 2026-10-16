"""B118 -- randomise reward SEMANTICS: does the foraging rule extend to 'which pool pays'? (Finding 2 open question 3)

In the B32 family gain = pools[i]: the observed magnitude IS the payoff, so 'harvest the non-empty pool' can never be
wrong about meaning. Toxic wrapper (inside NoClock): per episode each pool is independently toxic with p = 1/3, and
harvesting a toxic pool SUBTRACTS its gain. One type word per pool is APPENDED to channel 0 (1 = toxic, shown only
when the pool is local, like the amount). The existing hand generalist is structurally unaffected; only meaning
changes. max_reward is left as the base world's (lift vs the best constant normalises).
CONTROLS (this file, step 1; 12 echo-free family worlds, keys ('b118ctl', i), each scored E=8 like score()):
  gen_plain  hand generalist (B29), plain world, lift vs best constant
  gen_toxic  hand generalist on Toxic
  chk_toxic  hand CHECKER (generalist + skip pools whose type word is 1) on Toxic
PREDICTION (committed before running):
  (a) the generalist is hurt by toxicity: mean(gen_toxic) < mean(gen_plain), lower in >= 9/12 worlds;
  (b) the type check carries value: mean(chk_toxic - gen_toxic) > .02, positive in >= 9/12 worlds.
If (b) fails, the semantic version is not a test (the type word carries no usable value) and B118 is not run.
"""
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import HALT, IN, JZ, LDC, OUT_
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.beta.b32_world_distribution import echo_free_world

OUT = Path(__file__).resolve().parent / "results" / "B118_toxic"
P_TOXIC = 1 / 3


class Toxic:
    def __init__(self, cw):
        self.w = cw; self.K = cw.K; self.features = cw.features

    def __getattr__(self, k):
        return getattr(self.w, k)

    def reset(self, seed, ep, shared=None):
        st = self.w.reset(seed, ep, shared)
        rng = SplitMix64(seed_from("b118.toxic", seed, ep))
        st["toxic"] = [rng.randbelow(1000) < int(P_TOXIC * 1000) for _ in range(len(st["pools"]))]
        return st

    def observe(self, st):
        obs = self.w.observe(st)
        loc = "locality" in self.w.features
        types = [1 if (t and ((not loc) or st["pool_node"][i] == st["pos"])) else 0 for i, t in enumerate(st["toxic"])]
        return [obs[0] + types] + obs[1:]

    def act(self, st, outputs):
        before = st["reward"]
        i = (outputs[0][0] % self.w.R) if (outputs and outputs[0] and st["pools"]) else None
        self.w.act(st, outputs)
        gain = st["reward"] - before
        if i is not None and gain > 0 and st["toxic"][i]:
            st["reward"] = before - gain


def plain_and_toxic(key):
    w, s = echo_free_world(key)                        # NoClock(ComposedWorld)
    return w, NoClock(Toxic(w.w)), s


def checker(w, s):
    """Generalist + type check, laid out for this world's observation length."""
    R = w.w.R
    n = len(w.observe(w.reset(s, 0, None))[0])        # Toxic observation length (pools .. extras .. types)
    gap = n - 2 * R
    prog = [(IN, 1 + i, 0) for i in range(R)] + [(IN, 13, 0)] * gap + [(IN, 6 + i, 0) for i in range(R)]
    for i in range(R):
        prog += [(JZ, 1 + i, 6), (JZ, 6 + i, 2), (JZ, 15, 4), (LDC, 12, i), (OUT_, 12, 0), (HALT,)]
    prog += [(LDC, 14, 1), (OUT_, 0, 14), (HALT,)]
    g = []
    for t in prog:
        g += (list(t) + [0, 0, 0])[:4]
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 16, "tape_words": max(16, len(g) + 16), "genome": g,
            "code_writable": False, "persist": "none", "tick_budget": 256, "out_cap": 1}


def lift(m, w, s):
    return score(m, w, s) - max(score(constant_manifest(c, w.K), w, s) for c in CONSTS)


def controls(n=12):
    rows = []
    for i in range(n):
        wp, wt, s = plain_and_toxic(("b118ctl", i)); g = generalist(wp.w.R)
        r = {"i": i, "R": wp.w.R, "gen_plain": round(lift(g, wp, s), 4), "gen_toxic": round(lift(g, wt, s), 4),
             "chk_toxic": round(lift(checker(wt, s), wt, s), 4)}
        rows.append(r); print(json.dumps(r), flush=True)
    a = [r["gen_toxic"] < r["gen_plain"] for r in rows]; b = [r["chk_toxic"] - r["gen_toxic"] for r in rows]
    summ = {"mean_gen_plain": round(sum(r["gen_plain"] for r in rows) / n, 4), "mean_gen_toxic": round(sum(r["gen_toxic"] for r in rows) / n, 4),
            "mean_chk_toxic": round(sum(r["chk_toxic"] for r in rows) / n, 4), "a_lower": sum(a), "b_mean_gain": round(sum(b) / n, 4),
            "b_pos": sum(x > 0 for x in b)}
    summ["pred_a"] = summ["mean_gen_toxic"] < summ["mean_gen_plain"] and summ["a_lower"] >= 9
    summ["pred_b"] = summ["b_mean_gain"] > .02 and summ["b_pos"] >= 9
    print(json.dumps(summ))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B118_controls.json").write_text(json.dumps({"rows": rows, "summary": summ}, indent=1), encoding="utf-8")
    return summ


if __name__ == "__main__":
    controls(int(sys.argv[1]) if len(sys.argv) > 1 else 12); sys.exit(0)
