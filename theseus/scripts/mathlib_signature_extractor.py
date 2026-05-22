"""Extract mathlib4 type signatures as Theseus primitive candidates.

Per persona_seed_prompts_2026-05-21.md Techne idea #2:
"Mathlib-prim importer. The orphan cartography/mathlib/mathlib4_source
submodule was about importing mathlib4 type signatures as substrate.
Resurrect the import (without breaking Pages — clone outside docs/)
and translate the top-200 mathlib type signatures into primitive
candidates."

This is the catalog-expansion swing that addresses the saturation
surfaced in Fires #47/#48 (b5@99.9%, e4@100%, b2@100%, d2@75%).
Theseus's claim space is exhausted on the closed (catalog × invariant
× relation × operator) cross-product; mathlib4 has thousands of
theorem statements expressing relationships our substrate doesn't yet
know about.

Strategy:
1. Walk mathlib4_source/Mathlib/ under target subdirs (NumberTheory,
   AlgebraicGeometry/EllipticCurve, RingTheory, FieldTheory)
2. Regex-extract theorem/lemma/def signatures + their statements
3. Filter to candidates Theseus could plausibly test (involves
   integer/algebraic/structural notions)
4. Output JSONL: theseus/handoff/mathlib_primitive_candidates.jsonl
5. Future fires (#50+): score by import-graph centrality, author
   specs for top 20

This fire (#49): pure extraction. Future scoring + spec-authoring
are subsequent fires.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from theseus.config import THESEUS_ROOT


REPO_ROOT = THESEUS_ROOT.parent
MATHLIB_DIR = REPO_ROOT / "cartography" / "mathlib" / "mathlib4_source" / "Mathlib"
DEFAULT_OUTPUT = (
    REPO_ROOT / "techne" / "handoff" / "mathlib_primitive_candidates.jsonl"
)


# Target subdirectories — substrate-relevant math domains where mathlib4
# theorems most likely have statements Theseus's catalog can test.
TARGET_SUBDIRS = (
    "NumberTheory",
    "AlgebraicGeometry/EllipticCurve",
    "RingTheory",
    "FieldTheory",
    "Geometry",  # includes some topology/knot-adjacent
)


# Lean 4 declaration patterns. We're matching at the start of a line.
# Captures: kind (theorem/lemma/def), name, args+statement (one line
# of signature, may continue to next line in source but we'll truncate).
DECL_PATTERNS = (
    re.compile(
        r"^(?P<kind>theorem|lemma)\s+(?P<name>[a-zA-Z_][\w'.]*)"
        r"\s*(?P<sig>[^\n]+?):=",
        re.MULTILINE,
    ),
    re.compile(
        r"^(?P<kind>theorem|lemma)\s+(?P<name>[a-zA-Z_][\w'.]*)"
        r"\s*(?P<sig>[^\n]+?:)$",
        re.MULTILINE,
    ),
    re.compile(
        r"^(?P<kind>def)\s+(?P<name>[a-zA-Z_][\w'.]*)"
        r"\s*(?P<sig>[^\n:]+?:[^\n=]+?):=",
        re.MULTILINE,
    ),
)


MAX_SIG_LEN = 600  # bound signature length to avoid runaway captures
MIN_SIG_LEN = 10


def _iter_lean_files(root: Path) -> Iterator[Path]:
    """Yield .lean files under target subdirs."""
    for sub in TARGET_SUBDIRS:
        d = root / sub
        if not d.exists():
            continue
        yield from d.rglob("*.lean")


def _extract_one(path: Path) -> List[dict]:
    """Extract all theorem/lemma/def signatures from a single .lean file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    out: List[dict] = []
    seen_names: set[str] = set()
    for pat in DECL_PATTERNS:
        for m in pat.finditer(text):
            name = m.group("name").strip()
            sig = m.group("sig").strip()
            kind = m.group("kind").strip()
            if not name or not sig:
                continue
            if name in seen_names:
                continue
            seen_names.add(name)
            # Cleanup signature
            sig = " ".join(sig.split())
            if len(sig) > MAX_SIG_LEN:
                sig = sig[:MAX_SIG_LEN] + "...(truncated)"
            if len(sig) < MIN_SIG_LEN:
                continue
            try:
                rel = path.relative_to(MATHLIB_DIR).as_posix()
            except ValueError:
                rel = str(path)
            out.append({
                "kind": kind,
                "name": name,
                "signature": sig,
                "source_path": rel,
                "domain": rel.split("/")[0] if "/" in rel else rel,
            })
    return out


def extract_all(
    mathlib_dir: Path = MATHLIB_DIR,
    output_path: Path = DEFAULT_OUTPUT,
    max_per_file: int = 50,
    max_total: Optional[int] = None,
) -> dict:
    """Walk mathlib4 target subdirs, extract signatures, write JSONL.

    Returns summary {n_files, n_signatures, by_kind, by_domain}.
    """
    if not mathlib_dir.exists():
        return {
            "error": f"mathlib_dir not found: {mathlib_dir}",
            "n_files": 0,
            "n_signatures": 0,
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_files = 0
    n_sigs = 0
    by_kind: dict[str, int] = {}
    by_domain: dict[str, int] = {}

    with output_path.open("w", encoding="utf-8") as out:
        for path in _iter_lean_files(mathlib_dir):
            n_files += 1
            sigs = _extract_one(path)[:max_per_file]
            for sig in sigs:
                out.write(json.dumps(sig, sort_keys=True) + "\n")
                n_sigs += 1
                by_kind[sig["kind"]] = by_kind.get(sig["kind"], 0) + 1
                by_domain[sig["domain"]] = by_domain.get(sig["domain"], 0) + 1
                if max_total is not None and n_sigs >= max_total:
                    return {
                        "n_files": n_files,
                        "n_signatures": n_sigs,
                        "by_kind": by_kind,
                        "by_domain": by_domain,
                        "stopped": "max_total",
                        "extracted_at": datetime.now(timezone.utc).isoformat(),
                        "output_path": str(output_path),
                    }

    return {
        "n_files": n_files,
        "n_signatures": n_sigs,
        "by_kind": by_kind,
        "by_domain": by_domain,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "output_path": str(output_path),
    }


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.mathlib_signature_extractor")
    p.add_argument(
        "--mathlib-dir", type=Path, default=MATHLIB_DIR,
        help="Path to mathlib4 source tree (subdir Mathlib/).",
    )
    p.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Output JSONL path.",
    )
    p.add_argument(
        "--max-per-file", type=int, default=50,
        help="Max signatures to extract per .lean file (avoids one-file dominance).",
    )
    p.add_argument(
        "--max-total", type=int, default=None,
        help="Cap on total signatures extracted (None = no cap).",
    )
    args = p.parse_args()

    summary = extract_all(
        mathlib_dir=args.mathlib_dir,
        output_path=args.output,
        max_per_file=args.max_per_file,
        max_total=args.max_total,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
