"""Reduce out/e3.json against PLAN E3-P1..P4 (thresholds frozen in PLAN)."""
import json, pathlib, numpy as np
R = json.loads((pathlib.Path(__file__).parent / "out/e3.json").read_text())
OPS = ["SUM", "SAT2", "ALOHA2", "ARB"]
rng = np.random.default_rng(0x5EF)
def boot(x):
    x = np.asarray(x, float); m = rng.choice(x, (4000, len(x))).mean(1)
    return f"{x.mean():+.3f}[{np.quantile(m,.005):+.3f},{np.quantile(m,.995):+.3f}] n={len(x)}"
res = {}
for arm in ["SUM", "SAT2", "ALOHA2"]:
    rows = [v for v in R.values() if v["arm"] == arm]
    A = np.array([[r["transfer"][o][0] for o in OPS] for r in rows])
    own = A[:, OPS.index(arm)]
    print(f"{arm}: mean acc under", {o: round(float(A[:, i].mean()), 3) for i, o in enumerate(OPS)})
    for i, o in enumerate(OPS):
        if o != arm:
            print(f"   drop own->{o}: {boot(own - A[:, i])}")
    adv = own - np.delete(A, OPS.index(arm), 1).mean(1)
    print(f"   own-operator advantage: {boot(adv)}")
    comp = [r for r in rows if r["transfer"][arm][1] >= .55]
    vv = {}
    for r in comp:
        for n, p in r["probes"].items():
            if n != "normal":
                vv.setdefault(n, []).append(p["verdict"] + ("*" if p.get("identical") else ""))
    print("   competent (own lo99>=.55):", len(comp), {n: dict(zip(*np.unique(v, return_counts=True))) for n, v in vv.items()})
