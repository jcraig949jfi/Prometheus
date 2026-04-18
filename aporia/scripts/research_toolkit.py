"""
Aporia Research Toolkit — Shared infrastructure for ALL agents.

Provides unified access to research APIs:
  - Semantic Scholar (S2): Paper search with TLDRs, citations
  - arXiv: Recent preprints by category/keyword
  - OpenAlex: 100K/day free, broad coverage
  - GitHub: Repository search for tools/implementations
  - Tavily: Web search (limited budget)
  - Serper: Google search results

All keys loaded from agents/Eos/.env (Eos discovered these free tiers).
Rate-limited to stay well under quotas.

Usage:
    from aporia.scripts.research_toolkit import ResearchToolkit
    rt = ResearchToolkit()
    papers = rt.search_papers("pair correlation L-function zeros")
    repos = rt.search_github("tensor decomposition mathematics")
    web = rt.search_web("Zaremba conjecture recent progress")
"""

import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional


class ResearchToolkit:
    """Unified research API for all Prometheus agents."""

    def __init__(self):
        self._load_keys()
        self._setup_ssl()
        self._last_request = {}

    def _load_keys(self):
        """Load API keys from Eos .env file."""
        eos_env = Path(__file__).resolve().parent.parent.parent / "agents" / "Eos" / ".env"
        if eos_env.exists():
            for line in eos_env.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

        self.s2_key = os.environ.get("S2_API_KEY")
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.tavily_key = os.environ.get("TAVILY_API_KEY")
        self.serper_key = os.environ.get("SERPER_API_KEY")

    def _setup_ssl(self):
        self.ctx = ssl.create_default_context()
        try:
            import certifi
            self.ctx.load_verify_locations(certifi.where())
        except ImportError:
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE

    def _rate_limit(self, source: str, min_interval: float = 1.5):
        """Respect rate limits."""
        last = self._last_request.get(source, 0)
        elapsed = time.time() - last
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request[source] = time.time()

    def _get(self, url: str, headers: dict = None, timeout: int = 20) -> dict:
        """Make a GET request and return JSON."""
        h = {"User-Agent": "Prometheus-Aporia/1.0"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout, context=self.ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, url: str, data: dict, headers: dict = None, timeout: int = 20) -> dict:
        """Make a POST request and return JSON."""
        h = {"User-Agent": "Prometheus-Aporia/1.0", "Content-Type": "application/json"}
        if headers:
            h.update(headers)
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=timeout, context=self.ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ----- SEMANTIC SCHOLAR -----

    def search_papers(self, query: str, limit: int = 10, year_from: str = None) -> list:
        """Search Semantic Scholar for papers. Returns list of dicts."""
        if not self.s2_key:
            return []
        self._rate_limit("s2", 1.2)
        params = {
            "query": query, "limit": limit,
            "fields": "title,authors,year,citationCount,tldr,openAccessPdf,url,externalIds",
        }
        if year_from:
            params["publicationDateOrYear"] = f"{year_from}:"
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?{urllib.parse.urlencode(params)}"
        try:
            data = self._get(url, headers={"x-api-key": self.s2_key})
            results = []
            for p in data.get("data", []):
                if not p.get("title"):
                    continue
                results.append({
                    "source": "s2",
                    "title": p["title"],
                    "authors": [a.get("name", "") for a in (p.get("authors") or [])[:3]],
                    "year": p.get("year"),
                    "citations": p.get("citationCount", 0),
                    "tldr": (p.get("tldr") or {}).get("text", ""),
                    "url": p.get("url", ""),
                    "arxiv": (p.get("externalIds") or {}).get("ArXiv", ""),
                    "pdf": (p.get("openAccessPdf") or {}).get("url", ""),
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    # ----- OPENALEX -----

    def search_openalex(self, query: str, limit: int = 10, year_from: str = None) -> list:
        """Search OpenAlex (free, no key, 100K/day)."""
        self._rate_limit("openalex", 0.5)
        params = {
            "search": query, "per_page": limit,
            "sort": "cited_by_count:desc",
            "mailto": "prometheus@users.noreply.github.com",
        }
        if year_from:
            params["filter"] = f"from_publication_date:{year_from}"
        url = f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"
        try:
            data = self._get(url)
            results = []
            for w in data.get("results", []):
                if not w.get("title"):
                    continue
                authors = [a.get("author", {}).get("display_name", "")
                           for a in (w.get("authorships") or [])[:3]]
                results.append({
                    "source": "openalex",
                    "title": w["title"],
                    "authors": authors,
                    "year": int(str(w.get("publication_date", "2024"))[:4]) if w.get("publication_date") else None,
                    "citations": w.get("cited_by_count", 0),
                    "url": w.get("doi", w.get("id", "")),
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    # ----- GITHUB -----

    def search_github(self, query: str, limit: int = 10) -> list:
        """Search GitHub for repositories."""
        if not self.github_token:
            return []
        self._rate_limit("github", 6.0)
        params = urllib.parse.urlencode({
            "q": query, "sort": "stars", "order": "desc", "per_page": limit,
        })
        url = f"https://api.github.com/search/repositories?{params}"
        try:
            data = self._get(url, headers={
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            })
            results = []
            for repo in data.get("items", []):
                results.append({
                    "source": "github",
                    "name": repo.get("full_name", ""),
                    "url": repo.get("html_url", ""),
                    "description": (repo.get("description") or "")[:200],
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "updated": (repo.get("updated_at") or "")[:10],
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    # ----- TAVILY -----

    def search_web(self, query: str, limit: int = 5) -> list:
        """Search the web via Tavily (limited budget: ~1/hour)."""
        if not self.tavily_key:
            return []
        self._rate_limit("tavily", 60.0)  # Very conservative
        try:
            data = self._post("https://api.tavily.com/search", {
                "api_key": self.tavily_key,
                "query": query,
                "max_results": limit,
                "search_depth": "basic",
            })
            results = []
            for r in data.get("results", []):
                results.append({
                    "source": "tavily",
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:200],
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    # ----- SERPER (Google Search) -----

    def search_google(self, query: str, limit: int = 5) -> list:
        """Search Google via Serper API."""
        if not self.serper_key:
            return []
        self._rate_limit("serper", 3.0)
        try:
            data = self._post("https://google.serper.dev/search", {
                "q": query, "num": limit,
            }, headers={"X-API-KEY": self.serper_key})
            results = []
            for r in data.get("organic", []):
                results.append({
                    "source": "serper",
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "snippet": r.get("snippet", "")[:200],
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    # ----- CONVENIENCE -----

    def search_all(self, query: str, limit: int = 5) -> dict:
        """Search across all available sources. Returns dict keyed by source."""
        return {
            "s2": self.search_papers(query, limit=limit, year_from="2024-01-01"),
            "openalex": self.search_openalex(query, limit=limit, year_from="2024-01-01"),
            "github": self.search_github(query, limit=3),
        }

    def available_sources(self) -> dict:
        """Show which APIs are configured."""
        return {
            "semantic_scholar": bool(self.s2_key),
            "openalex": True,  # Always free
            "github": bool(self.github_token),
            "tavily": bool(self.tavily_key),
            "serper": bool(self.serper_key),
        }


if __name__ == "__main__":
    rt = ResearchToolkit()
    print("Research Toolkit — Available sources:")
    for source, available in rt.available_sources().items():
        status = "READY" if available else "NO KEY"
        print(f"  {source:20s}: {status}")

    print("\nTest search: 'pair correlation L-function zeros'")
    papers = rt.search_papers("pair correlation L-function zeros", limit=3)
    for p in papers:
        if "error" not in p:
            print(f"  [{p['year']}] {p['title'][:60]} (cites:{p['citations']})")

    print("\nTest GitHub: 'knot invariant computation'")
    repos = rt.search_github("knot invariant computation", limit=3)
    for r in repos:
        if "error" not in r:
            print(f"  {r['name']} ({r['stars']} stars) - {r['description'][:50]}")
