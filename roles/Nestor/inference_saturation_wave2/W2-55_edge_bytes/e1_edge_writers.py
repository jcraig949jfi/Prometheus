"""W2-55 E1: who writes the edge bytes (half positions 0 and 63) of the target half, after the owner's run?

Panel: W2-24 / N17e realized-partner panel (W2-14 BASE bank, N=1000, donor ctx ZERO, partner ctx = bank cy),
copy errors off.  Each focal genome x in {F, C3, AC, C3+AC} is placed at BOTH placements against all 1000 partners
(forced side), and separately the panel's native side draw is reported (reproduces W2-30 exact keep s0).

Instrumentation: own source-injected copy of the stock z8 VM (same injection points as W2-24 tvm.py) but with ONE
ordered event log: fetch events ('F', who, pc, op, regs) and write events ('W', who, pc_of_instr, addr, old, new,
ldir_info).  For LDIR writes we also record the copy offset i, the raw (unmasked) src/dst at that byte, so a write
into the target edge can be classified as first lap / wrapped lap of the destination and by which half was read.
Bit-equality with common.pair checked on every call."""
import json, pathlib, sys, types, random, collections, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
from q1_trace import panel, mk  # noqa: E402
from tvm import C  # noqa: E402


def build():
    src = pathlib.Path(C.Z8PLAIN.__file__).read_text()
    f_old = "        op = mem[pc]\n"
    assert src.count(f_old) == 1
    src = src.replace(f_old, f_old + "        _CUR[0] = pc\n        _CUR[1] = op\n"
                      "        if _EV is not None: _EV.append(('F', _WHO[0], pc, op, tuple(r)))\n")
    w_old = "        pv = ctx.prov\n"
    assert src.count(w_old) == 1
    src = src.replace(w_old, "        if _EV is not None: _EV.append(('W', _WHO[0], _CUR[0], _CUR[1], a, mem[a], val & 0xFF, _LI[0]))\n" + w_old)
    l_old = "                for _ in range(n):\n                    v = rd(src)\n"
    assert src.count(l_old) == 1
    l_new = ("                _src0, _dst0 = src, dst\n"
             "                for _i in range(n):\n"
             "                    _LI[0] = (_i, n, _src0, _dst0, (src) & 0x7F)\n"
             "                    v = rd(src)\n")
    src = src.replace(l_old, l_new)
    # clear LDIR info after the loop
    e_old = "                steps += n\n                src &= 0xFFFF\n"
    assert src.count(e_old) == 1
    src = src.replace(e_old, "                _LI[0] = None\n" + e_old)
    m = types.ModuleType("z8_traced_w255")
    m.__dict__.update({"_EV": None, "_WHO": [0], "_CUR": [0, 0], "_LI": [None]})
    exec(compile(src, "z8_traced_w255", "exec"), m.__dict__)
    return m


T = build()
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "C3": mk(F, {43: 0xC3}), "AC": mk(F, {44: 0xAC}), "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}
OPN = {0x02: "LD(BC),A", 0x12: "LD(DE),A", 0x77: "LD(HL),A", 0x36: "LD(HL),n", 0x34: "INC(HL)", 0x35: "DEC(HL)"}


def pair_ev(ga, gb, sa, sb):
    tape = bytearray(C.world._pow2(2 * n))
    tape[0:n] = ga
    tape[n:2 * n] = gb
    rng = random.Random(0)
    T._EV = []
    T._LI[0] = None
    after0 = None
    for who, start, st in ((0, 0, sa), (1, n, sb)):
        T._WHO[0] = who
        ctx = T.Ctx(tape, start, n, policy=T.ARENA, rng=rng, copy_mut_rate=0.0, sense=who)
        ctx.regs = None if st[0] is None else list(st[0])
        ctx.fz, ctx.fc = st[1], st[2]
        T.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        if who == 0:
            after0 = bytes(tape)
    ev = T._EV
    T._EV = None
    return bytes(tape[0:n]), bytes(tape[n:2 * n]), ev, after0


def hname(a):
    return "H0" if (a & 127) < n else "H1"


