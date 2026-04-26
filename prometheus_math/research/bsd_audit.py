"""BSD-audit batch composer.

Composes the elliptic-curve BSD chain (regulator + conductor +
analytic_sha + selmer_2_rank + faltings_height + root_number) over a
list of curves and produces a per-curve consistency report.

This codifies the manual auditing pattern Charon used during the F011
session: for each curve, compute every BSD-relevant invariant, query
LMFDB for the curated value, and flag any disagreement above a
numerical tolerance.

Public API
----------
``run(curves, lmfdb_compare=True, parallel=False, timeout_s=30,
      tolerance=1e-6)``
    Audit a list of curves (LMFDB labels or 5-tuples of a-invariants).
    Returns one CSV-serialisable ``dict`` per curve.
``to_csv(audit_results, path)``
    Round-tripable CSV writer.
``summary(audit_results)``
    n_curves, n_consistent, n_inconsistent, mean_runtime_ms, top_outliers.
``filter_inconsistent(audit_results, tolerance=1e-6)``
    Records whose max absolute delta exceeds ``tolerance``.
``rank_consistency_check(label, lmfdb_rank=None)``
    Cheap subset: rank, parity, root number cross-check. Skips the
    heavy regulator / analytic_sha computation.

Conventions
-----------
* ``curves`` accepts a heterogeneous list. Each entry is either:
  - an LMFDB label (``str``, e.g. ``"11.a2"``), or
  - a length-5 list/tuple of ints (the a-invariants ``[a1,a2,a3,a4,a6]``).
* If ``lmfdb_compare`` is ``True`` and the entry is a label, the LMFDB
  row is fetched and used both as the reference for deltas AND as the
  source of ``rank_hint`` (faster ``analytic_sha`` for high-rank curves).
* ``deltas`` are computed as ``computed - lmfdb`` for floats,
  ``computed != lmfdb`` for ints/strings (stored as 0.0/1.0 sentinels
  to keep the dict CSV-flat).
* ``all_consistent`` is True iff every numeric delta is below
  ``tolerance`` AND every integer/parity check matches.

Per-curve runtime cap
---------------------
We use a worker-thread cap (the Python ``signal`` interface that GNU
agents use is unreliable on Windows). When the worker thread doesn't
return before ``timeout_s``, the audit dict is closed out with the
partial values that completed plus a ``"runtime_exceeded"`` warning.

Failure isolation
-----------------
- If one curve's ``ellrank`` blows the PARI stack, only that curve's
  audit is closed out as a failure; the rest of the batch continues.
- LMFDB rows are fetched lazily and any DB/network error is caught
  per-curve. The audit still runs the local-side computations.

Author: Techne — project #8 from techne/PROJECT_BACKLOG_1000.md.
Forged: 2026-04-25.
"""
from __future__ import annotations

import csv
import math
import threading
import time
import traceback
from typing import Any, Iterable, Optional, Sequence, Union

# Local arsenal imports — all already TDD-tested in techne/lib (see
# techne/TDD_LOG.md project #17).
from techne.lib.regulator import regulator as _regulator
from techne.lib.conductor import conductor as _conductor, global_reduction as _global_reduction
from techne.lib.root_number import root_number as _root_number
from techne.lib.analytic_sha import analytic_sha as _analytic_sha
from techne.lib.selmer_rank import selmer_2_rank as _selmer_2_rank
from techne.lib.faltings_height import faltings_height as _faltings_height

CurveSpec = Union[str, Sequence[int]]
"""Either an LMFDB label or a 5-tuple of a-invariants."""


__all__ = [
    "run",
    "to_csv",
    "summary",
    "filter_inconsistent",
    "rank_consistency_check",
    "BSDAuditError",
]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class BSDAuditError(RuntimeError):
    """Raised for malformed inputs that cannot even start the audit."""


# ---------------------------------------------------------------------------
# Lazy LMFDB import (don't pay the cost at import time)
# ---------------------------------------------------------------------------


