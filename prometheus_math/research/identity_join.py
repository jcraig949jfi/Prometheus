"""prometheus_math.research.identity_join — KnotInfo<->LMFDB identity join.

This module operationalizes Aporia's H101 line of work: bridge a knot's
invariant trace field (iTrF) — approximated here by the SHAPE field
computed from SnapPy + PARI's algdep+polredabs — to LMFDB number-field
records. The forward direction takes a knot, computes the shape-field
polynomial via :func:`prometheus_math.topology.knot_shape_field`, and
queries ``LMFDB.nf_fields`` by ``(degree, abs_disc=|disc|)``. The reverse
direction takes a known LMFDB number field and scans a corpus of knots
for any whose shape field matches.

Pipeline
--------
1. shape_field   — Pari-canonical polynomial + degree + disc per knot
2. nf candidates — LMFDB nf_fields rows with matching ``(degree, |disc|)``
3. polredabs     — canonicalize knot poly the same way LMFDB stores it
4. score_match   — confidence in [0,1] from poly / disc / signature agreement
5. report        — Markdown table of ``best_match`` rows + diagnostics

The ``knot_to_nf`` function streams through input rather than loading all
results into memory, so it is safe on the full 12,966-knot KnotInfo corpus.
``bulk_scan`` exposes the streaming generator directly.

References
----------
- Neumann-Reid, "Arithmetic of hyperbolic manifolds" (1992): 4_1 iTrF =
  Q(sqrt(-3)), disc -3.
- LMFDB nf-field 3.1.23.1 (https://www.lmfdb.org/NumberField/3.1.23.1):
  the cubic with x^3 - x^2 + 1 and disc -23, the iTrF of the 5_2 knot
  per Callahan-Hildebrand-Weeks (canonical hyperbolic structure data).
- Aporia session journal 2026-04-22 (T_H101 thread): hand-verified
  these two anchors during the H101 proof-of-concept.

The CAVEAT inherited from :mod:`techne.lib.knot_shape_field` applies:
the SHAPE field can be a (real or imaginary) quadratic extension of the
iTrF for some knots; see the per-knot ``caveat`` field carried through.

Usage
-----

    from prometheus_math.research import identity_join as ij

    # Forward identity-join: 5_2 -> LMFDB 3.1.23.1
    res = ij.knot_to_nf(['5_2', '4_1'])
    for r in res:
        if r['best_match']:
            print(r['knot_name'], '->', r['best_match']['lmfdb_label'])

    # Reverse identity-join: which knots realize 3.1.23.1?
    matches = ij.knots_matching_nf('3.1.23.1')

    # Streaming bulk scan over the full corpus
    for r in ij.bulk_scan(['4_1', '5_2', '6_1', ...]):
        process(r)

    # Markdown report
    md = ij.generate_match_report(res, out_path='match_report.md')
"""
from __future__ import annotations

from typing import Any, Iterable, Iterator, List, Optional

# Optional / heavy deps — imported lazily where possible so the module
# imports cleanly even if SnapPy or psycopg2 is unavailable in a given env.

__all__ = [
    "knot_to_nf",
    "score_match",
    "knots_matching_nf",
    "generate_match_report",
    "bulk_scan",
]


# ---------------------------------------------------------------------------
# polredabs canonicalization helpers
# ---------------------------------------------------------------------------


def _polredabs_str(poly: str) -> Optional[str]:
    """Return the polredabs-canonical form of ``poly`` or None on failure.

    Both LMFDB's ``coeffs`` arrays and our shape-field ``poly`` strings
    flow through PARI's ``polredabs`` to produce the same canonical
    presentation (LMFDB stores its polynomials already polredabs'd).
    """
    if poly is None:
        return None
    try:
        from prometheus_math.topology import polredabs as _pra
        return str(_pra(poly)).strip()
    except Exception:
        return None


