"""W2-6 check C2 (T3 vs T4(c), revival attack): is the generic synthetic lethality of evolved copiers also present in
UNEVOLVED competent genomes?

S3 found ~3.7% synthetic-lethal pairs among fully dispensable pairs (both singles 0/3, additive null 0) in evolved
state-free AND state-dependent genomes alike, but 0% among the negative control's passenger pairs. A T4 defender can
say: "organization is in all evolved copiers, so SF vs SD is the wrong contrast". This check runs the identical S3
pipeline (s3_pipeline / s3_common, function = COMPETENT, as for the SD comparators) on competent genomes that never
evolved: the 3 random competent hits of minimal_prior.json, plus `1E 40 E5` / `1E C0 E5` / `2E 40 E5` planted at
offsets 8-40 in uniform random 64-byte genomes (random code is executed before the copy, like EXEC_PRE in evolved ones).
T4 (evolved organization) predicts unevolved null-0 synthetic lethality << 3.7%; T3 (generic executed-code
epistasis) predicts about the same.
Read-only; VM calls only, single process. python -B c2_unevolved_epistasis.py -> c2_unevolved_epistasis.json
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
import s3_pipeline as P  # noqa: E402

CELL = "7ae3"
NPAIRS = 100
MAXG = int(sys.argv[1]) if len(sys.argv) > 1 else 15
t0 = time.process_time()
mp = json.load(open(FOR / "minimal_prior.json"))
cands = []
for k in ("P1R", "P2R", "P3R"):
    for h in mp[k]["pass_hex"]:
        cands.append(("random_hit_" + k, bytes.fromhex(h)))
rng = random.Random(20261001)
motifs = [bytes.fromhex(m) for m in ("1E40E5", "1EC0E5", "2E40E5")]
planted = []
tries = 0
while len(planted) < MAXG - len(cands) and tries < 200:
    tries += 1
    m = motifs[tries % 3]
    off = rng.choice((8, 16, 24, 32, 40))
    g = bytearray(rng.randrange(256) for _ in range(64))
    g[off:off + len(m)] = m
    if S.competent(CELL, bytes(g), True):
        planted.append(("planted_%s@%d" % (m.hex().upper(), off), bytes(g)))
cands += planted
print("candidates", len(cands), "plant tries", tries, round(time.process_time() - t0, 1), flush=True)
rows = []
for name, g in cands:
    if not S.competent(CELL, g, True):
        rows.append({"name": name, "competent": False})
        continue
    prof = P.singles(CELL, g, True, False, range(64))
    p = {q: 1 - sum(v) / 3 for q, v in prof.items()}
    disp = sorted(q for q, v in prof.items() if sum(v) >= 2)
    pairs = P.sample_pairs(g, disp, NPAIRS)
    res = []
    for i, j in pairs:
        l, c = P.pair_call(CELL, g, True, False, i, j)
        res.append([i, j, bool(l and c), S.null_lethal(p[i], p[j])])
    null0 = [x for x in res if x[3] == 0]
    rows.append({"name": name, "hex": g.hex(), "competent": True, "n_necessary": 64 - len(disp), "n_disp": len(disp),
                 "n_pairs": len(res), "lethal": sum(x[2] for x in res),
                 "null0_pairs": len(null0), "null0_lethal": sum(x[2] for x in null0), "pairs": res})
    print(name, len(disp), len(res), rows[-1]["lethal"], rows[-1]["null0_pairs"], rows[-1]["null0_lethal"],
          round(time.process_time() - t0, 1), flush=True)
ok = [r for r in rows if r["competent"]]
n0 = sum(r["null0_pairs"] for r in ok)
l0 = sum(r["null0_lethal"] for r in ok)
out = {"cell": CELL, "npairs": NPAIRS, "genomes": len(ok),
       "pooled_null0": {"pairs": n0, "lethal": l0, "rate": round(l0 / n0, 4) if n0 else None},
       "evolved_reference_null0": {"SF": 0.0375, "SD": 0.0371},
       "per_genome_null0_rates": [round(r["null0_lethal"] / r["null0_pairs"], 4) if r["null0_pairs"] else None for r in ok],
       "rows": rows, "cpu_s": round(time.process_time() - t0, 1)}
(HERE / "c2_unevolved_epistasis.json").write_text(json.dumps(out))
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
