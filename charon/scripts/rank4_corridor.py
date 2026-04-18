"""
Rank-4 Corridor Investigation
Charon — 2026-04-15

The finding: at rank >= 4, log|disc| = log(conductor) exactly,
num_bad_primes = 1, and all curves are essentially semistable.

Five-phase investigation:
  Phase 1: Complete census of rank >= 4 curves
  Phase 2: Bad prime characterization
  Phase 3: Isogeny structure
  Phase 4: Predictions for rank 5+
  Phase 5: Comparison to random curves at same conductors
"""

import json
import math
import sys
import time
import numpy as np
import psycopg2
from collections import Counter, defaultdict

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT = r"F:\Prometheus\charon\data\rank4_corridor.json"


def get_conn():
    return psycopg2.connect(**DB)


def safe_float(x):
    if x is None:
        return None
    try:
        return float(x)
    except:
        return None


def safe_int(x):
    if x is None:
        return None
    try:
        return int(x)
    except:
        return None


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def is_squarefree(n):
    if n <= 1:
        return n == 1
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


def parse_pg_array(s):
    """Parse a postgres text array like {2,3,5} or [2,3,5] into list of ints."""
    if s is None:
        return []
    s = s.strip()
    for ch in '{}[]':
        s = s.replace(ch, '')
    if not s:
        return []
    parts = [x.strip() for x in s.split(',') if x.strip()]
    result = []
    for p in parts:
        try:
            result.append(int(p))
        except:
            result.append(p)
    return result


# ── Phase 1: Complete census ─────────────────────────────────────────────────

