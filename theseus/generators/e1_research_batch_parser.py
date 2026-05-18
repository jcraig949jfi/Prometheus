"""E1 — research-batch parser.

Mines `aporia/docs/deep_research_batch*/` markdown for claim-shaped
text (sentences naming a conjecture, theorem, equality, or inequality)
and emits them as UNVERIFIED TheseusRecords. The substrate's downstream
verification phase (sigma) routes them to terminal states later.

Pattern detection is lightweight regex over sentence shapes that
classify as claim-candidates. Not deep NLP — that's a Tier-1 LLM
augmentation. The point at v0.1 is to recover token-yield from already-
paid Gemini research that produces narrative-only output.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from theseus.config import DEEP_RESEARCH_BATCH_GLOB
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus


# Patterns that suggest claim-like statements
CLAIM_PATTERNS = (
    re.compile(r"\bconjectur[ea]\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\btheorem\b[^.]{20,300}\.", re.IGNORECASE),
    re.compile(r"\bif and only if\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bequivalent to\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\bimplies\s+that\b[^.]{10,300}\.", re.IGNORECASE),
    re.compile(r"\b(holds|fails)\s+(for\s+all|when|unless)\b[^.]{10,300}\.",
               re.IGNORECASE),
)

MAX_CLAIM_LEN = 320
MIN_CLAIM_LEN = 30


def _iter_batch_files(root: Path) -> Iterator[Path]:
    """Yield .md files from deep_research_batch* directories under root."""
    if not root.exists():
        return
    for child in root.iterdir():
        if child.is_dir() and child.name.startswith("deep_research_batch"):
            yield from child.glob("*.md")


def _extract_claims_from_text(text: str) -> List[str]:
    seen = set()
    out = []
    for pat in CLAIM_PATTERNS:
        for m in pat.finditer(text):
            s = m.group(0).strip()
            s = " ".join(s.split())  # normalize whitespace
            if len(s) < MIN_CLAIM_LEN or len(s) > MAX_CLAIM_LEN:
                continue
            if s in seen:
                continue
            seen.add(s)
            out.append(s)
    return out


class E1ResearchBatchParserGenerator(Generator):
    generator_id = "e1"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        root: Optional[Path] = None,
    ) -> None:
        super().__init__(batch_id)
        self._root = root if root is not None else DEEP_RESEARCH_BATCH_GLOB
        self._files: List[Path] = list(_iter_batch_files(self._root))
        self._cur_idx = 0
        self._cur_claims: List[str] = []
        self._cur_file: Optional[Path] = None

    def description(self) -> str:
        return (
            f"e1: deep_research_batch parser "
            f"({len(self._files)} markdown files in {self._root})"
        )

    def _load_next_file(self) -> bool:
        while self._cur_idx < len(self._files):
            p = self._files[self._cur_idx]
            self._cur_idx += 1
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            claims = _extract_claims_from_text(text)
            if claims:
                self._cur_file = p
                self._cur_claims = claims
                return True
        return False

    def next(self) -> Optional[TheseusRecord]:
        if not self._cur_claims:
            if not self._load_next_file():
                return None

        claim_text = self._cur_claims.pop()
        self.attempts += 1

        # Content-address by claim text + source file
        src = self._cur_file
        src_name = src.name if src else "unknown"

        canonical = f"LIT[{src_name}]: {claim_text}"
        payload = {
            "source_file": str(src) if src else None,
            "source_relative": src.relative_to(self._root).as_posix() if src else None,
            "claim_text": claim_text,
            "pattern_count": 1,
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
        )
        self.emitted.append(record_id)
        return r
