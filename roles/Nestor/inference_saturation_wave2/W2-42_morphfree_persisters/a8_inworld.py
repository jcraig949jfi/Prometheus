"""W2-42 a8: in-world realized keep/conversion of causal-lineage members by static keep band (a4/a5 bands), from the
r1 'minter' records (no sims). keep = same oid after the interaction and FID(post, pre) >= 0.9; conv = partner slot
(non-lineage, anc != 0) became a lineage child in that interaction. Only member genomes that were scored in a4
(i.e. that were ever a donor) are included."""
import json, pathlib, collections
from a5_summarize import band
HERE = pathlib.Path(__file__).resolve().parent
S = json.loads((HERE / "a4_panel.json").read_text())["scores"]
out = {}
for name in ("FULL_1438", "FULL_1469", "BANK_1505"):
    X = json.loads((HERE / ("r1_%s.json" % name)).read_text())
    gs = X["gid"]
    st = collections.defaultdict(lambda: [0, 0, 0, 0])
    for ep, s, oid, pre, post, chg, anc, ppre, panc, pinl, ppost, pconv in X["minter"]:
        sc = S.get(gs[pre])
        if sc is None or panc == 0:
            continue
        a, b = bytes.fromhex(gs[pre]), bytes.fromhex(gs[post])
        k = (not chg) and sum(x == y for x, y in zip(a, b)) >= 0.9 * 64
        v = st[(band(sc), s)]
        v[0] += 1; v[1] += k; v[2] += bool(pconv)
    out[name] = {"%s|side%d" % k: {"n": v[0], "keep": round(v[1] / v[0], 3), "conv": round(v[2] / v[0], 3)}
                 for k, v in sorted(st.items())}
pool = collections.defaultdict(lambda: [0, 0, 0])
for name, d in out.items():
    for k, v in d.items():
        pool[k][0] += v["n"]; pool[k][1] += v["keep"] * v["n"]; pool[k][2] += v["conv"] * v["n"]
out["pooled"] = {k: {"n": v[0], "keep": round(v[1] / v[0], 3), "conv": round(v[2] / v[0], 3)} for k, v in sorted(pool.items())}
(HERE / "a8_inworld.json").write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(k, v)
