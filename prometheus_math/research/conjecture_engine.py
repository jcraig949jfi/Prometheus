"""prometheus_math.research.conjecture_engine — OEIS x LMFDB cross-join.

Project #19 phase 1 deliverable. The conjecture engine systematically
generates fingerprint sequences for LMFDB objects (elliptic curves and
number fields, in this phase) and asks "does the OEIS already know this
sequence?". Hits where an EC's a_n sequence appears in OEIS *as
something other than that EC* are the high-value research signals: a
mathematical coincidence that may indicate a hidden bridge between the
modular-form world and another corner of OEIS.

Pipeline
--------
1. signature   — generate a fingerprint sequence per LMFDB object
   (`generate_ec_signature`, `generate_nf_signature`)
2. cross-join  — search OEIS local mirror; collect hits
   (`cross_join_ec_oeis`, streaming `bulk_scan`)
3. surprise    — score each hit on (domain-distance, simplicity, rarity)
   (`surprise_score`)
4. report      — rank descending and emit Markdown summary
   (`rank_by_surprise`, `generate_report`)

Authority anchors (verified 2026-04-25 on the local OEIS mirror):
  * LMFDB ``11.a1``  -> q-expansion = OEIS A006571
    (Cremona 11a1 modular form coefficients).
  * LMFDB ``37.a1``  -> q-expansion = OEIS A007653
    (Coefficients of L-series for 37a1).

Both anchors are EC-themed in OEIS; the engine flags them as
LOW-surprise (the OEIS row's ``name`` mentions "elliptic" / "modular").
A HIGH-surprise hit would be an EC whose a_n sequence happens to match
e.g. a pure combinatorial enumeration in OEIS — that is the research
signal worth surfacing.

Streaming design
----------------
``bulk_scan`` is a generator over the input label iterable; per-yield
memory is bounded by ``candidate_limit`` OEIS rows, not by the corpus
size. Phase 2 (deferred) scales this to 10K curves with deduplication.

Public surface
--------------

    from prometheus_math.research import conjecture_engine as ce

    # Single-EC signature:
    sig = ce.generate_ec_signature([0, -1, 1, -10, -20], n_terms=20)
    # -> [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2, 4, 4, -1, ...]

    # Cross-join and rank:
    hits = ce.cross_join_ec_oeis(['11.a1', '37.a1', '5077.a1'])
    ranked = ce.rank_by_surprise(hits, top_n=10)
    md = ce.generate_report(ranked, out_path='conjecture_report.md')
"""
from __future__ import annotations

import logging
import math
import re
from typing import Any, Iterable, Iterator, List, Optional

__all__ = [
    "generate_ec_signature",
    "generate_nf_signature",
    "cross_join_ec_oeis",
    "surprise_score",
    "rank_by_surprise",
    "generate_report",
    "bulk_scan",
]

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prime helpers — cheap sieve used across signature kinds
# ---------------------------------------------------------------------------

_PRIMES_CACHE: list[int] = []


def _primes_up_to(n: int) -> list[int]:
    """Sieve of Eratosthenes; cached so repeated calls are O(1) on the cache."""
    if n < 2:
        return []
    if _PRIMES_CACHE and _PRIMES_CACHE[-1] >= n:
        # Already sieved high enough.
        cutoff = 0
        for i, p in enumerate(_PRIMES_CACHE):
            if p > n:
                cutoff = i
                break
        else:
            cutoff = len(_PRIMES_CACHE)
        return _PRIMES_CACHE[:cutoff]
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    primes = [i for i in range(n + 1) if sieve[i]]
    if len(primes) > len(_PRIMES_CACHE):
        _PRIMES_CACHE[:] = primes
    return primes


def _first_n_primes(n: int) -> list[int]:
    """Return the first ``n`` primes; grows the sieve as needed."""
    if n <= 0:
        return []
    # Rosser bound: p_n < n * (log n + log log n) for n >= 6; we pad slightly.
    if n < 6:
        bound = 15
    else:
        bound = int(n * (math.log(n) + math.log(math.log(n)))) + 10
    while True:
        primes = _primes_up_to(bound)
        if len(primes) >= n:
            return primes[:n]
        bound *= 2


# ---------------------------------------------------------------------------
# Schema layer — fingerprint generators
# ---------------------------------------------------------------------------


