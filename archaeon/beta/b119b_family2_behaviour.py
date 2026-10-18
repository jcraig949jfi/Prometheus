"""B119b -- PREREGISTERED family-2 replication with the BEHAVIOURAL readout fixed in advance.

B119 (family 2, constant-twin readout): TOXIC 3/8, PLAIN 2/8 -- prediction FAILED (PLAIN false positives: an
accidental reaction to a non-zero type word is credited as information).
B121 (exploratory; readout chosen after the B119 decode): toxic share of harvests < .25 separates the arms --
family 1 TOXIC 12/20 vs PLAIN 1/20; family 2 TOXIC 7/8 vs PLAIN 0/8. The one PLAIN avoider (B118f 11837: 27 toxic of
544 harvests) shows the accidental-avoidance base rate (~1/28 PLAIN overall).
B119b: the B119 design (P-boom-lineage family 2, interleaved strong Toxic, gen 0 = 200 x GEN(3) tape 128, G=300),
NEW seeds 11911-11918 per arm, held-out ('b119ho', 12 worlds).
READOUT (fixed in advance): avoids = toxic share of harvests < .25 on the held-out set (b118h_decode.trace).
The constant-twin info is also reported.
PREDICTION (committed before running): TOXIC avoids >= 5/8 AND PLAIN avoids <= 1/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b118d_seeded_forager as D
import archaeon.beta.b119_semantics_family2 as F2
from archaeon.beta.b118c_interleaved import gen
from archaeon.beta.b118e_type_info import info
from archaeon.beta.b118h_decode import trace

OUT = Path(__file__).resolve().parent / "results" / "B119b_family2_behaviour"


def cell(job):
    F2._patch(); D.OUT = OUT; assert gen(3)["tape_words"] == 128
    r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    ho = D.heldout(); i = info(m, ho); t = trace(m, ho)
    r.update({"type_info": i["info"], "toxic_share": t["toxic_share"], "harvests": t["safe"] + t["toxic"], "avoids": t["toxic_share"] < .25})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    F2._patch(); D.OUT = OUT
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    cf = OUT / "B119b_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [j for j in ({"arm": a, "seed": 11911 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) for a in ("TOXIC", "PLAIN"))
            if (j["arm"], j["seed"]) not in done]
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
    summ = {a: sum(r.get("avoids", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] >= 5 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B119b_result.json").write_text(json.dumps({"probe": "B119b", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
