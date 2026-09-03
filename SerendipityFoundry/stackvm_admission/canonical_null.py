"""The native stackvm-v1 canonical admission family.

Built ONLY from corpus-independent sources: the interpreter source, the opcode
table, the legal-program grammar, the operator definitions, resource semantics,
and externally fixed engineering limits. No success frequency, failure
frequency, length distribution, lineage outcome, discovered band, candidate
neighbourhood, or step-limit outcome curve is used anywhere.

THE LOAD-BEARING SPEC PROPERTY: every byte sequence is a legal program
(opcode = byte % 33; operand bytes past the end read as 0; pop of empty stack
= 0; div/mod by zero pushes 0; addresses and register indices wrap). There are
no invalid programs and no exceptions. Therefore the UNIFORM MEASURE OVER BYTE
STRINGS is a well-defined, canonical measure on program space -- which is what
makes a corpus-independent reference law possible at all. On a substrate where
most byte strings were invalid, the only available reference law would have
been "programs that actually occurred", i.e. the corpus, and Rule A would have
made this whole exercise impossible.

WHAT IS DELIBERATELY *NOT* DONE HERE: the canonical samplers are not broadened
to cover the archaeological candidates. R3 keeps the spec-default create_random
support of [16, 96] bytes even though known candidates fall outside it. A
protocol that refuses an interesting claim is preferable to one whose null was
reverse-engineered to admit it.
"""
from __future__ import annotations

import hashlib
import random

from provenance import (Tagged, NullPath, SPEC_DERIVED, PROTOCOL_CONSTANT,
                        EXTERNAL_RANDOMNESS, CORPUS_DERIVED, ProvenanceError)

VM_SRC = "F:/SerendipityD/foundry/engines/gp/stackvm/vm.py"
AD_SRC = "F:/SerendipityD/foundry/engines/gp/stackvm/adapter.py"

# ---- SPEC constants, transcribed from source with citations ----------------
N_OPCODES = 33          # vm.py OPCODES tuple length
STACK_MAX = 1024
MEMORY_SIZE = 256
NUM_REGISTERS = 8
MASK = (1 << 64) - 1
SIGN_BIT = 1 << 63

SPEC_CREATE = {"min_len": 16, "max_len": 96}          # adapter _DEFAULT_CREATE
SPEC_MUTATE = {"p_point": 0.5, "p_insert": 0.2, "p_delete": 0.2,
               "p_dup_block": 0.1, "max_point_sites": 3, "max_indel": 4,
               "max_block": 16}                        # adapter _DEFAULT_MUTATE


def _beacon_rng(beacon: str, purpose: str, index: int) -> random.Random:
    """All reference randomness derives from the beacon. Nothing else."""
    h = hashlib.sha256(("%s|%s|%d" % (beacon, purpose, index)).encode())
    return random.Random(int.from_bytes(h.digest()[:8], "big"))


# ---- CANONICAL REFERENCE SAMPLERS -----------------------------------------
def R1_mutation_local(candidate: bytes, beacon: str, i: int) -> bytes:
    """R1: references are spec-default mutations of the candidate.
    Justification: the operator law is the substrate's OWN definition of a
    neighbour. Config is the adapter default verbatim -- not tuned."""
    rng = _beacon_rng(beacon, "R1", i)
    g = bytearray(candidate)
    c = SPEC_MUTATE
    r = rng.random() * (c["p_point"] + c["p_insert"] + c["p_delete"]
                        + c["p_dup_block"])
    if r < c["p_point"] or not g:
        if g:
            for _ in range(1 + rng.randrange(c["max_point_sites"])):
                g[rng.randrange(len(g))] = rng.randrange(256)
    elif r < c["p_point"] + c["p_insert"]:
        k = 1 + rng.randrange(c["max_indel"])
        pos = rng.randint(0, len(g))
        g[pos:pos] = bytes(rng.randrange(256) for _ in range(k))
    elif r < c["p_point"] + c["p_insert"] + c["p_delete"]:
        k = 1 + rng.randrange(min(c["max_indel"], len(g)))
        pos = rng.randrange(len(g) - k + 1)
        del g[pos:pos + k]
    else:
        blen = 1 + rng.randrange(min(c["max_block"], len(g)))
        start = rng.randrange(len(g) - blen + 1)
        block = bytes(g[start:start + blen])
        pos = rng.randint(0, len(g))
        g[pos:pos] = block
    return bytes(g)


def R2_length_matched_uniform(candidate: bytes, beacon: str, i: int) -> bytes:
    """R2: uniform random bytes of the SAME LENGTH as the candidate.
    Justification: every byte string is a legal program, so uniform is the
    canonical measure on program space; and length is taken from the
    CANDIDATE, which is hypothesis-side (free under Rule A). It is NOT a
    corpus band boundary -- no discovered length band appears anywhere."""
    rng = _beacon_rng(beacon, "R2", i)
    return bytes(rng.randrange(256) for _ in range(len(candidate)))


def R3_canonical_create(candidate: bytes, beacon: str, i: int) -> bytes:
    """R3: spec-default create_random. Support is [16, 96] BY SPEC and is
    NOT broadened. A candidate outside that support cannot use R3 -- see
    expressibility_report()."""
    rng = _beacon_rng(beacon, "R3", i)
    n = rng.randint(SPEC_CREATE["min_len"], SPEC_CREATE["max_len"])
    return bytes(rng.randrange(256) for _ in range(n))


