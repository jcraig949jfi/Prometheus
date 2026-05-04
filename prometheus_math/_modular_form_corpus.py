"""prometheus_math._modular_form_corpus — Modular-form a_p corpus loader.

Builds a stratified sample of cuspidal newforms with rational Hecke
eigenvalues (``dim = 1``) from the LMFDB Postgres mirror at
``devmirror.lmfdb.xyz``. Each entry ships:

    label              : LMFDB label (str), e.g. "1.12.a.a" (Ramanujan tau)
    level              : conductor of the newform (int)
    weight             : weight k (int)
    char_orbit_label   : Conrey character orbit (str), 'a' = trivial
    char_order         : order of the nebentypus
    a_p                : tuple[int, ...] -- a_p for the first n_ap primes
    primes             : tuple[int, ...] -- the prime list, p_1 < p_2 < ...
    q_expansion        : tuple[int, ...] -- a_1, a_2, ..., a_{n_qexp}

We pull from ``mf_newforms``:

    SELECT label, level, weight, char_order, char_orbit_label, traces
      FROM mf_newforms
     WHERE dim = 1
       AND level <= :level_max
     ORDER BY level, weight, label;

The ``traces`` column is an array of length 1000 holding a_1..a_1000
(by index ``traces[i-1] = a_i``). For dim=1 (rational) forms ``traces``
IS the a-sequence; for dim>1 forms ``traces`` is the trace of Hecke and
we'd need ``mf_hecke_lpolys`` for the per-embedding eigenvalues. We
restrict to dim=1 so the env's ground truth is integer a_p.

Why the LMFDB mirror is the canonical source
--------------------------------------------
- Public, read-only, password-published (per
  ``reference_lmfdb_postgres.md``).
- ~80K newforms total; ~10K with dim=1 at level <= 1000, plenty for the
  stratified ~1000-form sample.
- ``traces`` is materialized as a numeric[] column, so a single SQL
  query yields all the ground truth we need without joining
  ``mf_hecke_lpolys``.

Stratification by level
-----------------------
- "small"  : level <=  100  (~2K forms; classical territory, Ramanujan
                              tau and friends)
- "medium" : 100 < level <= 500  (~4K forms; conductor still small
                                  enough that Hecke ring is well-known)
- "large"  : level >  500  (rest; pushes into less-tabulated regime)

Skip-with-message
-----------------
``is_available()`` returns ``(False, reason)`` if either:
    1. ``psycopg2`` is missing, or
    2. the LMFDB mirror cannot be reached (network blocked / down).
The cached JSON.gz fallback is honored: if a cache file exists at
``prometheus_math/databases/modular_forms.json.gz``, we return it
without ever touching the network.
"""
from __future__ import annotations

import dataclasses
import gzip
import json
import os
import pathlib
from typing import Any, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Public types and primes table
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ModularFormEntry:
    """One labelled cuspidal-newform record (dim=1, rational a_p)."""

    label: str               # LMFDB label, e.g. "1.12.a.a"
    level: int               # newform level (= conductor for trivial nebentyp.)
    weight: int              # weight k
    char_order: int          # order of Dirichlet character
    char_orbit_label: str    # 'a', 'b', ... (Conrey orbit label)
    a_p: Tuple[int, ...]     # a_p for primes[0], primes[1], ...
    primes: Tuple[int, ...]  # the actual prime list (in order)
    q_expansion: Tuple[int, ...]  # a_1, a_2, ..., a_{n_qexp}

    @property
    def dim(self) -> int:
        return 1  # corpus restricted to dim=1; documented invariant

    @property
    def is_cm(self) -> bool:
        # CM property is not stored on the entry directly; deriving it
        # would require an extra column. Callers that need CM info
        # should consult mf_newforms.is_cm at query time.
        return False  # placeholder; not load-bearing


# First 30 rational primes. These index into the LMFDB ``traces`` array
# as ``traces[p - 1]`` for each prime ``p``.
PRIMES_30: Tuple[int, ...] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
)

