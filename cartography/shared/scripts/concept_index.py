"""
Concept Index — Atomic concept extraction and bridge detection.
================================================================
Extracts normalized concepts from all datasets and finds cross-domain
bridges (Swanson's ABC model as a database join).

Concepts are atomic: "prime", "modular_form", "determinant_5", "conductor_11".
Links are many-to-many: each dataset object maps to multiple concepts.
Bridges are concept-sharing pairs across different datasets.

Storage:
  convergence/data/concepts.jsonl       — the atoms
  convergence/data/concept_links.jsonl  — many-to-many edges
  convergence/data/bridges.jsonl        — cross-domain bridges

Usage:
    from concept_index import build_index, find_bridges
    build_index()        # Extract concepts from all datasets
    find_bridges()       # Detect cross-domain connections

    python concept_index.py   # Full build + bridge detection
"""

import json
import math
import re
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
CONCEPTS_FILE = CONVERGENCE / "data" / "concepts.jsonl"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
BRIDGES_FILE = CONVERGENCE / "data" / "bridges.jsonl"


def _is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def _number_concepts(n: int) -> list[str]:
    """Extract mathematical property concepts from an integer."""
    concepts = []
    if isinstance(n, int) and n > 0:
        concepts.append(f"integer_{n}")
        if _is_prime(n):
            concepts.append("prime")
        if n % 2 == 1:
            concepts.append("odd")
        else:
            concepts.append("even")
        if int(math.sqrt(n)) ** 2 == n:
            concepts.append("perfect_square")
        if n < 100:
            concepts.append("small_integer")
        elif n < 1000:
            concepts.append("medium_integer")
        else:
            concepts.append("large_integer")
    return concepts


# ---------------------------------------------------------------------------
# Extractors — one per dataset
# ---------------------------------------------------------------------------

def extract_knotinfo() -> tuple[list[dict], list[dict]]:
    """Extract concepts from KnotInfo knots."""
    from search_engine import _load_knots, _knots_cache, KNOTS_JSON
    if not KNOTS_JSON.exists(): return [], []
    _load_knots()

    concepts = set()
    links = []

    for knot in _knots_cache.get("knots", []):
        name = knot["name"]
        det = knot.get("determinant")
        crossing = knot.get("crossing_number", 0)

        knot_concepts = [f"crossing_{crossing}"]
        if det is not None:
            knot_concepts.extend(_number_concepts(det))
            knot_concepts.append(f"determinant_{det}")
        if knot.get("alex_coeffs"):
            knot_concepts.append("has_alexander_polynomial")
        if knot.get("jones_coeffs"):
            knot_concepts.append("has_jones_polynomial")

        for c in knot_concepts:
            concepts.add(c)
            links.append({
                "concept": c, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "KnotInfo"} for c in concepts], links


def extract_lmfdb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from LMFDB objects."""
    from search_engine import _get_duck, CHARON_DB
    if not CHARON_DB.exists(): return [], []

    concepts = set()
    links = []

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, object_type, conductor,
               json_extract_string(properties, '$.rank') as rank
        FROM objects LIMIT 50000
    """).fetchall()
    con.close()

    for label, obj_type, conductor, rank in rows:
        obj_concepts = [f"object_type_{obj_type}"]

        if conductor:
            c = int(conductor)
            obj_concepts.extend(_number_concepts(c))
            obj_concepts.append(f"conductor_{c}")

        if rank is not None:
            obj_concepts.append(f"rank_{rank}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LMFDB", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "LMFDB"} for c in concepts], links


def extract_fungrim() -> tuple[list[dict], list[dict]]:
    """Extract concepts from Fungrim formulas."""
    from search_engine import FUNGRIM_JSON
    if not FUNGRIM_JSON.exists(): return [], []
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for formula in data.get("formulas", []):
        fid = formula["id"]
        module = formula["module"]
        concepts.add(f"topic_{module}")
        links.append({
            "concept": f"topic_{module}", "dataset": "Fungrim", "object_id": fid,
            "relationship": "in_module",
        })
        for symbol in formula.get("symbols", []):
            sym_concept = f"symbol_{symbol}"
            concepts.add(sym_concept)
            links.append({
                "concept": sym_concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "uses_symbol",
            })

    return [{"id": c, "type": "symbol" if c.startswith("symbol_") else "topic",
             "source": "Fungrim"} for c in concepts], links


