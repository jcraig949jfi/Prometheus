"""Mutational robustness of a competent self-copier (multi-day campaign, Q2 protection metric; Bellerophon 2026-09-26).

Replaces the coupling campaign's r_cc retention measure, which sat at its ceiling (~0.999) because whole-window
copiers copy faithfully (COUPLING_FAILURE_LEDGER F6/F7). Robustness asks instead: when a copy error DOES hit the tape,
how often does the damaged tape keep its computation, its copying, or both?

    robustness(tape, cfg, task, n, seed) samples n single-byte substitutions (position uniform over the L window, new
    byte uniform over the 255 values different from the old one; random.Random(seed)) and scores each mutant ALONE:
      task    the mutant answers the configured task's fixed panel exactly (adjudication.verify_tape)
      copy    the mutant self-copies (adjudication.repro_descriptor self_copy)
      joint   both
    It returns the three fractions and the per-position neutral counts. The founder must itself be competent and a
    self-copier; otherwise the result is {"eligible": False} (robustness of a trait the tape lacks is undefined).

Pure measurement: a deterministic function of (tape, cfg, task, n, seed); it never feeds back into a world.
"""
from __future__ import annotations

import random
from typing import Dict, Optional

from prometheus.z80atlas import adjudication as A
from prometheus.z80atlas.tasks import Task


def robustness(tape: bytes, cfg, task: Optional[Task] = None, n: int = 512, seed: int = 0) -> Dict:
    task = task or Task(cfg.task)
    L = cfg.L
    t = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    base_task = bool(A.verify_tape(t, cfg, task)["exact"])
    base_copy = bool(A.repro_descriptor(t, cfg, task)["self_copy"])
    if not (base_task and base_copy):
        return {"eligible": False, "base_task": base_task, "base_copy": base_copy}
    rng = random.Random(seed)
    k_task = k_copy = k_joint = 0
    pos_n = [0] * L; pos_joint = [0] * L
    for _ in range(n):
        p = rng.randrange(L)
        v = rng.randrange(255)
        v = v if v < t[p] else v + 1                     # uniform over the 255 values != t[p]
        m = bytearray(t); m[p] = v; m = bytes(m)
        ok_t = bool(A.verify_tape(m, cfg, task)["exact"])
        ok_c = bool(A.repro_descriptor(m, cfg, task)["self_copy"])
        k_task += ok_t; k_copy += ok_c; k_joint += ok_t and ok_c
        pos_n[p] += 1; pos_joint[p] += ok_t and ok_c
    return {"eligible": True, "n": n, "seed": seed, "task": k_task / n, "copy": k_copy / n, "joint": k_joint / n,
            "fragile_positions": sum(1 for i in range(L) if pos_n[i] and pos_joint[i] == 0),
            "sampled_positions": sum(1 for i in range(L) if pos_n[i])}