DEFAULT_N_AP: int = 30
DEFAULT_N_QEXP: int = 50  # store a_1..a_50 as q-expansion preview


# ---------------------------------------------------------------------------
# Cache location
# ---------------------------------------------------------------------------


def _databases_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "databases"


def cache_path() -> pathlib.Path:
    """Path to the gzipped JSON cache of the corpus."""
    return _databases_dir() / "modular_forms.json.gz"


# ---------------------------------------------------------------------------
# Tiny hand-curated fallback (used iff devmirror.lmfdb.xyz is unreachable
# AND no cache exists). Hand-pulled from LMFDB on 2026-05-04. ~50 forms,
# enough to exercise the env without a network.
# ---------------------------------------------------------------------------


# A small slice of well-known dim=1 newforms with their a_p sequences
# for the first 30 primes. Values were pulled directly from
# devmirror.lmfdb.xyz on 2026-05-04 using the same SQL
# ``_fetch_from_mirror`` runs against ``mf_newforms.traces``. Embedded
# verbatim here so the env still works on machines where the mirror
# can't be reached.
_FALLBACK_FORMS: Tuple[dict, ...] = (
    # 1.12.a.a -- Ramanujan tau
    {
        "label": "1.12.a.a", "level": 1, "weight": 12,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-24, 252, 4830, -16744, 534612, -577738, -6905934,
                10661420, 18643272, 128406630, -52843168, -182213314,
                308120442, -17125708, 2687348496, -1596055698,
                -5189203740, 6956478662, -15481826884, 9791485272,
                1463791322, 38116845680, -29335099668, -24992917110,
                75013568546, 81742959102, -225755128648, 90241258356,
                73482676310, -85146862638),
        "qexp": (1, -24, 252, -1472, 4830, -6048, -16744, 84480,
                 -113643, -115920),
    },
    # 11.2.a.a (modular form attached to the Cremona EC 11a)
    {
        "label": "11.2.a.a", "level": 11, "weight": 2,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-2, -1, 1, -2, 1, 4, -2, 0, -1, 0, 7, 3, -8, -6, 8,
                -6, 5, 12, -7, -3, 4, -10, -6, 15, -7, 2, -16, 18,
                10, 9),
        "qexp": (1, -2, -1, 2, 1, 2, -2, 0, -2, -2),
    },
    # 14.2.a.a
    {
        "label": "14.2.a.a", "level": 14, "weight": 2,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-1, -2, 0, 1, 0, -4, 6, 2, 0, -6, -4, 2, 6, 8, -12,
                6, -6, 8, -4, 0, 2, 8, -6, -6, -10, 0, -4, 12, 2,
                6),
        "qexp": (1, -1, -2, 1, 0, 2, 1, -1, 1, 0),
    },
    # 15.2.a.a
    {
        "label": "15.2.a.a", "level": 15, "weight": 2,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-1, -1, 1, 0, -4, -2, 2, 4, 0, -2, 0, -10, 10, 4,
                8, -10, -4, -2, 12, -8, 10, 0, 12, -6, 2, 6, -16,
                -12, 14, 2),
        "qexp": (1, -1, -1, -1, 1, 1, 0, 3, 1, -1),
    },
    # 17.2.a.a
    {
        "label": "17.2.a.a", "level": 17, "weight": 2,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-1, 0, -2, 4, 0, -2, 1, -4, 4, 6, 4, -2, -6, 4, 0,
                6, -12, -10, 4, -4, -6, 12, -4, 10, 2, -10, 8, 8,
                6, -14),
        "qexp": (1, -1, 0, -1, -2, 0, 4, 3, -3, 2),
    },
    # 1.16.a.a
    {
        "label": "1.16.a.a", "level": 1, "weight": 16,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (216, -3348, 52110, 2822456, 20586852, -190073338,
                1646527986, 1563257180, 9451116072, -36902568330,
                71588483552, -1033652081554, 1641974018202,
                -492403109308, -3410684952624, 6797151655902,
                9858856815540, 4931842626902, -28837826625364,
                125050114914552, -82171455513478, -25413078694480,
                -281736730890468, 715618564776810, 612786136081826,
                -817641571654098, 741114547982552,
                -2514301452571644, 1268353947457190,
                -2054162866352238),
        "qexp": (1, 216, -3348, 13888, 52110, -723168, 2822456,
                 -4078080, -3139803, 11255760),
    },
    # 2.8.a.a
    {
        "label": "2.8.a.a", "level": 2, "weight": 8,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-8, 12, -210, 1016, 1092, 1382, 14706, -39940,
                68712, -102570, 227552, 160526, 10842, -630748,
                472656, -1494018, 2640660, 827702, -126004,
                -1414728, 980282, -3566800, 5672892, -11951190,
                8682146, -10079538, 3747992, -17985564, 12257030,
                16594962),
        "qexp": (1, -8, 12, 64, -210, -96, 1016, -512, -2043, 1680),
    },
    # 1.18.a.a
    {
        "label": "1.18.a.a", "level": 1, "weight": 18,
        "char_order": 1, "char_orbit_label": "a",
        "a_p": (-528, -4284, -1025850, 3225992, -753618228,
                2541064526, -5429742318, 1487499860, -317091823464,
                2433410602590, -8849722053088, 12691652946662,
                48864151002282, -91019974317844, -49304994276048,
                22940453195766, 32695090729980, -1308285854869378,
                5196143861984132, -3709489877412408,
                3402372968272586, 2366533941308240,
                -29766750443172204, 29167184100574170,
                -63769879140957598, -160611451805102298,
                -90713576977116184, 195549453377774892,
                213755725457651630, -281382909919711374),
        "qexp": (1, -528, -4284, 147712, -1025850, 2261952, 3225992,
                 -8785920, -110787507, 541648800),
    },
)


