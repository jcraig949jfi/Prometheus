"""W2-13 step 1: random-hit competent genomes on the dense VM (cell 7ae3 runner, S3 fast exact COMPETENT screen).

    python -B search_hits.py WORKER NGENOMES   -> hits_wWORKER.json
Uniform random 64-byte genomes, RNG seed 20261013 + 1000*WORKER. Pre-filter (static, cheap): the genome contains a dense
single-byte copy op (E5/E7) or ED B0 / ED B8. Every genome passing the filter gets the full S3 COMPETENT screen
(s3_common.competent, exact). Filter validation: every 10th REJECTED genome also gets the full screen; any hit there is
recorded as a filter miss (and also kept as a hit, flagged).
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
W = int(sys.argv[1]); N = int(sys.argv[2])
rng = random.Random(20261013 + 1000 * W)
OUT = HERE / ("hits_w%d.json" % W)


def filt(g):
    return any(b in (0xE5, 0xE7) for b in g) or any(g[i] == 0xED and g[i + 1] in (0xB0, 0xB8) for i in range(63))


t0 = time.process_time()
res = {"worker": W, "n": 0, "n_filter_pass": 0, "n_filter_reject": 0, "n_reject_screened": 0, "filter_misses": [],
       "hits": [], "cpu_s": 0}
for k in range(N):
    g = bytes(rng.randrange(256) for _ in range(64))
    res["n"] += 1
    if filt(g):
        res["n_filter_pass"] += 1
        if S.competent(CELL, g, True):
            res["hits"].append({"hex": g.hex(), "k": k, "filter": True})
            print("HIT", W, k, len(res["hits"]), round(time.process_time() - t0, 1), flush=True)
    else:
        res["n_filter_reject"] += 1
        if res["n_filter_reject"] % 10 == 0:
            res["n_reject_screened"] += 1
            if S.competent(CELL, g, True):
                res["filter_misses"].append(g.hex())
                res["hits"].append({"hex": g.hex(), "k": k, "filter": False})
                print("MISS", W, k, flush=True)
    if k % 2000 == 0:
        res["cpu_s"] = round(time.process_time() - t0, 1)
        OUT.write_text(json.dumps(res))
res["cpu_s"] = round(time.process_time() - t0, 1)
OUT.write_text(json.dumps(res))
print("done", W, res["n"], res["n_filter_pass"], len(res["hits"]), res["cpu_s"], flush=True)
