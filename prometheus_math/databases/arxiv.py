"""arXiv — Cornell preprint server wrapper.

arXiv (https://arxiv.org) is the universal preprint server for mathematics,
physics, computer science, and adjacent fields. It hosts ~2.5M papers
accessible through a clean public API, and is the primary literature
source for Prometheus's research workflows: Aporia uses it to crawl
recent results around its open questions, Cartography uses it to surface
related work for emerging concepts, and Charon checks it before claiming
priority on conjectures.

This module wraps the well-maintained `arxiv` pip package, normalizing
results to plain `dict`s so callers don't depend on third-party types.
The third-party client handles its own polite rate-limiting (it sleeps
~3s between paginated requests by default), so this wrapper does not add
its own throttle — instead it tunes the client's parameters and converts
errors to None / [].

Public surface:

    search(query, max_results=20, sort_by='relevance',
           categories=None)            -> list[dict]
    get(arxiv_id)                      -> dict | None
    download_pdf(arxiv_id,
                 dirpath='.',
                 filename=None)        -> str
    recent(category, max_results=50,
           days=7)                     -> list[dict]
    by_author(author_name,
              max_results=50)          -> list[dict]
    by_category(category,
                max_results=100,
                year=None)             -> list[dict]
    latex_source(arxiv_id,
                 dirpath='.')          -> str
    probe(timeout=3.0)                 -> bool

Result dict shape (returned by `search()`, `get()`, `recent()`, ...):

    {
        "id":               "2410.12345",        # short id, no version
        "title":            "On the modularity of ...",
        "authors":          ["Alice Smith", ...],
        "abstract":         "We show that ...",
        "categories":       ["math.NT", "math.AG"],
        "primary_category": "math.NT",
        "published":        "2024-10-15T00:00:00+00:00",  # ISO 8601
        "updated":          "2024-10-20T00:00:00+00:00",
        "pdf_url":          "https://arxiv.org/pdf/2410.12345",
        "entry_url":        "http://arxiv.org/abs/2410.12345v2",
        "comment":          "32 pages, 4 figures",
        "journal_ref":      "Compositio Math. 160 (2024)",
        "doi":              "10.1112/...",
    }
"""
from __future__ import annotations

import datetime as _dt
from typing import Iterable, Optional

try:
    import arxiv as _arxiv  # third-party `arxiv` pip package
except ImportError:  # pragma: no cover
    _arxiv = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Reuse a single Client across calls so its internal rate-limiter is shared.
# The `arxiv` library defaults to delay_seconds=3.0 which is the rate the
# arXiv API operators have asked for. We keep that.
_DEFAULT_PAGE_SIZE = 100
_DEFAULT_DELAY = 3.0
_DEFAULT_RETRIES = 3

_client: "Optional[_arxiv.Client]" = None


def _get_client() -> "Optional[_arxiv.Client]":
    global _client
    if _arxiv is None:
        return None
    if _client is None:
        _client = _arxiv.Client(
            page_size=_DEFAULT_PAGE_SIZE,
            delay_seconds=_DEFAULT_DELAY,
            num_retries=_DEFAULT_RETRIES,
        )
    return _client


_SORT_MAP = {
    "relevance": "Relevance",
    "submittedDate": "SubmittedDate",
    "submitted_date": "SubmittedDate",
    "lastUpdatedDate": "LastUpdatedDate",
    "last_updated_date": "LastUpdatedDate",
    "updated": "LastUpdatedDate",
    "submitted": "SubmittedDate",
}


def _resolve_sort(sort_by: str):
    if _arxiv is None:
        return None
    name = _SORT_MAP.get(sort_by, sort_by)
    try:
        return getattr(_arxiv.SortCriterion, name)
    except AttributeError:
        return _arxiv.SortCriterion.Relevance


# ---------------------------------------------------------------------------
# Result shaping
# ---------------------------------------------------------------------------

