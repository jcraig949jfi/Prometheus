"""TOOL_PARADIGM_GAP_MATRIX — Paradigm × Problem matrix with EV scoring.

Builds the M[problem, paradigm] matrix that identifies which attack angles
have never been tried on which problems. Computes Expected Information Gain
for each empty cell to prioritize exploration.

All three frontier model reviewers converged on this as the key strategic
instrument. The matrix factors themselves may reveal meta-structure of
mathematical problem-solving.

Interface:
    build_matrix(problems_path, paradigms_path, graph_path) -> dict
    score_gaps(matrix, graph) -> list[dict]  # ranked by EIG
    export_matrix(matrix, out_path) -> None

Forged: 2026-04-21 | Tier: 1 (Python) | Frontier-model-recommended
"""
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

import numpy as np


# ─── Paradigm-Problem classification keywords ──────────────────────────────

# Maps paradigm IDs to keyword sets for detecting if a paradigm has been
# applied to a problem (based on problem description / literature)
PARADIGM_KEYWORDS = {
    "P01": {"modularity", "galois representation", "langlands", "automorphic", "base change", "deformation", "categorif"},
    "P02": {"cohomolog", "obstruction", "brauer", "selmer", "sha", "local-global", "etale"},
    "P03": {"symmetry", "group action", "representation", "invariant theory", "equivariant", "character"},
    "P04": {"spectral", "eigenvalue", "random matrix", "gue", "goe", "trace formula", "laplacian"},
    "P05": {"analytic continuation", "l-function", "zeta", "functional equation", "euler product"},
    "P06": {"flow", "ricci", "curvature", "deformation", "surgery", "metric"},
    "P07": {"descent", "induction", "well-order", "noetherian", "filtration"},
    "P08": {"probabilistic", "random", "lovasz", "expected value", "second moment", "janson"},
    "P09": {"computation", "verified", "exhaustive", "sat ", "computer proof", "enumerate"},
    "P10": {"formal", "lean", "coq", "isabelle", "proof assistant", "verified"},
    "P11": {"sieve", "selberg sieve", "large sieve", "brun", "parity"},
    "P12": {"height", "faltings", "bombieri", "diophantine", "rational point", "mordell"},
    "P13": {"tropical", "degeneration", "piecewise-linear", "newton polygon", "toric"},
    "P14": {"forcing", "independence", "consistency", "large cardinal", "zfc"},
    "P15": {"tensor", "decomposition", "multilinear", "bond dimension", "mps"},
    "P16": {"mod p", "frobenius", "chebotarev", "arithmetic statistics", "distribution"},
    "P17": {"variational", "extremal", "sdp", "optimization", "flag algebra", "min-max"},
    "P18": {"operad", "category", "infinity-category", "topos", "derived", "functor"},
    "P19": {"o-minimal", "model theory", "definab", "pila-wilkie", "tame"},
    "P20": {"ergodic", "dynamical", "mixing", "recurrence", "invariant measure", "orbit"},
    "P21": {"gowers norm", "higher-order fourier", "inverse theorem", "nilsequence", "regularity"},
    "P22": {"entropy", "information", "kolmogorov", "compression", "shearer", "submodular"},
    "P23": {"proof mining", "reverse math", "bound extraction", "proof-theoretic"},
    "P24": {"renormalization", "scale", "fixed point", "universality", "coarse-grain", "rg flow"},
}


