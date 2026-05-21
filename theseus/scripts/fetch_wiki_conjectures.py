"""Fetch Wikipedia conjecture/theorem pages into the E5 cache.

Hits Wikipedia's public REST API (no key required, 100 req/s polite cap).
Pulls the lead-paragraph summary of each page name in CONJECTURE_PAGES,
falling back to the full extract if the summary is empty.

Run offline before E5 fires:
    python -m theseus.scripts.fetch_wiki_conjectures

Appends to theseus/cache/conjectures/wiki_conjectures.jsonl:
    {"title", "extract", "url", "categories", "fetched_at"}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

import urllib.parse

import requests

from theseus.config import THESEUS_ROOT
from theseus.scripts._backoff import is_rate_limited, sleep_for_retry


CACHE_DIR = THESEUS_ROOT / "cache" / "conjectures"
CACHE_PATH = CACHE_DIR / "wiki_conjectures.jsonl"


# Curated seed list of conjecture/theorem pages. The fetcher reads from
# Wikipedia's REST API which returns the page summary (lead paragraph).
# Extend this list as the corpus grows.
CONJECTURE_PAGES = (
    # Number theory
    "Riemann_hypothesis",
    "Birch_and_Swinnerton-Dyer_conjecture",
    "Goldbach's_conjecture",
    "Twin_prime_conjecture",
    "Collatz_conjecture",
    "ABC_conjecture",
    "Hodge_conjecture",
    "Modularity_theorem",
    "Mordell_conjecture",
    "Catalan's_conjecture",
    "Beal's_conjecture",
    "Erdős–Straus_conjecture",
    "Lehmer's_conjecture",
    "Sato–Tate_conjecture",
    "Vojta's_conjecture",
    "Tate_conjecture",
    "Langlands_program",
    "Stark_conjectures",
    "Bloch–Kato_conjecture",
    # Algebraic geometry
    "Standard_conjectures_on_algebraic_cycles",
    "Weil_conjectures",
    "Resolution_of_singularities",
    "Minimal_model_program",
    "Iitaka_conjecture",
    # Topology
    "Poincaré_conjecture",
    "Smooth_Poincaré_conjecture",
    "Geometrization_conjecture",
    "Whitehead_conjecture",
    "Volume_conjecture",
    # Combinatorics
    "Erdős–Faber–Lovász_conjecture",
    "Erdős–Ko–Rado_theorem",
    "Hadwiger_conjecture",
    "Four_color_theorem",
    # Modular forms / L-functions
    "Maeda's_conjecture",
    "Lehmer's_totient_problem",
    "Generalized_Riemann_hypothesis",
    # Analytic number theory
    "Polignac's_conjecture",
    "Cramér's_conjecture",
    "Firoozbakht's_conjecture",
    "Andrica's_conjecture",
    # Diophantine
    "Pillai's_conjecture",
    "Erdős_conjecture_on_arithmetic_progressions",
    "Green–Tao_theorem",
)

API = "https://en.wikipedia.org/api/rest_v1/page/summary"
HEADERS = {
    "User-Agent": "Prometheus-Theseus/0.1 (research; contact via repo)",
    "Accept": "application/json",
}


def _existing_titles(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    out: Set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = rec.get("title")
            if t:
                out.add(t)
    return out


def fetch_one(
    title: str,
    timeout: float = 10.0,
    max_429_attempts: int = 5,
) -> dict | None:
    # Wikipedia's REST API requires URL-encoded paths. Without quoting
    # apostrophes, en-dashes, and non-ASCII (Erdős, Pólya, Cramér...)
    # the request returns 404. Pass safe='' so the / in any sub-paths
    # would be encoded (we don't have any, but defensive).
    url = f"{API}/{urllib.parse.quote(title, safe='')}"
    # 429-aware retry loop. Honor Retry-After header when present.
    for attempt in range(max_429_attempts):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
        except requests.RequestException:
            return None
        if r.status_code == 200:
            j = r.json()
            extract = j.get("extract", "") or ""
            if not extract:
                return None
            return {
                "title": title,
                "extract": extract,
                "url": j.get("content_urls", {})
                       .get("desktop", {}).get("page", ""),
                "categories": [],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        if r.status_code in (429, 503):
            retry_after = None
            ra = r.headers.get("Retry-After")
            if ra:
                try:
                    retry_after = float(ra)
                except (TypeError, ValueError):
                    pass
            if attempt + 1 >= max_429_attempts:
                return None
            sleep_for_retry(
                attempt=attempt,
                base_delay=10.0,  # Wikipedia recovers quickly
                cap=120.0,
                retry_after=retry_after,
            )
            continue
        # Other status (404 etc.): give up on this title.
        return None
    return None


def fetch_and_append(
    pages: tuple[str, ...] = CONJECTURE_PAGES,
    cache_path: Path = CACHE_PATH,
    delay: float = 0.2,
) -> int:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _existing_titles(cache_path)

    appended = 0
    with cache_path.open("a", encoding="utf-8") as f:
        for title in pages:
            if title in existing:
                continue
            rec = fetch_one(title)
            if rec is None:
                time.sleep(delay)
                continue
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            existing.add(title)
            appended += 1
            time.sleep(delay)
    return appended


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.fetch_wiki_conjectures")
    p.add_argument("--cache-path", type=Path, default=CACHE_PATH)
    args = p.parse_args()

    n = fetch_and_append(cache_path=args.cache_path)
    print(f"[fetch_wiki_conjectures] appended {n} pages -> {args.cache_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
