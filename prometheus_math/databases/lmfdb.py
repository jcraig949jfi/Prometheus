"""Typed wrapper over the LMFDB Postgres mirror at devmirror.lmfdb.xyz.

LMFDB (the L-functions and Modular Forms Database, https://www.lmfdb.org)
maintains a public read-only Postgres mirror. This module is the canonical
entry point for Prometheus agents (Charon, Ergon, Aporia, ...) doing
elliptic-curve, number-field, modular-form, L-function, or genus-2-curve
research.

Connection model
----------------
psycopg2 connections are cheap; this module opens a fresh connection per
query unless the caller provides one. Pass ``conn=...`` to any accessor
(or ``query``) when running many queries in a tight loop.

    # one-shot
    rows = lmfdb.elliptic_curves(conductor=37)

    # batched (cheaper if you're hammering the mirror)
    with lmfdb.connect() as conn:
        for label in labels:
            row = lmfdb.elliptic_curves(label=label, conn=conn)

Return shape
------------
All accessors return ``list[dict]`` (or ``dict | None`` for ``ec_mwbsd``).
Decimal columns are converted to ``float``; integer-typed Postgres arrays
(``ainvs``, ``coeffs``, ...) are converted to ``list[int]``; numeric
arrays to ``list[float]``. The original column names from LMFDB are
preserved.

Safety
------
Every accessor uses parameterized SQL (``%s`` placeholders). Free-form
``where`` clauses in :func:`count` accept user-provided text — if you
expose those to untrusted input you must validate them yourself.
"""
from __future__ import annotations

from contextlib import contextmanager
from decimal import Decimal
from typing import Any, Iterable, Optional

import psycopg2
import psycopg2.extensions

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

LMFDB_HOST = "devmirror.lmfdb.xyz"
LMFDB_PORT = 5432
LMFDB_DBNAME = "lmfdb"
LMFDB_USER = "lmfdb"
LMFDB_PASSWORD = "lmfdb"  # public read-only mirror; no secrets concern


class LMFDBConnectionError(RuntimeError):
    """Raised when the LMFDB mirror cannot be reached."""


def connect(timeout: int = 10) -> psycopg2.extensions.connection:
    """Open a new connection to the LMFDB Postgres mirror.

    The caller is responsible for ``close()`` (or use as a context manager;
    psycopg2 connections support ``with``).
    """
    try:
        return psycopg2.connect(
            host=LMFDB_HOST,
            port=LMFDB_PORT,
            dbname=LMFDB_DBNAME,
            user=LMFDB_USER,
            password=LMFDB_PASSWORD,
            connect_timeout=timeout,
        )
    except psycopg2.OperationalError as e:
        raise LMFDBConnectionError(
            f"Could not connect to LMFDB mirror at {LMFDB_HOST}:{LMFDB_PORT} "
            f"(dbname={LMFDB_DBNAME}). The mirror may be unreachable, your "
            f"network blocked, or the connection timed out after {timeout}s. "
            f"Original error: {e}"
        ) from e


def probe(timeout: float = 3.0) -> bool:
    """Cheap reachability check used by ``prometheus_math.registry``.

    Returns True iff a Postgres connection to the LMFDB mirror succeeds
    within ``timeout`` seconds. Never raises.
    """
    try:
        conn = psycopg2.connect(
            host=LMFDB_HOST,
            port=LMFDB_PORT,
            dbname=LMFDB_DBNAME,
            user=LMFDB_USER,
            password=LMFDB_PASSWORD,
            connect_timeout=int(max(1, round(timeout))),
        )
        conn.close()
        return True
    except Exception:
        return False


@contextmanager
def _maybe_conn(conn: Optional[psycopg2.extensions.connection], timeout: int):
    """Yield ``conn`` if provided, else open a fresh one and close it."""
    if conn is not None:
        yield conn
        return
    own = connect(timeout=timeout)
    try:
        yield own
    finally:
        try:
            own.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Value coercion
# ---------------------------------------------------------------------------


def _coerce_scalar(v: Any) -> Any:
    if isinstance(v, Decimal):
        # int when integral, else float
        if v == v.to_integral_value():
            try:
                return int(v)
            except (OverflowError, ValueError):
                return float(v)
        return float(v)
    return v


def _coerce_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return _coerce_scalar(v)
    if isinstance(v, list):
        return [_coerce_value(x) for x in v]
    if isinstance(v, tuple):
        return tuple(_coerce_value(x) for x in v)
    return v


def _row_to_dict(cols: list[str], row: tuple) -> dict:
    return {c: _coerce_value(v) for c, v in zip(cols, row)}


# ---------------------------------------------------------------------------
# Generic query
# ---------------------------------------------------------------------------


def query(
    sql: str,
    params: Optional[Iterable[Any]] = None,
    timeout: int = 10,
    conn: Optional[psycopg2.extensions.connection] = None,
) -> list[tuple]:
    """Execute a SQL query and return all rows as raw tuples.

    Use parameterized queries (``%s`` placeholders) — never string-format
    user input into ``sql``. For dict-shaped results prefer the typed
    accessors below or :func:`query_dicts`.
    """
    with _maybe_conn(conn, timeout) as c:
        with c.cursor() as cur:
            cur.execute(sql, tuple(params) if params else None)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                # No results to fetch (e.g. DDL); return empty list
                return []


