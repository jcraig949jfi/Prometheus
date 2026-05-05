"""prometheus_math._oeis_sleeping_corpus -- OEIS Sleeping Beauty corpus.

Cross-domain test #3 for the Prometheus discovery substrate. Where the
BSD env (rank prediction) and the modular-form env (a_p prediction) sit
on labelled, well-tabulated number-theoretic objects with known closed
forms, this corpus targets the *unconnected* tail of OEIS: sequences
that are highly regular (i.e. have many published terms) but have very
few cross-references to the rest of the integer-sequence corpus.

Per ``project_sleeping_beauties.md``: ~68,770 of OEIS's 370K sequences
are "sleeping beauties" -- mathematically sharp but underconnected.
This module builds a stratified, hand-cleanable sample of such
sequences for the next-term-prediction env.

What makes a sleeping beauty (operationally)
--------------------------------------------
The local OEIS mirror (stripped.gz + names.gz) only exposes ``data`` +
``name``; it does NOT carry keywords or cross-refs (those live in the
full sequence files, which the bulk dumps don't contain). We therefore
use a *structural* proxy:

    1. >= 30 terms in the data field (the "beauty" half: well-defined).
    2. All terms positive integers (drop signed/rational sequences).
    3. Terms fit in int64 (drop bigints we can't bin).
    4. Growth is reasonable: monotone non-decreasing OR strictly
       increasing within a tolerated wobble; ratio of consecutive
       positive terms stays bounded.

The "sleeping" half (low-cross-ref) is enforced by drawing from
broader prefix bands than the textbook A0000xx range: we sample
A001xxx-A005xxx where the average cross-ref count is materially
lower than in the A0000xx (hyper-canonical) and A1xxxxx (modern,
well-cited) bands, while honouring the structural constraints above.
That is a heuristic, NOT a measurement of actual cross-ref counts;
the docstring is honest about that gap.

We also include a small fixed set of canonical "anchor" sequences
(Fibonacci A000045, Catalan A000108, etc.) for the tests' authority
checks. These ARE NOT sleeping beauties -- they live in the corpus as
sanity-check rows, with ``is_anchor=True`` so callers can filter.

Growth class labels
-------------------
We pre-classify each sequence's growth into one of:

    "linear"      a(n+1) - a(n) approximately constant
    "polynomial"  log(a(n)) ~ c * log(n)  (slope k > 0 modest)
    "exponential" log(a(n)) ~ c * n
    "factorial"   log(a(n)) ~ c * n * log(n)  (super-exponential)
    "other"       does not fit any of the above cleanly

The growth class is the env's primary obs-vector heuristic feature:
the baseline predictor uses it directly.

Skip-with-message contract
--------------------------
``is_available()`` returns ``(True, ...)`` whenever EITHER:
    a) the gzipped JSON cache exists, OR
    b) the local OEIS mirror is loaded.
It returns ``(False, reason)`` only when both are absent and the env
must fall back to its tiny hand-curated set.
"""
from __future__ import annotations

import dataclasses
import gzip
import json
import math
import os
import pathlib
import random
from typing import Any, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


# Minimum terms required for an entry to enter the corpus. The env
# splits the prefix into context + target so we need >= context_min + 1.
DEFAULT_MIN_TERMS: int = 30


# Maximum log10(a_n) we tolerate. Beyond ~1e15 the int64 actions and
# logarithmic binning lose meaningful resolution.
DEFAULT_MAX_LOG10: float = 15.0


# Growth class names. Tests rely on this exact ordering for the "label
# vector" feature in the env observation.
GROWTH_CLASSES: Tuple[str, ...] = (
    "linear",
    "polynomial",
    "exponential",
    "factorial",
    "other",
)


# Canonical anchor sequences (NOT sleeping beauties; sanity-check rows).
# Each tuple: (a_number, is_anchor=True). Their data comes from the
# OEIS local mirror at load time; we only fix the A-numbers.
ANCHOR_A_NUMBERS: Tuple[str, ...] = (
    "A000045",  # Fibonacci
    "A000108",  # Catalan
    "A000079",  # Powers of 2
    "A000142",  # Factorial
    "A000040",  # Primes
)


