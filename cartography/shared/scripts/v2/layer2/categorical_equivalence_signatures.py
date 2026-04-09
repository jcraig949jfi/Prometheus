"""
Categorical Equivalence Signatures (Strategy S34) — category classification.
==============================================================================
Classify formulas by mathematical category using keyword and operator analysis
from formula trees. Cross-categorical formulas encode connections between fields.

Usage:
    python categorical_equivalence_signatures.py
    python categorical_equivalence_signatures.py --max-formulas 50000
    python categorical_equivalence_signatures.py --sample 10000
"""

import argparse
import hashlib
import json
import re
import sys
import time
import random
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "categorical_equivalence_signatures.jsonl"


# ---------------------------------------------------------------------------
# Category detection rules
# ---------------------------------------------------------------------------

# Operators/keywords that signal each category
CATEGORY_RULES = {
    "combinatorics": {
        "ops": {"binom", "binomial", "choose", "perm", "stirling",
                "bell", "catalan", "fibonacci"},
        "keywords": {"sum", "prod", "product", "factorial", "ncr",
                     "partition", "permutation", "combination"},
    },
    "analysis": {
        "ops": {"int", "integral", "lim", "limit", "partial", "nabla",
                "grad", "gradient", "laplacian", "divergence", "curl",
                "diff", "derivative", "infty"},
        "keywords": {"continuous", "convergence", "epsilon", "delta",
                     "supremum", "infimum", "measure", "lebesgue",
                     "riemann", "cauchy", "banach", "hilbert"},
    },
    "linear_algebra": {
        "ops": {"det", "determinant", "trace", "tr", "rank",
                "dim", "dimension", "ker", "kernel", "image",
                "eigenvalue", "eigenvector", "transpose"},
        "keywords": {"matrix", "vector", "tensor", "span", "basis",
                     "orthogonal", "unitary", "hermitian", "symmetric",
                     "diagonalize", "svd", "projection"},
    },
    "logic": {
        "ops": {"forall", "exists", "implies", "iff", "neg",
                "and", "or", "not", "vdash", "models", "turnstile"},
        "keywords": {"predicate", "quantifier", "proposition", "theorem",
                     "proof", "axiom", "consistent", "complete",
                     "decidable", "satisfiable", "boolean"},
    },
    "algebra": {
        "ops": {"oplus", "otimes", "rtimes", "ltimes", "cong",
                "simeq", "iso", "hom", "aut", "end"},
        "keywords": {"group", "ring", "field", "module", "ideal",
                     "subgroup", "normal", "abelian", "cyclic", "solvable",
                     "galois", "extension", "homomorphism", "isomorphism",
                     "kernel", "cokernel", "quotient", "algebra",
                     "representation", "character"},
    },
    "trigonometric": {
        "ops": {"sin", "cos", "tan", "cot", "sec", "csc",
                "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh"},
        "keywords": {"angle", "radian", "periodic", "fourier",
                     "harmonic", "oscillation", "wave"},
    },
    "number_theory": {
        "ops": {"mod", "gcd", "lcm", "phi", "euler", "totient",
                "legendre", "jacobi", "kronecker"},
        "keywords": {"prime", "divisor", "congruence", "residue",
                     "quadratic", "reciprocity", "diophantine",
                     "arithmetic", "modular", "coprime", "sieve",
                     "zeta", "riemann", "dirichlet", "lfunc"},
    },
    "topology": {
        "ops": {"cup", "cap", "wedge", "smash", "homotopy"},
        "keywords": {"genus", "manifold", "topology", "topological",
                     "homotopy", "homology", "cohomology", "fundamental",
                     "covering", "fiber", "bundle", "sheaf",
                     "compact", "connected", "hausdorff", "open", "closed"},
    },
    "probability": {
        "ops": {"expectation", "variance", "cov", "corr"},
        "keywords": {"probability", "random", "distribution", "expected",
                     "variance", "stochastic", "markov", "bayes",
                     "gaussian", "poisson", "bernoulli", "binomial_dist"},
    },
    "calculus": {
        "ops": {"frac", "dfrac"},  # fractions with d/dx pattern
        "keywords": {"derivative", "antiderivative", "fundamental",
                     "taylor", "maclaurin", "series", "power_series"},
    },
}

# Flatten all keywords and ops for fast lookup
ALL_OPS_BY_CAT = {cat: rules["ops"] for cat, rules in CATEGORY_RULES.items()}
ALL_KW_BY_CAT = {cat: rules["keywords"] for cat, rules in CATEGORY_RULES.items()}


# ---------------------------------------------------------------------------
# Tree analysis
# ---------------------------------------------------------------------------

