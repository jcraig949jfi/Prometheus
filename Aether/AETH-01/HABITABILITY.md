# AETH-01 -- habitability map (Design Task 6)

Status: DRAFT. Before asking whether AETH-01 supports life-like
organization, this campaign asks a smaller, prior question: does its
parameter space contain ANY dynamically interesting region at all, and
where are its boundaries? Labels below are informal, overlapping,
non-exhaustive working buckets, not scientifically privileged
categories -- `UNKNOWN` is a first-class, expected, acceptable output.

## Measurable quantities (computed per run, over a trailing window)

- `activity_density(t)` = fraction of cells that emitted a proposal
  (WRITE, non-starved) at tick t.
- `change_rate(t)` = fraction of (cell, field) pairs with
  `stored_bits_changed=true` at tick t (from the required trace).
- `state_entropy(t)` = Shannon entropy of the empirical distribution of
  a chosen field (typically opcode, separately payload) across all
  cells at tick t.
- `energy_total(t)`, `energy_gini(t)` = total energy and a
  concentration measure (Gini coefficient) across cells.
- `global_hash(t)` = a cheap hash of the full lattice bytes at t (for
  exact-recurrence detection).
- `spatial_autocorr(t)` = correlation between a cell's opcode/payload
  and its 4 von Neumann neighbors', averaged over the lattice.
- `compression_ratio(t)` = size of a generic lossless compressor's
  output over the raw lattice bytes at t, relative to the same
  compressor's output on i.i.d. random bytes of the same size (a cheap
  compressibility/structure proxy).
- `component_track(t)` = connected components of "recently active"
  cells (activity in the last k ticks), matched frame-to-frame by
  maximum spatial overlap, giving a persistence duration and a centroid
  trajectory per tracked component.
- `perturbation_divergence(t)` = Hamming distance, at tick t, between a
  baseline run and a replay from the same initial state with exactly
  one bit flipped at t=0 (both under identical seed/parameters
  otherwise) -- requires re-running, computed only in the deepen/verify
  tier (EXPERIMENTS.md / GPU_RUNPOD.md scout->qualify->deepen->verify).

## Regime labels and their measured signatures

| Label | Working signature (trailing-window behavior) |
|---|---|
| DEAD | `activity_density -> 0` and stays 0; no cell ever proposes again |
| FROZEN | `activity_density` stabilizes `>0` but `change_rate -> 0` -- cells keep trying, nothing effectively changes (e.g. every proposal loses, or wins with same-value writes) |
| HOMOGENIZED | `state_entropy` collapses to near-0 for a targeted field (one byte value covers the lattice) while `activity_density` may stay `>0` |
| EXPLOSIVE | `change_rate` spikes far above its own later steady-state value in the first few ticks, typically followed by rapid `energy_total` depletion and transition to DEAD/FROZEN/HOMOGENIZED |
| PERIODIC | `global_hash(t)` (or a coarser summary vector) recurs exactly, or near-exactly, at a fixed lag `p`, sustained over many periods |
| CHAOTIC | `activity_density`/`state_entropy` stay bounded away from 0 without settling, AND `perturbation_divergence(t)` grows rapidly (super-linearly early, then saturating) from a single-bit initial difference |
| METASTABLE | `change_rate(t)` is heavy-tailed/bursty: long low-change intervals punctuated by rare large-change events, measured via burst-interval statistics rather than a single mean |
| STRUCTURED | `compression_ratio` and `spatial_autocorr` both indicate non-trivial structure (neither near-1 as random soup, nor near-0 as a single repeated value) |
| MOBILE | `component_track` finds a component whose centroid displacement over time exceeds a pure-diffusion null baseline at the same activity density |
| BOUNDARY_FORMING | a persistent spatial discontinuity in a chosen field's local statistics (e.g. two adjacent regions each internally more homogeneous than the lattice-wide average, separated by a stable seam) survives across the trailing window |
| UNKNOWN | none of the above signatures clears its threshold, or two signatures conflict -- reported as-is, never forced into the nearest label |

A single run may match more than one label (e.g. STRUCTURED and
MOBILE together); labels are tags, not a partition.

## Campaign design

1. **Scope: tiny worlds only (R13).** H, W in {4, 8, 16, 32}; run
   length short enough for full CPU exhaustive/property-test-style
   replay (a few thousand ticks, sized so `activity_density` and
   `change_rate` visibly stabilize or visibly fail to).
2. **Parameter axes swept**: `WRITE_COST`, `MAINTENANCE_COST`,
   `REPLENISH_NUMER x REPLENISH_AMOUNT` (as one combined "inflow rate"
   axis), `MUT_NUMER`, initial WRITE density (EXPERIMENTS.md regime 2).
   Fix everything else (H, W, seed count per cell) per sweep.
3. **Coarse grid first.** Log-spaced grid over each axis (e.g. 5-7
   points per axis), Regime A and Regime B (ECONOMICS.md) run
   separately since they occupy different corners of the same space.
   Each grid cell replicated across >=8 independent seeds (random
   soup / sparse soup, EXPERIMENTS.md regimes 1-2) to get a majority
   label plus a disagreement rate (seeds landing on different labels
   at the same parameters is itself a reported quantity, not
   suppressed by majority voting).
4. **Adaptive refinement at boundaries.** Wherever adjacent grid points
   disagree in majority label, bisect the parameter interval between
   them and resample (more seeds) -- this is a phase-boundary search,
   not a uniform re-scan of the whole space, and is the same
   scout -> qualify -> deepen logic used for cost control on Runpod
   later (GPU_RUNPOD.md).
5. **Special interest in the non-trivial middle.** Grid cells labeled
   STRUCTURED, MOBILE, METASTABLE, BOUNDARY_FORMING, or CHAOTIC (i.e.
   anything other than DEAD/FROZEN/HOMOGENIZED/EXPLOSIVE) are flagged
   for the deepen/verify tier: longer runs, `perturbation_divergence`
   computed, and forensic trace capture (OBSERVATORY.md) retained in
   full rather than only summary statistics.
6. **Negative-control axis.** Every sweep is repeated once at
   Regime C ("free compute," ECONOMICS.md) as a boring-control column,
   confirming that observed regime boundaries move when cost is
   removed (if they don't move at all, that is itself a surprising,
   reportable result, not evidence to discard).

## Output of this campaign

A labeled table (parameters -> majority label, disagreement rate,
metric values) and a set of flagged "interesting" parameter regions for
EXPERIMENTS.md-regime-based follow-up and for OBSERVATORY.md's deeper
instruments. This campaign does NOT claim to find life, heredity, or
organisms -- only where the physics is dynamically alive at all versus
trivially dead/frozen/saturated, which is the honest prerequisite the
brief asks for before any of those later questions are meaningful.
