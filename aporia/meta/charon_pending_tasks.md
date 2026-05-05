# Charon Pending Tasks — Queued for Future

**Date queued:** 2026-05-05
**Owner:** Aporia (queue maintenance); fired by James when needed
**Status:** Documented for future use, NOT currently active

These two tasks were generated alongside the Substrate Cartography Suite
(CG5 + G5 + CG6, currently in flight) but deferred. Both are
substrate-grade Charon work; neither is on the critical path for Ergon's
immediate training-unblock decision.

Fire each as a standalone Charon instance when the prerequisite condition
in "When to fire" is met.

---

## Pending Task 1 — F-gate orthogonality MI audit

**Origin:** Gemini synthesis (G4)
**When to fire:** After Substrate Cartography Suite completes AND
                  Ergon's training-unblock decision is made. This is
                  substrate-hygiene work, not training-unblock work.
**Time budget:** ~3 hours wall clock
**Charon-fit:** Strong — measures the battery's own epistemic efficiency

### Prompt

```
You are Charon, instantiated fresh for one task. Your normal role is
running the falsification battery and managing the validation ladder.
This task turns the battery's diagnostic gaze inward: you are auditing
the 4-fold falsification gates (F1, F6, F9, F11) to measure their actual
epistemic independence.

## Context: Project Prometheus + Substrate v1.5

The discovery pipeline forces every claim through a 4-fold battery:
  - F1: Permutation null
  - F6: Base rate
  - F9: Simpler explanation
  - F11: Cross-validation

We currently operate on the assumption that these four gates provide
orthogonal falsification pressure. If F6 and F9 have a 99% kill-rate
overlap, we don't have a 4-fold battery; we have a 3-fold battery with
redundant compute overhead. If Ergon's Learner trains on
`battery_survival_depth`, that depth must represent mathematically
independent hurdles, not correlated proxy metrics.

## Your task

Compute the pairwise conditional kill rates and Mutual Information (in
bits) between the four F-gates across the substrate's existing kill
ledger.

### Where the data lives

- The shadow archive of ~92K killed hypotheses (location: use Glob to
  confirm canonical path)
- KillVectors logged in `F:/Prometheus/prometheus_math/_*_pilot.json`
- `F:/Prometheus/prometheus_math/discovery_pipeline.py` — read for exact
  F-gate execution logic and ordering

### Method

1. Extract the terminal state and F-gate boolean outcomes for all killed
   hypotheses
2. Compute the unconditional kill rate for each of the 4 gates
3. Compute conditional probability P(Kill_Fy | Kill_Fx) for all pairs
4. Calculate the Mutual Information (in bits) between each pair of gates

### Output

Write to:
- `F:/Prometheus/charon/diagnostics/f_gate_orthogonality.json`
- `F:/Prometheus/charon/diagnostics/F_GATE_ORTHOGONALITY_REPORT.md`

JSON schema:
{
  "computed_date": "...",
  "n_records_analyzed": ...,
  "unconditional_kill_rates": {
    "F1": ..., "F6": ..., "F9": ..., "F11": ...
  },
  "conditional_kill_matrix": {
    "F1_given_F6": ..., "F6_given_F1": ...,
    // ... all ordered pairs
  },
  "mutual_information_bits": {
    "F1_F6": ..., "F1_F9": ..., "F1_F11": ...,
    "F6_F9": ..., "F6_F11": ..., "F9_F11": ...
  },
  "redundancy_flags": ["pairs with MI > 0.8 bits"],
  "honesty_notes": [...]
}

### Discipline

- Caveat-as-metadata: note if the sequential nature of the pipeline biases
  results (e.g., F11 is only evaluated if F1 clears — that's a sampling
  artifact, not real orthogonality data)
- Falsification-first: if data shows two tests are functionally identical
  in this domain space, state it cleanly without defending the original
  design
- Calibrated negatives preferred: "the battery is not as orthogonal as
  designed" is a substrate-grade finding worth shipping

## Why this matters to Prometheus

If the tests are highly correlated, Ergon learns to optimize against a
single mathematical bias disguised as a robust battery. We need to know
if we're lying to ourselves about the depth of our verification.
```

---

## Pending Task 2 — Lehmer exclusion zone topology

**Origin:** Gemini synthesis (G6)
**When to fire:** When Techne actively starts implementing the
                  ExclusionZone primitive (P4). Currently this is a
                  Techne dependency, not a free-floating diagnostic.
                  Without P4 work in flight, this output sits unused.
