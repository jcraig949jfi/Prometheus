"""prometheus_math._bsd_rich_features — enriched BSD corpus loader.

Sidecar to ``_bsd_corpus.py`` (which is left untouched as a regression
anchor). Builds the same 1000-curve stratified sample, then attaches a
``RichFeatures`` block per entry containing fields that ``BSDEntry``
does not carry:

    regulator              : float       (Cremona allbsd OM/REG column)
    real_period            : float       (Cremona allbsd OM column)
    L1                     : float       (Cremona allbsd L1 column)
    tamagawa_product       : int         (Cremona allbsd CP column)
    torsion                : int         (Cremona allcurves T column)
    sha_an                 : int|float   (Cremona allbsd SHA column)
    torsion_structure      : tuple[int,...]   (LMFDB ec_curvedata)
    bad_primes             : tuple[int,...]   (LMFDB ec_curvedata)
    cm                     : int         (LMFDB ec_curvedata; 0 = non-CM)
    num_bad_primes         : int         (LMFDB ec_curvedata)
    semistable             : bool        (LMFDB ec_curvedata)
    signD                  : int         (LMFDB ec_curvedata)
    faltings_height        : float       (LMFDB ec_curvedata)
    abc_quality            : float       (LMFDB ec_curvedata)
    szpiro_ratio           : float       (LMFDB ec_curvedata)
    j_invariant_log        : float       (log10|num| - log10|den| of jinv)
    conductor_radical      : int         (product of distinct bad primes)

Sato-Tate group is NOT a column on ``ec_curvedata``; we tested the
schema (2026-05-04) and it is only populated for modular forms. We
document the gap and proceed without that feature.

Cache layout
------------
The enriched records are persisted as a single gzip JSON at
``prometheus_math/databases/bsd_rich.json.gz``. Same loader semantics
as ``_bsd_corpus.load_bsd_corpus`` — call ``load_bsd_rich_corpus`` and
the on-disk cache is honored if its provenance header matches.

Skip-with-message
-----------------
``is_available`` returns False if the underlying ``_bsd_corpus`` is
unavailable. The LMFDB enrichment is best-effort: if the mirror is
unreachable, we fall back to fields-from-Cremona-only (the rich block
is partially populated and the vectorizer treats missing values as 0).
"""
from __future__ import annotations

import dataclasses
import gzip
import json
import math
import pathlib
from typing import Any, Iterable, Optional, Sequence

from . import _bsd_corpus
from ._bsd_corpus import BSDEntry, DEFAULT_N_AP


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class RichFeatures:
    """Numerical + categorical metadata attached to one ``BSDEntry``."""

    # Cremona allbsd-derived (always present when the local mirror is
    # complete; default sentinels otherwise).
    regulator: float = 0.0
    real_period: float = 0.0
    L1: float = 0.0
    tamagawa_product: int = 0
    torsion: int = 0
    sha_an: float = 1.0
    # LMFDB-derived (best-effort; defaults if mirror is unreachable).
    torsion_structure: tuple[int, ...] = ()
    bad_primes: tuple[int, ...] = ()
    cm: int = 0
    num_bad_primes: int = 0
    semistable: bool = False
    signD: int = 0
    faltings_height: float = 0.0
    abc_quality: float = 0.0
    szpiro_ratio: float = 0.0
    j_invariant_log: float = 0.0
    conductor_radical: int = 1


@dataclasses.dataclass(frozen=True)
class RichBSDEntry:
    """``BSDEntry`` + ``RichFeatures`` bundle."""

    base: BSDEntry
    rich: RichFeatures

    # Convenience accessors (so callers can treat the bundle as if it
    # were a ``BSDEntry`` for label / rank / a_p purposes).
    @property
    def label(self) -> str:
        return self.base.label

    @property
    def cremona_label(self) -> str:
        return self.base.cremona_label

    @property
    def conductor(self) -> int:
        return self.base.conductor

    @property
    def rank(self) -> int:
        return self.base.rank

    @property
    def a_p(self) -> tuple[int, ...]:
        return self.base.a_p

    @property
    def ainvs(self) -> tuple[int, ...]:
        return self.base.ainvs


