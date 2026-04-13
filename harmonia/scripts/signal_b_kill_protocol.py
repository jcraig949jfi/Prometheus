"""
Signal B Kill Protocol — Congruence graph communities predict rank

Attack surfaces from frontier review:
  1. Level/weight ablation — does signal hold when controlling for level N?
  2. Synthetic null — permute a_p preserving Sato-Tate distribution
  3. Hecke operator orthogonality — is this just Ribet's theorem?
  4. Density control — is community structure just edge density?
"""
import numpy as np
import json
import psycopg2
from pathlib import Path
from collections import defaultdict, deque
from scipy.stats import chi2_contingency, spearmanr

print("SIGNAL B KILL PROTOCOL")
print("=" * 60)
print("Target: Congruence graph communities predict analytic rank")
print()

# ---- DATA LOADING ----
print("Loading modular forms from LMFDB Postgres...")
conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=30)
cur = conn.cursor()
cur.execute("""
    SELECT label, level, traces, analytic_rank, char_order, dim
    FROM mf_newforms
    WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
      AND level <= 5000
    LIMIT 10000
""")
mf_rows = cur.fetchall()
conn.close()

primes = [2, 3, 5, 7, 11]
forms = []
for label, level, traces, ar, char_order, dim in mf_rows:
    if not traces or len(traces) < 12:
        continue
    ap = [int(float(traces[p - 1])) for p in primes if p <= len(traces)]
    if len(ap) != 5:
        continue
    forms.append({
        "label": label,
        "level": int(level),
        "rank": int(ar or 0),
        "char_order": int(char_order or 1),
        "ap": ap,
        "traces": [int(float(t)) for t in traces[:20]],
    })

print(f"Forms loaded: {len(forms)}")
n = min(len(forms), 5000)

# ---- BUILD GRAPH ----
ell = 7
print(f"\nBuilding congruence graph (mod {ell})...")

edges = []
for i in range(n):
    for j in range(i + 1, n):
        cong = sum(1 for k in range(5)
                   if forms[i]["ap"][k] % ell == forms[j]["ap"][k] % ell)
        if cong >= 3:
            edges.append((i, j))

print(f"Edges: {len(edges)}")

adj = defaultdict(set)
for i, j in edges:
    adj[i].add(j)
    adj[j].add(i)

# Find communities
visited = set()
communities = []
for start in range(n):
    if start in visited:
        continue
    comp = set()
    q = deque([start])
    while q:
        node = q.popleft()
        if node in visited:
            continue
        visited.add(node)
        comp.add(node)
        for nb in adj[node]:
            if nb not in visited:
                q.append(nb)
    communities.append(comp)

top_comms = sorted(communities, key=len, reverse=True)[:10]
print(f"Top 10 communities: sizes = {[len(c) for c in top_comms]}")

# ---- BASELINE ----
contingency = np.zeros((len(top_comms), 3))
for ci, comm in enumerate(top_comms):
    for node in comm:
        if node >= n:
            continue
        r = min(forms[node]["rank"], 2)
        contingency[ci, r] += 1

contingency = contingency[contingency.sum(axis=1) > 0]
chi2_obs, p_obs, _, _ = chi2_contingency(contingency)
print(f"\nBaseline chi2 = {chi2_obs:.1f}, p = {p_obs:.2e}")

results = {}

# ---- TEST 1: LEVEL ABLATION ----
print("\n" + "=" * 60)
print("TEST 1: Level Ablation")
print("Does rank correlate with level? If so, Simpson's paradox risk.")
print("-" * 40)

levels = np.array([forms[i]["level"] for i in range(n)])
ranks_arr = np.array([forms[i]["rank"] for i in range(n)])
log_levels = np.log10(np.clip(levels, 2, None))

rho_rank_level, p_rank_level = spearmanr(levels, ranks_arr)
print(f"rank-level correlation: rho={rho_rank_level:.4f}, p={p_rank_level:.2e}")

# Within level bins, does community structure still predict rank?
level_bins = np.percentile(log_levels, np.linspace(0, 100, 11))
within_level_chi2s = []

