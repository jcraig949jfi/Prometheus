"""Expressiveness witness: can the FROZEN v0 ISA express a two-value KEYED memory?

Why this exists (point release, Stage 0, 2026-09-17). Campaign 3 (C3-SFE-02, C3-SFE-08) found
that every W2_K2 shelf organism is a ONE-value memory and that no search reached the two-value
summit in 0 of 60 runs; its recommendation C4-3 asks whether the cause is "a register/addressing
primitive the grammar lacks, or a search operator that can cross the two-value valley". Those are
different point-release items (an ISA profile versus a search-operator study), so the first
question to settle is whether the primitive is absent. This module settles it by CONSTRUCTION,
not by opinion: a hand-written genome under the frozen runtime, run on a neutral probe that
Proteus owns and that is not a qualification world.

What it is NOT: a claim about W2_K2 (whose protocol this seat has not read and does not read), a
claim that search CAN find this program, or a score of any organism. It is a witness that the
affordance exists, plus its cost in ops, plus the controls that show the probe discriminates.

Probe protocol (neutral, world-free). Two input channels per tick: channel 0 carries a key,
channel 1 carries a value when the tick is a PUT and is EMPTY when the tick is an ASK. One
output channel. Correct behaviour: on an ASK for key k, output the most recent value PUT under
k. Keys are in [0, 15] so the address key+OFFSET stays inside the tape and outside the genome.

Genome (12 instructions, 4 words each; operand slots per proteus/foundry/vm.py, which is the
authority over the affordance-table prose -- TODO T9):
    0  LDC  r1 <- 1          channel index 1
    1  INQ  r2 <- unread(ch r1)   value present this tick?
    2  IN   r3 <- ch r0          key (r0 is 0 after the persist reset)
    3  LDC  r4 <- OFFSET
    4  ADD  r3 <- r3 + r4        address = key + OFFSET
    5  JZ   r2, +4               no value -> ASK path (instruction 9)
    6  IN   r5 <- ch r1          value
    7  ST   tape[r3] <- r5       PUT
    8  HALT
    9  LD   r6 <- tape[r3]       ASK
   10  OUT  ch r0 <- r6
   11  HALT
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.identity import RUNTIME_HASH, hash_obj
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import SCHEMA, Meter, Player, validate_manifest

WITNESS_SCHEMA = "proteus.keyed_memory_witness.v1"
OUT_PATH = Path(__file__).resolve().parent / "KEYED_MEMORY_WITNESS.json"

# opcodes by number (affordance_table.v0.json / vm.py)
NOP, HALT, YIELD, LDC, MOV, LD, ST, ADD = 0, 1, 2, 3, 4, 5, 6, 7
EQ, JMP, JZ, JNZ, IN, INQ, OUT = 16, 18, 19, 20, 21, 22, 23

TAPE_WORDS = 64
N_REGS = 8
MAX_KEY = 15


def _instr(op, a=0, b=0, c=0):
    return [op, a, b, c]


def keyed_memory_genome(offset: int) -> list:
    g = []
    g += _instr(LDC, 1, 1)          # r1 = 1
    g += _instr(INQ, 2, 1)          # r2 = unread on channel r1
    g += _instr(IN, 3, 0)           # r3 = key from channel r0
    g += _instr(LDC, 4, offset)     # r4 = OFFSET
    g += _instr(ADD, 3, 3, 4)       # r3 = key + OFFSET
    g += _instr(JZ, 2, 4)           # if r2 == 0 goto instruction 9
    g += _instr(IN, 5, 1)           # r5 = value from channel r1
    g += _instr(ST, 3, 5)           # tape[r3] = r5
    g += _instr(HALT)
    g += _instr(LD, 6, 3)           # r6 = tape[r3]
    g += _instr(OUT, 6, 0)          # output channel r0 <- r6
    g += _instr(HALT)
    return g


def one_value_genome() -> list:
    """The shelf strategy C3-SFE-02 describes: remember the LAST value PUT, answer every ASK
    with it. Negative control: the probe must score it below the keyed program on two-key asks."""
    g = []
    g += _instr(LDC, 1, 1)          # 0 r1 = 1
    g += _instr(INQ, 2, 1)          # 1 value present?
    g += _instr(LDC, 4, 60)         # 2 fixed slot
    g += _instr(JZ, 2, 4)           # 3 no value -> instruction 7
    g += _instr(IN, 5, 1)           # 4 r5 = value
    g += _instr(ST, 4, 5)           # 5 tape[60] = r5
    g += _instr(HALT)               # 6
    g += _instr(LD, 6, 4)           # 7 r6 = tape[60]
    g += _instr(OUT, 6, 0)          # 8
    g += _instr(HALT)               # 9
    return g


def manifest_for(genome: list) -> dict:
    m = {
        "schema_version": SCHEMA,
        "n_regs": N_REGS,
        "tape_words": TAPE_WORDS,
        "genome": list(genome),
        "code_writable": False,
        "persist": "tape",
        "tick_budget": 16,
        "out_cap": 1,
    }
    validate_manifest(m)
    return m


def run_episode(manifest: dict, ticks: list, seed: int = 0) -> dict:
    """ticks: list of ("PUT", key, value) or ("ASK", key, expected). Returns per-tick outputs,
    correctness on ASK ticks, and the meter's ops_by_category (timings excluded, per T2)."""
    p = Player(manifest)
    st = p.fresh_state()
    rng = SplitMix64(seed)
    meter = Meter()
    outs, correct, total = [], 0, 0
    statuses = []
    for t in ticks:
        if t[0] == "PUT":
            inputs = [[t[1]], [t[2]]]
        else:
            inputs = [[t[1]], []]
        o, status = p.run_tick(st, inputs, 1, rng, meter=meter)
        statuses.append(status)
        got = o[0][0] if o and o[0] else None
        outs.append(got)
        if t[0] == "ASK":
            total += 1
            correct += 1 if got == t[2] else 0
        st["ticks"] += 1
    md = meter.as_dict()
    return {
        "outputs": outs,
        "asks": total,
        "correct": correct,
        "statuses": sorted(set(statuses)),
        "ops": md.get("ops"),
        "ops_by_category": md.get("ops_by_category"),
    }