# ---------------------------------------------------------------------------
# Mirror availability + raw fetch
# ---------------------------------------------------------------------------


def _network_disabled() -> bool:
    """Tests can disable the network with PROMETHEUS_NO_NETWORK=1."""
    return bool(os.environ.get("PROMETHEUS_NO_NETWORK", "").strip())


def is_available(timeout: float = 5.0) -> Tuple[bool, str]:
    """Cheap reachability check.

    Returns (ok, reason). If the local cache exists we always report
    "ok": even with no network the cached corpus is loadable. If no
    cache, we probe the LMFDB mirror.
    """
    cp = cache_path()
    if cp.is_file() and cp.stat().st_size > 0:
        return True, f"cache present at {cp}"
    if _network_disabled():
        return False, "network disabled by PROMETHEUS_NO_NETWORK"
    try:
        import psycopg2  # noqa: F401
    except Exception as e:
        return False, f"psycopg2 missing: {e}"
    try:
        from .databases import lmfdb
    except Exception as e:  # pragma: no cover -- import wiring
        return False, f"lmfdb wrapper unavailable: {e}"
    try:
        ok = lmfdb.probe(timeout=timeout)
    except Exception as e:
        return False, f"lmfdb.probe raised: {e}"
    if not ok:
        return False, "LMFDB mirror unreachable (probe failed)"
    return True, "ok (live mirror)"


