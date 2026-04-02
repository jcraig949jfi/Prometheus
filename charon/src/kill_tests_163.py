"""
Kill Tests for the 163 Dim-2 Forms
===================================
Kill Test 1: Is EVERY dim-2 weight-2 form EC-zero-proximate?
             If yes, it's just "weight-2" not "paramodular candidate."
Kill Test 2: Is non-trivial character doing the work?
             Compare trivial vs non-trivial vs ECs.
"""

import duckdb
import numpy as np
import logging
from collections import Counter
from sklearn.neighbors import NearestNeighbors
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.kill')


def run():
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    all_objs = duck.execute("""
        SELECT oz.object_id, o.object_type, o.conductor,
               oz.zeros_vector, oz.n_zeros_stored
        FROM object_zeros oz
        JOIN objects o ON oz.object_id = o.id
        WHERE oz.zeros_vector IS NOT NULL
    """).fetchall()

    mf_meta = {}
    for row in duck.execute("SELECT mf.object_id, mf.dim, mf.weight, mf.char_order FROM modular_forms mf").fetchall():
        mf_meta[row[0]] = {'dim': row[1], 'weight': row[2], 'char_order': row[3]}

    ec_isos = {}
    for row in duck.execute("SELECT ec.object_id, ec.lmfdb_iso FROM elliptic_curves ec").fetchall():
        ec_isos[row[0]] = row[1]

    duck.close()

    obj_list = []
    for oid, otype, cond, zvec, nz in all_objs:
        n = min(nz or 0, 20)
        vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(20)]
        meta = mf_meta.get(oid, {})
        obj_list.append({
            'id': oid, 'type': otype, 'conductor': int(cond), 'vec': np.array(vec),
            'dim': meta.get('dim'), 'weight': meta.get('weight'), 'char_order': meta.get('char_order'),
        })

    X = np.array([o['vec'] for o in obj_list])
    means, stds = X.mean(0), X.std(0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X - means) / stds

    nn = NearestNeighbors(n_neighbors=11, metric='euclidean', algorithm='brute')
    nn.fit(X_norm)

    # ================================================================
    # KILL TEST 1
    # ================================================================
    log.info("=" * 60)
    log.info("KILL TEST 1: Is 'weight-2 dim-2' sufficient for EC proximity?")
    log.info("=" * 60)

    dim2_wt2 = [i for i, o in enumerate(obj_list)
                if o['type'] == 'modular_form' and o['dim'] == 2 and o['weight'] == 2]
    log.info(f"Total dim-2 weight-2 MFs: {len(dim2_wt2)}")

    _, nn_indices = nn.kneighbors(X_norm[dim2_wt2])

    has_ec = 0
    for i in range(len(dim2_wt2)):
        for j_pos in range(1, nn_indices.shape[1]):
            if obj_list[nn_indices[i, j_pos]]['type'] == 'elliptic_curve':
                has_ec += 1
                break

    total = len(dim2_wt2)
    pct = has_ec / total * 100
    log.info(f"With EC in top-10: {has_ec}/{total} ({pct:.1f}%)")
    log.info(f"Without EC neighbor: {total - has_ec}/{total} ({100-pct:.1f}%)")

    if pct > 80:
        log.info("*** KILL TEST 1: KILLED — most dim-2 wt-2 forms are EC-proximate ***")
    elif pct < 20:
        log.info("*** KILL TEST 1: SURVIVED — only a minority have EC neighbors ***")
    else:
        log.info(f"*** KILL TEST 1: AMBIGUOUS ({pct:.1f}%) ***")

    # Also check: what about OTHER dimensions?
    for dim in [3, 4, 5, 6, 8]:
        dim_idx = [i for i, o in enumerate(obj_list)
                   if o['type'] == 'modular_form' and o['dim'] == dim and o['weight'] == 2]
        if len(dim_idx) < 10:
            continue
        _, nn_i = nn.kneighbors(X_norm[dim_idx])
        has = sum(1 for i in range(len(dim_idx))
                  if any(obj_list[nn_i[i, j]]['type'] == 'elliptic_curve' for j in range(1, nn_i.shape[1])))
        log.info(f"  dim-{dim} wt-2: {has}/{len(dim_idx)} ({has/len(dim_idx)*100:.1f}%) have EC neighbor")

    # ================================================================
    # KILL TEST 2
    # ================================================================
    log.info("")
    log.info("=" * 60)
    log.info("KILL TEST 2: Is character doing the work?")
    log.info("=" * 60)

    trivial = [i for i, o in enumerate(obj_list)
               if o['type'] == 'modular_form' and o['dim'] == 2
               and o['weight'] == 2 and o['char_order'] == 1]
    nontrivial = [i for i, o in enumerate(obj_list)
                  if o['type'] == 'modular_form' and o['dim'] == 2
                  and o['weight'] == 2 and o['char_order'] is not None and o['char_order'] > 1]

    seen_iso = set()
    ec_idx = []
    for i, o in enumerate(obj_list):
        if o['type'] == 'elliptic_curve':
            iso = ec_isos.get(o['id'])
            if iso and iso not in seen_iso:
                seen_iso.add(iso)
                ec_idx.append(i)

    log.info(f"Trivial char dim-2 wt-2: {len(trivial)}")
    log.info(f"Non-trivial char dim-2 wt-2: {len(nontrivial)}")
    log.info(f"EC representatives: {len(ec_idx)}")

    # Centroid distances
    ec_mean = X_norm[ec_idx].mean(axis=0)
    triv_mean = X_norm[trivial].mean(axis=0) if trivial else np.zeros(X_norm.shape[1])
    nontriv_mean = X_norm[nontrivial].mean(axis=0) if nontrivial else np.zeros(X_norm.shape[1])

    d_triv_ec = np.linalg.norm(triv_mean - ec_mean)
    d_nontriv_ec = np.linalg.norm(nontriv_mean - ec_mean)
    d_triv_nontriv = np.linalg.norm(triv_mean - nontriv_mean)

    log.info(f"\nCentroid distances:")
    log.info(f"  Trivial dim-2 <-> EC:           {d_triv_ec:.4f}")
    log.info(f"  Non-trivial dim-2 <-> EC:       {d_nontriv_ec:.4f}")
    log.info(f"  Trivial <-> Non-trivial dim-2:  {d_triv_nontriv:.4f}")

    # EC-neighbor rate by character
    for label, indices in [("trivial", trivial), ("non-trivial", nontrivial)]:
        if not indices:
            continue
        _, nn_i = nn.kneighbors(X_norm[indices])
        has = sum(1 for i in range(len(indices))
                  if any(obj_list[nn_i[i, j]]['type'] == 'elliptic_curve' for j in range(1, nn_i.shape[1])))
        log.info(f"  {label:15s}: {has}/{len(indices)} ({has/len(indices)*100:.1f}%) have EC in top-10")

    # Base rates
    base_triv_pct = len(trivial) / (len(trivial) + len(nontrivial)) if (len(trivial) + len(nontrivial)) > 0 else 0
    observed_triv_pct = 7 / 163  # from previous investigation

    log.info(f"\nBase rate trivial among dim-2 wt-2: {base_triv_pct:.1%}")
    log.info(f"Observed trivial in the 163: {observed_triv_pct:.1%}")

    if observed_triv_pct < base_triv_pct * 0.5:
        log.info("Non-trivial character is ENRICHED in the 163.")
        log.info("Character is likely contributing to the signal.")
    elif abs(observed_triv_pct - base_triv_pct) / max(base_triv_pct, 0.01) < 0.3:
        log.info("Character distribution matches base rate.")
        log.info("Character is NOT the driver.")
    else:
        log.info(f"Moderate enrichment/depletion. Investigate further.")

    log.info("")
    log.info("=" * 60)
    log.info("KILL TEST VERDICT")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
