"""
Decisive conductor-matched + prime-only + shuffled-control test
for the two surviving Harmonia signals.

SIGNAL 1: Spectral tail encodes isogeny structure
SIGNAL 2: Congruence graph curvature predicts rank
"""
import json, sys, os, time
import numpy as np
import psycopg2
import networkx as nx
from scipy import stats
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

DB_PARAMS = dict(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb'
)

RESULTS = {}

def connect():
    return psycopg2.connect(**DB_PARAMS)

# ========== TEST A: Spectral tail vs isogeny (conductor-matched) ==========

def test_a_spectral_tail():
    print("=" * 70)
    print("TEST A: Spectral tail encodes isogeny structure")
    print("=" * 70)
    conn = connect()
    cur = conn.cursor()

    # Use JOIN with proper format conversion (ec: "11.a" -> lfunc: "EllipticCurve/Q/11/a")
    # Pull in batches by conductor range to avoid timeout
    rows = []
    conductor_ranges = [(1, 10000), (10001, 30000), (30001, 50000), (50001, 100000)]
    for cmin, cmax in conductor_ranges:
        print(f"  Pulling conductor {cmin}-{cmax}...")
        cur.execute("""
            SELECT e.lmfdb_label, e.conductor, e.rank, e.class_size,
                   l.positive_zeros, l.analytic_conductor
            FROM ec_curvedata e
            JOIN lfunc_lfunctions l
                ON l.origin = CONCAT('EllipticCurve/Q/', REPLACE(e.lmfdb_iso, '.', '/'))
            WHERE l.positive_zeros IS NOT NULL AND e.class_size IS NOT NULL
                  AND e.conductor >= %s AND e.conductor <= %s
            LIMIT 10000
        """, (cmin, cmax))
        batch = cur.fetchall()
        print(f"    Got {len(batch)} rows")
        rows.extend(batch)
    print(f"  Total matched: {len(rows)} rows")

    conn.close()

    if len(rows) < 100:
        print("INSUFFICIENT DATA for Test A")
        return {"status": "INSUFFICIENT_DATA", "n": len(rows)}

    # Parse zeros
    data = []
    for row in rows:
        label, cond, rank, class_size, pz_raw, ac = row
        # pz_raw might be a list or postgres array
        if pz_raw is None:
            continue
        if isinstance(pz_raw, str):
            pz_raw = pz_raw.strip('{}')
            zeros = [float(x) for x in pz_raw.split(',') if x.strip()]
        elif isinstance(pz_raw, (list, tuple)):
            zeros = [float(x) for x in pz_raw]
        else:
            continue
        if len(zeros) < 1:
            continue
        gamma1 = zeros[0]  # first zero
        data.append({
            'label': label, 'conductor': int(cond), 'rank': int(rank),
            'class_size': int(class_size), 'gamma1': float(gamma1),
            'analytic_conductor': float(ac) if ac else None
        })

    print(f"\nParsed {len(data)} curves with valid zeros")

    if len(data) < 100:
        print("INSUFFICIENT parsed data for Test A")
        return {"status": "INSUFFICIENT_DATA", "n": len(data)}

    # Bin by conductor (log-scale, tight windows)
    conductors = np.array([d['conductor'] for d in data])
    log_cond = np.log10(conductors + 1)
    # bins of width ~0.5 in log10
    bin_edges = np.arange(log_cond.min(), log_cond.max() + 0.5, 0.5)
    bin_indices = np.digitize(log_cond, bin_edges)

    # Group by bin
    bins = defaultdict(list)
    for i, d in enumerate(data):
        bins[bin_indices[i]].append(d)

    # Filter bins with enough variety
    usable_bins = {k: v for k, v in bins.items() if len(v) >= 10
                   and len(set(d['class_size'] for d in v)) >= 2}
    print(f"Usable conductor bins: {len(usable_bins)} (out of {len(bins)})")
    print(f"Total curves in usable bins: {sum(len(v) for v in usable_bins.values())}")

    if len(usable_bins) < 3:
        print("NOT ENOUGH usable bins")
        return {"status": "INSUFFICIENT_BINS", "n_bins": len(usable_bins)}

    # Within each bin: correlation gamma1 vs class_size
    def compute_pooled_correlation(bin_dict, class_size_key='class_size'):
        """Compute partial correlation controlling for conductor bin."""
        all_gamma1 = []
        all_cs = []
        for bk, items in bin_dict.items():
            g1 = np.array([d['gamma1'] for d in items])
            cs = np.array([d[class_size_key] for d in items])
            # Demean within bin to control for conductor
            g1_dm = g1 - g1.mean()
            cs_dm = cs - cs.mean()
            all_gamma1.extend(g1_dm)
            all_cs.extend(cs_dm)
        all_gamma1 = np.array(all_gamma1)
        all_cs = np.array(all_cs)
        if len(all_gamma1) < 10:
            return 0.0, 1.0
        rho, p = stats.spearmanr(all_gamma1, all_cs)
        return float(rho), float(p)

    real_rho, real_p = compute_pooled_correlation(usable_bins)
    n_total = sum(len(v) for v in usable_bins.values())
    real_z = real_rho * np.sqrt(n_total)
    print(f"\nREAL (conductor-controlled): rho={real_rho:.4f}, p={real_p:.2e}, z={real_z:.2f}")

    # Shuffled control: permute class_size within each bin
    N_SHUFFLE = 500
    shuffle_rhos = []
    rng = np.random.default_rng(42)
    for _ in range(N_SHUFFLE):
        shuffled_bins = {}
        for bk, items in usable_bins.items():
            cs_vals = [d['class_size'] for d in items]
            rng.shuffle(cs_vals)
            shuffled_items = []
            for i, d in enumerate(items):
                sd = dict(d)
                sd['class_size'] = cs_vals[i]
                shuffled_items.append(sd)
            shuffled_bins[bk] = shuffled_items
        sr, _ = compute_pooled_correlation(shuffled_bins)
        shuffle_rhos.append(sr)

    shuffle_rhos = np.array(shuffle_rhos)
    null_mean = float(shuffle_rhos.mean())
    null_std = float(shuffle_rhos.std())
    if null_std > 0:
        z_vs_null = (real_rho - null_mean) / null_std
    else:
        z_vs_null = 0.0

    # How often does shuffled beat real?
    p_empirical = float(np.mean(np.abs(shuffle_rhos) >= np.abs(real_rho)))

    print(f"\nSHUFFLED NULL (500 permutations):")
    print(f"  Null mean: {null_mean:.4f}, Null std: {null_std:.4f}")
    print(f"  Z-score vs null: {z_vs_null:.2f}")
    print(f"  Empirical p: {p_empirical:.4f}")

    survives = abs(z_vs_null) > 3.0 and p_empirical < 0.01
    print(f"\n>>> SIGNAL A {'SURVIVES' if survives else 'KILLED'} <<<")

    result = {
        "signal": "Spectral tail encodes isogeny structure",
        "original_claim": {"rho": -0.088, "z": -12.3},
        "n_curves": n_total,
        "n_bins": len(usable_bins),
        "conductor_controlled": {
            "rho": real_rho, "p": real_p, "z": real_z
        },
        "shuffled_null": {
            "n_permutations": N_SHUFFLE,
            "null_mean": null_mean, "null_std": null_std,
            "z_vs_null": z_vs_null, "empirical_p": p_empirical
        },
        "verdict": "SURVIVES" if survives else "KILLED"
    }
    RESULTS["test_a_spectral_tail"] = result
    return result


