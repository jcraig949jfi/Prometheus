"""prometheus_math._obstruction_corpus_live — live adapter into Charon's
real OEIS battery data.

The synthetic sibling at ``_obstruction_corpus.py`` plants the
OBSTRUCTION_SHAPE signature deterministically. THIS module reads the
ACTUAL data Charon has been generating in
``cartography/convergence/data/`` and exposes it through the same
``CorpusEntry``-shaped interface so ``ObstructionEnv`` can swap between
synthetic and live by toggling a constructor flag.

The live corpus is constructed by joining two of Charon's files:

  asymptotic_deviations.jsonl
    OEIS-style names with the step set parseable from the title
    (Source B in ``a149_obstruction.py``). One row per OEIS sequence.

  battery_sweep_v2.jsonl
    Per-sequence kill records from the falsification battery (Source C
    in ``a149_obstruction.py``). Multiple kill_tests may fire per row;
    the same seq_id can have multiple rows from different battery layers.

The "kill_verdict" used here mirrors Charon's UNANIMOUS_BATTERY: a row
is killed iff *all four* of {F1_permutation_null, F6_base_rate,
F9_simpler_explanation, F11_cross_validation} fired against it. This
is the exact gate that produced the reported 54x lift on the
OBSTRUCTION_SHAPE signature in ``a149_obstruction.py``.

Schema of ``LiveCorpusEntry`` mirrors synthetic ``CorpusEntry``:

  n_steps, neg_x, pos_x, neg_y, pos_y, neg_z, pos_z (int 0..n_steps),
  has_diag_neg, has_diag_pos (bool),
  kill_verdict (bool),
  sequence_id (str, e.g. "A149090") — preserved from OEIS, NOT
    a fake name.

Default file paths use the repo-root data directory; tests can override
via the ``path``/``deviations_path`` arguments.

Skip-clean policy: if either file is missing, ``load_live_corpus`` raises
``FileNotFoundError``. ``get_corpus_or_skip`` wraps this with a
``pytest.skip`` so CI degrades gracefully when the live data isn't
present.
"""
from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Repository paths (resolved relative to this file)
# ---------------------------------------------------------------------------


# Resolve ``<repo>/cartography/convergence/data`` from this file's location.
# This file lives at ``<repo>/prometheus_math/_obstruction_corpus_live.py``;
# go up two levels to reach the repo root.
_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent
DEFAULT_DATA_DIR = _REPO / "cartography" / "convergence" / "data"
DEFAULT_BATTERY_PATH = DEFAULT_DATA_DIR / "battery_sweep_v2.jsonl"
DEFAULT_DEVIATIONS_PATH = DEFAULT_DATA_DIR / "asymptotic_deviations.jsonl"


# ---------------------------------------------------------------------------
# Charon's UNANIMOUS_BATTERY definition — verbatim from a149_obstruction.py.
# A sequence's kill_verdict is True iff every member of this set fired.
# ---------------------------------------------------------------------------


UNANIMOUS_BATTERY: frozenset = frozenset(
    {
        "F1_permutation_null",
        "F6_base_rate",
        "F9_simpler_explanation",
        "F11_cross_validation",
    }
)


# ---------------------------------------------------------------------------
# Step-set parsing — copied from sigma_kernel/a149_obstruction.py so this
# module stays import-light (the sigma_kernel module pulls SigmaKernel,
# sqlite, etc. that we don't need here).
# ---------------------------------------------------------------------------


_STEP_SET_RE = re.compile(r"\{([^}]+)\}")
_STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def parse_step_set(name: str) -> Optional[List[Tuple[int, int, int]]]:
    """Parse step-set out of an OEIS name like:

        'Number of walks within N^3 (the first octant of Z^3) starting
         at (0,0,0) and consisting of n steps taken from
         {(-1, -1, -1), (-1, -1, 0), (-1, 0, 1), (0, 0, -1), (1, 0, 1)}.'

    Returns the list of (dx, dy, dz) tuples, or None if no step set is
    parseable.
    """
    if not name:
        return None
    m = _STEP_SET_RE.search(name)
    if not m:
        return None
    body = m.group(1)
    triples = _STEP_RE.findall(body)
    if not triples:
        return None
    return [tuple(int(x) for x in s) for s in triples]


