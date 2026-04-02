"""
Genus-2 Crossing: The Definitive Test for the 163
===================================================

Ingest genus-2 curves from LMFDB, compute their zero vectors,
and test whether they cluster near the 163 dim-2 forms.

If genus-2 curves ARE zero-proximate to the 163:
  → Charon detected Paramodular Conjecture objects computationally
  → Character is a feature, not a confound

If genus-2 curves are NOT zero-proximate:
  → EC-proximity is a zero-statistics artifact
  → The 163 are interesting but not paramodular candidates
"""

import duckdb
import psycopg2
import numpy as np
import math
import json
import time
import logging
from collections import defaultdict, Counter
from sklearn.neighbors import NearestNeighbors
from pathlib import Path

from charon.src.config import DB_PATH, LMFDB_PG

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.genus2')

N_ZEROS = 20


def ingest_genus2():
    """Ingest genus-2 curves and their L-function zeros from LMFDB."""
    log.info("=" * 60)
    log.info("GENUS-2 CROSSING: Ingestion")
    log.info("=" * 60)
    t0 = time.time()

    pg = psycopg2.connect(**LMFDB_PG)
    cur = pg.cursor()

    # Get genus-2 curves with conductor <= 5000
    cur.execute("""
        SELECT label, cond, class, analytic_rank, root_number,
               is_gl2_type, is_simple_base, st_group, mw_rank, torsion_order
        FROM g2c_curves
        WHERE cond <= 5000
        ORDER BY cond, label
    """)
    g2_curves = cur.fetchall()
    log.info(f"Genus-2 curves (cond <= 5000): {len(g2_curves)}")

    duck = duckdb.connect(str(DB_PATH), read_only=False)

    # Add genus-2 objects to the objects table and object_zeros
    ingested = 0
    no_zeros = 0
    seen_classes = set()

    for label, cond, cls, arank, rn, is_gl2, is_simple, st_group, mw_rank, torsion in g2_curves:
        # One per isogeny class
        if cls in seen_classes:
            continue
        seen_classes.add(cls)

        # Get L-function zeros
        parts = cls.split('.')
        origin = f"Genus2Curve/Q/{parts[0]}/{parts[1]}"

        cur.execute("""
            SELECT positive_zeros, z1, z2, z3, root_number, order_of_vanishing, degree
            FROM lfunc_lfunctions WHERE origin = %s LIMIT 1
        """, [origin])
        lf_row = cur.fetchone()

        if lf_row is None or (lf_row[0] is None and lf_row[1] is None):
            no_zeros += 1
            continue

        pos_zeros = lf_row[0]
        if pos_zeros and len(pos_zeros) > 0:
            zeros = [float(z) for z in pos_zeros]
        else:
            zeros = [float(z) for z in [lf_row[1], lf_row[2], lf_row[3]] if z is not None]

        if len(zeros) < 3:
            no_zeros += 1
            continue

        # Build zero vector (same normalization as all other objects)
        log_cond = math.log(max(int(cond), 2))
        normalized = []
        for i in range(N_ZEROS):
            if i < len(zeros):
                normalized.append(zeros[i] / log_cond)
            else:
                normalized.append(None)

        # Parse root number
        rn_val = float(rn) if rn is not None else 0.0

        # Note: genus-2 L-functions are degree 4, not degree 2
        degree = int(lf_row[6]) if lf_row[6] else 4
        rov = int(lf_row[5]) if lf_row[5] else (int(arank) if arank is not None else 0)

        vec = normalized + [rn_val, float(rov), float(degree), log_cond]
        completeness = sum(1 for v in vec if v is not None) / len(vec)

        # Check if object already exists
        existing = duck.execute(
            "SELECT id FROM objects WHERE lmfdb_label = ?", [label]
        ).fetchone()

        if existing:
            obj_id = existing[0]
        else:
            obj_id = duck.execute("SELECT nextval('objects_id_seq')").fetchone()[0]
            properties = {
                'is_gl2_type': is_gl2, 'is_simple': is_simple,
                'st_group': st_group, 'mw_rank': mw_rank,
                'torsion_order': torsion, 'analytic_rank': arank,
            }
            duck.execute("""
                INSERT INTO objects (id, lmfdb_label, object_type, conductor, properties)
                VALUES (?, ?, 'genus2_curve', ?, ?)
            """, [obj_id, label, int(cond), json.dumps(properties)])

        # Insert/update zeros
        duck.execute("""
            INSERT OR REPLACE INTO object_zeros
            (object_id, zeros_vector, zeros_completeness, root_number, analytic_rank, n_zeros_stored)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [obj_id, vec, completeness, rn_val, rov, len(zeros)])

        ingested += 1

    cur.close()
    pg.close()
    duck.close()

    log.info(f"Ingested: {ingested} genus-2 classes, {no_zeros} without zeros")
    log.info(f"Ingestion completed in {time.time()-t0:.1f}s")
    return ingested


def test_163_proximity():
    """
    THE TEST: Are the 163 dim-2 forms zero-proximate to genus-2 curves?
    """
    log.info("")
    log.info("=" * 60)
    log.info("THE TEST: Are the 163 near genus-2 curves?")
    log.info("=" * 60)

    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Load all objects with zeros (including new genus-2)
    all_rows = duck.execute("""
        SELECT oz.object_id, o.object_type, o.conductor, o.lmfdb_label,
               oz.zeros_vector, oz.n_zeros_stored
        FROM object_zeros oz
        JOIN objects o ON oz.object_id = o.id
        WHERE oz.zeros_vector IS NOT NULL
    """).fetchall()

    # Load MF metadata for the 163
    mf_meta = {}
    for row in duck.execute("SELECT mf.object_id, mf.dim, mf.weight, mf.char_order FROM modular_forms mf").fetchall():
        mf_meta[row[0]] = {'dim': row[1], 'weight': row[2], 'char_order': row[3]}

    # Get the 163 Type B EC-neighbor MFs (dim-2 wt-2)
    type_b_163 = duck.execute("""
        SELECT da.object_id, da.label, da.conductor
        FROM disagreement_atlas da
        WHERE da.disagreement_type = 'B'
    """).fetchall()

    duck.close()

    # Build vectors
    obj_list = []
    for oid, otype, cond, label, zvec, nz in all_rows:
        n = min(nz or 0, N_ZEROS)
        vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(N_ZEROS)]
        obj_list.append({
            'id': oid, 'type': otype, 'conductor': int(cond),
            'label': label, 'vec': np.array(vec),
        })

    id_to_idx = {o['id']: i for i, o in enumerate(obj_list)}
    X = np.array([o['vec'] for o in obj_list])
    means, stds = X.mean(0), X.std(0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X - means) / stds

    # Count genus-2 objects
    g2_indices = [i for i, o in enumerate(obj_list) if o['type'] == 'genus2_curve']
    ec_indices = [i for i, o in enumerate(obj_list) if o['type'] == 'elliptic_curve']
    log.info(f"Total objects: {len(obj_list)}")
    log.info(f"Genus-2 curves: {len(g2_indices)}")
    log.info(f"Elliptic curves: {len(ec_indices)}")

    if len(g2_indices) == 0:
        log.error("No genus-2 curves ingested! Cannot run test.")
        return

    # k-NN with enough neighbors to find cross-type
    nn = NearestNeighbors(n_neighbors=30, metric='euclidean', algorithm='brute')
    nn.fit(X_norm)

    # For each of the 163, find nearest genus-2 curve and nearest EC
    # The 163 are Type B dim-2 wt-2 MFs with EC zero-neighbors
    type_b_ids = set(r[0] for r in type_b_163)
    the_163 = []
    for i, o in enumerate(obj_list):
        if o['id'] in type_b_ids:
            meta = mf_meta.get(o['id'], {})
            if meta.get('dim') == 2 and meta.get('weight') == 2:
                the_163.append(i)

    log.info(f"The 163 (dim-2 wt-2 Type B with EC neighbors): {len(the_163)}")

    if not the_163:
        log.error("Could not find the 163 in the dataset!")
        return

    _, nn_indices = nn.kneighbors(X_norm[the_163])

    g2_found = 0
    ec_found = 0
    g2_dists = []
    ec_dists = []
    g2_details = []

    for i, mf_idx in enumerate(the_163):
        mf_obj = obj_list[mf_idx]
        nearest_g2 = None
        nearest_ec = None
        g2_dist = None
        ec_dist = None

        for j_pos in range(nn_indices.shape[1]):
            n_idx = nn_indices[i, j_pos]
            if n_idx == mf_idx:
                continue
            n_obj = obj_list[n_idx]
            d = np.linalg.norm(X_norm[mf_idx] - X_norm[n_idx])

            if n_obj['type'] == 'genus2_curve' and nearest_g2 is None:
                nearest_g2 = n_obj
                g2_dist = d
            elif n_obj['type'] == 'elliptic_curve' and nearest_ec is None:
                nearest_ec = n_obj
                ec_dist = d

            if nearest_g2 is not None and nearest_ec is not None:
                break

        if nearest_g2 is not None:
            g2_found += 1
            g2_dists.append(g2_dist)
        if nearest_ec is not None:
            ec_found += 1
            ec_dists.append(ec_dist)

        g2_details.append({
            'mf': mf_obj['label'],
            'mf_cond': mf_obj['conductor'],
            'g2_label': nearest_g2['label'] if nearest_g2 else None,
            'g2_cond': nearest_g2['conductor'] if nearest_g2 else None,
            'g2_dist': g2_dist,
            'ec_label': nearest_ec['label'] if nearest_ec else None,
            'ec_cond': nearest_ec['conductor'] if nearest_ec else None,
            'ec_dist': ec_dist,
        })

    log.info(f"\nOf the {len(the_163)}:")
    log.info(f"  Found genus-2 neighbor: {g2_found}")
    log.info(f"  Found EC neighbor: {ec_found}")

    g2_dists = np.array(g2_dists) if g2_dists else np.array([])
    ec_dists = np.array(ec_dists) if ec_dists else np.array([])

    if len(g2_dists) > 0 and len(ec_dists) > 0:
        log.info(f"\n  Nearest genus-2 distance: mean={g2_dists.mean():.4f}, median={np.median(g2_dists):.4f}")
        log.info(f"  Nearest EC distance:     mean={ec_dists.mean():.4f}, median={np.median(ec_dists):.4f}")

        # THE KEY COMPARISON: are the 163 closer to genus-2 curves or to ECs?
        closer_to_g2 = sum(1 for g, e in zip(g2_dists, ec_dists) if g < e)
        closer_to_ec = sum(1 for g, e in zip(g2_dists, ec_dists) if e < g)
        tied = sum(1 for g, e in zip(g2_dists, ec_dists) if abs(g - e) < 0.001)

        log.info(f"\n  Closer to genus-2: {closer_to_g2}")
        log.info(f"  Closer to EC:      {closer_to_ec}")
        log.info(f"  Tied:              {tied}")

        # Statistical test
        from scipy.stats import wilcoxon
        if len(g2_dists) > 10:
            try:
                stat, p = wilcoxon(g2_dists[:len(ec_dists)], ec_dists[:len(g2_dists)])
                log.info(f"  Wilcoxon signed-rank: p={p:.4e}")
            except Exception as e:
                log.info(f"  Wilcoxon test failed: {e}")

    # Also: baseline comparison. For RANDOM dim-2 wt-2 MFs (not the 163),
    # how far is the nearest genus-2 curve?
    log.info(f"\n--- Baseline: random dim-2 wt-2 MFs ---")
    all_dim2_wt2 = [i for i, o in enumerate(obj_list)
                    if o['type'] == 'modular_form' and mf_meta.get(o['id'], {}).get('dim') == 2
                    and mf_meta.get(o['id'], {}).get('weight') == 2]

    np.random.seed(42)
    sample = np.random.choice(all_dim2_wt2, min(500, len(all_dim2_wt2)), replace=False)
    _, nn_sample = nn.kneighbors(X_norm[sample])

    baseline_g2_dists = []
    for i in range(len(sample)):
        for j_pos in range(nn_sample.shape[1]):
            n_idx = nn_sample[i, j_pos]
            if n_idx == sample[i]:
                continue
            if obj_list[n_idx]['type'] == 'genus2_curve':
                d = np.linalg.norm(X_norm[sample[i]] - X_norm[n_idx])
                baseline_g2_dists.append(d)
                break

    baseline_g2 = np.array(baseline_g2_dists) if baseline_g2_dists else np.array([])
    if len(baseline_g2) > 0:
        log.info(f"  Random dim-2 wt-2 → nearest G2: mean={baseline_g2.mean():.4f}, median={np.median(baseline_g2):.4f}")
        log.info(f"  The 163 → nearest G2:            mean={g2_dists.mean():.4f}, median={np.median(g2_dists):.4f}")
        log.info(f"  (Lower = closer to genus-2)")

        # Are the 163 significantly closer to genus-2 than random dim-2 MFs?
        from scipy.stats import mannwhitneyu
        if len(g2_dists) > 5 and len(baseline_g2) > 5:
            u, p = mannwhitneyu(g2_dists, baseline_g2, alternative='less')
            log.info(f"  Mann-Whitney U (163 < random): p={p:.4e}")

    # Show top cases
    g2_details.sort(key=lambda x: x['g2_dist'] if x['g2_dist'] is not None else 999)
    log.info(f"\n--- Top 15 MF → Genus-2 pairs ---")
    for d in g2_details[:15]:
        log.info(f"  {d['mf']:20s} (cond={d['mf_cond']}) "
                 f"→ G2: {d['g2_label'] or 'NONE':20s} (cond={d['g2_cond']}, dist={d['g2_dist']:.4f}) "
                 f"| EC: {d['ec_label'] or 'NONE':12s} (dist={d['ec_dist']:.4f})")

    # VERDICT
    log.info(f"\n{'=' * 60}")
    log.info("GENUS-2 CROSSING VERDICT")
    log.info(f"{'=' * 60}")

    if len(g2_dists) == 0:
        log.info("NO GENUS-2 NEIGHBORS FOUND. Test inconclusive.")
    elif len(g2_dists) > 0 and len(ec_dists) > 0:
        if closer_to_g2 > closer_to_ec:
            log.info("The 163 are CLOSER to genus-2 curves than to elliptic curves.")
            log.info("This SUPPORTS the paramodular interpretation.")
            log.info("Character may be a feature (selecting the right forms), not a confound.")
        elif closer_to_ec > closer_to_g2:
            log.info("The 163 are CLOSER to elliptic curves than to genus-2 curves.")
            log.info("The EC-proximity is NOT explained by paramodular correspondence.")
            log.info("The signal is likely a zero-statistics artifact of weight-2 similarity.")
        else:
            log.info("The 163 are equidistant from genus-2 and elliptic curves.")
            log.info("Ambiguous. No clear paramodular signal.")


def run():
    n = ingest_genus2()
    if n > 0:
        test_163_proximity()
    else:
        log.error("No genus-2 curves ingested. Cannot run test.")


if __name__ == "__main__":
    run()
