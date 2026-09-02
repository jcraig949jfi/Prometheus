"""The mutation grammar. Thirteen syntactic/genotypic operators, frozen weights, hashed identity.

Amendment A3: operators manipulate REPRESENTATION. None of them "adds" a capability. Every
operator below is describable without cognition-laden language; the descriptions are the
operator table and are part of the hashed identity. Deletion mass exceeds insertion mass so that
growth is not the default direction (brief S8); whether the grammar is free of a complexity
ratchet in EITHER direction is a measured property (A6), not a design claim.

An operator takes (manifest, rng, mate_manifest|None) and returns (new_manifest, op_record).
Manifests are never mutated in place. A resulting manifest that violates the published bounds is
the operator's error and is caught by validate_manifest; operators are written to stay in bounds.
"""
from __future__ import annotations

from .affordances import STORAGE_BOUNDS, N_OPCODES, OPCODES_IN
from .identity import hash_obj
from .prng import SplitMix64
from .vm import PERSIST_POLICIES, validate_manifest

MASK32 = 0xFFFFFFFF
IW = 4  # instruction words

# name -> (weight, description). Weights sum to 1.00. Frozen; changing them changes GRAMMAR_HASH.
OPERATORS = (
    ("insertion",             0.08, "insert k in [1,4] uniformly random instructions at an aligned position"),
    ("deletion",              0.11, "delete k in [1,4] contiguous instructions at an aligned position"),
    ("duplication",           0.04, "copy k in [1,4] contiguous instructions and insert the copy at an aligned position"),
    ("movement",              0.08, "cut k in [1,4] contiguous instructions and paste them at another aligned position"),
    ("replacement",           0.12, "overwrite one instruction with four uniformly random words"),
    ("operand_perturbation",  0.19, "pick one word; add a signed delta in [-8,8] or flip one bit"),
    ("reference_redirection", 0.08, "pick one instruction; keep its opcode word; overwrite one operand word uniformly"),
    ("region_swap",           0.06, "swap two non-overlapping regions of k in [1,4] instructions"),
    ("splice",                0.05, "replace a region of k instructions with a region of k' instructions copied from a mate (self if none)"),
    ("zeroing",               0.04, "set a region of k in [1,4] instructions to all-zero words (NOP 0 0 0)"),
    ("randomization",         0.04, "set a region of k in [1,4] instructions to uniformly random words"),
    ("unreachable_removal",   0.03, "delete one instruction not statically reachable from ip=0 by fallthrough or jump targets (no offset fixup; approximate when code_writable)"),
    ("config_perturbation",   0.08, "step one manifest limit (n_regs, tape_words, code_writable, persist, tick_budget, out_cap) within published bounds"),
)
NAMES = tuple(o[0] for o in OPERATORS)
WEIGHTS = tuple(o[1] for o in OPERATORS)
assert abs(sum(WEIGHTS) - 1.0) < 1e-9

# v0 -> v0.1 (2026-09-02): neutrality run 1 FAILED (proteus/v0/NEUTRALITY_RESULT_grammar_v0_FAIL.json).
# Two changes, both to LENGTH behaviour only: deletion 0.10 -> 0.11 and operand_perturbation
# 0.20 -> 0.19 so that expected instructions removed per generation (0.275 + unreachable
# 0.01..0.03) matches expected instructions added (0.30); and config_perturbation no longer
# clamps a halved tape to the genome length (which pinned genomes at their cap) -- it is a
# no-op when the genome would not fit. Calibrated on random genomes, not on any probe result.
# v0.1 -> v0.2 (2026-09-02): run 2 FAILED at cohort 128 because a halving that fits the genome
# EXACTLY still lands the cap on the genome. Halving is now a no-op unless the genome would
# occupy at most half of the new tape. Weights unchanged. Nothing else changed.
GRAMMAR_VERSION = "proteus.grammar.v0.2"
GRAMMAR_HASH = hash_obj({"version": GRAMMAR_VERSION, "operators": [list(o) for o in OPERATORS],
                         "k_range": [1, 4], "delta_range": [-8, 8],
                         "config_tape_halving": "noop_unless_genome_at_most_half_of_new_tape"})

GMIN = STORAGE_BOUNDS["genome_words"]["min"] // IW
GMAX = STORAGE_BOUNDS["genome_words"]["max"] // IW


def _n_instr(m):
    return len(m["genome"]) // IW


def _copy(m):
    c = dict(m)
    c["genome"] = list(m["genome"])
    return c


def _rand_instr(rng, k):
    return [rng.next_u32() for _ in range(IW * k)]


def _k(rng):
    return rng.randint(1, 4)


