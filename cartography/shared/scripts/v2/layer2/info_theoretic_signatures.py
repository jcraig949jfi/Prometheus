"""
Information-Theoretic Signature Extractor (S24) — entropy and complexity.
=========================================================================
Computes information-theoretic signatures from OEIS sequences and formula
trees: Shannon entropy, compression ratio, Lempel-Ziv complexity, and
operator diversity.

Usage:
    python info_theoretic_signatures.py                          # full run
    python info_theoretic_signatures.py --max-formulas 100000    # cap formulas
    python info_theoretic_signatures.py --sample 50000           # sample formulas
    python info_theoretic_signatures.py --max-seqs 50000         # cap sequences
"""

import argparse
import gzip
import json
import math
import sys
import time
import zlib
import random
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
STRIPPED_TXT = OEIS_DATA / "stripped_new.txt"
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "info_theoretic_signatures.jsonl"


# ---------------------------------------------------------------------------
# OEIS loader
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=20, max_seqs=None):
    """Parse OEIS stripped format, keep sequences with >= min_length terms."""
    # Try gz first, then plain text
    if STRIPPED_GZ.exists():
        src, opener = STRIPPED_GZ, lambda p: gzip.open(p, "rt", encoding="utf-8", errors="ignore")
    elif STRIPPED_FALLBACK.exists():
        src, opener = STRIPPED_FALLBACK, lambda p: gzip.open(p, "rt", encoding="utf-8", errors="ignore")
    elif STRIPPED_TXT.exists():
        src, opener = STRIPPED_TXT, lambda p: open(p, "r", encoding="utf-8", errors="ignore")
    else:
        print(f"  ERROR: no OEIS stripped file found")
        return {}

    print(f"  Loading OEIS sequences from {src.name} (min_length={min_length}) ...")
    seqs = {}
    with opener(src) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0].strip()
            if not sid.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t) for t in terms_str.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= min_length:
                seqs[sid] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


# ---------------------------------------------------------------------------
# Information-theoretic measures for sequences
# ---------------------------------------------------------------------------

def shannon_entropy_binned(terms, n_bins=50):
    """Shannon entropy of binned sequence values."""
    if not terms:
        return 0.0
    mn, mx = min(terms), max(terms)
    if mn == mx:
        return 0.0
    span = mx - mn
    binned = [int((t - mn) / span * (n_bins - 1)) for t in terms]
    counts = Counter(binned)
    total = len(binned)
    ent = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            ent -= p * math.log2(p)
    return round(ent, 6)


def compression_ratio(terms):
    """Ratio of compressed to original string length."""
    s = ",".join(str(t) for t in terms)
    raw = s.encode("utf-8")
    compressed = zlib.compress(raw)
    if len(raw) == 0:
        return 1.0
    return round(len(compressed) / len(raw), 6)


def lempel_ziv_complexity(terms):
    """Lempel-Ziv complexity: count of distinct substrings in a scan."""
    # Convert to string of symbols for LZ parsing
    s = ",".join(str(t) for t in terms)
    n = len(s)
    if n == 0:
        return 0
    i, k, l_val = 0, 1, 1
    c = 1
    while k + l_val <= n:
        # Check if s[k:k+l] appears in s[0:k+l-1]
        if s[k:k + l_val] in s[i:k + l_val - 1]:
            l_val += 1
        else:
            c += 1
            k += l_val
            l_val = 1
            i = 0
    return c


def first_order_diff_entropy(terms, n_bins=50):
    """Shannon entropy of consecutive differences."""
    if len(terms) < 2:
        return 0.0
    diffs = [terms[i + 1] - terms[i] for i in range(len(terms) - 1)]
    return shannon_entropy_binned(diffs, n_bins)


def sequence_signature(seq_id, terms):
    """Compute full info-theoretic signature for a sequence."""
    return {
        "id": seq_id,
        "source": "oeis",
        "entropy": shannon_entropy_binned(terms),
        "compression_ratio": compression_ratio(terms),
        "lz_complexity": lempel_ziv_complexity(terms),
        "diff_entropy": first_order_diff_entropy(terms),
        "n_terms": len(terms),
    }


# ---------------------------------------------------------------------------
# Information-theoretic measures for formula trees
# ---------------------------------------------------------------------------

def collect_operators(node):
    """Walk tree and collect all operator names."""
    ops = []
    if not isinstance(node, dict):
        return ops
    ntype = node.get("type", "")
    if ntype not in ("variable", "number", ""):
        op = node.get("op", ntype) or ntype
        if op:
            ops.append(op.lower())
    for c in node.get("children", []):
        ops.extend(collect_operators(c))
    return ops


def count_nodes(node):
    """Count total nodes in tree."""
    if not isinstance(node, dict):
        return 1
    total = 1
    for c in node.get("children", []):
        total += count_nodes(c)
    return total


