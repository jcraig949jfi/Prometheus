"""B120 -- DISTANCE ISOLATION for the reward-semantics result (review packet weakness 6e).

B118b (types at the END of channel 0, random gen 0) failed 0/4; B118f/g (types INTERLEAVED, gen 0 = a working
forager) met 8/16. Two things changed at once: layout AND gen 0. B120 isolates layout. It uses the B118g design
(R = 3 family-1 worlds, gen 0 = 200 x a working forager, tape 128, strong Toxic, TOXIC vs PLAIN, G=300), but with
the type words APPENDED at the end of channel 0 (b118_toxic.Toxic layout), ~7 words past the pools.
Hand programs for this layout: GENe = B29 generalist(3) (reads 3 pools, ignores the rest); CHKe = b118_toxic.checker
(reads pools, skips the gap, reads types). Both are rebuilt with tape 128 (generalist's 88 halves to an invalid 22).
Readout = constant-twin type info for the END layout (last R words fixed to 0 or to 1), semantic = info > .01.
Seeds 12001-12004 per arm (8 cells).
STEP 1 CONTROLS (prediction committed before running): CHKe info > .03 and GENe info = 0 on the held-out set
('b120ho', 12 worlds); training-side CHKe - GENe > 0 on >= 6/8 training worlds.
STEP 2 PREDICTION (committed before running), distance hypothesis: TOXIC semantic <= 1/4 (vs B118g 4/8 interleaved);
PLAIN 0/4. If TOXIC >= 2/4, distance is NOT what blocked B118b (gen 0 was).
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.beta.b32_world_distribution import echo_free_world
from archaeon.beta.b118_toxic import Toxic, checker, lift
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B120_distance_isolation"


def world_e(key, p):
    for t in range(60):
        w, s = echo_free_world(key + (t,))
        if w.w.R == 3:
            break
    assert w.w.R == 3, key
    return NoClock(Toxic(w.w, p, 2.0)), s


def tape128(m):
    """Power-of-two tape (>= 128): the GA halves/doubles tape_words. GENe fits 128; CHKe (control only) may need 256."""
    m = dict(m); tw = 128
    while tw < len(m["genome"]) + 16:
        tw *= 2
    m["tape_words"] = tw; return m


def gen_e():
    return tape128(generalist(3))


def chk_e(w, s):
    return tape128(checker(w, s))


class ConstEnd:
    def __init__(self, w, c):
        self.w = w; self.c = c; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.w.w.R
        return [obs[0][:-R] + [self.c] * R] + obs[1:]


def info(m, ho):
    full = sum(lift(m, w, s) for w, s in ho) / len(ho)
    cs = {c: sum(lift(m, ConstEnd(w, c), s) for w, s in ho) / len(ho) for c in (0, 1)}
    return {"full": round(full, 4), "const0": round(cs[0], 4), "const1": round(cs[1], 4), "info": round(full - max(cs.values()), 4)}


def heldout(n=12):
    return [world_e(("b120ho", i), .5) for i in range(n)]


def controls():
    ho = heldout()
    g = info(gen_e(), ho)
    full = sum(lift(chk_e(w, s), w, s) for w, s in ho) / len(ho)
    cs = {c: sum(lift(chk_e(w, s), ConstEnd(w, c), s) for w, s in ho) / len(ho) for c in (0, 1)}
    c = {"full": round(full, 4), "info": round(full - max(cs.values()), 4)}
    tr = []
    for gi in range(8):
        w, s = world_e(("b120train", 12001, gi), .5); tr.append(round(lift(chk_e(w, s), w, s) - lift(gen_e(), w, s), 4))
    summ = {"GENe": g, "CHKe": c, "train_gain": tr, "train_pos": sum(x > 0 for x in tr)}
    summ["pred"] = c["info"] > .03 and abs(g["info"]) < 1e-9 and summ["train_pos"] >= 6
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B120_controls.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    return summ


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world_e(("b120train", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    rec = G.organism_record(gen_e(), None, 0); rec["origins"] = ["gen0_GENe"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b120", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x GENe (tape 128)", "verified_common": True})
    for g in range(job["G"]):
        state["g"] = g
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(m), encoding="utf-8")
    i = info(m, heldout())
    return {"arm": job["arm"], "seed": job["seed"], "mean_lift": i["full"], "type_info": i["info"], "const0": i["const0"], "const1": i["const1"],
            "semantic": i["info"] > .01}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        controls(); return 0
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    cf = OUT / "B120_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [j for j in ({"arm": a, "seed": 12001 + i, "G": G_} for i in range(4) for a in ("TOXIC", "PLAIN")) if (j["arm"], j["seed"]) not in done]
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
    summ = {a: sum(r.get("semantic", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] <= 1 and summ["PLAIN"] == 0
    print(json.dumps(summ))
    (OUT / "B120_result.json").write_text(json.dumps({"probe": "B120", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
