"""zbMATH Open — wrapper over the open-access subset of zbMATH.

zbMATH (https://zbmath.org/) is the world's most comprehensive abstracting
and reviewing service for pure and applied mathematics, run by FIZ Karlsruhe.
Since 2021, zbMATH Open (https://zbmath.org/open/) makes a substantial slice
of the database — including reviews, MSC classifications, and bibliographic
metadata — available for free under CC-BY-SA. The companion REST API at
https://api.zbmath.org/v1/ exposes that subset to programs.

For Prometheus this is a curated, review-rich complement to arXiv:

  * arxiv.py    — preprints, raw and recent, no editorial layer
  * zbmath.py   — peer-edited indices, reviews, and MSC tags

zbMATH and arXiv together cover essentially the entire mathematical
literature; pulling from both is how we cross-check that a "novel" finding
isn't already known. Aporia uses this wrapper to seed literature crawls
around its open questions; Charon uses it to find priority references for
conjectures; Cartography uses MSC tags as concept anchors.

API surface (live, verified 2026-04-22):

    GET  /v1/document                    — list/search documents
    GET  /v1/document/_search            — primary search endpoint
                                            param: search_string=...
                                            param: results_per_page=N
                                            param: page=N
    GET  /v1/document/<id_or_identifier> — single document by numeric id
                                            (e.g. 732023) or zbMATH
                                            identifier (e.g. '0823.11029')

The search syntax accepts field prefixes:

    au:Wiles            — author surname
    cc:11G05            — MSC2020 classification code
    py:2020             — publication year
    py:2010-2020        — publication year range
    ti:elliptic         — title contains
    so:Annals           — source / journal contains
    rv:Faltings         — reviewer

These can be combined: ``au:Wiles cc:11G05 py:1990-2000``.

Public surface:

    search(query, author, msc, year, year_range,
           max_results, page)                       -> list[dict]
    get(zbmath_id)                                  -> dict | None
    by_author(author_name, max_results)             -> list[dict]
    by_msc(msc_code, year_range, max_results)       -> list[dict]
    reviews(zbmath_id)                              -> dict | None
    msc_codes(level='leaf'|'subject'|'top')         -> list[str]
    msc_descriptions(level=...)                     -> dict[str, str]
    msc_lookup(code)                                -> dict
    msc_subtree(parent_code)                        -> list[str]
    msc_path(code)                                  -> list[(code, desc)]
    msc_search(query, max_results=20)               -> list[dict]
    msc_anchors()                                   -> list[(code, desc)]   # legacy
    probe(timeout)                                  -> bool

Result dict shape:

    {
        "zbmath_id":  "0823.11029",            # canonical "DDDD.DDDDD" id
        "internal_id": 105023,                  # zbMATH numeric id
        "title":      "Modular elliptic curves and Fermat's Last Theorem",
        "authors":    ["Wiles, Andrew"],
        "year":       1995,
        "msc_codes":  ["11G05", "11F33", ...],
        "journal":    "Ann. Math. (2)",
        "doi":        "10.2307/2118559",
        "source":     "Ann. Math. (2) 141, No. 3, 443-551 (1995).",
        "abstract":   "...",                    # if open-access; else ""
        "keywords":   ["elliptic curves", ...],
        "url":        "https://zbmath.org/?q=an:0823.11029",
    }

Coverage / known limitations:

  * Only a subset of zbMATH is "open"; closed records may return less
    detail. The 422 / "field required" errors that appear on URL play
    are surfaced here as empty results.
  * Full MSC2020 has ~6000 leaf codes; the leveled ``msc_codes()`` /
    ``msc_lookup()`` / ``msc_search()`` API ships an embedded snapshot
    of all of them (built from https://msc2020.org/MSC_2020.csv). The
    legacy curated ~200-entry anchor list is still available via
    ``msc_anchors()``.
  * No authentication is required for this open subset, but the API is
    polite-rate-limited; this wrapper enforces 1 request/second.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_BASE = "https://api.zbmath.org/v1"
_USER_AGENT = "prometheus-math/0.1 (mathematical research tool)"
_DEFAULT_TIMEOUT = 15.0
_MIN_INTERVAL = 1.0  # seconds between requests

_lock = threading.Lock()
_last_request_ts: float = 0.0

# Cache: keyed by (endpoint, params-tuple).
_cache: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------

def _throttle() -> None:
    """Sleep so we don't exceed 1 request/sec."""
    global _last_request_ts
    with _lock:
        delta = time.monotonic() - _last_request_ts
        if delta < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - delta)
        _last_request_ts = time.monotonic()


