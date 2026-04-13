#!/usr/bin/env python3
"""Congruence Graph: a_p mod ell topology predicts rank?"""
import sys, os, json, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
rng = np.random.default_rng(42)
import duckdb
print("=" * 100)
print("CONGRUENCE GRAPH: Pure arithmetic topology")
print("=" * 100)
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""SELECT aplist, conductor, rank FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL AND conductor BETWEEN 100 AND 5000 LIMIT 5000""").fetchall()
con.close()
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
ec_all = []
for aplist_json, cond, rank in ec_data:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= len(primes):
            ec_all.append({"ap": tuple(int(a) for a in aplist[:len(primes)]), "cond": cond, "rank": rank})
    except: pass
print(f"  EC: {len(ec_all)}")
for ell in [2, 3, 5]:
    for k in [3, 5, 7]:
        print(f"\n--- mod-{ell}, {k} primes ---")
        groups = defaultdict(list)
        for i, ec in enumerate(ec_all):
            fp = tuple(ec["ap"][j] % ell for j in range(k))
            groups[fp].append(i)
        n_g = len(groups)
        sizes = [len(v) for v in groups.values()]
        print(f"  Groups: {n_g}, Max: {max(sizes)}, Isolated: {sum(1 for s in sizes if s == 1)}")
        # eta^2 with permutation null
        labels = [""] * len(ec_all)
        for fp, indices in groups.items():
            for idx in indices: labels[idx] = str(fp)
        ranks = np.array([ec["rank"] for ec in ec_all])
        g_map = defaultdict(list)
        for i, gl in enumerate(labels): g_map[gl].append(ranks[i])
        valid = {kk: np.array(v) for kk, v in g_map.items() if len(v) >= 5}
        if len(valid) >= 2:
            all_v = np.concatenate(list(valid.values()))
            gm = np.mean(all_v)
            ss_t = np.sum((all_v - gm)**2)
            ss_b = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
            eta = ss_b / ss_t if ss_t > 0 else 0
            null_etas = []
            for _ in range(200):
                shuf = ranks.copy(); rng.shuffle(shuf)
                g_s = defaultdict(list)
                for i in range(len(shuf)): g_s[labels[i]].append(shuf[i])
                v_s = {kk: np.array(v) for kk, v in g_s.items() if len(v) >= 5}
                if len(v_s) >= 2:
                    av = np.concatenate(list(v_s.values())); gms = np.mean(av)
                    sst = np.sum((av - gms)**2)
                    ssb = sum(len(v) * (np.mean(v) - gms)**2 for v in v_s.values())
                    null_etas.append(ssb / sst if sst > 0 else 0)
            null_etas = np.array(null_etas)
            z = (eta - np.mean(null_etas)) / np.std(null_etas) if np.std(null_etas) > 0 else 0
            print(f"  eta^2={eta:.4f}, null={np.mean(null_etas):.4f}, z={z:.1f}")
            # degree vs rank
            degrees = np.array([len(groups[tuple(ec["ap"][j] % ell for j in range(k))]) - 1 for ec in ec_all])
            rho, p = spearmanr(degrees, ranks)
            log_c = np.log(np.array([ec["cond"] for ec in ec_all], dtype=float))
            X = np.column_stack([np.ones(len(log_c)), log_c])
            rd = degrees - X @ np.linalg.lstsq(X, degrees.astype(float), rcond=None)[0]
            rr = ranks - X @ np.linalg.lstsq(X, ranks.astype(float), rcond=None)[0]
            rho_p, p_p = spearmanr(rd, rr)
            print(f"  rho(degree, rank)={rho:.4f}  partial|cond={rho_p:.4f} (p={p_p:.2e})")
            if z > 3 and abs(rho_p) > 0.03:
                print(f"  *** SIGNAL: Congruence topology predicts rank (z={z:.0f}) ***")
