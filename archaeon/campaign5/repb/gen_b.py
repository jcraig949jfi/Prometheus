"""Generators for representation B (Campaign 5, Phase B).

    canonicalize(m)          the OLD program's meaning, written in the narrow encoding: every opcode
                             word -> word mod 25, every register field the opcode reads -> word mod
                             n_regs, other fields untouched. Behaviour under PlayerB equals the old
                             player's behaviour on the ORIGINAL words (the fixtures check it).
    sample_valid(fm, rng)    a generator-valid program: opcode uniform in [0,25), register fields
                             uniform in [0,n_regs), immediate/offset fields uniform 32-bit, other
                             fields uniform 32-bit (unread). Same manifest knobs as the old FOUNDRY.
    inject_invalid(m, rng, k) k controlled invalid words: k distinct instructions, each given one
                             out-of-range word in a field the opcode reads (opcode word >= 25 or
                             register word >= n_regs, chosen at random), so that static validity
                             drops by exactly k.
    raw_words(fm, rng)       the OLD generator's uniform-32-bit program (proteus generate), for the
                             raw-word population.
"""
from __future__ import annotations

from proteus.foundry.affordances import N_OPCODES
from proteus.foundry.generate import sample_manifest, validate_foundry_manifest
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import validate_manifest, MASK32

from .vm_b import REG_FIELDS, instruction_validity

IW = 4


def canonicalize(m: dict) -> dict:
    g, nr = m["genome"], m["n_regs"]
    out = list(g)
    for i in range(0, len(g), IW):
        op = g[i] % N_OPCODES
        out[i] = op
        for f in REG_FIELDS[op]:
            out[i + f] = g[i + f] % nr
    c = dict(m); c["genome"] = out
    validate_manifest(c)
    return c


def valid_instr(rng: SplitMix64, n_regs: int) -> list:
    op = rng.randbelow(N_OPCODES)
    w = [op, rng.next_u32(), rng.next_u32(), rng.next_u32()]
    for f in REG_FIELDS[op]:
        w[f] = rng.randbelow(n_regs)
    return w


def sample_valid(fm: dict, rng: SplitMix64) -> dict:
    """Same knob draws as proteus.generate.sample_manifest (n_regs, tape, length, flags), then a
    generator-valid genome of the same length drawn from the same stream position."""
    m = sample_manifest(fm, rng)               # consumes the knob draws and 4*n_instr raw words
    nr = m["n_regs"]
    g = []
    for _ in range(len(m["genome"]) // IW):
        g.extend(valid_instr(rng, nr))
    m = dict(m); m["genome"] = g
    validate_manifest(m)
    return m


def raw_words(fm: dict, rng: SplitMix64) -> dict:
    return sample_manifest(fm, rng)


def inject_invalid(m: dict, rng: SplitMix64, k: int) -> tuple:
    """Return (child, sites). Picks k distinct VALID instructions and breaks one read field each."""
    g, nr = m["genome"], m["n_regs"]
    n = len(g) // IW
    valid_idx = [i for i in range(n) if instruction_validity(g[i * IW:i * IW + IW], nr) == "ok"]
    if k > len(valid_idx):
        raise ValueError("not enough valid instructions to inject %d faults" % k)
    out = list(g); sites = []
    for _ in range(k):
        j = valid_idx.pop(rng.randbelow(len(valid_idx)))
        op = out[j * IW]
        fields = [0] + list(REG_FIELDS[op])          # 0 = the opcode word itself
        f = fields[rng.randbelow(len(fields))]
        if f == 0:
            out[j * IW] = N_OPCODES + rng.randbelow((1 << 32) - N_OPCODES)
            sites.append({"instr": j, "field": "opcode"})
        else:
            out[j * IW + f] = nr + rng.randbelow((1 << 32) - nr)
            sites.append({"instr": j, "field": "reg%d" % f})
    c = dict(m); c["genome"] = out
    validate_manifest(c)
    return c, sites


def population(kind: str, fm: dict, seed: int, n: int, k: int = 0) -> list:
    """kind in raw | valid | injected(k). Deterministic in (kind, seed, n, k)."""
    validate_foundry_manifest(dict(fm, n=n, seed=seed))
    from proteus.foundry.prng import seed_from                               # noqa: PLC0415
    root = SplitMix64(seed_from("archaeon.repb.population.v1", kind, seed, k))
    out = []
    for i in range(n):
        r = root.derive("organism", i)
        if kind == "raw":
            m = raw_words(fm, r)
        elif kind == "valid":
            m = sample_valid(fm, r)
        elif kind == "injected":
            base = sample_valid(fm, r)
            need = k
            while len(base["genome"]) // IW < need:              # too short to carry k faults: lengthen with valid instructions
                base = dict(base); base["genome"] = base["genome"] + valid_instr(r, base["n_regs"])
                if len(base["genome"]) > base["tape_words"]:
                    base["tape_words"] = min(4096, base["tape_words"] * 2)
            m, _ = inject_invalid(base, r, k)
        else:
            raise ValueError(kind)
        out.append(m)
    return out


__all__ = ["canonicalize", "valid_instr", "sample_valid", "raw_words", "inject_invalid", "population", "MASK32"]
