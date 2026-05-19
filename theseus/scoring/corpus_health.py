"""corpus_health — empirical inspection of accumulated substrate corpus.

Scans all corpus JSONL files and reports:
  - Cross-batch dedup: unique record_ids across all files vs total emissions
  - Per-relation H4-rate (real-time confirmation of the parity > divides
    > equal finding from Fires #13-14)
  - Top-N records by training_weight (concrete Ergon-training candidates)
  - Per-generator verdict distributions
  - Verdict-distribution evolution across batches (oldest → newest)

Outputs: theseus/corpus_health_report.md

Use the engine to inspect the engine.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from theseus.config import CORPUS_DIR, THESEUS_ROOT
from theseus.scoring.training_weight import training_weight
from theseus.emit.record_schema import TheseusRecord


REPORT_PATH = THESEUS_ROOT / "corpus_health_report.md"


def _bucket_relation(rel: str) -> str:
    """Aggregate abs_diff_le_K variants into one bucket."""
    if rel.startswith("abs_diff_le_"):
        return "abs_diff_le_*"
    return rel


def analyze_corpus(corpus_dir: Path = CORPUS_DIR) -> Dict[str, Any]:
    """Walk all JSONLs in corpus_dir; return structured stats."""
    from theseus.emit.corpus_files import iter_batch_paths
    files = iter_batch_paths(corpus_dir)

    # Global counters
    n_total_emissions = 0
    seen_record_ids = set()  # cross-batch dedup tracker
    cross_batch_dupes = 0

    # Per-verdict counters
    verdicts = Counter()
    # Per-generator verdicts: gen → Counter(verdict→n)
    per_gen_verdicts: Dict[str, Counter] = defaultdict(Counter)
    per_gen_records: Counter = Counter()

    # H4 per-relation tally (multi-arrow bridge extension records)
    h4_shadow_by_rel: Counter = Counter()
    h4_total_by_rel: Counter = Counter()

    # All-records per-relation rate (any record with a relation field)
    rel_shadow: Counter = Counter()
    rel_total: Counter = Counter()

    # Top-N highest-weight records
    top_records: List[Tuple[float, Dict]] = []
    TOP_N_KEEP = 25

    # Per-batch verdict distribution
    per_batch: Dict[str, Counter] = defaultdict(Counter)

    from theseus.emit.corpus_files import open_batch
    for jf in files:
        try:
            with open_batch(jf) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r_dict = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    n_total_emissions += 1
                    rid = r_dict.get("record_id")
                    if rid in seen_record_ids:
                        cross_batch_dupes += 1
                        continue
                    if rid:
                        seen_record_ids.add(rid)

                    verdict = r_dict.get("verdict", "?")
                    gid = r_dict.get("generator_id", "?")
                    bid = r_dict.get("batch_id", "?")
                    verdicts[verdict] += 1
                    per_gen_verdicts[gid][verdict] += 1
                    per_gen_records[gid] += 1
                    per_batch[bid][verdict] += 1

                    p = r_dict.get("claim_payload") or {}
                    rel = _bucket_relation(p.get("relation", ""))
                    if rel:
                        rel_total[rel] += 1
                        if verdict == "SHADOW_CATALOG":
                            rel_shadow[rel] += 1

                    if gid == "h4":
                        parent_rel = _bucket_relation(p.get("relation", ""))
                        if parent_rel:
                            h4_total_by_rel[parent_rel] += 1
                            if verdict == "SHADOW_CATALOG":
                                h4_shadow_by_rel[parent_rel] += 1

                    # Top-weighted tracker
                    try:
                        r = TheseusRecord(**r_dict)
                        w = training_weight(r)
                    except Exception:
                        continue
                    if len(top_records) < TOP_N_KEEP:
                        top_records.append((w, r_dict))
                        top_records.sort(key=lambda x: x[0])
                    elif w > top_records[0][0]:
                        top_records[0] = (w, r_dict)
                        top_records.sort(key=lambda x: x[0])
        except OSError:
            continue

    top_records.sort(key=lambda x: -x[0])

    return {
        "n_corpus_files": len(files),
        "n_total_emissions": n_total_emissions,
        "n_unique_record_ids": len(seen_record_ids),
        "cross_batch_dupes": cross_batch_dupes,
        "dedup_rate": (
            len(seen_record_ids) / n_total_emissions
            if n_total_emissions else 1.0
        ),
        "verdict_distribution": dict(verdicts),
        "per_generator_records": dict(per_gen_records),
        "per_generator_verdicts": {
            gid: dict(c) for gid, c in per_gen_verdicts.items()
        },
        "h4_by_relation": {
            rel: {
                "shadow": h4_shadow_by_rel[rel],
                "total": h4_total_by_rel[rel],
                "rate": (
                    h4_shadow_by_rel[rel] / h4_total_by_rel[rel]
                    if h4_total_by_rel[rel] else 0
                ),
            }
            for rel in sorted(h4_total_by_rel)
        },
        "global_rel_shadow_rate": {
            rel: {
                "shadow": rel_shadow[rel],
                "total": rel_total[rel],
                "rate": rel_shadow[rel] / rel_total[rel] if rel_total[rel] else 0,
            }
            for rel in sorted(rel_total)
        },
        "top_records_by_weight": [
            {"weight": round(w, 4), "record": r}
            for w, r in top_records
        ],
        "per_batch": {bid: dict(c) for bid, c in per_batch.items()},
    }


def render_report(stats: Dict[str, Any]) -> str:
    """Render structured stats as a human-readable Markdown report."""
    lines = [
        "# Theseus Corpus Health Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Corpus files scanned: {stats['n_corpus_files']}",
        "",
        "## Volume",
        "",
        f"- Total emissions across all corpus files: **{stats['n_total_emissions']:,}**",
        f"- Unique record_ids (cross-batch deduplicated): **{stats['n_unique_record_ids']:,}**",
        f"- Cross-batch duplicates: {stats['cross_batch_dupes']:,}",
        f"- Cross-batch dedup rate: **{stats['dedup_rate']:.1%}** unique",
        "",
        "## Verdict distribution (across all unique records)",
        "",
    ]
    total_v = sum(stats["verdict_distribution"].values()) or 1
    for v, n in sorted(stats["verdict_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- **{v}**: {n:,} ({100*n/total_v:.1f}%)")

    lines += ["", "## H4 cross-catalog bridge extensibility (per-relation)",
              ""]
    if stats["h4_by_relation"]:
        for rel, m in sorted(stats["h4_by_relation"].items(),
                             key=lambda x: -x[1]["rate"]):
            rate_pct = 100 * m["rate"]
            lines.append(
                f"- **{rel}**: {m['shadow']:,}/{m['total']:,} = "
                f"**{rate_pct:.1f}%** categorical"
            )
        lines.append("")
        lines.append("Reference: Fires #13-14 seed-confirmed rates were "
                     "parity ~63%, divides ~40%, equal ~2%.")
    else:
        lines.append("(no H4 records in corpus)")

    lines += ["", "## Per-generator record counts", ""]
    for gid, n in sorted(stats["per_generator_records"].items(),
                         key=lambda x: -x[1])[:30]:
        lines.append(f"- **{gid}**: {n:,}")

    lines += ["", "## Top high-weight records (Ergon training candidates)",
              ""]
    for entry in stats["top_records_by_weight"][:15]:
        w = entry["weight"]
        r = entry["record"]
        gid = r.get("generator_id", "?")
        v = r.get("verdict", "?")
        text = (r.get("canonical_claim_text") or "")[:140]
        lines.append(f"- `{w:.4f}` | {gid} | {v}")
        lines.append(f"   {text}")

    lines += ["", "## Verdict evolution across batches (chronological)", ""]
    batches_sorted = sorted(stats["per_batch"].items())
    for bid, c in batches_sorted[-10:]:  # last 10 batches
        total_b = sum(c.values()) or 1
        kills_pct = 100 * c.get("REJECTED", 0) / total_b
        shadows_pct = 100 * c.get("SHADOW_CATALOG", 0) / total_b
        inconc_pct = 100 * c.get("INCONCLUSIVE", 0) / total_b
        lines.append(
            f"- **{bid[:30]}** (n={total_b:,}): "
            f"REJ {kills_pct:.0f}% / SHADOW {shadows_pct:.0f}% / INC {inconc_pct:.0f}%"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.scoring.corpus_health")
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    parser.add_argument(
        "--print", action="store_true", help="Print the report to stdout in addition to writing"
    )
    args = parser.parse_args()

    stats = analyze_corpus(args.corpus_dir)
    report = render_report(stats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    if args.print:
        print(report)
    print(f"[corpus_health] Wrote report to {args.output}")
    print(f"[corpus_health] {stats['n_total_emissions']:,} emissions / "
          f"{stats['n_unique_record_ids']:,} unique / "
          f"dedup {stats['dedup_rate']:.1%}")


if __name__ == "__main__":
    main()
