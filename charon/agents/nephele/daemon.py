"""Nephele — Clio fallback substrate gatherer (Charon swarm v0.5).

Per James 2026-05-24 directive: "write your own Clio fallback generator
but slow roll it. Just a periodic gathering when Clio is not producing.
And only if Clio not active for 4 hours."

Activation gate (BOTH must hold):
  1. Clio's daemon log (logs/clio_daemon.log) hasn't been modified in
     CLIO_INACTIVITY_HOURS (default 4). Proxy for "Clio not active."
  2. Nephele's own last fetch was >= NEPHELE_THROTTLE_MINUTES ago.
     Slow-roll guard so even a dead-Clio scenario doesn't spam arxiv
     at Charon's 4-min rotation cadence.

If either condition fails, emit a cheap "skipped" artifact and exit.
If both hold, rotate through a curated list of arxiv RSS feeds (one
per fire), fetch + parse, emit one candidate-paper artifact per recent
entry.

The fetch surface area is intentionally tiny (one urllib call, one
XML parse, no Postgres, no LLM) so Nephele can't accidentally
duplicate Clio's pipeline or contaminate Clio's index. When Clio
recovers, Nephele goes back to no-op skip mode automatically.
"""
from __future__ import annotations

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


# Activation gates
CLIO_LOG_PATH = REPO_ROOT / "logs" / "clio_daemon.log"
CLIO_INACTIVITY_HOURS = 4
NEPHELE_THROTTLE_MINUTES = 30