def query_dicts(
    sql: str,
    params: Optional[Iterable[Any]] = None,
    timeout: int = 10,
    conn: Optional[psycopg2.extensions.connection] = None,
) -> list[dict]:
    """Same as :func:`query` but returns rows as coerced dicts."""
    with _maybe_conn(conn, timeout) as c:
        with c.cursor() as cur:
            cur.execute(sql, tuple(params) if params else None)
            cols = [d[0] for d in cur.description] if cur.description else []
            try:
                rows = cur.fetchall()
            except psycopg2.ProgrammingError:
                return []
            return [_row_to_dict(cols, r) for r in rows]


# ---------------------------------------------------------------------------
# Internal: filter builder
# ---------------------------------------------------------------------------


def _build_select(
    table: str,
    columns: Optional[list[str]],
    filters: dict[str, Any],
    extra_clauses: Optional[list[tuple[str, Any]]] = None,
    limit: Optional[int] = None,
) -> tuple[str, list[Any]]:
    """Build a parameterized SELECT statement.

    Identifiers (``table``, ``columns``, filter keys) are NOT user-provided
    here — they are constants from the typed accessors below. Values flow
    through ``%s`` placeholders.
    """
    col_sql = "*" if not columns else ", ".join(f'"{c}"' for c in columns)
    sql = f'SELECT {col_sql} FROM "{table}"'
    where_parts: list[str] = []
    params: list[Any] = []
    for key, val in filters.items():
        if val is None:
            continue
        where_parts.append(f'"{key}" = %s')
        params.append(val)
    if extra_clauses:
        for clause, val in extra_clauses:
            where_parts.append(clause)
            if val is not None:
                if isinstance(val, (list, tuple)):
                    params.extend(val)
                else:
                    params.append(val)
    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)
    if limit is not None:
        sql += " LIMIT %s"
        params.append(int(limit))
    return sql, params


# ---------------------------------------------------------------------------
# Typed accessors
# ---------------------------------------------------------------------------

# Curated subset of columns we expose by default. The full row is large;
# callers wanting other columns can use query_dicts().
_EC_CURVEDATA_COLS = [
    "lmfdb_label",
    "ainvs",
    "conductor",
    "rank",
    "analytic_rank",
    "torsion",
    "torsion_structure",
    "sha",
    "regulator",
    "cm",
    "faltings_height",
    "signD",
    "jinv",
    "bad_primes",
]


