"""Job functions for the supervise failure-injection tests (must be importable by spawned workers)."""
import os
import time
from pathlib import Path


def ok(j):
    return {"i": j["i"], "sq": j["i"] ** 2}


def raises_on_odd(j):
    if j["i"] % 2:
        raise ValueError(f"injected failure {j['i']}")
    return {"i": j["i"]}


def dies_on_3(j):
    if j["i"] == 3:
        os._exit(17)                       # hard worker death (segfault / OOM-kill stand-in)
    return {"i": j["i"]}


def hangs_once(j):
    """Job 2 hangs forever on the first attempt (marker file absent), succeeds after a restart."""
    m = Path(j["marker"])
    if j["i"] == 2 and not m.exists():
        m.write_text("hung once")
        while True:
            time.sleep(1)
    return {"i": j["i"]}


def hangs_always(j):
    if j["i"] == 2:
        while True:
            time.sleep(1)
    return {"i": j["i"]}