def build_matrix(problems_path: str, paradigms_path: str,
                 graph_path: Optional[str] = None) -> dict:
    """Build the paradigm × problem matrix.

    Parameters
    ----------
    problems_path : str — path to questions.jsonl
    paradigms_path : str — path to attack_paradigms.json
    graph_path : str, optional — path to math_graph.json for centrality

    Returns
    -------
    dict with:
        matrix : dict[str, dict[str, float]]  # problem_id -> paradigm_id -> score
        problems : list[dict]  # problem metadata
        paradigms : list[dict]  # paradigm metadata
        stats : dict  # summary statistics
    """
    # Load problems
    problems = []
    prob_path = Path(problems_path)
    if prob_path.exists():
        for line in prob_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                problems.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Load paradigms
    paradigms_data = json.loads(Path(paradigms_path).read_text(encoding="utf-8"))
    paradigms = paradigms_data.get("paradigms", [])
    paradigm_ids = [p["id"] for p in paradigms]

    # Build matrix
    matrix = {}
    for prob in problems:
        pid = prob.get("id", "")
        if not pid:
            continue

        title = str(prob.get("title", "")).lower()
        desc = str(prob.get("description", "")).lower()
        domain = str(prob.get("domain", "")).lower()
        text = f"{title} {desc} {domain}"

        row = {}
        for par_id in paradigm_ids:
            keywords = PARADIGM_KEYWORDS.get(par_id, set())
            # Score: how many keywords match
            matches = sum(1 for kw in keywords if kw in text)
            if matches >= 2:
                row[par_id] = 1.0  # strong match
            elif matches == 1:
                row[par_id] = 0.5  # partial match
            else:
                row[par_id] = 0.0  # gap (untried)

        matrix[pid] = row

    # Stats
    total_cells = len(matrix) * len(paradigm_ids)
    filled = sum(1 for row in matrix.values() for v in row.values() if v > 0)
    gaps = total_cells - filled

    return {
        "matrix": matrix,
        "problems": problems,
        "paradigms": paradigms,
        "paradigm_ids": paradigm_ids,
        "stats": {
            "n_problems": len(matrix),
            "n_paradigms": len(paradigm_ids),
            "total_cells": total_cells,
            "filled_cells": filled,
            "gap_cells": gaps,
            "density": round(filled / total_cells, 4) if total_cells > 0 else 0,
        }
    }


def score_gaps(matrix_data: dict, centrality: Optional[dict] = None) -> list:
    """Score empty cells by Expected Information Gain.

    EIG(p, a) = Importance(p) × Novelty(a, p) × Feasibility(a)

    Parameters
    ----------
    matrix_data : dict — output of build_matrix()
    centrality : dict, optional — {problem_id: betweenness_centrality}

    Returns
    -------
    list of dict, sorted by EIG descending. Each entry:
        problem_id, problem_title, paradigm_id, paradigm_name,
        importance, novelty, feasibility, eig
    """
    matrix = matrix_data["matrix"]
    paradigms = {p["id"]: p for p in matrix_data["paradigms"]}
    problems = {p.get("id", ""): p for p in matrix_data["problems"]}

    # Feasibility scores based on Prometheus status
    feasibility_map = {
        "LIVE": 1.0,
        "NEED_INFRA": 0.5,
        "OUT_OF_REACH": 0.1,
    }

    # Compute paradigm frequency (how often each paradigm appears in filled cells)
    paradigm_freq = defaultdict(float)
    for row in matrix.values():
        for par_id, score in row.items():
            if score > 0:
                paradigm_freq[par_id] += 1
    total_problems = len(matrix)

    gaps = []
    for pid, row in matrix.items():
        prob = problems.get(pid, {})
        title = prob.get("title", prob.get("name", pid))

        # Importance: use centrality if available, else uniform
        importance = centrality.get(pid, 0.01) if centrality else 0.01

        # Count how many paradigms have been applied to this problem
        applied = sum(1 for v in row.values() if v > 0)

        for par_id, score in row.items():
            if score > 0:
                continue  # not a gap

            par = paradigms.get(par_id, {})
            par_name = par.get("name", par_id)
            status = par.get("prometheus_status", "NEED_INFRA")

            # Novelty: 1 - (frequency of this paradigm / total)
            freq = paradigm_freq.get(par_id, 0) / max(total_problems, 1)
            novelty = 1.0 - freq

            # Feasibility
            feasibility = feasibility_map.get(status, 0.3)

            # Neighbor success bonus: if paradigm works on related problems
            # (simplified: more applications = more likely to work generally)
            success_rate = freq  # crude proxy

            # EIG
            eig = importance * novelty * feasibility * (1.0 + success_rate)

            gaps.append({
                "problem_id": pid,
                "problem_title": title[:60],
                "paradigm_id": par_id,
                "paradigm_name": par_name,
                "importance": round(importance, 6),
                "novelty": round(novelty, 4),
                "feasibility": feasibility,
                "eig": round(eig, 6),
                "applied_count": applied,
            })

    # Sort by EIG
    gaps.sort(key=lambda x: -x["eig"])
    return gaps


