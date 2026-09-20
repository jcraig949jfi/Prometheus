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

**[REPAIRED per ASTRA_REVIEW_01.md S05, ACCEPT, see REPAIR_LEDGER_01.md
-- the reviewed draft treated finite low-activity windows as PROOF a
world cannot change again. A starved writer can be replenished later; a
same-value winner can later mutate; a losing writer can win under a
later tick's priority; even an all-inert world's ENERGY can still be
changing under replenishment/decay. `DEAD`/`FROZEN` below are therefore
split into a mathematically CERTIFIED variant and a heuristic,
explicitly CENSORED variant -- never conflated.]**

| Label | Working signature (trailing-window behavior) |
|---|---|
| DEAD_CERTIFIED | Provable, not heuristic: zero cells anywhere carry `opcode=WRITE` AND `REPLENISH_NUMER=0`. No WRITE proposal can ever be emitted again (so no `mutation_applied` event can ever fire either, since mutation only triggers on a winning WRITE, PHYSICS_SPEC_DRAFT.md), and energy is monotonically non-increasing under `MAINTENANCE_COST` with no inflow, reaching a fixed floor within at most `ceil(255/MAINTENANCE_COST)` ticks (immediately if `MAINTENANCE_COST=0`). After that many ticks under this precondition, `S[t]` is fixed forever -- safe to hard-stop. |
| DEAD_CENSORED | `activity_density -> 0` (near-zero) and stays there for a preregistered window, WITHOUT the `DEAD_CERTIFIED` precondition holding. This is a RIGHT-CENSORED stop, not a proof: reactivation via replenishment, a later-arriving external write, or a rare mutation on a still-live copy path remains possible and must be recorded as an open question, not excluded. |
| FROZEN_CENSORED | `activity_density` stabilizes `>0` but `change_rate -> 0` for a preregistered window (e.g. every contest's winner writes the same value that was already stored -- **[REPAIRED per ASTRA_REVIEW_01.md N02: "every proposal loses" is impossible, since every nonempty contest has exactly one winner by construction]**). Also a censored, not proven, stop -- a currently-losing writer can win under a later tick's priority, and a same-value winner can later mutate. |
| HOMOGENIZED | `state_entropy` collapses to near-0 for a targeted field (one byte value covers the lattice) while `activity_density` may stay `>0` |
| EXPLOSIVE | `change_rate` spikes far above its own later steady-state value in the first few ticks, typically followed by rapid `energy_total` depletion and transition to a DEAD/FROZEN/HOMOGENIZED label |
| PERIODIC | **[REPAIRED per S05]** `global_hash(t)` (or a coarser summary vector) matches at a candidate lag `p` is only a CANDIDATE, not a confirmed period: because `Mu`/`Rho` both hash in `tick` (PHYSICS_SPEC_DRAFT.md), `S[t1]=S[t2]` for `t1 != t2` does NOT imply `S[t1+1]=S[t2+1]` -- the two continuations are keyed by different tick values even from an identical lattice state. Confirmation requires checking FORWARD-trajectory agreement (`S[t1+k]=S[t2+k]`) for several `k`, not a single lattice-hash match at one lag. |
| CHAOTIC | `activity_density`/`state_entropy` stay bounded away from 0 without settling, AND `perturbation_divergence(t)` grows rapidly (super-linearly early, then saturating) from a single-bit initial difference |
| METASTABLE | `change_rate(t)` is heavy-tailed/bursty: long low-change intervals punctuated by rare large-change events, measured via burst-interval statistics rather than a single mean |
| STRUCTURED | `compression_ratio` and `spatial_autocorr` both indicate non-trivial structure (neither near-1 as random soup, nor near-0 as a single repeated value); PROVISIONAL at scout tier, CONFIRMED only after tier-2 data exists (OBSERVATORY.md M06 repair) |
| MOBILE | `component_track` (torus-aware, OBSERVATORY.md M08 repair) finds a component whose centroid displacement over time exceeds a pure-diffusion null baseline at the same activity density; PROVISIONAL at scout tier, CONFIRMED only after tier-2 data exists |
| BOUNDARY_FORMING | a persistent spatial discontinuity in a chosen field's local statistics (e.g. two adjacent regions each internally more homogeneous than the lattice-wide average, separated by a stable seam) survives across the trailing window |
| UNKNOWN | none of the above signatures clears its threshold, or two signatures conflict -- reported as-is, never forced into the nearest label |

A single run may match more than one label (e.g. STRUCTURED and
MOBILE together); labels are tags, not a partition. `_CERTIFIED` labels
carry a mathematical proof; `_CENSORED` labels carry only a stopping
tick and trigger metric and must be treated as right-censored data, not
as a resolved outcome, until an audit (K5, deferred) resamples a subset
to a fixed further horizon.

## Campaign design

1. **Scope: tiny worlds only (R13).** H, W in {4, 8, 16, 32}; run
   length short enough for full CPU exhaustive/property-test-style
   replay (a few thousand ticks, sized so `activity_density` and
   `change_rate` visibly stabilize or visibly fail to).
2. **Parameter axes swept**: `WRITE_COST`, `MAINTENANCE_COST`,
   `REPLENISH_NUMER` and `REPLENISH_AMOUNT` **[REPAIRED per
   ASTRA_REVIEW_01.md M04, ACCEPT, see REPAIR_LEDGER_01.md -- swept AS
   TWO SEPARATE AXES, not combined into one "mean inflow" product. A
   counterexample: at `MAINTENANCE_COST=2, WRITE_COST=3`, probability
   1/2 amount 2 never permits emission (energy caps at 2, can't cover a
   cost of 3), while probability 1/16 amount 16 does, after any single
   replenishment event -- both have the same mean nominal inflow (1 per
   tick) but qualitatively different reachability. Burstiness, not just
   mean, is load-bearing.]**, `MUT_NUMER`, initial WRITE density
   (EXPERIMENTS.md regime 2). Fix everything else (H, W, seed count per
   cell) per sweep.
3. **Coarse grid first.** Log-spaced grid over each axis (e.g. 5-7
   points per axis), Regime A and Regime B (ECONOMICS.md) run
   separately since they occupy different corners of the same space.
   Each grid cell replicated across >=8 independent seeds (random
   soup / sparse soup, EXPERIMENTS.md regimes 1-2) to get a majority
   label plus a disagreement rate (seeds landing on different labels
   at the same parameters is itself a reported quantity, not
   suppressed by majority voting). **[REPAIRED per M04]** `H,W` values
   must include at least one odd and one non-power-of-two pair, not
   only `{4,8,16,32}` -- an all-even, all-power-of-two grid privileges
   the torus's bipartite structure and short wraparound paths, an
   unaudited topology confound. Initial-writer-count at `t=0` is
   reported separately from later extinction (a 4x4 uniform-soup world
   has ~94% probability of zero writers at init at 1/256 opcode
   density -- absence-of-machinery is a different phenomenon from
   extinction-of-machinery, and must not be conflated in a DEAD label).
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
