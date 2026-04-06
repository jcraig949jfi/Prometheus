"""
Search Engine — Cross-dataset queries for Charon/Cartography.
==============================================================
Searches real data: OEIS (392K sequences), LMFDB (336K objects via DuckDB),
mathlib (8.4K modules), Metamath (46K theorems).

Each search returns a list of SearchResult dicts with:
  {source, id, label, match_reason, data, score}
"""

import gzip
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# Paths relative to repo root
REPO = Path(__file__).resolve().parents[3]
CARTOGRAPHY = REPO / "cartography"
CHARON = REPO / "charon"

OEIS_STRIPPED = CARTOGRAPHY / "oeis" / "data" / "stripped_full.gz"
OEIS_NAMES = CARTOGRAPHY / "oeis" / "data" / "names.gz"
MATHLIB_GRAPH = CARTOGRAPHY / "mathlib" / "data" / "import_graph.json"
METAMATH_INDEX = CARTOGRAPHY / "metamath" / "data" / "theorem_list.json"
MATERIALS_JSON = CARTOGRAPHY / "physics" / "data" / "materials_project_1000.json"
KNOTS_JSON = CARTOGRAPHY / "knots" / "data" / "knots.json"
FUNGRIM_JSON = CARTOGRAPHY / "fungrim" / "data" / "fungrim_index.json"
ANTEDB_JSON = CARTOGRAPHY / "antedb" / "data" / "antedb_index.json"
CHARON_DB = CHARON / "data" / "charon.duckdb"


# ---------------------------------------------------------------------------
# OEIS Search
# ---------------------------------------------------------------------------

_oeis_cache: dict = {}  # {id: terms_list}
_oeis_names_cache: dict = {}  # {id: name}


