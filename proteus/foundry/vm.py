"""The player runtime: a bounded tape machine interpreting a manifest. Genomes are DATA.

A player is (manifest, state). The manifest is immutable and content-addressed; the state is
the tape, the registers and the instruction pointer, and is what persists across ticks according
to the manifest's persist policy and across encounters according to the lineage's
state-inheritance policy.

Single address space: the genome is copied to the front of the tape and executed in place. If
`code_writable` is true, ST may overwrite the genome region and the program can rewrite itself;
if false, writes into that region are ignored. Whether self-modification is a good idea is not
this module's business -- it is an axis the population varies on.

Nothing in this module carries a string into the player. Channels are lists of 32-bit
integers, addressed by integer index. The runtime does not know what any channel means.
"""
from __future__ import annotations

import time

from .affordances import N_OPCODES, STORAGE_BOUNDS, CATEGORY
from .prng import SplitMix64

MASK32 = 0xFFFFFFFF
PERSIST_POLICIES = ("none", "regs", "tape", "all")
SCHEMA = "proteus.player_manifest.v0"


class ManifestError(ValueError):
    """Fail closed: a manifest that violates the published bounds is not a player."""


def validate_manifest(m: dict) -> None:
    b = STORAGE_BOUNDS
    if not isinstance(m, dict):
        raise ManifestError("manifest must be a dict")
    required = {"schema_version", "n_regs", "tape_words", "genome", "code_writable", "persist",
                "tick_budget", "out_cap"}
    keys = set(m.keys())
    if keys != required:
        raise ManifestError(f"manifest keys must be exactly {sorted(required)}; got {sorted(keys)}")
    if m["schema_version"] != SCHEMA:
        raise ManifestError("schema_version mismatch")
    for k in ("n_regs", "tape_words", "tick_budget", "out_cap"):
        v = m[k]
        if not isinstance(v, int) or isinstance(v, bool):
            raise ManifestError(f"{k} must be int")
        lo, hi = b[k]["min"], b[k]["max"]
        if not lo <= v <= hi:
            raise ManifestError(f"{k}={v} outside [{lo},{hi}]")
    if m["tape_words"] % 4 != 0:
        raise ManifestError("tape_words must be a multiple of 4")
    g = m["genome"]
    if not isinstance(g, list):
        raise ManifestError("genome must be a list of words")
    if not b["genome_words"]["min"] <= len(g) <= b["genome_words"]["max"]:
        raise ManifestError(f"genome length {len(g)} outside bounds")
    if len(g) % 4 != 0:
        raise ManifestError("genome length must be a multiple of 4")
    if len(g) > m["tape_words"]:
        raise ManifestError("genome longer than tape")
    for w in g:
        if not isinstance(w, int) or isinstance(w, bool) or not 0 <= w <= MASK32:
            raise ManifestError("genome words must be integers in [0, 2^32)")
    if not isinstance(m["code_writable"], bool):
        raise ManifestError("code_writable must be bool")
    if m["persist"] not in PERSIST_POLICIES:
        raise ManifestError("persist policy unknown")


class Meter:
    """Resource vector for one tick or accumulated over an encounter. No field named fitness."""
    __slots__ = ("ops", "by_category", "code_region_writes", "branches_taken", "in_reads",
                 "out_writes", "out_dropped", "rnd_draws", "wall_s", "cpu_s", "ticks",
                 "budget_exhausted_ticks")

    def __init__(self):
        self.ops = 0
        self.by_category = {}
        self.code_region_writes = 0
        self.branches_taken = 0
        self.in_reads = 0
        self.out_writes = 0
        self.out_dropped = 0
        self.rnd_draws = 0
        self.wall_s = 0.0
        self.cpu_s = 0.0
        self.ticks = 0
        self.budget_exhausted_ticks = 0

    def as_dict(self, manifest: dict | None = None) -> dict:
        d = {
            "ops": self.ops,
            "ops_by_category": dict(sorted(self.by_category.items())),
            "code_region_writes": self.code_region_writes,
            "branches_taken": self.branches_taken,
            "in_reads": self.in_reads,
            "out_writes": self.out_writes,
            "out_dropped": self.out_dropped,
            "rnd_draws": self.rnd_draws,
            "wall_s": self.wall_s,
            "cpu_s": self.cpu_s,
            "gpu": "unavailable",
            "ticks": self.ticks,
            "budget_exhausted_ticks": self.budget_exhausted_ticks,
            # Declared PROXIES (brief S9 asks for search and adaptation expenditure; in a bytecode
            # organism neither is a separable quantity, so the closest mechanical counts are
            # reported under their mechanical names and the mapping is declared, not assumed).
            "proxy_search_expenditure": self.branches_taken,
            "proxy_adaptation_expenditure": self.code_region_writes,
        }
        if manifest is not None:
            p = manifest["persist"]
            persistent = (manifest["tape_words"] if p in ("tape", "all") else 0) + \
                         (manifest["n_regs"] if p in ("regs", "all") else 0)
            d["footprint_words"] = manifest["tape_words"] + manifest["n_regs"]
            d["persistent_state_words"] = persistent
        return d