def _lmfdb():
    """Return the prometheus_math.databases.lmfdb module, or None."""
    try:
        from prometheus_math.databases import lmfdb  # local import on purpose
        return lmfdb
    except Exception:  # pragma: no cover
        return None


# ---------------------------------------------------------------------------
# Curve-spec normalisation
# ---------------------------------------------------------------------------


def _is_label(spec: Any) -> bool:
    return isinstance(spec, str)


def _is_ainvs(spec: Any) -> bool:
    return (
        isinstance(spec, (list, tuple))
        and len(spec) == 5
        and all(isinstance(a, (int,)) or (isinstance(a, float) and float(a).is_integer())
                for a in spec)
    )


def _normalise_spec(spec: Any) -> tuple[Optional[str], Optional[list[int]]]:
    """Return (label, ainvs). At least one is non-None on success."""
    if _is_label(spec):
        return str(spec), None
    if _is_ainvs(spec):
        return None, [int(a) for a in spec]
    raise BSDAuditError(
        f"Unrecognised curve spec: {spec!r}. Expected an LMFDB label "
        f"(str like '11.a2') or a length-5 list of ints."
    )


def _resolve_ainvs(label: Optional[str], ainvs: Optional[list[int]],
                   lmfdb_row: Optional[dict]) -> Optional[list[int]]:
    """Pick the canonical ainvs for downstream local computation.

    Priority: explicit ainvs argument > LMFDB row's ainvs.
    Returns None if label is given but LMFDB lookup failed.
    """
    if ainvs is not None:
        return ainvs
    if lmfdb_row and "ainvs" in lmfdb_row and lmfdb_row["ainvs"]:
        return [int(a) for a in lmfdb_row["ainvs"]]
    return None


# ---------------------------------------------------------------------------
# Per-curve thread-bounded executor (default 30s cap)
# ---------------------------------------------------------------------------


def _run_with_timeout(fn, args=(), kwargs=None, timeout_s: float = 30.0):
    """Run ``fn(*args, **kwargs)`` in a daemon thread, return value or
    raise ``TimeoutError``. Exceptions inside fn are re-raised in the
    caller thread.

    Note: the worker is a daemon thread; if it stalls in PARI we simply
    abandon it. PARI is process-global so a stuck worker may interfere
    with subsequent calls — caller should consider restarting the
    process if many timeouts occur.
    """
    if kwargs is None:
        kwargs = {}
    out: dict[str, Any] = {"v": None, "err": None}

    def _target():
        try:
            out["v"] = fn(*args, **kwargs)
        except BaseException as e:  # noqa: BLE001 — capture for caller
            out["err"] = e

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        raise TimeoutError(f"computation exceeded {timeout_s}s cap")
    if out["err"] is not None:
        raise out["err"]
    return out["v"]


# ---------------------------------------------------------------------------
# LMFDB row fetching (per-curve, swallow errors)
# ---------------------------------------------------------------------------


def _fetch_lmfdb(label: str) -> tuple[Optional[dict], Optional[dict], list[str]]:
    """Return (ec_curvedata_row, ec_mwbsd_row, warnings)."""
    warnings: list[str] = []
    mod = _lmfdb()
    if mod is None:
        warnings.append("lmfdb_module_unavailable")
        return None, None, warnings
    try:
        rows = mod.elliptic_curves(label=label, columns=["*"])
        cd = rows[0] if rows else None
    except Exception as e:  # noqa: BLE001
        cd = None
        warnings.append(f"ec_curvedata_query_failed:{type(e).__name__}")
    try:
        mwbsd = mod.ec_mwbsd(label)
    except Exception as e:  # noqa: BLE001
        mwbsd = None
        warnings.append(f"ec_mwbsd_query_failed:{type(e).__name__}")
    if cd is None and mwbsd is None:
        warnings.append("lmfdb_row_missing")
    return cd, mwbsd, warnings


# ---------------------------------------------------------------------------
# The single-curve audit
# ---------------------------------------------------------------------------