def _load_oeis():
    """Lazy-load OEIS stripped sequences into cache."""
    if _oeis_cache:
        return
    if not OEIS_STRIPPED.exists():
        print(f"  [OEIS] WARNING: {OEIS_STRIPPED} not found")
        return
    print(f"  [OEIS] Loading {OEIS_STRIPPED.name}...")
    with gzip.open(OEIS_STRIPPED, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            seq_id = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except ValueError:
                        pass
            if terms:
                _oeis_cache[seq_id] = terms
    print(f"  [OEIS] Loaded {len(_oeis_cache):,} sequences")


def _load_oeis_names():
    """Lazy-load OEIS sequence names."""
    if _oeis_names_cache:
        return
    if not OEIS_NAMES.exists():
        return
    try:
        with gzip.open(OEIS_NAMES, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                idx = line.find(" ")
                if idx > 0:
                    _oeis_names_cache[line[:idx]] = line[idx+1:].strip()
    except Exception as e:
        print(f"  [OEIS] WARNING: Could not load names: {e}")


def oeis_search_terms(target_terms: list[int], min_match: int = 5,
                      max_results: int = 20) -> list[dict]:
    """Find OEIS sequences containing a subsequence of target terms."""
    _load_oeis()
    _load_oeis_names()
    results = []
    target_set = set(target_terms)
    for seq_id, terms in _oeis_cache.items():
        term_set = set(terms[:50])  # Compare first 50 terms
        overlap = target_set & term_set
        if len(overlap) >= min_match:
            results.append({
                "source": "OEIS",
                "id": seq_id,
                "label": _oeis_names_cache.get(seq_id, ""),
                "match_reason": f"{len(overlap)}/{len(target_terms)} terms match",
                "data": {"overlap": sorted(overlap), "first_10": terms[:10]},
                "score": len(overlap) / max(len(target_terms), 1),
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def oeis_search_keyword(keyword: str, max_results: int = 20) -> list[dict]:
    """Search OEIS sequence names by keyword."""
    _load_oeis()
    _load_oeis_names()
    keyword_lower = keyword.lower()
    results = []
    for seq_id, name in _oeis_names_cache.items():
        if keyword_lower in name.lower():
            terms = _oeis_cache.get(seq_id, [])
            results.append({
                "source": "OEIS",
                "id": seq_id,
                "label": name,
                "match_reason": f"Name contains '{keyword}'",
                "data": {"first_10": terms[:10]},
                "score": 1.0 if keyword_lower == name.lower() else 0.5,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def oeis_search_by_id(seq_id: str) -> list[dict]:
    """Fetch a specific OEIS sequence by A-number (e.g., 'A000040')."""
    _load_oeis()
    _load_oeis_names()
    # Normalize: accept 'A000040' or 'a000040' or '40'
    if not seq_id.upper().startswith("A"):
        seq_id = f"A{int(seq_id):06d}"
    else:
        seq_id = seq_id.upper()
    terms = _oeis_cache.get(seq_id)
    if not terms:
        return [{"error": f"Sequence {seq_id} not found in OEIS cache"}]
    return [{
        "source": "OEIS",
        "id": seq_id,
        "label": _oeis_names_cache.get(seq_id, ""),
        "match_reason": f"Exact match: {seq_id} ({len(terms)} terms)",
        "data": {"terms": terms[:100], "n_terms": len(terms)},
        "score": 1.0,
    }]


def oeis_find_containing(integers: list[int], min_fraction: float = 0.5,
                          max_results: int = 20) -> list[dict]:
    """Find OEIS sequences whose terms contain a high fraction of the given integers.

    Unlike oeis_search_terms (which checks overlap of sets), this checks what
    fraction of the input integers appear in each sequence — measuring how well
    the sequence 'covers' the input set.
    """
    _load_oeis()
    _load_oeis_names()
    target_set = set(integers)
    results = []
    for seq_id, terms in _oeis_cache.items():
        term_set = set(terms)
        hits = target_set & term_set
        fraction = len(hits) / len(target_set) if target_set else 0
        if fraction >= min_fraction:
            results.append({
                "source": "OEIS",
                "id": seq_id,
                "label": _oeis_names_cache.get(seq_id, ""),
                "match_reason": f"{len(hits)}/{len(target_set)} input integers found ({fraction:.0%})",
                "data": {
                    "hits": sorted(hits)[:20],
                    "misses": sorted(target_set - term_set)[:20],
                    "fraction": round(fraction, 4),
                    "n_seq_terms": len(terms),
                    "first_10": terms[:10],
                },
                "score": fraction,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def oeis_search_growth(growth_type: str = "exponential",
                       max_results: int = 20) -> list[dict]:
    """Find sequences by growth class (sub-linear, polynomial, exponential, super-exponential)."""
    _load_oeis()
    _load_oeis_names()
    results = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < 10:
            continue
        # Classify growth from first 10 positive terms
        pos = [t for t in terms[:20] if t > 0]
        if len(pos) < 5:
            continue
        ratios = [pos[i+1]/pos[i] for i in range(len(pos)-1) if pos[i] > 0]
        if not ratios:
            continue
        avg_ratio = sum(ratios) / len(ratios)
        if growth_type == "exponential" and 1.5 < avg_ratio < 10:
            score = 1.0 - abs(avg_ratio - 2.0) / 8.0
        elif growth_type == "super-exponential" and avg_ratio >= 10:
            score = min(1.0, avg_ratio / 100)
        elif growth_type == "polynomial" and 1.0 < avg_ratio <= 1.5:
            score = 1.0 - abs(avg_ratio - 1.2) / 0.5
        elif growth_type == "sub-linear" and avg_ratio <= 1.0:
            score = 1.0
        else:
            continue
        if score > 0:
            results.append({
                "source": "OEIS",
                "id": seq_id,
                "label": _oeis_names_cache.get(seq_id, ""),
                "match_reason": f"Growth class: {growth_type} (avg_ratio={avg_ratio:.2f})",
                "data": {"first_10": terms[:10], "avg_ratio": round(avg_ratio, 3)},
                "score": max(0, score),
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


# ---------------------------------------------------------------------------
# LMFDB / Charon DuckDB Search
# ---------------------------------------------------------------------------

def _get_duck():
    """Connect to Charon DuckDB."""
    import duckdb
    if not CHARON_DB.exists():
        raise FileNotFoundError(f"Charon DB not found: {CHARON_DB}")
    return duckdb.connect(str(CHARON_DB), read_only=True)


def lmfdb_search_conductor_range(low: int, high: int, object_type: str = None,
                                  max_results: int = 20) -> list[dict]:
    """Search LMFDB objects by conductor range."""
    con = _get_duck()
    query = "SELECT id, lmfdb_label, object_type, conductor, properties FROM objects WHERE conductor BETWEEN ? AND ?"
    params = [low, high]
    if object_type:
        query += " AND object_type = ?"
        params.append(object_type)
    query += " ORDER BY conductor LIMIT ?"
    params.append(max_results)
    rows = con.execute(query, params).fetchall()
    con.close()
    results = []
    for row in rows:
        props = json.loads(row[4]) if isinstance(row[4], str) else (row[4] or {})
        results.append({
            "source": "LMFDB",
            "id": str(row[0]),
            "label": row[1],
            "match_reason": f"Conductor {row[3]} in [{low},{high}], type={row[2]}",
            "data": {"object_type": row[2], "conductor": row[3],
                     "rank": props.get("rank"), "torsion": props.get("torsion_structure")},
            "score": 1.0,
        })
    return results


def lmfdb_search_rank(rank: int, conductor_max: int = 5000,
                       max_results: int = 20) -> list[dict]:
    """Search for elliptic curves of a specific rank."""
    con = _get_duck()
    rows = con.execute("""
        SELECT o.id, o.lmfdb_label, o.conductor, o.properties
        FROM objects o
        WHERE o.object_type = 'elliptic_curve'
          AND o.conductor <= ?
          AND json_extract_string(o.properties, '$.rank') = ?
        ORDER BY o.conductor
        LIMIT ?
    """, [conductor_max, str(rank), max_results]).fetchall()
    con.close()
    results = []
    for row in rows:
        props = json.loads(row[3]) if isinstance(row[3], str) else (row[3] or {})
        results.append({
            "source": "LMFDB",
            "id": str(row[0]),
            "label": row[1],
            "match_reason": f"EC rank={rank}, conductor={row[2]}",
            "data": {"conductor": row[2], "rank": rank,
                     "torsion": props.get("torsion_structure")},
            "score": 1.0,
        })
    return results


def lmfdb_stats(object_type: str = None) -> dict:
    """Get summary statistics from LMFDB store."""
    con = _get_duck()
    if object_type:
        count = con.execute("SELECT COUNT(*) FROM objects WHERE object_type = ?",
                           [object_type]).fetchone()[0]
        cond = con.execute("SELECT MIN(conductor), MAX(conductor), AVG(conductor) FROM objects WHERE object_type = ?",
                          [object_type]).fetchone()
    else:
        count = con.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
        cond = con.execute("SELECT MIN(conductor), MAX(conductor), AVG(conductor) FROM objects").fetchone()
    types = con.execute("SELECT object_type, COUNT(*) FROM objects GROUP BY object_type").fetchall()
    con.close()
    return {
        "total_objects": count,
        "conductor_range": [cond[0], cond[1]],
        "conductor_mean": round(cond[2], 1) if cond[2] else None,
        "type_counts": {t: c for t, c in types},
    }


def lmfdb_conductor_distribution(rank: int = None, conductor_max: int = 5000,
                                  bin_size: int = 100) -> list[dict]:
    """Return conductor histogram — counts per bin, optionally filtered by rank.

    Returns one result dict with arrays suitable for battery testing:
    bin_centers, counts, and full conductor list.
    """
    con = _get_duck()
    query = """
        SELECT o.conductor
        FROM objects o
        WHERE o.object_type = 'elliptic_curve'
          AND o.conductor <= ?
    """
    params = [conductor_max]
    if rank is not None:
        query += " AND json_extract_string(o.properties, '$.rank') = ?"
        params.append(str(rank))
    rows = con.execute(query, params).fetchall()
    con.close()

    conductors = sorted([int(r[0]) for r in rows])
    if not conductors:
        return [{"error": f"No EC found with rank={rank}, conductor<={conductor_max}"}]

    # Build histogram
    import numpy as np
    bins = list(range(0, conductor_max + bin_size, bin_size))
    counts, edges = np.histogram(conductors, bins=bins)

    return [{
        "source": "LMFDB",
        "id": f"conductor_dist_rank{rank}",
        "label": f"Conductor distribution (rank={rank}, N<={conductor_max})",
        "match_reason": f"{len(conductors)} ECs, {len(bins)-1} bins of width {bin_size}",
        "data": {
            "n_curves": len(conductors),
            "rank": rank,
            "conductor_max": conductor_max,
            "bin_size": bin_size,
            "bin_centers": [int(e + bin_size // 2) for e in edges[:-1]],
            "counts": [int(c) for c in counts],
            "mean_conductor": round(float(np.mean(conductors)), 1),
            "median_conductor": int(np.median(conductors)),
            "conductors_sample": conductors[:50],
        },
        "score": 1.0,
    }]


def lmfdb_rank_comparison(conductor_max: int = 5000, bin_size: int = 100) -> list[dict]:
    """Compare rank-0 vs rank-1 conductor distributions. Returns paired arrays for battery.

    This is the search that produces battery-testable numerical data:
    two arrays of conductor values (or bin counts) for direct statistical comparison.
    """
    con = _get_duck()
    rows_r0 = con.execute("""
        SELECT o.conductor FROM objects o
        WHERE o.object_type = 'elliptic_curve' AND o.conductor <= ?
          AND json_extract_string(o.properties, '$.rank') = '0'
    """, [conductor_max]).fetchall()
    rows_r1 = con.execute("""
        SELECT o.conductor FROM objects o
        WHERE o.object_type = 'elliptic_curve' AND o.conductor <= ?
          AND json_extract_string(o.properties, '$.rank') = '1'
    """, [conductor_max]).fetchall()
    con.close()

    import numpy as np
    cond_r0 = np.array([int(r[0]) for r in rows_r0], dtype=float)
    cond_r1 = np.array([int(r[0]) for r in rows_r1], dtype=float)

    if len(cond_r0) < 10 or len(cond_r1) < 10:
        return [{"error": f"Insufficient data: {len(cond_r0)} rank-0, {len(cond_r1)} rank-1"}]

    # Bin counts for distribution comparison
    bins = list(range(0, conductor_max + bin_size, bin_size))
    counts_r0, _ = np.histogram(cond_r0, bins=bins)
    counts_r1, _ = np.histogram(cond_r1, bins=bins)

    return [{
        "source": "LMFDB",
        "id": "rank_comparison",
        "label": f"Rank 0 vs 1 conductor distributions (N<={conductor_max})",
        "match_reason": f"{len(cond_r0)} rank-0 vs {len(cond_r1)} rank-1 ECs",
        "data": {
            "n_rank0": len(cond_r0),
            "n_rank1": len(cond_r1),
            "mean_r0": round(float(np.mean(cond_r0)), 1),
            "mean_r1": round(float(np.mean(cond_r1)), 1),
            "median_r0": int(np.median(cond_r0)),
            "median_r1": int(np.median(cond_r1)),
            "bin_counts_r0": [int(c) for c in counts_r0],
            "bin_counts_r1": [int(c) for c in counts_r1],
            "conductor_max": conductor_max,
            "bin_size": bin_size,
            "values_r0": cond_r0.tolist(),
            "values_r1": cond_r1.tolist(),
        },
        "score": 1.0,
    }]


def lmfdb_cross_type_neighbors(label: str, k: int = 5) -> list[dict]:
    """Find nearest cross-type neighbors for a given LMFDB object by invariant vector."""
    con = _get_duck()
    # Get the source object
    src = con.execute(
        "SELECT id, object_type, invariant_vector FROM objects WHERE lmfdb_label = ?",
        [label]
    ).fetchone()
    if not src:
        con.close()
        return [{"error": f"Object {label} not found"}]
    src_type = src[1]
    src_vec = src[2]
    if not src_vec:
        con.close()
        return [{"error": f"Object {label} has no invariant vector"}]

    # Find different-type objects with invariant vectors and compute distance
    # DuckDB supports list operations
    rows = con.execute("""
        SELECT id, lmfdb_label, object_type, conductor, invariant_vector
        FROM objects
        WHERE object_type != ? AND invariant_vector IS NOT NULL
        LIMIT 50000
    """, [src_type]).fetchall()
    con.close()

    # Compute distances in Python (DuckDB list math is limited)
    import numpy as np
    sv = np.array(src_vec[:25], dtype=float)  # First 25 primes (EC limit)
    candidates = []
    for row in rows:
        ov = row[4]
        if not ov or len(ov) < 25:
            continue
        ov_arr = np.array(ov[:25], dtype=float)
        dist = np.linalg.norm(sv - ov_arr)
        candidates.append((dist, row))
    candidates.sort(key=lambda x: x[0])

    results = []
    for dist, row in candidates[:k]:
        results.append({
            "source": "LMFDB",
            "id": str(row[0]),
            "label": row[1],
            "match_reason": f"Cross-type neighbor (L2={dist:.4f}), type={row[2]}",
            "data": {"object_type": row[2], "conductor": row[3], "distance": round(dist, 6)},
            "score": 1.0 / (1.0 + dist),
        })
    return results


# ---------------------------------------------------------------------------
# mathlib Search
# ---------------------------------------------------------------------------

_mathlib_graph: dict = {}


def _load_mathlib():
    if _mathlib_graph:
        return
    if not MATHLIB_GRAPH.exists():
        print(f"  [mathlib] WARNING: {MATHLIB_GRAPH} not found")
        return
    with open(MATHLIB_GRAPH, "r") as f:
        _mathlib_graph.update(json.load(f))
    print(f"  [mathlib] Loaded {len(_mathlib_graph.get('nodes', []))} nodes, "
          f"{len(_mathlib_graph.get('edges', []))} edges")


def mathlib_search_namespace(namespace: str, max_results: int = 20) -> list[dict]:
    """Search mathlib modules by namespace prefix."""
    _load_mathlib()
    results = []
    ns_lower = namespace.lower()
    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        if ns_lower in name.lower():
            results.append({
                "source": "mathlib",
                "id": name,
                "label": name,
                "match_reason": f"Namespace matches '{namespace}'",
                "data": {"module": name},
                "score": 1.0 if name.lower().startswith(ns_lower) else 0.5,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def mathlib_search_imports(module_name: str) -> list[dict]:
    """Find what a mathlib module imports and what imports it."""
    _load_mathlib()
    edges = _mathlib_graph.get("edges", [])
    imports = []
    imported_by = []
    for edge in edges:
        src = edge.get("source", edge[0] if isinstance(edge, list) else "")
        tgt = edge.get("target", edge[1] if isinstance(edge, list) else "")
        if module_name.lower() in str(src).lower():
            imports.append(tgt)
        if module_name.lower() in str(tgt).lower():
            imported_by.append(src)
    return [{
        "source": "mathlib",
        "id": module_name,
        "label": module_name,
        "match_reason": f"Import graph: {len(imports)} outbound, {len(imported_by)} inbound",
        "data": {"imports": imports[:10], "imported_by": imported_by[:10]},
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Metamath Search
# ---------------------------------------------------------------------------

_metamath_cache: list = []


def _load_metamath():
    if _metamath_cache:
        return
    if not METAMATH_INDEX.exists():
        print(f"  [Metamath] WARNING: {METAMATH_INDEX} not found")
        return
    with open(METAMATH_INDEX, "r") as f:
        data = json.load(f)
    _metamath_cache.extend(data if isinstance(data, list) else data.get("theorems", []))
    print(f"  [Metamath] Loaded {len(_metamath_cache):,} theorems")


def metamath_search(keyword: str, max_results: int = 20) -> list[dict]:
    """Search Metamath theorems by label keyword."""
    _load_metamath()
    kw = keyword.lower()
    results = []
    for thm in _metamath_cache:
        label = thm if isinstance(thm, str) else thm.get("label", "")
        if kw in label.lower():
            results.append({
                "source": "Metamath",
                "id": label,
                "label": label,
                "match_reason": f"Label contains '{keyword}'",
                "data": {"theorem": label},
                "score": 1.0 if kw == label.lower() else 0.5,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


# ---------------------------------------------------------------------------
# Materials Project Search
# ---------------------------------------------------------------------------

_materials_cache: list = []


def _load_materials():
    if _materials_cache:
        return
    if not MATERIALS_JSON.exists():
        print(f"  [Materials] WARNING: {MATERIALS_JSON} not found")
        return
    with open(MATERIALS_JSON, "r") as f:
        _materials_cache.extend(json.load(f))
    print(f"  [Materials] Loaded {len(_materials_cache)} structures")


def materials_search(crystal_system: str = None, band_gap_range: tuple = None,
                     max_results: int = 20) -> list[dict]:
    """Search Materials Project crystal structures."""
    _load_materials()
    results = []
    for mat in _materials_cache:
        match = True
        reasons = []
        if crystal_system:
            cs = mat.get("crystal_system", mat.get("symmetry", {}).get("crystal_system", ""))
            if crystal_system.lower() not in str(cs).lower():
                match = False
            else:
                reasons.append(f"crystal_system={cs}")
        if band_gap_range and match:
            bg = mat.get("band_gap", None)
            if bg is not None:
                if not (band_gap_range[0] <= bg <= band_gap_range[1]):
                    match = False
                else:
                    reasons.append(f"band_gap={bg:.2f}")
            else:
                match = False
        if match and reasons:
            results.append({
                "source": "MaterialsProject",
                "id": mat.get("material_id", mat.get("task_id", "")),
                "label": mat.get("pretty_formula", ""),
                "match_reason": ", ".join(reasons),
                "data": {k: mat.get(k) for k in
                         ["pretty_formula", "band_gap", "formation_energy_per_atom",
                          "crystal_system", "spacegroup"] if k in mat},
                "score": 1.0,
            })
    return results[:max_results]


# ---------------------------------------------------------------------------
# KnotInfo Search
# ---------------------------------------------------------------------------

_knots_cache: dict = {}


def _load_knots():
    if _knots_cache:
        return
    if not KNOTS_JSON.exists():
        print(f"  [Knots] WARNING: {KNOTS_JSON} not found. Run ingest_knotinfo.py first.")
        return
    data = json.loads(KNOTS_JSON.read_text(encoding="utf-8"))
    _knots_cache.update(data)
    print(f"  [Knots] Loaded {data['n_knots']:,} knots")


def knots_search_determinant(target_det: int = None, det_range: tuple = None,
                              max_results: int = 20) -> list[dict]:
    """Search knots by determinant value or range. Bridge to OEIS and LMFDB conductors."""
    _load_knots()
    results = []
    for k in _knots_cache.get("knots", []):
        det = k.get("determinant")
        if det is None:
            continue
        match = False
        if target_det is not None and det == target_det:
            match = True
        elif det_range and det_range[0] <= det <= det_range[1]:
            match = True
        if match:
            results.append({
                "source": "KnotInfo",
                "id": k["name"],
                "label": k["name"],
                "match_reason": f"determinant={det}, crossing={k['crossing_number']}",
                "data": {
                    "determinant": det,
                    "crossing_number": k["crossing_number"],
                    "alex_coeffs": k.get("alex_coeffs", [])[:10],
                    "jones_coeffs": k.get("jones_coeffs", [])[:10],
                },
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"]["crossing_number"])
    return results[:max_results]


def knots_search_crossing(crossing_number: int, max_results: int = 50) -> list[dict]:
    """Find all knots with a specific crossing number."""
    _load_knots()
    results = []
    for k in _knots_cache.get("knots", []):
        if k["crossing_number"] == crossing_number:
            results.append({
                "source": "KnotInfo",
                "id": k["name"],
                "label": k["name"],
                "match_reason": f"crossing_number={crossing_number}",
                "data": {
                    "determinant": k.get("determinant"),
                    "alex_coeffs": k.get("alex_coeffs", [])[:10],
                    "jones_coeffs": k.get("jones_coeffs", [])[:10],
                },
                "score": 1.0,
            })
    return results[:max_results]


def knots_determinant_list() -> list[dict]:
    """Return all unique knot determinants as a sorted list. Bridge query to OEIS/LMFDB."""
    _load_knots()
    dets = _knots_cache.get("determinants_list", [])
    return [{
        "source": "KnotInfo",
        "id": "determinant_list",
        "label": f"{len(dets)} unique knot determinants",
        "match_reason": f"All unique determinants from {_knots_cache.get('n_knots', 0)} knots",
        "data": {"determinants": dets, "n_determinants": len(dets)},
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Fungrim Search
# ---------------------------------------------------------------------------

_fungrim_cache: dict = {}


def _load_fungrim():
    if _fungrim_cache:
        return
    if not FUNGRIM_JSON.exists():
        print(f"  [Fungrim] WARNING: {FUNGRIM_JSON} not found. Run ingest_fungrim.py first.")
        return
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))
    _fungrim_cache.update(data)
    print(f"  [Fungrim] Loaded {data['n_formulas']:,} formulas, {data['n_symbols']} symbols")


def fungrim_search_symbol(symbol: str, max_results: int = 20) -> list[dict]:
    """Find formulas containing a specific mathematical symbol."""
    _load_fungrim()
    sym_lower = symbol.lower()
    results = []
    for f in _fungrim_cache.get("formulas", []):
        for s in f.get("symbols", []):
            if sym_lower in s.lower():
                results.append({
                    "source": "Fungrim",
                    "id": f["id"],
                    "label": f"{f['module']}/{f['id']}",
                    "match_reason": f"Contains symbol '{s}' in module {f['module']}",
                    "data": {
                        "module": f["module"],
                        "type": f["type"],
                        "symbols": f["symbols"][:10],
                        "n_symbols": f["n_symbols"],
                    },
                    "score": 1.0 if sym_lower == s.lower() else 0.5,
                })
                break  # One match per formula
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def fungrim_search_module(module: str, max_results: int = 20) -> list[dict]:
    """Find formulas in a specific topic module (e.g., 'dirichlet', 'bernoulli')."""
    _load_fungrim()
    mod_lower = module.lower()
    results = []
    for f in _fungrim_cache.get("formulas", []):
        if mod_lower in f.get("module", "").lower():
            results.append({
                "source": "Fungrim",
                "id": f["id"],
                "label": f"{f['module']}/{f['id']}",
                "match_reason": f"Module: {f['module']}, type: {f['type']}",
                "data": {
                    "module": f["module"],
                    "type": f["type"],
                    "symbols": f["symbols"][:10],
                },
                "score": 1.0,
            })
    return results[:max_results]


def fungrim_bridge_symbols() -> list[dict]:
    """Return symbols that appear across 3+ modules — cross-domain bridges."""
    _load_fungrim()
    bridges = _fungrim_cache.get("bridge_symbols", {})
    results = []
    for symbol, modules in sorted(bridges.items(), key=lambda x: -len(x[1])):
        results.append({
            "source": "Fungrim",
            "id": symbol,
            "label": symbol,
            "match_reason": f"Appears in {len(modules)} modules: {', '.join(modules[:5])}",
            "data": {"modules": modules, "n_modules": len(modules)},
            "score": len(modules) / 10.0,
        })
    return results[:30]


# ---------------------------------------------------------------------------
# ANTEDB Search
# ---------------------------------------------------------------------------

_antedb_cache: dict = {}


def _load_antedb():
    if _antedb_cache:
        return
    if not ANTEDB_JSON.exists():
        print(f"  [ANTEDB] WARNING: {ANTEDB_JSON} not found. Run ingest_antedb.py first.")
        return
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))
    _antedb_cache.update(data)
    print(f"  [ANTEDB] Loaded {data['n_chapters']} chapters, {data['n_theorems']} theorems")


def antedb_search_topic(topic: str, max_results: int = 20) -> list[dict]:
    """Search ANTEDB chapters and theorems by topic keyword."""
    _load_antedb()
    topic_lower = topic.lower()
    results = []
    for ch in _antedb_cache.get("chapters", []):
        if topic_lower in ch["chapter"].lower():
            for t in ch.get("theorems", []):
                results.append({
                    "source": "ANTEDB",
                    "id": f"{ch['chapter']}/{t['label']}",
                    "label": t["label"],
                    "match_reason": f"{t['type']} in {ch['chapter']}",
                    "data": {
                        "chapter": ch["chapter"],
                        "type": t["type"],
                        "numerical_values": t.get("numerical_values", []),
                        "body_preview": t.get("body_preview", "")[:150],
                    },
                    "score": 1.0,
                })
    results.sort(key=lambda x: x["id"])
    return results[:max_results]


def antedb_search_bounds(max_results: int = 30) -> list[dict]:
    """Return all theorems with numerical bounds. Battery-testable exponent values."""
    _load_antedb()
    results = []
    for ch in _antedb_cache.get("chapters", []):
        for t in ch.get("theorems", []):
            nums = t.get("numerical_values", [])
            if nums:
                results.append({
                    "source": "ANTEDB",
                    "id": f"{ch['chapter']}/{t['label']}",
                    "label": t["label"],
                    "match_reason": f"{t['type']}: {len(nums)} bounds in {ch['chapter']}",
                    "data": {
                        "chapter": ch["chapter"],
                        "type": t["type"],
                        "bounds": nums,
                    },
                    "score": len(nums) / 5.0,
                })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


# ---------------------------------------------------------------------------
# Dispatcher — route search requests from hypotheses
# ---------------------------------------------------------------------------

SEARCH_REGISTRY = {
    "oeis_terms": oeis_search_terms,
    "oeis_keyword": oeis_search_keyword,
    "oeis_growth": oeis_search_growth,
    "oeis_by_id": oeis_search_by_id,
    "oeis_find_containing": oeis_find_containing,
    "lmfdb_conductor": lmfdb_search_conductor_range,
    "lmfdb_rank": lmfdb_search_rank,
    "lmfdb_stats": lmfdb_stats,
    "lmfdb_conductor_distribution": lmfdb_conductor_distribution,
    "lmfdb_rank_comparison": lmfdb_rank_comparison,
    "lmfdb_neighbors": lmfdb_cross_type_neighbors,
    "mathlib_namespace": mathlib_search_namespace,
    "mathlib_imports": mathlib_search_imports,
    "metamath_search": metamath_search,
    "materials_search": materials_search,
    "knots_determinant": knots_search_determinant,
    "knots_crossing": knots_search_crossing,
    "knots_determinant_list": knots_determinant_list,
    "fungrim_symbol": fungrim_search_symbol,
    "fungrim_module": fungrim_search_module,
    "fungrim_bridges": fungrim_bridge_symbols,
    "antedb_topic": antedb_search_topic,
    "antedb_bounds": antedb_search_bounds,
}


def validate_search_params(search_type: str, params: dict) -> tuple[bool, str]:
    """Validate search_type exists and params bind to the function signature.
    Returns (ok, error_message)."""
    import inspect
    fn = SEARCH_REGISTRY.get(search_type)
    if not fn:
        return False, f"Unknown search type: {search_type}. Available: {list(SEARCH_REGISTRY.keys())}"
    try:
        sig = inspect.signature(fn)
        sig.bind(**params)
        return True, ""
    except TypeError as e:
        return False, f"Invalid params for {search_type}: {e}"


def dispatch_search(search_type: str, params: dict,
                    thread_id: str = "") -> list[dict]:
    """Route a search request to the appropriate engine. Logs via CycleLogger."""
    import cycle_logger
    log = cycle_logger.get()

    # Validate search type and params before executing
    ok, err_msg = validate_search_params(search_type, params)
    if not ok:
        err = [{"error": err_msg, "search_type": search_type, "params": params}]
        if log:
            log.error("search", "validation_failed", {
                "search_type": search_type, "params": params, "error": err_msg,
            }, msg=err_msg)
        return err

    fn = SEARCH_REGISTRY[search_type]

    if log:
        log.log_search_start(thread_id, search_type, params)

    t0 = time.time()
    try:
        result = fn(**params)
        if isinstance(result, dict):
            result = [result]
        elapsed = time.time() - t0
        if log:
            log.log_search_result(thread_id, search_type, params, result, elapsed)
        return result
    except Exception as e:
        elapsed = time.time() - t0
        err = [{"error": f"Search failed: {e}", "search_type": search_type, "params": params}]
        if log:
            log.log_search_result(thread_id, search_type, params, err, elapsed)
            log.error("search", "search_exception", {
                "search_type": search_type, "params": params, "error": str(e),
            }, msg=f"Search {search_type} failed: {e}")
        return err


# Dataset metadata — groups searches by source dataset
DATASET_REGISTRY = {
    "oeis": {
        "name": "OEIS",
        "description": "392K integer sequences with terms, growth rates, and cross-references",
        "path": OEIS_STRIPPED,
        "searches": ["oeis_terms", "oeis_keyword", "oeis_growth", "oeis_by_id", "oeis_find_containing"],
        "prompt_block": """OEIS (392K integer sequences):
- oeis_terms(target_terms=[list of ints], min_match=5) — find sequences containing these numbers
- oeis_by_id(seq_id="A000040") — fetch a specific sequence by A-number
- oeis_find_containing(integers=[list of ints], min_fraction=0.5) — find sequences covering the input set
- oeis_growth(growth_type="exponential|polynomial|super-exponential|sub-linear") — find by growth class""",
    },
    "lmfdb": {
        "name": "LMFDB",
        "description": "31K elliptic curves + 102K modular forms with conductors, ranks, L-functions",
        "path": CHARON_DB,
        "searches": ["lmfdb_conductor", "lmfdb_rank", "lmfdb_stats",
                     "lmfdb_conductor_distribution", "lmfdb_rank_comparison", "lmfdb_neighbors"],
        "prompt_block": """LMFDB (31K elliptic curves, 102K modular forms):
- lmfdb_rank_comparison(conductor_max=5000, bin_size=100) — PAIRED rank-0 vs rank-1 conductor arrays. USE THIS for rank comparisons.
- lmfdb_conductor_distribution(rank=int, conductor_max=5000, bin_size=100) — histogram of conductors for one rank
- lmfdb_conductor(low=int, high=int, object_type="elliptic_curve"|"modular_form") — individual objects
- lmfdb_stats(object_type=optional) — summary statistics
- lmfdb_neighbors(label="LMFDB label", k=5) — cross-type nearest neighbors by L-function coefficients""",
    },
    "mathlib": {
        "name": "mathlib",
        "description": "8.4K Lean 4 modules with import dependency graph (1.8K edges)",
        "path": MATHLIB_GRAPH,
        "searches": ["mathlib_namespace", "mathlib_imports"],
        "prompt_block": """mathlib (8.4K Lean modules, 1.8K import edges):
- mathlib_namespace(namespace="Algebra"|"NumberTheory"|etc) — search modules by namespace
- mathlib_imports(module_name="Mathlib.NumberTheory.LSeries") — find imports and dependents""",
    },
    "metamath": {
        "name": "Metamath",
        "description": "46K formal theorems from set.mm proof database",
        "path": METAMATH_INDEX,
        "searches": ["metamath_search"],
        "prompt_block": """Metamath (46K formal theorems):
- metamath_search(keyword="prime"|"group"|etc) — search theorem labels""",
    },
    "materials": {
        "name": "Materials Project",
        "description": "1K crystal structures with band gaps, formation energies, space groups",
        "path": MATERIALS_JSON,
        "searches": ["materials_search"],
        "prompt_block": """Materials Project (1K crystal structures):
- materials_search(crystal_system="cubic"|etc, band_gap_range=(low,high)) — search crystals""",
    },
    "knots": {
        "name": "KnotInfo",
        "description": "13K knots with polynomial invariants (Alexander, Jones, Conway), determinants, crossing numbers",
        "path": KNOTS_JSON,
        "searches": ["knots_determinant", "knots_crossing", "knots_determinant_list"],
        "prompt_block": """KnotInfo (13K knots, polynomial invariants):
- knots_determinant(target_det=int) or knots_determinant(det_range=(low,high)) — find knots by determinant value. Determinants bridge to OEIS and LMFDB conductors.
- knots_crossing(crossing_number=int) — find all knots with N crossings
- knots_determinant_list() — get all unique knot determinants as a list (for OEIS/LMFDB bridge queries)""",
    },
    "fungrim": {
        "name": "Fungrim",
        "description": "3.1K machine-readable mathematical formulas, 825 symbols, 280 cross-domain bridge symbols",
        "path": FUNGRIM_JSON,
        "searches": ["fungrim_symbol", "fungrim_module", "fungrim_bridges"],
        "prompt_block": """Fungrim (3.1K formulas, 825 symbols, cross-domain):
- fungrim_symbol(symbol="Zeta"|"BernoulliB"|"DirichletL"|etc) — find formulas using a symbol
- fungrim_module(module="dirichlet"|"bernoulli"|"zeta"|etc) — find formulas by topic
- fungrim_bridges() — symbols appearing in 3+ modules (cross-domain connections)""",
    },
    "antedb": {
        "name": "ANTEDB",
        "description": "244 theorems on analytic number theory exponents (Tao), zero density, L-function bounds",
        "path": ANTEDB_JSON,
        "searches": ["antedb_topic", "antedb_bounds"],
        "prompt_block": """ANTEDB — Analytic Number Theory Exponent Database (244 theorems, Tao et al.):
- antedb_topic(topic="zero_density"|"zeta"|"primes"|"exponent_pairs"|etc) — search by topic
- antedb_bounds() — all theorems with numerical bounds (exponent values, battery-testable)""",
    },
}


def inventory(datasets: list[str] = None) -> dict:
    """Return inventory, optionally filtered to specific datasets."""
    inv = {}
    for key, ds in DATASET_REGISTRY.items():
        if datasets and key not in datasets:
            continue
        inv[key] = {
            "available": ds["path"].exists(),
            "path": str(ds["path"]),
            "searches": ds["searches"],
            "description": ds["description"],
        }
    return inv


def available_datasets() -> list[str]:
    """Return list of dataset keys that have data files present."""
    return [k for k, ds in DATASET_REGISTRY.items() if ds["path"].exists()]


def dataset_prompt_blocks(datasets: list[str]) -> str:
    """Build the search functions prompt text for selected datasets."""
    blocks = []
    for key in datasets:
        ds = DATASET_REGISTRY.get(key)
        if ds:
            blocks.append(ds["prompt_block"])
    return "\n\n".join(blocks)


if __name__ == "__main__":
    print("=== Search Engine Inventory ===")
    for domain, info in inventory().items():
        status = "OK" if info["available"] else "MISSING"
        print(f"  {domain}: {status} | searches: {info['searches']}")