def extract_antedb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from ANTEDB theorems."""
    from search_engine import ANTEDB_JSON
    if not ANTEDB_JSON.exists(): return [], []
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for chapter in data.get("chapters", []):
        ch_name = chapter["chapter"]
        concepts.add(f"topic_{ch_name}")
        for thm in chapter.get("theorems", []):
            tid = f"{ch_name}/{thm['label']}"
            links.append({
                "concept": f"topic_{ch_name}", "dataset": "ANTEDB", "object_id": tid,
                "relationship": "in_chapter",
            })
            for val in thm.get("numerical_values", []):
                concepts.add(f"bound_{val}")
                links.append({
                    "concept": f"bound_{val}", "dataset": "ANTEDB", "object_id": tid,
                    "relationship": "has_bound",
                })

    return [{"id": c, "type": "topic" if "topic_" in c else "bound",
             "source": "ANTEDB"} for c in concepts], links


def extract_mathlib() -> tuple[list[dict], list[dict]]:
    """Extract concepts from mathlib namespace hierarchy."""
    from search_engine import MATHLIB_GRAPH, _load_mathlib, _mathlib_graph
    if not MATHLIB_GRAPH.exists(): return [], []
    _load_mathlib()

    concepts = set()
    links = []

    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        parts = name.split(".")
        # Extract namespace as concept
        if len(parts) >= 2:
            ns = parts[1] if parts[0] == "Mathlib" else parts[0]
            concept = f"namespace_{ns}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "mathlib", "object_id": name,
                "relationship": "in_namespace",
            })
        # Last part is often the specific topic
        if len(parts) >= 3:
            topic = parts[-1]
            if len(topic) > 3:
                concept = f"topic_{topic}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "mathlib", "object_id": name,
                    "relationship": "about",
                })

    return [{"id": c, "type": "namespace" if "namespace_" in c else "topic",
             "source": "mathlib"} for c in concepts], links


# ---------------------------------------------------------------------------
# Verb concept extractors — cross-domain bridges
# ---------------------------------------------------------------------------

# Canonical math tokens: map variations to a single normalized form so that
# the same mathematical idea from different datasets lands on the same concept.
_CANONICAL = {
    "Zeta": "zeta", "RiemannZeta": "zeta", "DirichletLFunction": "l_function",
    "LFunction": "l_function", "LSeries": "l_function",
    "BernoulliB": "bernoulli", "Bernoulli": "bernoulli",
    "EulerE": "euler", "Euler": "euler",
    "Integral": "integral", "integral": "integral",
    "Sum": "sum", "Product": "product",
    "Equal": "equal", "Inequality": "inequality",
    "Pi": "pi", "Gamma": "gamma", "GammaFunction": "gamma",
    "Exp": "exp", "Log": "log",
    "Sin": "sin", "Cos": "cos", "Theta": "theta",
    "Modular": "modular", "ModularForm": "modular_form",
    "Elliptic": "elliptic", "EllipticCurve": "elliptic_curve",
    "Prime": "prime", "Primes": "prime",
    "Polynomial": "polynomial", "Poly": "polynomial",
    "Matrix": "matrix", "Determinant": "determinant",
    "Conductor": "conductor", "Rank": "rank",
    "Bound": "bound", "Estimate": "estimate",
    "Convergence": "convergence", "Limit": "limit",
    "NumberTheory": "number_theory", "Analysis": "analysis",
    "Algebra": "algebra", "Topology": "topology",
    "CategoryTheory": "category_theory",
    "Combinatorics": "combinatorics",
    "Probability": "probability",
    "MeasureTheory": "measure_theory",
    "RingTheory": "ring_theory",
    "AlgebraicGeometry": "algebraic_geometry",
    "RepresentationTheory": "representation_theory",
    "LinearAlgebra": "linear_algebra",
    "Alexander": "alexander", "Jones": "jones",
    "Knot": "knot", "Crossing": "crossing",
    "Dirichlet": "dirichlet",
}


def _canonicalize(token: str) -> str:
    """Map a token to its canonical form, or lowercase it."""
    return _CANONICAL.get(token, token.lower())


def _split_camel(name: str) -> list[str]:
    """Split CamelCase or dot-separated names into tokens."""
    # First split on dots and underscores
    parts = re.split(r'[._]', name)
    tokens = []
    for part in parts:
        # Split camelCase
        sub = re.sub(r'([a-z])([A-Z])', r'\1_\2', part)
        for t in sub.split('_'):
            if len(t) > 2:
                tokens.append(t)
    return tokens


def extract_verb_fungrim() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Fungrim: symbol pairs, formula types, cross-module bridges."""
    from search_engine import FUNGRIM_JSON
    if not FUNGRIM_JSON.exists():
        return [], []
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    # Track which modules each symbol appears in (for cross-module bridges)
    symbol_modules = defaultdict(set)

    for formula in data.get("formulas", []):
        fid = formula["id"]
        module = formula.get("module", "")
        ftype = formula.get("type", "")
        symbols = formula.get("symbols", [])

        # 1) Formula type as verb concept
        if ftype:
            concept = f"verb_formula_{ftype}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "has_type",
            })

        # 2) Symbol PAIRS as verb concepts (sorted to deduplicate)
        canon_syms = sorted(set(_canonicalize(s) for s in symbols if len(s) > 2))
        for s1, s2 in combinations(canon_syms[:8], 2):  # cap to avoid combinatorial explosion
            concept = f"verb_{s1}_{s2}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "relates_symbols",
            })

        # 3) Track symbol-module mapping
        for sym in symbols:
            csym = _canonicalize(sym)
            symbol_modules[csym].add(module)

        # 4) Individual canonical symbols as verb concepts (for cross-dataset matching)
        for sym in symbols:
            csym = _canonicalize(sym)
            if len(csym) > 2:
                concept = f"verb_involves_{csym}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "Fungrim", "object_id": fid,
                    "relationship": "involves",
                })

    # 5) Cross-module bridge concepts
    for sym, modules in symbol_modules.items():
        if len(modules) >= 2:
            for m1, m2 in combinations(sorted(modules), 2):
                concept = f"verb_bridges_{m1}_{m2}"
                concepts.add(concept)
                # Link to a synthetic object representing this bridge
                links.append({
                    "concept": concept, "dataset": "Fungrim",
                    "object_id": f"bridge_{sym}_{m1}_{m2}",
                    "relationship": "cross_module_bridge",
                })

    return [{"id": c, "type": "verb", "source": "Fungrim"} for c in concepts], links


