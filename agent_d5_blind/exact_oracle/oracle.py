"""Exact correctness oracle. A candidate solves a task iff it matches the
target on EVERY domain point (exhaustive; domains are 4-64 points).
Partial credit (diagnostics only): exact-match count. Spec: PREREG-TASKS.md."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
from rm_vm import run


def solves(prog, task):
    return all(run(prog, inp)[0] == out for inp, out in task['table'])


def match_count(prog, task):
    return sum(1 for inp, out in task['table'] if run(prog, inp)[0] == out)


def mismatch_capped(prog, task, cap):
    """Mismatch count early-stopped past cap (ordering-preserving; for
    navigator selection only, never for correctness)."""
    d = 0
    for inp, out in task['table']:
        if run(prog, inp)[0] != out:
            d += 1
            if d > cap:
                return cap + 1
    return d


def bit_mismatch_capped(prog, task, cap):
    """Bitwise Hamming distance between candidate and target outputs, summed
    over the FULL domain, early-stopped past cap. Deterministic partial credit
    (constitution section 23) used as the NAVIGATION objective for all arms;
    0 iff the exact oracle passes. Correctness still uses solves()."""
    d = 0
    for inp, out in task['table']:
        d += bin(run(prog, inp)[0] ^ out).count('1')
        if d > cap:
            return cap + 1
    return d
