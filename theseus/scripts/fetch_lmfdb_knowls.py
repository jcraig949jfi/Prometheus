"""Fetch LMFDB knowledge nodes into the E4 cache.

LMFDB stores its wiki-style knowledge nodes (descriptions of mathematical
objects, conjectures, theorems) in the kwl_knowls table on the public
Postgres mirror. This script pulls them all into a local JSONL cache so
E4 can mine claim-shaped sentences without network calls.

Run offline before E4 fires:
    python -m theseus.scripts.fetch_lmfdb_knowls

Appends to theseus/cache/lmfdb/knowls.jsonl (one record per line):
    {"id", "title", "content", "category", "authors", "last_saved"}
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

from theseus.config import THESEUS_ROOT


CACHE_DIR = THESEUS_ROOT / "cache" / "lmfdb"
CACHE_PATH = CACHE_DIR / "knowls.jsonl"


def _existing_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    out: Set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kid = rec.get("id")
            if kid:
                out.add(kid)
    return out


def fetch_and_append(cache_path: Path = CACHE_PATH) -> int:
    """Pull knowls from the LMFDB postgres mirror; append novel ones."""
    from prometheus_math.databases import lmfdb

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _existing_ids(cache_path)

    appended = 0
    with lmfdb.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content, cat, authors, last_saved
                FROM kwl_knowls
                WHERE status = 1 AND content IS NOT NULL AND content <> ''
                """
            )
            rows = cur.fetchall()
            with cache_path.open("a", encoding="utf-8") as f:
                for kid, title, content, cat, authors, last_saved in rows:
                    if kid in existing:
                        continue
                    rec = {
                        "id": str(kid),
                        "title": title or "",
                        "content": content or "",
                        "category": cat or "",
                        "authors": list(authors) if authors else [],
                        "last_saved": (
                            last_saved.isoformat() if last_saved else None
                        ),
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
                    existing.add(kid)
                    appended += 1
    return appended


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.fetch_lmfdb_knowls")
    p.add_argument("--cache-path", type=Path, default=CACHE_PATH)
    args = p.parse_args()

    try:
        n = fetch_and_append(cache_path=args.cache_path)
    except Exception as e:
        print(f"[fetch_lmfdb_knowls] failed: {e}", file=sys.stderr)
        return 1
    print(f"[fetch_lmfdb_knowls] appended {n} knowls -> {args.cache_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
