"""prometheus_math._oeis_prefix_extension — pre-extend Charon's
OBSTRUCTION_SHAPE corpus to OEIS prefixes the real falsification battery
hasn't visited (A152*, A153*, A154*, A155*).

Background
----------

The Stream-C surrogate, calibrated against Charon's A149 ground truth,
classifies a sequence as kill-equivalent iff::

    delta_pct > 50.0  AND  regime_change is True

On the 5 unanimous-killed A149 anchors, this rule has 100% precision
and 100% recall vs the real F1+F6+F9+F11 battery. It is not a substitute
for that battery — it is a structural-anomaly proxy that PRE-FILTERS
candidates worth running the real battery on.

The base extended loader (``_obstruction_corpus_extended.py``) covers
A148/A149/A150/A151 because those prefixes appear in
``cartography/convergence/data/asymptotic_deviations.jsonl``. This
module extends to A152*/A153*/A154*/A155*, which DON'T appear in
that file. We reach them via ``prometheus_math.databases.oeis``
(local mirror, no API hit) and synthesize the deviation fields
(``short_rate``, ``long_rate``, ``delta_pct``, ``regime_change``)
from the raw integer-data terms using the same definitions Charon's
asymptotic_deviations pipeline uses:

  * ``short_rate``   — log-ratio fit on the first half of the data.
  * ``long_rate``    — log-ratio fit on the second half.
  * ``delta_pct``    — ``100 * (long_rate - short_rate) / short_rate``.
  * ``regime_change``— True iff ``|delta_pct| > 5%`` AND short/long
                       rates are both finite/positive.

Honest framing (mirrors the surrogate's docstring): A152-A155 are
sparse OEIS prefixes that don't sample the 3-D octant lattice-walk
family Charon's anchors live in. Most sequences will have no parseable
step set. We still extract growth-rate features so the brute-force
signature enumerator has something to chew on; whether any
high-lift signature emerges is the empirical question this module
answers.

Public API
----------

``pull_oeis_prefix(prefix, max_sequences) -> list[OeisRawEntry]``
``compute_surrogate_kill(features) -> bool``
``extend_corpus_with_surrogate(prefixes, max_per_prefix) -> ExtendedCorpus``
``enumerate_signatures(corpus, max_complexity) -> list[(predicate, lift, n_match)]``
"""
from __future__ import annotations

