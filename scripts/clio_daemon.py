"""
Clio — Substrate paper-mining daemon (Muse of history)

v0.1 scope: arxiv-only mining with substrate-priority queries. Dedup against
disk index. Write to agora.clio_papers (Postgres, cross-machine). Heartbeat
to agora.agent_heartbeats. NO LLM claim extraction, NO Sigma submission yet —
those layer in subsequent versions per fail-early-fail-often discipline.

Usage:
    python scripts/clio_daemon.py --once        # single cycle, then exit
    python scripts/clio_daemon.py               # loop at config interval
    python scripts/clio_daemon.py --interval 1800   # override interval

Design seams (for testability):
    - _build_arxiv_url(query, max_results)       — pure function
    - _parse_arxiv_atom(xml_bytes)               — pure function, no I/O
    - PaperIndex                                 — disk dedup, swappable path
    - _fetch_arxiv(url, timeout) → bytes         — the only HTTP call
    - run_cycle(config, paper_index, fetcher, persister) — DI for tests
"""
import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "clio_config.yaml"

# Postgres dual-write via agora_persist (defensive — fail-soft if unreachable)
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

# Quality observability — best-effort; never blocks the mining cycle
try:
    import clio_quality
    HAS_QUALITY = True
except Exception:
    HAS_QUALITY = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLIO] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("clio")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(path: Optional[Path] = None) -> dict:
    """Load YAML config. Raises FileNotFoundError if missing — fail-loud at boot."""
    import yaml
    p = path or CONFIG_PATH
    with open(p, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # Required fields
    if "arxiv_queries" not in cfg or not cfg["arxiv_queries"]:
        raise ValueError(f"clio config missing or empty 'arxiv_queries' (path={p})")
    return cfg


# ---------------------------------------------------------------------------
# Paper Index — disk-based cross-cycle dedup
# ---------------------------------------------------------------------------

class PaperIndex:
    """Persistent fingerprint index. Fingerprint = (normalized title prefix, first-author surname, year).

    Same idea as Eos's PaperIndex but local to Clio's data dir.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.index: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.index = data.get("papers", {}) if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError) as e:
            log.warning(f"paper_index load failed at {self.path}: {e}; starting fresh")
            self.index = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "_meta": {
                "description": "Clio paper-mining dedup index",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(self.index),
            },
            "papers": self.index,
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

    @staticmethod
    def fingerprint(paper: dict) -> str:
        """Stable fingerprint. Prefer external_id (arxiv ID) when present;
        fall back to title+first-author+year."""
        ext = (paper.get("external_id") or "").strip()
        if ext:
            return f"id|{ext}"
        title = (paper.get("title") or "").lower().strip()
        title = re.sub(r"[^a-z0-9 ]", "", title)[:80]
        authors = paper.get("authors") or []
        first = (authors[0].lower().split()[-1] if authors else "")
        date = paper.get("pub_date") or paper.get("date") or ""
        year = date[:4] if len(date) >= 4 else ""
        return f"tay|{title}|{first}|{year}"

    def is_known(self, paper: dict) -> bool:
        return self.fingerprint(paper) in self.index

    def add(self, paper: dict) -> None:
        fp = self.fingerprint(paper)
        now = datetime.now(timezone.utc).isoformat()
        if fp in self.index:
            entry = self.index[fp]
            entry["last_seen"] = now
            entry["seen_count"] = entry.get("seen_count", 1) + 1
        else:
            self.index[fp] = {
                "title": paper.get("title", ""),
                "external_id": paper.get("external_id", ""),
                "first_seen": now,
                "last_seen": now,
                "seen_count": 1,
            }


# ---------------------------------------------------------------------------
# arXiv scanner
# ---------------------------------------------------------------------------

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"}


def _build_arxiv_url(query: str, max_results: int = 20) -> str:
    """Compose arxiv search URL. Pure function for testability."""
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": int(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    return f"{ARXIV_API}?{params}"


def _fetch_arxiv(url: str, timeout: int = 30) -> bytes:
    """HTTP GET. Default fetcher; tests inject a fake."""
    import ssl
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Clio/0.1 (Prometheus Project)"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def _parse_arxiv_atom(xml_bytes: bytes) -> list[dict]:
    """Parse arxiv Atom feed → list of paper dicts. Pure function (no I/O)."""
    out: list[dict] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        log.error(f"arxiv XML parse error: {e}")
        return out
    for entry in root.findall("atom:entry", ARXIV_NS):
        full_id = (entry.findtext("atom:id", default="", namespaces=ARXIV_NS) or "").strip()
        # arxiv id format: http://arxiv.org/abs/2605.00001v1
        ext = full_id.rsplit("/", 1)[-1] if full_id else ""
        title = (entry.findtext("atom:title", default="", namespaces=ARXIV_NS) or "").strip().replace("\n", " ")
        title = re.sub(r"\s+", " ", title)
        summary = (entry.findtext("atom:summary", default="", namespaces=ARXIV_NS) or "").strip()
        summary = re.sub(r"\s+", " ", summary)
        published = (entry.findtext("atom:published", default="", namespaces=ARXIV_NS) or "")[:10]
        authors = []
        for author in entry.findall("atom:author", ARXIV_NS):
            name = author.findtext("atom:name", default="", namespaces=ARXIV_NS)
            if name:
                authors.append(name.strip())
        categories = []
        for cat in entry.findall("atom:category", ARXIV_NS):
            term = cat.get("term")
            if term:
                categories.append(term)
        out.append({
            "source": "arxiv",
            "external_id": ext,
            "title": title,
            "abstract": summary,
            "url": full_id,
            "authors": authors[:10],
            "arxiv_categories": categories,
            "pub_date": published,
        })
    return out


def scan_arxiv_query(query: str, max_results: int, fetcher: Callable[[str], bytes] = None,
                    timeout: int = 30) -> list[dict]:
    """One arxiv query → list of papers. Injectable fetcher for tests."""
    fetcher = fetcher or (lambda u: _fetch_arxiv(u, timeout=timeout))
    url = _build_arxiv_url(query, max_results=max_results)
    try:
        data = fetcher(url)
    except Exception as e:
        log.error(f"arxiv fetch failed for query={query!r}: {e}")
        return []
    return _parse_arxiv_atom(data)


# ---------------------------------------------------------------------------
# Persister — Postgres dual-write
# ---------------------------------------------------------------------------

def default_persister(paper: dict, query_matched: str, cycle_id: str) -> bool:
    """Write one paper to agora.clio_papers. Best-effort."""
    if not HAS_PG:
        return False
    return agora_persist.write_clio_paper(
        source=paper.get("source", "arxiv"),
        external_id=paper.get("external_id") or None,
        title=paper.get("title") or "",
        abstract=paper.get("abstract") or None,
        url=paper.get("url") or None,
        authors=paper.get("authors") or [],
        query_matched=query_matched,
        arxiv_categories=paper.get("arxiv_categories") or [],
        pub_date=paper.get("pub_date") or None,
        cycle_id=cycle_id,
        raw_json=paper,
    )


def emit_heartbeat(config: dict, status_json: dict) -> None:
    """Heartbeat to agora.agent_heartbeats. Best-effort."""
    if not HAS_PG:
        return
    agora_persist.write_heartbeat(
        agent_name=config.get("agent_name", "Clio"),
        machine=config.get("machine", "M1"),
        status="online",
        status_json=status_json,
        pid=os.getpid(),
    )


# ---------------------------------------------------------------------------
# Main cycle
# ---------------------------------------------------------------------------

def run_cycle(
    config: dict,
    paper_index: Optional[PaperIndex] = None,
    fetcher: Optional[Callable[[str], bytes]] = None,
    persister: Optional[Callable[[dict, str, str], bool]] = None,
) -> dict:
    """One full mining cycle. Returns stats dict.

    Injectable paper_index/fetcher/persister for tests.
    """
    cycle_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    queries = config.get("arxiv_queries", [])
    min_interval = float(config.get("arxiv_min_interval_sec", 3.5))
    timeout = int(config.get("http_timeout_sec", 30))

    if paper_index is None:
        idx_path = REPO_ROOT / config.get("paper_index_path", "data/clio/paper_index.json")
        paper_index = PaperIndex(idx_path)
    persister = persister or default_persister

    total_found = 0
    total_new = 0
    per_query_stats = []

    for i, qcfg in enumerate(queries):
        query = qcfg["query"]
        max_n = int(qcfg.get("max_results", 20))
        if i > 0:
            time.sleep(min_interval)  # polite arxiv pacing
        log.info(f"Query {i+1}/{len(queries)}: {query[:80]}")
        papers = scan_arxiv_query(query, max_n, fetcher=fetcher, timeout=timeout)
        total_found += len(papers)
        new_this_query = 0
        for p in papers:
            if paper_index.is_known(p):
                continue
            ok = persister(p, query, cycle_id)
            paper_index.add(p)
            if ok:
                total_new += 1
                new_this_query += 1
        per_query_stats.append({
            "query": query,
            "found": len(papers),
            "new": new_this_query,
        })
        log.info(f"  -> found={len(papers)}, new={new_this_query}")

    paper_index.save()

    finished = datetime.now(timezone.utc)
    duration_sec = (finished - started).total_seconds()
    stats = {
        "cycle_id": cycle_id,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_sec": round(duration_sec, 2),
        "queries_run": len(queries),
        "papers_found": total_found,
        "papers_new": total_new,
        "per_query": per_query_stats,
    }

    # Quality snapshot (best-effort; never blocks the cycle on PG/quality failures).
    # Computes a 24h window over agora.clio_papers + agora.clio_claim_extractions,
    # persists to agora.clio_quality_snapshots, and merges headline numbers into
    # the heartbeat status_json so the dashboard + Metis brief surface them.
    quality_headline = None
    if HAS_QUALITY and HAS_PG:
        try:
            snap = clio_quality.compute_quality_snapshot(window_hours=24)
            sid = agora_persist.write_clio_quality_snapshot(24, snap)
            quality_headline = {
                k: snap.get(k) for k in (
                    "papers_24h", "claims_extracted_24h", "claims_submitted_24h",
                    "claims_per_paper_mean", "paradigm_coverage_count",
                    "paradigm_hint_pct", "falsifiable_pct",
                    "confidence_mean", "confidence_p50",
                    "sigma_submission_error_pct",
                    "theorem_with_counterexample_kill_path_pct",
                )
            }
            quality_headline["snapshot_id"] = sid
            log.info(f"quality snapshot id={sid}: "
                     f"papers={snap.get('papers_24h')}, "
                     f"claims={snap.get('claims_extracted_24h')}, "
                     f"paradigms={snap.get('paradigm_coverage_count')}, "
                     f"conf_p50={snap.get('confidence_p50')}")
        except Exception as e:
            log.warning(f"quality snapshot failed (non-fatal): {e}")

    # Heartbeat: short status_json (full per_query stays in memory/log).
    # Quality headline merges into status_json under a 'quality' key.
    hb_status = {
        "cycle_id": cycle_id,
        "queries_run": len(queries),
        "papers_found": total_found,
        "papers_new": total_new,
        "duration_sec": stats["duration_sec"],
        "last_cycle_at": finished.isoformat(),
    }
    if quality_headline:
        hb_status["quality"] = quality_headline
    emit_heartbeat(config, hb_status)

    log.info(f"Cycle complete: found={total_found}, new={total_new}, dur={stats['duration_sec']}s, id={cycle_id[:8]}")
    return stats


def main():
    parser = argparse.ArgumentParser(description="Clio — substrate paper-mining daemon")
    parser.add_argument("--once", action="store_true", help="Single cycle, then exit")
    parser.add_argument("--interval", type=int, default=None, help="Override cycle interval (seconds)")
    parser.add_argument("--config", type=str, default=None, help="Path to clio_config.yaml")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_PATH
    config = load_config(config_path)
    interval = args.interval or int(config.get("scan_interval_sec", 3600))

    sep = "=" * 60
    print(f"{sep}\n  CLIO — substrate paper-mining daemon (v0.1)\n  Muse of history. Mining the written record.\n{sep}")
    print(f"  Config:    {config_path}")
    print(f"  Queries:   {len(config.get('arxiv_queries', []))}")
    print(f"  Postgres:  {'on' if HAS_PG else 'OFF (agora_persist unavailable)'}")
    print(f"  Mode:      {'single' if args.once else f'loop @ {interval}s'}")
    print(sep)

    if args.once:
        stats = run_cycle(config)
        print(json.dumps({k: v for k, v in stats.items() if k != "per_query"}, indent=2))
        return 0

    while True:
        try:
            run_cycle(config)
        except Exception as e:
            log.exception(f"cycle error: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main() or 0)
