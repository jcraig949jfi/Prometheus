"""B123 -- DOSE-RESPONSE in read-chain distance for reward semantics (clean single-variable test of the conjecture).

Same world family (family 1, R = 3, strong Toxic), same gen 0 (a working forager, tape 128), same search; ONLY the
position of the type words varies:
  interleaved [p0,t0,p1,t1,p2,t2, rest]   distance 1   B118i/f/g: avoid 6/8 (behaviour), 12/16 on preregs
  BLOCK       [p0,p1,p2,t0,t1,t2, rest]   distance 3   THIS RUN
  end         [p0,p1,p2, rest..., t0,t1,t2] distance ~7  B120: 0/4
Hand programs for the block layout: GENb = B29 generalist(3) (reads 3 pools only), tape 128; CHKb = reads 3 pools, then
3 types, harvests the first non-empty SAFE pool, else moves.
Readout (fixed in advance): avoids = toxic share of harvests < .25 on held-out ('b123ho', 12 worlds).
Arms: TOXIC seeds 12301-12308, PLAIN seeds 12301-12304 (12 cells; budget).
CONTROLS (committed before running): GENb share .35-.65; CHKb share < .02; training-side CHKb - GENb > 0 on >= 6/8.
PREDICTION (committed before running), dose-response: TOXIC avoids in [1, 5] of 8 -- strictly between the end layout
(0/4) and the interleaved rate (6/8); PLAIN <= 1/4. Fails if TOXIC is 0/8 (distance 3 already blocks) or >= 6/8
(distance 3 costs nothing).
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, IN, JNZ, JZ, LDC, OUT_, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import Toxic, lift
from archaeon.beta.b118c_interleaved import _man
from archaeon.beta.b118h_decode import trace
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B123_distance_dose"


class BToxic(Toxic):
    """Type words as a BLOCK right after the pools: [p0, p1, p2, t0, t1, t2, rest]."""

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.R
        loc = "locality" in self.w.features
        types = [1 if (t and ((not loc) or st["pool_node"][i] == st["pos"])) else 0 for i, t in enumerate(st["toxic"])]
        ch = obs[0]; head = ch[:2]; pools = ch[2:2 + R]; rest = ch[2 + R:]
        return [head + pools + types + rest] + obs[1:]


def world_b(key, p):
    for t in range(60):
        w, s = echo_free_world(key + (t,))
        if w.w.R == 3:
            break
    assert w.w.R == 3, key
    return NoClock(BToxic(w.w, p, 2.0)), s


def gen_b():
    m = dict(generalist(3)); m["tape_words"] = 128; return m


def chk_b():
    prog = [(IN, 1 + i, 0) for i in range(3)] + [(IN, 6 + i, 0) for i in range(3)]
    for i in range(3):
        prog += [(JZ, 1 + i, 5), (JNZ, 6 + i, 4), (LDC, 12, i), (OUT_, 12, 0), (HALT,)]
    return _man(prog + [(LDC, 14, 1), (OUT_, 0, 14), (HALT,)])


def heldout(n=12):
    return [world_b(("b123ho", i), .5) for i in range(n)]


def controls():
    ho = heldout(); g, c = trace(gen_b(), ho), trace(chk_b(), ho)
    tr = []
    for gi in range(8):
        w, s = world_b(("b123train", 12301, gi), .5); tr.append(round(lift(chk_b(), w, s) - lift(gen_b(), w, s), 4))
    summ = {"GENb": g, "CHKb": c, "train_gain": tr, "train_pos": sum(x > 0 for x in tr)}
    summ["pred"] = .35 <= g["toxic_share"] <= .65 and c["toxic_share"] < .02 and summ["train_pos"] >= 6
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B123_controls.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    return summ


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world_b(("b123train", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    rec = G.organism_record(gen_b(), None, 0); rec["origins"] = ["gen0_GENb"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b123", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x GENb (tape 128)", "verified_common": True})
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    t = trace(m, heldout())
    return {"arm": job["arm"], "seed": job["seed"], "toxic_share": t["toxic_share"], "harvests": t["safe"] + t["toxic"], "avoids": t["toxic_share"] < .25}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        controls(); return 0
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    cf = OUT / "B123_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [{"arm": "TOXIC", "seed": 12301 + i, "G": G_} for i in range(8)] + [{"arm": "PLAIN", "seed": 12301 + i, "G": G_} for i in range(4)]
    jobs = [j for j in jobs if (j["arm"], j["seed"]) not in done]
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
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = 1 <= summ["TOXIC"] <= 5 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B123_result.json").write_text(json.dumps({"probe": "B123", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