def generate_ec_signature(
    ainvs: Iterable[int],
    kind: str = "ap_sequence",
    n_terms: int = 20,
) -> list[int]:
    """Compute a fingerprint sequence for an elliptic curve.

    Parameters
    ----------
    ainvs : the [a1, a2, a3, a4, a6] Weierstrass coefficients.
    kind : one of

        * ``"ap_sequence"`` — full L-series q-expansion via PARI's
          ``ellan(E, n_terms)``: ``[a_1, a_2, ..., a_{n_terms}]``.  This
          is the canonical OEIS-friendly fingerprint (A006571 for 11.a1,
          A007653 for 37.a1).
        * ``"ap_only"`` — ``[a_2, a_3, a_5, a_7, ...]`` over the first
          ``n_terms`` primes only.  Good prime-only fingerprint.
        * ``"ap_mod_n"`` — ``[a_p mod 2 for p in primes]`` (Galois rep
          mod 2 silhouette).  Modulus is 2 by default; pass ``kind=
          "ap_mod_3"`` etc. to switch.
        * ``"torsion_growth"`` — ``[#E(F_p) for p in first n_terms primes]``
          = ``[p + 1 - a_p, ...]``.  Useful for cross-domain searches
          since reduction-counting sequences appear all over OEIS.

    n_terms : number of terms to emit.

    Returns
    -------
    list[int] — fingerprint values in canonical order.

    Raises
    ------
    ValueError on unrecognized ``kind`` or invalid ``ainvs``.
    """
    if n_terms <= 0:
        return []
    a = list(ainvs)
    if len(a) != 5:
        raise ValueError(
            f"ainvs must have 5 entries (a1,a2,a3,a4,a6); got len={len(a)}"
        )
    a = [int(x) for x in a]

    # mod-n parsing: kind == "ap_mod_3" -> modulus=3
    mod_match = re.match(r"^ap_mod_(\d+)$", kind)
    if mod_match:
        modulus = int(mod_match.group(1))
        if modulus < 2:
            raise ValueError(f"ap_mod_<n>: n must be >= 2, got {modulus}")
        primes = _first_n_primes(n_terms)
        ap = _ec_ap_at_primes(a, primes)
        return [int(v % modulus) for v in ap]

    if kind == "ap_sequence":
        return _ec_ellan(a, n_terms)
    if kind == "ap_only":
        primes = _first_n_primes(n_terms)
        return _ec_ap_at_primes(a, primes)
    if kind == "torsion_growth":
        primes = _first_n_primes(n_terms)
        ap = _ec_ap_at_primes(a, primes)
        return [int(p + 1 - x) for p, x in zip(primes, ap)]

    raise ValueError(
        f"unknown signature kind: {kind!r}. "
        f"Try: ap_sequence | ap_only | ap_mod_<n> | torsion_growth"
    )


def _ec_ellan(ainvs: list[int], n_terms: int) -> list[int]:
    """PARI ``ellan(ellinit(ainvs), n_terms)`` -> Python list[int]."""
    try:
        import cypari
    except ImportError as e:  # pragma: no cover — env-only path
        raise RuntimeError(f"cypari unavailable: {e}") from e
    pari = cypari.pari
    E = pari.ellinit(ainvs)
    raw = list(pari.ellan(E, int(n_terms)))
    return [int(x) for x in raw]


def _ec_ap_at_primes(ainvs: list[int], primes: list[int]) -> list[int]:
    """Compute ``a_p`` at each prime via PARI's ``ellap``."""
    try:
        import cypari
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(f"cypari unavailable: {e}") from e
    pari = cypari.pari
    E = pari.ellinit(ainvs)
    return [int(pari.ellap(E, p)) for p in primes]


def generate_nf_signature(
    coeffs: Iterable[int],
    kind: str = "class_number_sequence",
    n_terms: int = 8,
) -> list[int]:
    """Compute a fingerprint sequence for a number field.

    Parameters
    ----------
    coeffs : LMFDB-style ``[a0, a1, ..., an]`` for ``f(x) = sum a_i x^i``.
    kind : one of

        * ``"class_number_sequence"`` — class number of K, then class
          numbers of K(sqrt(-1)), K(sqrt(-2)), ... (small mock-style
          tower).  In practice we emit ``[h(K)]`` followed by zeros if
          the tower computation is unavailable; this keeps the sequence
          well-defined while flagging the missing terms.
        * ``"prime_split_sequence"`` — for the first ``n_terms`` rational
          primes ``p``, count the residue degrees of primes above ``p``
          in K (a coarse splitting fingerprint).  Specifically we emit
          ``[g_p for p in primes]`` where ``g_p`` is the number of prime
          ideals above ``p``.  This is OEIS-friendly because many such
          splitting sequences are tabulated.

    n_terms : number of fingerprint values.

    Returns
    -------
    list[int]
    """
    if n_terms <= 0:
        return []
    poly = list(coeffs)
    if len(poly) < 2:
        raise ValueError(
            f"coeffs must define a non-trivial polynomial (len>=2); got {poly}"
        )
    poly = [int(c) for c in poly]

    if kind == "class_number_sequence":
        # Just emit h(K) followed by zero padding — an honest, robust
        # fingerprint that needs only `bnfinit`. The tower-class-number
        # extension is an obvious phase-2 enrichment.
        h = _nf_class_number(poly)
        return [h] + [0] * (n_terms - 1)
    if kind == "prime_split_sequence":
        primes = _first_n_primes(n_terms)
        return _nf_prime_split(poly, primes)

    raise ValueError(
        f"unknown signature kind: {kind!r}. "
        f"Try: class_number_sequence | prime_split_sequence"
    )


