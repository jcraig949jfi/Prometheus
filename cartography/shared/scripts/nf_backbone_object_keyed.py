"""
NF Backbone retest v2 — proper object-keyed null.

The statistic must depend on object identity, not just category distribution.
We use: conditional mean of a continuous NF feature given the shared Galois
label, correlated with the conditional mean on the Artin side.

Under permutation of NF labels, the conditional means become random and the
cross-side correlation drops to zero.

Author: Harmonia
"""
import sys, io, time
import numpy as np
from scipy import stats
import psycopg2
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_nfs(conn, per_degree=2000):
    """Balanced sample across degrees 2-20."""
    cur = conn.cursor()
    all_rows = []
    for degree in range(2, 21):
        cur.execute("""
        SELECT label, degree::int, galois_label, class_number::numeric, disc_abs::numeric
        FROM nf_fields
        WHERE degree::int = %s AND galois_label IS NOT NULL
          AND class_number IS NOT NULL AND disc_abs IS NOT NULL
        ORDER BY disc_abs::numeric ASC
        LIMIT %s
        """, (degree, per_degree))
        all_rows.extend(cur.fetchall())
    cur.close()
    return [(l, d, g, float(cn) if cn else 0, float(da) if da else 0) for l, d, g, cn, da in all_rows]


def load_artin(conn, per_combo=500):
    """Balanced sample across (Galn, Galt) combinations."""
    cur = conn.cursor()
    # Get all distinct combos
    cur.execute("""
    SELECT "Galn"::int AS galn, "Galt"::int AS galt, COUNT(*) AS n
    FROM artin_reps
    WHERE "Galn" IS NOT NULL AND "Galt" IS NOT NULL
    GROUP BY "Galn", "Galt"
    ORDER BY "Galn", "Galt"
    """)
    combos = cur.fetchall()

    out = []
    for galn, galt, n in combos:
        cur.execute("""
        SELECT "Baselabel", "Dim"::int, "Galn"::int, "Galt"::int, "Conductor"::numeric
        FROM artin_reps
        WHERE "Galn" = %s AND "Galt" = %s AND "Conductor" IS NOT NULL
        ORDER BY "Conductor"::numeric ASC
        LIMIT %s
        """, (str(galn), str(galt), per_combo))
        for bl, dim, g, t, c in cur.fetchall():
            if g is not None and t is not None:
                key = f"{g}T{t}"
                out.append((bl, dim, key, float(c) if c else 0))
    cur.close()
    return out


def cross_domain_correlation(nfs, artins):
    """
    For each Galois label shared between NF and Artin sides:
      - Compute mean log(disc_abs) among NFs with that label
      - Compute mean log(Conductor) among Artin reps with that label
    Report Pearson correlation across shared labels.
    """
    nf_by_key = defaultdict(list)
    for _, _, gal, cn, da in nfs:
        if da > 0:
            nf_by_key[gal].append(np.log(da))

    art_by_key = defaultdict(list)
    for _, _, key, c in artins:
        if c > 0:
            art_by_key[key].append(np.log(c))

    shared = set(nf_by_key.keys()) & set(art_by_key.keys())
    if len(shared) < 3:
        return None, 0, list(shared)

    nf_means = []
    art_means = []
    for k in shared:
        if len(nf_by_key[k]) >= 3 and len(art_by_key[k]) >= 3:
            nf_m = np.mean(nf_by_key[k])
            art_m = np.mean(art_by_key[k])
            if np.isfinite(nf_m) and np.isfinite(art_m):
                nf_means.append(nf_m)
                art_means.append(art_m)

    if len(nf_means) < 3:
        return None, 0, list(shared)

    nf_arr = np.array(nf_means)
    art_arr = np.array(art_means)
    if nf_arr.std() < 1e-10 or art_arr.std() < 1e-10:
        return 0.0, len(nf_means), list(shared)

    rho, p = stats.pearsonr(nf_arr, art_arr)
    if not np.isfinite(rho):
        rho = 0.0
    return rho, len(nf_means), list(shared)


