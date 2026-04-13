"""Decisive test: conductor-matched + shuffled control on both surviving signals."""
import numpy as np
import duckdb
import json
import psycopg2
from pathlib import Path
from collections import defaultdict, deque
from scipy.stats import spearmanr, chi2_contingency

print("DECISIVE TEST")
print("=" * 60)

# SIGNAL 1: Spectral tail vs isogeny class
print("\nSIGNAL 1: Spectral tail vs isogeny class")
print("Conductor-matched + shuffled control")
print("-" * 40)

conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=15)
cur = conn.cursor()
cur.execute("SELECT lmfdb_label, conductor, class_size, rank FROM ec_curvedata "
            "WHERE conductor <= 10000 AND class_size IS NOT NULL LIMIT 30000")
ec_data = {r[0]: {"conductor": int(r[1]), "class_size": int(r[2]),
                   "rank": int(r[3] or 0)} for r in cur.fetchall()}
conn.close()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.lmfdb_label, oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 10000
""").fetchall()
db.close()

matched = []
for label, zvec in rows:
    if label not in ec_data:
        continue
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    matched.append({
        "gamma1": zeros[0],
        "conductor": ec_data[label]["conductor"],
        "class_size": ec_data[label]["class_size"],
    })

print("Matched curves: %d" % len(matched))

gamma1 = np.array([m["gamma1"] for m in matched])
class_size = np.array([m["class_size"] for m in matched])
log_N = np.log10(np.clip([m["conductor"] for m in matched], 2, None))

bins = np.percentile(log_N, np.linspace(0, 100, 11))
within_bin_rhos = []
for b in range(10):
    mask = (log_N >= bins[b]) & (log_N < bins[b + 1])
    if mask.sum() < 50:
        continue
    rho, _ = spearmanr(gamma1[mask], class_size[mask])
    within_bin_rhos.append(rho)

mean_within_rho = np.mean(within_bin_rhos)

null_rhos = []
for trial in range(200):
    shuffled_cs = class_size.copy()
    for b in range(10):
        mask = (log_N >= bins[b]) & (log_N < bins[b + 1])
        idx = np.where(mask)[0]
        shuffled_cs[idx] = np.random.permutation(shuffled_cs[idx])

    bin_rhos = []
    for b in range(10):
        mask = (log_N >= bins[b]) & (log_N < bins[b + 1])
        if mask.sum() < 50:
            continue
        r, _ = spearmanr(gamma1[mask], shuffled_cs[mask])
        bin_rhos.append(r)
    null_rhos.append(np.mean(bin_rhos))

null_mean = np.mean(null_rhos)
null_std = np.std(null_rhos)
z1 = (mean_within_rho - null_mean) / max(null_std, 1e-10)

print("Within-bin rho: %.4f" % mean_within_rho)
print("Shuffled null: mean=%.4f, std=%.4f" % (null_mean, null_std))
print("z-score: %.2f" % z1)
verdict1 = "SURVIVES" if abs(z1) > 3 else "KILLED"
print("SIGNAL 1: %s (z=%.1f)" % (verdict1, z1))

# SIGNAL 2: Congruence community vs rank
print("\nSIGNAL 2: Congruence graph (prime-only + shuffled)")
print("-" * 40)

conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=15)
cur = conn.cursor()
cur.execute("SELECT label, level, traces, analytic_rank FROM mf_newforms "
            "WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL AND level <= 3000 "
            "LIMIT 3000")
mf_rows = cur.fetchall()
conn.close()

primes = [2, 3, 5, 7, 11]
forms = []
for label, level, traces, ar in mf_rows:
    if not traces or len(traces) < 12:
        continue
    ap = [int(float(traces[p - 1])) for p in primes if p <= len(traces)]
    if len(ap) == 5:
        forms.append({"label": label, "rank": int(ar or 0), "ap": ap})

print("Forms: %d" % len(forms))
n = min(len(forms), 2000)

ell = 7
edges = []
for i in range(n):
    for j in range(i + 1, n):
        cong = sum(1 for k in range(5) if forms[i]["ap"][k] % ell == forms[j]["ap"][k] % ell)
        if cong >= 3:
            edges.append((i, j))

print("Edges (mod-%d): %d" % (ell, len(edges)))

adj = defaultdict(set)
for i, j in edges:
    adj[i].add(j)
    adj[j].add(i)

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
contingency = np.zeros((len(top_comms), 3))
for ci, comm in enumerate(top_comms):
    for node in comm:
        if node >= len(forms):
            continue
        r = min(forms[node]["rank"], 2)
        contingency[ci, r] += 1

contingency = contingency[contingency.sum(axis=1) > 0]
z2 = 0.0
verdict2 = "INSUFFICIENT DATA"

if contingency.shape[0] >= 2:
    chi2, p_chi, _, _ = chi2_contingency(contingency)
    print("Chi-squared: %.1f, p=%.2e" % (chi2, p_chi))

    ranks = np.array([min(forms[i]["rank"], 2) for i in range(n)])
    null_chi2s = []
    for _ in range(200):
        sr = np.random.permutation(ranks)
        cn = np.zeros((len(top_comms), 3))
        for ci, comm in enumerate(top_comms):
            for node in comm:
                if node >= len(sr):
                    continue
                cn[ci, sr[node]] += 1
        cn = cn[cn.sum(axis=1) > 0]
        if cn.shape[0] >= 2:
            c2, _, _, _ = chi2_contingency(cn)
            null_chi2s.append(c2)

    if null_chi2s:
        nm = np.mean(null_chi2s)
        ns = np.std(null_chi2s)
        z2 = (chi2 - nm) / max(ns, 1e-10)
        print("Null chi2: mean=%.1f, std=%.1f" % (nm, ns))
        print("z-score: %.2f" % z2)
        verdict2 = "SURVIVES" if z2 > 3 else "KILLED"
        print("SIGNAL 2: %s (z=%.1f)" % (verdict2, z2))

results = {
    "signal_1_spectral_tail": {
        "within_bin_rho": float(mean_within_rho),
        "null_mean": float(null_mean),
        "null_std": float(null_std),
        "z_score": float(z1),
        "verdict": verdict1,
    },
    "signal_2_congruence": {
        "z_score": float(z2),
        "verdict": verdict2,
    },
}

with open("harmonia/results/decisive_test.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to harmonia/results/decisive_test.json")
