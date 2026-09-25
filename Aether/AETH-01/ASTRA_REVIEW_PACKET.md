# AETH-01 -- Astra review packet (index)

Status: DRAFT design packet, no implementation, no Runpod spend.
Baseline commit: `2959a7274` (AETH-00B, last frozen/tested milestone).
This packet's own commit hash is reported alongside its delivery (see
git log; not self-referenced here to avoid a circular hash).

This index states facts and pointers. It does not tell you what to
conclude -- that is the point of an independent review.

## Aether's objective (unchanged from AETH-00-era framing)

A GPU-native artificial physics in which executable matter must
discover persistent organization, heredity, reproduction, and useful
computation without predefined organism/genome boundaries. Central
question: does removing predefined organism boundaries and changing
the representation of heredity expose evolutionary pathways discrete
genome evolution cannot reach? (AETHER_CONCEPT.md)

## Hard requirements and their status

Full table: REQUIREMENTS.md Part 1. Summary: 12 of 15 requirements
(R1, R2, R4, R6, R7, R8, R9, R10, R11, R12, R13, R15) assessed
SATISFIED (R4 and R7 carry stated caveats, not failures). Three (R3,
R5, R14) carry a named, unresolved TENSION -- not a violation, not
silently resolved:
- R3 (no externally imposed genome boundary): mutation excludes the
  energy field by construction, partially pre-deciding where heredity
  can live.
- R5 (endogenous persistence): initial energy is exogenous
  configuration, so persistence differences can reflect starting
  conditions rather than dynamics unless controlled for.
- R14 (alien organization possible): a single active opcode with no
  branch/compare primitive is a real expressivity ceiling.
No requirement was found impossible or mutually contradictory.

## Selected physics

Candidate 1, "Costed Executable Lattice" (PHYSICS_CANDIDATES.md):
AETH-00's toroidal von-Neumann lattice and WRITE/arbitration law,
extended with a 5th field (`energy`), an execution cost
(`WRITE_COST`), a conservative lossy transfer mechanism on that field,
optional maintenance decay and replenishment, and explicit,
domain-separated, replayable mutation on the other four fields. Full
formal contract: PHYSICS_SPEC_DRAFT.md (draft `semantics_id`
`aeth01.v1`, NOT frozen). Two rejected candidates (an asynchronous
chemistry-like reaction automaton; a mobile-particle dynamic-adjacency
automaton) are fully specified, not discarded, in PHYSICS_CANDIDATES.md.

## Most consequential design decisions

Full ledger: DECISIONS.md (14 entries, each with rationale,
alternatives, hidden prior, and a stated falsifier). The five most
load-bearing:
1. D-AETH01-01: chose Candidate 1 primarily for proven GPU viability
   and because construction/movement ambiguity directly instantiates
   an R6-required hard case rather than avoiding it.
2. D-AETH01-04: introduced explicit mutation, breaking AETH-00's
   "no byte synthesis" limitation on purpose, but excluding the
   resource field -- the source of the R3 tension above.
3. D-AETH01-05: energy transfer is unconditionally costed to the
   sender and destructively lost on contest loss (100% loss, not
   partial) -- an arbitrary point on a severity spectrum, chosen for
   simplicity.
4. D-AETH01-07: no literal matter-movement primitive exists;
   "movement" and "copying" are physically the same process --
   deliberate, reversible if this proves unresolvable even with full
   intervention evidence (HEREDITY_REQUIREMENTS.md).
