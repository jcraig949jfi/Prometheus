"""Positive controls for the substrate. The campaign is not calibrated until these pass.

The directive requires proof that the VM executes correctly, that known replicators
replicate and that known task witnesses solve, BEFORE any evolutionary claim. This file
is that gate, and it returns PASS / FAIL / NOT_VERIFIED per check - never a silent skip.
"""
from __future__ import annotations

import json
import random
import sys

import tasks
import z8

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append({"check": name, "outcome": "PASS" if cond else "FAIL", "detail": str(detail)[:300]})
    return cond


def arena(size=1 << 12):
    return bytearray(size)


def run_code(code, base=0, budget=500, inputs=(), size=1 << 12, policy=z8.OWN,
             ops_enabled=0xFF, on_alloc=None, on_birth=None, length=None, rng=None,
             copy_mut_rate=0.0):
    mem = arena(size)
    mem[base:base + len(code)] = code
    ctx = z8.Ctx(mem, base, length if length is not None else len(code), policy=policy,
                 inputs=inputs, on_alloc=on_alloc, on_birth=on_birth, rng=rng,
                 copy_mut_rate=copy_mut_rate)
    pc = z8.run(ctx, base, budget, ops_enabled=ops_enabled)
    return mem, ctx, pc


# ------------------------------------------------------------------ 1. instructions
def test_instructions():
    code, _ = z8.asm("LD A,5\nLD B,3\nADD B\nOUT\nHALT")
    _, ctx, _ = run_code(code)
    check("alu_add", ctx.outputs == [8], ctx.outputs)

    code, _ = z8.asm("LD A,0x0F\nXOR 0x0F\nOUT\nHALT")
    _, ctx, _ = run_code(code)
    check("alu_xor_imm_zero", ctx.outputs == [0], ctx.outputs)

    code, _ = z8.asm("LD A,1\nCP 1\nJRZ hit\nLD A,0xAA\nOUT\nHALT\nhit:\nLD A,0x55\nOUT\nHALT")
    _, ctx, _ = run_code(code)
    check("branch_jrz_taken", ctx.outputs == [0x55], ctx.outputs)

    code, _ = z8.asm("LD A,2\nCP 1\nJRZ hit\nLD A,0xAA\nOUT\nHALT\nhit:\nLD A,0x55\nOUT\nHALT")
    _, ctx, _ = run_code(code)
    check("branch_jrz_nottaken", ctx.outputs == [0xAA], ctx.outputs)

    # memory write through (HL), then read back
    code, _ = z8.asm("LD HL,0x40\nLD A,0x7E\nLD (HL),A\nLD A,0\nLD A,(HL)\nOUT\nHALT")
    mem, ctx, _ = run_code(code, length=0x80)
    check("mem_write_read", ctx.outputs == [0x7E] and mem[0x40] == 0x7E, (ctx.outputs, mem[0x40]))

    # input order and the answer-before-read probe
    code, _ = z8.asm("IN\nOUT\nIN\nHALT")
    _, ctx, _ = run_code(code, inputs=[9, 4])
    check("io_order", ctx.outputs == [9], ctx.outputs)
    check("probe_reads_at_answer", ctx.in_reads_at_first_out == 1, ctx.in_reads_at_first_out)

    # undefined bytes are one-byte NOPs, and the machine stays inside its budget
    mem = arena(256)
    rnd = random.Random(7)
    for i in range(256):
        mem[i] = rnd.randrange(256)
    ctx = z8.Ctx(mem, 0, 256, policy=z8.OWN, rng=rnd)
    z8.run(ctx, 0, 300)
    check("random_bytes_run_without_fault", ctx.ops > 0, ctx.ops)

    # variable-length reframing: inserting a byte changes what later bytes mean
    a, _ = z8.asm("LD A,5\nOUT\nHALT")
    b = b"\x00" + a
    _, c1, _ = run_code(a)
    mem = arena(1 << 12)
    mem[0:len(b)] = b
    c2 = z8.Ctx(mem, 0, len(b))
    z8.run(c2, 0, 100)
    check("frame_shift_is_runnable", c1.outputs == [5] and c2.outputs == [5],
          (c1.outputs, c2.outputs))


