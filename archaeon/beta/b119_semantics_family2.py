"""B119 -- SECOND WORLD FAMILY for the reward-semantics result (ensemble invariance for B118d/f/g).

B118f/g (family 1 = the C6 procedural generator, echo-free, R = 3): TOXIC 8/16 type readers vs PLAIN 0/16.
Family 2 = the P-BOOM base world (B32 v1 style), a different generator lineage: P-boom params with
resources.types = 3, history OFF (it makes pool 0 pay only after harvests elsewhere, which is confounded with
toxicity), and per-world redraws of locality.nodes (6..16), deplete (.2-.7), regen (.1-.4). Other P-boom features kept
(objects, hazards lethal, coupling, 4 channels). Wrapped NoClock(IToxic(.)), interleaved layout, strong toxicity.
STEP 1 CONTROLS (12 worlds, keys ('b119ctl', i)), PREDICTION committed before running:
  (a) GEN3 lift lower on Toxic than on p = 0 in >= 9/12;
  (b) CHK3 - GEN3 on Toxic: mean > .02, positive in >= 9/12;
  (c) training-side value: CHK3 - GEN3 > 0 on >= 6/8 training worlds of seed 11901.
STEP 2 (only if (a)-(c) hold): the B118g design on family 2 -- gen 0 = 200 x GEN(3) (tape 128), TOXIC vs PLAIN,
seeds 11901-11908, G=300, readout semantic = constant-twin type info > .01 on held-out ('b119ho', 12 worlds).
PREDICTION (committed before running): TOXIC semantic >= 3/8 AND PLAIN <= 1/8.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

import archaeon.beta.b118d_seeded_forager as D
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b32_world_distribution import _base
from archaeon.beta.b118_toxic import lift
from archaeon.beta.b118c_interleaved import IToxic, chk, gen
from archaeon.beta.b118e_type_info import info
from archaeon.campaign6.worlds.runtime import ComposedWorld

OUT = Path(__file__).resolve().parent / "results" / "B119_semantics_family2"


def world_f2(key, p):
    rng = SplitMix64(seed_from("archaeon.beta.b119.family2", *key))
    q = copy.deepcopy(_base().params)
    q["resources"] = dict(q["resources"], types=3, deplete=.2 + rng.randbelow(501) / 1000, regen=.1 + rng.randbelow(301) / 1000)
    q["locality"] = dict(q["locality"], nodes=6 + rng.randbelow(11))
    q["history"] = {"on": False}
    cw = ComposedWorld(q)
    assert cw.R == 3
    return NoClock(IToxic(cw, p, 2.0)), 1000 + rng.randbelow(10 ** 6)


def controls(n=12):
    rows = []
    for i in range(n):
        wt, s = world_f2(("b119ctl", i), .5); wp, _ = world_f2(("b119ctl", i), 0.0)
        r = {"i": i, "gen_plain": round(lift(gen(3), wp, s), 4), "gen_toxic": round(lift(gen(3), wt, s), 4), "chk_toxic": round(lift(chk(3), wt, s), 4)}
        rows.append(r); print(json.dumps(r), flush=True)
    tr = []
    for g in range(8):
        w, s = world_f2(("b119train", 11901, g), .5); tr.append(round(lift(chk(3), w, s) - lift(gen(3), w, s), 4))
    b = [r["chk_toxic"] - r["gen_toxic"] for r in rows]
    summ = {"a_lower": sum(r["gen_toxic"] < r["gen_plain"] for r in rows), "b_mean_gain": round(sum(b) / n, 4), "b_pos": sum(x > 0 for x in b),
            "train_gain": tr, "c_pos": sum(x > 0 for x in tr)}
    summ["pred_a"] = summ["a_lower"] >= 9; summ["pred_b"] = summ["b_mean_gain"] > .02 and summ["b_pos"] >= 9; summ["pred_c"] = summ["c_pos"] >= 6
    print(json.dumps(summ)); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "B119_controls.json").write_text(json.dumps({"rows": rows, "summary": summ}, indent=1), encoding="utf-8")
    return summ


def _patch():
    D.world3 = lambda key, p: world_f2(("b119train",) + tuple(key[1:]), p) if key and key[0] == "b118dtrain" else world_f2(key, p)
    D.heldout = lambda n=12: [world_f2(("b119ho", i), .5) for i in range(n)]
    D.OUT = OUT


def cell(job):
    _patch(); assert gen(3)["tape_words"] == 128
    r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    i = info(m, D.heldout()); r.update({"type_info": i["info"], "const0": i["const0"], "const1": i["const1"], "semantic": i["info"] > .01})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        controls(); return 0
    _patch(); G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    cf = OUT / "B119_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [{"arm": a, "seed": 11901 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) for a in ("TOXIC", "PLAIN")]
    jobs = [j for j in jobs if (j["arm"], j["seed"]) not in done]
    if len(argv) > 2:
        jobs = jobs[:int(argv[2])]
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
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] >= 3 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B119_result.json").write_text(json.dumps({"probe": "B119", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
