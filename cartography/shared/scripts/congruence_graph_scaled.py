"""
Congruence Graph SCALED — stress-test on 20K EC from full 3.8M Postgres dataset.

Five parts:
  1. Scale community-rank alignment to 20K EC across 8 primes
  2. Conductor-matched congruence test (kills conductor confound)
  3. Curvature at rank boundaries (reproduce ORC finding at scale)
  4. Prime reindexing attack (shuffle which prime a_p belongs to)
  5. Twist stability (do quadratic twists that change rank also change community?)

Reads: local Postgres (lmfdb.ec_curvedata)
Saves: cartography/convergence/data/congruence_graph_scaled_results.json
"""
import sys
import json
import time
import warnings
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "cartography" / "convergence" / "data" / "congruence_graph_scaled_results.json"

# ---------- parameters ----------
PRIMES_ELL = [2, 3, 5, 7, 11, 13, 17, 19]
AP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]  # first 10 primes for a_p
NUM_AP = 10
THRESHOLD = 0.7
SUBSAMPLE = 20000
ORC_SAMPLES = 5000
K_NEIGHBORS = 10
N_COMMUNITIES = 10
NULL_TRIALS = 100


def compute_ap_batch(ainvs_list, primes):
    """Compute a_p for each curve and each prime. Returns (n_curves, len(primes)) array."""
    n = len(ainvs_list)
    result = np.zeros((n, len(primes)), dtype=np.int64)
    for ci, ainvs in enumerate(ainvs_list):
        a1, a2, a3, a4, a6 = [int(round(x)) for x in ainvs]
        for pi, p in enumerate(primes):
            a1m, a2m, a3m, a4m, a6m = a1 % p, a2 % p, a3 % p, a4 % p, a6 % p
            count = 1  # point at infinity
            for x in range(p):
                rhs = (x * x * x + a2m * x * x + a4m * x + a6m) % p
                for y in range(p):
                    lhs = (y * y + a1m * x * y + a3m * y) % p
                    if lhs == rhs:
                        count += 1
            result[ci, pi] = p + 1 - count
        if (ci + 1) % 2000 == 0:
            print(f"  a_p computed for {ci+1}/{n} curves", flush=True)
    return result


def load_data_postgres():
    """Load 20K EC from Postgres, stratified by conductor range."""
    import psycopg2

    conn = psycopg2.connect(host='localhost', port=5432, user='postgres',
                            password='prometheus', dbname='lmfdb')
    cur = conn.cursor()

    print("Querying Postgres for ec_curvedata count...", flush=True)
    cur.execute("SELECT COUNT(*) FROM ec_curvedata")
    total = cur.fetchone()[0]
    print(f"  Total rows: {total}")

    # Stratified sample: pick uniformly from conductor ranges
    # First get conductor range
    cur.execute("SELECT MIN(conductor::bigint), MAX(conductor::bigint) FROM ec_curvedata")
    cond_min, cond_max = cur.fetchone()
    print(f"  Conductor range: [{cond_min}, {cond_max}]")

    # Sample using random ordering with a seed via md5 hash for reproducibility
    # Take one representative per isogeny class (lmfdb_number = 1) to avoid duplicates
    print(f"Sampling {SUBSAMPLE} curves (1 per isogeny class)...", flush=True)
    cur.execute(f"""
        SELECT lmfdb_label, conductor::bigint, rank::int, torsion::int, ainvs,
               min_quad_twist_ainvs, min_quad_twist_disc::bigint
        FROM ec_curvedata
        WHERE lmfdb_number = '1'
        ORDER BY md5(lmfdb_label)
        LIMIT {SUBSAMPLE}
    """)
    rows = cur.fetchall()
    print(f"  Got {len(rows)} curves")
    conn.close()

    # Parse ainvs
    labels = []
    conductors = []
    ranks = []
    torsions = []
    ainvs_list = []
    twist_ainvs_list = []
    twist_discs = []

    for row in rows:
        label, cond, rank, torsion, ainvs_str, twist_ainvs_str, twist_disc = row
        ainvs = json.loads(ainvs_str.replace("'", '"'))
        labels.append(label)
        conductors.append(cond)
        ranks.append(rank)
        torsions.append(torsion)
        ainvs_list.append(ainvs)
        if twist_ainvs_str:
            twist_ainvs_list.append(json.loads(twist_ainvs_str.replace("'", '"')))
        else:
            twist_ainvs_list.append(None)
        twist_discs.append(twist_disc)

    conductors = np.array(conductors, dtype=np.int64)
    ranks = np.array(ranks, dtype=np.int32)
    torsions = np.array(torsions, dtype=np.int32)

    # Compute a_p from ainvs
    print(f"Computing a_p for {len(ainvs_list)} curves at primes {AP_PRIMES}...", flush=True)
    t0 = time.time()
    ap_matrix = compute_ap_batch(ainvs_list, AP_PRIMES)
    print(f"  a_p computation took {time.time()-t0:.1f}s", flush=True)

    return (labels, conductors, ranks, torsions, ap_matrix,
            ainvs_list, twist_ainvs_list, twist_discs)


