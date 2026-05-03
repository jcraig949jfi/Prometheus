"""prometheus_math._bsd_corpus — BSD rank-prediction corpus loader.

Builds a stratified sample of elliptic curves over Q with known rank from
the local Cremona mirror (``prometheus_math.databases.cremona``). Each
entry ships:

    label              : LMFDB label (str), e.g. "11.a2"
    cremona_label      : Cremona label, e.g. "11a1"
    ainvs              : Weierstrass coefficients [a1, a2, a3, a4, a6]
    conductor          : int
    a_p                : list[int] -- first ~20 a_p values, with bad-prime
                                       slots filled by an "encoded" int
                                       (+1, -1, 0 for split/nonsplit/add.
                                       per Cremona convention).
    rank               : int -- KNOWN ground-truth Mordell-Weil rank.

The ``aplist`` files in the Cremona mirror are keyed by isogeny class
(one row per class) and contain Hecke eigenvalues for the first 25
primes. We splice these into per-curve records by matching
``(conductor, isogeny_class)``.

Stratified sampling:
    rank-0     -> ~500
    rank-1     -> ~400
    rank-2+    -> ~100
keeps the class imbalance close to the curated LMFDB shape (~50/40/10)
while preserving enough rank-2 curves for the agent to *see* the high-
rank tail.

Skip-with-message if the Cremona mirror is absent or empty.
"""
from __future__ import annotations

import dataclasses
import pathlib
from typing import Any, Iterable, Optional

from .databases import cremona


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class BSDEntry:
    """One labelled elliptic-curve record."""

    label: str            # LMFDB label, e.g. "11.a2"
    cremona_label: str    # Cremona label, e.g. "11a1"
    ainvs: tuple[int, ...]
    conductor: int
    a_p: tuple[int, ...]  # first N_AP primes
    rank: int


# Small primes used as the a_p feature axis. Order matches the Cremona
# aplist file column order (which is the first 25 rational primes; we
# truncate to the requested length below).
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

DEFAULT_N_AP = 20  # first 20 primes (through p=71)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bad_prime_token(token: str) -> int:
    """Map Cremona aplist bad-reduction tokens to integer features.

    The Cremona aplist format encodes bad-reduction primes with single
    characters:
        '+'  -> split multiplicative   (a_p = +1)
        '-'  -> nonsplit multiplicative (a_p = -1)
        '0'  -> additive               (a_p = 0)
    Returns the encoded integer.
    """
    if token == "+":
        return 1
    if token == "-":
        return -1
    if token == "0":
        return 0
    raise ValueError(f"unknown aplist bad-reduction token {token!r}")


def _parse_ap_token(token: str) -> int:
    """Parse a single aplist column token to its integer a_p value."""
    try:
        return int(token)
    except ValueError:
        return _bad_prime_token(token)


def _aplist_root() -> pathlib.Path:
    """Return the on-disk aplist directory of the Cremona mirror."""
    return cremona._root() / "aplist"


def _load_aplist_class_table(n_ap: int = DEFAULT_N_AP) -> dict[tuple[int, str], list[int]]:
    """Read every aplist.* file present and return {(N, class) -> [a_p, ...]}.

    ``n_ap`` selects the first n_ap primes from each row. Rows shorter
    than n_ap are returned at their natural length.
    """
    root = _aplist_root()
    table: dict[tuple[int, str], list[int]] = {}
    if not root.is_dir():
        return table
    for p in sorted(root.iterdir()):
        if not p.is_file() or p.stat().st_size == 0:
            continue
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 3:
                    continue
                try:
                    n = int(parts[0])
                except ValueError:
                    continue
                cls = parts[1]
                ap_tokens = parts[2:2 + n_ap]
                try:
                    ap = [_parse_ap_token(t) for t in ap_tokens]
                except ValueError:
                    # Skip malformed rows.
                    continue
                table[(n, cls)] = ap
    return table


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------


def is_available() -> tuple[bool, str]:
    """Cheap reachability check.

    Returns (ok, reason). When ``ok`` is False, ``reason`` is a short
    human-readable explanation of why the corpus can't be built.
    """
    if not cremona.has_local_mirror():
        return False, "Cremona mirror missing; run cremona.update_mirror()"
    info = cremona.mirror_info()
    if info.get("n_curves", 0) == 0:
        # n_curves comes from the metadata sidecar OR an active load — try a
        # cheap query to be sure.
        rows = cremona.elliptic_curves(limit=1, fall_back_to_lmfdb=False)
        if not rows:
            return False, "Cremona mirror present but indexes 0 curves"
    aplist_dir = _aplist_root()
    if not aplist_dir.is_dir() or not any(aplist_dir.iterdir()):
        return False, ("Cremona mirror missing aplist family; run "
                       "cremona.update_mirror(families=('aplist',))")
    return True, "ok"


