"""B71 -- third-world replication of Finding 4 (packet S3), on a procedural world OUTSIDE the C6 named set.

World: results/B71_world.json, chosen by the pre-set rule in b71_world_scan.py (first qualifier: index 0).
- R=3, L=12, K=4;
- features: resources, locality, coupling, channels only (no hazards / history / hidden / regime);
- teeth: generalist solo .346, 4 copies .090 each (.26x); lift over the best constant .204.
Arms CONC/SOLO/SHAM, seeds 7101-7106, G=200, via the B62 cell and the B64 regime-aware evaluator. Then:
- B63-style rare test (24 groups);
- B70 hardened rare test (niches >= 10, 48 groups, bootstrap lo > 0).
PREDICTION (before running):
- CONC entropy > SHAM by >= .2 in >= 4/6;
- CONC HET > HOM in >= 4/6 testable;
- hardened rare-type wins CONC >= 4/6, with SOLO + SHAM <= 1 in total.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b62_niche_attack as B62
import archaeon.beta.b64_niche_replication as B64
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.campaign6.worlds.runtime import ComposedWorld

RES = Path(__file__).resolve().parent / "results"
OUT = RES / "B71_third"
_W = {}


def load():
    if "w" not in _W:
        c = json.loads((RES / "B71_world.json").read_text(encoding="utf-8")); _W["w"] = (ComposedWorld(c["params"]), c["seed"], None)
    return _W["w"]


def _patch():
    B64.load = load; B64.OUT = OUT; B64._patch()


def cell(job):
    _patch(); return B62.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "rare":
        from archaeon.beta.b70_rare_hardened import test as hard
        _patch(); world, s, _ = load(); w = NoClock(world); rows = []
        for arm in ("CONC", "SOLO", "SHAM"):
            for sd in range(7101, 7107):
                f = OUT / ("B62_pop_%s_%d.json" % (arm, sd))
                if f.exists():
                    rows.append({"arm": arm, "seed": sd, **hard(json.loads(f.read_text(encoding="utf-8")), w, s, world.R, sd, B64.group_rewards)})
                    print(json.dumps(rows[-1]), flush=True)
        summ = {a: {"testable": sum(r["testable"] for r in rows if r["arm"] == a), "win": sum(r["win"] for r in rows if r["arm"] == a)} for a in ("CONC", "SOLO", "SHAM")}
        print(json.dumps(summ)); (OUT / "B71_rare_hardened.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
        return 0
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 7101 + i, "G": G_}): (a, i) for i in range(6) for a in ("CONC", "SOLO", "SHAM")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 7101 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B71_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    (OUT / "B71_result.json").write_text(json.dumps({"probe": "B71", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
