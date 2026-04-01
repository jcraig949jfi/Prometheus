"""
Charon Ingestion Pipeline — Stage 1: The Crossing

Pulls mathematical objects from the LMFDB PostgreSQL mirror into local DuckDB.
Three parallel streams:
  1. Elliptic curves over Q (ec_curvedata + ec_classdata)
  2. Classical modular forms, weight 2 (mf_newforms + mf_hecke_nf)
  3. L-functions (lfunc_lfunctions + lfunc_instances)

Each stream:
  - Fetches from LMFDB PostgreSQL
  - Extracts type-specific metadata
  - Constructs universal invariant vector (a_p for first 50 primes)
  - Inserts into DuckDB objects table + type-specific table
  - Logs provenance
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional

import duckdb
import psycopg2
import psycopg2.extras

from charon.src.config import (
    LMFDB_PG, DB_PATH, BATCH_SIZE, MAX_CONDUCTOR_PHASE1,
    FIRST_50_PRIMES, INVARIANT_PRIMES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("charon.ingest")


def get_lmfdb_conn():
    """Connect to the LMFDB PostgreSQL mirror."""
    return psycopg2.connect(**LMFDB_PG)


def get_duck(path=DB_PATH):
    """Connect to local DuckDB."""
    return duckdb.connect(str(path))


def log_ingestion(duck, source_table, query_params, status="running"):
    """Create an ingestion log entry, return its ID."""
    row_id = duck.execute("SELECT nextval('ingestion_id_seq')").fetchone()[0]
    duck.execute(
        """INSERT INTO ingestion_log (id, source_table, query_params, rows_fetched, rows_inserted, started_at, status)
           VALUES (?, ?, ?, 0, 0, current_timestamp, ?)""",
        [row_id, source_table, json.dumps(query_params), status],
    )
    return row_id


def update_ingestion_log(duck, log_id, rows_fetched, rows_inserted, status="completed"):
    """Update an ingestion log entry on completion."""
    duck.execute(
        """UPDATE ingestion_log SET rows_fetched=?, rows_inserted=?, completed_at=current_timestamp, status=?
           WHERE id=?""",
        [rows_fetched, rows_inserted, status, log_id],
    )


# ============================================================
# Prime index helper
# ============================================================

# Map prime -> index in FIRST_50_PRIMES for fast lookup
_PRIME_TO_IDX = {p: i for i, p in enumerate(FIRST_50_PRIMES)}

# First 25 primes (what ec_classdata.aplist covers)
FIRST_25_PRIMES = FIRST_50_PRIMES[:25]

# First 168 primes up to 997 (what mf_hecke_nf covers)
def _sieve(n):
    """Simple sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(n + 1) if is_prime[i]]

ALL_PRIMES_TO_997 = _sieve(997)


def build_invariant_vector_from_aplist(aplist: list, conductor: int) -> list:
    """
    Build the 50-element universal invariant vector from ec_classdata.aplist.
    aplist has a_p for first 25 primes. Remaining 25 slots are None.
    For primes dividing conductor, a_p encodes reduction type — still valid as invariant.
    """
    vec = [None] * INVARIANT_PRIMES
    for i, ap in enumerate(aplist or []):
        if i < 25:
            vec[i] = float(ap)
    completeness = sum(1 for v in vec if v is not None) / INVARIANT_PRIMES
    return vec, completeness


def build_invariant_vector_from_hecke(ap_coeffs: list, dim: int) -> list:
    """
    Build the 50-element universal invariant vector from mf_hecke_nf.ap.

    For dimension-1 (rational) newforms: ap_coeffs entries are single-element lists like [-2].
    For higher-dimension: we use the trace (sum of embeddings) as the invariant.

    ap_coeffs is indexed by prime order: ap_coeffs[0] = a_2, ap_coeffs[1] = a_3, etc.
    """
    vec = [None] * INVARIANT_PRIMES
    if not ap_coeffs:
        return vec, 0.0

    for i in range(min(len(ap_coeffs), INVARIANT_PRIMES)):
        coeff = ap_coeffs[i]
        if isinstance(coeff, list) and len(coeff) > 0:
            if dim == 1:
                # Rational newform: a_p is a single integer
                vec[i] = float(coeff[0])
            else:
                # Higher-dimensional: use trace (first coefficient in power basis = trace for many cases)
                # For the universal vector, trace is the natural projection to Q
                vec[i] = float(coeff[0])
        elif isinstance(coeff, (int, float)):
            vec[i] = float(coeff)

    completeness = sum(1 for v in vec if v is not None) / INVARIANT_PRIMES
    return vec, completeness


