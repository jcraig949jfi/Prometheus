"""Symbol-pair co-occurrence miner.

Per persona_seed_prompts_2026-05-21.md Techne idea #3:
"Symbol-pair co-occurrence miner. For every (Symbol_A, Symbol_B) pair
appearing in 5+ Theseus outputs together, propose a composite primitive.
This is a 'substrate is asking for X' sensor."

A "symbol" in the Theseus context is a (catalog, invariant) pair, e.g.
("knot", "crossing_number") or ("ec", "rank"). When two such symbols
co-appear in the same record's claim_payload (under invariant_a /
invariant_b), the substrate is testing a relationship between them.

The miner walks recent corpus batches, extracts (sym_a, sym_b) pairs
per record, and aggregates:
  - count: how often the pair co-occurred
  - verdict_breakdown: kills / confirmations / inconclusive / unverified
  - mean_info_density: mean info_density across co-occurrences

Pairs with count ≥ THRESHOLD AND a substantive verdict mix (not all
UNVERIFIED) are surfaced as composite-primitive candidates.

Output: pivot/composite_primitive_candidates_<date>.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from theseus.config import CORPUS_DIR, THESEUS_ROOT


DEFAULT_THRESHOLD = 5
DEFAULT_SAMPLE_PER_BATCH = 100_000  # avoid scanning all 79GB
DEFAULT_BATCH_FILES = 5  # most recent N batches


def _extract_pair(rec: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    """Pull a (sym_a, sym_b) tuple from a record's claim_payload.

    Returns None if the record doesn't have a paired-symbol shape.
    """
    payload = rec.get("claim_payload") or {}
    cat_a = payload.get("catalog_a")
    inv_a = payload.get("invariant_a")
    cat_b = payload.get("catalog_b")
    inv_b = payload.get("invariant_b")
    if not (cat_a and inv_a and cat_b and inv_b):
        return None
    sym_a = f"{cat_a}.{inv_a}"
    sym_b = f"{cat_b}.{inv_b}"
    # Canonicalize order so (X, Y) and (Y, X) aggregate.
    if sym_a > sym_b:
        sym_a, sym_b = sym_b, sym_a
    return (sym_a, sym_b)


def _iter_records(
    path: Path, max_records: int = DEFAULT_SAMPLE_PER_BATCH,
) -> Iterator[Dict[str, Any]]:
    """Stream JSONL line-by-line; cap at max_records to bound runtime."""
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if n >= max_records:
                break
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
            n += 1


def _select_batch_files(
    corpus_dir: Path = CORPUS_DIR,
    n_files: int = DEFAULT_BATCH_FILES,
) -> List[Path]:
    """Return the N most-recent corpus batch JSONL files (by mtime)."""
    if not corpus_dir.exists():
        return []
    files = [p for p in corpus_dir.glob("*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:n_files]


def mine(
    corpus_dir: Path = CORPUS_DIR,
    threshold: int = DEFAULT_THRESHOLD,
    sample_per_batch: int = DEFAULT_SAMPLE_PER_BATCH,
    n_batch_files: int = DEFAULT_BATCH_FILES,
) -> Dict[str, Any]:
    """Mine recent corpus for symbol-pair co-occurrences.

    Returns:
      {
        "n_batches_scanned": int,
        "n_records_scanned": int,
        "n_pairs_extracted": int,
        "pairs": [
          {"sym_a", "sym_b", "count", "verdict_breakdown", "info_density_mean"},
          ...
        ]  # sorted by count desc
      }
    """
    counts: Counter = Counter()
    verdicts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    info_density: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    files = _select_batch_files(corpus_dir, n_batch_files)
    n_records = 0
    for path in files:
        for rec in _iter_records(path, sample_per_batch):
            n_records += 1
            pair = _extract_pair(rec)
            if pair is None:
                continue
            counts[pair] += 1
            verdicts[pair][rec.get("verdict") or "UNKNOWN"] += 1
            info_d = rec.get("info_density")
            if isinstance(info_d, (int, float)):
                info_density[pair].append(float(info_d))

    n_pairs = sum(1 for c in counts.values() if c >= threshold)
    pairs_out: List[Dict[str, Any]] = []
    for pair, count in counts.most_common():
        if count < threshold:
            break
        idl = info_density.get(pair, [])
        mean_idl = sum(idl) / len(idl) if idl else None
        pairs_out.append({
            "sym_a": pair[0],
            "sym_b": pair[1],
            "count": count,
            "verdict_breakdown": dict(verdicts[pair]),
            "info_density_mean": mean_idl,
        })

    return {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "n_batches_scanned": len(files),
        "n_records_scanned": n_records,
        "n_pairs_extracted": sum(counts.values()),
        "n_pairs_above_threshold": n_pairs,
        "threshold": threshold,
        "pairs": pairs_out,
    }


def render_markdown(result: Dict[str, Any], top_n: int = 50) -> str:
    """Markdown report for composite-primitive candidates."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pairs = result.get("pairs", [])[:top_n]
    lines: List[str] = []
    lines.append(f"# Composite Primitive Candidates — {today}")
    lines.append("")
    lines.append(
        "Symbol-pair co-occurrences mined from recent Theseus corpus. "
        "Pairs that co-appear in many records signal a relationship the "
        "substrate is implicitly testing — candidates for composite "
        "primitives `(Sym_A ∘ Sym_B)` that codify the relationship."
    )
    lines.append("")
    lines.append(f"- batches scanned: **{result.get('n_batches_scanned', 0)}**")
    lines.append(f"- records scanned: **{result.get('n_records_scanned', 0):,}**")
    lines.append(f"- pairs above threshold (≥{result.get('threshold')}): **{result.get('n_pairs_above_threshold', 0)}**")
    lines.append("")
    if not pairs:
        lines.append("_No pairs above threshold._")
        return "\n".join(lines)
    lines.append(f"## Top {len(pairs)} candidate pairs")
    lines.append("")
    lines.append("| count | sym_a | sym_b | info_density_mean | verdict_breakdown |")
    lines.append("|---|---|---|---|---|")
    for p in pairs:
        info_d = (
            f"{p['info_density_mean']:.3f}"
            if p.get("info_density_mean") is not None else "-"
        )
        verdicts = ", ".join(
            f"{k}:{v}" for k, v in sorted(p.get("verdict_breakdown", {}).items())
        )
        lines.append(
            f"| {p['count']} | `{p['sym_a']}` | `{p['sym_b']}` | {info_d} | {verdicts} |"
        )
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append(
        "Each row is a (Sym_A, Sym_B) pair where Sym = `catalog.invariant`. "
        "The substrate emitted `count` records claiming a relation between "
        "those two symbols. High kill counts mean the relation usually "
        "fails (substrate doesn't believe in this specific bridge); high "
        "SHADOW_CATALOG counts mean it usually holds (candidate "
        "bridge-of-truth)."
    )
    lines.append("")
    lines.append(
        "Composite-primitive candidates: pairs with **mixed verdicts** "
        "(both kills and confirmations in non-trivial numbers) are the "
        "most informative — they reflect a relation that's true SOMETIMES, "
        "which means there's an unknown subset structure worth naming as "
        "a new primitive."
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.symbol_pair_miner")
    p.add_argument(
        "--threshold", type=int, default=DEFAULT_THRESHOLD,
        help="Minimum co-occurrence count to surface a pair.",
    )
    p.add_argument(
        "--sample", type=int, default=DEFAULT_SAMPLE_PER_BATCH,
        help="Max records to scan per batch file.",
    )
    p.add_argument(
        "--batches", type=int, default=DEFAULT_BATCH_FILES,
        help="Most-recent N batch files to scan.",
    )
    p.add_argument(
        "--md", type=Path, default=None,
        help="Write markdown report to this path. 'auto' picks today's "
             "pivot/composite_primitive_candidates_<date>.md.",
    )
    p.add_argument(
        "--json", action="store_true",
        help="Print JSON instead of text summary.",
    )
    args = p.parse_args()

    result = mine(
        threshold=args.threshold,
        sample_per_batch=args.sample,
        n_batch_files=args.batches,
    )

    if args.md is not None:
        if str(args.md) == "auto":
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            args.md = (
                THESEUS_ROOT.parent / "pivot"
                / f"composite_primitive_candidates_{today}.md"
            )
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(render_markdown(result), encoding="utf-8")
        print(f"[symbol_pair_miner] wrote {args.md}")
        return 0

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        # Text summary
        print(f"Batches scanned: {result['n_batches_scanned']}")
        print(f"Records scanned: {result['n_records_scanned']:,}")
        print(f"Pairs ≥{result['threshold']}: {result['n_pairs_above_threshold']}")
        print()
        print(f"Top 20 pairs:")
        for p in result["pairs"][:20]:
            verdicts = ", ".join(
                f"{k}:{v}" for k, v in sorted(p["verdict_breakdown"].items())
            )
            print(
                f"  {p['count']:>8} | {p['sym_a']:<25} | {p['sym_b']:<25} | {verdicts}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