def tree_signature(formula_hash, root):
    """Compute info-theoretic signature for a formula tree."""
    ops = collect_operators(root)
    n_nodes = count_nodes(root)

    # Operator distribution entropy
    if ops:
        counts = Counter(ops)
        total = len(ops)
        op_entropy = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                op_entropy -= p * math.log2(p)
        op_entropy = round(op_entropy, 6)
        unique_ops = len(counts)
        op_diversity = round(unique_ops / total, 6) if total > 0 else 0.0
    else:
        op_entropy = 0.0
        unique_ops = 0
        op_diversity = 0.0

    # Tree compression ratio: serialized size / node count
    serialized = json.dumps(root, separators=(",", ":"))
    tree_cr = round(len(serialized) / max(n_nodes, 1), 4)

    return {
        "id": formula_hash,
        "source": "formula",
        "entropy": op_entropy,
        "compression_ratio": tree_cr,
        "lz_complexity": lempel_ziv_complexity(list(range(n_nodes))),  # structural complexity
        "operator_diversity": op_diversity,
        "n_operators": len(ops),
        "unique_operators": unique_ops,
        "n_nodes": n_nodes,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(max_seqs=50000, max_formulas=100000, sample_size=None):
    print("=" * 70)
    print("  Information-Theoretic Signature Extractor (S24)")
    print("=" * 70)

    t0 = time.time()
    written = 0

    with open(OUT_FILE, "w", encoding="utf-8") as out:
        # --- OEIS sequences ---
        seqs = load_oeis_sequences(min_length=20, max_seqs=max_seqs)
        seq_count = 0
        for sid, terms in seqs.items():
            sig = sequence_signature(sid, terms)
            out.write(json.dumps(sig, separators=(",", ":")) + "\n")
            seq_count += 1
            written += 1
            if seq_count % 10_000 == 0:
                elapsed = time.time() - t0
                print(f"    OEIS: {seq_count:,} processed  ({seq_count / max(elapsed, 0.01):,.0f}/s)")
        print(f"  OEIS sequences processed: {seq_count:,}")

        # --- Formula trees ---
        if TREES_FILE.exists():
            print(f"  Loading formula trees from {TREES_FILE.name} ...")
            formula_count = 0
            skipped = 0

            if sample_size:
                # Reservoir sampling
                print(f"  Reservoir sampling {sample_size:,} formulas ...")
                reservoir = []
                scan_count = 0
                with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if max_formulas and scan_count >= max_formulas:
                            break
                        scan_count += 1
                        if len(reservoir) < sample_size:
                            reservoir.append(line)
                        else:
                            j = random.randint(0, scan_count - 1)
                            if j < sample_size:
                                reservoir[j] = line
                        if scan_count % 2_000_000 == 0:
                            print(f"    ... scanned {scan_count:,} lines")
                lines = reservoir
                print(f"  Sampled {len(lines):,} from {scan_count:,} total lines")
            else:
                lines = None

            def process_formula_line(line):
                nonlocal formula_count, skipped
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    skipped += 1
                    return None
                root = rec.get("root")
                if not root:
                    skipped += 1
                    return None
                formula_hash = rec.get("hash", "")
                sig = tree_signature(formula_hash, root)
                formula_count += 1
                return sig

            if lines is not None:
                for line in lines:
                    sig = process_formula_line(line)
                    if sig:
                        out.write(json.dumps(sig, separators=(",", ":")) + "\n")
                        written += 1
                    if formula_count % 50_000 == 0 and formula_count > 0:
                        elapsed = time.time() - t0
                        print(f"    Formulas: {formula_count:,} processed  ({formula_count / max(elapsed, 0.01):,.0f}/s)")
            else:
                with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if max_formulas and formula_count >= max_formulas:
                            break
                        sig = process_formula_line(line)
                        if sig:
                            out.write(json.dumps(sig, separators=(",", ":")) + "\n")
                            written += 1
                        if formula_count % 500_000 == 0 and formula_count > 0:
                            elapsed = time.time() - t0
                            print(f"    Formulas: {formula_count:,} processed  ({formula_count / max(elapsed, 0.01):,.0f}/s)")

            print(f"  Formula trees processed: {formula_count:,}  (skipped: {skipped:,})")
        else:
            print(f"  [warn] Formula trees not found: {TREES_FILE}")
            formula_count = 0

    elapsed = time.time() - t0
    print()
    print("=" * 70)
    print(f"  Information-Theoretic Signatures Complete")
    print(f"  {'=' * 40}")
    print(f"  OEIS sequences:    {seq_count:>12,}")
    print(f"  Formula trees:     {formula_count:>12,}")
    print(f"  Total written:     {written:>12,}")
    print(f"  Time:              {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:              {written / elapsed:>11,.0f}/s")
    print(f"  Output: {OUT_FILE}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Information-Theoretic Signature Extractor (S24)")
    parser.add_argument("--max-formulas", type=int, default=100_000,
                        help="Cap on formula trees to process (default: 100000)")
    parser.add_argument("--max-seqs", type=int, default=50_000,
                        help="Cap on OEIS sequences to process (default: 50000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    run(max_seqs=args.max_seqs, max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
