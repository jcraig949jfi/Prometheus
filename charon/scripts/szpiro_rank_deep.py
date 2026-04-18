"""
Charon: Deep investigation of szpiro_ratio vs rank anticorrelation.
Hypothesis: higher-rank curves are more arithmetically constrained.
Potential abc↔BSD connection.

Phases:
1. Confirm & quantify szpiro per rank (all quantiles)
2. abc_quality vs rank
3. Mechanism: discriminant vs conductor decomposition
4. Conductor selection effect (Goldfeld)
5. BSD coupling: szpiro × regulator product
"""

import json
import sys
import numpy as np
import psycopg2
from collections import defaultdict

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')

def query(sql, params=None):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    return cols, rows

def percentile(arr, p):
    return float(np.percentile(arr, p))

def stats_dict(arr):
    a = np.array(arr, dtype=float)
    return {
        'count': len(a),
        'mean': float(np.mean(a)),
        'median': float(np.median(a)),
        'std': float(np.std(a)),
        'p95': percentile(a, 95),
        'p99': percentile(a, 99),
        'max': float(np.max(a)),
        'min': float(np.min(a)),
    }

results = {}

# ── Phase 1: szpiro_ratio statistics per rank ──
print("Phase 1: szpiro_ratio per rank...")
cols, rows = query("""
    SELECT
        CASE WHEN rank::int >= 5 THEN '5+' ELSE rank END AS rank_bin,
        szpiro_ratio::double precision
    FROM ec_curvedata
    WHERE szpiro_ratio IS NOT NULL AND szpiro_ratio != ''
      AND rank IS NOT NULL AND rank != ''
""")
by_rank = defaultdict(list)
for rank_bin, szp in rows:
    by_rank[str(rank_bin)].append(szp)

phase1 = {}
for r in sorted(by_rank.keys()):
    phase1[f"rank_{r}"] = stats_dict(by_rank[r])
    print(f"  rank={r}: n={len(by_rank[r])}, max={max(by_rank[r]):.4f}, "
          f"p99={percentile(by_rank[r], 99):.4f}, mean={np.mean(by_rank[r]):.4f}")

# Check monotone decrease across quantiles
quantiles = ['max', 'p99', 'p95', 'mean', 'median']
ranks_ordered = ['0', '1', '2', '3', '4', '5+']
monotone = {}
for q in quantiles:
    vals = [phase1[f"rank_{r}"][q] for r in ranks_ordered if f"rank_{r}" in phase1]
    # Check if each step decreases
    decreasing = all(vals[i] >= vals[i+1] for i in range(len(vals)-1))
    monotone[q] = {'values': vals, 'monotone_decreasing': decreasing}

phase1['monotone_check'] = monotone
results['phase1_szpiro_per_rank'] = phase1
print(f"  Monotone decreasing? {json.dumps({k: v['monotone_decreasing'] for k,v in monotone.items()})}")

# ── Phase 1b: Conductor-matched test ──
print("\nPhase 1b: Conductor-matched test (szpiro by rank within conductor decades)...")
cols, rows = query("""
    SELECT
        rank::int AS r,
        szpiro_ratio::double precision AS szp,
        conductor::double precision AS cond
    FROM ec_curvedata
    WHERE szpiro_ratio IS NOT NULL AND szpiro_ratio != ''
      AND rank IS NOT NULL AND rank != ''
      AND conductor IS NOT NULL AND conductor != ''
""")

# Bin by conductor decade
cond_rank = defaultdict(lambda: defaultdict(list))
for r, szp, cond in rows:
    if cond > 0:
        decade = int(np.floor(np.log10(cond)))
        rank_bin = str(min(r, 4))
        cond_rank[decade][rank_bin].append(szp)

phase1b = {}
for decade in sorted(cond_rank.keys()):
    decade_data = {}
    for rank_bin in sorted(cond_rank[decade].keys()):
        arr = cond_rank[decade][rank_bin]
        if len(arr) >= 10:
            decade_data[f"rank_{rank_bin}"] = {
                'count': len(arr),
                'mean': float(np.mean(arr)),
                'p99': percentile(arr, 99),
                'max': float(np.max(arr)),
            }
    if len(decade_data) >= 2:
        phase1b[f"decade_{decade}"] = decade_data
        ranks_present = sorted(decade_data.keys())
        means = [decade_data[r]['mean'] for r in ranks_present]
        parts = [f"{r}={decade_data[r]['mean']:.3f}" for r in ranks_present]
        print(f"  10^{decade}: {', '.join(parts)}")