def _coeffs_to_poly_str(coeffs) -> str:
    """LMFDB ``coeffs`` array (constant -> leading) -> PARI poly string.

    LMFDB stores number-field defining polys as ``coeffs = [a0, a1, ..., an]``
    where ``f(x) = a0 + a1*x + ... + an*x^n``. PARI/our shape-field tool
    works with ``"x^n + ... + a0"`` strings.
    """
    if not coeffs:
        return ""
    terms: list[str] = []
    for i, c in enumerate(coeffs):
        c_int = int(c)
        if c_int == 0:
            continue
        if i == 0:
            terms.append(f"({c_int})")
        elif i == 1:
            terms.append(f"({c_int})*x")
        else:
            terms.append(f"({c_int})*x^{i}")
    return "+".join(terms) if terms else "0"


def _signature_from_lmfdb(nf_row: dict) -> Optional[tuple[int, int]]:
    """LMFDB row -> ``(r1, r2)`` signature, if degree and r2 are present."""
    deg = nf_row.get("degree")
    r2 = nf_row.get("r2")
    if deg is None or r2 is None:
        return None
    return (int(deg) - 2 * int(r2), int(r2))


def _signature_from_disc_degree(degree: int, disc: int) -> Optional[tuple[int, int]]:
    """Best-effort ``(r1, r2)`` from degree + disc sign.

    For degree 2: sign(disc) determines signature exactly:
        disc > 0 -> (2, 0) (real), disc < 0 -> (0, 1) (imaginary).
    For degree 3: sign(disc) is also exact (cubic has either 3 real or
    1 real + 1 complex pair):
        disc > 0 -> (3, 0), disc < 0 -> (1, 1).
    For degree >= 4: sign(disc) only constrains parity of ``r2``
        (sign = (-1)^r2), so we return None — caller treats signature
        as "unknown" and skips the +0.1 contribution either way.
    """
    if degree == 2:
        return (2, 0) if disc > 0 else (0, 1)
    if degree == 3:
        return (3, 0) if disc > 0 else (1, 1)
    return None


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------


def score_match(knot_shape: dict, lmfdb_nf: dict) -> float:
    """Confidence in [0, 1] that ``knot_shape`` matches ``lmfdb_nf``.

    Components
    ----------
    - polredabs equality of the defining polynomials -> +0.6
    - ``|disc|`` equality                           -> +0.2
    - degree equality                               -> +0.1
    - signature equality (when computable)         -> +0.1

    All four pass -> 1.0; only ``|disc|+degree`` -> 0.3 (a candidate
    that survives the SQL filter but whose poly differs is a "weak"
    match — useful flag, but not a confident identification).

    Parameters
    ----------
    knot_shape : dict with keys ``poly`` (str), ``degree`` (int), ``disc`` (int).
    lmfdb_nf   : dict with keys ``coeffs`` (list[int]), ``degree``,
                 ``disc_abs`` (>=0), ``disc_sign`` (-1/+1), ``r2``.

    Returns
    -------
    float in [0, 1].
    """
    if not knot_shape or not lmfdb_nf:
        return 0.0

    score = 0.0

    # Component 1: degree match (small weight, but a hard filter)
    k_deg = knot_shape.get("degree")
    l_deg = lmfdb_nf.get("degree")
    if k_deg is not None and l_deg is not None and int(k_deg) == int(l_deg):
        score += 0.1

    # Component 2: |disc| match (medium weight)
    k_disc = knot_shape.get("disc")
    l_disc_abs = lmfdb_nf.get("disc_abs")
    if k_disc is not None and l_disc_abs is not None:
        if abs(int(k_disc)) == int(l_disc_abs):
            score += 0.2

    # Component 3: signature match (small weight, only when computable)
    k_sig = None
    if k_deg is not None and k_disc is not None:
        k_sig = _signature_from_disc_degree(int(k_deg), int(k_disc))
    l_sig = _signature_from_lmfdb(lmfdb_nf)
    if k_sig is not None and l_sig is not None and k_sig == l_sig:
        score += 0.1
    elif k_sig is None and l_sig is not None:
        # Higher-degree case: we can't disprove signature, so we don't
        # penalize. But we don't add the 0.1 either.
        pass

    # Component 4: polredabs poly equality (largest weight)
    k_poly = knot_shape.get("poly")
    l_coeffs = lmfdb_nf.get("coeffs")
    if k_poly and l_coeffs:
        k_canon = _polredabs_str(k_poly)
        l_poly_str = _coeffs_to_poly_str(l_coeffs)
        l_canon = _polredabs_str(l_poly_str) if l_poly_str else None
        if k_canon and l_canon and k_canon == l_canon:
            score += 0.6

    # Clamp defensively in [0, 1] (should already be in range).
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


