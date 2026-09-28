"""Reduce out/e2_*.json against PLAN E2-P1..P9 (frozen)."""
import json, pathlib, numpy as np
OUT = pathlib.Path(__file__).parent / "out"
OPS = ["SUM", "SAT2", "ALOHA2", "ARB"]
R = [json.loads(f.read_text()) for f in sorted(OUT.glob("e2_*_*_*.json"))]
def sel(arm, task): return [r for r in R if r["arm"] == arm and r["task"] == task]
med = lambda xs: float(np.median(xs)) if len(xs) else float("nan")
summary = {}
for task in ["MAJ", "RELAY"]:
    print(f"== {task}")
    for arm in OPS:
        rs = sel(arm, task)
        if not rs: continue
        acc = [r["held"]["acc"] for r in rs]; lo = [r["held"]["lo99"] for r in rs]
        cd = [r["held"]["comm_delta"] for r in rs]; em = [r["held_tel"]["emit_rate"] for r in rs]
        X = np.array([[r["transfer"][o]["acc"][0] for o in OPS] for r in rs])
        own = X[:, OPS.index(arm)]
        adv = own - np.delete(X, OPS.index(arm), 1).mean(1)
        pv = {}
        for r in rs:
            for n, p in r["probes"].items():
                if n != "normal": pv.setdefault(n, []).append(p["verdict"][0] + ("*" if p["identical"] else ""))
        summary[f"{task}/{arm}"] = dict(acc=acc, lo=lo, cd=cd, emit=em, xfer=X.tolist(), adv=adv.tolist())
        print(f" {arm:6s} acc {np.round(acc,3)} med {med(acc):.3f} | cd {np.round(cd,3)} | emit {np.round(em,3)} med {med(em):.3f}")
        print(f"        xfer mean {dict(zip(OPS, np.round(X.mean(0),3)))} own-adv {adv.mean():+.3f}  probes {{{', '.join(k+':'+''.join(v) for k,v in pv.items())}}}")
(OUT / "e2_summary.json").write_text(json.dumps(summary, indent=1))
S = summary; g = lambda k, f: S[k][f] if k in S else []
print("\n== frozen predictions")
if "RELAY/SUM" in S and "RELAY/ARB" in S:
    d = med(g("RELAY/SUM","acc")) - med(g("RELAY/ARB","acc")); print(f"P1 RELAY |SUM-ARB| median = {abs(d):.3f} -> {'HOLDS' if abs(d)<.05 else 'FAILS'}")
if "MAJ/SUM" in S and "MAJ/ARB" in S:
    d = med(g("MAJ/SUM","acc")) - med(g("MAJ/ARB","acc")); print(f"P2 MAJ SUM-ARB median = {d:+.3f} -> {'HOLDS' if d>=.05 else 'FAILS'}")
    hi = [i for i, a in enumerate(g("MAJ/ARB","acc")) if a > .72]; print(f"P3 ARB MAJ champions > .72: {len(hi)} (vacuous if 0)")
    d = med(g("MAJ/SUM","emit")) - med(g("MAJ/ALOHA2","emit")); print(f"P4 emit SUM - ALOHA2 median = {d:+.4f} -> {'HOLDS' if d>0 else 'FAILS'}")
    d = med(g("MAJ/SAT2","acc")) - med(g("MAJ/SUM","acc")); print(f"P5 MAJ SAT2-SUM median = {d:+.3f} -> {'HOLDS' if d>0 else 'FAILS'}")
    n = sum(np.mean(g(f"MAJ/{a}","adv")) > .03 for a in OPS); print(f"P6 arms with own-adv > .03: {n}/4 -> {'HOLDS' if n>=3 else 'FAILS'}")
    a = np.mean([x[0]-x[3] for x in g("MAJ/SUM","xfer")]); b = np.mean([x[3]-x[0] for x in g("MAJ/ARB","xfer")])
    print(f"P7 SUM-evolved drop under ARB {a:+.3f} vs ARB-evolved drop under SUM {b:+.3f} -> {'HOLDS' if a>b else 'FAILS'}")
    ms, mu = med(g("MAJ/SAT2","emit")), med(g("MAJ/SUM","emit")); print(f"P8 SAT2 emit med {ms:.3f} vs SUM {mu:.3f} -> {'HOLDS' if ms>.2 and ms>5*mu else 'FAILS'}")
    dd = [x[1]-x[0] for x, e in zip(g("MAJ/SAT2","xfer"), g("MAJ/SAT2","emit")) if e >= .2]
    print(f"P9 dense SAT2 champions drop to SUM: {np.round(dd,3)} -> {'NOT_TESTABLE (none dense)' if not dd else ('HOLDS' if np.mean(dd)>=.05 else 'FAILS')}")
