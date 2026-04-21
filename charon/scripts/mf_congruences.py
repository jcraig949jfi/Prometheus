"""
Aporia Deep Research Report #27: Modular form congruences (Ramanujan-type).

For dim=1 newforms, traces[n] = a_{n+1} (0-indexed), i.e. traces[0]=a_1=1.
Two forms f,g are congruent mod p if a_ell(f) = a_ell(g) (mod p)
for all primes ell up to the Sturm bound (not dividing the level).
"""

import json
import time
import psycopg2
from collections import defaultdict
from fractions import Fraction

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')

def sieve_primes(n):
    if n < 2: return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]

PRIMES_1000 = sieve_primes(1000)
PRIME_SET_1000 = set(PRIMES_1000)

def sigma_mod(n, k, p):
    """sigma_k(n) mod p, computed efficiently."""
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s = (s + pow(d, k, p)) % p
    return s

def bernoulli(n_max):
    """Compute B_0 through B_{n_max} using the standard recurrence.
    B_m = -1/(m+1) * sum_{k=0}^{m-1} C(m+1,k) * B_k
    """
    from math import comb
    B = [Fraction(0)] * (n_max + 1)
    B[0] = Fraction(1)
    for m in range(1, n_max + 1):
        s = Fraction(0)
        for k in range(m):
            s += Fraction(comb(m + 1, k)) * B[k]
        B[m] = -s / (m + 1)
    return B

_bernoulli_cache = None
def bernoulli_even(k):
    """B_k using cached table."""
    global _bernoulli_cache
    if _bernoulli_cache is None or k >= len(_bernoulli_cache):
        _bernoulli_cache = bernoulli(max(k, 50))
    return _bernoulli_cache[k]

def eisenstein_primes(k_max):
    """For even k, find primes p dividing numerator of B_k/(2k).
    Only check primes up to 10000 to avoid trial-division explosion on huge numerators."""
    small_primes = sieve_primes(10000)
    result = {}
    for k in range(2, k_max + 1, 2):
        Bk = bernoulli_even(k)
        ratio = Bk / (2 * k)
        num = abs(ratio.numerator)
        primes = [p for p in small_primes if num % p == 0]
        result[k] = {'ratio': str(ratio), 'numerator': str(num), 'primes': primes}
    return result

