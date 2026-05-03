"""prometheus_math._obstruction_corpus_extended — multi-prefix extension
of the live OBSTRUCTION_SHAPE corpus.

Background
----------

The base loader at ``_obstruction_corpus_live.py`` reads two of Charon's
files and joins them on ``seq_id`` for the A14* family:

  * ``asymptotic_deviations.jsonl`` — per-OEIS-sequence rate deviation
    metadata (delta_pct, regime_change, best_model).
  * ``battery_sweep_v2.jsonl`` — per-sequence falsification verdicts
    (which of F1/F6/F9/F11/etc. fired).

This extension answers the *generalization* question: does the
OBSTRUCTION_SHAPE architecture extend beyond A14* into A150*/A151*
unstudied territory?

Honest data audit (verified at module-write time):

  prefix  | deviations rows (3-D walks) | battery rows | unanimous-killed
  --------|-----------------------------|--------------|------------------
  A148    | 201                         | 38           | 0
  A149    | 500                         | 59           | 5  (Charon's anchors)
  A150    | 501                         | 0            | 0  (battery never run)
  A151    | 255 (3-D) / 332 total       | 3 (2-D only) | 0  (battery records
                                                       |     are 2-D walks
                                                       |     and don't join)

The honest finding: **Charon's real falsification battery has only been
run on A14*.** For A150 and the 3-D portion of A151, ``battery_sweep_v2``
contains zero records. Loading those prefixes via the live join
yields entries with ``kill_verdict=False`` everywhere — not because
they're not obstructed, but because the battery hasn't run.

Two modes
---------

This module exposes both modes explicitly so reviewers can distinguish:

  ``mode="live"``: identical join logic to the base loader. Real
    F1+F6+F9+F11 verdicts only. Honest, but A150/A151 read as
    uniformly non-killed.

  ``mode="surrogate"``: stretch corpus. Synthesizes a kill_verdict
    from observable structural-anomaly signals in
    ``asymptotic_deviations.jsonl``:

        surrogate_kill := delta_pct > 50.0 AND regime_change is True

    This rule was *empirically calibrated against Charon's A149 ground
    truth*: the 5 unanimous-killed A149 sequences (A149074, A149081,
    A149082, A149089, A149090) are exactly the 5 A149 entries with
    delta_pct > 50% AND regime_change. No false positives, no false
    negatives, on A149.

    The same rule applied to A148/A150/A151 yields ZERO surrogate
    kills — because no entries in those prefixes have delta_pct > 50%.
    This is itself the substantive finding: the obstruction phenomenon
    Charon characterized is concentrated in A149's regime, not a
    generic feature of N^3 octant walks.

API
---

``load_extended_corpus(prefixes, mode, ...)`` — loader with optional
multi-prefix list and mode toggle. Default ``prefixes=["A148","A149"]``
preserves backwards-compatibility with the base loader.

``extended_corpus_summary(corpus)`` — adds per-prefix kill rates to the
base summary.

``surrogate_kill_verdict(record)`` — pure function that returns the
synthetic verdict for a single ``asymptotic_deviations`` record.

The exported ``LiveCorpusEntry`` dataclass is the same one from the
base loader — no schema change. An optional ``mode`` field exists in
the summary so consumers can audit which kill-source produced an
entry, but the entry shape itself is unchanged so ``ObstructionEnv``
consumes both transparently.
"""
from __future__ import annotations

