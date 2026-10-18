"""B124 -- CLEAN distance test: block layout with a precursor that ALREADY reads the type words (repairs B123).

B123 (block layout, gen 0 = GENb reading only the 3 pools): TOXIC 0/8. Confounded: the interleaved GEN already READS
each type word (into dummy r13), the block GENb did not, so edits-from-precursor differed (~2 vs ~6).
B124: block layout [p0,p1,p2,t0,t1,t2,rest], gen 0 = GENb+ = IN p0..p2 into r1-r3, then IN t0..t2 into dummy r13,
then the generalist blocks. The type check is now the SAME edit count as from the interleaved GEN (retarget a type
IN to a usable register + insert a JNZ). Only the instruction distance between pool i's read and type i's read
differs (block: 3; interleaved: 1).
Readout (fixed in advance): avoids = toxic share < .25 on held-out ('b123ho', 12 worlds).
Arms: TOXIC seeds 12401-12408, PLAIN 12401-12404.
CONTROLS (committed before running): GENb+ share .35-.65; CHKb share < .02 (reuse B123); training-side CHKb - GENb+ > 0
on >= 6/8.
PREDICTION (committed before running), edits-count conjecture: TOXIC avoids >= 4/8 (interleaved-like) AND PLAIN <= 1/4.
If TOXIC <= 1/8, instruction distance itself matters (not only the edit count).
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, IN, JZ, LDC, OUT_, REGIMES, TARGET
from archaeon.beta.b118_toxic import lift
from archaeon.beta.b118c_interleaved import _man
from archaeon.beta.b118h_decode import trace
from archaeon.beta.b123_distance_dose import chk_b, heldout, world_b
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B124_clean_distance"


def gen_bplus():
    prog = [(IN, 1 + i, 0) for i in range(3)] + [(IN, 13, 0)] * 3
    for i in range(3):
        prog += [(JZ, 1 + i, 4), (LDC, 12, i), (OUT_, 12, 0), (HALT,)]
    return _man(prog + [(LDC, 14, 1), (OUT_, 0, 14), (HALT,)])


def controls():
    ho = heldout(); g, c = trace(gen_bplus(), ho), trace(chk_b(), ho)
    tr = []
    for gi in range(8):
        w, s = world_b(("b124train", 12401, gi), .5); tr.append(round(lift(chk_b(), w, s) - lift(gen_bplus(), w, s), 4))
    summ = {"GENbplus": g, "CHKb": c, "tape": gen_bplus()["tape_words"], "train_gain": tr, "train_pos": sum(x > 0 for x in tr)}
    summ["pred"] = .35 <= g["toxic_share"] <= .65 and c["toxic_share"] < .02 and summ["train_pos"] >= 6
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B124_controls.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    return summ


def cell(job):
    state = {"g": 0}; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        k = (job["arm"], job["seed"], state["g"])
        if k not in cache:
            cache.clear(); cache[k] = world_b(("b124train", job["seed"], state["g"]), .5 if job["arm"] == "TOXIC" else 0.0)
        w, s = cache[k]
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    rec = G.organism_record(gen_bplus(), None, 0); rec["origins"] = ["gen0_GENbplus"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b124", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x GENb+ (tape 128)", "verified_common": True})
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
    cf = OUT / "B124_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [{"arm": "TOXIC", "seed": 12401 + i, "G": G_} for i in range(8)] + [{"arm": "PLAIN", "seed": 12401 + i, "G": G_} for i in range(4)]
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
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] >= 4 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B124_result.json").write_text(json.dumps({"probe": "B124", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
