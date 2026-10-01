"""Tables for Task 1 dynamic sample."""
from r_common import *
d = json.load(open(OUT / "dyn.json"))["rows"]
def f(x): return f"{x:6.3f}"
print("noise lab static  n   acc   sens_act   X(excess)  bonus  CMmed  distinct8med top3med  n(sa>=.5 & acc<.6)")
for nz in (0, 16, 64):
    for lab in (False, True):
        for st in ("LINC", "THR", "OTHER"):
            xs = [x for x in d if x["noise"] == nz and x["SIG"] == lab and x["static"] == st]
            if not xs: continue
            A = lambda k: np.array([x[k] for x in xs])
            hi = sum((x["sens_act"] >= .5) and (x["acc"] < .6) for x in xs)
            cmv = [x["CM"] for x in xs if x["CM"] < 1e3]
            print(f"{nz:5d} {'SIG' if lab else 'NULL':4s} {st:6s} {len(xs):2d} {f(A('acc').mean())} {f(A('sens_act').mean())} {f(A('X').mean())} {f(A('bonus').mean())} "
                  f"{(np.median(cmv) if cmv else float('nan')):6.2f} {np.median(A('n_distinct8')):6.0f} {np.median(A('top3_8')):6.2f}   {hi}")
print("\nchampions with sens_act >= .3 and acc < .6 (bonus paid at ~chance):")
for x in sorted(d, key=lambda x: -x["X"]):
    if x["sens_act"] >= .3 and x["acc"] < .6:
        print(x["cell"][:8], x["fam"], x["noise"], "SIG" if x["SIG"] else "NULL", x["static"], "acc", round(x["acc"], 3), "sa", round(x["sens_act"], 3), "X", round(x["X"], 3), "CM", round(x["CM"], 2), "distinct", x["n_distinct8"])
print("\nX > .2 by noise:", {nz: (sum(x["X"] > .2 for x in d if x["noise"] == nz), sum(1 for x in d if x["noise"] == nz)) for nz in (0, 16, 64)})
