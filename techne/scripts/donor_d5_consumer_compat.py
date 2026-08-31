"""D-5 consumer compatibility: what can the one demonstrated machine consumer actually eat?

    python -m techne.scripts.donor_d5_consumer_compat --out techne/donor_d5_compat_2026-08-31.json

READ-ONLY. This script imports the frozen D-5 substrate to READ its artifact contract. It does
not modify, rerun, or re-analyse the D-5 experiment, and it writes nothing under
`agent_d5_blind/`.

WHY THIS REPORT EXISTS. D-5 is the only component in the programme with a demonstrated appetite
for accumulated experience AND a metered proof that eating changed its behaviour (+10.95pp CFR,
p=0.0007, task-level n=42, at identical budget; shuffled-history retained 100%, random-library
39%). So "can a donor emit into that slot?" is the only Gen-0 question about donor usefulness
that has an existing, frozen, adversarially-controlled answer key.

THE RULE THAT GOVERNS THE ANSWER. Section 14 of the Gen-0 brief: do not widen the consumer to
make a donor appear useful. A compatible donor is one whose NATIVE output type can enter the
slot WITHOUT changing the meaning of the original assay. Writing an encoder from a donor's
output to a genotype is not compatibility -- it is a new bespoke component whose behaviour
would then be the thing under test, and it would silently redefine what the library contains.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
D5 = REPO / "agent_d5_blind"


def read_contract() -> dict:
    """Read the frozen substrate's artifact contract at source."""
    for sub in ("substrate", "mutation"):
        p = str(D5 / sub)
        if p not in sys.path:
            sys.path.insert(0, p)
    from rm_vm import MAX_LEN, NREG, OP_LIST, OPS, PALETTE       # type: ignore
    from physics import SEED_REPERTOIRE                          # type: ignore

    lib_cap = None
    for line in (D5 / "learner" / "m1.py").read_text(encoding="utf-8").splitlines():
        if line.startswith("LIB_CAP"):
            lib_cap = int(line.split("=")[1].strip())
    return {
        "artifact_type": "genotype = tuple of instruction tuples (OPCODE:str, a:int, b:int)",
        "opcodes": list(OP_LIST),
        "argument_typing": dict(OPS),
        "n_registers": NREG,
        "max_program_length": MAX_LEN,
        "constant_palette": list(PALETTE),
        "library_capacity": lib_cap,
        "library_policy": "most-recent-first eviction, genotype-deduped, cap LIB_CAP",
        "admission_policy": "per task: the solving genotype if any, plus up to 4 "
                            "behaviour-distinct best-scoring candidates from the last "
                            "scored generation",
        "seed_repertoire_size": len(SEED_REPERTOIRE),
        "seed_repertoire_sample": [list(map(list, g)) for g in SEED_REPERTOIRE[:3]],
    }


def validate_genotype(g, contract: dict) -> tuple:
    """Exactly the shape the slot accepts. Used to prove the contract is checkable, and to
    demonstrate that a hand-written genotype passes while a donor's native output does not."""
    ops, typing = set(contract["opcodes"]), contract["argument_typing"]
    nreg, maxlen = contract["n_registers"], contract["max_program_length"]
    npal = len(contract["constant_palette"])
    if not isinstance(g, tuple) or not g:
        return False, "genotype must be a non-empty tuple of instructions"
    if len(g) > maxlen:
        return False, "program longer than MAX_LEN=" + str(maxlen)
    for i, ins in enumerate(g):
        if not isinstance(ins, tuple) or len(ins) != 3:
            return False, "instruction " + str(i) + " must be a 3-tuple"
        op, a, b = ins
        if op not in ops:
            return False, "instruction " + str(i) + " has unknown opcode " + repr(op)
        if not isinstance(a, int) or not 0 <= a < nreg:
            return False, "instruction " + str(i) + " register arg out of range"
        kind = typing[op]
        if kind == "const" and not (isinstance(b, int) and 0 <= b < npal):
            return False, "instruction " + str(i) + " constant index out of palette"
        if kind == "reg" and not (isinstance(b, int) and 0 <= b < nreg):
            return False, "instruction " + str(i) + " second register out of range"
        if kind == "jump" and not (isinstance(b, int) and 1 <= b <= 8):
            return False, "instruction " + str(i) + " jump offset out of range"
    return True, "valid genotype"


#: Per-donor assessment. `native_output_type` is what the adapter actually returns at Gen 0;
#: `verdict` is COMPATIBLE only if that type can enter the slot unchanged.
ASSESSMENTS = [
    ("tensorly", "dict of float factor shapes / weights / fit error",
     "NO_COMPATIBLE_CONSUMER",
     "Emits real-valued factor matrices. The slot takes variable-length instruction sequences "
     "over a 14-opcode alphabet with per-opcode argument typing. There is no type-preserving "
     "map; producing one would mean inventing a float-to-program encoding, which is a new "
     "bespoke component and would redefine what the library contains."),
    ("pyribs", "fixed-length real-valued solution vectors in a behavioural archive",
     "NO_COMPATIBLE_CONSUMER",
     "Two independent blockers. (1) Type: archive solutions are fixed-length real vectors; "
     "genotypes are variable-length discrete instruction tuples. (2) Semantics: pyribs needs a "
     "behavioural descriptor to index cells, and the D-5 slot has no notion of one. Choosing a "
     "behaviour space for programs IS the experiment, so supplying one here would embed the "
     "future experiment's answer in the wrapper."),
    ("discopy", "string diagrams and tensor-network evaluations",
     "NO_COMPATIBLE_CONSUMER",
     "Emits typed diagrams, not register-machine programs. A diagram could in principle be "
     "given RM semantics by a functor, but writing that functor is a build, not a wrap, and "
     "it has no Gen-0 consumer."),
    ("cvc5", "sat/unsat verdicts plus integer models",
     "NO_COMPATIBLE_CONSUMER",
     "Emits variable assignments, not programs. cvc5's SyGuS front end could synthesise "
     "program-shaped output, but that is a different capability class AND it would change the "
     "assay's meaning: D-5 measures findability F conditional on existence E and reachability "
     "R, and seeding the library from a complete decision procedure collapses that conditional "
     "structure. This is precisely the widening section 14 forbids."),
    ("egglog", "extracted minimum-cost terms from an e-graph",
     "NO_COMPATIBLE_CONSUMER",
     "Operates on algebraic terms. RM genotypes are imperative instruction sequences with "
     "jumps (JNZ, SKZ, SKG), which are not equational terms. Making egglog rewrite genotypes "
     "requires giving it the RM's semantics as a theory -- the 'Ruler on egglog' build the "
     "Gen-0 brief explicitly defers."),
]