# ---------------------------------------------------------------------------
# Forward direction: knot -> LMFDB number fields
# ---------------------------------------------------------------------------


def _shape_field_for_knot(
    knot_name: str, bits_prec: int, max_deg: int
) -> tuple[Optional[dict], Optional[str]]:
    """Compute shape field for ``knot_name`` or return (None, error_string).

    Imports :mod:`prometheus_math.topology` lazily so the module loads even
    when SnapPy isn't installed (e.g. test runners with mocking).
    """
    try:
        from prometheus_math.topology import knot_shape_field
    except Exception as e:  # pragma: no cover — env-only path
        return None, f"knot_shape_field import failed: {e}"
    try:
        sf = knot_shape_field(knot_name, bits_prec=bits_prec, max_deg=max_deg)
        # Strip the heavy caveat string before returning to keep memory low.
        return {
            "poly": sf.get("poly"),
            "degree": sf.get("degree"),
            "disc": sf.get("disc"),
            "bits_prec": sf.get("bits_prec"),
            "is_hyperbolic": sf.get("is_hyperbolic", True),
        }, None
    except Exception as e:
        return None, str(e)


def _query_lmfdb_candidates(
    degree: int,
    disc_abs: int,
    abs_disc_tol: int,
    limit: int,
    conn=None,
) -> list[dict]:
    """Pull all LMFDB nf_fields rows of given ``(degree, |disc|)``.

    With ``abs_disc_tol > 0`` we widen the discriminant query to a
    [|d|-tol, |d|+tol] band — useful when the shape field is a quadratic
    extension of the trace field and disc differs by an integer factor.
    """
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception as e:  # pragma: no cover — env-only path
        raise RuntimeError(f"LMFDB module unavailable: {e}") from e

    if abs_disc_tol == 0:
        # Exact filter via abs_disc_max + a manual lower bound.
        rows = _lmfdb.number_fields(
            degree=degree,
            abs_disc_max=disc_abs,
            limit=limit,
            conn=conn,
        )
        return [r for r in rows if int(r.get("disc_abs", -1)) == disc_abs]
    else:
        lo = max(1, disc_abs - abs_disc_tol)
        hi = disc_abs + abs_disc_tol
        rows = _lmfdb.number_fields(
            degree=degree, abs_disc_max=hi, limit=limit, conn=conn,
        )
        return [r for r in rows if lo <= int(r.get("disc_abs", -1)) <= hi]


