#!/usr/bin/env python3
"""
M7: Nonlinear Transformation Search — Break the Linear Ceiling
Tests nonlinear transforms (quadratic, product, convolution, logarithmic, modular)
between OEIS sequences and EC a_p sequences to find cross-domain bridges that
linear functors miss.
"""

import json
import math
import time
import random
import sys
from pathlib import Path
from collections import Counter

# ── paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[4]
OEIS_FILE = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
NEAR_MISS_FILE = Path(__file__).resolve().parent / "near_miss_results.json"
OUT_FILE = Path(__file__).resolve().parent / "nonlinear_transform_results.json"

# ── parameters ─────────────────────────────────────────────────────────
N_OEIS = 500
N_EC = 500
FINGERPRINT_PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
FINGERPRINT_LEN = 12          # terms used for fingerprinting
MATCH_THRESHOLD = 0.75        # fraction of fingerprint positions that must match
CONVOLUTION_DEPTH = 20
LOG_CONSTANTS = [1.0, 2.0, math.e, math.pi, 10.0]
MOD_VALUES = [3, 5, 7, 11]
SEED = 42


def load_oeis(n=N_OEIS, min_terms=30):
    """Load n OEIS sequences with at least min_terms terms."""
    seqs = {}
    with open(OEIS_FILE) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ,", 1)
            if len(parts) < 2:
                continue
            aid = parts[0].strip()
            terms_str = parts[1].rstrip(",\n").split(",")
            terms = []
            for t in terms_str:
                t = t.strip()
                if t == "" or t == " ":
                    continue
                try:
                    terms.append(int(t))
                except ValueError:
                    break
            if len(terms) >= min_terms:
                seqs[aid] = terms
    # Deterministic sample
    rng = random.Random(SEED)
    keys = sorted(seqs.keys())
    if len(keys) > n:
        keys = rng.sample(keys, n)
    return {k: seqs[k] for k in keys}


def load_ec_aplist(n=N_EC):
    """Load n EC a_p sequences from DuckDB."""
    import duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        "SELECT lmfdb_label, aplist FROM elliptic_curves "
        "WHERE aplist IS NOT NULL AND len(aplist) >= 15 "
        "ORDER BY conductor LIMIT ?",
        [n * 2],
    ).fetchall()
    con.close()
    rng = random.Random(SEED + 1)
    if len(rows) > n:
        rows = rng.sample(rows, n)
    return {label: list(ap) for label, ap in rows}


# ── fingerprint helpers ────────────────────────────────────────────────

def mod_fingerprint(seq, p, length=FINGERPRINT_LEN):
    """Return tuple of (seq[i] mod p) for first `length` terms."""
    return tuple(v % p for v in seq[:length])


def fingerprint_set(seq, length=FINGERPRINT_LEN):
    """Compute mod-p fingerprints for a sequence across all primes."""
    if len(seq) < length:
        return None
    return {p: mod_fingerprint(seq, p, length) for p in FINGERPRINT_PRIMES}


def fingerprint_match_rate(fp1, fp2):
    """Fraction of fingerprint primes where the fingerprints match."""
    if fp1 is None or fp2 is None:
        return 0.0
    matches = sum(1 for p in FINGERPRINT_PRIMES if fp1.get(p) == fp2.get(p))
    return matches / len(FINGERPRINT_PRIMES)


def partial_fingerprint_match(fp1, fp2):
    """Average fraction of positions matching per prime (softer match)."""
    if fp1 is None or fp2 is None:
        return 0.0
    scores = []
    for p in FINGERPRINT_PRIMES:
        a, b = fp1.get(p), fp2.get(p)
        if a is None or b is None:
            scores.append(0.0)
            continue
        n = min(len(a), len(b))
        if n == 0:
            scores.append(0.0)
            continue
        scores.append(sum(1 for i in range(n) if a[i] == b[i]) / n)
    return sum(scores) / len(scores)


# ── nonlinear transforms ──────────────────────────────────────────────