# ---------------------------------------------------------------------------
# On-disk cache path + provenance
# ---------------------------------------------------------------------------


def _cache_path() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve().parent
    return here / "databases" / "bsd_rich.json.gz"


# Bump when the cache schema changes.
_CACHE_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Helpers: pull Cremona allbsd fields for a known cremona_label
# ---------------------------------------------------------------------------


def _cremona_record(cremona_label: str) -> dict:
    """Look up the on-disk Cremona row for ``cremona_label``.

    Returns {} on miss (e.g. when the allbsd block is absent for that
    conductor range). Never raises on unknown label.
    """
    from .databases import cremona

    rows = cremona.elliptic_curves(
        label=cremona_label, limit=1, fall_back_to_lmfdb=False
    )
    if not rows:
        return {}
    return dict(rows[0])


# ---------------------------------------------------------------------------
# Helpers: pull LMFDB fields by lmfdb_label, in batches
# ---------------------------------------------------------------------------


_LMFDB_FIELDS = [
    "lmfdb_label",
    "jinv",
    "torsion_structure",
    "bad_primes",
    "cm",
    "num_bad_primes",
    "semistable",
    '"signD"',
    "faltings_height",
    "abc_quality",
    "szpiro_ratio",
]


def _coerce_lmfdb_record(rec: dict) -> dict:
    """Normalize a raw LMFDB row into native Python types.

    Handles the Decimal -> int/float conversion already performed by
    ``lmfdb.query_dicts``, plus the jinv [num, den] -> log magnitude.
    """
    out = dict(rec)
    jinv = out.get("jinv")
    if isinstance(jinv, (list, tuple)) and len(jinv) >= 2:
        try:
            num = float(jinv[0])
            den = float(jinv[1])
        except (TypeError, ValueError):
            num, den = 0.0, 1.0
        if den == 0:
            j_log = 0.0
        else:
            try:
                j_log = math.log10(max(abs(num), 1e-300)) - math.log10(
                    max(abs(den), 1e-300)
                )
            except ValueError:
                j_log = 0.0
        out["j_invariant_log"] = float(j_log)
    else:
        out["j_invariant_log"] = 0.0

    bp = out.get("bad_primes") or []
    out["bad_primes"] = tuple(int(p) for p in bp)
    ts = out.get("torsion_structure") or []
    out["torsion_structure"] = tuple(int(x) for x in ts)
    rad = 1
    for p in out["bad_primes"]:
        rad *= int(p)
    out["conductor_radical"] = int(rad)
    return out


def _fetch_lmfdb_rich(
    lmfdb_labels: Sequence[str],
    timeout: int = 30,
) -> dict[str, dict]:
    """Pull LMFDB ec_curvedata rich fields for the given labels.

    Returns a dict ``{lmfdb_label: rich_dict}``. Empty dict on connection
    failure (the caller treats that as "no LMFDB enrichment").
    """
    if not lmfdb_labels:
        return {}
    try:
        from .databases import lmfdb
        from .databases.lmfdb import query_dicts
    except Exception:
        return {}

    # Parameterized IN-list (psycopg2 expands tuples cleanly).
    cols_sql = ", ".join(_LMFDB_FIELDS)
    sql = (
        f"SELECT {cols_sql} FROM ec_curvedata "
        f"WHERE lmfdb_label IN %s"
    )
    out: dict[str, dict] = {}
    # Chunk to keep the query small.
    BATCH = 500
    labels = list(dict.fromkeys(lmfdb_labels))  # dedupe, preserve order
    try:
        for i in range(0, len(labels), BATCH):
            chunk = tuple(labels[i: i + BATCH])
            rows = query_dicts(sql, (chunk,), timeout=timeout)
            for r in rows:
                lbl = r.get("lmfdb_label")
                if lbl is None:
                    continue
                out[str(lbl)] = _coerce_lmfdb_record(r)
    except Exception:
        # Network / mirror flap; return whatever we got so far.
        pass
    return out


