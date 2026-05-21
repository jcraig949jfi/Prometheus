"""E4 — LMFDB knowledge-node mining.

Reads theseus/cache/lmfdb/knowls.jsonl (built offline by
theseus.scripts.fetch_lmfdb_knowls) and emits claim-shaped sentences
from the descriptive content of each knowl as UNVERIFIED TheseusRecords.

LMFDB knowls are short wiki-style entries describing mathematical
objects, conjectures, and theorems used throughout the database. They
are an authoritative source of claim text grounded in real mathematical
literature — every entry is curated by working number theorists.

Same offline-cache pattern as E2: no network in next().
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


DEFAULT_CACHE_PATH = THESEUS_ROOT / "cache" / "lmfdb" / "knowls.jsonl"


CLAIM_PATTERNS = (
    re.compile(r"\bconjectur[ea]\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\btheorem\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\bif and only if\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bequivalent to\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bimplies\s+that\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\b(holds|fails)\s+(for\s+all|when|unless)\b[^.]{10,300}\.",
               re.IGNORECASE),
    re.compile(r"\bis defined as\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bis called\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bif \w+[^.]{10,300}then\b[^.]{10,300}\.", re.IGNORECASE),
)

MAX_CLAIM_LEN = 320
MIN_CLAIM_LEN = 30


# Strip TeX so the regex matches plain prose, not "Theorem $\sum_{n=1}^{\infty}$".
_TEX_INLINE = re.compile(r"\$[^$]*\$")
_TEX_DISPLAY = re.compile(r"\\\[.*?\\\]", re.DOTALL)
_TEX_BRACES = re.compile(r"\\[a-zA-Z]+\s*(\{[^}]*\})*")


def _strip_tex(text: str) -> str:
    text = _TEX_DISPLAY.sub(" MATH ", text)
    text = _TEX_INLINE.sub(" MATH ", text)
    text = _TEX_BRACES.sub(" ", text)
    return " ".join(text.split())


def _extract_claims_from_text(text: str) -> List[str]:
    text = _strip_tex(text)
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


class E4LMFDBKnowledgeMiningGenerator(Generator):
    generator_id = "e4"
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
        return f"e4: LMFDB knowledge mining ({n} cached knowls at {self._cache_path})"

    def _load_next_knowl(self) -> bool:
        if self._iter is None:
            self._iter = _iter_cache(self._cache_path)
        while True:
            try:
                rec = next(self._iter)
            except StopIteration:
                # Reset iter so race-with-fetcher recovers (see E2 note).
                self._iter = None
                return False
            text = " ".join(
                str(rec.get(k, "")) for k in ("title", "content")
            )
            claims = _extract_claims_from_text(text)
            if claims:
                self._cur_claims = [(c, rec) for c in claims]
                return True

    def next(self) -> Optional[TheseusRecord]:
        if not self._cur_claims:
            if not self._load_next_knowl():
                return None

        claim_text, knowl = self._cur_claims.pop()
        self.attempts += 1

        kid = knowl.get("id", "unknown")
        cat = knowl.get("category", "unknown")

        canonical = f"LMFDB_KNOWL[{kid}|{cat}]: {claim_text}"
        payload = {
            "knowl_id": kid,
            "title": knowl.get("title", ""),
            "category": cat,
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
            extras={"role": "literature_corpus_lmfdb_knowls"},
        )
        self.emitted.append(record_id)
        return r