_FLOAT_FIELDS = ("regulator", "faltings_height", "analytic_sha")
_INT_FIELDS = ("conductor", "rank", "root_number", "selmer_2_rank",
               "tamagawa_product", "torsion_order")


def _audit_one(spec: CurveSpec,
               lmfdb_compare: bool,
               timeout_s: float,
               tolerance: float) -> dict:
    """Audit a single curve. Returns a CSV-flat dict.

    Output keys (all simple types):
        label, ainvs (str-encoded list), ainvs_source,
        regulator, conductor, root_number, analytic_sha, selmer_2_rank,
        faltings_height, tamagawa_product, rank, torsion_order,
        lmfdb_regulator, lmfdb_conductor, lmfdb_root_number,
        lmfdb_analytic_sha, lmfdb_faltings_height, lmfdb_tamagawa_product,
        lmfdb_rank, lmfdb_torsion_order,
        delta_regulator, delta_conductor, delta_root_number,
        delta_analytic_sha, delta_faltings_height, delta_tamagawa_product,
        delta_rank, delta_torsion_order,
        bsd_residual, all_consistent, warnings, runtime_ms,
        parity_ok
    """
    t_start = time.perf_counter()
    warnings: list[str] = []
    try:
        label, ainvs = _normalise_spec(spec)
    except BSDAuditError as e:
        return _empty_result(spec, [f"input_error:{e}"], t_start)

    # ---- LMFDB lookup (lazy, swallow errors) ----
    cd_row: Optional[dict] = None
    mwbsd_row: Optional[dict] = None
    if lmfdb_compare and label is not None:
        cd_row, mwbsd_row, db_warnings = _fetch_lmfdb(label)
        warnings.extend(db_warnings)

    # If we only had a label, we need ainvs from LMFDB to compute
    if ainvs is None:
        ainvs = _resolve_ainvs(label, None, cd_row)
        if ainvs is None:
            return _empty_result(
                {"label": label}, warnings + ["ainvs_unresolvable"], t_start
            )
        ainvs_source = "lmfdb"
    else:
        ainvs_source = "input"

    rank_hint = None
    if cd_row is not None and "rank" in cd_row and cd_row["rank"] is not None:
        rank_hint = int(cd_row["rank"])

    # ---- Local computations under timeout ----
    computed: dict[str, Any] = {
        "regulator": None,
        "conductor": None,
        "root_number": None,
        "analytic_sha": None,
        "rank": None,
        "tamagawa_product": None,
        "torsion_order": None,
        "selmer_2_rank": None,
        "faltings_height": None,
    }

    def _try(key, fn, *args, **kwargs):
        try:
            computed[key] = _run_with_timeout(
                fn, args=args, kwargs=kwargs, timeout_s=timeout_s
            )
        except TimeoutError:
            warnings.append(f"{key}_runtime_exceeded")
        except Exception as e:  # noqa: BLE001 — capture per-tool failure
            warnings.append(f"{key}_failed:{type(e).__name__}")

    # global_reduction supplies conductor + tamagawa_product cheaply.
    try:
        glob = _run_with_timeout(_global_reduction, args=(ainvs,),
                                 timeout_s=timeout_s)
        computed["conductor"] = int(glob["conductor"])
        computed["tamagawa_product"] = int(glob["tamagawa_product"])
    except TimeoutError:
        warnings.append("global_reduction_runtime_exceeded")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"global_reduction_failed:{type(e).__name__}")

    _try("root_number", _root_number, ainvs)

    # analytic_sha is the most expensive call; pass rank_hint when known.
    try:
        sha = _run_with_timeout(
            _analytic_sha, args=(ainvs,), kwargs={"rank_hint": rank_hint},
            timeout_s=timeout_s,
        )
        computed["analytic_sha"] = float(sha["value"])
        computed["rank"] = int(sha["rank"])
        computed["torsion_order"] = int(sha["tors"])
        # regulator already inside analytic_sha; reuse for free.
        if computed["regulator"] is None:
            computed["regulator"] = float(sha["Reg"])
    except TimeoutError:
        warnings.append("analytic_sha_runtime_exceeded")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"analytic_sha_failed:{type(e).__name__}")

    # selmer_2_rank — independent ellrank call; respects per-curve cap.
    _try("selmer_2_rank", _selmer_2_rank, ainvs)
    _try("faltings_height", _faltings_height, ainvs)

    # If analytic_sha didn't run (e.g. timeout), fall back to a direct
    # regulator call — useful for partial reports.
    if computed["regulator"] is None:
        _try("regulator", _regulator, ainvs)

    # ---- Pull LMFDB-curated reference values ----
    lmfdb_vals: dict[str, Any] = {}
    if cd_row is not None:
        lmfdb_vals.update({
            "regulator": _to_float(cd_row.get("regulator")),
            "conductor": _to_int(cd_row.get("conductor")),
            "rank": _to_int(cd_row.get("rank")),
            "faltings_height": _to_float(cd_row.get("faltings_height")),
            "torsion_order": _to_int(cd_row.get("torsion")),
            "analytic_sha": _to_float(cd_row.get("sha")),
        })
    if mwbsd_row is not None:
        lmfdb_vals.setdefault("tamagawa_product",
                              _to_int(mwbsd_row.get("tamagawa_product")))
    # LMFDB doesn't store root_number directly on ec_curvedata; compute
    # from analytic_rank parity if available (parity conjecture).
    if cd_row is not None and "analytic_rank" in cd_row:
        ar = cd_row.get("analytic_rank")
        if ar is not None:
            lmfdb_vals["root_number"] = (-1) ** int(ar)

    # ---- Deltas ----
    deltas: dict[str, float] = {}
    for k in _FLOAT_FIELDS:
        c, l = computed.get(k), lmfdb_vals.get(k)
        if c is not None and l is not None:
            try:
                # Sha is computed as a float that should round to int;
                # compare to the LMFDB-curated integer Sha by rounding.
                if k == "analytic_sha":
                    deltas[k] = float(round(c) - l)
                else:
                    deltas[k] = float(c) - float(l)
            except Exception:  # noqa: BLE001
                deltas[k] = float("nan")
    for k in _INT_FIELDS:
        c, l = computed.get(k), lmfdb_vals.get(k)
        if c is not None and l is not None:
            deltas[k] = float(int(c) - int(l))

    # ---- BSD residual: assembled BSD value vs LMFDB-curated Sha ----
    bsd_residual: Optional[float] = None
    if (computed["analytic_sha"] is not None
            and lmfdb_vals.get("analytic_sha") is not None):
        try:
            bsd_residual = float(computed["analytic_sha"]) - float(
                lmfdb_vals["analytic_sha"]
            )
        except Exception:  # noqa: BLE001
            bsd_residual = None

    # ---- Parity check (rank parity vs root number) ----
    parity_ok: Optional[bool] = None
    if computed["rank"] is not None and computed["root_number"] is not None:
        parity_ok = ((-1) ** int(computed["rank"])) == int(computed["root_number"])

    # ---- Consistency verdict ----
    all_consistent = _verdict(deltas, parity_ok, tolerance)

    runtime_ms = (time.perf_counter() - t_start) * 1000.0
    out: dict[str, Any] = {
        "label": label or "",
        "ainvs": str(list(ainvs)),
        "ainvs_source": ainvs_source,
        # Computed
        "regulator": computed["regulator"],
        "conductor": computed["conductor"],
        "root_number": computed["root_number"],
        "analytic_sha": computed["analytic_sha"],
        "selmer_2_rank": computed["selmer_2_rank"],
        "faltings_height": computed["faltings_height"],
        "tamagawa_product": computed["tamagawa_product"],
        "rank": computed["rank"],
        "torsion_order": computed["torsion_order"],
        # LMFDB reference
        "lmfdb_regulator": lmfdb_vals.get("regulator"),
        "lmfdb_conductor": lmfdb_vals.get("conductor"),
        "lmfdb_root_number": lmfdb_vals.get("root_number"),
        "lmfdb_analytic_sha": lmfdb_vals.get("analytic_sha"),
        "lmfdb_faltings_height": lmfdb_vals.get("faltings_height"),
        "lmfdb_tamagawa_product": lmfdb_vals.get("tamagawa_product"),
        "lmfdb_rank": lmfdb_vals.get("rank"),
        "lmfdb_torsion_order": lmfdb_vals.get("torsion_order"),
        # Deltas (only those we could compute)
        "delta_regulator": deltas.get("regulator"),
        "delta_conductor": deltas.get("conductor"),
        "delta_root_number": deltas.get("root_number"),
        "delta_analytic_sha": deltas.get("analytic_sha"),
        "delta_faltings_height": deltas.get("faltings_height"),
        "delta_tamagawa_product": deltas.get("tamagawa_product"),
        "delta_rank": deltas.get("rank"),
        "delta_torsion_order": deltas.get("torsion_order"),
        # Verdicts
        "bsd_residual": bsd_residual,
        "parity_ok": parity_ok,
        "all_consistent": all_consistent,
        # Diagnostics
        "warnings": ";".join(warnings),
        "runtime_ms": runtime_ms,
    }
    return out