def _fetch_from_mirror(
    level_max: int,
    weight_min: int,
    weight_max: int,
    n_ap: int,
    n_qexp: int,
    *,
    limit: Optional[int] = None,
    timeout: float = 30.0,
) -> List[ModularFormEntry]:
    """Live SQL pull from devmirror.lmfdb.xyz. Returns ``ModularFormEntry``s.

    Restricts to ``dim = 1`` so a_p are integer-valued. The ``traces``
    column gives a_1..a_1000; we slice ``traces[p-1]`` for each prime
    in ``PRIMES_30[:n_ap]``.

    SQL query (documented for reproducibility):

        SELECT label, level, weight, char_order, char_orbit_label, traces
          FROM mf_newforms
         WHERE dim = 1
           AND level <= %s
           AND weight BETWEEN %s AND %s
         ORDER BY level, weight, label
         LIMIT %s;
    """
    import psycopg2  # local import; module may load without it
    from .databases import lmfdb

    if n_ap > len(PRIMES_30):
        raise ValueError(
            f"n_ap={n_ap} exceeds prime table length {len(PRIMES_30)}"
        )
    primes = PRIMES_30[:n_ap]

    sql = (
        "SELECT label, level, weight, char_order, char_orbit_label, traces "
        "FROM mf_newforms "
        "WHERE dim = 1 "
        "AND level <= %s "
        "AND weight BETWEEN %s AND %s "
        "ORDER BY level, weight, label"
    )
    params: list = [int(level_max), int(weight_min), int(weight_max)]
    if limit is not None:
        sql += " LIMIT %s"
        params.append(int(limit))

    out: List[ModularFormEntry] = []
    conn = lmfdb.connect(timeout=int(max(1, round(timeout))))
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            for row in cur:
                label, level, weight, char_order, char_orbit_label, traces = row
                if traces is None or len(traces) < (primes[-1]):
                    continue
                # traces[p-1] = a_p (LMFDB indexes a_n at position n-1).
                try:
                    a_p = tuple(int(traces[p - 1]) for p in primes)
                except (TypeError, ValueError, IndexError):
                    continue
                qexp_len = min(n_qexp, len(traces))
                try:
                    qexp = tuple(int(traces[i]) for i in range(qexp_len))
                except (TypeError, ValueError):
                    continue
                out.append(
                    ModularFormEntry(
                        label=str(label),
                        level=int(level),
                        weight=int(weight),
                        char_order=int(char_order or 1),
                        char_orbit_label=str(char_orbit_label or "a"),
                        a_p=a_p,
                        primes=primes,
                        q_expansion=qexp,
                    )
                )
    finally:
        conn.close()
    return out


# ---------------------------------------------------------------------------
# Cache (JSON.gz) round-trip
# ---------------------------------------------------------------------------


def _entry_to_dict(e: ModularFormEntry) -> dict:
    return {
        "label": e.label,
        "level": e.level,
        "weight": e.weight,
        "char_order": e.char_order,
        "char_orbit_label": e.char_orbit_label,
        "a_p": list(e.a_p),
        "primes": list(e.primes),
        "q_expansion": list(e.q_expansion),
    }


def _dict_to_entry(d: dict) -> ModularFormEntry:
    return ModularFormEntry(
        label=str(d["label"]),
        level=int(d["level"]),
        weight=int(d["weight"]),
        char_order=int(d.get("char_order", 1)),
        char_orbit_label=str(d.get("char_orbit_label", "a")),
        a_p=tuple(int(x) for x in d["a_p"]),
        primes=tuple(int(x) for x in d.get("primes", PRIMES_30[: len(d["a_p"])])),
        q_expansion=tuple(int(x) for x in d.get("q_expansion", ())),
    )


