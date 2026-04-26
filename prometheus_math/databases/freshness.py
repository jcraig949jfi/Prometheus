"""Database freshness automation for prometheus_math.databases.

A single source-of-truth module that probes the upstream and the local
mirror for every database wrapper Prometheus relies on, decides whether
the local copy is stale, optionally refreshes it, and emits a freshness
report suitable for a CI job summary.

Design
------
Each database wrapper (oeis, lmfdb, arxiv, knotinfo, zbmath, mahler,
atlas, cremona, arxiv_corpus) is registered as a :class:`DataSource`
with:

  * ``name``                 — short identifier ('oeis', 'lmfdb', ...).
  * ``kind``                 — 'bulk' (downloadable dump),
                               'api'  (live HTTP/SQL endpoint), or
                               'embedded' (snapshot shipped in-tree).
  * ``upstream_url``         — best HEAD-able URL for liveness probing.
                               Empty string means no live probe is
                               possible (purely embedded data).
  * ``local_cache_path``     — Callable[[], pathlib.Path] resolving to
                               the on-disk artifact (or directory) that
                               we treat as the local cache.  Resolved
                               lazily so PROMETHEUS_DATA_DIR can be
                               overridden in tests.
  * ``max_staleness_days``   — float; staleness threshold.  ``inf``
                               for embedded snapshots (never auto-stale).
  * ``fetch_callable``       — Callable[[], Any] | None invoked by
                               ``refresh_if_stale`` to refresh the local
                               cache.  ``None`` for sources with no
                               programmatic refresh path (typically
                               purely live APIs).

The module never calls upstream during import — every probe is lazy.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import logging
import math
import os
import pathlib
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Optional

from . import _local

_log = logging.getLogger(__name__)

_USER_AGENT = "prometheus-math-freshness/0.1"
_HEAD_TIMEOUT = 10.0  # seconds

# ---------------------------------------------------------------------------
# DataSource
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DataSource:
    """Specification for one upstream + local-cache pair."""

    name: str
    kind: str  # 'bulk' | 'api' | 'embedded'
    upstream_url: str
    local_cache_path: Callable[[], pathlib.Path]
    max_staleness_days: float
    fetch_callable: Optional[Callable[..., Any]] = None
    notes: str = ""

    def cache_path(self) -> pathlib.Path:
        """Resolve the local cache artifact path lazily."""
        return self.local_cache_path()


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def _oeis_cache_path() -> pathlib.Path:
    return _local.dataset_path("oeis") / "stripped.gz"


def _arxiv_corpus_cache_path() -> pathlib.Path:
    return _local.dataset_path("arxiv_corpus")


def _knotinfo_cache_path() -> pathlib.Path:
    return _local.dataset_path("knotinfo")


def _cremona_cache_path() -> pathlib.Path:
    return _local.dataset_path("cremona")


def _mahler_cache_path() -> pathlib.Path:
    # Mahler is embedded — point at the data module file as the
    # cache-age proxy (refresh = re-bundling the snapshot).
    return pathlib.Path(__file__).with_name("_mahler_data.py")


def _atlas_cache_path() -> pathlib.Path:
    return pathlib.Path(__file__).with_name("_atlas_data.py")


def _lmfdb_cache_path() -> pathlib.Path:
    # LMFDB is queried live; we synthesize a "last successful probe"
    # marker file under the data dir so freshness tracking still works.
    return _local.dataset_path("lmfdb") / ".last_probe"


def _zbmath_cache_path() -> pathlib.Path:
    return _local.dataset_path("zbmath") / ".last_probe"


def _arxiv_cache_path() -> pathlib.Path:
    return _local.dataset_path("arxiv") / ".last_probe"


def _oeis_refresh() -> dict:
    """Refresh OEIS bulk dumps via the wrapper's update_mirror()."""
    from . import oeis as _oeis  # local import avoids hard dep at import time
    return _oeis.update_mirror(force=True)


def _mahler_refresh() -> dict:
    from . import mahler as _mahler
    return _mahler.update_mirror()