def export_matrix(matrix_data: dict, gaps: list, out_path: str) -> None:
    """Export matrix and gap analysis as JSON + markdown."""
    out = Path(out_path)
    out.mkdir(parents=True, exist_ok=True)

    # JSON
    (out / "paradigm_gap_matrix.json").write_text(
        json.dumps({
            "stats": matrix_data["stats"],
            "top_50_gaps": gaps[:50],
        }, indent=2), encoding="utf-8"
    )

    # Markdown
    lines = [
        "# Paradigm Gap Matrix — Strategic Targeting",
        f"## {matrix_data['stats']['n_problems']} problems × "
        f"{matrix_data['stats']['n_paradigms']} paradigms",
        "",
        f"- Filled cells: {matrix_data['stats']['filled_cells']} "
        f"({matrix_data['stats']['density']*100:.1f}%)",
        f"- Gap cells: {matrix_data['stats']['gap_cells']}",
        "",
        "---",
        "",
        "## Top 30 Highest-EIG Gaps (untried paradigm × problem combinations)",
        "",
        "| Rank | Problem | Paradigm | EIG | Novelty | Feasibility |",
        "|------|---------|----------|-----|---------|-------------|",
    ]
    for i, g in enumerate(gaps[:30]):
        lines.append(
            f"| {i+1} | {g['problem_title'][:40]} | "
            f"{g['paradigm_name']} | {g['eig']:.6f} | "
            f"{g['novelty']:.2f} | {g['feasibility']:.1f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Paradigm Coverage Distribution",
        "",
        "| Paradigm | Applied To | Coverage |",
        "|----------|-----------|----------|",
    ])
    par_counts = defaultdict(int)
    for row in matrix_data["matrix"].values():
        for par_id, v in row.items():
            if v > 0:
                par_counts[par_id] += 1
    n = matrix_data["stats"]["n_problems"]
    for par in matrix_data["paradigms"]:
        pid = par["id"]
        cnt = par_counts.get(pid, 0)
        pct = cnt / n * 100 if n > 0 else 0
        lines.append(f"| {pid}: {par['name']} | {cnt} | {pct:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "*Generated by Techne paradigm_gap_matrix.py — "
        "frontier-model-recommended strategic instrument*",
    ])

    (out / "PARADIGM_GAP_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Exported: {out / 'PARADIGM_GAP_REPORT.md'}")


if __name__ == "__main__":
    import sys
    base = Path(".")
    if len(sys.argv) > 1:
        base = Path(sys.argv[1])

    print("Paradigm Gap Matrix Builder")
    print("=" * 50)

    m = build_matrix(
        str(base / "aporia" / "mathematics" / "questions.jsonl"),
        str(base / "aporia" / "data" / "attack_paradigms.json"),
    )
    print(f"Matrix: {m['stats']['n_problems']} × {m['stats']['n_paradigms']}")
    print(f"Density: {m['stats']['density']*100:.1f}% "
          f"({m['stats']['filled_cells']} filled, {m['stats']['gap_cells']} gaps)")

    # Load centrality from math graph if available
    centrality = {}
    graph_path = base / "techne" / "math-graph-out" / "math_analysis.json"
    if graph_path.exists():
        analysis = json.loads(graph_path.read_text(encoding="utf-8"))
        for b in analysis.get("bridge_nodes", []):
            # Map node IDs back to problem IDs
            nid = b["id"]
            centrality[nid] = b["betweenness"]
        print(f"Loaded centrality for {len(centrality)} nodes")

    gaps = score_gaps(m, centrality)
    print(f"\nTop 10 highest-EIG gaps:")
    for i, g in enumerate(gaps[:10]):
        print(f"  {i+1}. {g['paradigm_name']:30s} × {g['problem_title'][:40]}")
        print(f"     EIG={g['eig']:.6f}  novelty={g['novelty']:.2f}  "
              f"feasibility={g['feasibility']}")

    export_matrix(m, gaps, str(base / "techne" / "paradigm-gap-out"))
