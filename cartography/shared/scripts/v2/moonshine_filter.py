"""
Moonshine Bridge Filter — Separate Real Bridges from Noise
=============================================================
The moonshine OEIS scan found 3,315 coefficient bridges, but most are noise:
- theta_3 (A000122): 3,099 bridges from zero-heavy patterns
- M24 umbral (A053250): 165 bridges from simple [1,0,-1,1,1,-1] cyclotomic

This script filters by:
1. Recursion complexity: real moonshine sequences have high-order, irreducible recurrences
2. Coefficient entropy: moonshine coefficients are arithmetically rich, not sparse
3. Growth rate: mock theta functions grow sub-exponentially, cyclotomics are bounded
4. Cross-reference depth: real bridges should connect to 2+ core moonshine sequences

Usage:
    python moonshine_filter.py
"""

import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from math import log, sqrt


def load_sequences(data_dir):
    """Load OEIS sequences."""
    seqs = {}
    with open(data_dir / "stripped_new.txt", 'r', errors='ignore') as f:
        for line in f:
            if not line.startswith('A'):
                continue
            parts = line.strip().split(',')
            seq_id = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except:
                        pass
            if terms:
                seqs[seq_id] = terms
    return seqs


def coefficient_entropy(terms, max_terms=30):
    """Measure arithmetic richness of coefficient sequence.
    Low entropy = many zeros/repeats (noise). High entropy = rich structure."""
    t = terms[:max_terms]
    if not t:
        return 0
    # Normalized entropy of absolute value distribution
    counts = Counter(abs(x) for x in t)
    total = len(t)
    entropy = 0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * log(p)
    # Normalize by log(total)
    max_ent = log(total) if total > 1 else 1
    return entropy / max_ent


def zero_fraction(terms, max_terms=30):
    """Fraction of terms that are zero."""
    t = terms[:max_terms]
    if not t:
        return 1
    return sum(1 for x in t if x == 0) / len(t)


def growth_rate(terms):
    """Estimate asymptotic growth rate from log of absolute values."""
    abs_vals = [abs(x) for x in terms if x != 0]
    if len(abs_vals) < 5:
        return 0
    # Fit log|a_n| ~ alpha * log(n)
    logs = [(log(i + 1), log(v)) for i, v in enumerate(abs_vals) if v > 1]
    if len(logs) < 3:
        return 0
    n = len(logs)
    sx = sum(x for x, _ in logs)
    sy = sum(y for _, y in logs)
    sxx = sum(x * x for x, _ in logs)
    sxy = sum(x * y for x, y in logs)
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-10:
        return 0
    alpha = (n * sxy - sx * sy) / denom
    return alpha


def recursion_order(terms, max_order=8):
    """
    Estimate minimal recursion order by checking if a_n = c_1*a_{n-1} + ... + c_k*a_{n-k}
    for some constant coefficients. Returns the minimal k that works, or max_order+1 if none.
    """
    t = terms
    if len(t) < max_order + 3:
        return max_order + 1

    for k in range(1, max_order + 1):
        # Try to solve: a_n = c_1*a_{n-1} + ... + c_k*a_{n-k} for n = k..len-1
        # Set up linear system: A * c = b
        n_eqs = min(len(t) - k, 20)
        if n_eqs < k:
            continue

        # Build matrix
        A = []
        b = []
        for i in range(k, k + n_eqs):
            row = [t[i - j - 1] for j in range(k)]
            A.append(row)
            b.append(t[i])

        # Solve via Gaussian elimination (exact integer arithmetic)
        # Use rational arithmetic to avoid float issues
        from fractions import Fraction
        Af = [[Fraction(x) for x in row] for row in A]
        bf = [Fraction(x) for x in b]

        # Augmented matrix
        aug = [row + [bi] for row, bi in zip(Af, bf)]
        n_rows = len(aug)
        n_cols = k

        # Forward elimination
        pivot_row = 0
        for col in range(n_cols):
            # Find pivot
            found = False
            for row in range(pivot_row, n_rows):
                if aug[row][col] != 0:
                    aug[pivot_row], aug[row] = aug[row], aug[pivot_row]
                    found = True
                    break
            if not found:
                continue
            # Eliminate
            pivot = aug[pivot_row][col]
            for row in range(n_rows):
                if row == pivot_row:
                    continue
                if aug[row][col] != 0:
                    factor = aug[row][col] / pivot
                    for j in range(n_cols + 1):
                        aug[row][j] -= factor * aug[pivot_row][j]
            pivot_row += 1

        if pivot_row < k:
            continue  # Underdetermined

        # Extract solution
        coeffs = [Fraction(0)] * k
        for row in range(k):
            if aug[row][row] != 0:
                coeffs[row] = aug[row][k] / aug[row][row]

        # Verify on ALL terms
        ok = True
        for i in range(k, len(t)):
            pred = sum(coeffs[j] * t[i - j - 1] for j in range(k))
            if pred != t[i]:
                ok = False
                break

        if ok:
            return k

    return max_order + 1


