"""Pipeline-D data filter (W3.7) — morphology-based pre-filter.

Per pivot/ergon_learner_v0.5_design_2026-05-05.md §5 W3.7 + §3.4 Aporia
artifact 3. Filters the 17-entry boundary layer + synthetic env outputs
through Charon's surviving_claim_morphology classifier
(charon/diagnostics/surviving_claim_morphology.json) and drops records
flagged as ``battery_blind_spot`` or ``template_overfitting`` before the
W4.1 / W4.2 LoRA tire-kick.

CLOSED-LOOP BIAS (per Aporia 2026-05-05 sign-off + Techne smaller-concern #5)
----------------------------------------------------------------------------
Charon's classifier was itself trained on substrate verdicts. If we filter
Ergon's training corpus through it, Ergon learns a constrained subset of
substrate-blessed records — i.e., the filter is potentially a closed loop
between substrate verdict and Learner training signal. Mitigation discipline
shipped with this module:

1. Per-class drop counts logged so the W6.1 dossier can quote the bias size.
2. ``filter_corpus`` always emits BOTH the filtered and the unfiltered
   corpus so W4.1 can run a parallel control. The control is the
   substrate-grade defense: if filtered and unfiltered runs agree, the
   classifier wasn't doing meaningful work; if they disagree, the gap
   measures the bias the filter introduced.
3. INDETERMINATE records are RETAINED with a metadata flag (per spec) —
   silence is not evidence.

GENERALIZATION CAVEAT
---------------------
The classifier's feature space is *A149 lattice-walk geometry* (has_diag_*,
n_steps_5, axis_asymmetry, regime_change, delta_pct_high, known_count_low,
best_model). The 17-entry Lehmer boundary layer's feature space is poly
coefficients + Mahler measure — disjoint. For records that don't expose
the classifier's features, classification falls back to INDETERMINATE
(retained). Documented in W6.1 as a ``filter_was_no_op`` event when it
fires; not a silent failure.

Per Charon's own SURVIVING_CLAIM_MORPHOLOGY_REPORT.md honesty notes: the
4 classes collapse to mostly INDETERMINATE under the current
single-domain (n=100) data; ``productive_morphology`` has no feature
support at all in the shipped JSON. This module honours that limitation:
``productive_morphology`` is reachable only via explicit positive-prior
feature scoring (currently empty); records can't be promoted to that
class on flimsy evidence.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

# ---------------------------------------------------------------------------
# Constants — class names per spec (NOT Charon's internal names)
# ---------------------------------------------------------------------------

CLASS_PRODUCTIVE = "productive_morphology"
CLASS_BATTERY_BLIND_SPOT = "battery_blind_spot"
CLASS_THIN_DATA_ARTIFACT = "thin_data_artifact"
CLASS_TEMPLATE_OVERFITTING = "template_overfitting"
CLASS_INDETERMINATE = "INDETERMINATE"

# Charon JSON's per-feature classifications -> spec class names.
# Charon's "indeterminate" maps to battery_blind_spot per spec wording
# (the substrate has nothing to say about these features = blind spot).
_CHARON_TO_SPEC = {
    "overfitting": CLASS_TEMPLATE_OVERFITTING,
    "thin_data": CLASS_THIN_DATA_ARTIFACT,
    "indeterminate": CLASS_BATTERY_BLIND_SPOT,
    "productive": CLASS_PRODUCTIVE,  # not present in current JSON; kept for forward-compat
}

DEFAULT_CLASSIFIER_PATH = Path("charon/diagnostics/surviving_claim_morphology.json")
DEFAULT_DROP_CLASSES: tuple[str, ...] = (CLASS_BATTERY_BLIND_SPOT, CLASS_TEMPLATE_OVERFITTING)


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FeatureRule:
    """A single feature -> class verdict, derived from Charon's per-(feature,
    outcome) rows by majority vote across outcomes."""
    feature: str
    spec_class: str
    n_total: int
    rationale: str


@dataclass(frozen=True)
class Classifier:
    """The morphology classifier as loaded from Charon's JSON.

    ``rules`` is a {feature_name -> FeatureRule} map (one verdict per feature,
    aggregated across outcomes). ``meta`` carries provenance for downstream
    logging. ``feature_extractors`` is the order-preserving list of feature
    names this classifier knows how to score; records lacking ALL of them
    return INDETERMINATE.
    """
    rules: Mapping[str, FeatureRule]
    feature_extractors: tuple[str, ...]
    meta: Mapping[str, Any] = field(default_factory=dict)


def load_morphology_classifier(
    path: Path | str = DEFAULT_CLASSIFIER_PATH,
) -> Classifier:
    """Load Charon's surviving_claim_morphology.json into a Classifier.

    The JSON ships per-(feature, outcome) rows with a ``classification``
    field (``thin_data`` / ``overfitting`` / ``indeterminate``). We
    aggregate to one verdict per feature by majority vote, with ties
    broken in favour of the more conservative drop class (overfitting >
    thin_data > indeterminate)."""
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    rows = raw.get("feature_outcome_correlations", [])

    # Group rows by feature.
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["feature"], []).append(row)

    rules: dict[str, FeatureRule] = {}
    for feat, group in grouped.items():
        labels = [r.get("classification", "indeterminate") for r in group]
        counts = Counter(labels)
        # Tie-break order: overfitting > thin_data > indeterminate > productive.
        priority = {"overfitting": 3, "thin_data": 2, "indeterminate": 1, "productive": 0}
        winner = max(counts.items(), key=lambda kv: (kv[1], priority.get(kv[0], -1)))[0]
        spec_class = _CHARON_TO_SPEC.get(winner, CLASS_INDETERMINATE)
        n_total = max((r.get("n_total", 0) for r in group), default=0)
        rules[feat] = FeatureRule(
            feature=feat,
            spec_class=spec_class,
            n_total=n_total,
            rationale=f"majority vote across {len(group)} outcomes: {dict(counts)}",
        )

    return Classifier(
        rules=rules,
        feature_extractors=tuple(sorted(rules.keys())),
        meta={
            "source_path": str(p),
            "computed_date": raw.get("computed_date"),
            "n_claims_analyzed": raw.get("n_claims_analyzed"),
            "scope_flag": raw.get("scope_flag"),
        },
    )


# ---------------------------------------------------------------------------
# Feature extraction (records -> classifier-readable features)
# ---------------------------------------------------------------------------

# Step-set name parser — matches ergon.learner.trials._a149_real_corpus.
# Tokens look like "(1,0,0)", "(-1,-1,-1)", "(1,1,1)", etc.
_STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def _parse_step_set(name: str) -> list[tuple[int, int, int]]:
    return [(int(a), int(b), int(c)) for a, b, c in _STEP_RE.findall(name or "")]


def extract_features(record: Mapping[str, Any]) -> dict[str, bool]:
    """Extract the binary feature flags this classifier knows.

    Returns only flags that are TRUE for the record (sparse). Missing
    features are treated as absent (False); the caller treats "no
    features extracted at all" as INDETERMINATE.

    Feature space mirrors Charon's compute_surviving_claim_morphology.py
    plus a149 step-set parsing.
    """
    features: dict[str, bool] = {}

    # 1. Walk-step-set geometry features (from sequence/name field).
    name = record.get("name") or record.get("sequence") or ""
    if isinstance(name, str) and name:
        steps = _parse_step_set(name)
        if steps:
            n_steps = len(steps)
            if n_steps == 5:
                features["n_steps_5"] = True
            if any(s == (-1, -1, -1) for s in steps):
                features["has_diag_neg"] = True
            if any(s == (1, 1, 1) for s in steps):
                features["has_diag_pos"] = True
            counts_x = [s[0] for s in steps]
            counts_y = [s[1] for s in steps]
            counts_z = [s[2] for s in steps]
            asym_x = abs(sum(1 for v in counts_x if v > 0) - sum(1 for v in counts_x if v < 0))
            asym_y = abs(sum(1 for v in counts_y if v > 0) - sum(1 for v in counts_y if v < 0))
            asym_z = abs(sum(1 for v in counts_z if v > 0) - sum(1 for v in counts_z if v < 0))
            if asym_x >= 3:
                features["max_x_asymmetry_ge3"] = True
            if asym_y >= 3:
                features["max_y_asymmetry_ge3"] = True
            if asym_z >= 3:
                features["max_z_asymmetry_ge3"] = True
            if max(asym_x, asym_y, asym_z) >= 3:
                features["any_axis_asymmetry_ge3"] = True

    # 2. Corpus-level features (read directly when present).
    if record.get("source") == "regime_change" or record.get("regime_change") is True:
        features["regime_change"] = True
    if record.get("flagged") is True:
        features["flagged"] = True
    delta = record.get("delta_pct")
    if isinstance(delta, (int, float)) and delta >= 0.5:
        features["delta_pct_high"] = True
    known = record.get("known_count")
    if isinstance(known, (int, float)) and known < 50:
        features["known_count_low"] = True
    if record.get("best_model"):
        features["best_model"] = True

    return features


def classify_record(record: Mapping[str, Any], classifier: Classifier) -> str:
    """Classify a record into one of the 4 morphology classes, or
    INDETERMINATE if no classifier feature applies.

    Aggregation is *conservative-drop*: scan feature verdicts in priority
    order template_overfitting > battery_blind_spot > thin_data_artifact
    > productive_morphology, and the first class with at least one
    triggering feature wins. Rationale: any feature firing on a "drop"
    verdict means there's substrate-grade evidence the record is
    pathological; we'd rather drop a borderline record than train on a
    contaminated one. Productive_morphology requires the absence of any
    pathology-flagging feature — the substrate-grade equivalent of "all
    other evidence cleared."

    If zero features fire, return INDETERMINATE (retained per spec).
    INDETERMINATE is the substrate-grade calibrated negative: silence is
    not evidence, so we keep the record but flag it for the audit."""
    features = extract_features(record)
    fired = [f for f in features if f in classifier.rules]
    if not fired:
        return CLASS_INDETERMINATE

    verdicts = {classifier.rules[f].spec_class for f in fired}
    # Conservative-drop priority: pathological verdicts dominate.
    for cls in (
        CLASS_TEMPLATE_OVERFITTING,
        CLASS_BATTERY_BLIND_SPOT,
        CLASS_THIN_DATA_ARTIFACT,
        CLASS_PRODUCTIVE,
    ):
        if cls in verdicts:
            return cls
    return CLASS_INDETERMINATE


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DroppedRecord:
    """A record removed by the filter, plus the class it was flagged as."""
    record: Mapping[str, Any]
    flagged_class: str


def filter_corpus(
    records: Iterable[Mapping[str, Any]],
    classifier: Classifier,
    drop_classes: tuple[str, ...] = DEFAULT_DROP_CLASSES,
) -> tuple[list[Mapping[str, Any]], list[DroppedRecord], dict[str, int]]:
    """Filter ``records`` through the morphology classifier.

    Returns:
        filtered: records NOT flagged for drop (INDETERMINATE retained
                  with a ``morphology_class`` metadata field).
        dropped: records flagged as one of ``drop_classes`` (default
                 = battery_blind_spot + template_overfitting per spec).
        drop_counts: per-class drop count for the W6.1 dossier.

    INDETERMINATE behaviour: retained with metadata flag (substrate-grade
    discipline — silence is not evidence). Per Aporia closed-loop
    mitigation, the caller should ALSO retain the original unfiltered
    corpus and run W4.1 on both.
    """
    filtered: list[Mapping[str, Any]] = []
    dropped: list[DroppedRecord] = []
    drop_counts: Counter[str] = Counter()

    for rec in records:
        cls = classify_record(rec, classifier)
        if cls in drop_classes:
            dropped.append(DroppedRecord(record=rec, flagged_class=cls))
            drop_counts[cls] += 1
            continue
        # Tag retained records with the morphology verdict for downstream audit.
        # We never mutate the input; we shallow-copy and add a metadata field.
        if isinstance(rec, dict):
            tagged = {**rec, "morphology_class": cls}
        else:
            tagged = dict(rec)
            tagged["morphology_class"] = cls
        filtered.append(tagged)

    return filtered, dropped, dict(drop_counts)


__all__ = [
    "CLASS_PRODUCTIVE",
    "CLASS_BATTERY_BLIND_SPOT",
    "CLASS_THIN_DATA_ARTIFACT",
    "CLASS_TEMPLATE_OVERFITTING",
    "CLASS_INDETERMINATE",
    "DEFAULT_CLASSIFIER_PATH",
    "DEFAULT_DROP_CLASSES",
    "Classifier",
    "FeatureRule",
    "DroppedRecord",
    "load_morphology_classifier",
    "extract_features",
    "classify_record",
    "filter_corpus",
]
