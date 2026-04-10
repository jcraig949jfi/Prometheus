"""
OSC-1: Generalize the Oscillation Shadow Law

Tests whether bad primes create standing-wave autocorrelation signatures
in a_p sequences of weight-2 dim-1 modular forms.

Hypothesis: the lag k* of maximum negative autocorrelation is determined
by the bad prime structure of the conductor.
"""

import json
import numpy as np
from collections import defaultdict
from sympy import factorint, isprime, primerange
import duckdb
import os

# ── paths ──────────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "..", "data", "charon.duckdb")
OUT_PATH = os.path.join(HERE, "oscillation_shadow_results.json")

# ── primes up to 1000 ─────────────────────────────────────────────────
PRIMES = list(primerange(2, 1000))
PRIME_SET = set(PRIMES)
PRIME_INDEX = {p: i for i, p in enumerate(PRIMES)}  # prime -> 0-based index


def is_squarefree(n):
    """Check if n is squarefree."""
    f = factorint(n)
    return all(e == 1 for e in f.values())


def bad_primes(level):
    """Return sorted list of prime divisors of level."""
    return sorted(factorint(level).keys())


def extract_ap_good(traces, level):
    """
    Extract a_p values at good primes from the traces array.
    traces[i] = a_{i+1}, so traces[p-1] = a_p for prime p.
    We skip primes dividing the level (bad primes).
    """
    bads = set(bad_primes(level))
    ap_good = []
    for p in PRIMES:
        if p in bads:
            continue
        idx = p - 1  # traces is 0-indexed, traces[0] = a_1
        if idx < len(traces):
            ap_good.append(traces[idx])
    return np.array(ap_good, dtype=float)


def autocorrelation(x, max_lag=15):
    """Compute autocorrelation for lags 1..max_lag."""
    x = x - x.mean()
    n = len(x)
    var = np.sum(x**2)
    if var == 0:
        return np.zeros(max_lag)
    ac = []
    for lag in range(1, max_lag + 1):
        if lag >= n:
            ac.append(0.0)
        else:
            ac.append(np.sum(x[:n-lag] * x[lag:]) / var)
    return np.array(ac)


def gap_pattern_from_bad_primes(level):
    """
    Return the pattern of gaps in the prime sequence caused by bad primes.
    For each bad prime p, which index in the prime list does it occupy?
    This gives the periodicity of the "holes" in the a_p sequence.
    """
    bads = set(bad_primes(level))
    # positions of bad primes in the full prime list
    positions = []
    for p in bads:
        if p in PRIME_INDEX:
            positions.append(PRIME_INDEX[p])
    return sorted(positions)


def analyze_form(label, level, traces, max_lag=15):
    """Analyze a single form. Return dict with results."""
    ap = extract_ap_good(traces, level)
    if len(ap) < max_lag + 5:
        return None

    ac = autocorrelation(ap, max_lag)
    k_star = int(np.argmin(ac)) + 1  # lag of max negative AC (1-indexed)
    ac_star = float(ac[k_star - 1])

    bads = bad_primes(level)
    gap_positions = gap_pattern_from_bad_primes(level)

    return {
        "label": label,
        "level": level,
        "bad_primes": bads,
        "n_bad": len(bads),
        "k_star": k_star,
        "ac_star": round(ac_star, 6),
        "ac_profile": [round(float(a), 6) for a in ac],
        "gap_positions": gap_positions,
        "n_good_primes": len(ap),
    }


