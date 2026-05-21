"""CorpusWriter — JSONL append to per-batch corpus files.

One file per batch: theseus/corpus/<batch_id>.jsonl
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

from theseus.config import CORPUS_DIR
from theseus.emit.record_schema import TheseusRecord


def _digest_key(record_id: str) -> int:
    # 16 hex chars = 64 bits of entropy from the front of the sha256.
    # At 5M records, collision probability ~ 5e6^2 / 2^65 ≈ 7e-7, negligible.
    # Switching from full-string set to int set drops dedup memory ~10x.
    return int(record_id[:16], 16)


class CorpusWriter:
    """Append-only JSONL writer with in-process dedup by record_id."""

    def __init__(self, batch_id: str, corpus_dir: Path | None = None) -> None:
        self.batch_id = batch_id
        self.corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.corpus_dir / f"{batch_id}.jsonl"
        # Set of int digests (64-bit prefix of sha256). At 5M records this
        # is ~150-300MB instead of ~3GB for full hex strings — addresses
        # the b3 OOM root cause from 2026-05-20.
        self._seen: Set[int] = set()
        self.records_written = 0
        self.duplicates_skipped = 0

    def write(self, record: TheseusRecord) -> bool:
        """Append record if not already seen this batch. Returns True iff
        the record was written (False = duplicate skipped)."""
        key = _digest_key(record.record_id)
        if key in self._seen:
            self.duplicates_skipped += 1
            return False
        self._seen.add(key)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(record.to_jsonl() + "\n")
        self.records_written += 1
        return True

    def write_many(self, records: Iterable[TheseusRecord]) -> int:
        """Write multiple records; returns count actually written."""
        n = 0
        for r in records:
            if self.write(r):
                n += 1
        return n