def extract_ops_and_names(node, ops=None, names=None, values=None):
    """Walk a formula tree, collecting operators, variable names, and values."""
    if ops is None:
        ops = []
    if names is None:
        names = []
    if values is None:
        values = []

    if not isinstance(node, dict):
        return ops, names, values

    ntype = node.get("type", "")
    op = (node.get("op", "") or "").lower().strip()
    name = (node.get("name", "") or "").lower().strip()
    value = (node.get("value", "") or "")

    if op:
        ops.append(op)
    if name:
        names.append(name)
    if ntype == "number" and value:
        values.append(str(value))

    for c in node.get("children", []):
        extract_ops_and_names(c, ops, names, values)

    return ops, names, values


def classify_formula(root, domain_text=""):
    """Classify a formula into mathematical categories.

    Returns list of (category, confidence) tuples, sorted by confidence desc.
    """
    ops, names, values = extract_ops_and_names(root)

    # Normalize: lowercase set of all tokens
    all_tokens = set()
    for o in ops:
        all_tokens.add(o)
    for n in names:
        all_tokens.add(n)
        # Also add substrings for compound names
        for part in re.split(r"[_\s]+", n):
            if len(part) > 2:
                all_tokens.add(part)

    # Add domain text tokens
    if domain_text:
        for tok in re.split(r"[\s,;:]+", domain_text.lower()):
            if len(tok) > 2:
                all_tokens.add(tok)

    # Score each category
    scores = {}
    for cat, rules in CATEGORY_RULES.items():
        cat_ops = rules["ops"]
        cat_kw = rules["keywords"]

        # Operator matches (weighted higher — structural)
        op_hits = all_tokens & cat_ops
        # Keyword matches
        kw_hits = all_tokens & cat_kw

        score = len(op_hits) * 2.0 + len(kw_hits) * 1.0
        if score > 0:
            scores[cat] = score

    if not scores:
        return []

    # Normalize scores
    max_score = max(scores.values())
    result = []
    for cat, score in sorted(scores.items(), key=lambda x: -x[1]):
        confidence = score / max_score
        result.append((cat, round(confidence, 4)))

    return result


