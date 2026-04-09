"""
Modular Arithmetic Signature Extractor (Strategy S3)
=====================================================
For each formula tree that reduces to a polynomial or rational function,
compute f(x) mod p for x = 0..p-1 across small primes.  The concatenated
residue vector is the modular fingerprint.  Formulas sharing fingerprints
across domains are cross-domain bridges.

Usage:
    python mod_p_signatures.py
    python mod_p_signatures.py --max-formulas 50000 --primes "2,3,5,7"
    python mod_p_signatures.py --sample 10000
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "mod_p_signatures.jsonl"
OUT_CLUSTERS = OUT_DIR / "mod_p_clusters.jsonl"

# Operators that keep us in the polynomial/rational world
POLY_OPS = {"add", "sub", "multiply", "power", "neg"}
RATIONAL_OPS = POLY_OPS | {"frac", "dfrac"}
TRANSCENDENTAL_OPS = {"sin", "cos", "log", "exp", "sqrt", "int", "sum"}
# Structural ops we can walk through transparently
TRANSPARENT_OPS = {"eq", "paren"}

DEFAULT_PRIMES = [2, 3, 5, 7, 11, 13]


# ── Tree → Polynomial Extraction ──────────────────────────────────────

# Characters that are punctuation/text artifacts, not mathematical variables
_JUNK_VARS = frozenset(",|.;:!?'\"()[]{}/ \\")


def _classify_tree(root):
    """Classify a tree as polynomial, rational, transcendental, or opaque."""
    ops = set()
    has_subscript = False
    n_vars = set()

    def walk(node):
        nonlocal has_subscript
        if not isinstance(node, dict):
            return
        t = node.get("type", "")
        if t in ("operator", "equation", "relation"):
            op = node.get("op", "")
            if op == "subscript":
                has_subscript = True
            elif op not in TRANSPARENT_OPS and op:
                ops.add(op)
        elif t == "variable":
            name = node.get("name", "")
            if name and name not in _JUNK_VARS:
                n_vars.add(name)
        for c in node.get("children", []):
            walk(c)

    walk(root)

    # Heuristic: text artifact detection (tightened after Kill #11)
    # - >5 single-char vars = likely parsed text
    # - >12 total vars = definitely not a single formula
    single_chars = {v for v in n_vars if len(v) == 1}
    if len(single_chars) > 5 or len(n_vars) > 12:
        return "text_artifact", ops, n_vars

    if ops & TRANSCENDENTAL_OPS:
        return "transcendental", ops, n_vars
    if has_subscript:
        return "indexed", ops, n_vars  # subscripted vars = sequences, not polynomials
    if ops <= RATIONAL_OPS:
        if ops & {"frac", "dfrac"}:
            return "rational", ops, n_vars
        return "polynomial", ops, n_vars
    return "opaque", ops, n_vars


def _eval_tree_mod_p(node, var_val, p):
    """Evaluate a tree node mod p given variable assignments.

    Returns (value_mod_p, ok).  ok=False means we hit something unevaluable.
    """
    if not isinstance(node, dict):
        return (0, False)

    t = node.get("type", "")

    if t == "number":
        try:
            v = int(node["value"])
            return (v % p, True)
        except (ValueError, KeyError):
            # Float or missing — try to interpret
            try:
                v = float(node["value"])
                if v == int(v):
                    return (int(v) % p, True)
            except (ValueError, KeyError):
                pass
            return (0, False)

    if t == "variable":
        name = node.get("name", "")
        if not name or name in _JUNK_VARS:
            return (0, False)  # punctuation artifact
        if name in var_val:
            return (var_val[name] % p, True)
        return (0, False)  # unknown variable

    children = node.get("children", [])
    op = node.get("op", "")

    # Transparent containers
    if t == "group" or op in TRANSPARENT_OPS:
        # For groups/parens, evaluate the meaningful child
        # Filter out punctuation children
        real_children = []
        for c in children:
            if isinstance(c, dict):
                if c.get("type") == "variable" and (
                        not c.get("name") or c.get("name") in _JUNK_VARS):
                    continue
                real_children.append(c)
        if not real_children:
            return (0, False)
        if len(real_children) == 1:
            return _eval_tree_mod_p(real_children[0], var_val, p)
        if op == "eq":
            # For equations, evaluate the RHS (or first meaningful side)
            return _eval_tree_mod_p(real_children[-1], var_val, p)
        # Multiple children in a group — treat as implicit multiply
        result = 1
        for c in real_children:
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            result = (result * v) % p
        return (result, True)

    if op == "add":
        total = 0
        for c in children:
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            total = (total + v) % p
        return (total, True)

    if op == "sub":
        if len(children) < 2:
            return (0, False)
        left, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        right, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        return ((left - right) % p, True)

    if op == "neg":
        if not children:
            return (0, False)
        v, ok = _eval_tree_mod_p(children[0], var_val, p)
        if not ok:
            return (0, False)
        return ((-v) % p, True)

    if op == "multiply":
        result = 1
        for c in children:
            if isinstance(c, dict) and c.get("type") == "variable" and (
                    not c.get("name") or c.get("name") in _JUNK_VARS):
                continue
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            result = (result * v) % p
        return (result, True)

    if op == "power":
        if len(children) < 2:
            return (0, False)
        base, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        exp_val, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        # Negative exponents: need modular inverse
        # The exponent in the tree might be wrapped in neg
        # pow(base, exp, p) handles non-negative exponents
        if exp_val < 0:
            # Modular inverse: base^(-1) mod p
            if base % p == 0:
                return (0, False)  # no inverse
            inv = pow(base, p - 2, p)  # Fermat's little theorem
            return (pow(inv, (-exp_val) % (p - 1), p), True)
        return (pow(base, exp_val, p), True)

    if op in ("frac", "dfrac"):
        if len(children) < 2:
            return (0, False)
        num, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        den, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        if den % p == 0:
            return (0, False)  # division by zero mod p
        inv = pow(den, p - 2, p)
        return ((num * inv) % p, True)

    return (0, False)


# ── Fingerprint Computation ──────────────────────────────────────────

def compute_fingerprint(root, primes, var_name=None):
    """Compute the mod-p fingerprint for a formula tree.

    If var_name is given, evaluate f(x) for x=0..p-1 for that variable.
    If None, auto-detect a single variable.

    Returns (signature_vector, degree_estimate) or (None, None) if not evaluable.
    """
    kind, ops, variables = _classify_tree(root)
    if kind in ("transcendental", "opaque", "indexed"):
        return None, None, kind

    # Pick the evaluation variable
    if var_name and var_name in variables:
        eval_var = var_name
    elif len(variables) == 1:
        eval_var = next(iter(variables))
    elif len(variables) == 0:
        # Constant expression: evaluate once per prime
        eval_var = None
    else:
        # Multiple variables: use first alphabetically, set others to 1
        sorted_vars = sorted(variables)
        eval_var = sorted_vars[0]

    # Evaluate at multiple base points for non-eval variables (Kill #11 fix)
    # Using {2,3} instead of just {1} avoids identity-fingerprint degeneracy
    base_points = [2, 3]
    other_vars_base = {v: base_points[i % len(base_points)]
                       for i, v in enumerate(sorted(v2 for v2 in variables if v2 != eval_var))}

    signature = []
    all_ok = True

    for p in primes:
        residues = []
        for x in range(p):
            var_val = dict(other_vars_base)
            if eval_var is not None:
                var_val[eval_var] = x
            val, ok = _eval_tree_mod_p(root, var_val, p)
            if not ok:
                all_ok = False
                break
            residues.append(val)
        if not all_ok:
            break
        signature.extend(residues)

    if not all_ok or not signature:
        return None, None, kind

    # Rough degree estimate: for the largest prime, count how many
    # consecutive differences are non-zero
    deg = _estimate_degree(signature, primes)

    return signature, deg, kind


def _estimate_degree(sig, primes):
    """Rough polynomial degree estimate from the last prime's residues."""
    last_p = primes[-1]
    tail = sig[-last_p:]
    # Iterated finite differences
    diffs = list(tail)
    deg = 0
    for d in range(last_p):
        if all(v == 0 for v in diffs):
            break
        deg = d
        diffs = [(diffs[i + 1] - diffs[i]) % last_p for i in range(len(diffs) - 1)]
        if not diffs:
            break
    return deg