# ---------------------------------------------------------------------------
# Build / load
# ---------------------------------------------------------------------------


def is_available() -> tuple[bool, str]:
    return _bsd_corpus.is_available()


def _build_rich_entry(
    base: BSDEntry,
    cremona_row: dict,
    lmfdb_row: dict,
) -> RichBSDEntry:
    """Combine base + Cremona allbsd + LMFDB rows into a RichBSDEntry."""
    sha_an_raw = cremona_row.get("sha_an", 1.0)
    if sha_an_raw is None:
        sha_an_val = 1.0
    else:
        try:
            sha_an_val = float(sha_an_raw)
        except (TypeError, ValueError):
            sha_an_val = 1.0

    rf = RichFeatures(
        regulator=float(cremona_row.get("regulator") or 0.0),
        real_period=float(cremona_row.get("real_period") or 0.0),
        L1=float(cremona_row.get("L1") or 0.0),
        tamagawa_product=int(cremona_row.get("tamagawa") or 0),
        torsion=int(cremona_row.get("torsion") or 0),
        sha_an=sha_an_val,
        torsion_structure=tuple(int(x) for x in lmfdb_row.get("torsion_structure", ())),
        bad_primes=tuple(int(p) for p in lmfdb_row.get("bad_primes", ())),
        cm=int(lmfdb_row.get("cm") or 0),
        num_bad_primes=int(lmfdb_row.get("num_bad_primes") or 0),
        semistable=bool(lmfdb_row.get("semistable") or False),
        signD=int(lmfdb_row.get("signD") or 0),
        faltings_height=float(lmfdb_row.get("faltings_height") or 0.0),
        abc_quality=float(lmfdb_row.get("abc_quality") or 0.0),
        szpiro_ratio=float(lmfdb_row.get("szpiro_ratio") or 0.0),
        j_invariant_log=float(lmfdb_row.get("j_invariant_log") or 0.0),
        conductor_radical=int(lmfdb_row.get("conductor_radical") or 1),
    )
    return RichBSDEntry(base=base, rich=rf)


def _serialize(entries: Sequence[RichBSDEntry]) -> dict:
    return {
        "schema_version": _CACHE_SCHEMA_VERSION,
        "n_entries": len(entries),
        "entries": [
            {
                "base": {
                    "label": e.base.label,
                    "cremona_label": e.base.cremona_label,
                    "ainvs": list(e.base.ainvs),
                    "conductor": int(e.base.conductor),
                    "a_p": list(e.base.a_p),
                    "rank": int(e.base.rank),
                },
                "rich": {
                    "regulator": e.rich.regulator,
                    "real_period": e.rich.real_period,
                    "L1": e.rich.L1,
                    "tamagawa_product": e.rich.tamagawa_product,
                    "torsion": e.rich.torsion,
                    "sha_an": e.rich.sha_an,
                    "torsion_structure": list(e.rich.torsion_structure),
                    "bad_primes": list(e.rich.bad_primes),
                    "cm": e.rich.cm,
                    "num_bad_primes": e.rich.num_bad_primes,
                    "semistable": e.rich.semistable,
                    "signD": e.rich.signD,
                    "faltings_height": e.rich.faltings_height,
                    "abc_quality": e.rich.abc_quality,
                    "szpiro_ratio": e.rich.szpiro_ratio,
                    "j_invariant_log": e.rich.j_invariant_log,
                    "conductor_radical": e.rich.conductor_radical,
                },
            }
            for e in entries
        ],
    }


