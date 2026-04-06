"""
Tensor Review — Computational quality audit of each dataset.
==============================================================
For each dataset in the registry, computes:
  - Coverage: how many objects, what % have complete data
  - Variance: do numerical fields have sufficient spread for testing
  - Connectivity: for graph datasets, edge density and component count
  - Searchability: do search functions return non-trivial results
  - Suggestions: what data could be added to improve quality

NO LLM involved. Pure computation. Output: convergence/reports/tensor_review_{date}.md

Usage:
    from tensor_review import run_tensor_review
    report = run_tensor_review()

Or standalone:
    python tensor_review.py
"""

import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from search_engine import (DATASET_REGISTRY, available_datasets, dispatch_search,
                           inventory, _get_duck, _load_oeis, _oeis_cache,
                           _load_mathlib, _mathlib_graph, _load_metamath,
                           _metamath_cache, _load_materials, _materials_cache,
                           OEIS_STRIPPED)

REPORT_DIR = Path(__file__).resolve().parents[2] / "convergence" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def review_oeis() -> dict:
    """Audit OEIS dataset quality."""
    _load_oeis()
    if not _oeis_cache:
        return {"status": "MISSING", "n_objects": 0}

    n = len(_oeis_cache)
    term_counts = [len(terms) for terms in _oeis_cache.values()]
    term_arr = np.array(term_counts)

    # Check for sequences with very few terms
    short = sum(1 for t in term_counts if t < 10)
    long = sum(1 for t in term_counts if t >= 50)

    # Growth rate diversity
    sample_ids = list(_oeis_cache.keys())[:1000]
    growth_rates = []
    for sid in sample_ids:
        terms = _oeis_cache[sid]
        pos = [t for t in terms[:20] if t > 0]
        if len(pos) >= 3:
            ratios = [pos[i+1]/pos[i] for i in range(min(5, len(pos)-1)) if pos[i] > 0]
            if ratios:
                growth_rates.append(np.mean(ratios))

    suggestions = []
    if short / n > 0.3:
        suggestions.append(f"30%+ sequences have <10 terms — consider filtering or enriching")
    suggestions.append("OEIS names.gz is corrupted (HTML, not gzip) — keyword search is disabled")
    suggestions.append("Cross-reference data (b-files, formulas) not ingested — high-value enrichment")

    return {
        "status": "OK",
        "n_objects": n,
        "term_stats": {
            "mean": round(float(term_arr.mean()), 1),
            "median": int(np.median(term_arr)),
            "min": int(term_arr.min()),
            "max": int(term_arr.max()),
            "short_pct": round(short / n * 100, 1),
            "long_pct": round(long / n * 100, 1),
        },
        "growth_diversity": {
            "n_sampled": len(growth_rates),
            "mean_ratio": round(float(np.mean(growth_rates)), 3) if growth_rates else 0,
            "std_ratio": round(float(np.std(growth_rates)), 3) if growth_rates else 0,
        },
        "suggestions": suggestions,
    }


def review_lmfdb() -> dict:
    """Audit LMFDB/Charon DuckDB quality."""
    try:
        con = _get_duck()
    except FileNotFoundError:
        return {"status": "MISSING", "n_objects": 0}

    total = con.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
    types = con.execute("SELECT object_type, COUNT(*) FROM objects GROUP BY object_type").fetchall()

    # Invariant vector completeness
    with_vec = con.execute("SELECT COUNT(*) FROM objects WHERE invariant_vector IS NOT NULL").fetchone()[0]

    # Conductor distribution stats
    conds = con.execute("SELECT conductor FROM objects WHERE conductor IS NOT NULL").fetchall()
    cond_arr = np.array([c[0] for c in conds], dtype=float)

    # Rank distribution (EC only)
    ranks = con.execute("""
        SELECT json_extract_string(properties, '$.rank') as r, COUNT(*)
        FROM objects WHERE object_type = 'elliptic_curve'
        GROUP BY r
    """).fetchall()

    con.close()

    suggestions = []
    vec_pct = with_vec / total * 100 if total > 0 else 0
    if vec_pct < 80:
        suggestions.append(f"Only {vec_pct:.0f}% have invariant vectors — enrichment opportunity")
    if not any(t == "genus2_curve" for t, _ in types):
        suggestions.append("No genus-2 curves ingested — high-value for cross-family testing")
    else:
        g2_count = next((c for t, c in types if t == "genus2_curve"), 0)
        if g2_count < 5000:
            suggestions.append(f"Only {g2_count} genus-2 curves — consider expanding")
    suggestions.append("Per-object zero vectors (from charon.duckdb) could enable spectral searches")

    return {
        "status": "OK",
        "n_objects": total,
        "type_counts": {t: c for t, c in types},
        "invariant_vector_pct": round(vec_pct, 1),
        "conductor_stats": {
            "mean": round(float(cond_arr.mean()), 1),
            "median": int(np.median(cond_arr)),
            "min": int(cond_arr.min()),
            "max": int(cond_arr.max()),
        },
        "rank_distribution": {r: c for r, c in ranks},
        "suggestions": suggestions,
    }