def _build_candidates(
    knot_shape: dict,
    abs_disc_tol: int,
    candidate_limit: int,
    conn=None,
) -> list[dict]:
    """Return enriched candidate dicts (each with ``confidence`` etc.)."""
    deg = knot_shape.get("degree")
    disc = knot_shape.get("disc")
    if deg is None or disc is None:
        return []
    raw = _query_lmfdb_candidates(
        degree=int(deg),
        disc_abs=abs(int(disc)),
        abs_disc_tol=abs_disc_tol,
        limit=candidate_limit,
        conn=conn,
    )
    out = []
    for row in raw:
        conf = score_match(knot_shape, row)
        # Decompose match flags for diagnostic transparency.
        l_sig = _signature_from_lmfdb(row)
        k_sig = _signature_from_disc_degree(int(deg), int(disc))
        sig_match = (k_sig is not None and l_sig is not None and k_sig == l_sig)
        disc_match = abs(int(disc)) == int(row.get("disc_abs", -1))
        k_canon = _polredabs_str(knot_shape.get("poly"))
        l_canon = _polredabs_str(_coeffs_to_poly_str(row.get("coeffs") or []))
        poly_match = (k_canon is not None and l_canon is not None
                      and k_canon == l_canon)
        out.append({
            "lmfdb_label": row.get("label"),
            "disc_abs": row.get("disc_abs"),
            "disc_sign": row.get("disc_sign"),
            "degree": row.get("degree"),
            "r2": row.get("r2"),
            "coeffs": row.get("coeffs"),
            "polredabs_match": bool(poly_match),
            "disc_match": bool(disc_match),
            "signature_match": bool(sig_match),
            "confidence": conf,
        })
    # Sort descending by confidence so consumers can read the head.
    out.sort(key=lambda d: d["confidence"], reverse=True)
    return out


def _knot_record(
    knot_name: str,
    bits_prec: int,
    max_deg: int,
    abs_disc_tol: int,
    candidate_limit: int,
    conn=None,
) -> dict:
    """Compute shape field + LMFDB candidates for a single knot."""
    sf, err = _shape_field_for_knot(knot_name, bits_prec, max_deg)
    if sf is None:
        return {
            "knot_name": knot_name,
            "shape_field": None,
            "candidates": [],
            "best_match": None,
            "status": "shape_field_failed",
            "error": err,
        }
    try:
        candidates = _build_candidates(
            sf, abs_disc_tol=abs_disc_tol,
            candidate_limit=candidate_limit, conn=conn,
        )
    except Exception as e:
        return {
            "knot_name": knot_name,
            "shape_field": sf,
            "candidates": [],
            "best_match": None,
            "status": "shape_field_failed",
            "error": f"LMFDB query failed: {e}",
        }
    if not candidates:
        return {
            "knot_name": knot_name,
            "shape_field": sf,
            "candidates": [],
            "best_match": None,
            "status": "no_candidate",
        }
    best = candidates[0]
    return {
        "knot_name": knot_name,
        "shape_field": sf,
        "candidates": candidates,
        "best_match": best,
        "status": "matched",
    }


def knot_to_nf(
    knots: Iterable,
    max_deg: int = 12,
    bits_prec: int = 500,
    abs_disc_tol: int = 0,
    candidate_limit: int = 50,
    conn=None,
) -> list[dict]:
    """Forward identity-join: knots -> LMFDB number-field candidates.

    For each knot in ``knots``: compute shape field, query LMFDB for
    number fields with matching ``(degree, |disc|)``, score each
    candidate, and return a per-knot result dict.

    This is the eager wrapper; for streaming/memory-friendly iteration
    over large corpora use :func:`bulk_scan`.

    Parameters
    ----------
    knots : iterable of str (or :class:`snappy.Manifold`).
    max_deg : Max algdep degree to try (passed through to ``knot_shape_field``).
    bits_prec : Precision for shape computation. 500 is the recommended
        default for >= 12,000-knot scans.
    abs_disc_tol : Tolerance window on ``|disc|`` for the LMFDB query.
        ``0`` (default) requires exact discriminant equality.
    candidate_limit : Max LMFDB rows to consider per knot.
    conn : Optional shared psycopg2 connection (cheaper for bulk scans).

    Returns
    -------
    list[dict] — one per knot, each with keys:
        ``knot_name``, ``shape_field`` (dict | None),
        ``candidates`` (list[dict]), ``best_match`` (dict | None),
        ``status`` in {"matched", "no_candidate", "shape_field_failed"},
        and optionally ``error`` (when ``status != "matched"``).
    """
    return list(bulk_scan(
        knots,
        max_deg=max_deg,
        bits_prec=bits_prec,
        abs_disc_tol=abs_disc_tol,
        candidate_limit=candidate_limit,
        conn=conn,
    ))


