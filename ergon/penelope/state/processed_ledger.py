"""Append-only ledger of input files Penelope has already ingested.

Idempotency contract: a file's (path, sha256) pair appears at most once
in the ledger after successful ingest. Re-ingest is short-circuited.

The ledger is JSONL — one record per ingested file — so it survives
crashes mid-batch and is human-greppable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

from ergon.penelope.config import PROCESSED_LEDGER_PATH


@dataclass
class LedgerEntry:
    path: str
    sha256: str
    size_bytes: int
    source: str
    ingested_at: str
    batch_id: str
    n_records_ingested: int
    n_records_dropped: int
    validation_failures: int
    result: str
    notes: str = ""


def sha256_of_file(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_processed_keys(ledger_path: Optional[Path] = None) -> Set[Tuple[str, str]]:
    """Return the set of (path, sha256) keys already in the ledger.

    Missing ledger file → empty set.
    """
    path = ledger_path or PROCESSED_LEDGER_PATH
    keys: Set[Tuple[str, str]] = set()
    if not path.exists():
        return keys
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                keys.add((obj["path"], obj["sha256"]))
            except (json.JSONDecodeError, KeyError):
                continue
    return keys


def append_entry(entry: LedgerEntry, ledger_path: Optional[Path] = None) -> None:
    path = ledger_path or PROCESSED_LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), sort_keys=True) + "\n")


def make_entry(
    file_path: Path,
    source: str,
    batch_id: str,
    n_records_ingested: int,
    n_records_dropped: int,
    validation_failures: int,
    result: str,
    notes: str = "",
    sha256: Optional[str] = None,
    size_bytes: Optional[int] = None,
) -> LedgerEntry:
    """Ledger entry. Pre-computed sha256 / size_bytes can be passed in for
    cases where the file has already moved (e.g., Theseus consumed/) by
    the time the entry is built — re-hashing would FileNotFoundError.
    """
    return LedgerEntry(
        path=str(file_path),
        sha256=sha256 if sha256 is not None else sha256_of_file(file_path),
        size_bytes=size_bytes if size_bytes is not None else file_path.stat().st_size,
        source=source,
        ingested_at=datetime.now(timezone.utc).isoformat(),
        batch_id=batch_id,
        n_records_ingested=n_records_ingested,
        n_records_dropped=n_records_dropped,
        validation_failures=validation_failures,
        result=result,
        notes=notes,
    )
