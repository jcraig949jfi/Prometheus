"""Deterministic population generation from a compact Foundry manifest.

Every organism is a sample from the manifest's declared ranges, drawn from a stream derived from
(seed, index). Same manifest + same runtime => byte-identical population. Genome words are
uniform 32-bit integers: the generator holds NO opinion about which opcodes or operands are
common. Whatever bias exists is the affordance table's own (opcode = word mod N_OPCODES), which
is published and hashed.
"""
from __future__ import annotations

from .affordances import STORAGE_BOUNDS
from .identity import RUNTIME_HASH, hash_obj
from .prng import SplitMix64, seed_from
from .vm import SCHEMA, PERSIST_POLICIES, validate_manifest

FOUNDRY_SCHEMA = "proteus.foundry_manifest.v0"

DEFAULT_FOUNDRY_MANIFEST = {
    "schema_version": FOUNDRY_SCHEMA,
    "seed": 0,
    "n": 0,
    "n_regs_range": [2, 16],
    "tape_words_choices": [16, 32, 64, 128, 256, 512, 1024],
    "genome_instr_range": [1, 64],          # instructions (4 words each); capped by tape_words/4
    "code_writable_weights": [1, 1],         # [false, true]
    "persist_weights": [1, 1, 1, 1],         # none, regs, tape, all
    "tick_budget_choices": [16, 64, 256, 1024],
    "out_cap_choices": [1, 4, 16],
}


def validate_foundry_manifest(fm: dict) -> None:
    if fm.get("schema_version") != FOUNDRY_SCHEMA:
        raise ValueError("foundry manifest schema mismatch")
    b = STORAGE_BOUNDS
    lo, hi = fm["n_regs_range"]
    if not (b["n_regs"]["min"] <= lo <= hi <= b["n_regs"]["max"]):
        raise ValueError("n_regs_range outside affordance bounds")
    for t in fm["tape_words_choices"]:
        if t % 4 or not b["tape_words"]["min"] <= t <= b["tape_words"]["max"]:
            raise ValueError("tape_words choice invalid")
    glo, ghi = fm["genome_instr_range"]
    if glo < 1 or ghi * 4 > b["genome_words"]["max"] or glo > ghi:
        raise ValueError("genome_instr_range invalid")
    for t in fm["tick_budget_choices"]:
        if not b["tick_budget"]["min"] <= t <= b["tick_budget"]["max"]:
            raise ValueError("tick_budget choice invalid")
    for t in fm["out_cap_choices"]:
        if not b["out_cap"]["min"] <= t <= b["out_cap"]["max"]:
            raise ValueError("out_cap choice invalid")
    if len(fm["persist_weights"]) != len(PERSIST_POLICIES) or len(fm["code_writable_weights"]) != 2:
        raise ValueError("weight vectors wrong length")
    if not isinstance(fm["n"], int) or fm["n"] < 0:
        raise ValueError("n invalid")


def sample_manifest(fm: dict, rng: SplitMix64) -> dict:
    n_regs = rng.randint(*fm["n_regs_range"])
    tape_words = rng.choice(fm["tape_words_choices"])
    glo, ghi = fm["genome_instr_range"]
    ghi = min(ghi, tape_words // 4)
    glo = min(glo, ghi)
    n_instr = rng.randint(glo, ghi)
    genome = [rng.next_u32() for _ in range(4 * n_instr)]
    code_writable = bool(rng.weighted([False, True], fm["code_writable_weights"]))
    persist = rng.weighted(list(PERSIST_POLICIES), fm["persist_weights"])
    m = {
        "schema_version": SCHEMA,
        "n_regs": n_regs,
        "tape_words": tape_words,
        "genome": genome,
        "code_writable": code_writable,
        "persist": persist,
        "tick_budget": rng.choice(fm["tick_budget_choices"]),
        "out_cap": rng.choice(fm["out_cap_choices"]),
    }
    validate_manifest(m)
    return m


def organism_record(manifest: dict, lineage_id: str | None, generation: int) -> dict:
    oid = hash_obj(manifest)
    return {
        "organism_id": oid,
        "lineage_id": lineage_id or oid,
        "generation": generation,
        "runtime_hash": RUNTIME_HASH,
        "manifest": manifest,
    }


def generate(fm: dict) -> list:
    """Generation-0 population. Each organism is the root of its own lineage."""
    validate_foundry_manifest(fm)
    root = SplitMix64(seed_from("proteus.generate.v0", fm["seed"], RUNTIME_HASH))
    out = []
    for i in range(fm["n"]):
        r = root.derive("organism", i)
        m = sample_manifest(fm, r)
        out.append(organism_record(m, None, 0))
    return out


def foundry_identity(fm: dict) -> str:
    return hash_obj({"foundry_manifest": fm, "runtime_hash": RUNTIME_HASH})