results['phase1b_conductor_matched'] = phase1b

# ── Phase 2: abc_quality vs rank ──
print("\nPhase 2: abc_quality per rank...")
cols, rows = query("""
    SELECT
        CASE WHEN rank::int >= 5 THEN '5+' ELSE rank END AS rank_bin,
        abc_quality::double precision
    FROM ec_curvedata
    WHERE abc_quality IS NOT NULL AND abc_quality != ''
      AND rank IS NOT NULL AND rank != ''
""")
abc_by_rank = defaultdict(list)
for rank_bin, abc in rows:
    abc_by_rank[str(rank_bin)].append(abc)

phase2 = {}
for r in sorted(abc_by_rank.keys()):
    phase2[f"rank_{r}"] = stats_dict(abc_by_rank[r])
    print(f"  rank={r}: n={len(abc_by_rank[r])}, max={max(abc_by_rank[r]):.4f}, "
          f"p99={percentile(abc_by_rank[r], 99):.4f}, mean={np.mean(abc_by_rank[r]):.4f}")

# abc-szpiro correlation per rank
print("\n  abc-szpiro correlation per rank:")
cols, rows = query("""
    SELECT
        CASE WHEN rank::int >= 5 THEN '5+' ELSE rank END AS rank_bin,
        abc_quality::double precision,
        szpiro_ratio::double precision
    FROM ec_curvedata
    WHERE abc_quality IS NOT NULL AND abc_quality != ''
      AND szpiro_ratio IS NOT NULL AND szpiro_ratio != ''
      AND rank IS NOT NULL AND rank != ''
""")
abc_szp_by_rank = defaultdict(lambda: {'abc': [], 'szp': []})
for rank_bin, abc, szp in rows:
    abc_szp_by_rank[str(rank_bin)]['abc'].append(abc)
    abc_szp_by_rank[str(rank_bin)]['szp'].append(szp)

corr_by_rank = {}
for r in sorted(abc_szp_by_rank.keys()):
    d = abc_szp_by_rank[r]
    if len(d['abc']) > 2:
        c = float(np.corrcoef(d['abc'], d['szp'])[0, 1])
        corr_by_rank[f"rank_{r}"] = c
        print(f"    rank={r}: corr(abc, szpiro) = {c:.4f}")

phase2['abc_szpiro_correlation'] = corr_by_rank
results['phase2_abc_quality'] = phase2

# ── Phase 3: Mechanism — discriminant vs conductor ──
print("\nPhase 3: Mechanism — disc vs conductor decomposition...")
# szpiro_ratio = log|disc| / log(cond). We can reconstruct from absD and conductor.
cols, rows = query("""
    SELECT
        CASE WHEN rank::int >= 5 THEN '5+' ELSE rank END AS rank_bin,
        "absD"::double precision AS disc,
        conductor::double precision AS cond
    FROM ec_curvedata
    WHERE "absD" IS NOT NULL AND "absD" != '' AND "absD"::double precision > 0
      AND conductor IS NOT NULL AND conductor != '' AND conductor::double precision > 1
      AND rank IS NOT NULL AND rank != ''
""")

disc_cond_by_rank = defaultdict(lambda: {'log_disc': [], 'log_cond': []})
for rank_bin, disc, cond in rows:
    disc_cond_by_rank[str(rank_bin)]['log_disc'].append(np.log(disc))
    disc_cond_by_rank[str(rank_bin)]['log_cond'].append(np.log(cond))

