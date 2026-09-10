"""D-16 -- expose `genome_read`: did any load touch a genome address?

WHY THIS IS A DIFFERENTIAL AND NOT INSTRUMENTATION. Recording loads directly would mean editing
`proteus/foundry/vm.py`, which changes `runtime_hash`, which changes the interpretation identity
of every frozen specimen and invalidates Harmonia's existing fossils. The same constraint already
forced `activation_evidence` and the ablation certificate to be differentials. This follows that
established pattern rather than inventing a second one.

THE METHOD. The genome is copied into the tape, so a genome word is simultaneously an
INSTRUCTION and a DATUM. Perturb genome words in a way that provably cannot change any decoded
instruction, then re-run. If behaviour moves, something read those words AS DATA -- which is
exactly a load touching a genome address.

TWO WORD SLOTS CAN BE PERTURBED SAFELY, and the reason is read off the interpreter:

    slot 0 (op)       `op = tape[ip] % N_OPCODES`     -> adding k*N_OPCODES is invariant
    slot 1 (operand a) `a = tape[ip+1] % n_regs`      -> adding k*n_regs is invariant
                       vm.py computes `a` this way for EVERY opcode, unconditionally

    slots 2, 3 (b, c) are consumed RAW and their meaning is opcode-dependent -- LDC's immediate
                      lives in slot b -- so no offset is safe in general. They are NOT perturbed.

THEREFORE THE RESULT IS A LOWER BOUND, and says so in its own payload. `detected: true` is sound:
something read a perturbed word as data. `detected: false` means no read was DETECTED over the
perturbations and probes actually run -- a program that reads only slot-2/slot-3 words, or whose
read never reaches the observable on these cases, returns false. It is evidence of absence only
to the width of the ensemble, which is the same honest bound the alias-differential ablation
certificate carries.
"""
from __future__ import annotations

from proteus.eval.library import EvaluationError, evaluate

SCHEMA = "proteus.genome_read.v1"
COVERED_SLOTS = (0, 1)          # opcode word and operand-a word
UNCOVERED_SLOTS = (2, 3)        # raw, opcode-dependent


def perturb_genome(manifest, k_op=1, k_reg=1):
    """Offset slot 0 by k_op*N_OPCODES and slot 1 by k_reg*n_regs. Instruction-identical."""
    from proteus.foundry.affordances import N_OPCODES
    n_regs = manifest["n_regs"]
    g = []
    for i, w in enumerate(manifest["genome"]):
        slot = i % 4
        if slot == 0:
            v = w + k_op * N_OPCODES
        elif slot == 1:
            v = w + k_reg * n_regs
        else:
            v = w
        if v >= 2 ** 32:
            raise EvaluationError("perturbation would overflow uint32; lower k")
        g.append(v)
    out = dict(manifest)
    out["genome"] = g
    return out


def _signature(result):
    return [(c["outputs_all_ticks"], c["statuses_all_ticks"], c["ops"]) for c in result["cases"]]


def genome_read_report(manifest, spec, seed=0, perturbations=((1, 1), (2, 3))):
    """Did execution depend on genome words read as DATA? Pure; no IO."""
    base = evaluate(manifest, spec, seed=seed, trace_limit=0)
    base_sig = _signature(base)
    differing = []
    for k_op, k_reg in perturbations:
        alt = evaluate(perturb_genome(manifest, k_op, k_reg), spec, seed=seed, trace_limit=0)
        if _signature(alt) != base_sig:
            idx = [i for i, (a, b) in enumerate(zip(base_sig, _signature(alt))) if a != b]
            differing.append({"k_op": k_op, "k_reg": k_reg, "case_indices": idx})
    return {
        "schema_version": SCHEMA,
        "detected": bool(differing),
        "method": "alias differential on instruction-invariant genome word slots",
        "covered_word_slots": list(COVERED_SLOTS),
        "uncovered_word_slots": list(UNCOVERED_SLOTS),
        "perturbations": [{"k_op": a, "k_reg": b} for a, b in perturbations],
        "differing": differing,
        "bound": ("LOWER BOUND. detected=true is sound. detected=false means no genome read was "
                  "DETECTED over the perturbed slots and the probes actually run; reads confined "
                  "to slots 2/3, or reads that never reach the observable, are not excluded."),
    }