def features_of(steps: List[Tuple[int, int, int]]) -> Dict[str, Any]:
    """Structural features of a 3-D step set.

    Mirrors ``sigma_kernel/a149_obstruction.py::features_of`` so a
    sequence's signature is identical whether read by Charon or by the
    env.
    """
    n = len(steps)
    nx = sum(1 for s in steps if s[0] < 0)
    ny = sum(1 for s in steps if s[1] < 0)
    nz = sum(1 for s in steps if s[2] < 0)
    px = sum(1 for s in steps if s[0] > 0)
    py = sum(1 for s in steps if s[1] > 0)
    pz = sum(1 for s in steps if s[2] > 0)
    has_diag_neg = any(s == (-1, -1, -1) for s in steps)
    has_diag_pos = any(s == (1, 1, 1) for s in steps)
    return {
        "n_steps": n,
        "neg_x": nx,
        "neg_y": ny,
        "neg_z": nz,
        "pos_x": px,
        "pos_y": py,
        "pos_z": pz,
        "has_diag_neg": has_diag_neg,
        "has_diag_pos": has_diag_pos,
    }


# ---------------------------------------------------------------------------
# Public dataclass — same shape as synthetic CorpusEntry, plus sequence_id.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveCorpusEntry:
    """A single OEIS sequence with parsed step-set features and a
    battery-derived kill verdict.

    Fields mirror synthetic ``CorpusEntry`` so ``ObstructionEnv`` can
    consume both. The added ``sequence_id`` field preserves the OEIS
    A-number (e.g. "A149090") so REINFORCE rediscoveries can be
    audited against the actual sequences.
    """

    n_steps: int
    neg_x: int
    pos_x: int
    neg_y: int
    pos_y: int
    neg_z: int
    pos_z: int
    has_diag_neg: bool
    has_diag_pos: bool
    kill_verdict: bool
    sequence_id: str

    def features(self) -> Dict[str, Any]:
        """Feature dict (no kill_verdict, no sequence_id) — same shape
        as synthetic ``CorpusEntry.features()`` so ``evaluate_predicate``
        works unchanged."""
        return {
            "n_steps": self.n_steps,
            "neg_x": self.neg_x,
            "pos_x": self.pos_x,
            "neg_y": self.neg_y,
            "pos_y": self.pos_y,
            "neg_z": self.neg_z,
            "pos_z": self.pos_z,
            "has_diag_neg": self.has_diag_neg,
            "has_diag_pos": self.has_diag_pos,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# JSONL loader (lenient) + battery-merge
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> Tuple[List[Dict[str, Any]], int]:
    """Read a JSONL file. Skip blank lines and malformed JSON with
    a warning; return (rows, n_skipped)."""
    if not path.exists():
        raise FileNotFoundError(str(path))
    rows: List[Dict[str, Any]] = []
    n_skipped = 0
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                n_skipped += 1
                logger.warning(
                    "skipping malformed JSONL line %d in %s: %s",
                    lineno,
                    path.name,
                    e,
                )
                continue
    return rows, n_skipped


def _kills_by_seq_id(battery_rows: List[Dict[str, Any]]) -> Dict[str, set]:
    """Aggregate the union of kill_tests per seq_id across the battery."""
    out: Dict[str, set] = defaultdict(set)
    for r in battery_rows:
        sid = r.get("seq_id")
        if not sid:
            continue
        kt = r.get("kill_tests") or []
        out[sid].update(kt)
    return out


# ---------------------------------------------------------------------------
# Main loader
# ---------------------------------------------------------------------------


def load_live_corpus(
    path: Optional[os.PathLike] = None,
    deviations_path: Optional[os.PathLike] = None,
    a_number_prefix: Optional[str] = "A14",
    require_steps: bool = True,
) -> List[LiveCorpusEntry]:
    """Construct the live corpus by joining battery_sweep_v2 and
    asymptotic_deviations.

    Parameters
    ----------
    path : path-like, optional
        Path to ``battery_sweep_v2.jsonl``. Defaults to
        ``DEFAULT_BATTERY_PATH``.
    deviations_path : path-like, optional
        Path to ``asymptotic_deviations.jsonl``. Defaults to
        ``DEFAULT_DEVIATIONS_PATH``.
    a_number_prefix : str, optional
        Restrict to OEIS sequences whose seq_id starts with this prefix.
        Default ``"A14"`` covers the A148/A149 octant-walk family
        Charon studied; pass ``None`` for no filter.
    require_steps : bool
        If True (default), drop rows whose step set can't be parsed
        from the OEIS name. Empirically every A14x* row has a
        parseable step set; we keep the flag for testability with
        bespoke fixtures.

    Returns
    -------
    list[LiveCorpusEntry]
        Sorted by sequence_id ascending so reads are reproducible.

    Raises
    ------
    FileNotFoundError
        If either file is missing.
    ValueError
        If the resulting corpus is empty (e.g. empty input file).
    """
    bpath = Path(path) if path is not None else DEFAULT_BATTERY_PATH
    dpath = (
        Path(deviations_path)
        if deviations_path is not None
        else DEFAULT_DEVIATIONS_PATH
    )

    # Load both files (raises FileNotFoundError if missing).
    battery_rows, battery_skipped = _load_jsonl(bpath)
    deviation_rows, deviation_skipped = _load_jsonl(dpath)

    if battery_skipped:
        logger.info("battery_sweep_v2: %d malformed lines skipped", battery_skipped)
    if deviation_skipped:
        logger.info(
            "asymptotic_deviations: %d malformed lines skipped",
            deviation_skipped,
        )

    kills = _kills_by_seq_id(battery_rows)

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
        if a_number_prefix is not None and not sid.startswith(a_number_prefix):
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
        seq_kill_tests = kills.get(sid, set())
        kill_verdict = UNANIMOUS_BATTERY.issubset(seq_kill_tests)

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
            f"live corpus empty: 0 entries kept "
            f"(no_seq_id={n_no_seq_id}, wrong_prefix={n_wrong_prefix}, "
            f"no_steps={n_no_steps}); battery_path={bpath}, "
            f"deviations_path={dpath}"
        )

    # Reproducibility: deterministic order by sequence_id.
    entries.sort(key=lambda e: e.sequence_id)

    logger.info(
        "live_corpus: %d entries kept "
        "(skipped: no_seq_id=%d, wrong_prefix=%d, no_steps=%d, dups=%d, "
        "battery_malformed=%d, deviations_malformed=%d)",
        len(entries),
        n_no_seq_id,
        n_wrong_prefix,
        n_no_steps,
        n_dups,
        battery_skipped,
        deviation_skipped,
    )
    return entries


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def live_corpus_summary(corpus: List[LiveCorpusEntry]) -> Dict[str, Any]:
    """Sanity-check summary of the live corpus."""
    n_total = len(corpus)
    if n_total == 0:
        return {
            "n_total": 0,
            "n_killed": 0,
            "kill_rate": 0.0,
            "feature_value_distribution": {},
            "by_a_number_prefix": {},
        }
    n_killed = sum(1 for e in corpus if e.kill_verdict)
    kill_rate = n_killed / n_total

    # Per-feature value frequency (small histogram — useful for review).
    from collections import Counter

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
        # Sort keys for stable pretty-print.
        value_dist[feat] = dict(sorted(c.items(), key=lambda kv: (str(type(kv[0])), kv[0])))

    # Coarse OEIS-prefix bucket (e.g. "A148" vs "A149").
    prefix_counts: Counter = Counter()
    for e in corpus:
        prefix_counts[e.sequence_id[:4]] += 1
    by_prefix = dict(sorted(prefix_counts.items()))

    return {
        "n_total": n_total,
        "n_killed": n_killed,
        "kill_rate": kill_rate,
        "feature_value_distribution": value_dist,
        "by_a_number_prefix": by_prefix,
    }