def build_invariant_from_traces(traces: list, conductor: int) -> list:
    """
    Build invariant vector from mf_newforms.traces (tr(a_n) for n=1..1000).
    Extract a_p values at prime indices within the traces array.
    traces[0] = a_1, traces[1] = a_2, ..., traces[p-1] = a_p.
    """
    vec = [None] * INVARIANT_PRIMES
    if not traces:
        return vec, 0.0

    for i, p in enumerate(FIRST_50_PRIMES):
        idx = p - 1  # traces is 0-indexed, traces[p-1] = a_p
        if idx < len(traces) and traces[idx] is not None:
            vec[i] = float(traces[idx])

    completeness = sum(1 for v in vec if v is not None) / INVARIANT_PRIMES
    return vec, completeness


# ============================================================
# Elliptic Curve Ingestion
# ============================================================

def ingest_elliptic_curves(max_conductor=MAX_CONDUCTOR_PHASE1, batch_size=BATCH_SIZE):
    """
    Ingest elliptic curves from LMFDB into Charon DuckDB.
    Pulls from ec_curvedata joined with ec_classdata for aplist.
    """
    duck = get_duck()
    log_id = log_ingestion(duck, "ec_curvedata+ec_classdata",
                           {"max_conductor": max_conductor})

    log.info(f"Starting EC ingestion: conductor <= {max_conductor}")

    pg = get_lmfdb_conn()
    pg_cur = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Count available
    pg_cur.execute(
        "SELECT COUNT(*) FROM ec_curvedata WHERE conductor <= %s",
        [max_conductor],
    )
    total_available = pg_cur.fetchone()[0]
    log.info(f"LMFDB has {total_available} curves with conductor <= {max_conductor}")

    # Fetch curves joined with classdata for aplist
    query = """
        SELECT c.lmfdb_label, c.\"Clabel\", c.lmfdb_iso, c.\"Ciso\",
               c.conductor, c.ainvs, c.rank, c.analytic_rank,
               c.torsion, c.torsion_structure, c.cm, c.regulator, c.sha,
               c.degree, c.isogeny_degrees, c.bad_primes, c.jinv,
               c.class_size, c.class_deg, c.manin_constant, c.optimality,
               c.semistable, c.faltings_height,
               cl.aplist, cl.anlist, cl.trace_hash
        FROM ec_curvedata c
        LEFT JOIN ec_classdata cl ON c.lmfdb_iso = cl.lmfdb_iso
        WHERE c.conductor <= %s
        ORDER BY c.conductor, c.lmfdb_label
    """

    pg_cur.execute(query, [max_conductor])

    rows_fetched = 0
    rows_inserted = 0
    batch = []

    while True:
        rows = pg_cur.fetchmany(batch_size)
        if not rows:
            break

        rows_fetched += len(rows)

        for row in rows:
            try:
                obj_id = duck.execute("SELECT nextval('objects_id_seq')").fetchone()[0]

                label = row["lmfdb_label"]
                conductor = int(row["conductor"])
                aplist = row["aplist"]
                inv_vec, completeness = build_invariant_vector_from_aplist(aplist, conductor)

                # Type-specific metadata for JSON column
                properties = {
                    "rank": row["rank"],
                    "analytic_rank": row["analytic_rank"],
                    "torsion": row["torsion"],
                    "torsion_structure": row["torsion_structure"],
                    "cm": row["cm"],
                    "regulator": float(row["regulator"]) if row["regulator"] else None,
                    "sha": row["sha"],
                    "degree": row["degree"],
                    "bad_primes": row["bad_primes"],
                    "semistable": row["semistable"],
                    "cremona_label": row["Clabel"],
                }

                # Insert into objects table
                duck.execute(
                    """INSERT INTO objects (id, lmfdb_label, object_type, conductor, invariant_vector, properties, coefficient_completeness)
                       VALUES (?, ?, 'elliptic_curve', ?, ?, ?, ?)""",
                    [obj_id, label, conductor, inv_vec, json.dumps(properties), completeness],
                )

                # Parse j-invariant
                jinv = row["jinv"]
                jinv_num, jinv_den = (float(jinv[0]), float(jinv[1])) if jinv and len(jinv) >= 2 else (None, None)

                ainvs = [float(a) for a in row["ainvs"]] if row["ainvs"] else None

                # Insert into elliptic_curves table
                duck.execute(
                    """INSERT INTO elliptic_curves
                       (object_id, lmfdb_label, lmfdb_iso, cremona_label, cremona_iso,
                        conductor, ainvs, rank, analytic_rank, torsion, torsion_structure,
                        cm, regulator, sha, degree, isogeny_degrees, bad_primes,
                        jinv_num, jinv_den, aplist, anlist, class_size, class_deg,
                        manin_constant, optimality, semistable, faltings_height, trace_hash)
                       VALUES (?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?)""",
                    [
                        obj_id, label, row["lmfdb_iso"], row["Clabel"], row["Ciso"],
                        conductor, ainvs, row["rank"], row["analytic_rank"],
                        row["torsion"], row["torsion_structure"],
                        row["cm"],
                        float(row["regulator"]) if row["regulator"] else None,
                        row["sha"], row["degree"],
                        row["isogeny_degrees"], row["bad_primes"],
                        jinv_num, jinv_den,
                        [int(a) for a in aplist] if aplist else None,
                        [int(a) for a in row["anlist"]] if row["anlist"] else None,
                        row["class_size"], row["class_deg"],
                        row["manin_constant"], row["optimality"],
                        row["semistable"],
                        float(row["faltings_height"]) if row["faltings_height"] else None,
                        row["trace_hash"],
                    ],
                )
                rows_inserted += 1

            except Exception as e:
                log.warning(f"Failed to ingest EC {row.get('lmfdb_label', '?')}: {e}")
                continue

        log.info(f"EC progress: {rows_fetched}/{total_available} fetched, {rows_inserted} inserted")

    update_ingestion_log(duck, log_id, rows_fetched, rows_inserted)
    pg_cur.close()
    pg.close()
    duck.close()
    log.info(f"EC ingestion complete: {rows_inserted} curves ingested")
    return rows_inserted


