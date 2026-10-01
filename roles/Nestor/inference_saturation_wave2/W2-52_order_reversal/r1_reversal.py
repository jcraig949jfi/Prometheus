"""W2-52 r1: call-order reversal on the N17e / W2-24 panel (PREREG.md, frozen 03:11:03Z).
Harness-level swap (W2-16 s4 style): pair_o() is common.pair() with an explicit execution order; each context keeps
its start, sense (= placement), carried state, slice, ops mask; cmr = 0. Traced VM = W2-24 tvm.T (log appends only),
checked byte-identical to untraced Z8PLAIN in both orders and to common.pair in stock order.
python -B r1_reversal.py -> r1_reversal.json, r1_calls.pkl"""
import json, pickle, random, sys, pathlib, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel, mk  # noqa: E402
from tvm import C, T  # noqa: E402

t0 = time.process_time()
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "AC": mk(F, {44: 0xAC}), "5C": mk(F, {49: 0x5C}), "C3": mk(F, {43: 0xC3}),
     "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}
CLS = (43, 44, 45, 49)
ORD = {"STOCK": (0, 1), "REVERSED": (1, 0)}


def pair_o(ga, gb, sa, sb, order, vm, trace=False):
    z8 = C.world.z8 = vm
    tape = bytearray(C.world._pow2(2 * n))
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    rng = random.Random(0)
    if trace:
        T._TR, T._WL, T._LD = [], [], []
    ctxs, after_first = [None, None], None
    for k, who in enumerate(order):
        start, st = (0, sa) if who == 0 else (n, sb)
        if trace:
            T._WHO[0] = who
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=rng, copy_mut_rate=0.0, sense=who)
        ctx.regs = None if st[0] is None else list(st[0])
        ctx.fz, ctx.fc = st[1], st[2]
        z8.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        ctxs[who] = (None if ctx.regs is None else list(ctx.regs), ctx.fz, ctx.fc, ctx.writes_other)
        if k == 0:
            after_first = (bytes(tape[0:n]), bytes(tape[n:2 * n]))
    out = {"na": bytes(tape[0:n]), "nb": bytes(tape[n:2 * n]), "ctx": ctxs, "after_first": after_first}
    if trace:
        out["tr"], out["wl"], out["ld"] = T._TR, T._WL, T._LD
        T._TR = T._WL = T._LD = None
    return out


def rulers(x, h):
    f = C.FID(x, h) >= 0.9
    return {"FID": f, "class": f and all(h[i] == x[i] for i in CLS), "exact": h == x}


def one(x, y, cy, s, arm):
    ga, gb, sa, sb = (x, y, C.ZERO, cy) if s == 0 else (y, x, cy, C.ZERO)
    o = pair_o(ga, gb, sa, sb, ORD[arm], T, trace=True)
    u = pair_o(ga, gb, sa, sb, ORD[arm], C.Z8PLAIN)
    chk = {"traced_eq_plain": (o["na"], o["nb"], o["ctx"]) == (u["na"], u["nb"], u["ctx"])}
    if arm == "STOCK":
        ref = C.pair(r, ga, gb, sa, sb, 0.0)
        chk["eq_common_pair"] = (ref["na"], ref["nb"]) == (o["na"], o["nb"]) and \
            all(tuple(ref["ctx"][w]) == tuple(o["ctx"][w][:3]) and ref["wo"][w] == o["ctx"][w][3] for w in (0, 1))
    nx, ny = (o["na"], o["nb"]) if s == 0 else (o["nb"], o["na"])
    rec = {"chk": chk}
    for rn in ("FID", "class", "exact"):
        rec["keep_" + rn] = rulers(x, nx)[rn]
        rec["conv_" + rn] = rulers(x, ny)[rn]
    pt = 1 - s
    base = s * n
    tr, wl, ld = o["tr"], o["wl"], o["ld"]
    ppcs = [t[1] for t in tr if t[0] == pt]
    first = ORD[arm][0]
    # donor half intact when the donor's own context starts (donor runs second => after the partner's slice)
    rec["donor_runs_first"] = (first == s)
    rec["intact_at_donor_start"] = True if first == s else (o["after_first"][s] == x)
    rec["partner_enters_donor_half"] = any(base <= p < base + n for p in ppcs)
    rec["partner_runs_donor_LDIR52"] = any(l[0] == pt and l[1] == base + 52 for l in ld)
    rec["partner_jumps_43_to_108"] = any(ppcs[k] == base + 43 and ppcs[k + 1] == 108 for k in range(len(ppcs) - 1))
    # who wrote the donor half's changed bytes last (by context, by whose code)
    last = {}
    for who, pc, a, old, new in wl:
        last[a & (2 * n - 1)] = (who, pc & (2 * n - 1))
    auth = collections.Counter()
    for i in range(n):
        if nx[i] != x[i]:
            w = last.get(base + i)
            if w is None:
                auth["unwritten"] += 1
                continue
            who, pc = w
            code = "donor_code" if base <= pc < base + n else "partner_code"
            auth[("donor_ctx_" if who == s else "partner_ctx_") + code] += 1
    rec["auth"] = dict(auth)
    return rec


def main():
    pan = panel()
    calls = {}
    for g, x in G.items():
        for arm in ORD:
            calls[(g, arm)] = [one(x, y, cy, s, arm) for y, cy, cx, s in pan]
        print(g, round(time.process_time() - t0, 1), flush=True)
    sides = [s for _, _, _, s in pan]
    pickle.dump({"calls": calls, "sides": sides}, open(HERE / "r1_calls.pkl", "wb"))
    print("cpu_s", round(time.process_time() - t0, 1))


if __name__ == "__main__":
    main()
