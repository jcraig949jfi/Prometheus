# AETH-01 -- provisional decision ledger (Design Task 15)

Status: every entry PROVISIONAL. Nothing here is scientifically sacred;
each entry states its own reversal condition. Numbered `D-AETH01-nn`,
distinct from the frozen `AETHER_DECISIONS.md` D-1..D-19 (AETH-00),
which this ledger does not touch or reopen.

**D-AETH01-01 -- Selected Candidate 1 ("Costed Executable Lattice") as
the AETH-01 primary physics.**
Rationale: proven GPU mapping and conformance methodology (reuses
AETH-00's arbitration law unmodified); construction/movement ambiguity
is a feature for R6 rather than a defect.
Alternatives considered: Candidate 2 (asynchronous reaction automaton,
PHYSICS_CANDIDATES.md) -- rejected primarily on R12 (exact Gillespie is
serial); Candidate 3 (mobile-particle dynamic-adjacency) -- rejected as
a larger, riskier engineering bet for this milestone, not as
scientifically inferior.
Hidden prior introduced: keeps AETH-00's opcode/operand ("small VM")
ontology rather than a chemistry- or particle-based one; R7's caution
against recreating a conventional VM is only partially honored.
Falsifier/reversal: **[TIGHTENED per ASTRA_REVIEW_01.md B03, see
REPAIR_LEDGER_01.md -- "reasonably thorough" named no finite
adjudication]** if the full coarse grid specified in HABITABILITY.md
step 3 (5-7 points/axis, Regime A and B, >=8 seeds/point, including at
least one odd and one non-power-of-two H/W pair per M04's repair) shows
`DEAD_CERTIFIED`/`DEAD_CENSORED`/`FROZEN_CENSORED`/`HOMOGENIZED` as the
majority label at >=90% of grid points with no adjacent-point
disagreement warranting refinement (HABITABILITY.md step 4), Candidate
2 or 3 should be built next instead of iterating further on Candidate
1's parameters alone.

**D-AETH01-02 -- Extend site state from 4 to 5 uint8 fields, adding
`energy`, rather than a separate resource substrate/layer.**
Rationale: minimal, additive change; reuses AETH-00's arbitration law
with no modification (field index is already a generic uint64 input).
Alternatives considered: a separate global resource grid decoupled from
the executable-matter grid -- rejected as a bigger ontological
commitment (two coupled substrates) for no established need yet.
Hidden prior: resource capacity is capped at exactly the same 0-255
range and same physical location as the instruction fields, coupling
"how much matter can hold" to the same byte-width choice made for
opcode/payload for engineering convenience, not a physical derivation.
**[REPAIRED per ASTRA_REVIEW_01.md M01, see REPAIR_LEDGER_01.md]** This
entry described the 5-field extension as purely additive; it is NOT
additive at the `arg1` field-SELECTOR level -- extending the selector
from mod-4 to mod-5 destroys AETH-00's single-bit-neutral subspace
entirely (no power of two is divisible by 5), a real, accepted mutation-
topology change, not analyzed in the original version of this entry.
Falsifier/reversal: **[TIGHTENED per B03]** if 0-255 is shown, via K1's
hand-worked cases or the (deferred) K4 economic gates, to saturate or
floor in >50% of a preregistered Regime-B parameter sample before any
non-trivial dynamics are observed, revisit field width (e.g. uint16
energy) as a new semantics_id.

**D-AETH01-03 -- WRITE costs a fixed `WRITE_COST`, debited
unconditionally from the source before emission; insufficient energy
causes starvation (RESERVED_INERT-like behavior that tick only).**
Rationale: minimal, single mechanism realizing R8's "remaining
active"/"executing local transformations" cost categories.
Alternatives considered: cost proportional to target distance or field
(rejected as unjustified added complexity for a first milestone,
ADVERSARIAL_ANALYSIS.md notes the flat-cost prior explicitly instead).
Hidden prior: cost is content- and direction-independent -- an
arbitrary simplification, named in PHYSICS_SPEC_DRAFT.md's
accessibility analysis (moat #3).
Falsifier/reversal: **[TIGHTENED per B03]** if K4's isolated
pulse-budget cell probe (deferred this cycle) shows >90% of a
preregistered sample of surviving strategies converge on the identical
narrow behavior class (e.g. minimal-cost same-value writes) across
Regime B's parameter range, a content/direction-sensitive cost model
should be designed as a new semantics_id.

**D-AETH01-04 -- Introduce explicit, reproducible mutation (`Mu`,
single-bit flip at rate `MUT_NUMER`) on fields 0-3 only, breaking
AETH-00's "no byte synthesis" property on purpose.**
Rationale: AETH-00 explicitly disqualified itself from being a
primordial physics because its distinct-byte-value count can only
shrink (AETHER_SPEC.md, "Known limitation"); AETH-01 is the first
candidate that must address this, and a domain-separated, explicit,
seed/tick/target-keyed hash keeps it exactly as replayable as
arbitration (R11).
Alternatives considered: no mutation at all (kept as `MUT_NUMER=0`, a
valid degenerate case, not removed as an option); mutation applied
uniformly across all 5 fields including energy -- rejected because a
"mutated" conserved quantity has no clean physical source/sink
interpretation (would break the accounting equation).
Hidden prior: mutation strictly excludes the resource field, which is
the R3-tension already named in REQUIREMENTS.md and
PHYSICS_SPEC_DRAFT.md. **[REPAIRED per ASTRA_REVIEW_01.md B02]** This is
NOT, by itself, proof that resource-handling traits cannot be
inherited: routing/capacity-use patterns encoded in fields 0-3 can
still vary and be inherited; the MORE restrictive fact was the
observer's own planned categorical exclusion of resource-flow evidence,
now removed (HEREDITY_REQUIREMENTS.md S04 repair).
Falsifier/reversal: if this asymmetry is shown to make resource-handling
strategies structurally impossible to inherit (as opposed to merely
indirect), a further semantics revision allowing energy-field variation
via a separately-accounted mechanism should be designed.

**D-AETH01-05 -- Conservative, lossy energy transfer: source always
pays the attempted amount; only the arbitration winner is credited;
losers' amounts are destroyed, not refunded or redirected.**
Rationale: makes contested transport genuinely risky (a real, testable
economic pressure, ECONOMICS.md), and keeps a single unified
arbitration law across all 5 fields rather than needing a second
conflict-resolution mechanism just for energy.
Alternatives considered: refund losers (rejected -- makes transfer
attempts free except for WRITE_COST, undermining the scarcity goal);
split a contested amount proportionally among losers (rejected -- adds
complexity and a new non-integer-friendly rule with no stated
scientific motivation).
Hidden prior: contested transfer is maximally punishing (100% loss),
an arbitrary point on a spectrum of possible partial-loss rules.
Falsifier/reversal: **[TIGHTENED per B03]** if a preregistered K4 sample
(deferred this cycle) shows winning transfer proposals occur in <1% of
opportunities across a swept Regime-B grid (i.e. contests are so risky
that transfer is essentially never attempted-and-won), a partial-loss
variant should be tried as a new semantics_id.

**D-AETH01-06 -- Maintenance decay and replenishment are one
parameterized law; Regimes A/B/C (ECONOMICS.md) are parameter points,
not separate physics.**
Rationale: keeps exactly one transition function to specify and test;
qualification can start at the simplest point (Regime A) without a
second code path.
Alternatives considered: genuinely different physics for a
"conservation-only" vs. "metabolic" mode -- rejected as needless
duplication of the conformance/testing burden for no added expressive
power (both are reachable as parameter settings of one law).
Hidden prior: assumes decay and replenishment are well-modeled as
uniform, spatially-blind per-cell probabilities -- no notion of
distance-to-a-resource-source or spatial gradient exists yet (partially
addressed by EXPERIMENTS.md's heterogeneous-environment regime, which
varies parameters by zone rather than by a continuous field).
Falsifier/reversal: if heterogeneous-environment experiments show
zone-level parameter variation is too coarse to produce interesting
gradient-following dynamics, a continuous spatial resource FIELD
(rather than per-cell independent Bernoulli draws) should be designed
as a new semantics_id.

**D-AETH01-07 -- No primitive relocates an (opcode,arg0,arg1,payload)
tuple as a unit; movement only emerges from repeated copying.**
Rationale: keeps the spec small; directly operationalizes the
traveling-structure-vs-constructor ambiguity R6 requires be
distinguishable later (PHYSICS_CANDIDATES.md selection reason 3).
Alternatives considered: an explicit MOVE opcode/mechanism -- rejected
for AETH-01 as an added primitive without a stated need yet (doctrine
item 7), and as a bigger step toward Candidate 3's ontology than
justified by any finding so far.
Hidden prior: "movement" and "replication" are physically fused by this
choice; a system that badly needs literal relocation (e.g. to model
real transport cost distinct from copying cost) cannot express it.
Falsifier/reversal: if HEREDITY_REQUIREMENTS.md's traveling-structure
adversarial case turns out to be UNRESOLVABLE even with full lineage
graphs and intervention testing (i.e. copying-based movement and
copying-based construction are provably indistinguishable from any
evidence the physics can produce), a literal movement primitive should
be added as a new semantics_id specifically to make the distinction
possible.

**D-AETH01-08 -- Reuse AETH-00's SplitMix64 arbitration law unchanged;
only the target_field domain widens from mod 4 to mod 5.**
Rationale: the frozen law already generalizes to any uint64
target_field value with no change to the hash chain or its
tie-freedom proof (AETHER_SPEC.md); re-deriving a new law would be
pure risk with no benefit.
Alternatives considered: none seriously considered -- this is the
lowest-risk option available and no reason to deviate was found.
Hidden prior: whatever positional/statistical-neutrality caveats
already apply to AETH-00's law (AETHER_SPEC.md's explicit
non-neutrality caveat) now apply with economic stakes attached
(ADVERSARIAL_ANALYSIS.md #6, #16), which AETH-00 itself did not have.
Falsifier/reversal: if AETH-01's statistical-diagnostic rerun (an
AETH-00A-style stratified sweep, REQUIREMENTS.md) finds a bias that
was invisible at AETH-00's stakes but material at AETH-01's (e.g.
consistently determines who wins scarce energy), the arbitration law
itself -- not just its consequences -- must be revisited.

**D-AETH01-09 -- Replay identity extends to an 11-component tuple**
(`semantics_id, H, W, seed, tick, WRITE_COST, MAINTENANCE_COST,
REPLENISH_NUMER, REPLENISH_AMOUNT, MUT_NUMER, lattice bytes`).
Rationale: all five new parameters are causally load-bearing inputs to
the transition law (PHYSICS_SPEC_DRAFT.md), not observational metadata,
so AETH-00's own replay-identity discipline requires including them.
Alternatives considered: treating parameters as external campaign
config rather than part of replay identity -- rejected because two
runs with identical seed/tick/lattice-bytes but different WRITE_COST
are NOT the same physics trajectory and must not be compared as if
they were.
Hidden prior: none beyond what AETH-00 already introduced by having a
replay-identity concept at all.
Falsifier/reversal: if a future milestone adds more run parameters,
this tuple must grow again the same way -- this is a standing pattern,
not a one-time decision.

**D-AETH01-10 -- Habitability campaign scoped to H,W in {4,8,16,32} and
a five-axis parameter sweep (WRITE_COST, MAINTENANCE_COST, combined
inflow rate, MUT_NUMER, initial WRITE density).**
Rationale: satisfies R13 directly; keeps the scout tier cheap enough to
run on CPU alone if needed, GPU only for scale-up.
Alternatives considered: sweeping H,W as a first-class axis too --
deferred, not rejected, to keep the first sweep's dimensionality
tractable (HABITABILITY.md).
Hidden prior: assumes the five chosen axes are the most informative
ones; other axes (e.g. neighborhood shape, were it swept) are not
explored at all in this design.
Falsifier/reversal: if scout-tier results are uninformative or
contradictory across replicate seeds at every point in this 5-axis
grid, the axis choice itself (not just the grid resolution) should be
reconsidered before assuming the physics itself is uninteresting.

**D-AETH01-11 -- Heredity claims are structured into four strictly
ordered tiers (STRUCTURAL_RESEMBLANCE / CAUSAL_CONSTRUCTION /
RECURSIVE_CONSTRUCTION / HERITABLE_VARIATION), each requiring
intervention evidence, not pattern-matching alone.**
Rationale: directly implements D-11 (AETHER_DECISIONS.md, AETH-00-era)
and AETHER_DOCTRINE.md's falsification-over-confirmation stance at the
most consequential possible claim category.
Alternatives considered: a single binary "heredity detected" flag --
rejected outright as incompatible with D-11 and with
HEREDITY_REQUIREMENTS.md's adversarial-case table, which specifically
requires distinguishing degrees of evidence.
Hidden prior: the four-tier ordering itself is a design choice; a
different taxonomy might carve the evidence space differently.
Falsifier/reversal: if, once a detector is actually built, real
specimens repeatedly produce evidence that does not fit cleanly into
any one tier (e.g. genuinely partial/graded cases), the tier boundaries
-- not the requirement for tiers at all -- should be revisited.

**D-AETH01-12 -- Spontaneous/seeded separation via an
`instrument_class` provenance tag plus a mandatory structural-
fingerprint cross-check, never encoded in lattice bytes.**
Rationale: directly implements R1/R10 and D-9/D-11 (seeded structures
are calibration instruments, never evidence of spontaneous origin).
Alternatives considered: relying on campaign-script discipline alone
(no automated cross-check) -- rejected as insufficient given
ADVERSARIAL_ANALYSIS.md #5's explicit contamination scenario.
Hidden prior: assumes a structural-fingerprint match is a reliable
contamination signal; a sufficiently different-looking but still
leaked/copied pattern could in principle evade this specific check.
Falsifier/reversal: if a contamination incident is ever found that this
check did not catch, the fingerprinting method (not just this
instance) must be strengthened before further spontaneous-origin claims
are trusted.

**D-AETH01-13 -- GPU/Runpod funnel does deepen/verify analysis on CPU,
never on-GPU, in AETH-01.**
Rationale: AETH-01's tiny-world scale (R13) makes CPU replay of
flagged worlds cheap (AETH-00B's measured ~300K cell-steps/second);
building GPU-side forensic/intervention analysis is unjustified
engineering cost for a first milestone.
Alternatives considered: on-GPU forensic buffers and intervention runs
-- deferred, not rejected outright; may become necessary if the deepen
tier's flagged-world count grows too large for CPU replay to keep up.
Hidden prior: assumes the deepen tier will remain a small fraction of
the scout tier's population; if habitability turns out to be common
rather than rare in the swept parameter space, this assumption fails.
Falsifier/reversal: if the deepen tier's CPU replay backlog becomes the
throughput bottleneck of an actual campaign, on-GPU forensic tooling
should be designed at that point, not preemptively.

**D-AETH01-14 -- Explicit agents, external GA loops, neural networks,
and LLMs-in-physics are REJECTED for AETH-01 and its immediate
successors, not merely deferred.**
Rationale: each would presuppose exactly the organizational categories
(R1, R2, R14) Aether is designed to let emerge rather than assume.
Alternatives considered: "defer" rather than "reject" -- rejected as
too weak a statement for mechanisms that are foundationally
incompatible with the stated scientific question (AETHER_CONCEPT.md),
as opposed to merely not-yet-justified (which is the DEFER category,
GPU_RUNPOD.md).
Hidden prior: none beyond the founding stance itself, which this
decision merely re-affirms in the specific context of AETH-01's
engineering scope.
Falsifier/reversal: only a deliberate, operator-approved change to
Aether's founding scientific question (not an engineering convenience)
could reverse this.