def transform_quadratic(seq):
    """a_n -> a_n^2"""
    return [v * v for v in seq]


def transform_product(seq):
    """a_n -> a_n * a_{n-1}"""
    return [seq[i] * seq[i - 1] for i in range(1, len(seq))]


def transform_convolution(seq, depth=CONVOLUTION_DEPTH):
    """b_n = sum_{k=1}^{n} a_k * a_{n-k} for n up to depth"""
    n = min(len(seq), depth)
    result = []
    for m in range(1, n):
        s = sum(seq[k] * seq[m - k] for k in range(1, m) if m - k < len(seq))
        result.append(s)
    return result


def transform_log(seq, C):
    """If all a_n > 0: round(log(a_n) * C)"""
    result = []
    for v in seq:
        if v <= 0:
            return None
        result.append(round(math.log(v) * C))
    return result


def transform_mod(seq, m):
    """a_n mod m"""
    return [v % m for v in seq]


def apply_transforms(seq):
    """Return dict of transform_name -> transformed sequence."""
    results = {}
    results["quadratic"] = transform_quadratic(seq)
    results["product"] = transform_product(seq)
    conv = transform_convolution(seq)
    if len(conv) >= FINGERPRINT_LEN:
        results["convolution"] = conv
    for C in LOG_CONSTANTS:
        lseq = transform_log(seq, C)
        if lseq is not None and len(lseq) >= FINGERPRINT_LEN:
            results[f"log_C={C:.2f}"] = lseq
    for m in MOD_VALUES:
        results[f"mod_{m}"] = transform_mod(seq, m)
    return results


# ── main search ───────────────────────────────────────────────────────

def search_cross_domain(oeis_seqs, ec_seqs):
    """Test nonlinear transforms on OEIS x EC pairs."""
    print(f"Cross-domain search: {len(oeis_seqs)} OEIS x {len(ec_seqs)} EC")

    # Pre-compute EC fingerprints (raw)
    ec_fps = {}
    for label, ap in ec_seqs.items():
        fp = fingerprint_set(ap)
        if fp:
            ec_fps[label] = fp

    # Pre-compute EC transformed fingerprints
    ec_transformed_fps = {}
    for label, ap in ec_seqs.items():
        transforms = apply_transforms(ap)
        ec_transformed_fps[label] = {}
        for tname, tseq in transforms.items():
            fp = fingerprint_set(tseq)
            if fp:
                ec_transformed_fps[label][tname] = fp

    matches = []
    baseline_scores = []
    transform_scores = {t: [] for t in [
        "quadratic", "product", "convolution",
        "log_C=1.00", "log_C=2.00", f"log_C={math.e:.2f}",
        f"log_C={math.pi:.2f}", "log_C=10.00",
        "mod_3", "mod_5", "mod_7", "mod_11"
    ]}

    total_pairs = 0
    for oi, (oid, oseq) in enumerate(oeis_seqs.items()):
        if oi % 100 == 0:
            print(f"  OEIS {oi}/{len(oeis_seqs)} ({len(matches)} matches so far)")

        oeis_fp = fingerprint_set(oseq)
        if oeis_fp is None:
            continue

        # Pre-compute OEIS transforms
        oeis_transforms = apply_transforms(oseq)
        oeis_transform_fps = {}
        for tname, tseq in oeis_transforms.items():
            fp = fingerprint_set(tseq)
            if fp:
                oeis_transform_fps[tname] = fp

        for label, ap in ec_seqs.items():
            ec_fp = ec_fps.get(label)
            if ec_fp is None:
                continue
            total_pairs += 1

            # Baseline: untransformed match
            base_rate = partial_fingerprint_match(oeis_fp, ec_fp)
            baseline_scores.append(base_rate)

            # Strategy 1: Transform OEIS, compare to raw EC
            for tname, tfp in oeis_transform_fps.items():
                rate = partial_fingerprint_match(tfp, ec_fp)
                if tname in transform_scores:
                    transform_scores[tname].append(rate)
                if rate >= MATCH_THRESHOLD:
                    matches.append({
                        "oeis_id": oid,
                        "ec_label": label,
                        "transform": f"oeis_{tname}",
                        "match_rate": round(rate, 4),
                        "baseline_rate": round(base_rate, 4),
                        "direction": "oeis_transformed->ec_raw",
                    })

            # Strategy 2: Transform EC, compare to raw OEIS
            for tname, tfp in ec_transformed_fps.get(label, {}).items():
                rate = partial_fingerprint_match(oeis_fp, tfp)
                if rate >= MATCH_THRESHOLD:
                    matches.append({
                        "oeis_id": oid,
                        "ec_label": label,
                        "transform": f"ec_{tname}",
                        "match_rate": round(rate, 4),
                        "baseline_rate": round(base_rate, 4),
                        "direction": "oeis_raw->ec_transformed",
                    })

            # Strategy 3: Transform both with same transform, compare
            for tname in oeis_transform_fps:
                tfp_o = oeis_transform_fps[tname]
                tfp_e = ec_transformed_fps.get(label, {}).get(tname)
                if tfp_e:
                    rate = partial_fingerprint_match(tfp_o, tfp_e)
                    if rate >= MATCH_THRESHOLD:
                        matches.append({
                            "oeis_id": oid,
                            "ec_label": label,
                            "transform": f"both_{tname}",
                            "match_rate": round(rate, 4),
                            "baseline_rate": round(base_rate, 4),
                            "direction": "both_transformed",
                        })

    avg_baseline = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
    transform_means = {}
    for tname, scores in transform_scores.items():
        if scores:
            transform_means[tname] = round(sum(scores) / len(scores), 6)

    return {
        "total_pairs_tested": total_pairs,
        "avg_baseline_match": round(avg_baseline, 6),
        "transform_avg_match": transform_means,
        "matches_above_threshold": len(matches),
        "threshold": MATCH_THRESHOLD,
        "top_matches": sorted(matches, key=lambda x: -x["match_rate"])[:50],
    }


