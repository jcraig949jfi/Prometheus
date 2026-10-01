"""Step 3: the world carries registers (world.py _pair_interact: ctx.regs = org.regs; org.regs = ctx.regs after the
slice; only founders / external births start FRESH). So in the world a copier almost never runs from FRESH. What
registers does it actually start from, and does that differ by side?

World order fact: a then b. A side-0 copier X writes child G into b's half BEFORE b runs, so the child's carrier Y
executes G (from offset 64, its own context) in the same interaction, and carries G-conditioned registers into its
next interaction. A side-1 copier Y writes G into a's half AFTER a ran, so the child's carrier X carries the registers
left by whatever X executed (the dead victim's code), and its first own run of G starts from those.

Measured per copier, 30 junk register files J (same seeds as s10), copy test = own side, own context, HALT partner:
  JUNK          start from J (= s10 random arm)
  COND_S1       start from regs after running G at side 1 (base 64, sense 1, pc 64) on [G | G] from J
                (= a side-0 copier's child after its same-interaction run; for a side-1 copier: its own prior run)
  COND_S0       start from regs after running G at side 0 on [G | G] from J
  SELF_FRESH    start from the regs G leaves after its own successful FRESH copy (one value per genome)
  CHAIN3        three successive own-side copy runs, each carrying the previous final regs, starting from J;
                good = all three good"""
import json, pathlib, random, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
sys.path.insert(0, str(HERE))
from _env import A                            # noqa: E402
import p11                                    # noqa: E402
from s1_operand_taint import SEL              # noqa: E402
from s2_fragility_decomposition import randsets   # noqa: E402


def run_from(z, tape, base, sense, pc, st, budget=300):
    ctx = z.Ctx(tape, base, 64, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=sense)
    ctx.regs, ctx.fz, ctx.fc = (None if st[0] is None else list(st[0])), st[1], st[2]
    z.run(ctx, pc, budget, ops_enabled=42)
    return (list(ctx.regs), ctx.fz, ctx.fc)


def copy_test(z, G, side, st):
    tape = bytearray(128); d0 = 64 * side; v0 = 64 - d0
    tape[d0:d0 + 64] = G; tape[v0:v0 + 64] = bytes([0x76]) * 64
    end = run_from(z, tape, d0, side, d0, st)
    return p11.fidelity(G, bytes(tape[v0:v0 + 64])) >= 0.9, end


def cond(z, G, prior_side, st):
    tape = bytearray(128); tape[0:64] = G; tape[64:128] = G
    return run_from(z, tape, 64 * prior_side, prior_side, 64 * prior_side, st)


if __name__ == "__main__":
    out = {"per_genome": {}, "summary": {}}
    for s in (0, 1):
        agg = collections.Counter()
        for r in SEL[s]:
            G = bytes.fromhex(r["hex"]); _, _, z = A.env(r["vm"], r["cell"])
            ok0, end0 = copy_test(z, G, s, (None, 0, 0))
            if not ok0:
                continue
            c = collections.Counter()
            c["SELF_FRESH"] = 30 * copy_test(z, G, s, end0)[0]
            for J in randsets(r["key"]):
                c["JUNK"] += copy_test(z, G, s, J)[0]
                c["COND_S1"] += copy_test(z, G, s, cond(z, G, 1, J))[0]
                c["COND_S0"] += copy_test(z, G, s, cond(z, G, 0, J))[0]
                st, ok = J, True
                for _ in range(3):
                    g, st = copy_test(z, G, s, st)
                    ok = ok and g
                c["CHAIN3"] += ok
            out["per_genome"][r["key"]] = dict(c)
            agg.update(c); agg["genomes"] += 1
        agg = dict(agg); n = agg["genomes"] * 30
        out["summary"]["side%d" % s] = {k: (v if k == "genomes" else [v, n, round(v / n, 3)]) for k, v in agg.items()}
        print(s, out["summary"]["side%d" % s])
    (HERE / "s3_carried_registers.json").write_text(json.dumps(out, indent=1))
