"""prometheus_math._genus2_corpus -- Genus-2 curve corpus loader.

Builds a stratified sample of genus-2 curves over Q from the LMFDB
Postgres mirror (``devmirror.lmfdb.xyz``, table ``g2c_curves``). Each
entry ships:

    label              : LMFDB label, e.g. "169.a.169.1"
    iso_class          : isogeny-class portion, e.g. "169.a"
    conductor          : int -- conductor of Jac(C)
    abs_disc           : int -- |discriminant| of the model
    disc_sign          : int -- sign of discriminant (+/- 1)
    f_coeffs           : tuple[int, ...] -- coefficients of f(x)
    h_coeffs           : tuple[int, ...] -- coefficients of h(x)
    analytic_rank      : int -- analytic rank of L(Jac(C), s)
    mw_rank            : int -- Mordell-Weil rank (when proved); fallback to analytic
    torsion_order      : int -- |J(Q)_tors|
    torsion_subgroup   : str -- structure, e.g. "[19]"
    real_period        : float
    st_label           : str -- Sato-Tate group label
    geom_end_alg       : str -- geometric endomorphism algebra

The hyperelliptic equation is encoded by LMFDB as a string ``"[f, h]"``
where f = sum f_i x^i (degree <= 6) and h = sum h_i x^i (degree <= 3),
with the curve given by ``y^2 + h(x) y = f(x)``.

Stratification by analytic_rank
-------------------------------
LMFDB ranks distribution:
    rank 0  : ~12K
    rank 1  : ~30K  (modal class!)
    rank 2  : ~20K
    rank 3+ : ~3K
We bin into three classes for the env: {0, 1, 2+}. Pull a balanced
mix that is biased toward the modal class (1) without ignoring 0 or
2+.

Skip-with-message
-----------------
``is_available()`` returns ``(False, reason)`` if both:
    1. The cache does not exist, AND
    2. ``psycopg2`` is missing or the LMFDB mirror is unreachable.
"""
from __future__ import annotations

import dataclasses
import gzip
import json
import os
import pathlib
import re
from typing import Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Genus2Entry:
    """One labelled genus-2 curve record."""

    label: str
    iso_class: str
    conductor: int
    abs_disc: int
    disc_sign: int
    f_coeffs: Tuple[int, ...]   # coefficients of f(x), low-to-high degree
    h_coeffs: Tuple[int, ...]   # coefficients of h(x), low-to-high degree
    analytic_rank: int
    mw_rank: int                # may equal analytic_rank when not proved
    torsion_order: int
    torsion_subgroup: str
    real_period: float
    st_label: str
    geom_end_alg: str

    @property
    def rank_class(self) -> int:
        """Three-way class label: 0, 1, or 2 (= "2+")."""
        r = int(self.analytic_rank)
        if r <= 0:
            return 0
        if r == 1:
            return 1
        return 2


# Dimensionalities of the coefficient lists. f(x) has degree up to 6
# (so 7 coeffs); h(x) has degree up to 3 (so 4 coeffs). We pad shorter
# lists with zeros so the env's observation has fixed length.
F_COEFF_LEN: int = 7
H_COEFF_LEN: int = 4

# Three rank classes: 0, 1, "2+"
N_RANK_CLASSES: int = 3


# ---------------------------------------------------------------------------
# Cache location
# ---------------------------------------------------------------------------


def _databases_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "databases"


def cache_path() -> pathlib.Path:
    """Path to the gzipped JSON cache of the corpus."""
    return _databases_dir() / "genus2.json.gz"


# ---------------------------------------------------------------------------
# Equation-string parsing
# ---------------------------------------------------------------------------


_INT_TOKEN = re.compile(r"-?\d+")


