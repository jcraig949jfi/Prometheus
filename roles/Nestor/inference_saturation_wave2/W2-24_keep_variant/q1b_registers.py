"""Register state at the copy-setup instructions (donor positions 23 SELF, 48 LD E,A, 49, 52 LDIR) for the donor
context and, when it gets there, the partner context. Mode over the N17e panel. Re-runs the traced VM (seconds)."""
import collections, json, pathlib
from q1_trace import panel, mk, VARS
from tvm import C, pair_t
HERE = pathlib.Path(__file__).resolve().parent
RN = "B C D E H L - A".split()


def fmt(regs):
    return " ".join("%s=%02x" % (RN[i], regs[i]) for i in (7, 1, 0, 2, 3, 4, 5))


r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
pan = panel()
out = {}
for name, muts in VARS:
    x = mk(F, muts)
    for s in (0, 1):
        tab = collections.defaultdict(collections.Counter)
        for y, cy, cx, side in pan:
            if side != s:
                continue
            ga, gb, sa, sb = (x, y, C.ZERO, cy) if s == 0 else (y, x, cy, C.ZERO)
            na, nb, ctxs, tr, wl, after0, ld = pair_t(r, ga, gb, sa, sb)
            nx = na if s == 0 else nb
            lost = C.FID(x, nx) < 0.9
            for who, pc, op, regs, fz, fc in tr:
                if pc - s * 64 in (48, 52) or (pc == 43 + s * 64):
                    role = "donor" if who == s else ("partner_LOSTCASE" if lost else "partner_keptcase")
                    tab["%s@pos%d" % (role, pc - s * 64)][fmt(regs)] += 1
        out["%s_side%d" % (name, s)] = {k: dict(v.most_common(3)) for k, v in sorted(tab.items())}
(HERE / "q1b_registers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
