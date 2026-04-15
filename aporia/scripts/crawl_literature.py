"""
Aporia — Literature crawler for open questions.

For each question in a domain's questions.jsonl, searches Semantic Scholar
and arXiv for related papers, then appends results to the question's
`papers` field.

Usage:
    python scripts/crawl_literature.py                    # all domains
    python scripts/crawl_literature.py mathematics        # one domain
    python scripts/crawl_literature.py mathematics --limit 5  # first 5 Qs
    python scripts/crawl_literature.py --dry-run          # preview queries

APIs used (no keys required):
    - Semantic Scholar Academic Graph API (free, 100 req/5min)
    - arXiv API (free, 3 req/sec)

Rate limiting is built in.
"""

import argparse, json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RATE_LIMIT_S2 = 4.0    # seconds between Semantic Scholar calls (100/5min, generous)
RATE_LIMIT_ARXIV = 4.0  # seconds between arXiv calls (3/sec limit, generous)
MAX_PAPERS_PER_Q = 10
MAX_RETRIES = 3
RETRY_BACKOFF = 10     # seconds to wait on 429 before retry

# ── HTTP helpers ─────────────────────────────────────────────────────────

def _get_json(url, timeout=30):
    """GET a URL and parse JSON response, with retry on 429."""
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(url, headers={"User-Agent": "Aporia/1.0 (research-crawler; mailto:jcraig949@gmail.com)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF * (attempt + 1)
                print(f"    [429] Rate limited, waiting {wait}s before retry {attempt+2}/{MAX_RETRIES}...")
                time.sleep(wait)
                continue
            print(f"    [WARN] HTTP {e.code} for {url[:120]}")
            return None
        except Exception as e:
            print(f"    [WARN] {e} for {url[:120]}")
            return None


def _get_text(url, timeout=30):
    """GET a URL and return raw text, with retry on 429."""
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(url, headers={"User-Agent": "Aporia/1.0 (research-crawler; mailto:jcraig949@gmail.com)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF * (attempt + 1)
                print(f"    [429] Rate limited, waiting {wait}s before retry {attempt+2}/{MAX_RETRIES}...")
                time.sleep(wait)
                continue
            print(f"    [WARN] HTTP {e.code} for {url[:120]}")
            return None
        except Exception as e:
            print(f"    [WARN] {e} for {url[:120]}")
            return None


# ── Semantic Scholar ─────────────────────────────────────────────────────

def search_semantic_scholar(query, limit=5):
    """Search Semantic Scholar for papers matching a query string."""
    encoded = urllib.parse.quote(query)
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={encoded}&limit={limit}"
        f"&fields=title,authors,year,citationCount,url,abstract,externalIds"
    )
    data = _get_json(url)
    if not data or "data" not in data:
        return []

    papers = []
    for p in data["data"]:
        arxiv_id = (p.get("externalIds") or {}).get("ArXiv", "")
        papers.append({
            "source": "semantic_scholar",
            "title": p.get("title", ""),
            "authors": [a.get("name", "") for a in (p.get("authors") or [])],
            "year": p.get("year"),
            "citations": p.get("citationCount", 0),
            "url": p.get("url", ""),
            "arxiv_id": arxiv_id,
            "abstract_snippet": (p.get("abstract") or "")[:300],
        })
    return papers


# ── arXiv ────────────────────────────────────────────────────────────────

def search_arxiv(query, max_results=5):
    """Search arXiv API for papers matching a query string."""
    encoded = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=all:{encoded}&start=0&max_results={max_results}"
        f"&sortBy=relevance&sortOrder=descending"
    )
    xml = _get_text(url)
    if not xml:
        return []

    papers = []
    # Simple XML parsing — no dependency on lxml/feedparser
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.DOTALL)
    for entry in entries:
        title = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        title = title.group(1).strip().replace("\n", " ") if title else ""
        summary = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        summary = summary.group(1).strip().replace("\n", " ")[:300] if summary else ""
        published = re.search(r"<published>(.*?)</published>", entry)
        year = int(published.group(1)[:4]) if published else None
        arxiv_url = re.search(r'<id>(.*?)</id>', entry)
        arxiv_url = arxiv_url.group(1).strip() if arxiv_url else ""
        authors = re.findall(r"<name>(.*?)</name>", entry)

        papers.append({
            "source": "arxiv",
            "title": title,
            "authors": authors[:5],  # cap at 5 authors
            "year": year,
            "citations": None,
            "url": arxiv_url,
            "arxiv_id": arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else "",
            "abstract_snippet": summary,
        })
    return papers


# ── Query builder ────────────────────────────────────────────────────────

def build_query(question):
    """Build a search query from a question's title and subdomain."""
    title = question["title"]
    subdomain = question.get("subdomain", "").replace("_", " ")
    # For math, prepend "open problem" to improve relevance
    if question["domain"] == "mathematics":
        return f"{title} conjecture {subdomain}"
    return f"{title} open problem {subdomain}"


# ── Main crawl loop ─────────────────────────────────────────────────────

def crawl_domain(domain, limit=None, dry_run=False):
    """Crawl literature for all questions in a domain."""
    qfile = ROOT / domain / "questions.jsonl"
    if not qfile.exists():
        print(f"  [SKIP] No questions.jsonl for {domain}")
        return

    # Read all questions
    questions = []
    with open(qfile, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    if limit:
        questions = questions[:limit]

    print(f"\n{'='*60}")
    print(f"  {domain.upper()} — {len(questions)} questions to crawl")
    print(f"{'='*60}")

    updated = 0
    for i, q in enumerate(questions):
        qid = q["id"]
        title = q["title"]
        query = build_query(q)

        # Skip if already has papers
        if q.get("papers") and len(q["papers"]) > 0:
            print(f"  [{qid}] {title} — already has {len(q['papers'])} papers, skipping")
            continue

        print(f"  [{qid}] {title}")
        print(f"    query: {query}")

        if dry_run:
            continue

        # Search Semantic Scholar
        papers = []
        s2_results = search_semantic_scholar(query, limit=5)
        papers.extend(s2_results)
        print(f"    S2: {len(s2_results)} papers")
        time.sleep(RATE_LIMIT_S2)

        # Search arXiv
        arxiv_results = search_arxiv(query, max_results=5)
        papers.extend(arxiv_results)
        print(f"    arXiv: {len(arxiv_results)} papers")
        time.sleep(RATE_LIMIT_ARXIV)

        # Deduplicate by title (case-insensitive)
        seen_titles = set()
        deduped = []
        for p in papers:
            key = p["title"].lower().strip()
            if key and key not in seen_titles:
                seen_titles.add(key)
                deduped.append(p)
        papers = deduped[:MAX_PAPERS_PER_Q]

        q["papers"] = papers
        updated += 1
        print(f"    -> {len(papers)} unique papers attached")

    # Write back
    if not dry_run and updated > 0:
        with open(qfile, "w", encoding="utf-8") as f:
            for entry in questions:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\n  Wrote {updated} updated questions back to {qfile}")
    elif dry_run:
        print(f"\n  [DRY RUN] Would crawl {len(questions)} questions")


def main():
    parser = argparse.ArgumentParser(description="Aporia literature crawler")
    parser.add_argument("domain", nargs="?", default=None, help="Single domain to crawl (default: all)")
    parser.add_argument("--limit", type=int, default=None, help="Max questions per domain")
    parser.add_argument("--dry-run", action="store_true", help="Preview queries without fetching")
    args = parser.parse_args()

    if args.domain:
        crawl_domain(args.domain, limit=args.limit, dry_run=args.dry_run)
    else:
        # Crawl all domains
        for domain_dir in sorted(ROOT.iterdir()):
            if domain_dir.is_dir() and (domain_dir / "questions.jsonl").exists():
                crawl_domain(domain_dir.name, limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