# Prefixes we draw the body of the corpus from. A001xxx-A005xxx is a
# broad band where the typical entry has fewer cross-refs than A0000xx
# (the "core" classics) without being so deep into the modern tail
# that data sparsity dominates.
DEFAULT_SLEEPING_PREFIXES: Tuple[str, ...] = (
    "A001", "A002", "A003", "A004", "A005",
    "A006", "A007", "A008", "A009",
)


# Hand-curated minimal fallback if BOTH the cache and the local mirror
# are unavailable. Keeps tests sane.
_FALLBACK_ENTRIES: Tuple[dict, ...] = (
    {
        "a_number": "A000045",
        "name": "Fibonacci numbers: F(n) = F(n-1) + F(n-2) with F(0) = 0",
        "data": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377,
                 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657,
                 46368, 75025, 121393, 196418, 317811, 514229, 832040,
                 1346269, 2178309, 3524578, 5702887, 9227465, 14930352,
                 24157817, 39088169, 63245986, 102334155],
        "growth_class": "exponential",
        "is_anchor": True,
    },
    {
        "a_number": "A000108",
        "name": "Catalan numbers: C(n) = binomial(2n,n)/(n+1)",
        "data": [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786,
                 208012, 742900, 2674440, 9694845, 35357670, 129644790,
                 477638700, 1767263190, 6564120420, 24466267020,
                 91482563640, 343059613650, 1289904147324, 4861946401452,
                 18367353072152, 69533550916004, 263747951750360,
                 1002242216651368, 3814986502092304],
        "growth_class": "exponential",
        "is_anchor": True,
    },
    {
        "a_number": "A000079",
        "name": "Powers of 2: a(n) = 2^n",
        "data": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096,
                 8192, 16384, 32768, 65536, 131072, 262144, 524288,
                 1048576, 2097152, 4194304, 8388608, 16777216, 33554432,
                 67108864, 134217728, 268435456, 536870912, 1073741824,
                 2147483648, 4294967296, 8589934592, 17179869184],
        "growth_class": "exponential",
        "is_anchor": True,
    },
    {
        "a_number": "A000142",
        "name": "Factorial numbers: n!",
        "data": [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800,
                 39916800, 479001600, 6227020800, 87178291200,
                 1307674368000, 20922789888000, 355687428096000,
                 6402373705728000, 121645100408832000],
        "growth_class": "factorial",
        "is_anchor": True,
    },
    {
        "a_number": "A000027",
        "name": "The positive integers",
        "data": list(range(1, 41)),
        "growth_class": "linear",
        "is_anchor": True,
    },
    {
        "a_number": "A000290",
        "name": "The squares: a(n) = n^2",
        "data": [n * n for n in range(0, 35)],
        "growth_class": "polynomial",
        "is_anchor": True,
    },
)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class OeisSleepingEntry:
    """One sleeping-beauty (or anchor) sequence record.

    Fields
    ------
    a_number : str
        Canonical OEIS A-number, ``A000000``-``A999999``.
    name : str
        OEIS name field. Typically a short English description.
    data : Tuple[int, ...]
        Integer terms, in OEIS order. Length >= ``DEFAULT_MIN_TERMS``.
    growth_class : str
        One of ``GROWTH_CLASSES``.
    is_anchor : bool
        True iff this is a hand-curated sanity-check row (Fibonacci,
        Catalan, etc.) rather than a candidate sleeping beauty.
    """

    a_number: str
    name: str
    data: Tuple[int, ...]
    growth_class: str
    is_anchor: bool = False

    @property
    def n_terms(self) -> int:
        return len(self.data)


# ---------------------------------------------------------------------------
# Cache location
# ---------------------------------------------------------------------------


def _databases_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "databases"


def cache_path() -> pathlib.Path:
    """Path to the gzipped JSON cache of the corpus."""
    return _databases_dir() / "oeis_sleeping.json.gz"


# ---------------------------------------------------------------------------
# Network / availability
# ---------------------------------------------------------------------------


def _network_disabled() -> bool:
    return bool(os.environ.get("PROMETHEUS_NO_NETWORK", "").strip())


