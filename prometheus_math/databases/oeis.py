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

import datetime as _dt
import gzip
import json
import logging
import pathlib
import re
import threading
import time
from typing import Any, Iterable, Optional

import requests

from . import _local

_log = logging.getLogger(__name__)

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
# Local mirror state
# ---------------------------------------------------------------------------
#
# OEIS publishes two bulk dump files that are NOT Cloudflare-gated:
#   * https://oeis.org/stripped.gz  — A-num + 30-50 leading terms per sequence
#   * https://oeis.org/names.gz     — A-num<TAB>name
#
# Once mirrored locally these resolve `lookup()`, `find_sequence()`, and
# `is_known()` calls without ever touching the network.  Other fields
# (formula, program, keywords, references, cross_refs, offset, author)
# are NOT in the bulk dumps; for those callers must fall through to the
# live API or accept the partial record.

_OEIS_DATASET = "oeis"
_OEIS_FILES = {
    "stripped.gz": "https://oeis.org/stripped.gz",
    "names.gz":    "https://oeis.org/names.gz",
}

# A-NUM -> {"data": [int, ...], "name": str}
_OEIS_LOCAL_CACHE: dict[str, dict] = {}
# Reverse index: tuple of leading values -> A-NUM (built lazily for
# find_sequence / is_known).
_OEIS_PREFIX_INDEX: dict[tuple, str] = {}
_OEIS_LOCAL_LOADED = False
_OEIS_LOCAL_LOCK = threading.Lock()
_OEIS_USE_LOCAL_FIRST: Optional[bool] = None  # None = auto-detect


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

    Resolution priority:
      1. Local mirror (stripped.gz + names.gz) when present and
         use_local_first() is True.  Returns a partial dict — only
         `number`, `name`, and `data` are populated; other fields are
         empty/None because they are not in the bulk dumps.
      2. Live OEIS HTTPS API.
    """
    a_id = _normalize_a_number(a_number)

    if has_local_mirror() and use_local_first():
        local = _local_lookup(a_id)
        if local is not None:
            return local

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
    """Convenience: 'I have these N integers — what sequences match?'.

    Resolution priority:
      1. Local mirror prefix index (when present and use_local_first()).
      2. Live OEIS sequence search.
    """
    seq = [int(v) for v in values]
    if not seq:
        return []
    if has_local_mirror() and use_local_first():
        local_hits = _local_find_sequence(seq, max_results=max_results)
        if local_hits:
            return local_hits
    return search(sequence=seq, max_results=max_results)


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

    Resolution priority:
      1. Local mirror prefix lookup.
      2. Live OEIS search (delegated through `find_sequence`).

    Useful for one-line conjecture checks:

        >>> is_known([1, 1, 2, 3, 5, 8, 13])
        'A000045'
    """
    seq = [int(v) for v in values]
    if not seq:
        return None
    if has_local_mirror() and use_local_first():
        a = _local_is_known(seq)
        if a is not None:
            return a
    hits = find_sequence(seq, max_results=1)
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

    Returns True if EITHER a local mirror is present OR the live
    HTTPS endpoint responds.  Cloudflare-blocked networks therefore
    still report OEIS as available so long as `update_mirror()` has
    been run at least once.
    """
    if has_local_mirror():
        return True
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


# ---------------------------------------------------------------------------
# Local mirror — public API
# ---------------------------------------------------------------------------

def _parse_stripped_line(line: str) -> Optional[tuple[str, list[int]]]:
    """Parse one line of stripped.gz: ``A000045 ,0,1,1,2,3,5,...,``.

    Returns (a_number, [int, ...]) or None on malformed lines.
    Lines beginning with '#' are comments.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Split on first whitespace to separate the A-num from the data.
    parts = line.split(None, 1)
    if len(parts) != 2:
        return None
    a_id, body = parts
    if not (a_id.startswith("A") and a_id[1:].isdigit()):
        return None
    body = body.strip().strip(",")
    if not body:
        return (a_id, [])
    out: list[int] = []
    for tok in body.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            out.append(int(tok))
        except ValueError:
            # Some sequences carry signs or unparseable cells; skip silently.
            continue
    return (a_id, out)


def _parse_names_line(line: str) -> Optional[tuple[str, str]]:
    """Parse one line of names.gz: ``A000045\tFibonacci numbers: ...``."""
    line = line.rstrip("\n").rstrip("\r")
    if not line or line.startswith("#"):
        return None
    # Names file is TAB-delimited.
    if "\t" in line:
        a_id, name = line.split("\t", 1)
    else:
        # Fallback: first token + rest.
        parts = line.split(None, 1)
        if len(parts) != 2:
            return None
        a_id, name = parts
    a_id = a_id.strip()
    if not (a_id.startswith("A") and a_id[1:].isdigit()):
        return None
    return (a_id, name.strip())