def _shape_result(r) -> dict:
    """Convert an `arxiv.Result` to a plain dict."""
    # `r.published` and `r.updated` are timezone-aware datetimes.
    published = r.published.isoformat() if isinstance(r.published, _dt.datetime) else None
    updated = r.updated.isoformat() if isinstance(r.updated, _dt.datetime) else None

    short_id = r.get_short_id() if hasattr(r, "get_short_id") else ""
    # Strip trailing version (e.g. '2410.12345v2' -> '2410.12345').
    if short_id and "v" in short_id:
        head, _, tail = short_id.rpartition("v")
        if tail.isdigit():
            short_id = head

    return {
        "id":               short_id,
        "title":            (r.title or "").strip().replace("\n", " "),
        "authors":          [str(a) for a in (r.authors or [])],
        "abstract":         (r.summary or "").strip(),
        "categories":       list(r.categories or []),
        "primary_category": r.primary_category or "",
        "published":        published,
        "updated":          updated,
        "pdf_url":          r.pdf_url or "",
        "entry_url":        r.entry_id or "",
        "comment":          r.comment or "",
        "journal_ref":      r.journal_ref or "",
        "doi":              r.doi or "",
    }


def _normalize_id(arxiv_id) -> str:
    """Strip any trailing version suffix and surrounding whitespace."""
    s = str(arxiv_id).strip()
    if s.startswith("arXiv:"):
        s = s[len("arXiv:"):]
    # Old-style: math.NT/0501234. New-style: 2410.12345 (with optional vN).
    if "v" in s:
        head, _, tail = s.rpartition("v")
        if tail.isdigit():
            s = head
    return s


def _build_query(query: Optional[str],
                 categories: Optional[Iterable[str]] = None) -> str:
    """Combine a free-text query with optional category filters.

    arXiv's query syntax uses `AND`, `OR`, `ANDNOT`. Categories are
    expressed as `cat:math.NT`. We build:

        (<query>) AND (cat:math.NT OR cat:math.AG)
    """
    parts: list[str] = []
    q = (query or "").strip()
    if q:
        parts.append(f"({q})" if categories else q)
    if categories:
        cats = [c.strip() for c in categories if c and str(c).strip()]
        if cats:
            cat_q = " OR ".join(f"cat:{c}" for c in cats)
            parts.append(f"({cat_q})")
    return " AND ".join(parts) if parts else "*"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search(query: str,
           max_results: int = 20,
           sort_by: str = "relevance",
           categories: Optional[Iterable[str]] = None) -> list[dict]:
    """Free-text search of arXiv.

    `query` can include arXiv field prefixes, for example::

        search('au:Tao')
        search('ti:zeta cat:math.NT')
        search('Riemann hypothesis', categories=['math.NT'])

    sort_by    : 'relevance' | 'submittedDate' | 'lastUpdatedDate'
    categories : optional list to AND onto the query, e.g.
                 ['math.NT', 'math.AG'].

    Returns a list of dicts (see module docstring). On network error,
    returns an empty list.
    """
    client = _get_client()
    if client is None:
        return []

    full_query = _build_query(query, categories)
    sort = _resolve_sort(sort_by)
    try:
        s = _arxiv.Search(
            query=full_query,
            max_results=max_results,
            sort_by=sort,
        )
        out: list[dict] = []
        for r in client.results(s):
            out.append(_shape_result(r))
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def get(arxiv_id) -> Optional[dict]:
    """Fetch metadata for a single arXiv paper by id.

    Accepts modern ids ('2410.12345', '2410.12345v2') and legacy ids
    ('math.NT/0501234'). Returns the normalized dict, or None on miss
    or network error.
    """
    client = _get_client()
    if client is None:
        return None
    aid = _normalize_id(arxiv_id)
    try:
        s = _arxiv.Search(id_list=[aid], max_results=1)
        for r in client.results(s):
            return _shape_result(r)
        return None
    except Exception:
        return None


def download_pdf(arxiv_id,
                 dirpath: str = ".",
                 filename: Optional[str] = None) -> Optional[str]:
    """Download the PDF for a paper to `dirpath`.

    Returns the saved path on success, None on failure. The default
    filename is ``<arxiv_id>.pdf``. The underlying `arxiv` client uses
    its own rate limiter; do not call this in tight loops.
    """
    client = _get_client()
    if client is None:
        return None
    aid = _normalize_id(arxiv_id)
    if filename is None:
        filename = f"{aid}.pdf"
    try:
        s = _arxiv.Search(id_list=[aid], max_results=1)
        for r in client.results(s):
            return r.download_pdf(dirpath=dirpath, filename=filename)
        return None
    except Exception:
        return None


