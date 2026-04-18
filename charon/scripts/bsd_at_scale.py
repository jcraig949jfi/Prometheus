"""
BSD At Scale — Full BSD Ratio Verification at Production Scale
Charon — 2026-04-15

Scale-up from 218/218 Phase 2 verification to thousands of curves.
Strategy:
  1. Stratified random: 1000 curves per rank (0, 1, 2, 3+), spread across conductor decades
  2. Extreme curves: highest conductor, highest sha, highest regulator
  3. Rank 2+ conditional BSD: any deviation would be extraordinary

Data sources:
  - ec_curvedata (local): rank, regulator, sha, torsion, conductor, lmfdb_label
  - lfunc_lfunctions (local): leading_term via origin = 'EllipticCurve/Q/{N}/{iso}'
  - ec_mwbsd (devmirror.lmfdb.xyz): real_period, tamagawa_product, sha_an
"""

import json
import math
import time
import numpy as np
import psycopg2

LOCAL_DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
MIRROR_DB = dict(host='devmirror.lmfdb.xyz', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = r"F:\Prometheus\charon\data\bsd_at_scale.json"

# Stratified sampling plan
SAMPLES_PER_RANK = {0: 1000, 1: 1000, 2: 500, 3: 200}
EXTREME_SAMPLES = 300  # highest conductor, sha, regulator
BATCH_SIZE = 200  # for remote queries — be polite to devmirror


def compute_bsd_ratio(rank, leading_term, real_period, tamagawa_product,
                      sha_an, torsion, regulator):
    """BSD ratio. Should equal 1.0 if BSD holds."""
    if any(v is None or v == 0 for v in [leading_term, real_period, tamagawa_product, torsion]):
        return None, "missing_data"
    if sha_an is None or sha_an == 0:
        return None, "sha_zero_or_none"

    denom = float(real_period) * float(tamagawa_product) * float(sha_an) / (int(torsion) ** 2)

    if rank > 0:
        if regulator is None or float(regulator) == 0:
            return None, "missing_regulator"
        denom *= float(regulator)

    ratio = float(leading_term) / denom
    return ratio, "ok"


def label_to_origin(label):
    """Convert lmfdb_label like '11.a1' to origin 'EllipticCurve/Q/11/a'."""
    parts = label.split('.')
    conductor = parts[0]
    iso_letter = ''.join(c for c in parts[1] if c.isalpha())
    return f"EllipticCurve/Q/{conductor}/{iso_letter}"


def select_stratified_sample(local_cur):
    """Select stratified random sample across ranks and conductor decades."""
    print("\n[1] Selecting stratified sample from local ec_curvedata...")
    curve_data = {}

    for rank, n in SAMPLES_PER_RANK.items():
        # Spread across conductor decades for better coverage
        # Decades: [1-100], [100-1K], [1K-10K], [10K-100K], [100K-1M], [1M+]
        decades = [
            (1, 100), (100, 1000), (1000, 10000),
            (10000, 100000), (100000, 1000000), (1000000, 10000000000)
        ]
        per_decade = max(n // len(decades), 10)

        for lo, hi in decades:
            local_cur.execute("""
                SELECT lmfdb_label, rank::int, regulator::double precision,
                       sha::int, torsion::int, conductor::bigint
                FROM ec_curvedata
                WHERE rank = %s AND conductor::bigint >= %s AND conductor::bigint < %s
                ORDER BY random()
                LIMIT %s
            """, (str(rank), lo, hi, per_decade))
            for label, rk, reg, sha, tor, cond in local_cur:
                curve_data[label] = {
                    'rank': rk, 'regulator': reg, 'sha': sha,
                    'torsion': tor, 'conductor': int(cond), 'source': 'stratified',
                }

        count_rk = sum(1 for v in curve_data.values() if v['rank'] == rank)
        print(f"  rank {rank}: {count_rk} curves selected")

    return curve_data


def select_extreme_curves(local_cur, existing_labels):
    """Target extreme curves where failures are most likely."""
    print("\n[2] Selecting extreme curves (highest conductor, sha, regulator)...")
    extreme = {}

    # Highest conductors
    local_cur.execute("""
        SELECT lmfdb_label, rank::int, regulator::double precision,
               sha::int, torsion::int, conductor::bigint
        FROM ec_curvedata
        WHERE rank IN ('0','1','2','3')
        ORDER BY conductor::bigint DESC
        LIMIT %s
    """, (EXTREME_SAMPLES,))
    for label, rk, reg, sha, tor, cond in local_cur:
        if label not in existing_labels:
            extreme[label] = {
                'rank': rk, 'regulator': reg, 'sha': sha,
                'torsion': tor, 'conductor': int(cond), 'source': 'extreme_conductor',
            }
    print(f"  Extreme conductor: {len(extreme)} new curves")

    # Highest sha (analytic)
    local_cur.execute("""
        SELECT lmfdb_label, rank::int, regulator::double precision,
               sha::int, torsion::int, conductor::bigint
        FROM ec_curvedata
        WHERE sha IS NOT NULL AND sha::int > 1
        ORDER BY sha::int DESC
        LIMIT %s
    """, (EXTREME_SAMPLES,))
    count_sha = 0
    for label, rk, reg, sha, tor, cond in local_cur:
        if label not in existing_labels and label not in extreme:
            extreme[label] = {
                'rank': rk, 'regulator': reg, 'sha': sha,
                'torsion': tor, 'conductor': int(cond), 'source': 'extreme_sha',
            }
            count_sha += 1
    print(f"  Extreme sha: {count_sha} new curves")

    # Highest regulators (rank >= 1)
    local_cur.execute("""
        SELECT lmfdb_label, rank::int, regulator::double precision,
               sha::int, torsion::int, conductor::bigint
        FROM ec_curvedata
        WHERE rank::int >= 1 AND regulator IS NOT NULL
        ORDER BY regulator::double precision DESC
        LIMIT %s
    """, (EXTREME_SAMPLES,))
    count_reg = 0
    for label, rk, reg, sha, tor, cond in local_cur:
        if label not in existing_labels and label not in extreme:
            extreme[label] = {
                'rank': rk, 'regulator': reg, 'sha': sha,
                'torsion': tor, 'conductor': int(cond), 'source': 'extreme_regulator',
            }
            count_reg += 1
    print(f"  Extreme regulator: {count_reg} new curves")

    return extreme


def fetch_leading_terms(local_cur, labels):
    """Fetch leading_term from lfunc_lfunctions for all labels."""
    print(f"\n[3] Fetching leading terms for {len(labels)} curves...")
    origins = {label: label_to_origin(label) for label in labels}
    unique_origins = list(set(origins.values()))

    lt_map = {}
    for i in range(0, len(unique_origins), 500):
        batch = unique_origins[i:i+500]
        placeholders = ','.join(['%s'] * len(batch))
        local_cur.execute(f"""
            SELECT origin, leading_term::double precision
            FROM lfunc_lfunctions
            WHERE origin IN ({placeholders})
        """, batch)
        for origin, lt in local_cur:
            lt_map[origin] = lt

    found = sum(1 for label in labels if origins[label] in lt_map)
    print(f"  Found leading_term for {found}/{len(labels)} curves")
    return origins, lt_map


def fetch_mwbsd_batched(labels):
    """Batch-fetch ec_mwbsd from devmirror, politely."""
    print(f"\n[4] Fetching MWBSD data from devmirror.lmfdb.xyz ({len(labels)} curves)...")
    mirror_conn = psycopg2.connect(**MIRROR_DB)
    mirror_cur = mirror_conn.cursor()

    mwbsd_data = {}
    total_batches = (len(labels) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(labels), BATCH_SIZE):
        batch = labels[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        placeholders = ','.join(['%s'] * len(batch))
        try:
            mirror_cur.execute(f"""
                SELECT lmfdb_label, real_period, tamagawa_product, sha_an
                FROM ec_mwbsd
                WHERE lmfdb_label IN ({placeholders})
            """, batch)
            for label, rp, tam, sha in mirror_cur:
                mwbsd_data[label] = {
                    'real_period': rp,
                    'tamagawa_product': tam,
                    'sha_an': sha,
                }
        except Exception as e:
            print(f"  WARNING: batch {batch_num} failed: {e}")
            mirror_conn.rollback()

        if batch_num % 10 == 0 or batch_num == total_batches:
            print(f"  Batch {batch_num}/{total_batches}: {len(mwbsd_data)} fetched so far")

        # Small delay between batches to be polite
        if batch_num % 20 == 0:
            time.sleep(0.5)

    mirror_conn.close()
    print(f"  Total MWBSD records: {len(mwbsd_data)}/{len(labels)}")
    return mwbsd_data


def compute_all_ratios(all_labels, curve_data, origins, lt_map, mwbsd_data):
    """Compute BSD ratio for all curves."""
    print(f"\n[5] Computing BSD ratios for {len(all_labels)} curves...")
    results = []
    stats = {
        'pass': 0, 'fail': 0, 'skip': 0,
        'skip_reasons': {},
        'by_rank': {},
        'by_source': {},
    }

    for label in all_labels:
        cd = curve_data[label]
        origin = origins[label]
        rank = cd['rank']
        source = cd['source']

        # Init rank/source tracking
        for key_dict, key_val in [('by_rank', rank), ('by_source', source)]:
            if key_val not in stats[key_dict]:
                stats[key_dict][key_val] = {'pass': 0, 'fail': 0, 'skip': 0}

        if origin not in lt_map:
            stats['skip'] += 1
            stats['by_rank'][rank]['skip'] += 1
            stats['by_source'][source]['skip'] += 1
            stats['skip_reasons']['no_leading_term'] = stats['skip_reasons'].get('no_leading_term', 0) + 1
            continue
        if label not in mwbsd_data:
            stats['skip'] += 1
            stats['by_rank'][rank]['skip'] += 1
            stats['by_source'][source]['skip'] += 1
            stats['skip_reasons']['no_mwbsd'] = stats['skip_reasons'].get('no_mwbsd', 0) + 1
            continue

        mw = mwbsd_data[label]
        ratio, status = compute_bsd_ratio(
            rank=rank,
            leading_term=lt_map[origin],
            real_period=mw['real_period'],
            tamagawa_product=mw['tamagawa_product'],
            sha_an=mw['sha_an'],
            torsion=cd['torsion'],
            regulator=cd['regulator'],
        )

        if ratio is None:
            stats['skip'] += 1
            stats['by_rank'][rank]['skip'] += 1
            stats['by_source'][source]['skip'] += 1
            stats['skip_reasons'][status] = stats['skip_reasons'].get(status, 0) + 1
            continue

        deviation = abs(ratio - 1.0)
        is_pass = deviation < 1e-6  # strict threshold

        rec = {
            'label': label,
            'rank': rank,
            'conductor': cd['conductor'],
            'source': source,
            'leading_term': lt_map[origin],
            'real_period': float(mw['real_period']),
            'tamagawa_product': int(mw['tamagawa_product']),
            'sha_an': float(mw['sha_an']),
            'torsion': cd['torsion'],
            'regulator': cd['regulator'],
            'bsd_ratio': ratio,
            'deviation': deviation,
            'log_deviation': math.log10(deviation) if deviation > 0 else -16,
            'pass': is_pass,
        }
        results.append(rec)

        if is_pass:
            stats['pass'] += 1
            stats['by_rank'][rank]['pass'] += 1
            stats['by_source'][source]['pass'] += 1
        else:
            stats['fail'] += 1
            stats['by_rank'][rank]['fail'] += 1
            stats['by_source'][source]['fail'] += 1

            # IMMEDIATE FLAG for failures
            print(f"\n  *** FAILURE: {label} ***")
            print(f"      rank={rank}, N={cd['conductor']}, ratio={ratio:.15f}")
            print(f"      deviation={deviation:.2e}, source={source}")
            print(f"      LT={lt_map[origin]}, Omega={float(mw['real_period']):.10f}")
            print(f"      tam={int(mw['tamagawa_product'])}, sha={float(mw['sha_an'])}, "
                  f"tor={cd['torsion']}, reg={cd['regulator']}")

    return results, stats


def analyze_deviations(results):
    """Analyze the distribution of deviations."""
    if not results:
        return {}

    deviations = [r['deviation'] for r in results]
    log_devs = [r['log_deviation'] for r in results]

    analysis = {
        'count': len(results),
        'mean_deviation': float(np.mean(deviations)),
        'median_deviation': float(np.median(deviations)),
        'max_deviation': float(np.max(deviations)),
        'min_deviation': float(np.min(deviations)),
        'std_deviation': float(np.std(deviations)),
        'mean_log_deviation': float(np.mean(log_devs)),
        'median_log_deviation': float(np.median(log_devs)),
        'std_log_deviation': float(np.std(log_devs)),
    }

    # Histogram of log deviations
    bins = [-16, -14, -12, -10, -8, -6, -4, -2, 0]
    counts, _ = np.histogram(log_devs, bins=bins)
    analysis['log_deviation_histogram'] = {
        f"[{bins[i]},{bins[i+1]})": int(counts[i]) for i in range(len(counts))
    }

    # Check correlation with conductor
    conductors = [r['conductor'] for r in results]
    if len(set(conductors)) > 2:
        from scipy.stats import spearmanr
        rho, pval = spearmanr(conductors, deviations)
        analysis['conductor_deviation_corr'] = {'rho': float(rho), 'pval': float(pval)}

    # Check correlation with rank
    ranks = [r['rank'] for r in results]
    if len(set(ranks)) > 1:
        from scipy.stats import spearmanr
        rho, pval = spearmanr(ranks, deviations)
        analysis['rank_deviation_corr'] = {'rho': float(rho), 'pval': float(pval)}

    return analysis


def main():
    t0 = time.time()
    print("=" * 70)
    print("BSD AT SCALE — Full BSD Ratio Verification")
    print("=" * 70)

    # Connect to local DB
    local_conn = psycopg2.connect(**LOCAL_DB)
    local_cur = local_conn.cursor()

    # Step 1: Stratified sample
    curve_data = select_stratified_sample(local_cur)

    # Step 2: Extreme curves
    extreme = select_extreme_curves(local_cur, set(curve_data.keys()))
    curve_data.update(extreme)

    all_labels = list(curve_data.keys())
    print(f"\n  Total curves to test: {len(all_labels)}")

    # Step 3: Leading terms (local)
    origins, lt_map = fetch_leading_terms(local_cur, all_labels)
    local_conn.close()

    # Step 4: MWBSD data (remote)
    mwbsd_data = fetch_mwbsd_batched(all_labels)

    # Step 5: Compute ratios
    results, stats = compute_all_ratios(all_labels, curve_data, origins, lt_map, mwbsd_data)

    # Step 6: Analysis
    print("\n" + "=" * 70)
    print("DEVIATION ANALYSIS")
    print("=" * 70)
    analysis = analyze_deviations(results)

    if analysis:
        print(f"  Curves tested:         {analysis['count']}")
        print(f"  Mean deviation:        {analysis['mean_deviation']:.2e}")
        print(f"  Median deviation:      {analysis['median_deviation']:.2e}")
        print(f"  Max deviation:         {analysis['max_deviation']:.2e}")
        print(f"  Median log deviation:  {analysis['median_log_deviation']:.1f}")
        print(f"\n  Log deviation histogram (base 10):")
        for bucket, count in analysis['log_deviation_histogram'].items():
            bar = '#' * min(count // 5, 60)
            print(f"    {bucket:>12}: {count:5d}  {bar}")

        if 'conductor_deviation_corr' in analysis:
            c = analysis['conductor_deviation_corr']
            print(f"\n  Conductor-deviation Spearman rho: {c['rho']:.4f} (p={c['pval']:.4e})")
        if 'rank_deviation_corr' in analysis:
            c = analysis['rank_deviation_corr']
            print(f"  Rank-deviation Spearman rho:      {c['rho']:.4f} (p={c['pval']:.4e})")

    # Step 7: Summary
    total_tested = stats['pass'] + stats['fail']
    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print("BSD AT SCALE — FINAL RESULTS")
    print("=" * 70)
    print(f"  Curves sampled:        {len(all_labels)}")
    print(f"  Curves tested:         {total_tested}")
    print(f"  PASS (|ratio-1|<1e-6): {stats['pass']}")
    print(f"  FAIL:                  {stats['fail']}")
    print(f"  Skipped:               {stats['skip']}")
    if total_tested > 0:
        print(f"  Pass rate:             {100*stats['pass']/total_tested:.4f}%")

    print(f"\n  Skip reasons: {stats['skip_reasons']}")

    print("\n  By rank:")
    for rk in sorted(stats['by_rank'].keys()):
        s = stats['by_rank'][rk]
        total_rk = s['pass'] + s['fail']
        if total_rk > 0:
            print(f"    rank {rk}: {s['pass']}/{total_rk} pass "
                  f"({100*s['pass']/total_rk:.2f}%), {s['skip']} skipped")
        else:
            print(f"    rank {rk}: 0 tested, {s['skip']} skipped")

    print("\n  By source:")
    for src in sorted(stats['by_source'].keys()):
        s = stats['by_source'][src]
        total_src = s['pass'] + s['fail']
        if total_src > 0:
            print(f"    {src:25s}: {s['pass']}/{total_src} pass "
                  f"({100*s['pass']/total_src:.2f}%), {s['skip']} skipped")

    # Top 20 worst deviations
    if results:
        sorted_by_dev = sorted(results, key=lambda x: -x['deviation'])
        print("\n  Top 20 worst deviations:")
        for r in sorted_by_dev[:20]:
            print(f"    {r['label']:20s} rank={r['rank']} N={r['conductor']:>10d} "
                  f"ratio={r['bsd_ratio']:.12f} dev={r['deviation']:.2e} [{r['source']}]")

    print(f"\n  Elapsed time: {elapsed:.1f}s")

    # Save
    output = {
        'test': 'BSD At Scale — Full BSD Ratio Verification',
        'source': 'ec_mwbsd (devmirror) + ec_curvedata + lfunc_lfunctions (local)',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'elapsed_seconds': round(elapsed, 1),
        'threshold': 1e-6,
        'summary': {
            'curves_sampled': len(all_labels),
            'curves_tested': total_tested,
            'pass': stats['pass'],
            'fail': stats['fail'],
            'skip': stats['skip'],
            'pass_rate': stats['pass'] / total_tested if total_tested > 0 else 0,
        },
        'skip_reasons': stats['skip_reasons'],
        'rank_breakdown': {str(k): v for k, v in stats['by_rank'].items()},
        'source_breakdown': stats['by_source'],
        'deviation_analysis': analysis,
        'worst_20': sorted(results, key=lambda x: -x['deviation'])[:20] if results else [],
        'results': results,
    }

    with open(OUT, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Results saved to {OUT}")


if __name__ == '__main__':
    main()