import dataclasses
import itertools
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ._obstruction_corpus_extended import (
    SURROGATE_DELTA_PCT_THRESHOLD,
    surrogate_kill_verdict,
)
from ._obstruction_corpus_live import (
    DEFAULT_DEVIATIONS_PATH,
    LiveCorpusEntry,
    _load_jsonl,
    features_of,
    parse_step_set,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants and feature-schema layouts
# ---------------------------------------------------------------------------


# The four prefixes outside Charon's A14* core that this module extends to.
DEFAULT_NEW_PREFIXES: Tuple[str, ...] = ("A152", "A153", "A154", "A155")


# Minimum integer-data terms required to fit short/long rates. Below this
# the regime-change inference is statistical noise.
MIN_TERMS_FOR_RATE_FIT: int = 8


# regime_change threshold (mirrors the convention in
# asymptotic_deviations.jsonl — empirically Charon flags entries whose
# |delta_pct| exceeds ~5%, but the kill-rule (>50%) is what matters).
REGIME_CHANGE_DELTA_THRESHOLD: float = 5.0


# Lattice-walk feature keys — the schema ObstructionEnv consumes.
LATTICE_FEATURE_KEYS: Tuple[str, ...] = (
    "n_steps",
    "neg_x",
    "pos_x",
    "neg_y",
    "pos_y",
    "neg_z",
    "pos_z",
    "has_diag_neg",
    "has_diag_pos",
)


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OeisRawEntry:
    """Raw OEIS record after local-mirror pull.

    ``a_number`` is the canonical 'A000045'-style id.
    ``data`` is the integer-data prefix (typically 30-50 terms).
    ``name`` is the OEIS name field.
    """

    a_number: str
    name: str
    data: Tuple[int, ...]


@dataclass(frozen=True)
class SurrogateRecord:
    """One sequence's surrogate-battery record.

    Contains both:
      * ``deviation_record`` — a dict with the synthesized
        ``short_rate``/``long_rate``/``delta_pct``/``regime_change``
        fields, in the exact shape ``surrogate_kill_verdict`` consumes.
      * ``features`` — feature dict in lattice-walk schema if the OEIS
        name parses as a step-set; otherwise an empty dict (callers
        should skip it from lattice-walk signature enumeration).
      * ``kill_verdict`` — output of the calibrated rule.
      * ``parseable_step_set`` — True if features comes from a parseable
        N^3 step-set; False otherwise.
    """

    a_number: str
    prefix: str
    name: str
    n_terms: int
    deviation_record: Dict[str, Any]
    features: Dict[str, Any]
    kill_verdict: bool
    parseable_step_set: bool


@dataclass
class ExtendedCorpus:
    """Surrogate-extended corpus across multiple OEIS prefixes.

    ``entries_lattice`` are LiveCorpusEntry-shaped records (parseable
    step-sets only) — these flow into ObstructionEnv and the existing
    ``obstruction_signature_lift_on_live``.

    ``entries_general`` are SurrogateRecords (any sequence; lattice
    features may be empty). The brute-force signature enumerator
    accepts EITHER list — the predicate-evaluation path is uniform on
    feature dicts.

    ``skip_count`` reports per-prefix how many sequences were skipped
    (no integer data, too few terms, malformed, etc.) and the reason.
    """

    entries_lattice: List[LiveCorpusEntry] = field(default_factory=list)
    entries_general: List[SurrogateRecord] = field(default_factory=list)
    per_prefix_total: Dict[str, int] = field(default_factory=dict)
    per_prefix_lattice: Dict[str, int] = field(default_factory=dict)
    per_prefix_killed: Dict[str, int] = field(default_factory=dict)
    skip_count: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Step 1 — pull OEIS prefix
# ---------------------------------------------------------------------------


def pull_oeis_prefix(
    prefix: str, max_sequences: int = 50
) -> List[OeisRawEntry]:
    """Pull the first ``max_sequences`` records of an OEIS prefix.

    Resolution order:
      1. Local mirror (no network) if available.
      2. Live API via ``oeis.lookup`` (one A-number at a time, throttled).

    The local mirror covers ~395K A-numbers including all of A152-A155
    in our environment; the live fallback is mostly for CI envs without
    the mirror parsed.

    Returns an empty list cleanly on:
      * unreachable mirror AND unreachable API,
      * no A-numbers under the requested prefix.

    Skip-clean: never raises on network failure; the surrogate pipeline
    must degrade gracefully.
    """
    from .databases import oeis

    out: List[OeisRawEntry] = []

    # Path 1 — local mirror (cheap, no network).
    if oeis.has_local_mirror():
        cache = oeis._OEIS_LOCAL_CACHE  # type: ignore[attr-defined]
        keys = sorted(k for k in cache if k.startswith(prefix))
        for k in keys[:max_sequences]:
            rec = cache[k]
            data = tuple(int(x) for x in rec.get("data", []) or [])
            name = rec.get("name", "") or ""
            out.append(OeisRawEntry(a_number=k, name=name, data=data))
        return out

    # Path 2 — live API. Polite + throttled.
    n = 0
    base_int = int(prefix[1:]) * 1000  # A152 -> 152000
    for offset in range(max_sequences * 4):  # generous cap on misses
        if n >= max_sequences:
            break
        a_id = f"A{base_int + offset:06d}"
        rec = oeis.lookup(a_id)
        if rec is None:
            continue
        data = tuple(int(x) for x in rec.get("data", []) or [])
        out.append(
            OeisRawEntry(a_number=a_id, name=rec.get("name", "") or "", data=data)
        )
        n += 1
    return out


# ---------------------------------------------------------------------------
# Step 2 — synthesize asymptotic deviation fields from raw data
# ---------------------------------------------------------------------------


def _safe_log_rate(values: Sequence[int]) -> Optional[float]:
    """Estimate the asymptotic log-growth rate r of a positive integer
    sequence: a(n) ~ C * exp(r*n). Linear fit of log|a(n)| vs n.

    Returns None if fewer than 3 finite log-values are available, all
    zeros, or the values are not strictly positive after filtering.
    """
    xs: List[float] = []
    ys: List[float] = []
    for i, v in enumerate(values):
        if v <= 0:
            continue
        try:
            ly = math.log(float(v))
        except (ValueError, OverflowError):
            continue
        if not math.isfinite(ly):
            continue
        xs.append(float(i))
        ys.append(ly)
    if len(xs) < 3:
        return None
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom <= 0.0:
        return None
    slope = (n * sxy - sx * sy) / denom
    if not math.isfinite(slope):
        return None
    return float(slope)


def synthesize_deviation_record(
    data: Sequence[int],
    name: str = "",
    seq_id: str = "",
) -> Dict[str, Any]:
    """Compute the asymptotic-deviation record for a raw integer sequence.

    Mirrors the field shape of ``asymptotic_deviations.jsonl``:

        {
          "seq_id": str,
          "name":   str,
          "n_terms": int,
          "short_rate": float | None,
          "long_rate":  float | None,
          "delta_pct":  float | None,
          "regime_change": bool,
        }

    The split is half/half on the available data prefix. Returns None
    fields when fewer than ``MIN_TERMS_FOR_RATE_FIT`` terms are
    available — the surrogate kill rule then treats the entry as
    'no anomaly information, presumed not killed'.
    """
    n = len(data)
    out: Dict[str, Any] = {
        "seq_id": seq_id,
        "name": name,
        "n_terms": n,
        "short_rate": None,
        "long_rate": None,
        "delta_pct": None,
        "regime_change": False,
    }
    if n < MIN_TERMS_FOR_RATE_FIT:
        return out
    # Halve the sequence; both halves need >= 3 positive terms for the rate fit.
    half = n // 2
    short = list(data[:half])
    long_ = list(data[half:])
    r_short = _safe_log_rate(short)
    r_long = _safe_log_rate(long_)
    if r_short is None or r_long is None:
        return out
    out["short_rate"] = float(r_short)
    out["long_rate"] = float(r_long)
    if abs(r_short) < 1e-9:
        # Cap delta_pct at infinity-marker so downstream compares cleanly.
        return out
    delta = 100.0 * (r_long - r_short) / abs(r_short)
    out["delta_pct"] = float(delta)
    out["regime_change"] = bool(abs(delta) > REGIME_CHANGE_DELTA_THRESHOLD)
    return out


def compute_surrogate_kill(features_or_record: Dict[str, Any]) -> bool:
    """Apply the calibrated surrogate kill rule.

    Rule: ``delta_pct > 50.0  AND  regime_change is True``

    Accepts either a deviation_record (with ``delta_pct`` /
    ``regime_change`` keys) or any dict with those keys. This is the
    EXACT calibration Stream C demonstrated had 100% precision +
    100% recall on Charon's A149 ground truth — delegated to
    ``_obstruction_corpus_extended.surrogate_kill_verdict``.
    """
    return surrogate_kill_verdict(features_or_record)


# ---------------------------------------------------------------------------
# Curated deviations cache (from asymptotic_deviations.jsonl)
# ---------------------------------------------------------------------------


_CURATED_DEVIATIONS: Optional[Dict[str, Dict[str, Any]]] = None


def _load_curated_deviations() -> Dict[str, Dict[str, Any]]:
    """Load Charon's ``asymptotic_deviations.jsonl`` and index by seq_id.

    Cached on first call. Empty dict if the file is missing.

    These records are the calibration ground-truth: applying
    ``compute_surrogate_kill`` to them recovers Charon's 5 A149
    anchors at 100% precision/recall (Stream C verification).
    """
    global _CURATED_DEVIATIONS
    if _CURATED_DEVIATIONS is not None:
        return _CURATED_DEVIATIONS
    out: Dict[str, Dict[str, Any]] = {}
    try:
        rows, _ = _load_jsonl(DEFAULT_DEVIATIONS_PATH)
    except FileNotFoundError:
        _CURATED_DEVIATIONS = out
        return out
    for r in rows:
        sid = r.get("seq_id")
        if sid:
            out[sid] = r
    _CURATED_DEVIATIONS = out
    return out


def get_deviation_record(
    seq_id: str,
    name: str,
    data: Sequence[int],
) -> Tuple[Dict[str, Any], str]:
    """Return ``(deviation_record, source)`` for a sequence.

    Resolution order:
      1. Curated record from ``asymptotic_deviations.jsonl`` if present
         for this seq_id. ``source = "curated"``. This is the EXACT
         calibration Stream C used.
      2. Synthesized record from raw integer data via
         ``synthesize_deviation_record``. ``source = "synthesized"``.

    A149 sequences will hit path 1 (curated) so the test
    ``surrogate_kill_verdict matches Charon's ground truth`` works
    unchanged.
    """
    curated = _load_curated_deviations()
    if seq_id in curated:
        return dict(curated[seq_id]), "curated"
    return synthesize_deviation_record(data, name=name, seq_id=seq_id), "synthesized"


# ---------------------------------------------------------------------------
# Step 3 — extend the corpus
# ---------------------------------------------------------------------------


def extend_corpus_with_surrogate(
    prefixes: Optional[Sequence[str]] = None,
    max_per_prefix: int = 50,
) -> ExtendedCorpus:
    """Pull each prefix and produce an ``ExtendedCorpus``.

    Lattice-walk-parseable sequences become ``LiveCorpusEntry`` records
    in ``entries_lattice``. ALL sequences (including those with no
    parseable step set) are stored as ``SurrogateRecord`` in
    ``entries_general`` for the brute-force enumerator.

    Skip-clean:
      * Empty data → counted under skip_count[prefix] and dropped
        from both lists (no rate fit possible).
      * Too few data terms (< MIN_TERMS_FOR_RATE_FIT) → still produces
        a SurrogateRecord with kill_verdict=False; counted as
        'shallow_data' in skip_count for transparency, kept in
        entries_general so the enumerator sees the row.
    """
    if prefixes is None:
        prefixes = DEFAULT_NEW_PREFIXES
    prefixes = list(prefixes)
    if not prefixes:
        raise ValueError("prefixes must be a non-empty list")
    if max_per_prefix <= 0:
        raise ValueError("max_per_prefix must be positive")

    corpus = ExtendedCorpus()
    for prefix in prefixes:
        raw = pull_oeis_prefix(prefix, max_sequences=max_per_prefix)
        n_total = 0
        n_lattice = 0
        n_killed = 0
        n_skipped_no_data = 0
        n_skipped_shallow = 0
        for r in raw:
            n_total += 1
            if not r.data:
                n_skipped_no_data += 1
                continue
            dev, _src = get_deviation_record(r.a_number, r.name, r.data)
            kill = compute_surrogate_kill(dev)
            steps = parse_step_set(r.name) if r.name else None
            parseable = bool(steps) and all(len(s) == 3 for s in steps)
            if parseable:
                feats = features_of(steps)  # type: ignore[arg-type]
            else:
                feats = {}
            if dev.get("delta_pct") is None:
                n_skipped_shallow += 1
            corpus.entries_general.append(
                SurrogateRecord(
                    a_number=r.a_number,
                    prefix=prefix,
                    name=r.name,
                    n_terms=len(r.data),
                    deviation_record=dev,
                    features=feats,
                    kill_verdict=kill,
                    parseable_step_set=parseable,
                )
            )
            if parseable:
                n_lattice += 1
                corpus.entries_lattice.append(
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
                        kill_verdict=bool(kill),
                        sequence_id=r.a_number,
                    )
                )
            if kill:
                n_killed += 1
        corpus.per_prefix_total[prefix] = n_total
        corpus.per_prefix_lattice[prefix] = n_lattice
        corpus.per_prefix_killed[prefix] = n_killed
        corpus.skip_count[prefix] = n_skipped_no_data + n_skipped_shallow
        logger.info(
            "prefix=%s pulled=%d lattice=%d killed=%d skipped(no_data=%d, shallow=%d)",
            prefix,
            n_total,
            n_lattice,
            n_killed,
            n_skipped_no_data,
            n_skipped_shallow,
        )
    return corpus