def _matches_predicate(
    entry: LiveCorpusEntry, predicate: Dict[str, Any]
) -> bool:
    if not predicate:
        return True
    feats = entry.features()
    for k, v in predicate.items():
        if feats.get(k) != v:
            return False
    return True


def obstruction_signature_lift_on_live(
    corpus: List[LiveCorpusEntry],
    signature: Dict[str, Any],
) -> Dict[str, Any]:
    """Echo of Charon's predictive-test step against the live corpus.

    Computes the kill-rate among rows matching the signature vs the
    kill-rate among the rest, and reports the ratio (Charon's "lift").

    A signature {n_steps:5, neg_x:4, pos_x:1, has_diag_neg:True} on the
    A14x corpus should reproduce Charon's 54x finding from
    ``a149_obstruction.py`` step [4].

    Returns
    -------
    dict
        match_kill_rate, non_match_kill_rate, lift, n_match, n_non_match,
        n_total, match_sequence_ids (the OEIS A-numbers in the match
        group — substrate-grade evidence for tagged discoveries).
    """
    n_total = len(corpus)
    matches = [e for e in corpus if _matches_predicate(e, signature)]
    non_matches = [e for e in corpus if not _matches_predicate(e, signature)]
    n_match = len(matches)
    n_non_match = len(non_matches)

    match_kill_rate = (
        sum(1 for e in matches if e.kill_verdict) / n_match
        if n_match > 0
        else 0.0
    )
    non_match_kill_rate = (
        sum(1 for e in non_matches if e.kill_verdict) / n_non_match
        if n_non_match > 0
        else 0.0
    )

    if n_match == 0:
        lift = 0.0
    elif non_match_kill_rate <= 1e-12:
        # Same convention as evaluate_predicate: cap via implicit 1e-6 floor
        # if matches kill but no non-matches do, else lift = 0.
        if match_kill_rate > 0:
            lift = match_kill_rate / 1e-6
        else:
            lift = 0.0
    else:
        lift = match_kill_rate / non_match_kill_rate

    return {
        "match_kill_rate": float(match_kill_rate),
        "non_match_kill_rate": float(non_match_kill_rate),
        "lift": float(lift),
        "n_match": int(n_match),
        "n_non_match": int(n_non_match),
        "n_total": int(n_total),
        "match_sequence_ids": [e.sequence_id for e in matches],
    }


