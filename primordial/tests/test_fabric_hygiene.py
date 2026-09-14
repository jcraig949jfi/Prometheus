"""Lane A fabric hygiene: regressions measured in PROFILE_ROUND1_2026-09-14.md.

1. On this host a Redis connect to "localhost" costs 10.0 s against 15 ms on
   127.0.0.1, so no primordial code may construct a client with the default
   host or name localhost.
2. Statically decorated numba kernels must cache to disk: a fresh process
   paid 6.2 s of JIT for the B6 kernel without cache=True and 0.32 s with it.
   Kernels compiled at runtime for both parallel=True and parallel=False
   (genomes._kernel, tt_policy._nb) are deliberately NOT cached: one Python
   function compiled under two flag sets could collide in the on-disk cache.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SELF = pathlib.Path(__file__).resolve()


def _py_files():
    for p in ROOT.rglob("*.py"):
        if "__pycache__" in p.parts or p.resolve() == SELF:
            continue
        yield p


def test_no_default_host_or_localhost_redis_clients():
    bad = []
    pat = re.compile(r"Redis\((port=|\))|StrictRedis\((port=|\))|localhost")
    for p in _py_files():
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pat.search(line):
                bad.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not bad, "use host='127.0.0.1' (localhost connect = 10 s here):\n" + "\n".join(bad)


def test_static_njit_decorators_cache_to_disk():
    bad = []
    pat = re.compile(r"^\s*@(?:numba\.|_nb\.)?njit\((?P<args>[^)]*)\)")
    for p in _py_files():
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = pat.match(line)
            if m and "cache=True" not in m.group("args"):
                bad.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not bad, "add cache=True (JIT 6.2 s -> 0.32 s per process):\n" + "\n".join(bad)
