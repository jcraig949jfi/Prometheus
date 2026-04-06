"""
External Research Feed — Daily pipeline for mining improvement ideas.
=====================================================================
Three sources, run once per day (or on demand):

1. Semantic Scholar + arXiv — academic papers on autonomous science, agentic research
2. Tavily — news, blogs, web content on the same
3. Gemini Deep Research — synthesis query on pipeline improvement

Results feed into the suggestions ledger for HITL review.
Report saved to convergence/reports/external_research_{date}.md

Rate limits (from Eos patterns):
  - Semantic Scholar: 2s interval with key, 5s without
  - arXiv: 3s interval (public)
  - Tavily: 1 query per cycle (~1000/month budget)
  - Gemini: 1 deep research call (counts against 20/day limit)

Usage:
    python external_research.py [--skip-gemini] [--skip-tavily] [--skip-scholarly]
"""

import json
import os
import ssl
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

# Windows SSL workaround — certifi if available, else unverified
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

REPORT_DIR = Path(__file__).resolve().parents[2] / "convergence" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Eos .env fallback for keys not in central keys.py
EOS_ENV = Path(__file__).resolve().parents[3] / "agents" / "eos" / ".env"


def _get_env_key(name: str) -> str:
    """Get API key from environment, then Eos .env fallback."""
    val = os.environ.get(name)
    if val:
        return val
    if EOS_ENV.exists():
        for line in EOS_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