def _empty_result(spec_or_label: Any, warnings: list[str],
                  t_start: float) -> dict:
    """Produce a minimal failure record (still CSV-flat)."""
    label = ""
    ainvs_str = ""
    if isinstance(spec_or_label, dict):
        label = spec_or_label.get("label", "") or ""
    elif isinstance(spec_or_label, str):
        label = spec_or_label
    elif isinstance(spec_or_label, (list, tuple)):
        ainvs_str = str(list(spec_or_label))
    runtime_ms = (time.perf_counter() - t_start) * 1000.0
    out = {k: None for k in (
        "regulator", "conductor", "root_number", "analytic_sha",
        "selmer_2_rank", "faltings_height", "tamagawa_product",
        "rank", "torsion_order",
        "lmfdb_regulator", "lmfdb_conductor", "lmfdb_root_number",
        "lmfdb_analytic_sha", "lmfdb_faltings_height",
        "lmfdb_tamagawa_product", "lmfdb_rank", "lmfdb_torsion_order",
        "delta_regulator", "delta_conductor", "delta_root_number",
        "delta_analytic_sha", "delta_faltings_height",
        "delta_tamagawa_product", "delta_rank", "delta_torsion_order",
        "bsd_residual", "parity_ok",
    )}
    out.update({
        "label": label,
        "ainvs": ainvs_str,
        "ainvs_source": "input" if ainvs_str else "unknown",
        "all_consistent": False,
        "warnings": ";".join(warnings),
        "runtime_ms": runtime_ms,
    })
    return out


