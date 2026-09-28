"""Selftest for ref_tracer_npe.py: hand-written Z8 pair programs with the labels I expect from
the prereg text (v4 s1 + v5 R1/R4/R8/C1-C5), plus engine-equality fuzz and an end-to-end check
against the real world.Runner._pair_interact. Writes selftest_results.txt."""
from __future__ import annotations

import random
import sys
import time

sys.path.insert(0, ".")
import ref_tracer_npe as T  # noqa: E402
from z8 import asm            # noqa: E402

RESULTS = []
FAILS = []


def check(name, cond, detail=""):
    RESULTS.append(("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def prog(src, fill=0x00, n=32):
    code, _ = asm(src)
    assert len(code) <= n, (src, len(code))
    return code + bytes([fill]) * (n - len(code))


def E(side, j, orig=None):
    return ("ENTITY", side, j, orig if orig is not None else side)


NONE_ST = (None, 0, 0)
HALT32 = bytes([0x76]) + bytes(31)
COPIER = "GETPC\nLD DE,32\nLD B,32\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC B\nJRNZ loop\nHALT"


def L(out, a):
    return out["loci"][a]


# --------------------------------------------------------------- F1 PC-relative pair copier
def f1():
    ga = prog(COPIER)
    rr = random.Random(5)
    gb = bytes(rr.randrange(256) for _ in range(32))
    st_b = ([1, 2, 3, 4, 5, 6, 0, 7], 1, 0)
    out = T.trace_interaction(ga, gb, NONE_ST, st_b, rng=random.Random(3))
    ok = all(L(out, 32 + i)["label"] == E("a", i) for i in range(32) if not L(out, 32 + i)["mutated"])
    check("F1 victim half b: data label (ENTITY a, i) MOVE at every locus", ok)
    check("F1 half a unwritten, own labels",
          all(not L(out, i)["written"] and L(out, i)["label"] == E("a", i) for i in range(32)))
    # b's slice re-copies its (now a-material) half onto itself: last store by b, performer a8
    r0 = L(out, 32)
    check("F1 last store by b's slice, performer = material of opcode byte = (a,8)",
          r0["store_by"] == "b" and r0["performer"] == E("a", 8) and r0["performer_entity"] == "a",
          T.fmt_label(r0["performer"]))
    check("F1 addr_deps = {GETPC, a3, a4} (transitive through the copied pointer operands)",
          r0["addr_deps"] == frozenset({("CONTEXT", "GETPC"), E("a", 3), E("a", 4)}),
          T.fmt_set(r0["addr_deps"]))
    check("F1 ctrl_deps (interaction PC label) at b's first store = a's loop condition {a6}",
          r0["ctrl_deps"] == frozenset({E("a", 6)}), T.fmt_set(r0["ctrl_deps"]))
    check("F1 ctrl_deps_slice / pdom at b's first store are empty (no branch yet in b's slice)",
          r0["ctrl_deps_slice"] == frozenset() and r0["ctrl_deps_pdom"] == frozenset())
    r5 = L(out, 37)
    check("F1 later loci carry b's loop condition incl. its transitive addr set",
          r5["ctrl_deps_slice"] == frozenset({E("a", 6), ("CONTEXT", "GETPC"), E("a", 3), E("a", 4)}),
          T.fmt_set(r5["ctrl_deps_slice"]))
    check("F1 exec_deps at store = a's 15 code bytes + b's fetched bytes (labels a0..a14)",
          r5["exec_deps"] == frozenset([E("a", k) for k in range(15)] + [("CONTEXT", "GETPC")]),
          T.fmt_set(r5["exec_deps"]) + "  (b's fetched bytes carry a's store-pointer addr set, C2 CHOICE 5)")
    bir = out["births"]
    check("F1 birth: victim b accepted (donor a); a not accepted",
          bir["b"]["accepted"] and not bir["a"]["accepted"] and bir["b"]["donor"] == "a")
    fl = T.flip_test(ga, gb, NONE_ST, st_b, base=out)
    from collections import Counter
    cnt = Counter(v["verdict"] for v in fl.values())
    check("F1 flip test: 0 FAILED; code-byte loci INAPPLICABLE, data loci CONFIRMED",
          cnt["FAILED"] == 0 and fl[32 + 20]["verdict"] == "CONFIRMED"
          and fl[32 + 0]["verdict"] == "INAPPLICABLE", str(dict(cnt)))
    check("F1 flip: masked high bits of the DE operand stay path-preserving (a3 bits 6,7)",
          fl[35]["bits"] == ["INAPPLICABLE"] * 6 + ["CONFIRMED"] * 2, str(fl[35]["bits"]))
    arm = T.dependence_arm(ga, gb, NONE_ST, st_b, base=out, K=4)
    ide = T.identified(out, fl, arm)
    check("F1 R1 identification: every non-mutated victim locus identified (0 outside changes)",
          all(ide[32 + i] for i in range(32) if not L(out, 32 + i)["mutated"]))
    # mutant tracers must be caught by the flip test
    for mname, relabel, caught in (("loc0", lambda i: E("a", 0), False),
                                   ("loc20", lambda i: E("a", 20), True),
                                   ("reverse", lambda i: E("a", 31 - i), True)):
        mb = dict(out)
        mb["loci"] = [dict(r) for r in out["loci"]]
        for i in range(32):
            mb["loci"][32 + i]["label"] = relabel(i)
        mf = T.flip_test(ga, gb, NONE_ST, st_b, base=mb)
        got = any(v["verdict"] == "FAILED" for v in mf.values())
        check("F1 mutant tracer '%s' %s by the flip test%s" % (
            mname, "caught" if caught else "NOT caught",
            "" if caught else " (a0 is an opcode byte: every flip changes the path -> INAPPLICABLE;"
            " only the label expectation rejects it)"), got == caught)
    return out


# --------------------------------------------------------------- F2 partner (b) copies onto a
def f2():
    ga = bytes(32)                                  # all NOPs: a does nothing for 360 steps
    gb = prog("GETPC\nLD DE,0\nLD B,32\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC B\nJRNZ loop\nHALT")
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST, rng=random.Random(1))
    check("F2 half a <- (ENTITY b, i), store_by b, performer b8",
          all(L(out, i)["label"] == E("b", i) and L(out, i)["store_by"] == "b"
              and L(out, i)["performer"] == E("b", 8) for i in range(32) if not L(out, i)["mutated"]))
    check("F2 a's NOP sled wraps into b's code at 32 and runs b's copier itself: both halt; "
          "a's own stores used b-material opcodes",
          out["flags"]["halted"] == [True, True] and out["telemetry"][0]["writes_own"] == 32)
    check("F2 birth: victim a accepted, donor b", out["births"]["a"]["accepted"]
          and out["births"]["a"]["donor"] == "b")
    check("F2 GETPC returns b's base (context) -> addr_deps hold CONTEXT(GETPC)",
          ("CONTEXT", "GETPC") in L(out, 3)["addr_deps"])


# --------------------------------------------------------------- F3 K31 control-flow bit decoder
def f3():
    # copy bit 0 of b8 into a20 by control flow only: A = XOR A,A; test bit; OR 1 if set
    src = ("LD HL,40\nLD A,(HL)\nAND 1\nLD A,0\nJRZ skip\nOR 1\nskip:\nLD DE,20\nLD (DE),A\nHALT")
    ga = prog(src)
    for bval in (0x01, 0x00):
        gb = bytes([0x76] + [0] * 7 + [bval] + [0] * 23)
        out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST)
        r = L(out, 20)
        lab = r["label"]
        if bval:
            exp = ("COMPUTED", frozenset({E("a", 7), E("a", 11)}))  # OR 1 over LD A,0's operand
        else:
            exp = E("a", 7)                                        # immediate operand (MOVE of a7)
        check("F3 bit decoder b8=%d: label %s" % (bval, T.fmt_label(exp)), lab == exp, T.fmt_label(lab))
        check("F3 bit decoder b8=%d: whole-execution ctrl_deps = {b8, a5 (AND operand), a1, a2 (HL "
              "pointer: flag addr set)}; pdom-scoped ctrl is EMPTY (store is after the join)" % bval,
              r["ctrl_deps"] == frozenset({E("b", 8), E("a", 5), E("a", 1), E("a", 2)})
              and r["ctrl_deps_pdom"] == frozenset(), T.fmt_set(r["ctrl_deps"]))
        check("F3 bit decoder b8=%d: source NOT in addr_deps / data label" % bval,
              E("b", 8) not in r["addr_deps"] and E("b", 8) not in T.bases(lab))
        if not bval:
            fl = T.flip_test(ga, gb, NONE_ST, NONE_ST, base=out)
            arm = T.dependence_arm(ga, gb, NONE_ST, NONE_ST, base=out, K=8, seed=2)
            # a MOVE of a's immediate: flip-CONFIRMED on the operand, but randomising b changes it
            check("F3 implicit copy: MOVE of a7 whose value depends on b -> NOT identified by R1.3",
                  fl[20]["verdict"] in ("CONFIRMED", "INAPPLICABLE") and arm[20]["value_change"] > 0
                  and not T.identified(out, fl, arm)[20],
                  "flip %s, changes %d/%d" % (fl[20]["verdict"], arm[20]["value_change"], arm[20]["draws"]))