def search_intra_oeis(oeis_seqs):
    """Test nonlinear transforms within OEIS (OEIS <-> OEIS)."""
    print(f"Intra-OEIS search: {len(oeis_seqs)} sequences")

    # Pre-compute raw fingerprints
    raw_fps = {}
    for oid, seq in oeis_seqs.items():
        fp = fingerprint_set(seq)
        if fp:
            raw_fps[oid] = fp

    # Pre-compute transformed fingerprints
    transformed_fps = {}
    for oid, seq in oeis_seqs.items():
        transforms = apply_transforms(seq)
        transformed_fps[oid] = {}
        for tname, tseq in transforms.items():
            fp = fingerprint_set(tseq)
            if fp:
                transformed_fps[oid][tname] = fp

    matches = []
    oid_list = sorted(oeis_seqs.keys())
    total_pairs = 0

    for i in range(len(oid_list)):
        if i % 100 == 0:
            print(f"  OEIS-OEIS {i}/{len(oid_list)} ({len(matches)} matches)")
        oid_a = oid_list[i]
        fp_a = raw_fps.get(oid_a)
        if fp_a is None:
            continue

        for j in range(i + 1, len(oid_list)):
            oid_b = oid_list[j]
            fp_b = raw_fps.get(oid_b)
            if fp_b is None:
                continue
            total_pairs += 1

            # Check: transform A, compare to raw B
            for tname, tfp in transformed_fps.get(oid_a, {}).items():
                rate = partial_fingerprint_match(tfp, fp_b)
                if rate >= MATCH_THRESHOLD:
                    matches.append({
                        "oeis_a": oid_a,
                        "oeis_b": oid_b,
                        "transform": tname,
                        "match_rate": round(rate, 4),
                        "direction": f"{oid_a}_transformed->{oid_b}_raw",
                    })

            # Check: transform B, compare to raw A
            for tname, tfp in transformed_fps.get(oid_b, {}).items():
                rate = partial_fingerprint_match(fp_a, tfp)
                if rate >= MATCH_THRESHOLD:
                    matches.append({
                        "oeis_a": oid_a,
                        "oeis_b": oid_b,
                        "transform": tname,
                        "match_rate": round(rate, 4),
                        "direction": f"{oid_a}_raw->{oid_b}_transformed",
                    })

    return {
        "total_pairs_tested": total_pairs,
        "matches_above_threshold": len(matches),
        "threshold": MATCH_THRESHOLD,
        "top_matches": sorted(matches, key=lambda x: -x["match_rate"])[:50],
    }