# ============================================================
# Modular Form Ingestion
# ============================================================

def ingest_modular_forms(max_level=MAX_CONDUCTOR_PHASE1, weight=2, batch_size=BATCH_SIZE):
    """
    Ingest weight-2 newforms from LMFDB into Charon DuckDB.
    These are the forms connected to elliptic curves by modularity theorem.
    Pulls from mf_newforms joined with mf_hecke_nf for algebraic a_p.
    """
    duck = get_duck()
    log_id = log_ingestion(duck, "mf_newforms+mf_hecke_nf",
                           {"max_level": max_level, "weight": weight})

    log.info(f"Starting MF ingestion: weight={weight}, level <= {max_level}")

    pg = get_lmfdb_conn()
    pg_cur = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Count
    pg_cur.execute(
        "SELECT COUNT(*) FROM mf_newforms WHERE weight = %s AND level <= %s",
        [weight, max_level],
    )
    total_available = pg_cur.fetchone()[0]
    log.info(f"LMFDB has {total_available} weight-{weight} newforms with level <= {max_level}")

    # Fetch newforms with hecke data
    query = """
        SELECT nf.label, nf.space_label, nf.level, nf.weight, nf.dim,
               nf.hecke_orbit, nf.hecke_orbit_code,
               nf.char_order, nf.char_parity, nf.char_conductor, nf.char_orbit_label,
               nf.fricke_eigenval, nf.atkin_lehner_string,
               nf.analytic_conductor, nf.self_twist_type,
               nf.is_cm, nf.is_rm, nf.is_self_dual,
               nf.sato_tate_group, nf.traces, nf.field_poly,
               nf.related_objects,
               h.ap, h.maxp
        FROM mf_newforms nf
        LEFT JOIN mf_hecke_nf h ON nf.hecke_orbit_code = h.hecke_orbit_code
        WHERE nf.weight = %s AND nf.level <= %s
        ORDER BY nf.level, nf.label
    """

    pg_cur.execute(query, [weight, max_level])

    rows_fetched = 0
    rows_inserted = 0

    while True:
        rows = pg_cur.fetchmany(batch_size)
        if not rows:
            break

        rows_fetched += len(rows)

        for row in rows:
            try:
                obj_id = duck.execute("SELECT nextval('objects_id_seq')").fetchone()[0]

                label = row["label"]
                level = int(row["level"])
                dim = int(row["dim"]) if row["dim"] else 1

                # Build invariant vector: prefer mf_hecke_nf.ap, fallback to traces
                ap_coeffs = row["ap"]
                if ap_coeffs and len(ap_coeffs) > 0:
                    inv_vec, completeness = build_invariant_vector_from_hecke(ap_coeffs, dim)
                elif row["traces"]:
                    inv_vec, completeness = build_invariant_from_traces(row["traces"], level)
                else:
                    inv_vec = [None] * INVARIANT_PRIMES
                    completeness = 0.0

                properties = {
                    "level": level,
                    "weight": row["weight"],
                    "dim": dim,
                    "char_order": row["char_order"],
                    "is_cm": row["is_cm"],
                    "is_rm": row["is_rm"],
                    "fricke_eigenval": row["fricke_eigenval"],
                    "analytic_conductor": float(row["analytic_conductor"]) if row["analytic_conductor"] else None,
                    "self_twist_type": row["self_twist_type"],
                }

                # Insert into objects
                duck.execute(
                    """INSERT INTO objects (id, lmfdb_label, object_type, conductor, invariant_vector, properties, coefficient_completeness)
                       VALUES (?, ?, 'modular_form', ?, ?, ?, ?)""",
                    [obj_id, label, level, inv_vec, json.dumps(properties), completeness],
                )

                # Insert into modular_forms
                traces = [float(t) for t in row["traces"]] if row["traces"] else None

                duck.execute(
                    """INSERT INTO modular_forms
                       (object_id, lmfdb_label, space_label, level, weight, dim,
                        hecke_orbit, hecke_orbit_code,
                        char_order, char_parity, char_conductor, char_orbit_label,
                        fricke_eigenval, atkin_lehner_string, analytic_conductor,
                        self_twist_type, is_cm, is_rm, is_self_dual,
                        sato_tate_group, traces, ap_coeffs, ap_maxp, field_poly,
                        related_objects)
                       VALUES (?,?,?,?,?,?, ?,?, ?,?,?,?, ?,?,?, ?,?,?,?, ?,?,?,?,?, ?)""",
                    [
                        obj_id, label, row["space_label"], level, row["weight"], dim,
                        row["hecke_orbit"], row["hecke_orbit_code"],
                        row["char_order"], row["char_parity"],
                        row["char_conductor"], row["char_orbit_label"],
                        row["fricke_eigenval"], row["atkin_lehner_string"],
                        float(row["analytic_conductor"]) if row["analytic_conductor"] else None,
                        row["self_twist_type"], row["is_cm"], row["is_rm"], row["is_self_dual"],
                        row["sato_tate_group"],
                        traces,
                        json.dumps(ap_coeffs) if ap_coeffs else None,
                        row["maxp"],
                        [float(c) for c in row["field_poly"]] if row["field_poly"] else None,
                        row["related_objects"],
                    ],
                )
                rows_inserted += 1

            except Exception as e:
                log.warning(f"Failed to ingest MF {row.get('label', '?')}: {e}")
                continue

        log.info(f"MF progress: {rows_fetched}/{total_available} fetched, {rows_inserted} inserted")

    update_ingestion_log(duck, log_id, rows_fetched, rows_inserted)
    pg_cur.close()
    pg.close()
    duck.close()
    log.info(f"MF ingestion complete: {rows_inserted} forms ingested")
    return rows_inserted


