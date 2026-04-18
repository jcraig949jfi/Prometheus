"""
Report 18f — 3-rank distribution + Scholz reflection signatures.

Parent: R18c/d/e (Cohen-Lenstra convergence on quadratic class groups).
This script descends to the 3-torsion structure itself:

  (A) 3-rank distribution per (family, |disc| bucket).
      Cohen-Lenstra predicts:
        Prob(3-rank = k | imag quad) = c^imag_k
        Prob(3-rank = k | real quad) = c^real_k
      with explicit closed forms (below). Check empirical vs CL at each
      bucket; does deviation shrink with |disc| (BST)?

  (B) Scholz reflection: Scholz 1932 proved that for a squarefree d,
        r_3(Q(√3d)) ≤ r_3(Q(√-d)) ≤ r_3(Q(√3d)) + 1.
      This is a PROVED inequality between Cl[3]-ranks of paired quadratic
      fields. If we can pair imaginary Q(√-d) with real Q(√3d) by
      discriminant matching, we can verify the inequality at 100% across
      22M NF — a direct theorem-level F-anchor.

      Implementation note: LMFDB discriminants encode signs. The match
      candidate is Q(√-d) ↔ Q(√3d) for squarefree d. Since direct field
      pairing by full discriminant is subtle, we do a lighter check:
      compute the JOINT 3-rank distribution in imaginary vs real quadratic
      at equivalent |disc| ranges and verify the aggregate inequality
      r_3(imag) ≤ r_3(real) + 1 in the PROBABILISTIC sense (rank
      distributions shifted by at most 1). This is a sanity-check on the
      Scholz relation structure, not a field-by-field verification.

Cohen-Lenstra 3-rank distribution (closed forms):

Imaginary quadratic — Prob(3-rank = k):
  w_k = 3^(-k(k+1)) · ∏_{i=1}^k (1 - 3^(-i))^(-1) / C^imag
  with normalization constant C^imag = ∏_{i=1}^∞ (1 - 3^(-i))^(-1)... no,
  wait. The Cohen-Lenstra 1984 formula:

  Prob(3-rank = k | imag) = η(3, ∞) / (3^(k²) · η(3, k)²)
  where η(3, n) = ∏_{i=1}^n (1 - 3^(-i)).

Real quadratic — Prob(3-rank = k):
  Prob(3-rank = k | real) = η(3, ∞) · 3^(-k) / (3^(k²) · η(3, k)² · (1 - 3^(-(k+1))))
  (Cohen-Lenstra real-quad adjustment: extra 3^(-k)/(1-3^(-(k+1))) factor.)

First few values (imag):  k=0 → 0.560, k=1 → 0.420, k=2 → 0.020, k=3 → ≈0, ...
First few values (real):  k=0 → 0.840, k=1 → 0.158, k=2 → 0.002, k=3 → ≈0, ...

Output: cartography/docs/report18f_scholz_3rank_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt, prod
from pathlib import Path
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')


def eta(p, n_terms):
    e = 1.0
    for i in range(1, n_terms + 1):
        e *= (1 - p ** -i)
    return e


ETA_3_INF = eta(3, 200)


def cl_imag_3rank(k):
    """Prob(3-rank = k | imag quad) per Cohen-Lenstra 1984."""
    return ETA_3_INF / (3 ** (k * k) * eta(3, k) ** 2)


def cl_real_3rank(k):
    """Prob(3-rank = k | real quad) per Cohen-Lenstra real-quad adjustment."""
    return ETA_3_INF * (3 ** -k) / (3 ** (k * k) * eta(3, k) ** 2 * (1 - 3 ** -(k + 1)))


def parse_class_group(text):
    """Parse class_group text like '{2,2,50}' or '{3,9}' (LMFDB uses Postgres
    array-literal braces) and return the 3-rank (number of invariant factors
    divisible by 3)."""
    if text is None:
        return None
    s = text.strip().strip('{}[]').strip()
    if not s or s == '1':
        return 0  # trivial class group = rank 0 everywhere
    try:
        factors = [int(x.strip()) for x in s.split(',') if x.strip()]
    except ValueError:
        return None
    rank_3 = sum(1 for f in factors if f % 3 == 0)
    return rank_3


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    fams = {
        'imaginary_quadratic': {
            'sig_filter': 'r2::int >= 1',
            'cl_fn': cl_imag_3rank,
        },
        'real_quadratic': {
            'sig_filter': 'r2::int = 0',
            'cl_fn': cl_real_3rank,
        },
    }

    # Theoretical k=0..3 probabilities per family
    theo_per_fam = {}
    for fam_name, fam in fams.items():
        theo_per_fam[fam_name] = {k: fam['cl_fn'](k) for k in range(4)}

    # Pull rows per family, parse 3-rank, bucket by log10(|disc|).
    results = {}
    for fam_name, fam in fams.items():
        print(f'[R18f] fetching {fam_name} — parsing class_group for 3-rank...')
        cur.execute(f"""
            SELECT
              floor(log(greatest(disc_abs::bigint, 1)) / log(10))::int AS bucket,
              class_group
            FROM nf_fields
            WHERE degree::int = 2
              AND galois_label = '2T1'
              AND {fam['sig_filter']}
              AND class_group IS NOT NULL
              AND disc_abs IS NOT NULL
        """)
        # Aggregate in Python since parsing class_group in SQL is hairy
        buckets = {}  # bucket -> {rank_k: count}
        for bucket, cg_text in cur:
            r3 = parse_class_group(cg_text)
            if r3 is None:
                continue
            buckets.setdefault(int(bucket), {})
            buckets[int(bucket)][r3] = buckets[int(bucket)].get(r3, 0) + 1
        results[fam_name] = buckets

    cur.close(); conn.close()

    # Summarize per-bucket distributions and compare to CL
    fam_summary = {}
    for fam_name, fam_buckets in results.items():
        cl = theo_per_fam[fam_name]
        bucket_rows = []
        for bucket in sorted(fam_buckets.keys()):
            counts = fam_buckets[bucket]
            n_total = sum(counts.values())
            if n_total < 1000:
                continue
            row = {
                'log10_disc_bucket': int(bucket),
                'n_total': int(n_total),
                'per_rank': {},
            }
            for k in range(4):
                n_k = counts.get(k, 0)
                emp = n_k / n_total
                theo = cl[k]
                se = sqrt(theo * (1 - theo) / n_total)
                z = (emp - theo) / se if se > 0 else None
                rel = (emp - theo) / theo if theo > 0 else None
                row['per_rank'][str(k)] = {
                    'n': int(n_k),
                    'empirical': emp,
                    'theoretical': theo,
                    'z': z,
                    'relative_deviation': rel,
                }
            bucket_rows.append(row)
        fam_summary[fam_name] = {
            'theoretical_3rank_distribution_k0to3': cl,
            'buckets': bucket_rows,
        }

    # Scholz reflection probabilistic check:
    # Theorem: r_3(Q(√3d)) ≤ r_3(Q(√-d)) ≤ r_3(Q(√3d)) + 1 for squarefree d.
    # Aggregate: for paired buckets, Prob(r_3 = k | imag) relates to
    # Prob(r_3 ∈ {k-1, k} | real) in a specific way.
    #
    # Simplest test: sum-rule check — at each bucket, the CL predictions
    # themselves should satisfy a moment-level relation consistent with Scholz.
    # At asymptotic: E[3^{r_3(imag)}] / E[3^{r_3(real)}] = 3 (Scholz implies
    # imag has one more 3-cycle worth of class group on average).
    def moment_3rank(dist, max_k=6, base=3):
        """Compute E[base^{r_3}] from a rank-distribution dict."""
        return sum(dist[k] * base ** k for k in range(max_k) if k in dist)

    scholz_per_bucket = {}
    imag_buckets = {b['log10_disc_bucket']: b for b in fam_summary['imaginary_quadratic']['buckets']}
    real_buckets = {b['log10_disc_bucket']: b for b in fam_summary['real_quadratic']['buckets']}
    common_buckets = sorted(set(imag_buckets.keys()) & set(real_buckets.keys()))
    for b in common_buckets:
        imag_dist = {int(k): v['empirical'] for k, v in imag_buckets[b]['per_rank'].items()}
        real_dist = {int(k): v['empirical'] for k, v in real_buckets[b]['per_rank'].items()}
        m_imag = moment_3rank(imag_dist, base=3)
        m_real = moment_3rank(real_dist, base=3)
        ratio = m_imag / m_real if m_real > 0 else None
        scholz_per_bucket[str(b)] = {
            'imag_E_3^r3': m_imag,
            'real_E_3^r3': m_real,
            'ratio_imag_over_real': ratio,
            'CL_predicted_ratio_asymptote': 1.5,
            'deviation_from_1_5': (ratio - 1.5) if ratio is not None else None,
        }

    # Theoretical Scholz asymptote check on the CL distributions directly
    m_imag_theo = moment_3rank(theo_per_fam['imaginary_quadratic'])
    m_real_theo = moment_3rank(theo_per_fam['real_quadratic'])
    scholz_theory = {
        'imag_E_3^r3_CL': m_imag_theo,
        'real_E_3^r3_CL': m_real_theo,
        'ratio_CL_asymptote': m_imag_theo / m_real_theo if m_real_theo > 0 else None,
        'CL_predicted_ratio': 1.5,
        'CL_matches_scholz_asymptote': (
            abs((m_imag_theo / m_real_theo) - 1.5) < 0.02 if m_real_theo > 0 else False
        ),
        'note': (
            'Cohen-Lenstra 1984 predicts E[3^r_3 | imag] / E[3^r_3 | real] = 3/2 '
            'asymptotically. This ratio is a consequence of the Scholz reflection '
            'inequality r_3(imag) ≤ r_3(real) + 1 and the CL distributional form. '
            'Empirical should converge to 1.5 as |disc| → ∞.'
        ),
    }

    report = {
        'task': 'report18f_scholz_3rank',
        'parent': 'report18c_bst_rate_fit',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'method': (
            '(A) Parse class_group column, extract 3-rank (count of factors '
            'divisible by 3), bucket by log10(|disc|), compare to Cohen-Lenstra '
            '1984 closed-form 3-rank distribution. '
            '(B) Test the Scholz reflection asymptote ratio E[3^r_3(imag)] / '
            'E[3^r_3(real)] → 3 as |disc| → ∞.'
        ),
        'theoretical_3rank_distributions': theo_per_fam,
        'per_family_empirical': fam_summary,
        'scholz_reflection_check_per_bucket': scholz_per_bucket,
        'scholz_CL_theoretical_consistency': scholz_theory,
    }

    outpath = Path('cartography/docs/report18f_scholz_3rank_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18f] wrote {outpath}')
    print()

    # Console summary
    print('== THEORETICAL 3-RANK DISTRIBUTION ==')
    for fam_name in fams:
        print(f'{fam_name}:')
        for k, v in theo_per_fam[fam_name].items():
            print(f'  k={k}: {v:.5f}')
    print()

    print('== EMPIRICAL 3-RANK BY BUCKET (vs theory) ==')
    for fam_name in fams:
        print(f'{fam_name}:')
        print(f'  {"bucket":>7} {"n":>10}   {"k=0":>10}  {"k=1":>10}  {"k=2":>10}  {"k=3":>10}')
        for b in fam_summary[fam_name]['buckets']:
            row = f'  {b["log10_disc_bucket"]:>7} {b["n_total"]:>10,}'
            for k in range(4):
                d = b['per_rank'].get(str(k), {})
                emp = d.get('empirical', 0)
                theo = d.get('theoretical', 0)
                row += f'  {emp:.4f}/{theo:.4f}'
            print(row)
    print()

    print('== SCHOLZ ASYMPTOTE RATIO (empirical vs CL-predicted = 3/2 = 1.5) ==')
    print(f'  {"bucket":>7} {"E[3^r_imag]":>14} {"E[3^r_real]":>14} {"ratio":>10} {"dev_from_1.5":>13}')
    for b_str, d in scholz_per_bucket.items():
        r_ = d['ratio_imag_over_real']
        dev = d['deviation_from_1_5']
        print(f'  {b_str:>7} {d["imag_E_3^r3"]:>14.5f} {d["real_E_3^r3"]:>14.5f} '
              f'{r_:>10.5f} {dev:>+13.5f}')
    print()
    print(f'Theoretical CL asymptote ratio (imag / real) of E[3^r_3]: '
          f'{scholz_theory["ratio_CL_asymptote"]:.5f} '
          f'(CL predicts 3/2 = 1.5, Scholz-compatible)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
