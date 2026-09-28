"""Prereg v4 fixture pack for BEE r025144's world: VM_COPY (COPYALL enabled), L = 64, SHARED layout (one vm.execute call per
interaction, entry 0, budget 256), frozen VM git 16fc6c2a. The v3 pack (r004041 world) is bee_fixtures_v3.py.

Each fixture: an exact pre-execution memory image plus EXPECTED properties written here by hand from the fixture's semantics.
Validation (python -m archaeon.attribution.bee_fixtures):
  (1) Archaeon's tracer (bee_ref_tracer.py) meets every expectation; every run is value-checked against the frozen VM;
  (2) the path-preserving flip test (v4 s4.1, with Amendment B1's load-sequence condition) FAILS no identified locus;
  (3) completeness: every locus that changes under a W / P / INPUT randomisation names that source;
  (4) mutation testing: every mutant tracer (bee_ref_tracer.MUTANTS) fails >= 1 fixture.
The same images and expectations are what the owner's and the reference tracer must satisfy.
"""
from __future__ import annotations

import sys
from collections import Counter

from archaeon.attribution import bee_ref_tracer as T

L = 64; BUDGET = 256


def V():
    return T.vm16()


def image(code, occ=None, inputs=(7,)):
    v = V()
    w = bytes(code) + bytes([v.HALT]) * (L - len(code)); assert len(w) == L
    o = bytes(occ) if occ is not None else bytes((0x90 + i) & 0xFF for i in range(L))       # 0x90..0xCF: undefined -> NOP
    m = bytearray(256); m[:L] = w; m[L:2 * L] = o
    for k, x in enumerate(inputs): m[v.IN_BASE + k] = x
    return m, list(inputs)


def E(e, i): return ("E", e, i)


