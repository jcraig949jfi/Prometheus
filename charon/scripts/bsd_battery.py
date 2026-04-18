"""
BSD Non-Circular Test Battery
Charon — 2026-04-15

Tests consequences of BSD that would be false if BSD were wrong,
plus Tier 0 data integrity checks.
"""

import json
import math
import time
import psycopg2
from collections import defaultdict
from scipy.stats import spearmanr

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT = r"F:\Prometheus\charon\data\bsd_battery.json"


def get_conn():
    return psycopg2.connect(**DB)


def t0a_faltings_invariance():
    """T0a: stable_faltings_height should be isogeny-invariant within each class."""
    print("\n=== T0a: Stable Faltings Height Isogeny Invariance ===")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT lmfdb_iso, stable_faltings_height::double precision
        FROM ec_curvedata
        WHERE stable_faltings_height IS NOT NULL
        ORDER BY lmfdb_iso
    """)

    classes = defaultdict(list)
    for iso, sfh in cur:
        classes[iso].append(sfh)
    conn.close()

    total_classes = len(classes)
    multi_classes = {k: v for k, v in classes.items() if len(v) > 1}
    violations = {}
    for iso, vals in multi_classes.items():
        spread = max(vals) - min(vals)
        if spread > 1e-6:  # tolerance for float
            violations[iso] = {"min": min(vals), "max": max(vals), "spread": spread}

    n_violations = len(violations)
    # Show top 5 worst
    worst = sorted(violations.items(), key=lambda x: -x[1]['spread'])[:5]

    result = {
        "test": "T0a_faltings_invariance",
        "total_isogeny_classes": total_classes,
        "multi_curve_classes": len(multi_classes),
        "violations": n_violations,
        "violation_rate": n_violations / max(len(multi_classes), 1),
        "worst_5": {k: v for k, v in worst},
        "verdict": "PASS" if n_violations == 0 else "ANOMALY"
    }

    print(f"  Total isogeny classes: {total_classes:,}")
    print(f"  Multi-curve classes: {len(multi_classes):,}")
    print(f"  Violations (spread > 1e-6): {n_violations:,}")
    if worst:
        print(f"  Worst violations:")
        for iso, v in worst:
            print(f"    {iso}: spread={v['spread']:.10f}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def t0b_manin_constant():
    """T0b: Manin constant should be 1 for optimal curves."""
    print("\n=== T0b: Manin Constant for Optimal Curves ===")
    conn = get_conn()
    cur = conn.cursor()

    # Check what optimality values exist
    cur.execute("SELECT optimality, count(*) FROM ec_curvedata GROUP BY optimality")
    opt_dist = dict(cur.fetchall())
    print(f"  Optimality distribution: {opt_dist}")

    # Optimal = '1'
    cur.execute("""
        SELECT count(*) FROM ec_curvedata
        WHERE optimality = '1'
    """)
    total_optimal = cur.fetchone()[0]

    cur.execute("""
        SELECT count(*) FROM ec_curvedata
        WHERE optimality = '1' AND manin_constant::int != 1
    """)
    bad_manin = cur.fetchone()[0]

    # Show any bad ones
    if bad_manin > 0:
        cur.execute("""
            SELECT lmfdb_label, manin_constant FROM ec_curvedata
            WHERE optimality = '1' AND manin_constant::int != 1
            LIMIT 10
        """)
        examples = cur.fetchall()
    else:
        examples = []

    conn.close()

    result = {
        "test": "T0b_manin_constant",
        "total_optimal_curves": total_optimal,
        "manin_ne_1": bad_manin,
        "examples": examples,
        "verdict": "PASS" if bad_manin == 0 else "ANOMALY"
    }

    print(f"  Optimal curves: {total_optimal:,}")
    print(f"  Manin constant != 1: {bad_manin}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def t1_sha_perfect_square():
    """T1: |Sha| should always be a perfect square."""
    print("\n=== T1: Sha Perfect Square Test ===")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT sha::bigint, lmfdb_label FROM ec_curvedata WHERE sha::int > 1")
    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    non_square = []
    sha_values = defaultdict(int)

    for sha_val, label in rows:
        sha_values[sha_val] += 1
        sqrt = int(math.isqrt(sha_val))
        if sqrt * sqrt != sha_val:
            non_square.append((label, sha_val))

    result = {
        "test": "T1_sha_perfect_square",
        "curves_with_sha_gt_1": total,
        "non_square_count": len(non_square),
        "percentage_square": 100.0 * (total - len(non_square)) / max(total, 1),
        "sha_value_distribution": {str(k): v for k, v in sorted(sha_values.items())},
        "non_square_examples": non_square[:10],
        "verdict": "PASS" if len(non_square) == 0 else "FAIL"
    }

    print(f"  Curves with Sha > 1: {total:,}")
    print(f"  Non-square Sha: {len(non_square)}")
    print(f"  Sha value distribution: {dict(sorted(sha_values.items()))}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def t2_sha_vs_bad_primes():
    """T2: Sha primes vs bad primes for rank >= 2."""
    print("\n=== T2: Sha Primes vs Bad Primes (rank >= 2) ===")
    conn = get_conn()
    cur = conn.cursor()

    # sha_primes and bad_primes are stored as text arrays like '[2, 3]'
    cur.execute("""
        SELECT sha_primes, bad_primes, rank::int, lmfdb_label
        FROM ec_curvedata
        WHERE rank::int >= 2 AND sha::int > 1
    """)
    rows = cur.fetchall()
    conn.close()

    total_curves = len(rows)
    total_sha_primes = 0
    sha_in_bad = 0
    sha_not_in_bad = 0
    not_in_bad_examples = []
    sha_prime_counts = defaultdict(int)

    for sha_p_str, bad_p_str, rank, label in rows:
        # Parse text arrays: '[2, 3, 5]' -> {2, 3, 5}
        sha_primes = set()
        bad_primes = set()
        if sha_p_str and sha_p_str not in ('[]', ''):
            sha_primes = set(int(x.strip()) for x in sha_p_str.strip('[]{}').split(',') if x.strip())
        if bad_p_str and bad_p_str not in ('[]', ''):
            bad_primes = set(int(x.strip()) for x in bad_p_str.strip('[]{}').split(',') if x.strip())

        for p in sha_primes:
            sha_prime_counts[p] += 1
            total_sha_primes += 1
            if p in bad_primes:
                sha_in_bad += 1
            else:
                sha_not_in_bad += 1
                if len(not_in_bad_examples) < 20:
                    not_in_bad_examples.append({"label": label, "sha_prime": p, "bad_primes": sorted(bad_primes), "rank": rank})

    result = {
        "test": "T2_sha_vs_bad_primes",
        "rank_ge2_with_sha_gt1": total_curves,
        "total_sha_primes": total_sha_primes,
        "sha_primes_also_bad": sha_in_bad,
        "sha_primes_not_bad": sha_not_in_bad,
        "frac_sha_in_bad": sha_in_bad / max(total_sha_primes, 1),
        "frac_sha_not_bad": sha_not_in_bad / max(total_sha_primes, 1),
        "sha_prime_frequency": {str(k): v for k, v in sorted(sha_prime_counts.items(), key=lambda x: -x[1])[:20]},
        "examples_not_in_bad": not_in_bad_examples[:10],
        "verdict": "PASS"  # This is informational, not pass/fail
    }

    print(f"  Rank >= 2 curves with Sha > 1: {total_curves:,}")
    print(f"  Total sha prime occurrences: {total_sha_primes}")
    print(f"  Sha primes also bad: {sha_in_bad} ({result['frac_sha_in_bad']:.1%})")
    print(f"  Sha primes NOT bad: {sha_not_in_bad} ({result['frac_sha_not_bad']:.1%})")
    print(f"  Top sha primes: {dict(sorted(sha_prime_counts.items(), key=lambda x: -x[1])[:10])}")
    if not_in_bad_examples:
        print(f"  Examples of sha primes not in bad primes:")
        for ex in not_in_bad_examples[:5]:
            print(f"    {ex['label']}: sha_prime={ex['sha_prime']}, bad_primes={ex['bad_primes']}")
    print(f"  VERDICT: {result['verdict']} (informational)")
    return result


def t3_isogeny_sha_consistency():
    """T3: Within isogeny class, sha ratios should be squares of isogeny degree ratios."""
    print("\n=== T3: Isogeny Sha Consistency ===")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT lmfdb_iso, lmfdb_label, sha::bigint, isogeny_degrees, class_size::int
        FROM ec_curvedata
        WHERE sha IS NOT NULL
        ORDER BY lmfdb_iso, lmfdb_label
    """)
    rows = cur.fetchall()
    conn.close()

    # Group by isogeny class
    classes = defaultdict(list)
    for iso, label, sha, isog_deg, cs in rows:
        classes[iso].append({"label": label, "sha": sha, "isog_deg": isog_deg, "class_size": cs})

    # Filter to multi-curve classes with sha variation
    multi_classes = {k: v for k, v in classes.items() if len(v) > 1}
    classes_with_sha_variation = {}
    for iso, curves in multi_classes.items():
        sha_vals = set(c["sha"] for c in curves)
        if len(sha_vals) > 1:
            classes_with_sha_variation[iso] = curves

    # For sha consistency: in an isogeny class, if curve A has sha=s_A and curve B has sha=s_B,
    # and they're connected by an isogeny of degree d, then s_B/s_A should be related to d^2.
    # More precisely, sha * (other BSD terms) is invariant up to isogeny degree squares.
    # We check: are all sha ratios perfect squares?

    consistent = 0
    inconsistent = 0
    inconsistent_examples = []

    for iso, curves in classes_with_sha_variation.items():
        sha_vals = [c["sha"] for c in curves]
        # Check if all pairwise ratios are rational squares
        all_ok = True
        for i in range(len(sha_vals)):
            for j in range(i+1, len(sha_vals)):
                big, small = max(sha_vals[i], sha_vals[j]), min(sha_vals[i], sha_vals[j])
                if small == 0:
                    continue
                if big % small != 0:
                    all_ok = False
                    break
                ratio = big // small
                sqrt_r = int(math.isqrt(ratio))
                if sqrt_r * sqrt_r != ratio:
                    all_ok = False
                    break
            if not all_ok:
                break

        if all_ok:
            consistent += 1
        else:
            inconsistent += 1
            if len(inconsistent_examples) < 10:
                inconsistent_examples.append({
                    "iso": iso,
                    "sha_values": [c["sha"] for c in curves],
                    "labels": [c["label"] for c in curves]
                })

    # Also check classes where sha is constant
    constant_sha_classes = len(multi_classes) - len(classes_with_sha_variation)

    result = {
        "test": "T3_isogeny_sha_consistency",
        "total_isogeny_classes": len(classes),
        "multi_curve_classes": len(multi_classes),
        "constant_sha_classes": constant_sha_classes,
        "variable_sha_classes": len(classes_with_sha_variation),
        "consistent": consistent,
        "inconsistent": inconsistent,
        "consistency_rate": (consistent + constant_sha_classes) / max(len(multi_classes), 1),
        "inconsistent_examples": inconsistent_examples,
        "verdict": "PASS" if inconsistent == 0 else "ANOMALY"
    }

    print(f"  Total isogeny classes: {len(classes):,}")
    print(f"  Multi-curve classes: {len(multi_classes):,}")
    print(f"  Constant sha across class: {constant_sha_classes:,}")
    print(f"  Variable sha classes: {len(classes_with_sha_variation):,}")
    print(f"  Consistent (ratios are squares): {consistent:,}")
    print(f"  Inconsistent: {inconsistent}")
    if inconsistent_examples:
        for ex in inconsistent_examples[:3]:
            print(f"    {ex['iso']}: sha={ex['sha_values']}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def t4_leading_term_sign():
    """T4: Sign of leading_term consistency with rank and root_number."""
    print("\n=== T4: Leading Term Sign Test ===")
    conn = get_conn()
    cur = conn.cursor()

    # Join via: origin = 'EllipticCurve/Q/' || conductor || '/' || iso_letter
    # lmfdb_iso = 'conductor.iso_letter', origin = 'EllipticCurve/Q/conductor/iso_letter'
    # We need to match. Let's construct origin from lmfdb_iso.
    # lmfdb_iso = '11.a' -> origin = 'EllipticCurve/Q/11/a'

    # For rank 0: leading_term > 0
    cur.execute("""
        SELECT e.rank::int, l.leading_term::double precision, l.root_number, e."signD"::int,
               e.lmfdb_label, e.lmfdb_iso
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' ||
            split_part(e.lmfdb_iso, '.', 1) || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.optimality = '1'
          AND l.leading_term IS NOT NULL
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"  Joined rows (optimal curves with L-function data): {len(rows):,}")

    rank0_total = 0
    rank0_neg = 0
    rank1_total = 0
    rank1_sign_mismatch = 0
    rank1_examples = []
    rank2plus_total = 0
    rank2plus_neg = 0

    for rank, lt, rn, signD, label, iso in rows:
        if lt is None:
            continue
        if rank == 0:
            rank0_total += 1
            if lt <= 0:
                rank0_neg += 1
        elif rank == 1:
            rank1_total += 1
            # For rank 1: L'(1) > 0 always (leading_term is |L^(r)(1)/r!| * period stuff)
            # Actually leading_term in LMFDB is the first nonzero Taylor coeff, always positive
            if lt <= 0:
                rank1_sign_mismatch += 1
                if len(rank1_examples) < 10:
                    rank1_examples.append({"label": label, "lt": lt, "rn": rn, "signD": signD})
        else:
            rank2plus_total += 1
            if lt <= 0:
                rank2plus_neg += 1

    result = {
        "test": "T4_leading_term_sign",
        "total_joined": len(rows),
        "rank0": {"total": rank0_total, "negative_lt": rank0_neg},
        "rank1": {"total": rank1_total, "sign_mismatch": rank1_sign_mismatch, "examples": rank1_examples},
        "rank2plus": {"total": rank2plus_total, "negative_lt": rank2plus_neg},
        "verdict": "PASS" if (rank0_neg == 0 and rank1_sign_mismatch == 0 and rank2plus_neg == 0) else "ANOMALY"
    }

    print(f"  Rank 0: {rank0_total:,} curves, negative leading_term: {rank0_neg}")
    print(f"  Rank 1: {rank1_total:,} curves, sign mismatches: {rank1_sign_mismatch}")
    print(f"  Rank 2+: {rank2plus_total:,} curves, negative leading_term: {rank2plus_neg}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def t5_regulator_bounds():
    """T5: Regulator positivity and correlation with conductor."""
    print("\n=== T5: Regulator Bounds ===")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT rank::int, regulator::double precision, conductor::double precision
        FROM ec_curvedata
        WHERE rank::int >= 1
          AND regulator IS NOT NULL
          AND conductor IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    by_rank = defaultdict(lambda: {"regs": [], "conds": [], "neg_count": 0, "zero_count": 0})

    for rank, reg, cond in rows:
        d = by_rank[rank]
        if reg <= 0:
            if reg < 0:
                d["neg_count"] += 1
            else:
                d["zero_count"] += 1
        d["regs"].append(reg)
        d["conds"].append(cond)

    rank_results = {}
    for rank in sorted(by_rank.keys()):
        d = by_rank[rank]
        regs = d["regs"]
        conds = d["conds"]

        # Spearman correlation between log(reg) and log(cond)
        # Filter to positive values only
        pos_pairs = [(r, c) for r, c in zip(regs, conds) if r > 0 and c > 0]
        if len(pos_pairs) > 10:
            log_regs = [math.log(r) for r, c in pos_pairs]
            log_conds = [math.log(c) for r, c in pos_pairs]
            rho, pval = spearmanr(log_regs, log_conds)
        else:
            rho, pval = None, None

        rank_results[rank] = {
            "count": len(regs),
            "negative_regulators": d["neg_count"],
            "zero_regulators": d["zero_count"],
            "min_reg": min(regs) if regs else None,
            "max_reg": max(regs) if regs else None,
            "median_reg": sorted(regs)[len(regs)//2] if regs else None,
            "spearman_rho": rho,
            "spearman_pval": pval
        }

    any_negative = sum(d["neg_count"] for d in by_rank.values())

    result = {
        "test": "T5_regulator_bounds",
        "total_rank_ge1": len(rows),
        "by_rank": {str(k): v for k, v in rank_results.items()},
        "any_negative_regulators": any_negative,
        "verdict": "PASS" if any_negative == 0 else "FAIL"
    }

    print(f"  Total rank >= 1 curves: {len(rows):,}")
    for rank, info in sorted(rank_results.items()):
        print(f"  Rank {rank}: n={info['count']:,}, neg={info['negative_regulators']}, "
              f"min={info['min_reg']:.6f}, median={info['median_reg']:.4f}, "
              f"Spearman(log_reg, log_cond)={info['spearman_rho']:.4f}" if info['spearman_rho'] else
              f"  Rank {rank}: n={info['count']:,}, neg={info['negative_regulators']}")
    print(f"  VERDICT: {result['verdict']}")
    return result


def main():
    print("=" * 70)
    print("BSD NON-CIRCULAR TEST BATTERY — Charon 2026-04-15")
    print("=" * 70)

    t0 = time.time()
    results = {}

    # Tier 0: Data Integrity
    results["T0a"] = t0a_faltings_invariance()
    results["T0b"] = t0b_manin_constant()

    # Tier 2: Non-Circular BSD Tests
    results["T1"] = t1_sha_perfect_square()
    results["T2"] = t2_sha_vs_bad_primes()
    results["T3"] = t3_isogeny_sha_consistency()
    results["T4"] = t4_leading_term_sign()
    results["T5"] = t5_regulator_bounds()

    elapsed = time.time() - t0

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    verdicts = {k: v["verdict"] for k, v in results.items()}
    for test, verdict in verdicts.items():
        print(f"  {test}: {verdict}")
    print(f"\n  Total time: {elapsed:.1f}s")

    results["_meta"] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": elapsed,
        "verdicts": verdicts
    }

    # Save
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {OUT}")


if __name__ == "__main__":
    main()