# ---------------------------------------------------------------------------
# Skip-clean helper for tests
# ---------------------------------------------------------------------------


def get_corpus_or_skip(
    path: Optional[os.PathLike] = None,
    deviations_path: Optional[os.PathLike] = None,
    a_number_prefix: Optional[str] = "A14",
) -> List[LiveCorpusEntry]:
    """Load the live corpus or skip the calling pytest test if data is missing.

    If pytest is not importable (running outside pytest), raises the
    underlying FileNotFoundError instead.
    """
    try:
        return load_live_corpus(
            path=path,
            deviations_path=deviations_path,
            a_number_prefix=a_number_prefix,
        )
    except FileNotFoundError as e:
        try:
            import pytest  # type: ignore
        except ImportError:
            raise
        pytest.skip(f"live corpus data file missing: {e}")
        # pragma: no cover — pytest.skip raises Skipped
        raise


__all__ = [
    "LiveCorpusEntry",
    "UNANIMOUS_BATTERY",
    "DEFAULT_BATTERY_PATH",
    "DEFAULT_DEVIATIONS_PATH",
    "DEFAULT_DATA_DIR",
    "parse_step_set",
    "features_of",
    "load_live_corpus",
    "live_corpus_summary",
    "obstruction_signature_lift_on_live",
    "get_corpus_or_skip",
]
