"""Static readout classification of a genome rule (see PLAN.md).
Unroll the program U ticks (S loop-carried; T/EMIT/CHAN/RPORT/RVAL/PAY zero at each tick start, as engine.py
builds regs fresh each tick), forward-taint from inputs, backward-slice the final S0 definition, keep signal ops."""
from __future__ import annotations
import numpy as np
from prometheus.ananke import plants

OPN = {v: k for k, v in plants.OPS.items()}
U = 4


def _srcs(o, d, a, b):
    if o in ("NOP", "SETRULE", "WIMM"):
        return None              # does not define d
    if o == "CONST":
        return []
    if o in ("MOV", "ADDI", "SHR", "RAND"):
        return [a]
    if o == "SEL":
        return [d, a, b]         # d = condition (old value)
    return [a, b]


def classify_rule(ph, body):
    rm = plants.regmap(ph)
    D = ph.state_dim
    NW, NR = ph.n_write(), ph.n_read()
    inputs = {v for k, v in rm.items() if k.startswith("IN") or k.startswith("CNT") or k == "SENSE"}
    comm_in = {v for k, v in rm.items() if k.startswith("IN") or k.startswith("CNT")}
    sense = rm["SENSE"]
    prog = []
    for (op, d, a, b, imm) in np.asarray(body):
        o = OPN[int(op) % 16]
        prog.append((o, int(d) % NW, int(a) % NR, int(b) % NR))
    L = len(prog)
    # forward taint over the unrolled sequence: taint[reg] = set of input kinds {"sense","comm"}
    seq = []
    state = {}                     # reg -> frozenset of kinds
    for u in range(U):
        for r in list(state):
            if r >= D and r < NW:
                state[r] = frozenset()     # non-S write regs are zero at tick start
        for i, (o, d, a, b) in enumerate(prog):
            def k(r):
                if r in comm_in:
                    return frozenset({"comm"})
                if r == sense:
                    return frozenset({"sense"})
                if r >= NW:
                    return frozenset()     # ENERGY / ZERO
                return state.get(r, frozenset())
            ss = _srcs(o, d, a, b)
            pre = {r: k(r) for r in {d, a, b}}
            seq.append((u, i, o, d, a, b, pre))
            if ss is None:
                continue
            state[d] = frozenset().union(*[k(r) for r in ss]) if ss else frozenset()
    # backward slice from the end for S0 (reg 0)
    need = {0}
    sig_ops = []
    for (u, i, o, d, a, b, pre) in reversed(seq):
        if i == L - 1 and u < U - 1:
            # crossing a tick boundary backwards: non-S needs are zero constants at the next tick's start
            need = {r for r in need if r < D or r >= NW}
        if d not in need:
            continue
        ss = _srcs(o, d, a, b)
        if ss is None:
            continue
        need.discard(d)
        need.update(r for r in ss if r < NW)
        tainted = [r for r in ss if pre[r]]
        if tainted:
            sig_ops.append((o, d, a, b, tuple(sorted(set().union(*[pre[r] for r in ss])))
                            , [r for r in ss if pre[r]]))
    kinds = set()
    for s in sig_ops:
        kinds.update(s[4])
    if not sig_ops:
        return {"cls": "NOINPUT", "kinds": [], "ops": []}
    thresh = lin_ok = True
    is_thresh = False
    nonlin = False
    for (o, d, a, b, kk, tl) in sig_ops:
        if o == "GT":
            is_thresh = True
        elif o == "SEL":
            if d in tl:
                is_thresh = True
        elif o in ("MOV", "ADD", "SUB", "ADDI", "SHR"):
            pass
        elif o == "MULQ":
            if a in tl and b in tl:
                nonlin = True
        else:                       # MAX XOR MOD RAND
            nonlin = True
    cls = "THRESH" if is_thresh else ("NONLIN" if nonlin else "LINEAR")
    return {"cls": cls, "kinds": sorted(kinds), "ops": sorted({s[0] for s in sig_ops})}


def classify_genome(ph, g):
    g = np.asarray(g)
    per = [classify_rule(ph, g[r]) for r in range(g.shape[0])]
    cl = sorted({p["cls"] for p in per})
    return {"rules": per, "set": cl, "cls": cl[0] if len(cl) == 1 else "MIXED:" + "+".join(cl)}