**Time budget:** ~3 hours wall clock
**Charon-fit:** Strong — direct negative-space cartography

### Prerequisite

Techne must have at minimum a draft ExclusionZone schema so the metric
choices in this task align with how Techne will consume the output.
Without that alignment, this task may compute an L_2 norm Techne can't
use.

### Prompt

```
You are Charon, instantiated fresh for one task. This touches directly on
Techne's v2 Substrate proposal and your ownership of negative-space
cartography.

## Context: Project Prometheus + Substrate v2 ExclusionZones

Techne is building the ExclusionZone primitive (P4) to formally record
negative space. However, "distance to nearest proven-empty region" is
mathematically meaningless without a canonical metric topology for
heterogeneous parameter spaces.

This task computes the empirical density of killed hypotheses in the
Lehmer-Mahler coefficient space and drafts the first canonical metric
bounds for the densest "voids" — regions where every claim has been
killed and zero have ever survived to PROMOTE.

## Your task

1. Compute empirical density of the killed hypotheses within the Lehmer-
   Mahler coefficient space
2. Draft the first canonical metric bounds for the densest voids

### Where the data lives

- `F:/Prometheus/aporia/mathematics/kills.jsonl` (focus exclusively on
  the A149 / Lehmer-Mahler subset)
- `F:/Prometheus/prometheus_math/lehmer_boundary_layer.py` — existing
  k-means clustering logic on margin features
- `F:/Prometheus/prometheus_math/lehmer_brute_force.py` — for context on
  how the deg-14 ±5 palindromic subspace is parameterized
- `F:/Prometheus/prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md`
  — yesterday's INCONCLUSIVE result (97M polys enumerated; 26 Mossinghoff
  rediscoveries + 17 borderline near-cyclotomic entries)

### Method

1. Isolate the Lehmer-Mahler killed claims
2. Define an explicit L_2 norm function over polynomial coefficient
   vectors. Document EXACTLY how polynomials of different degrees are
   padded or aligned (this is the load-bearing decision).
3. Run a density-based spatial clustering algorithm (e.g., DBSCAN) over
   the space to find the largest contiguous clusters of kills where
   ZERO claims have ever survived to PROMOTE
4. Compute bounding geometry (centroid + maximum radius) for the top 5
   largest dead zones
5. Verify each zone's purity (no PROMOTEs inside the radius)

### Output

Write to:
- `F:/Prometheus/charon/diagnostics/lehmer_exclusion_zones.json`
- `F:/Prometheus/charon/diagnostics/EXCLUSION_ZONE_TOPOLOGY_REPORT.md`

JSON schema:
{
  "computed_date": "...",
  "domain": "Lehmer-Mahler",
  "metric_used": "L2_norm_coefficient_vector (with padding rule X)",
  "metric_definition_full": "verbose description of padding / alignment /
    canonicalization choices",
  "total_kills_analyzed": ...,
  "top_5_voids": [
    {
      "centroid_vector": [...],
      "radius": ...,
      "n_kills_inside": ...,
      "density_kills_per_unit_volume": ...,
      "purity": "1.0 (0 promotes inside radius)",
      "structural_notes": "describe what kind of polys live here"
    },
    ...
  ],
  "honesty_notes": [...]
}

### Discipline

- The metric definition is the most important part of this output.
  Document exactly how polynomials of different degrees were padded /
  aligned for the L_2 norm calculation. If Techne disagrees with the
  metric choice, the output becomes unusable.
- If the space is uniformly distributed and no meaningful voids exist,
  REPORT THAT. The 17 inconclusive entries from yesterday's brute-force
  may indicate the space is more uniform than expected.
- Do NOT extrapolate the void boundaries beyond the empirical kill data.
  An ExclusionZone declared on extrapolation is worse than no
  ExclusionZone.

## Why this matters to Prometheus

Techne cannot deploy P4 (ExclusionZone) without a mathematical definition
of what a zone is. This task transitions negative-space from abstract
idea into actionable coordinate geometry, explicitly preventing Ergon
from wasting time in mathematically barren regions.
```

---

## Maintenance notes

- These prompts assume no schema drift in `kills.jsonl`, `prometheus_math`,
  or `sigma_kernel` paths. Re-verify paths before firing.
- If either task is fired, update this file with execution date and
  outcome summary.
- If a third Charon batch is queued, append below this section in the
  same format.
