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
from datetime import datetime, timedelta, timezone
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

# session_telemetry — log_work + emit_discovery wrappers (Aletheia 2026-05-18 feedback)
try:
    import session_telemetry
    HAS_TELEMETRY = True
except Exception:
    HAS_TELEMETRY = False

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

def _derive_target_domains(queries: list) -> list:
    """Pull unique tag strings off the configured queries.

    config queries can carry an optional `tags` list (see clio_config.yaml);
    those are the substrate-priority domain labels we expose in status_json.
    """
    domains: list = []
    seen: set = set()
    for q in queries or []:
        for t in q.get("tags") or []:
            if t not in seen:
                seen.add(t)
                domains.append(t)
    return domains


def _high_relevance_threshold(paper: dict) -> bool:
    """Heuristic for the agora:discoveries stream emission (Aletheia feedback).

    A paper is 'high-relevance' for v0.4.5 if its title or abstract suggests
    falsification/withdrawal content (anti-anchor signal — the highest-value
    substrate type per project_falsification_routing_learner) OR mentions a
    Tier-1 substrate keyword cluster. Tuned conservatively so the stream
    doesn't drown the dashboard.
    """
    text = ((paper.get("title") or "") + " " + (paper.get("abstract") or "")).lower()
    falsification_signals = ("withdrawn", "counterexample to ", "erratum",
                              "disproved", "is false", "retracted")
    if any(s in text for s in falsification_signals):
        return True
    # Tier-1 substrate clusters (sourced from attack_angle_taxonomy P22/P27/P29/P31)
    tier1 = ("polynomial method", "border rank", "secant variety",
             "tensor decomposition", "modularity lifting")
    hits = sum(1 for s in tier1 if s in text)
    return hits >= 2


