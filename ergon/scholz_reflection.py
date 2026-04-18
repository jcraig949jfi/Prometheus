"""
Scholz Reflection Theorem (1932) — Empirical Audit
===================================================
Harmonia work queue item #5: audit_scholz_reflection_p3_BST

Scholz's theorem: For a quadratic field K = Q(sqrt(d)) with d > 0,
let K* = Q(sqrt(-3d)). Then:
    |rank_3(Cl(K)) - rank_3(Cl(K*))| <= 1
and more precisely:
    rank_3(Cl(K*)) <= rank_3(Cl(K)) + 1
    rank_3(Cl(K))  <= rank_3(Cl(K*))

This script tests the theorem on ~1.37M quadratic number fields from LMFDB Postgres.

Context: Harmonia sessionD found the p=3 BST exponent is distinctly slower than
p=2,5,7. Scholz reflection couples real and imaginary 3-ranks, which could
explain the anomalous p=3 behavior.
"""

import psycopg2
import numpy as np
from collections import Counter, defaultdict
import time
import sys
import os

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


def parse_class_group(cg_str):
    """Parse LMFDB class_group text like '{2,118}' into list of ints."""
    s = cg_str.strip('{}')
    if not s:
        return []
    return [int(x) for x in s.split(',')]


def three_rank(invariant_factors):
    """
    Compute 3-rank = number of cyclic factors divisible by 3.

    The class group is given in invariant factor form [d1, d2, ...] where d_i | d_{i+1}.
    The 3-rank is the number of factors divisible by 3 (equivalently, dim of Cl[3] over F_3).
    """
    return sum(1 for d in invariant_factors if d % 3 == 0)


def fundamental_discriminant_of_neg3d(d):
    """
    Given a positive fundamental discriminant d, compute the discriminant of Q(sqrt(-3d)).

    The discriminant of Q(sqrt(m)) for squarefree m is:
      m   if m ≡ 1 (mod 4)
      4m  if m ≡ 2,3 (mod 4)

    But we work with discriminants directly. If d is a fundamental discriminant > 0,
    then -3d might not be a fundamental discriminant. We need to find the fundamental
    discriminant of Q(sqrt(-3d)).

    For the LMFDB lookup, we need disc_abs = |disc| of Q(sqrt(-3d)).
    """
    # d is a fundamental discriminant > 0
    # We want the field Q(sqrt(-3d))
    # The squarefree kernel of -3d determines the field
    # But since d is a fundamental discriminant, d is either:
    #   d ≡ 1 (mod 4) and squarefree, OR
    #   d = 4m where m ≡ 2,3 (mod 4) and m squarefree

    # Case 1: d ≡ 1 (mod 4), d squarefree
    #   -3d: squarefree part of 3d
    #   If 3 ∤ d: sqfree(3d) = 3d, disc = -3d if 3d ≡ 3 (mod 4) → disc = -4*3d = -12d
    #                                         or -3d if 3d ≡ 1 (mod 4)
    #   Since d ≡ 1 (mod 4), 3d ≡ 3 (mod 4), so disc = -12d, abs = 12d
    #   If 3 | d: d = 3k, sqfree(3d) = sqfree(9k) = k, disc of Q(sqrt(-k))
    #             k ≡ ? ... depends

    # This gets complicated. Let's just compute directly.
    # Extract the squarefree part of 3*|core(d)| where core(d) is from d.

    # Actually for LMFDB matching, it's simpler to just precompute
    # disc_abs for Q(sqrt(-3d)) and look it up.

    # A fundamental discriminant d > 0 has core:
    #   if d ≡ 1 (mod 4): core = d (squarefree)
    #   if d ≡ 0 (mod 4): core = d/4 (squarefree, ≡ 2,3 mod 4)

    if d % 4 == 0:
        m = d // 4  # squarefree, m ≡ 2 or 3 (mod 4)
    else:
        m = d  # squarefree, m ≡ 1 (mod 4)

    # Q(sqrt(-3d)) = Q(sqrt(-3m)) since d and m generate the same field up to sign
    # Wait no — d is the discriminant, m is the radicand.
    # Q(sqrt(m)) has discriminant d. We want Q(sqrt(-3m)).

    # Compute squarefree part of 3m
    n = 3 * m
    # Remove square factors — but m is squarefree, so only 3 could create a square
    if m % 3 == 0:
        # 3m = 3 * 3k = 9k, squarefree part = k
        sf = m // 3
    else:
        sf = 3 * m  # already squarefree since m is squarefree and 3 ∤ m

    # Now Q(sqrt(-sf)) where sf > 0, squarefree
    # Discriminant:
    #   if sf ≡ 3 (mod 4): disc = -4*sf
    #   if sf ≡ 1 (mod 4): disc = -sf  ... but sf must be ≡ 1 mod 4 for this
    #   if sf ≡ 2 (mod 4): disc = -4*sf
    # Actually: for negative radicand -sf:
    #   -sf ≡ 1 (mod 4) iff sf ≡ 3 (mod 4)
    #   disc = -sf if sf ≡ 3 (mod 4)
    #   disc = -4*sf if sf ≡ 1 or 2 (mod 4)

    if sf % 4 == 3:
        disc_abs = sf
    else:
        disc_abs = 4 * sf

    return disc_abs


