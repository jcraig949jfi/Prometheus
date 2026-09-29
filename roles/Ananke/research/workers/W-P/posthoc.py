"""Post-hoc descriptors of the N pair-trials (LOGGED as post-hoc, not frozen rules)."""
import json, pickle, sys, itertools
import numpy as np
import common
name = sys.argv[1]
recs = pickle.load(open(common.HERE / f"out/recs_{name}.pkl", "rb"))
SITE = {"S", "inbox", "Kp", "r", "w", "E"}
out = {}


def monotone(fn):
    n = int(np.log2(len(fn)))
    C = list(itertools.product((0, 1), repeat=n))
    v = dict(zip(C, map(int, fn)))
    return all(v[a] <= v[b] for a in C for b in C if all(x <= y for x, y in zip(a, b)))


for o, rr in sorted(recs.items()):
    N = [r for r in rr if r["pat"] == "N" and r.get("full")]
    nN = sum(r["pat"] == "N" for r in rr)
    if not N:
        continue
    md_site_only = np.mean([bool(r["md"]) and all(set(s) <= SITE for s in r["md"]) for r in N])
    mono = np.mean([monotone(r["fn"]) for r in N])
    comp = {c: round(float(np.mean([c in r["R"] for r in N])), 2) for c in N[0]["R"] + tuple(
        sorted({x for r in N for x in r["R"]}))}
    nR = {k: round(float(np.mean([len(r["R"]) == k for r in N])), 2) for k in (2, 3, 4, 5)}
    out[o] = {"N_all": nN, "N_full": len(N), "md_site_only": round(float(md_site_only), 3),
              "monotone": round(float(mono), 3), "comp_in_R": comp, "size_R": nR}
    print(f"o{o:>2} N {nN} full {len(N)} md_site_only {md_site_only:.2f} monotone {mono:.2f} |R| {nR} inR {comp}")
json.dump(out, open(common.HERE / f"out/posthoc_{name}.json", "w"), indent=1)