def run_cycle(
    config: dict,
    paper_index: Optional[PaperIndex] = None,
    fetcher: Optional[Callable[[str], bytes]] = None,
    persister: Optional[Callable[[dict, str, str], bool]] = None,
    triggered_by: str = "schedule",
) -> dict:
    """One full mining cycle. Returns stats dict.

    Injectable paper_index/fetcher/persister for tests. triggered_by labels
    the source of the cycle ("schedule", "aporia_request", "manual") so the
    brief can distinguish autonomous from operator-driven activity.
    """
    cycle_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    queries = config.get("arxiv_queries", [])
    min_interval = float(config.get("arxiv_min_interval_sec", 3.5))
    timeout = int(config.get("http_timeout_sec", 30))
    interval_sec = int(config.get("scan_interval_sec", 3600))

    if paper_index is None:
        idx_path = REPO_ROOT / config.get("paper_index_path", "data/clio/paper_index.json")
        paper_index = PaperIndex(idx_path)
    persister = persister or default_persister

    total_found = 0
    total_new = 0
    per_query_stats = []
    sources_scanned: set = set()
    errors_this_cycle: list = []
    discoveries_emitted = 0

    for i, qcfg in enumerate(queries):
        query = qcfg["query"]
        max_n = int(qcfg.get("max_results", 20))
        if i > 0:
            time.sleep(min_interval)  # polite arxiv pacing
        log.info(f"Query {i+1}/{len(queries)}: {query[:80]}")
        try:
            papers = scan_arxiv_query(query, max_n, fetcher=fetcher, timeout=timeout)
            sources_scanned.add("arxiv")
        except Exception as e:  # defensive: scan_arxiv_query already catches, but cover all
            errors_this_cycle.append({
                "endpoint": "arxiv",
                "query": query[:80],
                "error": f"{type(e).__name__}: {e}"[:300],
                "at": datetime.now(timezone.utc).isoformat(),
            })
            papers = []
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
                # Aletheia 2026-05-18: emit high-relevance finds to agora:discoveries
                if HAS_TELEMETRY and _high_relevance_threshold(p):
                    try:
                        eid = session_telemetry.emit_discovery(
                            sender=config.get("agent_name", "Clio"),
                            subject=f"High-relevance paper: {p.get('title','')[:140]}",
                            body=(p.get("abstract") or "")[:600],
                            machine=config.get("machine", "M1"),
                            type_="share",
                            confidence=0.8,
                            extras={
                                "external_id": p.get("external_id"),
                                "url": p.get("url"),
                                "query_matched": query,
                            },
                        )
                        if eid:
                            discoveries_emitted += 1
                    except Exception as e:
                        log.debug(f"emit_discovery failed (non-fatal): {e}")
        per_query_stats.append({
            "query": query,
            "found": len(papers),
            "new": new_this_query,
        })
        log.info(f"  -> found={len(papers)}, new={new_this_query}")

    paper_index.save()

    finished = datetime.now(timezone.utc)
    duration_sec = (finished - started).total_seconds()
    next_cycle_at = (finished + timedelta(seconds=interval_sec)).isoformat()
    stats = {
        "cycle_id": cycle_id,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_sec": round(duration_sec, 2),
        "queries_run": len(queries),
        "papers_found": total_found,
        "papers_new": total_new,
        "errors_this_cycle": errors_this_cycle,
        "discoveries_emitted": discoveries_emitted,
        "per_query": per_query_stats,
    }

    # Quality snapshot (best-effort; never blocks the cycle on PG/quality failures).
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

    # Lifetime counts (cumulative across all cycles since boot) — Aletheia field
    # `lifetime_papers_indexed`. Held in paper_index size since that index is
    # the authoritative dedup record across cycle restarts.
    lifetime_papers_indexed = len(paper_index.index)

    # Enriched heartbeat per Aletheia 2026-05-18 feedback.
    # New fields: operator, target_domains, sources, lifetime_papers_indexed,
    #             dedup_rate, errors_this_cycle, next_cycle_at, triggered_by.
    hb_status = {
        "cycle_id": cycle_id,
        "queries_run": len(queries),
        "papers_found": total_found,
        "papers_new": total_new,
        "duration_sec": stats["duration_sec"],
        "last_cycle_at": finished.isoformat(),
        # Aletheia enrichment:
        "operator": config.get("operator", "Aporia"),
        "kind": "tool",
        "target_domains": _derive_target_domains(queries),
        "sources": sorted(sources_scanned),
        "lifetime_papers_indexed": lifetime_papers_indexed,
        "dedup_rate": round(total_new / total_found, 4) if total_found else 0.0,
        "errors_this_cycle": errors_this_cycle,
        "next_cycle_at": next_cycle_at,
        "triggered_by": triggered_by,
        "discoveries_emitted": discoveries_emitted,
    }
    if quality_headline:
        hb_status["quality"] = quality_headline
    emit_heartbeat(config, hb_status)

    # Aletheia 2026-05-18: log_work per cycle into agora.intelligence_outputs.
    # Heartbeat says "alive"; log_work says "did this useful thing." The brief
    # walks log_work for a navigable timeline.
    if HAS_TELEMETRY:
        try:
            err_count = len(errors_this_cycle)
            session_telemetry.log_work(
                stage="paper_scan_cycle",
                agent=config.get("agent_name", "Clio"),
                summary=(
                    f"{len(queries)} queries, {total_found} papers retrieved, "
                    f"{total_new} new after dedup, {stats['duration_sec']:.0f}s duration. "
                    f"Sources: {','.join(sorted(sources_scanned)) or 'none'}. "
                    f"Errors: {err_count}. Discoveries emitted: {discoveries_emitted}. "
                    f"Triggered by: {triggered_by}."
                ),
                success=(err_count == 0),
                cycle_id=cycle_id,
                started_at=started,
                error=(json.dumps(errors_this_cycle, default=str) if errors_this_cycle else None),
            )
        except Exception as e:
            log.warning(f"log_work failed (non-fatal): {e}")

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