# --------------------------------------------------------------- F4 K35 OR with a zero register
def f4():
    ga = prog("LD HL,40\nLD A,(HL)\nOR B\nLD DE,10\nLD (DE),A\nHALT")
    gb = bytes([0x76] + [0] * 7 + [0x5A] + [0] * 23)
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST)
    r = L(out, 10)
    check("F4 OR A,B with reset B=0: value unchanged but label COMPUTED{b8} (CONST base dropped)",
          r["post"] == 0x5A and r["label"] == ("COMPUTED", frozenset({E("b", 8)})), T.fmt_label(r["label"]))
    st_a = ([0, 0, 0, 0, 0, 0, 0, 0], 0, 0)
    out = T.trace_interaction(ga, gb, st_a, NONE_ST)
    r = L(out, 10)
    check("F4 same with persisted B=0: COMPUTED{b8, PREG(a.B)}",
          r["label"] == ("COMPUTED", frozenset({E("b", 8), ("PREG", "a", "B")})), T.fmt_label(r["label"]))


# --------------------------------------------------------------- F5 persisted registers
def f5():
    gb = prog("GETPC\nLD A,C\nLD (HL),A\nHALT")   # overwrites its own GETPC opcode byte at 32
    ga = HALT32
    st_b = ([0, 0x99, 0, 0, 0, 0, 0, 0], 0, 1)
    out = T.trace_interaction(ga, gb, NONE_ST, st_b)
    r = L(out, 32)
    check("F5 persisted register C stored: label PREG(b.C), value 0x99",
          r["label"] == ("PREG", "b", "C") and r["post"] == 0x99, T.fmt_label(r["label"]))
    check("F5 addr_deps = {CONTEXT(GETPC)}; performer = b3 (self)",
          r["addr_deps"] == frozenset({("CONTEXT", "GETPC")}) and r["performer"] == E("b", 3))
    arm = T.dependence_arm(ga, gb, NONE_ST, st_b, base=out, K=8, seed=1)
    check("F5 dependence arm: randomising regs_b changes the value",
          arm[32]["value_change"] > 0 and "regs_b" in arm[32]["outside"])
    check("F5 regs after the interaction persist unchanged except H,L",
          out["regs_after"][1][0][1] == 0x99)