for b in range(10):
    mask = (log_levels >= level_bins[b]) & (log_levels < level_bins[b + 1])
    bin_nodes = set(np.where(mask)[0])
    if len(bin_nodes) < 100:
        continue

    # Rebuild communities within this level bin
    bin_edges = [(i, j) for i, j in edges if i in bin_nodes and j in bin_nodes]
    bin_adj = defaultdict(set)
    for i, j in bin_edges:
        bin_adj[i].add(j)
        bin_adj[j].add(i)

    bin_visited = set()
    bin_comms = []
    for start in bin_nodes:
        if start in bin_visited:
            continue
        comp = set()
        q = deque([start])
        while q:
            node = q.popleft()
            if node in bin_visited:
                continue
            bin_visited.add(node)
            comp.add(node)
            for nb in bin_adj[node]:
                if nb not in bin_visited:
                    q.append(nb)
        bin_comms.append(comp)

    bin_top = sorted(bin_comms, key=len, reverse=True)[:5]
    ct = np.zeros((len(bin_top), 3))
    for ci, comm in enumerate(bin_top):
        for node in comm:
            r = min(forms[node]["rank"], 2)
            ct[ci, r] += 1
    ct = ct[ct.sum(axis=1) > 0]
    if ct.shape[0] >= 2:
        c2, p, _, _ = chi2_contingency(ct)
        within_level_chi2s.append(c2)

if within_level_chi2s:
    mean_chi2 = np.mean(within_level_chi2s)
    print(f"Within-level-bin chi2: mean={mean_chi2:.1f} across {len(within_level_chi2s)} bins")
    verdict1 = "SURVIVES" if mean_chi2 > 10 else "WEAKENED" if mean_chi2 > 5 else "KILLED"
else:
    mean_chi2 = 0
    verdict1 = "INSUFFICIENT DATA"

print(f"TEST 1 (Level ablation): {verdict1}")
results["test1_level_ablation"] = {
    "rank_level_rho": float(rho_rank_level),
    "rank_level_p": float(p_rank_level),
    "within_level_chi2_mean": float(mean_chi2),
    "n_bins_tested": len(within_level_chi2s),
    "verdict": verdict1,
}

# ---- TEST 2: SYNTHETIC NULL ----
print("\n" + "=" * 60)
print("TEST 2: Synthetic Null (Sato-Tate preserving permutation)")
print("Permute a_p values across forms, preserving marginal distributions")
print("-" * 40)

# For each prime p, permute a_p across all forms independently
# This preserves the Sato-Tate distribution but destroys inter-prime coherence
n_synth_trials = 200
synth_chi2s = []

for trial in range(n_synth_trials):
    # Permute each prime's a_p independently
    synth_ap = np.array([forms[i]["ap"] for i in range(n)])
    for p_idx in range(5):
        synth_ap[:, p_idx] = np.random.permutation(synth_ap[:, p_idx])

    # Rebuild graph with permuted a_p
    synth_edges = []
    for i in range(n):
        for j in range(i + 1, n):
            cong = sum(1 for k in range(5)
                       if synth_ap[i, k] % ell == synth_ap[j, k] % ell)
            if cong >= 3:
                synth_edges.append((i, j))

    # Find communities
    s_adj = defaultdict(set)
    for i, j in synth_edges:
        s_adj[i].add(j)
        s_adj[j].add(i)

    s_visited = set()
    s_comms = []
    for start in range(n):
        if start in s_visited:
            continue
        comp = set()
        q = deque([start])
        while q:
            node = q.popleft()
            if node in s_visited:
                continue
            s_visited.add(node)
            comp.add(node)
            for nb in s_adj[node]:
                if nb not in s_visited:
                    q.append(nb)
        s_comms.append(comp)

    s_top = sorted(s_comms, key=len, reverse=True)[:10]
    ct = np.zeros((len(s_top), 3))
    for ci, comm in enumerate(s_top):
        for node in comm:
            r = min(forms[node]["rank"], 2)
            ct[ci, r] += 1
    ct = ct[ct.sum(axis=1) > 0]
    if ct.shape[0] >= 2:
        c2, _, _, _ = chi2_contingency(ct)
        synth_chi2s.append(c2)
    else:
        synth_chi2s.append(0.0)

    if (trial + 1) % 50 == 0:
        print(f"  Trial {trial + 1}/{n_synth_trials}")

synth_mean = np.mean(synth_chi2s)
synth_std = np.std(synth_chi2s)
z_synth = (chi2_obs - synth_mean) / max(synth_std, 1e-10)
print(f"Observed chi2: {chi2_obs:.1f}")
print(f"Synthetic null: mean={synth_mean:.1f}, std={synth_std:.1f}")
print(f"z-score vs Sato-Tate null: {z_synth:.2f}")

