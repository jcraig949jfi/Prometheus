"""Q4 detail: for each SELF-free competent genome, which executed instruction last set B, C, D, E, H, L before the
donor's first block-copy (side 0 and side 1; SELF disabled; victim = seeded random bytes), plus per-side P-11 pass
counts (10 seeds) so the working side is known. Reads q4_trace_all.json; writes q4_provenance.json. One process."""
import collections
import json
import random
import sys

import corpus_analysis as ca

REGN = ["B", "C", "D", "E", "H", "L"]


def step_trace(world, r, g, side, victim, mask):
    n = r.L
    tl = world._pow2(2 * n)
    z = world.z8
    budget = r.t["slice"]
    tape = bytearray(tl)
    tape[0:n] = (g + bytes(n))[:n] if side == 0 else victim
    tape[n:2 * n] = victim if side == 0 else (g + bytes(n))[:n]
    if side == 1:
        c0 = z.Ctx(tape, 0, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=0)
        z.run(c0, 0, budget, ops_enabled=mask)
    pre = bytes(tape)
    start = side * n
    dense = ca.vm_is_dense(z)
    last = {k: "fresh(0)" for k in REGN}
    prev_regs = [0] * 8
    prev_pc = start
    prev_txt = None
    for b in range(0, budget + 1):
        t2 = bytearray(pre)
        c = z.Ctx(t2, start, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=side)
        pc = z.run(c, start, b, ops_enabled=mask) if b else start
        if b and c.halted:
            return None
        regs = c.regs if b else [0] * 8
        if b:
            for i, k in enumerate(REGN):
                if regs[i] != prev_regs[i]:
                    last[k] = "%s @%+d" % (prev_txt, (prev_pc - start) % tl if (prev_pc - start) % tl < 64 else (prev_pc - start) % tl - tl)
        op, op2 = t2[pc % tl], t2[(pc + 1) % tl]
        if (op == 0xED and op2 in (0xB0, 0xB8)) or (dense and op in (0xE5, 0xE7)):
            kind = "LDIR" if op in (0xE5,) or op2 == 0xB0 and op == 0xED else "LDDR"
            return {"step": b, "pc_rel": (pc - start) % tl, "kind": kind,
                    "HL": (regs[4] << 8) | regs[5], "DE": (regs[2] << 8) | regs[3], "BC": (regs[0] << 8) | regs[1],
                    "last_setter": dict(last)}
        # disassemble the instruction about to execute
        code = bytes(t2[(pc + i) % tl] for i in range(4))
        txt = ca.dis_dense(code, "DENSE" if dense else "PLAIN")[0].split("  ", 1)[1]
        prev_regs, prev_pc, prev_txt = list(regs), pc, txt
    return None


def main():
    q = json.load(open(ca.HERE / "q4_trace_all.json"))
    out = []
    for d in q:
        world, r = ca.env(d["vm"], d["cell"])
        g = bytes.fromhex(d["hex"])
        mask = r._ops_mask() & ~0x02
        vr = random.Random(("CORPUS-Q4", d["hex"]).__repr__())
        victim = bytes(vr.randrange(256) for _ in range(r.L))
        rec = {k: d[k] for k in ("vm", "cell", "hex", "rate_full", "rate_noself", "origin_run", "nocopy_donor")}
        rec["side"] = {s: step_trace(world, r, g, s, victim, mask) for s in (0, 1)}
        _, sides = ca.assay_state(world, r, g, ca.FRESH, ("CORPUS-Q4-side", d["hex"]), 10, mask=mask)
        rec["side_pass_10"] = sides
        out.append(rec)
    (ca.HERE / "q4_provenance.json").write_text(json.dumps(out))
    print(len(out))


if __name__ == "__main__":
    main()
