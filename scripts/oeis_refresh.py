#!/usr/bin/env python
"""Refresh the OEIS local mirror; report sequence delta.

Exit codes:
  0 — refresh attempted (regardless of whether sequences changed); CI
       continues even if delta == 0.
  2 — download failed (no mirror on disk after the call).

CI usage:
    python scripts/oeis_refresh.py            # respects PROMETHEUS_DATA_DIR
    python scripts/oeis_refresh.py --force    # re-download even if present

The script prints (in order, one per line):
    SEQUENCES_PREV=<int>
    SEQUENCES_CUR=<int>
    DELTA=<int>          # CUR - PREV (signed)
    REFRESHED_AT=<iso>
plus a human-readable summary line to stderr.
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="re-download even if files exist")
    args = parser.parse_args(argv)

    # Imported here so --help works without requiring the dependency.
    from prometheus_math.databases import oeis

    prev = oeis.mirror_metadata()
    prev_count = int(prev.get("sequences", 0))

    result = oeis.update_mirror(force=args.force)
    if "error" in result:
        print(f"oeis_refresh: download failed: {result['error']}",
              file=sys.stderr)
        # Still emit the keys so the workflow's parser doesn't choke.
        cur = oeis.mirror_metadata()
        print(f"SEQUENCES_PREV={prev_count}")
        print(f"SEQUENCES_CUR={cur.get('sequences', 0)}")
        print(f"DELTA={cur.get('sequences', 0) - prev_count}")
        print(f"REFRESHED_AT={cur.get('last_refresh_iso') or ''}")
        return 2

    cur = oeis.mirror_metadata()
    cur_count = int(cur.get("sequences", 0))
    delta = cur_count - prev_count

    print(f"SEQUENCES_PREV={prev_count}")
    print(f"SEQUENCES_CUR={cur_count}")
    print(f"DELTA={delta}")
    print(f"REFRESHED_AT={cur.get('last_refresh_iso') or ''}")
    print(f"oeis_refresh: prev={prev_count} cur={cur_count} delta={delta:+d}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