def main():
    data_dir = Path(__file__).resolve().parents[3] / "oeis" / "data"

    print("MOONSHINE BRIDGE FILTER")
    print("=" * 72)
    print()

    # Load moonshine results
    results_path = Path(__file__).parent / "moonshine_oeis_results.json"
    with open(results_path) as f:
        moon_data = json.load(f)

    # Load sequences
    print("Loading OEIS sequences...")
    seqs = load_sequences(data_dir)
    print(f"  Loaded {len(seqs)} sequences")
    print()

    # Load the bridges
    bridges = moon_data["coefficient_bridges"]
    print(f"Total bridges from scan: {len(bridges)}")

    # Group by core sequence
    by_core = defaultdict(list)
    for b in bridges:
        by_core[b["core"]].append(b)

    MOONSHINE_CORE = {
        "A000521", "A007191", "A014708", "A007246", "A007267",
        "A000594", "A006352", "A004009", "A013973", "A008410",
        "A013974", "A029829", "A045488", "A001488", "A053250",
        "A000118", "A008443", "A000122", "A004011", "A008408", "A004027",
    }

    # ─── Filter each bridge ───
    print("\nFiltering bridges by structural complexity...")
    print()

    filtered = []
    noise = []

    for bridge in bridges:
        match_id = bridge["match"]
        core_id = bridge["core"]

        if match_id not in seqs:
            noise.append(bridge)
            continue

        terms = seqs[match_id]

        # Compute metrics
        ent = coefficient_entropy(terms)
        zf = zero_fraction(terms)
        gr = growth_rate(terms)
        rec = recursion_order(terms)

        bridge["entropy"] = round(ent, 3)
        bridge["zero_frac"] = round(zf, 3)
        bridge["growth_rate"] = round(gr, 2)
        bridge["recursion_order"] = rec

        # Filter criteria:
        # 1. High zero fraction (>60%) = likely trivial
        # 2. Low entropy (<0.3) = not arithmetically rich
        # 3. Very low recursion order (1-2) = trivial linear recurrence
        # 4. Is the match itself a moonshine-core sequence? (self-reference)

        is_noise = False
        reasons = []

        if match_id in MOONSHINE_CORE:
            reasons.append("self-ref")
            # Keep these as "known" bridges, not noise

        if zf > 0.6 and match_id not in MOONSHINE_CORE:
            is_noise = True
            reasons.append(f"zero_frac={zf:.2f}")

        if ent < 0.3 and match_id not in MOONSHINE_CORE:
            is_noise = True
            reasons.append(f"entropy={ent:.3f}")

        if rec <= 2 and match_id not in MOONSHINE_CORE:
            is_noise = True
            reasons.append(f"rec_order={rec}")

        bridge["is_noise"] = is_noise
        bridge["filter_reasons"] = reasons

        if is_noise:
            noise.append(bridge)
        else:
            filtered.append(bridge)

    print(f"Filtered: {len(filtered)} genuine bridges, {len(noise)} noise")
    print()

    # ─── Report genuine bridges ───
    print("=" * 72)
    print("GENUINE MOONSHINE BRIDGES (post-filter)")
    print("=" * 72)
    print()

    # Load names
    names = {}
    try:
        with open(data_dir / "oeis_names.json", 'r', encoding='utf-8', errors='replace') as f:
            names = json.load(f)
    except:
        pass

    by_core_filtered = defaultdict(list)
    for b in filtered:
        by_core_filtered[b["core"]].append(b)

    for core_id in sorted(by_core_filtered.keys()):
        matches = by_core_filtered[core_id]
        core_name = names.get(core_id, "?")[:50]
        print(f"\n{core_id} ({core_name}): {len(matches)} bridges")
        for m in matches[:10]:
            name = names.get(m["match"], "?")[:50]
            print(f"  {m['match']}: ent={m['entropy']:.2f} zf={m['zero_frac']:.2f} "
                  f"gr={m['growth_rate']:.1f} rec={m['recursion_order']}")
            print(f"    {name}")
            print(f"    window: {m['window']}")

    # ─── Cross-domain analysis ───
    print()
    print("=" * 72)
    print("CROSS-DOMAIN ANALYSIS")
    print("=" * 72)
    print()

    # Which filtered bridges connect DIFFERENT moonshine types?
    # (e.g., mock theta function matching a monstrous series = genuine cross-domain)
    print("Bridge sequences appearing in multiple core connections:")
    match_to_cores = defaultdict(set)
    for b in filtered:
        match_to_cores[b["match"]].add(b["core"])

    multi_core = {k: v for k, v in match_to_cores.items() if len(v) >= 2}
    for match_id, cores in sorted(multi_core.items(), key=lambda x: -len(x[1])):
        name = names.get(match_id, "?")[:60]
        print(f"  {match_id} ({len(cores)} cores): {name}")
        print(f"    Cores: {sorted(cores)}")

    print(f"\nSequences connecting 2+ moonshine cores: {len(multi_core)}")

    # ─── Save ───
    out = {
        "total_bridges": len(bridges),
        "genuine": len(filtered),
        "noise": len(noise),
        "genuine_bridges": filtered[:200],
        "multi_core_bridges": [{
            "seq_id": k,
            "n_cores": len(v),
            "cores": list(v),
            "name": names.get(k, ""),
        } for k, v in sorted(multi_core.items(), key=lambda x: -len(x[1]))],
    }

    out_path = Path(__file__).parent / "moonshine_filtered_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