# ── Domain Lookup ────────────────────────────────────────────────────

def load_domains(needed_hashes=None, limit=None):
    """Load hash -> domain from openwebmath_formulas.jsonl.

    If needed_hashes is provided, only retain those hashes (saves memory
    and allows early exit once all are found).
    """
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
                # Fast path: extract hash before full parse
                h_start = line.find('"hash"')
                if h_start == -1:
                    continue
                # Quick hash extraction
                d = json.loads(line)
                h = d["hash"]
                if target and h not in target:
                    continue
                domains = d.get("domains", ["unclassified"])
                mapping[h] = domains[0] if domains else "unclassified"
                if target and len(mapping) >= len(target):
                    break  # found all we need
            except Exception:
                pass
    return mapping


# ── Clustering ───────────────────────────────────────────────────────

def find_clusters(records):
    """Group records by signature, find cross-domain clusters."""
    by_sig = defaultdict(list)
    for r in records:
        key = tuple(r["signature"])
        by_sig[key].append(r)

    clusters = []
    for sig, members in by_sig.items():
        if len(members) < 2:
            continue
        domains = set(m["domain"] for m in members)
        clusters.append({
            "signature": list(sig),
            "size": len(members),
            "n_domains": len(domains),
            "domains": sorted(domains),
            "cross_domain": len(domains) > 1,
            "hashes": [m["hash"] for m in members],
            "degree_range": [
                min(m["degree"] for m in members),
                max(m["degree"] for m in members),
            ],
        })

    clusters.sort(key=lambda c: (-int(c["cross_domain"]), -c["n_domains"], -c["size"]))
    return clusters