# ---------------------------------------------------------------------------
# Step 4 — brute-force signature enumeration
# ---------------------------------------------------------------------------


def _evaluate_signature(
    predicate: Dict[str, Any],
    records_with_features: List[Tuple[Dict[str, Any], bool]],
) -> Tuple[float, int, int]:
    """Return (lift, n_match, n_killed_in_match) for a predicate over a
    list of (features, kill_verdict) pairs.

    Lift convention mirrors ``obstruction_signature_lift_on_live``:
      lift = match_kill_rate / non_match_kill_rate

    Returns ``lift = 0.0`` when n_match == 0; uses 1e-6 floor when
    non_match_kill_rate is 0 to keep the channel finite.
    """
    matches: List[bool] = []
    nonmatches: List[bool] = []
    for feats, kill in records_with_features:
        ok = True
        for k, v in predicate.items():
            if feats.get(k) != v:
                ok = False
                break
        if ok:
            matches.append(kill)
        else:
            nonmatches.append(kill)
    n_m = len(matches)
    n_n = len(nonmatches)
    if n_m == 0:
        return 0.0, 0, 0
    match_rate = sum(1 for k in matches if k) / n_m
    non_rate = (sum(1 for k in nonmatches if k) / n_n) if n_n > 0 else 0.0
    if non_rate <= 1e-12:
        if match_rate > 0:
            lift = match_rate / 1e-6
        else:
            lift = 0.0
    else:
        lift = match_rate / non_rate
    n_killed_in_match = sum(1 for k in matches if k)
    return float(lift), int(n_m), int(n_killed_in_match)


