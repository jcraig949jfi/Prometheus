# AETH-01 -- observatory v0 (Design Task 7)

Status: DRAFT. Physics and observation are separate layers (R10):
nothing below reads or writes lattice state; it only reads the
trace/state stream a run already produces, and turning any of it
on/off must not change a single committed byte (a required regression
test, REQUIREMENTS.md). **[REPAIRED per ASTRA_REVIEW_01.md M09, ACCEPT,
see REPAIR_LEDGER_01.md]** That regression test establishes only
NONINTERFERENCE, i.e. that enabling observation cannot itself perturb
the physics -- it does NOT establish that the trace's CONTENT is true
or causally complete. Every metric below is only as trustworthy as the
trace rows it reads; REQUIREMENTS.md's independent event-ledger
cross-check (Part 2) must pass, and REPAIR_LEDGER_01.md's K7 (tiny
audit of oracle/trace agreement including intentionally suppressed
events) must be run, before any metric here is used to support a
scientific claim rather than a debugging observation.

## Metric catalog

Each entry: what it measures / what it does NOT establish / likely
false positives / cost / tier.

**Activity density** -- fraction of sites proposing per tick. / Does
NOT establish organization, only that *something* is happening. /
False positive: uniform random soup at high WRITE density looks
"active" with zero structure. / O(H*W) per tick, trivial. / Always-on.

**State entropy** (per field, lattice-wide) -- how uniformly byte
values are distributed. / Does NOT establish anything about spatial
arrangement (a checkerboard and a random shuffle of the same two values
have identical entropy). / False positive: low entropy from a single
huge inert region misread as "one interesting structure." / O(H*W) per
tick. / Always-on.

**Local mutual information** (a site's state at t vs. its neighbor's
state at t+1) -- whether a neighbor's future state is statistically
predictable from a site's current state, beyond what tick-global
statistics predict. / Does NOT establish causation (correlation from
shared ancestry or a common upstream cause looks the same). / False
positive: two sites both being repeatedly overwritten by the same
distant fast-copying source show high mutual information despite never
directly interacting. / Moderate -- needs a sliding window of joint
histograms, O(H*W) per window. / Rolling forensic buffer.

**Persistence time** -- how long a given byte value, or a tracked
component's identity, persists before being overwritten/dispersed. /
Does NOT establish *why* something persisted (dynamics vs. simply never
being targeted). / False positive: a site nobody's arg0/arg1 ever
happens to address looks "persistent" for a boring combinatorial
reason. / Cheap if computed incrementally (track last-changed tick per
field). / Always-on counter, forensic detail on trigger.

**Spatial autocorrelation** -- similarity between a site and its
immediate neighbors, lattice-wide average. / Does NOT distinguish
"organized structure" from "one big homogenized blob" (both are highly
autocorrelated). / False positive: HOMOGENIZED regimes score exactly
like STRUCTURED ones on this metric alone -- must be paired with
entropy/compressibility. / O(H*W) per tick. / Always-on.

**Flux** -- count of winning proposals (by field, separately for
value-templating fields 0-3 and the energy field 4) crossing a chosen
spatial boundary per tick. / Does NOT establish direction of "benefit"
(an energy flux toward a site could be feeding or draining it,
ECONOMICS.md). / False positive: a region boundary drawn arbitrarily
(not aligned with any real structure) still reports nonzero flux from
ordinary background activity. / O(boundary length) per tick, cheap. /
Always-on for a few fixed boundaries; forensic for arbitrary ones.