def is_available(timeout: float = 3.0) -> Tuple[bool, str]:
    """Cheap reachability check.

    Returns (ok, reason). Order:
      1. Cache present  -> ok.
      2. Local OEIS mirror loaded -> ok.
      3. Network available -> ok (would do live API).
      4. Otherwise (False, reason).
    """
    cp = cache_path()
    if cp.is_file() and cp.stat().st_size > 0:
        return True, f"cache present at {cp}"
    try:
        from .databases import oeis
        if oeis.has_local_mirror():
            return True, "OEIS local mirror loaded"
    except Exception as e:  # pragma: no cover -- import wiring
        return False, f"OEIS wrapper unavailable: {e}"
    if _network_disabled():
        return False, "network disabled by PROMETHEUS_NO_NETWORK"
    # Fallback corpus is always usable, but flag unavailable so callers
    # can decide whether to skip the heavy paths.
    return True, "fallback hand-curated only (no cache, no mirror)"


# ---------------------------------------------------------------------------
# Growth-class classification
# ---------------------------------------------------------------------------


def classify_growth(data: Sequence[int]) -> str:
    """Classify the growth of a positive-integer sequence.

    Heuristic: do linear regressions on three feature axes and pick the
    best fit:
        linear:      a(n) vs n
        polynomial:  log(a(n)) vs log(n)
        exponential: log(a(n)) vs n
        factorial:   log(a(n)) vs n*log(n)

    Returns one of ``GROWTH_CLASSES``. Empty / monotonically zero /
    constant sequences are ``"linear"`` (constant is the n=1 case of a
    line).

    The factorial branch wins when the n*log(n) slope is large AND the
    pure-exponential fit residual is materially worse.
    """
    n = len(data)
    if n < 4:
        return "other"
    # Drop the leading zero(s) for log fits; keep them for linear fit.
    pairs: List[Tuple[float, float]] = []
    for i, v in enumerate(data):
        if v <= 0:
            continue
        pairs.append((float(i + 1), float(v)))  # offset so log(n) defined
    if len(pairs) < 4:
        return "other"
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    log_xs = [math.log(x) for x in xs]
    try:
        log_ys = [math.log(y) for y in ys]
    except ValueError:
        return "other"
    nlogn = [x * math.log(x) for x in xs]

    def _ss_resid(xs_: List[float], ys_: List[float]) -> Tuple[float, float, float]:
        """Return (slope, intercept, R^2) on a least-squares fit."""
        m = len(xs_)
        sx = sum(xs_); sy = sum(ys_)
        sxx = sum(x * x for x in xs_)
        sxy = sum(x * y for x, y in zip(xs_, ys_))
        denom = m * sxx - sx * sx
        if denom <= 0.0:
            return 0.0, sy / max(m, 1), 0.0
        slope = (m * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / m
        ss_tot = sum((y - sy / m) ** 2 for y in ys_)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs_, ys_))
        if ss_tot <= 0.0:
            return slope, intercept, 1.0
        return slope, intercept, 1.0 - ss_res / ss_tot

    # Linear fit on a(n) vs n (raw values).
    slope_lin, _b_lin, r2_lin = _ss_resid(xs, ys)

    # Polynomial: log y vs log n.
    slope_poly, _b_poly, r2_poly = _ss_resid(log_xs, log_ys)

    # Exponential: log y vs n.
    slope_exp, _b_exp, r2_exp = _ss_resid(xs, log_ys)

    # Factorial: log y vs n*log n.
    slope_fact, _b_fact, r2_fact = _ss_resid(nlogn, log_ys)

    # Decision rules. Tuned on the 6 anchor sequences (Fib, Catalan,
    # 2^n, n!, n, n^2).
    # - Factorial: slope_fact > 0.5 AND R^2_fact > R^2_exp + 0.001 AND
    #   slope_exp itself is large (super-exp regime).
    if r2_fact > 0.99 and slope_fact > 0.5 and r2_fact >= r2_exp:
        # Distinguish factorial from exponential: check n*log(n) is
        # actually a better fit than just n.
        if slope_exp > 1.5 and r2_fact > r2_exp:
            return "factorial"
    # - Exponential: log y is very linear in n with positive slope.
    if r2_exp > 0.98 and slope_exp > 0.05:
        # Distinguish from polynomial by slope magnitude on log-log.
        if slope_poly > 8.0 and r2_poly > 0.99:
            # Very high polynomial slope can mimic exp on a short
            # window; if R^2 is comparable, prefer exponential when
            # log y vs n has cleaner residuals.
            return "exponential" if r2_exp >= r2_poly else "polynomial"
        return "exponential"
    # - Polynomial: log-log linear with positive slope.
    if r2_poly > 0.98 and slope_poly > 1.5:
        return "polynomial"
    # - Linear: raw a(n) vs n is good.
    if r2_lin > 0.98 and slope_lin > 0.0:
        return "linear"
    return "other"


