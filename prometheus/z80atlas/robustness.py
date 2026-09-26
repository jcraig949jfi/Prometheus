"""Mutational robustness of a competent self-copier (multi-day campaign, Q2 protection metric; Bellerophon 2026-09-26).

Replaces the coupling campaign's r_cc retention measure, which sat at its ceiling (~0.999) because whole-window
copiers copy faithfully (COUPLING_FAILURE_LEDGER F6/F7). Robustness asks instead: when a copy error DOES hit the tape,
how often does the damaged tape keep its computation, its copying, or both?

    robustness(tape, cfg, task, n, seed) samples n single-byte substitutions (position uniform over the L window, new
    byte uniform over the 255 values different from the old one; random.Random(seed)) and scores each mutant ALONE:
      task    the mutant answers the configured task's fixed panel exactly (adjudication.verify_tape)
      copy    the mutant self-copies (adjudication.repro_descriptor self_copy)
      joint   both
    It returns the three fractions and the per-position neutral counts. Eligibility (2026-09-26 pilot revision, before
    any freeze): the tape must itself be COMPETENT (task mode) -- the primary Q2 metric is `task`, the fraction of
    single-byte mutants that stay exactly competent. `joint` is reported always and is meaningful only when base_copy is
    True: lineage-level self-replicators often fail the isolated self_copy test (they copy with help from the shared
    window), so requiring both traits made most dominant competent tapes ineligible in the smoke pilot.
    copy_only=True scores the copy trait alone (task None, joint = copy AND not-scored-task = 0 is NOT reported: joint
    is None) and needs only a self-copying founder -- the OFF-arm control for general robustness drift.

Pure measurement: a deterministic function of (tape, cfg, task, n, seed); it never feeds back into a world.
"""
from __future__ import annotations

import random
from typing import Dict, Optional

from prometheus.z80atlas import adjudication as A
from prometheus.z80atlas.tasks import Task


def robustness(tape: bytes, cfg, task: Optional[Task] = None, n: int = 512, seed: int = 0, copy_only: bool = False) -> Dict:
    task = task or Task(cfg.task)
    L = cfg.L
    t = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    base_task = bool(A.verify_tape(t, cfg, task)["exact"])
    base_copy = bool(A.repro_descriptor(t, cfg, task)["self_copy"])
    if not (base_copy if copy_only else base_task):
        return {"eligible": False, "base_task": base_task, "base_copy": base_copy}
    rng = random.Random(seed)
    k_task = k_copy = k_joint = 0
    pos_n = [0] * L; pos_joint = [0] * L
    for _ in range(n):
        p = rng.randrange(L)
        v = rng.randrange(255)
        v = v if v < t[p] else v + 1                     # uniform over the 255 values != t[p]
        m = bytearray(t); m[p] = v; m = bytes(m)
        ok_t = False if copy_only else bool(A.verify_tape(m, cfg, task)["exact"])
        ok_c = bool(A.repro_descriptor(m, cfg, task)["self_copy"])
        k_task += ok_t; k_copy += ok_c; k_joint += ok_t and ok_c
        pos_n[p] += 1; pos_joint[p] += ok_c if copy_only else (ok_t and ok_c)      # copy_only: a position is fragile if no sampled mutant there still copies
    return {"eligible": True, "copy_only": copy_only, "base_task": base_task, "base_copy": base_copy, "n": n, "seed": seed, "task": None if copy_only else k_task / n, "copy": k_copy / n, "joint": None if copy_only else k_joint / n,
            "fragile_positions": sum(1 for i in range(L) if pos_n[i] and pos_joint[i] == 0),
            "sampled_positions": sum(1 for i in range(L) if pos_n[i])}