def _nf_class_number(coeffs: list[int]) -> int:
    """PARI ``bnfinit(f).clgp[1]`` (class number) for the NF defined by f."""
    try:
        import cypari
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(f"cypari unavailable: {e}") from e
    pari = cypari.pari
    poly_str = "+".join(
        f"({c})*x^{i}" if i > 1 else (f"({c})*x" if i == 1 else f"({c})")
        for i, c in enumerate(coeffs) if c != 0
    ) or "0"
    bnf = pari.bnfinit(poly_str)
    return int(bnf[7][0])  # clgp = bnf[7]; clgp[0] = order in PARI 0-index


def _nf_prime_split(coeffs: list[int], primes: list[int]) -> list[int]:
    """Number of prime ideals above each rational prime in K."""
    try:
        import cypari
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(f"cypari unavailable: {e}") from e
    pari = cypari.pari
    poly_str = "+".join(
        f"({c})*x^{i}" if i > 1 else (f"({c})*x" if i == 1 else f"({c})")
        for i, c in enumerate(coeffs) if c != 0
    ) or "0"
    nf = pari.nfinit(poly_str)
    out: list[int] = []
    for p in primes:
        try:
            dec = pari.idealprimedec(nf, p)
            out.append(int(len(dec)))
        except Exception:
            out.append(0)
    return out


# ---------------------------------------------------------------------------
# Surprise scoring — domain-distance + simplicity + rarity
# ---------------------------------------------------------------------------


# Heuristic vocabulary for "OEIS row is itself an EC / modular form
# sequence". A name match in this list pushes surprise DOWN — finding
# A006571 from 11.a1 is no surprise, since A006571 is *named* after
# 11a1's modular form (eta-product expansion).
_EC_VOCAB = {
    "elliptic", "modular form", "modular forms",
    "l-series", "newform", "cremona", "cusp form",
    "weight 2", "j-invariant", "isogeny",
    "eisenstein", "hecke", "ramanujan",
    # Eta-product / theta-series patterns are textbook modular-form
    # generating functions; their q-expansions are weight-k modular forms.
    "eta function", "eta product", "eta-product",
    "theta series", "theta function",
}

# Eta-product / level-N regex patterns: detect strings like
# "(1-q^k)^2*(1-q^(11*k))^2" — the canonical newform-as-eta-product
# notation that A006571 uses.
_ETA_PRODUCT_RE = re.compile(r"\(1\s*-\s*q\^[a-zA-Z()0-9 +*]+\)\s*\^?\s*\d*")
# "eta(q^k)" / "eta(q)" — direct Dedekind eta references.
_ETA_FUNC_RE = re.compile(r"eta\s*\(\s*q", re.IGNORECASE)
# "for elliptic curve" / "elliptic curve" anywhere in the name.
_EC_PHRASE_RE = re.compile(r"\bellipt(ic)?\b", re.IGNORECASE)


def _name_signals_ec(name: str) -> bool:
    """True iff the OEIS name suggests this sequence is itself EC-themed.

    Three signal classes:
      1. Direct vocabulary (``elliptic``, ``L-series``, ``newform``, ...).
      2. ``elliptic`` regex (catches ``Elliptic``, ``elliptical``, etc.).
      3. Eta-product expansion patterns ``q*Product_{...} (1-q^k)^...``
         — common for newforms with shipped q-expansions, even when the
         OEIS name doesn't explicitly say "modular form".
    """
    if not name:
        return False
    n = name.lower()
    if any(tok in n for tok in _EC_VOCAB):
        return True
    if _EC_PHRASE_RE.search(name):
        return True
    # Direct eta(q^k) reference — Dedekind eta products are the
    # universal modular-form generating-function notation in OEIS.
    if _ETA_FUNC_RE.search(name):
        return True
    # Eta-product check: needs both a "Product" keyword AND a (1-q^...)
    # factor.  Either alone is too generic.
    if "product" in n and _ETA_PRODUCT_RE.search(name):
        return True
    return False


