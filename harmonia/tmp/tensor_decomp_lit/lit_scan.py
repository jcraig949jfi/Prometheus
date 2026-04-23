"""
Literature scan for tensor-decomposition / low-rank-identity research.

Uses three public APIs directly (arxiv / OpenAlex / Semantic Scholar) with
polite rate-limits. Pattern borrowed from agents/eos but with custom queries
and no 30-day filter (we want historical + recent).

Usage:
    python lit_scan.py <pass_number>

Output: pass<N>_results.json + pass<N>_digest.md in the same directory.
"""
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

UA = "Harmonia-LitScan/1.0 (Prometheus; mailto:prometheus-project@users.noreply.github.com)"


# -----------------------------------------------------------------------------
# Query packs
# -----------------------------------------------------------------------------

PASSES = {
    1: {
        "name": "prior_art_calibration",
        "description": "Known landmarks in low-rank tensor decomposition and algorithm search",
        "arxiv_queries": [
            'ti:"AlphaTensor" OR abs:"AlphaTensor"',
            'ti:"matrix multiplication" AND abs:"decomposition" AND abs:"rank"',
            'ti:"Strassen" OR abs:"Strassen algorithm"',
            'abs:"tensor decomposition" AND abs:"CP" AND abs:"rank"',
            'abs:"fast matrix multiplication" AND abs:"tensor"',
        ],
        "openalex_queries": [
            "AlphaTensor deep learning matrix multiplication",
            "Strassen tensor rank algorithm discovery",
            "Laderman Smirnov matrix multiplication decomposition",
            "Kolda Bader tensor decomposition survey",
            "bilinear complexity matrix multiplication",
        ],
        "s2_queries": [
            "AlphaTensor discovering matrix multiplication algorithms",
            "fast matrix multiplication algorithm tensor rank",
            "bilinear algorithms Strassen decomposition",
        ],
    },
    2: {
        "name": "qd_times_tensor",
        "description": "MAP-Elites / Quality-Diversity × tensor decomposition / algorithm discovery",
        "arxiv_queries": [
            'abs:"MAP-Elites" AND abs:"algorithm"',
            'abs:"quality diversity" AND abs:"algorithm discovery"',
            'abs:"quality diversity" AND abs:"matrix multiplication"',
            'abs:"evolutionary" AND abs:"tensor decomposition"',
            'abs:"genetic algorithm" AND abs:"matrix multiplication"',
            'ti:"AlphaEvolve" OR abs:"AlphaEvolve"',
            'abs:"LLM" AND abs:"evolutionary" AND abs:"algorithm discovery"',
        ],
        "openalex_queries": [
            "MAP-Elites quality diversity algorithm discovery",
            "evolutionary tensor decomposition search",
            "AlphaEvolve LLM evolutionary algorithm design",
            "quality diversity matrix multiplication",
        ],
        "s2_queries": [
            "MAP-Elites algorithm discovery",
            "quality diversity tensor decomposition",
            "AlphaEvolve LLM-guided evolutionary algorithm",
        ],
    },
    3: {
        "name": "frontier_adjacencies",
        "description": "Border rank, finite-field, symmetric, polynomial-multiplication tensors",
        "arxiv_queries": [
            'abs:"border rank" AND abs:"tensor"',
            'abs:"symmetric tensor decomposition"',
            'abs:"tensor network" AND abs:"rank" AND abs:"algorithm"',
            'abs:"polynomial multiplication" AND abs:"algorithm" AND abs:"complexity"',
            'abs:"Karatsuba" AND abs:"multiplication" AND abs:"rank"',
            'abs:"tensor decomposition" AND abs:"finite field"',
            'abs:"asymptotic exponent" AND abs:"matrix multiplication"',
        ],
        "openalex_queries": [
            "border rank tensor matrix multiplication",
            "symmetric tensor decomposition rank",
            "polynomial multiplication bilinear rank finite field",
            "tensor rank omega matrix multiplication exponent",
        ],
        "s2_queries": [
            "border rank tensor algorithm",
            "polynomial multiplication rank bilinear algorithm",
            "matrix multiplication exponent omega 2024",
        ],
    },
}


# -----------------------------------------------------------------------------
# API clients
# -----------------------------------------------------------------------------

def arxiv_search(query: str, max_results: int = 15) -> list[dict]:
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"http://export.arxiv.org/api/query?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(data)
    results = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else ""
        summary_el = entry.find("atom:summary", ns)
        summary = (summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else ""
        pid_el = entry.find("atom:id", ns)
        paper_id = (pid_el.text or "").strip() if pid_el is not None else ""
        pub_el = entry.find("atom:published", ns)
        published = (pub_el.text or "")[:10] if pub_el is not None else ""
        authors = []
        for author in entry.findall("atom:author", ns):
            name_el = author.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())
        results.append({
            "source": "arxiv",
            "query": query,
            "title": title,
            "authors": authors[:8],
            "url": paper_id,
            "date": published,
            "summary": summary[:800],
        })
    return results