def _verdict(deltas: dict[str, float], parity_ok: Optional[bool],
             tolerance: float) -> bool:
    """Aggregate consistency verdict.

    True iff every available delta is within tolerance AND parity_ok
    isn't actively False. (Parity unknown => not penalised.)
    """
    if parity_ok is False:
        return False
    if not deltas:
        return False
    for k, d in deltas.items():
        if d is None or (isinstance(d, float) and math.isnan(d)):
            return False
        if abs(d) > tolerance:
            return False
    return True


def _to_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run(curves: Iterable[CurveSpec],
        lmfdb_compare: bool = True,
        parallel: bool = False,
        timeout_s: float = 30.0,
        tolerance: float = 1e-6) -> list[dict]:
    """Audit a batch of elliptic curves.

    Parameters
    ----------
    curves : iterable of curve specs
        Each entry is an LMFDB label (``str``) or a length-5 list of
        ints (``[a1, a2, a3, a4, a6]``).
    lmfdb_compare : bool, default True
        If True, fetch the LMFDB-curated row and compute deltas.
        Failures (network, missing label) are swallowed per-curve and
        recorded in ``warnings``.
    parallel : bool, default False
        Reserved for future thread-pool dispatch. PARI is process-global
        and not thread-safe in our cypari build, so this is currently a
        no-op (the audit runs sequentially). The flag is plumbed so
        callers can opt in once a concurrent backend is in place.
    timeout_s : float, default 30.0
        Per-curve runtime cap (in seconds). When a single tool exceeds
        this, that field stays ``None`` and a ``"<tool>_runtime_exceeded"``
        warning is appended; the rest of the audit continues.
    tolerance : float, default 1e-6
        Numerical tolerance for the per-field deltas. Used by
        ``all_consistent``.

    Returns
    -------
    list[dict] — one CSV-flat dict per curve.
    """
    curves = list(curves)
    if not curves:
        return []
    results: list[dict] = []
    for spec in curves:
        try:
            res = _audit_one(spec, lmfdb_compare=lmfdb_compare,
                             timeout_s=timeout_s, tolerance=tolerance)
        except Exception:  # noqa: BLE001 — total fence, no curve should
            #                       crash the whole batch.
            tb = traceback.format_exc(limit=2)
            res = _empty_result(spec, [f"audit_uncaught:{tb.splitlines()[-1]}"],
                                time.perf_counter())
        results.append(res)
    return results


