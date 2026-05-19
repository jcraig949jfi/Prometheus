"""Corpus-file helpers — uniform access to .jsonl and .jsonl.gz batches.

The CorpusWriter writes plain .jsonl. The handoff daemon periodically
compresses idle batches to .jsonl.gz to control disk footprint. All
readers should go through these helpers so the on-disk form is
transparent.
"""
from __future__ import annotations

import gzip
import io
from pathlib import Path
from typing import Iterator, List


def iter_batch_paths(corpus_dir: Path, pattern: str = "*") -> List[Path]:
    """Return all corpus batch files (.jsonl + .jsonl.gz) for `pattern`,
    sorted by name (which is timestamp-prefixed → chronological).

    Excludes paths containing 'annotated' (a downstream-tool convention).
    """
    if not corpus_dir.is_dir():
        return []
    paths = list(corpus_dir.glob(f"{pattern}.jsonl"))
    paths += list(corpus_dir.glob(f"{pattern}.jsonl.gz"))
    paths = [p for p in paths if "annotated" not in p.name]
    return sorted(paths, key=lambda p: p.name)


def open_batch(path: Path) -> io.TextIOBase:
    """Open a corpus batch file for reading as UTF-8 text.

    Handles both plain .jsonl and .jsonl.gz transparently. Caller is
    responsible for closing (use as a context manager).
    """
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8")
    return path.open(mode="r", encoding="utf-8")


def iter_batch_lines(path: Path) -> Iterator[str]:
    """Yield non-empty stripped lines from a batch file."""
    with open_batch(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line
