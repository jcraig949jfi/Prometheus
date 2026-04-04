"""
Extended Ablation: 36-zero resolution test.
Compare clustering with 20-zero vs extended vectors.

Key question: Does the spectral tail signal get SHARPER or BLURRIER
when we use more zeros?
"""

import duckdb
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"


def load_extended_data(min_zeros=20):
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_url, conductor, rank, zeros_vector, n_zeros_raw
        FROM object_zeros_ext
        WHERE n_zeros_raw >= ?
    """, [min_zeros]).fetchall()
    con.close()

    data = []
    for url, cond, rank, zvec, nz_raw in rows:
        zeros = np.array([float(z) for z in zvec[:36]])
        root_num = float(zvec[36]) if len(zvec) > 36 else 1.0
        data.append({
            "url": url, "conductor": int(cond), "rank": int(rank),
            "root_num": root_num, "zeros": zeros, "n_raw": nz_raw
        })
    return data


def compute_ari(objects, zero_slice):
    """Compute ARI using k-means within conductor strata."""
    by_cond = defaultdict(list)
    for d in objects:
        by_cond[d["conductor"]].append(d)

    aris = []
    for c, objs in by_cond.items():
        if len(objs) < 5:
            continue
        ranks = [o["rank"] for o in objs]
        if len(set(ranks)) < 2:
            continue
        X = np.array([o["zeros"][zero_slice] for o in objs])
        if X.shape[1] == 0:
            continue
        k = max(2, min(len(objs) // 2, 5))
        try:
            pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
            aris.append(adjusted_rand_score(ranks, pred))
        except:
            pass
    return np.mean(aris) if aris else float('nan'), len(aris)


def main():
    # Use objects with 25+ raw zeros (most of our data)
    data = load_extended_data(min_zeros=25)
    print(f"Loaded {len(data)} ECs with 25+ raw zeros")
    print(f"Rank distribution: {dict(sorted(defaultdict(int, {r: sum(1 for d in data if d['rank']==r) for r in set(d['rank'] for d in data)}).items()))}")
    print()

    # === ABLATION SWEEP ===
    print("=" * 72)
    print("ABLATION SWEEP: Which zero ranges carry the most rank signal?")
    print("=" * 72)
    print(f"{'Slice':>15s} | {'ARI':>8s} | {'N_strata':>8s} | {'N_zeros':>7s}")
    print("-" * 50)

    slices = [
        ("z1-4 (head)", slice(0, 4)),
        ("z5-10", slice(4, 10)),
        ("z5-15", slice(4, 15)),
        ("z5-19", slice(4, 19)),
        ("z5-25", slice(4, 25)),
        ("z10-19", slice(9, 19)),
        ("z10-25", slice(9, 25)),
        ("z15-25", slice(14, 25)),
        ("z20-25", slice(19, 25)),
        ("z1-19 (orig)", slice(0, 19)),
        ("z1-25 (all)", slice(0, 25)),
    ]

    for name, sl in slices:
        ari, n_s = compute_ari(data, sl)
        n_z = sl.stop - sl.start
        print(f"{name:>15s} | {ari:>8.4f} | {n_s:>8d} | {n_z:>7d}")

    # === SO(even) ONLY ===
    so_even = [d for d in data if d["root_num"] == 1.0]
    print()
    print("=" * 72)
    print(f"SO(even) ONLY ({len(so_even)} objects)")
    print("=" * 72)
    print(f"{'Slice':>15s} | {'ARI':>8s} | {'N_strata':>8s}")
    print("-" * 40)

    for name, sl in slices:
        ari, n_s = compute_ari(so_even, sl)
        print(f"{name:>15s} | {ari:>8.4f} | {n_s:>8d}")

    # === INDIVIDUAL ZERO IMPORTANCE ===
    print()
    print("=" * 72)
    print("INDIVIDUAL ZERO IMPORTANCE (leave-one-out from z1-25)")
    print("=" * 72)

    base_ari, _ = compute_ari(data, slice(0, 25))
    print(f"Baseline (all 25): ARI = {base_ari:.4f}")
    print()
    print(f"{'Dropped':>10s} | {'ARI':>8s} | {'Delta':>8s}")
    print("-" * 35)

    for drop in range(25):
        keep = [i for i in range(25) if i != drop]
        by_cond = defaultdict(list)
        for d in data:
            by_cond[d["conductor"]].append(d)
        aris = []
        for c, objs in by_cond.items():
            if len(objs) < 5:
                continue
            ranks = [o["rank"] for o in objs]
            if len(set(ranks)) < 2:
                continue
            X = np.array([[o["zeros"][i] for i in keep] for o in objs])
            k = max(2, min(len(objs) // 2, 5))
            try:
                pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
                aris.append(adjusted_rand_score(ranks, pred))
            except:
                pass
        ari_loo = np.mean(aris) if aris else float('nan')
        delta = ari_loo - base_ari
        marker = " ***" if abs(delta) > 0.01 else ""
        print(f"  z{drop+1:>2d}      | {ari_loo:>8.4f} | {delta:>+8.4f}{marker}")


if __name__ == "__main__":
    main()
