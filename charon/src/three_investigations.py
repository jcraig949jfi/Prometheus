"""
Three Investigations from Google Deep Research Leads
=====================================================
All on existing data. No new ingestion.

1. The 165 EC-neighbor Type B forms: what are they?
2. Symmetry type splitting of the giant cluster
3. Murmuration detection in EC a_p data
"""

import duckdb
import numpy as np
import json
import logging
from collections import defaultdict, Counter
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
REPORT_DIR = Path(__file__).parent.parent / "reports"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.investigations')


# ================================================================
# INVESTIGATION 1: The 165 EC-Neighbor Type B Forms
# ================================================================

def investigation_1():
    """
    Deep dive on the 165 higher-dim MFs that have elliptic curve
    zero-space neighbors despite being Type B (no graph edges).

    Questions:
    - What dimensions are they? (dim=2 → possible genus-2 correspondence)
    - Do conductors align with their EC neighbors?
    - Do inferred ranks match?
    - Any patterns suggesting functorial lifts?
    """
    log.info("=" * 60)
    log.info("INVESTIGATION 1: The 165 EC-Neighbor Type B Forms")
    log.info("=" * 60)

    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Find Type B objects that have EC zero-neighbors
    # We need to reconstruct this from the atlas + k-NN
    # First get all Type B MF ids
    type_b_mfs = duck.execute("""
        SELECT da.object_id, da.label, da.conductor, da.zero_coherence
        FROM disagreement_atlas da
        WHERE da.disagreement_type = 'B'
    """).fetchall()

    # Get all objects with zeros for k-NN
    all_objs = duck.execute("""
        SELECT oz.object_id, o.object_type, o.conductor, o.lmfdb_label,
               oz.zeros_vector, oz.n_zeros_stored
        FROM object_zeros oz
        JOIN objects o ON oz.object_id = o.id
        WHERE oz.zeros_vector IS NOT NULL
    """).fetchall()

    # Get MF metadata
    mf_meta = {}
    for row in duck.execute("""
        SELECT mf.object_id, mf.dim, mf.level, mf.weight, mf.char_order,
               mf.is_cm, mf.fricke_eigenval, mf.lmfdb_label
        FROM modular_forms mf
    """).fetchall():
        mf_meta[row[0]] = {'dim': row[1], 'level': row[2], 'weight': row[3],
                           'char_order': row[4], 'is_cm': row[5],
                           'fricke': row[6], 'label': row[7]}

    # Get EC metadata
    ec_meta = {}
    for row in duck.execute("""
        SELECT ec.object_id, ec.lmfdb_label, ec.lmfdb_iso, ec.conductor,
               ec.rank, ec.analytic_rank, ec.torsion, ec.cm
        FROM elliptic_curves ec
    """).fetchall():
        ec_meta[row[0]] = {'label': row[1], 'iso': row[2], 'conductor': row[3],
                           'rank': row[4], 'analytic_rank': row[5],
                           'torsion': row[6], 'cm': row[7]}

    duck.close()

    # Build vectors and k-NN
    from sklearn.neighbors import NearestNeighbors

    obj_list = []
    for oid, otype, cond, label, zvec, nz in all_objs:
        n = min(nz or 0, 20)
        vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(20)]
        obj_list.append({'id': oid, 'type': otype, 'conductor': int(cond),
                         'label': label, 'vec': np.array(vec)})

    id_to_idx = {o['id']: i for i, o in enumerate(obj_list)}
    X = np.array([o['vec'] for o in obj_list])
    means, stds = X.mean(0), X.std(0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X - means) / stds

    nn = NearestNeighbors(n_neighbors=11, metric='euclidean', algorithm='brute')
    nn.fit(X_norm)

    # Find Type B MFs with EC neighbors
    type_b_ids = set(r[0] for r in type_b_mfs)
    type_b_indices = [id_to_idx[oid] for oid in type_b_ids if oid in id_to_idx]

    _, nn_indices = nn.kneighbors(X_norm[type_b_indices])

    ec_neighbor_cases = []
    for i, tb_idx in enumerate(type_b_indices):
        tb_obj = obj_list[tb_idx]
        ec_neighbors = []
        for j_pos in range(1, nn_indices.shape[1]):
            n_idx = nn_indices[i, j_pos]
            n_obj = obj_list[n_idx]
            if n_obj['type'] == 'elliptic_curve':
                dist = np.linalg.norm(X_norm[tb_idx] - X_norm[n_idx])
                ec_neighbors.append({'ec_obj': n_obj, 'dist': dist, 'rank_pos': j_pos})

        if ec_neighbors:
            mf_m = mf_meta.get(tb_obj['id'], {})
            ec_neighbor_cases.append({
                'mf_id': tb_obj['id'],
                'mf_label': tb_obj['label'],
                'mf_conductor': tb_obj['conductor'],
                'mf_dim': mf_m.get('dim'),
                'mf_weight': mf_m.get('weight'),
                'mf_char_order': mf_m.get('char_order'),
                'mf_is_cm': mf_m.get('is_cm'),
                'ec_neighbors': ec_neighbors,
            })

    log.info(f"Type B MFs with EC zero-neighbors: {len(ec_neighbor_cases)}")

    # Analyze the 165
    dims = [c['mf_dim'] for c in ec_neighbor_cases if c['mf_dim'] is not None]
    char_orders = [c['mf_char_order'] for c in ec_neighbor_cases if c['mf_char_order'] is not None]
    weights = [c['mf_weight'] for c in ec_neighbor_cases if c['mf_weight'] is not None]

    log.info(f"\nDimension distribution:")
    for d, n in sorted(Counter(dims).items()):
        log.info(f"  dim {d}: {n}")

    log.info(f"\nCharacter order distribution:")
    for c, n in sorted(Counter(char_orders).items())[:10]:
        log.info(f"  char_order {c}: {n}")

    log.info(f"\nWeight distribution:")
    for w, n in sorted(Counter(weights).items()):
        log.info(f"  weight {w}: {n}")

    # KEY: How many are dim-2? (genus-2 candidates)
    dim2_count = sum(1 for d in dims if d == 2)
    log.info(f"\n*** Dim-2 forms (genus-2 candidates): {dim2_count}/{len(ec_neighbor_cases)} ({dim2_count/len(ec_neighbor_cases)*100:.1f}%) ***")

    # Conductor alignment: how close is MF conductor to EC neighbor conductor?
    log.info(f"\nConductor alignment (MF vs nearest EC neighbor):")
    cond_diffs = []
    cond_ratios = []
    rank_matches = []
    detailed_cases = []

    for case in ec_neighbor_cases:
        best_ec = case['ec_neighbors'][0]  # closest EC
        ec_m = ec_meta.get(best_ec['ec_obj']['id'], {})
        ec_cond = ec_m.get('conductor', 0)
        mf_cond = case['mf_conductor']

        if mf_cond > 0 and ec_cond > 0:
            ratio = max(mf_cond, ec_cond) / min(mf_cond, ec_cond)
            cond_ratios.append(ratio)
            cond_diffs.append(abs(mf_cond - ec_cond))

        detailed_cases.append({
            'mf_label': case['mf_label'],
            'mf_dim': case['mf_dim'],
            'mf_cond': mf_cond,
            'mf_char': case['mf_char_order'],
            'ec_label': ec_m.get('label', '?'),
            'ec_cond': ec_cond,
            'ec_rank': ec_m.get('rank'),
            'ec_torsion': ec_m.get('torsion'),
            'ec_cm': ec_m.get('cm'),
            'zero_dist': best_ec['dist'],
            'nn_rank': best_ec['rank_pos'],
        })

    if cond_ratios:
        cond_ratios = np.array(cond_ratios)
        log.info(f"  Conductor ratio (max/min): mean={cond_ratios.mean():.2f}, median={np.median(cond_ratios):.2f}")
        log.info(f"  Same conductor (ratio=1): {(cond_ratios == 1.0).sum()}")
        log.info(f"  Within 2x: {(cond_ratios <= 2.0).sum()}")
        log.info(f"  Within 5x: {(cond_ratios <= 5.0).sum()}")

    # Show top cases (dim-2, close conductor, low distance)
    dim2_cases = [c for c in detailed_cases if c['mf_dim'] == 2]
    dim2_cases.sort(key=lambda x: x['zero_dist'])

    log.info(f"\n--- TOP DIM-2 CASES (most likely genus-2 candidates) ---")
    for c in dim2_cases[:20]:
        log.info(f"  {c['mf_label']:20s} (dim=2, cond={c['mf_cond']}, char={c['mf_char']}) "
                 f"<-> {c['ec_label']:12s} (cond={c['ec_cond']}, rank={c['ec_rank']}, "
                 f"torsion={c['ec_torsion']}, cm={c['ec_cm']}) "
                 f"zero_dist={c['zero_dist']:.4f}, nn_rank={c['nn_rank']}")

    # Show non-dim-2 cases
    non_dim2 = [c for c in detailed_cases if c['mf_dim'] != 2]
    non_dim2.sort(key=lambda x: x['zero_dist'])
    log.info(f"\n--- TOP NON-DIM-2 CASES (higher-rank phenomena) ---")
    for c in non_dim2[:10]:
        log.info(f"  {c['mf_label']:20s} (dim={c['mf_dim']}, cond={c['mf_cond']}) "
                 f"<-> {c['ec_label']:12s} (cond={c['ec_cond']}, rank={c['ec_rank']}) "
                 f"zero_dist={c['zero_dist']:.4f}")

    return ec_neighbor_cases, detailed_cases


