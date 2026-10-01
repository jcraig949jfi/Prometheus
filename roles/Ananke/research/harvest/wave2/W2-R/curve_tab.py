"""Population-level test (zero compute): per-generation max_contrast (max sens_act over the population on that
generation's 8 training worlds) from the recorded C1 evolve curves, by family x noise x SIGNAL/NULL.
Also the top-of-ranking genome's shaping share: best_fit - best_acc."""
from r_common import *
E = [r for r in rows() if r["kind"] == "evolve"]
print("fam   noise lab   n  median(final max_contrast)  frac runs final mc>=.5  frac mc>=.5 & final max_acc<.6  "
      "median(best_fit-best_acc) final  frac top-genome bonus>=.05")
res = {}
for fam in ("RELAY", "XOR", "MAJ", "FLIP", "HOLD"):
    for nz in (0, 16, 64):
        for sig in (False, True):
            xs = [r for r in E if r["env"]["family"] == fam and r["physics"]["noise"] == nz and bool(r["labels"]["SIGNAL"]) == sig]
            if not xs: continue
            fin = [r["result"]["curve"][-1] for r in xs]
            mc = np.array([c["max_contrast"] for c in fin])
            ma = np.array([c["max_acc"] for c in fin])
            sh = np.array([c["best_fit"] - c["best_acc"] for c in fin])
            mc_any = np.array([max(c["max_contrast"] for c in r["result"]["curve"]) for r in xs])
            row = dict(n=len(xs), mc_med=float(np.median(mc)), mc_hi=float((mc >= .5).mean()),
                       mc_hi_chance=float(((mc >= .5) & (ma < .6)).mean()), sh_med=float(np.median(sh)),
                       sh_hi=float((sh >= .05).mean()), mc_any_hi=float((mc_any >= .5).mean()))
            res[f"{fam}|{nz}|{'SIG' if sig else 'NULL'}"] = row
            print(f"{fam:5s} {nz:5d} {'SIG ' if sig else 'NULL'} {len(xs):3d}  {row['mc_med']:6.3f}  {row['mc_hi']:6.2f}  {row['mc_hi_chance']:6.2f}   "
                  f"{row['sh_med']:6.3f}  {row['sh_hi']:6.2f}   (any gen mc>=.5: {row['mc_any_hi']:.2f})")
save("curve_tab.json", res)
