"""
Charon: NF-EC conductor/discriminant bridge test at scale.

Tests whether NF discriminant distribution encodes EC conductor structure
beyond trivial prime-sharing ("the prime atmosphere").

All tests use permutation nulls, not uniform nulls.
"""

import json
import time
import numpy as np
import psycopg2
from collections import Counter, defaultdict
from pathlib import Path

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT_PATH = Path(r'F:\Prometheus\charon\data\nf_ec_bridge.json')

def get_conn():
    return psycopg2.connect(**DB_PARAMS)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

# ─────────────────────────────────────────────────────────────
# 1. Load data
# ─────────────────────────────────────────────────────────────
def load_ec_conductors(conn, limit=500000):
    """Load EC conductors and ranks (sample if needed)."""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT conductor::bigint, rank::int
        FROM ec_curvedata
        ORDER BY random()
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    conductors = np.array([r[0] for r in rows], dtype=np.int64)
    ranks = np.array([r[1] for r in rows], dtype=np.int64)
    return conductors, ranks


def load_nf_disc_by_degree(conn, max_disc=300000000):
    """Load NF |disc| and class_number, stratified by degree.
    Only keep disc_abs <= max_disc (EC conductor range)."""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT degree::int, disc_abs::bigint, class_number::int
        FROM nf_fields
        WHERE disc_abs::numeric <= {max_disc}
    """)
    by_degree = defaultdict(lambda: {'disc': [], 'class_number': []})
    total = 0
    for deg, disc, cn in cur:
        by_degree[deg]['disc'].append(disc)
        by_degree[deg]['class_number'].append(cn)
        total += 1
    log(f"Loaded {total} NF fields with disc_abs <= {max_disc}")
    for deg in by_degree:
        by_degree[deg]['disc'] = np.array(by_degree[deg]['disc'], dtype=np.int64)
        by_degree[deg]['class_number'] = np.array(by_degree[deg]['class_number'], dtype=np.int64)
    return dict(by_degree)


# ─────────────────────────────────────────────────────────────
# 2. Distribution comparison
# ─────────────────────────────────────────────────────────────
def log_histogram(values, n_bins=50, label=""):
    """Compute log-spaced histogram."""
    pos = values[values > 0]
    if len(pos) == 0:
        return None, None
    bins = np.logspace(np.log10(pos.min()), np.log10(pos.max()), n_bins + 1)
    counts, edges = np.histogram(pos, bins=bins)
    return counts.tolist(), edges.tolist()


# ─────────────────────────────────────────────────────────────
# 3. Direct match test with permutation null
# ─────────────────────────────────────────────────────────────
def direct_match_test(nf_discs, ec_conductors, n_perms=1000):
    """
    How many NF |disc| exactly equal an EC conductor?
    Null: shuffle the EC conductor set (permutation of labels).

    Since we're testing set overlap, the null is:
    draw len(nf_discs) values from the EC conductor pool with replacement,
    count matches. Actually, the proper null is:
    keep the EC conductor SET fixed, shuffle which integers the NF discs are.
    But that's the uniform null we want to avoid.

    Better permutation null: among NF discs in the EC conductor range,
    how many match vs how many would match if we randomly reassigned
    each NF disc to another NF disc from the same degree?

    Simplest valid approach: the EC conductor set is fixed.
    Count real overlaps. For null: resample NF discs by drawing
    with replacement from ALL NF discs (preserving their distribution)
    and count overlaps. This tests whether the specific values matter
    beyond the marginal distribution — which they shouldn't differ from.

    Even better: the real question is whether the OVERLAP RATE between
    NF disc values and EC conductor values exceeds what you'd expect
    from two independent sets of integers with the same size/prime structure.
    Use bootstrap on the NF side.
    """
    ec_set = set(ec_conductors.tolist())

    # Real overlap
    real_matches = np.sum(np.isin(nf_discs, list(ec_set)))

    # Permutation null: shuffle NF disc values (break any structure)
    null_matches = []
    nf_list = nf_discs.copy()
    for _ in range(n_perms):
        # Resample from NF discs with replacement (bootstrap)
        resampled = np.random.choice(nf_list, size=len(nf_list), replace=True)
        null_matches.append(np.sum(np.isin(resampled, list(ec_set))))

    null_matches = np.array(null_matches)
    null_mean = null_matches.mean()
    null_std = null_matches.std()
    z_score = (real_matches - null_mean) / null_std if null_std > 0 else 0.0

    return {
        'real_matches': int(real_matches),
        'n_nf': int(len(nf_discs)),
        'n_ec_unique': int(len(ec_set)),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z_score),
        'match_rate': float(real_matches / len(nf_discs)) if len(nf_discs) > 0 else 0,
        'null_match_rate': float(null_mean / len(nf_discs)) if len(nf_discs) > 0 else 0,
    }


# ─────────────────────────────────────────────────────────────
# 4. Prime factor structure test
# ─────────────────────────────────────────────────────────────
def small_prime_signature(n, primes=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)):
    """Return tuple of valuations at small primes."""
    sig = []
    for p in primes:
        v = 0
        while n > 0 and n % p == 0:
            n //= p
            v += 1
        sig.append(v)
    return tuple(sig)


def prime_factor_test(nf_discs, ec_conductors, n_sample=50000, n_perms=200):
    """
    Compare prime factorization patterns.
    Use small-prime signatures and measure cosine similarity
    between the signature distributions.
    """
    rng = np.random.default_rng(42)

    # Sample
    nf_sample = rng.choice(nf_discs, size=min(n_sample, len(nf_discs)), replace=False)
    ec_sample = rng.choice(ec_conductors, size=min(n_sample, len(ec_conductors)), replace=False)

    # Compute signatures
    nf_sigs = np.array([small_prime_signature(int(d)) for d in nf_sample])
    ec_sigs = np.array([small_prime_signature(int(c)) for c in ec_sample])

    # Mean signature vectors
    nf_mean = nf_sigs.mean(axis=0)
    ec_mean = ec_sigs.mean(axis=0)

    # Cosine similarity
    def cosine_sim(a, b):
        dot = np.dot(a, b)
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        return float(dot / (na * nb)) if na > 0 and nb > 0 else 0.0

    real_cos = cosine_sim(nf_mean, ec_mean)

    # KL-divergence on number-of-prime-factors distribution
    def n_prime_factors(vals):
        """Count total prime factors (with multiplicity) for small primes."""
        return np.array([sum(small_prime_signature(int(v))) for v in vals])

    nf_npf = n_prime_factors(nf_sample)
    ec_npf = n_prime_factors(ec_sample)

    # Histogram overlap (Bhattacharyya coefficient)
    max_npf = max(nf_npf.max(), ec_npf.max()) + 1
    nf_hist = np.bincount(nf_npf, minlength=max_npf).astype(float)
    ec_hist = np.bincount(ec_npf, minlength=max_npf).astype(float)
    nf_hist /= nf_hist.sum()
    ec_hist /= ec_hist.sum()
    bhatt = float(np.sum(np.sqrt(nf_hist * ec_hist)))

    # Permutation null: shuffle labels between NF and EC pools
    combined_sigs = np.vstack([nf_sigs, ec_sigs])
    null_cos = []
    null_bhatt = []
    for _ in range(n_perms):
        perm = rng.permutation(len(combined_sigs))
        half = len(nf_sigs)
        a_mean = combined_sigs[perm[:half]].mean(axis=0)
        b_mean = combined_sigs[perm[half:]].mean(axis=0)
        null_cos.append(cosine_sim(a_mean, b_mean))

        a_npf = combined_sigs[perm[:half]].sum(axis=1)
        b_npf = combined_sigs[perm[half:]].sum(axis=1)
        max_n = max(a_npf.max(), b_npf.max()) + 1
        a_h = np.bincount(a_npf, minlength=max_n).astype(float)
        b_h = np.bincount(b_npf, minlength=max_n).astype(float)
        a_h /= a_h.sum()
        b_h /= b_h.sum()
        null_bhatt.append(float(np.sum(np.sqrt(a_h * b_h))))

    null_cos = np.array(null_cos)
    null_bhatt = np.array(null_bhatt)

    return {
        'real_cosine_similarity': real_cos,
        'null_cosine_mean': float(null_cos.mean()),
        'null_cosine_std': float(null_cos.std()),
        'cosine_z': float((real_cos - null_cos.mean()) / null_cos.std()) if null_cos.std() > 0 else 0.0,
        'real_bhattacharyya': bhatt,
        'null_bhatt_mean': float(null_bhatt.mean()),
        'null_bhatt_std': float(null_bhatt.std()),
        'bhatt_z': float((bhatt - null_bhatt.mean()) / null_bhatt.std()) if null_bhatt.std() > 0 else 0.0,
        'nf_mean_signature': nf_mean.tolist(),
        'ec_mean_signature': ec_mean.tolist(),
        'primes_used': [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31],
    }


# ─────────────────────────────────────────────────────────────
# 5. Degree stratification
# ─────────────────────────────────────────────────────────────
def degree_stratified_test(nf_by_degree, ec_set, n_perms=500):
    """Run direct match test per degree."""
    results = {}
    for deg in sorted(nf_by_degree.keys()):
        discs = nf_by_degree[deg]['disc']
        if len(discs) < 100:
            continue
        log(f"  Degree {deg}: {len(discs)} fields")
        res = direct_match_test(discs, np.array(list(ec_set)), n_perms=n_perms)
        results[str(deg)] = res
    return results


# ─────────────────────────────────────────────────────────────
# 6. Class number vs EC rank correlation
# ─────────────────────────────────────────────────────────────
def class_number_rank_test(nf_by_degree, ec_cond_to_ranks, n_perms=1000):
    """
    For NF fields whose |disc| matches an EC conductor,
    correlate class_number with EC rank.
    Null: permute the EC rank labels.
    """
    # Collect matched pairs
    matched_cn = []
    matched_rank = []

    for deg in nf_by_degree:
        discs = nf_by_degree[deg]['disc']
        cns = nf_by_degree[deg]['class_number']
        for i in range(len(discs)):
            d = int(discs[i])
            if d in ec_cond_to_ranks:
                for rank in ec_cond_to_ranks[d]:
                    matched_cn.append(int(cns[i]))
                    matched_rank.append(rank)

    if len(matched_cn) < 10:
        return {'n_matched': len(matched_cn), 'status': 'too_few_matches'}

    matched_cn = np.array(matched_cn, dtype=float)
    matched_rank = np.array(matched_rank, dtype=float)

    # Pearson correlation
    real_corr = float(np.corrcoef(matched_cn, matched_rank)[0, 1])

    # Permutation null
    null_corrs = []
    for _ in range(n_perms):
        perm_rank = np.random.permutation(matched_rank)
        null_corrs.append(float(np.corrcoef(matched_cn, perm_rank)[0, 1]))

    null_corrs = np.array(null_corrs)
    z_score = (real_corr - null_corrs.mean()) / null_corrs.std() if null_corrs.std() > 0 else 0.0

    # Also: mean rank by class number bucket
    cn_buckets = {}
    for cn_val in sorted(set(matched_cn.astype(int).tolist())):
        mask = matched_cn == cn_val
        if mask.sum() >= 5:
            cn_buckets[str(cn_val)] = {
                'count': int(mask.sum()),
                'mean_rank': float(matched_rank[mask].mean()),
                'std_rank': float(matched_rank[mask].std()),
            }

    return {
        'n_matched': len(matched_cn),
        'real_correlation': real_corr,
        'null_mean': float(null_corrs.mean()),
        'null_std': float(null_corrs.std()),
        'z_score': float(z_score),
        'p_value_approx': float(np.mean(np.abs(null_corrs) >= np.abs(real_corr))),
        'cn_buckets': cn_buckets,
    }


# ─────────────────────────────────────────────────────────────
# 7. Conductor divisibility test
# ─────────────────────────────────────────────────────────────
def divisibility_test(nf_discs, ec_conductors, n_sample=100000, n_perms=500):
    """
    Beyond exact matches: does disc | conductor or conductor | disc
    happen more often than expected?
    """
    rng = np.random.default_rng(99)
    nf_s = rng.choice(nf_discs, size=min(n_sample, len(nf_discs)), replace=False)
    ec_s = rng.choice(ec_conductors, size=min(n_sample, len(ec_conductors)), replace=False)

    # For efficiency, only test a cross-sample
    cross_n = min(5000, len(nf_s), len(ec_s))
    nf_cross = nf_s[:cross_n]
    ec_cross = ec_s[:cross_n]

    # Real: count pairs where one divides the other
    real_div = 0
    for d in nf_cross:
        for c in ec_cross[:500]:  # limit to keep tractable
            if d > 0 and c > 0:
                if c % d == 0 or d % c == 0:
                    real_div += 1

    # Null: permute EC conductors
    null_divs = []
    for _ in range(min(n_perms, 100)):
        perm_ec = rng.permutation(ec_cross)[:500]
        nd = 0
        for d in nf_cross:
            for c in perm_ec:
                if d > 0 and c > 0:
                    if c % d == 0 or d % c == 0:
                        nd += 1
        null_divs.append(nd)

    null_divs = np.array(null_divs)
    z = (real_div - null_divs.mean()) / null_divs.std() if null_divs.std() > 0 else 0.0

    return {
        'real_divisibility_count': int(real_div),
        'n_pairs_tested': int(cross_n * 500),
        'null_mean': float(null_divs.mean()),
        'null_std': float(null_divs.std()),
        'z_score': float(z),
    }


# ─────────────────────────────────────────────────────────────
# 8. Shared radical test (same set of prime divisors)
# ─────────────────────────────────────────────────────────────
def load_nf_ramps(conn, max_disc=300000000):
    """Load NF ramps (ramified primes = radical of discriminant)."""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT disc_abs::bigint, ramps
        FROM nf_fields
        WHERE disc_abs::numeric <= {max_disc} AND degree::int = 2
        ORDER BY random()
        LIMIT 200000
    """)
    disc_to_ramps = {}
    for disc, ramps_str in cur:
        # ramps is stored as '{2,3,5}' format
        try:
            primes = set()
            if ramps_str and ramps_str != '{}':
                for p in ramps_str.strip('{}').split(','):
                    p = p.strip()
                    if p:
                        primes.add(int(p))
            disc_to_ramps[int(disc)] = frozenset(primes)
        except:
            pass
    return disc_to_ramps


