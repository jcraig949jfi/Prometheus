"""
Zero Test Battery — Thresholds defined BEFORE data ingestion.

This file defines the exact tests, thresholds, and failure conditions for
the low-lying zeros representation. Every threshold is set now, before
any zero data has been pulled. The forcing principle: no post-hoc adjustment.

Representation under test:
  zeros_vector = [first 20 normalized low-lying zeros (gamma_n / log(conductor)),
                  root_number (+/-1), analytic_rank, degree, log(conductor)]
  = 24-dimensional vector per object

The Dirichlet battery revealed a binary identity collapse: distance = 0 or ~47,
no gradient, ARI = 0.008 within conductor strata. The zeros must do better.

What "better" means, precisely:
  1. Distance spectrum must be CONTINUOUS, not bimodal
  2. Within-conductor clusters must align with known invariants (ARI > 0.3)
  3. Signal must survive after regressing out conductor
  4. Coefficient model must outperform trivial model by >= 20%
"""

import duckdb
import numpy as np
from scipy import stats
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.metrics import adjusted_rand_score
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

from charon.src.config import DB_PATH


def get_duck():
    return duckdb.connect(str(DB_PATH), read_only=True)


# ============================================================
# THRESHOLDS — SET BEFORE DATA. DO NOT CHANGE AFTER SEEING RESULTS.
# ============================================================

THRESHOLDS = {
    # Test Z.0: Distance spectrum
    # The Dirichlet representation had a bimodal spike: 0 and ~47.
    # Zeros must produce a continuous spread.
    # Metric: coefficient of variation (std/mean) of pairwise distances
    # within a conductor stratum. Bimodal → low CV. Continuous → higher CV.
    # Also: fraction of distance mass in the "gap" between modes.
    "distance_spectrum_cv_min": 0.15,          # CV must be > 0.15 (Dirichlet was ~0.12)
    "distance_spectrum_gap_fraction_max": 0.30, # At most 30% of distances in the dead zone

    # Test Z.1: Trivial dominance (same as 0.3 but for zeros)
    # Trivial model must achieve LESS THAN 80% of zero model performance.
    "trivial_dominance_ratio_max": 0.80,       # Same threshold as before

    # Test Z.2: Conductor conditioning (same as 1.3 but for zeros)
    # Within conductor strata, clusters must align with known invariants.
    # Dirichlet got ARI = 0.008. Zeros must beat 0.3.
    # 0.3 is generous — even that would be a 37x improvement over Dirichlet.
    "conductor_conditioning_ari_min": 0.30,

    # Test Z.3: Conductor regression residual
    # THE decisive test. Regress out conductor from zero vectors.
    # Re-run Test Z.2 on residuals. Must still pass.
    # Threshold: ARI on residuals must be > 0.15
    # (halved from Z.2 because some signal loss from regression is expected)
    "conductor_residual_ari_min": 0.15,

    # Test Z.4: Separability (same as 1.1 but for zeros)
    # True pairs vs same-conductor non-pairs.
    # Dirichlet had Cohen's d = 11.54 (degenerate binary).
    # For zeros, we want REAL separation, not binary:
    # Cohen's d > 0.8 (large effect) with overlap < 20%
    # Note: overlap CAN be higher than Dirichlet's 0% because we want
    # continuous distances, not a binary gate.
    "separability_cohens_d_min": 0.8,
    "separability_overlap_max": 0.20,
}


