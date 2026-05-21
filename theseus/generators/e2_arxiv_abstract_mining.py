"""E2 — arxiv abstract mining.

Reads the local cache at theseus/cache/arxiv/abstracts.jsonl (built
offline by theseus.scripts.fetch_arxiv_abstracts) and emits claim-shaped
sentences from each abstract as UNVERIFIED TheseusRecords.

Mirrors E1's pattern: lightweight regex over sentence shapes. Generator
does NO network calls in next() — all fetching is offline. If the cache
is missing, the generator emits nothing and the daemon's
consecutive-Nones threshold marks it exhausted gracefully.

Token-free. Substrate-grade idempotency: same cache → same record_ids.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from theseus.config import THESEUS_ROOT
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus


DEFAULT_CACHE_PATH = THESEUS_ROOT / "cache" / "arxiv" / "abstracts.jsonl"


CLAIM_PATTERNS = (
    re.compile(r"\bconjectur[ea]\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\btheorem\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\bif and only if\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bequivalent to\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bimplies\s+that\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\b(holds|fails)\s+(for\s+all|when|unless)\b[^.]{10,300}\.",
               re.IGNORECASE),
    re.compile(r"\bwe (prove|show|establish|demonstrate)\b[^.]{20,300}\.",
               re.IGNORECASE),
    re.compile(r"\bit is (known|conjectured|proved|believed)\b[^.]{20,300}\.",
               re.IGNORECASE),
)

MAX_CLAIM_LEN = 320
MIN_CLAIM_LEN = 30


def _extract_claims_from_text(text: str) -> List[str]:
    seen = set()
    out = []
    for pat in CLAIM_PATTERNS:
        for m in pat.finditer(text):
            s = m.group(0).strip()
            s = " ".join(s.split())
            if len(s) < MIN_CLAIM_LEN or len(s) > MAX_CLAIM_LEN:
                continue
            if s in seen:
                continue
            seen.add(s)
            out.append(s)
    return out


def _iter_cache(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


class E2ArxivAbstractMiningGenerator(Generator):
    generator_id = "e2"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        cache_path: Optional[Path] = None,
    ) -> None:
        super().__init__(batch_id)
        self._cache_path = cache_path if cache_path is not None else DEFAULT_CACHE_PATH
        # Materialize the cache iterator lazily on first next().
        self._iter: Optional[Iterator[dict]] = None
        self._cur_claims: List[Tuple[str, dict]] = []
        self._cur_abstract: Optional[dict] = None

    def description(self) -> str:
        # Lightweight count of available cache entries (read once).
        try:
            n = sum(1 for _ in _iter_cache(self._cache_path))
        except Exception:
            n = 0
        return f"e2: arxiv abstract mining ({n} cached abstracts at {self._cache_path})"

    def _load_next_abstract(self) -> bool:
        if self._iter is None:
            self._iter = _iter_cache(self._cache_path)
        while True:
            try:
                rec = next(self._iter)
            except StopIteration:
                # Reset iterator so that if the cache file is populated
                # mid-batch (race with fetcher), the next call picks up
                # the new content rather than staying stuck at empty.
                self._iter = None
                return False
            text = " ".join(
                str(rec.get(k, "")) for k in ("title", "abstract")
            )
            claims = _extract_claims_from_text(text)
            if claims:
                self._cur_abstract = rec
                self._cur_claims = [(c, rec) for c in claims]
                return True

    def next(self) -> Optional[TheseusRecord]:
        if not self._cur_claims:
            if not self._load_next_abstract():
                return None

        claim_text, abstract_rec = self._cur_claims.pop()
        self.attempts += 1

        aid = abstract_rec.get("arxiv_id", "unknown")
        cats = abstract_rec.get("categories", []) or []
        primary_cat = cats[0] if cats else "unknown"

        canonical = f"ARXIV[{aid}|{primary_cat}]: {claim_text}"
        payload = {
            "arxiv_id": aid,
            "title": abstract_rec.get("title", ""),
            "categories": cats,
            "published": abstract_rec.get("published"),
            "claim_text": claim_text,
        }
        record_id = TheseusRecord.compute_record_id(
            canonical_claim_text=canonical,
            generator_id=self.generator_id,
        )
        r = TheseusRecord(
            record_id=record_id,
            generator_id=self.generator_id,
            batch_id=self.batch_id,
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=self.claim_kind,
            claim_payload=payload,
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
            method="regex_pattern_match",
            convergence_status="n/a",
            extras={"role": "literature_corpus_arxiv"},
        )
        self.emitted.append(record_id)
        return r