# ── Main ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Modular arithmetic signature extractor")
    ap.add_argument("--max-formulas", type=int, default=0, help="0 = all")
    ap.add_argument("--primes", type=str, default="2,3,5,7,11,13")
    ap.add_argument("--sample", type=int, default=0, help="Random sample size (0 = sequential)")
    ap.add_argument("--trees-file", type=str, default=str(TREES_FILE))
    ap.add_argument("--skip-domains", action="store_true",
                    help="Skip domain lookup (fast mode)")
    args = ap.parse_args()

    primes = [int(x) for x in args.primes.split(",")]
    sig_len = sum(primes)
    print("=" * 70)
    print(f"  Mod-p Signature Extractor — primes {primes}")
    print(f"  Signature length: {sig_len} integers")
    print("=" * 70)

    t0 = time.time()

    # Load trees
    trees_path = Path(args.trees_file)
    if not trees_path.exists():
        print(f"  ERROR: {trees_path} not found")
        sys.exit(1)

    # Stream processing — never load entire file into memory
    import random
    random.seed(42)

    limit = args.max_formulas if args.max_formulas else float("inf")
    sample_k = args.sample if args.sample else 0

    print(f"  Streaming {trees_path.name}...")
    if sample_k:
        print(f"  Reservoir sampling {sample_k:,} formulas")

    records = []
    stats = Counter()
    t_proc = time.time()
    n_read = 0

    # If sampling, use reservoir sampling on parsed results
    # If not sampling, process sequentially up to limit
    reservoir = []  # only used when sampling

    with open(trees_path) as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            n_read = i + 1

            if i % 100000 == 0 and i > 0:
                elapsed = time.time() - t_proc
                rate = i / elapsed
                print(f"    {i:,} read ({rate:.0f}/s) — "
                      f"{len(records):,} evaluable, skips: {dict(stats)}")

            try:
                d = json.loads(line)
            except Exception:
                stats["parse_error"] += 1
                continue

            h = d["hash"]
            root = d["root"]
            sig, deg, kind = compute_fingerprint(root, primes)

            if sig is None:
                stats[f"skip_{kind}"] += 1
                continue

            rec = {
                "hash": h,
                "signature": sig,
                "degree": deg,
                "domain": "unknown",
                "kind": kind,
                "evaluable": True,
            }

            if sample_k:
                # Reservoir sampling on evaluable records
                n_evaluable = stats.get("_evaluable_seen", 0)
                stats["_evaluable_seen"] = n_evaluable + 1
                if len(reservoir) < sample_k:
                    reservoir.append(rec)
                else:
                    j = random.randint(0, n_evaluable)
                    if j < sample_k:
                        reservoir[j] = rec
            else:
                records.append(rec)

    if sample_k:
        records = reservoir
    n_total = n_read

    # Deferred domain lookup — only load domains for evaluable hashes
    if not args.skip_domains and records:
        needed = {r["hash"] for r in records}
        print(f"\n  Loading domains for {len(needed):,} evaluable hashes...")
        domains = load_domains(needed_hashes=needed)
        print(f"  {len(domains):,} domain mappings found")
        for r in records:
            r["domain"] = domains.get(r["hash"], "unknown")

    elapsed = time.time() - t0
    print()
    print(f"  Processed {n_total:,} formulas in {elapsed:.1f}s")
    print(f"  Evaluable: {len(records):,} ({100*len(records)/max(n_total,1):.1f}%)")
    print(f"  Skip breakdown: {dict(stats)}")

    # Write signatures
    OUT_SIGS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_SIGS, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"  Wrote {OUT_SIGS}")

    # Cluster
    print()
    print("  Clustering by signature...")
    clusters = find_clusters(records)
    n_cross = sum(1 for c in clusters if c["cross_domain"])

    with open(OUT_CLUSTERS, "w") as f:
        for c in clusters:
            f.write(json.dumps(c) + "\n")
    print(f"  Wrote {OUT_CLUSTERS}")

    # Summary
    print()
    print("=" * 70)
    print(f"  SUMMARY")
    print(f"  Total formulas:         {n_total:,}")
    print(f"  Evaluable:              {len(records):,}")
    print(f"  Unique signatures:      {len(set(tuple(r['signature']) for r in records)):,}")
    print(f"  Clusters (size >= 2):   {len(clusters):,}")
    print(f"  Cross-domain clusters:  {n_cross:,}")
    if clusters:
        biggest = clusters[0]
        print(f"  Largest cluster:        {biggest['size']} formulas, "
              f"{biggest['n_domains']} domains")
    print(f"  Time:                   {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
