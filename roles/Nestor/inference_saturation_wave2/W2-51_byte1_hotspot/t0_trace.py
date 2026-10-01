"""W2-51 t0: static trace of the founder (ZERO and bank contexts) on the W2-14 bank panel (first 200 partners of
W2-24 q1_trace.panel()): which instructions write each own/partner byte (absolute addr), with which values.
Focus: writes into byte 1 of either half (abs 1 / 65). python -B t0_trace.py -> t0_trace.json"""
import json, pathlib, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C, pair_t  # noqa: E402
r = C.runner_for_spec(C.run_ds.DONOR); n = r.L
F = C.run_ds.donor_genome()
pan = panel()[:200]
out = {}
for ctxname in ("ZERO", "BANK"):
    for s in (0, 1):
        byaddr = collections.Counter(); b1 = collections.Counter(); b1v = collections.Counter(); fb1 = collections.Counter()
        hit = 0
        for y, cy, *_ in pan:
            sx = C.ZERO if ctxname == "ZERO" else cy
            ga, gb, sa, sb = (F, y, sx, cy) if s == 0 else (y, F, cy, sx)
            na, nb, ctxs, tr, wl, a0, ld = pair_t(r, ga, gb, sa, sb)
            fin = na if s == 0 else nb
            if fin[1] != F[1]:
                fb1["changed"] += 1
                fb1["%02x" % fin[1]] += 1
            any1 = False
            for who, pc, a, old, new in wl:
                if a % n == 1 and old != new:
                    tgt = "own" if (a // n) == s else "partner"
                    actor = "F" if who == s else "P"
                    rel = pc - (n if who == 1 else 0)
                    b1[(actor, tgt, rel)] += 1
                    b1v[(actor, tgt, "%02x" % new)] += 1
                    any1 = True
            hit += any1
        out["%s_side%d" % (ctxname, s)] = {"pairs": len(pan), "pairs_with_b1_change": hit,
                                           "founder_final_b1": dict(fb1),
                                           "b1_writes_actor_target_pc": {"%s|%s|%d" % k: v for k, v in b1.most_common(20)},
                                           "b1_values": {"%s|%s|%s" % k: v for k, v in b1v.most_common(15)}}
        print(ctxname, s, hit, dict(fb1), b1.most_common(8), flush=True)
(HERE / "t0_trace.json").write_text(json.dumps(out, indent=1))
