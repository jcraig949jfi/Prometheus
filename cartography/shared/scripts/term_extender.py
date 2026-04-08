"""
Term Extender — Compute new terms for OEIS sequences beyond what's published.
===============================================================================
Targets lattice walk sequences (A148xxx family) and any sequence where we can
enumerate directly. Saves extended terms for batch OEIS submission.

Strategy:
  1. Load sequences from OEIS cache
  2. For lattice walk sequences: parse step set from name, run DP enumeration
  3. Verify computed terms match known terms exactly
  4. Save new terms to queue for submission

Usage:
    python term_extender.py                        # extend all lattice walks
    python term_extender.py --seq A148763          # one sequence
    python term_extender.py --family 148700 148900 # range
    python term_extender.py --target-n 45          # compute to n=45
"""

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
QUEUE_DIR = ROOT / "cartography" / "oeis" / "data" / "new_terms"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def parse_step_set(name):
    """Parse step set from OEIS sequence name like 'walks... steps taken from {(-1,-1,0), ...}'."""
    m = re.search(r'\{([^}]+)\}', name)
    if not m:
        return None
    raw = m.group(1)
    steps = []
    for tup in re.findall(r'\(([^)]+)\)', raw):
        parts = [int(x.strip()) for x in tup.split(',')]
        if len(parts) == 3:
            steps.append(tuple(parts))
        elif len(parts) == 2:
            steps.append(tuple(parts))
    return steps if steps else None


def count_walks_3d(steps, n_max, verify_terms=None):
    """Count walks in Z^3 octant using dynamic programming.

    Returns list of counts [a(0), a(1), ..., a(n_max)].
    If verify_terms is provided, checks against known values.
    """
    current = defaultdict(int)
    current[(0, 0, 0)] = 1
    counts = [1]
    verified = 0
    mismatch_at = None

    for step_num in range(1, n_max + 1):
        next_pos = defaultdict(int)
        for (x, y, z), cnt in current.items():
            for dx, dy, dz in steps:
                nx, ny, nz = x + dx, y + dy, z + dz
                if nx >= 0 and ny >= 0 and nz >= 0:
                    next_pos[(nx, ny, nz)] += cnt
        current = next_pos
        total = sum(current.values())
        counts.append(total)

        if verify_terms and step_num < len(verify_terms):
            if total == verify_terms[step_num]:
                verified += 1
            else:
                mismatch_at = step_num
                break

    return counts, verified, mismatch_at


def count_walks_2d(steps, n_max, verify_terms=None):
    """Count walks in Z^2 quarter plane using dynamic programming."""
    current = defaultdict(int)
    current[(0, 0)] = 1
    counts = [1]
    verified = 0
    mismatch_at = None

    for step_num in range(1, n_max + 1):
        next_pos = defaultdict(int)
        for (x, y), cnt in current.items():
            for dx, dy in steps:
                nx, ny = x + dx, y + dy
                if nx >= 0 and ny >= 0:
                    next_pos[(nx, ny)] += cnt
        current = next_pos
        total = sum(current.values())
        counts.append(total)

        if verify_terms and step_num < len(verify_terms):
            if total == verify_terms[step_num]:
                verified += 1
            else:
                mismatch_at = step_num
                break

    return counts, verified, mismatch_at


def extend_sequence(seq_id, known_terms, name, target_n=45):
    """Try to extend a sequence by computing more terms."""
    steps = parse_step_set(name)
    if not steps:
        return None

    dim = len(steps[0])
    if dim == 3:
        counter = count_walks_3d
    elif dim == 2:
        counter = count_walks_2d
    else:
        return None

    t0 = time.time()
    counts, verified, mismatch = counter(steps, target_n, verify_terms=known_terms)
    elapsed = time.time() - t0

    if mismatch is not None:
        return {"seq_id": seq_id, "status": "MISMATCH", "at": mismatch, "elapsed": elapsed}

    n_known = len(known_terms)
    n_new = len(counts) - n_known

    if n_new <= 0:
        return {"seq_id": seq_id, "status": "NO_NEW", "elapsed": elapsed}

    new_terms = {f"a({i})": counts[i] for i in range(n_known, len(counts))}

    return {
        "seq_id": seq_id,
        "status": "EXTENDED",
        "known_terms": n_known,
        "new_terms_count": n_new,
        "total_terms": len(counts),
        "verified": verified,
        "new_terms": new_terms,
        "all_terms": counts,
        "elapsed": round(elapsed, 2),
        "step_set": [list(s) for s in steps],
        "dimension": dim,
    }


