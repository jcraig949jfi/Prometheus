"""Source acquisition for the cartography campaign: OpenAlex, Crossref, arXiv, DBLP.

POLITENESS IS NOT OPTIONAL AND IT IS NOT ONLY ETIQUETTE. These are free scholarly APIs run on
public money; an agent hammering them is both rude and, practically, about to be blocked
mid-campaign. Every client here identifies itself with a mailto (which puts us in OpenAlex's
polite pool), enforces a minimum inter-request interval, backs off on 429, and gives up rather
than retrying forever.

WHAT IS DELIBERATELY NOT HERE: no scraping of publisher HTML, no paywall circumvention, no
CAPTCHA handling, no authentication defeat. Where full text is unavailable, the genome records
`fulltext_available=False` and every extraction from it is scoped to "abstract" -- because an
extraction from an abstract recorded as if the methods section had been read is a fabricated
provenance, which is worse than a missing one.

MEASURED 2026-08-31 on this machine:
    OpenAlex   HTTP 200, ~0.95s   -- primary. Has the citation graph and OA status.
    Crossref   HTTP 200, ~0.25s   -- metadata, DOI resolution, independent formulation
    arXiv      HTTP 200, ~0.25s   -- preprints + full abstracts, independent formulation
    DBLP       HTTP 200, ~5.6s    -- venue/author coverage, slow; use sparingly
    Semantic Scholar  HTTP 429    -- rate-limited without an API key. Recorded as a blocker,
                                     used only as a best-effort fourth formulation.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional

MAILTO = "jcraig949@gmail.com"
UA = "Prometheus-Techne-Cartography/0.1 (mailto:" + MAILTO + ")"

#: Minimum seconds between requests, per host. Deliberately conservative: the campaign has 48
#: hours and no reason to sprint, and being blocked at hour 6 costs far more than waiting.
MIN_INTERVAL = {
    "api.openalex.org": 0.20,
    "api.crossref.org": 0.30,
    "export.arxiv.org": 3.10,     # arXiv asks for >= 3s between requests
    "dblp.org": 2.00,             # slow server; do not pile on
    "api.semanticscholar.org": 3.00,
}
_last_call: dict = {}

MAX_RETRIES = 3


class SourceError(RuntimeError):
    """A source failed. Carries the host and status so a blocker can be recorded precisely
    rather than as a generic 'network problem'."""

    def __init__(self, host: str, message: str, status: Optional[int] = None):
        self.host, self.status = host, status
        super().__init__("[" + host + "] " + message)


def _throttle(host: str) -> None:
    gap = MIN_INTERVAL.get(host, 1.0)
    last = _last_call.get(host)
    if last is not None:
        wait = gap - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
    _last_call[host] = time.time()


def _fetch(url: str, accept: str = "application/json") -> bytes:
    host = urllib.parse.urlparse(url).netloc
    for attempt in range(MAX_RETRIES):
        _throttle(host)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Honour the server's own backoff hint when it gives one.
                retry_after = e.headers.get("Retry-After")
                delay = float(retry_after) if (retry_after or "").isdigit() else 5.0 * (attempt + 1)
                if attempt == MAX_RETRIES - 1:
                    raise SourceError(host, "rate limited after " + str(MAX_RETRIES)
                                      + " attempts", 429)
                time.sleep(min(delay, 30.0))
                continue
            raise SourceError(host, "HTTP " + str(e.code), e.code)
        except Exception as e:                                        # noqa: BLE001
            if attempt == MAX_RETRIES - 1:
                raise SourceError(host, type(e).__name__ + ": " + str(e)[:120])
            time.sleep(2.0 * (attempt + 1))
    raise SourceError(host, "exhausted retries")


# --- OpenAlex ----------------------------------------------------------------------------

#: Strings that arrive in the abstract field but are not abstracts. Measured on the first 97
#: genomes: 4 of 91 abstract spans (4.4%) were repository metadata -- "International audience"
#: (a HAL artifact), "info:eu-repo/semantics/published", a bare arXiv citation line, and a
#: conference name. Low rate, real consequences: one of them drove a genuine GECCO
#: fitness-landscape paper out of the corpus, because the domain gate's lexical signal found no
#: computational term in a 21-character string and voted to reject.
_ABSTRACT_PLACEHOLDER = re.compile(
    r"^\s*(international audience|abstract|no abstract(?: available)?|n/?a|none|null|"
    r"info:eu-repo\S*|see (?:the )?(?:paper|article|full text)|full text|copyright.*|"
    r"[A-Za-z ]*\d{4}\s*-\s*[A-Za-z ]+conference.*|arxiv[: ].*)\s*$", re.I)

#: Below this, an "abstract" is a metadata fragment, not evidence. 120 characters is roughly
#: one sentence; nothing shorter can support a claim predicate.
MIN_ABSTRACT_CHARS = 120


def usable_abstract(text: Optional[str]) -> Optional[str]:
    """Return the abstract, or None if it is a placeholder or too short to be evidence.

    Returning None rather than the fragment matters in three places at once: the genome records
    honestly that it has no abstract, the claim predicates do not run over metadata and emit
    garbage claims, and the domain gate's lexical signal ABSTAINS instead of voting to reject a
    paper for not saying "algorithm" in a repository tag.
    """
    if not text:
        return None
    t = text.strip()
    if len(t) < MIN_ABSTRACT_CHARS:
        return None
    if _ABSTRACT_PLACEHOLDER.match(t):
        return None
    return t


def _invert_abstract(inv: Optional[dict]) -> Optional[str]:
    """OpenAlex ships abstracts as an inverted index for licensing reasons. Reconstruct it.

    Returns None rather than "" when absent, because downstream code treats None as 'we do not
    have this' and "" would read as 'the abstract is empty'.
    """
    if not inv:
        return None
    positions = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    if not positions:
        return None
    positions.sort()
    return " ".join(w for _, w in positions)


def openalex_search(query: str, per_page: int = 25, year_max: Optional[int] = None,
                    cursor: Optional[str] = None, cited_by_max: Optional[int] = None) -> dict:
    """Full-text search over works.

    `year_max` implements the historical-backtest cutoff -- the map must be buildable from
    information available before a date, or the backtest is just retrospective storytelling.

    `cited_by_max` caps citation count, and exists because OpenAlex's relevance ranking is
    heavily citation-weighted. Measured cycle 025:

        "negative results evolutionary computation"   rank 1-8 cited_by:
            4368, 1336, 4196, 1912, 46871, 2068, 1817, 1967
        "replication study evolutionary algorithm"    rank 1-8 cited_by:
            11822, 22339, 1208, 7119, 60622, 734, 865, 745

    So a query FOR buried literature returns the most famous papers in the field that happen
    to contain the words -- the exact inverse of the intent, and it had been doing so for 25
    cycles. The default results were also mostly off-domain biology ("PhyloSuite",
    "polyploidy", "Evolutionarily conserved elements in vertebrate"), so the lane was
    popularity-biased AND wasting its budget on papers the domain gate would reject.

    Sorting by date is not the fix -- it swaps a popularity prior for a recency one (every
    result 2026, every result 0 citations). Capping citations targets the band where
    negative results, replications and critiques actually live.
    """
    params = {"search": query, "per-page": str(per_page), "mailto": MAILTO}
    filters = []
    if year_max is not None:
        filters.append("publication_year:<" + str(year_max + 1))
    if cited_by_max is not None:
        filters.append("cited_by_count:<" + str(cited_by_max))
    if filters:
        params["filter"] = ",".join(filters)
    if cursor:
        params["cursor"] = cursor
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = json.loads(_fetch(url))
    data["_request_url"] = url
    return data


def openalex_work(work_id: str) -> dict:
    wid = work_id.rsplit("/", 1)[-1]
    url = "https://api.openalex.org/works/" + wid + "?mailto=" + MAILTO
    data = json.loads(_fetch(url))
    data["_request_url"] = url
    return data


def openalex_cited_by(work_id: str, per_page: int = 25,
                      year_max: Optional[int] = None) -> dict:
    """Forward citation edges -- who later cited this. This is the edge the historical backtest
    needs: it is how we ask whether researchers subsequently entered a predicted region."""
    wid = work_id.rsplit("/", 1)[-1]
    filt = "cites:" + wid
    if year_max is not None:
        filt += ",publication_year:<" + str(year_max + 1)
    url = ("https://api.openalex.org/works?"
           + urllib.parse.urlencode({"filter": filt, "per-page": str(per_page),
                                     "mailto": MAILTO}))
    data = json.loads(_fetch(url))
    data["_request_url"] = url
    return data


def openalex_normalize(work: dict) -> dict:
    """Project one OpenAlex work into the fields the genome compiler consumes.

    Every field can come back None. That is correct and must not be patched: OpenAlex coverage
    of venues, OA status and referenced works is genuinely uneven, and filling gaps with
    plausible defaults would put fabricated values into the operational vectors.
    """
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    oa = work.get("open_access") or {}
    ids = work.get("ids") or {}
    return {
        "source_id": work.get("id"),
        "title": work.get("title") or work.get("display_name") or "",
        "year": work.get("publication_year"),
        "doi": ids.get("doi"),
        "venue": src.get("display_name"),
        "authors": [a.get("author", {}).get("display_name")
                    for a in (work.get("authorships") or [])][:12],
        "cited_by_count": work.get("cited_by_count"),
        "citation_edges": list(work.get("referenced_works") or [])[:200],
        "abstract": usable_abstract(_invert_abstract(work.get("abstract_inverted_index"))),
        "open_access": oa.get("is_oa"),
        "oa_url": oa.get("oa_url"),
        "source_url": ids.get("doi") or work.get("id"),
        "concepts": [c.get("display_name") for c in (work.get("concepts") or [])][:10],
        "type": work.get("type"),
    }


# --- Crossref ----------------------------------------------------------------------------

def crossref_search(query: str, rows: int = 20, year_max: Optional[int] = None) -> dict:
    params = {"query": query, "rows": str(rows), "mailto": MAILTO}
    if year_max is not None:
        params["filter"] = "until-pub-date:" + str(year_max) + "-12-31"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = json.loads(_fetch(url))
    data["_request_url"] = url
    return data


# --- arXiv -------------------------------------------------------------------------------

_ATOM = "{http://www.w3.org/2005/Atom}"


def arxiv_search(query: str, max_results: int = 20) -> dict:
    """arXiv returns Atom XML. Parsed into the same shape as the other sources so the retrieval
    log can compare formulations without special-casing."""
    params = {"search_query": "all:" + query, "max_results": str(max_results),
              "sortBy": "relevance"}
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    raw = _fetch(url, accept="application/atom+xml")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        raise SourceError("export.arxiv.org", "malformed Atom: " + str(e)[:80])
    entries = []
    for e in root.findall(_ATOM + "entry"):
        def txt(tag):
            node = e.find(_ATOM + tag)
            return (node.text or "").strip() if node is not None else None
        entries.append({
            "source_id": txt("id"),
            "title": re.sub(r"\s+", " ", txt("title") or ""),
            "abstract": usable_abstract(re.sub(r"\s+", " ", txt("summary") or "")),
            "published": txt("published"),
            "year": int((txt("published") or "0000")[:4]) or None,
            "authors": [a.find(_ATOM + "name").text
                        for a in e.findall(_ATOM + "author")
                        if a.find(_ATOM + "name") is not None][:12],
            "source_url": txt("id"),
        })
    total = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    return {"entries": entries, "_request_url": url,
            "total": int(total.text) if total is not None and total.text else len(entries)}


# --- DBLP --------------------------------------------------------------------------------

def dblp_search(query: str, hits: int = 20) -> dict:
    """DBLP is slow (~5.6s measured) but has venue and author coverage the others lack. Use it
    as an independent formulation for gap-killing, not as a bulk crawler."""
    params = {"q": query, "format": "json", "h": str(hits)}
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode(params)
    data = json.loads(_fetch(url))
    data["_request_url"] = url
    return data


def dblp_hits(data: dict) -> list:
    result = (data.get("result") or {}).get("hits") or {}
    raw = result.get("hit") or []
    out = []
    for h in raw:
        info = h.get("info") or {}
        out.append({
            "source_id": info.get("key"),
            "title": info.get("title"),
            "year": int(info["year"]) if str(info.get("year", "")).isdigit() else None,
            "venue": info.get("venue"),
            "source_url": info.get("ee") or info.get("url"),
        })
    return out


# --- Semantic Scholar --------------------------------------------------------------------
#
# KEY STATUS: PRESENT BUT REJECTED. The repo has one S2 credential, reachable through the
# canonical accessor `keys.get_key("S2")` (which resolves S2_API_KEY from the repo-root .env
# then agents/eos/.env). Measured 2026-08-31, 40-character key, correct format:
#
#     with x-api-key   -> HTTP 403 {"message":"Forbidden"}   <- credential rejected
#     without a key    -> HTTP 429 (rate limited)
#
# 403 is rejection, not throttling: the key is expired, revoked, or was never activated. This
# matches the programme's recorded pattern of lapsed third-party credentials. The client below
# is wired anyway so the source activates the moment the key is renewed, with no code change --
# and until then every call records the blocker rather than silently degrading.
#
# WHAT WE LOSE WHILE IT IS DEAD, stated because it bears directly on the campaign's current
# bottleneck: S2 exposes `fieldsOfStudy` (a fourth independent domain signal), `tldr` (a
# machine-written summary that would give title-only records real text to tag), and abstracts
# for papers where OpenAlex has none. All three attack the 3.3%-classification problem head on.

def s2_api_key() -> Optional[str]:
    """Resolve the S2 key through the repository's canonical accessor. Never printed."""
    try:
        import sys
        import pathlib as _pl
        root = str(_pl.Path(__file__).resolve().parents[2])
        if root not in sys.path:
            sys.path.insert(0, root)
        from keys import get_key
        return get_key("S2") or None
    except Exception:                                                 # noqa: BLE001
        return None