class Player:
    """Interpreter bound to one manifest. State is passed in and mutated in place."""

    def __init__(self, manifest: dict):
        validate_manifest(manifest)
        self.m = manifest
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
        """Apply the persist policy at the boundary. The first tick of a fresh state is a no-op."""
        if state["ticks"] == 0:
            return
        p = self.persist
        if p in ("none", "regs"):
            state["tape"] = self.genome + [0] * (self.tape_words - self.genome_len)
        if p in ("none", "tape"):
            state["regs"] = [0] * self.n_regs

    def run_tick(self, state: dict, inputs: list, n_out: int, rng: SplitMix64,
                 meter: Meter | None = None, budget: int | None = None):
        """One tick. Returns (outputs, status). status in {halt, yield, budget}.

        inputs: list of channels, each a list of 32-bit ints; read cursors are tick-scoped.
        n_out:  number of output channels this tick.
        rng:    the externally supplied random stream (the caller seeds it; the player cannot).
        budget: op cap for this tick; defaults to the manifest's tick_budget; never exceeds it.
        """
        self.begin_tick(state)
        t0 = time.perf_counter()
        c0 = time.process_time()
        tape = state["tape"]
        regs = state["regs"]
        ip = state["ip"]
        n = self.tape_words
        nr = self.n_regs
        glen = self.genome_len
        writable = self.code_writable
        n_in = len(inputs)
        cursors = [0] * n_in
        outputs = [[] for _ in range(n_out)]
        out_cap = self.out_cap
        cap = self.tick_budget if budget is None else min(budget, self.tick_budget)
        m = meter
        nops = N_OPCODES
        status = "budget"
        ops = 0
        code_writes = branches = in_reads = out_writes = out_dropped = rnd_draws = 0
        cat_counts = m.by_category if m is not None else None

        while ops < cap:
            op = tape[ip] % nops
            a = tape[(ip + 1) % n] % nr
            bw = tape[(ip + 2) % n]
            cw = tape[(ip + 3) % n]
            ops += 1
            if cat_counts is not None:
                c = CATEGORY[op]
                cat_counts[c] = cat_counts.get(c, 0) + 1
            nip = (ip + 4) % n
            if op == 0:
                pass
            elif op == 1:
                status = "halt"
                ip = 0
                break
            elif op == 2:
                status = "yield"
                ip = nip
                break
            elif op == 3:
                regs[a] = bw & MASK32
            elif op == 4:
                regs[a] = regs[bw % nr]
            elif op == 5:
                regs[a] = tape[regs[bw % nr] % n]
            elif op == 6:
                addr = regs[a] % n
                if addr < glen and not writable:
                    pass
                else:
                    if addr < glen:
                        code_writes += 1
                    tape[addr] = regs[bw % nr]
            elif op == 7:
                regs[a] = (regs[bw % nr] + regs[cw % nr]) & MASK32
            elif op == 8:
                regs[a] = (regs[bw % nr] - regs[cw % nr]) & MASK32
            elif op == 9:
                regs[a] = (regs[bw % nr] * regs[cw % nr]) & MASK32
            elif op == 10:
                regs[a] = regs[bw % nr] & regs[cw % nr]
            elif op == 11:
                regs[a] = regs[bw % nr] | regs[cw % nr]
            elif op == 12:
                regs[a] = regs[bw % nr] ^ regs[cw % nr]
            elif op == 13:
                regs[a] = (~regs[bw % nr]) & MASK32
            elif op == 14:
                regs[a] = (regs[bw % nr] << (regs[cw % nr] % 32)) & MASK32
            elif op == 15:
                regs[a] = regs[bw % nr] >> (regs[cw % nr] % 32)
            elif op == 16:
                regs[a] = 1 if regs[bw % nr] == regs[cw % nr] else 0
            elif op == 17:
                regs[a] = 1 if regs[bw % nr] < regs[cw % nr] else 0
            elif op == 18:
                off = bw - (1 << 32) if bw >= (1 << 31) else bw
                nip = (ip + 4 * off) % n
                branches += 1
            elif op == 19:
                if regs[a] == 0:
                    off = bw - (1 << 32) if bw >= (1 << 31) else bw
                    nip = (ip + 4 * off) % n
                    branches += 1
            elif op == 20:
                if regs[a] != 0:
                    off = bw - (1 << 32) if bw >= (1 << 31) else bw
                    nip = (ip + 4 * off) % n
                    branches += 1
            elif op == 21:
                if n_in:
                    ch = regs[bw % nr] % n_in
                    cur = cursors[ch]
                    src = inputs[ch]
                    if cur < len(src):
                        regs[a] = src[cur] & MASK32
                        cursors[ch] = cur + 1
                        in_reads += 1
                    else:
                        regs[a] = 0
                else:
                    regs[a] = 0
            elif op == 22:
                if n_in:
                    ch = regs[bw % nr] % n_in
                    regs[a] = len(inputs[ch]) - cursors[ch]
                else:
                    regs[a] = 0
            elif op == 23:
                if n_out:
                    ch = regs[bw % nr] % n_out
                    dst = outputs[ch]
                    if len(dst) < out_cap:
                        dst.append(regs[a])
                        out_writes += 1
                    else:
                        out_dropped += 1
            elif op == 24:
                regs[a] = rng.next_u32()
                rnd_draws += 1
            ip = nip

        if status == "budget":
            ip = 0
        state["ip"] = ip
        state["ticks"] += 1
        if m is not None:
            m.ops += ops
            m.code_region_writes += code_writes
            m.branches_taken += branches
            m.in_reads += in_reads
            m.out_writes += out_writes
            m.out_dropped += out_dropped
            m.rnd_draws += rnd_draws
            m.wall_s += time.perf_counter() - t0
            m.cpu_s += time.process_time() - c0
            m.ticks += 1
            if status == "budget":
                m.budget_exhausted_ticks += 1
        return outputs, status
