"""W2-10 diagnosis: why does the construct fail to convert some random partners, and how is it ever 'hijacked'?
Same static harness idea as verify.py (one world _pair_interact per call, runner never run), but the birth hook
keeps the P-11 record. Outputs diag_failures.json."""
from __future__ import annotations

import collections
import json
import random
import sys

from common import HERE, CELL, world, run_dd, run_ds, fsetup
import construct

NAME = sys.argv[1] if len(sys.argv) > 1 else "CT_UA"
VM = sys.argv[2] if len(sys.argv) > 2 else "dense"   # "plain" = negative control: E5 is a NOP there
G = construct.genomes()[NAME]
N = 400


def main():
    fsetup.set_vm(VM == "dense")
    a = run_ds.cells()[run_dd.CELLS[CELL]]
    births = []

    class H(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            births.append((parent, bool(causal), fid, {k: p11_rec.get(k) for k in ("pass", "draws_passed", "C2", "C4", "C5")}))

    r = H(dict(a["cell"], atlas_axis="NONE"), 31_600_000, tier=a["tier"])
    d, p = r._place(bytes(64), 0), r._place(bytes(64), 1)
    rng = random.Random("W2-10/diag/" + NAME)
    tab = collections.Counter()
    ex = collections.defaultdict(list)
    for k in range(N):
        pg = bytes(rng.randrange(256) for _ in range(64))
        side = rng.randrange(2)
        for o, g in ((d, G), (p, pg)):
            r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
            r.mem[o.slot:o.slot + 64] = g
            o.length, o.regs, o.fz, o.fc = 64, None, 0, 0
        del births[:]
        r.epoch = k
        d_oid, p_oid = d.oid, p.oid
        x, y = (d, p) if side == 0 else (p, d)
        r._pair_interact(0, x, y)
        conv = [b for b in births if b[0] == d_oid]
        hij = [b for b in births if b[0] == p_oid]
        cls = ("donor_side_%d" % side, ("P11" if conv[0][1] else "LABEL") if conv else "NO_CONV",
               "HIJACKED" if hij else "-")
        key = "|".join(cls)
        tab[key] += 1
        if cls[1] != "P11" or hij:
            if len(ex[key]) < 3:
                ex[key].append({"partner": pg.hex(), "partner_E5_E7_ED_at": [i for i, b in enumerate(pg) if b in (0xE5, 0xE7, 0xED)],
                                "births": [(("donor" if b[0] == d_oid else "partner"), b[1], round(b[2], 3), b[3]) for b in births],
                                "partner_half_after": r._genome(p).hex(), "donor_half_after": r._genome(d).hex()})
    out = {"genome": NAME, "vm": world.z8.__name__, "hex": G.hex().upper(), "n": N, "table": dict(sorted(tab.items())), "examples": ex}
    (HERE / ("diag_failures_%s_%s.json" % (NAME, VM))).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["table"], indent=1))


if __name__ == "__main__":
    main()
