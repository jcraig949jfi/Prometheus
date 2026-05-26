"""Per-record training-value weight assignment.

Combines:
  1. Per-relation structural extensibility (H4-confirmed weights from
     Fires #13-14): parity ~63%, divides ~40%, equal ~2%, abs_diff_le_K
     K-dependent.
  2. Verdict-based informativeness multiplier.
  3. Triangulation bonus (records with step_trace populated carry
     process-supervised information).

The output is a scalar in [0, 1] that downstream Ergon training can use
to weight examples. Higher = more structural / more informative.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from theseus.emit.record_schema import TheseusRecord, Verdict


# Empirically-confirmed per-relation extensibility rates from H4.
#
# v0.1 (Fires #13-14, 2 seeds × ~2K records each):
#   parity 0.63, divides 0.40, equal 0.02
# v0.2 (Fire #20, 8 corpus files via corpus_health):
#   parity 0.65, abs_diff_* 0.65, divides 0.50, equal 0.025
# v0.3 (Fire #21 stratified audit + Fire #22 anchoring):
#   parity 0.65 (robust ±9pp across ec_invariants),
#   divides 0.35 (conductor-anchored; aggregate 50% was inflated by
#       small-range invariants — rank 91%, torsion 88%, tamagawa 50%,
#       conductor 33% — only conductor reflects real structural rate),
#   equal 0.025 (robust ±2pp).
#
# Hierarchy parity > divides > equal holds at every measurement.
# Anchoring divides on the high-range invariant (conductor) is the
# substrate-honest call: the small-range invariants' high rates are
# trivial-divisibility artifacts, not structural bridges.
PER_RELATION_STRUCTURAL_RATE = {
    "equal": 0.025,
    "equal_mod_2": 0.65,
    "divides": 0.35,
    # abs_diff_le_K is K-dependent; handled below.
}


# Information-content multiplier per relation (Fire #141, 2026-05-26).
# Triage finding (pivot/techne_promoted_record_triage_2026-05-25.md):
# H4's PER_RELATION_STRUCTURAL_RATE measures EXTENSIBILITY — how often
# the relation holds across the catalog. equal_mod_2 = 0.65 because
# parity is extensible. But triage showed the resulting promoted
# records are visually trivial: random integer pairings happen to
# share parity 50% of the time by chance, and "X equal_mod_2 -X" is
# a tautology by construction.
#
# Extensibility ≠ information content. A relation that holds 90% of
# the time across the catalog is HIGHLY extensible but carries LOW
# information about specific records. A relation that holds 2% of the
# time is LOW extensibility but each instance carries HIGH information
# (it picks out something specific).
#
# This multiplier scales the extensibility rate by the relation's
# information-content potential, so the composite weight reflects
# Learner-training value rather than catalog statistics.
#
# Calibrated to ensure parity-equality records (current dominant
# promoted-record type) fall below the 0.6 promote threshold:
#   equal_mod_2 base 0.65 × info 0.30 = 0.195 → below threshold ✓
#   equal       base 0.025 × info 1.0 = 0.025 → still below ✓
#   divides     base 0.35 × info 0.70 = 0.245 → below threshold
#   tighter     base 0.60 × info 0.55 = 0.33  → below threshold
PER_RELATION_INFO_CONTENT = {
    "equal": 1.00,         # rare-equality is high-info (only 2.5% hold)
    "equal_mod_2": 0.30,   # parity is trivial-by-construction
    "divides": 0.70,       # divisibility carries arithmetic structure
}


def _info_content_multiplier(rel: str) -> float:
    """Information-content scaling factor per relation.

    See PER_RELATION_INFO_CONTENT docstring. Returns 1.0 for
    relations not in the table (default: no penalty).
    """
    if rel in PER_RELATION_INFO_CONTENT:
        return PER_RELATION_INFO_CONTENT[rel]
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
        except ValueError:
            return 1.0
        # Tighter K is more specific → more info-bearing.
        # Wider K approaches parity-tautology territory.
        if k <= 3:
            return 0.55
        if k <= 10:
            return 0.50
        if k <= 50:
            return 0.40
        return 0.30
    return 1.0


def _abs_diff_K_weight(k: int) -> float:
    """Threshold-K-dependent structural weight. Tighter K is more specific.

    Fire #19 corpus_health found abs_diff_le_* aggregated ≈ 67%
    categorical (parity-equivalent). Tighter Ks should weight even
    higher; very wide Ks (catalog-spanning) trivially hold and weight
    lower.
    """
    if k <= 3:
        return 0.60  # very tight, parity-like
    if k <= 10:
        return 0.50
    if k <= 50:
        return 0.35
    if k <= 500:
        return 0.20
    return 0.10  # very wide K is almost trivial


def _verdict_multiplier(record: TheseusRecord) -> float:
    """Verdict-based informativeness multiplier."""
    v = record.verdict
    if v == Verdict.PROMOTED.value:
        return 1.5
    if v == Verdict.SHADOW_CATALOG.value:
        return 1.0
    if v == Verdict.INCONCLUSIVE.value:
        return 0.6
    if v == Verdict.REJECTED.value:
        # Specific kill patterns carry more info than generic kills.
        # Fire #33: boosted from (0.7 / 0.4) → (1.0 / 0.6) to reflect
        # the falsification-routing-learner direction (memory:
        # project_falsification_routing_learner.md, feedback_assume_wrong.md
        # — "kills are the most valuable output"). Specific kills are
        # now at parity with SHADOW confirmations; generic kills carry
        # moderate value.
        kp = record.kill_pattern or ""
        if any(s in kp for s in (
            "specific", "violated", "boundary", "F1_triggered",
            "F6_triggered", "F9_triggered", "F11_triggered",
        )):
            return 1.0
        return 0.6
    if v == Verdict.UNVERIFIED.value:
        return 0.1
    return 0.3


def _triangulation_bonus(record: TheseusRecord) -> float:
    """Records with step_trace populated carry process-supervised info."""
    if record.step_trace:
        return 1.3
    return 1.0


def _base_weight(record: TheseusRecord) -> float:
    """Per-relation weight: H4 extensibility × info-content multiplier.

    H4 framework (PER_RELATION_STRUCTURAL_RATE) captures how often a
    relation holds across the catalog. Info-content multiplier
    (Fire #141) scales by the relation's Learner-training value:
    high-extensibility but low-info relations (parity, wide
    abs_diff) are downweighted so they don't dominate the promote
    pile with trivial coincidences.

    See triage report:
    pivot/techne_promoted_record_triage_2026-05-25.md
    """
    rel = record.claim_payload.get("relation", "")
    info_mult = _info_content_multiplier(rel)
    if rel in PER_RELATION_STRUCTURAL_RATE:
        return PER_RELATION_STRUCTURAL_RATE[rel] * info_mult
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
            return _abs_diff_K_weight(k) * info_mult
        except ValueError:
            return 0.25 * info_mult
    # Non-A1-shape records (B/D/E/G/H families): use a kind-based default.
    kind = record.claim_kind
    if kind in (
        "operator_rotation", "composition_test", "conservation_law",
        "symmetry_transform",
    ):
        return 0.35  # operator-algebra records — modest weight
    if kind == "literature_mined":
        return 0.20  # E1/E3 are unverified literature
    if kind == "kill_neighborhood":
        return 0.40  # D1/D2/D3/D4 — boundary information
    if kind == "bridge_extension":
        return 0.55  # H4 multi-arrow categorical bridges
    if kind == "statistical_correlation":
        return 0.35  # A2 — correlation magnitude carries info
    if kind == "functional_identity":
        return 0.30  # A3 — operator-pair specific
    if kind == "ratio_invariance":
        return 0.40  # A4 symbolic regression — depends on R²
    if kind == "distribution_match":
        return 0.30  # A5 — distribution-level
    return 0.25


def training_weight(record: TheseusRecord) -> float:
    """Compute the training-value weight for a record. Clamps to [0, 1]."""
    base = _base_weight(record)
    v_mult = _verdict_multiplier(record)
    t_bonus = _triangulation_bonus(record)
    return float(max(0.0, min(1.0, base * v_mult * t_bonus)))


def annotate_corpus(
    input_path: Path,
    output_path: Optional[Path] = None,
) -> dict:
    """Read corpus JSONL; add training_weight to each record; write
    annotated output. Returns aggregate statistics.

    If output_path is None, writes to `<input_path>.annotated.jsonl`.
    """
    if output_path is None:
        output_path = input_path.with_suffix(".annotated.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_records = 0
    weight_sum = 0.0
    weight_max = 0.0
    weight_min = 1.0
    weight_buckets = {"<0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, ">=0.8": 0}

    with input_path.open(encoding="utf-8") as inp, output_path.open(
        "w", encoding="utf-8"
    ) as out:
        for line in inp:
            line = line.strip()
            if not line:
                continue
            try:
                r_dict = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                r = TheseusRecord(**r_dict)
            except (TypeError, ValueError):
                continue
            w = training_weight(r)
            r_dict["training_weight"] = w
            out.write(json.dumps(r_dict, sort_keys=True) + "\n")
            n_records += 1
            weight_sum += w
            weight_max = max(weight_max, w)
            weight_min = min(weight_min, w)
            if w < 0.2:
                weight_buckets["<0.2"] += 1
            elif w < 0.4:
                weight_buckets["0.2-0.4"] += 1
            elif w < 0.6:
                weight_buckets["0.4-0.6"] += 1
            elif w < 0.8:
                weight_buckets["0.6-0.8"] += 1
            else:
                weight_buckets[">=0.8"] += 1

    return {
        "input": str(input_path),
        "output": str(output_path),
        "n_records": n_records,
        "weight_mean": weight_sum / max(n_records, 1),
        "weight_min": weight_min,
        "weight_max": weight_max,
        "weight_buckets": weight_buckets,
    }


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(prog="theseus.scoring.training_weight")
    p.add_argument("input", help="Path to corpus JSONL")
    p.add_argument("--output", help="Annotated output path (optional)")
    args = p.parse_args()

    stats = annotate_corpus(
        Path(args.input),
        Path(args.output) if args.output else None,
    )
    print(json.dumps(stats, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
