"""PRE-PRODUCTION tracer agreement set (operator directive s3.2: compare outputs only after both implementations are frozen,
and before production). 300 random pair interactions (NOT production data): random 64-byte tapes biased toward executable
structure, random persisted or fresh registers, budgets up to 300, op mask 0x0C. For each: the full pre-state and MY tracer's
per-locus output for BOTH halves (label, addr, written, store_by, performer, ctrl, ctrl_slice, exec). Archaeon runs the
reference tracer on the same pre-states; per-locus agreement >= 99.5% per class (v4 s4.3).

    python export_fuzz_agreement.py   -> FUZZ_AGREEMENT_nestor.jsonl (seed 20260929)
"""
import json, pathlib, random, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import interventions as I, observe as O, selftest_shadow as T

SEED = 20260929


def main():
    rng = random.Random(SEED)
    out = open(HERE / "FUZZ_AGREEMENT_nestor.jsonl", "w", encoding="utf-8", newline="\n")
    for k in range(300):
        tape, regs, flags, budget, _mask = T.rand_case(rng)
        budget = min(budget, 300)
        p = I.Pre()
        p.n, p.size, p.budget, p.mask, p.vside = 32, 64, budget, 0x0C, 0
        p.g = {0: bytearray(tape[:32]), 1: bytearray(tape[32:])}
        p.regs, p.flags = regs, flags
        r = I.Run(p)
        loci = {}
        for side in (0, 1):
            off = 0 if side == 0 else 32
            rows = []
            for j in range(32):
                cell = r.sh.lab[off + j]
                st = r.last.get(off + j)
                row = {"j": j, "label": O.enc_label(cell[0]), "addr": O.enc_set(cell[1]), "written": st is not None}
                if st is not None:
                    row.update({"store_by": "ab"[st.side], "performer": O.enc_label(st.performer),
                                "ctrl": O.enc_set(st.ctrl), "ctrl_slice": O.enc_set(st.ctrl_slice),
                                "exec": O.enc_set(st.exec_)})
                rows.append(row)
            loci["ab"[side]] = rows
        out.write(json.dumps({"k": k, "pre": {"ga": tape[:32].hex(), "gb": tape[32:].hex(), "regs_a": regs[0],
                                               "regs_b": regs[1], "flags_a": list(flags[0]), "flags_b": list(flags[1]),
                                               "budget": budget, "ops_mask": 0x0C, "tape_len": 64},
                              "loci": loci}, sort_keys=True) + "\n")
    out.close()
    print("ok")


if __name__ == "__main__":
    main()
