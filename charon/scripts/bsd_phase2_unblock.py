"""
BSD Phase 2 Unblock — Full BSD Ratio Test
Charon — 2026-04-15

Joins ec_curvedata (local) + lfunc_lfunctions (local) + ec_mwbsd (LMFDB mirror)
to compute the actual BSD conjecture ratio:

  rank 0:  L(1) / (Omega * prod(c_p) * |Sha| / |Tor|^2) == 1
  rank r:  L^(r)(1)/r! / (Omega * Reg * prod(c_p) * |Sha| / |Tor|^2) == 1

Data sources:
  - ec_curvedata (local Postgres): rank, regulator, sha, torsion, conductor
  - lfunc_lfunctions (local Postgres): leading_term (via origin)
  - ec_mwbsd (devmirror.lmfdb.xyz): real_period, tamagawa_product, sha_an
"""

import json
import time
from decimal import Decimal
import psycopg2

LOCAL_DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
MIRROR_DB = dict(host='devmirror.lmfdb.xyz', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = r"F:\Prometheus\charon\data\bsd_phase2_unblock.json"

# Stratified sample: N curves per rank
SAMPLES_PER_RANK = {0: 100, 1: 100, 2: 50, 3: 20}


def compute_bsd_ratio(rank, leading_term, real_period, tamagawa_product,
                      sha_an, torsion, regulator):
    """
    BSD conjecture ratio. Should equal 1.0 if BSD holds.
    leading_term from LMFDB is already L^(r)(1)/r!.
    """
    if any(v is None or v == 0 for v in [leading_term, real_period, tamagawa_product, torsion]):
        return None, "missing data"
    if sha_an is None or sha_an == 0:
        return None, "sha is 0 or None"

    denom = float(real_period) * float(tamagawa_product) * float(sha_an) / (int(torsion) ** 2)

    if rank > 0:
        if regulator is None or float(regulator) == 0:
            return None, "missing regulator for rank > 0"
        denom *= float(regulator)

    ratio = float(leading_term) / denom
    return ratio, "ok"


def main():
    print("=" * 70)
    print("BSD Phase 2: Full Ratio Test via LMFDB PostgreSQL Mirror")
    print("=" * 70)

    # Step 1: Get stratified sample of curve labels from local DB
    print("\n[1] Selecting stratified sample from local ec_curvedata...")
    local_conn = psycopg2.connect(**LOCAL_DB)
    local_cur = local_conn.cursor()

    curve_data = {}  # label -> {rank, reg, sha, torsion, conductor}
    for rank, n in SAMPLES_PER_RANK.items():
        local_cur.execute(f"""
            SELECT lmfdb_label, rank::int, regulator::double precision,
                   sha::int, torsion::int, conductor::int
            FROM ec_curvedata
            WHERE rank = %s AND conductor::int < 50000
            ORDER BY random()
            LIMIT %s
        """, (str(rank), n))
        for label, rk, reg, sha, tor, cond in local_cur:
            curve_data[label] = {
                'rank': rk, 'regulator': reg, 'sha': sha,
                'torsion': tor, 'conductor': cond,
            }
        print(f"  rank {rank}: selected {len([v for v in curve_data.values() if v['rank']==rank])}")

    all_labels = list(curve_data.keys())
    print(f"  Total: {len(all_labels)} curves")

    # Step 2: Get leading_term from lfunc_lfunctions
    print("\n[2] Fetching leading terms from lfunc_lfunctions...")
    origins = {}
    for label in all_labels:
        parts = label.split('.')
        conductor = parts[0]
        iso_letter = ''.join(c for c in parts[1] if c.isalpha())
        origins[label] = f"EllipticCurve/Q/{conductor}/{iso_letter}"

    unique_origins = list(set(origins.values()))
    # Fetch in batches
    lt_map = {}  # origin -> leading_term
    batch_size = 500
    for i in range(0, len(unique_origins), batch_size):
        batch = unique_origins[i:i+batch_size]
        placeholders = ','.join(['%s'] * len(batch))
        local_cur.execute(f"""
            SELECT origin, leading_term::double precision
            FROM lfunc_lfunctions
            WHERE origin IN ({placeholders})
        """, batch)
        for origin, lt in local_cur:
            lt_map[origin] = lt

    lt_found = sum(1 for label in all_labels if origins[label] in lt_map)
    print(f"  Found leading_term for {lt_found}/{len(all_labels)} curves")
    local_conn.close()

    # Step 3: Fetch real_period + tamagawa_product from LMFDB mirror
    print("\n[3] Fetching MWBSD data from devmirror.lmfdb.xyz...")
    mirror_conn = psycopg2.connect(**MIRROR_DB)
    mirror_cur = mirror_conn.cursor()

    mwbsd_data = {}  # label -> {real_period, tamagawa_product, sha_an}
    for i in range(0, len(all_labels), batch_size):
        batch = all_labels[i:i+batch_size]
        placeholders = ','.join(['%s'] * len(batch))
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

    print(f"  Found MWBSD data for {len(mwbsd_data)}/{len(all_labels)} curves")
    mirror_conn.close()

    # Step 4: Compute BSD ratios
    print("\n[4] Computing BSD ratios...")
    results = []
    pass_count = 0
    fail_count = 0
    skip_count = 0
    rank_stats = {}

    for label in all_labels:
        cd = curve_data[label]
        origin = origins[label]
        rank = cd['rank']

        if rank not in rank_stats:
            rank_stats[rank] = {'pass': 0, 'fail': 0, 'skip': 0}

        if origin not in lt_map:
            skip_count += 1
            rank_stats[rank]['skip'] += 1
            continue
        if label not in mwbsd_data:
            skip_count += 1
            rank_stats[rank]['skip'] += 1
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
            skip_count += 1
            rank_stats[rank]['skip'] += 1
            continue

        is_pass = abs(ratio - 1.0) < 1e-4
        rec = {
            'label': label,
            'rank': rank,
            'conductor': cd['conductor'],
            'leading_term': lt_map[origin],
            'real_period': float(mw['real_period']),
            'tamagawa_product': int(mw['tamagawa_product']),
            'sha_an': float(mw['sha_an']),
            'torsion': cd['torsion'],
            'regulator': cd['regulator'],
            'bsd_ratio': ratio,
            'deviation': abs(ratio - 1.0),
            'pass': is_pass,
        }
        results.append(rec)

        if is_pass:
            pass_count += 1
            rank_stats[rank]['pass'] += 1
        else:
            fail_count += 1
            rank_stats[rank]['fail'] += 1

    # Summary
    total_tested = pass_count + fail_count
    print("\n" + "=" * 70)
    print("BSD PHASE 2 RESULTS")
    print("=" * 70)
    print(f"Curves sampled:      {len(all_labels)}")
    print(f"Curves tested:       {total_tested}")
    print(f"PASS (|ratio-1|<1e-4): {pass_count}")
    print(f"FAIL:                  {fail_count}")
    print(f"Skipped:               {skip_count}")
    if total_tested > 0:
        print(f"Pass rate:             {100*pass_count/total_tested:.2f}%")

    print("\nBy rank:")
    for rk in sorted(rank_stats.keys()):
        s = rank_stats[rk]
        total_rk = s['pass'] + s['fail']
        if total_rk > 0:
            print(f"  rank {rk}: {s['pass']}/{total_rk} pass ({100*s['pass']/total_rk:.1f}%), "
                  f"{s['skip']} skipped")
        else:
            print(f"  rank {rk}: 0 tested, {s['skip']} skipped")

    # Show worst deviations
    if results:
        sorted_by_dev = sorted(results, key=lambda x: -x['deviation'])
        print("\nTop 10 worst deviations:")
        for r in sorted_by_dev[:10]:
            print(f"  {r['label']}: ratio={r['bsd_ratio']:.10f}, "
                  f"dev={r['deviation']:.2e}, rank={r['rank']}, N={r['conductor']}")

        print("\nSample passing curves (each rank):")
        for rk in sorted(rank_stats.keys()):
            passing_rk = [r for r in results if r['pass'] and r['rank'] == rk]
            for r in passing_rk[:3]:
                print(f"  [{r['label']}] rank={r['rank']}: ratio={r['bsd_ratio']:.10f}, "
                      f"Omega={r['real_period']:.6f}, tam={r['tamagawa_product']}, "
                      f"sha={r['sha_an']:.1f}, tor={r['torsion']}, reg={r['regulator']:.6f}")

    # Save results
    output = {
        'test': 'BSD Phase 2 Full Ratio Test',
        'source': 'ec_mwbsd from devmirror.lmfdb.xyz + local ec_curvedata + lfunc_lfunctions',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'summary': {
            'curves_sampled': len(all_labels),
            'curves_tested': total_tested,
            'pass': pass_count,
            'fail': fail_count,
            'skip': skip_count,
            'pass_rate': pass_count / total_tested if total_tested > 0 else 0,
        },
        'rank_breakdown': {str(k): v for k, v in rank_stats.items()},
        'results': results,
    }

    with open(OUT, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == '__main__':
    main()
