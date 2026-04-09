"""
OpenWebMath Ingestion — Extract LaTeX formulas from HuggingFace dataset.
=========================================================================
Streams open-web-math/open-web-math, extracts LaTeX blocks, parses to
structural features, and saves for ast_bridge consumption.

Usage:
    python openwebmath_ingest.py                    # default 50K docs
    python openwebmath_ingest.py --max-docs 200000  # more docs
    python openwebmath_ingest.py --formulas-only    # skip doc metadata
"""

import argparse
import json
import re
import sys
import time
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]  # F:/Prometheus
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# LaTeX extraction patterns
DISPLAY_MATH = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
INLINE_MATH = re.compile(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)')
LATEX_ENV = re.compile(r'\\begin\{(equation|align|gather|multline)\*?\}(.*?)\\end\{\1\*?\}', re.DOTALL)

# Known mathematical operators/functions for feature extraction
MATH_FUNCTIONS = {
    'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'sum', 'prod', 'int',
    'lim', 'inf', 'sup', 'max', 'min', 'det', 'dim', 'ker', 'gcd',
    'zeta', 'Gamma', 'gamma', 'theta', 'phi', 'psi', 'eta', 'xi',
    'alpha', 'beta', 'delta', 'epsilon', 'lambda', 'mu', 'nu', 'sigma', 'tau', 'omega',
    'pi', 'Pi', 'frac', 'binom', 'partial', 'nabla', 'infty',
    'mathbb', 'mathcal', 'mathfrak', 'mathrm', 'operatorname',
    'forall', 'exists', 'in', 'subset', 'cup', 'cap', 'setminus',
    'equiv', 'sim', 'approx', 'cong', 'neq', 'leq', 'geq',
    'rightarrow', 'leftarrow', 'Rightarrow', 'Leftarrow', 'mapsto',
    'otimes', 'oplus', 'times', 'cdot', 'circ',
}

# Structural tokens for AST-like features
STRUCTURAL_TOKENS = {
    'frac': 'division',
    'sum': 'summation',
    'prod': 'product',
    'int': 'integral',
    'lim': 'limit',
    'sqrt': 'radical',
    'binom': 'binomial',
    '^': 'superscript',
    '_': 'subscript',
    '{': 'group_open',
    '}': 'group_close',
    '(': 'paren_open',
    ')': 'paren_close',
    '[': 'bracket_open',
    ']': 'bracket_close',
}


def extract_latex(text):
    """Extract all LaTeX formulas from a document."""
    formulas = []

    # Display math ($$...$$)
    for m in DISPLAY_MATH.finditer(text):
        f = m.group(1).strip()
        if f and len(f) > 2:
            formulas.append(("display", f))

    # LaTeX environments
    for m in LATEX_ENV.finditer(text):
        f = m.group(2).strip()
        if f and len(f) > 2:
            formulas.append(("environment", f))

    # Inline math ($...$) — skip trivial single-letter vars
    for m in INLINE_MATH.finditer(text):
        f = m.group(1).strip()
        if f and len(f) > 3:  # skip $x$, $n$, etc.
            formulas.append(("inline", f))

    return formulas


def extract_features(latex_str):
    """Extract structural features from a LaTeX formula string."""
    # Operators present
    operators = set()
    for op in MATH_FUNCTIONS:
        # Match \op or bare op (for Greek letters etc.)
        if re.search(r'\\' + re.escape(op) + r'(?![a-zA-Z])', latex_str):
            operators.add(op)
        elif op in ('sin', 'cos', 'tan', 'log', 'ln', 'exp', 'det', 'dim',
                     'gcd', 'max', 'min', 'lim', 'inf', 'sup'):
            if re.search(r'\\' + op + r'\b', latex_str):
                operators.add(op)

    # Structural depth (nesting of braces)
    max_depth = 0
    depth = 0
    for ch in latex_str:
        if ch == '{':
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == '}':
            depth = max(0, depth - 1)

    # Structural tokens
    struct = []
    for token, label in STRUCTURAL_TOKENS.items():
        if token in latex_str:
            struct.append(label)

    # Length and complexity proxies
    n_backslash = latex_str.count('\\')
    n_subscript = latex_str.count('_')
    n_superscript = latex_str.count('^')
    n_frac = len(re.findall(r'\\frac', latex_str))
    n_sum = len(re.findall(r'\\sum', latex_str))
    n_int = len(re.findall(r'\\int', latex_str))

    return {
        "operators": sorted(operators),
        "n_operators": len(operators),
        "structural_tokens": sorted(set(struct)),
        "max_depth": max_depth,
        "n_commands": n_backslash,
        "n_subscripts": n_subscript,
        "n_superscripts": n_superscript,
        "n_fractions": n_frac,
        "n_sums": n_sum,
        "n_integrals": n_int,
        "length": len(latex_str),
    }


