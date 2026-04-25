"""OEIS — Online Encyclopedia of Integer Sequences wrapper.

The OEIS (https://oeis.org) is a curated database of ~370,000 integer
sequences, with formulas, generating programs, citations, and dense
cross-references. It is the canonical reference for the question
"is the sequence I just computed already known?", which is the central
move of Prometheus's conjecture-seeding workflow (Aporia, Charon,
Cartography all hit this).

The public API is JSON over HTTPS; no authentication required, but the
host is fronted by Cloudflare and rate-limits aggressive callers. This
wrapper:

  * Pins a polite User-Agent identifying Prometheus.
  * Throttles to <= 1 request/sec per process.
  * Caches responses in-memory for the life of the process. Cache keys
    are the canonical query strings, so repeated lookups of the same
    A-number or sequence prefix do NOT re-hit the network.
  * Returns None / [] on network errors rather than raising — callers
    in research pipelines should be able to "ask OEIS but keep going".

Public surface:

    lookup(a_number)         -> dict | None        # by A-number
    search(terms=None,
           sequence=None,
           max_results=20,
           start=0)          -> list[dict]         # full-text or value search
    find_sequence(values,
                  max_results=10) -> list[dict]    # convenience wrapper
    get_data(a_number)       -> list[int]
    cross_refs(a_number)     -> list[str]
    b_file(a_number,
           max_terms=None)   -> list[tuple[int,int]]
    is_known(values)         -> str | None         # A-number or None

The dict shape returned by `lookup()` and items in `search()`/
`find_sequence()` results:

    {
        "number":      "A000045",                # canonical, zero-padded
        "name":        "Fibonacci numbers: ...",
        "data":        [0, 1, 1, 2, 3, 5, 8, ...],
        "formula":     ["a(n) = a(n-1) + a(n-2)", ...],
        "program":     ["(PARI) a(n) = ...", ...],
        "keywords":    ["nonn", "core", "easy", ...],
        "references":  ["D. E. Knuth, ...", ...],
        "cross_refs":  ["A000032", "A000204", ...],   # A-numbers
        "offset":      (0, 3),                   # (offset, sign-change-after)
        "author":      "N. J. A. Sloane, ...",
    }
"""
from __future__ import annotations

import re
import threading
import time
from typing import Any, Iterable, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_BASE = "https://oeis.org"
_USER_AGENT = "prometheus-math/0.1 (mathematical research tool)"
_DEFAULT_TIMEOUT = 15.0  # seconds
_MIN_INTERVAL = 1.0      # seconds between requests

# Throttle state — module-level so all callers share it.
_lock = threading.Lock()
_last_request_ts: float = 0.0

# Cache: maps cache-key (str) -> response payload (parsed JSON or text).
# Two separate caches keep the lookup logic uniform.
#   _json_cache:   key="search:<query>:<start>"  ->  list[dict] | None
#   _bfile_cache:  key="bfile:<A-number>"        ->  str (raw text) | None
_json_cache: dict[str, Any] = {}
_bfile_cache: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_A_RE = re.compile(r"A0*(\d+)")


def _normalize_a_number(a_number) -> str:
    """Coerce 45, 'a45', 'A45', 'A000045' all to canonical 'A000045'."""
    if isinstance(a_number, int):
        n = a_number
    else:
        s = str(a_number).strip().upper()
        if s.startswith("A"):
            s = s[1:]
        if not s.isdigit():
            raise ValueError(f"not a valid A-number: {a_number!r}")
        n = int(s)
    if n < 0 or n > 9_999_999:
        raise ValueError(f"A-number out of range: {a_number!r}")
    return f"A{n:06d}"


def _throttle() -> None:
    """Sleep so we don't exceed _MIN_INTERVAL between OEIS requests."""
    global _last_request_ts
    with _lock:
        delta = time.monotonic() - _last_request_ts
        if delta < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - delta)
        _last_request_ts = time.monotonic()


