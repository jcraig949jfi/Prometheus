"""B118c -- reward-semantics test with the DISTANCE confound removed: type words INTERLEAVED with the pools.

B118b (TOXIC 0/4, PLAIN 0/4; prediction FAILED): every elite had type use exactly 0. Two confounds, not separated:
(1) DISTANCE -- the type words sat at the END of channel 0 (~8 words in), so reading them needs a long IN chain
(Finding 3's wiring wall); (2) weak foraging overall (no elite beat the hand generalist).
B118c: the same strong Toxic (R >= 2, p 1/2, cost 2x), but channel 0 = [p0, t0, p1, t1, ..., rest]. The shortest
type-aware forager is now about the generalist's length (IN p_i; IN t_i; JZ/JNZ; harvest i).
Hand programs for this layout: GEN (reads p_i, skips t_i, harvests the first non-empty pool) and CHK (also skips toxic).
CONTROLS (12 worlds, keys ('b118cctl', i)), PREDICTION committed before running:
  (a) mean(GEN on Toxic) < mean(GEN on p=0), lower in >= 9/12;
  (b) mean(CHK - GEN) on Toxic > .02, positive in >= 9/12.
EVOLUTION (only if (a) and (b) hold): TOXIC vs PLAIN (p = 0, same layout), seeds 11811-11814 each, B35 scheme,
G=300, 8 procs; held-out ('b118cho', 12 worlds); type use = lift - lift(type words zeroed).
PREDICTION (committed before running): TOXIC type-reading (lift >= .03 AND type use >= .02) >= 2/4; PLAIN 0/4.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, IN, JNZ, JZ, LDC, OUT_, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import Toxic, lift
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B118c_interleaved"


class IToxic(Toxic):
    """Toxic with the type words interleaved after each pool word: [p0, t0, p1, t1, ..., rest]."""

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.R
        loc = "locality" in self.w.features
        types = [1 if (t and ((not loc) or st["pool_node"][i] == st["pos"])) else 0 for i, t in enumerate(st["toxic"])]
        ch = obs[0]; head = ch[:2]; pools = ch[2:2 + R]; rest = ch[2 + R:]      # NoClock strips head (tick, pos) later
        inter = [x for i in range(R) for x in (pools[i], types[i])]
        return [head + inter + rest] + obs[1:]


class Blind:
    """Zero the interleaved type words (odd positions 1, 3, ..., 2R-1 after NoClock)."""

    def __init__(self, w):
        self.w = w; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.w.w.R
        ch = list(obs[0])
        for i in range(R):
            ch[2 * i + 1] = 0
        return [ch] + obs[1:]


def world(key, p):
    for t in range(20):
        w, s = echo_free_world(key + (t,))
        if w.w.R >= 2:
            break
    return NoClock(IToxic(w.w, p, 2.0)), s


def _man(prog, n_regs=16):
    g = []
    for t in prog:
        g += (list(t) + [0, 0, 0])[:4]
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": n_regs, "tape_words": max(16, len(g) + 16), "genome": g,
            "code_writable": False, "persist": "none", "tick_budget": 256, "out_cap": 1}


def gen(R):
    prog = [x for i in range(R) for x in ((IN, 1 + i, 0), (IN, 13, 0))]
    for i in range(R):
        prog += [(JZ, 1 + i, 4), (LDC, 12, i), (OUT_, 12, 0), (HALT,)]
    return _man(prog + [(LDC, 14, 1), (OUT_, 0, 14), (HALT,)])


def chk(R):
    prog = [x for i in range(R) for x in ((IN, 1 + i, 0), (IN, 6 + i, 0))]
    for i in range(R):
        prog += [(JZ, 1 + i, 5), (JNZ, 6 + i, 4), (LDC, 12, i), (OUT_, 12, 0), (HALT,)]
    return _man(prog + [(LDC, 14, 1), (OUT_, 0, 14), (HALT,)])


def controls(n=12):
    rows = []
    for i in range(n):
        wt, s = world(("b118cctl", i), .5); wp, _ = world(("b118cctl", i), 0.0); R = wt.w.w.R
        r = {"i": i, "R": R, "gen_plain": round(lift(gen(R), wp, s), 4), "gen_toxic": round(lift(gen(R), wt, s), 4),
             "chk_toxic": round(lift(chk(R), wt, s), 4), "chk_plain": round(lift(chk(R), wp, s), 4)}
        rows.append(r); print(json.dumps(r), flush=True)
    b = [r["chk_toxic"] - r["gen_toxic"] for r in rows]
    summ = {"mean_gen_plain": round(sum(r["gen_plain"] for r in rows) / n, 4), "mean_gen_toxic": round(sum(r["gen_toxic"] for r in rows) / n, 4),
            "mean_chk_toxic": round(sum(r["chk_toxic"] for r in rows) / n, 4), "a_lower": sum(r["gen_toxic"] < r["gen_plain"] for r in rows),
            "b_mean_gain": round(sum(b) / n, 4), "b_pos": sum(x > 0 for x in b)}
    summ["pred_a"] = summ["mean_gen_toxic"] < summ["mean_gen_plain"] and summ["a_lower"] >= 9
    summ["pred_b"] = summ["b_mean_gain"] > .02 and summ["b_pos"] >= 9
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B118c_controls.json").write_text(json.dumps({"rows": rows, "summary": summ}, indent=1), encoding="utf-8")
    return summ


def heldout(n=12):
    return [world(("b118cho", i), .5) for i in range(n)]


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world(("b118ctrain", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b118c", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    ho = heldout()
    lifts = [lift(m, w, s) for w, s in ho]; uses = [lift(m, w, s) - lift(m, Blind(w), s) for w, s in ho]
    ml, mu = sum(lifts) / len(lifts), sum(uses) / len(uses)
    return {"arm": job["arm"], "seed": job["seed"], "mean_lift": round(ml, 4), "mean_type_use": round(mu, 4), "type_reading": ml >= .03 and mu >= .02}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        controls(); return 0
    ho = heldout(); hc = {}
    for nm, f in (("GEN", gen), ("CHK", chk)):
        ls = [lift(f(w.w.w.R), w, s) for w, s in ho]; us = [lift(f(w.w.w.R), w, s) - lift(f(w.w.w.R), Blind(w), s) for w, s in ho]
        hc[nm] = {"mean_lift": round(sum(ls) / len(ls), 4), "mean_type_use": round(sum(us) / len(us), 4)}
    print("heldout_controls", json.dumps(hc), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 11811 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("TOXIC", "PLAIN") for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 11811 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B118c_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("type_reading", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["pred"] = summ["TOXIC"] >= 2 and summ["PLAIN"] == 0
    print(json.dumps(summ))
    (OUT / "B118c_result.json").write_text(json.dumps({"probe": "B118c", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