def probe_near_misses():
    """Apply the specific transform type identified in R3-1 to the 26 near-misses."""
    with open(NEAR_MISS_FILE) as f:
        data = json.load(f)

    probes = data.get("nonlinear_probes", {}).get("records", [])
    if not probes:
        return {"error": "No nonlinear probes found in near_miss_results.json"}

    results = []
    for probe in probes:
        best = probe["best_transform"]
        claim = probe["claim"]
        nl_matches = probe["nonlinear_matches"]

        # We can't directly test these claims (they're about distributions, not sequences),
        # but we can report what transforms were identified and whether the claim structure
        # suggests a testable nonlinear bridge.
        testable = False
        recovery_status = "untestable_distribution_claim"

        # Check if claim references specific sequences or numerical data
        claim_lower = claim.lower()
        has_numerical = any(kw in claim_lower for kw in [
            "a_p", "conductor", "determinant", "exponent", "discriminant",
            "coefficient", "eigenvalue", "trace"
        ])
        has_transform_keyword = any(kw in claim_lower for kw in [
            "modulo", "mod ", "logarithm", "log ", "squared", "quadratic",
            "product", "multiplicative"
        ])

        if has_numerical and has_transform_keyword:
            testable = True
            recovery_status = "potentially_recoverable"

        results.append({
            "claim_prefix": claim[:120],
            "best_transform": best,
            "nonlinear_matches": nl_matches,
            "testable": testable,
            "recovery_status": recovery_status,
        })

    # Summary
    transform_counts = Counter(r["best_transform"] for r in results)
    testable_count = sum(1 for r in results if r["testable"])

    return {
        "total_near_misses": len(results),
        "transform_distribution": dict(transform_counts),
        "testable_count": testable_count,
        "untestable_count": len(results) - testable_count,
        "recovery_rate": round(testable_count / len(results), 4) if results else 0,
        "records": results,
    }


def permutation_null(oeis_seqs, ec_seqs, n_shuffles=20):
    """Permutation null: shuffle EC labels, measure match rate distribution."""
    print(f"  Running permutation null ({n_shuffles} shuffles)...")
    rng = random.Random(SEED + 99)

    ec_labels = list(ec_seqs.keys())
    oeis_ids = list(oeis_seqs.keys())[:50]  # subsample for speed

    # Pre-compute fingerprints for subsample
    oeis_fps = {}
    for oid in oeis_ids:
        transforms = apply_transforms(oeis_seqs[oid])
        oeis_fps[oid] = {}
        for tname, tseq in transforms.items():
            fp = fingerprint_set(tseq)
            if fp:
                oeis_fps[oid][tname] = fp

    ec_fps_raw = {}
    for label in ec_labels:
        fp = fingerprint_set(ec_seqs[label])
        if fp:
            ec_fps_raw[label] = fp

    # Real match count
    def count_matches(oid_list, label_list):
        cnt = 0
        for oid in oid_list:
            for label in label_list:
                fp_ec = ec_fps_raw.get(label)
                if fp_ec is None:
                    continue
                for tname, tfp in oeis_fps.get(oid, {}).items():
                    rate = partial_fingerprint_match(tfp, fp_ec)
                    if rate >= MATCH_THRESHOLD:
                        cnt += 1
        return cnt

    real_count = count_matches(oeis_ids, ec_labels)

    # Shuffled counts
    null_counts = []
    for _ in range(n_shuffles):
        shuffled = ec_labels[:]
        rng.shuffle(shuffled)
        # Reassign EC data to shuffled labels
        null_counts.append(count_matches(oeis_ids, shuffled))

    null_mean = sum(null_counts) / len(null_counts) if null_counts else 0
    null_std = (sum((c - null_mean) ** 2 for c in null_counts) / len(null_counts)) ** 0.5 if null_counts else 1
    z_score = (real_count - null_mean) / null_std if null_std > 0 else 0

    return {
        "real_matches": real_count,
        "null_mean": round(null_mean, 2),
        "null_std": round(null_std, 2),
        "z_score": round(z_score, 2),
        "n_shuffles": n_shuffles,
        "subsample_oeis": len(oeis_ids),
        "significant": abs(z_score) > 3.0,
    }