def _http_get(url: str, params: Optional[dict] = None,
              accept_json: bool = True) -> Optional[requests.Response]:
    """Perform a polite, throttled GET. Returns Response or None on failure."""
    _throttle()
    headers = {"User-Agent": _USER_AGENT}
    if accept_json:
        headers["Accept"] = "application/json"
    try:
        r = requests.get(url, params=params, headers=headers,
                         timeout=_DEFAULT_TIMEOUT)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    return r


def _parse_data_field(s: str) -> list[int]:
    """OEIS 'data' is a comma-separated string of integers."""
    if not s:
        return []
    out: list[int] = []
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            out.append(int(tok))
        except ValueError:
            # Some sequences include things like 'inf' or fractions; skip.
            continue
    return out


def _parse_offset(s: str) -> tuple:
    """OEIS 'offset' is e.g. '0,3' meaning offset=0, first |a(n)|>1 at n=3."""
    if not s:
        return ()
    parts = []
    for tok in s.split(","):
        tok = tok.strip()
        try:
            parts.append(int(tok))
        except ValueError:
            pass
    return tuple(parts)


def _extract_cross_refs(xref_lines: Iterable[str]) -> list[str]:
    """Pull all A-numbers mentioned in xref lines, deduped, in order."""
    seen: set[str] = set()
    out: list[str] = []
    for line in xref_lines or []:
        for m in _A_RE.finditer(line):
            try:
                an = _normalize_a_number(m.group(0))
            except ValueError:
                continue
            if an not in seen:
                seen.add(an)
                out.append(an)
    return out


def _shape_entry(entry: dict) -> dict:
    """Convert a raw OEIS JSON entry to our normalized dict shape."""
    num = entry.get("number")
    if isinstance(num, int):
        a_id = f"A{num:06d}"
    else:
        a_id = _normalize_a_number(num) if num is not None else ""
    return {
        "number":     a_id,
        "name":       entry.get("name", ""),
        "data":       _parse_data_field(entry.get("data", "")),
        "formula":    list(entry.get("formula", []) or []),
        "program":    list(entry.get("program", []) or []),
        "keywords":   [k.strip() for k in (entry.get("keyword", "") or "").split(",") if k.strip()],
        "references": list(entry.get("reference", []) or []),
        "cross_refs": _extract_cross_refs(entry.get("xref", []) or []),
        "offset":     _parse_offset(entry.get("offset", "")),
        "author":     entry.get("author", ""),
    }


def _do_search(query: str, start: int = 0) -> Optional[list[dict]]:
    """Hit /search?q=<query>&fmt=json&start=<n>. Cached."""
    key = f"search:{query}:{start}"
    if key in _json_cache:
        return _json_cache[key]

    r = _http_get(f"{_BASE}/search",
                  params={"q": query, "fmt": "json", "start": start})
    if r is None:
        _json_cache[key] = None
        return None
    try:
        payload = r.json()
    except ValueError:
        _json_cache[key] = None
        return None
    # The API returns either {"results": [...]} or {"results": null} for misses.
    results = payload.get("results") or []
    _json_cache[key] = results
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def lookup(a_number) -> Optional[dict]:
    """Fetch one sequence by A-number.

    Accepts: 'A000045', 'a45', 45 (int).  Returns the normalized dict
    described in the module docstring, or None if not found / network error.
    """
    a_id = _normalize_a_number(a_number)
    results = _do_search(f"id:{a_id}")
    if not results:
        return None
    # Take exact match if present; otherwise first.
    for entry in results:
        shaped = _shape_entry(entry)
        if shaped["number"] == a_id:
            return shaped
    return _shape_entry(results[0])


