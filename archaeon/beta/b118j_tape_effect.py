"""B118j -- does the seed's TAPE SIZE matter? (review packet weakness 6b)

B118f's tape-100 cells gave 3/7 readers; the tape-128 runs (B118g 4/8 info; B118i 6/8 behaviour) did as well or
better. The two seeds differ only in tape_words: the program is identical and uses no LD/ST/JMP, so behaviour is
identical. They differ in which shrunken tapes the halve/double mutation can reach (128 -> 64 -> 32 -> 16; 100 -> 50
is INVALID, and crashed one B118f cell) and in tape-relative semantics after mutation (LD/ST/JMP are taken mod
tape_words).
B118j: the B118i design (family 1, TOXIC arm, behavioural readout), seeds 11851-11858 PAIRED with B118i's TOXIC cells,
but gen 0 = GEN(3) with tape_words 96 (96 -> 48 -> 24 are all valid multiples of 4; 12 is out of bounds).
PREDICTION (committed before running), no-tape-effect hypothesis: TOXIC avoids >= 4/8 on tape 96 (B118i tape 128:
6/8). A result <= 3/8 would indicate the tape-128 seed is privileged (weakness 6b real).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b118c_interleaved as C
import archaeon.beta.b118d_seeded_forager as D
from archaeon.beta.b118h_decode import trace

OUT = Path(__file__).resolve().parent / "results" / "B118j_tape_effect"


def _gen96(R):
    m = dict(_GEN(R)); m["tape_words"] = 96; assert len(m["genome"]) <= 96 - 8; return m


_GEN = C.gen


def cell(job):
    D.gen = _gen96; D.OUT = OUT
    assert D.gen(3)["tape_words"] == 96
    r = D.cell(job)
    m = json.loads((OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    t = trace(m, D.heldout())
    r.update({"toxic_share": t["toxic_share"], "harvests": t["safe"] + t["toxic"], "avoids": t["toxic_share"] < .25, "tape_seed": 96,
              "final_tape": m["tape_words"]})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    G_ = int(argv[0]) if argv else 300; W = int(argv[1]) if len(argv) > 1 else 8
    hc = D.hcontrols(D.heldout())
    cf = OUT / "B118j_cells.jsonl"
    done = {json.loads(l)["seed"] for l in open(cf, encoding="utf-8")} if cf.exists() else set()
    jobs = [{"arm": "TOXIC", "seed": 11851 + i, "G": G_, "gen_lift": hc["GEN3"]["mean_lift"]} for i in range(8) if 11851 + i not in done]
    with ProcessPoolExecutor(max_workers=W) as ex:
        futs = {ex.submit(cell, j): j for j in jobs}
        for fu in as_completed(futs):
            j = futs[fu]
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": "TOXIC", "seed": j["seed"], "error": repr(e)[:300]}
            print(json.dumps(r), flush=True)
            with open(cf, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    rows = [json.loads(l) for l in open(cf, encoding="utf-8")]
    b118i = {r["seed"]: r for r in (json.loads(l) for l in open(OUT.parent / "B118i_family1_behaviour" / "B118i_cells.jsonl", encoding="utf-8"))
             if r.get("arm") == "TOXIC"}
    k = sum(r.get("avoids", False) for r in rows)
    pairs = [(r["seed"], b118i.get(r["seed"], {}).get("avoids"), r.get("avoids")) for r in rows]
    summ = {"tape96_avoids": k, "n": len(rows), "tape128_avoids_same_seeds": sum(bool(p[1]) for p in pairs), "pairs": pairs, "pred": k >= 4}
    print(json.dumps(summ))
    (OUT / "B118j_result.json").write_text(json.dumps({"probe": "B118j", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
