"""W2-51 t1: static mechanism of byte-1 writes into a founder half (stock traced VM, W2-24 tvm.pair_t), on the
W2-14 bank panel (q1_trace.panel(), first 400 partners), founder contexts ZERO and BANK, both sides.
For every pair: the set of founder-half positions changed, which actor/pc changed byte 1, the LDIR record
(actor, pc, src, dst, n) that covers abs address of founder byte 1, and the register file at that LDIR.
Also per-position change frequency of the founder's own half (to rank byte 1 among opcode positions).
python -B t1_mechanism.py -> t1_mechanism.json"""
import json, pathlib, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C, pair_t  # noqa: E402
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
pan = panel()[:400]
OPS = sorted(r._boundaries(F))
out = {"opcode_positions": OPS}
for ctxname in ("ZERO", "BANK"):
    for s in (0, 1):
        pos = collections.Counter()
        b1_only = collections.Counter()
        b1_writer = collections.Counter()
        b1_ld = collections.Counter()
        fp = collections.Counter()
        ex = []
        nb1 = 0
        for y, cy, cx, _s in pan:
            sx = C.ZERO if ctxname == "ZERO" else cx
            ga, gb, sa, sb = (F, y, sx, cy) if s == 0 else (y, F, cy, sx)
            na, nb, ctxs, tr, wl, a0, ld = pair_t(r, ga, gb, sa, sb)
            fin = na if s == 0 else nb
            ch = [j for j in range(n) if fin[j] != F[j]]
            for j in ch:
                pos[j] += 1
            if 1 not in ch:
                continue
            nb1 += 1
            A1 = s * n + 1
            last = [w for w in wl if w[2] == A1 and w[3] != w[4]][-1:]
            who, wpc = (last[0][0], last[0][1]) if last else (None, None)
            actor = "F" if who == s else "P"
            locpc = None if wpc is None else ("Fhalf:%d" % (wpc - s * n) if wpc // n == s else "Phalf:%d" % (wpc - (1 - s) * n))
            b1_writer[(actor, locpc)] += 1
            # which LDIR covers A1 (forward copy)
            cov = None
            for lw, lpc, src, dst, cnt, regs in ld:
                a0_ = dst & 127
                if (A1 - a0_) % 128 < cnt and lpc == wpc:
                    cov = (("F" if lw == s else "P"), "%s" % ("Fhalf:%d" % (lpc - s * n) if lpc // n == s else "Phalf:%d" % (lpc - (1 - s) * n)),
                           src & 127, dst & 127, cnt)
            b1_ld[str(cov[:3] + (cov[3],) if cov else None)] += 1
            k = len(ch)
            fp["[1]" if ch == [1] else ("[0,1]" if ch == [0, 1] else ("n<=4:" + str(ch) if k <= 4 else "n=%d" % (64 if k == 64 else (k // 8) * 8)))] += 1
            if len(ex) < 6 and k <= 4:
                ex.append({"ch": ch, "new": ["%02x" % fin[j] for j in ch], "writer": [actor, locpc], "ldir": cov,
                           "ctx_F": sx[0], "ctx_P": cy[0]})
        out["%s_side%d" % (ctxname, s)] = {"pairs": len(pan), "b1_changed": nb1,
                                           "pos_change": [pos[j] for j in range(n)],
                                           "b1_rank_among_opcodes": sorted(OPS, key=lambda j: -pos[j]).index(1) + 1,
                                           "top_opcode_positions": [(j, pos[j]) for j in sorted(OPS, key=lambda j: -pos[j])[:8]],
                                           "b1_writer": {"%s|%s" % k: v for k, v in b1_writer.most_common(10)},
                                           "b1_ldir": dict(b1_ld.most_common(10)), "b1_footprint": dict(fp.most_common(12)),
                                           "examples": ex}
        o = out["%s_side%d" % (ctxname, s)]
        print(ctxname, s, nb1, o["b1_rank_among_opcodes"], o["top_opcode_positions"][:6], o["b1_writer"], o["b1_footprint"], flush=True)
        print("   ldir", o["b1_ldir"])
(HERE / "t1_mechanism.json").write_text(json.dumps(out, indent=1))