def _candidate_value_table(
    records_with_features: List[Tuple[Dict[str, Any], bool]]
) -> Dict[str, List[Any]]:
    """Build per-feature candidate value lists from observed values.

    For boolean features → [False, True] (always both).
    For int/scalar features → sorted unique observed values.
    """
    seen: Dict[str, set] = {}
    for feats, _ in records_with_features:
        for k, v in feats.items():
            seen.setdefault(k, set()).add(v)
    out: Dict[str, List[Any]] = {}
    for k, vs in seen.items():
        # Stable ordering: bools first, then sorted ints, then sorted others.
        try:
            sorted_vs = sorted(vs)
        except TypeError:
            sorted_vs = list(vs)
        out[k] = sorted_vs
    return out


def enumerate_signatures(
    corpus: List[Tuple[Dict[str, Any], bool]],
    max_complexity: int = 3,
    min_match_size: int = 1,
) -> List[Tuple[Dict[str, Any], float, int]]:
    """Brute-force signature search over a (features, kill) corpus.

    Returns ``(predicate, lift, n_match)`` triples ordered by lift
    descending. Determinism: all loops iterate in stable orderings.

    Complexity enumeration:
      * complexity 0 → empty predicate (matches all; lift=1.0).
      * complexity 1 → single (feature, value) conjunct.
      * complexity 2 → ordered pair of distinct features.
      * complexity 3 → ordered triple of distinct features.

    For tractability the value table is restricted to OBSERVED values
    only — we never test impossible combinations.

    ``min_match_size`` filters out signatures with vanishing
    match-groups (default 1: keep any signature that matches at least
    one record). Set higher to reduce noise from outlier rows.

    Edge cases:
      * Empty corpus → returns an empty list.
      * max_complexity = 0 → returns exactly one entry: empty predicate.
    """
    if max_complexity < 0:
        raise ValueError("max_complexity must be >= 0")
    if not corpus:
        return []
    table = _candidate_value_table(corpus)
    feature_keys = sorted(table.keys())

    seen_predicates: set = set()
    out: List[Tuple[Dict[str, Any], float, int]] = []

    def _emit(pred: Dict[str, Any]) -> None:
        # Canonical key for de-dup: sorted tuple of items.
        key = tuple(sorted((k, v) for k, v in pred.items()))
        if key in seen_predicates:
            return
        seen_predicates.add(key)
        lift, n_m, _ = _evaluate_signature(pred, corpus)
        if n_m < min_match_size:
            return
        out.append((dict(pred), float(lift), int(n_m)))

    # complexity 0
    if max_complexity == 0:
        # Only emit the trivial predicate.
        _emit({})
        return out

    # complexity 1
    for f in feature_keys:
        for v in table[f]:
            _emit({f: v})

    # complexity 2..max
    if max_complexity >= 2:
        for f1, f2 in itertools.combinations(feature_keys, 2):
            for v1 in table[f1]:
                for v2 in table[f2]:
                    _emit({f1: v1, f2: v2})

    if max_complexity >= 3:
        for f1, f2, f3 in itertools.combinations(feature_keys, 3):
            for v1 in table[f1]:
                for v2 in table[f2]:
                    for v3 in table[f3]:
                        _emit({f1: v1, f2: v2, f3: v3})

    # higher complexities: explicit refusal — combinatorial blowup.
    if max_complexity > 3:
        raise NotImplementedError(
            "max_complexity > 3 not supported (combinatorial blowup); "
            "use REINFORCE in obstruction_env for higher orders"
        )

    out.sort(key=lambda t: (-t[1], -t[2], tuple(sorted(t[0].items()))))
    return out