def search(terms: Optional[str] = None,
           sequence: Optional[Iterable[int]] = None,
           max_results: int = 20,
           start: int = 0) -> list[dict]:
    """Search OEIS by free-text or by leading sequence values.

    Provide exactly one of `terms` or `sequence`.

    `sequence` is the most powerful query OEIS supports: pass the first
    handful of computed integers and OEIS returns matching sequences.
    """
    if (terms is None) == (sequence is None):
        raise ValueError("exactly one of `terms` or `sequence` must be given")

    if sequence is not None:
        seq_list = list(sequence)
        if not seq_list:
            return []
        # OEIS accepts comma-separated digits: "1,1,2,3,5,8".
        query = ",".join(str(int(x)) for x in seq_list)
    else:
        query = str(terms)

    results: list[dict] = []
    cur = start
    while len(results) < max_results:
        page = _do_search(query, start=cur)
        if not page:
            break
        for entry in page:
            results.append(_shape_entry(entry))
            if len(results) >= max_results:
                break
        # OEIS pages are 10 entries; if we got fewer it's the last page.
        if len(page) < 10:
            break
        cur += 10
    return results


def find_sequence(values: Iterable[int], max_results: int = 10) -> list[dict]:
    """Convenience: 'I have these N integers — what sequences match?'."""
    return search(sequence=values, max_results=max_results)


def get_data(a_number) -> list[int]:
    """Just the numeric data of a sequence (the 30-50 'data' terms)."""
    rec = lookup(a_number)
    return rec["data"] if rec else []


def cross_refs(a_number) -> list[str]:
    """A-numbers cross-referenced from this sequence."""
    rec = lookup(a_number)
    return rec["cross_refs"] if rec else []


def b_file(a_number, max_terms: Optional[int] = None) -> list[tuple[int, int]]:
    """Fetch the b-file of an OEIS sequence.

    B-files contain the extended terms of a sequence — typically hundreds
    to thousands, vs. the 30-50 in the main 'data' field. Format is
    plain ASCII, "<index> <value>" per line, with comments starting '#'.

    Returns [(index, value), ...]. Empty list on miss / network error.
    """
    a_id = _normalize_a_number(a_number)
    key = f"bfile:{a_id}"
    if key in _bfile_cache:
        text = _bfile_cache[key]
    else:
        # The convention is /A000045/b000045.txt — note the lowercase b
        # and 6-digit number without the leading 'A'.
        digits = a_id[1:]
        url = f"{_BASE}/{a_id}/b{digits}.txt"
        r = _http_get(url, accept_json=False)
        text = r.text if r is not None else None
        _bfile_cache[key] = text

    if not text:
        return []

    out: list[tuple[int, int]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        try:
            idx = int(parts[0])
            val = int(parts[1])
        except ValueError:
            continue
        out.append((idx, val))
        if max_terms is not None and len(out) >= max_terms:
            break
    return out


def is_known(values: Iterable[int]) -> Optional[str]:
    """Quick 'is this prefix in OEIS?' — returns best-match A-number or None.

    The "best match" is OEIS's own ranking: the first result of the
    sequence-search call. Useful for one-line conjecture checks:

        >>> is_known([1, 1, 2, 3, 5, 8, 13])
        'A000045'
    """
    hits = find_sequence(values, max_results=1)
    if not hits:
        return None
    return hits[0]["number"] or None


# ---------------------------------------------------------------------------
# Cache management (mostly for tests / long-running processes)
# ---------------------------------------------------------------------------

def clear_cache() -> None:
    """Drop every cached response. Mostly useful in tests."""
    _json_cache.clear()
    _bfile_cache.clear()


def cache_info() -> dict:
    """Diagnostics for the in-memory cache."""
    return {
        "json_entries":  len(_json_cache),
        "bfile_entries": len(_bfile_cache),
        "min_interval":  _MIN_INTERVAL,
        "user_agent":    _USER_AGENT,
    }


# ---------------------------------------------------------------------------
# Probe (for registry.py)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check used by prometheus_math.registry.

    Hits the search endpoint with a tiny query and a tight timeout. Does
    not respect the 1-req/sec throttle — registry probes run once at
    import time.
    """
    try:
        r = requests.get(
            f"{_BASE}/search",
            params={"q": "id:A000045", "fmt": "json"},
            headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException:
        return False
    return r.status_code == 200