def load_ec_bad_primes(conn, limit=200000):
    """Load EC bad primes (= primes dividing conductor)."""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT conductor::bigint, bad_primes
        FROM ec_curvedata
        ORDER BY random()
        LIMIT {limit}
    """)
    cond_to_bad = {}
    for cond, bp_str in cur:
        try:
            primes = set()
            if bp_str and bp_str not in ('{}', '[]', '', None):
                # EC uses JSON-style [2, 3, 5] format
                cleaned = bp_str.strip('{}[]')
                for p in cleaned.split(','):
                    p = p.strip()
                    if p:
                        primes.add(int(p))
            if primes:
                cond_to_bad[int(cond)] = frozenset(primes)
        except:
            pass
    return cond_to_bad


def radical_overlap_test(nf_ramps, ec_bad_primes, n_perms=500):
    """
    For NF discs that match EC conductors: do ramps == bad_primes?
    (They should by theory for quadratic fields if disc = conductor.)

    More interesting: across non-matching values, is the Jaccard
    similarity of prime sets higher than expected?
    """
    # Get samples
    nf_discs = list(nf_ramps.keys())
    ec_conds = list(ec_bad_primes.keys())

    # Exact matches
    matching = set(nf_discs) & set(ec_conds)

    # For matching: check if ramps == bad_primes
    ramp_match = 0
    ramp_subset = 0
    for d in matching:
        if nf_ramps[d] == ec_bad_primes[d]:
            ramp_match += 1
        if nf_ramps[d].issubset(ec_bad_primes[d]) or ec_bad_primes[d].issubset(nf_ramps[d]):
            ramp_subset += 1

    # Cross-Jaccard: sample NF and EC, compute Jaccard similarity of prime sets
    n_sample = min(10000, len(nf_discs), len(ec_conds))
    rng = np.random.default_rng(77)
    nf_idx = rng.choice(len(nf_discs), size=n_sample, replace=False)
    ec_idx = rng.choice(len(ec_conds), size=n_sample, replace=False)

    def mean_jaccard(nf_indices, ec_indices):
        jaccards = []
        for i in range(len(nf_indices)):
            a = nf_ramps[nf_discs[nf_indices[i]]]
            b = ec_bad_primes[ec_conds[ec_indices[i]]]
            if len(a | b) > 0:
                jaccards.append(len(a & b) / len(a | b))
        return np.mean(jaccards) if jaccards else 0.0

    real_jaccard = mean_jaccard(nf_idx, ec_idx)

    # Null: permute EC indices
    null_jaccards = []
    for _ in range(n_perms):
        perm_ec_idx = rng.permutation(ec_idx)
        null_jaccards.append(mean_jaccard(nf_idx, perm_ec_idx))

    null_jaccards = np.array(null_jaccards)
    z = (real_jaccard - null_jaccards.mean()) / null_jaccards.std() if null_jaccards.std() > 0 else 0.0

    return {
        'n_exact_matches': len(matching),
        'ramp_equals_badprime_in_matches': ramp_match,
        'ramp_subset_in_matches': ramp_subset,
        'real_mean_jaccard': float(real_jaccard),
        'null_jaccard_mean': float(null_jaccards.mean()),
        'null_jaccard_std': float(null_jaccards.std()),
        'jaccard_z': float(z),
    }


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════
def main():
    results = {
        'metadata': {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'description': 'NF discriminant vs EC conductor bridge test',
            'null_model': 'permutation (shuffle labels, not uniform random)',
        }
    }

    conn = get_conn()

    # ── Load data ──
    log("Loading EC conductors...")
    ec_conductors, ec_ranks = load_ec_conductors(conn, limit=500000)
    ec_cond_unique = np.unique(ec_conductors)
    ec_set = set(ec_conductors.tolist())
    log(f"  {len(ec_conductors)} EC curves, {len(ec_cond_unique)} unique conductors")
    log(f"  Conductor range: [{ec_conductors.min()}, {ec_conductors.max()}]")

    # Build conductor -> ranks mapping
    ec_cond_to_ranks = defaultdict(list)
    for c, r in zip(ec_conductors, ec_ranks):
        ec_cond_to_ranks[int(c)].append(int(r))

    log("Loading NF fields (disc_abs <= 300M)...")
    nf_by_degree = load_nf_disc_by_degree(conn, max_disc=300000000)

    # All NF discs combined
    all_nf_discs = np.concatenate([nf_by_degree[d]['disc'] for d in nf_by_degree])
    log(f"  {len(all_nf_discs)} NF fields in EC conductor range")

    # ── Distribution comparison ──
    log("Computing distributions...")
    nf_hist_counts, nf_hist_edges = log_histogram(all_nf_discs, n_bins=50, label="NF disc")
    ec_hist_counts, ec_hist_edges = log_histogram(ec_conductors, n_bins=50, label="EC cond")
    results['distributions'] = {
        'nf_disc': {'counts': nf_hist_counts, 'edges': nf_hist_edges},
        'ec_cond': {'counts': ec_hist_counts, 'edges': ec_hist_edges},
        'nf_total': int(len(all_nf_discs)),
        'ec_total': int(len(ec_conductors)),
        'degrees_present': sorted([int(d) for d in nf_by_degree.keys()]),
        'degree_counts': {str(d): int(len(nf_by_degree[d]['disc'])) for d in sorted(nf_by_degree.keys())},
    }

    # ── Direct match test ──
    log("Running direct match test (all degrees combined)...")
    results['direct_match'] = direct_match_test(all_nf_discs, ec_cond_unique, n_perms=1000)
    log(f"  Real matches: {results['direct_match']['real_matches']}, "
        f"null mean: {results['direct_match']['null_mean']:.1f}, "
        f"z={results['direct_match']['z_score']:.2f}")

    # ── Prime factor structure ──
    log("Running prime factor structure test...")
    results['prime_factors'] = prime_factor_test(all_nf_discs, ec_conductors, n_sample=50000, n_perms=200)
    log(f"  Cosine sim: {results['prime_factors']['real_cosine_similarity']:.4f}, "
        f"z={results['prime_factors']['cosine_z']:.2f}")
    log(f"  Bhattacharyya: {results['prime_factors']['real_bhattacharyya']:.4f}, "
        f"z={results['prime_factors']['bhatt_z']:.2f}")

    # ── Degree stratification ──
    log("Running degree-stratified match test...")
    results['by_degree'] = degree_stratified_test(nf_by_degree, ec_set, n_perms=500)
    for deg in sorted(results['by_degree'].keys(), key=int):
        r = results['by_degree'][deg]
        log(f"  Degree {deg}: {r['real_matches']} matches (z={r['z_score']:.2f})")

    # ── Class number vs rank ──
    log("Running class number vs EC rank correlation...")
    results['class_number_rank'] = class_number_rank_test(nf_by_degree, ec_cond_to_ranks, n_perms=1000)
    if 'real_correlation' in results['class_number_rank']:
        log(f"  Correlation: {results['class_number_rank']['real_correlation']:.4f}, "
            f"z={results['class_number_rank']['z_score']:.2f}, "
            f"n={results['class_number_rank']['n_matched']}")
    else:
        log(f"  {results['class_number_rank']['status']}")

    # ── Divisibility test ──
    log("Running divisibility test...")
    results['divisibility'] = divisibility_test(all_nf_discs, ec_conductors, n_sample=50000, n_perms=100)
    log(f"  Divisibility count: {results['divisibility']['real_divisibility_count']}, "
        f"null mean: {results['divisibility']['null_mean']:.1f}, "
        f"z={results['divisibility']['z_score']:.2f}")

    # ── Radical overlap test ──
    log("Loading ramified primes for radical test...")
    nf_ramps = load_nf_ramps(conn, max_disc=300000000)
    ec_bad = load_ec_bad_primes(conn, limit=200000)
    log(f"  {len(nf_ramps)} NF with ramps, {len(ec_bad)} EC with bad_primes")

    log("Running radical overlap test...")
    results['radical_overlap'] = radical_overlap_test(nf_ramps, ec_bad, n_perms=500)
    log(f"  Exact matches: {results['radical_overlap']['n_exact_matches']}")
    log(f"  Ramp==BadPrime in matches: {results['radical_overlap']['ramp_equals_badprime_in_matches']}")
    log(f"  Jaccard z={results['radical_overlap']['jaccard_z']:.2f}")

    conn.close()

    # ── Summary ──
    log("Computing summary...")
    significant = []
    maybe = []
    dead = []

    tests = [
        ('direct_match', results['direct_match'].get('z_score', 0)),
        ('prime_factors_cosine', results['prime_factors'].get('cosine_z', 0)),
        ('prime_factors_bhatt', results['prime_factors'].get('bhatt_z', 0)),
        ('divisibility', results['divisibility'].get('z_score', 0)),
        ('radical_jaccard', results['radical_overlap'].get('jaccard_z', 0)),
    ]
    if 'z_score' in results['class_number_rank']:
        tests.append(('class_number_rank', results['class_number_rank']['z_score']))

    for name, z in tests:
        if abs(z) > 3:
            significant.append(f"{name} (z={z:.2f})")
        elif abs(z) > 2:
            maybe.append(f"{name} (z={z:.2f})")
        else:
            dead.append(f"{name} (z={z:.2f})")

    # Degree-stratified summary
    deg_significant = []
    for deg in results['by_degree']:
        z = results['by_degree'][deg].get('z_score', 0)
        if abs(z) > 3:
            deg_significant.append(f"deg={deg} (z={z:.2f})")

    results['summary'] = {
        'significant_tests': significant,
        'marginal_tests': maybe,
        'dead_tests': dead,
        'degree_significant': deg_significant,
        'verdict': 'SIGNAL' if significant else ('MARGINAL' if maybe else 'DEAD'),
    }

    log(f"\n{'='*60}")
    log(f"VERDICT: {results['summary']['verdict']}")
    log(f"Significant: {significant}")
    log(f"Marginal: {maybe}")
    log(f"Dead: {dead}")
    log(f"Degree-significant: {deg_significant}")
    log(f"{'='*60}")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    log(f"Results saved to {OUT_PATH}")


if __name__ == '__main__':
    main()