def recent(category: str,
           max_results: int = 50,
           days: int = 7) -> list[dict]:
    """Recent papers in `category`, sorted by submission date (newest first).

    `category` is a single arXiv category string ('math.NT', 'cs.LG', ...).
    `days` filters the returned list to papers submitted within the last
    N days (relative to today, UTC).
    """
    if not category:
        return []
    client = _get_client()
    if client is None:
        return []

    # Pull more than max_results when we need to date-filter, since some
    # of the newest entries may be category-cross posts older than `days`.
    fetch = max_results if days <= 0 else max(max_results * 3, max_results + 50)
    try:
        s = _arxiv.Search(
            query=f"cat:{category}",
            max_results=fetch,
            sort_by=_arxiv.SortCriterion.SubmittedDate,
            sort_order=_arxiv.SortOrder.Descending,
        )
        out: list[dict] = []
        cutoff: Optional[_dt.datetime] = None
        if days > 0:
            now = _dt.datetime.now(_dt.timezone.utc)
            cutoff = now - _dt.timedelta(days=days)
        for r in client.results(s):
            if cutoff is not None and isinstance(r.published, _dt.datetime):
                if r.published < cutoff:
                    # Sorted descending — once we cross the cutoff we're done.
                    break
            out.append(_shape_result(r))
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def by_author(author_name: str, max_results: int = 50) -> list[dict]:
    """Papers by an author, e.g. 'Terence Tao'.

    Wraps the arXiv `au:` field. arXiv's author indexing is fuzzy — the
    search treats this as substring/keyword matching on the author list,
    not as a strict identity. Use the returned `authors` field to
    disambiguate downstream.
    """
    if not author_name:
        return []
    # arXiv's au: field uses keyword matching; quoting helps with multi-word
    # names ("Terence Tao" -> au:"Terence Tao").
    name = author_name.strip()
    if " " in name and not (name.startswith('"') and name.endswith('"')):
        q = f'au:"{name}"'
    else:
        q = f"au:{name}"
    return search(q,
                  max_results=max_results,
                  sort_by="submittedDate")


def by_category(category: str,
                max_results: int = 100,
                year: Optional[int] = None) -> list[dict]:
    """Papers in a single arXiv category, optionally filtered by year.

    `year` filters by the calendar year of the `published` timestamp.
    Sorting is by submission date, newest first.
    """
    if not category:
        return []
    client = _get_client()
    if client is None:
        return []

    fetch = max_results if year is None else max(max_results * 3, max_results + 50)
    try:
        s = _arxiv.Search(
            query=f"cat:{category}",
            max_results=fetch,
            sort_by=_arxiv.SortCriterion.SubmittedDate,
            sort_order=_arxiv.SortOrder.Descending,
        )
        out: list[dict] = []
        for r in client.results(s):
            if year is not None and isinstance(r.published, _dt.datetime):
                if r.published.year > year:
                    continue
                if r.published.year < year:
                    # Descending sort — older years are past the window.
                    break
            out.append(_shape_result(r))
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def latex_source(arxiv_id, dirpath: str = ".") -> Optional[str]:
    """Download the LaTeX source tarball (`.tar.gz`) for a paper.

    Useful for AI training, formalization-tool ingestion, and recovering
    the original equations / macros that PDFs lose. Returns the saved
    path on success, None on failure.
    """
    client = _get_client()
    if client is None:
        return None
    aid = _normalize_id(arxiv_id)
    try:
        s = _arxiv.Search(id_list=[aid], max_results=1)
        for r in client.results(s):
            return r.download_source(dirpath=dirpath)
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Probe (for registry.py)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check used by prometheus_math.registry.

    Performs a short search via a one-off Client with tight retries, so
    a probe never blocks the import path for long. Returns True iff the
    third-party `arxiv` package is installed AND the API answered with
    at least one well-known result.
    """
    if _arxiv is None:
        return False
    try:
        # One-off client so we don't fight the module-level rate limiter.
        # delay_seconds is a no-op for a single request; num_retries=0
        # keeps the probe fast.
        client = _arxiv.Client(page_size=1, delay_seconds=0.0, num_retries=0)
        s = _arxiv.Search(id_list=["1505.05456"], max_results=1)
        # We don't have a per-request timeout knob in the arxiv lib, but
        # the underlying urllib request honors socket defaults. We rely
        # on num_retries=0 to make this fast on failure.
        for _ in client.results(s):
            return True
        return False
    except Exception:
        return False
