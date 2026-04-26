"""Cremona elliptic-curve dataset — local CSV mirror.

John Cremona's `ecdata` repository at
https://github.com/JohnCremona/ecdata is the canonical source for
elliptic curves over Q with conductor up to ~500,000. LMFDB is built on
top of this data; for bulk scans the local files are 50-100x faster
than round-tripping through the LMFDB Postgres mirror because there is
no network and no SQL planner overhead.

This module provides an opt-in local-first lookup for elliptic curve
data. When a local mirror is present, queries are served from disk;
otherwise we transparently fall back to ``prometheus_math.databases.lmfdb``.

Data layout
-----------
The mirror lives at ``<PROMETHEUS_DATA_DIR>/cremona/`` (resolved via
``prometheus_math.databases._local.dataset_path``). Inside it we keep:

    cremona/
      allcurves/
          allcurves.00000-09999      # ID AI R T
          allcurves.10000-19999
          ...
      allbsd/
          allbsd.00000-09999         # ID AI R T CP OM L1 REG SHA
          ...
      alllabels/
          alllabels.00000-09999      # Cremona <-> LMFDB label translation
          ...
      .metadata.json                 # populated by update_mirror

Each line in ``allcurves`` is whitespace-separated:

    <conductor> <isog_class> <curve_idx> <ainvs> <rank> <torsion>

e.g. ``11 a 1 [0,-1,1,-10,-20] 0 5``. ``allbsd`` adds Tamagawa, real
period, leading L-coefficient, regulator, analytic Sha. The full
file-format specification is the one in
``JohnCremona/ecdata/docs/file-format.txt`` (mirrored upstream).

Cremona vs LMFDB labels
-----------------------
Cremona's labels (``11a1``, ``37a1``, ``50a3``) and the LMFDB labels
(``11.a1``, ``37.a1``, ``50.a3``) sometimes differ in the isogeny-class
letter and curve index — they use different orderings for class > 1.
This module always returns dicts with BOTH ``cremona_label`` (e.g.
``11a1``) and ``lmfdb_label`` (e.g. ``11.a2``) when the mapping is
known, so callers can disambiguate.

Public surface
--------------
    has_local_mirror()                     -> bool
    mirror_info()                          -> dict
    update_mirror(force=False, ...)        -> dict
    elliptic_curves(label=..., ...)        -> list[dict]
    lookup_by_ainvs(ainvs)                 -> dict | None
    probe(timeout=3.0)                     -> bool

Cost model
----------
The full ecdata is ~600 MB across all dataset families (curvedata is the
biggest). By default we mirror only ``allcurves`` and ``allbsd`` for
conductor <= 100,000 (~25 MB + ~63 MB ~= 88 MB), which covers the
majority of bulk-scan use cases. Pass ``conductor_max`` to
``update_mirror`` for a different cap.

Tests in this module are gated behind ``PROMETHEUS_DOWNLOAD_CREMONA=1``
so CI doesn't pull megabytes of ECdata on every run.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import threading
import urllib.request
from typing import Any, Iterable, Optional

from . import _local


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DATASET_NAME = "cremona"
_GH_RAW_BASE = "https://raw.githubusercontent.com/JohnCremona/ecdata/master"
_GH_API_BASE = "https://api.github.com/repos/JohnCremona/ecdata/contents"
_DEFAULT_CONDUCTOR_MAX = 100_000  # opt-in default; 600 MB if uncapped

# Conductor range partitioning used by the upstream repo. The naming is
# "<lo>-<hi>" with conductors lo..hi (inclusive on both ends, no zero-pad
# on the high side). The first range is "00000-09999" (zero-padded, lo=0).
# We enumerate the canonical range tags up to 500000, the documented
# coverage of the dataset.
_RANGE_BLOCK = 10_000
_MAX_CONDUCTOR = 500_000  # documented coverage of ecdata


# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_cache: dict[str, Any] = {
    "loaded_for_max": None,        # int | None — conductor_max we loaded
    "by_cremona_label": None,      # dict[str, dict]
    "by_lmfdb_label":   None,      # dict[str, dict]
    "by_ainvs":         None,      # dict[tuple[int,...], dict]
    "all_rows":         None,      # list[dict]
    "load_error":       None,      # str | None
}


def clear_cache() -> None:
    """Drop the in-memory cache (the next query will re-read from disk)."""
    with _lock:
        for k in ("loaded_for_max", "by_cremona_label", "by_lmfdb_label",
                  "by_ainvs", "all_rows", "load_error"):
            _cache[k] = None


# ---------------------------------------------------------------------------
# Path / range helpers
# ---------------------------------------------------------------------------

def _root() -> pathlib.Path:
    """Return the cremona/ subdirectory under the prometheus data dir."""
    return _local.dataset_path(_DATASET_NAME)


def _range_tag(lo: int) -> str:
    """Return the canonical range tag '<lo>-<hi>' for a 10K block.

    The lo<10000 block is zero-padded to 5 digits; higher blocks are not.
    Examples:
        _range_tag(0)      -> '00000-09999'
        _range_tag(10000)  -> '10000-19999'
        _range_tag(100000) -> '100000-109999'
    """
    hi = lo + _RANGE_BLOCK - 1
    if lo < 10_000:
        return f"{lo:05d}-{hi:05d}"
    return f"{lo}-{hi}"


def _ranges_up_to(conductor_max: int) -> list[tuple[int, str]]:
    """Yield (lo, range_tag) covering conductors 0..conductor_max.

    The range is inclusive of the block containing conductor_max.
    """
    out = []
    cap = min(conductor_max, _MAX_CONDUCTOR)
    lo = 0
    while lo <= cap:
        out.append((lo, _range_tag(lo)))
        lo += _RANGE_BLOCK
    return out


def _file_path(family: str, range_tag: str) -> pathlib.Path:
    return _root() / family / f"{family}.{range_tag}"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_AINVS_RE = re.compile(r"\[\s*(-?\d+(?:\s*,\s*-?\d+)*)\s*\]")


def _parse_ainvs(token: str) -> Optional[list[int]]:
    """Parse '[0,-1,1,-10,-20]' -> [0, -1, 1, -10, -20]."""
    if not isinstance(token, str):
        return None
    m = _AINVS_RE.match(token.strip())
    if m is None:
        return None
    try:
        return [int(x) for x in m.group(1).split(",")]
    except ValueError:
        return None


def _to_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def _to_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _parse_allcurves_line(line: str) -> Optional[dict]:
    """Parse one line of an allcurves file -> dict.

    Format (per docs/file-format.txt):
        ID AI R T   = conductor class_letter idx ainvs rank torsion
    """
    parts = line.strip().split()
    if len(parts) < 6:
        return None
    cond = _to_int(parts[0])
    cls = parts[1]
    idx = _to_int(parts[2])
    ai = _parse_ainvs(parts[3])
    rank = _to_int(parts[4])
    tors = _to_int(parts[5])
    if cond is None or idx is None or ai is None:
        return None
    return {
        "conductor":     cond,
        "isogeny_class": cls,
        "curve_index":   idx,
        "ainvs":         ai,
        "rank":          rank,
        "torsion":       tors,
        "cremona_label": f"{cond}{cls}{idx}",
    }


def _parse_allbsd_line(line: str) -> Optional[dict]:
    """Parse one line of an allbsd file.

    Format: ID AI R T CP OM L1 REG SHA
        = conductor class idx ainvs rank torsion tamagawa real_period
          L1 regulator sha_an
    """
    parts = line.strip().split()
    if len(parts) < 11:
        return None
    cond = _to_int(parts[0])
    cls = parts[1]
    idx = _to_int(parts[2])
    ai = _parse_ainvs(parts[3])
    if cond is None or idx is None or ai is None:
        return None
    rank = _to_int(parts[4])
    tors = _to_int(parts[5])
    cp = _to_int(parts[6])
    omega = _to_float(parts[7])
    L1 = _to_float(parts[8])
    reg = _to_float(parts[9])
    sha_raw = parts[10]
    # sha_an is "either positive integer, or Real number" per the docs.
    sha_int = _to_int(sha_raw)
    sha: Any = sha_int if sha_int is not None else _to_float(sha_raw)
    return {
        "conductor":      cond,
        "isogeny_class":  cls,
        "curve_index":    idx,
        "ainvs":          ai,
        "rank":           rank,
        "torsion":        tors,
        "tamagawa":       cp,
        "real_period":    omega,
        "L1":             L1,
        "regulator":      reg,
        "sha_an":         sha,
        "cremona_label":  f"{cond}{cls}{idx}",
    }


def _parse_alllabels_line(line: str) -> Optional[tuple[str, str]]:
    """Parse one line of alllabels: N CRE_CLS CRE_NCURVE N LMFDB_CLS LMFDB_NCURVE.

    Returns (cremona_label, lmfdb_label) or None.
    """
    parts = line.strip().split()
    if len(parts) < 6:
        return None
    n1, cc, ci, n2, lc, li = parts[:6]
    if n1 != n2:
        return None
    if not n1.isdigit():
        return None
    return (f"{n1}{cc}{ci}", f"{n2}.{lc}{li}")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _existing_blocks(family: str, conductor_max: int) -> list[tuple[int, pathlib.Path]]:
    """Return [(lo, path), ...] for every existing file under cremona/<family>/
    whose lo<=conductor_max."""
    out = []
    for lo, tag in _ranges_up_to(conductor_max):
        p = _file_path(family, tag)
        if p.is_file() and p.stat().st_size > 0:
            out.append((lo, p))
    return out


def _ensure_loaded(conductor_max: int) -> None:
    """Populate the in-memory cache from on-disk files. Idempotent."""
    with _lock:
        if (_cache["all_rows"] is not None
                and (_cache["loaded_for_max"] or 0) >= conductor_max):
            return

        rows: list[dict] = []
        by_ainvs: dict[tuple[int, ...], dict] = {}
        by_cre: dict[str, dict] = {}

        # Prefer allbsd (richer); fall back to allcurves where allbsd is absent.
        allbsd_blocks = dict(_existing_blocks("allbsd", conductor_max))
        allcurves_blocks = dict(_existing_blocks("allcurves", conductor_max))

        if not allbsd_blocks and not allcurves_blocks:
            _cache["loaded_for_max"] = conductor_max
            _cache["by_cremona_label"] = {}
            _cache["by_lmfdb_label"] = {}
            _cache["by_ainvs"] = {}
            _cache["all_rows"] = []
            _cache["load_error"] = "no on-disk mirror present"
            return

        # Walk every block we have, BSD-first, allcurves backfill.
        seen_blocks: set[int] = set()
        for lo in sorted(set(list(allbsd_blocks) + list(allcurves_blocks))):
            seen_blocks.add(lo)
            block_rows: dict[str, dict] = {}

            bsd = allbsd_blocks.get(lo)
            if bsd is not None:
                with bsd.open("r", encoding="utf-8", errors="replace") as fh:
                    for ln in fh:
                        rec = _parse_allbsd_line(ln)
                        if rec is None:
                            continue
                        block_rows[rec["cremona_label"]] = rec

            ac = allcurves_blocks.get(lo)
            if ac is not None:
                with ac.open("r", encoding="utf-8", errors="replace") as fh:
                    for ln in fh:
                        rec = _parse_allcurves_line(ln)
                        if rec is None:
                            continue
                        # If allbsd already has this row, keep allbsd's
                        # (richer); otherwise insert the allcurves row.
                        block_rows.setdefault(rec["cremona_label"], rec)

            for clabel, rec in block_rows.items():
                rows.append(rec)
                by_cre[clabel] = rec
                ai_key = tuple(rec["ainvs"])
                # ainvs is the canonical key — first row wins on collision
                # (allbsd-rich rows came first, so this is the desired
                # behavior).
                by_ainvs.setdefault(ai_key, rec)

        # Layer the Cremona <-> LMFDB label map. alllabels is small (~few MB);
        # if absent we fall back to the trivial assumption "label letters
        # are the same" which is true for ~95% of conductors but wrong for
        # a known list of low-N classes — be honest and only set the
        # lmfdb_label when alllabels is present.
        by_lmfdb: dict[str, dict] = {}
        for lo, p in _existing_blocks("alllabels", conductor_max):
            with p.open("r", encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    pair = _parse_alllabels_line(ln)
                    if pair is None:
                        continue
                    cl, ll = pair
                    rec = by_cre.get(cl)
                    if rec is None:
                        continue
                    rec["lmfdb_label"] = ll
                    by_lmfdb[ll] = rec

        # Heuristic: for any row without an lmfdb_label, emit a "best-guess"
        # mapping with a `.` inserted between conductor and class. This is
        # correct for conductor < 11 (none) and the ~95% majority elsewhere
        # that uses identical Cremona/LMFDB letter codes; but we keep both
        # the heuristic and (where available) the verified label, and we
        # mark the heuristic with a flag so callers can tell.
        for rec in rows:
            if rec.get("lmfdb_label") is None:
                clabel = rec["cremona_label"]
                # Split conductor digits from the suffix
                m = re.match(r"^(\d+)([a-z]+)(\d+)$", clabel)
                if m:
                    rec["lmfdb_label"] = f"{m.group(1)}.{m.group(2)}{m.group(3)}"
                    rec["lmfdb_label_verified"] = False
                    by_lmfdb.setdefault(rec["lmfdb_label"], rec)
            else:
                rec["lmfdb_label_verified"] = True

        _cache["loaded_for_max"] = conductor_max
        _cache["all_rows"] = rows
        _cache["by_cremona_label"] = by_cre
        _cache["by_lmfdb_label"] = by_lmfdb
        _cache["by_ainvs"] = by_ainvs
        _cache["load_error"] = None


# ---------------------------------------------------------------------------
# Mirror status
# ---------------------------------------------------------------------------

def has_local_mirror() -> bool:
    """True iff at least one Cremona ecdata file is present on disk.

    We accept either ``allcurves/*`` or ``allbsd/*`` files; either family
    suffices for basic lookup. The check is filesystem-only (no parsing).
    """
    root = _root()
    if not root.is_dir():
        return False
    for family in ("allbsd", "allcurves"):
        sub = root / family
        if not sub.is_dir():
            continue
        try:
            for p in sub.iterdir():
                if p.is_file() and p.stat().st_size > 0:
                    return True
        except OSError:
            continue
    return False


def mirror_info() -> dict:
    """Return statistics about the on-disk Cremona mirror.

    Returns
    -------
    dict with keys:
        present:           bool — True iff has_local_mirror()
        n_curves:          int — number of distinct curves indexed
                                  (after _ensure_loaded(conductor_max))
        size_bytes:        int — total bytes used by the mirror dir
        files:             dict[str, list[str]] — family -> list of range tags
                                                  present on disk
        conductor_blocks:  list[int] — sorted lo conductor for each block
                                       present in either family
        last_refresh_iso:  str | None — populated by update_mirror()
        path:              str — absolute filesystem path to the mirror root
    """
    root = _root()
    info: dict[str, Any] = {
        "present":          has_local_mirror(),
        "n_curves":         0,
        "size_bytes":       _local.mirror_size(_DATASET_NAME),
        "files":            {},
        "conductor_blocks": [],
        "last_refresh_iso": None,
        "path":             str(root),
    }
    blocks: set[int] = set()
    for family in ("allcurves", "allbsd", "alllabels"):
        sub = root / family
        if not sub.is_dir():
            info["files"][family] = []
            continue
        names: list[str] = []
        try:
            for p in sorted(sub.iterdir()):
                if not p.is_file() or p.stat().st_size == 0:
                    continue
                # Names look like <family>.<lo>-<hi>; extract lo.
                tag = p.name.replace(f"{family}.", "", 1)
                names.append(tag)
                lo_str = tag.split("-", 1)[0]
                if lo_str.isdigit():
                    blocks.add(int(lo_str))
        except OSError:
            pass
        info["files"][family] = names
    info["conductor_blocks"] = sorted(blocks)

    meta = root / ".metadata.json"
    if meta.is_file():
        try:
            with meta.open("r", encoding="utf-8") as fh:
                m = json.load(fh)
            info["last_refresh_iso"] = m.get("last_refresh_iso")
            if "n_curves" in m:
                info["n_curves"] = int(m["n_curves"])
        except Exception:
            pass

    # If we already loaded the cache, prefer its actual count.
    if _cache["all_rows"] is not None:
        info["n_curves"] = len(_cache["all_rows"])

    return info


def _write_metadata(n_curves: int, conductor_max: int,
                    families: list[str]) -> None:
    """Persist a small sidecar describing the most-recent refresh."""
    import datetime
    root = _root()
    root.mkdir(parents=True, exist_ok=True)
    meta = {
        "last_refresh_iso": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds"),
        "n_curves":      n_curves,
        "conductor_max": conductor_max,
        "families":      families,
        "source":        "github.com/JohnCremona/ecdata",
    }
    with (root / ".metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check used by ``prometheus_math.registry``.

    Returns True iff the wrapper is "useful" — either we already have a
    local mirror, OR github.com is reachable so the user can download
    one with ``update_mirror()``.
    """
    if has_local_mirror():
        return True
    # Ping GitHub for any public 200; we hit the API root which is small.
    try:
        req = urllib.request.Request(
            "https://api.github.com",
            headers={"User-Agent": "prometheus-math/0.1",
                     "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


# ---------------------------------------------------------------------------
# update_mirror
# ---------------------------------------------------------------------------

def update_mirror(force: bool = False,
                  conductor_max: int = _DEFAULT_CONDUCTOR_MAX,
                  families: Iterable[str] = ("allcurves", "allbsd", "alllabels"),
                  ) -> dict:
    """Download Cremona's ecdata files into the local mirror.

    Parameters
    ----------
    force : bool
        If True, re-download files that already exist. Default False.
    conductor_max : int
        Only fetch blocks covering conductors 0..conductor_max. Default
        ``100_000`` (~88 MB). Set to ``500_000`` for the full dataset
        (~600 MB).
    families : iterable of str
        Which file families to download. Defaults to
        ``("allcurves", "allbsd", "alllabels")``. ``allcurves`` provides
        ainvs/rank/torsion; ``allbsd`` adds regulator + sha + Tamagawa +
        real period; ``alllabels`` carries the Cremona <-> LMFDB label
        translation.

    Returns
    -------
    dict with keys:
        refreshed:    bool — True iff at least one file was downloaded
                             (or re-downloaded under force=True).
        n_curves:     int  — distinct curves loaded after the refresh
        n_files:      int  — total files now present in the mirror
        downloaded:   list[str] — relative paths of files this call
                                  fetched
        skipped:      list[str] — relative paths already present
        failed:       list[str] — relative paths whose download raised
        source:       str  — "github.com/JohnCremona/ecdata"
        message:      str  — human-readable summary

    Side effects
    ------------
    Files are written under ``<PROMETHEUS_DATA_DIR>/cremona/``.
    A ``.metadata.json`` sidecar is written/updated. The in-memory
    cache is cleared so subsequent queries pick up fresh data.
    """
    root = _root()
    root.mkdir(parents=True, exist_ok=True)

    fams = [f for f in families if f in ("allcurves", "allbsd", "alllabels",
                                         "allgens", "allisog", "aplist",
                                         "alldegphi", "intpts", "galrep",
                                         "2adic", "curvedata")]
    downloaded: list[str] = []
    skipped:    list[str] = []
    failed:     list[str] = []

    ranges = _ranges_up_to(conductor_max)
    for family in fams:
        sub = root / family
        sub.mkdir(parents=True, exist_ok=True)
        for _lo, tag in ranges:
            url = f"{_GH_RAW_BASE}/{family}/{family}.{tag}"
            dest = sub / f"{family}.{tag}"
            rel = f"{family}/{family}.{tag}"
            if dest.exists() and not force:
                skipped.append(rel)
                continue
            try:
                _local.download(url, dest, show_progress=False)
                downloaded.append(rel)
            except Exception as e:  # 404, network error, etc.
                # Some upstream blocks are missing for higher families
                # (e.g. allbsd is dense up to N=500K but allgens is not).
                # We treat any non-200 as a soft skip.
                failed.append(f"{rel} ({type(e).__name__}: {e})")

    refreshed = len(downloaded) > 0

    # Reload the cache fresh.
    clear_cache()
    _ensure_loaded(conductor_max)
    n_curves = len(_cache["all_rows"] or [])

    # Persist metadata when at least one file was attempted (downloaded,
    # skipped because already-present, or failed). A truly trivial call
    # (families=() — no work attempted at all) leaves any existing
    # sidecar untouched.
    attempted = bool(downloaded) or bool(skipped) or bool(failed)
    if attempted:
        _write_metadata(n_curves, conductor_max, fams)

    if not refreshed and not skipped and not failed:
        msg = "no work — empty family list"
    elif refreshed:
        msg = (f"refreshed {len(downloaded)} files "
               f"(skipped {len(skipped)}, failed {len(failed)}); "
               f"now indexing {n_curves} curves "
               f"(conductor_max={conductor_max})")
    else:
        msg = (f"already up to date — {len(skipped)} files present, "
               f"indexing {n_curves} curves "
               f"(conductor_max={conductor_max}); "
               "pass force=True to re-download")

    return {
        "refreshed":  refreshed,
        "n_curves":   n_curves,
        "n_files":    sum(len(v) for v in mirror_info()["files"].values()),
        "downloaded": downloaded,
        "skipped":    skipped,
        "failed":     failed,
        "source":     "github.com/JohnCremona/ecdata",
        "message":    msg,
    }


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def _normalize_label(label: str) -> tuple[Optional[str], Optional[str]]:
    """Parse a label string and return (cremona_label, lmfdb_label).

    Either component may be None if the input doesn't determine it.
    Accepted forms:
        '11.a1'   -> lmfdb '11.a1', cremona heuristic '11a1'
        '11a1'    -> cremona '11a1' (no lmfdb commitment)
        '11 a 1'  -> ID-style; coerced to cremona '11a1'
    """
    if not isinstance(label, str):
        return None, None
    s = label.strip()
    if not s:
        return None, None
    # ID style: '11 a 1' or 'N a I'
    parts = s.split()
    if len(parts) == 3 and parts[0].isdigit() and parts[2].isdigit():
        return f"{parts[0]}{parts[1]}{parts[2]}", None
    # LMFDB style: '11.a1'
    if "." in s:
        m = re.match(r"^(\d+)\.([a-z]+)(\d+)$", s)
        if m:
            n, cls, idx = m.group(1), m.group(2), m.group(3)
            return f"{n}{cls}{idx}", f"{n}.{cls}{idx}"
        return None, s
    # Cremona style: '11a1'
    m = re.match(r"^(\d+)([a-z]+)(\d+)$", s)
    if m:
        return s, None
    return None, None


def lookup_by_ainvs(ainvs) -> Optional[dict]:
    """Exact match by Weierstrass 5-tuple [a1, a2, a3, a4, a6].

    Returns the canonical curve dict (rank, torsion, regulator, sha_an,
    real_period, etc.) or None if not in the mirror.
    """
    if not isinstance(ainvs, (list, tuple)):
        return None
    if len(ainvs) != 5:
        return None
    try:
        key = tuple(int(x) for x in ainvs)
    except (TypeError, ValueError):
        return None
    # Make sure cache is populated
    cmax = _cache["loaded_for_max"] or _DEFAULT_CONDUCTOR_MAX
    _ensure_loaded(cmax)
    return (_cache["by_ainvs"] or {}).get(key)


def elliptic_curves(label: Optional[str] = None,
                    conductor: Optional[int] = None,
                    rank: Optional[int] = None,
                    ainvs: Optional[list] = None,
                    conductor_max: Optional[int] = None,
                    limit: int = 10_000,
                    fall_back_to_lmfdb: bool = True,
                    ) -> list[dict]:
    """Local-first elliptic-curve lookup with LMFDB fallback.

    Parameters
    ----------
    label : LMFDB or Cremona label (e.g. "11.a1" or "11a1"). Both
            spellings are accepted; we look up under both.
    conductor : exact conductor filter (int).
    rank : exact rank filter (int).
    ainvs : 5-tuple Weierstrass coefficients (exact match).
    conductor_max : when scanning, only return rows with conductor <=
                    this. Defaults to whatever is loaded in cache.
    limit : max rows returned. Default 10_000.
    fall_back_to_lmfdb : if no local match (or no local mirror), try
                        ``prometheus_math.databases.lmfdb.elliptic_curves``
                        with the same filters. Default True.

    Returns
    -------
    list[dict] of curve records. Each record carries at least
    ``cremona_label``, ``lmfdb_label``, ``ainvs``, ``conductor``,
    ``rank``, ``torsion``; ``regulator``, ``sha_an``, ``real_period``,
    ``L1``, ``tamagawa`` are present iff the allbsd file was mirrored.
    """
    cmax = conductor_max or _cache["loaded_for_max"] or _DEFAULT_CONDUCTOR_MAX

    # Local-first
    local_results: list[dict] = []
    if has_local_mirror():
        _ensure_loaded(cmax)

        # Fast paths: single-row queries.
        if ainvs is not None and len(ainvs) == 5:
            row = lookup_by_ainvs(ainvs)
            if row is not None:
                if conductor is None or row["conductor"] == conductor:
                    if rank is None or row["rank"] == rank:
                        local_results = [row]

        elif label is not None:
            cl, ll = _normalize_label(label)
            row = None
            if cl is not None:
                row = (_cache["by_cremona_label"] or {}).get(cl)
            if row is None and ll is not None:
                row = (_cache["by_lmfdb_label"] or {}).get(ll)
            if row is not None:
                if conductor is None or row["conductor"] == conductor:
                    if rank is None or row["rank"] == rank:
                        local_results = [row]

        else:
            # Range scan
            for r in _cache["all_rows"] or []:
                if conductor is not None and r["conductor"] != conductor:
                    continue
                if rank is not None and r["rank"] != rank:
                    continue
                if conductor_max is not None and r["conductor"] > conductor_max:
                    continue
                local_results.append(r)
                if len(local_results) >= limit:
                    break

    if local_results:
        return local_results[:limit]

    # Fallback
    if not fall_back_to_lmfdb:
        return []
    try:
        from . import lmfdb as _lmfdb
    except Exception:
        return []
    # Translate label to LMFDB form.
    lmfdb_label: Optional[str] = None
    if label is not None:
        _, ll = _normalize_label(label)
        lmfdb_label = ll or label
    try:
        return _lmfdb.elliptic_curves(label=lmfdb_label,
                                      conductor=conductor,
                                      rank=rank,
                                      limit=limit)
    except Exception:
        return []


__all__ = [
    "has_local_mirror",
    "mirror_info",
    "update_mirror",
    "elliptic_curves",
    "lookup_by_ainvs",
    "probe",
    "clear_cache",
]