def run() -> dict:
    contract = read_contract()

    # Prove the contract is checkable both ways: a genuine seed artifact validates, and a
    # plausible-looking near-miss does not.
    sys.path.insert(0, str(D5 / "mutation"))
    from physics import SEED_REPERTOIRE                          # type: ignore
    ok_real, msg_real = validate_genotype(SEED_REPERTOIRE[0], contract)
    ok_fake, msg_fake = validate_genotype(((("ADD"), 0, 99),), contract)
    ok_float, msg_float = validate_genotype(((0.5, 0.2, 0.1),), contract)

    return {
        "generated": "2026-08-31",
        "read_only": True,
        "source": "agent_d5_blind/ (frozen; imported read-only, nothing written or rerun)",
        "why_this_consumer": {
            "advantage": "+10.95pp CFR over the frozen empty-library comparator",
            "p_value": 0.0007,
            "unit": "task-level, n = 42",
            "budget": "identical, metered both arms",
            "ablation_shuffled_history_retained": "100%",
            "ablation_random_library_retained": "39%",
            "reading": "the effect is attributable to artifact CONTENT, not to ordering",
        },
        "consumer_contract": contract,
        "contract_is_checkable": {
            "real_seed_artifact_validates": ok_real,
            "real_seed_message": msg_real,
            "bad_constant_index_rejected": not ok_fake,
            "bad_constant_message": msg_fake,
            "float_triple_rejected": not ok_float,
            "float_triple_message": msg_float,
        },
        "donor_assessments": [
            {"donor": d, "native_output_type": t, "verdict": v, "reason": r}
            for d, t, v, r in ASSESSMENTS
        ],
        "OVERALL": "NO_COMPATIBLE_CONSUMER",
        "summary": (
            "None of the five Gen-0 donors emits, natively, an artifact the D-5 library slot "
            "can accept. The slot's type is program-shaped: variable-length sequences over a "
            "fixed 14-opcode instruction set with typed arguments. The Gen-0 donors emit "
            "tensors, real vectors, diagrams, models and algebraic terms. No optional adapter "
            "path was implemented, because every route to one required either a bespoke "
            "encoder or a semantic widening of the assay."),
        "what_would_be_compatible": (
            "A donor whose native output is a program over the same instruction set -- which "
            "is exactly what the library-learning families produce: DreamCoder/Stitch "
            "(Family A) mine abstractions from program corpora, and Ruler/babble/Enumo "
            "(Family B) rewrite and abstract programs modulo a theory. That makes the "
            "Family A vs Family B decision -- which belongs to Lexis, not to this seat -- the "
            "gate on any donor-to-D-5 circulation. It is a scientific choice with an "
            "acquisition-cost asymmetry attached: Family A ships a working win_amd64 Python "
            "wheel (stitch_core 0.1.29); Family B has no Python distribution at all except "
            "egglog, so reaching it means building the rule-inference layer rather than "
            "wrapping it."),
        "NON_CLAIMS": [
            "no claim that the Gen-0 donors are useless -- only that none feeds THIS consumer",
            "no claim about which library-learning family is scientifically preferable",
            "no claim that feeding this slot is the only way a donor could earn rent",
            "the D-5 result is quoted from its committed verdict; it was not recomputed here",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="techne/donor_d5_compat_2026-08-31.json")
    a = ap.parse_args()
    if not D5.exists():
        print("agent_d5_blind/ not found at " + str(D5))
        return 2
    rep = run()
    c = rep["consumer_contract"]
    print("D-5 consumer contract:")
    print("  artifact  :", c["artifact_type"])
    print("  opcodes   :", len(c["opcodes"]), "->", ",".join(c["opcodes"]))
    print("  registers :", c["n_registers"], " max_len:", c["max_program_length"],
          " palette:", c["constant_palette"])
    print("  library   : cap", c["library_capacity"], "-", c["library_policy"])
    print("\ncontract checkable:", rep["contract_is_checkable"]["real_seed_artifact_validates"],
          "/ rejects bad:", rep["contract_is_checkable"]["bad_constant_index_rejected"],
          rep["contract_is_checkable"]["float_triple_rejected"])
    print("\ndonor assessments:")
    for d in rep["donor_assessments"]:
        print("  {:10s} {:24s} {}".format(d["donor"], d["verdict"], d["native_output_type"][:44]))
    print("\nOVERALL:", rep["OVERALL"])
    dest = pathlib.Path(a.out)
    dest.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
