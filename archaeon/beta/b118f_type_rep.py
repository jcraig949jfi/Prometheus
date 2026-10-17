"""B118f -- PREREGISTERED replication of the weak type-reading signal (B118c/B118d).

B118d RESULT: TOXIC 1/4 type-reading by the prereg bar (11821: lift .035, use .035), PLAIN 0/4. Prediction (>= 2/4)
FAILED. Exploratory, post hoc (B118e constant-twin info = lift - max lift with every type word fixed to 0 or 1):
TOXIC .035 / .025 / .011 / 0; PLAIN 0 / -.014 / 0 / (.004 use). With B118c, TOXIC 5/8 > .01 vs PLAIN 0/8
(Fisher p ~ .013, but the .01 threshold and the pooling were chosen after seeing the data).
B118f fixes the readout IN ADVANCE: semantic = constant-twin type info > .01 on the B118d held-out set.
Design = B118d (R = 3 interleaved strong Toxic, gen 0 = 200 x GEN(3), G=300) with NEW seeds 11831-11838 per arm,
16 cells, run in waves of <= 8 procs.
PREDICTION (committed before running): TOXIC semantic >= 4/8 AND PLAIN semantic <= 1/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b118d_seeded_forager as D
from archaeon.beta.b118e_type_info import info

OUT = Path(__file__).resolve().parent / "results" / "B118f_type_rep"


def cell(job):
    D.OUT = OUT; r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    i = info(m, D.heldout()); r.update({"type_info": i["info"], "const0": i["const0"], "const1": i["const1"], "semantic": i["info"] > .01})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout()); print("heldout_controls", json.dumps(hc), flush=True)
    done = set()
    if (OUT / "B118f_cells.jsonl").exists():
        done = {(json.loads(l)["arm"], json.loads(l)["seed"]) for l in open(OUT / "B118f_cells.jsonl", encoding="utf-8")}
    jobs = [{"arm": a, "seed": 11831 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) for a in ("TOXIC", "PLAIN")]
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
            with open(OUT / "B118f_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    rows = [json.loads(l) for l in open(OUT / "B118f_cells.jsonl", encoding="utf-8")]
    summ = {a: sum(r.get("semantic", False) for r in rows if r.get("arm") == a) for a in ("TOXIC", "PLAIN")}
    summ["n"] = len(rows); summ["pred"] = summ["TOXIC"] >= 4 and summ["PLAIN"] <= 1
    print(json.dumps(summ))
    (OUT / "B118f_result.json").write_text(json.dumps({"probe": "B118f", "heldout_controls": hc, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
