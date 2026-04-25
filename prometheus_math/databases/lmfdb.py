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
]
