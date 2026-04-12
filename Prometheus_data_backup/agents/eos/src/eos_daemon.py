"""
Eos — The Dawn Scanner

Horizon scanning daemon for the Prometheus project.
Monitors the frontier of AI research, open-source tools, and free API resources.
Watches the primordial soup and reports what's emerging.

Usage:
    python eos_daemon.py                    # Default: hourly scans
    python eos_daemon.py --once             # Single scan, no loop
    python eos_daemon.py --interval 1800    # Custom interval (seconds)

Eos's first mission: discover what free resources exist for herself.
Her ongoing mission: watch the frontier and surface what matters.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

EOS_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = EOS_ROOT / "configs" / "eos_config.yaml"
DATA_DIR = EOS_ROOT / "data"
REPORTS_DIR = EOS_ROOT / "reports"

# Load .env file if present (keys, tokens)
_env_file = EOS_ROOT / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EOS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("eos")


def load_config() -> dict:
    """Load YAML config. Falls back to defaults if missing."""
    try:
        import yaml
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        log.warning("PyYAML not installed — using defaults")
        return {}
    except FileNotFoundError:
        log.warning(f"Config not found at {CONFIG_PATH} — using defaults")
        return {}


def load_registry() -> dict:
    """Load the API registry."""
    reg_path = DATA_DIR / "api_registry.json"
    try:
        return json.loads(reg_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"_meta": {}, "apis": {}}


def save_registry(registry: dict) -> None:
    """Save the API registry."""
    reg_path = DATA_DIR / "api_registry.json"
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    registry["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    reg_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Rate Limit Engine
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple per-source rate limiter with exponential backoff."""

    def __init__(self):
        self._last_request: dict[str, float] = {}
        self._backoff: dict[str, float] = {}
        self._request_counts: dict[str, int] = {}

    def wait_if_needed(self, source: str, min_interval: float = 3.0) -> None:
        """Block until it's safe to make a request to this source."""
        backoff = self._backoff.get(source, 0)
        effective_interval = max(min_interval, backoff)

        last = self._last_request.get(source, 0)
        elapsed = time.time() - last
        if elapsed < effective_interval:
            sleep_time = effective_interval - elapsed
            log.debug(f"Rate limit: sleeping {sleep_time:.1f}s for {source}")
            time.sleep(sleep_time)

        self._last_request[source] = time.time()
        self._request_counts[source] = self._request_counts.get(source, 0) + 1

    def report_429(self, source: str) -> None:
        """Report a rate limit hit — increase backoff."""
        current = self._backoff.get(source, 3.0)
        self._backoff[source] = min(current * 2, 300)  # Cap at 5 minutes
        log.warning(f"429 from {source} — backoff now {self._backoff[source]:.0f}s")

    def report_success(self, source: str) -> None:
        """Report a successful request — decay backoff."""
        if source in self._backoff:
            self._backoff[source] = max(self._backoff[source] * 0.8, 3.0)

    def stats(self) -> dict:
        return {
            "requests": dict(self._request_counts),
            "backoffs": {k: f"{v:.0f}s" for k, v in self._backoff.items() if v > 3},
        }


# ---------------------------------------------------------------------------
# Paper / Repo Dedup Index
# ---------------------------------------------------------------------------

