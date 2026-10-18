"""B122 -- FALSIFIER for the cross-finding conjecture: a SHORT-chain semantics task FROM SCRATCH.

Conjecture (BETA_FINDINGS, 2026-10-18): reachability is set by the coupled read-chain length; precursors help only
when they pre-build that chain. Reward semantics with R = 3 was NOT reached from random gen 0 (B118b/c 0/4, 0/4).
B122 shortens the chain: R = 1 worlds only (family 1, echo-free, interleaved strong Toxic: p 1/2, cost 2x). The
type-aware program is ~4 instructions (IN p; IN t; JNZ t -> move; harvest), one link longer than plain foraging, which
evolves from scratch (Finding 2).
Arms: TOXIC vs PLAIN (p = 0, same layout), RANDOM gen 0 (FOUNDRY_C2), seeds 12201-12208 each, G=300, fresh world per
generation. Held-out: 12 R = 1 worlds ('b122ho', i).
Readout (fixed in advance): avoids = toxic share of harvests < .25 AND harvests >= 100 (a non-forager is excluded).
CONTROLS (step 1, committed before running): GEN1 toxic share ~.5; CHK1 0; training-side CHK1 - GEN1 > 0 on >= 6/8
training worlds.
PREDICTION (committed before running), conjecture: TOXIC avoids >= 3/8 AND PLAIN <= 1/8.
If TOXIC <= 1/8, the conjecture's 'short chain is reachable from scratch' half is wrong (or R = 1 differs otherwise).
B122 CONTROLS RESULT (~07:20Z): FAILED -- training-side value 0.00 on 8/8 worlds; CHK1 lift = GEN1 lift (-.0009).
Cause: rewards are clipped at 0 per EPISODE, and with R = 1 a toxic pool is toxic for the whole episode, so harvesting
and not harvesting both score 0. Avoidance has no value. B122 as designed is NOT run (the training-side rule caught it).
B122b (NEW design, NEW prereg, argv 'b'): toxicity re-drawn EVERY TICK (p 1/2, cost 2x), so the type word says whether
harvesting pays NOW; GEN's expected harvest value is negative and CHK harvests only on safe ticks. Same arms, seeds
12211-12218, readout and PREDICTION as above; controls re-run first with the same criteria.
B122b CONTROLS RESULT (~07:30Z): FAILED -- training value positive 3/8 (< 6). Cause: the hand CHK1 (written for
R >= 2) MOVES when its only pool is toxic; with locality on, that walks it off the pool node (safe harvests 269 vs
GEN1 814). Instrument refinement (declared before re-running; criteria unchanged): CHK1w WAITS (halts with no
output) on a toxic tick, harvests on a safe one, and moves only when the pool is empty.
CHK1w CONTROLS (~07:35Z): still 3/8. Cause found: the 5 zero-gain training worlds are EXACTLY those with the 'history'
feature, which makes pool 0 pay only after k harvests ELSEWHERE -- with R = 1 there is no elsewhere, so nothing ever
pays. Repair (declared before re-running; same criteria): world1 rebuilds each world with history OFF (as family 2
already does).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import lift
from archaeon.beta.b118c_interleaved import IToxic, chk, gen
from archaeon.beta.b118h_decode import trace
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B122_short_chain_scratch"


class TickToxic(IToxic):
    """B122b: re-draw every pool's toxicity on every tick (after the world advances)."""

    def reset(self, seed, ep, shared=None):
        st = super().reset(seed, ep, shared); st["_tox_key"] = (seed, ep); return st

    def act(self, st, outputs):
        super().act(st, outputs)
        from proteus.foundry.prng import SplitMix64, seed_from
        rng = SplitMix64(seed_from("b122b.tick", *st["_tox_key"], st["tick"]))
        st["toxic"] = [rng.randbelow(1000) < int(self.p * 1000) for _ in st["toxic"]]


MODE = {"tick": False}