def main():
    print("OSC-1: Oscillation Shadow Law")
    print("=" * 60)

    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE dim = 1 AND weight = 2 AND traces IS NOT NULL
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"Loaded {len(rows)} dim-1 weight-2 forms")

    # ── Classify by squarefree vs non-squarefree ──
    results_sqfree = []
    results_nonsqfree = []

    for label, level, traces in rows:
        if traces is None or len(traces) < 20:
            continue
        res = analyze_form(label, level, traces)
        if res is None:
            continue
        if is_squarefree(level):
            results_sqfree.append(res)
        else:
            results_nonsqfree.append(res)

    print(f"Squarefree forms: {len(results_sqfree)}")
    print(f"Non-squarefree forms: {len(results_nonsqfree)}")

    # ── Analysis 1: k* distribution by number of bad primes (squarefree) ──
    print("\n" + "=" * 60)
    print("SQUAREFREE CONDUCTORS: k* distribution by #bad_primes")
    print("=" * 60)

    by_nbad = defaultdict(list)
    for r in results_sqfree:
        by_nbad[r["n_bad"]].append(r)

    kstar_by_nbad = {}
    for nbad in sorted(by_nbad.keys()):
        forms = by_nbad[nbad]
        kstars = [f["k_star"] for f in forms]
        ac_stars = [f["ac_star"] for f in forms]
        kstar_counts = defaultdict(int)
        for k in kstars:
            kstar_counts[k] += 1
        top_k = sorted(kstar_counts.items(), key=lambda x: -x[1])[:5]

        print(f"\n  n_bad={nbad}: {len(forms)} forms")
        print(f"    k* distribution (top 5): {top_k}")
        print(f"    mean AC(k*) = {np.mean(ac_stars):.4f}")
        print(f"    median k* = {np.median(kstars):.1f}")

        kstar_by_nbad[nbad] = {
            "count": len(forms),
            "kstar_distribution": dict(kstar_counts),
            "mean_ac_star": round(float(np.mean(ac_stars)), 6),
            "median_kstar": round(float(np.median(kstars)), 1),
        }

    # ── Analysis 2: Does k* predict bad primes? ──
    # For squarefree level = p*q, check if k* relates to p, q, or pq
    print("\n" + "=" * 60)
    print("HYPOTHESIS TEST: k* vs bad prime structure (squarefree)")
    print("=" * 60)

    # Group by specific bad prime sets
    by_badset = defaultdict(list)
    for r in results_sqfree:
        key = tuple(r["bad_primes"])
        by_badset[key].append(r)

    # For two-bad-prime case, test specific hypotheses
    two_bad = [(bps, forms) for bps, forms in by_badset.items() if len(bps) == 2]
    two_bad.sort(key=lambda x: x[0])

    print(f"\n  Two-bad-prime sets: {len(two_bad)}")
    formula_tests = []
    for bps, forms in two_bad[:20]:  # show first 20
        kstars = [f["k_star"] for f in forms]
        modal_k = max(set(kstars), key=kstars.count)
        p, q = bps
        # Test hypotheses
        gap_pos = forms[0]["gap_positions"]
        print(f"    bad=({p},{q}), N={len(forms)}, modal k*={modal_k}, "
              f"gap_pos={gap_pos}, AC(k*)={np.mean([f['ac_star'] for f in forms]):.4f}")
        formula_tests.append({
            "bad_primes": list(bps),
            "n_forms": len(forms),
            "modal_kstar": modal_k,
            "gap_positions": gap_pos,
        })

    # ── Analysis 3: Gap position hypothesis ──
    # The key insight: bad primes create gaps at specific positions in the
    # prime-indexed sequence. The autocorrelation at lag k reflects the
    # density of "aligned" pairs of good primes separated by k positions.
    print("\n" + "=" * 60)
    print("GAP POSITION ANALYSIS")
    print("=" * 60)

    # For each form, compute the "gap signature" - the positions where
    # bad primes sit in the prime list
    # Hypothesis: k* = smallest gap position + 1, or related to gap spacing

    # More precise: compute the expected AC structure from gaps alone
    def expected_ac_from_gaps(level, n_primes=168, max_lag=15):
        """
        If a_p were iid with some bad-prime gaps removed, what would the
        AC look like? Under null (iid good primes), AC should be ~0 everywhere.
        The standing wave comes from ARITHMETIC structure, not gaps.

        But let's test: maybe Sato-Tate + gaps = standing wave?
        Actually, for truly iid sequences with gaps removed, AC = 0.
        The signal must be arithmetic.
        """
        pass  # We'll test this empirically with shuffled controls

    # Shuffled null test: for each form, shuffle a_p and recompute AC
    print("\n  Null test: shuffled a_p sequences (100 forms, 50 shuffles each)")
    rng = np.random.RandomState(42)
    null_ac_magnitudes = []
    real_ac_magnitudes = []

    sample_forms = results_sqfree[:100]
    for r in sample_forms:
        real_ac_magnitudes.append(abs(r["ac_star"]))

    # Recompute with shuffled data
    con = duckdb.connect(DB_PATH, read_only=True)
    sample_labels = [r["label"] for r in sample_forms]
    placeholders = ",".join(f"'{l}'" for l in sample_labels)
    shuffle_rows = con.execute(f"""
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE lmfdb_label IN ({placeholders})
    """).fetchall()
    con.close()

    shuffle_data = {r[0]: (r[1], r[2]) for r in shuffle_rows}
    null_kstars = []
    for r in sample_forms:
        level, traces = shuffle_data[r["label"]]
        ap = extract_ap_good(traces, level)
        for _ in range(50):
            shuffled = rng.permutation(ap)
            ac = autocorrelation(shuffled, 15)
            null_ac_magnitudes.append(abs(float(ac[np.argmin(ac)])))
            null_kstars.append(int(np.argmin(ac)) + 1)

    print(f"    Real |AC(k*)| mean: {np.mean(real_ac_magnitudes):.4f}")
    print(f"    Null |AC(k*)| mean: {np.mean(null_ac_magnitudes):.4f}")
    print(f"    Null k* distribution: uniform? {defaultdict(int)}")
    null_k_counts = defaultdict(int)
    for k in null_kstars:
        null_k_counts[k] += 1
    print(f"    Null k* counts: {dict(sorted(null_k_counts.items()))}")

    # ── Analysis 4: The actual formula search ──
    print("\n" + "=" * 60)
    print("FORMULA SEARCH: k* as function of bad primes")
    print("=" * 60)

    # For single-bad-prime (level = p), group by p and check k*
    one_bad = [(bps, forms) for bps, forms in by_badset.items() if len(bps) == 1]
    one_bad.sort(key=lambda x: x[0])

    print("\n  Single bad prime (level = p):")
    one_bad_results = []
    for bps, forms in one_bad[:30]:
        p = bps[0]
        kstars = [f["k_star"] for f in forms]
        modal_k = max(set(kstars), key=kstars.count)
        mean_ac = np.mean([f["ac_star"] for f in forms])
        p_idx = PRIME_INDEX.get(p, -1)
        print(f"    p={p} (idx={p_idx}): N={len(forms)}, modal k*={modal_k}, "
              f"mean AC={mean_ac:.4f}")
        one_bad_results.append({
            "p": p, "p_index": p_idx, "n_forms": len(forms),
            "modal_kstar": modal_k, "mean_ac": round(float(mean_ac), 6)
        })

    # Three bad primes
    three_bad = [(bps, forms) for bps, forms in by_badset.items() if len(bps) == 3]
    three_bad.sort(key=lambda x: x[0])
    print(f"\n  Three bad primes: {len(three_bad)} sets")
    three_bad_results = []
    for bps, forms in three_bad[:15]:
        kstars = [f["k_star"] for f in forms]
        modal_k = max(set(kstars), key=kstars.count)
        mean_ac = np.mean([f["ac_star"] for f in forms])
        gap_pos = forms[0]["gap_positions"]
        print(f"    bad={bps}: N={len(forms)}, modal k*={modal_k}, gaps={gap_pos}, "
              f"AC={mean_ac:.4f}")
        three_bad_results.append({
            "bad_primes": list(bps), "n_forms": len(forms),
            "modal_kstar": modal_k, "gap_positions": gap_pos,
            "mean_ac": round(float(mean_ac), 6)
        })

    # ── Analysis 5: Train/test split to test any found formula ──
    print("\n" + "=" * 60)
    print("PREDICTION TEST (80/20 split)")
    print("=" * 60)

    rng2 = np.random.RandomState(123)
    indices = rng2.permutation(len(results_sqfree))
    split = int(0.8 * len(indices))
    train_idx = indices[:split]
    test_idx = indices[split:]

    train = [results_sqfree[i] for i in train_idx]
    test = [results_sqfree[i] for i in test_idx]

    # Learn the modal k* for each bad-prime-set from training data
    train_modal = {}
    by_badset_train = defaultdict(list)
    for r in train:
        key = tuple(r["bad_primes"])
        by_badset_train[key].append(r["k_star"])
    for key, kstars in by_badset_train.items():
        train_modal[key] = max(set(kstars), key=kstars.count)

    # Also learn modal k* by number of bad primes (fallback)
    by_nbad_train = defaultdict(list)
    for r in train:
        by_nbad_train[r["n_bad"]].append(r["k_star"])
    nbad_modal = {}
    for nbad, kstars in by_nbad_train.items():
        nbad_modal[nbad] = max(set(kstars), key=kstars.count)

    # Test: predict k* for test forms
    exact_match = 0
    fallback_match = 0
    total = 0
    for r in test:
        key = tuple(r["bad_primes"])
        actual = r["k_star"]
        total += 1
        if key in train_modal:
            pred = train_modal[key]
            if pred == actual:
                exact_match += 1
        else:
            pred = nbad_modal.get(r["n_bad"], 1)
            if pred == actual:
                fallback_match += 1

    print(f"  Train: {len(train)}, Test: {len(test)}")
    print(f"  Exact bad-prime-set match: {exact_match}/{total} = {exact_match/total:.3f}")
    print(f"  With n_bad fallback: {(exact_match+fallback_match)}/{total} = {(exact_match+fallback_match)/total:.3f}")

    # ── Analysis 6: Non-squarefree comparison ──
    print("\n" + "=" * 60)
    print("NON-SQUAREFREE CONDUCTORS")
    print("=" * 60)

    by_nbad_nonsq = defaultdict(list)
    for r in results_nonsqfree:
        by_nbad_nonsq[r["n_bad"]].append(r)

    nonsqfree_summary = {}
    for nbad in sorted(by_nbad_nonsq.keys()):
        forms = by_nbad_nonsq[nbad]
        kstars = [f["k_star"] for f in forms]
        ac_stars = [f["ac_star"] for f in forms]
        kstar_counts = defaultdict(int)
        for k in kstars:
            kstar_counts[k] += 1
        top_k = sorted(kstar_counts.items(), key=lambda x: -x[1])[:5]
        print(f"  n_bad={nbad}: {len(forms)} forms, top k*={top_k}, "
              f"mean AC={np.mean(ac_stars):.4f}")
        nonsqfree_summary[str(nbad)] = {
            "count": len(forms),
            "kstar_distribution": {str(k): v for k, v in kstar_counts.items()},
            "mean_ac_star": round(float(np.mean(ac_stars)), 6),
        }

    # Compare squarefree vs non-squarefree for same bad prime sets
    print("\n  Comparing squarefree vs non-squarefree (same bad primes):")
    nonsq_by_badset = defaultdict(list)
    for r in results_nonsqfree:
        key = tuple(r["bad_primes"])
        nonsq_by_badset[key].append(r)

    comparison_results = []
    compared = 0
    for key in sorted(by_badset.keys()):
        if key in nonsq_by_badset and len(by_badset[key]) >= 3 and len(nonsq_by_badset[key]) >= 3:
            sq_kstars = [f["k_star"] for f in by_badset[key]]
            nsq_kstars = [f["k_star"] for f in nonsq_by_badset[key]]
            sq_modal = max(set(sq_kstars), key=sq_kstars.count)
            nsq_modal = max(set(nsq_kstars), key=nsq_kstars.count)
            sq_ac = np.mean([f["ac_star"] for f in by_badset[key]])
            nsq_ac = np.mean([f["ac_star"] for f in nonsq_by_badset[key]])
            if compared < 15:
                print(f"    bad={key}: sqfree modal k*={sq_modal} (AC={sq_ac:.4f}), "
                      f"non-sqfree modal k*={nsq_modal} (AC={nsq_ac:.4f})")
            comparison_results.append({
                "bad_primes": list(key),
                "sqfree_modal_kstar": sq_modal,
                "nonsqfree_modal_kstar": nsq_modal,
                "sqfree_mean_ac": round(float(sq_ac), 6),
                "nonsqfree_mean_ac": round(float(nsq_ac), 6),
                "same_kstar": bool(sq_modal == nsq_modal),
            })
            compared += 1

    same_count = sum(1 for c in comparison_results if c["same_kstar"])
    print(f"\n  Same modal k* in {same_count}/{len(comparison_results)} comparisons "
          f"({same_count/max(len(comparison_results),1)*100:.1f}%)")

    # ── Analysis 7: AC magnitude vs conductor size ──
    print("\n" + "=" * 60)
    print("AC MAGNITUDE vs CONDUCTOR SIZE")
    print("=" * 60)

    for nbad in [1, 2, 3]:
        forms = by_nbad.get(nbad, [])
        if not forms:
            continue
        levels = np.array([f["level"] for f in forms])
        acs = np.array([abs(f["ac_star"]) for f in forms])
        # Bin by level quartiles
        quartiles = np.percentile(levels, [25, 50, 75])
        bins = [0] + list(quartiles) + [10000]
        for i in range(4):
            mask = (levels >= bins[i]) & (levels < bins[i+1])
            if mask.sum() > 0:
                print(f"  n_bad={nbad}, level in [{bins[i]:.0f},{bins[i+1]:.0f}): "
                      f"N={mask.sum()}, mean |AC|={acs[mask].mean():.4f}")

    # ── Compile results ──────────────────────────────────────────────
    output = {
        "summary": {
            "n_forms_total": len(rows),
            "n_squarefree": len(results_sqfree),
            "n_nonsquarefree": len(results_nonsqfree),
        },
        "null_test": {
            "real_mean_abs_ac_star": round(float(np.mean(real_ac_magnitudes)), 6),
            "null_mean_abs_ac_star": round(float(np.mean(null_ac_magnitudes)), 6),
            "null_kstar_uniform": {str(k): v for k, v in sorted(null_k_counts.items())},
        },
        "squarefree_by_nbad": {str(k): v for k, v in kstar_by_nbad.items()},
        "single_bad_prime": one_bad_results,
        "two_bad_primes_sample": formula_tests,
        "three_bad_primes_sample": three_bad_results,
        "prediction_test": {
            "train_size": len(train),
            "test_size": len(test),
            "exact_match_rate": round(exact_match / total, 4),
            "with_fallback_rate": round((exact_match + fallback_match) / total, 4),
        },
        "nonsquarefree_summary": nonsqfree_summary,
        "sqfree_vs_nonsqfree_comparison": comparison_results[:20],
        "sqfree_vs_nonsqfree_agreement": f"{same_count}/{len(comparison_results)}",
    }

    # ── Physical interpretation ──
    # Check: is AC(k*) significantly stronger than null?
    real_mean = np.mean(real_ac_magnitudes)
    null_mean = np.mean(null_ac_magnitudes)
    null_std = np.std(null_ac_magnitudes)
    z_score = (real_mean - null_mean) / null_std if null_std > 0 else 0

    # Is k* non-uniform in real data?
    real_kstars_all = [r["k_star"] for r in results_sqfree]
    real_k_counts = defaultdict(int)
    for k in real_kstars_all:
        real_k_counts[k] += 1

    output["interpretation"] = {
        "ac_magnitude_z_score": round(float(z_score), 2),
        "ac_is_significant": bool(z_score > 3.0),
        "real_kstar_distribution": {str(k): v for k, v in sorted(real_k_counts.items())},
        "kstar_is_nonuniform": bool(max(real_k_counts.values()) > 2 * np.mean(list(real_k_counts.values()))),
    }

    # Final diagnosis
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    print(f"  AC magnitude z-score (real vs null): {z_score:.2f}")
    print(f"  k* distribution in real data: {dict(sorted(real_k_counts.items()))}")
    print(f"  k* distribution in null: {dict(sorted(null_k_counts.items()))}")

    if z_score < 3.0:
        verdict = ("NEGATIVE: The oscillation in 15.2.a.a is NOT universal. "
                    "AC magnitudes in real data are not significantly larger than "
                    "shuffled null. The lag-3 standing wave in 15.2.a.a is either "
                    "a local arithmetic feature or an artifact of small sample size.")
    elif not output["interpretation"]["kstar_is_nonuniform"]:
        verdict = ("WEAK: AC magnitudes are significant but k* is uniformly distributed. "
                    "Bad primes create AC suppression/enhancement but NOT at a predictable lag.")
    else:
        verdict = ("POSITIVE: Both AC magnitude and k* distribution are non-null. "
                    "Bad primes create standing waves at specific, predictable lags.")

    output["verdict"] = verdict
    print(f"\n  VERDICT: {verdict}")

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
