"""Interventions on an organism's STATE between ticks (directive XI). Applied to a fixed
genotype; the readout is the reward difference per intervention = the failure geometry.

The non-code tape is tape[glen:] where glen is the genome length. For a code_writable
organism the genome region may also hold data; the boundary is still glen (a recorded
limitation of v0.1, not a claim that data cannot live there).
"""
from __future__ import annotations

from typing import List, Optional

from proteus.foundry.prng import SplitMix64

NAMES: List[str] = ["ERASE_ALL", "ERASE_REGS", "ERASE_TAPE", "SCRAMBLE_LOC", "SCRAMBLE_VAL",
                    "SWAP_TWO", "HALVE_CAP", "RESET_IP", "TRANSPLANT"]


def _noncode(player) -> range:
    return range(player.genome_len, player.tape_words)


def apply(name: str, player, state: dict, rng: SplitMix64, donor: Optional[dict] = None) -> None:
    tape, regs = state["tape"], state["regs"]
    nc = _noncode(player)
    if name == "ERASE_ALL":
        for i in nc:
            tape[i] = 0
        for i in range(len(regs)):
            regs[i] = 0
    elif name == "ERASE_REGS":
        for i in range(len(regs)):
            regs[i] = 0
    elif name == "ERASE_TAPE":
        for i in nc:
            tape[i] = 0
    elif name == "SCRAMBLE_LOC":
        idx = list(nc)
        old = [tape[i] for i in idx]
        for i in range(len(idx) - 1, 0, -1):
            j = rng.randbelow(i + 1)
            old[i], old[j] = old[j], old[i]
        for k, i in enumerate(idx):
            tape[i] = old[k]
    elif name == "SCRAMBLE_VAL":
        for i in nc:
            if tape[i] != 0:
                tape[i] = rng.next_u32()
    elif name == "SWAP_TWO":
        nz = [i for i in nc if tape[i] != 0]
        if len(nz) >= 2:
            a = nz[rng.randbelow(len(nz))]
            b = a
            while b == a:
                b = nz[rng.randbelow(len(nz))]
            tape[a], tape[b] = tape[b], tape[a]
    elif name == "HALVE_CAP":
        halve_cap_enforce(player, state)
    elif name == "RESET_IP":
        state["ip"] = 0
    elif name == "TRANSPLANT":
        if donor is None:
            raise ValueError("TRANSPLANT needs a donor state")
        state["tape"][:] = list(donor["tape"])
        state["regs"][:] = list(donor["regs"])
        state["ip"] = donor["ip"]
    else:
        raise ValueError("unknown intervention " + name)


def halve_cap_enforce(player, state: dict) -> None:
    """Zero the upper half of the non-code tape; the evaluator re-applies this after every
    later tick so the region stays frozen (capacity reduced, not merely erased once)."""
    tape = state["tape"]
    glen, n = player.genome_len, player.tape_words
    for i in range(glen + (n - glen) // 2, n):
        tape[i] = 0