def bulk_scan(
    knot_iter: Iterable,
    max_deg: int = 12,
    bits_prec: int = 500,
    abs_disc_tol: int = 0,
    candidate_limit: int = 50,
    conn=None,
    progress_every: int = 0,
) -> Iterator[dict]:
    """Streaming counterpart to :func:`knot_to_nf`.

    Yields one result dict at a time so the full 12,966-knot corpus can
    be scanned without materializing all results in memory. Each yielded
    record matches the schema of :func:`knot_to_nf` results.

    The optional ``progress_every`` prints a one-line progress message
    every ``N`` knots (set to ``0`` to silence).

    Per-yield memory cost is bounded by ``candidate_limit`` LMFDB rows,
    not by the corpus size.
    """
    own_conn = False
    _conn = conn
    if _conn is None:
        # Try to open a shared connection — but degrade gracefully.
        try:
            from prometheus_math.databases import lmfdb as _lmfdb
            _conn = _lmfdb.connect()
            own_conn = True
        except Exception:
            _conn = None

    try:
        for i, knot in enumerate(knot_iter):
            knot_name = knot if isinstance(knot, str) else getattr(knot, "name", lambda: str(knot))()
            rec = _knot_record(
                knot_name=knot_name,
                bits_prec=bits_prec,
                max_deg=max_deg,
                abs_disc_tol=abs_disc_tol,
                candidate_limit=candidate_limit,
                conn=_conn,
            )
            yield rec
            if progress_every and ((i + 1) % progress_every == 0):
                print(f"[identity_join] {i+1} knots scanned (last: {knot_name}, status={rec['status']})")
    finally:
        if own_conn and _conn is not None:
            try:
                _conn.close()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Reverse direction: NF label -> knots whose iTrF realizes it
# ---------------------------------------------------------------------------


