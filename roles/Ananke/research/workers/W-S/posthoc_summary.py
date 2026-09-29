"""POST HOC summary (labelled): P8_srcfirst (3-way) and P8any (C iff any first-emission source copy to the
readout is in flight at tau, else S) with 99% pair-bootstrap CIs and shuffled must-fail, per (cell, o, q)."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE))
from collections import Counter
import numpy as np
import analyze as A

f = lambda r: "n0" if not r or r.get("acc") is None else f"{r['acc']:.2f} [{r['ci99'][0]:.2f},{r['ci99'][1]:.2f}] n{r['n']}"
out, lines = {}, []
SUF = sys.argv[1] if len(sys.argv) > 1 else ""
for n in ("2dccdaa5", "c16d5231", "8c37f32e"):
    rows = json.loads((HERE / f"out/posthoc_{n}{SUF}.json").read_text())
    for o in (4, 5):
        for q in (0, 1):
            rr = [r for r in rows if r["o"] == o and r["q"] == q]
            pat = np.array([r["pat"] for r in rr]); pair = np.array([r["pair"] for r in rr])
            p8 = np.array([r["P8_srcfirst"] for r in rr])
            p8any = np.where(p8 == "M", "C", np.where(p8 == "U", "S", p8))
            dec = np.isin(p8, ("S", "C")); sc = np.isin(pat, ("S", "C"))
            res = {"census": dict(Counter(pat.tolist())),
                   "P8_strict": A.accuracy(p8, pat, pair), "P8_decisive": A.accuracy(p8[dec], pat[dec], pair[dec]),
                   "P8_coverage": float(np.mean(dec[sc])),
                   "P8_decisive_shuffled": A.accuracy(A.shuffled(p8[dec], pat[dec], 0), pat[dec], pair[dec]),
                   "P8any": A.accuracy(p8any, pat, pair), "P8any_shuffled": A.accuracy(A.shuffled(p8any, pat, 0), pat, pair),
                   "xtab_incl_N": dict(sorted(Counter(zip(pat.tolist(), p8.tolist())).items()))}
            res["xtab_incl_N"] = {f"{a}>{b}": c for (a, b), c in res["xtab_incl_N"].items()}
            out[f"{n}_o{o}q{q}"] = res
            lines.append(f"{n} o{o} q{q} census {res['census']}\n   P8 strict {f(res['P8_strict'])} | decisive {f(res['P8_decisive'])} cov {res['P8_coverage']:.2f} | dec-shuf {f(res['P8_decisive_shuffled'])}"
                         f"\n   P8any {f(res['P8any'])} | shuf {f(res['P8any_shuffled'])}\n   {res['xtab_incl_N']}")
(HERE / f"out/posthoc_summary{SUF}.json").write_text(json.dumps(out, indent=1))
(HERE / f"out/posthoc_summary{SUF}.txt").write_text("\n".join(lines))
print("\n".join(lines))