class PaperIndex:
    """Persistent index for cross-cycle deduplication of papers and repos.

    Fingerprints items by normalized title + first author + year.
    Tracks first_seen, last_seen, seen_count, and all source URLs.
    """

    def __init__(self, path: Path):
        self.path = path
        self.index: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.index = data.get("papers", {})
                log.info(f"Paper index loaded: {len(self.index)} known items")
            except (json.JSONDecodeError, OSError) as e:
                log.warning(f"Paper index corrupt, starting fresh: {e}")
                self.index = {}
        else:
            log.info("No paper index found — starting fresh")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "_meta": {
                "description": "Cross-cycle dedup index for Eos scanner",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_items": len(self.index),
            },
            "papers": self.index,
        }
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _fingerprint(item: dict) -> str:
        """Stable fingerprint: normalized title prefix + first author + year."""
        import re
        title = (item.get("title") or item.get("name") or "").lower().strip()
        title = re.sub(r"[^a-z0-9 ]", "", title)[:80]

        authors = item.get("authors") or []
        first_author = (authors[0] if authors else "").lower().split()[-1] if authors else ""

        date_str = item.get("date") or item.get("updated") or ""
        year = date_str[:4] if len(date_str) >= 4 else ""

        return f"{title}|{first_author}|{year}"

    def is_known(self, item: dict) -> bool:
        return self._fingerprint(item) in self.index

    def add(self, item: dict) -> None:
        """Add or update an item in the index."""
        fp = self._fingerprint(item)
        now = datetime.now(timezone.utc).isoformat()
        url = item.get("url") or ""

        if fp in self.index:
            entry = self.index[fp]
            entry["last_seen"] = now
            entry["seen_count"] = entry.get("seen_count", 1) + 1
            if url and url not in entry.get("source_urls", []):
                entry.setdefault("source_urls", []).append(url)
        else:
            self.index[fp] = {
                "title": item.get("title") or item.get("name") or "",
                "first_seen": now,
                "last_seen": now,
                "seen_count": 1,
                "source_urls": [url] if url else [],
            }

    def filter_new(self, items: list[dict]) -> tuple[list[dict], int]:
        """Return (new_items, n_duplicates). Adds new items to index."""
        new = []
        dupes = 0
        for item in items:
            if self.is_known(item):
                dupes += 1
                # Still update last_seen
                self.add(item)
            else:
                self.add(item)
                new.append(item)
        return new, dupes


# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def scan_arxiv(config: dict, limiter: RateLimiter) -> list[dict]:
    """Scan arxiv for new papers matching our keywords."""
    results = []
    keywords = config.get("search_topics", {}).get("arxiv_keywords", [])
    if not keywords:
        return results

    try:
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET
    except ImportError:
        log.error("Missing stdlib modules for arxiv scan")
        return results

    # Batch keywords into a single OR query to minimize requests
    query = " OR ".join(f'all:"{kw}"' for kw in keywords[:5])  # Limit to avoid huge queries
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": 20,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"http://export.arxiv.org/api/query?{params}"

    limiter.wait_if_needed("arxiv", min_interval=3.0)
    try:
        import ssl
        ctx = ssl.create_default_context()
        try:
            import certifi
            ctx.load_verify_locations(certifi.where())
        except ImportError:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Eos/1.0 (Prometheus Project)"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read().decode("utf-8")
        limiter.report_success("arxiv")
    except Exception as e:
        log.error(f"arxiv scan failed: {e}")
        if "429" in str(e) or "Too Many" in str(e):
            limiter.report_429("arxiv")
        return results

    # Parse Atom XML
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(data)
        for entry in root.findall("atom:entry", ns):
            title = (entry.find("atom:title", ns).text or "").strip().replace("\n", " ")
            summary = (entry.find("atom:summary", ns).text or "").strip()[:300]
            paper_id = (entry.find("atom:id", ns).text or "").strip()
            published = (entry.find("atom:published", ns).text or "")[:10]

            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns)
                if name is not None and name.text:
                    authors.append(name.text.strip())

            results.append({
                "source": "arxiv",
                "title": title,
                "authors": authors[:5],
                "url": paper_id,
                "date": published,
                "summary": summary,
            })
    except ET.ParseError as e:
        log.error(f"arxiv XML parse error: {e}")

    log.info(f"arxiv: found {len(results)} papers")
    return results


def scan_github(config: dict, limiter: RateLimiter) -> list[dict]:
    """Scan GitHub for trending/new repos matching our topics."""
    results = []
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.warning("No GITHUB_TOKEN — skipping GitHub scan")
        return results

    keywords = config.get("search_topics", {}).get("github_keywords", [])
    if not keywords:
        return results

    import urllib.request
    import urllib.parse

    # Search for recently created/updated repos — one keyword at a time
    query = keywords[0]  # Most relevant keyword
    params = urllib.parse.urlencode({
        "q": f"{query} pushed:>{_days_ago(14)}",
        "sort": "updated",
        "order": "desc",
        "per_page": 15,
    })
    url = f"https://api.github.com/search/repositories?{params}"

    limiter.wait_if_needed("github", min_interval=6.0)
    try:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Eos/1.0 (Prometheus Project)",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        limiter.report_success("github")
    except Exception as e:
        log.error(f"GitHub scan failed: {e}")
        if "429" in str(e) or "rate limit" in str(e).lower():
            limiter.report_429("github")
        return results

    for repo in data.get("items", []):
        results.append({
            "source": "github",
            "name": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "description": (repo.get("description") or "")[:200],
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language"),
            "updated": (repo.get("updated_at") or "")[:10],
            "topics": repo.get("topics", []),
        })

    log.info(f"GitHub: found {len(results)} repos")
    return results