_CSV_FIELDS = [
    "label", "ainvs", "ainvs_source",
    "regulator", "conductor", "root_number", "analytic_sha",
    "selmer_2_rank", "faltings_height", "tamagawa_product",
    "rank", "torsion_order",
    "lmfdb_regulator", "lmfdb_conductor", "lmfdb_root_number",
    "lmfdb_analytic_sha", "lmfdb_faltings_height",
    "lmfdb_tamagawa_product", "lmfdb_rank", "lmfdb_torsion_order",
    "delta_regulator", "delta_conductor", "delta_root_number",
    "delta_analytic_sha", "delta_faltings_height",
    "delta_tamagawa_product", "delta_rank", "delta_torsion_order",
    "bsd_residual", "parity_ok", "all_consistent",
    "warnings", "runtime_ms",
]


def to_csv(audit_results: list[dict], path: str) -> None:
    """Write audit results to a CSV file (overwrites).

    The on-disk schema is the union of every dict's keys, ordered by
    ``_CSV_FIELDS``. Empty cells are left as the empty string.
    """
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in audit_results:
            row = {k: ("" if r.get(k) is None else r.get(k)) for k in _CSV_FIELDS}
            writer.writerow(row)


def _max_abs_delta(record: dict) -> float:
    """Max |delta| across the numeric delta fields. NaN if no deltas."""
    vals: list[float] = []
    for k in record:
        if k.startswith("delta_") and record[k] is not None:
            try:
                v = abs(float(record[k]))
                if not math.isnan(v):
                    vals.append(v)
            except (TypeError, ValueError):
                pass
    return max(vals) if vals else float("nan")


def summary(audit_results: list[dict]) -> dict:
    """Aggregate counts + descriptive stats over a result list."""
    n = len(audit_results)
    if n == 0:
        return {
            "n_curves": 0,
            "n_consistent": 0,
            "n_inconsistent": 0,
            "mean_runtime_ms": 0.0,
            "top_outliers": [],
        }
    n_consistent = sum(1 for r in audit_results if r.get("all_consistent"))
    n_inconsistent = n - n_consistent
    runtimes = [float(r.get("runtime_ms") or 0.0) for r in audit_results]
    mean_rt = sum(runtimes) / n
    # Top outliers: largest max-abs-delta first, ties by label.
    scored = [(r, _max_abs_delta(r)) for r in audit_results]
    scored.sort(
        key=lambda rs: (-rs[1] if not math.isnan(rs[1]) else -float("inf"),
                        rs[0].get("label", "")),
    )
    top = []
    for r, score in scored[:5]:
        if math.isnan(score):
            continue
        top.append({
            "label": r.get("label", ""),
            "ainvs": r.get("ainvs", ""),
            "max_abs_delta": score,
            "all_consistent": r.get("all_consistent", False),
        })
    return {
        "n_curves": n,
        "n_consistent": n_consistent,
        "n_inconsistent": n_inconsistent,
        "mean_runtime_ms": mean_rt,
        "top_outliers": top,
    }


