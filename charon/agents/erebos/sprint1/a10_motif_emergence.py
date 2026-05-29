"""Sprint-1 A10: motif emergence vs random (Phase 2, ITER-54).

Hypothesis (from roadmap v2 line 92):
> "Extracted motifs (Phase 1C ITER-40) match human-recognizable
> structural classes at rate > random clustering"
> Pass: motif-to-class purity > 0.4.

## What this replaced

Per the roadmap doc footnote: A10 was reframed from the v3
original "compare Erebos to one frontier LLM asked to propose
hypotheses directly" -- a gravity-well experiment that asked
"does Erebos beat an LLM at the LLM's game?" -- to this
motif-emergence test that stays inside the substrate's own
metrics.

## The claim being tested

If motif extraction (ITER-40) surfaces patterns that correspond
to MEANINGFUL structural classes in the underlying data, the
substrate is doing more than counting. If motifs are just
arbitrary co-occurrences, purity collapses to baseline.

## A10 protocol

1. Generate a synthetic ledger where each emission has a hidden
   ground-truth class label drawn from {"boundary", "decay",
   "outlier"}. Each class has a stable (plugin, kp) distribution
   that the substrate cannot see directly.
2. Run extract_plugin_kp_motifs(ledger, min_count=3) to get
   motifs.
3. For each motif, find the rows that produced its (plugin, kp)
   tuple; compute the dominant ground-truth class among those
   rows; count agreement (purity contribution).
4. Aggregate: purity = sum(dominant_class_count_per_motif) /
   sum(rows_in_motifs).
5. Baseline: shuffle ground-truth class labels (preserves
   marginals; breaks (plugin, kp) -> class correlation);
   recompute purity.
6. Pass if substrate_purity > 0.40 (pre-committed roadmap
   threshold, NOT a margin above baseline -- the roadmap
   commits to absolute 0.4).

## Why purity is the right metric

Purity is the standard clustering-quality measure for "how well
do the discovered clusters match a hidden ground truth?"
Substrate must beat the absolute 0.40 threshold. For 3 balanced
classes, random clustering gives purity = 0.33. The 0.4 threshold
is 20% above random -- a substantive structural signal.

A failure (purity <= 0.4) means: motif extraction surfaces
clusters that don't correspond to meaningful structural classes.
Layer 2's motif primitive is a counting tool, not a structure-
finding tool.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict

from charon.agents.erebos._motif_extraction import (
    extract_plugin_kp_motifs,
)
from charon.agents.erebos.sprint1 import SprintResult


CLASSES = ["boundary", "decay", "outlier"]
N_PER_CLASS = 50
SEED = 739
PASS_THRESHOLD_PURITY = 0.40
MIN_MOTIF_COUNT = 3

# Per-class (plugin, kp) distributions. Each class has a "favorite"
# (plugin, kp) tuple but with stochastic emission.
CLASS_GENERATIVE_MODEL: dict[str, dict[tuple[str, str], float]] = {
    "boundary": {
        ("g10_boundary", "sharp_boundary_detected_bocpd"): 0.55,
        ("g10_boundary", "PROMOTED"): 0.20,
        ("g02_contrast", "PROMOTED"): 0.15,
        ("g02_contrast", "out_of_sample_failure"): 0.10,
    },
    "decay": {
        ("g23_asymptotic_limit", "error_term_does_not_decay_bootstrap"): 0.50,
        ("g23_asymptotic_limit", "decay_slope_ci_straddles_boundary"): 0.20,
        ("g23_asymptotic_limit", "PROMOTED"): 0.15,
        ("g11_exception_miner", "PROMOTED"): 0.15,
    },
    "outlier": {
        ("g11_exception_miner", "catalog_flag_inconsistent"): 0.50,
        ("g11_exception_miner", "flag_distribution_uniform_under_mc_null"): 0.20,
        ("g25_degeneracy", "tautological_pass"): 0.15,
        ("g25_degeneracy", "PROMOTED"): 0.15,
    },
}


def _sample_from_dist(
    dist: dict[tuple[str, str], float], rng: random.Random,
) -> tuple[str, str]:
    r = rng.random()
    cum = 0.0
    last = None
    for k, p in dist.items():
        cum += p
        last = k
        if r <= cum:
            return k
    return last  # type: ignore[return-value]


def _generate_classified_ledger() -> list[dict]:
    rng = random.Random(SEED)
    rows: list[dict] = []
    row_idx = 0
    for class_name in CLASSES:
        dist = CLASS_GENERATIVE_MODEL[class_name]
        for _ in range(N_PER_CLASS):
            plugin, kp = _sample_from_dist(dist, rng)
            rows.append({
                "row_id": f"row_{row_idx:04d}",
                "plugin_id": plugin,
                "kill_pattern": None if kp == "PROMOTED" else kp,
                "_class": class_name,  # ground truth (not visible to motif extraction)
            })
            row_idx += 1
    rng.shuffle(rows)
    return rows


def _compute_motif_purity(
    rows: list[dict], motifs: list,
) -> tuple[float, int]:
    """For each motif, group rows by (plugin_id, kill_pattern or PROMOTED)
    matching the motif's key. Compute dominant-class count.
    Return (purity, total_rows_in_motifs)."""
    # Index rows by (plugin, kp)
    rows_by_tuple: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        kp = r.get("kill_pattern") or "PROMOTED"
        rows_by_tuple[(r["plugin_id"], kp)].append(r)

    total_in_motifs = 0
    total_correctly_classified = 0
    for motif in motifs:
        constituent_rows = rows_by_tuple.get(motif.key, [])
        if not constituent_rows:
            continue
        class_counts = Counter(r["_class"] for r in constituent_rows)
        dominant_count = class_counts.most_common(1)[0][1]
        total_in_motifs += len(constituent_rows)
        total_correctly_classified += dominant_count

    purity = (
        total_correctly_classified / total_in_motifs
        if total_in_motifs > 0 else 0.0
    )
    return purity, total_in_motifs


def run_a10() -> SprintResult:
    rows = _generate_classified_ledger()

    # Substrate: motif extraction (without class labels)
    # Motif extractor only sees plugin_id + kill_pattern; the
    # ground-truth class field is invisible to it (no extractor
    # reads "_class").
    result = extract_plugin_kp_motifs(rows, min_count=MIN_MOTIF_COUNT)
    motifs = list(result.motifs)
    substrate_purity, n_in_motifs = _compute_motif_purity(rows, motifs)

    # Baseline: shuffle class labels across rows (preserves marginals)
    rng_b = random.Random(SEED + 333)
    classes_pool = [r["_class"] for r in rows]
    rng_b.shuffle(classes_pool)
    rows_shuffled = [
        {**r, "_class": c} for r, c in zip(rows, classes_pool)
    ]
    baseline_purity, _ = _compute_motif_purity(rows_shuffled, motifs)

    passed = substrate_purity > PASS_THRESHOLD_PURITY

    return SprintResult(
        experiment_id="A10",
        hypothesis=(
            "Motif extraction surfaces clusters that match hidden "
            "ground-truth structural classes (purity > 0.4)"
        ),
        metric_name="motif_to_class_purity",
        metric_value=substrate_purity,
        pass_threshold=PASS_THRESHOLD_PURITY,
        comparator=">",
        passed=passed,
        protocol_summary=(
            f"Synthetic ledger: {len(CLASSES)} classes "
            f"({', '.join(CLASSES)}), N_PER_CLASS={N_PER_CLASS}; "
            f"each class has a (plugin, kp) distribution. "
            f"Run extract_plugin_kp_motifs(min_count="
            f"{MIN_MOTIF_COUNT}); compute dominant-class purity. "
            f"Pre-committed threshold = 0.40 (random over 3 classes "
            f"~= 0.33; 0.40 is ~20% above random)."
        ),
        notes=(
            f"n_motifs={len(motifs)}; "
            f"n_rows_in_motifs={n_in_motifs}/{len(rows)}; "
            f"substrate_purity={substrate_purity:.4f}; "
            f"baseline_purity_shuffled_classes={baseline_purity:.4f}; "
            f"pass_threshold>{PASS_THRESHOLD_PURITY}"
        ),
    )
