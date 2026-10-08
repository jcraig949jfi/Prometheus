"""FUNCK: the k-generation functional replication test, adopted from adversarial Review B's prototype (scratch
reviewB/adv.py, functional() + child_of(), 2026-10-08) as an ADDITIONAL offline measurement on stored specimens. It does
not replace FUNC (frozen) in any preregistered rule. Changes from the prototype: the world's budget, strict budget
(physics != v1) and chemistry are passed through; the reproduction 'need' comes from the physics.

For each background regime (zero window; fresh random window per generation) the lineage P -> g1 -> ... -> g_k is
executed in isolation; a generation is viable if its window writes meet the physics' need (unwritten child bytes are
the background, as in the 'preserve' physics). herit: from g2 on, the bytes each generation WROTE match the previous
generation's written bytes at >= 90% (shift tolerance +-8). FUNCTIONAL iff chain == k and herit in every regime.
Unlike FUNC it accepts prefix and shifted replicators that work under the physics, and it rejects sterile near-copies."""
from __future__ import annotations

import random

from prometheus.z80atlas import vm

NEED = {"ENDOGENOUS_COPY": 1.0, "ENDOGENOUS_PARTIAL": None, "OVERWRITE": 0.5, "CONSTRUCTIVE": 0.5, "PAIR_EXECUTION": 0.5}


def child_of(tape: bytes, need: int, bg: bytes, cfg, inputs=(1,)):
    L = cfg.L
    mem = bytearray(256); mem[:L] = tape; mem[L:2 * L] = bg
    for k, v in enumerate(inputs):
        mem[vm.IN_BASE + k] = v
    tr = vm.execute(mem, L, 0, cfg.budget, list(inputs), allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
    wr = {a - L for a in tr.writes if L <= a < 2 * L}
    if len(wr) < need:
        return None
    return bytes(mem[L:2 * L]), wr


def functional(tape: bytes, cfg, gens: int = 4, bgs=("zero", "rand"), seed: int = 0) -> dict:
    L = cfg.L
    f = NEED.get(cfg.reproduction, 0.5)
    need = 1 if f is None else int(L * f)
    rng = random.Random(seed); res = {}
    for bgk in bgs:
        cur = bytes(tape[:L]) + bytes(max(0, L - len(tape))); prev_w = None; chain = 0; herit = True; trail = []
        for _ in range(gens):
            bg = bytes(L) if bgk == "zero" else bytes(rng.randrange(256) for _ in range(L))
            r = child_of(cur, need, bg, cfg)
            if r is None:
                break
            ch, wrs = r; chain += 1
            sig = {o: ch[o] for o in wrs}
            if prev_w is not None:
                best = 0.0
                for s in range(-8, 9):
                    m = sum(1 for o, v in sig.items() if prev_w.get(o - s) == v)
                    best = max(best, m / max(1, max(len(sig), len(prev_w))))
                if best < 0.9:
                    herit = False
            prev_w = sig; trail.append(len(wrs)); cur = ch
        res[bgk] = {"chain": chain, "herit": herit and chain == gens, "written_per_gen": trail}
    res["FUNCTIONAL"] = all(res[b]["chain"] == gens and res[b]["herit"] for b in bgs)
    return res
