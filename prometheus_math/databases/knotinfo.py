"""KnotInfo / LinkInfo — knot and link census wrapper.

KnotInfo (https://knotinfo.math.indiana.edu/) is the canonical knot census
maintained by Charles Livingston, Allison Moore, and collaborators. It
catalogs every prime knot up to 13 crossings (12,965 knots) with a long
list of computed invariants: signature, determinant, three-genus, slice
genera, Alexander/Jones/Khovanov polynomials, Heegaard Floer data,
hyperbolic volume, fibered/alternating flags, L-space classification,
and dozens more.

LinkInfo (https://linkinfo.sitehost.iu.edu/) is the link analog: every
prime link up to 11 crossings, with link-specific invariants
(linking matrix, multivariable Alexander, HOMFLYPT, etc).

Prometheus uses this wrapper for:
  * Identity-join testing (knot trace fields <-> number fields).
  * Cross-checking Techne's TOOL_KNOT_SHAPE_FIELD outputs against the
    canonical census values.
  * Charon's tensor: feeding signature/genus/volume/tau/epsilon as
    coordinate axes for the knot island.

Backend strategy
----------------
This wrapper prefers the upstream `database_knotinfo` PyPI package
(https://pypi.org/project/database-knotinfo/), maintained by Sebastian
Oehms with the agreement of the KnotInfo authors. It ships the full CSV
exports inside the package so we don't hit the network at all once
installed. If the package is unavailable we fall back to a direct CSV
download from the live KnotInfo / LinkInfo sites.

Either way, the parsed data is cached in-memory after first access (the
combined knot+link tables are ~30K rows total, comfortably fits in RAM).

Name normalization
------------------
KnotInfo's canonical name format is:

    <crossings><class>_<index>      e.g. 3_1, 4_1, 11n_34, 12a_3

where `<class>` is one of:
  * absent (Rolfsen names for crossing<=10)
  * 'a' (alternating, 11+ crossings)
  * 'n' (non-alternating, 11+ crossings)

We accept the following as equivalent inputs to `lookup()` and friends:

    '3_1'   '3.1'    '3a1'    'K3a1'    'K3_1'      -> '3_1'
    '11n34' '11n_34' '11.n.34' 'K11n34'             -> '11n_34'
    '12a_5' '12a5'   'K12a5'                        -> '12a_5'

Returned dict shape (only present keys are guaranteed; missing data is
silently dropped rather than mapped to None unless explicitly noted):

    {
      'name':                       '3_1',
      'crossing_number':            3,
      'signature':                  -2,
      'determinant':                3,
      'genus':                      1,                # = three_genus
      'three_genus':                1,
      'smooth_four_genus':          1,
      'topological_four_genus':     1,
      'smooth_concordance_genus':   1,
      'topological_concordance_genus': 1,
      'fibered':                    True,
      'alternating':                True,
      'jones_polynomial':           't+ t^3-t^4',
      'alexander_polynomial':       '1-t+ t^2',
      'alexander_coeffs':           [1, -1, 1],      # ascending degree
      'hyperbolic':                 False,           # volume>0
      'hyperbolic_volume':          0.0,             # None if non-hyperbolic
      'khovanov_polynomial':        '...',
      'seifert_genus':              1,               # = three_genus
      'tau':                        1,               # Ozsvath-Szabo
      'epsilon':                    1,
      'nu':                         None,            # often missing
      'l_space':                    True,
      'thurston_bennequin':         1,
      'unknotting_number':          1,
      'crosscap_number':            1,
      ...  (raw KnotInfo fields preserved under their exact names too)
    }

Public surface
--------------
    lookup(name)                   -> dict | None
    all_knots(crossing_max=13,
              hyperbolic_only=False) -> list[dict]
    filter(...)                    -> list[dict]
    alexander(name)                -> list[int] | None
    jones(name)                    -> str | None
    signature(name)                -> int | None
    is_l_space(name)               -> bool | None
    list_l_space_knots(crossing_max=13) -> list[str]
    probe(timeout=3.0)             -> bool
    clear_cache()                  -> None
    cache_info()                   -> dict
"""
from __future__ import annotations

