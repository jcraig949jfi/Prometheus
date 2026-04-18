"""
Aporia Literature Scanner — Maps papers to open problems using Semantic Scholar.

Uses Eos's S2 API key. Rate-limited to 1 req/sec with key.
Scans for recent papers related to each Bucket A/B problem.

Usage:
    python aporia/scripts/literature_scanner.py              # Scan top 20 problems
    python aporia/scripts/literature_scanner.py --all        # Scan all 537
    python aporia/scripts/literature_scanner.py --id MATH-0063  # Scan specific problem
"""

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Load S2 API key from Eos's .env
EOS_ENV = Path(__file__).resolve().parent.parent.parent / "agents" / "Eos" / ".env"
if EOS_ENV.exists():
    for line in EOS_ENV.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

S2_API_KEY = os.environ.get("S2_API_KEY")
if not S2_API_KEY:
    print("ERROR: No S2_API_KEY found. Check agents/Eos/.env")
    sys.exit(1)

# SSL context
CTX = ssl.create_default_context()
try:
    import certifi
    CTX.load_verify_locations(certifi.where())
except ImportError:
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

# Search queries mapped from problem IDs to S2 search terms
PROBLEM_QUERIES = {
    "MATH-0062": "pair correlation zeros L-function GUE random matrix",
    "MATH-0063": "Birch Swinnerton-Dyer conjecture elliptic curve rank",
    "MATH-0042": "Lehmer Mahler measure polynomial lower bound",
    "MATH-0136": "abc conjecture Szpiro elliptic curve discriminant",
    "MATH-0130": "Langlands reciprocity Artin representation modular form",
    "MATH-0151": "Chowla conjecture Mobius autocorrelation",
    "MATH-0165": "moments L-functions random matrix Keating Snaith",
    "MATH-0260": "Artin conjecture L-function entire holomorphic",
    "MATH-0334": "volume conjecture colored Jones polynomial hyperbolic",
    "MATH-0370": "density hypothesis zeros L-function",
    "MATH-0492": "Zaremba conjecture continued fraction bounded partial quotients",
    "MATH-0501": "L-space conjecture left-orderable taut foliation",
    "MATH-0508": "Selberg zeta function compact hyperbolic surface",
    "MATH-0518": "Greenberg conjecture Iwasawa invariants totally real",
    "MATH-0522": "rational periodic points quadratic polynomial dynatomic",
    "MATH-0530": "chromatic symmetric function tree distinguishing",
    "MATH-0531": "Cohen-Lenstra heuristics class group number field",
    "MATH-0532": "Selmer group distribution quadratic twist elliptic curve",
    "MATH-0529": "analytic combinatorics singularity generating function",
    "MATH-0537": "spatial Moran model fixation probability",
    # Void detection
    "VOID-KNOT": "arithmetic topology knot prime Morishita A-polynomial",
}


def search_s2(query: str, limit: int = 10, year_from: str = None) -> list:
    """Search Semantic Scholar with API key."""
    params = {
        "query": query,
        "fields": "title,authors,year,citationCount,tldr,openAccessPdf,publicationDate,url,externalIds",
        "limit": limit,
    }
    if year_from:
        params["publicationDateOrYear"] = f"{year_from}:"

    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": "Aporia/1.0 (Prometheus Project)",
        "x-api-key": S2_API_KEY,
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("data", [])
    except Exception as e:
        print(f"  S2 error: {e}")
        return []


def scan_problem(problem_id: str, query: str, limit: int = 10) -> dict:
    """Scan for papers related to a specific problem."""
    # Recent papers (last 2 years)
    recent = search_s2(query, limit=limit, year_from="2024-01-01")
    time.sleep(1.1)  # Rate limit

    # High-citation papers (all time)
    classics = search_s2(query, limit=5)
    time.sleep(1.1)

    result = {
        "problem_id": problem_id,
        "query": query,
        "scan_time": datetime.now().isoformat(),
        "recent_papers": [],
        "classic_papers": [],
    }

    for p in recent:
        result["recent_papers"].append({
            "title": p.get("title", ""),
            "authors": [a.get("name", "") for a in (p.get("authors") or [])[:3]],
            "year": p.get("year"),
            "citations": p.get("citationCount", 0),
            "tldr": (p.get("tldr") or {}).get("text", ""),
            "url": p.get("url", ""),
            "arxiv": (p.get("externalIds") or {}).get("ArXiv", ""),
        })

    for p in classics:
        result["classic_papers"].append({
            "title": p.get("title", ""),
            "year": p.get("year"),
            "citations": p.get("citationCount", 0),
        })

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Scan all problems")
    parser.add_argument("--id", type=str, help="Scan specific problem ID")
    parser.add_argument("--limit", type=int, default=10, help="Papers per query")
    args = parser.parse_args()

    if args.id:
        queries = {args.id: PROBLEM_QUERIES.get(args.id, args.id)}
    elif args.all:
        queries = PROBLEM_QUERIES
    else:
        # Default: top 20 from research queue
        queries = dict(list(PROBLEM_QUERIES.items())[:20])

    print(f"Scanning {len(queries)} problems via Semantic Scholar...")
    print(f"API key: {S2_API_KEY[:8]}...")
    print()

    all_results = []
    for i, (pid, query) in enumerate(queries.items()):
        print(f"[{i+1}/{len(queries)}] {pid}: {query[:50]}...")
        result = scan_problem(pid, query, limit=args.limit)
        n_recent = len(result["recent_papers"])
        n_classic = len(result["classic_papers"])
        print(f"  Found: {n_recent} recent, {n_classic} classic")
        if result["recent_papers"]:
            top = result["recent_papers"][0]
            print(f"  Top recent: [{top['year']}] {top['title'][:60]}")
        all_results.append(result)

    # Save
    output_path = Path("aporia/data/literature_scan.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "scan_date": datetime.now().isoformat(),
        "n_problems": len(all_results),
        "results": all_results,
    }, indent=2), encoding="utf-8")
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