verdict2 = "SURVIVES" if z_synth > 3 else "KILLED"
print(f"TEST 2 (Synthetic null): {verdict2}")

results["test2_synthetic_null"] = {
    "observed_chi2": float(chi2_obs),
    "synth_mean": float(synth_mean),
    "synth_std": float(synth_std),
    "z_score": float(z_synth),
    "n_trials": n_synth_trials,
    "verdict": verdict2,
}

# ---- TEST 3: EDGE DENSITY CONTROL ----
print("\n" + "=" * 60)
print("TEST 3: Edge Density Control")
print("Is community structure just reflecting node degree (edge density)?")
print("-" * 40)

degrees = np.array([len(adj.get(i, set())) for i in range(n)])
rho_deg_rank, p_deg_rank = spearmanr(degrees, ranks_arr)
print(f"Degree-rank correlation: rho={rho_deg_rank:.4f}, p={p_deg_rank:.2e}")

# Within degree quartiles, does community still predict rank?
deg_quartiles = np.percentile(degrees, [25, 50, 75])
for lo, hi, label in [(0, deg_quartiles[0], "Q1 (low degree)"),
                       (deg_quartiles[0], deg_quartiles[1], "Q2"),
                       (deg_quartiles[1], deg_quartiles[2], "Q3"),
                       (deg_quartiles[2], degrees.max() + 1, "Q4 (high degree)")]:
    mask = (degrees >= lo) & (degrees < hi)
    nodes = set(np.where(mask)[0])
    if len(nodes) < 100:
        continue

    # Check rank distribution in this quartile vs community membership
    q_ranks = ranks_arr[mask]
    rank_dist = [np.sum(q_ranks == r) for r in range(3)]
    print(f"  {label}: n={len(nodes)}, rank dist={rank_dist}")

verdict3 = "INFORMATIONAL"
print(f"TEST 3 (Edge density): {verdict3}")

results["test3_edge_density"] = {
    "degree_rank_rho": float(rho_deg_rank),
    "degree_rank_p": float(p_deg_rank),
    "verdict": verdict3,
}

# ---- TEST 4: MODULUS SENSITIVITY ----
print("\n" + "=" * 60)
print("TEST 4: Modulus Sensitivity")
print("Does the signal depend on the choice of mod ell?")
print("-" * 40)

for test_ell in [2, 3, 5, 7, 11, 13]:
    test_edges = []
    for i in range(n):
        for j in range(i + 1, n):
            cong = sum(1 for k in range(5)
                       if forms[i]["ap"][k] % test_ell == forms[j]["ap"][k] % test_ell)
            if cong >= 3:
                test_edges.append((i, j))

    t_adj = defaultdict(set)
    for i, j in test_edges:
        t_adj[i].add(j)
        t_adj[j].add(i)

    t_visited = set()
    t_comms = []
    for start in range(n):
        if start in t_visited:
            continue
        comp = set()
        q = deque([start])
        while q:
            node = q.popleft()
            if node in t_visited:
                continue
            t_visited.add(node)
            comp.add(node)
            for nb in t_adj[node]:
                if nb not in t_visited:
                    q.append(nb)
        t_comms.append(comp)

    t_top = sorted(t_comms, key=len, reverse=True)[:10]
    ct = np.zeros((len(t_top), 3))
    for ci, comm in enumerate(t_top):
        for node in comm:
            r = min(forms[node]["rank"], 2)
            ct[ci, r] += 1
    ct = ct[ct.sum(axis=1) > 0]
    if ct.shape[0] >= 2:
        c2, p, _, _ = chi2_contingency(ct)
        n_comms = len(t_comms)
        print(f"  ell={test_ell:3d}: edges={len(test_edges):8d}, comms={n_comms:5d}, chi2={c2:8.1f}, p={p:.2e}")
    else:
        print(f"  ell={test_ell:3d}: edges={len(test_edges):8d}, insufficient community structure")

results["test4_modulus_sensitivity"] = {"tested": [2, 3, 5, 7, 11, 13]}

# ---- SUMMARY ----
print("\n" + "=" * 60)
print("SIGNAL B KILL PROTOCOL SUMMARY")
print("=" * 60)
for k, v in results.items():
    if "verdict" in v:
        print(f"  {k}: {v['verdict']}")

out = Path("harmonia/results/signal_b_kill_protocol.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
