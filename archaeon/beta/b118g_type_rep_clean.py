"""B118g -- CLEAN replication of B118f on a single seed manifest (tape_words 128 for every cell).

B118f RESULT: TOXIC semantic 4/8, PLAIN 0/8 -- prediction MET by the letter (Fisher one-sided p ~ .038). But the
deciding cell (TOXIC 11833, the strongest of the series: info .058, lift .085) was a RERUN on a modified seed (hand
GEN(3) with tape_words 128 instead of 100, after the 100 -> 50 halving crash). The other 15 cells used tape 100.
Excluding the rerun, TOXIC is 3/7. So B118f is a mixed-seed design and its 'met' is provisional.
B118g: the B118d/B118f design with EVERY cell on the tape-128 seed (b118c._man rounds to a power of two), NEW seeds
11841-11848 per arm (16 cells, waves of <= 8 procs, resumable). Readout fixed as in B118f: semantic = constant-twin
type info > .01 on the B118d held-out set.
PREDICTION (committed before running): TOXIC semantic >= 4/8 AND PLAIN semantic <= 1/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b118d_seeded_forager as D
from archaeon.beta.b118c_interleaved import gen
from archaeon.beta.b118e_type_info import info

OUT = Path(__file__).resolve().parent / "results" / "B118g_type_rep_clean"


def cell(job):
    assert gen(3)["tape_words"] == 128
    D.OUT = OUT; r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    i = info(m, D.heldout()); r.update({"type_info": i["info"], "const0": i["const0"], "const1": i["const1"], "semantic": i["info"] > .01})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    cf = OUT / "B118g_cells.jsonl"
    done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [{"arm": a, "seed": 11841 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) for a in ("TOXIC", "PLAIN")]
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
    summ = {a: sum(r.get("semantic", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["n"] = len(rows); summ["errors"] = sum("error" in r for r in rows); summ["pred"] = summ["TOXIC"] >= 4 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B118g_result.json").write_text(json.dumps({"probe": "B118g", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
