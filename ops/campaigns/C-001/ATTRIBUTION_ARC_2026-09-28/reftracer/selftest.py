"""Self-tests for ref_tracer_bee.py: hand-written memory images with the labels I expect from ANCESTRY_PREREG_v4 s1/s2/s4.1.

Each test gives the own tape (w), the occupant tape (o, or None = EMPTY) and inputs, and expectations for chosen window loci:
label, written, performer, addr_deps, ctrl_deps, exec_deps, rule_identified (formatted: w5 = (ENTITY w, 5), o3, in0, K:kind,
COMP{...}, CF(...)). The tracer asserts value equality with the frozen VM on every run (including every flip re-run).
Run: python3 selftest.py   (writes selftest_results.txt next to it)"""
from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref_tracer_bee as T  # noqa: E402

vm = T.vm
L = 64
CFG = T.Cfg()
OCC = bytes((0xA0 + 7 * j) & 0xFF for j in range(L))       # a fixed occupant tape (never executed unless jumped into)


def tape(code, fill=lambda j: (0x80 + 3 * j) & 0xFF):
    """code at 0.., data filler elsewhere (filler values are >= 0x80 except where noted: mostly undefined opcodes)."""
    t = bytearray(fill(j) for j in range(L))
    t[:len(code)] = bytes(code)
    return bytes(t)


def ws(*idx):
    return "{" + ",".join(sorted("w%d" % i for i in idx)) + "}"


def S(*names):
    return "{" + ",".join(sorted(set(names))) + "}"


LINES = []
FAILS = []


def out(s=""):
    LINES.append(s); print(s)


def check(name, w, o, inputs, expect, note="", flips=None, cfg=CFG):
    pre = T.make_pre_mem(w, o, inputs, L)
    r = T.trace_interaction(pre, inputs, cfg, occupant=o is not None)
    out("== %s  %s" % (name, note))
    out("   steps=%d halted=%s budget_end=%s n_written=%d birth=%s outputs=%s structural=%s" %
        (r.steps, r.halted, r.budget_end, r.n_written, r.birth, r.outputs[:4], sorted(r.structural_seen)))
    out("   ctrl=%s exec=%s" % (T.fmt_set(r.ctrl_deps), T.fmt_set(r.exec_deps)))
    for loci, exp in expect:
        for j in loci:
            loc = r.loci[j]
            got = {"label": T.fmt_label(loc.label), "written": loc.written, "performer": T.fmt_label(loc.performer),
                   "addr": T.fmt_set(loc.addr_deps), "ctrl": T.fmt_set(loc.ctrl_deps), "exec": T.fmt_set(loc.exec_deps),
                   "ident": loc.rule_identified}
            e = {k: (v(j) if callable(v) else v) for k, v in exp.items()}
            bad = {k: (e[k], got[k]) for k in e if e[k] != got[k]}
            if bad:
                FAILS.append((name, j, bad))
                out("   FAIL locus %d: %s" % (j, bad))
        j0 = loci[0]; loc = r.loci[j0]
        out("   locus %-3d label=%-12s written=%-5s perf=%-4s addr=%-12s ident=%s   (expectation for %d loci: %s)" %
            (j0, T.fmt_label(loc.label), loc.written, T.fmt_label(loc.performer), T.fmt_set(loc.addr_deps),
             loc.rule_identified, len(loci), "OK" if not any(f[0] == name and f[1] in loci for f in FAILS) else "FAIL"))
    if flips:
        for (j, strict, want) in flips:
            f = T.flip_test(pre, inputs, cfg, j, occupant=o is not None, result=r, strict_path=strict)
            ok = f["status"] == want
            if not ok:
                FAILS.append((name, j, ("flip", strict, want, f["status"])))
            out("   flip locus %d strict=%s -> %s bits=%s  expected %s %s" %
                (j, strict, f["status"], "".join(b[0] for b in f["bits"]), want, "OK" if ok else "FAIL"))
    return r