def load_bsd_corpus(
    n_total: int = 1000,
    n_ap: int = DEFAULT_N_AP,
    rank0_share: float = 0.5,
    rank1_share: float = 0.4,
    rank2plus_share: float = 0.1,
    seed: int = 0,
    conductor_max: Optional[int] = None,
    require_aplist: bool = True,
) -> list[BSDEntry]:
    """Build a stratified BSD-rank corpus from the Cremona mirror.

    Parameters
    ----------
    n_total : int
        Target total entry count. Stratified across (rank-0, rank-1,
        rank>=2) by the share parameters; trailing strata are clamped
        to whatever the corpus can supply.
    n_ap : int
        Number of leading primes to keep in the ``a_p`` feature vector.
        Defaults to 20 (covers p in {2, ..., 71}).
    rank0_share / rank1_share / rank2plus_share : float
        Target proportions per rank stratum. The three values do NOT
        need to sum to 1; they are normalized internally.
    seed : int
        Numpy-style seed for the stratified sampler. Same seed -> same
        corpus.
    conductor_max : int, optional
        Filter curves to ``conductor <= conductor_max``. None = no cap.
    require_aplist : bool
        If True (default), drop any curve whose isogeny class is missing
        from the aplist mirror. If False, fall back to ``a_p = (0,) *
        n_ap`` for missing classes (useful only for diagnostic runs).

    Returns
    -------
    list[BSDEntry]

    Raises
    ------
    RuntimeError
        If the Cremona mirror is unreachable, or no curves match.
        Callers should catch this and skip-with-message.
    ValueError
        If ``n_total <= 0`` or any share is negative.
    """
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0; got {n_total}")
    for name, val in (("rank0_share", rank0_share),
                      ("rank1_share", rank1_share),
                      ("rank2plus_share", rank2plus_share)):
        if val < 0:
            raise ValueError(f"{name} must be >= 0; got {val}")
    total_share = rank0_share + rank1_share + rank2plus_share
    if total_share <= 0:
        raise ValueError("at least one rank share must be positive")

    ok, reason = is_available()
    if not ok:
        raise RuntimeError(reason)

    # Pull every curve we can from the mirror (subject to conductor cap).
    curves = cremona.elliptic_curves(
        conductor_max=conductor_max,
        limit=10**9,
        fall_back_to_lmfdb=False,
    )
    if not curves:
        raise RuntimeError("Cremona mirror returned 0 curves")

    # Load the aplist class table (one a_p list per (N, class)).
    ap_table = _load_aplist_class_table(n_ap=n_ap)
    if require_aplist and not ap_table:
        raise RuntimeError(
            "aplist family absent from mirror; run "
            "cremona.update_mirror(families=('aplist',))"
        )

    # Build entries: skip curves with rank None or ainvs missing.
    raw: list[BSDEntry] = []
    for row in curves:
        rk = row.get("rank")
        ai = row.get("ainvs")
        cl = row.get("isogeny_class")
        cn = row.get("conductor")
        if rk is None or ai is None or cl is None or cn is None:
            continue
        ap = ap_table.get((cn, cl))
        if ap is None:
            if require_aplist:
                continue
            ap = [0] * n_ap
        # Truncate / pad to exactly n_ap.
        if len(ap) >= n_ap:
            ap = ap[:n_ap]
        else:
            ap = list(ap) + [0] * (n_ap - len(ap))
        # Clamp absurd ranks (rank-3 has 1 entry in the mirror; treat as 2+).
        rk_int = int(rk)
        if rk_int < 0:
            continue
        cremona_label = row.get("cremona_label", "")
        lmfdb_label = row.get("lmfdb_label") or cremona_label
        raw.append(
            BSDEntry(
                label=str(lmfdb_label),
                cremona_label=str(cremona_label),
                ainvs=tuple(int(x) for x in ai),
                conductor=int(cn),
                a_p=tuple(int(x) for x in ap),
                rank=rk_int,
            )
        )

    if not raw:
        raise RuntimeError("no curves left after filtering")

    # Stratified subsample. Bin by rank.
    import random as _random
    rng = _random.Random(seed)
    by_stratum: dict[str, list[BSDEntry]] = {"r0": [], "r1": [], "r2+": []}
    for e in raw:
        if e.rank == 0:
            by_stratum["r0"].append(e)
        elif e.rank == 1:
            by_stratum["r1"].append(e)
        else:
            by_stratum["r2+"].append(e)

    # Normalize shares.
    s_r0 = rank0_share / total_share
    s_r1 = rank1_share / total_share
    s_r2 = rank2plus_share / total_share
    target = {
        "r0": int(round(n_total * s_r0)),
        "r1": int(round(n_total * s_r1)),
        "r2+": int(round(n_total * s_r2)),
    }
    sampled: list[BSDEntry] = []
    for stratum, n_want in target.items():
        pool = list(by_stratum[stratum])
        rng.shuffle(pool)
        sampled.extend(pool[: min(n_want, len(pool))])
    rng.shuffle(sampled)
    return sampled


def split_train_test(
    corpus: list[BSDEntry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> tuple[list[BSDEntry], list[BSDEntry]]:
    """Reproducible train/test split.

    Same ``corpus`` + same ``seed`` always yields the same partition.
    """
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


def corpus_summary(corpus: Iterable[BSDEntry]) -> dict[str, Any]:
    """Diagnostic counts: total + per-rank tallies."""
    corpus = list(corpus)
    counts: dict[int, int] = {}
    for e in corpus:
        counts[e.rank] = counts.get(e.rank, 0) + 1
    return {
        "n_total": len(corpus),
        "rank_counts": dict(sorted(counts.items())),
        "max_rank": max((e.rank for e in corpus), default=None),
    }


__all__ = [
    "BSDEntry",
    "DEFAULT_N_AP",
    "PRIMES_25",
    "is_available",
    "load_bsd_corpus",
    "split_train_test",
    "corpus_summary",
]
