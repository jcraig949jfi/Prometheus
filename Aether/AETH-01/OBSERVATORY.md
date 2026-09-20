# AETH-01 -- observatory v0 (Design Task 7)

Status: DRAFT. Physics and observation are separate layers (R10):
nothing below reads or writes lattice state; it only reads the
trace/state stream a run already produces, and turning any of it
on/off must not change a single committed byte (a required regression
test, REQUIREMENTS.md).

## Metric catalog

Each entry: what it measures / what it does NOT establish / likely
false positives / cost / tier.

**Activity density** -- fraction of cells proposing per tick. / Does
NOT establish organization, only that *something* is happening. /
False positive: uniform random soup at high WRITE density looks
"active" with zero structure. / O(H*W) per tick, trivial. / Always-on.

**State entropy** (per field, lattice-wide) -- how uniformly byte
values are distributed. / Does NOT establish anything about spatial
arrangement (a checkerboard and a random shuffle of the same two values
have identical entropy). / False positive: low entropy from a single
huge inert region misread as "one interesting structure." / O(H*W) per
tick. / Always-on.

**Local mutual information** (a cell's state at t vs. its neighbor's
state at t+1) -- whether a neighbor's future state is statistically
predictable from a cell's current state, beyond what tick-global
statistics predict. / Does NOT establish causation (correlation from
shared ancestry or a common upstream cause looks the same). / False
positive: two cells both being repeatedly overwritten by the same
distant fast-copying source show high mutual information despite never
directly interacting. / Moderate -- needs a sliding window of joint
histograms, O(H*W) per window. / Rolling forensic buffer.

**Persistence time** -- how long a given byte value, or a tracked
component's identity, survives before being overwritten/dispersed. /
Does NOT establish *why* something persisted (dynamics vs. simply never
being targeted). / False positive: a cell nobody's arg0/arg1 ever
happens to address looks "persistent" for a boring combinatorial
reason. / Cheap if computed incrementally (track last-changed tick per
field). / Always-on counter, forensic detail on trigger.

**Spatial autocorrelation** -- similarity between a cell and its
immediate neighbors, lattice-wide average. / Does NOT distinguish
"organized structure" from "one big homogenized blob" (both are highly
autocorrelated). / False positive: HOMOGENIZED regimes score exactly
like STRUCTURED ones on this metric alone -- must be paired with
entropy/compressibility. / O(H*W) per tick. / Always-on.

**Flux** -- count of winning proposals (by field, separately for
value-templating fields 0-3 and the energy field 4) crossing a chosen
spatial boundary per tick. / Does NOT establish direction of "benefit"
(an energy flux toward a cell could be feeding or draining it,
ECONOMICS.md). / False positive: a region boundary drawn arbitrarily
(not aligned with any real structure) still reports nonzero flux from
ordinary background activity. / O(boundary length) per tick, cheap. /
Always-on for a few fixed boundaries; forensic for arbitrary ones.

**Conservation-equation check** -- verifies the exact energy
accounting identity (PHYSICS_SPEC_DRAFT.md) holds every tick from the
trace's individual debit/credit/loss/spillage/decay/replenish rows. /
Does NOT establish anything scientific about the physics (the identity
is guaranteed BY the transition law) -- a violation means an
IMPLEMENTATION or INSTRUMENTATION defect, never a physics finding. /
False positive: none expected if correct; a "false negative" (bug that
happens to still balance) is the real risk, so this check is necessary
but not sufficient evidence of correctness. / O(H*W) per tick,
trivial arithmetic. / Always-on, and a required CI-style regression
test independent of any live run.

**State/byte diversity** -- count of distinct (opcode,arg0,arg1,payload)
4-tuples present. / Does NOT establish functional diversity (two
4-tuples can differ in a byte that is behaviorally irrelevant, e.g. any
two RESERVED_INERT opcodes). / False positive: high diversity from pure
noise (random soup) misread as "rich organization." / O(H*W log(H*W))
per tick (needs a set/hash). / Always-on.

**Compressibility** -- generic-compressor output size on the raw
lattice bytes, relative to a same-size random-byte baseline. / Does NOT
establish what kind of structure is present, only that some exists;
also confounded by choice of compressor. / False positive: a single
large uniform region compresses extremely well and looks "highly
structured" by this metric alone even though it is just HOMOGENIZED. /
Cheap-moderate (a fast general compressor, run periodically not every
tick). / Rolling forensic buffer (e.g. every N ticks).

