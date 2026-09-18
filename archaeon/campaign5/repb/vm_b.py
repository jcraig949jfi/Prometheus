"""Representation B: the NARROW in-table encoding of the Proteus player (Campaign 5, Phase B).

Same affordance table (25 opcodes, four words per instruction, same registers/tape/persist
semantics) with ONE change: undefined words are undefined.

    OLD (proteus.foundry.vm.Player, total): op = word mod 25; register fields mod n_regs.
    NEW (PlayerB, narrow):                  op valid iff word < 25; a register field valid iff
                                            word < n_regs; anything else is a FAULT.

Addresses computed from register CONTENTS (LD/ST) and jump offsets stay modulo tape_words: those
are values, not encodings, and the directive's boundary is the encoding. Immediates are 32-bit.
Fields an opcode does not read (NOP/HALT/YIELD operands; c for two-register ops) are not
interpreted and therefore cannot fault.

Fault modes (fixed per evaluation, never per program):
    FAIL    the first fault ends the WHOLE evaluation: status "trap"; the caller scores every
            episode 0 (the maximal hard boundary, D5-002 default 2).
    FIZZLE  the faulting instruction is skipped (ip += 4), counted, and execution continues.
            Recovery is COUNTABLE: faults, distinct fault sites, ticks with a fault.

This module never imports the campaign; it is a candidate representation, not Proteus's VM,
which is untouched (D5-002 default 1).
"""
from __future__ import annotations

import time

from proteus.foundry.affordances import N_OPCODES, CATEGORY
from proteus.foundry.vm import validate_manifest, Meter, MASK32

REP_VERSION = "archaeon.repb.narrow.v1"
MODES = ("FAIL", "FIZZLE")

# which of the three operand fields each opcode reads AS A REGISTER INDEX (must be < n_regs)
REG_FIELDS = {
    0: (), 1: (), 2: (),
    3: (1,),                     # LDC a, imm
    4: (1, 2), 5: (1, 2), 6: (1, 2),
    7: (1, 2, 3), 8: (1, 2, 3), 9: (1, 2, 3), 10: (1, 2, 3), 11: (1, 2, 3), 12: (1, 2, 3),
    13: (1, 2),
    14: (1, 2, 3), 15: (1, 2, 3), 16: (1, 2, 3), 17: (1, 2, 3),
    18: (),                      # JMP off (field 2 = offset)
    19: (1,), 20: (1,),          # JZ/JNZ a, off
    21: (1, 2), 22: (1, 2), 23: (1, 2),
    24: (1,),
}


class MeterB(Meter):
    __slots__ = ("faults", "fault_sites", "fault_ticks", "trapped")

    def __init__(self):
        super().__init__()
        self.faults = 0
        self.fault_sites = set()
        self.fault_ticks = 0
        self.trapped = 0

    def as_dict(self, manifest=None) -> dict:
        d = super().as_dict(manifest)
        d.update({"faults": self.faults, "fault_sites": len(self.fault_sites), "fault_ticks": self.fault_ticks, "trapped": self.trapped,
                  "representation": REP_VERSION})
        return d


def instruction_validity(words, n_regs: int) -> str:
    """'ok' | 'opcode' | 'register' for one four-word instruction under the narrow encoding."""
    op = words[0]
    if op >= N_OPCODES:
        return "opcode"
    for f in REG_FIELDS[op]:
        if words[f] >= n_regs:
            return "register"
    return "ok"


def static_validity(manifest: dict) -> dict:
    """Counts over the genome's instructions (no execution, no fitness)."""
    g, nr = manifest["genome"], manifest["n_regs"]
    kinds = {"ok": 0, "opcode": 0, "register": 0}
    first_invalid = None
    for i in range(0, len(g), 4):
        k = instruction_validity(g[i:i + 4], nr)
        kinds[k] += 1
        if k != "ok" and first_invalid is None:
            first_invalid = i // 4
    n = len(g) // 4
    return {"n_instr": n, "valid": kinds["ok"], "invalid": n - kinds["ok"], "invalid_opcode": kinds["opcode"], "invalid_register": kinds["register"],
            "valid_share": round(kinds["ok"] / max(1, n), 4), "first_invalid_instr": first_invalid, "all_valid": kinds["ok"] == n}