def _load_local_cache(stripped: pathlib.Path,
                      names: pathlib.Path) -> int:
    """Populate _OEIS_LOCAL_CACHE from the gz dumps.  Returns N loaded."""
    _OEIS_LOCAL_CACHE.clear()
    _OEIS_PREFIX_INDEX.clear()
    with gzip.open(stripped, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parsed = _parse_stripped_line(line)
            if parsed is None:
                continue
            a_id, data = parsed
            _OEIS_LOCAL_CACHE[a_id] = {"data": data, "name": ""}
    if names.exists():
        with gzip.open(names, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                parsed = _parse_names_line(line)
                if parsed is None:
                    continue
                a_id, name = parsed
                if a_id in _OEIS_LOCAL_CACHE:
                    _OEIS_LOCAL_CACHE[a_id]["name"] = name
                else:
                    _OEIS_LOCAL_CACHE[a_id] = {"data": [], "name": name}
    return len(_OEIS_LOCAL_CACHE)


def _ensure_local_mirror(force: bool = False) -> bool:
    """Download stripped.gz + names.gz if absent; parse into the cache.

    Returns True iff the cache is loaded and non-empty after the call.
    Network failures are logged, not raised.
    """
    global _OEIS_LOCAL_LOADED
    with _OEIS_LOCAL_LOCK:
        if _OEIS_LOCAL_LOADED and not force and _OEIS_LOCAL_CACHE:
            return True
        try:
            base = _local.fetch_dataset(_OEIS_DATASET, _OEIS_FILES, force=force)
        except Exception as e:
            _log.warning("OEIS mirror download failed: %s", e)
            return False
        stripped = base / "stripped.gz"
        names = base / "names.gz"
        if not stripped.exists():
            _log.warning("OEIS mirror missing stripped.gz at %s", stripped)
            return False
        try:
            n = _load_local_cache(stripped, names)
        except Exception as e:
            _log.warning("OEIS mirror parse failed: %s", e)
            return False
        _OEIS_LOCAL_LOADED = n > 0
        return _OEIS_LOCAL_LOADED


def _autoload_if_present() -> None:
    """If the dump files are already on disk, parse them lazily — no network."""
    global _OEIS_LOCAL_LOADED
    if _OEIS_LOCAL_LOADED:
        return
    with _OEIS_LOCAL_LOCK:
        if _OEIS_LOCAL_LOADED:
            return
        if not _local.has_mirror(_OEIS_DATASET, "stripped.gz"):
            return
        base = _local.dataset_path(_OEIS_DATASET)
        try:
            n = _load_local_cache(base / "stripped.gz", base / "names.gz")
        except Exception as e:
            _log.warning("OEIS mirror auto-load failed: %s", e)
            return
        _OEIS_LOCAL_LOADED = n > 0


def has_local_mirror() -> bool:
    """True iff the OEIS local mirror is parsed and ready to serve lookups."""
    if _OEIS_LOCAL_LOADED and _OEIS_LOCAL_CACHE:
        return True
    # Lazy: auto-load if the files exist on disk.
    _autoload_if_present()
    return _OEIS_LOCAL_LOADED and bool(_OEIS_LOCAL_CACHE)


def use_local_first(value: Optional[bool] = None) -> bool:
    """Get or set the global local-first flag.

    With no argument, returns the current effective value (auto-detected
    from `has_local_mirror()` if never explicitly set).  With an argument,
    sets and returns the new value.
    """
    global _OEIS_USE_LOCAL_FIRST
    if value is not None:
        _OEIS_USE_LOCAL_FIRST = bool(value)
        return _OEIS_USE_LOCAL_FIRST
    if _OEIS_USE_LOCAL_FIRST is None:
        # Don't trigger autoload here — has_local_mirror handles that.
        return has_local_mirror()
    return _OEIS_USE_LOCAL_FIRST


def _local_record(a_id: str) -> Optional[dict]:
    """Shape a local-mirror entry into the same dict layout as `lookup()`."""
    rec = _OEIS_LOCAL_CACHE.get(a_id)
    if rec is None:
        return None
    return {
        "number":     a_id,
        "name":       rec.get("name", ""),
        "data":       list(rec.get("data", []) or []),
        "formula":    [],
        "program":    [],
        "keywords":   [],
        "references": [],
        "cross_refs": [],
        "offset":     (),
        "author":     "",
    }


def _local_lookup(a_number) -> Optional[dict]:
    """Look up one A-number in the local mirror."""
    if not has_local_mirror():
        return None
    a_id = _normalize_a_number(a_number)
    return _local_record(a_id)


def _local_find_sequence(values: list[int],
                         max_results: int = 10,
                         min_match: int = 4) -> list[dict]:
    """Brute-force scan of the local mirror for sequences whose `data`
    field contains `values` as a contiguous prefix or substring.

    The OEIS bulk dumps include only 30-50 leading terms per sequence,
    so we scan for occurrences anywhere in those terms (covers offset
    differences).  Sequences whose own first values match are ranked
    above those matching mid-stream.
    """
    if not has_local_mirror():
        return []
    if len(values) < min_match:
        # Don't return everything for tiny prefixes — too noisy.
        min_match = max(1, len(values))
    target = tuple(values)
    L = len(target)
    prefix_hits: list[str] = []
    sub_hits: list[str] = []
    for a_id, rec in _OEIS_LOCAL_CACHE.items():
        data = rec.get("data") or []
        if len(data) < L:
            continue
        if tuple(data[:L]) == target:
            prefix_hits.append(a_id)
            continue
        # Substring scan (cheap; data is short).
        for i in range(1, len(data) - L + 1):
            if tuple(data[i:i + L]) == target:
                sub_hits.append(a_id)
                break
    # Sort each tier by A-number ascending so the canonical (older) entry
    # wins ties — matches the spirit of OEIS's own ranking.
    prefix_hits.sort()
    sub_hits.sort()
    ordered = prefix_hits + sub_hits
    out: list[dict] = []
    for a_id in ordered[:max_results]:
        rec = _local_record(a_id)
        if rec is not None:
            out.append(rec)
    return out


def _local_is_known(values: list[int]) -> Optional[str]:
    hits = _local_find_sequence(values, max_results=1)
    if not hits:
        return None
    return hits[0]["number"]


_METADATA_FILE = ".metadata.json"


def _metadata_path() -> pathlib.Path:
    """Absolute path to the on-disk metadata sidecar."""
    return _local.dataset_path(_OEIS_DATASET) / _METADATA_FILE


def _empty_metadata() -> dict:
    """Default skeleton when no mirror exists yet."""
    return {
        "sequences":        0,
        "last_refresh_iso": None,
        "files":            [],
        "size_bytes":       0,
    }


def mirror_metadata() -> dict:
    """Read (or synthesize) the OEIS mirror metadata sidecar.

    Returns a dict with stable keys:

        {"sequences":        int,                # count of A-numbers loaded
         "last_refresh_iso": str | None,         # ISO 8601 UTC timestamp
         "files":            [str, ...],         # filenames present
         "size_bytes":       int}                # bytes on disk

    When the on-disk ``.metadata.json`` is missing, returns the in-memory
    state if a mirror is loaded (so CI can still produce a delta), or
    the empty default otherwise.  Never raises on a corrupt file — falls
    back to the empty default and logs a warning.
    """
    path = _metadata_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            _log.warning("OEIS metadata read failed: %s", e)
        else:
            # Be defensive about partial / future-format files.
            out = _empty_metadata()
            out.update({k: data.get(k, out[k]) for k in out})
            return out

    # No sidecar: synthesize from in-memory + on-disk size.
    base = _local.dataset_path(_OEIS_DATASET)
    files: list[str] = []
    if base.is_dir():
        for fn in sorted(_OEIS_FILES.keys()):
            if (base / fn).is_file():
                files.append(fn)
    out = _empty_metadata()
    out["sequences"] = len(_OEIS_LOCAL_CACHE)
    out["files"] = files
    out["size_bytes"] = _local.mirror_size(_OEIS_DATASET)
    return out


def _write_metadata(meta: dict) -> None:
    """Atomic write of the metadata sidecar."""
    path = _metadata_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    import os as _os
    _os.replace(tmp, path)


def update_mirror(force: bool = False) -> dict:
    """Refresh the OEIS local mirror.

    Downloads `stripped.gz` and `names.gz` (if missing or `force=True`)
    and reparses them into memory.  Returns a small status dict suitable
    for printing or logging:

        {"sequences_loaded": 372031,
         "files":            ["stripped.gz", "names.gz"],
         "size_bytes":       57_344_120,
         "refreshed_at":     "2026-04-22T18:33:09+00:00"}

    On success the on-disk ``.metadata.json`` is rewritten with the
    new sequence count, refresh timestamp, file list, and size.
    Network failures populate the dict with `error` and leave any
    previously-loaded cache (and prior metadata) intact.
    """
    started = _dt.datetime.now(_dt.timezone.utc).isoformat()
    ok = _ensure_local_mirror(force=force)
    files = sorted(_OEIS_FILES.keys())
    base = _local.dataset_path(_OEIS_DATASET)
    present = [fn for fn in files if (base / fn).is_file()] if base.is_dir() else []
    size = _local.mirror_size(_OEIS_DATASET)
    out: dict = {
        "sequences_loaded": len(_OEIS_LOCAL_CACHE),
        "files":            files,
        "size_bytes":       size,
        "refreshed_at":     started,
    }
    if not ok:
        out["error"] = "mirror not loaded (see warnings)"
        return out
    # Persist the metadata sidecar so the CI job can compute deltas.
    try:
        _write_metadata({
            "sequences":        len(_OEIS_LOCAL_CACHE),
            "last_refresh_iso": started,
            "files":            present,
            "size_bytes":       size,
        })
    except OSError as e:
        _log.warning("OEIS metadata write failed: %s", e)
    return out