def _safe_request(url: str, headers: dict = None, data: bytes = None,
                  method: str = "GET", timeout: int = 30) -> dict | str | None:
    """Make HTTP request with error handling."""
    req = urllib.request.Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            body = resp.read().decode("utf-8")
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return json.loads(body)
            return body
    except Exception as e:
        print(f"    Request failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Source 1: Semantic Scholar + arXiv
# ---------------------------------------------------------------------------

SCHOLARLY_QUERIES = [
    "autonomous scientific discovery machine learning",
    "automated hypothesis generation falsification",
    "agentic AI research pipeline",
    "cross-domain mathematical correlation discovery",
    "self-improving AI research loop",
]


def search_semantic_scholar(query: str, limit: int = 10) -> list[dict]:
    """Search Semantic Scholar for recent papers."""
    api_key = _get_env_key("S2_API_KEY")
    headers = {"User-Agent": "Charon/1.0 (Prometheus Project)"}
    if api_key:
        headers["x-api-key"] = api_key

    params = urllib.parse.urlencode({
        "query": query,
        "fields": "title,authors,year,citationCount,tldr,url,publicationDate",
        "publicationDateOrYear": f"{_days_ago(90)}:",
        "limit": limit,
        "fieldsOfStudy": "Computer Science,Mathematics",
    })

    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    time.sleep(2.0 if api_key else 5.0)

    result = _safe_request(url, headers=headers)
    if not result or not isinstance(result, dict):
        return []

    papers = []
    for p in result.get("data", []):
        authors = [a.get("name", "") for a in (p.get("authors") or [])[:3]]
        papers.append({
            "title": p.get("title", ""),
            "authors": authors,
            "year": p.get("year"),
            "url": p.get("url", ""),
            "citations": p.get("citationCount", 0),
            "summary": (p.get("tldr") or {}).get("text", ""),
            "date": p.get("publicationDate", ""),
            "source": "semantic_scholar",
        })
    return papers


def search_arxiv(query: str, limit: int = 10) -> list[dict]:
    """Search arXiv for recent preprints."""
    params = urllib.parse.urlencode({
        "search_query": f'all:"{query}"',
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })

    url = f"http://export.arxiv.org/api/query?{params}"
    time.sleep(3.0)

    result = _safe_request(url)
    if not result or not isinstance(result, str):
        return []

    papers = []
    try:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(result)
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", "", ns) or "").strip().replace("\n", " ")
            summary = (entry.findtext("atom:summary", "", ns) or "").strip()[:300]
            authors = [a.findtext("atom:name", "", ns)
                       for a in entry.findall("atom:author", ns)][:3]
            url = entry.findtext("atom:id", "", ns) or ""
            published = entry.findtext("atom:published", "", ns) or ""
            papers.append({
                "title": title,
                "authors": authors,
                "url": url,
                "date": published[:10],
                "summary": summary,
                "source": "arxiv",
            })
    except ET.ParseError:
        pass
    return papers


def run_scholarly_search() -> list[dict]:
    """Run all scholarly queries. Returns combined paper list."""
    print("  [Scholarly] Searching Semantic Scholar + arXiv...")
    all_papers = []
    seen_titles = set()

    for query in SCHOLARLY_QUERIES:
        print(f"    Query: {query}")

        # Semantic Scholar
        papers = search_semantic_scholar(query, limit=5)
        for p in papers:
            if p["title"].lower() not in seen_titles:
                seen_titles.add(p["title"].lower())
                all_papers.append(p)

        # arXiv
        papers = search_arxiv(query, limit=5)
        for p in papers:
            if p["title"].lower() not in seen_titles:
                seen_titles.add(p["title"].lower())
                all_papers.append(p)

    print(f"  [Scholarly] Found {len(all_papers)} unique papers")
    return all_papers


# ---------------------------------------------------------------------------
# Source 2: Tavily web search
# ---------------------------------------------------------------------------

TAVILY_QUERIES = [
    "autonomous AI scientific research pipeline 2026",
    "self-improving machine learning research agent",
]


def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search Tavily for web content."""
    api_key = _get_env_key("TAVILY_API_KEY")
    if not api_key:
        print("    [Tavily] No API key found — skipping")
        return []

    payload = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
    }).encode("utf-8")

    time.sleep(5.0)
    result = _safe_request(
        "https://api.tavily.com/search",
        headers={"Content-Type": "application/json"},
        data=payload, method="POST",
    )

    if not result or not isinstance(result, dict):
        return []

    items = []
    for r in result.get("results", []):
        items.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("content") or "")[:300],
            "score": r.get("score", 0),
            "source": "tavily",
        })
    return items


def run_tavily_search() -> list[dict]:
    """Run Tavily queries. Budget: 1-2 queries per day."""
    print("  [Tavily] Searching web...")
    all_items = []
    for query in TAVILY_QUERIES[:2]:  # Max 2 per day
        print(f"    Query: {query}")
        items = search_tavily(query)
        all_items.extend(items)
    print(f"  [Tavily] Found {len(all_items)} web results")
    return all_items


# ---------------------------------------------------------------------------
# Source 3: Gemini synthesis (optional — uses tokens)
# ---------------------------------------------------------------------------

GEMINI_RESEARCH_PROMPT = """You are advising a team building an autonomous scientific research pipeline. The pipeline:
- Ingests mathematical databases (OEIS, LMFDB, mathlib, Metamath, Materials Project)
- Generates cross-domain hypotheses via LLM
- Searches datasets computationally
- Runs an 11-test falsification battery (no LLM in the loop)
- Branches results into follow-up hypotheses mechanically
- Loops with periodic self-improvement reviews

Current weaknesses:
- Hypothesis quality depends on LLM creativity
- Search functions return aggregates but can't do semantic joins across datasets
- Battery tests are domain-agnostic (same 11 tests for all hypotheses)
- No literature grounding for hypothesis plausibility

What are the 5 most impactful improvements we should make? For each:
1. What specifically to change
2. Why it matters (what failure mode it prevents)
3. What the first implementation step would be

Be concrete. Name specific techniques, papers, or tools. No platitudes."""


def run_gemini_research() -> str:
    """Run a Gemini synthesis query. Returns response text."""
    print("  [Gemini] Running deep research query...")
    try:
        from keys import get_key
        from google import genai
        client = genai.Client(api_key=get_key("GEMINI"))
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=GEMINI_RESEARCH_PROMPT,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=4096,
                temperature=0.3,
            ),
        )
        elapsed = time.time() - t0
        text = response.text
        print(f"  [Gemini] Done in {elapsed:.1f}s ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"  [Gemini] Failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# Report and suggestions
# ---------------------------------------------------------------------------

def generate_report(papers: list, web_items: list, gemini_text: str) -> Path:
    """Generate the daily external research report."""
    now = datetime.now()
    report_path = REPORT_DIR / f"external_research_{now.strftime('%Y%m%d')}.md"

    lines = [
        f"# External Research Feed: {now.strftime('%Y-%m-%d')}",
        "", "---", "",
    ]

    # Papers
    lines.append(f"## Academic Papers ({len(papers)} found)")
    lines.append("")
    for p in papers[:20]:
        authors = ", ".join(p.get("authors", [])[:3])
        lines.append(f"### {p['title']}")
        lines.append(f"**{authors}** ({p.get('date', '?')}) | "
                     f"{p.get('source', '?')} | {p.get('citations', 0)} citations")
        if p.get("url"):
            lines.append(f"URL: {p['url']}")
        if p.get("summary"):
            lines.append(f"> {p['summary'][:200]}")
        lines.append("")

    # Web content
    lines.append(f"## Web Content ({len(web_items)} found)")
    lines.append("")
    for w in web_items[:10]:
        lines.append(f"- **{w['title']}** ([link]({w.get('url', '')}))")
        if w.get("content"):
            lines.append(f"  > {w['content'][:150]}")
        lines.append("")

    # Gemini synthesis
    if gemini_text:
        lines.append("## Gemini Pipeline Improvement Research")
        lines.append("")
        lines.append(gemini_text)
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated: {now.isoformat()} | Papers: {len(papers)} | "
                f"Web: {len(web_items)} | Gemini: {'yes' if gemini_text else 'no'}*")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def feed_suggestions(papers: list, web_items: list, gemini_text: str):
    """Extract actionable suggestions and add to ledger."""
    try:
        from suggestions import add
    except ImportError:
        return

    # High-citation papers about autonomous research → data_enrichment ideas
    for p in papers:
        if p.get("citations", 0) >= 10 and p.get("summary"):
            add(source=f"scholarly:{p['source']}",
                category="pipeline_change",
                description=f"Paper: {p['title'][:120]} — {p.get('summary', '')[:150]}",
                evidence=f"{p.get('citations', 0)} citations, {p.get('date', '?')}",
                priority="low")

    # Gemini suggestions → extract numbered items
    if gemini_text:
        from suggestions import add_from_council_review
        add_from_council_review(gemini_text, "gemini_research")


def archive_papers(papers: list):
    """Sort papers into domain archive folders for future reference.

    Papers are classified by keywords and filed into gitignored archive directories.
    Each domain folder accumulates over time — a searchable library of parked research.
    """
    ARCHIVE = Path(__file__).resolve().parents[2] / "convergence" / "archive"

    DOMAIN_KEYWORDS = {
        "materials_science": ["material", "crystal", "polymer", "molecular", "atomistic",
                              "photovoltaic", "battery", "catalysis", "synthesis"],
        "finance": ["financial", "stock", "market", "trading", "portfolio", "economic"],
        "cybersecurity": ["security", "vulnerability", "incident", "governance", "containment",
                          "threat", "cyber"],
        "agriculture": ["seed", "crop", "plant", "agricultural", "soil", "hyperspectral"],
        "general_agentic": ["agentic", "agent", "autonomous"],
        "domain_specific": [],  # catch-all
    }

    # Relevance keywords — papers matching these go to roadmap, not archive
    RELEVANT_KEYWORDS = ["hypothesis", "falsification", "scientific discovery",
                         "self-improving", "cross-domain", "mathematical",
                         "correlation", "research pipeline", "number theory"]

    today = datetime.now().strftime("%Y%m%d")
    domain_papers = {}

    for p in papers:
        title_lower = (p.get("title", "") + " " + p.get("summary", "")).lower()

        # Skip papers that are directly relevant (those go to roadmap)
        if any(kw in title_lower for kw in RELEVANT_KEYWORDS):
            continue

        # Classify into domain
        classified = False
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if domain == "domain_specific":
                continue
            if any(kw in title_lower for kw in keywords):
                domain_papers.setdefault(domain, []).append(p)
                classified = True
                break

        if not classified:
            domain_papers.setdefault("domain_specific", []).append(p)

    # Write to archive folders
    for domain, domain_list in domain_papers.items():
        if not domain_list:
            continue
        folder = ARCHIVE / domain
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / f"{today}_papers.md"

        lines = [f"# {domain.replace('_', ' ').title()} — Auto-archived Papers ({today})", ""]
        for p in domain_list:
            authors = ", ".join(p.get("authors", [])[:3])
            lines.append(f"### {p['title']}")
            lines.append(f"**{authors}** ({p.get('date', '?')}) | {p.get('source', '?')}")
            if p.get("url"):
                lines.append(f"URL: {p['url']}")
            if p.get("summary"):
                lines.append(f"> {p['summary'][:250]}")
            lines.append("")

        # Append if file exists (multiple runs same day), otherwise create
        if filepath.exists():
            existing = filepath.read_text(encoding="utf-8")
            filepath.write_text(existing + "\n" + "\n".join(lines), encoding="utf-8")
        else:
            filepath.write_text("\n".join(lines), encoding="utf-8")

    archived = sum(len(v) for v in domain_papers.values())
    if archived:
        print(f"  [Archive] {archived} papers filed to {len(domain_papers)} domains")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_external_research(skip_gemini: bool = False, skip_tavily: bool = False,
                          skip_scholarly: bool = False) -> Path:
    """Run the full daily external research feed."""
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"  EXTERNAL RESEARCH FEED — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*60}")

    papers = [] if skip_scholarly else run_scholarly_search()
    web_items = [] if skip_tavily else run_tavily_search()
    gemini_text = "" if skip_gemini else run_gemini_research()

    report = generate_report(papers, web_items, gemini_text)
    feed_suggestions(papers, web_items, gemini_text)
    archive_papers(papers)

    elapsed = time.time() - t0
    print(f"\n  Report: {report}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Papers: {len(papers)} | Web: {len(web_items)} | Gemini: {'yes' if gemini_text else 'no'}")
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Daily External Research Feed")
    parser.add_argument("--skip-gemini", action="store_true")
    parser.add_argument("--skip-tavily", action="store_true")
    parser.add_argument("--skip-scholarly", action="store_true")
    args = parser.parse_args()

    run_external_research(
        skip_gemini=args.skip_gemini,
        skip_tavily=args.skip_tavily,
        skip_scholarly=args.skip_scholarly,
    )