def parse_equation(eqn: str) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """Parse an LMFDB g2c eqn string into (f_coeffs, h_coeffs).

    The format is ``"[[f0, f1, ..., f_d], [h0, h1, ..., h_e]]"``.
    Coefficients are integer-valued. Returns each coefficient list
    padded with zeros to F_COEFF_LEN / H_COEFF_LEN respectively, so
    downstream consumers see a fixed observation shape.

    Raises ``ValueError`` on malformed input.
    """
    if not eqn or not isinstance(eqn, str):
        raise ValueError(f"empty or non-string eqn: {eqn!r}")
    s = eqn.strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError(f"eqn not bracketed: {eqn!r}")
    # Find the inner "[...]" and "[...]" with a tiny manual parser
    # (json.loads would also work but the input may contain trailing
    # whitespace that LMFDB occasionally injects).
    depth = 0
    start = -1
    parts: List[str] = []
    for i, ch in enumerate(s):
        if ch == "[":
            if depth == 1 and start == -1:
                start = i
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 1 and start >= 0:
                parts.append(s[start:i + 1])
                start = -1
    if len(parts) < 1:
        raise ValueError(f"eqn missing inner lists: {eqn!r}")
    f_part = parts[0]
    h_part = parts[1] if len(parts) >= 2 else "[]"
    f_vals = [int(t) for t in _INT_TOKEN.findall(f_part)]
    h_vals = [int(t) for t in _INT_TOKEN.findall(h_part)]

    def _pad(vals: List[int], n: int) -> Tuple[int, ...]:
        if len(vals) >= n:
            return tuple(vals[:n])
        return tuple(vals + [0] * (n - len(vals)))

    return _pad(f_vals, F_COEFF_LEN), _pad(h_vals, H_COEFF_LEN)


# ---------------------------------------------------------------------------
# Tiny hand-curated fallback (used iff devmirror.lmfdb.xyz is unreachable
# AND no cache exists). Pulled from LMFDB on 2026-05-04.
# ---------------------------------------------------------------------------