def main():
    t0 = time.time()
    results = {'report': 'Aporia Deep Research #27: Modular form congruences', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}

    # === Eisenstein table ===
    print("Computing Eisenstein table...")
    eis = eisenstein_primes(50)
    results['eisenstein_table'] = {}
    for k, v in eis.items():
        results['eisenstein_table'][str(k)] = v
        if v['primes']:
            print(f"  B_{k}/(2*{k}) = {v['ratio']}, primes dividing numerator: {v['primes']}")

    test_primes = [2, 3, 5, 7, 11, 13, 17, 691]

    # === Load forms ===
    print("\nLoading dim=1 forms (level <= 500)...")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM mf_newforms WHERE dim='1' AND traces IS NOT NULL")
    total_dim1 = cur.fetchone()[0]
    print(f"  Total dim=1 forms with traces: {total_dim1}")

    # Use CAST for reliable int comparison; limit level for speed
    cur.execute("""
        SELECT label, CAST(level AS int), CAST(weight AS int), CAST(char_order AS int), traces
        FROM mf_newforms
        WHERE dim='1' AND traces IS NOT NULL AND CAST(level AS int) <= 500
        ORDER BY CAST(level AS int), CAST(weight AS int)
    """)
    rows = cur.fetchall()
    print(f"  Loaded {len(rows)} rows")

    forms = []
    for label, level, weight, char_order, traces_str in rows:
        try:
            traces_raw = json.loads(traces_str)
            forms.append({
                'label': label, 'level': level, 'weight': weight,
                'char_order': char_order,
                'traces': [int(t) for t in traces_raw]
            })
        except:
            pass
    print(f"  Parsed {len(forms)} forms")
    print(f"  Time so far: {time.time()-t0:.1f}s")

    # === Ramanujan's congruence ===
    print("\n=== Ramanujan: tau(n) = sigma_11(n) (mod 691) ===")
    delta = [f for f in forms if f['level'] == 1 and f['weight'] == 12]
    if delta:
        delta = delta[0]
        n_check = min(50, len(delta['traces']))
        mismatches = []
        for n in range(1, n_check + 1):
            tau_n = delta['traces'][n - 1]
            sig_n = sigma_mod(n, 11, 691)
            if tau_n % 691 != sig_n:
                mismatches.append(n)
        verified = len(mismatches) == 0
        print(f"  {'VERIFIED' if verified else 'FAILED'}: checked n=1..{n_check}, mismatches={mismatches}")
        # Show first few tau values
        print(f"  tau(1..5) = {delta['traces'][:5]}")
        print(f"  tau(2) mod 691 = {delta['traces'][1] % 691}, sigma_11(2) mod 691 = {sigma_mod(2, 11, 691)}")
        results['ramanujan_691'] = {
            'verified': verified, 'n_checked': n_check, 'mismatches': mismatches,
            'first_tau': delta['traces'][:12]
        }
    else:
        results['ramanujan_691'] = {'verified': False, 'error': 'not found'}

    # === Systematic congruence search ===
    print("\n=== Systematic congruence search ===")
    # Focus on trivial character forms
    triv_forms = [f for f in forms if f['char_order'] == 1]
    print(f"  Trivial character forms: {len(triv_forms)}")

    congruence_results = {}
    for p in test_primes:
        print(f"\n--- mod {p} ---")
        fp_groups = defaultdict(list)

        for f in triv_forms:
            N, k = f['level'], f['weight']
            traces = f['traces']
            max_idx = min(len(traces), 500)
            # Primes not dividing level, up to available data
            check_ells = [ell for ell in PRIMES_1000 if ell <= max_idx and N % ell != 0][:30]
            if len(check_ells) < 5:
                continue

            fp = tuple(traces[ell - 1] % p for ell in check_ells)
            fp_groups[fp].append({'label': f['label'], 'level': N, 'weight': k})

        # Analyze collisions
        cross_groups = []
        same_lw_collision = 0
        for fp, group in fp_groups.items():
            if len(group) < 2:
                continue
            lw_set = set((g['level'], g['weight']) for g in group)
            if len(lw_set) > 1:
                cross_groups.append({
                    'n_forms': len(group),
                    'distinct_lw': sorted([list(x) for x in lw_set]),
                    'forms': [g['label'] for g in group[:8]],
                    'fingerprint_sample': list(fp[:8])
                })
            else:
                same_lw_collision += 1

        cross_groups.sort(key=lambda x: -x['n_forms'])
        total_coll = len(cross_groups) + same_lw_collision

        print(f"  Total collision groups: {total_coll}")
        print(f"  Cross-(level,weight) groups: {len(cross_groups)}")
        print(f"  Same-(level,weight) groups: {same_lw_collision}")
        for cg in cross_groups[:5]:
            print(f"    {cg['n_forms']} forms across {cg['distinct_lw'][:4]}: {cg['forms'][:4]}")

        congruence_results[str(p)] = {
            'total_collision_groups': total_coll,
            'cross_lw_groups': len(cross_groups),
            'same_lw_groups': same_lw_collision,
            'top_examples': cross_groups[:15]
        }

    results['congruence_search'] = congruence_results

    # === Level-1 deep dive ===
    print("\n=== Level-1 forms ===")
    l1 = sorted([f for f in triv_forms if f['level'] == 1], key=lambda f: f['weight'])
    print(f"  {len(l1)} level-1 forms")
    for f in l1:
        print(f"    {f['label']}: k={f['weight']}, a_2={f['traces'][1]}, a_3={f['traces'][2]}")

    l1_congs = []
    for i in range(len(l1)):
        for j in range(i+1, len(l1)):
            fi, fj = l1[i], l1[j]
            max_c = min(len(fi['traces']), len(fj['traces']), 500)
            check_ells = [ell for ell in PRIMES_1000 if ell <= max_c][:40]
            if len(check_ells) < 5:
                continue
            for p in test_primes:
                agree = all(fi['traces'][ell-1] % p == fj['traces'][ell-1] % p for ell in check_ells)
                if agree:
                    l1_congs.append({
                        'form1': fi['label'], 'w1': fi['weight'],
                        'form2': fj['label'], 'w2': fj['weight'],
                        'prime': p, 'n_checked': len(check_ells)
                    })
                    print(f"  CONGRUENCE: {fi['label']}(k={fi['weight']}) = {fj['label']}(k={fj['weight']}) mod {p}")
    results['level1_congruences'] = l1_congs

    # === Eisenstein verification ===
    # IMPORTANT: traces are stored as float64 in LMFDB JSON, so for high-weight
    # forms the eigenvalues lose precision beyond ~15 digits. We only check primes
    # ell where |a_ell| < 10^15 to avoid float truncation artifacts.
    FLOAT_SAFE = 10**15
    print("\n=== Eisenstein congruence verification ===")
    print("  (Note: only checking primes ell where |a_ell| < 10^15 due to float64 storage)")
    eis_verif = []
    for f in l1:
        k = f['weight']
        if k not in eis:
            continue
        for p in eis[k]['primes']:
            if p > 10000:
                continue
            max_c = min(len(f['traces']), 200)
            check_ells = [ell for ell in PRIMES_1000
                          if ell <= max_c and abs(f['traces'][ell-1]) < FLOAT_SAFE][:20]
            if len(check_ells) < 3:
                continue
            agree = all(f['traces'][ell-1] % p == sigma_mod(ell, k-1, p) for ell in check_ells)
            status = "VERIFIED" if agree else "FAILED"
            print(f"  {f['label']}(k={k}) vs E_{k} mod {p}: {status} ({len(check_ells)} primes, max_ell={check_ells[-1]})")
            eis_verif.append({
                'form': f['label'], 'weight': k, 'prime': p,
                'verified': agree, 'n_checked': len(check_ells),
                'max_ell_checked': check_ells[-1]
            })
    results['eisenstein_verifications'] = eis_verif
    results['float_precision_note'] = (
        'LMFDB stores traces as float64 JSON. For weights >= 20, eigenvalues at '
        'large primes exceed 10^15 and lose precision. Eisenstein verification '
        'restricted to primes where |a_ell| < 10^15.'
    )

    # === Congruence density by level ===
    print("\n=== Congruence density (mod 2, by level) ===")
    # For each level, how many mod-2 fingerprint collision groups?
    level_counts = defaultdict(int)
    for f in triv_forms:
        level_counts[f['level']] += 1

    density_data = []
    for N in sorted(level_counts.keys())[:30]:
        lf = [f for f in triv_forms if f['level'] == N]
        if len(lf) < 2:
            continue
        fps = defaultdict(list)
        for f in lf:
            max_idx = min(len(f['traces']), 200)
            ce = [ell for ell in PRIMES_1000 if ell <= max_idx and N % ell != 0][:20]
            if len(ce) < 3:
                continue
            fp = tuple(f['traces'][ell-1] % 2 for ell in ce)
            fps[fp].append(f['label'])
        n_coll = sum(1 for g in fps.values() if len(g) >= 2)
        largest = max((len(g) for g in fps.values()), default=0)
        density_data.append({'level': N, 'n_forms': len(lf), 'collision_groups_mod2': n_coll, 'largest': largest})
        print(f"  N={N}: {len(lf)} forms, {n_coll} collision groups, largest={largest}")
    results['density_mod2'] = density_data

    # === trace_hash collisions (any dimension) ===
    print("\n=== trace_hash collisions (all dims) ===")
    cur.execute("""
        SELECT trace_hash, COUNT(*) as cnt FROM mf_newforms
        WHERE trace_hash IS NOT NULL
        GROUP BY trace_hash HAVING COUNT(*) > 1
        ORDER BY cnt DESC LIMIT 15
    """)
    hash_colls = []
    for h, cnt in cur.fetchall():
        cur.execute("""
            SELECT label, level, weight, dim FROM mf_newforms
            WHERE trace_hash=%s LIMIT 5
        """, (h,))
        exs = [{'label': l, 'level': n, 'weight': w, 'dim': d} for l, n, w, d in cur.fetchall()]
        print(f"  hash={h}: {cnt} forms, e.g. {[e['label'] for e in exs]}")
        hash_colls.append({'hash': str(h), 'count': cnt, 'examples': exs})
    results['trace_hash_collisions'] = hash_colls

    conn.close()

    # === Summary ===
    elapsed = time.time() - t0
    results['elapsed_seconds'] = round(elapsed, 1)
    total_cross = sum(v['cross_lw_groups'] for v in congruence_results.values())
    results['summary'] = {
        'n_forms_analyzed': len(forms),
        'n_trivial_char': len(triv_forms),
        'n_dim1_total': total_dim1,
        'level_range': '1-500',
        'test_primes': test_primes,
        'total_cross_lw_congruence_groups': total_cross,
        'level1_congruences': len(l1_congs),
        'eisenstein_verifications': len(eis_verif),
        'eisenstein_all_passed': all(v['verified'] for v in eis_verif) if eis_verif else None,
        'ramanujan_691_verified': results.get('ramanujan_691', {}).get('verified', False)
    }

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Forms analyzed: {len(forms)} ({len(triv_forms)} trivial character)")
    print(f"  Cross-(level,weight) congruence groups: {total_cross}")
    print(f"  Level-1 congruences: {len(l1_congs)}")
    print(f"  Eisenstein verifications: {len(eis_verif)}, all passed: {results['summary']['eisenstein_all_passed']}")
    print(f"  Ramanujan mod 691: {results['summary']['ramanujan_691_verified']}")
    print(f"  Elapsed: {elapsed:.1f}s")

    with open('F:/Prometheus/charon/data/mf_congruences.json', 'w') as fout:
        json.dump(results, fout, indent=2, default=str)
    print(f"\nSaved to F:/Prometheus/charon/data/mf_congruences.json")

if __name__ == '__main__':
    main()