def two_key_episode() -> list:
    """Two keys, interleaved PUTs and ASKs, with an overwrite: the minimal protocol on which a
    one-value memory and a keyed memory differ."""
    return [
        ("PUT", 3, 1001), ("PUT", 9, 2002),
        ("ASK", 3, 1001), ("ASK", 9, 2002),
        ("PUT", 3, 3003),
        ("ASK", 3, 3003), ("ASK", 9, 2002),
        ("ASK", 9, 2002), ("ASK", 3, 3003),
    ]


def all_keys_episode() -> list:
    ticks = [("PUT", k, 5000 + 7 * k) for k in range(MAX_KEY + 1)]
    ticks += [("ASK", k, 5000 + 7 * k) for k in reversed(range(MAX_KEY + 1))]
    return ticks


def witness() -> dict:
    offset = 48  # = genome words; addresses 48..63 hold keys 0..15
    keyed = manifest_for(keyed_memory_genome(offset))
    one = manifest_for(one_value_genome())
    inert = manifest_for([NOP, 0, 0, 0] * 12)
    rows = {}
    for name, m in (("keyed", keyed), ("one_value", one), ("inert", inert)):
        rows[name] = {
            "organism_id": hash_obj(m),
            "genome_instructions": len(m["genome"]) // 4,
            "two_key": run_episode(m, two_key_episode()),
            "all_keys": run_episode(m, all_keys_episode()),
        }
    k2, o2 = rows["keyed"]["two_key"], rows["one_value"]["two_key"]
    verdict = (
        "ISA_EXPRESSES_KEYED_MEMORY"
        if k2["correct"] == k2["asks"] and rows["keyed"]["all_keys"]["correct"] == MAX_KEY + 1
        else "WITNESS_FAILED"
    )
    controls = {
        "negative_one_value_scores_below_keyed": o2["correct"] < k2["correct"],
        "negative_one_value_exact": [o2["correct"], o2["asks"]],
        "inert_outputs_nothing": all(v is None for v in rows["inert"]["two_key"]["outputs"]),
    }
    return {
        "schema_version": WITNESS_SCHEMA,
        "runtime_hash": RUNTIME_HASH,
        "probe": "two input channels (key, value-or-empty), one output channel; keys 0..15; "
                 "persist=tape, code_writable=false; NOT a qualification world",
        "verdict": verdict,
        "controls": controls,
        "rows": rows,
        "what_this_does_not_establish": [
            "that search under proteus.grammar.v0.4 reaches this program (C3 says 0/60 runs did on W2_K2)",
            "anything about W2_K2's protocol, which this seat has not read",
            "that this is the smallest such program",
        ],
    }


def main() -> int:
    w = witness()
    OUT_PATH.write_text(json.dumps(w, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT_PATH)
    print("verdict:", w["verdict"])
    for name, r in w["rows"].items():
        print("  %-10s instr=%2d two_key %d/%d ops=%s  all_keys %d/%d ops=%s" % (
            name, r["genome_instructions"], r["two_key"]["correct"], r["two_key"]["asks"],
            r["two_key"]["ops"], r["all_keys"]["correct"], r["all_keys"]["asks"], r["all_keys"]["ops"]))
    print("controls:", json.dumps(w["controls"]))
    return 0 if w["verdict"] == "ISA_EXPRESSES_KEYED_MEMORY" else 1


if __name__ == "__main__":
    sys.exit(main())