def classify_write(e, owner_who, base):
    _, who, pc, op, a, old, new, li = e
    ctx = "owner" if who == owner_who else "partner"
    code = "owner_code" if hname(pc) == hname(base) else "partner_code"
    if op == 0xED:
        i, nn, s0, d0, srcm = li
        lap = (d0 + i) // 128 - d0 // 128  # how many times dst has wrapped the 128-ring since start (approx)
        lap = ((d0 & 0x7F) + i) // 128
        rdh = "reads_" + ("owner_half" if hname(srcm) == hname(base) else "partner_half")
        tag = "%s LDIR@%d(%s) dst%02x src%02x lap%d %s" % (ctx, pc & 127, code, d0 & 0xFF, s0 & 0xFF, lap, rdh)
        kind = "%s_LDIR_lap%d_%s" % (ctx, lap, rdh)
    else:
        tag = "%s %s@%d(%s)" % (ctx, OPN.get(op, "op%02x" % op), pc & 127, code)
        kind = "%s_%s" % (ctx, OPN.get(op, "op%02x" % op))
    return ctx, tag, kind


def one(x, y, s, sx, sy):
    ga, gb, sa, sb = (x, y, sx, sy) if s == 0 else (y, x, sy, sx)
    na, nb, ev, after0 = pair_ev(ga, gb, sa, sb)
    ref = C.pair(r, ga, gb, sa, sb, 0.0)
    assert (ref["na"], ref["nb"]) == (na, nb)
    base = s * n
    nx = na if s == 0 else nb
    owner_who = s
    out = {"exact": nx == x, "fid": C.FID(x, nx) >= 0.9,
           "diff": [i for i in range(n) if nx[i] != x[i]],
           "inner_exact": nx[1:63] == x[1:63]}
    # every write to the edge bytes, in order
    edge = {0: [], 63: []}
    for e in ev:
        if e[0] == "W" and (e[4] - base) in (0, 63) and hname(e[4]) == hname(base):
            edge[e[4] - base].append(e)
    rec = {}
    for p in (0, 63):
        ws = edge[p]
        changed = nx[p] != x[p]
        last = ws[-1] if ws else None
        # first write that changes the byte away from x[p] (author of the alteration) and the last writer
        altw = [w for w in ws if w[6] != w[5]]
        lc = classify_write(last, owner_who, base) if last else None
        rec[p] = {"changed": changed, "n_writes": len(ws), "n_altering": len(altw),
                  "last": None if lc is None else lc[1], "last_kind": None if lc is None else lc[2],
                  "writers": sorted({classify_write(w, owner_who, base)[1] for w in ws}),
                  "after_owner": (after0[base + p] == x[p]) if s == 0 else None,
                  "final": nx[p]}
    out["edge"] = rec
    # owner-run-end state of the half (placement 0 only: owner = first mover)
    out["half_intact_after_owner"] = (after0[base:base + n] == x) if s == 0 else None
    # partner ctx path: did the partner ever fetch inside the owner half? what pcs did it execute there?
    ptn = 1 - s
    pf = [e for e in ev if e[0] == "F" and e[1] == ptn and hname(e[2]) == hname(base)]
    out["partner_entered"] = bool(pf)
    out["partner_first_entry_pc"] = (pf[0][2] & 127) - base if pf else None
    out["partner_ldirs"] = [(e[2] & 127, e[4][5] | e[4][4] << 8, e[4][3] | e[4][2] << 8, e[4][1] | e[4][0] << 8)
                            for e in ev if e[0] == "F" and e[1] == ptn and e[3] == 0xED]
    return out


if __name__ == "__main__":
    t0 = time.time()
    pan = panel()
    res = {}
    for nm, x in G.items():
        for s in (0, 1):
            recs = []
            for k, (y, cy, cx, snat) in enumerate(pan):
                o = one(x, y, s, C.ZERO, cy)
                o["native"] = (snat == s)
                o["k"] = k
                recs.append(o)
            res["%s/p%d" % (nm, s)] = recs
            N = len(recs)
            nat = [q for q in recs if q["native"]]
            ch0 = collections.Counter(q["edge"][0]["last_kind"] for q in recs if q["edge"][0]["changed"])
            ch63 = collections.Counter(q["edge"][63]["last_kind"] for q in recs if q["edge"][63]["changed"])
            print(nm, s, "exact %.3f (native %.3f n=%d) fid %.3f inner %.3f | b0 chg %d %s | b63 chg %d %s" % (
                sum(q["exact"] for q in recs) / N, sum(q["exact"] for q in nat) / len(nat), len(nat),
                sum(q["fid"] for q in recs) / N, sum(q["inner_exact"] for q in recs) / N,
                sum(q["edge"][0]["changed"] for q in recs), dict(ch0.most_common(4)),
                sum(q["edge"][63]["changed"] for q in recs), dict(ch63.most_common(4))), flush=True)
    import pickle
    pickle.dump(res, open(HERE / "e1_edge_writers.pkl", "wb"))
    print("wall", round(time.time() - t0, 1))