# ================================================================
# INVESTIGATION 2: Symmetry Type Splitting
# ================================================================

def investigation_2():
    """
    Use zero spacing statistics to estimate symmetry type
    (orthogonal vs symplectic vs unitary) for Type B objects.
    Check if the giant cluster splits into subclusters.
    """
    log.info("\n" + "=" * 60)
    log.info("INVESTIGATION 2: Symmetry Type Classification")
    log.info("=" * 60)

    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Get Type B objects with zeros
    rows = duck.execute("""
        SELECT da.object_id, da.label, da.conductor,
               oz.zeros_vector, oz.n_zeros_stored
        FROM disagreement_atlas da
        JOIN object_zeros oz ON da.object_id = oz.object_id
        WHERE da.disagreement_type = 'B'
          AND oz.n_zeros_stored >= 5
    """).fetchall()
    duck.close()

    log.info(f"Type B objects with >= 5 zeros: {len(rows)}")

    # Compute spacing statistics for each object
    # The nearest-neighbor spacing ratio r = min(s_i, s_{i+1}) / max(s_i, s_{i+1})
    # where s_i = gamma_{i+1} - gamma_i
    # Poisson (uncorrelated): <r> ≈ 0.386
    # GOE (orthogonal): <r> ≈ 0.536
    # GUE (unitary): <r> ≈ 0.603
    # GSE (symplectic): <r> ≈ 0.676

    spacing_data = []
    for oid, label, cond, zvec, nz in rows:
        n = min(nz or 0, 20)
        zeros = [float(zvec[i]) for i in range(n) if zvec[i] is not None]
        if len(zeros) < 4:
            continue

        # Compute spacings
        spacings = np.diff(sorted(zeros))
        spacings = spacings[spacings > 0]

        if len(spacings) < 3:
            continue

        # Spacing ratio (nearest-neighbor)
        ratios = []
        for i in range(len(spacings) - 1):
            s1, s2 = spacings[i], spacings[i+1]
            if max(s1, s2) > 0:
                ratios.append(min(s1, s2) / max(s1, s2))

        if not ratios:
            continue

        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        mean_spacing = np.mean(spacings)
        spacing_cv = np.std(spacings) / mean_spacing if mean_spacing > 0 else 0

        spacing_data.append({
            'id': oid, 'label': label, 'conductor': int(cond),
            'mean_ratio': mean_ratio,
            'std_ratio': std_ratio,
            'mean_spacing': mean_spacing,
            'spacing_cv': spacing_cv,
            'n_zeros': len(zeros),
        })

    log.info(f"Objects with computable spacing stats: {len(spacing_data)}")

    # Distribution of mean spacing ratio
    ratios = np.array([s['mean_ratio'] for s in spacing_data])
    log.info(f"\nSpacing ratio distribution:")
    log.info(f"  Mean: {ratios.mean():.4f}")
    log.info(f"  Std: {ratios.std():.4f}")
    log.info(f"  Min: {ratios.min():.4f}, Max: {ratios.max():.4f}")
    log.info(f"\n  Reference values:")
    log.info(f"    Poisson (uncorrelated): 0.386")
    log.info(f"    GOE (orthogonal):       0.536")
    log.info(f"    GUE (unitary):          0.603")
    log.info(f"    GSE (symplectic):        0.676")

    # Classify by nearest reference
    classifications = {'poisson': 0, 'orthogonal': 0, 'unitary': 0, 'symplectic': 0}
    refs = {'poisson': 0.386, 'orthogonal': 0.536, 'unitary': 0.603, 'symplectic': 0.676}
    labels_assigned = []

    for s in spacing_data:
        r = s['mean_ratio']
        best = min(refs.items(), key=lambda x: abs(x[1] - r))
        classifications[best[0]] += 1
        labels_assigned.append(best[0])

    log.info(f"\nClassification (nearest reference):")
    for cls, count in sorted(classifications.items(), key=lambda x: -x[1]):
        pct = count / len(spacing_data) * 100
        log.info(f"  {cls:15s}: {count:>6,} ({pct:.1f}%)")

    # K-means on spacing features to see if natural clusters emerge
    features = np.array([[s['mean_ratio'], s['spacing_cv']] for s in spacing_data])
    features_norm = (features - features.mean(0)) / (features.std(0) + 1e-10)

    for k in [2, 3, 4, 5]:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = km.fit_predict(features_norm)

        # Check if clusters align with reference classifications
        ari = adjusted_rand_score(labels_assigned, cluster_labels)
        sizes = Counter(cluster_labels)
        log.info(f"\n  K-means k={k}: ARI vs reference = {ari:.4f}, sizes = {dict(sorted(sizes.items()))}")

        # Cluster centers in original space
        for ci in range(k):
            mask = cluster_labels == ci
            mr = features[mask, 0].mean()
            cv = features[mask, 1].mean()
            closest_ref = min(refs.items(), key=lambda x: abs(x[1] - mr))
            log.info(f"    Cluster {ci}: mean_ratio={mr:.4f} (~{closest_ref[0]}), spacing_cv={cv:.4f}, n={mask.sum()}")

    # Does splitting improve anything? Check if conductor distribution differs across clusters
    km3 = KMeans(n_clusters=3, random_state=42, n_init=10)
    cl3 = km3.fit_predict(features_norm)

    log.info(f"\n--- K=3 cluster conductor profiles ---")
    for ci in range(3):
        members = [spacing_data[i] for i in range(len(spacing_data)) if cl3[i] == ci]
        conds = [m['conductor'] for m in members]
        log.info(f"  Cluster {ci}: n={len(members)}, "
                 f"conductor range={min(conds)}-{max(conds)}, "
                 f"mean={np.mean(conds):.0f}")

    return spacing_data, classifications