def scan_openalex(config: dict, limiter: RateLimiter) -> list[dict]:
    """Scan OpenAlex for recent papers matching our keywords."""
    results = []
    keywords = config.get("search_topics", {}).get("arxiv_keywords", [])
    if not keywords:
        return results

    import urllib.request
    import urllib.parse

    # OpenAlex search — use a single keyword phrase per request
    query = keywords[0]  # Most relevant keyword
    params = urllib.parse.urlencode({
        "search": query,
        "filter": f"from_publication_date:{_days_ago(14)}",
        "sort": "publication_date:desc",
        "per_page": 15,
        "mailto": "prometheus-project@users.noreply.github.com",
    })
    url = f"https://api.openalex.org/works?{params}"

    limiter.wait_if_needed("openalex", min_interval=0.5)
    try:
        import ssl
        ctx = ssl.create_default_context()
        try:
            import certifi
            ctx.load_verify_locations(certifi.where())
        except ImportError:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            "User-Agent": "Eos/1.0 (Prometheus Project; mailto:prometheus-project@users.noreply.github.com)",
        })
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        limiter.report_success("openalex")
    except Exception as e:
        log.error(f"OpenAlex scan failed: {e}")
        if "429" in str(e):
            limiter.report_429("openalex")
        return results

    for work in data.get("results", []):
        title = work.get("title") or ""
        doi = work.get("doi") or ""
        pub_date = work.get("publication_date") or ""
        cited = work.get("cited_by_count", 0)

        authors = []
        for authorship in (work.get("authorships") or [])[:5]:
            author = authorship.get("author", {})
            name = author.get("display_name")
            if name:
                authors.append(name)

        # Get abstract from inverted index if available
        abstract = ""
        inv_abstract = work.get("abstract_inverted_index")
        if inv_abstract:
            # Reconstruct abstract from inverted index
            words = {}
            for word, positions in inv_abstract.items():
                for pos in positions:
                    words[pos] = word
            abstract = " ".join(words[k] for k in sorted(words.keys()))[:300]

        results.append({
            "source": "openalex",
            "title": title,
            "authors": authors,
            "url": doi or work.get("id", ""),
            "date": pub_date,
            "summary": abstract,
            "cited_by": cited,
        })

    log.info(f"OpenAlex: found {len(results)} papers")
    return results


