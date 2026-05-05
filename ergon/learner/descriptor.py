"""ergon.learner.descriptor — content-aware MAP-Elites behavior descriptor.

Per pivot/ergon_learner_proposal_v8.md §6.2:

The descriptor is hot-swappable; v8 specifies a 5-axis content-aware
descriptor with 5,000 cells (4 x 5 x 10 x 5 x 5):

1. Output canonicalizer subclass (4 categorical: group_quotient /
   partition_refinement / ideal_reduction / variety_fingerprint)
2. Equivalence-class entropy of DAG (5 quantile buckets)
3. Output-type signature (~10 categorical)
4. Output magnitude bucket (5 BOUNDED ranges, NOT quantile-binned)
5. Output canonical-form distance (5 quantile buckets)

This module computes the per-axis cell coordinates from a Genome plus
its evaluation result. For axes computable pre-evaluation (DAG entropy,
output-type signature) the descriptor accepts None for evaluation_result.

Per round-2 review's MAP-Elites collapse concern: the descriptor
includes a per-axis fill-rate audit hook (compute_fill_rates) and a
hot-swap protocol (alternative_axis_specs). At MVP we ship the v8 axes
as primary; v0.5 may swap based on observed fill distribution.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

from ergon.learner.genome import Genome


# Per v8 §6.2: bounded magnitude buckets (NOT quantile-binned)
# Outside [10^0, 10^15] -> out_of_band cell (permanently de-emphasized)
MAGNITUDE_BUCKETS = (
    (1e0, 1e3),    # bucket 0: small-scale; gravitational-well risk; downweight 0.5
    (1e3, 1e6),    # bucket 1: mid-scale; LMFDB-conductor / OEIS typical; full weight
    (1e6, 1e9),    # bucket 2: large-scale; genuine structural rarity; full weight
    (1e9, 1e12),   # bucket 3: very large; computationally expensive; downweight 0.7
    (1e12, math.inf),  # bucket 4: extreme scale; usually artifact; downweight 0.7
)
OUT_OF_BAND_BUCKET = -1  # sentinel for outside [10^0, 10^15] (or fails stability check)
MAGNITUDE_BUCKET_WEIGHTS = (0.5, 1.0, 1.0, 0.7, 0.7)  # for cell-selection scoring


# Per v8 §6.2: 4 canonicalizer subclasses (axis 1)
CANONICALIZER_SUBCLASSES = (
    "group_quotient",
    "partition_refinement",
    "ideal_reduction",
    "variety_fingerprint",
)
N_CANONICALIZER_SUBCLASSES = len(CANONICALIZER_SUBCLASSES)  # = 4


# Per v8 §6.2 axis 3: ~10 output-type-signature categories.
# Coarse return-type buckets; specific names are domain-pragmatic.
OUTPUT_TYPE_SIGNATURES = (
    "polynomial",       # univariate or multivariate polynomial
    "rational",         # rational function
    "integer",          # exact integer
    "real_scalar",      # real-valued scalar (float)
    "complex_scalar",   # complex-valued scalar
    "sequence",         # OEIS-style integer or rational sequence
    "matrix",           # numerical matrix
    "tuple_or_record",  # structured tuple / record
    "boolean_or_class", # discrete classification result
    "other",            # fallback
)
N_OUTPUT_TYPE_SIGNATURES = len(OUTPUT_TYPE_SIGNATURES)  # = 10


# Quantile-binning resolution for axes 2 and 5
N_QUANTILE_BUCKETS = 5


@dataclass(frozen=True)
class CellCoordinate:
    """A genome's coordinate in the 5-axis MAP-Elites archive.

    Axis values:
      canonicalizer_subclass: int in [0, 3] indexing CANONICALIZER_SUBCLASSES;
                              -1 if no subclass match (genome routed elsewhere).
      dag_entropy_bucket:     int in [0, 4] (quantile bucket).
      output_type_signature:  int in [0, 9] indexing OUTPUT_TYPE_SIGNATURES.
      magnitude_bucket:       int in [0, 4]; -1 for out_of_band (outside [10^0, 10^15]).
      canonical_form_distance_bucket: int in [0, 4] (quantile bucket).

    The coordinate is the cell key. Two genomes with the same coordinate
    compete for the elite slot via three-tier lexicographic comparison.
    """
    canonicalizer_subclass: int
    dag_entropy_bucket: int
    output_type_signature: int
    magnitude_bucket: int
    canonical_form_distance_bucket: int

    def is_out_of_band(self) -> bool:
        """True if this coordinate is in any out-of-band cell.

        Out-of-band cells are de-emphasized in selection but not
        excluded; they remain queryable in the archive.
        """
        return (
            self.magnitude_bucket == OUT_OF_BAND_BUCKET
            or self.canonicalizer_subclass < 0
        )

    def to_tuple(self) -> Tuple[int, int, int, int, int]:
        return (
            self.canonicalizer_subclass,
            self.dag_entropy_bucket,
            self.output_type_signature,
            self.magnitude_bucket,
            self.canonical_form_distance_bucket,
        )


# ---------------------------------------------------------------------------
# Per-axis computation
# ---------------------------------------------------------------------------


def compute_dag_entropy_bucket(
    genome: Genome,
    quantile_thresholds: Optional[Sequence[float]] = None,
) -> int:
    """Axis 2: equivalence-class entropy of the DAG, quantile-binned.

    Per v8 §6.2: Shannon entropy over the canonicalizer subclasses
    represented in the genome's atom composition. High entropy = diverse
    composition; low entropy = repeated atom subclass.

    For MVP, we compute entropy over the genome's *callable_ref* names
    as a proxy for atom subclass (until arsenal_meta is wired uniformly
    to provide subclass tags for every atom). Quantile thresholds default
    to [0.5, 1.0, 1.5, 2.0] nats — calibrated against typical genomes
    of depth 4-8 and width 1-5.

    Returns an int in [0, 4].
    """
    if quantile_thresholds is None:
        quantile_thresholds = (0.5, 1.0, 1.5, 2.0)

    if not genome.nodes:
        return 0

    # Shannon entropy over callable_ref distribution
    counts = Counter(n.callable_ref for n in genome.nodes)
    total = sum(counts.values())
    entropy = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * math.log(p)

    # Bucket via quantile thresholds
    for i, threshold in enumerate(quantile_thresholds):
        if entropy < threshold:
            return i
    return len(quantile_thresholds)  # last bucket (= 4 for default 4 thresholds)


def compute_output_type_signature(
    genome: Genome,
    type_inference: Optional[Dict[str, str]] = None,
) -> int:
    """Axis 3: discrete output-type signature category.

    Per v8 §6.2: ~10 categorical buckets for the genome's overall return
    type (the root node's return_type). For MVP, we infer type from the
    callable_ref using a hand-curated mapping. v0.5+: integrates with
    arsenal_meta's return_type field uniformly.

    type_inference is an optional override map (callable_ref -> signature
    string) used by tests.

    Returns an int in [0, 9].
    """
    root = genome.root_node()
    if root is None:
        return OUTPUT_TYPE_SIGNATURES.index("other")

    if type_inference is None:
        type_inference = _DEFAULT_TYPE_INFERENCE_HEURISTIC

    callable_ref = root.callable_ref
    inferred = type_inference.get(callable_ref) or _heuristic_type_from_name(callable_ref)
    if inferred not in OUTPUT_TYPE_SIGNATURES:
        inferred = "other"
    return OUTPUT_TYPE_SIGNATURES.index(inferred)


def _heuristic_type_from_name(callable_ref: str) -> str:
    """Heuristic mapping callable_ref -> output type signature.

    Used as fallback when explicit type_inference doesn't have an entry.
    Matches against common arsenal naming patterns; defaults to "other".
    """
    name = callable_ref.lower()
    # Module path is informative
    if "polynomial" in name or "polred" in name or "factor_list" in name:
        return "polynomial"
    if "rational" in name:
        return "rational"
    if "modular_form" in name or "hecke" in name or "modular_l" in name:
        return "complex_scalar"
    if "elliptic_curve" in name or "lmfdb" in name:
        return "tuple_or_record"
    if "matrix" in name or "decomp" in name:
        return "matrix"
    if "sequence" in name or "oeis" in name or "partition" in name:
        return "sequence"
    if "is_irreducible" in name or "is_prime" in name or ":has_" in name or ":check_" in name:
        return "boolean_or_class"
    if "integer" in name or "isogeny" in name or "n_solutions" in name:
        return "integer"
    if "dilogarithm" in name or "polylogarithm" in name or "zeta" in name or "scalar" in name:
        return "real_scalar"
    return "other"


# Default type-inference heuristic table for MVP.
# v0.5 will replace this with explicit per-arsenal-atom return_type from arsenal_meta.
_DEFAULT_TYPE_INFERENCE_HEURISTIC: Dict[str, str] = {}


def compute_magnitude_bucket(magnitude: Optional[float]) -> int:
    """Axis 4: bounded output-magnitude bucket.

    Per v8 §6.2: explicit fixed ranges (NOT quantile-binned). Outputs
    outside [10^0, 10^15] fall into out_of_band (returns -1).

    Returns an int in [0, 4]; or -1 (out_of_band) if magnitude is None,
    negative, zero, NaN, or > 1e15.
    """
    if magnitude is None or math.isnan(magnitude) or magnitude < 1.0 or magnitude > 1e15:
        return OUT_OF_BAND_BUCKET

    for i, (low, high) in enumerate(MAGNITUDE_BUCKETS):
        if low <= magnitude < high:
            return i

    # Should not reach here given the > 1e15 guard above, but defensive
    return OUT_OF_BAND_BUCKET


def compute_canonical_form_distance_bucket(
    distance: Optional[float],
    quantile_thresholds: Optional[Sequence[float]] = None,
) -> int:
    """Axis 5: distance to nearest catalog entry, quantile-binned.

    Per v8 §6.2: 5 quantile buckets. Distance is in canonical-form space
    (typically Euclidean over canonicalized coefficient vectors, but
    domain-specific). Default quantile thresholds (calibrated against
    typical Lehmer-Mahler distance distributions): (0.001, 0.01, 0.1, 1.0).

    distance=None (couldn't compute) routes to bucket 4 (highest).

    Returns an int in [0, 4].
    """
    if quantile_thresholds is None:
        quantile_thresholds = (0.001, 0.01, 0.1, 1.0)

    if distance is None or math.isnan(distance):
        return len(quantile_thresholds)  # last bucket = 4

    for i, threshold in enumerate(quantile_thresholds):
        if distance < threshold:
            return i
    return len(quantile_thresholds)


def compute_canonicalizer_subclass(
    output_subclass: Optional[str],
) -> int:
    """Axis 1: discrete canonicalizer subclass of the output.

    Per v8 §6.2: 4 categorical (group_quotient, partition_refinement,
    ideal_reduction, variety_fingerprint).

    output_subclass is the canonicalizer subclass tag computed by
    classifying the genome's evaluation result (NOT the DAG's
    composition subclass — that's axis 2 entropy domain). Returns -1
    if no subclass is determined.

    Returns an int in [0, 3] or -1.
    """
    if output_subclass is None:
        return -1
    if output_subclass in CANONICALIZER_SUBCLASSES:
        return CANONICALIZER_SUBCLASSES.index(output_subclass)
    return -1


# ---------------------------------------------------------------------------
# Top-level descriptor computation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluationResult:
    """The post-EVAL data the descriptor needs.

    Fields are Optional so that genomes can be partially-coordinated
    (e.g., for pre-EVAL fitness prediction) using only the axes that
    don't require evaluation (axes 2, 3).
    """
    output_canonicalizer_subclass: Optional[str] = None
    output_magnitude: Optional[float] = None
    output_type_signature: Optional[str] = None  # override from inference
    canonical_form_distance_to_catalog: Optional[float] = None


def compute_cell_coordinate(
    genome: Genome,
    evaluation: Optional[EvaluationResult] = None,
    type_inference: Optional[Dict[str, str]] = None,
) -> CellCoordinate:
    """Compute the genome's cell coordinate from genome + optional evaluation.

    Pre-EVAL: pass evaluation=None. Returns a coordinate with axes 1, 4,
    5 set to out-of-band sentinels (since they require post-EVAL data).

    Post-EVAL: pass an EvaluationResult. Returns a fully-determined
    coordinate.
    """
    if evaluation is None:
        evaluation = EvaluationResult()

    # Axis 1
    cs_idx = compute_canonicalizer_subclass(evaluation.output_canonicalizer_subclass)

    # Axis 2
    entropy_idx = compute_dag_entropy_bucket(genome)

    # Axis 3
    if evaluation.output_type_signature is not None:
        # Explicit override from EVAL
        if evaluation.output_type_signature in OUTPUT_TYPE_SIGNATURES:
            type_idx = OUTPUT_TYPE_SIGNATURES.index(evaluation.output_type_signature)
        else:
            type_idx = OUTPUT_TYPE_SIGNATURES.index("other")
    else:
        type_idx = compute_output_type_signature(genome, type_inference=type_inference)

    # Axis 4
    mag_idx = compute_magnitude_bucket(evaluation.output_magnitude)

    # Axis 5
    cfd_idx = compute_canonical_form_distance_bucket(
        evaluation.canonical_form_distance_to_catalog
    )

    return CellCoordinate(
        canonicalizer_subclass=cs_idx,
        dag_entropy_bucket=entropy_idx,
        output_type_signature=type_idx,
        magnitude_bucket=mag_idx,
        canonical_form_distance_bucket=cfd_idx,
    )


# ---------------------------------------------------------------------------
# Per-axis fill-rate audit (per v8 §6.2 hot-swap protocol)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FillRateAudit:
    """Per-axis fill-rate audit result.

    Per v8 §6.2: every 1K-episode window, compute per-axis fill
    distribution. Flag axes >70% concentration; flag axis pairs with
    |corr|>0.7. Trigger axis-replacement protocol on flagged axes.
    """
    axis_concentrations: Dict[str, float]  # axis_name -> max-bin fill fraction
    flagged_axes: Tuple[str, ...]  # axes with >70% concentration
    axis_pair_correlations: Dict[Tuple[str, str], float]
    flagged_axis_pairs: Tuple[Tuple[str, str], ...]  # |corr|>0.7 pairs


AXIS_NAMES = (
    "canonicalizer_subclass",
    "dag_entropy_bucket",
    "output_type_signature",
    "magnitude_bucket",
    "canonical_form_distance_bucket",
)


def compute_fill_rates(
    coordinates: Sequence[CellCoordinate],
    concentration_threshold: float = 0.70,
    correlation_threshold: float = 0.70,
) -> FillRateAudit:
    """Per-axis fill-rate audit over a sequence of coordinates.

    Returns FillRateAudit with per-axis max-bin concentration, flagged
    axes (concentration > threshold), and flagged axis pairs (|corr| >
    threshold).

    For axis_pair_correlations we use Spearman rank correlation
    (computed via rank-then-Pearson for simplicity at MVP scale).
    """
    if not coordinates:
        return FillRateAudit(
            axis_concentrations={},
            flagged_axes=(),
            axis_pair_correlations={},
            flagged_axis_pairs=(),
        )

    # Per-axis concentration
    concentrations: Dict[str, float] = {}
    flagged: List[str] = []

    for axis_idx, axis_name in enumerate(AXIS_NAMES):
        values = [c.to_tuple()[axis_idx] for c in coordinates]
        counts = Counter(values)
        max_count = max(counts.values())
        concentration = max_count / len(values)
        concentrations[axis_name] = concentration
        if concentration > concentration_threshold:
            flagged.append(axis_name)

    # Pairwise Spearman correlation between axes
    correlations: Dict[Tuple[str, str], float] = {}
    flagged_pairs: List[Tuple[str, str]] = []

    for i in range(len(AXIS_NAMES)):
        for j in range(i + 1, len(AXIS_NAMES)):
            xi = [c.to_tuple()[i] for c in coordinates]
            xj = [c.to_tuple()[j] for c in coordinates]
            corr = _spearman_correlation(xi, xj)
            pair_key = (AXIS_NAMES[i], AXIS_NAMES[j])
            correlations[pair_key] = corr
            if abs(corr) > correlation_threshold:
                flagged_pairs.append(pair_key)

    return FillRateAudit(
        axis_concentrations=concentrations,
        flagged_axes=tuple(flagged),
        axis_pair_correlations=correlations,
        flagged_axis_pairs=tuple(flagged_pairs),
    )


def _spearman_correlation(x: Sequence[int], y: Sequence[int]) -> float:
    """Spearman rank correlation between two integer sequences.

    Returns 0.0 for empty or constant inputs (correlation is undefined).
    """
    n = len(x)
    if n < 2:
        return 0.0
    # Rank
    rx = _rank(x)
    ry = _rank(y)
    # Pearson on ranks
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den_x = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    den_y = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def _rank(values: Sequence[int]) -> List[float]:
    """Average-rank ranking for ties (standard Spearman handling)."""
    sorted_indices = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[sorted_indices[j + 1]] == values[sorted_indices[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[sorted_indices[k]] = avg_rank
        i = j + 1
    return ranks
