#!/usr/bin/env python
"""Database-freshness CLI thin entrypoint.

Probes every prometheus_math.databases.* wrapper, compares upstream
modification time/etag to the local cache age, and emits a freshness
report (markdown by default).  Used by `.github/workflows/db-freshness.yml`
and runnable locally.

Examples:
    python scripts/db_freshness.py --report-only
    python scripts/db_freshness.py --dry-run
    python scripts/db_freshness.py --refresh-stale --source oeis
"""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from prometheus_math.databases.freshness import cli
    return cli(argv)


if __name__ == "__main__":
    sys.exit(main())