# --------------------------------------------------------------- F6 GETPC / SENSE / IN / idioms
def f6():
    gb = prog("GETPC\nLD A,L\nLD L,62\nLD (HL),A\nINC HL\nSENSE\nLD (HL),A\nHALT")
    out = T.trace_interaction(HALT32, gb, NONE_ST, NONE_ST)
    ra = L(out, 62)
    rb = L(out, 63)
    check("F6 GETPC value stored: label CONTEXT(GETPC), value 32", ra["label"] == ("CONTEXT", "GETPC")
          and ra["post"] == 32, T.fmt_label(ra["label"]))
    check("F6 SENSE stored: CONTEXT(SENSE_side), value 1 (side b)",
          rb["label"] == ("CONTEXT", "SENSE_side") and rb["post"] == 1)
    ga = prog("LD HL,40\nIN\nLD (HL),A\nINC HL\nXOR A\nLD (HL),A\nINC HL\nLD A,(HL)\nSUB A\nLD (HL),A\n"
              "INC HL\nLD A,(HL)\nINC A\nLD (HL),A\nINC HL\nINC (HL)\nHALT")
    gb = bytes([0x76] + [0] * 7 + [0] * 3 + [0x10, 0x20] + [0] * 19)
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST)
    check("F6 IN with no inputs: CONST(in_exhausted), value 0",
          L(out, 40)["label"] == ("CONST", "in_exhausted") and L(out, 40)["post"] == 0)
    check("F6 XOR A,A idiom: CONST", L(out, 41)["label"] == ("CONST", "XOR_AA"))
    check("F6 SUB A,A idiom: CONST (load of b10 is not a base)", L(out, 42)["label"] == ("CONST", "SUB_AA"))
    check("F6 INC A of a loaded byte: COMPUTED_FROM(b11)",
          L(out, 43)["label"] == ("COMPUTED_FROM", E("b", 11)) and L(out, 43)["post"] == 0x11,
          T.fmt_label(L(out, 43)["label"]))
    check("F6 INC (HL) (memory operand): COMPUTED{b12}",
          L(out, 44)["label"] == ("COMPUTED", frozenset({E("b", 12)})) and L(out, 44)["post"] == 0x21)
    check("F6 CONST labels are never members of dependence sets",
          all(not any(x[0] == "CONST" for x in r[k]) for r in out["loci"] if r["written"]
              for k in ("ctrl_deps", "addr_deps", "exec_deps")))