def fixtures():
    v = V(); F = {}
    occ = bytes((0x90 + i) & 0xFF for i in range(L))
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 64, v.COPYALL])
    F["K1_copyall_self_copy"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "identified": list(range(L)), "exec_lacks": {0: "P"}})
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 64, v.LD_C_n, 64, v.LDIR])
    F["K1b_ldir_self_copy"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "identified": list(range(L))})
    m, x = image([v.LD_S_n, 64, v.LD_T_n, 0x80, v.LD_C_n, 8, v.LDIR, v.LD_S_n, 0x80, v.LD_T_n, 72, v.LD_C_n, 8, v.LDIR])
    F["K2_scratch_copy"] = (m, x, {"data": {**{i: E("P", i - 8) for i in range(8, 16)}, **{i: E("P", i) for i in range(8)}},
                                   "written": list(range(8, 16)), "unwritten": list(range(8)) + list(range(16, L))})
    # K3/K25: the writer sets S,T and jumps into the occupant, whose byte 0 is COPYALL: the occupant PERFORMS a copy of the writer
    occ3 = bytes([v.COPYALL]) + occ[1:]
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 64, v.JP_n, 64], occ=occ3)
    F["K3_partner_performed_copy"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "performer": {0: {"P"}}, "identified": list(range(L))})
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 68, v.LD_C_n, 60, v.LDIR])
    F["K4_shift4"] = (m, x, {"data": {**{i: E("W", i - 4) for i in range(4, L)}, **{i: E("P", i) for i in range(4)}},
                             "written": list(range(4, L))})
    m, x = image([v.LD_A_n, 0x5A, v.LD_T_n, 64, v.LD_B_n, 32, v.LD_pT_A, v.INC_T, v.DJNZ_d, 0xFC])
    F["K5_self_painter"] = (m, x, {"data": {i: E("W", 1) for i in range(32)}, "identified": list(range(32))})
    m, x = image([v.LD_S_n, 65, v.LD_A_pS, v.LD_B_A, v.LD_S_n, 66, v.LD_A_pS, v.ADD_A_B, v.LD_T_n, 64, v.LD_pT_A])
    F["K6_computed"] = (m, x, {"data": {0: ("COMPUTED", frozenset({E("P", 1), E("P", 2)}))}, "written": [0]})
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 64, v.LD_C_n, 32, v.LDIR])
    F["K7_retention"] = (m, x, {"data": {**{i: E("W", i) for i in range(32)}, **{i: E("P", i) for i in range(32, L)}},
                                "written": list(range(32)), "unwritten": list(range(32, L))})
    m, x = image([v.LD_A_n, occ[0], v.LD_T_n, 64, v.LD_pT_A])
    F["K8_value_coincidence"] = (m, x, {"data": {0: E("W", 1)}, "written": [0]})
    m, x = image([v.LD_S_n, 64, v.LD_T_n, 65, v.LD_C_n, 16, v.LDIR])
    F["K10_overlap_ldir"] = (m, x, {"data": {i: E("P", 0) for i in range(1, 17)}, "written": list(range(1, 17))})
    m, x = image([v.LD_S_n, 64, v.LD_T_n, 65, v.COPYALL])
    F["K10c_overlap_copyall"] = (m, x, {"data": {i: E("P", 0) for i in range(1, L)}, "written": list(range(1, L))})
    occ11 = bytes([5]) + occ[1:]
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.LD_B_A, v.LD_A_n, 0, v.INC_A, v.DJNZ_d, 0xFD, v.LD_T_n, 65, v.LD_pT_A], occ=occ11)
    F["K11_control_flow_copy"] = (m, x, {"value": {1: 5}, "data_kind": {1: "COMPUTED_FROM"}, "ctrl_has": {1: E("P", 0)}, "not_identified": [1]})
    occ12 = bytes([20]) + occ[1:]
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.LD_S_A, v.LD_A_pS, v.LD_T_n, 65, v.LD_pT_A], occ=occ12)
    F["K12_translation_table"] = (m, x, {"data": {1: E("W", 20)}, "addr_has": {1: E("P", 0)}, "not_identified": [1]})
    m, x = image([v.LD_S_n, 15, v.LD_A_pS, v.LD_T_n, 0xE0, v.LD_pT_A, v.IN_A, v.LD_T_n, 64, v.LD_pT_A])
    F["K13_input_laundering"] = (m, x, {"data": {0: E("W", 15)}, "written": [0]})
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.OUT_A, v.LD_S_n, 0xF0, v.LD_A_pS, v.LD_T_n, 65, v.LD_pT_A])
    F["K14_out_readback"] = (m, x, {"data": {1: E("P", 0)}, "written": [1]})
    m, x = image([v.LD_T_n, 64, v.LD_pT_A])
    F["K15_reset_register"] = (m, x, {"data": {0: ("CONST", "reset")}, "not_identified": [0]})
    # K16: the writer copies itself into the window and then executes the COPY in the window (performer = writer by material)
    m, x = image([v.LD_S_n, 0, v.LD_T_n, 64, v.COPYALL, v.JP_n, 64])
    F["K16_self_code_in_window"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "performer": {0: {"W"}}, "identified": list(range(L))})
    m, x = image([v.LD_S_n, 0xF8, v.LD_T_n, 64, v.LD_C_n, 16, v.LDIR])
    F["K17_ldir_wrap"] = (m, x, {"data": {**{i: ("CONST", "zero") for i in range(8)}, **{i: E("W", i - 8) for i in range(8, 16)}}})
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.CP_A_n, 0xFF, v.JZ_n, 12, v.LD_S_n, 0, v.LD_T_n, 64, v.COPYALL])
    F["K22_guard_not_taken"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "ctrl_has": {i: E("P", 0) for i in range(L)},
                                       "not_identified": list(range(L))})
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.ADD_A_n, 0x40, v.LD_T_n, 64, v.LD_pT_A])
    F["K23_operand_cipher"] = (m, x, {"data": {0: ("COMPUTED", frozenset({E("P", 0), E("W", 4)}))}})
    # K24: the input byte (0x16 = COPYALL) is executed as an opcode at 0xF0 after OUT
    m, x = image([v.IN_A, v.OUT_A, v.LD_S_n, 0, v.LD_T_n, 64, v.JP_n, 0xF0], inputs=(v.COPYALL,))
    F["K24_input_as_opcode"] = (m, x, {"data": {i: E("W", i) for i in range(L)}, "exec_has": {0: ("INPUT", 0)}, "not_identified": list(range(L))})
    m, x = image([v.LD_S_n, 0x80, v.LD_T_n, 0, v.LD_C_n, 0, v.LDIR])
    # window[j] <- mem[0xC0 + j]: zero scratch, except j = 32 which reads input byte 0 (0xE0). (Corrected after the first
    # validation run: the hand expectation had missed the input region; the tracer was right.)
    F["K26_ldir_c0_self_overwrite"] = (m, x, {"data": {i: (("INPUT", 0) if i == 32 else ("CONST", "zero")) for i in range(L)},
                                              "not_identified": list(range(L))})
    m, x = image([v.LD_S_n, 64, v.LD_T_n, 0, v.COPYALL])
    F["K27_copyall_over_own_code"] = (m, x, {"data": {i: E("P", i) for i in range(L)}, "unwritten": list(range(L))})
    # K31: bit decoder -- the child byte is chosen by a branch on occupant byte 5's low bit (0x95 is odd -> writes the operand 1)
    m, x = image([v.LD_S_n, 69, v.LD_A_pS, v.LD_B_n, 1, v.AND_A_B, v.JZ_n, 13, v.LD_A_n, 1, v.JP_n, 15, v.HALT,
                  v.LD_A_n, 0, v.LD_T_n, 73, v.LD_pT_A])
    F["K31_bit_decoder"] = (m, x, {"value": {9: 1}, "data": {9: E("W", 9)}, "ctrl_has": {9: E("P", 5)}, "not_identified": [9]})
    # K32: RESET-pointer self-overlap fill (Review 5 CX1): S = 0 and C = 0 from RESET; T = 32 -> window[j] = writer[j mod 32]
    m, x = image([v.LD_T_n, 32, v.LDIR])
    F["K32_reset_pointer_fill"] = (m, x, {"data": {j: E("W", j % 32) for j in range(L)}, "identified": list(range(L))})
    m, x = image([v.IN_A] * 17 + [v.LD_T_n, 64, v.LD_pT_A])
    F["K34_in_exhausted"] = (m, x, {"data": {0: ("CONST", "in_exhausted")}, "not_identified": [0]})
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.OR_A_B, v.LD_T_n, 65, v.LD_pT_A])
    F["K35_or_with_reset_zero"] = (m, x, {"data_kind": {1: "COMPUTED"}, "value": {1: occ[0]}, "not_identified": [1]})
    occ36 = bytes([16]) + occ[1:]
    m, x = image([v.LD_S_n, 64, v.LD_A_pS, v.LD_C_A, v.LD_S_n, 0, v.LD_T_n, 64, v.LDIR], occ=occ36)
    # locus 0 is written before the first C==0 exit test, so only loci 1..15 depend on the occupant-supplied count. (Corrected
    # after the first validation run: the hand expectation had put the dependence on locus 0 too; the tracer was right.)
    F["K36_count_from_occupant"] = (m, x, {"data": {i: E("W", i) for i in range(16)}, "ctrl_has": {i: E("P", 0) for i in range(1, 16)},
                                           "not_identified": list(range(1, 16)), "identified": [0]})
    return F


