"""ergon.learner.tools.characterize_clusters — cluster characterization tool.

Per Iter 32 / Task #96. Given a promotion ledger AND a corpus, produces a
"cluster characterization report" for the top-K unique high-confidence
predicates: full record details for each match-set, feature distributions,
parsimony alternatives.

Use case: Charon (or any consumer agent) wants to validate Ergon's
findings without re-running the engine. This tool consumes the existing
ledger + corpus snapshot and emits a markdown report.

Usage:
    python -m ergon.learner.tools.characterize_clusters \
        ergon/learner/trials/ledgers/trial_3_iter28_a149_u05_canonical_ledger.jsonl \
        --corpus a149_real

The --corpus flag selects which corpus loader to use (limited to known
domains for safety; add new corpora as a149-style modules are built).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# Corpus loader registry
def _load_a149_real():
    from ergon.learner.trials._a149_real_corpus import load_a149_real_corpus
    return load_a149_real_corpus()


def _load_obstruction_synthetic():
    from prometheus_math._obstruction_corpus import OBSTRUCTION_CORPUS
    return OBSTRUCTION_CORPUS


CORPUS_LOADERS: Dict[str, Callable[[], Any]] = {
    "a149_real": _load_a149_real,
    "obstruction_synthetic": _load_obstruction_synthetic,
}


def _matches(features: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    return all(features.get(k) == v for k, v in pred.items())


def find_top_clusters(
    ledger_records: List[Dict[str, Any]],
    corpus: List[Any],
    min_lift: float = 10.0,
    min_match: int = 3,
    require_full_kill_rate: bool = True,
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    """Identify high-confidence cluster predicates from the ledger."""
    by_hash: Dict[str, Dict[str, Any]] = {}
    for r in ledger_records:
        ch = r.get("genome_content_hash")
        if ch and ch not in by_hash:
            by_hash[ch] = {
                "predicate": r["predicate"],
                "lift": r["lift"],
                "match_size": r["match_size"],
                "n_occurrences": 1,
                "first_seed": r["seed"],
                "first_episode": r["episode"],
                "extra": r.get("extra", {}),
            }
        elif ch:
            by_hash[ch]["n_occurrences"] += 1

    candidates = []
    for u in by_hash.values():
        if u["lift"] < min_lift or u["match_size"] < min_match:
            continue
        kr = u["extra"].get("matched_kill_rate")
        if kr is None:
            continue
        if require_full_kill_rate and kr < 0.999:
            continue
        # Recompute against corpus to verify match_size is real
        matches = [
            e for e in corpus if _matches(e.features(), u["predicate"])
        ]
        u["actual_match_records"] = matches
        u["actual_match_size"] = len(matches)
        u["matched_kill_rate"] = kr
        candidates.append(u)

    # Group by match-set (deduplication: predicates with same match-set
    # are equivalent)
    by_match_set: Dict[frozenset, List[Dict[str, Any]]] = defaultdict(list)
    for c in candidates:
        key = frozenset(id(e) for e in c["actual_match_records"])
        by_match_set[key].append(c)

    clusters = []
    for key, members in by_match_set.items():
        # Pick the simplest predicate in the cluster (fewest conjuncts)
        simplest = min(members, key=lambda m: len(m["predicate"]))
        clusters.append({
            "match_records": members[0]["actual_match_records"],
            "match_size": members[0]["actual_match_size"],
            "matched_kill_rate": members[0]["matched_kill_rate"],
            "lift": members[0]["lift"],
            "simplest_predicate": simplest["predicate"],
            "n_simplest_conjuncts": len(simplest["predicate"]),
            "n_predicate_variants": len(members),
            "all_variants": [m["predicate"] for m in members],
            "first_seen_seed": simplest["first_seed"],
            "first_seen_episode": simplest["first_episode"],
        })

    clusters.sort(key=lambda c: -c["lift"])
    return clusters[:top_k]


def find_parsimony_alternatives(
    pred: Dict[str, Any], corpus: List[Any], max_drop: int = 3
) -> List[Dict[str, Any]]:
    """Try removing 1..max_drop conjuncts and check match-set equivalence."""
    target_match = {
        id(e) for e in corpus if _matches(e.features(), pred)
    }
    if not target_match:
        return []

    keys = list(pred.keys())
    alternatives = []
    for drop in range(1, min(max_drop + 1, len(keys))):
        for subset in combinations(keys, len(keys) - drop):
            sub_pred = {k: pred[k] for k in subset}
            sub_match = {
                id(e) for e in corpus if _matches(e.features(), sub_pred)
            }
            if sub_match == target_match:
                alternatives.append({
                    "predicate": sub_pred,
                    "n_conjuncts": len(sub_pred),
                    "dropped_conjuncts": drop,
                })
    return sorted(alternatives, key=lambda a: a["n_conjuncts"])


def render_cluster_report(
    clusters: List[Dict[str, Any]],
    corpus: List[Any],
    ledger_path: Path,
    corpus_id: str,
    feature_keys: Optional[List[str]] = None,
) -> str:
    """Render a markdown report for cluster characterization."""
    lines = [
        f"# Cluster characterization: {ledger_path.name}",
        "",
        f"- Corpus: `{corpus_id}` ({len(corpus)} records)",
        f"- Ledger: `{ledger_path}`",
        f"- High-confidence clusters found: **{len(clusters)}**",
        "",
    ]

    for i, c in enumerate(clusters, start=1):
        lines.append(f"## Cluster #{i}: lift={c['lift']:.2f}, match={c['match_size']}, kr={c['matched_kill_rate']:.3f}")
        lines.append("")
        lines.append(f"**Simplest predicate** ({c['n_simplest_conjuncts']}-conjunct):")
        lines.append("")
        lines.append(f"```")
        lines.append(json.dumps(c["simplest_predicate"], indent=2))
        lines.append(f"```")
        lines.append("")

        # Parsimony alternatives
        alternatives = find_parsimony_alternatives(
            c["simplest_predicate"], corpus, max_drop=3
        )
        if alternatives:
            lines.append("**Match-set-equivalent shorter forms**:")
            lines.append("")
            for a in alternatives:
                lines.append(f"- {a['n_conjuncts']}-conjunct: `{a['predicate']}`")
            lines.append("")

        # Variant count
        if c["n_predicate_variants"] > 1:
            lines.append(
                f"_{c['n_predicate_variants']} predicate variants in ledger "
                "represent this cluster._"
            )
            lines.append("")

        # Match records
        records = c["match_records"]
        lines.append(f"**Match records** ({len(records)}):")
        lines.append("")
        if not records:
            lines.append("(empty match-set)")
        else:
            # Try to use seq_id if present
            sample = records[0]
            has_seq_id = hasattr(sample, "seq_id")
            if feature_keys is None:
                # Auto-discover features
                feature_keys = sorted(sample.features().keys())[:10]
            cols = (["seq_id"] if has_seq_id else ["idx"]) + feature_keys + ["kill_verdict"]
            if hasattr(sample, "n_kill_tests_fired"):
                cols.append("n_kill_tests")
            lines.append(f"| {' | '.join(cols)} |")
            lines.append(f"|{'|'.join('---' for _ in cols)}|")
            for j, e in enumerate(records):
                row_vals = []
                for c_name in cols:
                    if c_name == "seq_id" and has_seq_id:
                        row_vals.append(str(e.seq_id))
                    elif c_name == "idx":
                        row_vals.append(str(j))
                    elif c_name == "kill_verdict":
                        row_vals.append(str(e.kill_verdict))
                    elif c_name == "n_kill_tests" and hasattr(e, "n_kill_tests_fired"):
                        row_vals.append(str(e.n_kill_tests_fired))
                    else:
                        row_vals.append(str(e.features().get(c_name, "")))
                lines.append(f"| {' | '.join(row_vals)} |")
        lines.append("")
        lines.append(f"**First found**: seed={c['first_seen_seed']}, ep={c['first_seen_episode']}")
        lines.append("")

    return "\n".join(lines)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: python -m ergon.learner.tools.characterize_clusters "
            "<ledger.jsonl> [--corpus a149_real|obstruction_synthetic]"
        )
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"Ledger not found: {path}")
        return 1

    corpus_id = "a149_real"
    if "--corpus" in argv:
        i = argv.index("--corpus")
        if i + 1 < len(argv):
            corpus_id = argv[i + 1]

    if corpus_id not in CORPUS_LOADERS:
        print(f"Unknown corpus '{corpus_id}'. Known: {list(CORPUS_LOADERS.keys())}")
        return 1

    print(f"Loading {corpus_id} corpus...", file=sys.stderr)
    corpus = CORPUS_LOADERS[corpus_id]()

    print(f"Loading ledger {path}...", file=sys.stderr)
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Finding top clusters from {len(records)} records...", file=sys.stderr)
    clusters = find_top_clusters(records, corpus)

    report = render_cluster_report(clusters, corpus, path, corpus_id)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
