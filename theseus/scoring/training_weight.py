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
# v0.2 (Fire #20, 8 corpus files × ~4K records each via corpus_health):
#   parity 0.65, abs_diff_* 0.65, divides 0.50, equal 0.025
#
# Hierarchy parity > divides > equal held robustly across both
# samples. Divides drifted up most (40 → 51) — the small-sample
# estimate underweighted it. The current values are conservative
# midpoints of the two measurements; further refresh expected as
# corpus grows.
PER_RELATION_STRUCTURAL_RATE = {
    "equal": 0.025,
    "equal_mod_2": 0.65,
    "divides": 0.50,
    # abs_diff_le_K is K-dependent; handled below.
}


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
        kp = record.kill_pattern or ""
        if any(s in kp for s in (
            "specific", "violated", "boundary", "F1_triggered",
            "F6_triggered", "F9_triggered", "F11_triggered",
        )):
            return 0.7
        return 0.4
    if v == Verdict.UNVERIFIED.value:
        return 0.1
    return 0.3


def _triangulation_bonus(record: TheseusRecord) -> float:
    """Records with step_trace populated carry process-supervised info."""
    if record.step_trace:
        return 1.3
    return 1.0


def _base_weight(record: TheseusRecord) -> float:
    """Per-relation structural extensibility weight (H4 finding)."""
    rel = record.claim_payload.get("relation", "")
    if rel in PER_RELATION_STRUCTURAL_RATE:
        return PER_RELATION_STRUCTURAL_RATE[rel]
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
            return _abs_diff_K_weight(k)
        except ValueError:
            return 0.25
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