def _deserialize(blob: dict) -> list[RichBSDEntry]:
    out: list[RichBSDEntry] = []
    for row in blob.get("entries", []):
        b = row["base"]
        r = row["rich"]
        base = BSDEntry(
            label=str(b["label"]),
            cremona_label=str(b["cremona_label"]),
            ainvs=tuple(int(x) for x in b["ainvs"]),
            conductor=int(b["conductor"]),
            a_p=tuple(int(x) for x in b["a_p"]),
            rank=int(b["rank"]),
        )
        rf = RichFeatures(
            regulator=float(r["regulator"]),
            real_period=float(r["real_period"]),
            L1=float(r["L1"]),
            tamagawa_product=int(r["tamagawa_product"]),
            torsion=int(r["torsion"]),
            sha_an=float(r["sha_an"]),
            torsion_structure=tuple(int(x) for x in r["torsion_structure"]),
            bad_primes=tuple(int(x) for x in r["bad_primes"]),
            cm=int(r["cm"]),
            num_bad_primes=int(r["num_bad_primes"]),
            semistable=bool(r["semistable"]),
            signD=int(r["signD"]),
            faltings_height=float(r["faltings_height"]),
            abc_quality=float(r["abc_quality"]),
            szpiro_ratio=float(r["szpiro_ratio"]),
            j_invariant_log=float(r["j_invariant_log"]),
            conductor_radical=int(r["conductor_radical"]),
        )
        out.append(RichBSDEntry(base=base, rich=rf))
    return out


def load_bsd_rich_corpus(
    *,
    n_total: int = 1000,
    n_ap: int = DEFAULT_N_AP,
    rank0_share: float = 0.5,
    rank1_share: float = 0.4,
    rank2plus_share: float = 0.1,
    seed: int = 0,
    conductor_max: Optional[int] = None,
    use_cache: bool = True,
    rebuild: bool = False,
    lmfdb_timeout: int = 30,
) -> list[RichBSDEntry]:
    """Build (or load from cache) the rich-features BSD corpus.

    Parameters mirror ``_bsd_corpus.load_bsd_corpus`` for stratification.
    Cache is honored when its ``schema_version`` and ``n_entries`` match
    the requested ``n_total`` and we are not asked to ``rebuild``.
    """
    cache = _cache_path()
    if use_cache and not rebuild and cache.is_file():
        try:
            with gzip.open(cache, "rt", encoding="utf-8") as fh:
                blob = json.load(fh)
            if (
                blob.get("schema_version") == _CACHE_SCHEMA_VERSION
                and blob.get("n_entries") == n_total
            ):
                return _deserialize(blob)
        except Exception:
            # Corrupt or stale cache: fall through to rebuild.
            pass

    base = _bsd_corpus.load_bsd_corpus(
        n_total=n_total,
        n_ap=n_ap,
        rank0_share=rank0_share,
        rank1_share=rank1_share,
        rank2plus_share=rank2plus_share,
        seed=seed,
        conductor_max=conductor_max,
    )

    # LMFDB enrichment in one batched query.
    lmfdb_labels = [b.label for b in base]
    lmfdb_rows = _fetch_lmfdb_rich(lmfdb_labels, timeout=lmfdb_timeout)

    entries: list[RichBSDEntry] = []
    for b in base:
        cre = _cremona_record(b.cremona_label)
        lf = lmfdb_rows.get(b.label, {})
        entries.append(_build_rich_entry(b, cre, lf))

    if use_cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        blob = _serialize(entries)
        blob["n_entries"] = len(entries)  # honor truncation if any
        with gzip.open(cache, "wt", encoding="utf-8") as fh:
            json.dump(blob, fh)

    return entries


def split_train_test_rich(
    corpus: list[RichBSDEntry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> tuple[list[RichBSDEntry], list[RichBSDEntry]]:
    """Reproducible train/test split (mirrors ``_bsd_corpus.split_train_test``)."""
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


__all__ = [
    "RichFeatures",
    "RichBSDEntry",
    "is_available",
    "load_bsd_rich_corpus",
    "split_train_test_rich",
]
