"""W2-20 step 1: S_late random-hit search (see PREREG.txt). Same screen and cell as W2-13 search_hits.py.

    python -B search_late.py WORKER  -> hits_w<WORKER>.json
Uniform random 64-byte genome; accepted for the exact S3 COMPETENT screen iff first copy-op site >= 35.
Every 20th rejected genome is also screened (validation only; such hits are not S_late hits).
Stop at 6 S_late hits or 270 CPU-s.
"""
import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))
import s3_common as S  # noqa: E402

CELL = "7ae3"
CUT = 35
MAXH, MAXS = 6, 270.0
W = int(sys.argv[1])
rng = random.Random(20261020 + 1000 * W)
OUT = HERE / ("hits_w%d.json" % W)


def first_copy(g):
    for i in range(64):
        if g[i] in (0xE5, 0xE7) or (i < 63 and g[i] == 0xED and g[i + 1] in (0xB0, 0xB8)):
            return i
    return None


t0 = time.process_time()
res = {"worker": W, "n": 0, "n_accept": 0, "n_reject": 0, "n_reject_screened": 0, "reject_hits": [], "hits": [],
       "cpu_s": 0, "first_copy_hist_accepted": {}}
k = -1
while len(res["hits"]) < MAXH and time.process_time() - t0 < MAXS:
    k += 1
    g = bytes(rng.randrange(256) for _ in range(64))
    res["n"] += 1
    f = first_copy(g)
    if f is not None and f >= CUT:
        res["n_accept"] += 1
        if S.competent(CELL, g, True):
            res["hits"].append({"hex": g.hex(), "k": k, "first_copy": f})
            print("HIT", W, k, f, len(res["hits"]), round(time.process_time() - t0, 1), flush=True)
    else:
        res["n_reject"] += 1
        if res["n_reject"] % 20 == 0:
            res["n_reject_screened"] += 1
            if S.competent(CELL, g, True):
                res["reject_hits"].append({"hex": g.hex(), "k": k, "first_copy": f})
    if k % 2000 == 0:
        res["cpu_s"] = round(time.process_time() - t0, 1)
        OUT.write_text(json.dumps(res))
res["cpu_s"] = round(time.process_time() - t0, 1)
OUT.write_text(json.dumps(res))
print("done", W, res["n"], res["n_accept"], len(res["hits"]), res["cpu_s"], flush=True)
