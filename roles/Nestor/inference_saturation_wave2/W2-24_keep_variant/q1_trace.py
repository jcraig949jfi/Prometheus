"""Q1/Q2: trace founder, 43->C3, 49->5C, 44->AC on the N17e realized-partner panel (W2-14 BASE bank, N=1000,
same rng seed and draw order as N17_setter_turnover/bank_assay.py; donor context ZERO). Copy errors off.
For every interaction: keep/conv (FID>=0.9 as in N17e, and exact), per-context path summary, every LDIR with
registers, and authorship of every changed byte in the donor's own half (last writer: which context, at which
pc, executing whose half, which instruction)."""
import json, pickle, random, collections, pathlib
from tvm import C, T, pair_t
HERE = pathlib.Path(__file__).resolve().parent
N = 1000
VARS = [("founder", {}), ("43-c3", {43: 0xC3}), ("49-5c", {49: 0x5C}), ("44-ac", {44: 0xAC})]
OPN = {0xED: "ED", 0x02: "LD(BC),A", 0x12: "LD(DE),A"}


def panel():
    banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
    rng = random.Random("N17e")
    pan = []
    for _ in range(N):
        ep = rng.randrange(10, 300)
        y, cy = banks[ep][rng.randrange(len(banks[ep]))]
        ep2 = rng.randrange(10, 300)
        _, cx = banks[ep2][rng.randrange(len(banks[ep2]))]
        pan.append((y, cy, cx, rng.randrange(2)))
    return pan


def mk(F, muts):
    g = bytearray(F)
    for p, v in muts.items():
        g[p] = v
    return bytes(g)


def half(a, n):
    return "H0" if (a & (2 * n - 1)) < n else "H1"


def analyse(r, x, y, cy, s):
    n = r.L
    ga, gb, sa, sb = (x, y, C.ZERO, cy) if s == 0 else (y, x, cy, C.ZERO)
    na, nb, ctxs, tr, wl, after0, ld = pair_t(r, ga, gb, sa, sb)
    ref = C.pair(r, ga, gb, sa, sb, 0.0)
    assert (ref["na"], ref["nb"]) == (na, nb)
    nx, ny = (na, nb) if s == 0 else (nb, na)
    me, pt = s, 1 - s                  # context ids: donor ctx = its side, partner ctx = other side
    myH = "H%d" % s
    rec = {"keep": C.FID(x, nx) >= 0.9, "conv": C.FID(x, ny) >= 0.9, "keep_exact": nx == x, "conv_exact": ny == x}
    # path summaries
    path = {}
    for who in (0, 1):
        pcs = [t for t in tr if t[0] == who]
        own = "H%d" % who
        first_cross = next((i for i, t in enumerate(pcs) if half(t[1], n) != own), None)
        path[who] = {"steps": len(pcs), "halted": ctxs[who].halted, "first_foreign_step": first_cross,
                     "first_foreign_pc": None if first_cross is None else pcs[first_cross][1],
                     "ldirs": [(pc, src, dst, nn, regs) for w, pc, src, dst, nn, regs in ld if w == who],
                     "pcs": [t[1] for t in pcs],
                     "visited_foreign_pcs": sorted({t[1] for t in pcs if half(t[1], n) != own})}
    rec["path"] = path
    # authorship of changed bytes in donor's own half (last writer per address)
    last = {}
    for who, pc, a, old, new in wl:
        last[a] = (who, pc)
    base = s * n
    auth = collections.Counter()
    sites = collections.Counter()
    for i in range(n):
        if nx[i] != x[i]:
            w = last.get(base + i)
            if w is None:
                auth["unwritten?"] += 1
                continue
            who, pc = w
            ctxname = "donor" if who == me else "partner"
            code = "donor_half" if half(pc, n) == myH else "partner_half"
            ins = OPN.get(tr_op(tr, who, pc), "other")
            auth["%s_ctx_running_%s_code" % (ctxname, code)] += 1
            sites["%s@%d(%s)" % (ctxname, pc, ins)] += 1
    rec["auth"] = dict(auth)
    rec["sites"] = dict(sites)
    rec["after0_donor_half_intact"] = (after0[s] == x)
    return rec


def tr_op(tr, who, pc):
    for t in tr:
        if t[0] == who and t[1] == pc:
            return t[2]
    return None


if __name__ == "__main__":
    import sys
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    pan = panel()
    out = {}
    for name, muts in VARS:
        x = mk(F, muts)
        recs = [analyse(r, x, y, cy, s) for y, cy, cx, s in pan]
        out[name] = recs
        k = sum(q["keep"] for q in recs) / N
        print(name, "keep", k, "m_base", sum(q["keep"] + q["conv"] for q in recs) / N, flush=True)
    pickle.dump(out, open(HERE / "q1_trace.pkl", "wb"))
