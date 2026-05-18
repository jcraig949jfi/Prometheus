"""H4 stratified audit — test whether parity > divides > equal hierarchy
is uniform across ec_invariants or driven by tamagawa_product's small-
range integer distribution.

For each (parent_ec_invariant, relation) combo:
  - Count H4 SHADOW (≥2 of 3 extensions hold; categorical bridge)
  - Count H4 total (SHADOW + INCONCLUSIVE + REJECTED)
  - Report rate

If rates vary wildly by parent_ec_invariant for the same relation, the
hierarchy is artifact-laden. If they're consistent, it's structural.

Substrate-honesty discipline: test the engine's own findings.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from theseus.config import CORPUS_DIR, THESEUS_ROOT


REPORT_PATH = THESEUS_ROOT / "h4_stratified_audit_report.md"


def _bucket_relation(rel: str) -> str:
    if rel.startswith("abs_diff_le_"):
        return "abs_diff_le_*"
    return rel


def stratified_audit(corpus_dir: Path = CORPUS_DIR) -> Dict[str, Any]:
    """Walk all H4 records; stratify by (parent_ec_invariant, relation)."""
    files = sorted(corpus_dir.glob("*.jsonl"))

    # (ec_inv, relation) -> {"shadow": n, "total": n}
    by_pair: Dict[tuple, Dict[str, int]] = defaultdict(
        lambda: {"shadow": 0, "total": 0}
    )
    # Just (relation) -> aggregate
    by_relation: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"shadow": 0, "total": 0}
    )
    n_h4_records = 0

    for jf in files:
        if "annotated" in jf.name:
            continue
        try:
            with jf.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if r.get("generator_id") != "h4":
                        continue
                    p = r.get("claim_payload", {})
                    rel = _bucket_relation(p.get("relation", ""))
                    parent_ec_inv = p.get("parent_ec_invariant", "?")
                    is_shadow = r.get("verdict") == "SHADOW_CATALOG"
                    key = (parent_ec_inv, rel)
                    by_pair[key]["total"] += 1
                    by_relation[rel]["total"] += 1
                    if is_shadow:
                        by_pair[key]["shadow"] += 1
                        by_relation[rel]["shadow"] += 1
                    n_h4_records += 1
        except OSError:
            continue

    pair_rates = [
        {
            "parent_ec_invariant": ec_inv,
            "relation": rel,
            "shadow": d["shadow"],
            "total": d["total"],
            "rate": d["shadow"] / d["total"] if d["total"] else 0,
        }
        for (ec_inv, rel), d in by_pair.items()
        if d["total"] >= 20  # require minimum sample
    ]
    pair_rates.sort(key=lambda x: (x["relation"], -x["rate"]))

    relation_rates = {
        rel: {
            "shadow": d["shadow"],
            "total": d["total"],
            "rate": d["shadow"] / d["total"] if d["total"] else 0,
        }
        for rel, d in by_relation.items()
    }

    # Within-relation variance check
    per_relation_variance = {}
    for rel in set(r["relation"] for r in pair_rates):
        rates_for_rel = [
            r["rate"] for r in pair_rates if r["relation"] == rel
        ]
        if len(rates_for_rel) < 2:
            continue
        mean = sum(rates_for_rel) / len(rates_for_rel)
        var = sum((x - mean) ** 2 for x in rates_for_rel) / len(rates_for_rel)
        per_relation_variance[rel] = {
            "n_invariants": len(rates_for_rel),
            "mean": mean,
            "min": min(rates_for_rel),
            "max": max(rates_for_rel),
            "stdev": var ** 0.5,
            "range_pp": (max(rates_for_rel) - min(rates_for_rel)) * 100,
        }

    return {
        "n_h4_records": n_h4_records,
        "n_corpus_files": len(files),
        "pair_rates": pair_rates,
        "relation_aggregate": relation_rates,
        "per_relation_variance": per_relation_variance,
    }


def render_report(stats: Dict[str, Any]) -> str:
    lines = [
        "# H4 Stratified Audit Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Corpus files: {stats['n_corpus_files']}",
        f"H4 records analyzed: {stats['n_h4_records']:,}",
        "",
        "## Verdict on parity > divides > equal hierarchy",
        "",
        "**Test**: do the categorical-rate findings hold uniformly across",
        "ec_invariants, or are they driven by specific small-range invariants",
        "(suspected: tamagawa_product)?",
        "",
        "## Aggregate relation rates (for reference)",
        "",
    ]
    for rel, d in sorted(stats["relation_aggregate"].items(),
                         key=lambda x: -x[1]["rate"]):
        if d["total"] < 10:
            continue
        lines.append(f"- **{rel}**: {d['shadow']:,}/{d['total']:,} = {100*d['rate']:.1f}%")

    lines += ["", "## Per-(ec_invariant, relation) stratified rates",
              "", "Sorted by relation then by rate descending.",
              "",
              "| ec_invariant | relation | shadow/total | rate |",
              "|---|---|---|---|"]
    for r in stats["pair_rates"]:
        lines.append(
            f"| {r['parent_ec_invariant']} | {r['relation']} | "
            f"{r['shadow']}/{r['total']} | {100*r['rate']:.1f}% |"
        )

    lines += ["", "## Within-relation variance across ec_invariants",
              "",
              "If a relation's rate varies wildly across ec_invariants,",
              "the aggregate is artifact-laden. If rates cluster tightly,",
              "the relation has uniform structural meaning.",
              ""]
    for rel, v in sorted(stats["per_relation_variance"].items(),
                         key=lambda x: -x[1]["mean"]):
        lines.append(
            f"### {rel}\n"
            f"- n_invariants analyzed: {v['n_invariants']}\n"
            f"- mean rate: {100*v['mean']:.1f}%\n"
            f"- min: {100*v['min']:.1f}% | max: {100*v['max']:.1f}%\n"
            f"- range: {v['range_pp']:.1f} percentage points\n"
            f"- stdev: {100*v['stdev']:.1f}pp\n"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.scoring.h4_stratified_audit")
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    stats = stratified_audit(args.corpus_dir)
    report = render_report(stats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"[h4_audit] Wrote report to {args.output}")
    print(f"[h4_audit] H4 records analyzed: {stats['n_h4_records']:,}")
    for rel, v in sorted(stats["per_relation_variance"].items(),
                         key=lambda x: -x[1]["mean"]):
        print(f"[h4_audit] {rel}: mean={100*v['mean']:.1f}% range={v['range_pp']:.1f}pp ({v['n_invariants']} ec_invs)")


if __name__ == "__main__":
    main()