SAMPLERS = {"R1_mutation_local": R1_mutation_local,
            "R2_length_matched_uniform": R2_length_matched_uniform,
            "R3_canonical_create": R3_canonical_create}


# ---- CANONICAL CONTEXT FAMILY ---------------------------------------------
def W1_uniform_words(beacon: str, block: int, arity: int) -> tuple:
    """Execution inputs: beacon-derived uniform 64-bit machine words.
    The historical task battery is CORPUS_DERIVED and is therefore NOT
    available as a context family."""
    rng = _beacon_rng(beacon, "W1", block)
    return tuple(rng.getrandbits(64) for _ in range(arity))


# ---- CANONICAL OBSERVABLES (intrinsic ExecResult fields only) --------------
def observables(res) -> dict:
    """Only fields the interpreter defines. Task success is not here: the
    task corpus is CORPUS_DERIVED."""
    return {
        "steps": res.steps,
        "halt_end": 1 if res.halt == "end" else 0,
        "halt_steps": 1 if res.halt == "steps" else 0,
        "n_opcodes_executed": len(res.opcodes_executed),
        "n_memory_written": len(res.memory_written),
        "stack_depth": len(res.stack),
        "output": res.output,
    }


def build_null_path(sampler_id: str, observable: str, arity: int,
                    max_steps: int, n_refs: int, n_blocks: int) -> NullPath:
    """Construct the tagged null path. Any CORPUS_DERIVED value raises."""
    return NullPath(
        reference_sampler=Tagged(
            sampler_id, SPEC_DERIVED,
            "canonical sampler defined from operator/program-space semantics",
            AD_SRC, "_DEFAULT_MUTATE" if sampler_id.startswith("R1")
            else "_DEFAULT_CREATE"),
        reference_config=Tagged(
            dict(SPEC_MUTATE) if sampler_id.startswith("R1")
            else dict(SPEC_CREATE), SPEC_DERIVED,
            "adapter default config transcribed verbatim; not tuned",
            AD_SRC, "_DEFAULT_MUTATE" if sampler_id.startswith("R1")
            else "_DEFAULT_CREATE"),
        context_family=Tagged(
            "W1_uniform_words", SPEC_DERIVED,
            "inputs are machine words per vm.machine_word; uniform is the "
            "canonical measure on that space", VM_SRC, "machine_word"),
        context_arity=Tagged(
            arity, PROTOCOL_CONSTANT,
            "fixed by protocol; must be justified without reference to any "
            "recorded outcome", fixed_at_seq=0),
        matching_law=Tagged(
            "candidate_length" if sampler_id.startswith("R2") else "none",
            SPEC_DERIVED,
            "matching is to the CANDIDATE's own length (hypothesis-side, "
            "free under Rule A), never to a discovered band",
            VM_SRC, "run_program"),
        role_rule=Tagged("beacon_uniform_permutation", EXTERNAL_RANDOMNESS,
                         "beacon-derived uniform permutation of slots"),
        tie_rule=Tagged("beacon_uniform", EXTERNAL_RANDOMNESS,
                        "beacon-derived uniform tie-break"),
        betting_rule=Tagged("LAM-MIX-V1", PROTOCOL_CONSTANT,
                            "fairness-certified mixture from the admission "
                            "protocol", fixed_at_seq=0),
        exclusions=Tagged((), PROTOCOL_CONSTANT,
                          "no exclusions; an exclusion set is a classic "
                          "corpus-smuggling channel", fixed_at_seq=0),
        stopping_rule=Tagged("fixed_block_budget", PROTOCOL_CONSTANT,
                             "fixed in advance; no data-dependent stopping",
                             fixed_at_seq=0),
        observable=Tagged(observable, SPEC_DERIVED,
                          "intrinsic ExecResult field defined by the VM",
                          VM_SRC, "ExecResult"),
        max_steps=Tagged(max_steps, PROTOCOL_CONSTANT,
                         "resource ceiling fixed by protocol, NOT chosen from "
                         "any observed step-limit outcome curve",
                         fixed_at_seq=0),
        n_references=Tagged(n_refs, PROTOCOL_CONSTANT,
                            "reference count fixed by protocol",
                            fixed_at_seq=0),
        n_blocks=Tagged(n_blocks, PROTOCOL_CONSTANT,
                        "block budget fixed by protocol", fixed_at_seq=0),
    )


def expressibility_report(candidate_len: int) -> dict:
    """Which canonical samplers can even be applied. Support limits are SPEC
    facts; they are reported, never widened."""
    out = {}
    out["R1_mutation_local"] = {
        "applicable": candidate_len > 0,
        "note": "defined for any non-empty genotype"}
    out["R2_length_matched_uniform"] = {
        "applicable": True,
        "note": "defined for every length; uniform measure is canonical "
                "because every byte string is a legal program"}
    ok3 = SPEC_CREATE["min_len"] <= candidate_len <= SPEC_CREATE["max_len"]
    out["R3_canonical_create"] = {
        "applicable": ok3,
        "note": ("in spec support [16,96]" if ok3 else
                 "OUT OF SPEC SUPPORT [16,96] -- claims requiring R3 for this "
                 "candidate are UNSTATEABLE. The sampler is NOT broadened.")}
    return out