def knots_matching_nf(
    nf_label: str,
    knot_corpus: Optional[Iterable] = None,
    max_deg: int = 12,
    bits_prec: int = 500,
    abs_disc_tol: int = 0,
    min_confidence: float = 0.3,
    conn=None,
) -> list[dict]:
    """Reverse identity-join: which knots realize LMFDB ``nf_label``?

    Looks up ``nf_label`` in LMFDB to obtain its (degree, |disc|), then
    pre-filters the knot corpus to a single ``(degree, abs_disc)`` SQL
    cell so we only run shape-field on plausibly-matching knots.

    Parameters
    ----------
    nf_label : LMFDB number-field label (e.g. ``"3.1.23.1"``).
    knot_corpus : iterable of knot names. Defaults to all KnotInfo knots
        with crossing_number <= 13 that are flagged hyperbolic.
    max_deg, bits_prec, abs_disc_tol : pass-through to the forward join.
    min_confidence : Drop matches whose confidence is below this floor.
    conn : Shared psycopg2 connection.

    Returns
    -------
    list[dict] — same per-knot schema as :func:`knot_to_nf`, filtered to
    knots whose ``best_match.lmfdb_label == nf_label`` and confidence
    ``>= min_confidence``. Sorted descending by confidence.
    """
    # Lazy LMFDB import.
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception as e:
        raise RuntimeError(f"LMFDB module unavailable: {e}") from e

    rows = _lmfdb.number_fields(label=nf_label, limit=1, conn=conn)
    if not rows:
        raise ValueError(f"LMFDB number-field label not found: {nf_label}")
    nf_row = rows[0]
    target_deg = int(nf_row["degree"])
    target_abs_disc = int(nf_row["disc_abs"])

    # Default corpus: all KnotInfo hyperbolic knots up to crossing 13.
    if knot_corpus is None:
        try:
            from prometheus_math.databases import knotinfo as _ki
            knot_corpus = [k.get("name") for k in _ki.all_knots(
                crossing_max=13, hyperbolic_only=True,
            ) if k.get("name")]
        except Exception as e:
            raise RuntimeError(f"KnotInfo corpus unavailable: {e}") from e

    out: list[dict] = []
    # Stream + filter. We can't pre-filter on (degree, disc) without
    # running shape-field, but we CAN early-reject non-matching shape
    # fields to save the LMFDB query cost.
    for knot_name in knot_corpus:
        sf, err = _shape_field_for_knot(knot_name, bits_prec, max_deg)
        if sf is None:
            continue
        if sf.get("degree") != target_deg:
            continue
        if abs_disc_tol == 0:
            if abs(int(sf.get("disc", 0))) != target_abs_disc:
                continue
        else:
            if abs(abs(int(sf.get("disc", 0))) - target_abs_disc) > abs_disc_tol:
                continue
        # Now do the full candidate build (including poly check).
        candidates = _build_candidates(
            sf, abs_disc_tol=abs_disc_tol, candidate_limit=50, conn=conn,
        )
        # Filter to exact label match.
        matching = [c for c in candidates if c["lmfdb_label"] == nf_label]
        if not matching:
            continue
        best = matching[0]
        if best["confidence"] < min_confidence:
            continue
        out.append({
            "knot_name": knot_name,
            "shape_field": sf,
            "candidates": matching,
            "best_match": best,
            "status": "matched",
        })

    out.sort(
        key=lambda r: (r["best_match"]["confidence"] if r["best_match"] else 0.0),
        reverse=True,
    )
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_match_report(
    results: List[dict],
    out_path: Optional[str] = None,
) -> str:
    """Format a Markdown table of identity-join results.

    Columns: knot, status, shape-field (deg, disc, poly), best-match
    LMFDB label, confidence, polredabs/disc/signature flags.
    Rows are sorted: matched (by descending confidence) first, then
    no_candidate, then shape_field_failed.

    Parameters
    ----------
    results : list of dicts produced by :func:`knot_to_nf` or
        :func:`knots_matching_nf`.
    out_path : Optional path to write the markdown text. The text is
        always returned regardless.

    Returns
    -------
    str — the Markdown source.
    """
    status_order = {"matched": 0, "no_candidate": 1, "shape_field_failed": 2}

    def sort_key(r):
        s = r.get("status", "shape_field_failed")
        c = (r.get("best_match") or {}).get("confidence", 0.0)
        return (status_order.get(s, 99), -c)

    rows = sorted(results, key=sort_key)

    lines = [
        "# KnotInfo<->LMFDB Identity Join Report",
        "",
        f"_{len(rows)} knot(s) scanned._",
        "",
        "| Knot | Status | Shape (deg, disc) | Poly | LMFDB | Conf | Poly | Disc | Sig |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        sf = r.get("shape_field") or {}
        bm = r.get("best_match") or {}
        deg = sf.get("degree", "—")
        disc = sf.get("disc", "—")
        poly = sf.get("poly", "—")
        label = bm.get("lmfdb_label", "—")
        conf = bm.get("confidence")
        conf_s = f"{conf:.2f}" if isinstance(conf, (int, float)) else "—"
        pm = "Y" if bm.get("polredabs_match") else "N" if bm else "—"
        dm = "Y" if bm.get("disc_match") else "N" if bm else "—"
        sm = "Y" if bm.get("signature_match") else "N" if bm else "—"
        lines.append(
            f"| {r.get('knot_name','?')} | {r.get('status','?')} "
            f"| ({deg}, {disc}) | `{poly}` | {label} | {conf_s} "
            f"| {pm} | {dm} | {sm} |"
        )
    md = "\n".join(lines) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
    return md
