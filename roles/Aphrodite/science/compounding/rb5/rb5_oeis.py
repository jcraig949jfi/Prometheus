"""RB-5 part (b)+(c)+(2): OEIS subset -> fold tasks, witness search, analysis
(forensic, not a disposition).

Mapping: list = the first k terms a(0..k-1) (k in 4..9 on dev), query m = k (the
index of the requested term, 0-based position in the OEIS data), answer = a(k).
Dev = the six instances k = 4..9; holdout = k = 10..19 (terms <= CEIL).
Search: G4 (all inits, bodies, finals + expr shape). If no verified G4 witness
class is T4-admissible AND Q2-qualified, also the G5 depth-3 extras with the G5
catalog's H1 inits {0, 1} (a17.draws convention). HOST NOTE: the host was
CPU-saturated by other jobs, so after the first 182 sequences (which got G5
whenever G4 did not qualify) G5 runs only on selection index % 3 == 0.
Usage: python rb5_oeis.py [limit]
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rb5_common as C      # noqa: E402

FULL_G5 = {}     # rows searched before the subsample rule (first 182 rows) searched G5 fully

OUT = HERE / "OEIS_SEARCH.jsonl"


def instances(t):
    dev = [(t[:k] + [k], t[k]) for k in range(4, 10)]
    hold = [(t[:k] + [k], t[k]) for k in range(10, min(len(t), 20))
            if all(abs(x) <= C.CEIL for x in t[:k + 1])]
    return dev, hold


G5_EVERY = 3     # G5 subsample (host saturated): selection index % 3 == 0, fixed a priori


def job(item):
    idx, seq = item
    t0 = time.time()
    t = seq["terms"]
    dev, hold = instances(t)
    row = {"A": seq["A"], "strata": seq["strata"], "recurrence": seq["recurrence"],
           "n_holdout": len(hold)}
    res = {}
    for grammar in ("g4", "g5"):
        if grammar == "g5":
            if res["g4"]["summary"]["q2_qualified"]:
                break
            if idx % G5_EVERY != 0 and not FULL_G5.get(seq["A"]):
                row["g5_searched"] = False
                break
            bodies = C.g5_extras()
            inits = C.G.H1_SPACE
        else:
            bodies, inits = C.G.BODY_SPACE, None
        h = C.search([n for n, _ in dev], {"s": tuple(g for _, g in dev)}, bodies,
                     inits=inits, cap=200, per_body=3, expr=(grammar == "g4")).get("s", [])
        ver = [p for p in h if C.verify(p, hold)]
        cls = C.analyse_family(ver)
        res[grammar] = {"dev_hits": len(h), "verified": len(ver),
                        "classes": cls, "summary": C.family_summary(cls)}
    row.setdefault("g5_searched", "g5" in res)
    row["sel_index"] = idx
    row.update(res)
    row["seconds"] = round(time.time() - t0, 1)
    return row


def main():
    sel = json.loads((HERE / "cache" / "oeis_selection_rb5.json").read_text(encoding="utf-8"))
    seqs = sel["sequences"]
    if len(sys.argv) > 1:
        seqs = seqs[: int(sys.argv[1])]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["A"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
    todo = [(i, s) for i, s in enumerate(seqs) if s["A"] not in done]
    print("todo", len(todo), "done", len(done), flush=True)
    with ProcessPoolExecutor(max_workers=C.WORKERS, initializer=C.worker_init) as ex, \
            OUT.open("a", encoding="utf-8") as fh:
        for i, row in enumerate(ex.map(job, todo)):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            if i % 10 == 0:
                print(i, row["A"], row["seconds"], row["g4"]["summary"]["expressible"], flush=True)


if __name__ == "__main__":
    main()
