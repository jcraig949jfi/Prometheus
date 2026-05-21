"""E5 — MathWorld/Wikipedia conjecture-list scrape.

Reads theseus/cache/conjectures/wiki_conjectures.jsonl (built offline by
theseus.scripts.fetch_wiki_conjectures) and emits claim-shaped sentences
from the lead-paragraph summary of each conjecture/theorem page.

MathWorld coverage is deferred to a future fetcher revision (their TOS
discourages bulk scraping); for v0.1 the cache is Wikipedia-only but
the generator's structure is source-agnostic — any source whose entries
look like {"title", "extract"} will work.

Same offline-cache pattern as E2/E4.
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


DEFAULT_CACHE_PATH = THESEUS_ROOT / "cache" / "conjectures" / "wiki_conjectures.jsonl"


CLAIM_PATTERNS = (
    re.compile(r"\bconjectur[ea][sd]?\b[^.]{20,400}\.", re.IGNORECASE),
    re.compile(r"\btheorem\b[^.]{20,400}\.", re.IGNORECASE),
    re.compile(r"\bstates that\b[^.]{20,400}\.", re.IGNORECASE),
    re.compile(r"\bif and only if\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bequivalent to\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bimplies\s+that\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\b(holds|fails)\s+(for\s+all|when|unless)\b[^.]{10,300}\.",
               re.IGNORECASE),
    re.compile(r"\bproved\s+by\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bis the (statement|claim) that\b[^.]{10,300}\.",
               re.IGNORECASE),
)

MAX_CLAIM_LEN = 420
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


class E5MathWorldWikipediaScrapeGenerator(Generator):
    generator_id = "e5"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        cache_path: Optional[Path] = None,
    ) -> None:
        super().__init__(batch_id)
        self._cache_path = cache_path if cache_path is not None else DEFAULT_CACHE_PATH
        self._iter: Optional[Iterator[dict]] = None
        self._cur_claims: List[Tuple[str, dict]] = []

    def description(self) -> str:
        try:
            n = sum(1 for _ in _iter_cache(self._cache_path))
        except Exception:
            n = 0
        return f"e5: Wikipedia/MathWorld conjecture mining ({n} cached pages at {self._cache_path})"

    def _load_next_page(self) -> bool:
        if self._iter is None:
            self._iter = _iter_cache(self._cache_path)
        while True:
            try:
                rec = next(self._iter)
            except StopIteration:
                return False
            text = " ".join(
                str(rec.get(k, "")) for k in ("title", "extract")
            )
            claims = _extract_claims_from_text(text)
            if claims:
                self._cur_claims = [(c, rec) for c in claims]
                return True

    def next(self) -> Optional[TheseusRecord]:
        if not self._cur_claims:
            if not self._load_next_page():
                return None

        claim_text, page = self._cur_claims.pop()
        self.attempts += 1

        title = page.get("title", "unknown")
        canonical = f"WIKI[{title}]: {claim_text}"
        payload = {
            "page_title": title,
            "url": page.get("url", ""),
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
            extras={"role": "literature_corpus_wikipedia"},
        )
        self.emitted.append(record_id)
        return r