def formula_hash(latex_str):
    """Deterministic hash for dedup."""
    normalized = re.sub(r'\s+', ' ', latex_str.strip())
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def classify_domain(operators, text_context=""):
    """Rough domain classification from operators."""
    domains = set()
    if operators & {'int', 'lim', 'partial', 'nabla', 'infty'}:
        domains.add('analysis')
    if operators & {'sum', 'prod', 'binom', 'gcd'}:
        domains.add('combinatorics')
    if operators & {'zeta', 'Gamma', 'gamma', 'eta', 'theta'}:
        domains.add('number_theory')
    if operators & {'det', 'dim', 'ker', 'otimes', 'oplus'}:
        domains.add('algebra')
    if operators & {'sin', 'cos', 'tan', 'pi'}:
        domains.add('trigonometry')
    if operators & {'forall', 'exists', 'subset', 'cup', 'cap'}:
        domains.add('set_theory')
    if operators & {'rightarrow', 'Rightarrow', 'mapsto'}:
        domains.add('logic')
    return sorted(domains) if domains else ['unclassified']


def ingest(max_docs=50000, formulas_only=False, min_formula_len=10):
    """Stream OpenWebMath and extract formula features."""
    from datasets import load_dataset

    print("=" * 70)
    print("  OpenWebMath Ingestion")
    print(f"  Max documents: {max_docs:,}")
    print("=" * 70)

    t0 = time.time()
    ds = load_dataset("open-web-math/open-web-math", split="train", streaming=True)

    n_docs = 0
    n_formulas = 0
    n_unique = 0
    n_dedup = 0
    seen_hashes = set()

    # Accumulators
    operator_counts = Counter()
    domain_counts = Counter()
    formula_type_counts = Counter()

    out_formulas = OUT_DIR / "openwebmath_formulas.jsonl"
    out_stats = OUT_DIR / "openwebmath_stats.json"

    with open(out_formulas, "w") as f_out:
        for doc in ds:
            n_docs += 1
            if n_docs > max_docs:
                break

            text = doc.get("text", "")
            url = doc.get("url", "")

            formulas = extract_latex(text)
            if not formulas:
                continue

            for ftype, latex in formulas:
                if len(latex) < min_formula_len:
                    continue

                n_formulas += 1
                fhash = formula_hash(latex)

                if fhash in seen_hashes:
                    n_dedup += 1
                    continue
                seen_hashes.add(fhash)
                n_unique += 1

                features = extract_features(latex)
                ops = set(features["operators"])
                domains = classify_domain(ops)

                for op in features["operators"]:
                    operator_counts[op] += 1
                for d in domains:
                    domain_counts[d] += 1
                formula_type_counts[ftype] += 1

                entry = {
                    "hash": fhash,
                    "type": ftype,
                    "latex": latex[:500],  # cap storage
                    "domains": domains,
                    **features,
                }

                if not formulas_only:
                    entry["source_url"] = url[:200]

                f_out.write(json.dumps(entry) + "\n")

            if n_docs % 5000 == 0:
                elapsed = time.time() - t0
                rate = n_docs / elapsed
                print(f"  {n_docs:>8,} docs | {n_formulas:>8,} formulas | "
                      f"{n_unique:>8,} unique | {rate:.0f} docs/s")

    elapsed = time.time() - t0

    # Save stats
    stats = {
        "n_docs_processed": n_docs - 1,
        "n_formulas_total": n_formulas,
        "n_unique": n_unique,
        "n_dedup": n_dedup,
        "top_operators": operator_counts.most_common(30),
        "domain_distribution": dict(domain_counts.most_common()),
        "formula_types": dict(formula_type_counts.most_common()),
        "elapsed_s": round(elapsed, 1),
    }

    with open(out_stats, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  INGESTION COMPLETE")
    print(f"  Documents: {n_docs - 1:,}")
    print(f"  Formulas:  {n_formulas:,} total, {n_unique:,} unique ({n_dedup:,} deduped)")
    print(f"  Time:      {elapsed:.1f}s ({n_docs/elapsed:.0f} docs/s)")
    print(f"\n  Top 15 operators:")
    for op, count in operator_counts.most_common(15):
        print(f"    {op:20s} {count:>8,}")
    print(f"\n  Domain distribution:")
    for d, count in domain_counts.most_common():
        print(f"    {d:20s} {count:>8,}")
    print(f"\n  Output: {out_formulas}")
    print(f"  Stats:  {out_stats}")
    print(f"{'=' * 70}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="OpenWebMath Ingestion")
    parser.add_argument("--max-docs", type=int, default=50000,
                        help="Max documents to process (default: 50K)")
    parser.add_argument("--formulas-only", action="store_true",
                        help="Skip source URL metadata")
    parser.add_argument("--min-len", type=int, default=10,
                        help="Minimum formula length in chars (default: 10)")
    args = parser.parse_args()

    ingest(max_docs=args.max_docs, formulas_only=args.formulas_only,
           min_formula_len=args.min_len)


if __name__ == "__main__":
    main()
