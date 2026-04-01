"""
Test 1.1 — Separability

The real teeth. Take pairs that share a conductor but don't correspond.
Are they farther apart than true pairs?

Method:
  - 500 true modularity pairs (distance should be ~0)
  - 500 provably non-corresponding pairs at the SAME conductor
  - KS test + Cohen's d on the distance distributions
  - Overlap must be < 5%

If the distributions overlap, proximity means conductor, not correspondence.
"""

import duckdb
import numpy as np
from scipy import stats
from collections import defaultdict
from charon.src.config import DB_PATH

np.random.seed(42)


def run_test():
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Get EC reps with vectors
    ecs_raw = duck.execute("""
        SELECT ec.lmfdb_iso, o.id, o.invariant_vector, o.conductor
        FROM elliptic_curves ec
        JOIN objects o ON ec.object_id = o.id
        WHERE o.invariant_vector IS NOT NULL
        ORDER BY ec.lmfdb_iso
    """).fetchall()

    seen = set()
    ec_data = {}
    for iso, oid, vec, cond in ecs_raw:
        if iso in seen:
            continue
        seen.add(iso)
        v25 = np.array([x if x is not None else 0.0 for x in vec[:25]])
        ec_data[oid] = {'iso': iso, 'vec': v25, 'conductor': int(cond)}

    # Get dim-1 weight-2 MFs
    mfs_raw = duck.execute("""
        SELECT o.id, o.invariant_vector, o.conductor
        FROM objects o
        JOIN modular_forms mf ON o.id = mf.object_id
        WHERE o.invariant_vector IS NOT NULL
          AND mf.weight = 2 AND mf.dim = 1 AND mf.char_order = 1
    """).fetchall()

    mf_data = {}
    mf_by_cond = defaultdict(list)
    for oid, vec, cond in mfs_raw:
        v25 = np.array([x if x is not None else 0.0 for x in vec[:25]])
        mf_data[oid] = {'vec': v25, 'conductor': int(cond)}
        mf_by_cond[int(cond)].append(oid)

    # Known bridges
    bridges = duck.execute(
        "SELECT source_id, target_id FROM known_bridges WHERE bridge_type = 'modularity'"
    ).fetchall()
    bridge_set = set((s, t) for s, t in bridges)
    bridge_by_ec = {s: t for s, t in bridges}

    duck.close()

    # ================================================================
    # Build TRUE pairs: known bridges
    # Only use conductors with >= 3 dim-1 forms (so negatives exist)
    # ================================================================

    true_distances = []
    false_distances = []

    for ec_id, mf_id in bridges:
        if ec_id not in ec_data or mf_id not in mf_data:
            continue

        ec = ec_data[ec_id]
        mf_true = mf_data[mf_id]
        cond = ec['conductor']

        # Only use conductors with multiple forms (so we can build negatives)
        other_mfs = [mid for mid in mf_by_cond[cond]
                     if mid != mf_id and mid in mf_data]
        if not other_mfs:
            continue

        # True distance (should be ~0)
        true_dist = np.linalg.norm(ec['vec'] - mf_true['vec'])
        true_distances.append(true_dist)

        # False distance: pick a random non-corresponding MF at same conductor
        neg_mf_id = np.random.choice(other_mfs)
        neg_dist = np.linalg.norm(ec['vec'] - mf_data[neg_mf_id]['vec'])
        false_distances.append(neg_dist)

        if len(true_distances) >= 500:
            break

    true_d = np.array(true_distances)
    false_d = np.array(false_distances)

    print("=" * 60)
    print("TEST 1.1: SEPARABILITY")
    print("=" * 60)
    print()
    print(f"True pairs (known bridges): {len(true_d)}")
    print(f"False pairs (same conductor, not corresponding): {len(false_d)}")
    print()

    # Distribution statistics
    print("Distance distributions:")
    print(f"  True pairs:  mean={true_d.mean():.6f}, std={true_d.std():.6f}, "
          f"median={np.median(true_d):.6f}, max={true_d.max():.6f}")
    print(f"  False pairs: mean={false_d.mean():.6f}, std={false_d.std():.6f}, "
          f"median={np.median(false_d):.6f}, min={false_d.min():.6f}")
    print()

    # Cohen's d
    pooled_std = np.sqrt((true_d.std()**2 + false_d.std()**2) / 2)
    if pooled_std > 0:
        cohens_d = (false_d.mean() - true_d.mean()) / pooled_std
    else:
        cohens_d = float('inf')
    print(f"Cohen's d: {cohens_d:.4f} (require > 1.0)")

    # KS test
    ks_stat, ks_p = stats.ks_2samp(true_d, false_d)
    print(f"KS statistic: {ks_stat:.4f}, p-value: {ks_p:.2e}")

    # Overlap estimation
    # Use the overlap between the distributions
    # True pairs should be at 0, false pairs should be > 0
    # Overlap = fraction of false pairs that fall within the range of true pairs
    true_max = true_d.max()
    overlap_fraction = np.mean(false_d <= true_max + 1e-10)
    print(f"Overlap: {overlap_fraction:.4f} (fraction of false pairs with dist <= max(true) = {true_max:.6f})")
    print()

    # More robust overlap: fraction of false distances below the 95th percentile of true distances
    # plus fraction of true distances above 5th percentile of false distances
    true_95 = np.percentile(true_d, 95)
    false_05 = np.percentile(false_d, 5)
    overlap_below = np.mean(false_d <= true_95)
    overlap_above = np.mean(true_d >= false_05)
    total_overlap = (overlap_below + overlap_above) / 2
    print(f"Robust overlap metric: {total_overlap:.4f}")
    print(f"  False dists below true 95th pctile ({true_95:.6f}): {overlap_below:.4f}")
    print(f"  True dists above false 5th pctile ({false_05:.6f}): {overlap_above:.4f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    print()

    passed = True
    if cohens_d < 1.0:
        print(f"FAIL: Cohen's d = {cohens_d:.4f} < 1.0")
        passed = False
    else:
        print(f"PASS: Cohen's d = {cohens_d:.4f} >= 1.0")

    if overlap_fraction > 0.05:
        print(f"FAIL: Overlap = {overlap_fraction:.4f} > 0.05")
        passed = False
    else:
        print(f"PASS: Overlap = {overlap_fraction:.4f} <= 0.05")

    print()
    if passed:
        print("TEST 1.1: PASSED — True pairs are clearly separated from same-conductor non-pairs.")
    else:
        print("TEST 1.1: FAILED — Distributions overlap; proximity may mean conductor, not correspondence.")

    return passed


if __name__ == "__main__":
    run_test()
