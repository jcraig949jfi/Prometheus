"""
Test: Do low-lying L-function zeros encode isogeny class structure?
Bridges the analytic side (zeros) to the algebraic side (isogeny classes).
"""
import psycopg2
import numpy as np
import pandas as pd
import json
import os
from scipy import stats

# ---- 1. Pull data ----
print("Connecting to LMFDB...")
conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb'
)
cur = conn.cursor()

# One curve per isogeny class (isogenous curves share L-function)
cur.execute("""
SELECT DISTINCT ON (e.lmfdb_iso)
       e.lmfdb_label, e.conductor, e.rank, e.class_size, e.class_deg,
       l.positive_zeros, l.analytic_conductor, l.order_of_vanishing
FROM ec_curvedata e
JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || REPLACE(e.lmfdb_iso, '.', '/')
WHERE l.positive_zeros IS NOT NULL AND e.class_size IS NOT NULL
      AND e.conductor <= 50000
ORDER BY e.lmfdb_iso, e.lmfdb_label
LIMIT 20000
""")
rows = cur.fetchall()
conn.close()
print(f"Fetched {len(rows)} isogeny classes")

# ---- 2. Build dataframe with spectral features ----
records = []
for row in rows:
    label, cond, rank, cs, cd, zeros_str, an_cond, ov = row
    zeros = sorted([float(z) for z in zeros_str])
    if len(zeros) < 3:
        continue

    gamma1 = zeros[0]
    mean3 = np.mean(zeros[:3])
    spacing_12 = zeros[1] - zeros[0]
    density_below_5 = sum(1 for z in zeros if z < 5)

    records.append({
        'label': label,
        'conductor': cond,
        'rank': rank,
        'class_size': cs,
        'class_deg': cd,
        'log_conductor': np.log(cond),
        'gamma1': gamma1,
        'mean3': mean3,
        'spacing_12': spacing_12,
        'density_below_5': density_below_5,
        'analytic_conductor': an_cond,
    })

df = pd.DataFrame(records)
print(f"Built dataframe: {len(df)} rows")
print(f"class_size distribution:\n{df['class_size'].value_counts().sort_index()}")
print(f"class_deg distribution:\n{df['class_deg'].value_counts().sort_index().head(10)}")

# ---- 3. Raw correlations ----
spectral_features = ['gamma1', 'mean3', 'spacing_12', 'density_below_5']
targets = ['class_size', 'class_deg']

print("\n=== RAW CORRELATIONS ===")
raw_corrs = {}
for feat in spectral_features:
    raw_corrs[feat] = {}
    for tgt in targets:
        r, p = stats.spearmanr(df[feat], df[tgt])
        raw_corrs[feat][tgt] = {'spearman_r': round(r, 6), 'p_value': float(f'{p:.2e}')}
        print(f"  {feat} vs {tgt}: rho={r:.4f}, p={p:.2e}")

# ---- 4. Partial correlation: condition on conductor ----
print("\n=== CONDUCTOR-CONTROLLED CORRELATIONS ===")
controlled_corrs = {}

def residualize(x, z):
    """Regress x on z, return residuals."""
    slope, intercept, _, _, _ = stats.linregress(z, x)
    return x - (slope * z + intercept)

log_cond = df['log_conductor'].values
for feat in spectral_features:
    controlled_corrs[feat] = {}
    feat_resid = residualize(df[feat].values, log_cond)
    for tgt in targets:
        tgt_resid = residualize(df[tgt].values.astype(float), log_cond)
        r, p = stats.spearmanr(feat_resid, tgt_resid)
        controlled_corrs[feat][tgt] = {'spearman_r': round(r, 6), 'p_value': float(f'{p:.2e}')}
        print(f"  {feat} vs {tgt} | log(N): rho={r:.4f}, p={p:.2e}")

# ---- 5. Null model: permutation test (500 shuffles) ----
print("\n=== PERMUTATION TEST (500 shuffles) ===")
n_perm = 500
rng = np.random.default_rng(42)

null_results = {}
for feat in spectral_features:
    null_results[feat] = {}
    feat_resid = residualize(df[feat].values, log_cond)
    for tgt in targets:
        tgt_vals = df[tgt].values.astype(float)
        tgt_resid = residualize(tgt_vals, log_cond)

        observed_r, _ = stats.spearmanr(feat_resid, tgt_resid)

        null_rs = []
        for _ in range(n_perm):
            perm_tgt = rng.permutation(tgt_resid)
            r_null, _ = stats.spearmanr(feat_resid, perm_tgt)
            null_rs.append(r_null)

        null_rs = np.array(null_rs)
        perm_p = np.mean(np.abs(null_rs) >= np.abs(observed_r))
        null_std = np.std(null_rs)
        z_score = round((observed_r - np.mean(null_rs)) / null_std, 4) if null_std > 0 else 0.0
        null_results[feat][tgt] = {
            'observed_r': round(observed_r, 6),
            'null_mean': round(np.mean(null_rs), 6),
            'null_std': round(null_std, 6),
            'perm_p_value': round(perm_p, 4),
            'z_score': z_score,
        }
        print(f"  {feat} vs {tgt}: obs_r={observed_r:.4f}, null_std={null_std:.4f}, perm_p={perm_p:.4f}, z={z_score:.2f}")