# arxiv RSS feeds — rotated one per fire so each fetch covers different
# territory. Selected to span math + CS where Prometheus pulls substrate.
ARXIV_RSS_FEEDS: list[dict] = [
    {"category": "math.NT", "url": "https://arxiv.org/rss/math.NT",
     "rationale": "Number theory -- BSD, Lehmer, anti-anchor candidates"},
    {"category": "math.AG", "url": "https://arxiv.org/rss/math.AG",
     "rationale": "Algebraic geometry -- modularity, varieties, Bombieri-Lang"},
    {"category": "math.CT", "url": "https://arxiv.org/rss/math.CT",
     "rationale": "Category theory -- structural substrate primitives"},
    {"category": "math.CO", "url": "https://arxiv.org/rss/math.CO",
     "rationale": "Combinatorics -- Saxl-class, partition rank, tensor decompositions"},
    {"category": "cs.LG", "url": "https://arxiv.org/rss/cs.LG",
     "rationale": "Learning -- cross-pollination with Ergon's Learner target"},
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
FETCH_TIMEOUT_SEC = 30
MAX_ENTRIES_PER_FIRE = 8  # cap artifact spam even when fire actually runs


def _clio_age_hours() -> Optional[float]:
    """How many hours since Clio's daemon log was last modified.
    None if the log file doesn't exist (Clio never ran on this machine)."""
    try:
        if not CLIO_LOG_PATH.exists():
            return None
        mtime = datetime.fromtimestamp(
            CLIO_LOG_PATH.stat().st_mtime, tz=timezone.utc
        )
        return (datetime.now(timezone.utc) - mtime).total_seconds() / 3600.0
    except Exception:
        return None


def _fetch_arxiv_rss(url: str) -> tuple[Optional[bytes], Optional[str]]:
    """Fetch raw arxiv RSS XML. Returns (bytes, None) on success or
    (None, error_string) on failure. Single point of network I/O."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml"},
        )
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SEC) as resp:
            return resp.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTPError {e.code}: {e.reason}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _parse_arxiv_rss(xml_bytes: bytes) -> list[dict]:
    """Pure parse function: arxiv RSS XML -> list of entry dicts.
    Each dict: {arxiv_id, title, abstract, link, published}."""
    entries: list[dict] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return entries
    # arxiv RSS is RSS 2.0; entries are <item> under <channel>
    # Namespaces vary; iterate generously.
    for item in root.iter("item"):
        title_el = item.find("title")
        desc_el = item.find("description")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        title = (title_el.text or "").strip() if title_el is not None else ""
        desc = (desc_el.text or "").strip() if desc_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        pub = (pub_el.text or "").strip() if pub_el is not None else ""
        # arxiv_id from the link tail
        arxiv_id = link.rsplit("/", 1)[-1] if link else ""
        entries.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": desc[:1500],
            "link": link,
            "published": pub,
        })
    return entries


class NepheleAgent(CharonAgent):
    """Clio-fallback substrate gatherer. Mostly no-ops when Clio is
    alive; activates on Clio silence for >=4h with own 30-min throttle."""

    name = "Nephele"
    role = "clio-fallback substrate gatherer (slow-roll arxiv RSS)"

    # ---- backlog ----------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Backlog is always one item: 'check Clio + maybe fetch one feed.'
        The expensive path (network fetch + parse + emit) is gated inside
        run_tick by activation checks."""
        return [{"kind": "clio_fallback_check"}]

    # ---- activation gate -------------------------------------------------

    def _should_fire(self) -> tuple[bool, str]:
        """Return (should_fire, reason). When False, reason explains
        whether Clio is alive, the throttle is engaged, or both."""
        clio_age = _clio_age_hours()
        if clio_age is None:
            clio_status = "clio_log_missing"
        elif clio_age < CLIO_INACTIVITY_HOURS:
            return False, f"clio_active_{clio_age:.2f}h_ago"
        else:
            clio_status = f"clio_silent_{clio_age:.2f}h"

        last_fetch = self.load_state("last_fetch_at", None)
        if last_fetch:
            try:
                last_dt = datetime.fromisoformat(
                    str(last_fetch).replace("Z", "+00:00")
                )
                throttle_age_min = (
                    datetime.now(timezone.utc) - last_dt
                ).total_seconds() / 60
                if throttle_age_min < NEPHELE_THROTTLE_MINUTES:
                    return False, f"throttled_{throttle_age_min:.1f}min_ago_({clio_status})"
            except Exception:
                pass
        return True, clio_status

    # ---- rotation --------------------------------------------------------

    def _pick_next_feed(self) -> dict:
        """Round-robin through ARXIV_RSS_FEEDS by index in state."""
        idx = int(self.load_state("feed_rotation_idx", 0) or 0)
        feed = ARXIV_RSS_FEEDS[idx % len(ARXIV_RSS_FEEDS)]
        self.save_state("feed_rotation_idx", (idx + 1) % len(ARXIV_RSS_FEEDS))
        return feed

    # ---- artifact writers ------------------------------------------------

    def _emit_skipped(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"clio_active_skip_{utc}.md"
        body = (
            f"# Nephele skip — {reason}\n\n"
            f"- at: {datetime.now(timezone.utc).isoformat()}\n"
            f"- reason: `{reason}`\n\n"
            f"Nephele is the Clio fallback generator (per James 2026-05-24). "
            f"Activation requires Clio silent >= {CLIO_INACTIVITY_HOURS}h AND "
            f"Nephele's own throttle (>= {NEPHELE_THROTTLE_MINUTES}min since "
            f"last fetch). Skip is the correct behavior whenever either gate "
            f"fails -- it means primary substrate channels are working as "
            f"designed.\n"
        )
        return self.write_artifact(fname, body)

    def _emit_candidate_paper(self, feed: dict, entry: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_id = (entry.get("arxiv_id") or "noid").replace("/", "_")[:60]
        fname = f"candidate_paper_{feed['category']}_{safe_id}_{utc}.md"
        title = entry.get("title", "(no title)")
        abstract = entry.get("abstract", "(no abstract)")
        link = entry.get("link", "")
        published = entry.get("published", "")
        body = (
            f"# Candidate paper — {entry.get('arxiv_id', '?')}\n\n"
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}\n"
            f"- emitted_by: Nephele (charon/agents/nephele/daemon.py)\n"
            f"- arxiv_category: `{feed['category']}`\n"
            f"- feed_rationale: {feed['rationale']}\n"
            f"- arxiv_id: `{entry.get('arxiv_id', '')}`\n"
            f"- link: {link}\n"
            f"- published: {published}\n\n"
            f"## Title\n\n{title}\n\n"
            f"## Abstract\n\n{abstract}\n\n"
            f"---\n\n"
            f"*Nephele candidate -- Clio-fallback substrate. NOT yet "
            f"Sigma-submitted, NOT yet LLM-extracted for claims. If Clio "
            f"recovers, this candidate will be superseded by Clio's "
            f"first-class extraction; if Clio stays dead, Aporia or "
            f"another agent should pick this up for downstream processing.*\n"
        )
        return self.write_artifact(fname, body)

    # ---- run_tick --------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "fired": False,
            "skip_reason": None,
            "clio_age_hours": None,
            "feed_category": None,
            "entries_emitted": 0,
        }
        clio_age = _clio_age_hours()
        stats["clio_age_hours"] = round(clio_age, 2) if clio_age is not None else None

        should_fire, reason = self._should_fire()
        if not should_fire:
            stats["skip_reason"] = reason
            if not dry_run:
                try:
                    self._emit_skipped(reason)
                    stats["artifacts_written"] += 1
                except Exception as e:
                    self.log.warning(f"skip-artifact emit failed: {e}")
                    stats["errors"] += 1
            stats["items_processed"] += 1
            self.log_work(
                "nephele_tick_complete",
                summary=f"skip ({reason})",
                success=stats["errors"] == 0,
            )
            return stats

        # Fire path: pick a feed, fetch, parse, emit per entry
        feed = self._pick_next_feed()
        stats["feed_category"] = feed["category"]
        stats["fired"] = True

        if dry_run:
            stats["items_processed"] += 1
            return stats

        xml_bytes, err = _fetch_arxiv_rss(feed["url"])
        if err or not xml_bytes:
            stats["skip_reason"] = f"fetch_failed: {err or 'empty_body'}"
            stats["errors"] += 1
            try:
                self._emit_skipped(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception:
                pass
            return stats

        entries = _parse_arxiv_rss(xml_bytes)[:MAX_ENTRIES_PER_FIRE]
        for entry in entries:
            try:
                self._emit_candidate_paper(feed, entry)
                stats["artifacts_written"] += 1
                stats["entries_emitted"] += 1
            except Exception as e:
                self.log.warning(f"candidate emit failed: {e}")
                stats["errors"] += 1
        # Mark fetch time for the throttle
        self.save_state(
            "last_fetch_at", datetime.now(timezone.utc).isoformat()
        )
        stats["items_processed"] += 1
        self.log_work(
            "nephele_tick_complete",
            summary=(
                f"fired feed={feed['category']} "
                f"entries={stats['entries_emitted']} "
                f"clio_age_h={stats['clio_age_hours']}"
            ),
            success=stats["errors"] == 0,
        )
        return stats