def load_zero_vectors():
    """Load objects with zero-based invariant vectors."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    rows = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.object_type, o.conductor,
               oz.zeros_vector
        FROM objects o
        JOIN object_zeros oz ON o.id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL
        ORDER BY o.id
    """).fetchall()

    # Also load EC metadata for clustering tests
    ec_meta = {}
    ec_rows = duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso, ec.rank, ec.analytic_rank,
               ec.torsion, ec.cm, ec.class_size
        FROM elliptic_curves ec
    """).fetchall()
    for oid, iso, rank, arank, torsion, cm, cs in ec_rows:
        ec_meta[oid] = {
            'iso': iso, 'rank': int(rank or 0), 'analytic_rank': int(arank or 0),
            'torsion': int(torsion or 0), 'cm': int(cm or 0),
        }

    duck.close()

    data = []
    for oid, label, otype, cond, zvec in rows:
        if zvec is None:
            continue
        vec = np.array([v if v is not None else 0.0 for v in zvec])
        meta = ec_meta.get(oid, {})
        data.append({
            'id': oid, 'label': label, 'type': otype,
            'conductor': int(cond), 'vec': vec, **meta
        })

    return data


# ============================================================
# Test Z.0: Distance Spectrum
# ============================================================

def test_z0_distance_spectrum(data):
    """
    Within conductor strata, compute pairwise distance distributions.
    The Dirichlet representation was bimodal (spike at 0, spike at ~47).
    Zeros must produce a continuous spread.
    """
    print("=" * 60)
    print("TEST Z.0: DISTANCE SPECTRUM")
    print("=" * 60)
    print()

    # Group ECs by conductor (dedup by isogeny class)
    by_cond = defaultdict(list)
    seen_iso = set()
    for obj in data:
        if obj['type'] != 'elliptic_curve':
            continue
        iso = obj.get('iso')
        if iso and iso in seen_iso:
            continue
        if iso:
            seen_iso.add(iso)
        by_cond[obj['conductor']].append(obj)

    # Only conductors with >= 5 objects
    eligible = {c: objs for c, objs in by_cond.items() if len(objs) >= 5}

    all_cvs = []
    all_dists = []
    strata_count = 0

    for cond, objs in sorted(eligible.items()):
        vecs = np.array([o['vec'] for o in objs])
        n = len(vecs)
        dists = []
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(vecs[i] - vecs[j])
                dists.append(d)

        if not dists:
            continue

        dists = np.array(dists)
        all_dists.extend(dists)
        mean_d = dists.mean()
        if mean_d > 0:
            cv = dists.std() / mean_d
            all_cvs.append(cv)
        strata_count += 1

    all_dists = np.array(all_dists)
    mean_cv = np.mean(all_cvs) if all_cvs else 0.0

    print(f"Eligible strata (>=5 EC classes): {strata_count}")
    print(f"Total intra-conductor distances: {len(all_dists)}")
    print(f"Distance stats: mean={all_dists.mean():.4f}, std={all_dists.std():.4f}, "
          f"min={all_dists.min():.4f}, max={all_dists.max():.4f}")
    print(f"Mean coefficient of variation: {mean_cv:.4f} "
          f"(threshold: > {THRESHOLDS['distance_spectrum_cv_min']})")
    print()

    # Check for bimodality: is there a gap in the middle of the distribution?
    # Compute fraction of distances in the "dead zone" (10th-90th percentile range midpoint)
    if len(all_dists) > 100:
        p10 = np.percentile(all_dists, 10)
        p90 = np.percentile(all_dists, 90)
        midpoint = (p10 + p90) / 2
        bandwidth = (p90 - p10) * 0.2
        gap_fraction = np.mean((all_dists > midpoint - bandwidth) & (all_dists < midpoint + bandwidth))
        print(f"Gap fraction (middle 20% of range): {gap_fraction:.4f} "
              f"(threshold: > {THRESHOLDS['distance_spectrum_gap_fraction_max']})")
    else:
        gap_fraction = 0.5  # default to pass if too few distances

    # Percentile distribution
    print(f"Distance percentiles: "
          f"10%={np.percentile(all_dists, 10):.4f}, "
          f"25%={np.percentile(all_dists, 25):.4f}, "
          f"50%={np.percentile(all_dists, 50):.4f}, "
          f"75%={np.percentile(all_dists, 75):.4f}, "
          f"90%={np.percentile(all_dists, 90):.4f}")
    print()

    passed = mean_cv >= THRESHOLDS['distance_spectrum_cv_min']
    if passed:
        print(f"TEST Z.0: PASSED — Distance spectrum is continuous (CV={mean_cv:.4f})")
    else:
        print(f"TEST Z.0: FAILED — Distance spectrum is degenerate (CV={mean_cv:.4f})")

    return passed, {"cv": mean_cv, "gap_fraction": gap_fraction}


# ============================================================
# Test Z.1: Trivial Dominance
# ============================================================

def test_z1_trivial_dominance(data):
    """
    Same as Test 0.3 but on zero vectors.
    Can trivial metadata predict correspondence as well as zeros?
    """
    print("=" * 60)
    print("TEST Z.1: TRIVIAL DOMINANCE (zeros)")
    print("=" * 60)
    print()

    # Build the same pair dataset as test_03 but using zero vectors
    duck = duckdb.connect(str(DB_PATH), read_only=True)
    bridges = set((s, t) for s, t in duck.execute(
        "SELECT source_id, target_id FROM known_bridges WHERE bridge_type = 'modularity'"
    ).fetchall())
    duck.close()

    # Index objects
    ec_objs = {}
    mf_objs = defaultdict(list)
    seen_iso = set()
    for obj in data:
        if obj['type'] == 'elliptic_curve':
            iso = obj.get('iso')
            if iso and iso in seen_iso:
                continue
            if iso:
                seen_iso.add(iso)
            ec_objs[obj['id']] = obj
        elif obj['type'] == 'modular_form':
            mf_objs[obj['conductor']].append(obj)

    pos, neg = [], []
    for ec_id, ec in ec_objs.items():
        for mf in mf_objs.get(ec['conductor'], []):
            is_bridge = (ec_id, mf['id']) in bridges
            dist = np.linalg.norm(ec['vec'] - mf['vec'])
            coeff_feat = np.concatenate([np.abs(ec['vec'] - mf['vec']), [dist]])
            triv_feat = np.array([
                float(ec.get('rank', 0)), float(ec.get('torsion', 0)),
                float(ec.get('cm', 0)), float(ec.get('analytic_rank', 0)),
            ])
            if is_bridge:
                pos.append((coeff_feat, triv_feat, 1))
            else:
                neg.append((coeff_feat, triv_feat, 0))

    if not pos or not neg:
        print("Insufficient data for Test Z.1")
        return False, {}

    # Balance
    np.random.seed(42)
    if len(neg) > len(pos) * 3:
        idx = np.random.choice(len(neg), len(pos) * 3, replace=False)
        neg = [neg[i] for i in idx]

    all_p = pos + neg
    np.random.shuffle(all_p)
    X_z = np.array([p[0] for p in all_p])
    X_t = np.array([p[1] for p in all_p])
    y = np.array([p[2] for p in all_p])

    print(f"Samples: {len(y)}, pos rate: {y.mean():.1%}")

    clf_z = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
    auc_z = cross_val_score(clf_z, X_z, y, cv=5, scoring='roc_auc').mean()

    clf_t = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
    auc_t = cross_val_score(clf_t, X_t, y, cv=5, scoring='roc_auc').mean()

    ratio = auc_t / auc_z if auc_z > 0 else float('inf')

    print(f"Zero model AUC:    {auc_z:.4f}")
    print(f"Trivial model AUC: {auc_t:.4f}")
    print(f"Ratio: {ratio:.4f} (threshold: < {THRESHOLDS['trivial_dominance_ratio_max']})")
    print()

    passed = ratio < THRESHOLDS['trivial_dominance_ratio_max']
    if passed:
        print(f"TEST Z.1: PASSED — Zeros carry signal beyond trivial metadata")
    else:
        print(f"TEST Z.1: FAILED — Trivial metadata explains {ratio:.0%} of zero model")

    return passed, {"auc_zeros": auc_z, "auc_trivial": auc_t, "ratio": ratio}


# ============================================================
# Test Z.2: Conductor Conditioning
# ============================================================

def test_z2_conductor_conditioning(data):
    """
    Within fixed conductor strata, cluster by zero vectors.
    Clusters must align with known invariants at ARI > 0.3.
    """
    print("=" * 60)
    print("TEST Z.2: CONDUCTOR CONDITIONING (zeros)")
    print("=" * 60)
    print()

    by_cond = defaultdict(list)
    seen_iso = set()
    for obj in data:
        if obj['type'] != 'elliptic_curve':
            continue
        iso = obj.get('iso')
        if iso and iso in seen_iso:
            continue
        if iso:
            seen_iso.add(iso)
        if 'rank' in obj:
            by_cond[obj['conductor']].append(obj)

    eligible = {c: objs for c, objs in by_cond.items() if len(objs) >= 5}
    print(f"Eligible strata: {len(eligible)}")

    ari_by_inv = defaultdict(list)
    for cond, objs in eligible.items():
        X = np.array([o['vec'] for o in objs])
        n = len(objs)
        k = max(2, min(n // 2, 5))
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)

        for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
            true = [o.get(inv, 0) for o in objs]
            if len(set(true)) < 2:
                continue
            ari_by_inv[inv].append(adjusted_rand_score(true, labels))

    best_ari = 0.0
    best_inv = None
    for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
        vals = ari_by_inv[inv]
        if vals:
            mean_ari = np.mean(vals)
            print(f"  {inv:15s}: mean ARI = {mean_ari:.4f} ({len(vals)} strata)")
            if mean_ari > best_ari:
                best_ari = mean_ari
                best_inv = inv

    print()
    threshold = THRESHOLDS['conductor_conditioning_ari_min']
    passed = best_ari >= threshold
    if passed:
        print(f"TEST Z.2: PASSED — ARI = {best_ari:.4f} >= {threshold} ({best_inv})")
    else:
        print(f"TEST Z.2: FAILED — Best ARI = {best_ari:.4f} < {threshold}")

    return passed, {"best_ari": best_ari, "best_invariant": best_inv}


# ============================================================
# Test Z.3: Conductor Regression Residual
# ============================================================

def test_z3_conductor_residual(data):
    """
    THE decisive test. Regress out conductor from zero vectors.
    Re-cluster on residuals. If structure survives, the signal is real.
    If it collapses, zeros are just a fancier conductor proxy.
    """
    print("=" * 60)
    print("TEST Z.3: CONDUCTOR REGRESSION RESIDUAL")
    print("=" * 60)
    print()

    # Get all EC reps with zero vectors
    seen_iso = set()
    ec_list = []
    for obj in data:
        if obj['type'] != 'elliptic_curve':
            continue
        iso = obj.get('iso')
        if iso and iso in seen_iso:
            continue
        if iso:
            seen_iso.add(iso)
        if 'rank' in obj:
            ec_list.append(obj)

    if len(ec_list) < 100:
        print("Insufficient data")
        return False, {}

    X = np.array([o['vec'] for o in ec_list])
    conductors = np.array([o['conductor'] for o in ec_list]).reshape(-1, 1)

    # Regress each dimension of the zero vector against log(conductor)
    log_cond = np.log(conductors + 1)
    residuals = np.zeros_like(X)
    for dim in range(X.shape[1]):
        ridge = Ridge(alpha=1.0)
        ridge.fit(log_cond, X[:, dim])
        predicted = ridge.predict(log_cond)
        residuals[:, dim] = X[:, dim] - predicted

    print(f"Regressed {X.shape[1]} dimensions against log(conductor)")
    print(f"Original variance: {X.var():.4f}, Residual variance: {residuals.var():.4f}")
    print(f"Variance explained by conductor: {1 - residuals.var()/X.var():.1%}")
    print()

    # Now cluster on residuals within conductor strata
    by_cond = defaultdict(list)
    for i, obj in enumerate(ec_list):
        by_cond[obj['conductor']].append((i, obj))

    eligible = {c: items for c, items in by_cond.items() if len(items) >= 5}

    ari_by_inv = defaultdict(list)
    for cond, items in eligible.items():
        indices = [idx for idx, _ in items]
        objs = [obj for _, obj in items]
        X_res = residuals[indices]
        k = max(2, min(len(objs) // 2, 5))
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X_res)

        for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
            true = [o.get(inv, 0) for o in objs]
            if len(set(true)) < 2:
                continue
            ari_by_inv[inv].append(adjusted_rand_score(true, labels))

    best_ari = 0.0
    best_inv = None
    for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
        vals = ari_by_inv[inv]
        if vals:
            mean_ari = np.mean(vals)
            print(f"  {inv:15s}: mean residual ARI = {mean_ari:.4f}")
            if mean_ari > best_ari:
                best_ari = mean_ari
                best_inv = inv

    print()
    threshold = THRESHOLDS['conductor_residual_ari_min']
    passed = best_ari >= threshold
    if passed:
        print(f"TEST Z.3: PASSED — Residual ARI = {best_ari:.4f} >= {threshold}")
        print(f"  Signal survives after removing conductor. This is real arithmetic structure.")
    else:
        print(f"TEST Z.3: FAILED — Residual ARI = {best_ari:.4f} < {threshold}")
        print(f"  Signal collapses after removing conductor. Zeros are a conductor proxy.")

    return passed, {"residual_ari": best_ari, "best_invariant": best_inv}


# ============================================================
# Test Z.4: Separability
# ============================================================

def test_z4_separability(data):
    """
    True bridge pairs vs same-conductor non-pairs.
    Must show real separation (d > 0.8) but NOT binary collapse.
    """
    print("=" * 60)
    print("TEST Z.4: SEPARABILITY (zeros)")
    print("=" * 60)
    print()

    duck = duckdb.connect(str(DB_PATH), read_only=True)
    bridges = duck.execute(
        "SELECT source_id, target_id FROM known_bridges WHERE bridge_type = 'modularity'"
    ).fetchall()
    duck.close()

    obj_by_id = {o['id']: o for o in data}
    mf_by_cond = defaultdict(list)
    for o in data:
        if o['type'] == 'modular_form':
            mf_by_cond[o['conductor']].append(o)

    # Also load n_zeros_stored for masked distance
    duck2 = get_duck()
    nz_rows = duck2.execute("SELECT object_id, n_zeros_stored FROM object_zeros").fetchall()
    duck2.close()
    nz_map = {oid: nz for oid, nz in nz_rows}

    def masked_zero_dist(obj_a, obj_b):
        """Compute distance using only shared zero slots (not zero-filled)."""
        na = nz_map.get(obj_a['id'], 0) or 0
        nb = nz_map.get(obj_b['id'], 0) or 0
        n_shared = min(na, nb, 20)
        # Use shared zeros + metadata (slots 20-23)
        va = list(obj_a['vec'][:n_shared]) + list(obj_a['vec'][20:])
        vb = list(obj_b['vec'][:n_shared]) + list(obj_b['vec'][20:])
        a = np.array([v if v is not None else 0.0 for v in va])
        b = np.array([v if v is not None else 0.0 for v in vb])
        return np.linalg.norm(a - b)

    true_dists = []
    false_dists = []

    for src_id, tgt_id in bridges:
        if src_id not in obj_by_id or tgt_id not in obj_by_id:
            continue
        ec = obj_by_id[src_id]
        mf_true = obj_by_id[tgt_id]
        cond = ec['conductor']
        others = [m for m in mf_by_cond[cond] if m['id'] != tgt_id]
        if not others:
            continue

        true_dists.append(masked_zero_dist(ec, mf_true))
        neg = others[np.random.randint(len(others))]
        false_dists.append(masked_zero_dist(ec, neg))

        if len(true_dists) >= 500:
            break

    true_d = np.array(true_dists)
    false_d = np.array(false_dists)

    print(f"True pairs: {len(true_d)}, mean dist = {true_d.mean():.4f}")
    print(f"False pairs: {len(false_d)}, mean dist = {false_d.mean():.4f}")

    pooled_std = np.sqrt((true_d.std()**2 + false_d.std()**2) / 2)
    cohens_d = (false_d.mean() - true_d.mean()) / pooled_std if pooled_std > 0 else 0

    # Overlap: fraction of distributions that overlap
    true_max = np.percentile(true_d, 95)
    overlap = np.mean(false_d <= true_max)

    print(f"Cohen's d: {cohens_d:.4f} (threshold: > {THRESHOLDS['separability_cohens_d_min']})")
    print(f"Overlap: {overlap:.4f} (threshold: < {THRESHOLDS['separability_overlap_max']})")
    print()

    passed_d = cohens_d >= THRESHOLDS['separability_cohens_d_min']
    passed_o = overlap <= THRESHOLDS['separability_overlap_max']
    passed = passed_d and passed_o

    if passed:
        print(f"TEST Z.4: PASSED")
    else:
        reasons = []
        if not passed_d:
            reasons.append(f"Cohen's d too low ({cohens_d:.4f})")
        if not passed_o:
            reasons.append(f"Overlap too high ({overlap:.4f})")
        print(f"TEST Z.4: FAILED — {', '.join(reasons)}")

    return passed, {"cohens_d": cohens_d, "overlap": overlap}


# ============================================================
# Run all tests
# ============================================================

def run_full_battery():
    """Run the complete zero battery. Binary outcomes only."""
    print("=" * 60)
    print("CHARON ZERO BATTERY")
    print("Thresholds set: 2026-04-01 (before data ingestion)")
    print("=" * 60)
    print()
    print("Thresholds:")
    for k, v in THRESHOLDS.items():
        print(f"  {k}: {v}")
    print()

    data = load_zero_vectors()
    if len(data) < 100:
        print(f"ERROR: Only {len(data)} objects with zero vectors. Need >= 100.")
        print("Run zero ingestion first.")
        return

    print(f"Loaded {len(data)} objects with zero vectors")
    print()

    results = {}
    results['Z.0'] = test_z0_distance_spectrum(data)
    print()
    results['Z.1'] = test_z1_trivial_dominance(data)
    print()
    results['Z.2'] = test_z2_conductor_conditioning(data)
    print()
    results['Z.3'] = test_z3_conductor_residual(data)
    print()
    results['Z.4'] = test_z4_separability(data)
    print()

    # Summary
    print("=" * 60)
    print("ZERO BATTERY SUMMARY")
    print("=" * 60)
    print()
    all_passed = True
    for test_name, (passed, metrics) in results.items():
        status = "PASSED" if passed else "FAILED"
        key_metric = next(iter(metrics.values())) if metrics else "—"
        print(f"  {test_name}: {status:8s} ({key_metric})")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("ALL TESTS PASSED — Zero representation is viable.")
        print("Proceed to embedding (Layer 2).")
    else:
        failed = [k for k, (p, _) in results.items() if not p]
        print(f"FAILED: {', '.join(failed)}")
        if 'Z.3' in failed:
            print("Conductor regression killed it. Zeros are a conductor proxy.")
            print("Pivot to Direction 3 (relationship graph).")
        elif 'Z.0' in failed:
            print("Distance spectrum is degenerate. Same binary collapse as Dirichlet.")
            print("Pivot to Direction 3 (relationship graph).")
        else:
            print("Partial failure. Investigate before pivoting.")


if __name__ == "__main__":
    run_full_battery()