import io
import re
import threading
from typing import Any, Iterable, Optional, Union

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_USER_AGENT = "prometheus-math/0.1 (mathematical research tool)"
_DEFAULT_TIMEOUT = 30.0  # seconds (CSV downloads can be slow)

# Live-CSV fallback URLs. These may shift over time; if both packages
# (database_knotinfo) and these URLs fail, the wrapper degrades to "no data".
# Order: tried in sequence; first 200-OK wins.
_KNOT_CSV_URLS = [
    "https://knotinfo.math.indiana.edu/homelinks/knotinfo_data_complete.csv",
    "https://knotinfo.math.indiana.edu/knotinfo_data_complete.csv",
]
_LINK_CSV_URLS = [
    "https://linkinfo.sitehost.iu.edu/linkinfo_data_complete.csv",
]

# Cache state — module-level so all callers share it.
_lock = threading.Lock()
_cache: dict[str, Any] = {
    "knots_by_name":   None,   # dict[str, dict]
    "knots_list":      None,   # list[dict]
    "links_by_name":   None,
    "links_list":      None,
    "source":          None,   # 'database_knotinfo' | 'csv-network' | None
    "load_error":      None,   # str | None
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_via_package() -> Optional[tuple[list[dict], list[dict]]]:
    """Try the packaged CSVs from `database_knotinfo`. Returns (knots, links) or None."""
    try:
        from database_knotinfo import link_list as _link_list  # type: ignore
    except Exception:
        return None
    try:
        knots = _link_list(proper_links=False)
        links = _link_list(proper_links=True)
    except Exception:
        return None
    if not knots:
        return None
    return knots, links


def _load_csv_from_url(url: str) -> Optional[list[dict]]:
    """Download a KnotInfo-style pipe-delimited CSV and parse to list[dict]."""
    import csv
    try:
        r = requests.get(url, headers={"User-Agent": _USER_AGENT},
                         timeout=_DEFAULT_TIMEOUT)
    except requests.RequestException:
        return None
    if r.status_code != 200 or not r.text:
        return None
    try:
        reader = csv.DictReader(io.StringIO(r.text), delimiter="|")
        rows = list(reader)
    except Exception:
        return None
    return rows or None


def _load_via_network() -> Optional[tuple[list[dict], list[dict]]]:
    """Try direct CSV downloads from KnotInfo / LinkInfo. Returns what we got
    (each side may be None if its server is unreachable)."""
    knots = None
    for url in _KNOT_CSV_URLS:
        knots = _load_csv_from_url(url)
        if knots:
            break
    links = None
    for url in _LINK_CSV_URLS:
        links = _load_csv_from_url(url)
        if links:
            break
    if knots is None and links is None:
        return None
    return knots or [], links or []


def _ensure_loaded() -> None:
    """Populate the module-level cache exactly once. Idempotent."""
    with _lock:
        if _cache["knots_by_name"] is not None:
            return
        # Strategy 1: pip package (preferred — no network).
        result = _load_via_package()
        source = "database_knotinfo"
        if result is None:
            result = _load_via_network()
            source = "csv-network"
        if result is None:
            _cache["knots_by_name"] = {}
            _cache["knots_list"] = []
            _cache["links_by_name"] = {}
            _cache["links_list"] = []
            _cache["source"] = None
            _cache["load_error"] = "all backends failed (no package, no network)"
            return

        knots_raw, links_raw = result
        knots = [_shape_knot(row) for row in (knots_raw or [])
                 if _is_real_data_row(row)]
        links = [_shape_link(row) for row in (links_raw or [])
                 if _is_real_data_row(row)]

        # Index by canonical name plus all known aliases.
        knots_by_name: dict[str, dict] = {}
        for k in knots:
            for alias in _name_aliases(k["name"]):
                knots_by_name.setdefault(alias, k)

        links_by_name: dict[str, dict] = {}
        for ll in links:
            for alias in _name_aliases(ll["name"]):
                links_by_name.setdefault(alias, ll)

        _cache["knots_list"] = knots
        _cache["knots_by_name"] = knots_by_name
        _cache["links_list"] = links
        _cache["links_by_name"] = links_by_name
        _cache["source"] = source
        _cache["load_error"] = None


def _is_real_data_row(row: dict) -> bool:
    """The first row of every KnotInfo CSV is a 'pretty header' row whose
    'name' field is literally 'Name'. Filter that out."""
    n = (row or {}).get("name", "")
    if not n or not isinstance(n, str):
        return False
    s = n.strip()
    if not s:
        return False
    if s.lower() == "name":
        return False
    return True


# ---------------------------------------------------------------------------
# Name normalization
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(
    r"^k?(\d+)([an]?)[._]?(\d+)$",
    re.IGNORECASE,
)
_LINK_NAME_RE = re.compile(
    r"^l(\d+)([an])(\d+)(?:\{(\d+)\})?$",
    re.IGNORECASE,
)


def _canonical_knot_name(name: str) -> Optional[str]:
    """Normalize a user-supplied knot name to KnotInfo's canonical form.

    Examples:
        '3_1', '3.1', '3a1', 'K3a1', 'K3_1', 'k3.1'  -> '3_1'
        '11n34', '11n_34', 'K11n_34'                 -> '11n_34'
        '12a5', '12a_5', 'K12.a.5'                   -> '12a_5'

    Returns None if the input doesn't parse.
    """
    if not isinstance(name, str):
        return None
    s = name.strip().replace(" ", "").replace(".", "_")
    # Strip leading 'K'
    if s.lower().startswith("k") and len(s) > 1 and s[1].isdigit():
        s = s[1:]
    m = _NAME_RE.match(s)
    if not m:
        return None
    crossings, cls, idx = m.group(1), m.group(2).lower(), m.group(3)
    cn = int(crossings)
    # 0-10 crossings have no class letter; 11+ require one.
    if cn <= 10:
        if cls and cls not in ("",):
            # 'K3a1' is awkward — let it pass anyway, we'll just emit '3_1'
            pass
        return f"{cn}_{int(idx)}"
    else:
        if not cls:
            # Without a class letter the canonical form is ambiguous; reject.
            return None
        return f"{cn}{cls}_{int(idx)}"


def _name_aliases(canonical: str) -> list[str]:
    """All input forms that should resolve to this canonical name."""
    out = {canonical, canonical.lower()}
    # 3_1 -> 3.1, 31 (well, 3a1 etc)
    m = re.match(r"^(\d+)([an]?)_(\d+)$", canonical)
    if m:
        cn, cls, idx = m.group(1), m.group(2), m.group(3)
        forms = [
            f"{cn}_{idx}",
            f"{cn}.{idx}" if not cls else f"{cn}{cls}.{idx}",
            f"{cn}{cls}{idx}" if cls else f"{cn}_{idx}",
            f"{cn}{cls}_{idx}",
            f"K{cn}{cls}_{idx}",
            f"K{cn}{cls}{idx}",
            f"k{cn}{cls}_{idx}",
        ]
        for f in forms:
            out.add(f)
            out.add(f.lower())
    return list(out)


# ---------------------------------------------------------------------------
# Field parsing
# ---------------------------------------------------------------------------

def _parse_int(s: Any) -> Optional[int]:
    if s is None:
        return None
    if isinstance(s, int):
        return s
    s = str(s).strip()
    if not s:
        return None
    # Some KnotInfo cells are e.g. '-2' or '0' or '1'; strip any junk.
    try:
        return int(s)
    except ValueError:
        # Sometimes 'g4' fields contain ranges like '0,1' meaning lower=0 upper=1.
        # We refuse to guess; return None.
        return None


def _parse_float(s: Any) -> Optional[float]:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_yes_no(s: Any) -> Optional[bool]:
    if s is None:
        return None
    s = str(s).strip().lower()
    if s in ("y", "yes", "true", "1"):
        return True
    if s in ("n", "no", "false", "0"):
        return False
    return None


def _parse_alex_vector(s: Any) -> Optional[list[int]]:
    """Parse KnotInfo's alexander_polynomial_vector format.

    Format (per KnotInfo docs):  '[lo_degree, length, c_lo, c_lo+1, ..., c_hi]'

    Returns the bare coefficient list in ascending degree order, e.g.
    trefoil's '[0, 2, 1, -1, 1]' -> [1, -1, 1] meaning 1 - t + t^2.
    """
    if s is None:
        return None
    txt = str(s).strip()
    if not txt:
        return None
    if txt.startswith("["):
        txt = txt[1:]
    if txt.endswith("]"):
        txt = txt[:-1]
    parts = [p.strip() for p in txt.split(",") if p.strip()]
    if len(parts) < 3:
        return None
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    # First two entries are degree-min and length; the rest are coefficients.
    return nums[2:] or None


# ---------------------------------------------------------------------------
# Row shaping
# ---------------------------------------------------------------------------

# (canonical_key, raw_field, parser)
_KNOT_FIELDS = [
    ("crossing_number",                "crossing_number",                 _parse_int),
    ("signature",                      "signature",                       _parse_int),
    ("determinant",                    "determinant",                     _parse_int),
    ("three_genus",                    "three_genus",                     _parse_int),
    ("smooth_four_genus",              "smooth_four_genus",               _parse_int),
    ("topological_four_genus",         "topological_four_genus",          _parse_int),
    ("smooth_concordance_genus",       "smooth_concordance_genus",        _parse_int),
    ("topological_concordance_genus",  "topological_concordance_genus",   _parse_int),
    ("fibered",                        "fibered",                         _parse_yes_no),
    ("alternating",                    "alternating",                     _parse_yes_no),
    ("jones_polynomial",               "jones_polynomial",                str),
    ("alexander_polynomial",           "alexander_polynomial",            str),
    ("hyperbolic_volume_raw",          "volume",                          _parse_float),
    ("khovanov_polynomial",            "khovanov_unreduced_integral_polynomial", str),
    ("tau",                            "ozsvath_szabo_tau_invariant",     _parse_int),
    ("epsilon",                        "epsilon",                         _parse_int),
    ("thurston_bennequin",             "thurston_bennequin_number",       _parse_int),
    ("unknotting_number",              "unknotting_number",               _parse_int),
    ("crosscap_number",                "crosscap_number",                 _parse_int),
    ("braid_index",                    "braid_index",                     _parse_int),
    ("turaev_genus",                   "turaev_genus",                    _parse_int),
    ("morse_novikov_number",           "morse_novikov_number",            _parse_int),
    ("tunnel_number",                  "tunnel_number",                   _parse_int),
]


def _shape_knot(row: dict) -> dict:
    """Convert a raw KnotInfo CSV row into our normalized dict."""
    out: dict[str, Any] = {"name": (row.get("name") or "").strip()}

    for canonical, raw_key, parser in _KNOT_FIELDS:
        raw_val = row.get(raw_key, "")
        if raw_val == "" or raw_val is None:
            continue
        try:
            parsed = parser(raw_val)
        except Exception:
            parsed = None
        if parsed is None and parser is str:
            parsed = str(raw_val).strip() or None
        if parsed is not None and not (isinstance(parsed, str) and not parsed):
            out[canonical] = parsed

    # Aliases / derived fields.
    if "three_genus" in out:
        out.setdefault("genus", out["three_genus"])
        out.setdefault("seifert_genus", out["three_genus"])

    # hyperbolic_volume: present and >0 means hyperbolic.
    vol = out.pop("hyperbolic_volume_raw", None)
    if vol is not None and vol > 0:
        out["hyperbolic_volume"] = vol
        out["hyperbolic"] = True
    else:
        out["hyperbolic_volume"] = None
        out["hyperbolic"] = False

    # Slice genera: KnotInfo separates smooth and topological. Provide a
    # conventional 'slice_genus_smooth' / 'slice_genus_topological' alias.
    if "smooth_four_genus" in out:
        out["slice_genus_smooth"] = out["smooth_four_genus"]
    if "topological_four_genus" in out:
        out["slice_genus_topological"] = out["topological_four_genus"]
    if "smooth_concordance_genus" in out:
        out["concordance_genus"] = out["smooth_concordance_genus"]

    # Alexander polynomial coefficients, parsed to list[int].
    apv = row.get("alexander_polynomial_vector")
    coeffs = _parse_alex_vector(apv)
    if coeffs is not None:
        out["alexander_coeffs"] = coeffs

    # L-space classification: KnotInfo uses 'Yes' / 'No'.
    ls = (row.get("l_space") or "").strip().lower()
    if ls == "yes":
        out["l_space"] = True
    elif ls == "no":
        out["l_space"] = False
    else:
        out["l_space"] = None

    # nu (HFK invariant): often missing in KnotInfo; we expose it as None
    # to keep the documented surface stable.
    out["nu"] = _parse_int(row.get("nu"))

    return out


def _shape_link(row: dict) -> dict:
    """Minimal shaping for a LinkInfo row. We expose the raw KnotInfo dict
    plus a couple of normalized keys; full link-invariant parsing isn't
    implemented yet (Prometheus's first uses are knot-only)."""
    out: dict[str, Any] = {"name": (row.get("name") or "").strip()}
    for key in ("crossing_number", "braid_index", "alternating"):
        v = row.get(key)
        if v in (None, ""):
            continue
        if key == "alternating":
            out[key] = _parse_yes_no(v)
        else:
            iv = _parse_int(v)
            if iv is not None:
                out[key] = iv
    # Preserve a handful of polynomial fields verbatim (LinkInfo convention).
    for key in ("homflypt_polynomial", "jones_polynomial",
                "multivariable_alexander_polynomial"):
        v = row.get(key)
        if v:
            out[key] = str(v).strip()
    return out


# ---------------------------------------------------------------------------
# Public API — knots
# ---------------------------------------------------------------------------

def lookup(name) -> Optional[dict]:
    """Look up a knot by name.

    Accepts canonical KnotInfo names ('3_1', '4_1', '11n_34') as well as
    common variants ('3.1', '3a1', 'K3_1', 'K11n34'). Returns the
    normalized dict described in the module docstring, or None if not
    found.
    """
    _ensure_loaded()
    by_name: dict[str, dict] = _cache["knots_by_name"] or {}
    if not by_name:
        return None
    # First try exact match.
    if name in by_name:
        return by_name[name]
    canon = _canonical_knot_name(name)
    if canon is None:
        return None
    return by_name.get(canon)


def all_knots(crossing_max: int = 13,
              hyperbolic_only: bool = False) -> list[dict]:
    """Return all knots up to `crossing_max` crossings.

    With the default `crossing_max=13` and `hyperbolic_only=False` you
    get ~12,965 knots. Set `hyperbolic_only=True` to drop the (rare)
    non-hyperbolic ones (torus knots, satellites at low crossings).
    """
    _ensure_loaded()
    knots: list[dict] = _cache["knots_list"] or []
    out = [k for k in knots
           if (k.get("crossing_number") or 0) <= crossing_max]
    if hyperbolic_only:
        out = [k for k in out if k.get("hyperbolic")]
    return out


def filter(crossing_number: Any = None,
           genus: Any = None,
           alternating: Any = None,
           determinant: Any = None,
           hyperbolic: Any = None,
           signature: Any = None,
           fibered: Any = None,
           l_space: Any = None) -> list[dict]:
    """Filter knots by computed invariants.

    Each parameter is either:
      * None         - don't filter on this attribute
      * a value      - exact match
      * a (lo, hi) tuple - inclusive range (numeric attributes only)

    Boolean filters (alternating, hyperbolic, fibered, l_space) accept
    True/False, and treat None values in the data as a non-match.
    """
    _ensure_loaded()
    knots: list[dict] = list(_cache["knots_list"] or [])

    def _match_numeric(val, spec) -> bool:
        if val is None:
            return False
        if isinstance(spec, tuple) and len(spec) == 2:
            lo, hi = spec
            try:
                return (lo is None or val >= lo) and (hi is None or val <= hi)
            except TypeError:
                return False
        return val == spec

    def _match_bool(val, spec) -> bool:
        if val is None:
            return False
        return bool(val) == bool(spec)

    out = []
    for k in knots:
        if crossing_number is not None and not _match_numeric(
                k.get("crossing_number"), crossing_number):
            continue
        if genus is not None and not _match_numeric(
                k.get("three_genus"), genus):
            continue
        if determinant is not None and not _match_numeric(
                k.get("determinant"), determinant):
            continue
        if signature is not None and not _match_numeric(
                k.get("signature"), signature):
            continue
        if alternating is not None and not _match_bool(
                k.get("alternating"), alternating):
            continue
        if fibered is not None and not _match_bool(
                k.get("fibered"), fibered):
            continue
        if hyperbolic is not None and not _match_bool(
                k.get("hyperbolic"), hyperbolic):
            continue
        if l_space is not None and not _match_bool(
                k.get("l_space"), l_space):
            continue
        out.append(k)
    return out


def alexander(name) -> Optional[list[int]]:
    """Alexander polynomial coefficients of `name`, ascending degree.

    Returns e.g. [1, -3, 1] for the figure-8 knot 4_1 (i.e. 1 - 3t + t^2).
    Sign convention matches KnotInfo's vector representation directly.
    """
    rec = lookup(name)
    if rec is None:
        return None
    coeffs = rec.get("alexander_coeffs")
    if coeffs is None:
        return None
    return list(coeffs)


def jones(name) -> Optional[str]:
    """Jones polynomial as a Laurent-polynomial string.

    KnotInfo stores the polynomial as a hand-formatted string like
    't+ t^3-t^4'; we return it verbatim. (Programmatic parsing into a
    polynomial object is left to the caller — typically sympy or Sage.)
    """
    rec = lookup(name)
    return None if rec is None else rec.get("jones_polynomial")


def signature(name) -> Optional[int]:
    """Knot signature (always an even integer for knots; positive or negative)."""
    rec = lookup(name)
    return None if rec is None else rec.get("signature")


def is_l_space(name) -> Optional[bool]:
    """Whether the knot is an L-space knot (per HFK detection in KnotInfo).

    Returns True / False / None (unknown / not in census).
    """
    rec = lookup(name)
    return None if rec is None else rec.get("l_space")


def list_l_space_knots(crossing_max: int = 13) -> list[str]:
    """Names of every L-space knot in the KnotInfo census up to `crossing_max`."""
    return [k["name"] for k in filter(crossing_number=(0, crossing_max),
                                      l_space=True)]


# ---------------------------------------------------------------------------
# Public API — links (small surface; expand as Prometheus needs grow)
# ---------------------------------------------------------------------------

def link_lookup(name: str) -> Optional[dict]:
    """Look up a link by LinkInfo name (e.g. 'L4a1{0}', 'L6n1{1,1}')."""
    _ensure_loaded()
    by_name: dict[str, dict] = _cache["links_by_name"] or {}
    if not by_name:
        return None
    if name in by_name:
        return by_name[name]
    return by_name.get(name.lower())


def all_links() -> list[dict]:
    """Every link in the LinkInfo census (~4,189 entries)."""
    _ensure_loaded()
    return list(_cache["links_list"] or [])


# ---------------------------------------------------------------------------
# Cache management & diagnostics
# ---------------------------------------------------------------------------

def clear_cache() -> None:
    """Drop every cached row. The next call re-loads from the package or net."""
    with _lock:
        _cache["knots_by_name"] = None
        _cache["knots_list"] = None
        _cache["links_by_name"] = None
        _cache["links_list"] = None
        _cache["source"] = None
        _cache["load_error"] = None


def cache_info() -> dict:
    """Diagnostics for the in-memory cache."""
    knots = _cache["knots_list"]
    links = _cache["links_list"]
    return {
        "knots_loaded": len(knots) if knots is not None else 0,
        "links_loaded": len(links) if links is not None else 0,
        "source":       _cache["source"],
        "load_error":   _cache["load_error"],
    }


# ---------------------------------------------------------------------------
# Probe (for registry.py)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Cheap availability check used by prometheus_math.registry.

    The wrapper is "available" if either:
      (a) the `database_knotinfo` PyPI package is importable AND yields
          a non-empty knot list, or
      (b) the live KnotInfo CSV is reachable in `timeout` seconds.

    No network is hit when (a) succeeds.
    """
    # Fast path: package is importable.
    try:
        from database_knotinfo import link_list as _link_list  # type: ignore
        rows = _link_list(proper_links=False)
        if rows and len(rows) > 100:
            return True
    except Exception:
        pass

    # Slow path: HEAD/GET the live CSV with a tight timeout.
    for url in _KNOT_CSV_URLS:
        try:
            r = requests.head(url, headers={"User-Agent": _USER_AGENT},
                              timeout=timeout, allow_redirects=True)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            return True
    return False
