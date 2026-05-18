"""
eos_substrate_helpers.py — pure helpers for redirecting Eos at substrate-relevant queries.

Lives in scripts/ (tracked) so it propagates across machines via git pull.
agents/eos/ is gitignored on the public repo, so daemon-internal logic must
either live in agents/eos/ (machine-local, manually synced) or import from here.

This module is the latter: pure helpers that the eos_daemon imports and calls.
No Eos-internal state, no agents-only deps. Safe to import from anywhere.

Helpers:
- scan_idx()                       — stateless rotation index, advances every hour
- select_keywords()                — top-N priority slots + (N_per_scan - N) rotating
- select_keyword_single()          — single-keyword scanners rotate keyword[0..N]
- build_arxiv_category_filter()    — composes the cat:X OR cat:Y clause
- persist_finding_to_postgres()    — wraps agora_persist.write_eos_finding with
                                     per-source external_id normalization

Integration into eos_daemon.py: see pivot/m4_eos_integration_patch_2026-05-18.md
"""
import sys
import time
from pathlib import Path

# Ensure scripts/ is importable for sibling agora_persist (defensive).
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    import agora_persist
    HAS_AGORA_PERSIST = True
except Exception:
    HAS_AGORA_PERSIST = False


def scan_idx() -> int:
    """Stateless rotation index. Advances every hour. Used to rotate through keyword pool.

    Hour-of-epoch — daemon survives restarts without losing rotation position.
    """
    return int(time.time() // 3600)


def select_keywords(keywords: list, n_top: int, n_per_scan: int, idx: int) -> list:
    """Return keywords for this scan: top n_top always-fire + (n_per_scan - n_top) rotating.

    n_top      = priority slots that always fire (substrate-priority keywords)
    n_per_scan = total keywords this scan
    idx        = monotonically incrementing counter (e.g. scan_idx())

    Example: keywords=[A,B,C,D,E,F,G,H], n_top=3, n_per_scan=5
        idx=0 → [A,B,C, D,E]
        idx=1 → [A,B,C, F,G]
        idx=2 → [A,B,C, H,D]
    """
    if not keywords:
        return []
    n_top = min(n_top, len(keywords))
    top = keywords[:n_top]
    if len(keywords) <= n_top or n_per_scan <= n_top:
        return top[:n_per_scan]
    pool = keywords[n_top:]
    n_rotating = n_per_scan - n_top
    selected_pool = [pool[(idx * n_rotating + i) % len(pool)] for i in range(n_rotating)]
    return top + selected_pool


def select_keyword_single(keywords: list, idx: int) -> str:
    """Pick ONE keyword for single-keyword scanners (github, openalex, semantic_scholar).

    Cycles through the entire list one per scan. idx 0 → keyword[0], idx 1 → keyword[1], wraps.
    Default behavior: full rotation through every keyword over time.
    """
    if not keywords:
        return ""
    return keywords[idx % len(keywords)]


def build_arxiv_category_filter(categories: list, max_n: int = 8) -> str:
    """Build arxiv API category filter clause. Returns empty if no categories.

    Arxiv supports `cat:math.NT OR cat:math.AG` syntax. Combine with keyword
    clauses via AND to restrict results to math papers matching substrate keywords.
    """
    if not categories:
        return ""
    cats = categories[:max_n]
    return " OR ".join(f"cat:{c}" for c in cats)


def persist_finding_to_postgres(
    item: dict,
    item_type: str,
    keywords_matched: list,
    categories: list,
    relevance_score: int = None,
    relevance_reason: str = None,
    scan_cycle_id: str = None,
) -> bool:
    """Best-effort Postgres dual-write of one Eos finding.

    Returns True if write succeeded, False otherwise. Never raises.
    Eos runs on M4; this writes to the central agora.eos_findings table
    so M1 substrate consumers can query it.

    item:       the scanner's result dict ({source, title, url, summary, ...})
    item_type:  'paper' | 'repo' | 'news'
    """
    if not HAS_AGORA_PERSIST:
        return False
    try:
        source = item.get("source") or "unknown"
        url = item.get("url", "")
        external_id = None
        if source == "arxiv" and url:
            external_id = url.rsplit("/", 1)[-1] if url else None
        elif source == "github":
            external_id = item.get("name") or url.replace("https://github.com/", "")
        elif source in ("openalex", "semantic_scholar", "tavily"):
            external_id = url or None

        title = item.get("title") or item.get("name", "")
        summary = item.get("summary") or item.get("description") or ""
        authors = item.get("authors") or []
        if isinstance(authors, str):
            authors = [authors]
        cited_by = item.get("cited_by") or item.get("stars") or None
        pub_date = item.get("date") or item.get("updated") or None
        if pub_date and isinstance(pub_date, str) and len(pub_date) > 10:
            pub_date = pub_date[:10]

        return agora_persist.write_eos_finding(
            source=source,
            item_type=item_type,
            external_id=external_id,
            title=title,
            summary=summary,
            url=url,
            authors=authors,
            keywords_matched=keywords_matched or [],
            categories=categories or [],
            relevance_score=relevance_score,
            relevance_reason=relevance_reason,
            cited_by=int(cited_by) if cited_by is not None else None,
            pub_date=pub_date,
            raw_json=item,
            scan_cycle_id=scan_cycle_id,
        )
    except Exception as e:
        print(f"[eos_substrate_helpers] persist_finding failed: {e}", file=sys.stderr)
        return False
