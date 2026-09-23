"""Grammar B: Proteus grammar v0.4 (12 operators, frozen weights) with its RANDOM-WORD draws
replaced by generator-valid draws (Campaign 5, Phase B).

Operators that draw whole instructions (insertion, replacement, randomization) draw valid
instructions; reference_redirection redraws one field within that field's valid range for the
instruction's opcode (or, for an unread field, uniform 32-bit). Structural operators (deletion,
duplication, movement, region_swap, splice, unreachable_removal, config_perturbation) move or
copy existing words and are unchanged. operand_perturbation (+-8 / bit flip on a raw word) is
UNCHANGED: it is the operator that can carry a valid word across the boundary, and how often it
does so is a measurement, not a design choice.

Names, weights and the operator record format are v0.4's. GRAMMAR_B_HASH identifies the variant.
"""
from __future__ import annotations

from proteus.foundry import grammar as GR
from proteus.foundry.affordances import N_OPCODES
from proteus.foundry.identity import hash_obj
from proteus.foundry.vm import validate_manifest

from .gen_b import valid_instr, IW
from .vm_b import REG_FIELDS

GRAMMAR_B_VERSION = "archaeon.grammar_b.v1(from proteus.grammar.v0.4)"
NAMES, WEIGHTS = GR.NAMES, GR.WEIGHTS


def _n_instr(m):
    return len(m["genome"]) // IW


def _copy(m):
    c = dict(m); c["genome"] = list(m["genome"]); return c


def op_insertion(m, rng, mate):
    n = _n_instr(m)
    cap = min(GR.GMAX, m["tape_words"] // IW)
    k = min(GR._k(rng), max(0, cap - n))
    if k == 0:
        return _copy(m), {"pos": None, "k": 0, "noop": True}
    pos = rng.randint(0, n) * IW
    c = _copy(m)
    new = []
    for _ in range(k):
        new.extend(valid_instr(rng, m["n_regs"]))
    c["genome"][pos:pos] = new
    return c, {"pos": pos // IW, "k": k}


def op_replacement(m, rng, mate):
    n = _n_instr(m)
    pos = rng.randint(0, n - 1) * IW
    c = _copy(m)
    c["genome"][pos:pos + IW] = valid_instr(rng, m["n_regs"])
    return c, {"pos": pos // IW}


def op_reference_redirection(m, rng, mate):
    n = _n_instr(m)
    pos = rng.randint(0, n - 1) * IW
    field = rng.randint(1, 3)
    c = _copy(m)
    op = m["genome"][pos]
    if op < N_OPCODES and field in REG_FIELDS[op]:
        c["genome"][pos + field] = rng.randbelow(m["n_regs"])
    else:
        c["genome"][pos + field] = rng.next_u32()
    return c, {"pos": pos // IW, "field": field}


def op_randomization(m, rng, mate):
    n = _n_instr(m)
    k = min(GR._k(rng), n)
    pos = rng.randint(0, n - k) * IW
    c = _copy(m)
    new = []
    for _ in range(k):
        new.extend(valid_instr(rng, m["n_regs"]))
    c["genome"][pos:pos + k * IW] = new
    return c, {"pos": pos // IW, "k": k}


IMPL = dict(GR.IMPL)
IMPL.update({"insertion": op_insertion, "replacement": op_replacement, "reference_redirection": op_reference_redirection,
             "randomization": op_randomization})
assert set(IMPL) == set(NAMES), sorted(set(IMPL) ^ set(NAMES))

GRAMMAR_B_HASH = hash_obj({"version": GRAMMAR_B_VERSION, "operators": [list(o) for o in GR.OPERATORS], "base": GR.GRAMMAR_HASH,
                           "valid_draw_operators": ["insertion", "replacement", "reference_redirection", "randomization"],
                           "unchanged": ["deletion", "duplication", "movement", "region_swap", "splice", "unreachable_removal",
                                         "config_perturbation", "operand_perturbation"]})


def mutate_b(manifest: dict, rng, mate=None, name=None):
    if name is None:
        name = rng.weighted(NAMES, WEIGHTS)
    child, args = IMPL[name](manifest, rng, mate)
    validate_manifest(child)
    return child, {"operator": name, "args": args, "len_before": len(manifest["genome"]) // IW, "len_after": len(child["genome"]) // IW,
                   "grammar": GRAMMAR_B_VERSION}


def descend_b(parent: dict, mutation_seed: int, mate=None, n_ops: int = 1, force_operator=None):
    """Mirror of proteus.foundry.lineage.descend with grammar B. Returns (child_record, record)."""
    from proteus.foundry.prng import SplitMix64, seed_from                     # noqa: PLC0415
    from proteus.foundry.generate import organism_record                      # noqa: PLC0415
    rng = SplitMix64(seed_from("archaeon.descend_b.v1", mutation_seed, parent["organism_id"], mate["organism_id"] if mate else "", GRAMMAR_B_HASH))
    m = parent["manifest"]; ops = []
    for _ in range(n_ops):
        m, rec = mutate_b(m, rng, mate["manifest"] if mate else None, force_operator); ops.append(rec)
    child = organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    record = {"schema_version": "archaeon.lineage_b.v1", "organism_id": child["organism_id"], "lineage_id": child["lineage_id"],
              "generation": child["generation"], "parent_ids": [parent["organism_id"]] + ([mate["organism_id"]] if mate else []),
              "operators": ops, "grammar_hash": GRAMMAR_B_HASH}
    return child, record