def run_extension(family_start=148700, family_end=148900, target_n=45, single_seq=None):
    """Extend a family of sequences."""
    from search_engine import _load_oeis, _oeis_cache, _load_oeis_names, _oeis_names_cache
    _load_oeis()
    _load_oeis_names()

    print("=" * 70)
    print("  TERM EXTENDER — Computing new OEIS terms")
    print(f"  Target: n={target_n}")
    print("=" * 70)

    t0 = time.time()

    if single_seq:
        seq_ids = [single_seq]
    else:
        seq_ids = [f"A{i:06d}" for i in range(family_start, family_end + 1)]

    extended = 0
    mismatches = 0
    skipped = 0
    total_new = 0
    results = []

    for seq_id in seq_ids:
        name = _oeis_names_cache.get(seq_id, "")
        terms = _oeis_cache.get(seq_id, [])

        if not name or "walks" not in name.lower() or not terms:
            skipped += 1
            continue

        if len(terms) >= target_n:
            skipped += 1
            continue

        result = extend_sequence(seq_id, terms, name, target_n)
        if result is None:
            skipped += 1
            continue

        if result["status"] == "EXTENDED":
            extended += 1
            n_new = result["new_terms_count"]
            total_new += n_new
            print(f"  {seq_id}: +{n_new} terms ({result['known_terms']} -> {result['total_terms']}) "
                  f"in {result['elapsed']:.1f}s")
            results.append(result)

            # Save to queue
            queue_file = QUEUE_DIR / f"{seq_id}.json"
            with open(queue_file, "w") as f:
                json.dump({
                    "seq_id": seq_id,
                    "name": name,
                    "known_terms": result["known_terms"],
                    "new_terms": result["new_terms"],
                    "total_terms": result["total_terms"],
                    "verified_known": result["verified"],
                    "step_set": result["step_set"],
                    "dimension": result["dimension"],
                    "computed": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "method": "Dynamic programming walk enumeration in positive octant/quadrant",
                }, f, indent=2)

        elif result["status"] == "MISMATCH":
            mismatches += 1
            print(f"  {seq_id}: MISMATCH at n={result['at']} — step set parse may be wrong")

    elapsed = time.time() - t0

    print(f"\n{'=' * 70}")
    print(f"  TERM EXTENSION COMPLETE in {elapsed:.1f}s")
    print(f"  Sequences extended: {extended}")
    print(f"  Total new terms: {total_new}")
    print(f"  Mismatches: {mismatches}")
    print(f"  Skipped: {skipped}")
    print(f"  Queue directory: {QUEUE_DIR}")
    print(f"{'=' * 70}")

    # Update README
    readme = QUEUE_DIR / "README.md"
    lines = readme.read_text().split("\n") if readme.exists() else ["# OEIS New Terms Queue\n"]
    with open(readme, "a") as f:
        for r in results:
            f.write(f"- {r['seq_id']}: +{r['new_terms_count']} terms "
                    f"({r['known_terms']}->{r['total_terms']})\n")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OEIS Term Extender")
    parser.add_argument("--seq", type=str, default=None, help="Single sequence ID")
    parser.add_argument("--family", type=int, nargs=2, default=[148700, 148900],
                        help="Family range (start end)")
    parser.add_argument("--target-n", type=int, default=45, help="Compute to n=target")
    args = parser.parse_args()

    run_extension(
        family_start=args.family[0],
        family_end=args.family[1],
        target_n=args.target_n,
        single_seq=args.seq,
    )
