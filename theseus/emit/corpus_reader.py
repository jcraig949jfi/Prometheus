"""CorpusReader — read past TheseusRecords from corpus JSONL files.

Used by self-play / mutation-from-kill generators that consume prior
batch output as parent claims.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Optional

from theseus.config import CORPUS_DIR
from theseus.emit.record_schema import TheseusRecord, Verdict


class CorpusReader:
    """Streams TheseusRecords from corpus JSONL files.

    Robust to malformed lines (skips them silently). Returns records
    as TheseusRecord instances via dataclass kwargs unpacking.
    """

    def __init__(self, corpus_dir: Optional[Path] = None) -> None:
        self.corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR

    def iter_records(
        self, batch_id_pattern: str = "*"
    ) -> Iterator[TheseusRecord]:
        """Yield records from all matching corpus files in modtime order."""
        if not self.corpus_dir.exists():
            return
        files = sorted(
            self.corpus_dir.glob(f"{batch_id_pattern}.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )
        for jf in files:
            try:
                with jf.open(encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            yield TheseusRecord(**data)
                        except (json.JSONDecodeError, TypeError, ValueError):
                            continue
            except OSError:
                continue

    def iter_survivors(
        self,
        max_records: int = 5000,
        require_payload_keys: Optional[List[str]] = None,
    ) -> Iterator[TheseusRecord]:
        """Yield records with SHADOW_CATALOG or PROMOTED verdicts.

        Optional payload-key filter (e.g. ["relation", "value_a"]) skips
        records whose payload lacks required fields.
        """
        survivor_verdicts = (
            Verdict.SHADOW_CATALOG.value,
            Verdict.PROMOTED.value,
        )
        count = 0
        for r in self.iter_records():
            if count >= max_records:
                return
            if r.verdict not in survivor_verdicts:
                continue
            if require_payload_keys is not None:
                if not all(k in r.claim_payload for k in require_payload_keys):
                    continue
            yield r
            count += 1