def main():
    print("=" * 70)
    print("Scholz Reflection Theorem (1932) — Empirical Audit")
    print("Harmonia work queue #5: audit_scholz_reflection_p3_BST")
    print("=" * 70)
    print()

    t0 = time.time()

    # Connect and load all degree-2 fields
    print("Connecting to Postgres (lmfdb)...")
    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()

    print("Loading all quadratic number fields...")
    cur.execute("""
        SELECT disc_abs::float, disc_sign::int, class_number::int, class_group
        FROM nf_fields
        WHERE degree::int = 2
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"  Loaded {len(rows):,} quadratic fields in {time.time()-t0:.1f}s")
    print()

    # Build lookup tables
    # Key: disc_abs (float) -> (disc_sign, class_number, class_group_str)
    real_fields = {}   # disc_abs -> (class_number, class_group, 3-rank)
    imag_fields = {}   # disc_abs -> (class_number, class_group, 3-rank)

    real_3rank_dist = Counter()
    imag_3rank_dist = Counter()

    for disc_abs, disc_sign, cn, cg_str in rows:
        disc_abs_int = int(disc_abs)
        factors = parse_class_group(cg_str)
        r3 = three_rank(factors)

        if disc_sign == 1:
            real_fields[disc_abs_int] = (cn, cg_str, r3)
            real_3rank_dist[r3] += 1
        else:
            imag_fields[disc_abs_int] = (cn, cg_str, r3)
            imag_3rank_dist[r3] += 1

    print(f"  Real quadratic fields: {len(real_fields):,}")
    print(f"  Imaginary quadratic fields: {len(imag_fields):,}")
    print()

    # ── 3-rank distributions ──
    print("─" * 50)
    print("3-RANK DISTRIBUTIONS")
    print("─" * 50)
    print(f"  {'rank_3':>6}  {'Real':>10}  {'Imaginary':>10}")
    max_rank = max(max(real_3rank_dist.keys()), max(imag_3rank_dist.keys()))
    for r in range(max_rank + 1):
        rc = real_3rank_dist.get(r, 0)
        ic = imag_3rank_dist.get(r, 0)
        print(f"  {r:>6}  {rc:>10,}  {ic:>10,}")
    print()

    # ── Scholz pairing ──
    print("─" * 50)
    print("SCHOLZ PAIRING: real K = Q(sqrt(d)) <-> K* = Q(sqrt(-3d))")
    print("─" * 50)

    paired = 0
    unpaired = 0
    violations = 0

    # Track |r3(K*) - r3(K)| distribution
    diff_dist = Counter()
    # Track (r3_real, r3_imag) joint distribution
    joint_dist = Counter()
    # Track the precise Scholz inequalities
    scholz_tight_lower = 0  # r3(K) = r3(K*)     (lower bound tight)
    scholz_tight_upper = 0  # r3(K*) = r3(K) + 1 (upper bound tight)
    scholz_strict = 0       # r3(K) < r3(K*) < r3(K) + 1 — impossible for integers!

    violation_examples = []

    for disc_abs_real, (cn_r, cg_r, r3_r) in real_fields.items():
        # Find conjugate
        conj_disc = fundamental_discriminant_of_neg3d(disc_abs_real)

        if conj_disc in imag_fields:
            cn_i, cg_i, r3_i = imag_fields[conj_disc]
            paired += 1

            diff = r3_i - r3_r
            diff_dist[diff] += 1
            joint_dist[(r3_r, r3_i)] += 1

            # Scholz says: r3(K) <= r3(K*) <= r3(K) + 1
            # i.e., diff ∈ {0, 1}
            if diff == 0:
                scholz_tight_lower += 1
            elif diff == 1:
                scholz_tight_upper += 1
            else:
                violations += 1
                if len(violation_examples) < 20:
                    violation_examples.append(
                        (disc_abs_real, conj_disc, r3_r, r3_i, cg_r, cg_i)
                    )
        else:
            unpaired += 1

    print(f"  Paired:   {paired:>10,}")
    print(f"  Unpaired: {unpaired:>10,}  (conjugate not in database)")
    print()

    if paired == 0:
        print("  ERROR: No pairs found. Check discriminant pairing logic.")
        return

    # ── Scholz results ──
    print("─" * 50)
    print("SCHOLZ THEOREM VERIFICATION")
    print("─" * 50)
    print(f"  Theorem: r3(K) <= r3(K*) <= r3(K) + 1")
    print(f"  Equivalently: r3(K*) - r3(K) ∈ {{0, 1}}")
    print()
    print(f"  r3(K*) = r3(K)     (equality):   {scholz_tight_lower:>10,}  ({100*scholz_tight_lower/paired:.2f}%)")
    print(f"  r3(K*) = r3(K) + 1 (upper tight): {scholz_tight_upper:>10,}  ({100*scholz_tight_upper/paired:.2f}%)")
    print(f"  VIOLATIONS (|diff| > 1 or diff < 0): {violations:>6,}  ({100*violations/paired:.4f}%)")
    print()

    if violation_examples:
        print("  *** VIOLATION EXAMPLES ***")
        for (da_r, da_i, r3r, r3i, cgr, cgi) in violation_examples[:10]:
            print(f"    disc_real={da_r}, disc_imag={da_i}, "
                  f"r3_real={r3r}, r3_imag={r3i}, "
                  f"cg_real={cgr}, cg_imag={cgi}, diff={r3i - r3r}")
        print()

    # ── Difference distribution ──
    print("─" * 50)
    print("DIFFERENCE DISTRIBUTION: r3(K*) - r3(K)")
    print("─" * 50)
    for d in sorted(diff_dist.keys()):
        c = diff_dist[d]
        print(f"  diff = {d:>3}: {c:>10,}  ({100*c/paired:.3f}%)")
    print()

    # ── Joint distribution ──
    print("─" * 50)
    print("JOINT (r3_real, r3_imag) DISTRIBUTION")
    print("─" * 50)
    for (r3r, r3i) in sorted(joint_dist.keys()):
        c = joint_dist[(r3r, r3i)]
        scholz_ok = "✓" if 0 <= r3i - r3r <= 1 else "✗ VIOLATION"
        print(f"  ({r3r}, {r3i}): {c:>10,}  ({100*c/paired:.3f}%)  {scholz_ok}")
    print()

    # ── Cohen-Lenstra comparison ──
    print("─" * 50)
    print("COHEN-LENSTRA COMPARISON")
    print("─" * 50)
    print()

    # Cohen-Lenstra heuristics predict for imaginary quadratic fields:
    #   Prob(3 | h) ~ 1 - prod_{k>=1}(1 - 3^{-k}) ≈ 43.987%
    #   More precisely, Prob(rank_3 >= 1) ≈ 43.987%
    #   Prob(rank_3 = 0) ≈ 56.013%
    #   Prob(rank_3 = 1) ≈ 39.455%
    #   Prob(rank_3 = 2) ≈ 4.310%
    #
    # For real quadratic fields:
    #   Prob(rank_3 >= 1) ≈ 1 - prod_{k>=2}(1 - 3^{-k}) ≈ 13.948%
    #   (the product starts at k=2 for real fields)

    # Cohen-Lenstra predictions
    cl_imag_r0 = 1.0
    for k in range(1, 20):
        cl_imag_r0 *= (1 - 3**(-k))
    cl_imag_r1_plus = 1 - cl_imag_r0

    cl_real_r0 = 1.0
    for k in range(2, 20):
        cl_real_r0 *= (1 - 3**(-k))
    cl_real_r1_plus = 1 - cl_real_r0

    total_real = sum(real_3rank_dist.values())
    total_imag = sum(imag_3rank_dist.values())

    obs_real_r0_frac = real_3rank_dist[0] / total_real
    obs_real_r1_frac = 1 - obs_real_r0_frac
    obs_imag_r0_frac = imag_3rank_dist[0] / total_imag
    obs_imag_r1_frac = 1 - obs_imag_r0_frac

    print("  IMAGINARY quadratic fields:")
    print(f"    Prob(rank_3 = 0): observed = {obs_imag_r0_frac:.5f}, C-L = {cl_imag_r0:.5f}, ratio = {obs_imag_r0_frac/cl_imag_r0:.5f}")
    print(f"    Prob(rank_3 >= 1): observed = {obs_imag_r1_frac:.5f}, C-L = {cl_imag_r1_plus:.5f}, ratio = {obs_imag_r1_frac/cl_imag_r1_plus:.5f}")
    print()
    print("  REAL quadratic fields:")
    print(f"    Prob(rank_3 = 0): observed = {obs_real_r0_frac:.5f}, C-L = {cl_real_r0:.5f}, ratio = {obs_real_r0_frac/cl_real_r0:.5f}")
    print(f"    Prob(rank_3 >= 1): observed = {obs_real_r1_frac:.5f}, C-L = {cl_real_r1_plus:.5f}, ratio = {obs_real_r1_frac/cl_real_r1_plus:.5f}")
    print()

    # ── Connection to BST p=3 anomaly ──
    print("─" * 50)
    print("BST p=3 ANOMALY INTERPRETATION")
    print("─" * 50)
    print()
    print("  Scholz reflection couples the 3-part of class groups between")
    print("  real and imaginary quadratic fields. This constraint does NOT")
    print("  exist for p=2,5,7 — making the p=3 case structurally different.")
    print()
    if paired > 0:
        eq_frac = scholz_tight_lower / paired
        up_frac = scholz_tight_upper / paired
        print(f"  Of {paired:,} Scholz pairs:")
        print(f"    {eq_frac:.1%} have equal 3-ranks (coupling is tight)")
        print(f"    {up_frac:.1%} differ by exactly 1")
        if violations > 0:
            print(f"    {violations} violations detected — investigate!")
        else:
            print(f"    0 violations — theorem holds perfectly")
    print()

    # ── Conditional 3-rank given pairing ──
    print("─" * 50)
    print("CONDITIONAL: 3-rank of paired vs all fields")
    print("─" * 50)

    # Collect 3-ranks of paired real fields vs all real fields
    paired_real_r3 = Counter()
    paired_imag_r3 = Counter()
    for disc_abs_real, (cn_r, cg_r, r3_r) in real_fields.items():
        conj_disc = fundamental_discriminant_of_neg3d(disc_abs_real)
        if conj_disc in imag_fields:
            paired_real_r3[r3_r] += 1
            paired_imag_r3[imag_fields[conj_disc][2]] += 1

    total_paired_real = sum(paired_real_r3.values())
    print(f"  Paired real fields: {total_paired_real:,}")
    print(f"  All real fields:    {total_real:,}")
    print()
    print(f"  {'r3':>4}  {'paired_real':>12}  {'all_real':>12}  {'paired_frac':>12}  {'all_frac':>12}")
    for r in range(max_rank + 1):
        pr = paired_real_r3.get(r, 0)
        ar = real_3rank_dist.get(r, 0)
        pf = pr / total_paired_real if total_paired_real > 0 else 0
        af = ar / total_real if total_real > 0 else 0
        print(f"  {r:>4}  {pr:>12,}  {ar:>12,}  {pf:>12.5f}  {af:>12.5f}")

    print()
    elapsed = time.time() - t0
    print(f"Total runtime: {elapsed:.1f}s")
    print("=" * 70)


if __name__ == '__main__':
    main()