# ------------------------------------------------------------------ 2. sandbox
def test_sandbox():
    code, _ = z8.asm("LD HL,0x200\nLD A,0xFF\nLD (HL),A\nHALT")
    mem, ctx, _ = run_code(code, length=0x40, policy=z8.OWN)
    check("own_policy_blocks_outside_write", ctx.writes_blocked == 1 and mem[0x200] == 0,
          (ctx.writes_blocked, mem[0x200]))
    mem, ctx, _ = run_code(code, length=0x40, policy=z8.ARENA)
    check("arena_policy_allows_write", ctx.writes_other == 1 and mem[0x200] == 0xFF,
          (ctx.writes_other, mem[0x200]))


# ------------------------------------------------------------------ 3. replicators
def replicator_self():
    """Instrument: the shortest self-replicator when the world grants SELF+ALLOC+LDIR.

    SELF gives (HL = base, BC = length); ALLOC returns the child base in DE and sets Z on
    success; LDIR copies BC bytes HL -> DE; BIRTH declares the allocation the organism was
    handed. LDIR leaves DE past the child's end, which is why BIRTH is defined against the
    world's pending allocation rather than against DE - see the mock world below and
    world.py: the organism still has to ask, copy and declare, and the bytes the child
    runs are exactly the bytes it wrote.
    """
    code, _ = z8.asm("""
        SELF
        ALLOC
        JRZ go
        HALT
    go:
        LDIR
        SELF
        BIRTH
        HALT
    """)
    return code


def replicator_manual():
    """Instrument: a replicator that never uses LDIR - a byte-at-a-time copy loop.

    This is the control for copy_primitive=BYTEWISE: the same phenotype, more
    instructions, so the campaign can ask whether the primitive's granularity (not the
    task) decides whether replication is reachable.
    """
    code, _ = z8.asm("""
        SELF
        ALLOC
        JRZ go
        HALT
    go:
        SELF
    loop:
        LD A,(HL)
        LD (DE),A
        INC HL
        INC DE
        DEC BC
        LD A,B
        OR C
        JRNZ loop
        SELF
        BIRTH
        HALT
    """)
    return code


class MockWorld:
    """The birth convention, in miniature, exactly as world.py implements it.

    ALLOC hands out a free span and REMEMBERS it as this organism's pending allocation.
    BIRTH declares that span. The world's bookkeeping is 'which span did I hand you',
    nothing more: it never copies bytes, so a child's contents are only ever what the
    organism wrote there. An organism that births without copying gets a child of zeros,
    which is a dead program - and that is the correct outcome, not an error.
    """

    def __init__(self, mem, free_lo, free_hi):
        self.mem = mem
        self.free = free_lo
        self.free_hi = free_hi
        self.pending = None
        self.births = []

    def on_alloc(self, ctx, want):
        want = max(1, want)
        if self.free + want > self.free_hi:
            return None
        b = self.free
        self.free += want
        self.pending = (b, want)
        return b

    def on_birth(self, ctx, dst, cnt, partial):
        if self.pending is None:
            return False
        base, size = self.pending
        n = min(cnt, size) if partial else size
        if n <= 0:
            return False
        self.births.append((base, n, bytes(self.mem[base:base + n])))
        self.pending = None
        return True