phase3 = {}
for r in sorted(disc_cond_by_rank.keys()):
    d = disc_cond_by_rank[r]
    phase3[f"rank_{r}"] = {
        'mean_log_disc': float(np.mean(d['log_disc'])),
        'mean_log_cond': float(np.mean(d['log_cond'])),
        'mean_ratio': float(np.mean(d['log_disc'])) / float(np.mean(d['log_cond'])),
        'count': len(d['log_disc']),
    }
    print(f"  rank={r}: mean_log_disc={np.mean(d['log_disc']):.2f}, "
          f"mean_log_cond={np.mean(d['log_cond']):.2f}, "
          f"ratio={np.mean(d['log_disc'])/np.mean(d['log_cond']):.4f}")

# num_bad_primes per rank (smoothness proxy)
cols, rows = query("""
    SELECT
        CASE WHEN rank::int >= 5 THEN '5+' ELSE rank END AS rank_bin,
        num_bad_primes::int
    FROM ec_curvedata
    WHERE num_bad_primes IS NOT NULL AND num_bad_primes != ''
      AND rank IS NOT NULL AND rank != ''
""")
nbp_by_rank = defaultdict(list)
for rank_bin, nbp in rows:
    nbp_by_rank[str(rank_bin)].append(nbp)

for r in sorted(nbp_by_rank.keys()):
    phase3[f"rank_{r}"]['mean_num_bad_primes'] = float(np.mean(nbp_by_rank[r]))
    print(f"  rank={r}: mean_num_bad_primes={np.mean(nbp_by_rank[r]):.2f}")

results['phase3_mechanism'] = phase3

# ── Phase 4: Conductor selection effect ──
print("\nPhase 4: Conductor selection effect (partial correlation)...")
cols, rows = query("""
    SELECT
        rank::int,
        szpiro_ratio::double precision,
        conductor::double precision
    FROM ec_curvedata
    WHERE szpiro_ratio IS NOT NULL AND szpiro_ratio != ''
      AND rank IS NOT NULL AND rank != ''
      AND conductor IS NOT NULL AND conductor != '' AND conductor::double precision > 0
""")

ranks_arr = np.array([r[0] for r in rows], dtype=float)
szp_arr = np.array([r[1] for r in rows], dtype=float)
logcond_arr = np.log(np.array([r[2] for r in rows], dtype=float))

# Raw correlation
raw_corr = float(np.corrcoef(ranks_arr, szp_arr)[0, 1])
print(f"  Raw corr(rank, szpiro) = {raw_corr:.6f}")

# Partial correlation controlling for log(conductor)
# residualize both rank and szpiro on log(conductor)
from numpy.polynomial.polynomial import polyfit, polyval

# Linear regression residuals
def residualize(y, x):
    coeffs = np.polyfit(x, y, 1)
    pred = np.polyval(coeffs, x)
    return y - pred

rank_resid = residualize(ranks_arr, logcond_arr)
szp_resid = residualize(szp_arr, logcond_arr)
partial_corr = float(np.corrcoef(rank_resid, szp_resid)[0, 1])
print(f"  Partial corr(rank, szpiro | log_cond) = {partial_corr:.6f}")

# Conductor distribution per rank
cond_stats_by_rank = defaultdict(list)
for r, szp, cond in rows:
    cond_stats_by_rank[str(min(r, 5))].append(np.log10(cond))

cond_dist = {}
for r in sorted(cond_stats_by_rank.keys()):
    cond_dist[f"rank_{r}"] = {
        'mean_log10_cond': float(np.mean(cond_stats_by_rank[r])),
        'median_log10_cond': float(np.median(cond_stats_by_rank[r])),
        'max_log10_cond': float(np.max(cond_stats_by_rank[r])),
    }
    print(f"  rank={r}: median_log10_cond={np.median(cond_stats_by_rank[r]):.2f}, "
          f"max_log10_cond={np.max(cond_stats_by_rank[r]):.2f}")

phase4 = {
    'raw_correlation': raw_corr,
    'partial_correlation_controlling_logcond': partial_corr,
    'conductor_distribution_by_rank': cond_dist,
    'interpretation': (
        'positive partial corr means conductor suppresses szpiro even more than rank alone; '
        'negative partial corr means rank-szpiro anticorrelation survives conductor control'
    ),
}
results['phase4_selection_effect'] = phase4

