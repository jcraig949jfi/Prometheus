"""G2 discrepancy shapes reduced to minimal synthetic interactions (operator directive 2026-09-28: "a disagreement should produce a
counterexample, not convergence by inspection"). Each case is a full pre-state. The frozen reference's reading is recorded; the
owner runs the same pre-state through his frozen tracer and returns his reading. Neither side sees the other's code.
Images use the fixture pack's cell conventions (a = side 0 at 0..31 runs first; b = side 1 at 32..63; op mask 0x0C).
    python -m archaeon.attribution.probes.npe_g2_minimal [OUT.json]
"""
import json
import os
import sys

from archaeon.attribution.probes.npe_fixture_validate import load_ref, ARC

R = load_ref()                                            # puts the frozen engine (assembler) on sys.path
sys.path.insert(0, os.path.join(ARC, "npe_fixture_validation"))
import nestor_v2_npe_fixtures as NF                       # noqa: E402  (assembler + cell constants only)

HALT = NF.HALT
CASES = [
    # D1: INC r over a COMPUTED value (fuzz shape: Nestor CF(COMPUTED S), reference COMPUTED S)
    ("D1_inc_over_computed", NF.A_HALT, NF.half(NF.asm("""
        LD HL, 48
        LD A, (HL)
        INC HL
        ADD A, (HL)
        INC A
        LD DE, 8
        LD (DE), A
        HALT
    """), NF.DATA_B), None, None, [8]),
    # D2: XOR A,A idiom stored (fuzz shape: CONST kind name)
    ("D2_xor_idiom_store", NF.A_HALT, NF.half(NF.asm("""
        XOR A, A
        LD DE, 8
        LD (DE), A
        HALT
    """)), None, None, [8]),
    # D3: INC over the idiom (fuzz shape: CF(CONST kind))
    ("D3_inc_over_idiom", NF.A_HALT, NF.half(NF.asm("""
        SUB A, A
        INC A
        LD DE, 8
        LD (DE), A
        HALT
    """)), None, None, [8]),
    # D4: slice-scoped ctrl (secondary): a loads through its PERSISTED HL and hands the byte to b's half; b branches on it and
    # stores. The condition value carries a's transitive addr set {PREG(a.H), PREG(a.L)}.
    ("D4_slice_ctrl_crosshalf", NF.half(NF.asm("""
        LD A, (HL)
        LD DE, 56
        LD (DE), A
        HALT
    """), {k: 0x10 + k for k in range(8, 32)}), NF.half(NF.asm("""
        LD HL, 56
        LD A, (HL)
        OR A, A
        JRZ skip
        LD DE, 40
        LD A, 0x77
        LD (DE), A
    skip:
        HALT
    """)), [0, 0, 0, 0, 0, 20, 0, 0], None, [40 - 32]),
    # D5 (after Nestor #852): the storing slice (b) WRAPS into a's half and executes a branch there. a halts at once, so every
    # branch below is executed by b's slice; slice scope and primary scope must both contain its condition deps.
    ("D5_slice_wraps_into_other_half", bytes([HALT]) + NF.asm("""
        LD A, (HL)
        OR A, A
        JRZ next
    next:
        JP 40
    """) + bytes(range(0x18, 0x18 + 24)), NF.half(NF.asm("""
        JP 1
    """), {8: 0x11, 9: 20, 10: 0, 11: 0x12, 12: HALT, 16: 0x5A}), None, [0, 0, 0, 0, 0, 48, 0, 0], [20]),
    # D6 (S3 diagnosed after Nestor #864): a's slice branches on a byte it loads through its PERSISTED HL; b's slice then executes
    # IN (0xDB) and stores. The IN input-cursor guard is the only condition evaluated in b's slice.
    ("D6_in_guard_in_storing_slice", NF.half(NF.asm("""
        LD A, (HL)
        OR A, A
        JRZ next
    next:
        HALT
    """), {k: 0x10 + k for k in range(8, 32)}), NF.half(NF.asm("""
        IN
        LD DE, 40
        LD A, 0x66
        LD (DE), A
        HALT
    """)), [0, 0, 0, 0, 0, 20, 0, 0], None, [8]),
]


def main(outp):
    res = []
    for name, ga, gb, regs_a, regs_b, loci in CASES:
        vs = 1 if name.startswith(("D4", "D6")) else 0
        r = R.trace_interaction(ga, gb, (regs_a, 0, 0), (regs_b, 0, 0), budget=300, ops_mask=NF.MASK)
        rows = {}
        for j in loci:
            y = r["loci"][vs * R.N + j]
            rows["%s[%d]" % ("ab"[vs], j)] = {"value": y["post"], "written": y["written"], "label": R.fmt_label(y["label"]),
                                             "performer": R.fmt_label(y["performer"]) if y["performer"] else None,
                                             "ctrl": R.fmt_set(y["ctrl_deps"]), "ctrl_slice": R.fmt_set(y["ctrl_deps_slice"]),
                                             "addr": R.fmt_set(y["addr_deps"]), "exec": R.fmt_set(y["exec_deps"])}
        res.append({"case": name, "pre": {"ga": ga.hex(), "gb": gb.hex(), "regs_a": regs_a, "regs_b": regs_b,
                                          "flags_a": [0, 0], "flags_b": [0, 0], "budget": 300, "ops_mask": NF.MASK},
                    "reference_reading": rows})
    json.dump(res, open(outp, "w", newline="\n"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ARC + "/gate_close/G2_MINIMAL_CASES.json")