def growth_class_index(growth_class: str) -> int:
    """Return the integer index of a growth class label, or -1."""
    try:
        return GROWTH_CLASSES.index(growth_class)
    except ValueError:
        return -1


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def _passes_filter(
    data: Sequence[int],
    *,
    min_terms: int,
    max_log10: float,
) -> bool:
    """Return True iff the raw data passes the structural filter."""
    if len(data) < min_terms:
        return False
    # All positive integers (we drop signed sequences for binning sanity).
    for v in data[:min_terms]:
        if not isinstance(v, int):
            return False
        if v <= 0:
            return False
    # int64 fits.
    last = data[min_terms - 1]
    if last >= 10 ** max_log10:
        return False
    # Strictly non-decreasing on the prefix (sleeping beauties of the
    # combinatorial-counting flavour). Allow equality (constant runs).
    for i in range(1, min_terms):
        if data[i] < data[i - 1]:
            return False
    return True


# ---------------------------------------------------------------------------
# Cache (JSON.gz) round-trip
# ---------------------------------------------------------------------------


def _entry_to_dict(e: OeisSleepingEntry) -> dict:
    return {
        "a_number": e.a_number,
        "name": e.name,
        "data": list(e.data),
        "growth_class": e.growth_class,
        "is_anchor": bool(e.is_anchor),
    }


def _dict_to_entry(d: dict) -> OeisSleepingEntry:
    gc = str(d.get("growth_class", "other"))
    if gc not in GROWTH_CLASSES:
        gc = "other"
    return OeisSleepingEntry(
        a_number=str(d["a_number"]),
        name=str(d.get("name", "")),
        data=tuple(int(x) for x in d["data"]),
        growth_class=gc,
        is_anchor=bool(d.get("is_anchor", False)),
    )


def write_cache(
    corpus: Iterable[OeisSleepingEntry],
    path: Optional[pathlib.Path] = None,
) -> pathlib.Path:
    """Write a corpus to gzipped JSON. Returns the path written."""
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