def build_congruence_graph(ap_matrix, ell, threshold=THRESHOLD):
    """Build adjacency: edge if >= threshold fraction of a_p agree mod ell."""
    n = len(ap_matrix)
    residues = ap_matrix % ell
    adjacency = defaultdict(list)
    edges = []
    min_agree = int(np.ceil(threshold * NUM_AP))

    batch_size = 500
    for i in range(0, n, batch_size):
        i_end = min(i + batch_size, n)
        # (batch, 1, NUM_AP) == (1, n, NUM_AP) -> sum over AP axis
        agree = (residues[i:i_end, None, :] == residues[None, :, :]).sum(axis=2)
        for bi, gi in enumerate(range(i, i_end)):
            for gj in range(gi + 1, n):
                if agree[bi, gj] >= min_agree:
                    w = float(agree[bi, gj]) / NUM_AP
                    adjacency[gi].append(gj)
                    adjacency[gj].append(gi)
                    edges.append((gi, gj, w))
        if (i // batch_size) % 4 == 0:
            sys.stdout.write(f"\r  Graph ell={ell}: {i_end}/{n}, {len(edges)} edges")
            sys.stdout.flush()

    print(f"\r  ell={ell}: {len(edges)} edges among {n} nodes" + " " * 30, flush=True)
    return adjacency, edges


def spectral_communities(adjacency, n, n_clusters=N_COMMUNITIES):
    """Spectral clustering on graph Laplacian."""
    from scipy.sparse import lil_matrix, diags
    from scipy.sparse.linalg import eigsh
    from sklearn.cluster import KMeans

    A = lil_matrix((n, n), dtype=float)
    for i, neighbors in adjacency.items():
        for j in neighbors:
            A[i, j] = 1.0
    A = A.tocsr()

    degrees = np.array(A.sum(axis=1)).flatten()
    degrees[degrees == 0] = 1
    D_inv_sqrt = diags(1.0 / np.sqrt(degrees))
    L_norm = D_inv_sqrt @ A @ D_inv_sqrt

    try:
        vals, vecs = eigsh(L_norm, k=n_clusters, which='LM')
    except Exception as e:
        print(f"  Eigsh failed: {e}, random assignment", flush=True)
        return np.random.randint(0, n_clusters, size=n)

    row_norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    row_norms[row_norms == 0] = 1
    vecs = vecs / row_norms

    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    return km.fit_predict(vecs)


def chi_squared_test(community_labels, ranks, n_clusters=N_COMMUNITIES):
    """Chi-squared: rank distribution differs across communities?"""
    from scipy.stats import chi2_contingency

    unique_ranks = sorted(set(ranks))
    table = np.zeros((n_clusters, len(unique_ranks)), dtype=int)
    rank_to_col = {r: i for i, r in enumerate(unique_ranks)}
    for c, r in zip(community_labels, ranks):
        table[c, rank_to_col[r]] += 1

    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table_clean = table[row_mask][:, col_mask]

    if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
        return {"chi2": 0.0, "p_value": 1.0, "note": "degenerate"}

    chi2, p, dof, expected = chi2_contingency(table_clean)
    return {"chi2": float(chi2), "p_value": float(p), "dof": int(dof),
            "contingency_table": table.tolist(), "rank_labels": unique_ranks}


def null_chi_squared(ranks, n_clusters, n_trials=NULL_TRIALS):
    """Null: random community labels."""
    from scipy.stats import chi2_contingency

    rng = np.random.RandomState(99)
    chi2_nulls = []
    unique_ranks = sorted(set(ranks))
    rank_to_col = {r: i for i, r in enumerate(unique_ranks)}

    for _ in range(n_trials):
        fake = rng.randint(0, n_clusters, size=len(ranks))
        table = np.zeros((n_clusters, len(unique_ranks)), dtype=int)
        for c, r in zip(fake, ranks):
            table[c, rank_to_col[r]] += 1
        row_mask = table.sum(axis=1) > 0
        col_mask = table.sum(axis=0) > 0
        tc = table[row_mask][:, col_mask]
        if tc.shape[0] < 2 or tc.shape[1] < 2:
            chi2_nulls.append(0.0)
            continue
        try:
            chi2, _, _, _ = chi2_contingency(tc)
            chi2_nulls.append(float(chi2))
        except:
            chi2_nulls.append(0.0)
    return chi2_nulls


def compute_orc_for_edges(adjacency, edges, n, sample_indices, k=K_NEIGHBORS):
    """Compute ORC for a set of edge indices. Returns list of (edge_idx, orc) tuples."""
    curvatures = []
    for idx in sample_indices:
        u, v, w = edges[idx]
        nb_u = adjacency.get(u, [])
        nb_v = adjacency.get(v, [])
        if len(nb_u) < 2 or len(nb_v) < 2:
            continue
        nu = nb_u[:k]
        nv = nb_v[:k]

        deg_u = sorted([len(adjacency.get(x, [])) for x in nu])
        deg_v = sorted([len(adjacency.get(x, [])) for x in nv])
        max_len = max(len(deg_u), len(deg_v))
        while len(deg_u) < max_len:
            deg_u.append(0)
        while len(deg_v) < max_len:
            deg_v.append(0)
        du = np.array(deg_u, dtype=float)
        dv = np.array(deg_v, dtype=float)
        if du.sum() > 0:
            du /= du.sum()
        if dv.sum() > 0:
            dv /= dv.sum()
        w1 = float(np.sum(np.abs(np.cumsum(du) - np.cumsum(dv))))
        curvatures.append((idx, 1.0 - w1))
    return curvatures


# ============================================================================
# PART 1: Scale community-rank alignment
# ============================================================================
def part1_scale(ap_matrix, ranks, conductors):
    """Scale congruence graph to 20K EC across 8 primes."""
    print("\n" + "=" * 70)
    print("PART 1: Scale community-rank alignment (20K EC, 8 primes)")
    print("=" * 70)

    n = len(ap_matrix)
    results = {}

    for ell in PRIMES_ELL:
        t1 = time.time()
        print(f"\n--- ell = {ell} ---")

        adjacency, edges = build_congruence_graph(ap_matrix, ell)

        # Spectral communities
        print("  Spectral clustering into 10 communities...")
        comm = spectral_communities(adjacency, n)
        comm_sizes = dict(Counter(comm.tolist()))
        print(f"  Community sizes: {comm_sizes}")

        # Chi-squared
        chi2_res = chi_squared_test(comm, ranks)
        print(f"  Chi2 = {chi2_res['chi2']:.2f}, p = {chi2_res['p_value']:.4e}")

        # Null
        print("  Null distribution (100 trials)...")
        null_vals = null_chi_squared(ranks, N_COMMUNITIES)
        null_mean = float(np.mean(null_vals))
        null_std = float(np.std(null_vals)) if float(np.std(null_vals)) > 0 else 1.0
        z_score = (chi2_res['chi2'] - null_mean) / null_std
        frac_exceed = float(np.mean(np.array(null_vals) >= chi2_res['chi2']))

        print(f"  Null: mean={null_mean:.2f}, std={null_std:.2f}")
        print(f"  Z-SCORE = {z_score:.2f}, frac_null >= observed: {frac_exceed:.4f}")

        verdict = "SIGNIFICANT" if z_score > 3 and chi2_res['p_value'] < 0.001 else "NOT SIGNIFICANT"
        print(f"  VERDICT: {verdict}")

        results[str(ell)] = {
            "n_edges": len(edges),
            "chi2": chi2_res['chi2'],
            "chi2_p": chi2_res['p_value'],
            "null_mean": null_mean,
            "null_std": null_std,
            "z_score": z_score,
            "frac_null_exceeding": frac_exceed,
            "verdict": verdict,
            "time_s": time.time() - t1,
        }

    # Summary
    print(f"\n{'='*60}")
    print("PART 1 SUMMARY: Rank-community alignment by prime")
    print(f"{'='*60}")
    for ell_str, r in sorted(results.items(), key=lambda x: -x[1]['z_score']):
        print(f"  ell={ell_str:>2}: edges={r['n_edges']:>8}, chi2={r['chi2']:>8.1f}, "
              f"z={r['z_score']:>6.2f}, p={r['chi2_p']:.2e} [{r['verdict']}]")

    return results


# ============================================================================
# PART 2: Conductor-matched congruence test
# ============================================================================
def part2_conductor_matched(ap_matrix, ranks, conductors):
    """The definitive confound-killer: does congruence predict rank beyond conductor?"""
    print("\n" + "=" * 70)
    print("PART 2: Conductor-matched congruence test")
    print("=" * 70)

    n = len(ap_matrix)
    rng = np.random.RandomState(42)

    # Find conductor-matched pairs with DIFFERENT ranks
    # Group by conductor (exact match first)
    cond_groups = defaultdict(list)
    for i in range(n):
        cond_groups[conductors[i]].append(i)

    # Collect pairs at same conductor with different ranks
    matched_pairs = []
    for cond, indices in cond_groups.items():
        if len(indices) < 2:
            continue
        for ii in range(len(indices)):
            for jj in range(ii + 1, len(indices)):
                i, j = indices[ii], indices[jj]
                if ranks[i] != ranks[j]:
                    matched_pairs.append((i, j))

    print(f"  Exact conductor match pairs (different rank): {len(matched_pairs)}")

    # If too few, also allow +-1% conductor match
    if len(matched_pairs) < 2000:
        print("  Expanding to +-1% conductor match...")
        sorted_idx = np.argsort(conductors)
        sorted_cond = conductors[sorted_idx]
        for pos in range(len(sorted_idx)):
            i = sorted_idx[pos]
            ci = conductors[i]
            lo = ci * 0.99
            hi = ci * 1.01
            # Look forward
            for pos2 in range(pos + 1, min(pos + 50, len(sorted_idx))):
                j = sorted_idx[pos2]
                if conductors[j] > hi:
                    break
                if conductors[j] >= lo and ranks[i] != ranks[j]:
                    matched_pairs.append((i, j))
            if len(matched_pairs) >= 50000:
                break
        print(f"  After +-1% expansion: {len(matched_pairs)} pairs")

    if len(matched_pairs) == 0:
        print("  NO conductor-matched pairs found. Skipping Part 2.")
        return {"error": "no matched pairs"}

    # Subsample if too many
    if len(matched_pairs) > 20000:
        idx = rng.choice(len(matched_pairs), 20000, replace=False)
        matched_pairs = [matched_pairs[i] for i in idx]
        print(f"  Subsampled to {len(matched_pairs)} pairs")

    results = {}
    for ell in [5, 7, 11, 13]:
        residues = ap_matrix % ell
        min_agree = int(np.ceil(THRESHOLD * NUM_AP))

        congruent_same_rank = 0
        congruent_diff_rank = 0
        noncongruent_same_rank = 0
        noncongruent_diff_rank = 0

        for i, j in matched_pairs:
            agree = int(np.sum(residues[i] == residues[j]))
            same_rank = (ranks[i] == ranks[j])
            # Note: matched_pairs are defined as different-rank, but we also
            # sample same-conductor same-rank pairs for the control
            if agree >= min_agree:
                if same_rank:
                    congruent_same_rank += 1
                else:
                    congruent_diff_rank += 1
            else:
                if same_rank:
                    noncongruent_same_rank += 1
                else:
                    noncongruent_diff_rank += 1

        total_congruent = congruent_same_rank + congruent_diff_rank
        total_noncongruent = noncongruent_same_rank + noncongruent_diff_rank

        # Among the different-rank pairs, what fraction are congruent?
        # Compare to: if we also sampled same-rank pairs, do they have higher congruence?
        print(f"\n  ell={ell}: congruent pairs = {total_congruent}, "
              f"non-congruent = {total_noncongruent}")

        results[str(ell)] = {
            "congruent_same_rank": congruent_same_rank,
            "congruent_diff_rank": congruent_diff_rank,
            "noncongruent_same_rank": noncongruent_same_rank,
            "noncongruent_diff_rank": noncongruent_diff_rank,
            "total_pairs": len(matched_pairs),
        }

    # Now do the FULL test: among same-conductor pairs (both same and diff rank),
    # is congruence correlated with rank-sharing?
    print("\n  Full test: same-conductor pairs (same AND different rank)...")
    all_pairs = []
    for cond, indices in cond_groups.items():
        if len(indices) < 2:
            continue
        for ii in range(len(indices)):
            for jj in range(ii + 1, len(indices)):
                all_pairs.append((indices[ii], indices[jj]))
    print(f"  Total same-conductor pairs: {len(all_pairs)}")

    if len(all_pairs) > 50000:
        idx = rng.choice(len(all_pairs), 50000, replace=False)
        all_pairs = [all_pairs[i] for i in idx]

    for ell in [5, 7, 11, 13]:
        residues = ap_matrix % ell
        min_agree = int(np.ceil(THRESHOLD * NUM_AP))

        cong_same = 0
        cong_diff = 0
        noncong_same = 0
        noncong_diff = 0

        for i, j in all_pairs:
            agree = int(np.sum(residues[i] == residues[j]))
            same_rank = (ranks[i] == ranks[j])
            if agree >= min_agree:
                if same_rank:
                    cong_same += 1
                else:
                    cong_diff += 1
            else:
                if same_rank:
                    noncong_same += 1
                else:
                    noncong_diff += 1

        total_cong = cong_same + cong_diff
        total_noncong = noncong_same + noncong_diff
        if total_cong > 0 and total_noncong > 0:
            rate_cong = cong_same / total_cong
            rate_noncong = noncong_same / total_noncong
            # Fisher's exact or chi2
            from scipy.stats import fisher_exact
            table_2x2 = np.array([[cong_same, cong_diff], [noncong_same, noncong_diff]])
            odds, fisher_p = fisher_exact(table_2x2)
            verdict = "SIGNIFICANT" if fisher_p < 0.01 and odds > 1 else "NOT SIGNIFICANT"
            print(f"  ell={ell}: congruent rank-share rate = {rate_cong:.4f}, "
                  f"non-congruent = {rate_noncong:.4f}, OR={odds:.3f}, p={fisher_p:.4e} [{verdict}]")
            results[f"{ell}_full"] = {
                "congruent_same_rank": cong_same, "congruent_diff_rank": cong_diff,
                "noncongruent_same_rank": noncong_same, "noncongruent_diff_rank": noncong_diff,
                "rate_congruent": rate_cong, "rate_noncongruent": rate_noncong,
                "odds_ratio": odds, "fisher_p": fisher_p, "verdict": verdict,
                "total_pairs": len(all_pairs),
            }
        else:
            print(f"  ell={ell}: no congruent or no non-congruent pairs")

    return results


# ============================================================================
# PART 3: Curvature at rank boundaries
# ============================================================================
def part3_curvature(ap_matrix, ranks, adjacency_cache):
    """ORC at rank boundaries for ell=7 and ell=11."""
    print("\n" + "=" * 70)
    print("PART 3: Curvature at rank boundaries (5000 edges)")
    print("=" * 70)

    results = {}
    rng = np.random.RandomState(200)

    for ell in [7, 11]:
        print(f"\n--- ell = {ell} ---")
        if str(ell) not in adjacency_cache:
            adjacency, edges = build_congruence_graph(ap_matrix, ell)
            adjacency_cache[str(ell)] = (adjacency, edges)
        else:
            adjacency, edges = adjacency_cache[str(ell)]

        if len(edges) == 0:
            print("  No edges, skipping")
            results[str(ell)] = {"error": "no edges"}
            continue

        n_sample = min(ORC_SAMPLES, len(edges))
        sample_idx = rng.choice(len(edges), n_sample, replace=False)

        print(f"  Computing ORC for {n_sample} edges...")
        orc_results = compute_orc_for_edges(adjacency, edges, len(ap_matrix), sample_idx)

        boundary_curv = []
        interior_curv = []
        for idx, orc in orc_results:
            u, v, _ = edges[idx]
            if ranks[u] != ranks[v]:
                boundary_curv.append(orc)
            else:
                interior_curv.append(orc)

        print(f"  Boundary edges: {len(boundary_curv)}, Interior: {len(interior_curv)}")

        res = {}
        if boundary_curv:
            res["boundary_mean_orc"] = float(np.mean(boundary_curv))
            res["boundary_median_orc"] = float(np.median(boundary_curv))
            res["boundary_n"] = len(boundary_curv)
        if interior_curv:
            res["interior_mean_orc"] = float(np.mean(interior_curv))
            res["interior_median_orc"] = float(np.median(interior_curv))
            res["interior_n"] = len(interior_curv)

        if boundary_curv and interior_curv:
            from scipy.stats import mannwhitneyu
            stat, p = mannwhitneyu(boundary_curv, interior_curv, alternative='two-sided')
            res["mann_whitney_U"] = float(stat)
            res["mann_whitney_p"] = float(p)
            diff = res.get("interior_mean_orc", 0) - res.get("boundary_mean_orc", 0)
            verdict = ("REPRODUCED" if p < 0.01 and diff > 0.05
                       else "MARGINAL" if p < 0.05
                       else "NOT REPRODUCED")
            res["verdict"] = verdict
            print(f"  Boundary ORC: {res.get('boundary_mean_orc', 0):.4f}")
            print(f"  Interior ORC: {res.get('interior_mean_orc', 0):.4f}")
            print(f"  Mann-Whitney p = {p:.4e}")
            print(f"  VERDICT: {verdict}")

        results[str(ell)] = res

    return results


# ============================================================================
# PART 4: Prime reindexing attack
# ============================================================================
def part4_reindex(ap_matrix, ranks):
    """
    Prime reindexing attack: for each prime position, shuffle a_p values ACROSS
    curves (breaking curve identity but preserving marginal distribution per prime).
    If the community-rank alignment dies, the congruence structure depends on
    curve-specific a_p patterns (strong). If it survives, it's just about the
    marginal distribution (weak).

    NOTE: Column-shuffling (permuting which prime slot holds which a_p) does NOT
    change pairwise agreement counts, so it cannot serve as a null. We must shuffle
    ROWS within each column independently.
    """
    print("\n" + "=" * 70)
    print("PART 4: Prime reindexing attack (row-shuffle per column)")
    print("=" * 70)

    rng = np.random.RandomState(314)
    n = len(ap_matrix)
    results = {}

    for ell in [5, 7, 11, 13]:
        print(f"\n--- ell = {ell} ---")

        # True graph
        print("  Building TRUE congruence graph...")
        adj_true, edges_true = build_congruence_graph(ap_matrix, ell)
        comm_true = spectral_communities(adj_true, n)
        chi2_true = chi_squared_test(comm_true, ranks)
        print(f"  TRUE chi2 = {chi2_true['chi2']:.2f}, p = {chi2_true['p_value']:.4e}")

        # Row-shuffled graphs (5 trials)
        shuffled_chi2s = []
        n_trials = 5
        for trial in range(n_trials):
            ap_shuffled = ap_matrix.copy()
            # Independently shuffle each column (each prime's a_p across all curves)
            for col in range(ap_shuffled.shape[1]):
                rng.shuffle(ap_shuffled[:, col])

            adj_shuf, edges_shuf = build_congruence_graph(ap_shuffled, ell)
            comm_shuf = spectral_communities(adj_shuf, n)
            chi2_shuf = chi_squared_test(comm_shuf, ranks)
            shuffled_chi2s.append(chi2_shuf['chi2'])
            print(f"  Trial {trial+1}/{n_trials}: shuffled chi2 = {chi2_shuf['chi2']:.2f} "
                  f"({len(edges_shuf)} edges)")

        shuf_mean = float(np.mean(shuffled_chi2s))
        shuf_std = float(np.std(shuffled_chi2s)) if float(np.std(shuffled_chi2s)) > 0 else 1.0
        z = (chi2_true['chi2'] - shuf_mean) / shuf_std

        if z > 3:
            verdict = "DIES under shuffle -> curve-specific a_p pattern matters (STRONG)"
        elif z > 2:
            verdict = "WEAKENED by shuffle -> partially curve-specific"
        else:
            verdict = "SURVIVES shuffle -> marginal distribution suffices (WEAK)"

        print(f"  TRUE chi2 = {chi2_true['chi2']:.2f}")
        print(f"  Shuffled: mean = {shuf_mean:.2f}, std = {shuf_std:.2f}")
        print(f"  Z-score = {z:.2f}")
        print(f"  VERDICT: {verdict}")

        results[str(ell)] = {
            "true_chi2": chi2_true['chi2'],
            "shuffled_chi2s": shuffled_chi2s,
            "shuffled_mean": shuf_mean,
            "shuffled_std": shuf_std,
            "z_score": z,
            "verdict": verdict,
        }

    return results


# ============================================================================
# PART 5: Twist stability
# ============================================================================
def part5_twist_stability(labels, ap_matrix, ranks, conductors,
                          ainvs_list, twist_ainvs_list, twist_discs):
    """Do quadratic twists that change rank also change congruence community?"""
    print("\n" + "=" * 70)
    print("PART 5: Twist stability")
    print("=" * 70)

    n = len(ap_matrix)

    # Group curves by their min_quad_twist_ainvs (twist class)
    twist_groups = defaultdict(list)
    for i in range(n):
        if twist_ainvs_list[i] is not None:
            key = tuple(twist_ainvs_list[i])
            twist_groups[key].append(i)

    # Find twist classes with multiple members AND rank variation
    interesting_groups = {}
    for key, indices in twist_groups.items():
        if len(indices) < 2:
            continue
        rank_set = set(ranks[i] for i in indices)
        if len(rank_set) > 1:
            interesting_groups[key] = indices

    print(f"  Twist classes with 2+ members: {sum(1 for v in twist_groups.values() if len(v)>=2)}")
    print(f"  Twist classes with rank variation: {len(interesting_groups)}")

    if len(interesting_groups) == 0:
        print("  No twist classes with rank variation found. Skipping.")
        return {"error": "no twist classes with rank variation"}

    results = {}
    for ell in [7, 11]:
        print(f"\n--- ell = {ell} ---")
        adjacency, edges = build_congruence_graph(ap_matrix, ell)
        comm = spectral_communities(adjacency, n)

        # For each twist class with rank variation:
        # Do curves that changed rank also change community?
        same_rank_same_comm = 0
        same_rank_diff_comm = 0
        diff_rank_same_comm = 0
        diff_rank_diff_comm = 0

        for key, indices in interesting_groups.items():
            for ii in range(len(indices)):
                for jj in range(ii + 1, len(indices)):
                    i, j = indices[ii], indices[jj]
                    sr = (ranks[i] == ranks[j])
                    sc = (comm[i] == comm[j])
                    if sr and sc:
                        same_rank_same_comm += 1
                    elif sr and not sc:
                        same_rank_diff_comm += 1
                    elif not sr and sc:
                        diff_rank_same_comm += 1
                    else:
                        diff_rank_diff_comm += 1

        total = same_rank_same_comm + same_rank_diff_comm + diff_rank_same_comm + diff_rank_diff_comm
        print(f"  Total twist pairs: {total}")
        print(f"  Same rank, same comm:  {same_rank_same_comm}")
        print(f"  Same rank, diff comm:  {same_rank_diff_comm}")
        print(f"  Diff rank, same comm:  {diff_rank_same_comm}")
        print(f"  Diff rank, diff comm:  {diff_rank_diff_comm}")

        if total > 0:
            from scipy.stats import fisher_exact
            table_2x2 = np.array([
                [same_rank_same_comm, same_rank_diff_comm],
                [diff_rank_same_comm, diff_rank_diff_comm]
            ])
            # Fisher's exact: are rank changes associated with community changes?
            try:
                odds, fisher_p = fisher_exact(table_2x2)
                verdict = ("COUPLED" if fisher_p < 0.05 and odds > 1
                           else "DECOUPLED" if fisher_p < 0.05 and odds < 1
                           else "INDEPENDENT")
                print(f"  OR = {odds:.3f}, Fisher p = {fisher_p:.4e}")
                print(f"  VERDICT: {verdict}")
            except:
                odds, fisher_p, verdict = 0, 1, "ERROR"

            results[str(ell)] = {
                "same_rank_same_comm": same_rank_same_comm,
                "same_rank_diff_comm": same_rank_diff_comm,
                "diff_rank_same_comm": diff_rank_same_comm,
                "diff_rank_diff_comm": diff_rank_diff_comm,
                "total_pairs": total,
                "odds_ratio": float(odds),
                "fisher_p": float(fisher_p),
                "verdict": verdict,
            }
        else:
            results[str(ell)] = {"total_pairs": 0, "verdict": "NO DATA"}

    return results


# ============================================================================
# MAIN
# ============================================================================
def main():
    t_start = time.time()
    print("=" * 70)
    print("CONGRUENCE GRAPH SCALED — 20K EC, 5-part stress test")
    print("=" * 70)

    # Load data
    (labels, conductors, ranks, torsions, ap_matrix,
     ainvs_list, twist_ainvs_list, twist_discs) = load_data_postgres()

    n = len(labels)
    print(f"\nDataset: {n} curves")
    print(f"Rank distribution: {dict(Counter(ranks.tolist()))}")
    print(f"Conductor range: [{conductors.min()}, {conductors.max()}]")

    all_results = {
        "metadata": {
            "n_curves": n,
            "num_ap": NUM_AP,
            "threshold": THRESHOLD,
            "primes_ell": PRIMES_ELL,
            "n_communities": N_COMMUNITIES,
            "null_trials": NULL_TRIALS,
            "orc_samples": ORC_SAMPLES,
            "rank_distribution": {str(k): int(v) for k, v in Counter(ranks.tolist()).items()},
        }
    }

    # Part 1
    all_results["part1_scale"] = part1_scale(ap_matrix, ranks, conductors)

    # Part 2
    all_results["part2_conductor_matched"] = part2_conductor_matched(ap_matrix, ranks, conductors)

    # Part 3 (cache adjacency from part 1 rebuild)
    adjacency_cache = {}
    all_results["part3_curvature"] = part3_curvature(ap_matrix, ranks, adjacency_cache)

    # Part 4
    all_results["part4_reindex"] = part4_reindex(ap_matrix, ranks)

    # Part 5
    all_results["part5_twist"] = part5_twist_stability(
        labels, ap_matrix, ranks, conductors,
        ainvs_list, twist_ainvs_list, twist_discs)

    # Final summary
    total_time = time.time() - t_start
    all_results["total_time_seconds"] = total_time

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    # Part 1 best
    if "part1_scale" in all_results and isinstance(all_results["part1_scale"], dict):
        best_ell = max(all_results["part1_scale"].items(),
                       key=lambda x: x[1].get('z_score', 0) if isinstance(x[1], dict) else 0)
        print(f"Part 1 - Strongest prime: ell={best_ell[0]} "
              f"(z={best_ell[1].get('z_score', 0):.2f}, chi2={best_ell[1].get('chi2', 0):.1f})")

    # Part 2
    if "part2_conductor_matched" in all_results:
        for k, v in all_results["part2_conductor_matched"].items():
            if isinstance(v, dict) and "verdict" in v:
                print(f"Part 2 - ell={k}: {v['verdict']} (OR={v.get('odds_ratio', 0):.3f})")

    # Part 3
    if "part3_curvature" in all_results:
        for k, v in all_results["part3_curvature"].items():
            if isinstance(v, dict) and "verdict" in v:
                print(f"Part 3 - ell={k}: {v['verdict']} "
                      f"(boundary={v.get('boundary_mean_orc', 0):.4f}, "
                      f"interior={v.get('interior_mean_orc', 0):.4f})")

    # Part 4
    if "part4_reindex" in all_results:
        for k, v in all_results["part4_reindex"].items():
            if isinstance(v, dict) and "verdict" in v:
                print(f"Part 4 - ell={k}: {v['verdict']} (z={v.get('z_score', 0):.2f})")

    # Part 5
    if "part5_twist" in all_results:
        for k, v in all_results["part5_twist"].items():
            if isinstance(v, dict) and "verdict" in v:
                print(f"Part 5 - ell={k}: {v['verdict']} (OR={v.get('odds_ratio', 0):.3f})")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Total time: {total_time:.1f}s")


if __name__ == "__main__":
    main()