def semantic_scholar_search(query: str, limit: int = 10) -> dict:
    """Search S2. Raises SourceError with the precise status so a dead key is recorded as a
    dead key rather than as a generic failure."""
    key = s2_api_key()
    params = urllib.parse.urlencode({
        "query": query, "limit": str(limit),
        "fields": "title,year,abstract,tldr,fieldsOfStudy,externalIds,citationCount,venue",
    })
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + params
    host = "api.semanticscholar.org"
    _throttle(host)
    headers = {"User-Agent": UA}
    if key:
        headers["x-api-key"] = key
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read())
        data["_request_url"] = url
        data["_used_key"] = bool(key)
        return data
    except urllib.error.HTTPError as e:
        if e.code == 403 and key:
            raise SourceError(host, "HTTP 403 Forbidden WITH a key present -- the S2 "
                                    "credential is rejected (expired/revoked/never "
                                    "activated), not rate limited", 403)
        raise SourceError(host, "HTTP " + str(e.code) + (" (no key)" if not key else ""), e.code)
    except Exception as e:                                            # noqa: BLE001
        raise SourceError(host, type(e).__name__ + ": " + str(e)[:120])


def semantic_scholar_available() -> tuple:
    """(usable, reason). Cheap liveness probe; callers record the reason as a blocker."""
    try:
        semantic_scholar_search("lexicase selection", limit=1)
        return True, "S2 reachable"
    except SourceError as e:
        return False, str(e)


#: Which sources are usable as INDEPENDENT retrieval formulations when trying to kill a
#: coverage hole. Independence matters: four rephrasings against one index is one search.
#: S2 is NOT in this tuple while its key is rejected -- a source that cannot answer cannot
#: contribute to an absence claim.
INDEPENDENT_SOURCES = ("openalex", "crossref", "arxiv", "dblp")

KNOWN_BLOCKERS = {
    "semanticscholar": "key PRESENT but REJECTED: HTTP 403 Forbidden with x-api-key, HTTP 429 "
                       "without (measured 2026-08-31). Wired via keys.get_key('S2') and will "
                       "activate on renewal with no code change. Never counted as an "
                       "independent formulation while dead.",
}
