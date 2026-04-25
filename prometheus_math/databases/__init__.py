"""prometheus_math.databases — typed wrappers over external math databases.

Submodules:
    lmfdb  — LMFDB Postgres mirror (devmirror.lmfdb.xyz)
    oeis   — OEIS API wrapper (when present)
"""
from __future__ import annotations

from . import oeis  # noqa: F401

try:  # optional, depends on psycopg2 + network
    from . import lmfdb  # noqa: F401
except ImportError:
    pass
