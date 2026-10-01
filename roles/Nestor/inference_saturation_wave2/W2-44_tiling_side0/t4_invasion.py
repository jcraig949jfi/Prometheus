"""W2-44 t4: W2-24 q3 invasion-table method (re-implemented verbatim; q3_invasion.py is not imported because it
writes its own JSON at import) extended with the in-world tiling converters.
W(x|y) = E[# halves exactly == x after one interaction] / (# x halves before), both sides averaged, copy errors off.
Write-back BASE and ATOMIC (p11 promotion); contexts ZERO and BANK (NB=200 pairs from W2-14 BASE bank, rng 'W2-24-Q3'
-> identical bank contexts to W2-24). Also per-placement winners under ZERO, and the N17e panel m_base/m_atomic.
python -B t4_invasion.py -> t4_invasion.json"""
import json, pickle, random, time
from common44 import *  # noqa
t0 = time.process_time()
n = r.L


def mk(muts):
    g = bytearray(F)
    for p, v in muts.items():
        g[p] = v
    return bytes(g)


t3 = json.loads((HERE / "t3_minimal.json").read_text())
G = {"F": F, "C3": mk({43: 0xC3}), "AC": mk({44: 0xAC}), "C3+AC": mk({43: 0xC3, 44: 0xAC}),
     "CRW1": GEN["CRW_1_first"], "CRW1core": bytes.fromhex(t3["CRW_1_first"]["core_hex"]),
     # byte-0 fixed point of the core (the frame-46 code zeroes byte 0 of every half it writes; t4 note)
     "CRW1fx": (lambda c: bytes([0]) + c[1:])(bytes.fromhex(t3["CRW_1_first"]["core_hex"])),
     # the same design in the founder frame: JPNC at 61 with operand low byte 0x34 = founder LDIR (t5 frame family)
     "JP0": mk({61: 0xD2, 62: 0x34}),
     "CNR22": GEN["CNR_s22_first"], "CRW78": GEN["CRW_78_first"], "XH2N1": GEN["XH2N_s1_first"]}
banks = pickle.load(open(W2 / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]


def finals(ga, gb, sa, sb):
    o = C.pair(r, ga, gb, sa, sb, 0.0)
    na, nb = o["na"], o["nb"]
    fa = na if C.promoted(ga, na, gb, o["wo"][1], n) else ga
    fb = nb if C.promoted(gb, nb, ga, o["wo"][0], n) else gb
    return (na, nb), (fa, fb)


def payoff(x, y, ctxs):
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
bctx = [(bank_ctx(rng), bank_ctx(rng)) for _ in range(200)]
names = list(G)
out = {"names": names, "hex": {k: v.hex() for k, v in G.items()}}
for cm, ctxs in (("ZERO", [(C.ZERO, C.ZERO)]), ("BANK", bctx)):
    out[cm] = {"%s|%s" % (a, b): payoff(G[a], G[b], ctxs) for a in names for b in names}
lab = lambda h: next((k for k in names if G[k] == h), "other")
det = {}
for a in names:
    for b in names:
        b0, a0 = finals(G[a], G[b], C.ZERO, C.ZERO)
        det["%s@0 vs %s@1" % (a, b)] = {"BASE": [lab(h) for h in b0], "ATOMIC": [lab(h) for h in a0]}
out["ZERO_placements"] = det
# BANK placements: fraction of the 200 bank-context draws in which row@0 vs col@1 ends with each half == row / col
bp = {}
for a in names:
    for b in names:
        cnt = {"0": {}, "1": {}}
        for cx, cy in bctx:
            (na, nb), _ = finals(G[a], G[b], cx, cy)
            for hk, h in (("0", na), ("1", nb)):
                L = lab(h); cnt[hk][L] = cnt[hk].get(L, 0) + 1
        bp["%s@0 vs %s@1" % (a, b)] = cnt
out["BANK_placements"] = bp
panel_m = {}
for nm, x in G.items():
    mb = ma = 0
    for y, cy, cx, s in PAN:
        o = C.outcome(r, x, y, s, C.ZERO, cy, 0.0, None)
        mb += o["m_base"]; ma += o["m_atomic"]
    a = A(x)
    panel_m[nm] = {"m_base": mb / 1000, "m_atomic": ma / 1000, **{k: a[k] for k in ("keep_s0", "keep_s1", "conv_s0", "conv_s1", "exact_child")}}
out["panel"] = panel_m
out["_cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "t4_invasion.json").write_text(json.dumps(out, indent=1))
for cm in ("ZERO", "BANK"):
    for w in ("BASE", "ATOMIC"):
        print("\n", cm, w, "  W(row|col)")
        print("%9s" % "" + "".join("%9s" % b for b in names))
        for a in names:
            print("%9s" % a + "".join("%9.3f" % out[cm]["%s|%s" % (a, b)][w] for b in names))
print(json.dumps(panel_m, indent=0))
print("cpu", out["_cpu_s"])
