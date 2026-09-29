"""L2 diagnostic (not a verdict input): does a P-11-certified donor genome rebuild a randomized partner when its
register file is set BY HAND to the ideal copy state (HL = own start, DE = partner start, BC = n; for LDDR the ends)?

If yes while it fails from every reachable state the harness tried, the genome contributes a bare block-copy opcode
and the addresses/length come from register state that the world carries per BODY, not per genome -- so the
certified event's heredity sat in non-heritable state.

    python3 l2_oracle_regs.py      -> L2_oracle.json
"""
from __future__ import annotations

import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2_npe_p11 as M  # noqa: E402


def regs_for(o, donor_side, mode):
    n = o.n
    d0, v0 = (0, n) if donor_side == 0 else (n, 0)
    if mode == "LDIR":
        hl, de = d0, v0
    else:
        hl, de = d0 + n - 1, v0 + n - 1
    r = [0] * 8                                       # B C D E H L (HL) A
    r[0], r[1] = (n >> 8) & 0xFF, n & 0xFF
    r[2], r[3] = (de >> 8) & 0xFF, de & 0xFF
    r[4], r[5] = (hl >> 8) & 0xFF, hl & 0xFF
    return (r, 0, 0)


def main():
    out = []
    for o in M.load():
        res = {}
        for side in (0, 1):
            for mode in ("LDIR", "LDDR"):
                vs = 1 - side
                st = regs_for(o, side, mode)
                dummy = bytes(o.n)
                ga, gb = (dummy, o.genome) if vs == 0 else (o.genome, dummy)
                st_a, st_b = (M.FRESH, st) if vs == 0 else (st, M.FRESH)
                a = M.p11.assay(M.z8, n=o.n, tape_len=o.tape_len, ga=ga, gb=gb, st_a=st_a, st_b=st_b, budget=o.budget,
                                ops_mask=o.mask, cmr=o.cmr, victim_side=vs, seed=("oracle", o.oid, side, mode))
                res["%s_side%d" % (mode, side)] = a["draws_passed"]
        out.append({"id": o.oid, "copy_primitive": o.cell["copy_primitive"], "oracle_draws_passed": res,
                    "passes_with_oracle_registers": any(v >= 2 for v in res.values())})
    s = {"n": len(out), "passes_with_oracle_registers": sum(r["passes_with_oracle_registers"] for r in out)}
    json.dump({"summary": s, "rows": out}, open(os.path.join(HERE, "L2_oracle.json"), "w"), indent=1)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
