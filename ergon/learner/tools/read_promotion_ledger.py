"""ergon.learner.tools.read_promotion_ledger — consumer-side ledger reader.

Per Iter 17 / Task #81 + Iter 20 / Task #84. The consumer of an Ergon
promotion ledger (e.g. Charon checking what Ergon discovered) needs a
minimal CLI to query the ledger without needing the full Ergon codebase.
This script demonstrates the consumer interface.

Single-ledger usage:
    python -m ergon.learner.tools.read_promotion_ledger <path_to_ledger.jsonl>

Multi-ledger merge (across runs):
    python -m ergon.learner.tools.read_promotion_ledger \\
        path_a.jsonl path_b.jsonl ...

Outputs a markdown summary covering:
  - Total substrate-PASS records, span (first/last episodes), seeds, trials
  - Classification breakdown (exact / discriminator / non-planted)
  - Top-5 most-frequent unique predicates
  - Top-5 highest-lift unique predicates
  - Per-operator-class contribution to substrate-PASS

Multi-ledger merge dedupes by (content_hash, seed, episode, trial_name)
to avoid double-counting records that may appear in multiple ledger files.

This is the format Charon / Aporia / Harmonia would consume.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_records(path: Path) -> List[Dict[str, Any]]:
    """Load all records from a promotion-ledger JSONL file.

    Intentionally does NOT depend on ergon.learner.promotion_ledger to
    prove the format is consumable from a vanilla Python script — what
    Charon would actually do.
    """
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_manifest(ledger_path: Path) -> Optional[Dict[str, Any]]:
    """Load the optional sidecar manifest for a ledger.

    Returns None if the .meta.json doesn't exist (older ledgers).
    """
    mp = ledger_path.with_suffix(ledger_path.suffix + ".meta.json")
    if not mp.exists():
        return None
    return json.loads(mp.read_text(encoding="utf-8"))


def load_and_merge_records(paths: List[Path]) -> List[Dict[str, Any]]:
    """Merge records across multiple ledger files, deduping by
    (content_hash, seed, episode, trial_name)."""
    seen: set = set()
    merged: List[Dict[str, Any]] = []
    for path in paths:
        for r in load_records(path):
            key = (
                r.get("genome_content_hash"),
                r.get("seed"),
                r.get("episode"),
                r.get("trial_name"),
            )
            if key not in seen:
                seen.add(key)
                merged.append(r)
    return merged


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"n_records": 0}

    seeds = sorted(set(r["seed"] for r in records))
    trials = sorted(set(r.get("trial_name", "unknown") for r in records))
    episodes = [r["episode"] for r in records]
    classifications = Counter()
    for r in records:
        if r["is_obstruction_exact"]:
            classifications["obstruction_exact"] += 1
        elif r["is_secondary_exact"]:
            classifications["secondary_exact"] += 1
        elif r["is_obstruction_discriminator"]:
            classifications["obstruction_discriminator_only"] += 1
        elif r["is_secondary_discriminator"]:
            classifications["secondary_discriminator_only"] += 1
        else:
            classifications["non_planted"] += 1

    operator_breakdown = Counter()
    for r in records:
        operator_breakdown[r["operator_class"]] += 1

    # Dedupe by canonical_predicate_hash (preferred) or content_hash (fallback).
    # The canonical hash collapses semantically-equivalent predicates that the
    # engine produced via different DAG paths into one unique entry.
    by_hash: Dict[str, Dict[str, Any]] = {}
    use_canonical = any("canonical_predicate_hash" in r for r in records)
    for r in records:
        key = r.get("canonical_predicate_hash") or r["genome_content_hash"]
        if key not in by_hash:
            by_hash[key] = {
                "content_hash": key,
                "predicate": r["predicate"],
                "lift": r["lift"],
                "match_size": r["match_size"],
                "n_occurrences": 1,
                "first_seed": r["seed"],
                "first_episode": r["episode"],
            }
        else:
            by_hash[key]["n_occurrences"] += 1

    unique_preds = list(by_hash.values())
    most_frequent = sorted(unique_preds, key=lambda u: -u["n_occurrences"])[:5]
    highest_lift = sorted(unique_preds, key=lambda u: -u["lift"])[:5]

    # Augment unique preds with planted-status flags from any record
    # carrying that content_hash (use the first matching record).
    planted_flags: Dict[str, bool] = {}
    for r in records:
        ch = r["genome_content_hash"]
        if ch in planted_flags:
            continue
        planted_flags[ch] = (
            r.get("is_obstruction_exact", False)
            or r.get("is_secondary_exact", False)
            or r.get("is_obstruction_discriminator", False)
            or r.get("is_secondary_discriminator", False)
        )

    non_planted_preds = [
        u for u in unique_preds
        if not planted_flags.get(u["content_hash"], False)
    ]
    top_non_planted_by_lift = sorted(
        non_planted_preds, key=lambda u: -u["lift"]
    )[:10]
    top_non_planted_by_freq = sorted(
        non_planted_preds, key=lambda u: -u["n_occurrences"]
    )[:5]

    return {
        "n_records": len(records),
        "n_unique_predicates": len(unique_preds),
        "n_unique_non_planted": len(non_planted_preds),
        "seeds": seeds,
        "trials": trials,
        "episode_min": min(episodes),
        "episode_max": max(episodes),
        "classifications": dict(classifications),
        "operator_breakdown": dict(operator_breakdown),
        "most_frequent": most_frequent,
        "highest_lift": highest_lift,
        "top_non_planted_by_lift": top_non_planted_by_lift,
        "top_non_planted_by_freq": top_non_planted_by_freq,
    }


def render_markdown(
    path_or_paths: Any, summary: Dict[str, Any]
) -> str:
    if summary["n_records"] == 0:
        if isinstance(path_or_paths, list):
            label = ", ".join(p.name for p in path_or_paths)
        else:
            label = path_or_paths.name
        return f"# {label}\n\nNo records.\n"

    c = summary["classifications"]
    o = summary["operator_breakdown"]
    if isinstance(path_or_paths, list):
        title = f"Ergon promotion ledger merge: {len(path_or_paths)} files"
        path_lines = [f"- Files merged:"]
        for p in path_or_paths:
            mani = load_manifest(p)
            if mani is not None:
                regime_str = (
                    f"weights={mani.get('weights', {})}, "
                    f"rate={mani.get('exploration_rate', 'n/a')}, "
                    f"n_eps={mani.get('n_episodes', 'n/a')}, "
                    f"corpus={mani.get('corpus_id', 'n/a')}"
                )
                path_lines.append(f"  - `{p.name}` — {regime_str}")
            else:
                path_lines.append(f"  - `{p.name}` (no manifest)")
    else:
        title = f"Ergon promotion ledger: {path_or_paths.name}"
        path_lines = [f"- Path: `{path_or_paths}`"]
        mani = load_manifest(path_or_paths)
        if mani is not None:
            path_lines.append(f"- Regime: weights={mani.get('weights', {})}, "
                              f"rate={mani.get('exploration_rate', 'n/a')}, "
                              f"n_eps={mani.get('n_episodes', 'n/a')}, "
                              f"corpus={mani.get('corpus_id', 'n/a')}")

    lines = [
        f"# {title}",
        "",
        *path_lines,
        f"- Total substrate-PASS records: **{summary['n_records']}**",
        f"- Unique predicates: **{summary['n_unique_predicates']}**",
        f"- Seeds: {summary['seeds']}",
        f"- Trials: {summary.get('trials', ['unknown'])}",
        f"- Episode span: {summary['episode_min']}-{summary['episode_max']}",
        "",
        "## Classification",
        "",
        f"| class | count |",
        f"|---|---|",
    ]
    for cls in (
        "obstruction_exact", "secondary_exact",
        "obstruction_discriminator_only", "secondary_discriminator_only",
        "non_planted",
    ):
        lines.append(f"| {cls} | {c.get(cls, 0)} |")

    lines += [
        "",
        "## Substrate-PASS by operator class",
        "",
        "| operator_class | count |",
        "|---|---|",
    ]
    for op, n in sorted(o.items(), key=lambda x: -x[1]):
        lines.append(f"| {op} | {n} |")

    lines += ["", "## Top-5 most-frequent unique predicates", ""]
    for u in summary["most_frequent"]:
        lines.append(
            f"- n_occ={u['n_occurrences']:>3d}, lift={u['lift']:.2f}, "
            f"match={u['match_size']}, predicate={u['predicate']}"
        )

    lines += ["", "## Top-5 highest-lift unique predicates", ""]
    for u in summary["highest_lift"]:
        lines.append(
            f"- lift={u['lift']:>6.2f}, match={u['match_size']:>3d}, "
            f"first seen seed={u['first_seed']} ep={u['first_episode']}, "
            f"predicate={u['predicate']}"
        )

    n_non_planted_uniq = summary.get("n_unique_non_planted", 0)
    lines += [
        "",
        "## Frontier hypotheses — non-planted unique predicates",
        "",
        f"Of {summary['n_unique_predicates']} unique predicates, "
        f"**{n_non_planted_uniq}** are non-planted (don't match planted "
        "signatures or their match-set discriminators). These are the "
        "engine's hypothesis-generator output beyond confirming known "
        "ground truth.",
        "",
        "### Top-10 non-planted by lift",
        "",
    ]
    for u in summary.get("top_non_planted_by_lift", []):
        lines.append(
            f"- lift={u['lift']:>6.2f}, match={u['match_size']:>3d}, "
            f"first seen seed={u['first_seed']} ep={u['first_episode']}, "
            f"predicate={u['predicate']}"
        )
    lines += ["", "### Top-5 non-planted by frequency", ""]
    for u in summary.get("top_non_planted_by_freq", []):
        lines.append(
            f"- n_occ={u['n_occurrences']:>3d}, lift={u['lift']:>6.2f}, "
            f"match={u['match_size']:>3d}, predicate={u['predicate']}"
        )

    return "\n".join(lines) + "\n"


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage:\n"
            "  python -m ergon.learner.tools.read_promotion_ledger "
            "<path.jsonl> [path2.jsonl ...]\n"
            "  python -m ergon.learner.tools.read_promotion_ledger --all "
            "[<dir>]\n"
            "    (--all: scan dir for *.jsonl; default dir is "
            "ergon/learner/trials/ledgers/)"
        )
        return 2

    if argv[1] == "--all":
        scan_dir = Path(argv[2]) if len(argv) > 2 else Path(
            "ergon/learner/trials/ledgers"
        )
        if not scan_dir.exists():
            print(f"Directory not found: {scan_dir}")
            return 1
        paths = sorted(scan_dir.glob("*.jsonl"))
        if not paths:
            print(f"No *.jsonl ledgers found in {scan_dir}")
            return 1
    else:
        paths = [Path(p) for p in argv[1:]]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"Ledger not found: {p}")
        return 1

    if len(paths) == 1:
        records = load_records(paths[0])
        summary = summarize(records)
        print(render_markdown(paths[0], summary))
    else:
        records = load_and_merge_records(paths)
        summary = summarize(records)
        print(render_markdown(paths, summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
