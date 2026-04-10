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
OEIS_NAMES_TXT = CARTOGRAPHY / "oeis" / "data" / "names.txt"  # Uncompressed, from James download
MATHLIB_GRAPH = CARTOGRAPHY / "mathlib" / "data" / "import_graph.json"
METAMATH_INDEX = CARTOGRAPHY / "metamath" / "data" / "theorem_list.json"
MATERIALS_JSON = CARTOGRAPHY / "physics" / "data" / "materials_project_full.json"
KNOTS_JSON = CARTOGRAPHY / "knots" / "data" / "knots.json"
FUNGRIM_JSON = CARTOGRAPHY / "fungrim" / "data" / "fungrim_index.json"
ANTEDB_JSON = CARTOGRAPHY / "antedb" / "data" / "antedb_index.json"
NUMBER_FIELDS_JSON = CARTOGRAPHY / "number_fields" / "data" / "number_fields.json"
CHARON_DB = CHARON / "data" / "charon.duckdb"
POLYTOPES_DIR = CARTOGRAPHY / "polytopes" / "data"
PIBASE_DIR = CARTOGRAPHY / "topology" / "data" / "pi-base"
MMLKG_REFS = CHARON / "james_downloads" / "mmlkg" / "csvs" / "theorem_references.csv"
ISOGENY_GRAPHS = CARTOGRAPHY / "isogenies" / "data" / "graphs"
LOCAL_FIELDS_DIR = CARTOGRAPHY / "local_fields" / "data" / "wildly_ramified"
BILBAO_DIR = CARTOGRAPHY / "physics" / "data" / "bilbao"
OEIS_CROSSREFS = CARTOGRAPHY / "oeis" / "data" / "oeis_crossrefs.jsonl"
OPENALEX_CONCEPTS = CARTOGRAPHY / "convergence" / "data" / "openalex_concepts.json"
OPENALEX_EDGES = CARTOGRAPHY / "convergence" / "data" / "openalex_concept_edges.json"
GENUS2_JSON = CARTOGRAPHY / "genus2" / "data" / "genus2_curves_full.json"
GENUS2_PG = CARTOGRAPHY / "lmfdb_dump" / "g2c_curves.json"  # postgres dump, 50+ fields
MAASS_JSON = CARTOGRAPHY / "maass" / "data" / "maass_rigor_full.json"
MAASS_PG = CARTOGRAPHY / "lmfdb_dump" / "maass_rigor.json"  # postgres dump, richer fields
LATTICES_JSON = CARTOGRAPHY / "lattices" / "data" / "lattices_full.json"
LATTICES_PG = CARTOGRAPHY / "lmfdb_dump" / "lat_lattices.json"  # postgres dump, 19 fields
FINDSTAT_JSON = CARTOGRAPHY / "findstat" / "data" / "findstat_index.json"
SMALLGROUPS_JSON = CARTOGRAPHY / "atlas" / "data" / "small_groups.json"


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
    """Lazy-load OEIS sequence names. Try uncompressed first, then gzip."""
    if _oeis_names_cache:
        return
    # Try uncompressed names.txt first (James download, 38MB)
    if OEIS_NAMES_TXT.exists():
        try:
            with open(OEIS_NAMES_TXT, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    idx = line.find(" ")
                    if idx > 0:
                        _oeis_names_cache[line[:idx]] = line[idx+1:].strip()
            print(f"  [OEIS] Loaded {len(_oeis_names_cache):,} sequence names from names.txt")
            return
        except Exception as e:
            print(f"  [OEIS] WARNING: Could not load names.txt: {e}")
    # Fallback to gzip
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
        print(f"  [OEIS] WARNING: Could not load names.gz: {e}")


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


# --- OEIS Cross-Reference Graph ---

_oeis_xref_cache: dict = {}  # seq_id → set of referenced seq_ids
_oeis_xref_reverse: dict = {}  # seq_id → set of sequences that reference it


def _load_oeis_crossrefs():
    """Load OEIS cross-reference graph from JSONL."""
    if _oeis_xref_cache:
        return
    if not OEIS_CROSSREFS.exists():
        return
    import json
    count = 0
    with open(OEIS_CROSSREFS, "r", encoding="utf-8") as f:
        for line in f:
            try:
                edge = json.loads(line)
                src, tgt = edge["source"], edge["target"]
                _oeis_xref_cache.setdefault(src, set()).add(tgt)
                _oeis_xref_reverse.setdefault(tgt, set()).add(src)
                count += 1
            except (json.JSONDecodeError, KeyError):
                pass
    print(f"  [OEIS Xref] Loaded {count:,} cross-reference edges, {len(_oeis_xref_cache):,} source sequences")


def oeis_crossrefs(seq_id: str, max_results: int = 50) -> list[dict]:
    """Find sequences cross-referenced by a given OEIS sequence (outgoing + incoming edges)."""
    _load_oeis_crossrefs()
    _load_oeis_names()
    seq_id = seq_id.upper().strip()

    results = []
    outgoing = _oeis_xref_cache.get(seq_id, set())
    incoming = _oeis_xref_reverse.get(seq_id, set())

    for ref_id in sorted(outgoing)[:max_results // 2]:
        results.append({
            "source": "OEIS",
            "id": ref_id,
            "label": _oeis_names_cache.get(ref_id, ""),
            "match_reason": f"Referenced BY {seq_id}",
            "data": {"direction": "outgoing", "from": seq_id, "to": ref_id},
            "score": 1.0,
        })
    for ref_id in sorted(incoming)[:max_results // 2]:
        if ref_id not in outgoing:  # avoid duplicates
            results.append({
                "source": "OEIS",
                "id": ref_id,
                "label": _oeis_names_cache.get(ref_id, ""),
                "match_reason": f"References {seq_id}",
                "data": {"direction": "incoming", "from": ref_id, "to": seq_id},
                "score": 0.9,
            })

    return results[:max_results]


def oeis_xref_hubs(min_degree: int = 50, max_results: int = 50) -> list[dict]:
    """Find OEIS hub sequences with many cross-references (high degree nodes)."""
    _load_oeis_crossrefs()
    _load_oeis_names()

    hub_scores = []
    for seq_id, refs in _oeis_xref_cache.items():
        out_deg = len(refs)
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total = out_deg + in_deg
        if total >= min_degree:
            hub_scores.append((seq_id, total, out_deg, in_deg))

    hub_scores.sort(key=lambda x: -x[1])
    results = []
    for seq_id, total, out_deg, in_deg in hub_scores[:max_results]:
        results.append({
            "source": "OEIS",
            "id": seq_id,
            "label": _oeis_names_cache.get(seq_id, ""),
            "match_reason": f"Hub: {total} xrefs (out={out_deg}, in={in_deg})",
            "data": {"total_degree": total, "out_degree": out_deg, "in_degree": in_deg},
            "score": min(1.0, total / 500),
        })

    return results


def oeis_sleeping_beauties(min_entropy: float = 4.0, max_degree: int = 2,
                           max_results: int = 50) -> list[dict]:
    """Find Sleeping Beauty sequences: high internal structure, low connectivity.

    The Isolatus Metric: sequences with high Shannon entropy of first differences
    (complex internal structure) but near-zero cross-reference degree (nobody noticed).
    These are the 'dark matter' of mathematics — structurally rich, arithmetically poor.
    """
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    results = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < 8:
            continue

        # Connectivity: total cross-reference degree
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total_deg = out_deg + in_deg
        if total_deg > max_degree:
            continue

        # Internal structure: Shannon entropy of first differences
        diffs = [terms[i+1] - terms[i] for i in range(min(len(terms)-1, 30))]
        if not diffs:
            continue
        from collections import Counter as _Counter
        counts = _Counter(diffs)
        total = len(diffs)
        import math as _math
        entropy = -sum((c/total) * _math.log2(c/total) for c in counts.values() if c > 0)
        if entropy < min_entropy:
            continue

        # Isolatus score: entropy / (1 + log(1 + degree))
        isolatus = entropy / (1 + _math.log2(1 + total_deg))

        results.append({
            "source": "OEIS",
            "id": seq_id,
            "label": _oeis_names_cache.get(seq_id, ""),
            "match_reason": f"Sleeping Beauty: entropy={entropy:.2f}, degree={total_deg}, isolatus={isolatus:.2f}",
            "data": {
                "entropy": round(entropy, 3),
                "total_degree": total_deg,
                "isolatus_score": round(isolatus, 3),
                "first_terms": terms[:10],
            },
            "score": isolatus,
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
        if isinstance(edge, dict):
            src = edge.get("source", "")
            tgt = edge.get("target", "")
        elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
            src, tgt = str(edge[0]), str(edge[1])
        else:
            continue
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
# Number Fields Search
# ---------------------------------------------------------------------------

_nf_cache: list = []


def _load_nf():
    if _nf_cache:
        return
    if not NUMBER_FIELDS_JSON.exists():
        print(f"  [NF] WARNING: {NUMBER_FIELDS_JSON} not found")
        return
    data = json.loads(NUMBER_FIELDS_JSON.read_text(encoding="utf-8"))
    _nf_cache.extend(data if isinstance(data, list) else [])
    print(f"  [NF] Loaded {len(_nf_cache):,} number fields")


def nf_search_degree(degree: int, max_results: int = 50) -> list[dict]:
    """Search number fields by degree."""
    _load_nf()
    results = []
    for f in _nf_cache:
        if f.get("degree") == degree:
            results.append({
                "source": "NumberFields",
                "id": f.get("label", ""),
                "label": f.get("label", ""),
                "match_reason": f"degree={degree}, disc={f.get('disc_abs')}, class_number={f.get('class_number')}",
                "data": {
                    "degree": degree,
                    "disc_abs": f.get("disc_abs"),
                    "disc_sign": f.get("disc_sign"),
                    "class_number": f.get("class_number"),
                    "class_group": f.get("class_group"),
                    "galois_label": f.get("galois_label"),
                    "regulator": f.get("regulator"),
                },
                "score": 1.0,
            })
    results.sort(key=lambda x: int(x["data"].get("disc_abs", 0) or 0))
    return results[:max_results]


def nf_search_class_number(class_number: int, max_results: int = 50) -> list[dict]:
    """Search number fields by class number. Bridge to OEIS."""
    _load_nf()
    results = []
    for f in _nf_cache:
        cn = f.get("class_number")
        if cn is not None and str(cn) == str(class_number):
            results.append({
                "source": "NumberFields",
                "id": f.get("label", ""),
                "label": f.get("label", ""),
                "match_reason": f"class_number={class_number}, degree={f.get('degree')}, disc={f.get('disc_abs')}",
                "data": {
                    "degree": f.get("degree"),
                    "disc_abs": f.get("disc_abs"),
                    "class_number": class_number,
                    "galois_label": f.get("galois_label"),
                },
                "score": 1.0,
            })
    return results[:max_results]


def nf_class_number_distribution() -> list[dict]:
    """Return distribution of class numbers. Battery-testable."""
    _load_nf()
    import numpy as np
    class_numbers = [int(f.get("class_number", 0)) for f in _nf_cache
                     if f.get("class_number") is not None]
    if not class_numbers:
        return [{"error": "No class numbers found"}]

    cn_arr = np.array(class_numbers)
    from collections import Counter
    cn_dist = Counter(class_numbers)

    return [{
        "source": "NumberFields",
        "id": "class_number_distribution",
        "label": f"Class number distribution ({len(class_numbers)} fields)",
        "match_reason": f"{len(cn_dist)} unique class numbers",
        "data": {
            "n_fields": len(class_numbers),
            "unique_class_numbers": len(cn_dist),
            "mean": round(float(cn_arr.mean()), 2),
            "median": int(np.median(cn_arr)),
            "max": int(cn_arr.max()),
            "class_numbers": class_numbers[:500],
            "distribution": {str(k): v for k, v in cn_dist.most_common(20)},
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# polyDB Polytopes Search
# ---------------------------------------------------------------------------

_polytopes_cache: list = []


def _load_polytopes():
    if _polytopes_cache:
        return
    if not POLYTOPES_DIR.exists():
        print(f"  [Polytopes] WARNING: {POLYTOPES_DIR} not found")
        return
    json_files = [f for f in POLYTOPES_DIR.glob("*.json") if f.name != "manifest.json"]
    if not json_files:
        print(f"  [Polytopes] WARNING: No JSON files in {POLYTOPES_DIR}")
        return
    for jf in sorted(json_files):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for obj in data:
                    obj["_collection"] = jf.stem
                _polytopes_cache.extend(data)
        except Exception as e:
            print(f"  [Polytopes] WARNING: Could not load {jf.name}: {e}")
    print(f"  [Polytopes] Loaded {len(_polytopes_cache):,} polytopes from {len(json_files)} collections")


def polytopes_search_fvector(dimension: int, max_results: int = 50) -> list[dict]:
    """Find polytopes by dimension, return f-vectors."""
    _load_polytopes()
    results = []
    for p in _polytopes_cache:
        dim = p.get("DIM") or p.get("dim") or p.get("dimension")
        if dim is not None and int(dim) == dimension:
            fv = p.get("F_VECTOR") or p.get("f_vector") or []
            results.append({
                "source": "polyDB",
                "id": f"{p.get('_collection', 'unknown')}_{len(results)}",
                "label": f"dim={dimension} f_vector={fv}",
                "match_reason": f"DIM={dimension}, collection={p.get('_collection', '')}",
                "data": {
                    "dimension": dimension,
                    "f_vector": fv,
                    "n_vertices": p.get("N_VERTICES") or p.get("n_vertices"),
                    "n_facets": p.get("N_FACETS") or p.get("n_facets"),
                    "n_edges": p.get("N_EDGES") or p.get("n_edges"),
                    "collection": p.get("_collection", ""),
                },
                "score": 1.0,
            })
    results.sort(key=lambda x: str(x["data"].get("f_vector", [])))
    return results[:max_results]


def polytopes_search_dimension(dimension: int, max_results: int = 50) -> list[dict]:
    """Find all polytopes of a given dimension."""
    _load_polytopes()
    results = []
    for p in _polytopes_cache:
        dim = p.get("DIM") or p.get("dim") or p.get("dimension")
        if dim is not None and int(dim) == dimension:
            results.append({
                "source": "polyDB",
                "id": f"{p.get('_collection', 'unknown')}_{len(results)}",
                "label": f"dim={dimension} vertices={p.get('N_VERTICES', '?')}",
                "match_reason": f"DIM={dimension}, collection={p.get('_collection', '')}",
                "data": {k: p.get(k) for k in
                         ["DIM", "N_VERTICES", "N_FACETS", "N_EDGES", "F_VECTOR", "_collection"]
                         if k in p},
                "score": 1.0,
            })
    return results[:max_results]


# ---------------------------------------------------------------------------
# pi-Base Topology Search
# ---------------------------------------------------------------------------

_pibase_spaces: list = []   # [{uid, name, aliases, properties: {pid: bool}}]
_pibase_props: dict = {}    # {pid: name}


def _load_pibase():
    if _pibase_spaces:
        return
    if not PIBASE_DIR.exists():
        print(f"  [pi-Base] WARNING: {PIBASE_DIR} not found")
        return
    # Load property names
    props_dir = PIBASE_DIR / "properties"
    if props_dir.exists():
        for pf in sorted(props_dir.glob("P*.md")):
            try:
                text = pf.read_text(encoding="utf-8")
                pid = pf.stem
                name = ""
                for line in text.splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                        # Strip LaTeX dollar signs for cleaner matching
                        name = name.replace("$", "")
                        break
                if name:
                    _pibase_props[pid] = name
            except Exception:
                pass
    # Load spaces
    spaces_dir = PIBASE_DIR / "spaces"
    if not spaces_dir.exists():
        print(f"  [pi-Base] WARNING: {spaces_dir} not found")
        return
    for sd in sorted(spaces_dir.iterdir()):
        if not sd.is_dir():
            continue
        readme = sd / "README.md"
        if not readme.exists():
            continue
        try:
            text = readme.read_text(encoding="utf-8")
            uid = sd.name
            name = ""
            aliases = []
            for line in text.splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    name = name.replace("$", "")
                elif line.strip().startswith("- ") and aliases is not None:
                    aliases.append(line.strip()[2:].strip('"').strip("'"))
                elif line.startswith("counterexamples_id:") or line.startswith("refs:"):
                    aliases = None  # Stop collecting aliases
            # Load properties for this space
            props = {}
            prop_dir = sd / "properties"
            if prop_dir.exists():
                for pf in prop_dir.glob("P*.md"):
                    try:
                        pt = pf.read_text(encoding="utf-8")
                        pid = pf.stem
                        val = None
                        for pline in pt.splitlines():
                            if pline.startswith("value:"):
                                val_str = pline.split(":", 1)[1].strip()
                                val = val_str.lower() == "true"
                                break
                        if val is not None:
                            props[pid] = val
                    except Exception:
                        pass
            _pibase_spaces.append({
                "uid": uid,
                "name": name,
                "aliases": aliases if isinstance(aliases, list) else [],
                "properties": props,
            })
        except Exception:
            pass
    print(f"  [pi-Base] Loaded {len(_pibase_spaces)} spaces, {len(_pibase_props)} properties")


def pibase_search_property(property_name: str = "compact",
                           max_results: int = 50) -> list[dict]:
    """Find spaces with a given topological property (e.g., 'compact', 'Hausdorff')."""
    _load_pibase()
    prop_lower = property_name.lower()
    # Find matching property IDs
    matching_pids = [pid for pid, pname in _pibase_props.items()
                     if prop_lower in pname.lower()]
    if not matching_pids:
        return [{"error": f"Property '{property_name}' not found in pi-Base. "
                 f"Available samples: {list(_pibase_props.values())[:10]}"}]
    results = []
    for space in _pibase_spaces:
        for pid in matching_pids:
            if space["properties"].get(pid) is True:
                results.append({
                    "source": "pi-Base",
                    "id": space["uid"],
                    "label": space["name"],
                    "match_reason": f"Has property {_pibase_props.get(pid, pid)} = true",
                    "data": {
                        "space": space["name"],
                        "uid": space["uid"],
                        "property": _pibase_props.get(pid, pid),
                        "property_id": pid,
                        "n_true_properties": sum(1 for v in space["properties"].values() if v),
                    },
                    "score": 1.0,
                })
                break  # One match per space per search
    return results[:max_results]


def pibase_search_space(space_name: str = "real line",
                        max_results: int = 20) -> list[dict]:
    """Search pi-Base spaces by name or alias."""
    _load_pibase()
    name_lower = space_name.lower()
    results = []
    for space in _pibase_spaces:
        matched = False
        if name_lower in space["name"].lower():
            matched = True
        else:
            for alias in space.get("aliases", []):
                if name_lower in alias.lower():
                    matched = True
                    break
        if matched:
            # Resolve property names
            named_props = {}
            for pid, val in space["properties"].items():
                pname = _pibase_props.get(pid, pid)
                named_props[pname] = val
            results.append({
                "source": "pi-Base",
                "id": space["uid"],
                "label": space["name"],
                "match_reason": f"Name matches '{space_name}'",
                "data": {
                    "space": space["name"],
                    "uid": space["uid"],
                    "aliases": space.get("aliases", [])[:5],
                    "properties": named_props,
                    "n_properties": len(space["properties"]),
                },
                "score": 1.0 if name_lower == space["name"].lower() else 0.5,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


# ---------------------------------------------------------------------------
# MMLKG Theorem References Search
# ---------------------------------------------------------------------------

_mmlkg_graph: dict = {}   # {article: set_of_referenced_articles}
_mmlkg_reverse: dict = {}  # {article: set_of_articles_referencing_it}


def _load_mmlkg():
    if _mmlkg_graph:
        return
    if not MMLKG_REFS.exists():
        print(f"  [MMLKG] WARNING: {MMLKG_REFS} not found")
        return
    import csv
    try:
        with open(MMLKG_REFS, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 4:
                    continue
                src_article = row[0].strip()
                tgt_article = row[2].strip()
                if not src_article or not tgt_article:
                    continue
                if src_article not in _mmlkg_graph:
                    _mmlkg_graph[src_article] = set()
                _mmlkg_graph[src_article].add(tgt_article)
                if tgt_article not in _mmlkg_reverse:
                    _mmlkg_reverse[tgt_article] = set()
                _mmlkg_reverse[tgt_article].add(src_article)
        n_edges = sum(len(v) for v in _mmlkg_graph.values())
        all_articles = set(_mmlkg_graph.keys()) | set(_mmlkg_reverse.keys())
        print(f"  [MMLKG] Loaded {len(all_articles):,} articles, {n_edges:,} edges")
    except Exception as e:
        print(f"  [MMLKG] WARNING: Could not load {MMLKG_REFS}: {e}")


def mmlkg_search_article(article: str = "tarski",
                         max_results: int = 50) -> list[dict]:
    """Find articles referencing or referenced by a given article name."""
    _load_mmlkg()
    article_lower = article.lower()
    results = []
    # Find matching articles
    all_articles = set(_mmlkg_graph.keys()) | set(_mmlkg_reverse.keys())
    matching = [a for a in all_articles if article_lower in a.lower()]
    for art in sorted(matching):
        refs_out = _mmlkg_graph.get(art, set())
        refs_in = _mmlkg_reverse.get(art, set())
        results.append({
            "source": "MMLKG",
            "id": art,
            "label": art,
            "match_reason": f"references {len(refs_out)} articles, referenced by {len(refs_in)}",
            "data": {
                "article": art,
                "references": sorted(refs_out)[:20],
                "referenced_by": sorted(refs_in)[:20],
                "n_references": len(refs_out),
                "n_referenced_by": len(refs_in),
            },
            "score": 1.0 if article_lower == art.lower() else 0.5,
        })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def mmlkg_stats() -> list[dict]:
    """Return graph statistics: n_articles, n_edges, top hub articles."""
    _load_mmlkg()
    all_articles = set(_mmlkg_graph.keys()) | set(_mmlkg_reverse.keys())
    n_edges = sum(len(v) for v in _mmlkg_graph.values())
    # Top hubs by total degree (out + in)
    degree = {}
    for art in all_articles:
        degree[art] = len(_mmlkg_graph.get(art, set())) + len(_mmlkg_reverse.get(art, set()))
    top_hubs = sorted(degree.items(), key=lambda x: -x[1])[:20]
    return [{
        "source": "MMLKG",
        "id": "graph_stats",
        "label": f"MMLKG reference graph ({len(all_articles):,} articles, {n_edges:,} edges)",
        "match_reason": "Graph statistics",
        "data": {
            "n_articles": len(all_articles),
            "n_edges": n_edges,
            "n_sources": len(_mmlkg_graph),
            "n_targets": len(_mmlkg_reverse),
            "top_hubs": [{"article": a, "degree": d} for a, d in top_hubs],
            "avg_degree": round(2 * n_edges / max(len(all_articles), 1), 2),
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Isogeny Graphs Search
# ---------------------------------------------------------------------------

_isogeny_cache: dict = {}  # {prime_str: metadata_dict}


def _load_isogeny():
    if _isogeny_cache:
        return
    if not ISOGENY_GRAPHS.exists():
        print(f"  [Isogeny] WARNING: {ISOGENY_GRAPHS} not found")
        return
    count = 0
    for d in ISOGENY_GRAPHS.iterdir():
        if d.is_dir() and d.name.isdigit():
            meta_file = d / f"{d.name}_metadata.json"
            if meta_file.exists():
                try:
                    data = json.loads(meta_file.read_text(encoding="utf-8"))
                    _isogeny_cache[d.name] = data
                    count += 1
                except Exception:
                    pass
    print(f"  [Isogeny] Loaded {count:,} prime graphs")


def isogeny_search_prime(prime: int, max_results: int = 20) -> list[dict]:
    """Find isogeny graph data for a specific prime."""
    _load_isogeny()
    key = str(prime)
    if key in _isogeny_cache:
        meta = _isogeny_cache[key]
        return [{
            "source": "IsogenyGraphs",
            "id": f"isogeny_{prime}",
            "label": f"Isogeny graph for p={prime}",
            "match_reason": f"Exact match: p={prime}, {meta.get('nodes', 0)} nodes",
            "data": meta,
            "score": 1.0,
        }]
    # Try range search: find primes near the requested value
    results = []
    for k, meta in _isogeny_cache.items():
        p = int(k)
        if abs(p - prime) <= max(prime // 10, 10):
            results.append({
                "source": "IsogenyGraphs",
                "id": f"isogeny_{p}",
                "label": f"Isogeny graph for p={p}",
                "match_reason": f"Near p={prime}: p={p}, {meta.get('nodes', 0)} nodes",
                "data": meta,
                "score": 1.0 / (1.0 + abs(p - prime)),
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def isogeny_stats() -> list[dict]:
    """Summary statistics for the isogeny graph database."""
    _load_isogeny()
    if not _isogeny_cache:
        return [{"error": "No isogeny data loaded"}]
    primes = sorted(int(k) for k in _isogeny_cache)
    nodes_list = [m.get("nodes", 0) for m in _isogeny_cache.values()]
    return [{
        "source": "IsogenyGraphs",
        "id": "isogeny_stats",
        "label": f"Isogeny graph database ({len(primes)} primes)",
        "match_reason": "Database statistics",
        "data": {
            "n_primes": len(primes),
            "prime_range": [primes[0], primes[-1]],
            "total_nodes": sum(nodes_list),
            "mean_nodes": round(sum(nodes_list) / max(len(nodes_list), 1), 2),
            "max_nodes": max(nodes_list) if nodes_list else 0,
            "sample_primes": primes[:20],
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Local Fields Search
# ---------------------------------------------------------------------------

_local_fields_cache: dict = {}  # {prime: [{field_data}, ...]}


def _load_local_fields():
    if _local_fields_cache:
        return
    if not LOCAL_FIELDS_DIR.exists():
        print(f"  [LocalFields] WARNING: {LOCAL_FIELDS_DIR} not found")
        return
    count = 0
    for f in LOCAL_FIELDS_DIR.iterdir():
        if not f.is_file():
            continue
        # Filenames like p2d4all, p3d6all — extract prime from name
        m = re.match(r"p(\d+)d(\d+)all", f.name)
        if not m:
            continue
        prime = int(m.group(1))
        degree = int(m.group(2))
        try:
            text = f.read_text(encoding="utf-8").strip()
            # Count entries: each top-level sub-list is a field extension
            # The data is a PARI/GP-style nested list; we store file metadata
            # Full parsing is expensive, so we store summary info
            n_entries = text.count("], [")  # Approximate count
            if prime not in _local_fields_cache:
                _local_fields_cache[prime] = []
            _local_fields_cache[prime].append({
                "prime": prime,
                "degree": degree,
                "file": f.name,
                "n_extensions_approx": n_entries + 1,
            })
            count += 1
        except Exception:
            pass
    print(f"  [LocalFields] Loaded {count} wildly ramified data files "
          f"({len(_local_fields_cache)} primes)")


def local_fields_search(prime: int, max_results: int = 20) -> list[dict]:
    """Search wildly ramified local field extensions by ramification prime."""
    _load_local_fields()
    entries = _local_fields_cache.get(prime, [])
    if not entries:
        # List available primes
        available = sorted(_local_fields_cache.keys())
        return [{
            "source": "LocalFields",
            "id": f"local_fields_p{prime}",
            "label": f"No data for p={prime}",
            "match_reason": f"Available primes: {available}",
            "data": {"available_primes": available},
            "score": 0.0,
        }]
    results = []
    total_ext = sum(e["n_extensions_approx"] for e in entries)
    degrees = sorted(set(e["degree"] for e in entries))
    results.append({
        "source": "LocalFields",
        "id": f"local_fields_p{prime}",
        "label": f"Wildly ramified extensions over Q_{prime}",
        "match_reason": f"p={prime}: {len(entries)} degree files, ~{total_ext} extensions",
        "data": {
            "prime": prime,
            "degrees": degrees,
            "files": entries,
            "n_extensions_approx": total_ext,
        },
        "score": 1.0,
    })
    return results[:max_results]


# ---------------------------------------------------------------------------
# Bilbao Space Groups Search
# ---------------------------------------------------------------------------

_spacegroup_cache: dict = {}  # {sg_number: data_dict}

# Standard crystal system classification by space group number ranges
_CRYSTAL_SYSTEM_RANGES = [
    (1, 2, "triclinic"),
    (3, 15, "monoclinic"),
    (16, 74, "orthorhombic"),
    (75, 142, "tetragonal"),
    (143, 167, "trigonal"),
    (168, 194, "hexagonal"),
    (195, 230, "cubic"),
]


def _sg_crystal_system(sg_number: int) -> str:
    """Return crystal system for a space group number."""
    for low, high, system in _CRYSTAL_SYSTEM_RANGES:
        if low <= sg_number <= high:
            return system
    return "unknown"


def _load_spacegroups():
    if _spacegroup_cache:
        return
    if not BILBAO_DIR.exists():
        print(f"  [SpaceGroups] WARNING: {BILBAO_DIR} not found")
        return
    count = 0
    for f in sorted(BILBAO_DIR.glob("sg_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sg_num = data.get("space_group_number", int(f.stem.split("_")[1]))
            data["crystal_system"] = _sg_crystal_system(sg_num)
            _spacegroup_cache[sg_num] = data
            count += 1
        except Exception:
            pass
    print(f"  [SpaceGroups] Loaded {count} space groups")


def spacegroup_search(sg_number: int) -> list[dict]:
    """Find a space group by its ITA number (1-230)."""
    _load_spacegroups()
    data = _spacegroup_cache.get(sg_number)
    if not data:
        return [{"error": f"Space group {sg_number} not found (available: 1-230)"}]
    return [{
        "source": "BilbaoSpaceGroups",
        "id": f"sg_{sg_number}",
        "label": f"Space group #{sg_number} ({data['crystal_system']})",
        "match_reason": f"Exact match: SG {sg_number}",
        "data": {
            "space_group_number": sg_number,
            "crystal_system": data["crystal_system"],
            "num_generators": data.get("num_generators"),
            "point_group_order": data.get("point_group_order"),
            "num_wyckoff_positions": data.get("num_wyckoff_positions"),
            "translation_basis": data.get("translation_basis"),
        },
        "score": 1.0,
    }]


def spacegroup_by_crystal_system(system: str, max_results: int = 50) -> list[dict]:
    """Find all space groups belonging to a crystal system."""
    _load_spacegroups()
    system_lower = system.lower()
    results = []
    for sg_num, data in sorted(_spacegroup_cache.items()):
        if system_lower in data.get("crystal_system", "").lower():
            results.append({
                "source": "BilbaoSpaceGroups",
                "id": f"sg_{sg_num}",
                "label": f"Space group #{sg_num} ({data['crystal_system']})",
                "match_reason": f"Crystal system: {data['crystal_system']}",
                "data": {
                    "space_group_number": sg_num,
                    "crystal_system": data["crystal_system"],
                    "num_generators": data.get("num_generators"),
                    "point_group_order": data.get("point_group_order"),
                    "num_wyckoff_positions": data.get("num_wyckoff_positions"),
                },
                "score": 1.0,
            })
    if not results:
        valid = sorted(set(d.get("crystal_system", "") for d in _spacegroup_cache.values()))
        return [{"error": f"Crystal system '{system}' not found. Valid: {valid}"}]
    return results[:max_results]


# ---------------------------------------------------------------------------
# OpenAlex Concept Taxonomy Search (10K+ concepts, 6 hierarchy levels)
# ---------------------------------------------------------------------------

_openalex_cache: list = []
_openalex_id_map: dict = {}  # concept_id -> concept
_openalex_name_index: dict = {}  # lowercase name -> concept


def _load_openalex():
    """Lazy-load OpenAlex concepts into cache."""
    if _openalex_cache:
        return
    if not OPENALEX_CONCEPTS.exists():
        print(f"  [OpenAlex] WARNING: {OPENALEX_CONCEPTS} not found")
        return
    print(f"  [OpenAlex] Loading {OPENALEX_CONCEPTS.name}...")
    with open(OPENALEX_CONCEPTS, "r", encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        _openalex_cache.append(c)
        cid = c.get("id", "")
        _openalex_id_map[cid] = c
        # Also index by short ID (e.g. "C41008148")
        if cid.startswith("https://openalex.org/"):
            short_id = cid.split("/")[-1]
            _openalex_id_map[short_id] = c
        name_lower = c.get("display_name", "").lower()
        if name_lower:
            _openalex_name_index[name_lower] = c
    print(f"  [OpenAlex] Loaded {len(_openalex_cache):,} concepts")


def openalex_concept(keyword: str, max_results: int = 20) -> list[dict]:
    """Search OpenAlex concepts by name or description keyword."""
    _load_openalex()
    kw_lower = keyword.lower()
    results = []
    for c in _openalex_cache:
        name = c.get("display_name") or ""
        desc = c.get("description") or ""
        name_match = kw_lower in name.lower()
        desc_match = kw_lower in desc.lower()
        if name_match or desc_match:
            score = 1.0 if kw_lower == name.lower() else (0.8 if name_match else 0.4)
            results.append({
                "source": "OpenAlex",
                "id": c["id"],
                "label": name,
                "match_reason": f"{'Name' if name_match else 'Description'} contains '{keyword}'",
                "data": {
                    "level": c.get("level"),
                    "description": desc[:200],
                    "works_count": c.get("works_count", 0),
                    "cited_by_count": c.get("cited_by_count", 0),
                    "wikidata": c.get("wikidata", ""),
                },
                "score": score,
            })
    results.sort(key=lambda x: (-x["score"], -x["data"]["works_count"]))
    return results[:max_results]


def openalex_hierarchy(concept_id: str, max_results: int = 50) -> list[dict]:
    """Find parent and child concepts for a given concept ID.

    Accepts full URL (https://openalex.org/C41008148) or short ID (C41008148).
    Since ancestor data may be sparse, also infers hierarchy from levels:
    returns concepts at level-1 (potential parents) and level+1 (potential children)
    that share name tokens with the target concept.
    """
    _load_openalex()
    concept = _openalex_id_map.get(concept_id)
    if not concept:
        # Try exact name match
        concept = _openalex_name_index.get(concept_id.lower())
    if not concept:
        return [{"error": f"Concept '{concept_id}' not found. Try openalex_concept(keyword) first."}]

    target_level = concept.get("level")
    target_name = concept.get("display_name", "")
    target_id = concept.get("id", "")

    results = [{
        "source": "OpenAlex",
        "id": target_id,
        "label": target_name,
        "match_reason": "Target concept",
        "data": {
            "level": target_level,
            "description": concept.get("description", "")[:200],
            "works_count": concept.get("works_count", 0),
            "role": "target",
        },
        "score": 1.0,
    }]

    # Check explicit ancestors stored in the concept
    for anc in concept.get("ancestors", []):
        anc_full = _openalex_id_map.get(anc.get("id", ""))
        if anc_full:
            results.append({
                "source": "OpenAlex",
                "id": anc["id"],
                "label": anc.get("display_name", ""),
                "match_reason": f"Ancestor (level {anc.get('level')})",
                "data": {
                    "level": anc.get("level"),
                    "description": anc_full.get("description", "")[:200],
                    "works_count": anc_full.get("works_count", 0),
                    "role": "ancestor",
                },
                "score": 0.9,
            })

    # Find concepts that list this concept as an ancestor (children)
    for c in _openalex_cache:
        if c.get("id") == target_id:
            continue
        for anc in c.get("ancestors", []):
            if anc.get("id") == target_id:
                results.append({
                    "source": "OpenAlex",
                    "id": c["id"],
                    "label": c.get("display_name", ""),
                    "match_reason": f"Child concept (level {c.get('level')})",
                    "data": {
                        "level": c.get("level"),
                        "description": c.get("description", "")[:200],
                        "works_count": c.get("works_count", 0),
                        "role": "child",
                    },
                    "score": 0.8,
                })

    # If we found no explicit hierarchy, use level-based heuristic
    ancestor_child_count = sum(1 for r in results if r["data"].get("role") in ("ancestor", "child"))
    if ancestor_child_count == 0 and target_level is not None:
        # Find related concepts at adjacent levels sharing name tokens
        name_tokens = set(target_name.lower().split()) - {"of", "the", "and", "in", "for", "a", "an"}
        for c in _openalex_cache:
            c_level = c.get("level")
            if c_level is None or c.get("id") == target_id:
                continue
            if abs(c_level - target_level) == 1:
                c_tokens = set(c.get("display_name", "").lower().split())
                overlap = name_tokens & c_tokens
                if overlap and len(overlap) >= 1:
                    role = "inferred_parent" if c_level < target_level else "inferred_child"
                    results.append({
                        "source": "OpenAlex",
                        "id": c["id"],
                        "label": c.get("display_name", ""),
                        "match_reason": f"{role} (shared tokens: {overlap})",
                        "data": {
                            "level": c_level,
                            "description": c.get("description", "")[:200],
                            "works_count": c.get("works_count", 0),
                            "role": role,
                        },
                        "score": 0.5 * len(overlap) / max(len(name_tokens), 1),
                    })

    results.sort(key=lambda x: (-x["score"], -x["data"].get("works_count", 0)))
    return results[:max_results]


# ---------------------------------------------------------------------------
# Genus-2 Curves (66K curves from LMFDB g2c database)
# ---------------------------------------------------------------------------

_genus2_cache: list = []


def _load_genus2():
    """Lazy-load genus-2 curves. Prefer postgres dump (50+ fields), fall back to flat JSON."""
    if _genus2_cache:
        return
    # Try postgres dump first (richest: analytic_rank, igusa_clebsch_inv, eqn, regulator, etc.)
    src = None
    for path in [GENUS2_PG, GENUS2_JSON]:
        if path.exists():
            src = path
            break
    if src is None:
        print(f"  [Genus2] WARNING: No genus-2 data found")
        return
    print(f"  [Genus2] Loading {src.name}...")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle postgres envelope or flat list
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = data.get("curves", [])
    # Normalize field names: postgres uses 'cond', flat uses 'conductor'
    for r in records:
        if "cond" in r and "conductor" not in r:
            r["conductor"] = r["cond"]
        if "conductor" not in r:
            r["conductor"] = 0
        # Ensure st_group has a default
        if "st_group" not in r:
            r["st_group"] = "unknown"
    _genus2_cache.extend(records)
    print(f"  [Genus2] Loaded {len(_genus2_cache):,} curves from {src.name}")


def genus2_search_conductor(low: int = 1, high: int = 1000,
                            max_results: int = 50) -> list[dict]:
    """Search genus-2 curves by conductor range."""
    _load_genus2()
    results = []
    for c in _genus2_cache:
        cond = c.get("conductor", 0)
        if low <= cond <= high:
            results.append({
                "source": "Genus2",
                "id": c["label"],
                "label": f"g2c cond={cond}",
                "match_reason": f"Conductor {cond} in [{low},{high}]",
                "data": c,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"]["conductor"])
    return results[:max_results]


def genus2_search_rank(rank: int = 0, max_results: int = 50) -> list[dict]:
    """Search genus-2 curves by analytic rank. Uses analytic_rank if available, else root_number parity."""
    _load_genus2()
    results = []
    for c in _genus2_cache:
        ar = c.get("analytic_rank")
        if ar is not None:
            match = (ar == rank)
        else:
            rn = c.get("root_number")
            if rank == 0 and rn == 1:
                match = True
            elif rank >= 1 and rn == -1:
                match = True
            else:
                match = False
        if match:
            ar_str = str(ar) if ar is not None else f"rn={c.get('root_number')}"
            results.append({
                "source": "Genus2",
                "id": c["label"],
                "label": f"g2c rank={ar_str}",
                "match_reason": f"Analytic rank = {ar_str}",
                "data": c,
                "score": 1.0,
            })
    return results[:max_results]


def genus2_search_st_group(st_group: str = "USp(4)",
                           max_results: int = 50) -> list[dict]:
    """Search genus-2 curves by Sato-Tate group."""
    _load_genus2()
    target = st_group.lower()
    results = []
    for c in _genus2_cache:
        if target in c.get("st_group", "").lower():
            results.append({
                "source": "Genus2",
                "id": c["label"],
                "label": f"g2c ST={c['st_group']}",
                "match_reason": f"Sato-Tate group matches '{st_group}'",
                "data": c,
                "score": 1.0,
            })
    return results[:max_results]


def genus2_search_endomorphism(end_alg: str = "Q", max_results: int = 50) -> list[dict]:
    """Search genus-2 curves by endomorphism algebra (Q, RM, CM, QM)."""
    _load_genus2()
    target = end_alg.upper()
    results = []
    for c in _genus2_cache:
        ea = str(c.get("end_alg", "")).upper()
        if target in ea:
            results.append({
                "source": "Genus2",
                "id": c["label"],
                "label": f"g2c end={c.get('end_alg')}",
                "match_reason": f"Endomorphism algebra matches '{end_alg}'",
                "data": c,
                "score": 1.0,
            })
    return results[:max_results]


def genus2_search_gl2(is_gl2: bool = True, max_results: int = 50) -> list[dict]:
    """Search genus-2 curves by GL(2)-type (modular abelian surface)."""
    _load_genus2()
    results = []
    for c in _genus2_cache:
        if c.get("is_gl2_type") == is_gl2:
            results.append({
                "source": "Genus2",
                "id": c["label"],
                "label": f"g2c GL2={is_gl2}",
                "match_reason": f"is_gl2_type = {is_gl2}",
                "data": c,
                "score": 1.0,
            })
    return results[:max_results]


def genus2_stats() -> list[dict]:
    """Summary statistics for genus-2 curves."""
    _load_genus2()
    if not _genus2_cache:
        return [{"error": "No genus-2 data loaded"}]
    conductors = [c["conductor"] for c in _genus2_cache if c.get("conductor")]
    st_groups = {}
    for c in _genus2_cache:
        sg = c.get("st_group", "unknown")
        st_groups[sg] = st_groups.get(sg, 0) + 1
    rank_dist = {}
    for c in _genus2_cache:
        ar = c.get("analytic_rank")
        if ar is not None:
            rank_dist[ar] = rank_dist.get(ar, 0) + 1
    end_algs = {}
    for c in _genus2_cache:
        ea = c.get("end_alg", "unknown")
        end_algs[ea] = end_algs.get(ea, 0) + 1
    return [{
        "source": "Genus2",
        "id": "genus2_stats",
        "label": "Genus-2 Curve Statistics",
        "match_reason": "Summary",
        "data": {
            "n_curves": len(_genus2_cache),
            "conductor_range": [min(conductors), max(conductors)] if conductors else [],
            "st_group_distribution": dict(sorted(st_groups.items(), key=lambda x: -x[1])[:15]),
            "analytic_rank_distribution": dict(sorted(rank_dist.items())),
            "endomorphism_algebra_distribution": dict(sorted(end_algs.items(), key=lambda x: -x[1])),
            "root_number_counts": {
                "+1 (even rank)": sum(1 for c in _genus2_cache if c.get("root_number") == 1),
                "-1 (odd rank)": sum(1 for c in _genus2_cache if c.get("root_number") == -1),
            },
            "gl2_type_count": sum(1 for c in _genus2_cache if c.get("is_gl2_type")),
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Maass Forms (35,416 rigorously computed forms from LMFDB)
# ---------------------------------------------------------------------------

_maass_cache: list = []


def _load_maass():
    """Lazy-load Maass forms. Prefer postgres dump (richer fields), fall back to local."""
    if _maass_cache:
        return
    src = None
    for path in [MAASS_PG, MAASS_JSON]:
        if path.exists():
            src = path
            break
    if src is None:
        print(f"  [Maass] WARNING: No Maass data found")
        return
    print(f"  [Maass] Loading {src.name}...")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle postgres envelope or flat list
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = []
    # Normalize fields across data sources
    for r in records:
        # Convert spectral_parameter from high-precision string to float
        sp = r.get("spectral_parameter")
        if isinstance(sp, str):
            try:
                r["spectral_parameter"] = float(sp)
            except (ValueError, OverflowError):
                r["spectral_parameter"] = None
        # Normalize field names: local uses 'label'/'fricke', postgres uses 'maass_label'/'fricke_eigenvalue'
        if "maass_label" not in r and "label" in r:
            r["maass_label"] = r["label"]
        if "fricke_eigenvalue" not in r and "fricke" in r:
            r["fricke_eigenvalue"] = r["fricke"]
    _maass_cache.extend(records)
    print(f"  [Maass] Loaded {len(_maass_cache):,} forms from {src.name}")


def maass_search_spectral(low: float = 0.0, high: float = 50.0,
                          max_results: int = 50) -> list[dict]:
    """Search Maass forms by spectral parameter range."""
    _load_maass()
    results = []
    for m in _maass_cache:
        sp = m.get("spectral_parameter")
        if sp is not None and low <= sp <= high:
            results.append({
                "source": "Maass",
                "id": m.get("maass_label", ""),
                "label": f"Maass R={sp:.4f}",
                "match_reason": f"Spectral parameter {sp:.6f} in [{low},{high}]",
                "data": m,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"].get("spectral_parameter", 0))
    return results[:max_results]


def maass_search_symmetry(symmetry: str = "even",
                          max_results: int = 50) -> list[dict]:
    """Search Maass forms by symmetry type (even/odd)."""
    _load_maass()
    target = symmetry.lower()
    results = []
    for m in _maass_cache:
        sym = str(m.get("symmetry", "")).lower()
        # symmetry may be stored as 0/1 or even/odd
        match = (target == sym) or (target == "even" and sym in ("0", "even")) or (target == "odd" and sym in ("1", "odd"))
        if match:
            results.append({
                "source": "Maass",
                "id": m.get("maass_label", ""),
                "label": f"Maass sym={symmetry}",
                "match_reason": f"Symmetry = {symmetry}",
                "data": m,
                "score": 1.0,
            })
    return results[:max_results]


def maass_search_level(level: int = 1, max_results: int = 50) -> list[dict]:
    """Search Maass forms by level (conductor)."""
    _load_maass()
    results = []
    for m in _maass_cache:
        if m.get("level") == level:
            sp = m.get("spectral_parameter", 0)
            results.append({
                "source": "Maass",
                "id": m.get("maass_label", ""),
                "label": f"Maass level={level} R={sp:.4f}" if sp else f"Maass level={level}",
                "match_reason": f"Level = {level}",
                "data": m,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"].get("spectral_parameter", 0))
    return results[:max_results]


def maass_search_fricke(fricke: int = 1, max_results: int = 50) -> list[dict]:
    """Search Maass forms by Fricke eigenvalue (+1 or -1)."""
    _load_maass()
    results = []
    for m in _maass_cache:
        if m.get("fricke_eigenvalue") == fricke:
            sp = m.get("spectral_parameter", 0)
            results.append({
                "source": "Maass",
                "id": m.get("maass_label", ""),
                "label": f"Maass fricke={fricke} R={sp:.4f}" if sp else f"Maass fricke={fricke}",
                "match_reason": f"Fricke eigenvalue = {fricke}",
                "data": m,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"].get("spectral_parameter", 0))
    return results[:max_results]


def maass_stats() -> list[dict]:
    """Summary statistics for Maass forms."""
    _load_maass()
    if not _maass_cache:
        return [{"error": "No Maass data loaded"}]
    spectral = [m["spectral_parameter"] for m in _maass_cache
                if m.get("spectral_parameter") is not None]
    levels = {}
    for m in _maass_cache:
        lv = m.get("level", "?")
        levels[lv] = levels.get(lv, 0) + 1
    symmetry_counts = {}
    for m in _maass_cache:
        s = m.get("symmetry", "?")
        symmetry_counts[s] = symmetry_counts.get(s, 0) + 1
    return [{
        "source": "Maass",
        "id": "maass_stats",
        "label": "Maass Form Statistics",
        "match_reason": "Summary",
        "data": {
            "n_forms": len(_maass_cache),
            "spectral_range": [min(spectral), max(spectral)] if spectral else [],
            "n_levels": len(levels),
            "level_distribution": dict(sorted(levels.items(), key=lambda x: -x[1])[:20]),
            "symmetry_counts": symmetry_counts,
            "fricke_counts": {
                "+1": sum(1 for m in _maass_cache if m.get("fricke_eigenvalue") == 1),
                "-1": sum(1 for m in _maass_cache if m.get("fricke_eigenvalue") == -1),
            },
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Lattices (root lattices, Leech, etc.)
# ---------------------------------------------------------------------------

_lattices_cache: list = []


def _load_lattices():
    """Lazy-load lattice data. Prefer postgres dump (39K lattices), fall back to local."""
    if _lattices_cache:
        return
    src = None
    for path in [LATTICES_PG, LATTICES_JSON]:
        if path.exists():
            src = path
            break
    if src is None:
        print(f"  [Lattices] WARNING: No lattice data found")
        return
    print(f"  [Lattices] Loading {src.name}...")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle postgres envelope, dict-with-lattices-key, or flat list
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, dict) and "lattices" in data:
        records = data["lattices"]
    elif isinstance(data, list):
        records = data
    else:
        records = []
    # Normalize: local had 'dimension'/'determinant', postgres has 'dim'/'det'
    for r in records:
        if "dimension" in r and "dim" not in r:
            r["dim"] = r["dimension"]
        if "determinant" in r and "det" not in r:
            r["det"] = r["determinant"]
        if "minimal_vector" in r and "minimum" not in r:
            r["minimum"] = r["minimal_vector"]
        if "aut_group_order" in r and "aut" not in r:
            r["aut"] = r["aut_group_order"]
        if "name" not in r:
            r["name"] = r.get("label", "")
    _lattices_cache.extend(records)
    print(f"  [Lattices] Loaded {len(_lattices_cache):,} lattices from {src.name}")


def lattices_search(keyword: str = "", max_results: int = 50) -> list[dict]:
    """Search lattices by name or label keyword (e.g. 'Leech', 'E8', 'A2')."""
    _load_lattices()
    kw = keyword.lower()
    results = []
    for lat in _lattices_cache:
        name = lat.get("name", "")
        label = lat.get("label", "")
        searchable = f"{name} {label}".lower()
        if not kw or kw in searchable:
            display = name if name else label
            results.append({
                "source": "Lattices",
                "id": label or name,
                "label": f"{display} (dim={lat.get('dim')}, det={lat.get('det')})",
                "match_reason": f"Name/label contains '{keyword}'" if kw else "All lattices",
                "data": lat,
                "score": 1.0 if kw and kw in name.lower() else 0.8,
            })
    results.sort(key=lambda x: (-x["score"], x["data"].get("dim", 0)))
    return results[:max_results]


def lattices_by_dimension(dimension: int, max_results: int = 50) -> list[dict]:
    """Search lattices by dimension."""
    _load_lattices()
    results = []
    for lat in _lattices_cache:
        if lat.get("dim") == dimension:
            display = lat.get("name") or lat.get("label", "")
            results.append({
                "source": "Lattices",
                "id": lat.get("label", display),
                "label": f"{display} (kissing={lat.get('kissing')}, det={lat.get('det')})",
                "match_reason": f"Dimension = {dimension}",
                "data": lat,
                "score": 1.0,
            })
    return results[:max_results]


def lattices_by_det(det_low: int = 1, det_high: int = 100,
                    max_results: int = 50) -> list[dict]:
    """Search lattices by determinant range."""
    _load_lattices()
    results = []
    for lat in _lattices_cache:
        d = lat.get("det")
        if d is not None and det_low <= d <= det_high:
            display = lat.get("name") or lat.get("label", "")
            results.append({
                "source": "Lattices",
                "id": lat.get("label", display),
                "label": f"{display} (dim={lat.get('dim')}, det={d})",
                "match_reason": f"Determinant {d} in [{det_low},{det_high}]",
                "data": lat,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"].get("det", 0))
    return results[:max_results]


def lattices_by_class_number(class_number: int = 1,
                             max_results: int = 50) -> list[dict]:
    """Search lattices by class number (genus class number)."""
    _load_lattices()
    results = []
    for lat in _lattices_cache:
        if lat.get("class_number") == class_number:
            display = lat.get("name") or lat.get("label", "")
            results.append({
                "source": "Lattices",
                "id": lat.get("label", display),
                "label": f"{display} (dim={lat.get('dim')}, det={lat.get('det')})",
                "match_reason": f"Class number = {class_number}",
                "data": lat,
                "score": 1.0,
            })
    return results[:max_results]


def lattices_stats() -> list[dict]:
    """Summary statistics for lattices."""
    _load_lattices()
    if not _lattices_cache:
        return [{"error": "No lattice data loaded"}]
    dims = [l["dim"] for l in _lattices_cache if "dim" in l]
    dets = [l["det"] for l in _lattices_cache if "det" in l]
    cn = {}
    for l in _lattices_cache:
        c = l.get("class_number", "?")
        cn[c] = cn.get(c, 0) + 1
    dim_dist = {}
    for d in dims:
        dim_dist[d] = dim_dist.get(d, 0) + 1
    return [{
        "source": "Lattices",
        "id": "lattices_stats",
        "label": "Lattice Statistics",
        "match_reason": "Summary",
        "data": {
            "n_lattices": len(_lattices_cache),
            "dimension_range": [min(dims), max(dims)] if dims else [],
            "determinant_range": [min(dets), max(dets)] if dets else [],
            "dimension_distribution": dict(sorted(dim_dist.items())[:20]),
            "class_number_distribution": dict(sorted(cn.items(), key=lambda x: -x[1])[:15]),
            "named_lattices": sum(1 for l in _lattices_cache if l.get("name")),
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# FindStat (combinatorial statistics on discrete structures)
# ---------------------------------------------------------------------------

_findstat_cache: dict = {}


def _load_findstat():
    """Lazy-load FindStat index."""
    if _findstat_cache:
        return
    if not FINDSTAT_JSON.exists():
        print(f"  [FindStat] WARNING: {FINDSTAT_JSON} not found")
        return
    print(f"  [FindStat] Loading {FINDSTAT_JSON.name}...")
    with open(FINDSTAT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    _findstat_cache.update(data)
    n_stats = len(data.get("statistics", []))
    n_maps = len(data.get("maps", []))
    n_cols = len(data.get("collections", []))
    print(f"  [FindStat] Loaded {n_stats} statistics, {n_maps} maps, {n_cols} collections")


def findstat_search(keyword: str = "", max_results: int = 50) -> list[dict]:
    """Search FindStat statistics by keyword in description or ID."""
    _load_findstat()
    # Try enriched data first
    enriched_path = FINDSTAT_JSON.parent / "findstat_enriched.json"
    if enriched_path.exists() and "enriched" not in _findstat_cache:
        import json as _json
        enriched = _json.loads(enriched_path.read_text(encoding="utf-8"))
        _findstat_cache["enriched"] = enriched.get("statistics", [])

    enriched_stats = _findstat_cache.get("enriched", [])
    if enriched_stats:
        kw = keyword.lower()
        results = []
        for s in enriched_stats:
            sid = s.get("id", "")
            title = s.get("title", "")
            desc = s.get("description", "")
            coll = s.get("collection", "")
            text = f"{sid} {title} {desc} {coll}".lower()
            if not kw or kw in text:
                score = 1.0 if kw and kw in sid.lower() else (0.8 if kw and kw in title.lower() else 0.5)
                results.append({
                    "source": "FindStat",
                    "id": sid,
                    "label": title[:100] if title else sid,
                    "match_reason": f"Matches '{keyword}' in {'title' if kw in title.lower() else 'description'}",
                    "data": {"statistic_id": sid, "collection": coll, "description": desc[:200]},
                    "score": score,
                })
        results.sort(key=lambda x: -x["score"])
        return results[:max_results]

    # Fallback to ID-only
    stats = _findstat_cache.get("statistics", [])
    kw = keyword.upper()
    results = []
    for sid in stats:
        if not kw or kw in sid:
            results.append({
                "source": "FindStat",
                "id": sid,
                "label": sid,
                "match_reason": f"Statistic ID contains '{keyword}'" if kw else "All statistics",
                "data": {"statistic_id": sid},
                "score": 1.0 if kw and kw == sid else 0.5,
            })
    return results[:max_results]


def findstat_stats() -> list[dict]:
    """Summary of FindStat database contents."""
    _load_findstat()
    return [{
        "source": "FindStat",
        "id": "findstat_stats",
        "label": "FindStat Summary",
        "match_reason": "Summary",
        "data": {
            "n_statistics": len(_findstat_cache.get("statistics", [])),
            "n_maps": len(_findstat_cache.get("maps", [])),
            "n_collections": len(_findstat_cache.get("collections", [])),
            "sample_statistics": _findstat_cache.get("statistics", [])[:10],
            "sample_collections": _findstat_cache.get("collections", [])[:10],
            "sample_maps": _findstat_cache.get("maps", [])[:10],
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Small Groups (GAP SmallGrp library — number of groups of order n)
# ---------------------------------------------------------------------------

_smallgroups_cache: list = []


def _load_smallgroups():
    """Lazy-load small groups data."""
    if _smallgroups_cache:
        return
    if not SMALLGROUPS_JSON.exists():
        print(f"  [SmallGroups] WARNING: {SMALLGROUPS_JSON} not found")
        return
    print(f"  [SmallGroups] Loading {SMALLGROUPS_JSON.name}...")
    with open(SMALLGROUPS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    _smallgroups_cache.extend(data.get("groups", []))
    print(f"  [SmallGroups] Loaded {len(_smallgroups_cache):,} orders")


def smallgroups_search_order(order: int, max_results: int = 50) -> list[dict]:
    """Search for groups of a specific order."""
    _load_smallgroups()
    results = []
    for g in _smallgroups_cache:
        if g.get("order") == order:
            results.append({
                "source": "SmallGroups",
                "id": f"order_{order}",
                "label": f"{g.get('n_groups', '?')} groups of order {order}",
                "match_reason": f"Order = {order}",
                "data": g,
                "score": 1.0,
            })
    return results[:max_results]


def smallgroups_search_count(min_groups: int = 1, max_groups: int = 100,
                             max_results: int = 50) -> list[dict]:
    """Search for orders with a specific number of groups."""
    _load_smallgroups()
    results = []
    for g in _smallgroups_cache:
        ng = g.get("n_groups", 0)
        if ng is not None and min_groups <= ng <= max_groups:
            results.append({
                "source": "SmallGroups",
                "id": f"order_{g['order']}",
                "label": f"{ng} groups of order {g['order']}",
                "match_reason": f"n_groups={ng} in [{min_groups},{max_groups}]",
                "data": g,
                "score": 1.0,
            })
    results.sort(key=lambda x: x["data"].get("n_groups", 0))
    return results[:max_results]


def smallgroups_stats() -> list[dict]:
    """Summary statistics for the small groups library."""
    _load_smallgroups()
    if not _smallgroups_cache:
        return [{"error": "No small groups data loaded"}]
    orders = [g["order"] for g in _smallgroups_cache]
    counts = [g.get("n_groups", 0) for g in _smallgroups_cache if g.get("n_groups")]
    abelian_only = sum(1 for g in _smallgroups_cache if g.get("all_abelian"))
    return [{
        "source": "SmallGroups",
        "id": "smallgroups_stats",
        "label": "Small Groups Library Statistics",
        "match_reason": "Summary",
        "data": {
            "n_orders": len(_smallgroups_cache),
            "order_range": [min(orders), max(orders)] if orders else [],
            "total_groups": sum(counts),
            "max_groups_at_order": max(counts) if counts else 0,
            "all_abelian_orders": abelian_only,
            "prime_orders": sum(1 for g in _smallgroups_cache if g.get("is_prime")),
        },
        "score": 1.0,
    }]


# ---------------------------------------------------------------------------
# Dispatcher — route search requests from hypotheses
# ---------------------------------------------------------------------------

SEARCH_REGISTRY = {
    "oeis_terms": oeis_search_terms,
    "oeis_crossrefs": oeis_crossrefs,
    "oeis_xref_hubs": oeis_xref_hubs,
    "oeis_sleeping_beauties": oeis_sleeping_beauties,
    "oeis_keyword": oeis_search_keyword,  # Re-enabled — James downloaded names.txt
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
    "nf_degree": nf_search_degree,
    "nf_class_number": nf_search_class_number,
    "nf_class_distribution": nf_class_number_distribution,
    "polytopes_fvector": polytopes_search_fvector,
    "polytopes_dimension": polytopes_search_dimension,
    "pibase_property": pibase_search_property,
    "pibase_space": pibase_search_space,
    "mmlkg_article": mmlkg_search_article,
    "mmlkg_stats": mmlkg_stats,
    "isogeny_prime": isogeny_search_prime,
    "isogeny_stats": isogeny_stats,
    "local_fields_search": local_fields_search,
    "spacegroup_search": spacegroup_search,
    "spacegroup_crystal_system": spacegroup_by_crystal_system,
    "openalex_concept": openalex_concept,
    "openalex_hierarchy": openalex_hierarchy,
    "genus2_conductor": genus2_search_conductor,
    "genus2_rank": genus2_search_rank,
    "genus2_st_group": genus2_search_st_group,
    "genus2_endomorphism": genus2_search_endomorphism,
    "genus2_gl2": genus2_search_gl2,
    "genus2_stats": genus2_stats,
    "maass_spectral": maass_search_spectral,
    "maass_symmetry": maass_search_symmetry,
    "maass_level": maass_search_level,
    "maass_fricke": maass_search_fricke,
    "maass_stats": maass_stats,
    "lattices_search": lattices_search,
    "lattices_dimension": lattices_by_dimension,
    "lattices_det": lattices_by_det,
    "lattices_class_number": lattices_by_class_number,
    "lattices_stats": lattices_stats,
    "findstat_search": findstat_search,
    "findstat_stats": findstat_stats,
    "smallgroups_order": smallgroups_search_order,
    "smallgroups_count": smallgroups_search_count,
    "smallgroups_stats": smallgroups_stats,
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
        "searches": ["oeis_terms", "oeis_growth", "oeis_by_id", "oeis_find_containing", "oeis_crossrefs", "oeis_xref_hubs", "oeis_sleeping_beauties"],
        "prompt_block": """OEIS (392K integer sequences, 1.6M cross-reference edges, 64K sleeping beauties):
- oeis_terms(target_terms=[list of ints], min_match=5) — find sequences containing these numbers. MUST pass actual integers, not strings.
- oeis_by_id(seq_id="A000040") — fetch a specific sequence by A-number
- oeis_find_containing(integers=[list of ints], min_fraction=0.5) — find sequences covering the input set. MUST pass actual integers like [3,5,7,11,13].
- oeis_growth(growth_type="exponential|polynomial|super-exponential|sub-linear") — find by growth class
- oeis_crossrefs(seq_id="A000045") — find all sequences cross-referenced by/to this sequence (the OEIS citation graph)
- oeis_xref_hubs(min_degree=50) — find hub sequences with many cross-references
- oeis_sleeping_beauties(min_entropy=4.0, max_degree=2) — find Sleeping Beauty sequences: high internal structure, low connectivity. The dark matter of mathematics.""",
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
    "number_fields": {
        "name": "Number Fields",
        "description": "9.1K algebraic number fields with class numbers, discriminants, Galois groups, regulators",
        "path": NUMBER_FIELDS_JSON,
        "searches": ["nf_degree", "nf_class_number", "nf_class_distribution"],
        "prompt_block": """Number Fields (9.1K algebraic number fields):
- nf_degree(degree=2) — find fields by degree (quadratic, cubic, etc.)
- nf_class_number(class_number=1) — find fields with a specific class number. Bridge to OEIS.
- nf_class_distribution() — distribution of class numbers across all fields. Battery-testable.""",
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
    "polytopes": {
        "name": "polyDB Polytopes",
        "description": "Polytopes from polyDB: combinatorial, lattice, tropical collections with f-vectors and dimensions",
        "path": POLYTOPES_DIR,
        "searches": ["polytopes_fvector", "polytopes_dimension"],
        "prompt_block": """polyDB Polytopes (17 collections, combinatorial/lattice/tropical):
- polytopes_fvector(dimension=3) — find polytopes by dimension, return f-vectors
- polytopes_dimension(dimension=4) — find all polytopes of a given dimension""",
    },
    "pibase": {
        "name": "pi-Base Topology",
        "description": "220 topological spaces with 230 properties from Steen & Seebach pi-Base",
        "path": PIBASE_DIR,
        "searches": ["pibase_property", "pibase_space"],
        "prompt_block": """pi-Base Topology (220 spaces, 230 properties):
- pibase_property(property_name="compact"|"Hausdorff"|"metrizable"|etc) — find spaces with a topological property
- pibase_space(space_name="real line"|"Sorgenfrey"|etc) — search spaces by name or alias""",
    },
    "mmlkg": {
        "name": "MMLKG Theorem References",
        "description": "464K theorem reference edges from Mizar Mathematical Library Knowledge Graph",
        "path": MMLKG_REFS,
        "searches": ["mmlkg_article", "mmlkg_stats"],
        "prompt_block": """MMLKG — Mizar Mathematical Library Knowledge Graph (464K reference edges):
- mmlkg_article(article="tarski"|"xboole"|etc) — find articles referencing or referenced by a given article
- mmlkg_stats() — graph statistics: n_articles, n_edges, top hub articles""",
    },
    "isogenies": {
        "name": "Isogeny Graphs",
        "description": "3.2K supersingular isogeny graphs indexed by prime, with adjacency matrices for multiple isogeny degrees",
        "path": ISOGENY_GRAPHS,
        "searches": ["isogeny_prime", "isogeny_stats"],
        "prompt_block": """Isogeny Graphs (3.2K primes, supersingular isogeny graphs):
- isogeny_prime(prime=13) — find isogeny graph data for a specific prime (nodes, spine, diameters per ell)
- isogeny_stats() — summary statistics: n_primes, node counts, prime range""",
    },
    "local_fields": {
        "name": "Local Fields",
        "description": "Wildly ramified local field extensions (LMFDB format) indexed by prime and degree",
        "path": LOCAL_FIELDS_DIR,
        "searches": ["local_fields_search"],
        "prompt_block": """Local Fields (wildly ramified extensions):
- local_fields_search(prime=2) — find wildly ramified extensions by ramification prime (available: 2, 3, 5)""",
    },
    "spacegroups": {
        "name": "Bilbao Space Groups",
        "description": "230 crystallographic space groups with generators, Wyckoff positions, point groups",
        "path": BILBAO_DIR,
        "searches": ["spacegroup_search", "spacegroup_crystal_system"],
        "prompt_block": """Bilbao Space Groups (230 crystallographic space groups):
- spacegroup_search(sg_number=1) — find space group by ITA number (1-230)
- spacegroup_crystal_system(system="cubic"|"hexagonal"|"trigonal"|"tetragonal"|"orthorhombic"|"monoclinic"|"triclinic") — find all SGs in a crystal system""",
    },
    "openalex": {
        "name": "OpenAlex Concepts",
        "description": "10K academic concepts from OpenAlex taxonomy with 6 hierarchy levels, works counts, and descriptions",
        "path": OPENALEX_CONCEPTS,
        "searches": ["openalex_concept", "openalex_hierarchy"],
        "prompt_block": """OpenAlex Concept Taxonomy (10K academic concepts, 6 hierarchy levels):
- openalex_concept(keyword="topology"|"number theory"|etc) — find concepts by name or description keyword
- openalex_hierarchy(concept_id="https://openalex.org/C41008148"|"C41008148"|"Mathematics") — find parent/child concepts in the hierarchy""",
    },
    "genus2": {
        "name": "Genus-2 Curves",
        "description": "66K genus-2 curves from LMFDB with conductors, analytic ranks, Sato-Tate groups, endomorphism algebras, Igusa invariants",
        "path": GENUS2_PG if GENUS2_PG.exists() else GENUS2_JSON,
        "searches": ["genus2_conductor", "genus2_rank", "genus2_st_group", "genus2_endomorphism", "genus2_gl2", "genus2_stats"],
        "prompt_block": """Genus-2 Curves (66K curves from LMFDB g2c database, 50+ fields per curve):
- genus2_conductor(low=1, high=1000) — search curves by conductor range. Bridges to LMFDB EC conductors and number field discriminants.
- genus2_rank(rank=0) — search by analytic rank (0, 1, 2, ...). Uses proven analytic_rank when available.
- genus2_st_group(st_group="USp(4)") — search by Sato-Tate group. Bridges to Galois representations.
- genus2_endomorphism(end_alg="Q"|"RM"|"CM"|"QM") — search by endomorphism algebra. GL(2)-type iff end_alg != "Q".
- genus2_gl2(is_gl2=True) — search by GL(2)-type flag. These are modular abelian surfaces.
- genus2_stats() — summary: conductor range, ST group distribution, rank distribution, endomorphism algebras.""",
    },
    "maass": {
        "name": "Maass Forms",
        "description": "35K rigorously computed Maass forms with spectral parameters, levels, symmetry, Fricke eigenvalues",
        "path": MAASS_PG if MAASS_PG.exists() else MAASS_JSON,
        "searches": ["maass_spectral", "maass_symmetry", "maass_level", "maass_fricke", "maass_stats"],
        "prompt_block": """Maass Forms (35,416 rigorously computed, LMFDB):
- maass_spectral(low=9.0, high=50.0) — search by spectral parameter range. The spectral parameters are eigenvalues of the Laplacian on the upper half-plane.
- maass_symmetry(symmetry="even"|"odd") — search by symmetry type (0=even, 1=odd).
- maass_level(level=1) — search by level (conductor). Level 1 forms live on SL(2,Z)\\H.
- maass_fricke(fricke=1) — search by Fricke eigenvalue (+1 or -1). Determines functional equation sign.
- maass_stats() — summary: spectral range, level distribution, symmetry counts, Fricke eigenvalue counts.""",
    },
    "lattices": {
        "name": "Lattices",
        "description": "39K integral lattices from LMFDB with dimensions, determinants, kissing numbers, class numbers, theta series",
        "path": LATTICES_PG if LATTICES_PG.exists() else LATTICES_JSON,
        "searches": ["lattices_search", "lattices_dimension", "lattices_det", "lattices_class_number", "lattices_stats"],
        "prompt_block": """Lattices (39,293 integral lattices from LMFDB):
- lattices_search(keyword="Leech"|"E8"|"") — search by name or label. Bridges to modular forms, sphere packing, coding theory.
- lattices_dimension(dimension=8) — find lattices by dimension. Dimension distribution bridges to number fields.
- lattices_det(det_low=1, det_high=100) — search by determinant range. Determinant bridges to discriminants.
- lattices_class_number(class_number=1) — search by genus class number. Connects to mass formulas.
- lattices_stats() — summary: dimension range, determinant range, class number distribution.""",
    },
    "findstat": {
        "name": "FindStat",
        "description": "1993 combinatorial statistics, 336 maps, 24 collections on discrete structures",
        "path": FINDSTAT_JSON,
        "searches": ["findstat_search", "findstat_stats"],
        "prompt_block": """FindStat (1993 combinatorial statistics, 336 maps, 24 collections):
- findstat_search(keyword="St000001") — search statistic IDs. Currently ID-only index.
- findstat_stats() — summary: counts of statistics, maps, collections with samples.""",
    },
    "smallgroups": {
        "name": "Small Groups",
        "description": "2,416 orders with group counts from GAP SmallGrp (A000001), factorizations, abelian/cyclic flags",
        "path": SMALLGROUPS_JSON,
        "searches": ["smallgroups_order", "smallgroups_count", "smallgroups_stats"],
        "prompt_block": """Small Groups (2,416 orders, GAP SmallGrp library, OEIS A000001):
- smallgroups_order(order=12) — find groups of a specific order (returns count, factorization, properties)
- smallgroups_count(min_groups=1, max_groups=10) — find orders with N groups. Bridges to OEIS A000001 and number field Galois groups.
- smallgroups_stats() — summary: order range, total groups, abelian-only count.""",
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