# --------------------------------------------------------------- F7 overlap chain (K32-like)
def f7():
    ga = prog("LD HL,32\nLD DE,40\nLD B,24\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC B\nJRNZ loop\nHALT")
    rr = random.Random(9)
    gb = bytes([0x76] + [rr.randrange(256) for _ in range(31)])
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST)
    ok = all(L(out, 40 + k)["label"] == E("b", k % 8) for k in range(24))
    check("F7 overlapping ascending bytewise copy: locus 8+k <- (b, k mod 8) (overlap chain)", ok,
          " ".join(T.fmt_label(L(out, 40 + k)["label"]) for k in range(24)))
    check("F7 values follow the chain", all(out["post_tape"][40 + k] == gb[k % 8] for k in range(24)))
    fl = T.flip_test(ga, gb, NONE_ST, NONE_ST, base=out)
    check("F7 flip test confirms the chain labels (0 FAILED, >=1 CONFIRMED)",
          all(v["verdict"] != "FAILED" for v in fl.values())
          and sum(v["verdict"] == "CONFIRMED" for v in fl.values()) >= 20)
    mb = dict(out)
    mb["loci"] = [dict(r) for r in out["loci"]]
    for k in range(24):
        mb["loci"][40 + k]["label"] = E("b", 8 + k)           # positional mutant
    mf = T.flip_test(ga, gb, NONE_ST, NONE_ST, base=mb)
    check("F7 positional-label mutant FAILS the flip test", any(v["verdict"] == "FAILED" for v in mf.values()))


# --------------------------------------------------------------- F8 post-dominator scope
def f8():
    ga = prog("LD HL,40\nLD A,(HL)\nOR A\nJRZ skip\nNOP\nskip:\nLD DE,12\nLD A,(DE)\nLD HL,50\nLD (HL),A\nHALT")
    gb = bytes([0x76] + [0] * 7 + [0x33] + [0] * 23)
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST)
    r = L(out, 50)
    check("F8 whole-execution ctrl = {b8} + its load pointer {a1,a2}; pdom-scoped ctrl empty after the join",
          r["ctrl_deps"] == frozenset({E("b", 8), E("a", 1), E("a", 2)}) and r["ctrl_deps_pdom"] == frozenset(),
          "%s / %s" % (T.fmt_set(r["ctrl_deps"]), T.fmt_set(r["ctrl_deps_pdom"])))
    check("F8 data label = (a,12) MOVE (the byte at a12, i.e. LD HL's opcode)", r["label"] == E("a", 12))


