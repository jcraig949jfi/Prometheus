"""W2-6 check C9 (is the 'cell axis' a real target?): BRIDGE's 2x2 (representation x structure) read as a factorial.
Code reading (z80atlas-verify world.py): on PAIR_TAPE + PAIR_EXECUTION the pair epoch shuffles ALL live organisms
regardless of niche; niche only selects a task spec (-> comp), and comp acts only through pressures that are absent in
these cells (QUALITY_DIVERSITY records, never kills). So 'structure' (NICHES_HIGH_MIG) is causally inert for pair
dynamics apart from RNG-stream consumption. Its apparent effect is therefore an empirical noise floor for the
representation effect. Read-only over x_p2_bridge/SUMMARY.json. Output c9_cell_axis_factorial.json
"""
import json, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
S = json.load(open(HERE.parents[1] / "campaigns" / "npe-p2-endogenous-heredity-2026-09-27" / "x_p2_bridge" / "SUMMARY.json"))
t = S["table"]
k = {a: round(v["S5"] * v["n"]) for a, v in t.items()}

def fisher(a, n1, c, n2):
    b, d = n1 - a, n2 - c
    k_, N = a + c, n1 + n2
    lf = lambda x: math.lgamma(x + 1)
    lp = lambda x: lf(n1) - lf(x) - lf(n1 - x) + lf(n2) - lf(k_ - x) - lf(n2 - k_ + x) - (lf(N) - lf(k_) - lf(N - k_))
    p0 = lp(a)
    return round(min(1.0, sum(math.exp(lp(x)) for x in range(max(0, k_ - n2), min(k_, n1) + 1) if lp(x) <= p0 + 1e-9)), 4)

out = {"counts_S5": k}
for st in ("PERSIST", "STATELESS", "BOTH"):
    sts = ("PERSIST", "STATELESS") if st == "BOTH" else (st,)
    g = lambda cells: (sum(k["%s/%s" % (c, s)] for c in cells for s in sts), 32 * len(cells) * len(sts))
    rep = (g(("C7S", "CF")), g(("C7", "C7N")))
    stru = (g(("C7N", "CF")), g(("C7", "C7S")))
    ext = (g(("CF",)), g(("C7",)))
    out[st] = {"representation_slotted_vs_not": [rep[0], rep[1], fisher(rep[0][0], rep[0][1], rep[1][0], rep[1][1])],
               "structure_niches_vs_not (code-inert)": [stru[0], stru[1], fisher(stru[0][0], stru[0][1], stru[1][0], stru[1][1])],
               "CF_vs_C7": [ext[0], ext[1], fisher(ext[0][0], ext[0][1], ext[1][0], ext[1][1])]}
(HERE / "c9_cell_axis_factorial.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
