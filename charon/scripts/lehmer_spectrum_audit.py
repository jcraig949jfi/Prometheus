"""F014:P040 Lehmer spectrum — empirical min M(f) per degree on NF corpus.

Background:
  The Lehmer catalog (harmonia/memory/catalogs/lehmer.md) proposes the
  decidable measurement: enumerate min M(f) per degree d in [10, 60] over
  non-cyclotomic monic integer polynomials, fit m(d) = f_inf + C*d^(-alpha).
  The pair (f_inf, alpha) distinguishes stance A/B/C of the five applied
  lenses.

  Original F014:P040 was framed as "density-in-Salem-window" but that
  statistic is trivially 0 on NF defining polynomials (they are not
  reciprocal; M(p) typically ~ sqrt|disc| scale). Reframing here to the
  catalog's decidable measurement.

This audit:
  1. Pull all nf_fields rows per degree d in [2..60] (capped at 100K per
     degree for tractability); parse defining polynomial coeffs.
  2. Compute M(f) via techne.lib.mahler_measure (numpy roots).
  3. Report per-degree statistics:
       min / p1 / p5 / p50 / max     Mahler measures
       min_log_M_per_deg              Weil height lower bound
       n_near_lehmer                  count with M < 1.2
       is_cyclotomic_count            (M <= 1.001)
  4. Fit m(d) = f_inf + C*d^(-alpha) on (min M) across d.
  5. Save JSON; announce summary on discoveries.

NOTE: The NF corpus is biased toward small |disc| and typical Galois groups.
This is NOT a rigorous Lehmer enumeration (Mossinghoff does that for
reciprocals to degree 44). It is an empirical scan of what the LMFDB NF
corpus shows. Any M(f) < 1.17628 would be a Lehmer counterexample — but
none is expected from NF defining polynomials since those are minimal
polynomials of algebraic integers whose conjugates are not all on the unit
circle (otherwise the field would be cyclotomic).

Block-shuffle null is deferred: the density-in-Salem-window stat cannot
be tested when the observed value is exactly 0 (null mean = 0, std = 0).
Reporting the degenerate diagnosis explicitly.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from techne.lib.mahler_measure import mahler_measure

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
DEGREES = list(range(2, 61))
LEHMER_BOUND = 1.17628081825991750654407033847403505069341580657
CAP_PER_DEG = 10000       # cap per degree for tractability
MIN_PER_DEG = 200         # skip degrees with fewer NFs

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'data', 'lehmer_spectrum_audit.json')


def parse_coeffs(s):
    s = s.strip('{}[]')
    if not s:
        return None
    try:
        asc = [int(x.strip()) for x in s.split(',') if x.strip()]
        if len(asc) < 2:
            return None
        return asc[::-1]  # descending for numpy
    except ValueError:
        return None


def count_per_degree(cur):
    cur.execute("SELECT degree::int, COUNT(*) FROM nf_fields GROUP BY 1 ORDER BY 1")
    return dict(cur.fetchall())


def pull(cur, degree, cap):
    cur.execute("""
        SELECT disc_abs, coeffs, label
        FROM nf_fields
        WHERE degree = %s
          AND coeffs IS NOT NULL
        ORDER BY random()
        LIMIT %s
    """, (str(degree), cap))
    for row in cur:
        yield row


def mahler_stats(records, degree):
    """Compute M(f) for each; return arrays and lowest specimens."""
    ms = []
    disc_abs = []
    labels_low = []  # keep (M, disc, label) for bottom 10
    for disc_s, coeffs_s, label in records:
        c = parse_coeffs(coeffs_s)
        if c is None or len(c) != degree + 1:
            continue
        try:
            m = mahler_measure(c)
            if not np.isfinite(m) or m < 0.999:
                continue
            m = max(m, 1.0)
        except Exception:
            continue
        try:
            d = float(disc_s) if disc_s is not None else 0.0
        except ValueError:
            d = 0.0
        ms.append(m)
        disc_abs.append(d)
        labels_low.append((m, d, label))
    ms = np.array(ms)
    disc_abs = np.array(disc_abs)
    labels_low.sort(key=lambda t: t[0])
    return ms, disc_abs, labels_low[:10]


def fit_powerlaw_tail(degrees, min_ms):
    """Fit m(d) = f_inf + C * d^(-alpha) via log-linear on (m - f_inf).
    Try grid of f_inf candidates including 1.0 and 1.17628...
    Return the best (f_inf, C, alpha, rmse)."""
    best = None
    for f_inf in np.linspace(1.0, 1.17, 35):
        r = np.array(min_ms) - f_inf
        d = np.array(degrees)
        if np.any(r <= 0):
            continue
        y = np.log(r)
        x = np.log(d)
        A = np.vstack([x, np.ones_like(x)]).T
        sol, *_ = np.linalg.lstsq(A, y, rcond=None)
        neg_alpha, logC = sol
        pred = f_inf + np.exp(logC) * d ** neg_alpha
        rmse = float(np.sqrt(((np.array(min_ms) - pred) ** 2).mean()))
        record = {
            'f_inf': float(f_inf),
            'alpha': float(-neg_alpha),
            'C': float(np.exp(logC)),
            'rmse': rmse,
        }
        if best is None or rmse < best['rmse']:
            best = record
    return best


def main():
    t0 = time.time()
    print(f'[{time.strftime("%H:%M:%S")}] Connecting to Postgres...')
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    counts = count_per_degree(cur)
    print(f'NF counts by degree: {[(d, counts.get(d, 0)) for d in [2,5,10,15,20,30,40,50,60]]}')

    results = {
        'meta': {
            'protocol': 'F014:P040 Lehmer min M(f) per degree — reframed from trivially-zero Salem density',
            'lehmer_bound': LEHMER_BOUND,
            'degree_range': [DEGREES[0], DEGREES[-1]],
            'cap_per_degree': CAP_PER_DEG,
            'min_per_degree': MIN_PER_DEG,
            'null_stat_note': 'density-in-Salem-window is 0 for NF defining polynomials (not reciprocal); BSWCD null degenerate (mean=0, std=0). Reporting STRATIFIER_INVARIANCE for the original framing and the reframed scan for the real signal.',
            'started': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        },
        'per_degree': {},
        'n_below_lehmer': 0,
        'counterexample_candidates': [],
    }

    degrees_with_data = []
    min_ms = []

    for deg in DEGREES:
        available = counts.get(deg, 0)
        if available < MIN_PER_DEG:
            continue
        cap = min(available, CAP_PER_DEG)
        print(f'\n[deg={deg}] available={available:,} cap={cap:,} pulling...')
        records = list(pull(cur, deg, cap))
        t_m = time.time()
        ms, disc_abs, low10 = mahler_stats(records, deg)
        dt = time.time() - t_m
        if len(ms) < 50:
            continue
        mn = float(ms.min())
        p1 = float(np.percentile(ms, 1))
        p5 = float(np.percentile(ms, 5))
        med = float(np.median(ms))
        mx = float(ms.max())
        # Weil height on primitive element: log M / deg
        log_m_per_deg = float(np.log(mn) / deg)
        below_lehmer = int((ms < LEHMER_BOUND).sum())
        near_lehmer = int((ms < 1.20).sum())
        cyclotomic_like = int((ms < 1.001).sum())

        print(f'  computed {len(ms):,} in {dt:.1f}s  min={mn:.6f} p1={p1:.3f} med={med:.3f} max={mx:.0e}')
        print(f'  log(min M)/deg = {log_m_per_deg:.4f}  below_Lehmer={below_lehmer}  cyclotomic_like={cyclotomic_like}')
        if below_lehmer > 0:
            print(f'  *** {below_lehmer} entries below Lehmer bound — CHECK: ')
            for (m, d, label) in low10[:5]:
                print(f'      M={m:.6f}  disc={d:.0f}  label={label}')

        results['per_degree'][str(deg)] = {
            'n_measures': int(len(ms)),
            'available': available,
            'min_M': mn,
            'p1_M': p1,
            'p5_M': p5,
            'median_M': med,
            'max_M': mx,
            'log_min_M_per_deg': log_m_per_deg,
            'below_lehmer_count': below_lehmer,
            'near_lehmer_count': near_lehmer,
            'cyclotomic_like_count': cyclotomic_like,
            'bottom_10': [{'M': float(m), 'disc_abs': float(d), 'label': str(lbl)} for (m, d, lbl) in low10],
        }
        results['n_below_lehmer'] += below_lehmer
        if below_lehmer > 0:
            for (m, d, lbl) in low10:
                if m < LEHMER_BOUND:
                    results['counterexample_candidates'].append({
                        'degree': deg,
                        'M': float(m),
                        'disc_abs': float(d),
                        'label': str(lbl),
                    })

        degrees_with_data.append(deg)
        min_ms.append(mn)

    # Fit m(d) = f_inf + C*d^(-alpha)
    if len(degrees_with_data) >= 5:
        fit = fit_powerlaw_tail(degrees_with_data, min_ms)
        print(f'\nPower-law fit over degrees {degrees_with_data[0]}..{degrees_with_data[-1]}:')
        print(f'  m(d) = {fit["f_inf"]:.4f} + {fit["C"]:.4f} * d^(-{fit["alpha"]:.3f})   rmse={fit["rmse"]:.4f}')
        results['fit'] = {
            'form': 'm(d) = f_inf + C * d^(-alpha)',
            'range': [degrees_with_data[0], degrees_with_data[-1]],
            **fit,
        }
        # Stance classifier
        if fit['f_inf'] <= 1.02:
            stance = 'C (asymptote -> 1, Lehmer gap is finite-d artifact)'
        elif fit['f_inf'] >= 1.15:
            stance = 'A (gap at 1.17628 holds asymptotically)'
        else:
            stance = 'B (intermediate asymptote ~ ' + f'{fit["f_inf"]:.3f})'
        results['fit']['stance'] = stance
        print(f'  -> Stance: {stance}')

    results['meta']['elapsed_sec'] = time.time() - t0
    results['meta']['finished'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n[done] {OUT}')
    print(f'elapsed: {results["meta"]["elapsed_sec"]:.1f}s')

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