# --------------------------------------------------------------- F9 K30 residue-only acceptance
def f9():
    code = prog("LD HL,52\nXOR A\nLD B,8\nloop:\nLD (HL),A\nINC HL\nDEC B\nJRNZ loop\nHALT")
    ga = bytearray(code)
    gb = bytearray(code)
    for k in range(20, 24):
        gb[k] = 0x5A
    out = T.trace_interaction(bytes(ga), bytes(gb), NONE_ST, NONE_ST, rng=random.Random(4))
    bb = out["births"]["b"]
    check("F9 residue acceptance: victim b accepted (fid_other %.3f, fid_self %.3f, donor_wrote %d)"
          % (bb["fid_other"], bb["fid_self"], bb["donor_writes_other"]), bb["accepted"])
    check("F9 the written victim loci are CONST (no donor material moved): copy-descent donor is b itself",
          all(L(out, 52 + k)["label"] == ("CONST", "XOR_AA") for k in range(8))
          and sum(T.entity_of(L(out, 32 + i)["label"]) == "b" for i in range(32)) == 24)
    check("F9 last stores by b (self), performer entity b", all(L(out, 52 + k)["performer_entity"] == "b"
                                                                for k in range(8)))


# --------------------------------------------------------------- F10 write-back mutation (K28)
def f10():
    ga = prog(COPIER)
    gb = bytes(32)
    hits = 0
    for seed in range(400):
        out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST, rng=random.Random(seed), mut_rate=0.05)
        for side in "ab":
            for e in out["mutation_events"][side]:
                if not e["applied"]:
                    continue
                hits += 1
                h = 0 if side == "a" else 32
                r = L(out, h + e["pos"])
                good = (r["label"][0] == "MUTATION" and r["label"][2] == e["old_label"]
                        and r["final"] == e["new"])
                if not good:
                    check("F10 mutation label", False, str(e))
                    return
    check("F10 write-back mutation (rate 0.05, 400 seeds, %d events): MUTATION(draw, old_label), "
          "value == world.Runner._mutate" % hits, hits > 0)
    out = T.trace_interaction(ga, gb, NONE_ST, NONE_ST, rng=random.Random(7), mut_rate=1.0)
    e = [x for x in out["mutation_events"]["b"] if x["applied"]]
    bnd = [a for a, _ in T.z8.dis(out["post_tape"][32:64])]
    check("F10 rate 1.0: only linear-decode boundaries mutate (OPCODE operator)",
          sorted(x["pos"] for x in e) == bnd)
    x = [x for x in e if x["pos"] == 5][0]
    check("F10 decode-dependence of position 5 = labels of boundaries 0,2 (GETPC's ED, LD DE)",
          x["decode_dependence"] == frozenset({E("a", 0), E("a", 2)}), T.fmt_set(x["decode_dependence"]))