def _touch_probe_marker(path: pathlib.Path) -> dict:
    """Write a tiny marker file recording 'last probe' wallclock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    path.write_text(now + "\n", encoding="utf-8")
    return {"refreshed": True, "marker": str(path), "at": now}


def _lmfdb_refresh() -> dict:
    """For the live Postgres mirror, 'refresh' means probe-and-record."""
    return _touch_probe_marker(_lmfdb_cache_path())


def _zbmath_refresh() -> dict:
    return _touch_probe_marker(_zbmath_cache_path())


def _arxiv_refresh() -> dict:
    return _touch_probe_marker(_arxiv_cache_path())


# ---------------------------------------------------------------------------
# SOURCE_REGISTRY
# ---------------------------------------------------------------------------

#: Default source registry.  Callers (CI, CLI, tests) can substitute
#: their own list via the ``sources=`` argument on the public functions.
SOURCE_REGISTRY: list[DataSource] = [
    DataSource(
        name="oeis",
        kind="bulk",
        upstream_url="https://oeis.org/stripped.gz",
        local_cache_path=_oeis_cache_path,
        max_staleness_days=7.0,
        fetch_callable=_oeis_refresh,
        notes="Bulk dump; weekly refresh.",
    ),
    DataSource(
        name="lmfdb",
        kind="api",
        upstream_url="https://www.lmfdb.org/",
        local_cache_path=_lmfdb_cache_path,
        max_staleness_days=30.0,
        fetch_callable=_lmfdb_refresh,
        notes="Postgres mirror at devmirror.lmfdb.xyz; "
              "freshness probed via the public site.",
    ),
    DataSource(
        name="arxiv",
        kind="api",
        upstream_url="https://export.arxiv.org/api/query?search_query=all:elliptic&max_results=1",
        local_cache_path=_arxiv_cache_path,
        max_staleness_days=14.0,
        fetch_callable=_arxiv_refresh,
        notes="Live API; freshness probed via 1-result query.",
    ),
    DataSource(
        name="knotinfo",
        kind="bulk",
        upstream_url="https://knotinfo.math.indiana.edu/homelinks/knotinfo_data_complete.csv",
        local_cache_path=_knotinfo_cache_path,
        max_staleness_days=180.0,
        fetch_callable=None,  # PyPI package preferred; no in-place refresher
        notes="CSV mirror; package database_knotinfo bundles the data.",
    ),
    DataSource(
        name="zbmath",
        kind="api",
        upstream_url="https://api.zbmath.org/v1/",
        local_cache_path=_zbmath_cache_path,
        max_staleness_days=30.0,
        fetch_callable=_zbmath_refresh,
        notes="zbMATH Open API.",
    ),
    DataSource(
        name="mahler",
        kind="embedded",
        upstream_url="https://wayback.cecm.sfu.ca/~mjm/Lehmer/",
        local_cache_path=_mahler_cache_path,
        max_staleness_days=365.0,
        fetch_callable=_mahler_refresh,
        notes="Embedded Mossinghoff snapshot; static, refresh checks "
              "upstream reachability only.",
    ),
    DataSource(
        name="atlas",
        kind="embedded",
        upstream_url="https://brauer.maths.qmul.ac.uk/Atlas/v3/",
        local_cache_path=_atlas_cache_path,
        max_staleness_days=math.inf,
        fetch_callable=None,
        notes="Embedded ATLAS-of-Finite-Groups snapshot; never auto-stale.",
    ),
    DataSource(
        name="cremona",
        kind="bulk",
        upstream_url="https://raw.githubusercontent.com/JohnCremona/ecdata/master/README.md",
        local_cache_path=_cremona_cache_path,
        max_staleness_days=90.0,
        fetch_callable=None,
        notes="GitHub-hosted ecdata; refresh via cremona.update_mirror().",
    ),
    DataSource(
        name="arxiv_corpus",
        kind="bulk",
        upstream_url="https://export.arxiv.org/api/query?search_query=cat:math.NT&max_results=1",
        local_cache_path=_arxiv_corpus_cache_path,
        max_staleness_days=30.0,
        fetch_callable=None,
        notes="Curated FV/NT subset; refresh via arxiv_corpus.refresh().",
    ),
]


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def probe_upstream(source: DataSource, timeout: float = _HEAD_TIMEOUT) -> dict:
    """HEAD-probe the upstream URL.  Returns a result dict.

    Keys (always present):
        last_modified : datetime | None    (Last-Modified header parsed)
        etag          : str | None         (ETag header)
        size          : int | None         (Content-Length, if any)
        status        : int | None         (HTTP status; -1 for non-HTTP)
        error         : str | None         (None on success)
    """
    out: dict[str, Any] = {
        "last_modified": None, "etag": None, "size": None,
        "status": None, "error": None,
    }
    if not source.upstream_url:
        out["error"] = "no upstream_url configured"
        return out

    req = urllib.request.Request(
        source.upstream_url,
        method="HEAD",
        headers={"User-Agent": _USER_AGENT, "Accept": "*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out["status"] = getattr(r, "status", None) or r.getcode()
            lm = r.headers.get("Last-Modified")
            if lm:
                try:
                    out["last_modified"] = parsedate_to_datetime(lm)
                except (TypeError, ValueError):
                    out["last_modified"] = None
            et = r.headers.get("ETag")
            if et:
                out["etag"] = et.strip('"')
            cl = r.headers.get("Content-Length")
            if cl is not None:
                try:
                    out["size"] = int(cl)
                except ValueError:
                    out["size"] = None
    except urllib.error.HTTPError as e:
        # Some hosts reject HEAD; retry once with GET (no body read).
        if e.code in (400, 403, 405, 501):
            return _probe_upstream_get(source, timeout)
        out["status"] = e.code
        out["error"] = f"HTTPError {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        out["error"] = f"{type(e).__name__}: {e}"
    except Exception as e:  # pragma: no cover — defensive
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _probe_upstream_get(source: DataSource, timeout: float) -> dict:
    """Fallback for hosts that reject HEAD; issues GET and reads 0 bytes."""
    out: dict[str, Any] = {
        "last_modified": None, "etag": None, "size": None,
        "status": None, "error": None,
    }
    req = urllib.request.Request(
        source.upstream_url,
        headers={"User-Agent": _USER_AGENT, "Accept": "*/*", "Range": "bytes=0-0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out["status"] = getattr(r, "status", None) or r.getcode()
            lm = r.headers.get("Last-Modified")
            if lm:
                try:
                    out["last_modified"] = parsedate_to_datetime(lm)
                except (TypeError, ValueError):
                    out["last_modified"] = None
            et = r.headers.get("ETag")
            if et:
                out["etag"] = et.strip('"')
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, OSError) as e:
        out["error"] = f"{type(e).__name__}: {e}"
    except Exception as e:  # pragma: no cover
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def probe_local(source: DataSource) -> dict:
    """Inspect the local cache.

    Returns:
        {exists: bool, last_refresh: datetime|None, size: int|None,
         path: str}
    """
    path = source.cache_path()
    out: dict[str, Any] = {
        "exists": False, "last_refresh": None,
        "size": None, "path": str(path),
    }
    try:
        if not path.exists():
            return out
        out["exists"] = True
        if path.is_file():
            st = path.stat()
            out["size"] = int(st.st_size)
            out["last_refresh"] = _dt.datetime.fromtimestamp(
                st.st_mtime, tz=_dt.timezone.utc,
            )
        elif path.is_dir():
            # Directory: take the newest file's mtime + sum sizes.
            newest = 0.0
            total = 0
            for root, _dirs, files in os.walk(path):
                for f in files:
                    p = pathlib.Path(root) / f
                    try:
                        s = p.stat()
                    except OSError:
                        continue
                    total += int(s.st_size)
                    if s.st_mtime > newest:
                        newest = s.st_mtime
            out["size"] = total
            if newest > 0:
                out["last_refresh"] = _dt.datetime.fromtimestamp(
                    newest, tz=_dt.timezone.utc,
                )
    except OSError as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out


# ---------------------------------------------------------------------------
# Staleness + refresh
# ---------------------------------------------------------------------------


def _age_days(then: Optional[_dt.datetime],
              now: Optional[_dt.datetime] = None) -> float:
    """Wallclock age in days, or +inf if `then` is missing."""
    if then is None:
        return math.inf
    if now is None:
        now = _dt.datetime.now(_dt.timezone.utc)
    if then.tzinfo is None:
        then = then.replace(tzinfo=_dt.timezone.utc)
    return max(0.0, (now - then).total_seconds() / 86400.0)


def is_stale(source: DataSource,
             now: Optional[_dt.datetime] = None,
             upstream: Optional[dict] = None) -> bool:
    """True iff the local cache is older than the source's threshold,
    or its etag has drifted from the upstream's, or it doesn't exist.

    Always returns a *bool* (never None / str / Exception)."""
    if math.isinf(source.max_staleness_days) and source.kind == "embedded":
        # Embedded sources never auto-stale.
        return False
    local = probe_local(source)
    if not local["exists"]:
        return True
    age = _age_days(local["last_refresh"], now=now)
    if age > source.max_staleness_days:
        return True
    if upstream and upstream.get("etag"):
        marker = source.cache_path().with_suffix(
            source.cache_path().suffix + ".etag"
        )
        try:
            local_etag = marker.read_text(encoding="utf-8").strip()
        except OSError:
            local_etag = ""
        if local_etag and local_etag != upstream["etag"]:
            return True
    return False


def refresh_if_stale(source: DataSource,
                     dry_run: bool = False,
                     now: Optional[_dt.datetime] = None) -> dict:
    """Refresh the local cache if stale.

    Returns:
        {refreshed: bool, before_age_days: float, after_age_days: float,
         error: str|None, dry_run: bool}
    """
    before = probe_local(source)
    before_age = _age_days(before["last_refresh"], now=now)
    out: dict[str, Any] = {
        "name": source.name,
        "refreshed": False,
        "before_age_days": before_age,
        "after_age_days": before_age,
        "error": None,
        "dry_run": bool(dry_run),
    }
    if not is_stale(source, now=now):
        return out
    if dry_run:
        out["error"] = "dry_run: would refresh"
        return out
    if source.fetch_callable is None:
        out["error"] = "no fetch_callable registered"
        return out
    try:
        source.fetch_callable()
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    after = probe_local(source)
    out["refreshed"] = True
    out["after_age_days"] = _age_days(after["last_refresh"], now=now)
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _row(source: DataSource,
         upstream: dict,
         local: dict,
         now: _dt.datetime) -> dict:
    age = _age_days(local["last_refresh"], now=now)
    return {
        "name": source.name,
        "kind": source.kind,
        "upstream_url": source.upstream_url,
        "upstream_status": upstream.get("status"),
        "upstream_error": upstream.get("error"),
        "upstream_last_modified": (
            upstream["last_modified"].isoformat()
            if upstream.get("last_modified") else None
        ),
        "local_path": local.get("path"),
        "local_exists": local.get("exists"),
        "local_size": local.get("size"),
        "local_age_days": (None if math.isinf(age) else round(age, 2)),
        "max_staleness_days": (
            None if math.isinf(source.max_staleness_days)
            else source.max_staleness_days
        ),
        "stale": is_stale(source, now=now, upstream=upstream),
    }


def freshness_report(sources: Optional[list[DataSource]] = None,
                     format: str = "dict",
                     probe_timeout: float = _HEAD_TIMEOUT) -> Any:
    """Probe every source and emit a structured report.

    format='dict'      -> {generated_at: iso, rows: [row, ...], summary: {...}}
    format='markdown'  -> str (Markdown table for CI summary)

    Network failures on any single upstream become row-level errors,
    not exceptions.
    """
    srcs = list(sources) if sources is not None else list(SOURCE_REGISTRY)
    now = _dt.datetime.now(_dt.timezone.utc)
    rows: list[dict] = []
    for s in srcs:
        try:
            up = probe_upstream(s, timeout=probe_timeout)
        except Exception as e:  # pragma: no cover — defensive
            up = {"last_modified": None, "etag": None, "size": None,
                  "status": None, "error": f"{type(e).__name__}: {e}"}
        try:
            loc = probe_local(s)
        except Exception as e:  # pragma: no cover
            loc = {"exists": False, "last_refresh": None,
                   "size": None, "path": str(s.cache_path()),
                   "error": f"{type(e).__name__}: {e}"}
        rows.append(_row(s, up, loc, now))

    n_stale = sum(1 for r in rows if r["stale"])
    n_unreachable = sum(1 for r in rows if r["upstream_error"])
    summary = {
        "n_sources": len(rows),
        "n_stale": n_stale,
        "n_unreachable": n_unreachable,
        "healthy": (n_stale == 0),
    }
    payload = {
        "generated_at": now.isoformat(),
        "rows": rows,
        "summary": summary,
    }
    if format == "dict":
        return payload
    if format == "markdown":
        return _to_markdown(payload)
    raise ValueError(f"unknown format: {format!r}")


def _to_markdown(payload: dict) -> str:
    lines: list[str] = []
    s = payload["summary"]
    lines.append("## Database freshness report")
    lines.append("")
    lines.append(f"_Generated: {payload['generated_at']}_")
    lines.append("")
    lines.append(
        f"- Sources: **{s['n_sources']}** | "
        f"Stale: **{s['n_stale']}** | "
        f"Unreachable upstreams: **{s['n_unreachable']}** | "
        f"Healthy: **{s['healthy']}**"
    )
    lines.append("")
    lines.append("| Source | Kind | Stale | Local age (days) | "
                 "Max stale | Upstream | Note |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in payload["rows"]:
        stale_marker = "YES" if r["stale"] else "no"
        age = r["local_age_days"]
        age_s = "-" if age is None else str(age)
        max_s = ("inf" if r["max_staleness_days"] is None
                 else str(r["max_staleness_days"]))
        up = (f"{r['upstream_status']}" if r["upstream_status"]
              else (r["upstream_error"] or "-"))
        note = (r["upstream_error"] or "ok") if r["upstream_error"] \
            else ("missing" if not r["local_exists"] else "ok")
        lines.append(
            f"| {r['name']} | {r['kind']} | {stale_marker} | "
            f"{age_s} | {max_s} | {up} | {note} |"
        )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cli(argv: Optional[list[str]] = None) -> int:
    """Argparse-driven CLI. Returns Unix-style exit code (0 = healthy)."""
    p = argparse.ArgumentParser(
        prog="python -m prometheus_math.databases.freshness",
        description="Probe and refresh prometheus_math.databases caches.",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument("--report-only", action="store_true",
                   help="Print the freshness report and exit.")
    g.add_argument("--dry-run", action="store_true",
                   help="Show what would be refreshed without doing it.")
    g.add_argument("--refresh-stale", action="store_true",
                   help="Actually refresh every stale source.")
    p.add_argument("--format", choices=("dict", "markdown"),
                   default="markdown",
                   help="Report format (default: markdown).")
    p.add_argument("--source", action="append", default=None,
                   help="Restrict to one source name (repeatable).")
    p.add_argument("--timeout", type=float, default=_HEAD_TIMEOUT,
                   help="Per-upstream HEAD timeout in seconds.")
    args = p.parse_args(argv)

    sources = list(SOURCE_REGISTRY)
    if args.source:
        wanted = set(args.source)
        sources = [s for s in sources if s.name in wanted]
        if not sources:
            print(f"error: no sources match {args.source}", file=sys.stderr)
            return 2

    if args.dry_run or args.refresh_stale:
        for s in sources:
            res = refresh_if_stale(s, dry_run=args.dry_run)
            line = (f"[{s.name}] refreshed={res['refreshed']} "
                    f"before={res['before_age_days']:.2f}d "
                    f"after={res['after_age_days']:.2f}d "
                    f"err={res['error']}")
            print(line)

    report = freshness_report(sources=sources, format=args.format,
                              probe_timeout=args.timeout)
    if args.format == "markdown":
        print(report)
        # Decide exit code from a fresh dict view of the same probe state.
        d = freshness_report(sources=sources, format="dict",
                             probe_timeout=args.timeout)
        n_stale = d["summary"]["n_stale"]
    else:
        # 'dict' format: print as JSON-ish for easy CI capture.
        import json
        print(json.dumps(report, default=str, indent=2))
        n_stale = report["summary"]["n_stale"]

    return 0 if n_stale == 0 else 1


__all__ = [
    "DataSource",
    "SOURCE_REGISTRY",
    "probe_upstream",
    "probe_local",
    "is_stale",
    "refresh_if_stale",
    "freshness_report",
    "cli",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