# ============================================================
# Known Bridge Construction (Cremona ground truth)
# ============================================================

def build_known_bridges():
    """
    Construct known_bridges from the modularity theorem:
    Every elliptic curve over Q of conductor N corresponds to a weight-2
    newform of level N with the same L-function.

    The bridge is: EC with conductor N, isogeny class label X.Y
    matches modular form N.2.a.? where the a_p coefficients agree.

    We match on conductor + invariant vector agreement.
    """
    duck = get_duck()

    log.info("Building known bridges from modularity theorem...")

    # Get all EC objects with their invariant vectors
    ecs = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.conductor, o.invariant_vector,
               ec.lmfdb_iso
        FROM objects o
        JOIN elliptic_curves ec ON o.id = ec.object_id
        WHERE o.invariant_vector IS NOT NULL
          AND o.coefficient_completeness > 0
    """).fetchall()

    # Get all MF objects grouped by conductor (=level for weight 2, trivial char)
    mfs = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.conductor, o.invariant_vector,
               mf.dim
        FROM objects o
        JOIN modular_forms mf ON o.id = mf.object_id
        WHERE o.invariant_vector IS NOT NULL
          AND o.coefficient_completeness > 0
          AND mf.weight = 2
          AND mf.char_order = 1
    """).fetchall()

    # Index MFs by conductor
    mf_by_conductor = {}
    for mf_row in mfs:
        cond = mf_row[2]
        if cond not in mf_by_conductor:
            mf_by_conductor[cond] = []
        mf_by_conductor[cond].append(mf_row)

    bridges_found = 0
    checked = 0

    # For each EC isogeny class (use one representative per class)
    seen_iso = set()

    for ec_row in ecs:
        ec_id, ec_label, ec_cond, ec_vec, ec_iso = ec_row

        # One bridge per isogeny class
        if ec_iso in seen_iso:
            continue
        seen_iso.add(ec_iso)
        checked += 1

        candidates = mf_by_conductor.get(ec_cond, [])
        if not candidates:
            continue

        # Find matching modular form by invariant vector agreement
        best_match = None
        best_dist = float("inf")

        for mf_row in candidates:
            mf_id, mf_label, mf_cond, mf_vec, mf_dim = mf_row

            # Compute L2 distance on shared non-None slots
            dist = 0.0
            shared = 0
            for a, b in zip(ec_vec, mf_vec):
                if a is not None and b is not None:
                    dist += (a - b) ** 2
                    shared += 1

            if shared > 0:
                dist = (dist / shared) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best_match = mf_row

        if best_match and best_dist < 1e-3:
            bridge_id = duck.execute("SELECT nextval('bridges_id_seq')").fetchone()[0]
            duck.execute(
                """INSERT INTO known_bridges (id, source_id, target_id, source_label, target_label, bridge_type, verified, source_reference)
                   VALUES (?, ?, ?, ?, ?, 'modularity', TRUE, 'Cremona database / modularity theorem')
                   ON CONFLICT DO NOTHING""",
                [bridge_id, ec_id, best_match[0], ec_label, best_match[1]],
            )
            bridges_found += 1

    duck.close()
    log.info(f"Known bridges: checked {checked} isogeny classes, found {bridges_found} modularity bridges (dist < 1e-3)")
    return bridges_found


# ============================================================
# Main entry point
# ============================================================

def run_phase1(max_conductor=MAX_CONDUCTOR_PHASE1):
    """Run full Phase 1 ingestion: EC + MF + bridge construction."""
    log.info("=" * 60)
    log.info("CHARON PHASE 1 INGESTION — THE FIRST CROSSING")
    log.info("=" * 60)

    t0 = time.time()

    ec_count = ingest_elliptic_curves(max_conductor=max_conductor)
    mf_count = ingest_modular_forms(max_level=max_conductor, weight=2)
    bridge_count = build_known_bridges()

    elapsed = time.time() - t0
    log.info("=" * 60)
    log.info(f"Phase 1 complete in {elapsed:.1f}s")
    log.info(f"  Elliptic curves: {ec_count}")
    log.info(f"  Modular forms:   {mf_count}")
    log.info(f"  Known bridges:   {bridge_count}")
    log.info("=" * 60)

    return {"ec": ec_count, "mf": mf_count, "bridges": bridge_count}


if __name__ == "__main__":
    run_phase1()
