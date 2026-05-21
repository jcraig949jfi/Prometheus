"""Fetch arxiv math abstracts into the E2 cache.

Run offline before E2 fires:
    python -m theseus.scripts.fetch_arxiv_abstracts --max-results 500

Appends to theseus/cache/arxiv/abstracts.jsonl (one record per line):
    {"arxiv_id", "title", "abstract", "categories", "published"}

Polite to arxiv's API: uses the `arxiv` package's default 3s delay.
Categories pulled: math.* + math-ph + cs.LG (for ML-meets-math claims).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Set

import arxiv

from theseus.config import THESEUS_ROOT


CACHE_DIR = THESEUS_ROOT / "cache" / "arxiv"
CACHE_PATH = CACHE_DIR / "abstracts.jsonl"

DEFAULT_QUERY = (
    "cat:math.NT OR cat:math.AG OR cat:math.CO OR cat:math.GT OR "
    "cat:math.RT OR cat:math.QA OR cat:math.NA OR cat:math-ph"
)


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
            aid = rec.get("arxiv_id")
            if aid:
                out.add(aid)
    return out


def fetch_and_append(
    query: str = DEFAULT_QUERY,
    max_results: int = 500,
    cache_path: Path = CACHE_PATH,
) -> int:
    """Fetch up to max_results abstracts matching query; append novel ones."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _existing_ids(cache_path)

    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    appended = 0
    with cache_path.open("a", encoding="utf-8") as f:
        for r in client.results(search):
            aid = r.entry_id.rsplit("/", 1)[-1]
            if aid in existing:
                continue
            rec = {
                "arxiv_id": aid,
                "title": r.title or "",
                "abstract": r.summary or "",
                "categories": list(r.categories or []),
                "published": r.published.isoformat() if r.published else None,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            existing.add(aid)
            appended += 1
    return appended


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.fetch_arxiv_abstracts")
    p.add_argument("--query", type=str, default=DEFAULT_QUERY)
    p.add_argument("--max-results", type=int, default=500)
    p.add_argument("--cache-path", type=Path, default=CACHE_PATH)
    args = p.parse_args()

    n = fetch_and_append(
        query=args.query,
        max_results=args.max_results,
        cache_path=args.cache_path,
    )
    print(f"[fetch_arxiv_abstracts] appended {n} new abstracts -> {args.cache_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