def extract_verb_mathlib() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from mathlib: import relationships, cross-namespace bridges."""
    from search_engine import MATHLIB_GRAPH, _load_mathlib, _mathlib_graph
    if not MATHLIB_GRAPH.exists():
        return [], []
    _load_mathlib()

    concepts = set()
    links = []

    # Extract top-level namespaces from nodes
    def _top_ns(name: str) -> str:
        parts = name.split(".")
        if parts[0] == "Mathlib" and len(parts) >= 2:
            return parts[1]
        return parts[0]

    # 1) Import relationship verbs from edges
    edges = _mathlib_graph.get("edges", [])
    # Track cross-namespace imports
    ns_imports = defaultdict(set)  # (src_ns, tgt_ns) pairs

    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            continue
        src, tgt = edge
        src_ns = _top_ns(src)
        tgt_ns = _top_ns(tgt)

        # Import relationship as verb
        concept = f"verb_imports_{_canonicalize(tgt_ns)}"
        concepts.add(concept)
        links.append({
            "concept": concept, "dataset": "mathlib", "object_id": src,
            "relationship": "imports",
        })

        # Cross-namespace bridge
        if src_ns != tgt_ns:
            ns_pair = tuple(sorted([_canonicalize(src_ns), _canonicalize(tgt_ns)]))
            ns_imports[ns_pair].add(src)

    # 2) Cross-namespace connection concepts
    for (ns1, ns2), modules in ns_imports.items():
        concept = f"verb_connects_{ns1}_{ns2}"
        concepts.add(concept)
        # Link a sample of modules (avoid millions of links)
        for mod in list(modules)[:20]:
            links.append({
                "concept": concept, "dataset": "mathlib", "object_id": mod,
                "relationship": "cross_namespace_import",
            })

    # 3) Canonical topic verbs from node names (for cross-dataset matching)
    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        tokens = _split_camel(name)
        for tok in tokens:
            ctok = _canonicalize(tok)
            if len(ctok) > 3:
                concept = f"verb_involves_{ctok}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "mathlib", "object_id": name,
                    "relationship": "involves",
                })

    return [{"id": c, "type": "verb", "source": "mathlib"} for c in concepts], links


def extract_verb_antedb() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from ANTEDB: theorem types, chapter connections."""
    from search_engine import ANTEDB_JSON
    if not ANTEDB_JSON.exists():
        return [], []
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    # Keyword patterns that indicate theorem types
    _TYPE_PATTERNS = {
        "bound": re.compile(r'\b(bound|upper|lower|majoriz|minoriz)\b', re.I),
        "estimate": re.compile(r'\b(estimat|approximat|asymptot)\b', re.I),
        "inequality": re.compile(r'\b(inequalit|leq|geq|≤|≥)\b', re.I),
        "identity": re.compile(r'\b(identity|equals|=)\b', re.I),
        "formula": re.compile(r'\b(formula|explicit|closed.form)\b', re.I),
        "convergence": re.compile(r'\b(converg|limit|tend)\b', re.I),
        "zero": re.compile(r'\b(zero|root|vanish)\b', re.I),
        "prime": re.compile(r'\b(prime|primes|primality)\b', re.I),
        "density": re.compile(r'\b(densit|distribut|counting)\b', re.I),
        "zeta": re.compile(r'\b(zeta|riemann|L.function|l.function)\b', re.I),
        "modular": re.compile(r'\b(modular|automorphic|eisenstein)\b', re.I),
        "elliptic": re.compile(r'\b(elliptic|curve|abelian)\b', re.I),
        "analytic": re.compile(r'\b(analytic|meromorphic|holomorphic)\b', re.I),
    }

    chapter_names = [ch.get("chapter", "") for ch in data.get("chapters", [])]

    for chapter in data.get("chapters", []):
        ch_name = chapter.get("chapter", "")
        ch_canon = _canonicalize(ch_name.replace("_", " ").replace("-", " "))

        for thm in chapter.get("theorems", []):
            tid = f"{ch_name}/{thm['label']}"
            label_text = thm.get("label", "")

            # 1) Theorem type verbs based on label/chapter keywords
            search_text = f"{ch_name} {label_text}"
            for ttype, pattern in _TYPE_PATTERNS.items():
                if pattern.search(search_text):
                    concept = f"verb_proves_{ttype}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                        "relationship": "proves",
                    })

            # 2) Canonical topic verbs (for cross-dataset matching)
            for token in _split_camel(search_text):
                ctok = _canonicalize(token)
                if len(ctok) > 3:
                    concept = f"verb_involves_{ctok}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                        "relationship": "involves",
                    })

            # 3) Chapter connection concepts: link this theorem's chapter to related chapters
            for other_ch in chapter_names:
                if other_ch != ch_name:
                    # Check if the theorem label references concepts from another chapter
                    other_tokens = set(_split_camel(other_ch))
                    label_tokens = set(_split_camel(label_text))
                    shared = other_tokens & label_tokens
                    if shared and any(len(t) > 3 for t in shared):
                        ch1, ch2 = sorted([ch_name, other_ch])
                        concept = f"verb_connects_{_canonicalize(ch1)}_{_canonicalize(ch2)}"
                        concepts.add(concept)
                        links.append({
                            "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                            "relationship": "chapter_connection",
                        })

    return [{"id": c, "type": "verb", "source": "ANTEDB"} for c in concepts], links


