"""Shared PARI stack-handling utility for all cypari-backed tools.

Importing this module sets a 1GB default PARI stack and provides a
`safe_call` that auto-doubles allocation up to 4GB on stack overflow.

Usage:
    from ._pari_util import pari, safe_call, set_stack_mb

    result = safe_call(pari.bnrclassfield, bnr, 0, 2)

This replaces the scattered `_pari.allocatemem(200_000_000)` / 1GB calls in
individual tool files. Centralization avoids divergent defaults and makes
"raise stack for this workload" uniform across the arsenal.
"""
import cypari

pari = cypari.pari

# Default: 1GB. bnrclassfield + iterated bnfinit + ellrank all benefit.
_DEFAULT_STACK_BYTES = 1_000_000_000
_MAX_STACK_BYTES = 4_000_000_000
pari.allocatemem(_DEFAULT_STACK_BYTES)


def set_stack_mb(mb: int) -> None:
    """Set PARI stack to `mb` megabytes (caller opt-in override)."""
    pari.allocatemem(int(mb) * 1_000_000)


def safe_call(fn, *args, max_retries: int = 3, **kwargs):
    """Run a PARI operation; double stack and retry on overflow.

    Raises the last PariError if retries are exhausted or the allocation
    caps at _MAX_STACK_BYTES.
    """
    last_err = None
    for _ in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except cypari._pari.PariError as e:
            if 'stack overflows' not in str(e):
                raise
            last_err = e
            current = pari.stacksize()
            new_size = min(2 * current, _MAX_STACK_BYTES)
            if new_size <= current:
                break
            pari.allocatemem(new_size)
    raise last_err if last_err is not None else RuntimeError("unknown PARI failure")
