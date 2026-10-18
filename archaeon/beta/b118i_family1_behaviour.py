"""B118i -- PREREGISTERED family-1 run with the BEHAVIOURAL readout (one readout across both families).

Family 1 met a prereg on the constant-twin readout (B118g 4/8 vs 0/8). Family 2 met a prereg on the behavioural
readout (B119b: TOXIC 6/8 avoid vs PLAIN 0/8). The family-1 behavioural rate (B121, post hoc) was 12/20 vs 1/20.
To claim the result across families on ONE fixed readout, family 1 needs a behavioural prereg too.
B118i: the B118g design (family 1, R = 3 interleaved strong Toxic, gen 0 = 200 x GEN(3) tape 128, G=300), NEW seeds
11851-11858 per arm, held-out = the B118d set.
READOUT (fixed in advance): avoids = toxic share of harvests < .25 (b118h_decode.trace).
PREDICTION (committed before running): TOXIC avoids >= 4/8 AND PLAIN avoids <= 1/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b118d_seeded_forager as D
from archaeon.beta.b118c_interleaved import gen
from archaeon.beta.b118e_type_info import info
from archaeon.beta.b118h_decode import trace

OUT = Path(__file__).resolve().parent / "results" / "B118i_family1_behaviour"


def cell(job):
    D.OUT = OUT; assert gen(3)["tape_words"] == 128
    r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    ho = D.heldout(); i = info(m, ho); t = trace(m, ho)
    r.update({"type_info": i["info"], "toxic_share": t["toxic_share"], "harvests": t["safe"] + t["toxic"], "avoids": t["toxic_share"] < .25})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True); D.OUT = OUT
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    cf = OUT / "B118i_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [j for j in ({"arm": a, "seed": 11851 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) for a in ("TOXIC", "PLAIN"))
            if (j["arm"], j["seed"]) not in done]
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
    (OUT / "B118i_result.json").write_text(json.dumps({"probe": "B118i", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