def main():
    random.seed(0)
    # T1 COPYALL replicator ------------------------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.COPYALL, vm.HALT])
    check("T1 COPYALL replicator", w, OCC, [7],
          [(range(L), dict(label=lambda j: "w%d" % j, written=True, performer="w4", addr=ws(1, 3), ctrl="{}",
                           exec=ws(0, 1, 2, 3, 4, 5), ident=True))],
          note="S,T from operands; COPYALL performer",
          flips=[(10, False, "CONFIRMED"), (4, False, "INAPPLICABLE"), (3, False, "INAPPLICABLE"),
                 # locus 1 = the S operand byte: flipping it moves the SOURCE pointer but not the fetch trace or the store
                 # addresses -> the literal v4 s4.1 test FAILS a correctly-labelled locus (SPEC_ISSUES FLIP-1)
                 (1, False, "FAILED"), (1, True, "INAPPLICABLE")])

    # T2 LDIR replicator ---------------------------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.LD_C_n, 64, vm.LDIR, vm.HALT])
    check("T2 LDIR replicator", w, OCC, [7],
          [(range(L), dict(label=lambda j: "w%d" % j, written=True, performer="w6", addr=ws(1, 3), ctrl=ws(5),
                           exec=ws(*range(8)), ident=True))],
          note="C==0 exit -> ctrl {w5}",
          flips=[(20, False, "CONFIRMED"), (5, False, "INAPPLICABLE")])

    # T3 K32: RESET-pointer LDIR self-overlap (first half copied into both halves) ------------------------------------------
    w = tape([vm.LD_T_n, 32, vm.LDIR])
    check("T3 K32 RESET-pointer LDIR overlap", w, OCC, [7],
          [(range(L), dict(label=lambda j: "w%d" % (j % 32), written=True, performer="w2", addr=ws(1), ctrl="{}",
                           exec=ws(0, 1, 2), ident=True))],
          note="S=C=RESET (CONSTANT, structural); runs to budget; loci 32..63 <- w0..31 via the overlap chain",
          flips=[(40, False, "CONFIRMED"), (8, False, "CONFIRMED"), (1, False, "INAPPLICABLE")])

    # T4 register copy loop with DJNZ --------------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 32, vm.LD_T_n, 64, vm.LD_B_n, 8, vm.LD_A_pS, vm.LD_pT_A, vm.INC_S, vm.INC_T, vm.DJNZ_d, 0xFA,
              vm.HALT])
    check("T4 LD A,(S)/LD (T),A loop", w, OCC, [7],
          [(range(8), dict(label=lambda j: "w%d" % (32 + j), written=True, performer="w7", addr=ws(1, 3), ctrl=ws(5),
                           exec=ws(*range(13)), ident=True)),
           # unwritten occupant loci: no performer -> w in exec/ctrl is "an ENTITY other than" o -> NOT rule-identified
           (range(8, L), dict(label=lambda j: "o%d" % j, written=False, performer="-", ident=False))],
          note="moves through A; DJNZ on B (operand w5)",
          flips=[(0, False, "CONFIRMED"), (7, False, "CONFIRMED")])

    # T5 INPUT-conditioned copy (implicit) ---------------------------------------------------------------------------------
    w = tape([vm.IN_A, vm.CP_A_n, 128, vm.JC_n, 10, vm.LD_S_n, 0, vm.LD_T_n, 64, vm.COPYALL, vm.HALT])
    check("T5 copy guarded by input", w, OCC, [200],
          [(range(L), dict(label=lambda j: "w%d" % j, written=True, performer="w9", addr=ws(6, 8),
                           ctrl=S("in0", "w2"), ident=False))],
          note="JC evaluated (not taken) on CP(in0, w2) -> INPUT in ctrl -> not identified")

    # T6 K35: OR with a zero RESET register ------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 32, vm.LD_T_n, 64, vm.LD_A_pS, vm.OR_A_B, vm.LD_pT_A, vm.HALT])
    check("T6 K35 OR A,B with B=RESET 0", w, OCC, [7],
          [([0], dict(label="COMP{w32}", written=True, performer="w6", addr=ws(1, 3), ident=False))],
          note="value unchanged, label COMPUTED")

    # T7 XOR idiom on a copied register ----------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 32, vm.LD_T_n, 64, vm.LD_A_pS, vm.LD_B_A, vm.XOR_A_B, vm.LD_pT_A, vm.HALT])
    check("T7 LD B,A ; XOR A,B idiom", w, OCC, [7],
          [([0], dict(label="K:idiom", written=True, performer="w7", addr=ws(3), ident=False))],
          note="XOR of two registers holding the same MOVE label -> CONSTANT; load pointer S dropped (value independent)")

    # T8 occupant-performed copy ------------------------------------------------------------------------------------------
    w = tape([vm.JP_n, 64, 0x90, 0x90, 0x90, vm.HALT])
    o = bytes([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.COPYALL]) + OCC[5:]
    check("T8 occupant performs COPYALL of w", w, o, [7],
          [(range(L), dict(label=lambda j: "w%d" % j, written=True, performer="o4", addr=S("o1", "o3"), ctrl="{}",
                           exec=S("w0", "w1", "o0", "o1", "o2", "o3", "o4", "w5"), ident=True))],
          note="PC enters the window; after COPYALL the byte at 69 is w5 (HALT)",
          flips=[(30, False, "CONFIRMED")])

    # T9 K34 IN past 16 into the window ------------------------------------------------------------------------------------
    w = tape([vm.LD_T_n, 64, vm.LD_B_n, 20, vm.IN_A, vm.LD_pT_A, vm.INC_T, vm.DJNZ_d, 0xFB, vm.HALT])
    check("T9 K34 IN x20 stored to window", w, OCC, [11, 22],
          [([0], dict(label="in0", written=True, performer="w5", addr=ws(1), ctrl=ws(3), ident=False)),
           ([1], dict(label="in1", addr=ws(1, 3))),
           (range(2, 16), dict(label="K:scratch", addr=ws(1, 3))),
           (range(16, 20), dict(label="K:in_exhausted", addr=ws(1))),
           (range(20, L), dict(label=lambda j: "o%d" % j, written=False))],
          note="IN counter label = PC label at the IN (first IN: {}); input bytes beyond len(inputs) are scratch")

    # T10 K34 OUT past 16, then COPYALL from the output region -----------------------------------------------------------
    w = tape([vm.LD_B_n, 20, vm.INC_A, vm.OUT_A, vm.DJNZ_d, 0xFC, vm.LD_S_n, 0xF0, vm.LD_T_n, 64, vm.COPYALL, vm.HALT])
    check("T10 K34 OUT x20 + COPYALL from 0xF0", w, OCC, [7],
          [([0], dict(label="CF(K:reset)", written=True, performer="w10", addr=ws(7, 9))),       # Amendment C11 (was K:computed)
           (range(1, 16), dict(label="CF(K:reset)", addr=ws(1, 7, 9), ident=False)),
           (range(16, L), dict(label=lambda j: "w%d" % (j - 16), addr=ws(7, 9), ctrl=ws(1), ident=True))],
          note="16 outputs kept; OUT counter label = PC label; INC of a RESET register stays structural")

    # T11 exec_deps: executed byte written from the input ----------------------------------------------------------------
    w = tape([vm.IN_A, vm.LD_T_n, 6, vm.LD_pT_A, vm.NOP, vm.NOP, 0x90, vm.LD_S_n, 0, vm.LD_T_n, 64, vm.COPYALL, vm.HALT])
    check("T11 self-modified code from input", w, OCC, [0],
          [([6], dict(label="in0", addr=ws(2, 8, 10), ident=False)),
           ([0], dict(label="w0", addr=ws(8, 10), ident=False,
                      exec=S("in0", *["w%d" % i for i in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)] + ["w2"])))],
          note="input byte (NOP) executed at 6 -> INPUT in exec_deps (incl. its store pointer w2)")

    # T12 store address from input ----------------------------------------------------------------------------------------
    w = tape([vm.IN_A, vm.LD_T_A, vm.LD_S_n, 0, vm.COPYALL, vm.HALT])
    check("T12 store pointer from input", w, OCC, [64],
          [(range(L), dict(label=lambda j: "w%d" % j, addr=S("in0", "w3"), ident=False))])

    # T13 EMPTY occupant, partial write -----------------------------------------------------------------------------------
    w = tape([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.LD_C_n, 10, vm.LDIR, vm.HALT])
    r = check("T13 EMPTY partner, 10 bytes", w, None, [7],
              [(range(10), dict(label=lambda j: "w%d" % j, written=True, ident=True)),
               (range(10, L), dict(label="K:empty", written=False, performer="-", ident=False))])
    if r.birth:
        FAILS.append(("T13", -1, "birth should be False"))

    # T14 overlap chain vs memmove: window shifted onto itself ------------------------------------------------------------
    w = tape([vm.LD_S_n, 64, vm.LD_T_n, 65, vm.COPYALL, vm.HALT])
    check("T14 COPYALL S=64,T=65 (overlap chain)", w, OCC, [7],
          [([0], dict(label="o0", written=False)),
           (range(1, L), dict(label="o0", written=True, performer="w4", addr=ws(1, 3), ident=True))],
          note="sequential per-byte copy: every locus <- o0 (a memmove would give o(j-1))",
          flips=[(33, False, "CONFIRMED")])

    # T15 JZ on a w data byte (ENTITY-only ctrl), bit-decoder style (K31 flavour) ----------------------------------------
    w = tape([vm.LD_S_n, 40, vm.LD_A_pS, vm.CP_A_n, 0x93, vm.JZ_n, 12, vm.LD_A_n, 0x11, vm.LD_T_n, 64, vm.HALT,
              vm.LD_A_n, 0x22, vm.LD_T_n, 64, vm.LD_pT_A, vm.HALT])
    w = bytearray(w); w[40] = 0x93; w = bytes(w)
    check("T15 value re-created by control flow", w, OCC, [7],
          [([0], dict(label="w13", written=True, performer="w16", addr=ws(15), ctrl=ws(1, 4, 40), ident=True))],
          note="stored byte = operand w13 chosen because w40==0x93: label w13 (operand), source w40 only in ctrl",
          flips=[(0, False, "CONFIRMED")])

    # random value-check fuzz (the tracer asserts equality with the frozen VM) -------------------------------------------
    rng = random.Random(12345)
    ops = sorted(vm.DEFINED)
    n = flips = fails = 0; fail_ex = []
    for t in range(300):
        w = bytes(rng.choice(ops) if rng.random() < 0.8 else rng.randrange(128) for _ in range(L))
        o = bytes(rng.randrange(256) for _ in range(L)) if t % 5 else None
        inp = [rng.randrange(256) for _ in range(rng.choice([1, 2]))]
        pre = T.make_pre_mem(w, o, inp, L)
        r = T.trace_interaction(pre, inp, CFG, occupant=o is not None)
        n += 1
        if r.n_written and t % 4 == 0:
            cand = [lc.locus for lc in r.loci if lc.written and lc.rule_identified and lc.label[0] == "ENTITY"][:6]
            for j in cand:
                f = T.flip_test(pre, inp, CFG, j, occupant=o is not None, result=r)
                flips += 1; fails += f["status"] == "FAILED"
                if f["status"] == "FAILED" and len(fail_ex) < 5:
                    fail_ex.append((t, j, T.fmt_label(r.loci[j].label), T.fmt_set(r.loci[j].addr_deps), f["bits"]))
    out("== FUZZ: %d random interactions value-checked against frozen vm.execute; %d flip-tested loci, %d FAILED" %
        (n, flips, fails))
    for e in fail_ex:
        out("   FAILED example (iter, locus, label, addr_deps, bits): %r" % (e,))

    out()
    out("RESULT: %d expectation failures" % len(FAILS))
    for f in FAILS:
        out("  %r" % (f,))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest_results.txt"), "w") as fh:
        fh.write("\n".join(LINES) + "\n")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