def world1(key, p):
    for t in range(200):
        w, s = echo_free_world(key + (t,))
        if w.w.R == 1:
            break
    assert w.w.R == 1, key
    cw = w.w
    if MODE["tick"] and "history" in cw.features:                   # B122b repair: history never pays at R = 1
        import copy as _c
        from archaeon.campaign6.worlds.runtime import ComposedWorld
        q = _c.deepcopy(cw.params); q["history"] = {"on": False}; cw = ComposedWorld(q)
    return NoClock((TickToxic if MODE["tick"] else IToxic)(cw, p, 2.0)), s


def heldout(n=12):
    return [world1(("b122ho", i), .5) for i in range(n)]


def chk1w():
    """Wait-checker for R = 1: harvest if (pool non-empty and safe); halt with no output if non-empty and toxic; move if empty."""
    from archaeon.beta.b01_w2k2_existence import HALT, IN, JNZ, JZ, LDC, OUT_
    from archaeon.beta.b118c_interleaved import _man
    return _man([(IN, 1, 0), (IN, 6, 0), (JZ, 1, 5), (JNZ, 6, 3), (LDC, 12, 0), (OUT_, 12, 0), (HALT,),
                 (LDC, 14, 1), (OUT_, 0, 14), (HALT,)])


def avoids(t):
    return t["toxic_share"] < .25 and t["safe"] + t["toxic"] >= 100


def controls():
    ho = heldout()
    C = chk1w() if MODE["tick"] else chk(1)
    g, c = trace(gen(1), ho), trace(C, ho)
    tr = []
    for gi in range(8):
        w, s = world1(("b122train", 12201, gi), .5); tr.append(round(lift(C, w, s) - lift(gen(1), w, s), 4))
    summ = {"GEN1": g, "CHK1": c, "checker": "CHK1w" if MODE["tick"] else "CHK1", "GEN1_lift": round(sum(lift(gen(1), w, s) for w, s in ho) / len(ho), 4),
            "CHK1_lift": round(sum(lift(C, w, s) for w, s in ho) / len(ho), 4), "train_gain": tr, "train_pos": sum(x > 0 for x in tr)}
    summ["pred"] = .35 <= g["toxic_share"] <= .65 and c["toxic_share"] < .02 and avoids(c) and summ["train_pos"] >= 6
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B122_controls.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    return summ


def cell(job):
    MODE["tick"] = job.get("tick", False); OUTX = OUT.parent / ("B122b_short_chain_tick" if MODE["tick"] else OUT.name)
    globals()["OUT"] = OUTX; OUTX.mkdir(parents=True, exist_ok=True)
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world1(("b122train", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b122", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    ho = heldout(); t = trace(m, ho)
    return {"arm": job["arm"], "seed": job["seed"], "mean_lift": round(sum(lift(m, w, s) for w, s in ho) / len(ho), 4),
            "toxic_share": t["toxic_share"], "harvests": t["safe"] + t["toxic"], "avoids": avoids(t)}


def main(argv):
    global OUT
    tick = "b" in argv; argv = [a for a in argv if a != "b"]; MODE["tick"] = tick
    if tick:
        OUT = OUT.parent / "B122b_short_chain_tick"
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        controls(); return 0
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    cf = OUT / "B122_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    base = 12211 if tick else 12201
    jobs = [j for j in ({"arm": a, "seed": base + i, "G": G_, "tick": tick} for i in range(8) for a in ("TOXIC", "PLAIN")) if (j["arm"], j["seed"]) not in done]
    with ProcessPoolExecutor(max_workers=W) as ex:
        futs = {ex.submit(cell, j): j for j in jobs}
        for fu in as_completed(futs):
            j = futs[fu]
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": j["arm"], "seed": j["seed"], "error": repr(e)[:300]}
            print(json.dumps(r), flush=True)
            with open(cf, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    rows = [json.loads(l) for l in open(cf, encoding="utf-8")]
    summ = {a: sum(r.get("avoids", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] >= 3 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B122_result.json").write_text(json.dumps({"probe": "B122", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