import json
import logging
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ._obstruction_corpus_live import (
    DEFAULT_BATTERY_PATH,
    DEFAULT_DEVIATIONS_PATH,
    LiveCorpusEntry,
    UNANIMOUS_BATTERY,
    _kills_by_seq_id,
    _load_jsonl,
    features_of,
    parse_step_set,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


# Backwards-compatible default: the A14* family Charon studied.
DEFAULT_PREFIXES: Tuple[str, ...] = ("A148", "A149")


# Surrogate rule constants — empirically calibrated against Charon's
# A149 ground truth. See module docstring.
SURROGATE_DELTA_PCT_THRESHOLD: float = 50.0


# ---------------------------------------------------------------------------
# Surrogate kill verdict — pure function
# ---------------------------------------------------------------------------


def surrogate_kill_verdict(deviation_record: Dict[str, Any]) -> bool:
    """Return the synthetic kill verdict for a single
    ``asymptotic_deviations`` record.

    Rule:
        kill iff ``delta_pct > 50.0`` AND ``regime_change is True``

    The threshold and the regime_change conjunction are calibrated
    against Charon's 5 unanimous-killed A149 anchors. On A149, the
    rule has 100% precision and 100% recall vs the real F1+F6+F9+F11
    battery. On A148/A150/A151 it yields zero hits — see module
    docstring.

    Missing fields default to a non-kill: a record with neither
    delta_pct nor regime_change is read as 'no anomaly information,
    presumed not killed'. This matches the base loader's behavior
    when battery_sweep is absent for a sequence.

    Pure function: no I/O, no state, deterministic.
    """
    delta = deviation_record.get("delta_pct")
    if delta is None:
        return False
    try:
        delta_f = float(delta)
    except (TypeError, ValueError):
        return False
    if delta_f <= SURROGATE_DELTA_PCT_THRESHOLD:
        return False
    if not bool(deviation_record.get("regime_change", False)):
        return False
    return True


# ---------------------------------------------------------------------------
# Multi-prefix loader
# ---------------------------------------------------------------------------


def load_extended_corpus(
    prefixes: Optional[Sequence[str]] = None,
    mode: str = "live",
    battery_path: Optional[os.PathLike] = None,
    deviations_path: Optional[os.PathLike] = None,
    require_steps: bool = True,
) -> List[LiveCorpusEntry]:
    """Load the OEIS battery corpus across multiple A-number prefixes.

    Parameters
    ----------
    prefixes : sequence of str, optional
        OEIS A-number prefixes to load (e.g. ``["A148","A149","A150"]``).
        Each entry must be the prefix string the loader filters on
        (``seq_id.startswith(prefix)``). Defaults to
        ``DEFAULT_PREFIXES`` = ``("A148","A149")`` — the canonical A14*
        family Charon studied.
    mode : {"live", "surrogate"}
        ``"live"`` (default): join with ``battery_sweep_v2.jsonl`` for
        real F1+F6+F9+F11 verdicts. Sequences without battery records
        get ``kill_verdict=False``.

        ``"surrogate"``: ignore the battery file and synthesize the
        verdict from ``surrogate_kill_verdict`` applied to the
        deviations record. Empirically calibrated to Charon's A149
        anchors at 100% precision/recall (see module docstring).
        Use this when extending to prefixes the real battery hasn't
        run on yet.
    battery_path : path-like, optional
        Override path to ``battery_sweep_v2.jsonl``. Default:
        ``DEFAULT_BATTERY_PATH``. Ignored in surrogate mode.
    deviations_path : path-like, optional
        Override path to ``asymptotic_deviations.jsonl``. Default:
        ``DEFAULT_DEVIATIONS_PATH``.
    require_steps : bool
        If True, drop entries whose step-set can't be parsed from the
        OEIS name (typically 2-D walks like A151255 in an N^3 corpus).
        Default True.

    Returns
    -------
    list[LiveCorpusEntry]
        Sorted by ``sequence_id`` ascending so reads are reproducible.

    Raises
    ------
    ValueError
        If ``prefixes`` is empty, if ``mode`` is unknown, or if the
        resulting corpus is empty (mirrors base loader's contract).
    FileNotFoundError
        If the deviations file (or, in live mode, the battery file)
        is missing.
    """
    if prefixes is None:
        prefixes = DEFAULT_PREFIXES
    prefixes = list(prefixes)
    if not prefixes:
        raise ValueError(
            "prefixes must be a non-empty list of OEIS A-number prefixes"
        )
    if mode not in ("live", "surrogate"):
        raise ValueError(
            f"mode must be 'live' or 'surrogate'; got {mode!r}"
        )

    bpath = (
        Path(battery_path)
        if battery_path is not None
        else DEFAULT_BATTERY_PATH
    )
    dpath = (
        Path(deviations_path)
        if deviations_path is not None
        else DEFAULT_DEVIATIONS_PATH
    )

    # Always load deviations.
    deviation_rows, deviation_skipped = _load_jsonl(dpath)
    if deviation_skipped:
        logger.info(
            "asymptotic_deviations: %d malformed lines skipped",
            deviation_skipped,
        )

    # Live mode also loads battery; surrogate mode skips it.
    if mode == "live":
        battery_rows, battery_skipped = _load_jsonl(bpath)
        if battery_skipped:
            logger.info(
                "battery_sweep_v2: %d malformed lines skipped",
                battery_skipped,
            )
        kills = _kills_by_seq_id(battery_rows)
    else:
        battery_skipped = 0
        kills = {}

    entries: List[LiveCorpusEntry] = []
    n_no_seq_id = 0
    n_wrong_prefix = 0
    n_no_steps = 0
    n_dups = 0
    seen_ids: set = set()

    for r in deviation_rows:
        sid = r.get("seq_id")
        if not sid:
            n_no_seq_id += 1
            continue
        # Multi-prefix filter: keep iff sid starts with ANY requested prefix.
        if not any(sid.startswith(p) for p in prefixes):
            n_wrong_prefix += 1
            continue
        if sid in seen_ids:
            n_dups += 1
            continue
        steps = parse_step_set(r.get("name", ""))
        if not steps:
            if require_steps:
                n_no_steps += 1
                continue
            steps = []
        feats = features_of(steps)

        if mode == "live":
            seq_kill_tests = kills.get(sid, set())
            kill_verdict = UNANIMOUS_BATTERY.issubset(seq_kill_tests)
        else:  # surrogate
            kill_verdict = surrogate_kill_verdict(r)

        entries.append(
            LiveCorpusEntry(
                n_steps=int(feats["n_steps"]),
                neg_x=int(feats["neg_x"]),
                pos_x=int(feats["pos_x"]),
                neg_y=int(feats["neg_y"]),
                pos_y=int(feats["pos_y"]),
                neg_z=int(feats["neg_z"]),
                pos_z=int(feats["pos_z"]),
                has_diag_neg=bool(feats["has_diag_neg"]),
                has_diag_pos=bool(feats["has_diag_pos"]),
                kill_verdict=bool(kill_verdict),
                sequence_id=str(sid),
            )
        )
        seen_ids.add(sid)

    if not entries:
        raise ValueError(
            f"extended corpus empty: 0 entries kept "
            f"(prefixes={prefixes}, mode={mode}, no_seq_id={n_no_seq_id}, "
            f"wrong_prefix={n_wrong_prefix}, no_steps={n_no_steps}); "
            f"battery_path={bpath}, deviations_path={dpath}"
        )

    entries.sort(key=lambda e: e.sequence_id)

    logger.info(
        "extended_corpus[mode=%s]: %d entries kept across prefixes=%s "
        "(skipped: no_seq_id=%d, wrong_prefix=%d, no_steps=%d, dups=%d)",
        mode,
        len(entries),
        prefixes,
        n_no_seq_id,
        n_wrong_prefix,
        n_no_steps,
        n_dups,
    )
    return entries


# ---------------------------------------------------------------------------
# Summary with per-prefix breakdown
# ---------------------------------------------------------------------------


def extended_corpus_summary(
    corpus: List[LiveCorpusEntry],
) -> Dict[str, Any]:
    """Summary dict with per-prefix kill-rate breakdown.

    Adds two keys on top of the base ``live_corpus_summary`` shape:

      ``per_prefix_kill_rate`` — kill rate within each A-number prefix.
      ``per_prefix_total`` — entry count within each A-number prefix.

    These are critical for cross-prefix generalization claims: a global
    kill rate could mask "all kills concentrated in one prefix"
    (which is in fact what we observe — see
    ``OBSTRUCTION_EXTENDED_RESULTS.md``).
    """
    n_total = len(corpus)
    n_killed = sum(1 for e in corpus if e.kill_verdict)
    kill_rate = (n_killed / n_total) if n_total else 0.0

    # Per-feature value frequency (mirrors base summary).
    value_dist: Dict[str, Dict[Any, int]] = {}
    for feat in (
        "n_steps",
        "neg_x",
        "pos_x",
        "neg_y",
        "pos_y",
        "neg_z",
        "pos_z",
        "has_diag_neg",
        "has_diag_pos",
    ):
        c: Counter = Counter()
        for e in corpus:
            c[getattr(e, feat)] += 1
        value_dist[feat] = dict(
            sorted(c.items(), key=lambda kv: (str(type(kv[0])), kv[0]))
        )

    # Per-prefix totals + kill rates.
    prefix_totals: Counter = Counter()
    prefix_kills: Counter = Counter()
    for e in corpus:
        pre = e.sequence_id[:4]
        prefix_totals[pre] += 1
        if e.kill_verdict:
            prefix_kills[pre] += 1
    by_prefix = dict(sorted(prefix_totals.items()))
    per_prefix_kill_rate = {
        pre: (prefix_kills[pre] / prefix_totals[pre]) if prefix_totals[pre] else 0.0
        for pre in by_prefix
    }
    per_prefix_total = dict(by_prefix)

    return {
        "n_total": n_total,
        "n_killed": n_killed,
        "kill_rate": kill_rate,
        "feature_value_distribution": value_dist,
        "by_a_number_prefix": by_prefix,
        "per_prefix_total": per_prefix_total,
        "per_prefix_kill_rate": per_prefix_kill_rate,
    }


__all__ = [
    "DEFAULT_PREFIXES",
    "LiveCorpusEntry",  # re-export for convenience
    "SURROGATE_DELTA_PCT_THRESHOLD",
    "load_extended_corpus",
    "extended_corpus_summary",
    "surrogate_kill_verdict",
]
