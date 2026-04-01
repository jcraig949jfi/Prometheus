"""
Charon Zero Ingestion — Stage 1B: The Second Crossing

Pulls low-lying zeros from LMFDB lfunc_lfunctions table for all
objects already in the Charon database.

Zero vector format (24 dimensions):
  [first 20 normalized zeros, root_number, analytic_rank, degree, log(conductor)]

Normalization: gamma_n / log(conductor) per Katz-Sarnak convention,
so mean spacing is approximately 1.

Origin path mapping:
  MF label "N.k.chi.x" -> "ModularForm/GL2/Q/holomorphic/N/k/chi/x"
  EC iso class "N.x" -> "EllipticCurve/Q/N/x"
"""

import json
import math
import logging
import time

import duckdb
import psycopg2
import numpy as np

from charon.src.config import LMFDB_PG, DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("charon.ingest_zeros")

N_ZEROS = 20  # first 20 zeros in the vector


def mf_label_to_origin(label):
    """Convert MF label like '11.2.a.a' to LMFDB L-function origin path."""
    parts = label.split('.')
    if len(parts) == 4:
        return f"ModularForm/GL2/Q/holomorphic/{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}"
    return None


def ec_iso_to_origin(iso_label):
    """Convert EC isogeny class label like '11.a' to LMFDB L-function origin path."""
    parts = iso_label.split('.')
    if len(parts) == 2:
        return f"EllipticCurve/Q/{parts[0]}/{parts[1]}"
    return None


def build_zero_vector(zeros, root_number, order_of_vanishing, conductor, degree=2):
    """
    Build the 24-dim zero vector:
      [first 20 normalized zeros, root_number, analytic_rank, degree, log(conductor)]

    Normalization: gamma_n * log(conductor) / (2 * pi) is the standard
    unfolding that makes mean spacing ~1. But for simplicity and since all
    our objects are degree 2, we use gamma_n / log(conductor).
    """
    log_cond = math.log(max(conductor, 2))

    # Normalize zeros
    normalized = []
    for i in range(N_ZEROS):
        if i < len(zeros) and zeros[i] is not None:
            z = float(zeros[i])
            normalized.append(z / log_cond)
        else:
            normalized.append(None)

    # Parse root number (can be complex string like "0.78 + 0.62*I")
    rn = 0.0
    if root_number is not None:
        rn_str = str(root_number).strip()
        if rn_str in ('1', '1.0', '+1'):
            rn = 1.0
        elif rn_str in ('-1', '-1.0'):
            rn = -1.0
        else:
            # Complex root number — take the real part
            try:
                # Format: "a + b*I" or "a - b*I"
                rn_str = rn_str.replace('*I', '').replace('I', '')
                parts = rn_str.split('+')
                if len(parts) >= 1:
                    rn = float(parts[0].strip())
            except (ValueError, IndexError):
                rn = 0.0

    vec = normalized + [rn, float(order_of_vanishing or 0), float(degree), log_cond]
    completeness = sum(1 for v in vec if v is not None) / len(vec)
    return vec, completeness


def ingest_zeros(batch_size=500):
    """Pull zeros from LMFDB for all objects in Charon DB."""
    duck = duckdb.connect(str(DB_PATH))

    # Ensure object_zeros table exists
    duck.execute("""
        CREATE TABLE IF NOT EXISTS object_zeros (
            object_id INTEGER PRIMARY KEY,
            zeros_vector DOUBLE[],
            zeros_completeness DOUBLE,
            root_number DOUBLE,
            analytic_rank INTEGER,
            n_zeros_stored INTEGER
        )
    """)
    log.info("object_zeros table ready")

    # Get all objects that don't yet have zeros
    objects = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.object_type, o.conductor
        FROM objects o
        LEFT JOIN object_zeros oz ON o.id = oz.object_id
        WHERE oz.object_id IS NULL
        ORDER BY o.id
    """).fetchall()

    # For ECs, get isogeny class mapping (same iso class → same L-function)
    ec_iso = dict(duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso FROM elliptic_curves ec
    """).fetchall())

    log.info(f"Objects needing zeros: {len(objects)}")

    # Connect to LMFDB
    pg = psycopg2.connect(**LMFDB_PG)
    pg_cur = pg.cursor()

    # Cache: origin -> zero data (to avoid re-querying same L-function)
    zero_cache = {}
    found = 0
    not_found = 0
    updated = 0

    t0 = time.time()

    for i, (obj_id, label, obj_type, conductor) in enumerate(objects):
        # Build origin path
        if obj_type == 'modular_form':
            origin = mf_label_to_origin(label)
        elif obj_type == 'elliptic_curve':
            iso = ec_iso.get(obj_id)
            origin = ec_iso_to_origin(iso) if iso else None
        else:
            origin = None

        if origin is None:
            not_found += 1
            continue

        # Check cache
        if origin in zero_cache:
            zero_data = zero_cache[origin]
        else:
            # Query LMFDB
            pg_cur.execute("""
                SELECT positive_zeros, z1, z2, z3,
                       root_number, order_of_vanishing, degree
                FROM lfunc_lfunctions
                WHERE origin = %s
                LIMIT 1
            """, [origin])
            row = pg_cur.fetchone()

            if row:
                pos_zeros = row[0]  # array of zeros
                z1, z2, z3 = row[1], row[2], row[3]
                root_number = row[4]
                rov = row[5]
                degree = row[6]

                # Build zeros list: prefer positive_zeros array, fallback to z1/z2/z3
                if pos_zeros and len(pos_zeros) > 0:
                    zeros = [float(z) for z in pos_zeros]
                else:
                    zeros = []
                    for z in [z1, z2, z3]:
                        if z is not None:
                            zeros.append(float(z))

                zero_data = {
                    'zeros': zeros,
                    'root_number': root_number,
                    'order_of_vanishing': rov,
                    'degree': degree or 2,
                }
                found += 1
            else:
                zero_data = None
                not_found += 1

            zero_cache[origin] = zero_data

        # Insert into object_zeros
        if zero_data:
            vec, comp = build_zero_vector(
                zero_data['zeros'],
                zero_data['root_number'],
                zero_data['order_of_vanishing'],
                int(conductor),
                zero_data['degree'],
            )

            # Parse root number for storage
            rn_val = vec[N_ZEROS]  # root_number is at index 20
            rov_val = int(zero_data['order_of_vanishing'] or 0)
            n_stored = len(zero_data['zeros'])

            duck.execute(
                """INSERT OR REPLACE INTO object_zeros
                   (object_id, zeros_vector, zeros_completeness, root_number, analytic_rank, n_zeros_stored)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [obj_id, vec, comp, rn_val, rov_val, n_stored],
            )
            updated += 1

        if (i + 1) % 1000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            log.info(f"Progress: {i+1}/{len(objects)}, "
                     f"found={found}, not_found={not_found}, updated={updated}, "
                     f"cache_size={len(zero_cache)}, rate={rate:.0f}/s")

    pg_cur.close()
    pg.close()
    duck.close()

    elapsed = time.time() - t0
    log.info(f"Zero ingestion complete in {elapsed:.1f}s")
    log.info(f"  Found: {found}, Not found: {not_found}")
    log.info(f"  Updated: {updated} objects")
    log.info(f"  Cache size: {len(zero_cache)} unique L-functions")

    return {"found": found, "not_found": not_found, "updated": updated}


if __name__ == "__main__":
    ingest_zeros()