class PlayerB:
    """Narrow-encoding interpreter. Same state layout as proteus.foundry.vm.Player."""

    def __init__(self, manifest: dict, mode: str = "FAIL"):
        validate_manifest(manifest)
        if mode not in MODES:
            raise ValueError("mode must be FAIL or FIZZLE")
        self.m = manifest
        self.mode = mode
        self.n_regs = manifest["n_regs"]
        self.tape_words = manifest["tape_words"]
        self.genome = list(manifest["genome"])
        self.genome_len = len(self.genome)
        self.code_writable = manifest["code_writable"]
        self.persist = manifest["persist"]
        self.tick_budget = manifest["tick_budget"]
        self.out_cap = manifest["out_cap"]

    def fresh_state(self) -> dict:
        tape = self.genome + [0] * (self.tape_words - self.genome_len)
        return {"tape": tape, "regs": [0] * self.n_regs, "ip": 0, "ticks": 0}

    def begin_tick(self, state: dict) -> None:
        if state["ticks"] == 0:
            return
        p = self.persist
        if p in ("none", "regs"):
            state["tape"] = self.genome + [0] * (self.tape_words - self.genome_len)
        if p in ("none", "tape"):
            state["regs"] = [0] * self.n_regs

    def run_tick(self, state: dict, inputs: list, n_out: int, rng, meter: MeterB | None = None, budget: int | None = None):
        """Returns (outputs, status); status in {halt, yield, budget, trap}. trap only in FAIL mode."""
        self.begin_tick(state)
        t0 = time.perf_counter(); c0 = time.process_time()
        tape = state["tape"]; regs = state["regs"]; ip = state["ip"]
        n = self.tape_words; nr = self.n_regs; glen = self.genome_len; writable = self.code_writable
        n_in = len(inputs); cursors = [0] * n_in
        outputs = [[] for _ in range(n_out)]; out_cap = self.out_cap
        cap = self.tick_budget if budget is None else min(budget, self.tick_budget)
        m = meter; nops = N_OPCODES; fizzle = self.mode == "FIZZLE"
        status = "budget"; ops = 0
        code_writes = branches = in_reads = out_writes = out_dropped = rnd_draws = faults = 0
        tick_faulted = False
        cat_counts = m.by_category if m is not None else None
        regf = REG_FIELDS

        while ops < cap:
            op = tape[ip]
            a = tape[(ip + 1) % n]; bw = tape[(ip + 2) % n]; cw = tape[(ip + 3) % n]
            ops += 1
            nip = (ip + 4) % n
            # ---- the boundary: undefined words are undefined ----
            bad = op >= nops
            if not bad:
                for f in regf[op]:
                    if (a if f == 1 else bw if f == 2 else cw) >= nr:
                        bad = True; break
            if bad:
                faults += 1; tick_faulted = True
                if m is not None:
                    m.fault_sites.add(ip)
                if fizzle:
                    ip = nip
                    continue
                status = "trap"; ip = 0
                break
            if cat_counts is not None:
                c = CATEGORY[op]; cat_counts[c] = cat_counts.get(c, 0) + 1
            if op == 0:
                pass
            elif op == 1:
                status = "halt"; ip = 0; break
            elif op == 2:
                status = "yield"; ip = nip; break
            elif op == 3:
                regs[a] = bw & MASK32
            elif op == 4:
                regs[a] = regs[bw]
            elif op == 5:
                regs[a] = tape[regs[bw] % n]
            elif op == 6:
                addr = regs[a] % n
                if addr < glen and not writable:
                    pass
                else:
                    if addr < glen:
                        code_writes += 1
                    tape[addr] = regs[bw]
            elif op == 7:
                regs[a] = (regs[bw] + regs[cw]) & MASK32
            elif op == 8:
                regs[a] = (regs[bw] - regs[cw]) & MASK32
            elif op == 9:
                regs[a] = (regs[bw] * regs[cw]) & MASK32
            elif op == 10:
                regs[a] = regs[bw] & regs[cw]
            elif op == 11:
                regs[a] = regs[bw] | regs[cw]
            elif op == 12:
                regs[a] = regs[bw] ^ regs[cw]
            elif op == 13:
                regs[a] = (~regs[bw]) & MASK32
            elif op == 14:
                regs[a] = (regs[bw] << (regs[cw] % 32)) & MASK32
            elif op == 15:
                regs[a] = regs[bw] >> (regs[cw] % 32)
            elif op == 16:
                regs[a] = 1 if regs[bw] == regs[cw] else 0
            elif op == 17:
                regs[a] = 1 if regs[bw] < regs[cw] else 0
            elif op == 18:
                off = bw - (1 << 32) if bw >= (1 << 31) else bw
                nip = (ip + 4 * off) % n; branches += 1
            elif op == 19:
                if regs[a] == 0:
                    off = bw - (1 << 32) if bw >= (1 << 31) else bw
                    nip = (ip + 4 * off) % n; branches += 1
            elif op == 20:
                if regs[a] != 0:
                    off = bw - (1 << 32) if bw >= (1 << 31) else bw
                    nip = (ip + 4 * off) % n; branches += 1
            elif op == 21:
                if n_in:
                    ch = regs[bw] % n_in; cur = cursors[ch]; src = inputs[ch]
                    if cur < len(src):
                        regs[a] = src[cur] & MASK32; cursors[ch] = cur + 1; in_reads += 1
                    else:
                        regs[a] = 0
                else:
                    regs[a] = 0
            elif op == 22:
                if n_in:
                    ch = regs[bw] % n_in; regs[a] = len(inputs[ch]) - cursors[ch]
                else:
                    regs[a] = 0
            elif op == 23:
                if n_out:
                    ch = regs[bw] % n_out; dst = outputs[ch]
                    if len(dst) < out_cap:
                        dst.append(regs[a]); out_writes += 1
                    else:
                        out_dropped += 1
            elif op == 24:
                regs[a] = rng.next_u32(); rnd_draws += 1
            ip = nip

        if status == "budget":
            ip = 0
        state["ip"] = ip; state["ticks"] += 1
        if m is not None:
            m.ops += ops; m.code_region_writes += code_writes; m.branches_taken += branches
            m.in_reads += in_reads; m.out_writes += out_writes; m.out_dropped += out_dropped; m.rnd_draws += rnd_draws
            m.wall_s += time.perf_counter() - t0; m.cpu_s += time.process_time() - c0; m.ticks += 1
            m.faults += faults
            if tick_faulted:
                m.fault_ticks += 1
            if status == "budget":
                m.budget_exhausted_ticks += 1
            if status == "trap":
                m.trapped += 1
        return outputs, status