def filter_inconsistent(audit_results: list[dict],
                        tolerance: float = 1e-6) -> list[dict]:
    """Records whose ``max |delta|`` exceeds ``tolerance``.

    Records with no available deltas are excluded (we can't claim
    inconsistency without a reference).
    """
    out = []
    for r in audit_results:
        m = _max_abs_delta(r)
        if math.isnan(m):
            continue
        if m > tolerance:
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# Cheap subset — just rank + parity + root number
# ---------------------------------------------------------------------------


def rank_consistency_check(label: str,
                           lmfdb_rank: Optional[int] = None,
                           timeout_s: float = 30.0) -> dict:
    """Rank/parity/root-number subset of the audit.

    Skips regulator + analytic_sha + selmer + faltings for speed. Useful
    when the full audit is too slow on pathological curves (e.g. very
    high-conductor where ``ellanalyticrank`` would take minutes).

    Parameters
    ----------
    label : str
        LMFDB curve label.
    lmfdb_rank : int, optional
        Override the LMFDB rank lookup. If neither this nor LMFDB
        provides a rank, the parity check is reported as ``None`` and
        ``rank_consistent`` is ``False``.
    timeout_s : float, default 30
        Per-tool runtime cap (root_number is fast; conductor is fast).

    Returns
    -------
    dict with keys
        label, ainvs, conductor, root_number, lmfdb_rank,
        rank_parity_ok (bool|None), rank_consistent (bool), warnings,
        runtime_ms.
    """
    t_start = time.perf_counter()
    warnings: list[str] = []

    cd_row, _, db_warnings = _fetch_lmfdb(label)
    warnings.extend(db_warnings)

    ainvs = None
    if cd_row is not None and cd_row.get("ainvs") is not None:
        ainvs = [int(a) for a in cd_row["ainvs"]]
    else:
        warnings.append("ainvs_unresolvable")
        return {
            "label": label,
            "ainvs": "",
            "conductor": None,
            "root_number": None,
            "lmfdb_rank": lmfdb_rank,
            "rank_parity_ok": None,
            "rank_consistent": False,
            "warnings": ";".join(warnings),
            "runtime_ms": (time.perf_counter() - t_start) * 1000.0,
        }

    # rank source: explicit > LMFDB row
    rank_to_use = lmfdb_rank
    if rank_to_use is None and cd_row is not None and cd_row.get("rank") is not None:
        rank_to_use = int(cd_row["rank"])

    cond = None
    rn = None
    try:
        cond = int(_run_with_timeout(_conductor, args=(ainvs,),
                                     timeout_s=timeout_s))
    except TimeoutError:
        warnings.append("conductor_runtime_exceeded")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"conductor_failed:{type(e).__name__}")

    try:
        rn = int(_run_with_timeout(_root_number, args=(ainvs,),
                                   timeout_s=timeout_s))
    except TimeoutError:
        warnings.append("root_number_runtime_exceeded")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"root_number_failed:{type(e).__name__}")

    parity_ok: Optional[bool] = None
    if rn is not None and rank_to_use is not None:
        parity_ok = ((-1) ** int(rank_to_use)) == int(rn)

    # Cross-check conductor against LMFDB
    conductor_consistent = True
    if cond is not None and cd_row is not None and cd_row.get("conductor") is not None:
        if int(cond) != int(cd_row["conductor"]):
            conductor_consistent = False
            warnings.append("conductor_disagrees_with_lmfdb")

    rank_consistent = (parity_ok is True) and conductor_consistent and (rn is not None)

    return {
        "label": label,
        "ainvs": str(ainvs),
        "conductor": cond,
        "root_number": rn,
        "lmfdb_rank": rank_to_use,
        "rank_parity_ok": parity_ok,
        "rank_consistent": rank_consistent,
        "warnings": ";".join(warnings),
        "runtime_ms": (time.perf_counter() - t_start) * 1000.0,
    }