def hub_analysis(matches):
    """Check if matches are dominated by a few 'hub' sequences."""
    ec_counts = Counter()
    oeis_counts = Counter()
    transform_counts = Counter()
    for m in matches:
        ec_counts[m.get("ec_label", "")] += 1
        oeis_counts[m.get("oeis_id", m.get("oeis_a", ""))] += 1
        transform_counts[m.get("transform", "")] += 1

    return {
        "top_ec_hubs": dict(ec_counts.most_common(10)),
        "top_oeis_hubs": dict(oeis_counts.most_common(10)),
        "transform_distribution": dict(transform_counts.most_common(15)),
        "unique_ec": len(ec_counts),
        "unique_oeis": len(oeis_counts),
        "total_matches": len(matches),
    }


def main():
    t0 = time.time()
    print("=" * 60)
    print("M7: Nonlinear Transformation Search")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading OEIS sequences...")
    oeis_seqs = load_oeis(N_OEIS)
    print(f"  Loaded {len(oeis_seqs)} OEIS sequences")

    print("\n[2/5] Loading EC a_p sequences...")
    ec_seqs = load_ec_aplist(N_EC)
    print(f"  Loaded {len(ec_seqs)} EC sequences")

    # Cross-domain search
    print("\n[3/5] Cross-domain OEIS x EC nonlinear search...")
    cross_results = search_cross_domain(oeis_seqs, ec_seqs)
    print(f"  Baseline avg match: {cross_results['avg_baseline_match']:.6f}")
    print(f"  Matches above {MATCH_THRESHOLD}: {cross_results['matches_above_threshold']}")
    for tname, avg in sorted(cross_results["transform_avg_match"].items()):
        delta = avg - cross_results["avg_baseline_match"]
        print(f"    {tname}: avg={avg:.6f} (delta={delta:+.6f})")

    # Intra-OEIS search
    print("\n[4/5] Intra-OEIS nonlinear search...")
    intra_results = search_intra_oeis(oeis_seqs)
    print(f"  Pairs tested: {intra_results['total_pairs_tested']}")
    print(f"  Matches above {MATCH_THRESHOLD}: {intra_results['matches_above_threshold']}")

    # Near-miss probes
    print("\n[5/5] Near-miss recovery probes...")
    near_miss_results = probe_near_misses()
    print(f"  Total probed: {near_miss_results['total_near_misses']}")
    print(f"  Transform distribution: {near_miss_results['transform_distribution']}")
    print(f"  Testable: {near_miss_results['testable_count']}")
    print(f"  Recovery rate: {near_miss_results['recovery_rate']}")

    # Permutation null test
    print("\n[6/7] Permutation null test...")
    null_results = permutation_null(oeis_seqs, ec_seqs)
    print(f"  Real matches (subsample): {null_results['real_matches']}")
    print(f"  Null mean: {null_results['null_mean']} +/- {null_results['null_std']}")
    print(f"  z-score: {null_results['z_score']}")
    print(f"  Significant: {null_results['significant']}")

    # Hub analysis
    print("\n[7/7] Hub analysis...")
    cross_hub = hub_analysis(cross_results.get("top_matches", []))
    intra_hub = hub_analysis(intra_results.get("top_matches", []))
    print(f"  Cross-domain: {cross_hub['unique_ec']} unique EC, {cross_hub['unique_oeis']} unique OEIS")
    print(f"  Cross transform dist: {cross_hub['transform_distribution']}")
    print(f"  Intra-OEIS: {intra_hub['unique_oeis']} unique OEIS sequences")

    elapsed = time.time() - t0

    # Assemble output
    output = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 2),
            "challenge": "M7: Nonlinear Transformation Search",
            "parameters": {
                "n_oeis": len(oeis_seqs),
                "n_ec": len(ec_seqs),
                "fingerprint_primes": FINGERPRINT_PRIMES,
                "fingerprint_len": FINGERPRINT_LEN,
                "match_threshold": MATCH_THRESHOLD,
                "transforms": [
                    "quadratic (a_n^2)",
                    "product (a_n * a_{n-1})",
                    "convolution (sum a_k * a_{n-k})",
                    "logarithmic (round(log(a_n) * C))",
                    "modular (a_n mod m)",
                ],
            },
        },
        "cross_domain": cross_results,
        "intra_oeis": intra_results,
        "near_miss_recovery": near_miss_results,
        "permutation_null": null_results,
        "hub_analysis": {
            "cross_domain": cross_hub,
            "intra_oeis": intra_hub,
        },
        "verdict": {},
    }

    # Compute verdict — require null-test significance
    cross_genuine = [
        m for m in cross_results.get("top_matches", [])
        if m["match_rate"] > m["baseline_rate"] + 0.15
    ]
    intra_genuine = intra_results.get("top_matches", [])
    null_significant = null_results.get("significant", False)

    # Check if matches are hub-dominated (degenerate)
    cross_degenerate = cross_hub["unique_ec"] <= 5 or cross_hub["unique_oeis"] <= 5
    intra_degenerate = intra_hub["unique_oeis"] <= 5

    real_cross = len(cross_genuine) if not cross_degenerate and null_significant else 0
    # Intra-OEIS: check if top hub has > 40% of matches (degenerate)
    if intra_hub["top_oeis_hubs"]:
        top_hub_count = max(intra_hub["top_oeis_hubs"].values())
        intra_hub_fraction = top_hub_count / max(intra_hub["total_matches"], 1)
    else:
        intra_hub_fraction = 0
    intra_degenerate = intra_degenerate or intra_hub_fraction > 0.4
    real_intra = len(intra_genuine) if not intra_degenerate else 0

    output["verdict"] = {
        "cross_domain_raw_matches": len(cross_genuine),
        "cross_domain_after_null": real_cross,
        "cross_hub_dominated": cross_degenerate,
        "intra_oeis_raw_matches": len(intra_genuine),
        "intra_oeis_after_null": real_intra,
        "intra_hub_dominated": intra_degenerate,
        "null_test_significant": null_significant,
        "null_z_score": null_results.get("z_score", 0),
        "near_miss_recovery_rate": near_miss_results.get("recovery_rate", 0),
        "linear_ceiling_broken": real_cross > 0 or real_intra > 0,
        "summary": (
            f"Tested {cross_results['total_pairs_tested']} OEIS x EC pairs and "
            f"{intra_results['total_pairs_tested']} OEIS x OEIS pairs with 5 nonlinear "
            f"transform families. Raw matches: {len(cross_genuine)} cross-domain, "
            f"{len(intra_genuine)} intra-OEIS. Permutation null z={null_results.get('z_score', 0):.1f}. "
            f"Hub analysis: cross={cross_hub['unique_ec']} unique EC / {cross_hub['unique_oeis']} unique OEIS, "
            f"intra={intra_hub['unique_oeis']} unique OEIS. "
            f"After null correction: {real_cross} cross-domain, {real_intra} intra-OEIS survive. "
            f"Near-miss recovery: {near_miss_results.get('testable_count', 0)}/26 testable. "
            f"Linear ceiling {'BROKEN' if real_cross > 0 or real_intra > 0 else 'HOLDS'}."
        ),
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"\nVERDICT: {output['verdict']['summary']}")


if __name__ == "__main__":
    main()
