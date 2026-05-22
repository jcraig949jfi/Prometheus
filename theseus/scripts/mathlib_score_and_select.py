"""Score mathlib4 signature candidates and cut to top 200.

Fire #50 of the #2 multi-fire build. Reads the 15,448-row JSONL from
theseus/handoff/mathlib_primitive_candidates.jsonl (from Fire #49's
extractor), scores each candidate on a hybrid heuristic, sorts
descending, writes top-200 to a curated JSONL ready for Fire #51's
primitive-spec stub generator.

Scoring components (each in [0, 1] before final weighted sum):
  - domain_weight: NumberTheory=1.0, EllipticCurve=1.0, RingTheory=0.7,
    FieldTheory=0.7, Geometry=0.5, Other=0.3
  - kind_weight: theorem=1.0, lemma=0.7, def=0.5
  - statement_complexity: min(len(sig)/300, 1.0) — longer sigs encode
    more structure but cap at "verbose" threshold
  - name_simplicity: 1 - min(name.count(".")/3, 1) — shorter, less-dotted
    names are usually foundational
  - structural_bonus: +0.2 if signature contains "↔" "→" "=" "≤" "≥"
    (relational content) — keeps numeric/structural claims over pure
    machinery
  - import_centrality: incoming edges from import_graph.json, normalized
    to [0, 1]. Sparse data so this is a small contributor.

Final score = sum(weight × component). Top-N selected.

Output: techne/handoff/mathlib_primitive_candidates_top200.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from theseus.config import THESEUS_ROOT


REPO_ROOT = THESEUS_ROOT.parent
INPUT_DEFAULT = (
    REPO_ROOT / "techne" / "handoff" / "mathlib_primitive_candidates.jsonl"
)
OUTPUT_DEFAULT = (
    REPO_ROOT / "techne" / "handoff"
    / "mathlib_primitive_candidates_top200.jsonl"
)
IMPORT_GRAPH_PATH = (
    REPO_ROOT / "cartography" / "mathlib" / "data" / "import_graph.json"
)


DOMAIN_WEIGHTS = {
    "NumberTheory": 1.0,
    "AlgebraicGeometry": 1.0,  # incl. EllipticCurve sub-tree
    "RingTheory": 0.7,
    "FieldTheory": 0.7,
    "Geometry": 0.5,
}
KIND_WEIGHTS = {"theorem": 1.0, "lemma": 0.7, "def": 0.5}
RELATIONAL_SYMBOLS = ("↔", "→", "=", "≤", "≥", "↦", "∈", "⊆")


def _load_import_centrality() -> Dict[str, int]:
    """Build incoming-edge count per node from the existing import graph."""
    if not IMPORT_GRAPH_PATH.exists():
        return {}
    try:
        with IMPORT_GRAPH_PATH.open("r", encoding="utf-8") as f:
            g = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    counts: Counter = Counter()
    for edge in g.get("edges", []):
        if len(edge) == 2:
            _, dst = edge
            counts[dst] += 1
    return dict(counts)


def _source_path_to_node(source_path: str) -> str:
    """Convert 'NumberTheory/ADEInequality.lean' to 'Mathlib.NumberTheory.ADEInequality'."""
    if source_path.endswith(".lean"):
        source_path = source_path[: -len(".lean")]
    parts = source_path.replace("\\", "/").split("/")
    return "Mathlib." + ".".join(parts)


def _domain_weight(domain: str) -> float:
    return DOMAIN_WEIGHTS.get(domain, 0.3)


def _kind_weight(kind: str) -> float:
    return KIND_WEIGHTS.get(kind, 0.5)


def _statement_complexity(signature: str) -> float:
    return min(len(signature) / 300.0, 1.0)


def _name_simplicity(name: str) -> float:
    dots = name.count(".")
    return max(0.0, 1.0 - min(dots / 3.0, 1.0))


def _structural_bonus(signature: str) -> float:
    return 0.2 if any(s in signature for s in RELATIONAL_SYMBOLS) else 0.0


def _normalize_centrality(counts: Dict[str, int]) -> Dict[str, float]:
    if not counts:
        return {}
    max_c = max(counts.values())
    if max_c == 0:
        return {k: 0.0 for k in counts}
    return {k: v / max_c for k, v in counts.items()}


def score_candidate(
    rec: Dict[str, Any],
    centrality_norm: Dict[str, float],
) -> float:
    domain = rec.get("domain", "")
    kind = rec.get("kind", "")
    sig = rec.get("signature", "")
    name = rec.get("name", "")
    source = rec.get("source_path", "")

    centrality = centrality_norm.get(_source_path_to_node(source), 0.0)

    score = (
        2.0 * _domain_weight(domain)
        + 1.5 * _kind_weight(kind)
        + 1.0 * _statement_complexity(sig)
        + 0.5 * _name_simplicity(name)
        + 1.0 * _structural_bonus(sig)
        + 0.5 * centrality
    )
    return score


DOMAIN_QUOTAS = {
    "NumberTheory": 70,
    "AlgebraicGeometry": 50,
    "RingTheory": 40,
    "FieldTheory": 25,
    "Geometry": 15,
}


def score_and_select(
    input_path: Path = INPUT_DEFAULT,
    output_path: Path = OUTPUT_DEFAULT,
    top_n: int = 200,
) -> Dict[str, Any]:
    """Read candidates, score, write top-N to output. Returns summary.

    Stratified by domain (per DOMAIN_QUOTAS) so the top-N reflects
    coverage breadth, not single-domain dominance. Quotas total to
    top_n; if a domain is short of its quota, the remainder is added
    back to NumberTheory (the deepest pool).
    """
    if not input_path.exists():
        return {
            "error": f"input not found: {input_path}",
            "n_total": 0,
            "n_selected": 0,
        }

    centrality_raw = _load_import_centrality()
    centrality_norm = _normalize_centrality(centrality_raw)

    candidates: List[Dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Dedupe by name (keep highest-scored copy if same name appears twice)
    name_to_best: Dict[str, tuple] = {}
    for rec in candidates:
        s = score_candidate(rec, centrality_norm)
        name = rec.get("name", "")
        if name not in name_to_best or s > name_to_best[name][0]:
            name_to_best[name] = (s, rec)

    # Group by domain
    by_domain: Dict[str, List[tuple]] = {}
    for s, rec in name_to_best.values():
        d = rec.get("domain", "Other")
        by_domain.setdefault(d, []).append((s, rec))
    for d in by_domain:
        by_domain[d].sort(key=lambda x: -x[0])

    # Apply quotas; spillover goes to NumberTheory (deepest pool)
    top: List[tuple] = []
    spillover = 0
    for domain, quota in DOMAIN_QUOTAS.items():
        available = by_domain.get(domain, [])
        take = min(quota, len(available))
        top.extend(available[:take])
        if take < quota:
            spillover += quota - take

    if spillover > 0:
        nt = by_domain.get("NumberTheory", [])
        # Skip already-taken NT records
        already_nt = sum(1 for _, r in top if r.get("domain") == "NumberTheory")
        top.extend(nt[already_nt:already_nt + spillover])

    top.sort(key=lambda x: -x[0])
    top = top[:top_n]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for s, rec in top:
            out = dict(rec)
            out["score"] = round(s, 4)
            f.write(json.dumps(out, sort_keys=True) + "\n")

    by_domain: Counter = Counter()
    by_kind: Counter = Counter()
    for _, rec in top:
        by_domain[rec.get("domain", "?")] += 1
        by_kind[rec.get("kind", "?")] += 1

    return {
        "n_total_candidates": len(candidates),
        "n_unique_names": len(name_to_best),
        "n_selected": len(top),
        "by_domain_top": dict(by_domain),
        "by_kind_top": dict(by_kind),
        "import_graph_nodes_with_incoming": len(centrality_raw),
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "output_path": str(output_path),
    }


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.mathlib_score_and_select")
    p.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    p.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    p.add_argument("--top-n", type=int, default=200)
    args = p.parse_args()

    summary = score_and_select(
        input_path=args.input,
        output_path=args.output,
        top_n=args.top_n,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
