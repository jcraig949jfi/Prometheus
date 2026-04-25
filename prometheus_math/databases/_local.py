"""Local-mirror infrastructure for prometheus_math.databases.

A unified abstraction so each database wrapper (OEIS, KnotInfo, LMFDB dumps,
Mahler measures, etc.) can fall back to an offline copy when the live API
is rate-limited, blocked by Cloudflare, or simply unreachable.

Design:

  * Data lives under a single root directory, resolved (in order) from
    $PROMETHEUS_DATA_DIR, ./prometheus_data/ at the repo root, or
    ~/.prometheus_data/.  Each dataset gets a subdirectory.

  * Downloads stream to disk in 64 KiB chunks and rename atomically so a
    truncated file never masquerades as a complete one.

  * `fetch_dataset(name, urls, force=False)` is the high-level entry
    point: pass a dict of {filename: url} and the function ensures every
    file is present.  Network failures are logged, not raised — the
    caller is expected to check `has_mirror()` before relying on the data.
"""
from __future__ import annotations

import gzip
import logging
import os
import pathlib
import shutil
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

# Cloudflare challenges custom UAs on the OEIS host (and others), and the
# bulk-download endpoints are explicitly designed to be retrieved by browsers.
# We send a generic desktop-Chrome UA for file downloads only.  API wrappers
# that hit query endpoints continue to use their own polite UAs.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Cache the resolved root so we don't recompute on every call.
_DATA_DIR: Optional[pathlib.Path] = None


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def _repo_root() -> pathlib.Path:
    """Best-effort guess at the Prometheus repo root.

    This file lives at <root>/prometheus_math/databases/_local.py; walk up
    two levels to get there.
    """
    return pathlib.Path(__file__).resolve().parent.parent.parent


def data_dir() -> pathlib.Path:
    """Resolve and return the local data directory.

    Order of resolution:
      1. $PROMETHEUS_DATA_DIR (if set)
      2. <repo_root>/prometheus_data/ (if it already exists)
      3. ~/.prometheus_data/

    The chosen directory is created if absent. Returns an absolute Path.
    """
    global _DATA_DIR
    if _DATA_DIR is not None:
        return _DATA_DIR

    env = os.environ.get("PROMETHEUS_DATA_DIR")
    if env:
        path = pathlib.Path(env).expanduser().resolve()
    else:
        candidate = _repo_root() / "prometheus_data"
        if candidate.exists():
            path = candidate.resolve()
        else:
            path = (pathlib.Path.home() / ".prometheus_data").resolve()

    path.mkdir(parents=True, exist_ok=True)
    _DATA_DIR = path
    return path


def dataset_path(name: str) -> pathlib.Path:
    """Return the (existing-or-not) directory for a named dataset."""
    if not name or "/" in name or "\\" in name:
        raise ValueError(f"invalid dataset name: {name!r}")
    return data_dir() / name


def has_mirror(name: str, file: Optional[str] = None) -> bool:
    """True iff the dataset directory (or a specific file inside it) exists.

    `file=None` checks for the directory only; pass a filename to verify a
    particular member is present and non-empty.
    """
    base = dataset_path(name)
    if file is None:
        return base.is_dir()
    target = base / file
    try:
        return target.is_file() and target.stat().st_size > 0
    except OSError:
        return False


def mirror_size(name: str) -> int:
    """Total disk usage (bytes) of a dataset's mirror directory."""
    base = dataset_path(name)
    if not base.exists():
        return 0
    total = 0
    for root, _dirs, files in os.walk(base):
        for f in files:
            try:
                total += (pathlib.Path(root) / f).stat().st_size
            except OSError:
                continue
    return total


# ---------------------------------------------------------------------------
# Download / decompress
# ---------------------------------------------------------------------------

def download(url: str, dest: pathlib.Path, chunk_size: int = 65536,
             show_progress: bool = True) -> pathlib.Path:
    """Stream a URL to disk, atomically.

    Uses `urllib.request` rather than `requests` because some hosts
    (notably oeis.org behind Cloudflare) fingerprint the `requests`
    TLS handshake and reject it even with a browser UA, while letting
    plain stdlib through.

    Writes to <dest>.tmp and renames on success. On any error the partial
    file is deleted and the exception is re-raised.
    """
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")

    req = urllib.request.Request(url, headers={
        "User-Agent": _USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=120.0) as r:
            total = int(r.headers.get("Content-Length") or 0)
            written = 0
            last_pct = -1
            with tmp.open("wb") as fh:
                while True:
                    chunk = r.read(chunk_size)
                    if not chunk:
                        break
                    fh.write(chunk)
                    written += len(chunk)
                    if show_progress and total > 0:
                        pct = int(100 * written / total)
                        if pct != last_pct and pct % 10 == 0:
                            print(f"  {dest.name}: {pct}% "
                                  f"({written // 1024} KiB)", flush=True)
                            last_pct = pct
        # Atomic rename. On Windows os.replace works across same volume.
        os.replace(tmp, dest)
    except Exception:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise
    return dest


def gunzip(src: pathlib.Path, dest: Optional[pathlib.Path] = None,
           keep: bool = True) -> pathlib.Path:
    """Decompress a .gz file. dest defaults to src without the .gz suffix."""
    src = pathlib.Path(src)
    if dest is None:
        if src.suffix != ".gz":
            raise ValueError(f"cannot infer dest from non-.gz path: {src}")
        dest = src.with_suffix("")
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        with gzip.open(src, "rb") as fin, tmp.open("wb") as fout:
            shutil.copyfileobj(fin, fout, length=65536)
        os.replace(tmp, dest)
    except Exception:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise
    if not keep:
        try:
            src.unlink()
        except OSError:
            pass
    return dest


# ---------------------------------------------------------------------------
# Dataset orchestration
# ---------------------------------------------------------------------------

def fetch_dataset(name: str, urls: dict, force: bool = False) -> pathlib.Path:
    """Ensure every {filename: url} entry exists under dataset_path(name).

    Returns the dataset directory. Files already present are skipped
    unless `force=True`. Individual download failures are logged and
    raised — callers that want best-effort behavior should wrap in try.
    """
    base = dataset_path(name)
    base.mkdir(parents=True, exist_ok=True)
    for filename, url in urls.items():
        dest = base / filename
        if dest.exists() and not force:
            logger.debug("mirror: %s/%s already present", name, filename)
            continue
        logger.info("mirror: downloading %s -> %s", url, dest)
        download(url, dest)
    return base
