"""
Phase Transition — Critical Connectivity for Sleeping Beauty Collapse (Q11).
=============================================================================
Find the exact connectivity threshold where a sleeping beauty "collapses"
into hub territory.  For each OEIS sequence, compute (xref_degree,
n_verb_concepts, depth_score) and bin by verb concept count to locate
the phase transition in average abstraction depth.

Since OEIS sequences are not directly in the concept_links layer, we
extract verb-like concepts from OEIS sequence names (mathematical keywords
such as "prime", "fibonacci", "zeta", "modular", "partition", etc.)
paralleling the canonicalization used in concept_index.py.

Usage:
    python phase_transition.py
"""

import json
import math
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# --- Imports from search_engine ---
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis, _oeis_cache,
    _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse,
    _load_oeis_names, _oeis_names_cache,
)

REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "phase_transition.json"
DEPTHS_FILE = OUTPUT_DIR / "abstraction_depths.json"
LINKS_FILE = OUTPUT_DIR / "concept_links.jsonl"

# ---------------------------------------------------------------------------
# Verb concept extraction from OEIS names
# ---------------------------------------------------------------------------

# Mathematical keywords that map to verb concepts (mirroring concept_index verbs)
MATH_KEYWORDS = [
    "prime", "fibonacci", "catalan", "bernoulli", "euler", "partition",
    "divisor", "sigma", "totient", "moebius", "mobius", "factorial",
    "binomial", "triangle", "square", "cube", "power", "polygon",
    "polyhedron", "graph", "tree", "lattice", "group", "ring", "field",
    "module", "algebra", "topology", "manifold", "knot", "braid",
    "permutation", "combination", "sequence", "series", "sum", "product",
    "integral", "derivative", "differential", "harmonic", "zeta",
    "dirichlet", "modular", "elliptic", "quadratic", "cubic", "quartic",
    "recurrence", "linear", "matrix", "determinant", "eigenvalue",
    "polynomial", "coefficient", "root", "zero", "function", "number",
    "arithmetic", "geometric", "analytic", "algebraic", "combinatorial",
    "probabilistic", "random", "walk", "automaton", "cellular",
    "fractal", "chaos", "entropy", "information", "code", "error",
    "correction", "weight", "distance", "metric", "norm", "order",
    "degree", "rank", "dimension", "genus", "conductor", "discriminant",
    "regulator", "class", "ideal", "unit", "valuation", "residue",
    "congruence", "reciprocity", "symmetry", "invariant", "transform",
    "fourier", "laplace", "galois", "frobenius", "hecke", "ramanujan",
    "riemann", "goldbach", "fermat", "mersenne", "perfect", "amicable",
    "abundant", "deficient", "coloring", "chromatic", "planar",
    "bipartite", "connected", "regular", "transitive", "abelian",
    "cyclic", "nilpotent", "solvable", "simple", "boolean", "poset",
    "chain", "antichain", "composition", "derangement", "involution",
    "stirling", "bell", "lucas", "pell", "tribonacci", "continued",
    "fraction", "convergent", "digit", "base", "binary", "ternary",
    "decimal", "palindrome", "repunit", "pandigital",
    "triangular", "pentagonal", "hexagonal", "figurate",
    "pythagorean", "gaussian", "eisenstein", "quaternion", "octonion",
    "cardinality", "ordinal", "cardinal", "ultrafilter", "filter",
    "sieve", "semigroup", "monoid", "category", "functor", "morphism",
    "homology", "cohomology", "homotopy", "spectrum",
    "theta", "phi", "tau", "omega", "lambda", "mu", "pi",
]

# Precompile patterns (word-boundary match, case-insensitive)
_KEYWORD_PATTERNS = {
    kw: re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
    for kw in MATH_KEYWORDS
}


def extract_verb_concepts_from_name(name: str) -> set:
    """Extract verb-like concepts from an OEIS sequence name."""
    verbs = set()
    name_lower = name.lower()
    for kw, pat in _KEYWORD_PATTERNS.items():
        if pat.search(name_lower):
            verbs.add(f"verb_involves_{kw}")
    return verbs


# ---------------------------------------------------------------------------
# Also count verb concepts from concept_links that mention the same keywords
# (for sequences whose names overlap with dataset verb concepts)
# ---------------------------------------------------------------------------