def extract_verb_lmfdb() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from LMFDB: object type relationships, property patterns."""
    from search_engine import _get_duck, CHARON_DB
    if not CHARON_DB.exists():
        return [], []

    concepts = set()
    links = []

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, object_type, conductor,
               json_extract_string(properties, '$.rank') as rank,
               json_extract_string(properties, '$.degree') as degree
        FROM objects LIMIT 50000
    """).fetchall()
    con.close()

    for label, obj_type, conductor, rank, degree in rows:
        # 1) Object type as verb: "has_elliptic_curve", "has_modular_form", etc.
        if obj_type:
            concept = f"verb_has_{_canonicalize(obj_type)}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LMFDB", "object_id": label,
                "relationship": "has_type",
            })

            # Also add canonical involvement
            for token in _split_camel(obj_type):
                ctok = _canonicalize(token)
                if len(ctok) > 3:
                    concept = f"verb_involves_{ctok}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })

        # 2) Property patterns
        if conductor is not None:
            c = int(conductor)
            if _is_prime(c):
                concept = "verb_conductor_is_prime"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "LMFDB", "object_id": label,
                    "relationship": "property_pattern",
                })

        if rank is not None:
            try:
                r = int(rank)
                concept = f"verb_has_rank_{r}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "LMFDB", "object_id": label,
                    "relationship": "property_pattern",
                })
                # Generic rank involvement
                concepts.add("verb_involves_rank")
                links.append({
                    "concept": "verb_involves_rank", "dataset": "LMFDB", "object_id": label,
                    "relationship": "involves",
                })
            except (ValueError, TypeError):
                pass

        # 3) Canonical math topic verbs from object type
        if obj_type:
            ot_lower = obj_type.lower()
            if "elliptic" in ot_lower or "ec" == ot_lower:
                for c in ["verb_involves_elliptic", "verb_involves_elliptic_curve"]:
                    concepts.add(c)
                    links.append({
                        "concept": c, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })
            if "modular" in ot_lower or "mf" in ot_lower:
                for c in ["verb_involves_modular", "verb_involves_modular_form"]:
                    concepts.add(c)
                    links.append({
                        "concept": c, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })

    return [{"id": c, "type": "verb", "source": "LMFDB"} for c in concepts], links


