"""W2-52 r3 (POST HOC, exploratory, not part of the PREREG decision): side-stratified AC-F and C3+AC-F with equal
side weights (the world's 50/50 placement), bootstrap resampling within side; exact-ruler side table.
python -B r3_posthoc.py -> r3_posthoc.json"""
import json, pickle, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
d = pickle.load(open(HERE / "r1_calls.pkl", "rb")); calls, sides = d["calls"], d["sides"]
def mv(g, a, rn): return [int(c["keep_" + rn]) + int(c["conv_" + rn]) for c in calls[(g, a)]]
def strat(dv, B=10000):
    rng = random.Random("W2-52-strat")
    s0 = [x for x, s in zip(dv, sides) if s == 0]; s1 = [x for x, s in zip(dv, sides) if s == 1]
    est = 0.5 * sum(s0) / len(s0) + 0.5 * sum(s1) / len(s1)
    bs = sorted(0.5 * sum(s0[rng.randrange(len(s0))] for _ in s0) / len(s0) + 0.5 * sum(s1[rng.randrange(len(s1))] for _ in s1) / len(s1) for _ in range(B))
    return {"est": est, "ci95": [bs[250], bs[9749]], "side0_mean": sum(s0) / len(s0), "side1_mean": sum(s1) / len(s1)}
out = {}
for rn in ("class", "FID", "exact"):
    for g in ("AC", "5C", "C3", "C3+AC"):
        for a in ("STOCK", "REVERSED"):
            dv = [p - q for p, q in zip(mv(g, a, rn), mv("F", a, rn))]
            out["%s-F|%s|%s" % (g, a, rn)] = strat(dv)
    for g in ("F", "AC", "5C", "C3", "C3+AC"):
        for a in ("STOCK", "REVERSED"):
            out["m_strat|%s|%s|%s" % (g, a, rn)] = strat(mv(g, a, rn))["est"]
for g in ("F", "AC", "C3", "C3+AC"):
    for a in ("STOCK", "REVERSED"):
        for s in (0, 1):
            cs = [c for c, ss in zip(calls[(g, a)], sides) if ss == s]
            out["exact_side|%s|%s|s%d" % (g, a, s)] = [round(sum(c["keep_exact"] for c in cs) / len(cs), 3), round(sum(c["conv_exact"] for c in cs) / len(cs), 3)]
(HERE / "r3_posthoc.json").write_text(json.dumps(out, indent=1))
for k, v in out.items(): print(k, v if not isinstance(v, dict) else "%+.3f [%+.3f,%+.3f] s0 %+.3f s1 %+.3f" % (v["est"], *v["ci95"], v["side0_mean"], v["side1_mean"]))
