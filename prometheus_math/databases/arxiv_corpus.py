"""arxiv_corpus — local cache + search index of formal-verification papers.

Downloads a *curated* slice of arXiv (math.LO, math.NT, cs.LO with
formal-verification keywords: Lean, Coq, Isabelle, mathlib, theorem
prover, proof assistant, etc.) and stores per-paper metadata + abstract
locally. Acts as the retrieval base for tactic-suggestion / RAG
workflows that don't yet have Lean installed.

This is a sibling of :mod:`prometheus_math.databases.arxiv`, which hits
the live API; this module reads from a local on-disk corpus first and
falls back to live arXiv only when explicitly invoked via
``update_corpus()``.

Storage layout::

    $PROMETHEUS_DATA_DIR/arxiv_corpus/
        <arxiv_id>.json         # one file per paper (~5-15 KiB each)
        _index.json             # corpus-level metadata + reverse index

Per-paper JSON shape (subset of the live arxiv.py shape; PDFs are
NOT cached — only metadata + abstract)::

    {
        "id":         "2410.12345",
        "title":      "...",
        "authors":    ["...", ...],
        "abstract":   "...",
        "categories": ["math.LO", ...],
        "published":  "2024-10-15T00:00:00+00:00",
        "updated":    "2024-10-20T00:00:00+00:00",
        "pdf_url":    "https://arxiv.org/pdf/2410.12345"
    }

Public surface::

    update_corpus(force=False, max_papers=500,
                  since_year=2018, categories=None)  -> dict
    search(query, limit=20, year_range=None)         -> list[dict]
    get_by_id(arxiv_id)                              -> dict | None
    corpus_stats()                                   -> dict
    tags_index()                                     -> dict[str, list[str]]
    probe(timeout=3.0)                               -> bool
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import time
from typing import Iterable, Optional

from . import _local

try:
    from . import arxiv as _live_arxiv
except Exception:  # pragma: no cover - arxiv pip pkg missing
    _live_arxiv = None  # type: ignore


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DATASET = "arxiv_corpus"

#: arXiv categories targeted by the curated corpus. Cross-listed papers
#: that primary-classify outside this set but appear because they're
#: cross-posted are still kept.
DEFAULT_CATEGORIES: tuple[str, ...] = ("math.LO", "math.NT", "cs.LO")

#: Free-text keywords that nudge the curated query toward formal
#: verification + proof assistants. Combined with ``OR`` inside the
#: query and ``AND``-ed against the category filter.
_FV_KEYWORDS: tuple[str, ...] = (
    "Lean",
    "Coq",
    "Isabelle",
    "mathlib",
    "formal proof",
    "formal verification",
    "theorem prover",
    "proof assistant",
    "interactive theorem proving",
    "formalization",
    "formalisation",
    "type theory",
    "dependent type",
)

#: Fields a per-paper JSON record must always contain.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "id", "title", "authors", "abstract",
    "categories", "published", "updated", "pdf_url",
)

# Filename for corpus-level summary written next to per-paper JSONs.
_INDEX_FILE = "_index.json"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _corpus_dir() -> pathlib.Path:
    """Resolve the on-disk corpus directory (creating it if needed)."""
    base = _local.dataset_path(_DATASET)
    base.mkdir(parents=True, exist_ok=True)
    return base


def _safe_id(arxiv_id: str) -> str:
    """Convert an arxiv id to a filesystem-safe filename stem.

    Old-style ids (math.NT/0501234) contain a slash; map it to '_' so
    Windows is happy. Any version suffix has already been stripped by
    the caller.
    """
    return str(arxiv_id).replace("/", "_").replace("\\", "_").strip()


def _paper_path(arxiv_id: str) -> pathlib.Path:
    return _corpus_dir() / f"{_safe_id(arxiv_id)}.json"


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def _read_paper(path: pathlib.Path) -> Optional[dict]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            obj = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(obj, dict):
        return None
    if not all(k in obj for k in _REQUIRED_FIELDS):
        return None
    return obj


def _write_paper(rec: dict) -> Optional[pathlib.Path]:
    aid = (rec.get("id") or "").strip()
    if not aid:
        return None
    dest = _paper_path(aid)
    tmp = dest.with_suffix(".json.tmp")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp, dest)
    except OSError:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        return None
    return dest


def _iter_paper_paths() -> list[pathlib.Path]:
    base = _corpus_dir()
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob("*.json") if p.name != _INDEX_FILE)


def _iter_papers() -> Iterable[dict]:
    for p in _iter_paper_paths():
        rec = _read_paper(p)
        if rec is not None:
            yield rec


# ---------------------------------------------------------------------------
# Curated query construction
# ---------------------------------------------------------------------------

def _build_curated_query(categories: Iterable[str]) -> str:
    """Compose the curated category-restricted, FV-keyword-weighted query.

    Result form::

        ((cat:math.LO OR cat:math.NT OR cat:cs.LO)
         AND (Lean OR Coq OR mathlib OR ...))
    """
    cats = [c.strip() for c in categories if c and str(c).strip()]
    if not cats:
        cats = list(DEFAULT_CATEGORIES)
    cat_clause = " OR ".join(f"cat:{c}" for c in cats)
    kw_clause = " OR ".join(f'"{k}"' if " " in k else k for k in _FV_KEYWORDS)
    return f"({cat_clause}) AND ({kw_clause})"


# ---------------------------------------------------------------------------
# Public: corpus refresh
# ---------------------------------------------------------------------------

def update_corpus(force: bool = False,
                  max_papers: int = 500,
                  since_year: int = 2018,
                  categories: Optional[Iterable[str]] = None) -> dict:
    """Refresh the on-disk curated corpus.

    Performs a single arXiv search with the curated query and writes one
    JSON file per matching paper to the corpus directory. Skips papers
    already present unless ``force=True``.

    Args:
        force: re-download metadata for papers already on disk.
        max_papers: cap on the number of papers fetched in this run.
        since_year: drop hits whose ``published`` year is older.
        categories: override DEFAULT_CATEGORIES.

    Returns a status dict with keys ``added``, ``skipped``, ``filtered``,
    ``errors``, ``corpus_dir``, and ``query``.
    """
    base = _corpus_dir()
    status = {
        "added": 0,
        "skipped": 0,
        "filtered": 0,
        "errors": 0,
        "corpus_dir": str(base),
        "query": "",
    }
    if _live_arxiv is None:
        status["errors"] += 1
        status["error"] = "arxiv pip package not installed"
        return status

    cats = list(categories) if categories is not None else list(DEFAULT_CATEGORIES)
    query = _build_curated_query(cats)
    status["query"] = query

    try:
        # Pull up to ~3x max_papers so date-filter losses don't starve us.
        # Hard cap at 1500 — beyond that arXiv reliably truncates anyway.
        fetch_limit = min(max(max_papers, 50) * 3, 1500)
        hits = _live_arxiv.search(query, max_results=fetch_limit,
                                  sort_by="submittedDate")
    except Exception as e:  # pragma: no cover - network
        status["errors"] += 1
        status["error"] = f"{type(e).__name__}: {e}"
        return status

    for h in hits:
        if status["added"] >= max_papers:
            break
        aid = (h.get("id") or "").strip()
        if not aid:
            status["errors"] += 1
            continue

        # Year filter
        pub = h.get("published") or ""
        if since_year and pub:
            try:
                yr = int(pub[:4])
                if yr < since_year:
                    status["filtered"] += 1
                    continue
            except ValueError:
                pass

        dest = _paper_path(aid)
        if dest.exists() and not force:
            status["skipped"] += 1
            continue

        rec = {k: h.get(k) for k in _REQUIRED_FIELDS}
        if _write_paper(rec) is None:
            status["errors"] += 1
            continue
        status["added"] += 1

    _write_index_summary()
    return status


def _write_index_summary() -> None:
    """Recompute and persist the corpus-level summary JSON."""
    base = _corpus_dir()
    stats = corpus_stats(_skip_index=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **stats,
    }
    try:
        with (base / _INDEX_FILE).open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Public: lookup + search
# ---------------------------------------------------------------------------

def get_by_id(arxiv_id: str) -> Optional[dict]:
    """Return the on-disk record for ``arxiv_id`` or None.

    Strips any trailing version suffix the caller may have included
    (e.g. ``2410.12345v2`` -> ``2410.12345``).
    """
    if not arxiv_id:
        return None
    aid = str(arxiv_id).strip()
    if aid.startswith("arXiv:"):
        aid = aid[len("arXiv:"):]
    if "v" in aid:
        head, _, tail = aid.rpartition("v")
        if tail.isdigit():
            aid = head
    path = _paper_path(aid)
    if not path.is_file():
        return None
    return _read_paper(path)


# Token splitter: alphanumerics only, lower-cased.
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _score_paper(paper: dict, qtokens: list[str]) -> float:
    """Bag-of-words relevance score.

    Title hits weigh 3x more than abstract hits; multiple-token queries
    that all appear pick up a small phrase bonus, and exact-substring
    matches in the title pick up an additional bonus. Returns 0.0 if no
    query token appears.
    """
    if not qtokens:
        return 0.0
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    title_tokens = _tokenize(title)
    abs_tokens = _tokenize(abstract)
    # Build counts (cheaper than calling list.count for each query token).
    title_counts: dict[str, int] = {}
    for t in title_tokens:
        title_counts[t] = title_counts.get(t, 0) + 1
    abs_counts: dict[str, int] = {}
    for t in abs_tokens:
        abs_counts[t] = abs_counts.get(t, 0) + 1

    score = 0.0
    distinct_hit = 0
    for q in qtokens:
        th = title_counts.get(q, 0)
        ah = abs_counts.get(q, 0)
        if th or ah:
            distinct_hit += 1
        score += 3.0 * th + 1.0 * ah
    if score == 0.0:
        return 0.0
    # Phrase bonus: every query token represented at least once.
    if len(qtokens) >= 2 and distinct_hit == len(qtokens):
        score += 2.0 * len(qtokens)
    # Exact substring bonus on title.
    full_q = " ".join(qtokens)
    if len(qtokens) >= 2 and full_q in title:
        score += 5.0
    return score


def search(query: str,
           limit: int = 20,
           year_range: Optional[tuple[int, int]] = None) -> list[dict]:
    """Local full-text search over titles + abstracts.

    Tokenization is alphanumeric and case-insensitive; multi-word
    queries are AND-ed (every query token must appear somewhere in the
    title or abstract). Results are sorted by relevance score
    (descending), with a stable tie-break on ``published`` date (newer
    first) and finally on arxiv id.

    Args:
        query: free-text. Empty -> empty list.
        limit: max results to return (>= 0).
        year_range: optional ``(min_year, max_year)`` inclusive filter on
            published year.

    Returns a list of dicts; each is the on-disk record plus a
    ``"score"`` key.
    """
    qtokens = _tokenize(query)
    if not qtokens or limit <= 0:
        return []

    yr_lo, yr_hi = (None, None)
    if year_range is not None:
        try:
            yr_lo, yr_hi = int(year_range[0]), int(year_range[1])
        except (TypeError, ValueError, IndexError):
            yr_lo, yr_hi = None, None

    scored: list[tuple[float, str, str, dict]] = []
    for rec in _iter_papers():
        if yr_lo is not None or yr_hi is not None:
            pub = rec.get("published") or ""
            try:
                yr = int(pub[:4])
            except ValueError:
                continue
            if yr_lo is not None and yr < yr_lo:
                continue
            if yr_hi is not None and yr > yr_hi:
                continue
        sc = _score_paper(rec, qtokens)
        if sc <= 0.0:
            continue
        # Tie-breaks: newer published first, then id ascending for stability.
        pub_key = rec.get("published") or ""
        scored.append((sc, pub_key, rec.get("id") or "", rec))

    scored.sort(key=lambda t: (-t[0], _neg_iso(t[1]), t[2]))
    out: list[dict] = []
    for sc, _pub, _aid, rec in scored[:limit]:
        item = dict(rec)
        item["score"] = sc
        out.append(item)
    return out


def _neg_iso(s: str) -> str:
    """Sort key that orders ISO date strings *descending* lexicographically.

    Used as a tie-break inside :func:`search`. Empty strings sort last.
    """
    if not s:
        return "\x00"  # last
    # Invert each char so larger date strings produce smaller keys.
    return "".join(chr(0xFFFF - ord(c)) for c in s)


# ---------------------------------------------------------------------------
# Public: stats / probes
# ---------------------------------------------------------------------------

def corpus_stats(_skip_index: bool = False) -> dict:
    """Return summary stats over the local corpus.

    ``_skip_index`` is internal: ``update_corpus`` calls this to compute
    a snapshot without recursing into a previously-written ``_index.json``.

    Returned dict::

        {
            "n_papers":         int,
            "by_category":      dict[str, int],
            "by_year":          dict[int, int],
            "total_size_bytes": int,
            "corpus_dir":       str,
        }
    """
    base = _corpus_dir()
    paths = _iter_paper_paths()
    n_papers = 0
    by_category: dict[str, int] = {}
    by_year: dict[int, int] = {}
    total_size = 0
    for p in paths:
        try:
            total_size += p.stat().st_size
        except OSError:
            continue
        rec = _read_paper(p)
        if rec is None:
            continue
        n_papers += 1
        for c in (rec.get("categories") or []):
            by_category[c] = by_category.get(c, 0) + 1
        pub = rec.get("published") or ""
        try:
            yr = int(pub[:4])
        except ValueError:
            yr = 0
        if yr:
            by_year[yr] = by_year.get(yr, 0) + 1
    if not _skip_index:
        # Don't double-count the index file on disk.
        idx = base / _INDEX_FILE
        if idx.exists():
            try:
                total_size += idx.stat().st_size
            except OSError:
                pass
    return {
        "n_papers": n_papers,
        "by_category": by_category,
        "by_year": by_year,
        "total_size_bytes": total_size,
        "corpus_dir": str(base),
    }


def tags_index() -> dict[str, list[str]]:
    """Reverse map ``arxiv_id -> [category, ...]`` over the local corpus."""
    out: dict[str, list[str]] = {}
    for rec in _iter_papers():
        aid = rec.get("id") or ""
        if not aid:
            continue
        cats = list(rec.get("categories") or [])
        out[aid] = cats
    return out


def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check for the registry.

    True iff (a) the corpus directory contains at least one paper JSON,
    OR (b) the live arXiv API responds. The sibling ``arxiv`` module is
    used for the network probe so we don't duplicate its rate-limiter.
    """
    base = _corpus_dir()
    try:
        for p in base.iterdir():
            if p.is_file() and p.suffix == ".json" and p.name != _INDEX_FILE:
                return True
    except OSError:
        pass
    if _live_arxiv is None:
        return False
    try:
        return bool(_live_arxiv.probe(timeout=timeout))
    except Exception:
        return False