def _http_get(path: str, params: Optional[dict] = None,
              timeout: float = _DEFAULT_TIMEOUT) -> Optional[dict]:
    """Throttled GET against the zbMATH Open API. Returns parsed JSON or None."""
    url = f"{_BASE}{path}"
    cache_key = f"{path}?{tuple(sorted((params or {}).items()))}"
    if cache_key in _cache:
        return _cache[cache_key]
    _throttle()
    headers = {"User-Agent": _USER_AGENT, "Accept": "application/json"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.RequestException:
        _cache[cache_key] = None
        return None
    if r.status_code != 200:
        _cache[cache_key] = None
        return None
    try:
        data = r.json()
    except ValueError:
        _cache[cache_key] = None
        return None
    _cache[cache_key] = data
    return data


# ---------------------------------------------------------------------------
# Result shaping
# ---------------------------------------------------------------------------

def _extract_title(record: dict) -> str:
    """zbMATH titles can land in any of several sub-fields depending on
    whether the original was English, translated, or has a subtitle."""
    t = record.get("title") or {}
    if isinstance(t, str):
        return t.strip()
    if not isinstance(t, dict):
        return ""
    for key in ("title", "original", "addition"):
        v = t.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _extract_authors(record: dict) -> list[str]:
    contrib = record.get("contributors") or {}
    authors = contrib.get("authors") or []
    out: list[str] = []
    for a in authors:
        if isinstance(a, dict):
            name = a.get("name")
            if isinstance(name, str) and name.strip():
                out.append(name.strip())
        elif isinstance(a, str) and a.strip():
            out.append(a.strip())
    return out


def _extract_year(record: dict) -> Optional[int]:
    """Year may live at top-level `year` or nested in source.series[0].year."""
    y = record.get("year")
    if isinstance(y, int):
        return y
    if isinstance(y, str) and y.strip().isdigit():
        return int(y.strip())
    src = (record.get("source") or {}).get("series") or []
    if src and isinstance(src[0], dict):
        sy = src[0].get("year")
        if isinstance(sy, str) and sy.strip().isdigit():
            return int(sy.strip())
        if isinstance(sy, int):
            return sy
    return None


def _extract_msc(record: dict) -> list[str]:
    msc = record.get("msc") or []
    out: list[str] = []
    for m in msc:
        if isinstance(m, dict):
            code = m.get("code")
            if isinstance(code, str) and code.strip():
                out.append(code.strip())
        elif isinstance(m, str) and m.strip():
            out.append(m.strip())
    return out


def _extract_journal(record: dict) -> str:
    src = (record.get("source") or {}).get("series") or []
    if src and isinstance(src[0], dict):
        for key in ("short_title", "title"):
            v = src[0].get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


def _extract_doi(record: dict) -> str:
    for link in record.get("links") or []:
        if isinstance(link, dict) and (link.get("type") or "").lower() == "doi":
            ident = link.get("identifier")
            if isinstance(ident, str) and ident.strip():
                return ident.strip()
    return ""


def _extract_abstract(record: dict) -> str:
    """Use the first review/abstract editorial contribution when open."""
    for contrib in record.get("editorial_contributions") or []:
        if not isinstance(contrib, dict):
            continue
        text = contrib.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return ""


def _extract_keywords(record: dict) -> list[str]:
    kws = record.get("keywords") or []
    return [k.strip() for k in kws if isinstance(k, str) and k.strip()]


def _shape_record(record: dict) -> dict:
    """Convert a raw zbMATH document record into our normalized dict."""
    if not isinstance(record, dict):
        return {}
    return {
        "zbmath_id":   record.get("identifier", "") or "",
        "internal_id": record.get("id"),
        "title":       _extract_title(record),
        "authors":     _extract_authors(record),
        "year":        _extract_year(record),
        "msc_codes":   _extract_msc(record),
        "journal":     _extract_journal(record),
        "doi":         _extract_doi(record),
        "source":      ((record.get("source") or {}).get("source") or "").strip(),
        "abstract":    _extract_abstract(record),
        "keywords":    _extract_keywords(record),
        "url":         record.get("zbmath_url", "") or "",
    }


# ---------------------------------------------------------------------------
# Search-string assembly
# ---------------------------------------------------------------------------

def _build_search_string(query: Optional[str] = None,
                         author: Optional[str] = None,
                         msc: Optional[str] = None,
                         year: Optional[int] = None,
                         year_range: Optional[tuple] = None) -> str:
    """Combine kwargs into a zbMATH `search_string`. Year range wins over year."""
    parts: list[str] = []
    if query:
        parts.append(str(query).strip())
    if author:
        a = str(author).strip()
        # Multi-word names: zbMATH accepts "Wiles, Andrew" but quoting is
        # safer with spaces; the API treats commas as field separators in
        # some contexts, so we only quote when there's no comma.
        if " " in a and "," not in a:
            parts.append(f'au:"{a}"')
        else:
            parts.append(f"au:{a}")
    if msc:
        parts.append(f"cc:{str(msc).strip()}")
    if year_range and len(year_range) == 2:
        lo, hi = year_range
        if lo and hi:
            parts.append(f"py:{int(lo)}-{int(hi)}")
        elif lo:
            parts.append(f"py:{int(lo)}-")
        elif hi:
            parts.append(f"py:-{int(hi)}")
    elif year is not None:
        parts.append(f"py:{int(year)}")
    return " ".join(parts).strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search(query: Optional[str] = None,
           author: Optional[str] = None,
           msc: Optional[str] = None,
           year: Optional[int] = None,
           year_range: Optional[tuple] = None,
           max_results: int = 20,
           page: int = 1) -> list[dict]:
    """Search zbMATH Open.

    All filters are optional; combine freely:

        search('zeta', msc='11M06')
        search(author='Wiles', year_range=(1990, 2000))
        search(msc='11G05', year=2020)

    Returns a list of normalized dicts (see module docstring). Pagination
    is via the `page` parameter; the API caps results-per-page at ~100, so
    `max_results` larger than that triggers multiple pages.
    """
    ss = _build_search_string(query, author, msc, year, year_range)
    if not ss:
        return []

    out: list[dict] = []
    cur_page = max(1, int(page))
    while len(out) < max_results:
        per = min(max(1, max_results - len(out)), 100)
        params = {
            "search_string": ss,
            "results_per_page": str(per),
            "page": str(cur_page),
        }
        data = _http_get("/document/_search", params=params)
        if not data:
            break
        records = data.get("result") or []
        if not records:
            break
        for rec in records:
            shaped = _shape_record(rec)
            if shaped:
                out.append(shaped)
            if len(out) >= max_results:
                break
        # Decide whether to fetch the next page.
        status = data.get("status") or {}
        total = status.get("nr_total_results")
        got = status.get("nr_request_results", len(records))
        if not got or len(records) < per:
            break
        if total is not None and (cur_page * per) >= total:
            break
        cur_page += 1

    return out


def get(zbmath_id) -> Optional[dict]:
    """Fetch a single document by zbMATH identifier or numeric internal id.

    Examples:
        get('0823.11029')   # zbMATH-style identifier (Wiles, FLT proof)
        get(732023)         # numeric internal id
    """
    if zbmath_id is None:
        return None
    sid = str(zbmath_id).strip()
    if not sid:
        return None
    data = _http_get(f"/document/{sid}")
    if not data:
        return None
    rec = data.get("result")
    if not isinstance(rec, dict):
        return None
    return _shape_record(rec)


def by_author(author_name: str, max_results: int = 20) -> list[dict]:
    """Papers by an author. Wrapper for ``search(author=...)``.

    zbMATH author resolution is fuzzy: 'Wiles' matches every author whose
    surname contains 'Wiles'. Pass 'Surname, First' to disambiguate when
    needed.
    """
    if not author_name:
        return []
    return search(author=author_name, max_results=max_results)


def by_msc(msc_code: str,
           year_range: Optional[tuple] = None,
           max_results: int = 50) -> list[dict]:
    """Papers in an MSC2020 classification code.

    `msc_code` may be a leaf code ('11G05'), a 2-character top-level code
    ('11'), or a hyphenated section code ('11-XX'). Use ``msc_codes()`` to
    browse the available top/second-level codes.
    """
    if not msc_code:
        return []
    return search(msc=msc_code, year_range=year_range, max_results=max_results)


def reviews(zbmath_id) -> Optional[dict]:
    """Return the open-access review of a paper, if one exists.

    Returns ``{"reviewer": str, "review_text": str, "review_year": int|None}``
    or None when no review is attached or when the record is closed.
    """
    if zbmath_id is None:
        return None
    sid = str(zbmath_id).strip()
    if not sid:
        return None
    data = _http_get(f"/document/{sid}")
    if not data:
        return None
    rec = data.get("result")
    if not isinstance(rec, dict):
        return None
    contribs = rec.get("editorial_contributions") or []
    for c in contribs:
        if not isinstance(c, dict):
            continue
        if (c.get("contribution_type") or "").lower() not in ("review", "abstract"):
            continue
        text = c.get("text") or ""
        if not text.strip():
            continue
        reviewer_obj = c.get("reviewer") or {}
        reviewer = ""
        if isinstance(reviewer_obj, dict):
            reviewer = (reviewer_obj.get("name")
                        or reviewer_obj.get("sign")
                        or "").strip()
        return {
            "reviewer":    reviewer,
            "review_text": text.strip(),
            "review_year": _extract_year(rec),
        }
    return None


# ---------------------------------------------------------------------------
# MSC2020 — full hierarchy (project #48)
#
# The full ~6000-leaf hierarchy lives in ``_msc2020_data.py`` (built from
# https://msc2020.org/MSC_2020.csv on 2026-04-25). This file exposes the
# public lookup / search / traversal API.
#
# Three normalized levels:
#
#     top      — 2-character (e.g. "11" = "Number theory")
#     subject  — 3-character (e.g. "11G" = "Arithmetic algebraic geometry")
#     leaf     — 5-character (e.g. "11G05" = "Elliptic curves over global
#                fields"; also "00-01" form for general-section leaves)
#
# Reference: https://mathscinet.ams.org/msnhtml/msc2020.pdf and the AMS /
# zbMATH joint CSV at https://msc2020.org/.
# ---------------------------------------------------------------------------

from . import _msc2020_data as _msc

_VALID_LEVELS = ("leaf", "subject", "top")


def _normalize_code(raw) -> str:
    """Canonicalize a user-supplied code.

    Accepts: "11G05", "11g05", " 11G05 ", "11" / "11-XX" (top), "11G" /
    "11Gxx" (subject), "00-01" (5-char leaf). Strips whitespace,
    upper-cases the letter, and rewrites the redundant suffix forms
    (-XX, xx) so they match the keys in ``_msc.TOP/SUBJECT/LEAF``.
    """
    if raw is None:
        raise ValueError("MSC code must not be None")
    s = str(raw).strip()
    if not s:
        raise ValueError("MSC code must not be empty")
    # Drop the redundant 'XX' / 'xx' / '-XX' suffixes upstream callers
    # sometimes pass through from the AMS notation.
    upper = s.upper()
    if upper.endswith("-XX") and len(upper) == 5:
        return upper[:2]                # "11-XX" -> "11"
    if upper.endswith("XX") and len(upper) == 5 and upper[2].isalpha():
        return upper[:3]                # "11GXX" -> "11G"
    # Generic shape preservation: digits + letter + digits or digits + dash + digits.
    # 5-char leaf "11G05" -> "11G05" ; "11-01" stays as is.
    return upper


def _classify_code(canonical: str) -> str:
    """Return the level of a *canonical* code, or raise KeyError if unknown."""
    if canonical in _msc.TOP:
        return "top"
    if canonical in _msc.SUBJECT:
        return "subject"
    if canonical in _msc.LEAF:
        return "leaf"
    raise KeyError(f"unknown MSC2020 code: {canonical!r}")


def _description_for(canonical: str, level: str) -> str:
    if level == "top":
        return _msc.TOP[canonical]
    if level == "subject":
        return _msc.SUBJECT[canonical]
    return _msc.LEAF[canonical]


def msc_codes(level: str = "leaf") -> list[str]:
    """Return all MSC2020 codes at the requested level, sorted.

    Parameters
    ----------
    level : {'leaf', 'subject', 'top'}
        - ``'leaf'``    -> 5-character codes (e.g. ``"11G05"``); ~6000 entries.
        - ``'subject'`` -> 3-character codes (e.g. ``"11G"``); ~530 entries.
        - ``'top'``     -> 2-character codes (e.g. ``"11"``); 63 entries.

    Raises
    ------
    ValueError
        If ``level`` is not one of the three valid values.
    """
    if level not in _VALID_LEVELS:
        raise ValueError(
            f"unknown level {level!r}; must be one of "
            f"{', '.join(_VALID_LEVELS)}"
        )
    if level == "leaf":
        return sorted(_msc.LEAF.keys())
    if level == "subject":
        return sorted(_msc.SUBJECT.keys())
    return sorted(_msc.TOP.keys())


def msc_descriptions(level: str = "leaf") -> dict[str, str]:
    """Return ``code -> description`` for every MSC2020 code at ``level``.

    The dict is a fresh copy; mutating it does not affect the embedded
    snapshot.
    """
    if level not in _VALID_LEVELS:
        raise ValueError(
            f"unknown level {level!r}; must be one of "
            f"{', '.join(_VALID_LEVELS)}"
        )
    if level == "leaf":
        return dict(_msc.LEAF)
    if level == "subject":
        return dict(_msc.SUBJECT)
    return dict(_msc.TOP)


def msc_lookup(code) -> dict:
    """Resolve a single MSC code to its full ancestry record.

    Returns a dict::

        {
            'code':                   canonical code,
            'level':                  'top' | 'subject' | 'leaf',
            'description':            string,
            'parent_code':            str | None,
            'parent_description':     str | None,
            'top_level_code':         str,
            'top_level_description':  str,
        }

    The lookup is robust to case and surrounding whitespace
    (``"11g05"``, ``" 11G05 "``, ``"11Gxx"`` all resolve as expected).

    Raises
    ------
    ValueError
        If ``code`` is empty, whitespace, or ``None``.
    KeyError
        If the (normalized) code is not in the MSC2020 spec.
    """
    canonical = _normalize_code(code)
    level = _classify_code(canonical)
    desc = _description_for(canonical, level)

    if level == "top":
        parent_code: str | None = None
        parent_desc: str | None = None
        top_code = canonical
    elif level == "subject":
        parent_code = canonical[:2]
        parent_desc = _msc.TOP.get(parent_code)
        top_code = parent_code
    else:  # leaf
        # Two leaf shapes: "11G05" -> parent "11G"; "00-01" -> parent "00".
        if canonical[2] == "-":
            parent_code = canonical[:2]
            parent_desc = _msc.TOP.get(parent_code)
        else:
            parent_code = canonical[:3]
            parent_desc = _msc.SUBJECT.get(parent_code)
        top_code = canonical[:2]

    return {
        "code":                  canonical,
        "level":                 level,
        "description":           desc,
        "parent_code":           parent_code,
        "parent_description":    parent_desc,
        "top_level_code":        top_code,
        "top_level_description": _msc.TOP.get(top_code),
    }


def msc_subtree(parent_code) -> list[str]:
    """All leaf codes that descend from a given top or subject node.

    Parameters
    ----------
    parent_code : str
        A top-level (``"11"``) or subject (``"11G"``) code. Leaves are
        returned in sorted order. Unknown / malformed parents return ``[]``
        (this is intentional; callers can ``msc_lookup`` first if they
        want a hard error).

    Examples
    --------
    >>> '11G05' in msc_subtree('11')
    True
    >>> set(msc_subtree('11G')).issubset(set(msc_subtree('11')))
    True
    """
    try:
        canonical = _normalize_code(parent_code)
    except ValueError:
        return []
    if canonical not in _msc.TOP and canonical not in _msc.SUBJECT:
        return []
    n = len(canonical)
    return sorted(c for c in _msc.LEAF if c.startswith(canonical) and len(c) > n)


def msc_path(code) -> list[tuple[str, str]]:
    """Walk the ancestry chain top -> subject -> leaf for ``code``.

    Returns ``[(top_code, top_desc), (subject_code, subject_desc),
    (leaf_code, leaf_desc)]`` for a leaf; shorter for higher-level
    queries (``[(top_code, top_desc)]`` for a top-level code).
    """
    info = msc_lookup(code)
    path: list[tuple[str, str]] = []
    if info["top_level_code"]:
        path.append((info["top_level_code"], info["top_level_description"]))
    if info["level"] == "subject":
        path.append((info["code"], info["description"]))
    elif info["level"] == "leaf":
        # Insert subject if any.
        if info["parent_code"] and info["parent_code"] != info["top_level_code"]:
            path.append((info["parent_code"], info["parent_description"]))
        path.append((info["code"], info["description"]))
    return path


def msc_search(query: str, max_results: int = 20) -> list[dict]:
    """Substring-match ``query`` against descriptions at every level.

    Returns a list of ``msc_lookup``-shaped dicts, sorted by (level
    priority [leaf, subject, top], code) so the most specific hits come
    first. The match is case-insensitive.

    Raises
    ------
    ValueError
        If ``query`` is empty or whitespace.
    """
    if query is None:
        raise ValueError("msc_search query must not be None")
    needle = str(query).strip().lower()
    if not needle:
        raise ValueError("msc_search query must not be empty")

    out: list[dict] = []
    # Search leaves first (most specific), then subjects, then top.
    for code, desc in _msc.LEAF.items():
        if needle in desc.lower():
            out.append(msc_lookup(code))
            if len(out) >= max_results:
                return out
    for code, desc in _msc.SUBJECT.items():
        if needle in desc.lower():
            out.append(msc_lookup(code))
            if len(out) >= max_results:
                return out
    for code, desc in _msc.TOP.items():
        if needle in desc.lower():
            out.append(msc_lookup(code))
            if len(out) >= max_results:
                return out
    return out


# Legacy compatibility: the pre-#48 msc_codes() returned ``[(code, desc), ...]``
# anchored at top-level + a curated section list, with codes in their
# AMS-suffixed form ("11-XX", "11G"). The leveled msc_codes(level=...) API
# above is the new canonical entry point; ``msc_anchors()`` below preserves
# the legacy shape so existing callers keep working unchanged.
_MSC_TOP: list[tuple[str, str]] = [
    ("00-XX", "General and overarching topics; collections"),
    ("01-XX", "History and biography"),
    ("03-XX", "Mathematical logic and foundations"),
    ("05-XX", "Combinatorics"),
    ("06-XX", "Order, lattices, ordered algebraic structures"),
    ("08-XX", "General algebraic systems"),
    ("11-XX", "Number theory"),
    ("12-XX", "Field theory and polynomials"),
    ("13-XX", "Commutative algebra"),
    ("14-XX", "Algebraic geometry"),
    ("15-XX", "Linear and multilinear algebra; matrix theory"),
    ("16-XX", "Associative rings and algebras"),
    ("17-XX", "Nonassociative rings and algebras"),
    ("18-XX", "Category theory; homological algebra"),
    ("19-XX", "K-theory"),
    ("20-XX", "Group theory and generalizations"),
    ("22-XX", "Topological groups, Lie groups"),
    ("26-XX", "Real functions"),
    ("28-XX", "Measure and integration"),
    ("30-XX", "Functions of a complex variable"),
    ("31-XX", "Potential theory"),
    ("32-XX", "Several complex variables and analytic spaces"),
    ("33-XX", "Special functions"),
    ("34-XX", "Ordinary differential equations"),
    ("35-XX", "Partial differential equations"),
    ("37-XX", "Dynamical systems and ergodic theory"),
    ("39-XX", "Difference and functional equations"),
    ("40-XX", "Sequences, series, summability"),
    ("41-XX", "Approximations and expansions"),
    ("42-XX", "Harmonic analysis on Euclidean spaces"),
    ("43-XX", "Abstract harmonic analysis"),
    ("44-XX", "Integral transforms, operational calculus"),
    ("45-XX", "Integral equations"),
    ("46-XX", "Functional analysis"),
    ("47-XX", "Operator theory"),
    ("49-XX", "Calculus of variations and optimal control; optimization"),
    ("51-XX", "Geometry"),
    ("52-XX", "Convex and discrete geometry"),
    ("53-XX", "Differential geometry"),
    ("54-XX", "General topology"),
    ("55-XX", "Algebraic topology"),
    ("57-XX", "Manifolds and cell complexes"),
    ("58-XX", "Global analysis, analysis on manifolds"),
    ("60-XX", "Probability theory and stochastic processes"),
    ("62-XX", "Statistics"),
    ("65-XX", "Numerical analysis"),
    ("68-XX", "Computer science"),
    ("70-XX", "Mechanics of particles and systems"),
    ("74-XX", "Mechanics of deformable solids"),
    ("76-XX", "Fluid mechanics"),
    ("78-XX", "Optics, electromagnetic theory"),
    ("80-XX", "Classical thermodynamics, heat transfer"),
    ("81-XX", "Quantum theory"),
    ("82-XX", "Statistical mechanics, structure of matter"),
    ("83-XX", "Relativity and gravitational theory"),
    ("85-XX", "Astronomy and astrophysics"),
    ("86-XX", "Geophysics"),
    ("90-XX", "Operations research, mathematical programming"),
    ("91-XX", "Game theory, economics, finance, and other social sciences"),
    ("92-XX", "Biology and other natural sciences"),
    ("93-XX", "Systems theory; control"),
    ("94-XX", "Information and communication theory, circuits"),
    ("97-XX", "Mathematics education"),
]

# Hand-picked second-level "XX-YY" anchors that researchers most often use
# as filters. Not exhaustive; adds ~140 entries.
_MSC_SECOND: list[tuple[str, str]] = [
    # Number theory (11)
    ("11A", "Elementary number theory"),
    ("11B", "Sequences and sets"),
    ("11C", "Polynomials and matrices"),
    ("11D", "Diophantine equations"),
    ("11E", "Forms and linear algebraic groups"),
    ("11F", "Discontinuous groups and automorphic forms"),
    ("11G", "Arithmetic algebraic geometry (Diophantine geometry)"),
    ("11H", "Geometry of numbers"),
    ("11J", "Diophantine approximation, transcendental number theory"),
    ("11K", "Probabilistic theory: distribution modulo 1; metric theory of algorithms"),
    ("11L", "Exponential sums and character sums"),
    ("11M", "Zeta and L-functions: analytic theory"),
    ("11N", "Multiplicative number theory"),
    ("11P", "Additive number theory; partitions"),
    ("11R", "Algebraic number theory: global fields"),
    ("11S", "Algebraic number theory: local and p-adic fields"),
    ("11T", "Finite fields and commutative rings (number-theoretic aspects)"),
    ("11U", "Connections of number theory with logic"),
    ("11Y", "Computational number theory"),
    ("11Z", "Miscellaneous applications of number theory"),
    # Combinatorics (05)
    ("05A", "Enumerative combinatorics"),
    ("05B", "Designs and configurations"),
    ("05C", "Graph theory"),
    ("05D", "Extremal combinatorics"),
    ("05E", "Algebraic combinatorics"),
    # Algebraic geometry (14)
    ("14A", "Foundations of algebraic geometry"),
    ("14B", "Local theory in algebraic geometry"),
    ("14C", "Cycles and subschemes"),
    ("14D", "Families, fibrations in algebraic geometry"),
    ("14E", "Birational geometry"),
    ("14F", "(Co)homology theory in algebraic geometry"),
    ("14G", "Arithmetic problems in algebraic geometry; Diophantine geometry"),
    ("14H", "Curves in algebraic geometry"),
    ("14J", "Surfaces and higher-dimensional varieties"),
    ("14K", "Abelian varieties and schemes"),
    ("14L", "Algebraic groups"),
    ("14M", "Special varieties"),
    ("14N", "Projective and enumerative algebraic geometry"),
    ("14P", "Real algebraic and real-analytic geometry"),
    ("14Q", "Computational aspects in algebraic geometry"),
    ("14R", "Affine geometry"),
    ("14T", "Tropical geometry"),
    # Group theory (20)
    ("20A", "Foundations of group theory"),
    ("20B", "Permutation groups"),
    ("20C", "Representation theory of groups"),
    ("20D", "Abstract finite groups"),
    ("20E", "Structure and classification of infinite or finite groups"),
    ("20F", "Special aspects of infinite or finite groups"),
    ("20G", "Linear algebraic groups and related topics"),
    ("20H", "Other groups of matrices"),
    ("20J", "Connections of group theory with homological algebra and category theory"),
    ("20K", "Abelian groups"),
    ("20L", "Groupoids"),
    ("20M", "Semigroups"),
    ("20N", "Other generalizations of groups"),
    ("20P", "Probabilistic methods in group theory"),
    # Algebraic topology (55)
    ("55M", "Classical topics in algebraic topology"),
    ("55N", "Homology and cohomology theories"),
    ("55P", "Homotopy theory"),
    ("55Q", "Homotopy groups"),
    ("55R", "Fiber spaces and bundles in algebraic topology"),
    ("55S", "Operations and obstructions in algebraic topology"),
    ("55T", "Spectral sequences in algebraic topology"),
    ("55U", "Applied homological algebra and category theory"),
    # Manifolds (57)
    ("57K", "Low-dimensional topology in specific dimensions"),
    ("57M", "General low-dimensional topology"),
    ("57N", "Topological manifolds"),
    ("57P", "Generalized manifolds"),
    ("57Q", "PL-topology"),
    ("57R", "Differential topology"),
    ("57S", "Topological transformation groups"),
    ("57T", "Homology and homotopy of topological groups and related structures"),
    # Probability (60)
    ("60A", "Foundations of probability theory"),
    ("60B", "Probability theory on algebraic and topological structures"),
    ("60C", "Combinatorial probability"),
    ("60D", "Geometric probability and stochastic geometry"),
    ("60E", "Distribution theory"),
    ("60F", "Limit theorems in probability theory"),
    ("60G", "Stochastic processes"),
    ("60H", "Stochastic analysis"),
    ("60J", "Markov processes"),
    ("60K", "Special processes"),
    # Computer science (68)
    ("68M", "Computer system organization"),
    ("68N", "Theory of software"),
    ("68P", "Theory of data"),
    ("68Q", "Theory of computing"),
    ("68R", "Discrete mathematics in relation to computer science"),
    ("68T", "Artificial intelligence"),
    ("68U", "Computing methodologies and applications"),
    ("68V", "Computer science support for mathematical research and practice"),
    ("68W", "Algorithms"),
]


def msc_anchors() -> list[tuple[str, str]]:
    """Legacy curated anchor list as ``[(code, description), ...]``.

    Pre-#48 callers used ``msc_codes()`` (no args) to fetch ~200
    AMS-suffixed entries (top-level "11-XX" + section "11G" anchors).
    The new canonical entry point is ``msc_codes(level=...)`` over the
    full ~6000-leaf snapshot in ``_msc2020_data.py``; this function is
    kept for backward compatibility with cartography pipelines that
    still consume the (code, desc) tuple form.
    """
    return list(_MSC_TOP) + list(_MSC_SECOND)


# ---------------------------------------------------------------------------
# Cache management (mostly for tests / long-running processes)
# ---------------------------------------------------------------------------

def clear_cache() -> None:
    """Drop every cached response. Mostly useful in tests."""
    _cache.clear()


def cache_info() -> dict:
    """Diagnostics for the in-memory cache."""
    return {
        "entries":      len(_cache),
        "min_interval": _MIN_INTERVAL,
        "user_agent":   _USER_AGENT,
        "base":         _BASE,
    }


# ---------------------------------------------------------------------------
# Probe (for registry.py)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check used by prometheus_math.registry.

    Hits the search endpoint with a minimal query and tight timeout.
    Returns True iff the API responded with a 200 and a JSON envelope
    we recognize.
    """
    try:
        # `an:` is the zbMATH "accession number" field; an exact-id query
        # gives a cheap, deterministic round-trip without hitting the
        # 404-on-nothing-found branch the bare-id form takes.
        r = requests.get(
            f"{_BASE}/document/_search",
            params={"search_string": "an:0823.11029", "results_per_page": "1"},
            headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException:
        return False
    if r.status_code != 200:
        return False
    try:
        data = r.json()
    except ValueError:
        return False
    return isinstance(data, dict) and ("result" in data or "status" in data)