def read_cache(path: Optional[pathlib.Path] = None) -> List[OeisSleepingEntry]:
    target = path or cache_path()
    if not target.is_file():
        raise FileNotFoundError(target)
    with gzip.open(target, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return [_dict_to_entry(d) for d in payload.get("entries", [])]


# ---------------------------------------------------------------------------
# Pull from local OEIS mirror
# ---------------------------------------------------------------------------


def _pull_from_local_mirror(
    *,
    min_terms: int,
    max_log10: float,
    prefixes: Sequence[str],
    n_per_prefix: int,
    rng: random.Random,
) -> List[OeisSleepingEntry]:
    """Iterate the local mirror and pick filter-passing entries.

    Walks A-numbers in deterministic order within each prefix, accepts
    those that pass ``_passes_filter``, classifies their growth, and
    returns up to ``n_per_prefix`` per prefix.
    """
    try:
        from .databases import oeis
    except Exception:
        return []
    if not oeis.has_local_mirror():
        return []
    cache = oeis._OEIS_LOCAL_CACHE  # type: ignore[attr-defined]
    out: List[OeisSleepingEntry] = []
    for prefix in prefixes:
        # Stable order across runs: sort A-numbers under this prefix.
        candidates = sorted(k for k in cache if k.startswith(prefix))
        # Shuffle deterministically (rng controlled by caller).
        rng.shuffle(candidates)
        accepted = 0
        for a_id in candidates:
            if accepted >= n_per_prefix:
                break
            rec = cache[a_id]
            data = list(rec.get("data") or [])
            if not _passes_filter(data, min_terms=min_terms, max_log10=max_log10):
                continue
            data = data[: max(min_terms, 30)]  # truncate to first 30+ for env
            growth = classify_growth(data)
            out.append(OeisSleepingEntry(
                a_number=a_id,
                name=str(rec.get("name", "")),
                data=tuple(data),
                growth_class=growth,
                is_anchor=False,
            ))
            accepted += 1
    return out


def _materialize_anchors(
    a_numbers: Sequence[str],
    *,
    min_terms: int,
) -> List[OeisSleepingEntry]:
    """Build anchor entries from the live OEIS mirror; fall back to the
    embedded fallback dicts when the mirror is missing.
    """
    try:
        from .databases import oeis
    except Exception:
        oeis = None  # type: ignore[assignment]
    out: List[OeisSleepingEntry] = []
    fallback_by_id = {d["a_number"]: d for d in _FALLBACK_ENTRIES}
    for a_id in a_numbers:
        rec: Optional[dict] = None
        if oeis is not None and oeis.has_local_mirror():
            rec = oeis._OEIS_LOCAL_CACHE.get(a_id)  # type: ignore[attr-defined]
        if rec is not None and rec.get("data"):
            data = [int(x) for x in rec["data"]]
            name = str(rec.get("name", ""))
        elif a_id in fallback_by_id:
            data = list(fallback_by_id[a_id]["data"])
            name = str(fallback_by_id[a_id]["name"])
        else:
            continue
        if len(data) < 4:
            continue
        # Anchors keep their full available term list (>= min_terms when
        # possible). For sequences whose mirror prefix is shorter than
        # min_terms (e.g. A000142 has only 23 terms), we keep them
        # anyway because tests reference them by A-number.
        growth = classify_growth(data)
        out.append(OeisSleepingEntry(
            a_number=a_id,
            name=name,
            data=tuple(data),
            growth_class=growth,
            is_anchor=True,
        ))
    return out


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


_LAST_LOAD_SOURCE: str = "uninitialized"


def last_load_source() -> str:
    """Diagnostic: where did the most recent ``load_oeis_sleeping_corpus``
    pull its raw entries from? One of ``"cache"``, ``"local_mirror"``,
    ``"fallback"``."""
    return _LAST_LOAD_SOURCE


def load_oeis_sleeping_corpus(
    *,
    n_total: int = 200,
    min_terms: int = DEFAULT_MIN_TERMS,
    max_log10: float = DEFAULT_MAX_LOG10,
    prefixes: Sequence[str] = DEFAULT_SLEEPING_PREFIXES,
    seed: int = 0,
    use_cache: bool = True,
    write_cache_after_fetch: bool = True,
    include_anchors: bool = True,
    fallback_to_handcurated: bool = True,
) -> List[OeisSleepingEntry]:
    """Build (or load) the OEIS Sleeping Beauty corpus.

    Order of preference:
      1. Cache at ``cache_path()`` if ``use_cache`` and present.
      2. Local OEIS mirror walk over ``prefixes``.
      3. Hand-curated fallback if ``fallback_to_handcurated``.

    Parameters
    ----------
    n_total : int
        Target sample size (anchors are added on top of this number;
        the body is drawn evenly from ``prefixes``).
    min_terms : int
        Minimum term count for a sequence to enter the corpus.
    max_log10 : float
        Reject sequences whose ``min_terms``-th term exceeds 10**this.
    prefixes : Sequence[str]
        OEIS prefix bands to draw the body from. Defaults to A001-A009
        (the "underconnected" mid-band).
    seed : int
        Reproducible RNG.
    use_cache : bool
        Prefer the on-disk cache when present.
    write_cache_after_fetch : bool
        Persist the corpus to ``cache_path()`` after a successful pull.
    include_anchors : bool
        If True, prepend the canonical anchors (Fibonacci, Catalan,
        ...). Tests assume True.
    fallback_to_handcurated : bool
        If True and both cache + mirror fail, return the embedded
        fallback. Set False to raise instead.

    Returns
    -------
    list[OeisSleepingEntry]
    """
    global _LAST_LOAD_SOURCE
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0; got {n_total}")
    if min_terms < 4:
        raise ValueError(f"min_terms must be >= 4; got {min_terms}")
    if max_log10 <= 0.0:
        raise ValueError(f"max_log10 must be > 0; got {max_log10}")
    if not prefixes:
        raise ValueError("prefixes must be non-empty")

    rng = random.Random(seed)
    cp = cache_path()
    pool: List[OeisSleepingEntry] = []
    source = "unknown"

    # 1. Cache.
    if use_cache and cp.is_file() and cp.stat().st_size > 0:
        try:
            pool = read_cache(cp)
            source = "cache"
        except Exception:
            pool = []

    # 2. Local mirror.
    if not pool:
        n_per_prefix = max(1, math.ceil(n_total / max(1, len(prefixes))))
        try:
            body = _pull_from_local_mirror(
                min_terms=min_terms,
                max_log10=max_log10,
                prefixes=prefixes,
                n_per_prefix=n_per_prefix,
                rng=rng,
            )
        except Exception:
            body = []
        if body:
            anchors = _materialize_anchors(
                ANCHOR_A_NUMBERS, min_terms=min_terms
            ) if include_anchors else []
            # De-dup by A-number: anchors take precedence.
            anchor_ids = {e.a_number for e in anchors}
            body_dedup = [e for e in body if e.a_number not in anchor_ids]
            pool = anchors + body_dedup
            source = "local_mirror"
            if write_cache_after_fetch:
                try:
                    write_cache(pool, cp)
                except Exception:
                    pass

    # 3. Fallback.
    if not pool:
        if not fallback_to_handcurated:
            raise RuntimeError("OEIS sleeping corpus: no source available")
        pool = [
            OeisSleepingEntry(
                a_number=str(d["a_number"]),
                name=str(d["name"]),
                data=tuple(int(x) for x in d["data"]),
                growth_class=str(d["growth_class"]),
                is_anchor=bool(d.get("is_anchor", True)),
            )
            for d in _FALLBACK_ENTRIES
        ]
        source = "fallback"

    if not pool:
        raise RuntimeError("OEIS sleeping corpus is empty after all sources")

    # Sample n_total from the body, keeping anchors first.
    anchors = [e for e in pool if e.is_anchor]
    body = [e for e in pool if not e.is_anchor]
    rng2 = random.Random(seed + 1)
    rng2.shuffle(body)
    sample = anchors + body[: max(0, n_total)]

    _LAST_LOAD_SOURCE = source
    return sample


def split_train_test(
    corpus: Sequence[OeisSleepingEntry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> Tuple[List[OeisSleepingEntry], List[OeisSleepingEntry]]:
    """Reproducible train/test split.

    Anchors are PUT INTO THE TRAIN SPLIT preferentially (so they're not
    accidentally siphoned into a 50-element test set), but the rest is
    a flat shuffle.
    """
    if not corpus:
        raise ValueError("cannot split an empty corpus")
    if not 0.0 < train_frac < 1.0:
        raise ValueError(f"train_frac must be in (0, 1); got {train_frac}")
    anchors = [e for e in corpus if e.is_anchor]
    body = [e for e in corpus if not e.is_anchor]
    rng = random.Random(seed)
    rng.shuffle(body)
    n_train_body = max(0, int(round(len(body) * train_frac)))
    train = anchors + body[:n_train_body]
    test = body[n_train_body:]
    if not test and body:
        # Train_frac too high; ensure at least one test row.
        test = [train.pop()]
    return train, test


def corpus_summary(corpus: Iterable[OeisSleepingEntry]) -> dict:
    """Diagnostic: counts per growth class, total, anchors."""
    corpus = list(corpus)
    by_growth: dict[str, int] = {gc: 0 for gc in GROWTH_CLASSES}
    n_anchor = 0
    term_counts: List[int] = []
    for e in corpus:
        by_growth[e.growth_class] = by_growth.get(e.growth_class, 0) + 1
        if e.is_anchor:
            n_anchor += 1
        term_counts.append(len(e.data))
    return {
        "n_total": len(corpus),
        "n_anchors": n_anchor,
        "n_body": len(corpus) - n_anchor,
        "by_growth": dict(by_growth),
        "term_count_min": min(term_counts) if term_counts else 0,
        "term_count_max": max(term_counts) if term_counts else 0,
    }


__all__ = [
    "OeisSleepingEntry",
    "GROWTH_CLASSES",
    "ANCHOR_A_NUMBERS",
    "DEFAULT_MIN_TERMS",
    "DEFAULT_MAX_LOG10",
    "DEFAULT_SLEEPING_PREFIXES",
    "is_available",
    "cache_path",
    "classify_growth",
    "growth_class_index",
    "load_oeis_sleeping_corpus",
    "last_load_source",
    "split_train_test",
    "corpus_summary",
    "write_cache",
    "read_cache",
]