# ---------------------------------------------------------------------------
# Step 5 — convenience: signatures per prefix + aggregate
# ---------------------------------------------------------------------------


def signatures_per_prefix(
    corpus: ExtendedCorpus,
    max_complexity: int = 3,
    top_k: int = 5,
    min_match_size: int = 2,
) -> Dict[str, List[Tuple[Dict[str, Any], float, int]]]:
    """Compute the top-k signatures within each prefix individually.

    Honours ``min_match_size=2`` by default — single-record matches
    almost always have lift = match_rate / 1e-6 = huge, but they're
    not signal, so the default filters them out for the per-prefix
    summary. Use ``min_match_size=1`` to keep them.

    Returns an empty list for prefixes with empty entries_general.
    """
    by_prefix: Dict[str, List[Tuple[Dict[str, Any], bool]]] = {}
    for rec in corpus.entries_general:
        # Use lattice features when present; otherwise the deviation_record
        # fields (n_terms, has-anomaly flag, regime_change) become the
        # backstop feature schema.
        if rec.parseable_step_set:
            feats = dict(rec.features)
        else:
            feats = _general_feature_dict(rec)
        by_prefix.setdefault(rec.prefix, []).append((feats, rec.kill_verdict))
    out: Dict[str, List[Tuple[Dict[str, Any], float, int]]] = {}
    for prefix, recs in by_prefix.items():
        sigs = enumerate_signatures(
            recs, max_complexity=max_complexity, min_match_size=min_match_size
        )
        out[prefix] = sigs[:top_k]
    return out