def scan_semantic_scholar(config: dict, limiter: RateLimiter) -> list[dict]:
    """Scan Semantic Scholar for recent papers with TLDRs and citation data."""
    results = []
    keywords = config.get("search_topics", {}).get("arxiv_keywords", [])
    if not keywords:
        return results

    import urllib.request
    import urllib.parse
    import ssl

    api_key = os.environ.get("S2_API_KEY")
    source_name = "semantic_scholar" if api_key else "semantic_scholar_nokey"

    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    # Search for recent papers — one query to conserve budget
    query = keywords[0]
    params = urllib.parse.urlencode({
        "query": query,
        "fields": "title,authors,year,citationCount,tldr,openAccessPdf,publicationDate,url",
        "publicationDateOrYear": f"{_days_ago(30)}:",
        "limit": 15,
        "fieldsOfStudy": "Computer Science",
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"

    limiter.wait_if_needed(source_name, min_interval=2.0 if api_key else 5.0)
    try:
        headers = {"User-Agent": "Eos/1.0 (Prometheus Project)"}
        if api_key:
            headers["x-api-key"] = api_key
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        limiter.report_success(source_name)
    except Exception as e:
        log.error(f"Semantic Scholar scan failed: {e}")
        if "429" in str(e):
            limiter.report_429(source_name)
        return results

    for paper in data.get("data", []):
        title = paper.get("title") or ""
        authors = [a.get("name", "") for a in (paper.get("authors") or [])[:5]]
        tldr = (paper.get("tldr") or {}).get("text", "")
        pdf = (paper.get("openAccessPdf") or {}).get("url", "")
        s2_url = paper.get("url") or ""
        cited = paper.get("citationCount", 0)
        pub_date = paper.get("publicationDate") or str(paper.get("year", ""))

        results.append({
            "source": "semantic_scholar",
            "title": title,
            "authors": authors,
            "url": s2_url,
            "pdf_url": pdf,
            "date": pub_date,
            "summary": tldr or "(no TLDR)",
            "cited_by": cited,
        })

    log.info(f"Semantic Scholar: found {len(results)} papers")
    return results


def scan_tavily(config: dict, limiter: RateLimiter) -> list[dict]:
    """Scan Tavily for AI news and announcements. Uses sparingly — 1000/month budget."""
    results = []
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        log.warning("No TAVILY_API_KEY — skipping Tavily scan")
        return results

    import urllib.request
    import ssl

    # Tavily search — focused on AI news and open-source announcements
    queries = [
        "mechanistic interpretability new tools 2026",
        "open source AI agent framework announcement",
    ]

    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    for query in queries[:1]:  # One query per cycle to conserve budget (~30/day = 900/month)
        limiter.wait_if_needed("tavily", min_interval=5.0)
        try:
            payload = json.dumps({
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.tavily.com/search",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            limiter.report_success("tavily")

            for item in data.get("results", []):
                results.append({
                    "source": "tavily",
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "summary": (item.get("content") or "")[:300],
                    "score": item.get("score", 0),
                })
        except Exception as e:
            log.error(f"Tavily scan failed: {e}")
            if "429" in str(e):
                limiter.report_429("tavily")

    log.info(f"Tavily: found {len(results)} results")
    return results


def scan_api_health(registry: dict, limiter: RateLimiter) -> list[dict]:
    """Check known APIs for availability and update registry status."""
    import urllib.request
    findings = []

    for api_key, api in registry.get("apis", {}).items():
        if api.get("status") == "needs_verification":
            url = api.get("url", "")
            if not url:
                continue

            limiter.wait_if_needed(f"health_{api_key}", min_interval=5.0)
            try:
                req = urllib.request.Request(url, method="HEAD",
                    headers={"User-Agent": "Eos/1.0 (Prometheus Project)"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status = resp.status
                if status < 400:
                    api["status"] = "active"
                    findings.append(f"{api['name']}: verified active")
                    limiter.report_success(f"health_{api_key}")
            except Exception as e:
                findings.append(f"{api['name']}: check failed ({e})")

    return findings


# ---------------------------------------------------------------------------
# Digest Writer
# ---------------------------------------------------------------------------

def llm_analyze(items: list[dict], limiter: RateLimiter, max_items: int = 3) -> list[dict]:
    """Use Nemotron 120B (or fallback to Groq) to analyze high-priority items."""
    api_key = os.environ.get("NVIDIA_API_KEY")
    endpoint = os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1")
    model = os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    source_name = "nvidia_nim"

    if not api_key:
        # Fallback to Groq
        api_key = os.environ.get("GROQ_API_KEY")
        endpoint = "https://api.groq.com/openai/v1"
        model = "llama-3.1-8b-instant"
        source_name = "groq"

    if not api_key:
        log.warning("No LLM API key — skipping analysis")
        return []

    import urllib.request
    import ssl

    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    analyses = []
    for item in items[:max_items]:
        title = item.get("title") or item.get("name", "Untitled")
        summary = item.get("summary") or item.get("description") or ""
        url = item.get("url", "")

        prompt = (
            f"You are a research analyst for the Prometheus project, which probes "
            f"transformer internals for reasoning circuits using evolutionary search "
            f"(CMA-ES steering vectors in the residual stream). Our core hypothesis "
            f"(RPH) predicts reasoning circuits precipitate at scale.\n\n"
            f"Analyze this paper/repo for relevance:\n"
            f"Title: {title}\n"
            f"Summary: {summary[:500]}\n\n"
            f"In 2-3 sentences: (1) What is the key finding? "
            f"(2) Can we adopt or leverage anything for our pipeline? "
            f"(3) Does it support, challenge, or extend RPH?"
        )

        limiter.wait_if_needed(source_name, min_interval=3.0)
        try:
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{endpoint}/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            limiter.report_success(source_name)

            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                # Handle models that return reasoning_content separately
                analysis_text = msg.get("content") or msg.get("reasoning_content") or ""
                analyses.append({
                    "title": title,
                    "url": url,
                    "analysis": analysis_text.strip(),
                    "model": model,
                })
                log.info(f"LLM analyzed: {title[:60]}...")

        except Exception as e:
            log.error(f"LLM analysis failed for '{title[:40]}': {e}")
            if "429" in str(e):
                limiter.report_429(source_name)
                break  # Stop analyzing if rate limited

    return analyses


def _score_relevance(item: dict) -> tuple[int, str]:
    """Score an item's relevance to Prometheus. Returns (score 0-100, reason)."""
    title = (item.get("title") or item.get("name") or "").lower()
    summary = (item.get("summary") or item.get("description") or "").lower()
    text = f"{title} {summary}"

    score = 0
    reasons = []

    # Tier 1: Directly in our lane (high priority)
    tier1 = [
        ("steering vector", 30), ("activation engineering", 30),
        ("mechanistic interpretability", 25), ("circuit discovery", 30),
        ("sparse autoencoder", 20), ("residual stream", 25),
        ("reasoning circuit", 30), ("cma-es", 25), ("cma es", 25),
        ("chain of thought internal", 25), ("meta cognition", 25),
    ]
    for kw, pts in tier1:
        if kw in text:
            score += pts
            reasons.append(kw)

    # Tier 2: Adjacent and useful
    tier2 = [
        ("transformer lens", 15), ("transformerlens", 15),
        ("activation patching", 15), ("causal intervention", 15),
        ("evolutionary algorithm", 10), ("quality diversity", 15),
        ("tensor decomposition", 15), ("autonomous agent", 10),
        ("free api", 20), ("free tier", 20), ("open source", 10),
        ("reasoning", 8), ("interpretability", 8),
    ]
    for kw, pts in tier2:
        if kw in text:
            score += pts
            reasons.append(kw)

    # Citation boost for papers
    cited = item.get("cited_by", 0)
    if cited > 50:
        score += 10
        reasons.append(f"{cited} citations")

    # Stars boost for repos
    stars = item.get("stars", 0)
    if stars > 100:
        score += 15
        reasons.append(f"{stars} stars")
    elif stars > 20:
        score += 5

    return min(score, 100), ", ".join(reasons[:3])


def write_digest(papers: list, repos: list, health: list, limiter: RateLimiter, news: list = None, analyses: list = None) -> Path:
    """Write a daily digest report with priority scoring."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report_path = REPORTS_DIR / f"{date_str}.md"

    # Score everything for relevance
    scored_papers = [(p, *_score_relevance(p)) for p in papers]
    scored_repos = [(r, *_score_relevance(r)) for r in repos]
    scored_news = [(n, *_score_relevance(n)) for n in (news or [])]

    # Collect high-priority items across all sources
    attention = []
    for item, score, reason in scored_papers:
        if score >= 20:
            attention.append(("paper", item, score, reason))
    for item, score, reason in scored_repos:
        if score >= 15:
            attention.append(("repo", item, score, reason))
    for item, score, reason in scored_news:
        if score >= 15:
            attention.append(("news", item, score, reason))
    attention.sort(key=lambda x: -x[2])

    # --- Semantic dedup of attention items ---
    # Cluster items with similar titles (same story from different sources)
    def _title_key(item):
        """Extract key phrases for clustering. Strips common words, lowercases."""
        title = (item.get("title") or item.get("name", "")).lower()
        # Remove common prefixes/suffixes
        for strip in ["- github", "- gist", "| ", "..."]:
            title = title.replace(strip, "")
        # Extract significant words (>3 chars, not stopwords)
        stops = {"the", "and", "for", "with", "from", "that", "this", "are", "was", "new", "how"}
        words = set(w for w in re.findall(r'\w+', title) if len(w) > 3 and w not in stops)
        return frozenset(words)

    if attention:
        clustered = []
        used = set()
        for i, (kind, item, score, reason) in enumerate(attention):
            if i in used:
                continue
            key_i = _title_key(item)
            cluster = [(kind, item, score, reason)]
            for j in range(i + 1, len(attention)):
                if j in used:
                    continue
                key_j = _title_key(attention[j][3 - 3:][1] if len(attention[j]) > 1 else {})
                key_j = _title_key(attention[j][1])
                # Cluster if >50% word overlap
                if key_i and key_j and len(key_i & key_j) / max(1, min(len(key_i), len(key_j))) > 0.5:
                    cluster.append(attention[j])
                    used.add(j)
            # Keep highest-scoring item from cluster, note the count
            clustered.append((cluster[0], len(cluster)))
            used.add(i)
        attention_deduped = clustered
    else:
        attention_deduped = []

    lines = [
        f"# Eos Daily Digest -- {date_str}",
        f"*Scan completed: {ts}*",
        "",
    ]

    # ATTENTION REQUIRED — the section James reads first
    if attention_deduped:
        lines.append(f"## !! ATTENTION REQUIRED ({len(attention_deduped)} items)")
        lines.append("*Items scored by relevance to Prometheus. Higher = more directly useful.*\n")
        for (kind, item, score, reason), n_sources in attention_deduped[:10]:
            title = item.get("title") or item.get("name", "Untitled")
            url = item.get("url", "")
            sources_note = f" ({n_sources} sources)" if n_sources > 1 else ""
            if kind == "paper":
                tldr = item.get("summary", "")[:150]
                lines.append(f"- [{score}] **[PAPER]** {title}")
                lines.append(f"  {url}")
                if tldr and tldr != "(no TLDR)":
                    lines.append(f"  _{tldr}..._")
                lines.append(f"  *Why: {reason}*")
            elif kind == "repo":
                stars = item.get("stars", 0)
                lines.append(f"- [{score}] **[REPO]** {title} ({stars} stars)")
                lines.append(f"  {url}")
                lines.append(f"  *Why: {reason}*")
            else:
                lines.append(f"- [{score}] **[NEWS]** {title}{sources_note}")
                lines.append(f"  {url}")
                lines.append(f"  *Why: {reason}*")
            lines.append("")
    else:
        lines.append("## Attention Required\n*Nothing scored above threshold this cycle.*\n")

    # LLM Deep Analysis (Nemotron 120B)
    analyses = analyses or []
    if analyses:
        lines.append(f"## Deep Analysis ({len(analyses)} items, via {analyses[0].get('model', '?')})")
        for a in analyses:
            lines.append(f"### {a['title']}")
            lines.append(f"_{a.get('url', '')}_\n")
            lines.append(a.get("analysis", "(no analysis)"))
            lines.append("")

    # Papers — sorted by relevance
    scored_papers.sort(key=lambda x: -x[1])
    lines.append(f"## All Papers ({len(papers)} found)")
    if papers:
        for p, score, reason in scored_papers[:10]:
            authors = ", ".join(p.get("authors", [])[:3])
            if len(p.get("authors", [])) > 3:
                authors += " et al."
            src = p.get("source", "?")
            lines.append(f"- [{score}] **{p['title']}** ({p.get('date', '?')}, {src})")
            lines.append(f"  {authors}")
            lines.append(f"  {p['url']}")
            tldr = p.get('summary', '')[:150]
            if tldr and tldr != "(no TLDR)":
                lines.append(f"  _{tldr}..._")
            lines.append("")
    else:
        lines.append("*No new papers found this cycle.*\n")

    # Repos — sorted by relevance
    scored_repos.sort(key=lambda x: -x[1])
    lines.append(f"## Repos ({len(repos)} found)")
    if repos:
        for r, score, reason in scored_repos[:10]:
            stars = r.get("stars", 0)
            lines.append(f"- [{score}] **{r['name']}** ({stars} stars, {r.get('language', '?')})")
            lines.append(f"  {r.get('description', '')}")
            lines.append(f"  {r['url']}")
            lines.append("")
    else:
        lines.append("*No new repos found this cycle.*\n")

    # News / Web Intelligence
    news = news or []
    if news:
        lines.append(f"## Web Intelligence ({len(news)} found)")
        for n in news[:5]:
            lines.append(f"- **{n.get('title', 'Untitled')}**")
            lines.append(f"  {n.get('url', '')}")
            lines.append(f"  _{n.get('summary', '')[:200]}..._")
            lines.append("")
    else:
        lines.append("## Web Intelligence\n*No Tavily results this cycle.*\n")

    # API Health
    if health:
        lines.append("## API Registry Updates")
        for h in health:
            lines.append(f"- {h}")
        lines.append("")

    # Rate limiter stats
    stats = limiter.stats()
    lines.append("## Scan Stats")
    lines.append(f"- Requests: {stats['requests']}")
    if stats["backoffs"]:
        lines.append(f"- Active backoffs: {stats['backoffs']}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Digest written: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _days_ago(n: int) -> str:
    """Return ISO date string for N days ago."""
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def run_cycle(config: dict, registry: dict, limiter: RateLimiter,
              paper_index: PaperIndex) -> None:
    """Execute one complete scan cycle."""
    log.info("=" * 60)
    log.info("Eos wake cycle starting")

    papers_arxiv = scan_arxiv(config, limiter)
    papers_openalex = scan_openalex(config, limiter)
    papers_s2 = scan_semantic_scholar(config, limiter)
    repos = scan_github(config, limiter)
    news = scan_tavily(config, limiter)
    health = scan_api_health(registry, limiter)

    # Merge papers, deduplicate within this cycle by title
    all_papers = papers_arxiv + papers_openalex + papers_s2
    seen_titles = set()
    cycle_unique = []
    for p in all_papers:
        key = p.get("title", "").lower()[:60]
        if key not in seen_titles:
            seen_titles.add(key)
            cycle_unique.append(p)

    # Cross-cycle dedup via persistent index
    papers, paper_dupes = paper_index.filter_new(cycle_unique)
    repos_new, repo_dupes = paper_index.filter_new(repos)
    paper_index.save()

    if paper_dupes or repo_dupes:
        log.info(f"Dedup: {paper_dupes} known papers filtered, {repo_dupes} known repos filtered")

    # LLM analysis of top items
    # Score all items to find the best candidates for deep analysis
    all_scored = [(p, *_score_relevance(p)) for p in papers]
    all_scored += [(r, *_score_relevance(r)) for r in repos_new]
    all_scored.sort(key=lambda x: -x[1])
    top_items = [item for item, score, reason in all_scored if score >= 25]
    analyses = llm_analyze(top_items, limiter, max_items=3)

    # Save updated registry
    save_registry(registry)

    # Write digest
    write_digest(papers, repos_new, health, limiter, news=news, analyses=analyses)

    within_dedup = len(all_papers) - len(cycle_unique)
    log.info(
        f"Cycle complete: {len(papers)} new papers "
        f"({len(all_papers)} raw, -{within_dedup} within-cycle dupes, -{paper_dupes} cross-cycle dupes), "
        f"{len(repos_new)} new repos (-{repo_dupes} known), {len(health)} health checks"
    )

    # Constitutional Law 3: Deposit findings into the substrate
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "aletheia" / "src"))
        from ingest import deposit_entity, deposit_relationship
        deposited = 0
        for p in papers:
            title = p.get("title", "untitled")
            eid = deposit_entity(
                name=title[:200],
                entity_type="paper",
                source_agent="eos",
                metadata={
                    "url": p.get("url", ""),
                    "authors": p.get("authors", ""),
                    "source": p.get("source", ""),
                    "abstract": p.get("abstract", "")[:500],
                },
            )
            deposited += 1
        for r in repos_new:
            name = r.get("title", r.get("name", "unnamed"))
            deposit_entity(
                name=name[:200],
                entity_type="tool",
                source_agent="eos",
                metadata={
                    "url": r.get("url", ""),
                    "description": r.get("abstract", r.get("description", ""))[:500],
                    "source": "github",
                },
            )
            deposited += 1
        log.info(f"Substrate: deposited {deposited} entities into Aletheia")
    except Exception as e:
        log.warning(f"Substrate deposition failed (non-fatal): {e}")


def main():
    parser = argparse.ArgumentParser(description="Eos — The Dawn Scanner")
    parser.add_argument("--once", action="store_true", help="Single scan, no loop")
    parser.add_argument("--interval", type=int, default=3600,
                        help="Scan interval in seconds (default: 3600)")
    args = parser.parse_args()

    config = load_config()
    registry = load_registry()
    limiter = RateLimiter()
    paper_index = PaperIndex(DATA_DIR / "paper_index.json")

    sep = "=" * 62
    dash = "-" * 62
    reports_str = str(REPORTS_DIR.relative_to(EOS_ROOT))
    registry_str = str(DATA_DIR / "api_registry.json")
    index_str = f"{len(paper_index.index)} known items"
    interval_str = f"{args.interval}s {'(single pass)' if args.once else ''}"
    print(f"{sep}\n  EOS -- THE DAWN SCANNER\n  She who sees the new day first.\n  Watching the primordial soup.\n{dash}\n  Reports:  {reports_str}\n  Registry: {registry_str}\n  Index:    {index_str}\n  Interval: {interval_str}\n{sep}\n")

    run_cycle(config, registry, limiter, paper_index)

    if args.once:
        return

    while True:
        log.info(f"Sleeping {args.interval}s until next scan...")
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            log.info("Eos shutting down (Ctrl+C)")
            break
        run_cycle(config, registry, limiter, paper_index)


if __name__ == "__main__":
    main()