def openalex_search(query: str, per_page: int = 15) -> list[dict]:
    params = urllib.parse.urlencode({
        "search": query,
        "sort": "relevance_score:desc",
        "per_page": per_page,
        "mailto": "prometheus-project@users.noreply.github.com",
    })
    url = f"https://api.openalex.org/works?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for work in data.get("results", []):
        title = work.get("title") or ""
        doi = work.get("doi") or ""
        pub_date = work.get("publication_date") or ""
        cited = work.get("cited_by_count", 0)
        authors = []
        for a in (work.get("authorships") or [])[:8]:
            auth = a.get("author", {})
            if auth.get("display_name"):
                authors.append(auth["display_name"])
        abstract = ""
        inv = work.get("abstract_inverted_index")
        if inv:
            pos_word = {}
            for word, positions in inv.items():
                for pos in positions:
                    pos_word[pos] = word
            abstract = " ".join(pos_word[k] for k in sorted(pos_word.keys()))[:800]
        results.append({
            "source": "openalex",
            "query": query,
            "title": title,
            "authors": authors,
            "url": doi or work.get("id", ""),
            "date": pub_date,
            "summary": abstract,
            "cited_by": cited,
        })
    return results


def s2_search(query: str, limit: int = 15) -> list[dict]:
    api_key = os.environ.get("S2_API_KEY")
    params = urllib.parse.urlencode({
        "query": query,
        "fields": "title,authors,year,citationCount,tldr,openAccessPdf,publicationDate,url,abstract",
        "limit": limit,
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    headers = {"User-Agent": UA}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for p in data.get("data", []):
        title = p.get("title") or ""
        authors = [a.get("name", "") for a in (p.get("authors") or [])[:8]]
        tldr_o = p.get("tldr") or {}
        tldr = tldr_o.get("text", "") if isinstance(tldr_o, dict) else ""
        abstract = p.get("abstract") or ""
        pdf_o = p.get("openAccessPdf") or {}
        pdf = pdf_o.get("url", "") if isinstance(pdf_o, dict) else ""
        s2_url = p.get("url") or ""
        cited = p.get("citationCount", 0) or 0
        pub_date = p.get("publicationDate") or str(p.get("year", ""))
        summary = tldr or abstract[:800]
        results.append({
            "source": "semantic_scholar",
            "query": query,
            "title": title,
            "authors": authors,
            "url": s2_url,
            "pdf_url": pdf,
            "date": pub_date,
            "summary": summary[:800],
            "cited_by": cited,
            "tldr": tldr,
        })
    return results


# -----------------------------------------------------------------------------
# Runner
# -----------------------------------------------------------------------------

def run_pass(pass_num: int):
    pack = PASSES[pass_num]
    print(f"\n=== Pass {pass_num}: {pack['name']} ===")
    print(f"{pack['description']}\n")

    all_results = []

    # arxiv: 3s minimum between requests
    print("[arxiv]")
    for q in pack["arxiv_queries"]:
        try:
            time.sleep(3.5)
            r = arxiv_search(q, max_results=10)
            print(f"  {q!r:60s} -> {len(r)} results")
            all_results.extend(r)
        except Exception as e:
            print(f"  {q!r:60s} -> ERROR: {e}")

    # OpenAlex: 0.5s is polite
    print("\n[openalex]")
    for q in pack["openalex_queries"]:
        try:
            time.sleep(0.5)
            r = openalex_search(q, per_page=10)
            print(f"  {q!r:60s} -> {len(r)} results")
            all_results.extend(r)
        except Exception as e:
            print(f"  {q!r:60s} -> ERROR: {e}")

    # S2: 15s interval without key (rate-limited easily), 2s with key
    interval = 2.0 if os.environ.get("S2_API_KEY") else 15.0
    print(f"\n[s2, interval={interval}s]")
    for q in pack["s2_queries"]:
        try:
            time.sleep(interval)
            r = s2_search(q, limit=10)
            print(f"  {q!r:60s} -> {len(r)} results")
            all_results.extend(r)
        except Exception as e:
            print(f"  {q!r:60s} -> ERROR: {e}")

    # Deduplicate by (source, title) — different queries often surface the same paper
    seen = set()
    unique = []
    for r in all_results:
        key = (r.get("source"), (r.get("title") or "").strip().lower()[:120])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    out_json = HERE / f"pass{pass_num}_results.json"
    out_json.write_text(
        json.dumps({
            "pass": pass_num,
            "name": pack["name"],
            "description": pack["description"],
            "run_timestamp": datetime.utcnow().isoformat() + "Z",
            "n_raw": len(all_results),
            "n_unique": len(unique),
            "results": unique,
        }, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\n  raw={len(all_results)} unique={len(unique)} -> {out_json}")
    return unique


if __name__ == "__main__":
    pass_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_pass(pass_num)
