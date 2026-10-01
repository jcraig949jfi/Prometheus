"""W2-20 check: replay W2-13 search worker 0's RNG stream (seed 20261013, 30,000 genomes) and re-screen every genome that
is S_late-eligible (first copy site >= 35). W2-13 screened all of them (its filter passes any genome with a copy site), so
the replay must recover exactly W2-13 w0's late hits. Tests screen reproducibility and explains the hit-rate difference.

    python -B replay_w13.py -> replay_w13.json
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


def first_copy(g):
    for i in range(64):
        if g[i] in (0xE5, 0xE7) or (i < 63 and g[i] == 0xED and g[i + 1] in (0xB0, 0xB8)):
            return i
    return None


rng = random.Random(20261013)
t0 = time.process_time()
rec = json.load(open(HERE.parent / "W2-13_chain_length_epistasis" / "hits_w0.json"))
w13 = {h["k"] for h in rec["hits"]}
res = {"n": 0, "n_eligible": 0, "hits": [], "w13_hits_eligible": []}
for k in range(30000):
    g = bytes(rng.randrange(256) for _ in range(64))
    res["n"] += 1
    f = first_copy(g)
    if k in w13 and f is not None and f >= 35:
        res["w13_hits_eligible"].append(k)
    if f is not None and f >= 35:
        res["n_eligible"] += 1
        if S.competent("7ae3", g, True):
            res["hits"].append([k, f])
res["match"] = sorted(h[0] for h in res["hits"]) == sorted(res["w13_hits_eligible"])
res["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(res, open(HERE / "replay_w13.json", "w"))
print(res)
