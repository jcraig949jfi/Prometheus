"""
Q10 Kill Test: Root Number Conditioning
========================================
If the spectral tail signal is just SO(even) vs SO(odd) symmetry type
classification, then within a fixed root number stratum, ARI should collapse.

Root number +1 → SO(even) → even analytic rank (0, 2, 4...)
Root number -1 → SO(odd)  → odd analytic rank (1, 3, 5...)

Test: Can zeros 5-19 separate rank 0 from rank 2 within SO(even)?
If yes → Q10 is dead. The tail discriminates WITHIN a symmetry class.
If no  → Q10 survives. The finding reduces to symmetry type classification.
"""

import duckdb
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "charon.duckdb"


def load_data():
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT ec.lmfdb_iso, ec.conductor, ec.rank,
               oz.zeros_vector, oz.n_zeros_stored
        FROM elliptic_curves ec
        JOIN object_zeros oz ON ec.object_id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL AND oz.n_zeros_stored >= 20
        ORDER BY ec.object_id
    """).fetchall()
    con.close()

    seen = set()
    data = []
    for iso, cond, rank, zvec, nz in rows:
        if iso in seen:
            continue
        seen.add(iso)
        root_num = zvec[20]
        zeros = np.array([float(zvec[i]) if zvec[i] is not None else 0.0 for i in range(20)])
        data.append({"conductor": int(cond), "rank": int(rank or 0),
                      "root_num": float(root_num), "zeros": zeros})
    return data


def compute_ari(objects, zero_slice):
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
        k = max(2, min(len(objs) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        aris.append(adjusted_rand_score(ranks, pred))
    return np.mean(aris) if aris else 0.0, len(aris)


def permutation_test(objects, zero_slice, n_trials=100):
    rng = np.random.default_rng(42)
    by_cond = defaultdict(list)
    for d in objects:
        by_cond[d["conductor"]].append(d)

    eligible = []
    for c, objs in by_cond.items():
        if len(objs) < 5:
            continue
        ranks = [o["rank"] for o in objs]
        if len(set(ranks)) < 2:
            continue
        eligible.append(objs)

    real_aris = []
    for objs in eligible:
        X = np.array([o["zeros"][zero_slice] for o in objs])
        ranks = [o["rank"] for o in objs]
        k = max(2, min(len(objs) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        real_aris.append(adjusted_rand_score(ranks, pred))
    real_mean = np.mean(real_aris) if real_aris else 0.0

    perm_means = []
    for _ in range(n_trials):
        trial_aris = []
        for objs in eligible:
            X = np.array([o["zeros"][zero_slice] for o in objs])
            ranks = [o["rank"] for o in objs]
            shuffled = list(ranks)
            rng.shuffle(shuffled)
            k = max(2, min(len(objs) // 2, 5))
            pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
            trial_aris.append(adjusted_rand_score(shuffled, pred))
        perm_means.append(np.mean(trial_aris))

    perm = np.array(perm_means)
    return real_mean, len(eligible), perm


def main():
    data = load_data()
    print(f"Loaded {len(data)} ECs")

    # Population summary
    for rn in [1.0, -1.0]:
        sub = [d for d in data if d["root_num"] == rn]
        rank_counts = defaultdict(int)
        for d in sub:
            rank_counts[d["rank"]] += 1
        print(f"  root_num={rn:+.0f}: {dict(sorted(rank_counts.items()))}")

    # === TEST A: Full population baseline ===
    print("\n" + "=" * 60)
    print("TEST A: FULL POPULATION (rank 0 + 1 + 2, both root numbers)")
    print("=" * 60)
    for label, sl in [("all_20", slice(0, 20)), ("zeros_5_19", slice(4, 20))]:
        ari, n = compute_ari(data, sl)
        print(f"  {label:15s}: ARI = {ari:.4f} ({n} strata)")

    # === TEST B: SO(even) only — rank 0 vs rank 2 ===
    so_even = [d for d in data if d["root_num"] == 1.0]
    print("\n" + "=" * 60)
    print("TEST B: SO(even) ONLY — rank 0 vs rank 2 (Q10 KILL TEST)")
    print("=" * 60)
    r0 = sum(1 for d in so_even if d["rank"] == 0)
    r2 = sum(1 for d in so_even if d["rank"] == 2)
    print(f"  rank 0: {r0}, rank 2: {r2}")

    for label, sl in [("all_20", slice(0, 20)), ("zeros_5_19", slice(4, 20)),
                       ("first_only", slice(0, 1))]:
        ari, n = compute_ari(so_even, sl)
        print(f"  {label:15s}: ARI = {ari:.4f} ({n} strata with mixed ranks)")

    # === TEST C: Permutation test within SO(even) ===
    print("\n" + "=" * 60)
    print("TEST C: PERMUTATION TEST within SO(even), zeros 5-19")
    print("=" * 60)
    real, n_strata, perm = permutation_test(so_even, slice(4, 20))
    print(f"  Real ARI: {real:.4f} ({n_strata} strata)")
    print(f"  Shuffled: mean={perm.mean():.4f}, std={perm.std():.4f}, max={perm.max():.4f}")
    if perm.std() > 0:
        z = (real - perm.mean()) / perm.std()
        print(f"  z-score: {z:.1f}")
    p_val = np.mean(perm >= real)
    print(f"  p-value: {p_val:.4f}")

    # === VERDICT ===
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    if real > 0.05 and (perm.std() == 0 or (real - perm.mean()) / max(perm.std(), 1e-9) > 3):
        print("  Q10 IS DEAD.")
        print("  Zeros 5-19 separate rank 0 from rank 2 WITHIN SO(even).")
        print("  The spectral tail discriminates within a symmetry class.")
        print("  This is NOT reducible to SO(even) vs SO(odd) classification.")
    elif real < 0.02:
        print("  Q10 SURVIVES.")
        print("  Within fixed symmetry type, the spectral tail cannot discriminate rank.")
        print("  The finding reduces to symmetry type classification via k-means.")
    else:
        print("  INCONCLUSIVE.")
        print(f"  ARI = {real:.4f} — weak signal within SO(even).")
        print("  May be a power issue (only {r2} rank-2 curves).")
        print("  Flag as limitation.")

    # === SO(odd) check ===
    so_odd = [d for d in data if d["root_num"] == -1.0]
    ranks_odd = set(d["rank"] for d in so_odd)
    print(f"\n  SO(odd) ranks present: {sorted(ranks_odd)}")
    if len(ranks_odd) < 2:
        print("  No rank variation within SO(odd). Test not applicable.")


if __name__ == "__main__":
    main()
