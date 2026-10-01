"""W2-13 step 2a: S3 pairwise screen on the new random-hit genomes (identical code path to W2-6 C2 / S3 comparators).

    python -B pairs_hits.py WORKER NWORKERS -> pairs_hits_wWORKER.json
Function = COMPETENT (as for the S3 state-dependent comparators and C2). Singles: 3 core_map draws at all 64 positions
(s3_pipeline.singles); dispensable <=> kept >= 2/3; p_i = lost/3; up to 100 pairs (s3_pipeline.sample_pairs);
pair_call = lethal in >= 2/3 joint draws, confirmed by re-assay with suffix "/S3R". Pairs stored as [i, j, l, c, null].
Hits are taken from hits_w*.json in (worker, k) order; genome m is handled by worker m % NWORKERS.
"""
import glob
import json
import pathlib
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))
import s3_common as S  # noqa: E402
import s3_pipeline as P  # noqa: E402

CELL = "7ae3"
NP = 100
W, NW = int(sys.argv[1]), int(sys.argv[2])
hits = []
for f in sorted(glob.glob(str(HERE / "hits_w*.json"))):
    d = json.load(open(f))
    hits += [(d["worker"], h["k"], h["hex"]) for h in d["hits"]]
hits.sort()
t0 = time.process_time()
out = {"rows": [], "cpu_s": 0}
OUT = HERE / ("pairs_hits_w%d.json" % W)
for m, (w, k, hx) in enumerate(hits):
    if m % NW != W:
        continue
    g = bytes.fromhex(hx)
    assert S.competent(CELL, g, True)
    prof = P.singles(CELL, g, True, False, range(64))
    p = {q: 1 - sum(v) / 3 for q, v in prof.items()}
    disp = sorted(q for q, v in prof.items() if sum(v) >= 2)
    res = []
    for i, j in P.sample_pairs(g, disp, NP):
        l, c = P.pair_call(CELL, g, True, False, i, j)
        res.append([i, j, bool(l), c, S.null_lethal(p[i], p[j])])
    out["rows"].append({"name": "rand_w%d_k%d" % (w, k), "hex": hx, "n_disp": len(disp), "p": {str(q): v for q, v in p.items()},
                        "pairs": res})
    out["cpu_s"] = round(time.process_time() - t0, 1)
    OUT.write_text(json.dumps(out))
    n0 = [x for x in res if x[4] == 0]
    print(m, len(disp), len(res), len(n0), sum(1 for x in n0 if x[2] and x[3]), out["cpu_s"], flush=True)
print("done", out["cpu_s"])