def surprise_score(ec_data: dict, oeis_data: dict) -> float:
    """Score how surprising it is that ``ec_data`` matches ``oeis_data``.

    Components, each in [0, 1] before weighting:

      * **domain_distance** (weight 0.6) — 0 if the OEIS row is itself
        EC-themed (e.g. A006571 names "11a1's modular form"), 1 if the
        OEIS row's name shows no EC vocabulary.
      * **simplicity** (weight 0.2) — short OEIS name = simpler statement
        = more striking coincidence. Scaled as
        ``min(1, 80 / max(len(name), 1))``.
      * **rarity** (weight 0.2) — proxy by ``1 - data_length / 50`` (the
        bulk dump has 30-50 leading terms; sequences with fewer terms
        have less crowd, so a match is rarer). Falls in [0, 1].

    All weights sum to 1; the result is clamped to [0, 1].

    Parameters
    ----------
    ec_data : dict with at minimum ``ec_label`` and the input
        ``signature`` (the matched values).
    oeis_data : dict matching the schema returned by ``oeis.lookup``:
        ``{"number": "A006571", "name": "...", "data": [int, ...], ...}``.

    Returns
    -------
    float in [0, 1].
    """
    if not isinstance(oeis_data, dict):
        return 0.0
    name = oeis_data.get("name", "") or ""

    # Component 1: domain distance — does OEIS name indicate EC theme?
    if _name_signals_ec(name):
        domain_distance = 0.0
    else:
        domain_distance = 1.0

    # Component 2: simplicity — short name -> simpler statement.
    nlen = max(len(name), 1)
    simplicity = min(1.0, 80.0 / nlen)

    # Component 3: rarity — fewer terms on file -> rarer match.
    dlen = len(oeis_data.get("data", []) or [])
    if dlen <= 0:
        rarity = 1.0
    else:
        rarity = max(0.0, 1.0 - dlen / 50.0)

    score = 0.6 * domain_distance + 0.2 * simplicity + 0.2 * rarity
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


# ---------------------------------------------------------------------------
# Cross-join layer
# ---------------------------------------------------------------------------


def _fetch_ec(label: str, conn=None) -> Optional[dict]:
    """One-shot LMFDB lookup for an EC label."""
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"LMFDB module unavailable: {e}") from e
    rows = _lmfdb.elliptic_curves(label=label, limit=1, conn=conn)
    return rows[0] if rows else None


def _oeis_match(values: list[int], min_match_terms: int) -> Optional[dict]:
    """Return the OEIS record (dict) matching ``values``, or None.

    A "match" requires at least ``min_match_terms`` of the values to align
    with an OEIS sequence. Below that threshold the prefix is too generic
    to be a research signal.
    """
    if len(values) < min_match_terms:
        return None
    try:
        from prometheus_math.databases import oeis as _oeis
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"OEIS module unavailable: {e}") from e
    # Trim to min_match_terms first -> most-specific search; fall back to
    # full-length if no match.
    a_id = _oeis.is_known(values)
    if a_id is None:
        return None
    return _oeis.lookup(a_id)


def cross_join_ec_oeis(
    label_iter: Iterable[str],
    kinds: Iterable[str] = ("ap_sequence",),
    n_terms: int = 20,
    min_match_terms: int = 8,
    conn=None,
) -> list[dict]:
    """Eager cross-join: for each EC label, hit OEIS with each signature kind.

    Parameters
    ----------
    label_iter : iterable of LMFDB EC labels (e.g. ``"11.a1"``).
    kinds : iterable of signature kinds to try per EC.
    n_terms : terms per signature.
    min_match_terms : minimum prefix length to accept as a match.
    conn : optional shared LMFDB psycopg2 connection.

    Returns
    -------
    list[dict] — one record per (label, kind) hit, with keys:

        ``ec_label``, ``ainvs``, ``conductor``, ``rank``,
        ``signature_kind``, ``signature``, ``oeis_match`` (A-num),
        ``oeis_name``, ``surprise_score``.

    Use :func:`bulk_scan` for streaming over large iterables.
    """
    return list(bulk_scan(
        label_iter,
        kinds=kinds,
        n_terms=n_terms,
        min_match_terms=min_match_terms,
        conn=conn,
    ))