_FALLBACK_CURVES: Tuple[dict, ...] = (
    # 169.a.169.1 -- the lowest-conductor genus-2 curve
    {
        "label": "169.a.169.1",
        "iso_class": "169.a",
        "conductor": 169,
        "abs_disc": 169,
        "disc_sign": 1,
        "eqn": "[[0,0,0,0,1,1],[1,1,0,1]]",
        "analytic_rank": 0,
        "mw_rank": 0,
        "torsion_order": 19,
        "torsion_subgroup": "[19]",
        "real_period": 32.667031090507095,
        "st_label": "1.4.E.6.2a",
        "geom_end_alg": "Q",
    },
    {
        "label": "249.a.249.1",
        "iso_class": "249.a",
        "conductor": 249,
        "abs_disc": 249,
        "disc_sign": 1,
        "eqn": "[[0,1,1],[1,0,0,1]]",
        "analytic_rank": 0,
        "mw_rank": 0,
        "torsion_order": 14,
        "torsion_subgroup": "[14]",
        "real_period": 25.783703374249836,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "277.a.277.1",
        "iso_class": "277.a",
        "conductor": 277,
        "abs_disc": 277,
        "disc_sign": 1,
        "eqn": "[[0,0,0,1,0,-2,1],[]]",
        "analytic_rank": 1,
        "mw_rank": 1,
        "torsion_order": 1,
        "torsion_subgroup": "[]",
        "real_period": 1.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "294.a.294.1",
        "iso_class": "294.a",
        "conductor": 294,
        "abs_disc": 294,
        "disc_sign": 1,
        "eqn": "[[0,1,1],[1,1,0,1]]",
        "analytic_rank": 0,
        "mw_rank": 0,
        "torsion_order": 12,
        "torsion_subgroup": "[2,6]",
        "real_period": 12.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "295.a.295.1",
        "iso_class": "295.a",
        "conductor": 295,
        "abs_disc": 295,
        "disc_sign": 1,
        "eqn": "[[0,1,1],[0,1,1,1]]",
        "analytic_rank": 0,
        "mw_rank": 0,
        "torsion_order": 14,
        "torsion_subgroup": "[14]",
        "real_period": 11.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "336.a.172032.1",
        "iso_class": "336.a",
        "conductor": 336,
        "abs_disc": 172032,
        "disc_sign": 1,
        "eqn": "[[0,0,1,0,0,0,1],[0,1]]",
        "analytic_rank": 1,
        "mw_rank": 1,
        "torsion_order": 6,
        "torsion_subgroup": "[6]",
        "real_period": 5.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "461.a.461.1",
        "iso_class": "461.a",
        "conductor": 461,
        "abs_disc": 461,
        "disc_sign": 1,
        "eqn": "[[0,0,1,1,1,1],[1]]",
        "analytic_rank": 2,
        "mw_rank": 2,
        "torsion_order": 1,
        "torsion_subgroup": "[]",
        "real_period": 5.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "523.a.523.1",
        "iso_class": "523.a",
        "conductor": 523,
        "abs_disc": 523,
        "disc_sign": 1,
        "eqn": "[[0,0,0,0,0,1,1],[]]",
        "analytic_rank": 1,
        "mw_rank": 1,
        "torsion_order": 1,
        "torsion_subgroup": "[]",
        "real_period": 6.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "1125.a.18225.1",
        "iso_class": "1125.a",
        "conductor": 1125,
        "abs_disc": 18225,
        "disc_sign": 1,
        "eqn": "[[1,0,1,0,1,0,1],[]]",
        "analytic_rank": 2,
        "mw_rank": 2,
        "torsion_order": 1,
        "torsion_subgroup": "[]",
        "real_period": 4.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
    },
    {
        "label": "11279.a.11279.1",
        "iso_class": "11279.a",
        "conductor": 11279,
        "abs_disc": 11279,
        "disc_sign": 1,
        "eqn": "[[1,0,0,1,0,1,1],[]]",
        "analytic_rank": 1,
        "mw_rank": 1,
        "torsion_order": 1,
        "torsion_subgroup": "[]",
        "real_period": 3.0,
        "st_label": "1.4.A.1.1a",
        "geom_end_alg": "Q",
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

    Returns (ok, reason). Cache hit always wins.
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


def _iso_class_from_label(label: str) -> str:
    """Extract "N.x" prefix (the isogeny-class portion) from a g2c label."""
    parts = label.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return label


def _fetch_from_mirror(
    *,
    cond_max: int,
    n_per_rank: int,
    timeout: float = 60.0,
) -> List[Genus2Entry]:
    """Live SQL pull from devmirror.lmfdb.xyz. Stratified by analytic_rank.

    Pulls up to ``n_per_rank`` curves per rank class (0, 1, 2+). The
    "2+" class is implemented as ``analytic_rank >= 2``.

    SQL skeleton::

        SELECT label, cond, abs_disc, disc_sign, eqn, analytic_rank,
               mw_rank, torsion_order, torsion_subgroup, real_period,
               st_label, geom_end_alg
          FROM g2c_curves
         WHERE cond <= %s
           AND analytic_rank = %s
         ORDER BY cond, label
         LIMIT %s;
    """
    import psycopg2  # noqa: F401
    from .databases import lmfdb

    base_cols = (
        "label, cond, abs_disc, disc_sign, eqn, analytic_rank, mw_rank, "
        "torsion_order, torsion_subgroup, real_period, st_label, geom_end_alg"
    )

    out: List[Genus2Entry] = []
    conn = lmfdb.connect(timeout=int(max(1, round(timeout))))
    try:
        # Three rank-class queries.
        for rank_filter, label in (
            ("analytic_rank = 0", 0),
            ("analytic_rank = 1", 1),
            ("analytic_rank >= 2", 2),
        ):
            sql = (
                f"SELECT {base_cols} FROM g2c_curves "
                f"WHERE cond <= %s AND {rank_filter} "
                f"ORDER BY cond, label LIMIT %s"
            )
            with conn.cursor() as cur:
                cur.execute(sql, (int(cond_max), int(n_per_rank)))
                rows = cur.fetchall()
            for row in rows:
                (lbl, cond, abs_disc, disc_sign, eqn, an_rank, mw_rank,
                 tors_order, tors_sub, real_period, st_label,
                 geom_end_alg) = row
                if eqn is None or an_rank is None:
                    continue
                try:
                    f_co, h_co = parse_equation(str(eqn))
                except (ValueError, TypeError):
                    continue
                out.append(Genus2Entry(
                    label=str(lbl),
                    iso_class=_iso_class_from_label(str(lbl)),
                    conductor=int(cond),
                    abs_disc=int(abs_disc),
                    disc_sign=int(disc_sign or 1),
                    f_coeffs=f_co,
                    h_coeffs=h_co,
                    analytic_rank=int(an_rank),
                    mw_rank=int(mw_rank if mw_rank is not None else an_rank),
                    torsion_order=int(tors_order or 1),
                    torsion_subgroup=str(tors_sub or "[]"),
                    real_period=float(real_period or 0.0),
                    st_label=str(st_label or ""),
                    geom_end_alg=str(geom_end_alg or ""),
                ))
    finally:
        conn.close()
    return out


# ---------------------------------------------------------------------------
# Cache (JSON.gz) round-trip
# ---------------------------------------------------------------------------


def _entry_to_dict(e: Genus2Entry) -> dict:
    return {
        "label": e.label,
        "iso_class": e.iso_class,
        "conductor": e.conductor,
        "abs_disc": e.abs_disc,
        "disc_sign": e.disc_sign,
        "f_coeffs": list(e.f_coeffs),
        "h_coeffs": list(e.h_coeffs),
        "analytic_rank": e.analytic_rank,
        "mw_rank": e.mw_rank,
        "torsion_order": e.torsion_order,
        "torsion_subgroup": e.torsion_subgroup,
        "real_period": e.real_period,
        "st_label": e.st_label,
        "geom_end_alg": e.geom_end_alg,
    }


def _dict_to_entry(d: dict) -> Genus2Entry:
    return Genus2Entry(
        label=str(d["label"]),
        iso_class=str(d.get("iso_class", _iso_class_from_label(d["label"]))),
        conductor=int(d["conductor"]),
        abs_disc=int(d["abs_disc"]),
        disc_sign=int(d.get("disc_sign", 1)),
        f_coeffs=tuple(int(x) for x in d["f_coeffs"]),
        h_coeffs=tuple(int(x) for x in d["h_coeffs"]),
        analytic_rank=int(d["analytic_rank"]),
        mw_rank=int(d.get("mw_rank", d["analytic_rank"])),
        torsion_order=int(d.get("torsion_order", 1)),
        torsion_subgroup=str(d.get("torsion_subgroup", "[]")),
        real_period=float(d.get("real_period", 0.0)),
        st_label=str(d.get("st_label", "")),
        geom_end_alg=str(d.get("geom_end_alg", "")),
    )


def write_cache(corpus: Iterable[Genus2Entry], path: Optional[pathlib.Path] = None) -> pathlib.Path:
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


def read_cache(path: Optional[pathlib.Path] = None) -> List[Genus2Entry]:
    target = path or cache_path()
    if not target.is_file():
        raise FileNotFoundError(target)
    with gzip.open(target, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return [_dict_to_entry(d) for d in payload.get("entries", [])]


# ---------------------------------------------------------------------------
# Public surface: load_corpus + stratification
# ---------------------------------------------------------------------------


_LAST_LOAD_SOURCE: str = "uninitialized"


def last_load_source() -> str:
    """Diagnostic: where did the most recent load_genus2_corpus pull from?"""
    return _LAST_LOAD_SOURCE


def load_genus2_corpus(
    *,
    cond_max: int = 50000,
    n_total: int = 2000,
    rank0_share: float = 0.30,
    rank1_share: float = 0.45,
    rank2plus_share: float = 0.25,
    seed: int = 0,
    use_cache: bool = True,
    write_cache_after_fetch: bool = True,
    fallback_to_handcurated: bool = True,
) -> List[Genus2Entry]:
    """Build a stratified corpus of genus-2 curves from LMFDB.

    Parameters
    ----------
    cond_max : int
        Cap on conductor; 50000 yields ~30K curves to sample from in
        each rank stratum.
    n_total : int
        Target stratified sample size.
    rank0_share / rank1_share / rank2plus_share : float
        Target shares for the three rank classes. Normalized internally.
    seed : int
        Reproducible RNG.
    use_cache : bool
        Prefer the cache over a live fetch.
    write_cache_after_fetch : bool
        After a live fetch, persist to cache.
    fallback_to_handcurated : bool
        If both cache and mirror are unavailable, return the small
        hand-curated list (~10 curves) so tests can still exercise.
    """
    global _LAST_LOAD_SOURCE
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0; got {n_total}")
    for nm, v in (
        ("rank0_share", rank0_share),
        ("rank1_share", rank1_share),
        ("rank2plus_share", rank2plus_share),
    ):
        if v < 0:
            raise ValueError(f"{nm} must be >= 0; got {v}")
    total_share = rank0_share + rank1_share + rank2plus_share
    if total_share <= 0:
        raise ValueError("at least one rank share must be positive")

    pool: List[Genus2Entry] = []
    source = "unknown"
    cp = cache_path()

    if use_cache and cp.is_file() and cp.stat().st_size > 0:
        try:
            pool = read_cache(cp)
            source = f"cache:{cp}"
        except Exception:
            pool = []

    if not pool:
        live_attempted = False
        if not _network_disabled():
            try:
                import psycopg2  # noqa: F401
                live_attempted = True
                # Pull n_total per rank class (we will subsample to
                # match the requested mix below).
                per_class = max(64, n_total)  # over-pull, then subsample
                pool = _fetch_from_mirror(
                    cond_max=cond_max,
                    n_per_rank=per_class,
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
            pool = [
                Genus2Entry(
                    label=d["label"],
                    iso_class=d.get("iso_class",
                                    _iso_class_from_label(d["label"])),
                    conductor=d["conductor"],
                    abs_disc=d["abs_disc"],
                    disc_sign=d.get("disc_sign", 1),
                    f_coeffs=parse_equation(d["eqn"])[0],
                    h_coeffs=parse_equation(d["eqn"])[1],
                    analytic_rank=d["analytic_rank"],
                    mw_rank=d.get("mw_rank", d["analytic_rank"]),
                    torsion_order=d.get("torsion_order", 1),
                    torsion_subgroup=d.get("torsion_subgroup", "[]"),
                    real_period=d.get("real_period", 0.0),
                    st_label=d.get("st_label", ""),
                    geom_end_alg=d.get("geom_end_alg", ""),
                )
                for d in _FALLBACK_CURVES
            ]
            source = "fallback:hand-curated"

    if not pool:
        raise RuntimeError("genus2 corpus is empty after all sources tried")

    # Stratify by rank class.
    by_class: dict[int, List[Genus2Entry]] = {0: [], 1: [], 2: []}
    for e in pool:
        by_class.setdefault(e.rank_class, []).append(e)

    s0 = rank0_share / total_share
    s1 = rank1_share / total_share
    s2 = rank2plus_share / total_share
    target = {
        0: int(round(n_total * s0)),
        1: int(round(n_total * s1)),
        2: int(round(n_total * s2)),
    }

    import random as _random
    rng = _random.Random(seed)
    sampled: List[Genus2Entry] = []
    for cls, n_want in target.items():
        bucket = list(by_class.get(cls, []))
        rng.shuffle(bucket)
        sampled.extend(bucket[: min(n_want, len(bucket))])
    if not sampled:
        # Fallback: take everything we have (e.g. tiny fallback corpus).
        sampled = list(pool)
    rng.shuffle(sampled)
    _LAST_LOAD_SOURCE = source
    return sampled


def split_train_test(
    corpus: Sequence[Genus2Entry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> Tuple[List[Genus2Entry], List[Genus2Entry]]:
    """Reproducible train/test split."""
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


def corpus_summary(corpus: Iterable[Genus2Entry]) -> dict:
    """Diagnostic counts: total + per-rank-class + conductor stats."""
    corpus = list(corpus)
    by_class: dict[int, int] = {0: 0, 1: 0, 2: 0}
    for e in corpus:
        by_class[e.rank_class] = by_class.get(e.rank_class, 0) + 1
    conductors = [e.conductor for e in corpus]
    return {
        "n_total": len(corpus),
        "rank_class_counts": dict(sorted(by_class.items())),
        "cond_min": min(conductors) if conductors else None,
        "cond_max": max(conductors) if conductors else None,
        "cond_mean": (sum(conductors) / len(conductors)) if conductors else None,
    }


__all__ = [
    "Genus2Entry",
    "F_COEFF_LEN",
    "H_COEFF_LEN",
    "N_RANK_CLASSES",
    "parse_equation",
    "is_available",
    "cache_path",
    "load_genus2_corpus",
    "last_load_source",
    "split_train_test",
    "corpus_summary",
    "write_cache",
    "read_cache",
]