def extract_verb_knotinfo() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from KnotInfo: polynomial relationships, crossing patterns."""
    from search_engine import _load_knots, _knots_cache, KNOTS_JSON
    if not KNOTS_JSON.exists():
        return [], []
    _load_knots()

    concepts = set()
    links = []

    for knot in _knots_cache.get("knots", []):
        name = knot["name"]
        crossing = knot.get("crossing_number", 0)

        # 1) Polynomial relationship verbs
        if knot.get("alex_coeffs"):
            concept = "verb_has_alexander_polynomial"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_polynomial",
            })
            # Alexander degree
            deg = len(knot["alex_coeffs"]) - 1
            concept = f"verb_alexander_degree_{deg}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "polynomial_degree",
            })
            # Generic polynomial involvement
            concepts.add("verb_involves_polynomial")
            links.append({
                "concept": "verb_involves_polynomial", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        if knot.get("jones_coeffs"):
            concept = "verb_has_jones_polynomial"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_polynomial",
            })
            concepts.add("verb_involves_polynomial")
            links.append({
                "concept": "verb_involves_polynomial", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        # 2) Crossing pattern verbs
        if crossing > 0:
            if crossing <= 6:
                concept = "verb_low_complexity"
            elif crossing <= 10:
                concept = "verb_medium_complexity"
            else:
                concept = "verb_high_complexity"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "complexity_class",
            })

        # 3) Determinant-related verbs
        det = knot.get("determinant")
        if det is not None:
            if _is_prime(det):
                concept = "verb_determinant_is_prime"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "KnotInfo", "object_id": name,
                    "relationship": "property_pattern",
                })
            # Generic determinant involvement
            concepts.add("verb_involves_determinant")
            links.append({
                "concept": "verb_involves_determinant", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        # 4) Canonical involvement verbs for cross-dataset matching
        concepts.add("verb_involves_knot")
        links.append({
            "concept": "verb_involves_knot", "dataset": "KnotInfo", "object_id": name,
            "relationship": "involves",
        })

    return [{"id": c, "type": "verb", "source": "KnotInfo"} for c in concepts], links


def extract_verb_concepts() -> tuple[list[dict], list[dict]]:
    """
    Master verb extractor: runs all per-dataset verb extractors.
    Returns (concepts, links) aggregated across datasets.
    """
    all_concepts = []
    all_links = []

    verb_extractors = [
        ("Fungrim-verbs", extract_verb_fungrim),
        ("mathlib-verbs", extract_verb_mathlib),
        ("ANTEDB-verbs", extract_verb_antedb),
        ("LMFDB-verbs", extract_verb_lmfdb),
        ("KnotInfo-verbs", extract_verb_knotinfo),
    ]

    for name, fn in verb_extractors:
        print(f"  Extracting {name}...")
        try:
            concepts, links = fn()
            all_concepts.extend(concepts)
            all_links.extend(links)
            print(f"    {len(concepts)} verb concepts, {len(links)} verb links")
        except Exception as e:
            print(f"    ERROR: {e}")

    return all_concepts, all_links


# ---------------------------------------------------------------------------
# Build and query
# ---------------------------------------------------------------------------

def build_index() -> dict:
    """Extract concepts from all datasets. Returns stats."""
    print("Building concept index...")
    CONVERGENCE.joinpath("data").mkdir(parents=True, exist_ok=True)

    all_concepts = {}  # id → concept dict
    all_links = []

    extractors = [
        ("KnotInfo", extract_knotinfo),
        ("LMFDB", extract_lmfdb),
        ("Fungrim", extract_fungrim),
        ("ANTEDB", extract_antedb),
        ("mathlib", extract_mathlib),
    ]

    for name, fn in extractors:
        print(f"  Extracting {name}...")
        try:
            concepts, links = fn()
            for c in concepts:
                cid = c["id"]
                if cid not in all_concepts:
                    all_concepts[cid] = c
                else:
                    # Merge sources
                    existing = all_concepts[cid]
                    if c["source"] not in existing.get("sources", [existing["source"]]):
                        existing.setdefault("sources", [existing["source"]]).append(c["source"])
            all_links.extend(links)
            print(f"    {len(concepts)} concepts, {len(links)} links")
        except Exception as e:
            print(f"    ERROR: {e}")

    # --- Verb concept extraction (cross-domain bridges) ---
    print("\n  Extracting verb concepts (cross-domain bridges)...")
    verb_concepts, verb_links = extract_verb_concepts()
    for c in verb_concepts:
        cid = c["id"]
        if cid not in all_concepts:
            all_concepts[cid] = c
        else:
            existing = all_concepts[cid]
            if c["source"] not in existing.get("sources", [existing["source"]]):
                existing.setdefault("sources", [existing["source"]]).append(c["source"])
    all_links.extend(verb_links)
    n_verb = len(verb_concepts)
    n_verb_links = len(verb_links)
    print(f"    Total: {n_verb} verb concepts, {n_verb_links} verb links")

    # Write concepts
    with open(CONCEPTS_FILE, "w", encoding="utf-8") as f:
        for c in sorted(all_concepts.values(), key=lambda x: x["id"]):
            f.write(json.dumps(c) + "\n")

    # Write links
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for link in all_links:
            f.write(json.dumps(link) + "\n")

    stats = {
        "n_concepts": len(all_concepts),
        "n_links": len(all_links),
        "by_dataset": defaultdict(int),
    }
    for link in all_links:
        stats["by_dataset"][link["dataset"]] += 1
    stats["by_dataset"] = dict(stats["by_dataset"])

    print(f"\nIndex built: {stats['n_concepts']} concepts, {stats['n_links']} links")
    print(f"  By dataset: {stats['by_dataset']}")
    return stats


def find_bridges(min_datasets: int = 2, max_results: int = 100) -> list[dict]:
    """Find concepts shared across multiple datasets — these are bridge points."""
    print("\nFinding bridges...")

    # Load links
    links_by_concept = defaultdict(lambda: defaultdict(list))
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            link = json.loads(line)
            links_by_concept[link["concept"]][link["dataset"]].append(link["object_id"])

    # Find concepts present in 2+ datasets
    bridges = []
    for concept, datasets in links_by_concept.items():
        if len(datasets) >= min_datasets:
            # Skip trivial concepts (too many objects = not informative)
            total_objects = sum(len(objs) for objs in datasets.values())
            if total_objects > 10000:
                continue

            bridge = {
                "concept": concept,
                "n_datasets": len(datasets),
                "datasets": {ds: len(objs) for ds, objs in datasets.items()},
                "total_objects": total_objects,
                "sample_objects": {ds: objs[:5] for ds, objs in datasets.items()},
                "specificity": 1.0 / max(total_objects, 1),
            }
            bridges.append(bridge)

    # Sort by: more datasets first, then more specific (fewer total objects)
    bridges.sort(key=lambda b: (-b["n_datasets"], b["total_objects"]))

    # Write bridges
    with open(BRIDGES_FILE, "w", encoding="utf-8") as f:
        for b in bridges[:max_results]:
            f.write(json.dumps(b) + "\n")

    # Stats
    by_n_datasets = defaultdict(int)
    for b in bridges:
        by_n_datasets[b["n_datasets"]] += 1

    print(f"Found {len(bridges)} bridge concepts")
    print(f"  By dataset count: {dict(by_n_datasets)}")

    # Show top bridges
    print(f"\nTop 20 bridges:")
    for b in bridges[:20]:
        ds_str = ", ".join(f"{ds}({n})" for ds, n in sorted(b["datasets"].items()))
        print(f"  {b['concept']:40s} | {b['n_datasets']} datasets | {ds_str}")

    return bridges[:max_results]


if __name__ == "__main__":
    stats = build_index()
    bridges = find_bridges()
    print(f"\nBridges saved to {BRIDGES_FILE}")