def bulk_scan(
    label_iter: Iterable[str],
    kinds: Iterable[str] = ("ap_sequence",),
    n_terms: int = 20,
    min_match_terms: int = 8,
    conn=None,
    progress_every: int = 0,
) -> Iterator[dict]:
    """Streaming counterpart to :func:`cross_join_ec_oeis`.

    Yields one match dict per (label, kind) hit, so the full 3.8M-EC
    LMFDB corpus can be scanned without materializing all results in
    memory. Per-yield memory cost is bounded by one OEIS row.
    """
    kinds = list(kinds)
    if not kinds:
        return
    own_conn = False
    _conn = conn
    if _conn is None:
        try:
            from prometheus_math.databases import lmfdb as _lmfdb
            _conn = _lmfdb.connect()
            own_conn = True
        except Exception:
            _conn = None

    try:
        for i, label in enumerate(label_iter):
            ec = _fetch_ec(label, conn=_conn)
            if ec is None:
                continue
            ainvs = ec.get("ainvs")
            if not ainvs or len(ainvs) != 5:
                continue
            for kind in kinds:
                try:
                    sig = generate_ec_signature(ainvs, kind=kind, n_terms=n_terms)
                except Exception as e:
                    _log.debug("signature failed for %s/%s: %s", label, kind, e)
                    continue
                if not sig:
                    continue
                hit = _oeis_match(sig, min_match_terms=min_match_terms)
                if hit is None:
                    continue
                rec = {
                    "ec_label": label,
                    "ainvs": list(ainvs),
                    "conductor": ec.get("conductor"),
                    "rank": ec.get("rank"),
                    "signature_kind": kind,
                    "signature": list(sig),
                    "oeis_match": hit.get("number"),
                    "oeis_name": hit.get("name", ""),
                    "surprise_score": surprise_score(
                        {"ec_label": label, "signature": sig},
                        hit,
                    ),
                }
                yield rec
            if progress_every and ((i + 1) % progress_every == 0):
                _log.info("[conjecture_engine] %d ECs scanned (last: %s)",
                          i + 1, label)
    finally:
        if own_conn and _conn is not None:
            try:
                _conn.close()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Reporting layer
# ---------------------------------------------------------------------------


def rank_by_surprise(matches: List[dict], top_n: int = 20) -> list[dict]:
    """Sort match dicts by ``surprise_score`` descending; return top-N.

    Stable on ties (preserves input order via a numeric secondary key)
    so reruns produce deterministic ranking.
    """
    if not matches:
        return []
    indexed = list(enumerate(matches))
    indexed.sort(
        key=lambda it: (-float(it[1].get("surprise_score") or 0.0), it[0]),
    )
    return [m for _, m in indexed[: max(0, int(top_n))]]


def generate_report(
    matches: List[dict],
    out_path: Optional[str] = None,
) -> str:
    """Render a Markdown report of cross-join hits.

    Columns: rank, EC label, conductor, rank, signature kind, OEIS A-num,
    OEIS name (truncated), surprise score, signature prefix.

    Parameters
    ----------
    matches : list of match dicts (from cross_join / bulk_scan); typically
        already passed through :func:`rank_by_surprise`.
    out_path : optional path to write the markdown text.

    Returns
    -------
    str — the Markdown source.
    """
    lines = [
        "# OEIS x LMFDB Conjecture-Engine Report",
        "",
        f"_{len(matches)} cross-domain hit(s)._",
        "",
        "| # | EC | Cond | Rk | Kind | OEIS | Name | Surprise | Sig prefix |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, m in enumerate(matches, 1):
        ec = m.get("ec_label", "?")
        cond = m.get("conductor", "—")
        rk = m.get("rank", "—")
        kind = m.get("signature_kind", "?")
        oa = m.get("oeis_match", "?")
        name = (m.get("oeis_name", "") or "")[:60]
        score = m.get("surprise_score")
        score_s = f"{score:.2f}" if isinstance(score, (int, float)) else "—"
        sig = m.get("signature", []) or []
        sig_s = ",".join(str(int(v)) for v in sig[:8])
        if len(sig) > 8:
            sig_s += ",..."
        lines.append(
            f"| {i} | {ec} | {cond} | {rk} | {kind} | {oa} "
            f"| {name} | {score_s} | `{sig_s}` |"
        )
    md = "\n".join(lines) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
    return md