def test_replication():
    """A replicator must produce a child whose bytes equal its own, in a mock world."""
    for name, code in (("self_ldir", replicator_self()), ("bytewise", replicator_manual())):
        size = 1 << 12
        mem = arena(size)
        base, n = 0x100, len(code)
        mem[base:base + n] = code
        w = MockWorld(mem, 0x800, 0x1000)
        ctx = z8.Ctx(mem, base, n, policy=z8.FREE, on_alloc=w.on_alloc, on_birth=w.on_birth,
                     free_lo=0x800, free_hi=0x1000)
        z8.run(ctx, base, 4000)
        ok = bool(w.births) and w.births[0][2] == bytes(code)
        check("replicator_%s_copies_itself" % name, ok,
              {"births": len(w.births), "child_len": w.births[0][1] if w.births else 0,
               "exact": (w.births[0][2] == bytes(code)) if w.births else False,
               "ops": ctx.ops, "copy_bytes": ctx.copy_bytes, "len": n})

    # a replicator that never copies produces a dead (zero) child rather than a clone
    code, _ = z8.asm("SELF\nALLOC\nJRZ go\nHALT\ngo:\nSELF\nBIRTH\nHALT")
    mem = arena(1 << 12)
    mem[0x100:0x100 + len(code)] = code
    w = MockWorld(mem, 0x800, 0x1000)
    ctx = z8.Ctx(mem, 0x100, len(code), policy=z8.FREE, on_alloc=w.on_alloc, on_birth=w.on_birth,
                 free_lo=0x800, free_hi=0x1000)
    z8.run(ctx, 0x100, 2000)
    check("birth_without_copy_yields_dead_child",
          bool(w.births) and set(w.births[0][2]) == {0}, w.births[:1])

    # copy mutation actually perturbs the child
    code = replicator_self()
    mem = arena(1 << 12)
    mem[0x100:0x100 + len(code)] = code
    w = MockWorld(mem, 0x800, 0x1000)
    rng = random.Random(3)
    ctx = z8.Ctx(mem, 0x100, len(code), policy=z8.FREE, rng=rng, copy_mut_rate=0.5,
                 on_alloc=w.on_alloc, on_birth=w.on_birth, free_lo=0x800, free_hi=0x1000)
    z8.run(ctx, 0x100, 4000)
    mutated = bool(w.births) and w.births[0][2] != bytes(code)
    check("copy_mutation_perturbs_child", mutated and ctx.copy_errors > 0,
          {"copy_errors": ctx.copy_errors, "differs": mutated})


# ------------------------------------------------------------------ 4. task witnesses
def test_tasks():
    for transform in ("XOR1", "XOR15", "ADD1", "XOR5A"):
        for read_order in tasks.READ_ORDERS:
            spec = tasks.TaskSpec(transform=transform, read_order=read_order, n_episodes=32)
            eps = tasks.episodes(spec, seed=11)
            w, _ = tasks.score(tasks.witness(spec), spec, eps)
            p, ptel = tasks.score(tasks.plateau(spec), spec, eps)
            check("witness_solves_%s_%s" % (transform, read_order), w == 1.0, w)
            if read_order == "ANSWER_BEFORE_READ":
                check("plateau_scores_half_%s" % transform, 0.35 <= p <= 0.65, p)
                check("plateau_answers_before_reading_cue_%s" % transform,
                      ptel["reads_at_answer"] == 1, ptel["reads_at_answer"])
            else:
                check("forced_read_kills_plateau_%s" % transform, p <= 0.05, p)

    # ONE_EDIT: the reader ancestor is exactly one operand byte from the witness
    for transform in ("XOR1", "XOR15", "XOR5A", "ADD1"):
        for read_order in tasks.READ_ORDERS:
            spec = tasks.TaskSpec(transform=transform, read_order=read_order, n_episodes=32)
            d = tasks.one_edit_distance(spec)
            check("one_edit_distance_%s_%s" % (transform, read_order),
                  d["differs"] == 1 and d["from"] == 0 and d["needs"] == tasks.TRANSFORMS[transform][0], d)
            eps = tasks.episodes(spec, seed=13, n=128)
            a, _ = tasks.score(tasks.reader_ancestor(spec), spec, eps)
            # the ancestor answers the base value in both regimes, so it scores exactly
            # the share of regime-0 episodes. Comparing against that share rather than a
            # fixed band keeps this a check on the program, not on the episode draw.
            expect = sum(1 for inp, _e, _b in eps if inp[-1] == 0) / len(eps)
            check("one_edit_ancestor_scores_regime0_share_%s_%s" % (transform, read_order),
                  abs(a - expect) <= 0.06, {"score": a, "regime0_share": expect})

    # held-out scoring uses a disjoint episode stream
    spec = tasks.TaskSpec(transform="XOR15", read_order="FORCED_READ", n_episodes=16)
    c = tasks.competence(tasks.witness(spec), spec, seed=5, held_seed=100005)
    check("witness_generalises_to_heldout", c["comp"] == 1.0 and c["held"] == 1.0, c)


def main():
    test_instructions()
    test_sandbox()
    test_replication()
    test_tasks()
    n_fail = sum(1 for c in CHECKS if c["outcome"] != "PASS")
    print(json.dumps({"checks": len(CHECKS), "failed": n_fail,
                      "failures": [c for c in CHECKS if c["outcome"] != "PASS"]}, indent=1))
    print("SELFTEST", "PASS" if n_fail == 0 else "FAIL")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