def permutation_null(nfs, artins, n_perms=200):
    """Permute NF Galois labels among NFs, recompute correlation."""
    rng = np.random.default_rng(42)
    real_rho, real_n, shared = cross_domain_correlation(nfs, artins)
    if real_rho is None:
        return None

    nf_keys = [n[2] for n in nfs]  # galois labels
    nf_discs = [n[4] for n in nfs]

    null_rhos = []
    for _ in range(n_perms):
        perm_keys = rng.permutation(nf_keys)
        perm_nfs = [(nfs[i][0], nfs[i][1], perm_keys[i], nfs[i][3], nf_discs[i])
                    for i in range(len(nfs))]
        null_rho, _, _ = cross_domain_correlation(perm_nfs, artins)
        if null_rho is not None:
            null_rhos.append(null_rho)

    null_arr = np.array(null_rhos)
    if len(null_arr) == 0 or null_arr.std() < 1e-10:
        z = float('inf') if real_rho != null_arr.mean() else 0
    else:
        z = (real_rho - null_arr.mean()) / null_arr.std()
    p_empirical = np.mean(np.abs(null_arr) >= abs(real_rho))

    return {
        'real_rho': real_rho,
        'real_n': real_n,
        'n_shared_cats': len(shared),
        'null_mean': null_arr.mean(),
        'null_std': null_arr.std(),
        'z': z,
        'p_perm': p_empirical,
    }


def main():
    print("=" * 70)
    print("NF BACKBONE v2 — OBJECT-KEYED conditional-mean correlation")
    print("=" * 70)

    conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb',
                            user='postgres', password='prometheus')

    t0 = time.time()
    nfs = load_nfs(conn, per_degree=2000)
    artins = load_artin(conn, per_combo=300)
    print(f"\n[{time.time()-t0:.1f}s] Loaded {len(nfs)} NFs, {len(artins)} Artin reps")

    # ==========================================
    # MAIN TEST
    # ==========================================
    print("\n--- Cross-domain correlation: NF log(disc) vs Artin log(conductor) by Galois label ---")
    result = permutation_null(nfs, artins, n_perms=200)
    if result is None:
        print("  No shared Galois labels. Cannot compute.")
        conn.close()
        return

    print(f"  Shared Galois categories: {result['n_shared_cats']}")
    print(f"  Real Pearson rho: {result['real_rho']:.4f}")
    print(f"  Null (permuted NF->Galois): {result['null_mean']:.4f} ± {result['null_std']:.4f}")
    print(f"  Z-score: {result['z']:.2f}")
    print(f"  Permutation p-value: {result['p_perm']:.4f}")

    print("\nVERDICT:")
    if result['p_perm'] < 0.01 and abs(result['z']) > 3:
        print(f"  SURVIVES: NF discriminant and Artin conductor are CORRELATED within Galois-label classes.")
        print(f"  This is object-level coupling — specific Galois labels pair specific NFs to specific Artin reps.")
        print(f"  The NF backbone exists as OBJECT-LEVEL structure, not just feature-distribution geometry.")
    elif abs(result['z']) > 2:
        print(f"  MARGINAL: |z|={abs(result['z']):.2f}. Needs more data / better stratification.")
    else:
        print(f"  KILLED: Even with object-level keying, no cross-domain coupling beyond null.")
        print(f"  The 'backbone' was a chimera of feature distributions. Galois labels don't carry information")
        print(f"  from NF discriminants to Artin conductors.")

    # ==========================================
    # DIAGNOSTIC: what labels are shared?
    # ==========================================
    print("\n--- DIAGNOSTIC: shared labels sample ---")
    nf_by_k = defaultdict(list)
    for _, _, g, _, da in nfs:
        if da > 0:
            nf_by_k[g].append(da)
    art_by_k = defaultdict(list)
    for _, _, k, c in artins:
        if c > 0:
            art_by_k[k].append(c)

    shared = sorted(set(nf_by_k.keys()) & set(art_by_k.keys()),
                    key=lambda k: -(len(nf_by_k[k]) + len(art_by_k[k])))

    print(f"  Total shared labels: {len(shared)}")
    print(f"  Top 10 most populated shared labels:")
    print(f"    {'label':<10} {'n_NF':>6} {'n_Artin':>8} {'NF_med_disc':>14} {'Artin_med_cond':>15}")
    for k in shared[:10]:
        nf_med = np.median(nf_by_k[k]) if nf_by_k[k] else 0
        art_med = np.median(art_by_k[k]) if art_by_k[k] else 0
        print(f"    {k:<10} {len(nf_by_k[k]):>6} {len(art_by_k[k]):>8} {nf_med:>14.2e} {art_med:>15.2e}")

    conn.close()


if __name__ == "__main__":
    main()
