"""CorpusWriter — JSONL append to per-batch corpus files.

One file per batch: theseus/corpus/<batch_id>.jsonl
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

from theseus.config import CORPUS_DIR
from theseus.emit.record_schema import TheseusRecord


class CorpusWriter:
    """Append-only JSONL writer with in-process dedup by record_id."""

    def __init__(self, batch_id: str, corpus_dir: Path | None = None) -> None:
        self.batch_id = batch_id
        self.corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.corpus_dir / f"{batch_id}.jsonl"
        self._seen: Set[str] = set()
        self.records_written = 0
        self.duplicates_skipped = 0

    def write(self, record: TheseusRecord) -> bool:
        """Append record if not already seen this batch. Returns True iff
        the record was written (False = duplicate skipped)."""
        if record.record_id in self._seen:
            self.duplicates_skipped += 1
            return False
        self._seen.add(record.record_id)
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