def _general_feature_dict(rec: SurrogateRecord) -> Dict[str, Any]:
    """Backstop feature schema for sequences without a parseable
    step-set.

    Provides enough discrete features for the brute-force enumerator
    to find structural patterns:

      * ``n_terms_bucket`` — bucketed term-count.
      * ``has_anomaly``    — proxy for delta_pct > 5%.
      * ``regime_change``  — direct from deviation record.
      * ``rate_sign``      — sign of long_rate when present.
    """
    n = rec.n_terms
    if n < 8:
        n_bucket = "tiny"
    elif n < 16:
        n_bucket = "short"
    elif n < 32:
        n_bucket = "medium"
    else:
        n_bucket = "long"
    delta = rec.deviation_record.get("delta_pct")
    has_anomaly = bool(delta is not None and abs(delta) > 5.0)
    long_rate = rec.deviation_record.get("long_rate")
    if long_rate is None:
        rate_sign = "none"
    elif long_rate > 0:
        rate_sign = "pos"
    elif long_rate < 0:
        rate_sign = "neg"
    else:
        rate_sign = "zero"
    return {
        "n_terms_bucket": n_bucket,
        "has_anomaly": has_anomaly,
        "regime_change": bool(rec.deviation_record.get("regime_change", False)),
        "rate_sign": rate_sign,
    }


# ---------------------------------------------------------------------------
# Pipeline summary
# ---------------------------------------------------------------------------


def extended_pipeline_summary(corpus: ExtendedCorpus) -> Dict[str, Any]:
    """Compact dict reporting per-prefix coverage, kill rates, and the
    general (non-lattice) row counts."""
    return {
        "n_lattice_total": len(corpus.entries_lattice),
        "n_general_total": len(corpus.entries_general),
        "per_prefix_total": dict(corpus.per_prefix_total),
        "per_prefix_lattice": dict(corpus.per_prefix_lattice),
        "per_prefix_killed": dict(corpus.per_prefix_killed),
        "per_prefix_skipped": dict(corpus.skip_count),
    }


__all__ = [
    "DEFAULT_NEW_PREFIXES",
    "MIN_TERMS_FOR_RATE_FIT",
    "REGIME_CHANGE_DELTA_THRESHOLD",
    "OeisRawEntry",
    "SurrogateRecord",
    "ExtendedCorpus",
    "pull_oeis_prefix",
    "synthesize_deviation_record",
    "compute_surrogate_kill",
    "get_deviation_record",
    "extend_corpus_with_surrogate",
    "enumerate_signatures",
    "signatures_per_prefix",
    "extended_pipeline_summary",
]