# ---- 6. Stratified analysis by conductor band ----
print("\n=== STRATIFIED BY CONDUCTOR BAND ===")
df['cond_band'] = pd.cut(
    df['conductor'],
    bins=[0, 1000, 5000, 15000, 50000],
    labels=['<1k', '1k-5k', '5k-15k', '15k-50k']
)
stratified = {}
for band in df['cond_band'].cat.categories:
    sub = df[df['cond_band'] == band]
    if len(sub) < 30:
        continue
    stratified[band] = {'n': len(sub)}
    for feat in spectral_features:
        for tgt in targets:
            r, p = stats.spearmanr(sub[feat], sub[tgt])
            stratified[band][f'{feat}_vs_{tgt}'] = {
                'rho': round(r, 4),
                'p': float(f'{p:.2e}')
            }
    g1_cs = stratified[band].get('gamma1_vs_class_size', {})
    print(f"  Band {band} (n={len(sub)}): gamma1 vs class_size rho={g1_cs.get('rho', 'N/A')}")

# ---- 7. Effect size: mean gamma1 by class_size ----
print("\n=== MEAN GAMMA1 BY CLASS_SIZE ===")
gamma1_by_cs = {}
for cs, grp in df.groupby('class_size'):
    if len(grp) >= 10:
        gamma1_by_cs[str(int(cs))] = {
            'n': len(grp),
            'gamma1_mean': round(grp['gamma1'].mean(), 6),
            'gamma1_std': round(grp['gamma1'].std(), 6),
            'mean3_mean': round(grp['mean3'].mean(), 6),
            'density5_mean': round(grp['density_below_5'].mean(), 4),
            'mean_log_cond': round(grp['log_conductor'].mean(), 4),
        }
        print(f"  class_size={cs}: n={len(grp)}, gamma1={grp['gamma1'].mean():.4f}, log_cond={grp['log_conductor'].mean():.4f}")

# ---- 8. Also check rank=0 only (remove rank confound) ----
print("\n=== RANK-0 ONLY (remove rank confound) ===")
df0 = df[df['rank'] == 0]
print(f"Rank-0 subset: {len(df0)} classes")
rank0_results = {}
log_cond0 = df0['log_conductor'].values
for feat in spectral_features:
    rank0_results[feat] = {}
    feat_resid = residualize(df0[feat].values, log_cond0)
    for tgt in targets:
        tgt_resid = residualize(df0[tgt].values.astype(float), log_cond0)
        r, p = stats.spearmanr(feat_resid, tgt_resid)
        rank0_results[feat][tgt] = {'spearman_r': round(r, 6), 'p_value': float(f'{p:.2e}')}
        print(f"  {feat} vs {tgt} | log(N), rank=0: rho={r:.4f}, p={p:.2e}")

# ---- 9. Assemble and save ----
result = {
    'test': 'spectral_tail_isogeny',
    'question': 'Do low-lying L-function zeros encode isogeny class structure?',
    'dataset': {
        'source': 'LMFDB (devmirror.lmfdb.xyz)',
        'n_isogeny_classes': len(df),
        'conductor_range': [int(df['conductor'].min()), int(df['conductor'].max())],
        'note': 'One curve per isogeny class (isogenous curves share L-function)',
    },
    'spectral_features': spectral_features,
    'raw_correlations': raw_corrs,
    'conductor_controlled_correlations': controlled_corrs,
    'permutation_test': {
        'n_permutations': n_perm,
        'method': 'Permute conductor-residualized target, recompute Spearman rho',
        'results': null_results,
    },
    'stratified_by_conductor': {str(k): v for k, v in stratified.items()},
    'gamma1_by_class_size': gamma1_by_cs,
    'rank0_controlled_correlations': rank0_results,
}

# Verdict
sig_controlled = []
for feat in spectral_features:
    for tgt in targets:
        nr = null_results[feat][tgt]
        if nr['perm_p_value'] < 0.05:
            sig_controlled.append(
                f"{feat} vs {tgt}: r={nr['observed_r']:.4f}, perm_p={nr['perm_p_value']:.4f}, z={nr['z_score']:.2f}"
            )

if sig_controlled:
    verdict = "SIGNAL: Some spectral features predict isogeny class structure beyond conductor."
    verdict_detail = sig_controlled
else:
    verdict = "NULL: No spectral features survive conductor control + permutation test."
    verdict_detail = []

result['verdict'] = verdict
result['verdict_detail'] = verdict_detail

os.makedirs('harmonia/results', exist_ok=True)
with open('harmonia/results/spectral_tail_isogeny.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\nSaved to harmonia/results/spectral_tail_isogeny.json")
print("\n" + "=" * 60)
print("VERDICT:", verdict)
for s in verdict_detail:
    print(f"  {s}")
print("=" * 60)