**Conservation-equation check** -- verifies the exact energy
accounting identity (PHYSICS_SPEC_DRAFT.md, **[REPAIRED per
ASTRA_REVIEW_01.md S01 -- the single `X/A/C/D/R` identity, not the
double-counting form the reviewed draft used]**) holds every tick from
the trace's individual debit/credit/loss/spillage/decay/replenish rows. /
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
one site, and measure downstream divergence (Hamming distance over
time, or divergence in a specific downstream region/component). / Does
NOT by itself establish *what* the influenced structure does, only that
an influence exists and how far/fast it propagates. / False positive:
apparent "no influence" merely because the perturbed bit happened to be
in a field nobody ever reads that tick (a correctly-negative result,
but easy to over-interpret as "this region is unresponsive in
general"). / Expensive -- requires a full second run per intervention. /
Triggered/forensic only, never continuous.

**Connected-component persistence and tracking** -- group
currently-active (or currently-similar) sites into components, match
components frame-to-frame by maximal spatial overlap, and report each
tracked component's lifetime and identity-continuity. / Does NOT
establish that a tracked component is "the same thing" in any
biological sense -- component tracking is a bookkeeping convenience,
not a claim about individuality (R1); grouping/centroid/matching choices
can manufacture apparent individuality purely from the observer's
scale/window (M08). / False positive: two unrelated components that
happen to overlap spatially at one frame get merged into one false
causal provenance by the tracker. **[REPAIRED per ASTRA_REVIEW_01.md M08]** Any
centroid/displacement computation MUST be torus-aware (wrap-corrected,
e.g. via minimum-image convention on each axis) -- a naive Euclidean
centroid discontinuously jumps at the torus wrap boundary and would
misreport ordinary stationary components as suddenly "moving." /
Moderate (connected-components labeling each frame, O(H*W) with a
union-find). / Rolling forensic buffer.

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

**Causal provenance-like construction evidence (forensic only)** -- reconstruct,
from the trace, a provenance graph of "this target field's stored value
at tick t was contributed by winning source site X" chains, and look
for chains consistent with CAUSAL_VALUE_CONSTRUCTION,
CONSTRUCTED_CAPACITY, or RECURSIVE_CONSTRUCTION shapes
(HEREDITY_REQUIREMENTS.md, repaired). **[REPAIRED per ASTRA_REVIEW_01.md
M05, see REPAIR_LEDGER_01.md]** The graph must preserve, per contest:
ALL contenders (not only the winner), the winning proposal's
pre-perturbation and post-perturbation payload, the source's energy/starvation
status, and whether the write targeted an ENABLING field (opcode/arg0/
arg1, i.e. the target's own capacity) versus a CONTENT field (payload)
-- winner-only, content-blind provenance cannot distinguish
CAUSAL_VALUE_CONSTRUCTION from CONSTRUCTED_CAPACITY at all. / Does NOT
by itself establish configuration transmission in any inference-worthy sense -- this is
raw graph reconstruction, evidence gathering, not a verdict; winners-
only edges also miss enabling, redundant, and initial-scaffold causes.
/ False positive: convergent copying from a shared, unrelated source
(two targets both repeatedly overwritten by the same distant fast
state copier) produces a causal provenance-graph shape indistinguishable from true
shared ancestry without further intervention-based checks; an arbitrary
source-bit perturbation causing Hamming divergence is not sufficient
attribution by itself, since it may destroy routing/energy rather than
transmitted information -- content-vs-enabling interventions (above)
and redundancy-aware joint ablation/rescue are required, not a single
perturbation. / Expensive (full trace replay + graph construction over
a window). / Triggered/forensic only, always paired with raw trace
retention (below).

Scientific claim tiers are separate from the telemetry-cost tiers below.
Use the FIVE-tier ladder in HEREDITY_REQUIREMENTS.md:
STRUCTURAL_RESEMBLANCE / CAUSAL_VALUE_CONSTRUCTION / CONSTRUCTED_CAPACITY /
RECURSIVE_CONSTRUCTION / TRANSMITTED_VARIATION. Reports also name the
mechanism and source set: K3 fixture 3 is distributed construction by
A_opcode and A_arg0 with initialized scaffold; fixture 4 is recursive
activation of preconfigured machinery, not recursive configuration
construction. Byte changes in enabling fields must change decoded
behavior under intervention; a neutral routing-byte change is only
value evidence. Fixture-local checks are not a qualified general detector.

## Tiered architecture

**[REPAIRED per ASTRA_REVIEW_01.md M06, see REPAIR_LEDGER_01.md -- the
reviewed draft let STRUCTURED/MOBILE/CHAOTIC promotion decisions depend
on tier-2/3 data scouts never compute, and verified only PROMOTED
worlds, leaving false-negative simulator failures unaudited.]**

1. **Cheap always-on counters** (every tick, every run, negligible
   overhead): activity density, state entropy, spatial autocorrelation,
   flux on a small fixed set of boundaries, byte diversity, the
   conservation-equation check, and the coarse periodicity summary
   signal. These alone drive the habitability sweep's PROVISIONAL
   labels only (HABITABILITY.md) -- a scout run may assign
   `PROVISIONAL_STRUCTURED`/`PROVISIONAL_MOBILE`/etc. from tier-1 proxies
   alone, but may NOT assign the CONFIRMED `STRUCTURED`/`MOBILE`/
   `CHAOTIC` labels, which require tier-2/3 data (below) that does not
   exist yet at this tier.
2. **Rolling forensic buffers** (a bounded recent-history window, e.g.
   last N ticks of full trace + full lattice snapshots, continuously
   overwritten unless frozen): local mutual information, persistence
   timers, compressibility samples, component tracking, boundary
   stability, transport tracking. Cheap enough to run on every "deepen"
   tier run (HABITABILITY.md step 5), not on every scout-tier run.
   CONFIRMED labels may be assigned once this tier's data exists.
3. **Expensive triggered analysis** (fires only on a predefined
   mechanical trigger -- e.g. a tracked component persists past a
   duration threshold, a boundary persists past a threshold, or a
   habitability-sweep run lands in a flagged non-trivial label):
   intervention/perturbation runs, full-state periodicity confirmation,
   causal provenance-graph reconstruction. On trigger, the rolling forensic
   buffer covering the anomaly is PROMOTED to permanent storage
   (never overwritten) before any further analysis -- raw evidence
   around anomalies is preserved first, interpreted second, per
   doctrine item 8 (AETHER_DOCTRINE.md).
4. **Mandatory negative/rejected-world audit (NEW, M06 repair).** A
   fixed, preregistered fraction (recommended 5%, never 0%) of
   scout-tier `DEAD`/`FROZEN`/`UNKNOWN`-labeled worlds is promoted to
   the qualify tier REGARDLESS of their scout label, specifically to
   measure the false-negative rate of the scout tier itself (CPU/GPU
   differential agreement AND a check for any tier-1-invisible
   activity). Every campaign report states this audit's sample size,
   denominators, and outcome distribution alongside the promoted-
   positive results -- "unmeasured" is never reported as "negative."

No metric here is included merely because it "sounds scientific" -- each
was chosen because it has a stated cost, a stated false-positive mode,
and a stated tier; anything that could not be given all three was left
out of this draft rather than added speculatively.