**Causal influence under intervention** -- fork a replay from an
identical (semantics_id, params, S[t]) state, flip exactly one field of
one cell, and measure downstream divergence (Hamming distance over
time, or divergence in a specific downstream region/component). / Does
NOT by itself establish *what* the influenced structure does, only that
an influence exists and how far/fast it propagates. / False positive:
apparent "no influence" merely because the perturbed bit happened to be
in a field nobody ever reads that tick (a correctly-negative result,
but easy to over-interpret as "this region is unresponsive in
general"). / Expensive -- requires a full second run per intervention. /
Triggered/forensic only, never continuous.

**Connected-component persistence and tracking** -- group
currently-active (or currently-similar) cells into components, match
components frame-to-frame by maximal spatial overlap, and report each
tracked component's lifetime and identity-continuity. / Does NOT
establish that a tracked component is "the same thing" in any
biological sense -- component tracking is a bookkeeping convenience,
not a claim about individuality (R1). / False positive: two unrelated
components that happen to overlap spatially at one frame get merged
into one false lineage by the tracker. / Moderate (connected-components
labeling each frame, O(H*W) with a union-find). / Rolling forensic
buffer.

**Boundary stability** -- whether a detected spatial discontinuity
(HABITABILITY.md's BOUNDARY_FORMING signature) persists, moves, or
dissolves over a window. / Does NOT establish the boundary is doing
anything functional (containment, protection) versus being an inert
frozen seam. / False positive: any FROZEN region trivially has
"stable boundaries" everywhere by having no change at all. / Moderate,
depends on the underlying boundary-detection pass. / Rolling forensic
buffer, deepened on trigger.

**Transport (mobility) tracking** -- centroid displacement of a tracked
component over time, compared against a pure-diffusion null model at
matched activity density. / Does NOT establish self-propulsion or
purpose -- copying-driven "movement" and true translation are
physically identical processes here (PHYSICS_SPEC_DRAFT.md). / False
positive: an artifact of component-tracker mis-merging can look like
fast, coherent movement. / Moderate (reuses component tracking). /
Rolling forensic buffer.

**Periodicity detection** -- autocorrelation / recurrence of a global
summary signal (or the full-state hash) at candidate lags. / Does NOT
establish the mechanism producing the period, only that one exists. /
False positive: the SYNCHRONOUS TICK ITSELF and a low-period
arbitration artifact (a small toroidal world where a fixed hash pattern
recurs early) can manufacture apparent periodicity with no interesting
internal cause -- must be checked against tiny/degenerate dimensions
specifically (H,W in {1,2}) as a known confound. / Cheap for a coarse
summary signal, moderate for full-state hashing. / Always-on for the
coarse signal; forensic for full-state confirmation.

**Lineage-like construction evidence (forensic only)** -- reconstruct,
from the trace, a provenance graph of "this target field's stored value
at tick t was contributed by winning source cell X" chains, and look
for chains consistent with CAUSAL_CONSTRUCTION or
RECURSIVE_CONSTRUCTION shapes (HEREDITY_REQUIREMENTS.md). / Does NOT by
itself establish heredity in any inference-worthy sense -- this is raw
graph reconstruction, evidence gathering, not a verdict. / False
positive: convergent copying from a shared, unrelated source (two
targets both repeatedly overwritten by the same distant fast copier)
produces a lineage-graph shape indistinguishable from true shared
ancestry without further intervention-based checks. / Expensive (full
trace replay + graph construction over a window). / Triggered/forensic
only, always paired with raw trace retention (below).

## Tiered architecture

1. **Cheap always-on counters** (every tick, every run, negligible
   overhead): activity density, state entropy, spatial autocorrelation,
   flux on a small fixed set of boundaries, byte diversity, the
   conservation-equation check, and the coarse periodicity summary
   signal. These alone drive the habitability sweep (HABITABILITY.md).
2. **Rolling forensic buffers** (a bounded recent-history window, e.g.
   last N ticks of full trace + full lattice snapshots, continuously
   overwritten unless frozen): local mutual information, persistence
   timers, compressibility samples, component tracking, boundary
   stability, transport tracking. Cheap enough to run on every "deepen"
   tier run (HABITABILITY.md step 5), not on every scout-tier run.
3. **Expensive triggered analysis** (fires only on a predefined
   mechanical trigger -- e.g. a tracked component survives past a
   duration threshold, a boundary persists past a threshold, or a
   habitability-sweep run lands in a flagged non-trivial label):
   intervention/perturbation runs, full-state periodicity confirmation,
   lineage-graph reconstruction. On trigger, the rolling forensic
   buffer covering the anomaly is PROMOTED to permanent storage
   (never overwritten) before any further analysis -- raw evidence
   around anomalies is preserved first, interpreted second, per
   doctrine item 8 (AETHER_DOCTRINE.md).

No metric here is included merely because it "sounds scientific" -- each
was chosen because it has a stated cost, a stated false-positive mode,
and a stated tier; anything that could not be given all three was left
out of this draft rather than added speculatively.
