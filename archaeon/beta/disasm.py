"""Disassembler + reachability trace for Proteus player genomes (Archaeon Beta instrument).

disasm(manifest) lists each 4-word instruction as mnemonic + operands (registers mod n_regs, jump targets as absolute
instruction indices). executed(manifest, episodes) runs the player and counts how often each instruction index is
executed, so a listing can be cut down to the code that actually runs (B02 showed most evolved code is silent).
"""
from __future__ import annotations

from collections import Counter

from proteus.foundry.prng import SplitMix64, seed_from


NAMES = ["NOP", "HALT", "YIELD", "LDC", "MOV", "LD", "ST", "ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOT", "SHL",
         "SHR", "EQ", "LT", "JMP", "JZ", "JNZ", "IN", "INQ", "OUT", "RND/SEL"]


def _off(w):
    return w - (1 << 32) if w >= (1 << 31) else w


def disasm(m, only=None):
    g, nr = m["genome"], m["n_regs"]
    lines = []
    n = len(g) // 4
    for i in range(n):
        if only is not None and i not in only:
            continue
        op, a, b, c = g[4 * i] % 25, g[4 * i + 1] % nr, g[4 * i + 2], g[4 * i + 3]
        nm = NAMES[op]
        if op in (0, 1, 2):
            s = nm
        elif op == 3:
            s = "LDC r%d, %d" % (a, b)
        elif op in (4, 13):
            s = "%s r%d, r%d" % (nm, a, b % nr)
        elif op == 5:
            s = "LD r%d, [r%d]" % (a, b % nr)
        elif op == 6:
            s = "ST [r%d], r%d" % (a, b % nr)
        elif op == 18:
            s = "JMP -> %d" % ((i + _off(b)) % (m["tape_words"] // 4))
        elif op in (19, 20):
            s = "%s r%d -> %d" % (nm, a, (i + _off(b)) % (m["tape_words"] // 4))
        elif op in (21, 22):
            s = "%s r%d, ch r%d" % (nm, a, b % nr)
        elif op == 23:
            s = "OUT r%d, ch r%d" % (a, b % nr)
        else:
            s = "%s r%d, r%d, r%d" % (nm, a, b % nr, c % nr)
        lines.append("%3d  %s" % (i, s))
    return "\n".join(lines)


def _tracer(patch=None):
    """patch: optional callable(src) -> src applied before the trace hook (variant VMs, e.g. b13 queue VM)."""
    import inspect, types
    import proteus.foundry.vm as stockvm
    src = inspect.getsource(stockvm)
    if patch is not None:
        src = patch(src)
    hook = "        while ops < cap:\n"
    assert src.count(hook) == 1
    src = src.replace(hook, hook + "            _TRACE.append(ip)\n")
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_tracevm")
    mod.__dict__["_TRACE"] = []
    exec(compile(src, "archaeon_beta_tracevm", "exec"), mod.__dict__)
    return mod


def executed(m, episodes, patch=None):
    """Instruction-index execution counts over the episodes, from a tracing copy of the stock VM (one added line)."""
    T = _tracer(patch)
    p = T.Player(m)
    for ei, ep in enumerate(episodes):
        st = p.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", 7, ei))
        for words in ep.ticks:
            p.run_tick(st, [words], 1, rng)
    return Counter(ip // 4 for ip in T._TRACE)
