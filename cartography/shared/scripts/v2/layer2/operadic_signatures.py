"""
Operadic Signature Extractor (S22) — operadic structure from formula trees.
============================================================================
Extracts the compositional skeleton of each formula tree: how operations
compose, ignoring variable names and numeric values. Two formulas with the
same skeleton share the same operadic type.

    sin(x + y)   ->  sin(add(V,V))
    cos(a * b)   ->  cos(mul(V,V))      # same operadic type

Cross-domain clusters of shared skeletons reveal universal computational
patterns used independently in different areas of mathematics.

Usage:
    python operadic_signatures.py                          # full run
    python operadic_signatures.py --max-formulas 100000    # cap input
    python operadic_signatures.py --sample 50000           # random sample
"""

import argparse
import hashlib
import json
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


# ── Skeleton extraction ────────────────────────────────────────────────

def skeleton(node):
    """Recursively compute the operadic skeleton string for a tree node."""
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        return "V"
    if ntype == "number":
        return "N"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    child_skels = [skeleton(c) for c in children]
    return f"{op}({','.join(child_skels)})"


def skeleton_hash(skel_str):
    """MD5 hash of skeleton string, truncated to 16 hex chars."""
    return hashlib.md5(skel_str.encode("utf-8", errors="replace")).hexdigest()[:16]


# ── Enriched signature ─────────────────────────────────────────────────

def arity_profile(node):
    """Return sorted tuple of (op, arity) pairs for all internal nodes."""
    pairs = []
    _arity_walk(node, pairs)
    pairs.sort()
    return tuple(pairs)


def _arity_walk(node, pairs):
    if not isinstance(node, dict):
        return
    children = node.get("children", [])
    if children:
        op = node.get("op", node.get("type", "unk"))
        pairs.append((op, len(children)))
        for c in children:
            _arity_walk(c, pairs)


def depth_profile(node, depth=0):
    """Return dict: op -> list of depths where it appears."""
    prof = defaultdict(list)
    _depth_walk(node, depth, prof)
    return dict(prof)


def _depth_walk(node, depth, prof):
    if not isinstance(node, dict):
        return
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        op = node.get("op", ntype)
        prof[op].append(depth)
    for c in node.get("children", []):
        _depth_walk(c, depth + 1, prof)


def op_counts(node):
    """Count each operator type in the tree."""
    counts = Counter()
    _op_count_walk(node, counts)
    return dict(counts)


def _op_count_walk(node, counts):
    if not isinstance(node, dict):
        return
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        counts[node.get("op", ntype)] += 1
    for c in node.get("children", []):
        _op_count_walk(c, counts)