def check(name, m, x, exp, bug=None):
    fails = []
    _, recs, info = T.trace(m, L, BUDGET, x, bug=bug)
    child = T.vm16(); mm = bytearray(m); child.execute(mm, L, 0, BUDGET, list(x), allow_copyall=True); child = mm[L:2 * L]
    for i, d in exp.get("data", {}).items():
        if recs[i]["data"] != d: fails.append("%s[%d] data %r != %r" % (name, i, recs[i]["data"], d))
    for i, k in exp.get("data_kind", {}).items():
        if recs[i]["data"][0] != k: fails.append("%s[%d] kind %s != %s" % (name, i, recs[i]["data"][0], k))
    for i, val in exp.get("value", {}).items():
        if child[i] != val: fails.append("%s[%d] value %d != %d" % (name, i, child[i], val))
    for key, f in (("ctrl_has", "ctrl"), ("addr_has", "addr"), ("exec_has", "exec")):
        for i, b in exp.get(key, {}).items():
            if b not in recs[i][f]: fails.append("%s[%d] %s lacks %r" % (name, i, f, b))
    for i, ent in exp.get("exec_lacks", {}).items():
        if any(b[0] == "E" and b[1] == ent for b in recs[i]["exec"]): fails.append("%s[%d] exec over-tainted with %s" % (name, i, ent))
    for i, ents in exp.get("performer", {}).items():
        if {b[1] for b in recs[i]["performer"]} != ents: fails.append("%s[%d] performer %r != %r" % (name, i, recs[i]["performer"], ents))
    for i in exp.get("written", []):
        if not recs[i]["written"]: fails.append("%s[%d] not written" % (name, i))
    for i in exp.get("unwritten", []):
        if recs[i]["written"]: fails.append("%s[%d] written" % (name, i))
    for i in exp.get("identified", []):
        if not T.identified(recs[i]): fails.append("%s[%d] not identified" % (name, i))
    for i in exp.get("not_identified", []):
        if T.identified(recs[i]): fails.append("%s[%d] identified" % (name, i))
    return fails, recs, info


def main():
    F = fixtures(); ok = True
    for name, (m, x, exp) in F.items():
        fails, recs, info = check(name, m, x, exp)
        st = Counter(T.flip_test(m, L, BUDGET, x, recs=recs, info=info).values())
        ar = T.arms(m, L, BUDGET, x, recs=recs)
        unnamed = {g: ar[g]["changed"] - ar[g]["named_among_changed"] for g in ("W", "P", "INPUT") if ar[g]["changed"] - ar[g]["named_among_changed"]}
        good = not fails and not st.get("FAILED") and not unnamed
        ok &= good
        print("%-28s %s flip=%s completeness_unnamed=%s Q8c=%.3f %s" % (name, "PASS" if good else "FAIL", dict(st), unnamed or "none",
                                                                    ar["Q8c_mean"] or 0.0, fails[:2]))
    print("\nmutation testing (each mutant must fail >= 1 fixture):")
    for bug in T.MUTANTS:
        caught = [n for n, (m, x, exp) in F.items() if check(n, m, x, exp, bug=bug)[0]]
        print("  %-16s caught by %s" % (bug, caught[:4] if caught else "NONE"))
        ok &= bool(caught)
    print("\nALL PASS" if ok else "\nFAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