# ================================================================
# INVESTIGATION 3: Murmuration Detection
# ================================================================

def investigation_3():
    """
    Average a_p values from ec_classdata.aplist by conductor bins and rank.
    Look for oscillatory patterns (murmurations).
    """
    log.info("\n" + "=" * 60)
    log.info("INVESTIGATION 3: Murmuration Detection")
    log.info("=" * 60)

    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Get all ECs with aplist and rank (one per isogeny class)
    rows = duck.execute("""
        SELECT ec.lmfdb_iso, ec.conductor, ec.rank, ec.aplist
        FROM elliptic_curves ec
        WHERE ec.aplist IS NOT NULL
        ORDER BY ec.lmfdb_iso
    """).fetchall()
    duck.close()

    # Dedup to one per isogeny class
    seen = set()
    ec_data = []
    for iso, cond, rank, aplist in rows:
        if iso in seen:
            continue
        seen.add(iso)
        if aplist and len(aplist) >= 10 and rank is not None:
            ec_data.append({
                'iso': iso, 'conductor': int(cond),
                'rank': int(rank), 'aplist': [int(a) for a in aplist],
            })

    log.info(f"EC isogeny classes with aplist: {len(ec_data)}")

    # The first 25 primes (what aplist covers)
    primes_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                 73, 79, 83, 89, 97]

    # Bin by conductor and rank
    # Murmurations are visible when you average a_p over conductor ranges
    conductor_bins = [(1, 500), (500, 1000), (1000, 2000), (2000, 3000), (3000, 5000)]

    log.info(f"\n--- Average a_p by conductor bin and rank ---")
    log.info(f"(Murmurations appear as oscillatory patterns in these averages)")

    murmuration_data = {}

    for rank in [0, 1]:
        log.info(f"\nRank {rank}:")
        for lo, hi in conductor_bins:
            curves = [e for e in ec_data if e['rank'] == rank and lo <= e['conductor'] < hi]
            if not curves:
                continue

            # Average a_p across all curves in this bin
            n_primes = min(len(primes_25), min(len(c['aplist']) for c in curves))
            avg_ap = np.zeros(n_primes)
            for c in curves:
                for i in range(n_primes):
                    avg_ap[i] += c['aplist'][i]
            avg_ap /= len(curves)

            key = f"rank{rank}_cond{lo}-{hi}"
            murmuration_data[key] = {
                'rank': rank, 'cond_lo': lo, 'cond_hi': hi,
                'n_curves': len(curves),
                'avg_ap': avg_ap.tolist(),
                'primes': primes_25[:n_primes],
            }

            # Show first 15 primes
            ap_str = ", ".join(f"{a:+.3f}" for a in avg_ap[:15])
            log.info(f"  [{lo:>4}-{hi:>4}] n={len(curves):>4}: {ap_str}")

    # Now the murmuration test: for a fixed prime p, does avg(a_p) oscillate
    # as a function of conductor bin?
    log.info(f"\n--- Murmuration oscillation test ---")
    log.info(f"For each prime, track avg(a_p) across conductor bins by rank")
    log.info(f"Murmurations show OPPOSITE phase for rank 0 vs rank 1")

    for p_idx, p in enumerate(primes_25[:15]):
        vals_r0 = []
        vals_r1 = []
        for lo, hi in conductor_bins:
            key0 = f"rank0_cond{lo}-{hi}"
            key1 = f"rank1_cond{lo}-{hi}"
            if key0 in murmuration_data:
                vals_r0.append(murmuration_data[key0]['avg_ap'][p_idx])
            if key1 in murmuration_data:
                vals_r1.append(murmuration_data[key1]['avg_ap'][p_idx])

        if len(vals_r0) >= 3 and len(vals_r1) >= 3:
            # Check: do rank 0 and rank 1 trends go in opposite directions?
            r0_trend = np.polyfit(range(len(vals_r0)), vals_r0, 1)[0]
            r1_trend = np.polyfit(range(len(vals_r1)), vals_r1, 1)[0]
            opposite = "YES" if (r0_trend > 0) != (r1_trend > 0) else "no"

            # Check for sign changes (oscillation)
            r0_signs = np.diff(np.sign(vals_r0))
            r1_signs = np.diff(np.sign(vals_r1))
            r0_oscillations = np.sum(r0_signs != 0)
            r1_oscillations = np.sum(r1_signs != 0)

            log.info(f"  p={p:3d}: rank0 trend={r0_trend:+.4f}, rank1 trend={r1_trend:+.4f}, "
                     f"opposite={opposite}, oscillations r0={r0_oscillations} r1={r1_oscillations}")

    # Grand test: compute correlation between rank-0 and rank-1 avg_ap sequences
    log.info(f"\n--- Rank-0 vs Rank-1 correlation (murmuration signature) ---")
    for lo, hi in conductor_bins:
        key0 = f"rank0_cond{lo}-{hi}"
        key1 = f"rank1_cond{lo}-{hi}"
        if key0 in murmuration_data and key1 in murmuration_data:
            r0 = np.array(murmuration_data[key0]['avg_ap'])
            r1 = np.array(murmuration_data[key1]['avg_ap'])
            n = min(len(r0), len(r1))
            from scipy.stats import pearsonr
            corr, pval = pearsonr(r0[:n], r1[:n])
            log.info(f"  [{lo:>4}-{hi:>4}]: Pearson r(rank0, rank1) = {corr:+.4f}, p={pval:.4f}")
            if corr < -0.3:
                log.info(f"    *** ANTI-CORRELATED — murmuration signature detected! ***")
            elif corr > 0.3:
                log.info(f"    (positively correlated — not murmuration)")

    return murmuration_data


# ================================================================
# MAIN
# ================================================================

def main():
    log.info("=" * 60)
    log.info("THREE INVESTIGATIONS FROM GOOGLE DEEP RESEARCH LEADS")
    log.info("All on existing data. No new ingestion.")
    log.info("=" * 60)

    ec_cases, detailed = investigation_1()
    spacing_data, classifications = investigation_2()
    murmuration_data = investigation_3()

    log.info("\n" + "=" * 60)
    log.info("ALL THREE INVESTIGATIONS COMPLETE")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
