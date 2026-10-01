"""s3 step 0: the fast screens in s3_common give the same booleans as fsetup.competent / fsetup.state_free.

    python -B s3_equiv.py  -> s3_equiv.json
Genomes: 12 panel genomes (6 state-free, 6 state-dependent) + 5 single and 5 double random mutants of each (132).
"""
import json, random, time
import fsetup as F
import s3_common as S

d = json.load(open("core_map.json"))
sf = [r for r in d["rows"] if r.get("state_free")]
sd = [r for r in d["rows"] if r.get("competent") and not r.get("state_free")]
rng = random.Random(7)
rows = rng.sample(sf, 6) + rng.sample(sd, 6)
t0 = time.process_time(); tf = ts = 0.0
out = {"n": 0, "comp_mismatch": 0, "sf_mismatch": 0, "comp_true": 0, "sf_true": 0}
for r in rows:
    g = bytes.fromhex(r["hex"]); dense = r["vm"] == "DENSE"
    muts = [g]
    for k in range(10):
        m = bytearray(g)
        for p in rng.sample(range(64), 1 + (k >= 5)):
            m[p] = rng.randrange(256)
        muts.append(bytes(m))
    for m in muts:
        a = time.process_time(); c0 = F.competent(r["cell"], m, dense=dense); s0 = F.state_free(r["cell"], m, dense=dense); b = time.process_time()
        c1 = S.competent(r["cell"], m, dense); s1 = S.state_free(r["cell"], m, dense); c = time.process_time()
        ts += b - a; tf += c - b
        out["n"] += 1; out["comp_mismatch"] += c0 != c1; out["sf_mismatch"] += s0 != s1
        out["comp_true"] += c0; out["sf_true"] += s0
out.update({"cpu_slow_s": round(ts, 1), "cpu_fast_s": round(tf, 1), "cpu_s": round(time.process_time() - t0, 1)})
print(out)
json.dump(out, open("s3_equiv.json", "w"), indent=1)