def is_symmetric(node):
    """Check if tree is left-right symmetric (mirror-equal children)."""
    if not isinstance(node, dict):
        return True
    children = node.get("children", [])
    if len(children) < 2:
        return True
    # Compare skeleton of first child with last, second with second-last, etc.
    n = len(children)
    for i in range(n // 2):
        if skeleton(children[i]) != skeleton(children[n - 1 - i]):
            return False
    return True


# ── Domain lookup ──────────────────────────────────────────────────────

def load_domain_map(max_load=None):
    """Load hash -> domains from openwebmath_formulas.jsonl."""
    dmap = {}
    if not FORMULAS_FILE.exists():
        print(f"  [warn] domain file not found: {FORMULAS_FILE}")
        return dmap
    print(f"  Loading domain map from {FORMULAS_FILE.name} ...")
    t0 = time.time()
    count = 0
    with open(FORMULAS_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if max_load and count >= max_load:
                break
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            h = rec.get("hash", "")
            domains = rec.get("domains", ["unclassified"])
            if h:
                dmap[h] = domains[0] if domains else "unclassified"
            count += 1
            if count % 2_000_000 == 0:
                print(f"    ... {count:,} domain entries loaded")
    print(f"  Domain map: {len(dmap):,} entries in {time.time()-t0:.1f}s")
    return dmap


# ── Depth profile summary (for serialization) ─────────────────────────

def depth_profile_summary(dp):
    """Compress depth profile to a short string: op:min-max, ..."""
    parts = []
    for op in sorted(dp):
        depths = dp[op]
        parts.append(f"{op}:{min(depths)}-{max(depths)}")
    return "|".join(parts)


# ── Main pipeline ─────────────────────────────────────────────────────

def process_formulas(max_formulas=None, sample_size=None):
    print("=" * 70)
    print("  Operadic Signature Extractor (S22)")
    print("=" * 70)

    # Load domain map
    domain_map = load_domain_map(max_load=max_formulas)

    # Determine sampling
    if sample_size:
        # Need to know total lines for reservoir sampling
        print(f"  Sampling {sample_size:,} formulas (reservoir sampling) ...")
        reservoir = []
        count = 0
        with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if max_formulas and count >= max_formulas:
                    break
                count += 1
                if len(reservoir) < sample_size:
                    reservoir.append(line)
                else:
                    j = random.randint(0, count - 1)
                    if j < sample_size:
                        reservoir[j] = line
                if count % 2_000_000 == 0:
                    print(f"    ... scanned {count:,} lines")
        lines = reservoir
        print(f"  Sampled {len(lines):,} from {count:,} total lines")
    else:
        lines = None  # stream mode

    # Output files
    sig_path = OUT_DIR / "operadic_signatures.jsonl"
    clust_path = OUT_DIR / "operadic_clusters.jsonl"

    # Cluster accumulators
    cluster_formulas = defaultdict(list)   # skel_hash -> [(formula_hash, domain, skel_str)]
    cluster_domains = defaultdict(set)     # skel_hash -> set of domains
    cluster_count = defaultdict(int)       # skel_hash -> count

    t0 = time.time()
    processed = 0
    skipped = 0

    def process_line(line, sig_out):
        nonlocal processed, skipped
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            return
        root = rec.get("root")
        if not root:
            skipped += 1
            return
        formula_hash = rec.get("hash", "")
        domain = domain_map.get(formula_hash, "unclassified")

        # Skeleton
        skel = skeleton(root)
        shash = skeleton_hash(skel)

        # Enriched features
        dp = depth_profile(root)
        oc = op_counts(root)
        n_ops = sum(oc.values())
        sym = is_symmetric(root)
        ap = arity_profile(root)
        ap_str = ",".join(f"{o}:{a}" for o, a in ap)
        dp_str = depth_profile_summary(dp)

        # Write signature record
        sig_rec = {
            "hash": formula_hash,
            "skeleton_hash": shash,
            "skeleton_str": skel[:200],
            "arity_profile": ap_str,
            "depth_profile": dp_str,
            "n_ops": n_ops,
            "is_symmetric": sym,
            "domain": domain,
        }
        sig_out.write(json.dumps(sig_rec, separators=(",", ":")) + "\n")

        # Accumulate cluster data
        cluster_count[shash] += 1
        cluster_domains[shash].add(domain)
        if len(cluster_formulas[shash]) < 3:
            cluster_formulas[shash].append({
                "hash": formula_hash,
                "domain": domain,
                "skeleton_str": skel[:200],
            })
        processed += 1

    with open(sig_path, "w", encoding="utf-8") as sig_out:
        if lines is not None:
            # Sampled mode
            for line in lines:
                process_line(line, sig_out)
                if processed % 500_000 == 0 and processed > 0:
                    elapsed = time.time() - t0
                    rate = processed / elapsed
                    print(f"    {processed:,} processed  ({rate:,.0f}/s)")
        else:
            # Streaming mode
            with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if max_formulas and processed >= max_formulas:
                        break
                    process_line(line, sig_out)
                    if processed % 500_000 == 0 and processed > 0:
                        elapsed = time.time() - t0
                        rate = processed / elapsed
                        print(f"    {processed:,} processed  ({rate:,.0f}/s)")

    elapsed = time.time() - t0

    # Write cluster file
    n_cross_domain = 0
    with open(clust_path, "w", encoding="utf-8") as cf:
        for shash in sorted(cluster_count, key=lambda h: -cluster_count[h]):
            domains = sorted(cluster_domains[shash])
            is_cross = len(domains) > 1 and not (len(domains) == 1 and domains[0] == "unclassified")
            if is_cross:
                n_cross_domain += 1
            rec = {
                "skeleton_hash": shash,
                "n_formulas": cluster_count[shash],
                "n_domains": len(domains),
                "domains": domains,
                "examples": cluster_formulas[shash],
            }
            cf.write(json.dumps(rec, separators=(",", ":")) + "\n")

    n_unique = len(cluster_count)

    # Top clusters
    top = sorted(cluster_count.items(), key=lambda kv: -kv[1])[:15]

    print()
    print("=" * 70)
    print(f"  Operadic Signature Extraction Complete")
    print(f"  {'=' * 38}")
    print(f"  Formulas processed:    {processed:>12,}")
    print(f"  Skipped (parse err):   {skipped:>12,}")
    print(f"  Unique skeletons:      {n_unique:>12,}")
    print(f"  Cross-domain clusters: {n_cross_domain:>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {processed/elapsed:>11,.0f}/s")
    print()
    print("  Top 15 operadic types:")
    for i, (shash, cnt) in enumerate(top, 1):
        doms = sorted(cluster_domains[shash])
        examples = cluster_formulas[shash]
        skel_preview = examples[0]["skeleton_str"][:60] if examples else ""
        print(f"    {i:>2}. [{shash}] n={cnt:>8,}  domains={len(doms):>3}  {skel_preview}")
    print()
    print(f"  Output: {sig_path}")
    print(f"  Output: {clust_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Operadic Signature Extractor (S22)")
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on total formulas to process")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    process_formulas(max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
