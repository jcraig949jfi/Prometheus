"""Scan Techne synthesis docs for quantitative claims worth verifying.

Per persona_seed_prompts_2026-05-21.md Techne idea #5:
"Self-claim verification. Techne has written synthesis-style claims in
pivot docs. Mine those claims for the quantitative ones, file as DR
tickets via Aporia. Closes the loop: claims produced by Techne get
verified by Aporia, which strengthens future substrate."

Output: techne/handoff/aporia_outbox/techne_self_claims_<date>.jsonl
plus one ticket filed to aporia/meta/queue/aporia_inbox.jsonl asking
Aporia to dispatch via Pythia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Synthesis docs to scan — Techne-authored or Techne-affecting pivots.
# Globbed under pivot/. Extend as new synthesis docs land.
SYNTHESIS_GLOBS = [
    "pivot/techne*.md",
    "pivot/substrate*.md",
    "pivot/strategic_pivot*.md",
    "pivot/prometheus_synthesis*.md",
    "pivot/killembedding*.md",
    "pivot/session_telemetry_prompts_techne*.md",
    "pivot/persona_seed_prompts*.md",
]


# Quantitative-claim patterns. Trying to catch:
# - Numerical bounds: ">= K", "< X%", "ratio of N", "K-fold improvement"
# - Conjecture statements: "we conjecture", "we expect", "we predict"
# - Implications: "X implies Y", "this means", "this shows"
# - Concrete claims with numbers: "%", "x", "K", arithmetic
QUANTITATIVE_PATTERNS = (
    # Conjecture-like
    re.compile(
        r"(?:we\s+(?:conjecture|expect|predict|claim|hypothesize))[^.]{20,300}\.",
        re.IGNORECASE,
    ),
    # Implication
    re.compile(
        r"(?:this\s+(?:implies|means|shows|suggests|predicts))[^.]{20,300}\.",
        re.IGNORECASE,
    ),
    # Numeric bound with operator
    re.compile(
        r"[^.\n]{10,200}(?:\d+(?:\.\d+)?(?:[%kKMm])?[^.\n]{5,100}"
        r"(?:[<>≤≥]=?|less than|greater than|at most|at least)[^.\n]{5,200})\.",
    ),
    # Ratio / fold / multiple
    re.compile(
        r"[^.\n]{10,200}\d+(?:\.\d+)?[\s-]?(?:fold|x|times|×)\s+"
        r"(?:improvement|increase|decrease|change|better|worse)[^.\n]{0,200}\.",
        re.IGNORECASE,
    ),
    # Rate / percentage with context
    re.compile(
        r"[^.\n]{10,200}\d+(?:\.\d+)?%[^.\n]{5,200}\.",
    ),
)


def _claim_id(text: str) -> str:
    """Stable content-addressed id for a claim."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"techne-claim-{h}"


def _extract_claims_from_text(text: str, source_path: Path) -> List[dict]:
    """Extract quantitative claim candidates from a markdown doc."""
    seen = set()
    claims: List[dict] = []
    for pat in QUANTITATIVE_PATTERNS:
        for m in pat.finditer(text):
            raw = m.group(0).strip()
            normalized = " ".join(raw.split())
            if len(normalized) < 30 or len(normalized) > 600:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            try:
                source_str = str(
                    source_path.relative_to(REPO_ROOT).as_posix()
                )
            except ValueError:
                # source_path not under REPO_ROOT (e.g. in tests); fall back
                source_str = str(source_path.as_posix())
            claims.append({
                "claim_id": _claim_id(normalized),
                "source_path": source_str,
                "claim_text": normalized,
                "pattern_kind": _classify_pattern(normalized),
            })
    return claims


def _classify_pattern(claim: str) -> str:
    """Coarse classification for downstream filtering."""
    low = claim.lower()
    if any(w in low for w in ("conjecture", "predict", "expect", "hypothesize")):
        return "conjecture"
    if any(w in low for w in ("implies", "means", "shows", "suggests")):
        return "implication"
    if "%" in claim:
        return "rate_or_percentage"
    if re.search(r"\d+\s*(?:fold|x|times|×)", claim, re.IGNORECASE):
        return "magnitude_change"
    if re.search(r"[<>≤≥]", claim):
        return "numeric_bound"
    return "other_quantitative"


def _iter_synthesis_files() -> Iterator[Path]:
    seen: set[Path] = set()
    for g in SYNTHESIS_GLOBS:
        for p in REPO_ROOT.glob(g):
            if p in seen or not p.is_file():
                continue
            seen.add(p)
            # Skip meta-analysis docs that are about Techne work, not Techne claims
            if p.name.startswith("meta_analysis_"):
                continue
            if p.name.startswith("feedback_"):
                continue
            yield p


def scan(output_path: Path) -> dict:
    """Scan all synthesis docs; write JSONL output; return summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_files = 0
    n_claims = 0
    by_kind: dict[str, int] = {}
    with output_path.open("w", encoding="utf-8") as f:
        for p in _iter_synthesis_files():
            n_files += 1
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for claim in _extract_claims_from_text(text, p):
                f.write(json.dumps(claim, sort_keys=True) + "\n")
                n_claims += 1
                by_kind[claim["pattern_kind"]] = by_kind.get(claim["pattern_kind"], 0) + 1
    return {
        "output_path": str(output_path),
        "n_files_scanned": n_files,
        "n_claims_extracted": n_claims,
        "by_pattern_kind": by_kind,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.scan_synthesis_claims")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL path. Defaults to "
             "techne/handoff/aporia_outbox/techne_self_claims_<date>.jsonl",
    )
    args = p.parse_args()

    if args.output is None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        args.output = (
            REPO_ROOT / "techne" / "handoff" / "aporia_outbox"
            / f"techne_self_claims_{today}.jsonl"
        )

    summary = scan(args.output)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