def load_verb_concept_universe() -> set:
    """Load the set of all verb concepts from concept_links.jsonl."""
    verbs = set()
    if not LINKS_FILE.exists():
        return verbs
    print("  [Phase] Loading verb concepts from concept_links.jsonl...")
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                c = rec.get("concept", "")
                if c.startswith("verb_"):
                    verbs.add(c)
            except json.JSONDecodeError:
                pass
    print(f"  [Phase] Found {len(verbs):,} unique verb concepts in concept layer")
    return verbs


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_phase_transition():
    t0 = time.time()

    # 1. Load abstraction depths
    print("[Phase] Loading abstraction depths...")
    with open(DEPTHS_FILE, "r", encoding="utf-8") as f:
        depths_data = json.load(f)
    oeis_depths = depths_data.get("oeis", {})
    print(f"  Loaded {len(oeis_depths):,} OEIS depth entries")

    # 2. Load OEIS cross-references
    print("[Phase] Loading OEIS cross-references...")
    _load_oeis_crossrefs()
    _load_oeis_names()

    # 3. Load verb concept universe (for cross-referencing)
    verb_universe = load_verb_concept_universe()

    # 4. For each OEIS sequence, compute (xref_degree, n_verb_concepts, depth)
    print("[Phase] Computing per-sequence metrics...")
    seq_metrics = {}  # seq_id -> {xref_degree, n_verb_concepts, depth, verbs, name}

    # All OEIS sequence IDs that have depths
    all_seq_ids = set(oeis_depths.keys())
    # Also include sequences from xref caches
    all_seq_ids |= set(_oeis_xref_cache.keys())
    all_seq_ids |= set(_oeis_xref_reverse.keys())

    for seq_id in sorted(all_seq_ids):
        name = _oeis_names_cache.get(seq_id, "")

        # Xref degree (total: in + out)
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total_xref = out_deg + in_deg

        # Verb concepts from name
        verbs = extract_verb_concepts_from_name(name)
        # Also check which extracted verbs overlap with the concept layer
        layer_overlap = verbs & verb_universe
        n_verb = len(verbs)

        # Depth score
        depth = oeis_depths.get(seq_id, None)

        seq_metrics[seq_id] = {
            "xref_degree": total_xref,
            "n_verb_concepts": n_verb,
            "n_layer_overlap": len(layer_overlap),
            "depth": depth,
            "name": name,
            "verbs": sorted(verbs),
        }

    total_with_depth = sum(1 for m in seq_metrics.values() if m["depth"] is not None)
    print(f"  Computed metrics for {len(seq_metrics):,} sequences "
          f"({total_with_depth:,} with depth scores)")

    # 5. Bin by verb concept count
    bins = {
        "0": (0, 0),
        "1-2": (1, 2),
        "3-5": (3, 5),
        "6-10": (6, 10),
        "11-20": (11, 20),
        "21+": (21, 999999),
    }

    bin_depths = {label: [] for label in bins}
    bin_xrefs = {label: [] for label in bins}

    for seq_id, m in seq_metrics.items():
        if m["depth"] is None:
            continue
        n = m["n_verb_concepts"]
        for label, (lo, hi) in bins.items():
            if lo <= n <= hi:
                bin_depths[label].append(m["depth"])
                bin_xrefs[label].append(m["xref_degree"])
                break

    # 6. Compute average depth per bin
    print("\n[Phase] Verb-count bins (avg depth):")
    print(f"  {'Bin':<10} {'Count':>8} {'Avg Depth':>10} {'Avg Xref':>10}")
    print("  " + "-" * 42)

    bin_table = []
    for label in ["0", "1-2", "3-5", "6-10", "11-20", "21+"]:
        depths_list = bin_depths[label]
        xrefs_list = bin_xrefs[label]
        count = len(depths_list)
        avg_d = sum(depths_list) / count if count else float("nan")
        avg_x = sum(xrefs_list) / count if count else float("nan")
        bin_table.append({
            "bin": label,
            "count": count,
            "avg_depth": round(avg_d, 4) if count else None,
            "avg_xref_degree": round(avg_x, 4) if count else None,
        })
        print(f"  {label:<10} {count:>8,} {avg_d:>10.4f} {avg_x:>10.2f}")

    # 7. Find the phase transition threshold
    # Walk bins in order; find where avg_depth drops below 1.5
    transition_threshold = None
    prev_bin = None
    for entry in bin_table:
        if entry["avg_depth"] is not None and entry["avg_depth"] < 1.5:
            transition_threshold = entry["bin"]
            break
        prev_bin = entry

    if transition_threshold:
        print(f"\n  >>> PHASE TRANSITION at verb count bin: {transition_threshold}")
        if prev_bin:
            print(f"      Previous bin '{prev_bin['bin']}' avg depth: "
                  f"{prev_bin['avg_depth']:.4f}")
    else:
        print("\n  >>> No phase transition found (depth never drops below 1.5)")
        # Use the bin with the steepest depth drop as the transition
        max_drop = 0
        for i in range(1, len(bin_table)):
            if bin_table[i - 1]["avg_depth"] and bin_table[i]["avg_depth"]:
                drop = bin_table[i - 1]["avg_depth"] - bin_table[i]["avg_depth"]
                if drop > max_drop:
                    max_drop = drop
                    transition_threshold = bin_table[i]["bin"]
        if transition_threshold:
            print(f"  >>> Steepest depth drop at bin: {transition_threshold} "
                  f"(delta = {max_drop:.4f})")

    # 8. Identify sequences RIGHT AT the threshold
    # Parse threshold bin to get its numeric range
    threshold_lo, threshold_hi = 0, 0
    if transition_threshold:
        for label, (lo, hi) in bins.items():
            if label == transition_threshold:
                threshold_lo, threshold_hi = lo, hi
                break

    # Sequences in the bin just below AND at the transition bin
    # These are "one bridge away" from becoming foundational
    threshold_candidates = []
    for seq_id, m in seq_metrics.items():
        if m["depth"] is None:
            continue
        n = m["n_verb_concepts"]
        # In the transition bin or one bin below
        if threshold_lo > 0:
            prev_lo = max(0, threshold_lo - 3)  # approximate previous bin
        else:
            prev_lo = 0
        if prev_lo <= n <= threshold_hi:
            threshold_candidates.append({
                "seq_id": seq_id,
                "name": m["name"],
                "n_verb_concepts": n,
                "xref_degree": m["xref_degree"],
                "depth": m["depth"],
                "verbs": m["verbs"],
            })

    # Sort by: highest depth first (deepest sleepers near threshold)
    threshold_candidates.sort(key=lambda x: (-x["depth"], -x["n_verb_concepts"]))
    top_20 = threshold_candidates[:20]

    print(f"\n[Phase] Top 20 threshold candidates (deepest sleepers near transition):")
    for i, c in enumerate(top_20, 1):
        safe_name = c['name'][:60].encode('ascii', 'replace').decode('ascii')
        print(f"  {i:2d}. {c['seq_id']} depth={c['depth']} verbs={c['n_verb_concepts']} "
              f"xref={c['xref_degree']} -- {safe_name}")

    # 9. Build output
    elapsed = time.time() - t0
    output = {
        "meta": {
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Phase transition analysis: verb concept count vs abstraction depth",
            "total_sequences_analyzed": len(seq_metrics),
            "sequences_with_depth": total_with_depth,
            "elapsed_seconds": round(elapsed, 2),
        },
        "phase_transition_threshold": transition_threshold,
        "bin_table": bin_table,
        "top_20_threshold_candidates": [
            {
                "seq_id": c["seq_id"],
                "name": c["name"],
                "n_verb_concepts": c["n_verb_concepts"],
                "xref_degree": c["xref_degree"],
                "depth": c["depth"],
                "verbs": c["verbs"],
            }
            for c in top_20
        ],
        "summary_stats": {
            "total_verb_concepts_extracted": len(
                set().union(*(set(m["verbs"]) for m in seq_metrics.values()))
            ),
            "verb_concept_universe_size": len(verb_universe),
            "sequences_with_zero_verbs": sum(
                1 for m in seq_metrics.values() if m["n_verb_concepts"] == 0
            ),
            "sequences_with_21plus_verbs": sum(
                1 for m in seq_metrics.values() if m["n_verb_concepts"] >= 21
            ),
        },
    }

    # 10. Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n[Phase] Saved to {OUTPUT_FILE}")
    print(f"[Phase] Done in {elapsed:.1f}s")

    return output


if __name__ == "__main__":
    compute_phase_transition()