5. D-AETH01-08: AETH-00's arbitration law is reused completely
   unmodified; its known non-neutrality caveat now has real economic
   stakes it did not have in AETH-00 (ADVERSARIAL_ANALYSIS.md #6, #16).

## Strongest scientific claims actually being made

Deliberately narrow, and none yet empirically tested (no code has been
run):
- The physics is FORMALLY COMPLETE enough for two independent
  implementers to build matching simulators (PHYSICS_SPEC_DRAFT.md) --
  a methodological claim, inherited from AETH-00's proven discipline,
  not yet independently verified for AETH-01 specifically.
- The energy accounting identity (PHYSICS_SPEC_DRAFT.md, "Conserved /
  accounted quantities") is an exact, zero-tolerance, testable
  invariant of the specification as written.
- Construction and literal movement are physically indistinguishable
  processes in this physics (by design, D-AETH01-07), which is offered
  as a genuine scientific opportunity (it forces the hardest heredity
  adversarial case to exist at the physics level) rather than a defect.
No claim is made yet about emergence, heredity, GPU correctness, or
scientific neutrality -- exactly mirroring AETH-00's own "Scope"
discipline (AETHER_SPEC.md).

## Unresolved questions (beyond the three named tensions above)

- Whether AETH-00's arbitration law is statistically neutral enough
  that its known non-neutrality caveat does not become a hidden
  "economic law" once real resource stakes are attached (ADVERSARIAL
  #6, #16) -- unverified, flagged as a required pre-campaign check
  (REQUIREMENTS.md).
- Whether the `Mu` mutation hash's trigger-bits and bit-index-bits are
  independent enough in practice (ADVERSARIAL #11) -- unverified.
- Whether the 5-axis habitability sweep (HABITABILITY.md) is even the
  right set of axes to find non-trivial regimes at all (D-AETH01-10's
  stated falsifier).
- Whether excluding literal movement (D-AETH01-07) will eventually
  force an R6 dead end that can only be resolved by adding a movement
  primitive as a new semantics_id.

## Known weaknesses, stated plainly

- Still an opcode/operand ("small VM") ontology, not a clean break from
  that style, despite R7's caution -- justified by continuity with
  AETH-00's proven testing methodology, not by any independent
  argument that this is the RIGHT ontology.
- No literal transport/movement primitive and no explicit
  gradient/boundary-maintenance primitive exist (ECONOMICS.md's cost
  table names both gaps openly).
- A single active opcode with no conditional/branch primitive is a
  real expressivity ceiling (R14 tension) that this design does not
  solve, only names for AETH-02.
- Nothing here has been run. Every number, threshold, and constant in
  PHYSICS_SPEC_DRAFT.md and ECONOMICS.md is a proposal, not a measured
  or validated value.

## Supporting documents

- `REQUIREMENTS.md` -- R1-R15 compliance table; engineering
  requirements (semantic/numerical/reliability/inference, kept separate).
- `PHYSICS_CANDIDATES.md` -- three candidate physics families, full
  specification of all three, selection rationale.
- `PHYSICS_SPEC_DRAFT.md` -- formal transition contract for the
  selected candidate, plus the representation/accessibility analysis.
- `ECONOMICS.md` -- cost-category mapping, three resource regimes, the
  persistent-state economic question, designed room for varied
  strategies.
- `EXPERIMENTS.md` -- seven initialization regimes; spontaneous/seeded
  separation mechanism.
- `HABITABILITY.md` -- measurable quantities, regime labels, campaign
  design (scout-tier grid, adaptive boundary refinement).
- `OBSERVATORY.md` -- 15-metric catalog (measures / does-not-establish /
  false positives / cost / tier for each), three-tier architecture.
- `HEREDITY_REQUIREMENTS.md` -- four-tier claim ladder, ten adversarial
  cases, novelty/gravitational-pull data-preservation requirements.
- `ADVERSARIAL_ANALYSIS.md` -- 22 specific ways this design could fool
  us, each with a control.
- `GPU_RUNPOD.md` -- batched-worlds architecture, scout->qualify->
  deepen->verify funnel, scope-comparison table (REJECT/DEFER/
  prerequisite-needed) for 13 named out-of-scope items.
- `DECISIONS.md` -- 14-entry provisional decision ledger.

## What this packet does not ask Astra to do

Does not ask for approval to implement. Does not pre-suggest which
tension (R3/R5/R14) matters most. Does not pre-suggest which rejected
candidate (PHYSICS_CANDIDATES.md) should be reconsidered first if
Candidate 1 fails its habitability sweep. Those are open for
independent judgment.
