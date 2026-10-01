"""Q3: static pairwise single-interaction payoffs among founder (F), 43->C3, 49->5C, 44->AC and the double
43->C3+44->AC, EXACT-identity scoring (FID>=0.9 cannot separate 1-byte variants).
W(x|y) = E[# halves exactly == x after one interaction] / (# x halves before), side random (both sides averaged),
copy errors off. Write-back: BASE (ring halves kept) and ATOMIC (a half takes its new bytes only if promoted by
p11.predecessor_accepts, else is restored). Contexts: ZERO (fresh, deterministic) and BANK (both contexts drawn
from W2-14 BASE bank, epochs 10-299, NB per side). Also: the double mutant against the N17e realized-partner panel."""
import json, pickle, random, pathlib
from q1_trace import panel, mk, HERE
from tvm import C

NB = 200
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "C3": mk(F, {43: 0xC3}), "5C": mk(F, {49: 0x5C}), "AC": mk(F, {44: 0xAC}),
     "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]


def finals(ga, gb, sa, sb):
    o = C.pair(r, ga, gb, sa, sb, 0.0)
    na, nb = o["na"], o["nb"]
    base = (na, nb)
    fa = na if C.promoted(ga, na, gb, o["wo"][1], n) else ga
    fb = nb if C.promoted(gb, nb, ga, o["wo"][0], n) else gb
    return base, (fa, fb)


def payoff(x, y, ctxs):
    """ctxs: list of (cx, cy). Returns {BASE: W(x|y), ATOMIC: W(x|y)} averaged over both sides and ctxs."""
    tot = {"BASE": 0.0, "ATOMIC": 0.0}
    k = 0
    init = 2 if x == y else 1
    for cx, cy in ctxs:
        for s in (0, 1):
            ga, gb, sa, sb = (x, y, cx, cy) if s == 0 else (y, x, cy, cx)
            b, a = finals(ga, gb, sa, sb)
            tot["BASE"] += sum(h == x for h in b) / init
            tot["ATOMIC"] += sum(h == x for h in a) / init
            k += 1
    return {w: round(v / k, 3) for w, v in tot.items()}


def bank_ctx(rng):
    ep = rng.randrange(10, 300)
    return banks[ep][rng.randrange(len(banks[ep]))][1]


rng = random.Random("W2-24-Q3")
bctx = [(bank_ctx(rng), bank_ctx(rng)) for _ in range(NB)]
names = list(G)
out = {"names": names, "NB": NB}
for cm, ctxs in (("ZERO", [(C.ZERO, C.ZERO)]), ("BANK", bctx)):
    M = {}
    for a in names:
        for b in names:
            M["%s|%s" % (a, b)] = payoff(G[a], G[b], ctxs)
    out[cm] = M
# per-side detail under ZERO (deterministic): who holds which half after each placement
det = {}
for a in names:
    for b in names:
        if a >= b and a != b:
            pass
        for s in (0,):
            b0, a0 = finals(G[a], G[b], C.ZERO, C.ZERO)
            lab = lambda h: next((k for k in names if G[k] == h), "other")
            det["%s@0 vs %s@1" % (a, b)] = {"BASE": [lab(h) for h in b0], "ATOMIC": [lab(h) for h in a0]}
out["ZERO_placements"] = det
# double mutant on the N17e realized-partner panel (FID scoring as in N17e for comparability)
pan = panel()
for nm in ("C3+AC",):
    x = G[nm]
    m = k = c0 = c1 = n0 = n1 = ma = 0
    for y, cy, cx, s in pan:
        o = C.outcome(r, x, y, s, C.ZERO, cy, 0.0, None)
        m += o["m_base"]; k += o["keep"]; ma += o["m_atomic"]
        if s == 0:
            n0 += 1; c0 += o["conv"]
        else:
            n1 += 1; c1 += o["conv"]
    out["bank_panel_" + nm] = {"m_base": m / 1000, "keep": k / 1000, "m_atomic": ma / 1000, "conv_side0": round(c0 / n0, 3), "conv_side1": round(c1 / n1, 3)}
for nm in ("F", "C3", "5C", "AC"):
    x = G[nm]
    ma = 0
    for y, cy, cx, s in pan:
        ma += C.outcome(r, x, y, s, C.ZERO, cy, 0.0, None)["m_atomic"]
    out["bank_panel_m_atomic_" + nm] = ma / 1000
(HERE / "q3_invasion.json").write_text(json.dumps(out, indent=1))
for cm in ("ZERO", "BANK"):
    for w in ("BASE", "ATOMIC"):
        print("\n", cm, w, "  W(row|col)")
        print("%7s" % "" + "".join("%8s" % b for b in names))
        for a in names:
            print("%7s" % a + "".join("%8.3f" % out[cm]["%s|%s" % (a, b)][w] for b in names))
print(json.dumps({k: v for k, v in out.items() if k.startswith("bank_panel") or k == "ZERO_placements"}, indent=1))