def elliptic_curves(
    label: Optional[str] = None,
    conductor: Optional[int] = None,
    rank: Optional[int] = None,
    cm: Optional[int] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
    columns: Optional[list[str]] = None,
) -> list[dict]:
    """Query ``ec_curvedata``.

    Parameters
    ----------
    label : LMFDB curve label (e.g. ``"37.a1"``).
    conductor : Filter on conductor.
    rank : Filter on Mordell-Weil rank.
    cm : Filter on CM discriminant (0 for non-CM).
    limit : Max rows (default 1000).
    columns : Override the default subset; pass ``["*"]`` for all.

    Returns dicts containing ``lmfdb_label``, ``ainvs``, ``conductor``,
    ``rank``, ``analytic_rank``, ``torsion``, ``sha``, ``regulator``,
    ``cm``, ``faltings_height``, ``signD``, ``jinv``, ``bad_primes``.
    """
    cols = None if columns == ["*"] else (columns or _EC_CURVEDATA_COLS)
    sql, params = _build_select(
        "ec_curvedata",
        cols,
        {"lmfdb_label": label, "conductor": conductor, "rank": rank, "cm": cm},
        limit=limit,
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


def ec_mwbsd(
    label: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> Optional[dict]:
    """Mordell-Weil + BSD data for a single elliptic curve.

    Returns a dict with ``lmfdb_label``, ``sha_an``, ``real_period``,
    ``area``, ``special_value``, ``tamagawa_product``, ``ngens``,
    ``rank_bounds``, ``gens``, ``heights``, ``torsion_generators``,
    ``xcoord_integral_points``, ``conductor``; or ``None`` if the label
    is not present in ``ec_mwbsd``. (The regulator lives on
    ``ec_curvedata`` -- pull it via :func:`elliptic_curves`.)
    """
    sql, params = _build_select(
        "ec_mwbsd",
        None,
        {"lmfdb_label": label},
        limit=1,
    )
    rows = query_dicts(sql, params, timeout=timeout, conn=conn)
    return rows[0] if rows else None


_NF_FIELDS_COLS = [
    "label",
    "coeffs",
    "degree",
    "r2",
    "disc_abs",
    "disc_sign",
    "class_number",
    "regulator",
    "galois_label",
    "is_galois",
    "gal_is_solvable",
    "ramps",
    "rd",
]


def number_fields(
    label: Optional[str] = None,
    degree: Optional[int] = None,
    signature: Optional[tuple[int, int]] = None,
    abs_disc_max: Optional[int] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
    columns: Optional[list[str]] = None,
) -> list[dict]:
    """Query ``nf_fields``.

    Parameters
    ----------
    label : LMFDB number-field label (e.g. ``"2.0.7751.1"``).
    degree : Filter by degree of the defining polynomial.
    signature : ``(r1, r2)`` tuple. Internally translates to
        ``degree = r1 + 2*r2`` and ``r2 = r2``.
    abs_disc_max : Upper bound on ``|disc|`` (inclusive).
    limit : Max rows.

    Returns dicts containing ``label``, ``coeffs`` (defining polynomial,
    polredabs'd), ``degree``, ``r2``, ``disc_abs``, ``disc_sign``,
    ``class_number``, ``regulator``, ``galois_label``, ``is_galois``,
    ``gal_is_solvable``, ``ramps``, ``rd``.
    """
    cols = None if columns == ["*"] else (columns or _NF_FIELDS_COLS)
    filters: dict[str, Any] = {"label": label, "degree": degree}
    extra: list[tuple[str, Any]] = []
    if signature is not None:
        r1, r2 = signature
        deg = r1 + 2 * r2
        # Override / add degree filter consistent with signature
        filters["degree"] = deg
        extra.append(('"r2" = %s', r2))
    if abs_disc_max is not None:
        extra.append(('"disc_abs" <= %s', abs_disc_max))
    sql, params = _build_select(
        "nf_fields", cols, filters, extra_clauses=extra, limit=limit
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


_MF_NEWFORMS_COLS = [
    "label",
    "level",
    "weight",
    "dim",
    "char_orbit_index",
    "char_orbit_label",
    "analytic_rank",
    "is_self_dual",
    "is_cm",
    "is_rm",
    "sato_tate_group",
    "nf_label",
]


def modular_forms(
    label: Optional[str] = None,
    level: Optional[int] = None,
    weight: Optional[int] = None,
    char_orbit: Optional[int] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
    columns: Optional[list[str]] = None,
) -> list[dict]:
    """Query ``mf_newforms`` (classical modular newforms).

    Parameters
    ----------
    label : LMFDB newform label (e.g. ``"11.2.a.a"``).
    level : Filter by level.
    weight : Filter by weight.
    char_orbit : Filter by ``char_orbit_index``.

    Returns dicts containing ``label``, ``level``, ``weight``, ``dim``,
    ``char_orbit_index``, ``char_orbit_label``, ``analytic_rank``,
    ``is_self_dual``, ``is_cm``, ``is_rm``, ``sato_tate_group``,
    ``nf_label``.
    """
    cols = None if columns == ["*"] else (columns or _MF_NEWFORMS_COLS)
    sql, params = _build_select(
        "mf_newforms",
        cols,
        {
            "label": label,
            "level": level,
            "weight": weight,
            "char_orbit_index": char_orbit,
        },
        limit=limit,
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


# Default columns for lfunc_lfunctions: omit huge JSONB blobs (zeros, plot,
# euler factors) unless explicitly requested.
_LFUNCTIONS_BASE_COLS = [
    "label",
    "origin",
    "primitive",
    "self_dual",
    "algebraic",
    "rational",
    "degree",
    "conductor",
    "motivic_weight",
    "order_of_vanishing",
    "central_character",
    "st_group",
    "symmetry_type",
    "root_angle",
    "analytic_conductor",
    "leading_term",
    "trace_hash",
]
_LFUNCTIONS_ZERO_COLS = ["positive_zeros", "z1", "z2", "z3", "plot_delta"]


def lfunctions(
    origin: Optional[str] = None,
    degree: Optional[int] = None,
    conductor: Optional[int] = None,
    order_of_vanishing: Optional[int] = None,
    limit: int = 1000,
    with_zeros: bool = False,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
    columns: Optional[list[str]] = None,
) -> list[dict]:
    """Query ``lfunc_lfunctions``.

    Parameters
    ----------
    origin : Filter on the L-function origin (substring match via LIKE),
        e.g. ``"EllipticCurve"`` or ``"ModularForm"``.
    degree : Degree of the gamma-factor / Euler product.
    conductor : Conductor (analytic).
    order_of_vanishing : Filter on the analytic rank.
    with_zeros : If True, include ``positive_zeros``, ``z1``, ``z2``,
        ``z3``, ``plot_delta`` in the result.
    limit : Max rows.

    By default the heavy JSONB columns (``positive_zeros``,
    ``euler_factors``, ``plot_values``) are NOT pulled. Set
    ``with_zeros=True`` for the zero list, or pass an explicit ``columns``.
    """
    if columns == ["*"]:
        cols = None
    else:
        cols = list(columns) if columns else list(_LFUNCTIONS_BASE_COLS)
        if columns is None and with_zeros:
            cols = cols + _LFUNCTIONS_ZERO_COLS

    filters: dict[str, Any] = {
        "degree": degree,
        "conductor": conductor,
        "order_of_vanishing": order_of_vanishing,
    }
    extra: list[tuple[str, Any]] = []
    if origin is not None:
        extra.append(('"origin" LIKE %s', f"%{origin}%"))
    sql, params = _build_select(
        "lfunc_lfunctions", cols, filters, extra_clauses=extra, limit=limit
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


_G2C_CURVES_COLS = [
    "label",
    "class",
    "abs_disc",
    "disc_sign",
    "cond",
    "mw_rank",
    "mw_rank_proved",
    "analytic_rank",
    "analytic_sha",
    "torsion_order",
    "torsion_subgroup",
    "real_period",
    "regulator",
    "tamagawa_product",
    "root_number",
    "is_simple_geom",
    "is_gl2_type",
    "geom_end_alg",
    "st_group",
    "st_label",
    "num_rat_pts",
    "num_rat_wpts",
]


def g2c_curves(
    label: Optional[str] = None,
    abs_disc: Optional[int] = None,
    mw_rank: Optional[int] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
    columns: Optional[list[str]] = None,
) -> list[dict]:
    """Query ``g2c_curves`` (genus-2 curves over Q).

    Returns dicts with the standard genus-2 BSD/MW data: ``label``,
    ``abs_disc``, ``cond``, ``mw_rank``, ``analytic_rank``,
    ``analytic_sha``, ``torsion_order``, ``real_period``, ``regulator``,
    ``tamagawa_product``, ``root_number``, ``geom_end_alg``, ``st_group``,
    plus several others.
    """
    cols = None if columns == ["*"] else (columns or _G2C_CURVES_COLS)
    sql, params = _build_select(
        "g2c_curves",
        cols,
        {"label": label, "abs_disc": abs_disc, "mw_rank": mw_rank},
        limit=limit,
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------


def schema(
    table_name: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[tuple[str, str]]:
    """Return ``[(column_name, data_type), ...]`` for ``table_name``.

    Uses ``information_schema.columns`` and is therefore portable across
    Postgres versions.
    """
    sql = (
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = %s ORDER BY ordinal_position"
    )
    rows = query(sql, (table_name,), timeout=timeout, conn=conn)
    return [(r[0], r[1]) for r in rows]


def list_tables(
    pattern: str = "%",
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[str]:
    """List LMFDB tables (in the public schema) matching a SQL LIKE pattern.

    Default pattern ``'%'`` returns everything. Examples: ``'ec_%'``,
    ``'%_stats'``.
    """
    sql = (
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
        "AND table_name LIKE %s ORDER BY table_name"
    )
    rows = query(sql, (pattern,), timeout=timeout, conn=conn)
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Modular form full extraction (project #49)
# ---------------------------------------------------------------------------
#
# These accessors give comprehensive access to LMFDB classical-modular-form
# data without writing SQL. Each newform combines fields from
# ``mf_newforms`` (master record), ``mf_hecke_nf`` (Hecke eigenvalues over
# the coefficient field), ``mf_newform_portraits`` (portrait metadata),
# ``mf_twists_nf`` (twists / inner twists), ``modlgal_reps`` (mod-l Galois
# representations), ``mf_newspaces`` (dimension data), and ``char_dirichlet``
# (Dirichlet character orbits).
#
# Newform labels follow ``N.k.x.y``: level, weight, char-orbit-letter,
# hecke-orbit-letter (e.g. ``11.2.a.a`` is the rational newform on Gamma_0(11)).


# Cached schema column sets (lazy; populated on first use of newform_full).
# The cache avoids round-tripping ``information_schema`` for column lists
# every call.
_MF_SCHEMA_CACHE: dict[str, list[str]] = {}


def _cached_columns(
    table: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[str]:
    """Return cached column names for ``table`` (lazy schema discovery)."""
    if table in _MF_SCHEMA_CACHE:
        return _MF_SCHEMA_CACHE[table]
    cols = [c for c, _ in schema(table, conn=conn, timeout=timeout)]
    _MF_SCHEMA_CACHE[table] = cols
    return cols


def _validate_newform_label(label: str) -> tuple[int, int, str, str]:
    """Parse and validate an LMFDB newform label ``N.k.x.y``.

    Returns ``(level, weight, char_orbit_letter, hecke_orbit_letter)``.
    Raises ``ValueError`` on malformed input.
    """
    if not isinstance(label, str) or not label:
        raise ValueError(f"invalid newform label: {label!r} (must be non-empty string)")
    parts = label.split(".")
    if len(parts) != 4:
        raise ValueError(
            f"invalid newform label: {label!r} (expected 'N.k.x.y' with 4 dot-separated parts)"
        )
    try:
        level = int(parts[0])
        weight = int(parts[1])
    except ValueError as e:
        raise ValueError(
            f"invalid newform label: {label!r} (level and weight must be integers)"
        ) from e
    if level <= 0 or weight < 1:
        raise ValueError(
            f"invalid newform label: {label!r} (level must be positive, weight >= 1)"
        )
    if not parts[2] or not parts[3]:
        raise ValueError(f"invalid newform label: {label!r} (empty char/hecke orbit)")
    return level, weight, parts[2], parts[3]


# Default columns for newform_full. Pulled from mf_newforms; the heavy
# trace array is requested explicitly (we truncate at the call site).
_MF_NEWFORM_FULL_COLS = [
    "label",
    "level",
    "weight",
    "dim",
    "relative_dim",
    "char_orbit_index",
    "char_orbit_label",
    "char_conductor",
    "char_order",
    "char_parity",
    "char_is_real",
    "conrey_index",
    "analytic_rank",
    "analytic_rank_proved",
    "is_self_dual",
    "is_cm",
    "is_rm",
    "is_self_twist",
    "self_twist_type",
    "self_twist_discs",
    "cm_discs",
    "rm_discs",
    "sato_tate_group",
    "atkin_lehner_eigenvals",
    "atkin_lehner_string",
    "fricke_eigenval",
    "inner_twist_count",
    "inner_twists",
    "field_poly",
    "field_disc",
    "field_disc_factorization",
    "hecke_ring_index",
    "hecke_ring_index_proved",
    "trace_zratio",
    "trace_moments",
    "traces",
    "projective_image",
    "projective_image_type",
    "artin_image",
    "artin_degree",
    "related_objects",
    "level_radical",
    "level_primes",
    "level_is_prime",
    "level_is_prime_power",
    "level_is_squarefree",
    "nf_label",
    "Nk2",
    "weight_parity",
    "minimal_twist",
    "char_is_minimal",
]


def _atkin_lehner_to_dict(eigenvals: Optional[list]) -> dict[int, int]:
    """Convert LMFDB ``atkin_lehner_eigenvals`` list-of-pairs to a dict.

    LMFDB stores Atkin-Lehner data as a list of ``[prime, eigenvalue]``
    pairs (e.g. ``[[11, -1]]``). We convert to a normal Python dict
    ``{prime: ±1}``. Returns ``{}`` if the input is None or empty.
    """
    out: dict[int, int] = {}
    if not eigenvals:
        return out
    for entry in eigenvals:
        if entry is None or len(entry) < 2:
            continue
        try:
            p = int(entry[0])
            v = int(entry[1])
        except (TypeError, ValueError):
            continue
        out[p] = v
    return out


def newform_full(
    label: str,
    traces_truncate: int = 30,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> Optional[dict]:
    """Comprehensive newform record for an LMFDB modular-form label.

    Pulls from ``mf_newforms`` and ``mf_newform_portraits`` and joins
    ``mf_hecke_nf`` summary fields when present.

    Parameters
    ----------
    label : LMFDB newform label, e.g. ``"11.2.a.a"``.
    traces_truncate : Number of leading entries of the ``traces`` array to
        return (default 30). Pass ``None`` to return the full trace list.

    Returns
    -------
    dict with the following canonical keys (subset of LMFDB schema, plus
    a few derived fields):

    - ``label``, ``level``, ``weight``, ``dim``, ``relative_dim``
    - ``char_orbit_label``, ``char_orbit_index``, ``char_conductor``,
      ``char_order``, ``char_parity``, ``conrey_index``
    - ``traces`` (first ``traces_truncate`` entries of a_1, a_2, ...)
    - ``hecke_ring`` (dict: ``{poly, index, index_proved, rank, power_basis}``)
    - ``nontrivial_character`` (bool: True iff char_orbit_index > 1)
    - ``is_self_dual``, ``is_cm``, ``is_rm``, ``is_self_twist``
    - ``inner_twist_count``, ``inner_twists`` (raw list)
    - ``atkin_lehner`` (dict ``{prime: ±1}``), ``atkin_lehner_string``,
      ``fricke_eigenval``
    - ``sato_tate_group``
    - ``analytic_rank``, ``analytic_rank_proved``
    - ``projective_image``, ``projective_image_type``, ``artin_image``,
      ``artin_degree``
    - ``related_objects``, ``nf_label``
    - ``portrait_hecke_orbit`` (from ``mf_newform_portraits`` if present)

    Returns ``None`` if the label is not in ``mf_newforms``.

    Raises
    ------
    ValueError if the label is malformed.
    """
    _validate_newform_label(label)

    with _maybe_conn(conn, timeout) as c:
        # Single query against mf_newforms with the curated columns.
        cols = list(_MF_NEWFORM_FULL_COLS)
        col_sql = ", ".join(f'"{x}"' for x in cols)
        sql = f'SELECT {col_sql} FROM "mf_newforms" WHERE "label" = %s LIMIT 1'
        rows = query_dicts(sql, (label,), timeout=timeout, conn=c)
        if not rows:
            return None
        rec = rows[0]

        # Pull the matching mf_hecke_nf row (summary; not the full ap list)
        hecke_sql = (
            'SELECT "hecke_orbit_code", "hecke_ring_rank", "hecke_ring_power_basis", '
            '"hecke_ring_cyclotomic_generator", "maxp", "field_poly" '
            'FROM "mf_hecke_nf" WHERE "label" = %s LIMIT 1'
        )
        hecke_rows = query_dicts(hecke_sql, (label,), timeout=timeout, conn=c)
        hecke = hecke_rows[0] if hecke_rows else {}

        # Portrait (one row per (label, hecke_orbit) at most)
        portrait_sql = (
            'SELECT "hecke_orbit" FROM "mf_newform_portraits" '
            'WHERE "label" = %s LIMIT 1'
        )
        portrait_rows = query(portrait_sql, (label,), timeout=timeout, conn=c)
        portrait_hecke_orbit = (
            int(portrait_rows[0][0]) if portrait_rows else None
        )

    # Truncate traces (note: a_1 is implicit = 1; the LMFDB ``traces`` array
    # stores tr(a_1), tr(a_2), tr(a_3), ... starting at n=1).
    traces = rec.get("traces") or []
    if traces_truncate is not None and traces is not None:
        traces = list(traces)[: int(traces_truncate)]

    out = {
        "label": rec.get("label"),
        "level": rec.get("level"),
        "weight": rec.get("weight"),
        "dim": rec.get("dim"),
        "relative_dim": rec.get("relative_dim"),
        "char_orbit_index": rec.get("char_orbit_index"),
        "char_orbit_label": rec.get("char_orbit_label"),
        "char_conductor": rec.get("char_conductor"),
        "char_order": rec.get("char_order"),
        "char_parity": rec.get("char_parity"),
        "char_is_real": rec.get("char_is_real"),
        "conrey_index": rec.get("conrey_index"),
        "nontrivial_character": (rec.get("char_orbit_index") or 1) != 1,
        "traces": traces,
        "hecke_ring": {
            "poly": hecke.get("field_poly") or rec.get("field_poly"),
            "index": rec.get("hecke_ring_index"),
            "index_proved": rec.get("hecke_ring_index_proved"),
            "rank": hecke.get("hecke_ring_rank"),
            "power_basis": hecke.get("hecke_ring_power_basis"),
            "cyclotomic_generator": hecke.get("hecke_ring_cyclotomic_generator"),
            "maxp": hecke.get("maxp"),
            "orbit_code": hecke.get("hecke_orbit_code"),
        },
        "is_self_dual": rec.get("is_self_dual"),
        "is_cm": rec.get("is_cm"),
        "is_rm": rec.get("is_rm"),
        "is_self_twist": rec.get("is_self_twist"),
        "self_twist_type": rec.get("self_twist_type"),
        "self_twist_discs": rec.get("self_twist_discs"),
        "cm_discs": rec.get("cm_discs"),
        "rm_discs": rec.get("rm_discs"),
        "inner_twist_count": rec.get("inner_twist_count"),
        "inner_twists": rec.get("inner_twists"),
        "atkin_lehner": _atkin_lehner_to_dict(rec.get("atkin_lehner_eigenvals")),
        "atkin_lehner_eigenvals": rec.get("atkin_lehner_eigenvals"),
        "atkin_lehner_string": rec.get("atkin_lehner_string"),
        "fricke_eigenval": rec.get("fricke_eigenval"),
        "sato_tate_group": rec.get("sato_tate_group"),
        "analytic_rank": rec.get("analytic_rank"),
        "analytic_rank_proved": rec.get("analytic_rank_proved"),
        "projective_image": rec.get("projective_image"),
        "projective_image_type": rec.get("projective_image_type"),
        "artin_image": rec.get("artin_image"),
        "artin_degree": rec.get("artin_degree"),
        "related_objects": rec.get("related_objects"),
        "nf_label": rec.get("nf_label"),
        "field_disc": rec.get("field_disc"),
        "level_primes": rec.get("level_primes"),
        "level_radical": rec.get("level_radical"),
        "level_is_prime": rec.get("level_is_prime"),
        "level_is_squarefree": rec.get("level_is_squarefree"),
        "trace_zratio": rec.get("trace_zratio"),
        "minimal_twist": rec.get("minimal_twist"),
        "char_is_minimal": rec.get("char_is_minimal"),
        "portrait_hecke_orbit": portrait_hecke_orbit,
    }
    return out


# Cached prime list (first 1000 primes is enough; mf_hecke_nf stores ap
# up to maxp <= 997 typically).
def _primes_up_to(n: int) -> list[int]:
    """Return all primes <= n via a simple sieve. Cheap, no deps."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytes(len(sieve[i * i :: i]))
    return [i for i in range(2, n + 1) if sieve[i]]


def newform_hecke_eigenvalues_full(
    label: str,
    p_max: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> dict[int, list[int]]:
    """All stored Hecke eigenvalues a_p for primes p <= p_max.

    For dimension-1 newforms each value is a single Python int; for
    dim > 1 each value is a list of integers (power-basis coefficients
    in the Hecke ring's chosen basis).

    Parameters
    ----------
    label : LMFDB newform label.
    p_max : Inclusive upper bound on primes to return (default 1000).

    Returns
    -------
    dict mapping prime ``p`` -> ``a_p`` (int for dim=1, list[int] for dim>1).
    Empty dict if the newform is not in ``mf_hecke_nf`` or stores fewer ap.
    """
    _validate_newform_label(label)
    if p_max < 2:
        return {}

    sql = (
        'SELECT "ap", "maxp", "hecke_ring_rank" FROM "mf_hecke_nf" '
        'WHERE "label" = %s LIMIT 1'
    )
    rows = query(sql, (label,), timeout=timeout, conn=conn)
    if not rows:
        return {}
    ap, maxp, _rank = rows[0]
    if ap is None:
        return {}
    primes = _primes_up_to(min(int(p_max), int(maxp) if maxp else int(p_max)))
    out: dict[int, list[int]] = {}
    for i, p in enumerate(primes):
        if i >= len(ap):
            break
        v = ap[i]
        if isinstance(v, list) and len(v) == 1:
            out[p] = int(v[0])
        elif isinstance(v, list):
            out[p] = [int(x) for x in v]
        else:
            out[p] = v
    return out


def newform_character_orbit(
    label: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> Optional[dict]:
    """Galois orbit of the Dirichlet character attached to a newform.

    Looks up the character orbit by ``"<level>.<char_orbit_label>"`` in
    ``char_dirichlet``. Returns ``None`` if the newform or character orbit
    isn't present.
    """
    _validate_newform_label(label)
    nf = newform_full(label, traces_truncate=0, conn=conn, timeout=timeout)
    if nf is None:
        return None
    level = nf["level"]
    orbit_label = nf.get("char_orbit_label")
    if orbit_label is None:
        return None
    full_orbit_label = f"{level}.{orbit_label}"
    return dirichlet_character_orbit(
        full_orbit_label, conn=conn, timeout=timeout
    )


def newform_inner_twists(
    label: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[dict]:
    """Inner-twist (CM/self-twist) data for a newform.

    Returns the rows of ``mf_twists_nf`` whose ``source_label`` equals
    ``label``, plus the parsed ``inner_twists`` array from ``mf_newforms``.
    Each returned dict includes ``twisting_char_label``, ``target_label``,
    ``source_is_minimal``, ``self_twist_disc``, etc.
    """
    _validate_newform_label(label)
    sql = (
        'SELECT "source_label", "target_label", "twisting_char_label", '
        '"twist_class_label", "multiplicity", "parity", "weight", '
        '"source_char_orbit", "target_char_orbit", "twisting_char_orbit", '
        '"source_is_minimal", "target_is_minimal", "conductor", "order", '
        '"degree", "self_twist_disc" '
        'FROM "mf_twists_nf" WHERE "source_label" = %s'
    )
    return query_dicts(sql, (label,), timeout=timeout, conn=conn)


def newform_galois_representations(
    label: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[dict]:
    """Mod-l Galois representations referencing this newform.

    LMFDB does not store a direct (newform_label -> modlgal_rep) join;
    instead each ``modlgal_reps`` row carries a JSON ``related_objects``
    array that may include ``["MF", <newform_label>]``. We search by JSON
    containment and return the matching rep records.

    Returns a list of dicts (possibly empty) with keys ``label``,
    ``base_ring_characteristic``, ``dimension``, ``conductor``,
    ``image_type``, ``image_label``, ``is_irreducible``,
    ``is_absolutely_irreducible``, ``is_surjective``, ``related_objects``.
    """
    _validate_newform_label(label)
    cols = [
        "label",
        "base_ring_characteristic",
        "base_ring_order",
        "dimension",
        "conductor",
        "image_type",
        "image_label",
        "image_order",
        "is_irreducible",
        "is_absolutely_irreducible",
        "is_surjective",
        "is_solvable",
        "projective_type",
        "related_objects",
        "weight",
    ]
    col_sql = ", ".join(f'"{c}"' for c in cols)
    # Use JSONB containment ``@>`` for an indexable exact-match search.
    # related_objects in modlgal_reps is JSONB.
    sql = (
        f'SELECT {col_sql} FROM "modlgal_reps" '
        f'WHERE "related_objects" @> %s::jsonb'
    )
    # JSON literal: array containing the pair ["MF", label]
    import json as _json

    needle = _json.dumps([["MF", label]])
    return query_dicts(sql, (needle,), timeout=timeout, conn=conn)


def newforms_by_level_weight(
    level: int,
    weight: int,
    char_orbit: Optional[int] = None,
    columns: Optional[list[str]] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[dict]:
    """Sweep query: all newforms at a fixed (level, weight).

    Parameters
    ----------
    level, weight : Positive integers; level >= 1, weight >= 1.
    char_orbit : Optional ``char_orbit_index`` filter (1 = trivial).
    columns : Optional column override; defaults to the curated
        ``_MF_NEWFORMS_COLS`` plus a few fields useful for filtering.

    Raises
    ------
    ValueError if level < 1 or weight < 1.
    """
    if level < 1:
        raise ValueError(f"level must be >= 1, got {level}")
    if weight < 1:
        raise ValueError(f"weight must be >= 1, got {weight}")

    cols = (
        None
        if columns == ["*"]
        else (
            columns
            or _MF_NEWFORMS_COLS
            + ["analytic_rank", "atkin_lehner_eigenvals", "inner_twist_count"]
        )
    )
    sql, params = _build_select(
        "mf_newforms",
        cols,
        {"level": level, "weight": weight, "char_orbit_index": char_orbit},
        limit=limit,
    )
    return query_dicts(sql, params, timeout=timeout, conn=conn)


def newforms_by_dim(
    dim: int,
    level_max: int = 1000,
    weight: Optional[int] = None,
    limit: int = 1000,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> list[str]:
    """List labels of newforms with a given absolute dimension.

    Parameters
    ----------
    dim : Required dimension. Returns ``[]`` if dim < 1.
    level_max : Skip newforms with level > level_max (default 1000).
    weight : Optional weight filter.
    """
    if dim is None or dim < 1:
        return []
    extra: list[tuple[str, Any]] = []
    if level_max is not None:
        extra.append(('"level" <= %s', int(level_max)))
    sql, params = _build_select(
        "mf_newforms",
        ["label"],
        {"dim": int(dim), "weight": weight},
        extra_clauses=extra,
        limit=limit,
    )
    sql += ' ORDER BY "level", "weight", "char_orbit_index", "label"' if False else ""
    rows = query(sql, params, timeout=timeout, conn=conn)
    return [r[0] for r in rows]


def newform_dim_data(
    level_max: int = 100,
    weight_max: int = 12,
    cusp_only: bool = True,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> dict[tuple[int, int], int]:
    """Full dimension table for low (level, weight).

    Aggregates ``dim`` (newform-space dimension) over all character orbits
    in ``mf_newspaces``: the returned ``dict[(N, k)]`` is the total
    newform-cusp-form dimension for that level and weight, summed over
    Dirichlet character orbits.

    Parameters
    ----------
    level_max : Inclusive level cap (default 100).
    weight_max : Inclusive weight cap (default 12).
    cusp_only : If True (default), use the ``dim`` (newform-cusp) field;
        if False, use ``mf_dim`` (full M_k newform space dim).
    """
    field = "dim" if cusp_only else "mf_dim"
    sql = (
        f'SELECT "level", "weight", SUM("{field}")::bigint AS d '
        f'FROM "mf_newspaces" '
        f'WHERE "level" <= %s AND "weight" <= %s '
        f'GROUP BY "level", "weight" ORDER BY "level", "weight"'
    )
    rows = query(
        sql,
        (int(level_max), int(weight_max)),
        timeout=timeout,
        conn=conn,
    )
    return {(int(r[0]), int(r[1])): int(r[2] or 0) for r in rows}


def dirichlet_character_orbit(
    orbit_label: str,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> Optional[dict]:
    """Dirichlet-character Galois orbit by orbit label, e.g. ``"23.b"``.

    Returns ``None`` if the orbit is not in ``char_dirichlet``.
    Raises ``ValueError`` for an empty input.
    """
    if not orbit_label:
        raise ValueError("orbit_label must be a non-empty string")
    sql = 'SELECT * FROM "char_dirichlet" WHERE "label" = %s LIMIT 1'
    rows = query_dicts(sql, (orbit_label,), timeout=timeout, conn=conn)
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Generic helpers (continued)
# ---------------------------------------------------------------------------


def count(
    table_name: str,
    where: Optional[str] = None,
    params: Optional[Iterable[Any]] = None,
    conn: Optional[psycopg2.extensions.connection] = None,
    timeout: int = 10,
) -> int:
    """Fast row count.

    Notes
    -----
    Without a ``where`` clause this returns ``reltuples`` from
    ``pg_class`` (the planner's estimate) for very fast counting on huge
    tables. For exact counts pass ``where='TRUE'``.

    The ``where`` argument is interpolated raw into the SQL — only pass
    fixed strings under your control. Use ``%s`` placeholders inside it
    and supply values via ``params``.
    """
    if where is None:
        sql = (
            "SELECT reltuples::bigint FROM pg_class "
            "WHERE relname = %s AND relkind = 'r'"
        )
        rows = query(sql, (table_name,), timeout=timeout, conn=conn)
        if not rows:
            return 0
        return int(rows[0][0])

    sql = f'SELECT COUNT(*) FROM "{table_name}" WHERE {where}'
    rows = query(sql, list(params) if params else None, timeout=timeout, conn=conn)
    return int(rows[0][0]) if rows else 0


__all__ = [
    "LMFDBConnectionError",
    "connect",
    "probe",
    "query",
    "query_dicts",
    "elliptic_curves",
    "ec_mwbsd",
    "number_fields",
    "modular_forms",
    "lfunctions",
    "g2c_curves",
    "schema",
    "list_tables",
    "count",
    # Modular form full extraction (project #49)
    "newform_full",
    "newform_hecke_eigenvalues_full",
    "newform_character_orbit",
    "newform_inner_twists",
    "newform_galois_representations",
    "newforms_by_level_weight",
    "newforms_by_dim",
    "newform_dim_data",
    "dirichlet_character_orbit",
]