def review_mathlib() -> dict:
    """Audit mathlib graph quality."""
    _load_mathlib()
    if not _mathlib_graph:
        return {"status": "MISSING", "n_objects": 0}

    nodes = _mathlib_graph.get("nodes", [])
    edges = _mathlib_graph.get("edges", [])
    n_nodes = len(nodes)
    n_edges = len(edges)
    density = n_edges / max(n_nodes * (n_nodes - 1), 1)

    # Namespace distribution
    ns_counts = {}
    for node in nodes:
        name = node if isinstance(node, str) else node.get("name", "")
        parts = name.split(".")
        if len(parts) >= 2:
            ns = parts[1] if parts[0] == "Mathlib" else parts[0]
            ns_counts[ns] = ns_counts.get(ns, 0) + 1

    top_ns = sorted(ns_counts.items(), key=lambda x: -x[1])[:10]

    suggestions = []
    if n_edges / n_nodes < 1:
        suggestions.append(f"Only {n_edges/n_nodes:.1f} edges/node — import extraction may be incomplete")
    suggestions.append("Theorem-level content not indexed — only file-level imports")
    suggestions.append("Adding theorem statements would enable semantic search")

    return {
        "status": "OK",
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "density": round(density, 6),
        "edges_per_node": round(n_edges / max(n_nodes, 1), 2),
        "top_namespaces": {k: v for k, v in top_ns},
        "suggestions": suggestions,
    }


def review_metamath() -> dict:
    """Audit Metamath theorem index quality."""
    _load_metamath()
    if not _metamath_cache:
        return {"status": "MISSING", "n_objects": 0}

    n = len(_metamath_cache)

    # Label length distribution
    if isinstance(_metamath_cache[0], str):
        lengths = [len(t) for t in _metamath_cache]
    else:
        lengths = [len(t.get("label", "")) for t in _metamath_cache]

    suggestions = []
    suggestions.append("Only theorem labels indexed — no statement content or proof structure")
    suggestions.append("Adding axiom/theorem dependency graph would enable structural search")

    return {
        "status": "OK",
        "n_theorems": n,
        "label_length_stats": {
            "mean": round(float(np.mean(lengths)), 1),
            "median": int(np.median(lengths)),
        },
        "suggestions": suggestions,
    }


def review_materials() -> dict:
    """Audit Materials Project dataset quality."""
    _load_materials()
    if not _materials_cache:
        return {"status": "MISSING", "n_objects": 0}

    n = len(_materials_cache)

    # Field completeness
    fields = ["band_gap", "formation_energy_per_atom", "crystal_system", "spacegroup"]
    completeness = {}
    for f in fields:
        count = sum(1 for m in _materials_cache if f in m and m[f] is not None)
        completeness[f] = round(count / n * 100, 1)

    # Band gap distribution
    bgs = [m["band_gap"] for m in _materials_cache
           if "band_gap" in m and m["band_gap"] is not None
           and isinstance(m["band_gap"], (int, float))]
    bg_arr = np.array(bgs) if bgs else np.array([])

    suggestions = []
    if n < 5000:
        suggestions.append(f"Only {n} structures — Materials Project has 150K+, expand via API")
    for f, pct in completeness.items():
        if pct < 80:
            suggestions.append(f"{f} only {pct}% complete")

    return {
        "status": "OK",
        "n_structures": n,
        "field_completeness": completeness,
        "band_gap_stats": {
            "n_with_bg": len(bgs),
            "mean": round(float(bg_arr.mean()), 3) if len(bg_arr) > 0 else None,
            "std": round(float(bg_arr.std()), 3) if len(bg_arr) > 0 else None,
        } if len(bg_arr) > 0 else {},
        "suggestions": suggestions,
    }


REVIEWERS = {
    "oeis": review_oeis,
    "lmfdb": review_lmfdb,
    "mathlib": review_mathlib,
    "metamath": review_metamath,
    "materials": review_materials,
}


def run_tensor_review() -> Path:
    """Run computational quality review on all datasets. Returns report path."""
    t0 = time.time()
    now = datetime.now()
    report_path = REPORT_DIR / f"tensor_review_{now.strftime('%Y%m%d-%H%M%S')}.md"

    results = {}
    for name, reviewer in REVIEWERS.items():
        print(f"  Reviewing {name}...")
        try:
            results[name] = reviewer()
        except Exception as e:
            results[name] = {"status": "ERROR", "error": str(e)}

    elapsed = time.time() - t0

    # Build report
    lines = [
        f"# Tensor Review: Dataset Quality Audit",
        f"## Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        f"## Elapsed: {elapsed:.1f}s",
        "", "---", "",
        "## Summary",
        "",
        f"| Dataset | Status | Objects | Top Suggestion |",
        f"|---------|--------|---------|----------------|",
    ]

    all_suggestions = []
    for name, r in results.items():
        status = r.get("status", "?")
        n = r.get("n_objects", r.get("n_nodes", r.get("n_theorems", r.get("n_structures", "?"))))
        sugs = r.get("suggestions", [])
        top_sug = sugs[0][:60] if sugs else "—"
        lines.append(f"| {name} | {status} | {n} | {top_sug} |")
        for s in sugs:
            all_suggestions.append(f"- **{name}**: {s}")

    lines.extend(["", "---", ""])

    # Per-dataset detail
    for name, r in results.items():
        lines.append(f"## {name.upper()}")
        lines.append("")

        # Dump key stats (skip suggestions, show separately)
        for k, v in r.items():
            if k in ("status", "suggestions"):
                continue
            if isinstance(v, dict):
                lines.append(f"**{k}:**")
                for kk, vv in v.items():
                    lines.append(f"  - {kk}: {vv}")
            else:
                lines.append(f"**{k}:** {v}")
        lines.extend(["", "---", ""])

    # All suggestions
    lines.append("## All Improvement Suggestions")
    lines.append("")
    lines.extend(all_suggestions)
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    # Feed suggestions into the ledger
    try:
        from suggestions import add_from_tensor_review
        add_from_tensor_review(results)
    except Exception as e:
        print(f"  Warning: Could not update suggestions ledger: {e}")

    print(f"  Tensor review: {report_path} ({elapsed:.1f}s)")
    return report_path


if __name__ == "__main__":
    run_tensor_review()