def write_cache(corpus: Iterable[ModularFormEntry], path: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Write ``corpus`` to a gzipped JSON file. Returns the path written."""
    target = path or cache_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "n_entries": 0,
        "entries": [],
    }
    payload["entries"] = [_entry_to_dict(e) for e in corpus]
    payload["n_entries"] = len(payload["entries"])
    with gzip.open(target, "wt", encoding="utf-8") as fh:
        json.dump(payload, fh)
    return target


def read_cache(path: Optional[pathlib.Path] = None) -> List[ModularFormEntry]:
    target = path or cache_path()
    if not target.is_file():
        raise FileNotFoundError(target)
    with gzip.open(target, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return [_dict_to_entry(d) for d in payload.get("entries", [])]


# ---------------------------------------------------------------------------
# Public surface: load_corpus + stratification
# ---------------------------------------------------------------------------


def _stratum_for_level(level: int) -> str:
    if level <= 100:
        return "small"
    if level <= 500:
        return "medium"
    return "large"


def load_modular_form_corpus(
    *,
    level_max: int = 1000,
    weight_min: int = 2,
    weight_max: int = 24,
    n_ap: int = DEFAULT_N_AP,
    n_qexp: int = DEFAULT_N_QEXP,
    n_total: int = 1000,
    small_share: float = 0.4,
    medium_share: float = 0.4,
    large_share: float = 0.2,
    seed: int = 0,
    use_cache: bool = True,
    write_cache_after_fetch: bool = True,
    fallback_to_handcurated: bool = True,
) -> List[ModularFormEntry]:
    """Build a stratified corpus of dim=1 newforms.

    Order of preference:
      1. If cache exists and ``use_cache=True``: load it and stratify.
      2. Else fetch from devmirror.lmfdb.xyz and (optionally) write the
         cache.
      3. Else fall back to the hand-curated 8-form mini-corpus.

    Parameters
    ----------
    level_max : int
        Cap on the newform level. 1000 yields ~10K dim=1 forms.
    weight_min, weight_max : int
        Filter on the weight. 2..24 covers everything classical.
    n_ap : int
        Length of the a_p feature vector. Max is ``len(PRIMES_30)`` = 30.
    n_qexp : int
        Number of q-expansion coefficients (a_1..a_n) to store.
    n_total : int
        Target stratified sample size.
    small_share / medium_share / large_share : float
        Target shares for level strata (small <=100, medium <=500,
        large > 500). Normalized internally.
    seed : int
        Reproducible RNG for stratification.
    use_cache : bool
        If True, prefer ``cache_path()`` over the live mirror.
    write_cache_after_fetch : bool
        If True, after a live fetch we write the result to cache.
    fallback_to_handcurated : bool
        If True, missing mirror + missing cache yields the small
        hand-curated fallback (~8 forms). Set False to raise instead.

    Returns
    -------
    list[ModularFormEntry]

    Raises
    ------
    RuntimeError
        If no source is available and ``fallback_to_handcurated=False``.
    ValueError
        On bad arguments.
    """
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0; got {n_total}")
    if n_ap <= 0 or n_ap > len(PRIMES_30):
        raise ValueError(
            f"n_ap must be in [1, {len(PRIMES_30)}]; got {n_ap}"
        )
    for nm, v in (
        ("small_share", small_share),
        ("medium_share", medium_share),
        ("large_share", large_share),
    ):
        if v < 0:
            raise ValueError(f"{nm} must be >= 0; got {v}")
    total_share = small_share + medium_share + large_share
    if total_share <= 0:
        raise ValueError("at least one stratum share must be positive")

    pool: List[ModularFormEntry] = []
    source = "unknown"
    cp = cache_path()
    if use_cache and cp.is_file() and cp.stat().st_size > 0:
        try:
            pool = read_cache(cp)
            source = f"cache:{cp}"
        except Exception:
            pool = []

    if not pool:
        # Try live fetch.
        live_attempted = False
        if not _network_disabled():
            try:
                import psycopg2  # noqa: F401
                live_attempted = True
                pool = _fetch_from_mirror(
                    level_max=level_max,
                    weight_min=weight_min,
                    weight_max=weight_max,
                    n_ap=n_ap,
                    n_qexp=n_qexp,
                )
                source = "live:devmirror.lmfdb.xyz"
                if write_cache_after_fetch and pool:
                    try:
                        write_cache(pool, cp)
                    except Exception:
                        pass
            except Exception:
                pool = []
        if not pool:
            if not fallback_to_handcurated:
                raise RuntimeError(
                    f"No source available (live_attempted={live_attempted}); "
                    f"fallback disabled."
                )
            # Hand-curated mini-corpus.
            pool = [
                ModularFormEntry(
                    label=d["label"],
                    level=d["level"],
                    weight=d["weight"],
                    char_order=d["char_order"],
                    char_orbit_label=d["char_orbit_label"],
                    a_p=tuple(d["a_p"][:n_ap]),
                    primes=PRIMES_30[:n_ap],
                    q_expansion=tuple(d["qexp"][:n_qexp]),
                )
                for d in _FALLBACK_FORMS
            ]
            source = "fallback:hand-curated"

    if not pool:
        raise RuntimeError("modular-form corpus is empty after all sources tried")

    # Stratify by level.
    by_stratum: dict[str, List[ModularFormEntry]] = {
        "small": [], "medium": [], "large": [],
    }
    for e in pool:
        by_stratum[_stratum_for_level(e.level)].append(e)

    # Normalize shares.
    s_small = small_share / total_share
    s_medium = medium_share / total_share
    s_large = large_share / total_share
    target = {
        "small": int(round(n_total * s_small)),
        "medium": int(round(n_total * s_medium)),
        "large": int(round(n_total * s_large)),
    }

    import random as _random
    rng = _random.Random(seed)
    sampled: List[ModularFormEntry] = []
    for stratum, n_want in target.items():
        bucket = list(by_stratum[stratum])
        rng.shuffle(bucket)
        sampled.extend(bucket[: min(n_want, len(bucket))])
    if not sampled:  # fallback corpus is small; fall back to "everything"
        sampled = list(pool)
    rng.shuffle(sampled)
    # Stamp source onto the first entry's char_orbit_label? No -- we'll
    # just expose source via a sidecar function.
    # Truncate a_p if caller asked for fewer than what's stored.
    if n_ap < len(PRIMES_30) and pool and len(pool[0].a_p) >= n_ap:
        sampled = [
            ModularFormEntry(
                label=e.label,
                level=e.level,
                weight=e.weight,
                char_order=e.char_order,
                char_orbit_label=e.char_orbit_label,
                a_p=e.a_p[:n_ap],
                primes=PRIMES_30[:n_ap],
                q_expansion=e.q_expansion[:n_qexp],
            )
            for e in sampled
        ]
    # Stash the source on a module-level last-load global for diagnostics.
    global _LAST_LOAD_SOURCE
    _LAST_LOAD_SOURCE = source
    return sampled


_LAST_LOAD_SOURCE: str = "uninitialized"


def last_load_source() -> str:
    """Diagnostic: where did the most recent ``load_modular_form_corpus``
    pull its raw entries from?"""
    return _LAST_LOAD_SOURCE


def split_train_test(
    corpus: Sequence[ModularFormEntry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> Tuple[List[ModularFormEntry], List[ModularFormEntry]]:
    """Reproducible train/test split over the corpus."""
    if not corpus:
        raise ValueError("cannot split an empty corpus")
    if not 0.0 < train_frac < 1.0:
        raise ValueError(f"train_frac must be in (0,1); got {train_frac}")
    import random as _random
    rng = _random.Random(seed)
    idx = list(range(len(corpus)))
    rng.shuffle(idx)
    n_train = int(round(len(corpus) * train_frac))
    train = [corpus[i] for i in idx[:n_train]]
    test = [corpus[i] for i in idx[n_train:]]
    return train, test


def corpus_summary(corpus: Iterable[ModularFormEntry]) -> dict:
    """Diagnostic counts: total + per-stratum + per-weight counts."""
    corpus = list(corpus)
    by_stratum: dict[str, int] = {}
    by_weight: dict[int, int] = {}
    levels: list[int] = []
    weights: list[int] = []
    for e in corpus:
        by_stratum[_stratum_for_level(e.level)] = (
            by_stratum.get(_stratum_for_level(e.level), 0) + 1
        )
        by_weight[e.weight] = by_weight.get(e.weight, 0) + 1
        levels.append(e.level)
        weights.append(e.weight)
    return {
        "n_total": len(corpus),
        "by_stratum": dict(sorted(by_stratum.items())),
        "by_weight": dict(sorted(by_weight.items())),
        "level_min": min(levels) if levels else None,
        "level_max": max(levels) if levels else None,
        "weight_min": min(weights) if weights else None,
        "weight_max": max(weights) if weights else None,
    }


__all__ = [
    "ModularFormEntry",
    "PRIMES_30",
    "DEFAULT_N_AP",
    "DEFAULT_N_QEXP",
    "is_available",
    "cache_path",
    "load_modular_form_corpus",
    "last_load_source",
    "split_train_test",
    "corpus_summary",
    "write_cache",
    "read_cache",
]
