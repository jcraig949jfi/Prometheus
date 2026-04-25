"""prometheus_math.databases — typed wrappers over external math databases.

Submodules:
    lmfdb     — LMFDB Postgres mirror (devmirror.lmfdb.xyz)
    oeis      — OEIS API wrapper (when present)
    arxiv     — arXiv preprint server (when the `arxiv` pip package is present)
    knotinfo  — KnotInfo + LinkInfo census (via `database_knotinfo` pkg)
    zbmath    — zbMATH Open API (mathematical literature, reviews, MSC tags)
    mahler    — Mossinghoff small-Mahler-measure tables (embedded snapshot)
    atlas     — ATLAS of Finite Groups (embedded snapshot; auto-upgrades to GAP)
"""
from __future__ import annotations

from . import oeis  # noqa: F401

try:  # optional, depends on psycopg2 + network
    from . import lmfdb  # noqa: F401
except ImportError:
    pass

try:  # optional, depends on the `arxiv` pip package
    from . import arxiv  # noqa: F401
except ImportError:
    pass

try:  # optional, depends on `database_knotinfo` (pip) or live CSV download
    from . import knotinfo  # noqa: F401
except ImportError:
    pass

try:  # optional, only needs `requests` which is part of the core stack
    from . import zbmath  # noqa: F401
except ImportError:
    pass

try:  # always-available: embedded Mossinghoff snapshot
    from . import mahler  # noqa: F401
except ImportError:
    pass

try:  # always-available: embedded ATLAS-of-Finite-Groups snapshot
    from . import atlas  # noqa: F401
except ImportError:
    pass