def op_insertion(m, rng, mate):
    n = _n_instr(m)
    cap = min(GMAX, m["tape_words"] // IW)
    k = min(_k(rng), cap - n)
    if k <= 0:
        return _copy(m), {"noop": "at_max"}
    pos = rng.randint(0, n) * IW
    c = _copy(m)
    c["genome"][pos:pos] = _rand_instr(rng, k)
    return c, {"k": k, "pos": pos // IW}


def op_deletion(m, rng, mate):
    n = _n_instr(m)
    k = min(_k(rng), n - GMIN)
    if k <= 0:
        return _copy(m), {"noop": "at_min"}
    pos = rng.randint(0, n - k) * IW
    c = _copy(m)
    del c["genome"][pos:pos + IW * k]
    return c, {"k": k, "pos": pos // IW}


def op_duplication(m, rng, mate):
    n = _n_instr(m)
    cap = min(GMAX, m["tape_words"] // IW)
    k = min(_k(rng), n, cap - n)
    if k <= 0:
        return _copy(m), {"noop": "at_max"}
    src = rng.randint(0, n - k) * IW
    seg = m["genome"][src:src + IW * k]
    pos = rng.randint(0, n) * IW
    c = _copy(m)
    c["genome"][pos:pos] = seg
    return c, {"k": k, "src": src // IW, "pos": pos // IW}


def op_movement(m, rng, mate):
    n = _n_instr(m)
    k = min(_k(rng), n)
    if n - k <= 0:
        return _copy(m), {"noop": "too_short"}
    src = rng.randint(0, n - k) * IW
    c = _copy(m)
    seg = c["genome"][src:src + IW * k]
    del c["genome"][src:src + IW * k]
    pos = rng.randint(0, n - k) * IW
    c["genome"][pos:pos] = seg
    return c, {"k": k, "src": src // IW, "pos": pos // IW}


def op_replacement(m, rng, mate):
    n = _n_instr(m)
    pos = rng.randint(0, n - 1) * IW
    c = _copy(m)
    c["genome"][pos:pos + IW] = _rand_instr(rng, 1)
    return c, {"pos": pos // IW}


def op_operand_perturbation(m, rng, mate):
    g = m["genome"]
    i = rng.randint(0, len(g) - 1)
    c = _copy(m)
    if rng.randbelow(2) == 0:
        d = rng.randint(-8, 8)
        c["genome"][i] = (g[i] + d) & MASK32
        return c, {"word": i, "delta": d}
    bit = rng.randbelow(32)
    c["genome"][i] = g[i] ^ (1 << bit)
    return c, {"word": i, "flip_bit": bit}


def op_reference_redirection(m, rng, mate):
    n = _n_instr(m)
    pos = rng.randint(0, n - 1) * IW
    field = rng.randint(1, 3)
    c = _copy(m)
    c["genome"][pos + field] = rng.next_u32()
    return c, {"pos": pos // IW, "field": field}


def op_region_swap(m, rng, mate):
    n = _n_instr(m)
    k = min(_k(rng), n // 2)
    if k <= 0:
        return _copy(m), {"noop": "too_short"}
    a = rng.randint(0, n - 2 * k)
    b = rng.randint(a + k, n - k)
    c = _copy(m)
    g = c["genome"]
    A = g[a * IW:(a + k) * IW]
    B = g[b * IW:(b + k) * IW]
    g[a * IW:(a + k) * IW] = B
    g[b * IW:(b + k) * IW] = A
    return c, {"k": k, "a": a, "b": b}


def op_splice(m, rng, mate):
    src_m = mate if mate is not None else m
    n = _n_instr(m)
    ns = _n_instr(src_m)
    k = min(_k(rng), n)
    k2 = min(_k(rng), ns)
    cap = min(GMAX, m["tape_words"] // IW)
    new_n = n - k + k2
    if new_n < GMIN or new_n > cap:
        return _copy(m), {"noop": "bounds", "mate_used": mate is not None}
    pos = rng.randint(0, n - k) * IW
    spos = rng.randint(0, ns - k2) * IW
    seg = src_m["genome"][spos:spos + IW * k2]
    c = _copy(m)
    c["genome"][pos:pos + IW * k] = seg
    return c, {"k": k, "k_mate": k2, "pos": pos // IW, "mate_pos": spos // IW, "mate_used": mate is not None}


def op_zeroing(m, rng, mate):
    n = _n_instr(m)
    k = min(_k(rng), n)
    pos = rng.randint(0, n - k) * IW
    c = _copy(m)
    c["genome"][pos:pos + IW * k] = [0] * (IW * k)
    return c, {"k": k, "pos": pos // IW}


def op_randomization(m, rng, mate):
    n = _n_instr(m)
    k = min(_k(rng), n)
    pos = rng.randint(0, n - k) * IW
    c = _copy(m)
    c["genome"][pos:pos + IW * k] = _rand_instr(rng, k)
    return c, {"k": k, "pos": pos // IW}


def static_reachable(genome: list, tape_words: int) -> set:
    """Instruction indices reachable from ip=0 over the genome region by fallthrough and jumps.

    The tape beyond the genome is zeros (NOP) and wraps to 0, so fallthrough past the genome end
    returns to instruction 0. HALT has no fallthrough within a tick but the next tick restarts at
    0, which is already in the set. Jumps landing outside the genome region land on NOPs that
    fall through back to 0. Static over the INITIAL tape only; unsound if code is rewritten.
    """
    n = len(genome) // IW
    total = tape_words // IW
    seen = set()
    stack = [0]
    ctrl = OPCODES_IN["control"]
    while stack:
        i = stack.pop()
        if i in seen or i >= n:
            continue
        seen.add(i)
        op = genome[i * IW] % N_OPCODES
        if op == 1:      # HALT
            continue
        nxt = (i + 1) % total
        if op in ctrl:
            bw = genome[i * IW + 2]
            off = bw - (1 << 32) if bw >= (1 << 31) else bw
            tgt = (i + off) % total
            if tgt < n:
                stack.append(tgt)
            else:
                stack.append(0)
            if op != 18:  # conditional: fallthrough too
                stack.append(nxt if nxt < n else 0)
        else:
            stack.append(nxt if nxt < n else 0)
    return seen


def op_unreachable_removal(m, rng, mate):
    n = _n_instr(m)
    if n <= GMIN:
        return _copy(m), {"noop": "at_min"}
    reach = static_reachable(m["genome"], m["tape_words"])
    unreach = [i for i in range(n) if i not in reach]
    if not unreach:
        return _copy(m), {"noop": "all_reachable"}
    i = rng.choice(unreach)
    c = _copy(m)
    del c["genome"][i * IW:(i + 1) * IW]
    return c, {"pos": i, "n_unreachable": len(unreach), "approx": m["code_writable"]}


def op_config_perturbation(m, rng, mate):
    b = STORAGE_BOUNDS
    c = _copy(m)
    which = rng.choice(["n_regs", "tape_words", "code_writable", "persist", "tick_budget", "out_cap"])
    if which == "n_regs":
        v = m["n_regs"] + rng.choice([-1, 1])
        c["n_regs"] = min(max(v, b["n_regs"]["min"]), b["n_regs"]["max"])
    elif which == "tape_words":
        v = m["tape_words"] * 2 if rng.randbelow(2) else m["tape_words"] // 2
        v = min(max(v, b["tape_words"]["min"]), b["tape_words"]["max"])
        v -= v % 4
        # v0.2: a tape change must not move the cap ONTO the genome. Halving is allowed only if the
        # genome would occupy at most half of the new tape, so the genome keeps at least as much
        # headroom (in fraction of tape) as the smallest tape it could have been generated on.
        if v < m["tape_words"] and len(m["genome"]) * 2 > v:
            return c, {"field": which, "noop": "cap_would_land_on_genome", "from": m["tape_words"], "to": m["tape_words"]}
        c["tape_words"] = v
    elif which == "code_writable":
        c["code_writable"] = not m["code_writable"]
    elif which == "persist":
        others = [p for p in PERSIST_POLICIES if p != m["persist"]]
        c["persist"] = rng.choice(others)
    elif which == "tick_budget":
        v = m["tick_budget"] * 2 if rng.randbelow(2) else m["tick_budget"] // 2
        c["tick_budget"] = min(max(v, b["tick_budget"]["min"]), b["tick_budget"]["max"])
    else:
        v = m["out_cap"] * 2 if rng.randbelow(2) else m["out_cap"] // 2
        c["out_cap"] = min(max(v, b["out_cap"]["min"]), b["out_cap"]["max"])
    return c, {"field": which, "from": m[which], "to": c[which]}


IMPL = {
    "insertion": op_insertion, "deletion": op_deletion, "duplication": op_duplication,
    "movement": op_movement, "replacement": op_replacement,
    "operand_perturbation": op_operand_perturbation, "reference_redirection": op_reference_redirection,
    "region_swap": op_region_swap, "splice": op_splice, "zeroing": op_zeroing,
    "randomization": op_randomization, "unreachable_removal": op_unreachable_removal,
    "config_perturbation": op_config_perturbation,
}
assert set(IMPL) == set(NAMES)

LENGTH_CHANGING = ("insertion", "deletion", "duplication", "splice", "unreachable_removal")


def mutate(manifest: dict, rng: SplitMix64, mate: dict | None = None, name: str | None = None):
    """Apply one operator (chosen by frozen weights unless named). Returns (child, op_record)."""
    if name is None:
        name = rng.weighted(NAMES, WEIGHTS)
    child, args = IMPL[name](manifest, rng, mate)
    validate_manifest(child)
    rec = {"operator": name, "args": args,
           "len_before": len(manifest["genome"]) // IW, "len_after": len(child["genome"]) // IW}
    return child, rec