def phase1_census():
    print("\n" + "=" * 70)
    print("PHASE 1: Complete Census of Rank >= 4 Curves")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT lmfdb_label, rank::int, conductor, "absD",
               num_bad_primes::int, bad_primes, semistable,
               torsion::int, sha::int, regulator,
               faltings_height, szpiro_ratio, abc_quality,
               cm::int, "signD"::int, class_size::int,
               isogeny_degrees, torsion_structure, degree, ainvs
        FROM ec_curvedata
        WHERE rank::int >= 4
        ORDER BY rank::int DESC, conductor::bigint ASC
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    print(f"  Total rank >= 4 curves: {len(rows)}")

    curves = []
    for row in rows:
        d = dict(zip(cols, row))
        curves.append(d)

    # Count by rank
    rank_counts = Counter(int(c['rank']) for c in curves)
    print(f"  Rank distribution: {dict(sorted(rank_counts.items()))}")

    # --- disc / conductor ratio ---
    print("\n  --- Discriminant / Conductor Ratio ---")
    ratio_stats = defaultdict(list)
    exact_match = defaultdict(int)
    close_match = defaultdict(int)  # within 1%

    for c in curves:
        r = int(c['rank'])
        cond = safe_float(c['conductor'])
        absD = safe_float(c['absD'])
        if cond and absD and cond > 0 and absD > 0:
            log_ratio = math.log(absD) / math.log(cond) if cond > 1 else None
            ratio = absD / cond
            ratio_stats[r].append({
                'label': c['lmfdb_label'],
                'conductor': cond,
                'absD': absD,
                'ratio': ratio,
                'log_ratio': log_ratio
            })
            if abs(ratio - 1.0) < 1e-9:
                exact_match[r] += 1
            if abs(ratio - 1.0) < 0.01:
                close_match[r] += 1

    for r in sorted(ratio_stats.keys()):
        ratios = [x['ratio'] for x in ratio_stats[r]]
        log_ratios = [x['log_ratio'] for x in ratio_stats[r] if x['log_ratio'] is not None]
        n = len(ratios)
        n_exact = exact_match[r]
        n_close = close_match[r]
        print(f"\n  Rank {r}: {n} curves")
        print(f"    disc == cond exactly: {n_exact}/{n} ({100*n_exact/n:.1f}%)")
        print(f"    disc ~= cond (1%):    {n_close}/{n} ({100*n_close/n:.1f}%)")
        print(f"    ratio min={min(ratios):.6g}, max={max(ratios):.6g}, "
              f"median={sorted(ratios)[n//2]:.6g}")
        if log_ratios:
            print(f"    log(disc)/log(cond) min={min(log_ratios):.6f}, "
                  f"max={max(log_ratios):.6f}, median={sorted(log_ratios)[len(log_ratios)//2]:.6f}")
        # Show some examples where ratio != 1
        outliers = [x for x in ratio_stats[r] if abs(x['ratio'] - 1.0) > 0.01]
        if outliers:
            print(f"    Outliers (ratio far from 1): {len(outliers)}")
            for o in outliers[:5]:
                print(f"      {o['label']}: disc={o['absD']:.0f}, cond={o['conductor']:.0f}, "
                      f"ratio={o['ratio']:.6g}")

    # --- Conductor properties ---
    print("\n  --- Conductor Properties ---")
    for r in sorted(rank_counts.keys()):
        conds = [safe_int(c['conductor']) for c in curves if int(c['rank']) == r]
        conds = [x for x in conds if x is not None]
        n_prime = sum(1 for x in conds if is_prime(x))
        n_sqfree = sum(1 for x in conds if is_squarefree(x))
        print(f"\n  Rank {r}: {len(conds)} conductors")
        print(f"    Prime: {n_prime}/{len(conds)} ({100*n_prime/len(conds):.1f}%)")
        print(f"    Squarefree: {n_sqfree}/{len(conds)} ({100*n_sqfree/len(conds):.1f}%)")
        print(f"    Range: {min(conds)} to {max(conds)}")
        print(f"    Median: {sorted(conds)[len(conds)//2]}")

    # --- Torsion ---
    print("\n  --- Torsion Distribution ---")
    for r in sorted(rank_counts.keys()):
        tors = Counter(safe_int(c['torsion']) for c in curves if int(c['rank']) == r)
        print(f"  Rank {r}: {dict(sorted(tors.items()))}")
        tors_struct = Counter(c['torsion_structure'] for c in curves if int(c['rank']) == r)
        print(f"    Structures: {dict(sorted(tors_struct.items(), key=lambda x: str(x[0])))}")

    # --- Sha ---
    print("\n  --- Sha Distribution ---")
    for r in sorted(rank_counts.keys()):
        shas = Counter(safe_int(c['sha']) for c in curves if int(c['rank']) == r)
        print(f"  Rank {r}: {dict(sorted(shas.items()))}")

    # --- CM ---
    print("\n  --- CM Status ---")
    for r in sorted(rank_counts.keys()):
        cm_vals = Counter(safe_int(c['cm']) for c in curves if int(c['rank']) == r)
        print(f"  Rank {r}: {dict(sorted(cm_vals.items()))}")

    # --- Semistable ---
    print("\n  --- Semistable Status ---")
    for r in sorted(rank_counts.keys()):
        ss = Counter(c['semistable'] for c in curves if int(c['rank']) == r)
        print(f"  Rank {r}: {dict(sorted(ss.items(), key=lambda x: str(x[0])))}")

    conn.close()

    return {
        'total_curves': len(curves),
        'rank_counts': {str(k): v for k, v in sorted(rank_counts.items())},
        'ratio_stats': {
            str(r): {
                'n': len(ratio_stats[r]),
                'exact_match': exact_match[r],
                'close_match': close_match[r],
                'ratio_min': min(x['ratio'] for x in ratio_stats[r]),
                'ratio_max': max(x['ratio'] for x in ratio_stats[r]),
                'ratio_median': sorted(x['ratio'] for x in ratio_stats[r])[len(ratio_stats[r])//2],
            }
            for r in sorted(ratio_stats.keys())
        },
        'curves_detail': [
            {
                'label': c['lmfdb_label'],
                'rank': safe_int(c['rank']),
                'conductor': safe_int(c['conductor']),
                'absD': c['absD'],
                'num_bad_primes': safe_int(c['num_bad_primes']),
                'bad_primes': c['bad_primes'],
                'semistable': c['semistable'],
                'torsion': safe_int(c['torsion']),
                'sha': safe_int(c['sha']),
                'cm': safe_int(c['cm']),
                'class_size': safe_int(c['class_size']),
                'isogeny_degrees': c['isogeny_degrees'],
                'regulator': c['regulator'],
                'szpiro_ratio': c['szpiro_ratio'],
            }
            for c in curves
        ]
    }


# ── Phase 2: Bad prime characterization ──────────────────────────────────────

def phase2_bad_primes():
    print("\n" + "=" * 70)
    print("PHASE 2: Bad Prime Characterization")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT lmfdb_label, rank::int, conductor, "absD",
               num_bad_primes::int, bad_primes, semistable
        FROM ec_curvedata
        WHERE rank::int >= 4
        ORDER BY rank::int, conductor::bigint
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    results = defaultdict(lambda: {
        'num_bad_primes_dist': Counter(),
        'single_bad_is_conductor': 0,
        'single_bad_not_conductor': 0,
        'multi_bad_examples': [],
        'bad_prime_frequency': Counter(),
    })

    for row in rows:
        d = dict(zip(cols, row))
        r = int(d['rank'])
        nbp = safe_int(d['num_bad_primes']) or 0
        cond = safe_int(d['conductor'])
        bp = parse_pg_array(d['bad_primes'])

        res = results[r]
        res['num_bad_primes_dist'][nbp] += 1

        for p in bp:
            if isinstance(p, int):
                res['bad_prime_frequency'][p] += 1

        if nbp == 1 and len(bp) == 1 and cond is not None:
            if isinstance(bp[0], int) and bp[0] == cond:
                res['single_bad_is_conductor'] += 1
            else:
                res['single_bad_not_conductor'] += 1

        if nbp > 1:
            res['multi_bad_examples'].append({
                'label': d['lmfdb_label'],
                'conductor': cond,
                'bad_primes': bp,
                'num_bad_primes': nbp,
                'semistable': d['semistable'],
            })

    for r in sorted(results.keys()):
        res = results[r]
        print(f"\n  Rank {r}:")
        print(f"    num_bad_primes distribution: {dict(sorted(res['num_bad_primes_dist'].items()))}")
        total_single = res['single_bad_is_conductor'] + res['single_bad_not_conductor']
        if total_single > 0:
            print(f"    Single bad prime == conductor: {res['single_bad_is_conductor']}/{total_single}")
            print(f"    Single bad prime != conductor: {res['single_bad_not_conductor']}/{total_single}")
        n_multi = len(res['multi_bad_examples'])
        if n_multi > 0:
            print(f"    Curves with >1 bad prime: {n_multi}")
            for ex in res['multi_bad_examples'][:10]:
                print(f"      {ex['label']}: cond={ex['conductor']}, "
                      f"bad_primes={ex['bad_primes']}, semistable={ex['semistable']}")
        # Top bad primes
        top_bp = res['bad_prime_frequency'].most_common(15)
        print(f"    Top bad primes: {top_bp}")

    conn.close()

    return {
        str(r): {
            'num_bad_primes_dist': {str(k): v for k, v in sorted(res['num_bad_primes_dist'].items())},
            'single_bad_is_conductor': res['single_bad_is_conductor'],
            'single_bad_not_conductor': res['single_bad_not_conductor'],
            'n_multi_bad': len(res['multi_bad_examples']),
            'multi_bad_examples': res['multi_bad_examples'][:20],
        }
        for r, res in sorted(results.items())
    }


# ── Phase 3: Isogeny structure ───────────────────────────────────────────────

def phase3_isogeny():
    print("\n" + "=" * 70)
    print("PHASE 3: Isogeny Structure")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT lmfdb_label, rank::int, class_size::int, isogeny_degrees
        FROM ec_curvedata
        WHERE rank::int >= 4
        ORDER BY rank::int, conductor::bigint
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    results = defaultdict(lambda: {
        'class_size_dist': Counter(),
        'isogeny_degree_dist': Counter(),
        'nontrivial_isogeny': [],
    })

    for row in rows:
        d = dict(zip(cols, row))
        r = int(d['rank'])
        cs = safe_int(d['class_size'])
        iso_deg = d['isogeny_degrees']

        res = results[r]
        res['class_size_dist'][cs] += 1
        res['isogeny_degree_dist'][iso_deg] += 1

        if cs is not None and cs > 1:
            res['nontrivial_isogeny'].append({
                'label': d['lmfdb_label'],
                'class_size': cs,
                'isogeny_degrees': iso_deg,
            })

    for r in sorted(results.keys()):
        res = results[r]
        print(f"\n  Rank {r}:")
        print(f"    Class size distribution: {dict(sorted(res['class_size_dist'].items()))}")
        n_nontrivial = len(res['nontrivial_isogeny'])
        total = sum(res['class_size_dist'].values())
        print(f"    Non-trivial isogeny classes: {n_nontrivial}/{total}")
        if n_nontrivial > 0:
            for ex in res['nontrivial_isogeny'][:10]:
                print(f"      {ex['label']}: class_size={ex['class_size']}, "
                      f"degrees={ex['isogeny_degrees']}")
        # Top isogeny degree patterns
        top_iso = res['isogeny_degree_dist'].most_common(10)
        print(f"    Top isogeny degree patterns: {top_iso}")

    conn.close()

    return {
        str(r): {
            'class_size_dist': {str(k): v for k, v in sorted(res['class_size_dist'].items())},
            'n_nontrivial_isogeny': len(res['nontrivial_isogeny']),
            'nontrivial_examples': res['nontrivial_isogeny'][:20],
        }
        for r, res in sorted(results.items())
    }


# ── Phase 4: Predictions for rank 5+ ─────────────────────────────────────────

def phase4_predictions():
    print("\n" + "=" * 70)
    print("PHASE 4: Predictions for Rank 5+")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    # All rank >= 4 with key fields
    cur.execute("""
        SELECT lmfdb_label, rank::int, conductor::bigint,
               "absD", num_bad_primes::int, bad_primes,
               semistable, regulator, szpiro_ratio
        FROM ec_curvedata
        WHERE rank::int >= 4
        ORDER BY rank::int, conductor::bigint
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    # Rank 5 detail
    rank5 = [dict(zip(cols, r)) for r in rows if int(r[1]) == 5]
    print(f"\n  Rank 5 curves: {len(rank5)}")
    corridor_fit_5 = 0
    for c in rank5:
        cond = int(c['conductor'])
        absD = safe_float(c['absD'])
        nbp = safe_int(c['num_bad_primes'])
        ratio = absD / cond if absD and cond else None
        fits = (nbp == 1) and (ratio is not None and abs(ratio - 1.0) < 0.01)
        if fits:
            corridor_fit_5 += 1
        ratio_str = f"{ratio:.6g}" if ratio else "N/A"
        print(f"    {c['lmfdb_label']}: cond={cond}, disc={absD}, "
              f"ratio={ratio_str}, nbp={nbp}, "
              f"semi={c['semistable']}, reg={c['regulator']}, "
              f"fits_corridor={fits}")

    print(f"\n  Rank 5 corridor fit: {corridor_fit_5}/{len(rank5)}")

    # Min conductor by rank
    print("\n  --- Minimum conductor by rank ---")
    min_cond = {}
    max_cond = {}
    for row in rows:
        d = dict(zip(cols, row))
        r = int(d['rank'])
        cond = int(d['conductor'])
        if r not in min_cond or cond < min_cond[r]:
            min_cond[r] = cond
        if r not in max_cond or cond > max_cond[r]:
            max_cond[r] = cond

    for r in sorted(min_cond.keys()):
        print(f"    Rank {r}: min_cond={min_cond[r]}, max_cond={max_cond[r]}")

    # Also get rank 0-3 min conductors for comparison
    cur.execute("""
        SELECT rank::int as r, MIN(conductor::bigint) as min_c, MAX(conductor::bigint) as max_c
        FROM ec_curvedata
        WHERE rank::int BETWEEN 0 AND 3
        GROUP BY rank::int
        ORDER BY r
    """)
    for row in cur.fetchall():
        print(f"    Rank {row[0]}: min_cond={row[1]}, max_cond={row[2]}")

    # Log-log scaling: log(min_cond) vs rank
    print("\n  --- Log(min_conductor) scaling ---")
    for r in sorted(min_cond.keys()):
        print(f"    Rank {r}: log(min_cond) = {math.log(min_cond[r]):.4f}")

    # Szpiro ratio distribution
    print("\n  --- Szpiro Ratio by Rank ---")
    for rank_val in sorted(min_cond.keys()):
        szpiros = [safe_float(d['szpiro_ratio'])
                   for d in (dict(zip(cols, r)) for r in rows)
                   if int(d['rank']) == rank_val and safe_float(d['szpiro_ratio']) is not None]
        if szpiros:
            szpiros.sort()
            print(f"    Rank {rank_val}: n={len(szpiros)}, "
                  f"min={szpiros[0]:.4f}, median={szpiros[len(szpiros)//2]:.4f}, "
                  f"max={szpiros[-1]:.4f}")

    conn.close()

    return {
        'rank5_detail': [
            {
                'label': c['lmfdb_label'],
                'conductor': int(c['conductor']),
                'absD': c['absD'],
                'num_bad_primes': safe_int(c['num_bad_primes']),
                'semistable': c['semistable'],
                'regulator': c['regulator'],
            }
            for c in rank5
        ],
        'rank5_corridor_fit': corridor_fit_5,
        'min_conductor_by_rank': {str(k): v for k, v in sorted(min_cond.items())},
        'max_conductor_by_rank': {str(k): v for k, v in sorted(max_cond.items())},
    }


# ── Phase 5: Comparison to random curves at same conductors ──────────────────

def phase5_comparison():
    print("\n" + "=" * 70)
    print("PHASE 5: Comparison — Same Conductors, Different Ranks")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    # Get distinct conductors for rank 4 curves
    cur.execute("""
        SELECT DISTINCT conductor::bigint
        FROM ec_curvedata
        WHERE rank::int = 4
        ORDER BY conductor::bigint
    """)
    rank4_conds = [r[0] for r in cur.fetchall()]
    print(f"  Distinct rank-4 conductors: {len(rank4_conds)}")

    # Sample: take first 200 conductors (or all if fewer)
    sample_conds = rank4_conds[:500]

    # For these conductors, get ALL curves of any rank
    if sample_conds:
        cur.execute("""
            SELECT lmfdb_label, rank::int, conductor::bigint, "absD",
                   num_bad_primes::int, semistable
            FROM ec_curvedata
            WHERE conductor::bigint = ANY(%s)
            ORDER BY conductor::bigint, rank::int
        """, (sample_conds,))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        print(f"  Total curves at those conductors: {len(rows)}")

        # Compare disc/cond ratio by rank at these conductors
        ratio_by_rank = defaultdict(list)
        nbp_by_rank = defaultdict(list)
        semi_by_rank = defaultdict(int)
        count_by_rank = Counter()

        for row in rows:
            d = dict(zip(cols, row))
            r = int(d['rank'])
            cond = int(d['conductor'])
            absD = safe_float(d['absD'])
            nbp = safe_int(d['num_bad_primes'])
            count_by_rank[r] += 1

            if absD and cond > 0:
                ratio_by_rank[r].append(absD / cond)
            if nbp is not None:
                nbp_by_rank[r].append(nbp)
            if d['semistable'] in ('t', 'True', True, '1', 'true'):
                semi_by_rank[r] += 1

        print(f"\n  Curves at rank-4 conductors, by rank: {dict(sorted(count_by_rank.items()))}")

        for r in sorted(ratio_by_rank.keys()):
            ratios = ratio_by_rank[r]
            nbps = nbp_by_rank[r]
            n = count_by_rank[r]
            n_exact = sum(1 for x in ratios if abs(x - 1.0) < 1e-9)
            n_close = sum(1 for x in ratios if abs(x - 1.0) < 0.01)
            n_nbp1 = sum(1 for x in nbps if x == 1)
            n_semi = semi_by_rank[r]
            print(f"\n    Rank {r} (n={n}):")
            print(f"      disc==cond exactly: {n_exact}/{len(ratios)} ({100*n_exact/max(len(ratios),1):.1f}%)")
            print(f"      disc~=cond (1%):    {n_close}/{len(ratios)} ({100*n_close/max(len(ratios),1):.1f}%)")
            print(f"      num_bad_primes==1:  {n_nbp1}/{len(nbps)} ({100*n_nbp1/max(len(nbps),1):.1f}%)")
            print(f"      semistable:         {n_semi}/{n} ({100*n_semi/max(n,1):.1f}%)")
            if ratios:
                ratios_s = sorted(ratios)
                print(f"      ratio: min={ratios_s[0]:.6g}, median={ratios_s[len(ratios_s)//2]:.6g}, "
                      f"max={ratios_s[-1]:.6g}")
    else:
        print("  No rank-4 conductors found!")

    # Also compare: for a RANDOM sample of conductors that DON'T have rank-4 curves
    print("\n  --- Control: Random conductors WITHOUT rank-4 curves ---")
    # Get conductors that are in a similar range but have no rank-4 curve
    if rank4_conds:
        median_cond = rank4_conds[len(rank4_conds) // 2]
        lo = max(1, rank4_conds[0])
        hi = rank4_conds[-1]
        cur.execute("""
            SELECT conductor::bigint, "absD",
                   num_bad_primes::int, semistable, rank::int
            FROM ec_curvedata
            WHERE conductor::bigint BETWEEN %s AND %s
              AND conductor::bigint NOT IN (
                  SELECT DISTINCT conductor::bigint FROM ec_curvedata WHERE rank::int >= 4
              )
            ORDER BY RANDOM()
            LIMIT 5000
        """, (lo, hi))
        control_rows = cur.fetchall()
        print(f"  Control sample (same conductor range, no rank-4): {len(control_rows)} curves")

        if control_rows:
            ctrl_ratios = []
            ctrl_nbp1 = 0
            ctrl_semi = 0
            for row in control_rows:
                cond = int(row[0])
                absD = safe_float(row[1])
                nbp = safe_int(row[2])
                if absD and cond > 0:
                    ctrl_ratios.append(absD / cond)
                if nbp == 1:
                    ctrl_nbp1 += 1
                if row[3] in ('t', 'True', True, '1', 'true'):
                    ctrl_semi += 1

            n_exact = sum(1 for x in ctrl_ratios if abs(x - 1.0) < 1e-9)
            n_close = sum(1 for x in ctrl_ratios if abs(x - 1.0) < 0.01)
            print(f"    disc==cond exactly: {n_exact}/{len(ctrl_ratios)} ({100*n_exact/max(len(ctrl_ratios),1):.1f}%)")
            print(f"    disc~=cond (1%):    {n_close}/{len(ctrl_ratios)} ({100*n_close/max(len(ctrl_ratios),1):.1f}%)")
            print(f"    num_bad_primes==1:  {ctrl_nbp1}/{len(control_rows)} ({100*ctrl_nbp1/max(len(control_rows),1):.1f}%)")
            print(f"    semistable:         {ctrl_semi}/{len(control_rows)} ({100*ctrl_semi/max(len(control_rows),1):.1f}%)")
            if ctrl_ratios:
                ctrl_s = sorted(ctrl_ratios)
                print(f"    ratio: min={ctrl_s[0]:.6g}, median={ctrl_s[len(ctrl_s)//2]:.6g}, "
                      f"max={ctrl_s[-1]:.6g}")

    conn.close()

    return {
        'n_rank4_conductors': len(rank4_conds),
        'conductor_range': [rank4_conds[0], rank4_conds[-1]] if rank4_conds else [],
    }


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 70)
    print("RANK-4 CORRIDOR INVESTIGATION")
    print("Charon — 2026-04-15")
    print("=" * 70)

    results = {}
    results['phase1'] = phase1_census()
    results['phase2'] = phase2_bad_primes()
    results['phase3'] = phase3_isogeny()
    results['phase4'] = phase4_predictions()
    results['phase5'] = phase5_comparison()

    elapsed = time.time() - t0
    results['elapsed_seconds'] = round(elapsed, 1)
    print(f"\n\nTotal elapsed: {elapsed:.1f}s")

    # Save — convert any non-serializable types
    def default_ser(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return str(obj)

    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2, default=default_ser)
    print(f"\nResults saved to {OUT}")


if __name__ == '__main__':
    main()