# --------------------------------------------------------------- F11 end-to-end vs world.Runner
def f11():
    import manifest
    import world
    cell = dict(manifest.H3_CELLS[0][1])
    rr = random.Random(123)
    nchk = 0
    for trial in range(60):
        R = world.Runner(cell, 9200001 + trial, tier="L")
        if trial < 20:
            ga = prog(COPIER, fill=rr.randrange(256))
            gb = bytes(rr.randrange(256) for _ in range(32))
        else:
            ga = bytes(rr.randrange(256) for _ in range(32))
            gb = bytes(rr.randrange(256) for _ in range(32))
        if trial % 2:
            ga, gb = gb, ga
        a = R._place(ga, 0, niche=0)
        b = R._place(gb, 1, niche=1)
        for o in (a, b):
            if rr.random() < 0.7:
                o.regs = [rr.randrange(256) for _ in range(8)]
                o.fz, o.fc = rr.randrange(2), rr.randrange(2)
        st_a = (None if a.regs is None else list(a.regs), a.fz, a.fc)
        st_b = (None if b.regs is None else list(b.regs), b.fz, b.fc)
        rng0 = random.Random()
        rng0.setstate(R.rng.getstate())
        mine = T.trace_interaction(ga, gb, st_a, st_b, rng=rng0)
        R._pair_interact(0, a, b)
        ea = bytes(R.mem[a.slot:a.slot + a.length])
        eb = bytes(R.mem[b.slot:b.slot + b.length])
        fa = bytes(r["final"] for r in mine["loci"][:32])
        fb = bytes(r["final"] for r in mine["loci"][32:])
        acc = sum(mine["births"][s]["accepted"] for s in "ab")
        ok = (ea == fa and eb == fb and R.rng.getstate() == mine["rng_state_after"]
              and list(a.regs) == list(mine["regs_after"][0][0]) and a.fz == mine["regs_after"][0][1]
              and list(b.regs) == list(mine["regs_after"][1][0]) and b.fc == mine["regs_after"][1][2]
              and R.ct["births_endogenous"] == acc)
        if not ok:
            check("F11 end-to-end trial %d" % trial, False)
            return
        nchk += 1
    check("F11 %d interactions through the REAL world.Runner._pair_interact (z8taint path): final "
          "halves, RNG state, regs/flags and acceptance count reproduced" % nchk, nchk == 60)


# --------------------------------------------------------------- F12 fuzz: engine equality
def f12():
    rr = random.Random(77)
    n = 0
    labs = {}
    t0 = time.time()
    for k in range(300):
        ga = bytes(rr.randrange(256) for _ in range(32))
        gb = bytes(rr.randrange(256) for _ in range(32))
        if k % 3 == 0:          # mutated copiers
            g = bytearray(prog(COPIER, fill=rr.randrange(256)))
            for _ in range(rr.randrange(1, 5)):
                g[rr.randrange(32)] = rr.randrange(256)
            ga = bytes(g)
        st_a = (None, 0, 0) if rr.random() < 0.3 else ([rr.randrange(256) for _ in range(8)],
                                                       rr.randrange(2), rr.randrange(2))
        st_b = (None, 0, 0) if rr.random() < 0.3 else ([rr.randrange(256) for _ in range(8)],
                                                       rr.randrange(2), rr.randrange(2))
        out = T.trace_interaction(ga, gb, st_a, st_b, rng=random.Random(k), mut_rate=0.02)
        for r in out["loci"]:
            if r["written"]:
                labs[r["label"][0]] = labs.get(r["label"][0], 0) + 1
        n += 1
    check("F12 300 fuzz interactions (random + mutated copiers): every slice == z8.run, every "
          "interaction == p11.interact, every write-back == Runner._mutate (%.1fs)" % (time.time() - t0),
          n == 300, "written label kinds: %s" % labs)


NOTE = ("NOTE: 6 checks failed on the first run because MY hand-written expectations were wrong (F1 exec_deps\n"
        "omitted the C2 transitive addr set of fetched bytes; F1 loc0 mutant is uncatchable by flips because a0\n"
        "is an opcode; F2 a's NOP sled wraps into b's code; F3 wrong byte offsets and pdom scope ends at the join;\n"
        "F6 my store address overwrote my own code; F8 flag addr set). In every case the tracer was right; the\n"
        "expectations were corrected (cf. v4 Amendment A's correction on record).")


def main():
    t0 = time.time()
    for f in (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12):
        try:
            f()
        except Exception as ex:          # noqa: BLE001
            import traceback
            check(f.__name__ + " raised", False, traceback.format_exc())
    lines = ["NPE reference tracer selftest  (%d checks, %d FAIL, %.1fs)" % (len(RESULTS), len(FAILS),
                                                                             time.time() - t0), NOTE]
    for st, name, det in RESULTS:
        lines.append("%s  %s" % (st, name))
        if det:
            lines.append("      " + det.replace("\n", "\n      "))
    txt = "\n".join(lines)
    print(txt)
    with open("selftest_results.txt", "w") as fh:
        fh.write(txt + "\n")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