# ========== TEST B: Congruence graph curvature predicts rank ==========

def test_b_congruence_graph():
    print("\n" + "=" * 70)
    print("TEST B: Congruence graph curvature predicts rank")
    print("=" * 70)
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT label, level, traces, analytic_rank FROM mf_newforms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL AND level <= 5000
        LIMIT 5000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"Fetched {len(rows)} newforms")

    if len(rows) < 100:
        print("INSUFFICIENT DATA for Test B")
        return {"status": "INSUFFICIENT_DATA", "n": len(rows)}

    # Parse traces
    forms = []
    for label, level, traces_raw, arank in rows:
        if traces_raw is None:
            continue
        if isinstance(traces_raw, str):
            traces_raw = traces_raw.strip('{}')
            traces = [int(x) for x in traces_raw.split(',') if x.strip()]
        elif isinstance(traces_raw, (list, tuple)):
            traces = [int(x) for x in traces_raw]
        else:
            continue
        rank = int(arank) if arank is not None else 0
        forms.append({
            'label': label, 'level': int(level),
            'traces': traces, 'rank': rank
        })

    print(f"Parsed {len(forms)} forms with valid traces")

    # Prime indices (0-based): a_2=index 1, a_3=index 2, a_5=index 4, a_7=index 6, a_11=index 10
    # traces[n] = a_{n+1} typically, i.e. traces[0]=a_1, traces[1]=a_2, ...
    prime_indices = [1, 2, 4, 6, 10]  # a_2, a_3, a_5, a_7, a_11
    composite_indices = [3, 5, 7, 8, 9]  # a_4, a_6, a_8, a_9, a_10

    def build_congruence_graph(forms_list, trace_indices, mod=7, threshold=3):
        """Build congruence graph: connect if >= threshold congruences at given indices."""
        n = len(forms_list)
        G = nx.Graph()
        G.add_nodes_from(range(n))

        # Pre-extract relevant traces mod p
        trace_vecs = []
        for f in forms_list:
            t = f['traces']
            vec = []
            for idx in trace_indices:
                if idx < len(t):
                    vec.append(t[idx] % mod)
                else:
                    vec.append(None)
            trace_vecs.append(vec)

        for i in range(n):
            for j in range(i + 1, n):
                matches = 0
                valid = 0
                for k in range(len(trace_indices)):
                    if trace_vecs[i][k] is not None and trace_vecs[j][k] is not None:
                        valid += 1
                        if trace_vecs[i][k] == trace_vecs[j][k]:
                            matches += 1
                if valid >= 3 and matches >= threshold:
                    G.add_edge(i, j)
        return G

    def get_communities(G):
        """Get community labels for each node."""
        if G.number_of_edges() == 0:
            return None, 0
        try:
            communities = list(nx.algorithms.community.greedy_modularity_communities(G))
        except Exception:
            communities = list(nx.connected_components(G))
        if len(communities) < 2:
            return None, len(communities)
        comm_labels = np.zeros(G.number_of_nodes(), dtype=int)
        for ci, comm in enumerate(communities):
            for node in comm:
                comm_labels[node] = ci
        return comm_labels, len(communities)

    def chi2_from_labels(comm_labels, ranks):
        """Compute chi-squared from pre-computed community labels and rank array."""
        if comm_labels is None:
            return 0.0, 1.0
        unique_comms = sorted(set(comm_labels))
        unique_ranks = sorted(set(ranks))
        if len(unique_ranks) < 2 or len(unique_comms) < 2:
            return 0.0, 1.0
        table = np.zeros((len(unique_comms), len(unique_ranks)), dtype=int)
        comm_map = {c: i for i, c in enumerate(unique_comms)}
        rank_map = {r: i for i, r in enumerate(unique_ranks)}
        for i in range(len(ranks)):
            table[comm_map[comm_labels[i]], rank_map[ranks[i]]] += 1
        table = table[table.sum(axis=1) > 0]
        if table.shape[0] < 2 or table.shape[1] < 2:
            return 0.0, 1.0
        chi2, p, dof, _ = stats.chi2_contingency(table)
        return float(chi2), float(p)

    ranks_arr = np.array([f['rank'] for f in forms])

    # --- PRIME-ONLY graph ---
    print("\nBuilding PRIME-ONLY congruence graph (a_2, a_3, a_5, a_7, a_11 mod 7)...")
    t0 = time.time()
    G_prime = build_congruence_graph(forms, prime_indices)
    print(f"  Built in {time.time()-t0:.1f}s: {G_prime.number_of_nodes()} nodes, {G_prime.number_of_edges()} edges")

    print("Computing communities (prime)...")
    comm_prime, n_comm_prime = get_communities(G_prime)
    chi2_prime, p_prime = chi2_from_labels(comm_prime, ranks_arr)
    print(f"  PRIME: chi2={chi2_prime:.2f}, p={p_prime:.2e}, n_communities={n_comm_prime}")

    # --- COMPOSITE-ONLY graph ---
    print("\nBuilding COMPOSITE-ONLY congruence graph (a_4, a_6, a_8, a_9, a_10 mod 7)...")
    t0 = time.time()
    G_comp = build_congruence_graph(forms, composite_indices)
    print(f"  Built in {time.time()-t0:.1f}s: {G_comp.number_of_nodes()} nodes, {G_comp.number_of_edges()} edges")

    print("Computing communities (composite)...")
    comm_comp, n_comm_comp = get_communities(G_comp)
    chi2_comp, p_comp = chi2_from_labels(comm_comp, ranks_arr)
    print(f"  COMPOSITE: chi2={chi2_comp:.2f}, p={p_comp:.2e}, n_communities={n_comm_comp}")

    # --- SHUFFLED CONTROLS (prime graph, shuffled ranks) ---
    # Reuse fixed community labels, just shuffle rank assignments
    print(f"\nRunning {500} shuffled controls (prime graph)...")
    rng = np.random.default_rng(123)
    shuffle_chi2s = []
    for s in range(500):
        shuffled_ranks = ranks_arr.copy()
        rng.shuffle(shuffled_ranks)
        sc2, _ = chi2_from_labels(comm_prime, shuffled_ranks)
        shuffle_chi2s.append(sc2)
        if (s + 1) % 100 == 0:
            print(f"  {s+1}/500 done")

    shuffle_chi2s = np.array(shuffle_chi2s)
    null_mean_b = float(shuffle_chi2s.mean())
    null_std_b = float(shuffle_chi2s.std())
    if null_std_b > 0:
        z_vs_null_b = (chi2_prime - null_mean_b) / null_std_b
    else:
        z_vs_null_b = 0.0
    p_empirical_b = float(np.mean(shuffle_chi2s >= chi2_prime))

    print(f"\nSHUFFLED NULL (prime graph):")
    print(f"  Null mean: {null_mean_b:.2f}, Null std: {null_std_b:.2f}")
    print(f"  Z-score vs null: {z_vs_null_b:.2f}")
    print(f"  Empirical p: {p_empirical_b:.4f}")

    # --- SHUFFLED CONTROLS (composite graph) ---
    print(f"\nRunning {500} shuffled controls (composite graph)...")
    shuffle_chi2s_comp = []
    rng2 = np.random.default_rng(456)
    for s in range(500):
        shuffled_ranks = ranks_arr.copy()
        rng2.shuffle(shuffled_ranks)
        sc2, _ = chi2_from_labels(comm_comp, shuffled_ranks)
        shuffle_chi2s_comp.append(sc2)
        if (s + 1) % 100 == 0:
            print(f"  {s+1}/500 done")

    shuffle_chi2s_comp = np.array(shuffle_chi2s_comp)
    null_mean_comp = float(shuffle_chi2s_comp.mean())
    null_std_comp = float(shuffle_chi2s_comp.std())
    if null_std_comp > 0:
        z_vs_null_comp = (chi2_comp - null_mean_comp) / null_std_comp
    else:
        z_vs_null_comp = 0.0
    p_empirical_comp = float(np.mean(shuffle_chi2s_comp >= chi2_comp))

    prime_stronger = chi2_prime > chi2_comp and z_vs_null_b > z_vs_null_comp

    survives_b = (z_vs_null_b > 3.0 and p_empirical_b < 0.01 and prime_stronger)

    print(f"\nCOMPOSITE SHUFFLED NULL:")
    print(f"  Null mean: {null_mean_comp:.2f}, Null std: {null_std_comp:.2f}")
    print(f"  Z-score vs null: {z_vs_null_comp:.2f}")
    print(f"  Empirical p: {p_empirical_comp:.4f}")

    print(f"\nPRIME vs COMPOSITE:")
    print(f"  Prime chi2={chi2_prime:.2f} (z={z_vs_null_b:.2f}) vs Composite chi2={chi2_comp:.2f} (z={z_vs_null_comp:.2f})")
    print(f"  Prime stronger: {prime_stronger}")
    print(f"\n>>> SIGNAL B {'SURVIVES' if survives_b else 'KILLED'} <<<")

    result = {
        "signal": "Congruence graph curvature predicts rank",
        "original_claim": {"chi2": 72.4, "p": 1.6e-12},
        "n_forms": len(forms),
        "prime_only": {
            "indices_used": "a_2, a_3, a_5, a_7, a_11",
            "modulus": 7, "threshold": 3,
            "n_edges": G_prime.number_of_edges(),
            "n_communities": n_comm_prime,
            "chi2": chi2_prime, "p": p_prime,
            "shuffled_null": {
                "n_permutations": 500,
                "null_mean": null_mean_b, "null_std": null_std_b,
                "z_vs_null": z_vs_null_b, "empirical_p": p_empirical_b
            }
        },
        "composite_only": {
            "indices_used": "a_4, a_6, a_8, a_9, a_10",
            "modulus": 7, "threshold": 3,
            "n_edges": G_comp.number_of_edges(),
            "n_communities": n_comm_comp,
            "chi2": chi2_comp, "p": p_comp,
            "shuffled_null": {
                "n_permutations": 500,
                "null_mean": null_mean_comp, "null_std": null_std_comp,
                "z_vs_null": z_vs_null_comp, "empirical_p": p_empirical_comp
            }
        },
        "prime_stronger_than_composite": prime_stronger,
        "verdict": "SURVIVES" if survives_b else "KILLED"
    }
    RESULTS["test_b_congruence_graph"] = result
    return result


if __name__ == "__main__":
    print("DECISIVE TEST: Conductor-matched + Prime-only + Shuffled Control")
    print("Date: 2026-04-12")
    print()

    try:
        res_a = test_a_spectral_tail()
    except Exception as e:
        print(f"\nTEST A FAILED WITH ERROR: {e}")
        import traceback; traceback.print_exc()
        RESULTS["test_a_spectral_tail"] = {"status": "ERROR", "error": str(e)}

    try:
        res_b = test_b_congruence_graph()
    except Exception as e:
        print(f"\nTEST B FAILED WITH ERROR: {e}")
        import traceback; traceback.print_exc()
        RESULTS["test_b_congruence_graph"] = {"status": "ERROR", "error": str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for key, val in RESULTS.items():
        v = val.get('verdict', val.get('status', 'UNKNOWN'))
        print(f"  {key}: {v}")

    # Save
    out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'decisive_test.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(RESULTS, f, indent=2)
    print(f"\nResults saved to {out_path}")