def category_pair_hash(cats):
    """Compute a deterministic hash for a sorted set of category pairs."""
    if len(cats) < 2:
        return None
    pairs = []
    cat_names = [c[0] for c in cats]
    for i in range(len(cat_names)):
        for j in range(i + 1, len(cat_names)):
            pair = tuple(sorted([cat_names[i], cat_names[j]]))
            pairs.append(pair)
    pairs.sort()
    pair_str = "|".join(f"{a}+{b}" for a, b in pairs)
    return hashlib.md5(pair_str.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Domain text loader
# ---------------------------------------------------------------------------

def load_domain_text(needed_hashes=None, limit=None):
    """Load hash -> domain text from openwebmath_formulas.jsonl."""
    mapping = {}
    if not FORMULAS_FILE.exists():
        return mapping
    target = set(needed_hashes) if needed_hashes else None
    t0 = time.time()
    with open(FORMULAS_FILE) as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            if i % 2_000_000 == 0 and i > 0:
                print(f"    domain scan: {i:,} lines, {len(mapping):,} matched "
                      f"({time.time()-t0:.0f}s)")
            try:
                d = json.loads(line)
                h = d.get("hash", "")
                if target and h not in target:
                    continue
                domains = d.get("domains", [])
                domain_str = " ".join(domains) if domains else ""
                mapping[h] = domain_str
                if target and len(mapping) >= len(target):
                    break
            except Exception:
                pass
    return mapping


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Categorical equivalence signature extractor (S34)")
    ap.add_argument("--max-formulas", type=int, default=0,
                    help="Max formulas to process (0 = all)")
    ap.add_argument("--sample", type=int, default=0,
                    help="Reservoir sample size (0 = sequential)")
    ap.add_argument("--skip-domains", action="store_true",
                    help="Skip domain text lookup (fast mode)")
    args = ap.parse_args()

    print("=" * 70)
    print("  Categorical Equivalence Signature Extractor (S34)")
    print("=" * 70)
    t0 = time.time()

    trees_path = TREES_FILE
    if not trees_path.exists():
        print(f"  ERROR: {trees_path} not found")
        sys.exit(1)

    limit = args.max_formulas if args.max_formulas else float("inf")
    sample_k = args.sample if args.sample else 0

    rng = random.Random(42)

    print(f"  Streaming {trees_path.name}...")
    if sample_k:
        print(f"  Reservoir sampling {sample_k:,} formulas")

    # Phase 1: read trees and compute categories
    records = []
    reservoir = []
    stats = Counter()
    n_read = 0
    n_evaluable = 0

    with open(trees_path) as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            n_read = i + 1

            if i % 100000 == 0 and i > 0:
                elapsed = time.time() - t0
                rate = i / elapsed
                n_out = len(reservoir) if sample_k else len(records)
                print(f"    {i:,} read ({rate:.0f}/s) — "
                      f"{n_out:,} classified, skips: {dict(stats)}")

            try:
                d = json.loads(line)
            except Exception:
                stats["parse_error"] += 1
                continue

            h = d.get("hash", f"tree_{i}")
            root = d.get("root", {})

            # Classify without domain text first
            cats = classify_formula(root)
            if not cats:
                stats["skip_no_category"] += 1
                continue

            primary = cats[0][0]
            secondary = [c[0] for c in cats[1:]]
            n_cats = len(cats)
            pair_h = category_pair_hash(cats) if n_cats >= 2 else None

            rec = {
                "hash": h,
                "primary_category": primary,
                "secondary_categories": secondary,
                "n_categories": n_cats,
                "category_pair_hash": pair_h,
                "category_scores": {c: s for c, s in cats},
                "is_cross_categorical": n_cats >= 2,
                "domain_text": "",
            }

            if sample_k:
                n_evaluable += 1
                if len(reservoir) < sample_k:
                    reservoir.append(rec)
                else:
                    j = rng.randint(0, n_evaluable - 1)
                    if j < sample_k:
                        reservoir[j] = rec
            else:
                records.append(rec)

    if sample_k:
        records = reservoir

    # Phase 2: enrich with domain text (optional)
    if not args.skip_domains and records:
        needed = {r["hash"] for r in records}
        print(f"\n  Loading domain text for {len(needed):,} hashes...")
        domain_map = load_domain_text(needed_hashes=needed)
        print(f"  {len(domain_map):,} domain mappings found")

        # Re-classify with domain text
        n_reclassified = 0
        if domain_map:
            # Re-read trees for the hashes we need
            hash_to_idx = {r["hash"]: idx for idx, r in enumerate(records)}
            enriched_hashes = set(domain_map.keys()) & set(hash_to_idx.keys())
            if enriched_hashes:
                print(f"  Re-classifying {len(enriched_hashes):,} with domain info...")
                with open(trees_path) as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            h = d.get("hash", "")
                            if h not in enriched_hashes:
                                continue
                            root = d.get("root", {})
                            domain_text = domain_map.get(h, "")
                            cats = classify_formula(root, domain_text)
                            if cats:
                                idx = hash_to_idx[h]
                                records[idx]["primary_category"] = cats[0][0]
                                records[idx]["secondary_categories"] = [
                                    c[0] for c in cats[1:]]
                                records[idx]["n_categories"] = len(cats)
                                records[idx]["category_pair_hash"] = (
                                    category_pair_hash(cats) if len(cats) >= 2 else None)
                                records[idx]["category_scores"] = {
                                    c: s for c, s in cats}
                                records[idx]["is_cross_categorical"] = len(cats) >= 2
                                records[idx]["domain_text"] = domain_text
                                n_reclassified += 1
                                enriched_hashes.discard(h)
                                if not enriched_hashes:
                                    break
                        except Exception:
                            pass
                print(f"  Re-classified {n_reclassified:,} formulas with domain enrichment")

    elapsed = time.time() - t0

    # Write output
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"\n  Wrote {len(records):,} signatures to {OUT_FILE}")

    # Summary
    print()
    print("=" * 70)
    print("  SUMMARY")
    print(f"  Total formulas read:    {n_read:,}")
    print(f"  Classified:             {len(records):,}")

    # Category distribution
    cat_counts = Counter()
    for r in records:
        cat_counts[r["primary_category"]] += 1
    print(f"\n  Primary category distribution:")
    for cat, cnt in cat_counts.most_common():
        pct = 100 * cnt / max(len(records), 1)
        print(f"    {cat:25s} {cnt:>7,}  ({pct:.1f}%)")

    # Cross-categorical stats
    n_cross = sum(1 for r in records if r["is_cross_categorical"])
    print(f"\n  Cross-categorical:      {n_cross:,} ({100*n_cross/max(len(records),1):.1f}%)")

    # Most common category pairs
    pair_counts = Counter()
    for r in records:
        if r["n_categories"] >= 2:
            cats = [r["primary_category"]] + r["secondary_categories"]
            for a in range(len(cats)):
                for b in range(a + 1, len(cats)):
                    pair = tuple(sorted([cats[a], cats[b]]))
                    pair_counts[pair] += 1
    if pair_counts:
        print(f"\n  Top 10 category pairs:")
        for pair, cnt in pair_counts.most_common(10):
            print(f"    {pair[0]:>20s} + {pair[1]:<20s}  {cnt:>6,}")

    print(f"\n  Skip breakdown:         {dict(stats)}")
    print(f"  Time:                   {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