# ── Phase 5: BSD coupling ──
print("\nPhase 5: BSD coupling — szpiro × regulator product...")
cols, rows = query("""
    SELECT
        rank::int,
        szpiro_ratio::double precision,
        regulator::double precision,
        sha::int,
        torsion::int,
        faltings_height::double precision
    FROM ec_curvedata
    WHERE szpiro_ratio IS NOT NULL AND szpiro_ratio != ''
      AND rank IS NOT NULL AND rank != ''
      AND regulator IS NOT NULL AND regulator != ''
      AND sha IS NOT NULL AND sha != ''
      AND torsion IS NOT NULL AND torsion != ''
      AND faltings_height IS NOT NULL AND faltings_height != ''
      AND rank::int >= 1
""")

phase5 = {}

# szpiro × regulator product by rank
prod_by_rank = defaultdict(list)
for r, szp, reg, sha_val, tor, fh in rows:
    prod_by_rank[str(min(r, 4))].append(szp * reg)

print("  szpiro × regulator product:")
for r in sorted(prod_by_rank.keys()):
    arr = prod_by_rank[r]
    phase5[f"rank_{r}_szp_x_reg"] = stats_dict(arr)
    print(f"    rank={r}: n={len(arr)}, mean={np.mean(arr):.4f}, median={np.median(arr):.4f}")

# Correlation matrix for rank >= 2
r2_data = {'szpiro': [], 'rank': [], 'regulator': [], 'sha': [], 'torsion': [], 'faltings': []}
for r, szp, reg, sha_val, tor, fh in rows:
    if r >= 2:
        r2_data['szpiro'].append(szp)
        r2_data['rank'].append(r)
        r2_data['regulator'].append(reg)
        r2_data['sha'].append(sha_val)
        r2_data['torsion'].append(tor)
        r2_data['faltings'].append(fh)

if len(r2_data['szpiro']) > 10:
    mat = np.array([r2_data[k] for k in ['szpiro', 'rank', 'regulator', 'sha', 'torsion', 'faltings']])
    corr_mat = np.corrcoef(mat)
    labels = ['szpiro', 'rank', 'regulator', 'sha', 'torsion', 'faltings']
    corr_dict = {}
    print(f"\n  Correlation matrix for rank >= 2 (n={len(r2_data['szpiro'])}):")
    for i, li in enumerate(labels):
        for j, lj in enumerate(labels):
            if j > i:
                corr_dict[f"{li}_vs_{lj}"] = float(corr_mat[i, j])
                print(f"    {li} vs {lj}: {corr_mat[i,j]:.4f}")
    phase5['rank_ge2_correlations'] = corr_dict
    phase5['rank_ge2_count'] = len(r2_data['szpiro'])

# szpiro × regulator vs faltings_height for rank >= 2
if len(r2_data['szpiro']) > 10:
    prod = np.array(r2_data['szpiro']) * np.array(r2_data['regulator'])
    falt = np.array(r2_data['faltings'])
    c = float(np.corrcoef(prod, falt)[0, 1])
    phase5['szp_x_reg_vs_faltings_corr_rank_ge2'] = c
    print(f"\n  corr(szpiro*reg, faltings) for rank>=2: {c:.4f}")

results['phase5_bsd_coupling'] = phase5

# ── Summary ──
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

# Key finding: does the anticorrelation survive conductor control?
pc = results['phase4_selection_effect']['partial_correlation_controlling_logcond']
rc = results['phase4_selection_effect']['raw_correlation']
print(f"Raw corr(rank, szpiro): {rc:.4f}")
print(f"Partial corr(rank, szpiro | log_cond): {pc:.4f}")
if abs(pc) < abs(rc) * 0.3:
    verdict = "MOSTLY SELECTION EFFECT: conductor explains most of rank-szpiro anticorrelation"
elif abs(pc) > abs(rc) * 0.7:
    verdict = "GENUINE CONSTRAINT: rank-szpiro anticorrelation survives conductor control"
else:
    verdict = "MIXED: partial conductor selection, partial genuine constraint"
print(f"Verdict: {verdict}")
results['summary'] = {
    'raw_correlation': rc,
    'partial_correlation': pc,
    'verdict': verdict,
}

# Save
out_path = 'F:/Prometheus/charon/data/szpiro_rank_deep.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
