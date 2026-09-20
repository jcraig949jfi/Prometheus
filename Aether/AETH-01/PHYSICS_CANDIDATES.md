# AETH-01 -- three physics candidates and selection

Status: DRAFT, not frozen. Baseline: AETH-00 frozen contract `aeth00.v1`
(commit `3ff4619de`), AETH-00A/B (`2d2468965`, `2959a7274`).

This document proposes three substantially different physics families
(not variations on opcode naming), specifies each along the required
axes, then selects one as the AETH-01 primary candidate. The two
rejected candidates are preserved in full below for Astra's review, not
deleted.

## Candidate 1 -- Costed Executable Lattice (chained extension of AETH-00)

- **State representation**: discrete 2-D toroidal lattice, von Neumann
  neighborhood, synchronous ticks (identical shape to AETH-00). Each
  site: 5 uint8 fields -- opcode, arg0, arg1, payload, **energy** (new).
  Matter carries its own rule (opcode IS the local law), exactly as
  AETH-00.
- **Local update law**: WRITE (0x01) still emits exactly one proposal
  (direction from arg0 mod 4, field from arg1 mod 5 -- now 5 fields,
  not 4) using only the tick-start snapshot; RESERVED_INERT (all other
  254+1 values) emits nothing. Same SplitMix64 chained max-arbitration
  law as `aeth00.v1`, reused unchanged (it already generalizes to a
  5-valued target_field with no change to the hash chain).
- **Source of change**: local, one-hop, instruction-like (a cell's own
  decoded opcode/operands determine its one proposal).
  Discrete/synchronous, not continuous/event-driven.
- **Information persistence**: a byte (opcode or payload) persists by
  being repeatedly re-copied (WRITE-templated) into place, or by simply
  never being targeted. No separate "memory" region; state IS the
  record.
- **Causal construction**: a cell can turn a neighbor's opcode field
  from RESERVED_INERT into WRITE (or vice versa) -- literally
  "switching on/off" a neighbor's own future agency -- and can template
  a neighbor's payload. Multi-field, multi-tick sequences of such
  writes are how anything more complex than a single copy gets built.
- **Resource/energy model (new, not in AETH-00)**: WRITE costs a fixed
  `WRITE_COST` debited from the source's own energy field before a
  proposal is even emitted; a cell below cost is starved (behaves as
  RESERVED_INERT that tick). Field 4 (energy) is a conservative
  TRANSFER, not an overwrite: source always pays the proposed amount
  once it attempts a transfer; only the contest winner's target is
  credited (saturating at 255); every losing transfer's amount is
  destroyed (dissipated), not refunded. Optional passive
  `MAINTENANCE_COST` decay and `REPLENISH_RATE` inflow (parameterized,
  see ECONOMICS.md) turn this into a real scarcity economy.
- **Failure modes**: freeze (energy exhausted, everything starves,
  lattice literally cannot change further); homogenization (one
  RESERVED_INERT value or one payload value colonizes everything via
  fast copying); explosive copying followed by resource collapse;
  chaotic flicker at high `P_MUT` (mutation, below); slow decay to a
  static residue under aggressive `MAINTENANCE_COST`.
- **GPU mapping**: identical shape to AETH-00's proven gather mapping --
  one lane per (target cell, target field) inspects <=4 physical
  neighbors, reduces each contest independently, writes a separate
  next-state buffer. Energy debits are also purely a function of each
  cell's own S[t] state (no cross-lane dependency at debit time); credit
  is the same reduction as any other field. No new parallelism hazard.
- **Major hidden priors**: von Neumann/toroidal locality (inherited from
  AETH-00); flat WRITE_COST regardless of target field/distance/content
  (arbitrary, not physically derived); mutation (if enabled, below)
  applies only to fields 0-3, never to energy -- segregates "genetic"
  information from "resource" information by construction, in tension
  with R3's instruction not to presume where heredity lives; single
  active opcode means no compare/branch/sense-then-act primitive exists
  -- conditional behavior is only expressible indirectly via what
  happens to be written where, never as an explicit "if."
- **What it may accidentally privilege**: small, spatially compact,
  fast-copying patterns (locality + per-hop cost reward tight loops
  over sprawling structures); "genome-in-the-instruction-fields, body
  absent" organization, since only 4 of 5 fields carry heritable-looking
  information and the 5th (energy) cannot itself be copied/mutated,
  only moved.

## Candidate 2 -- Asynchronous Local Reaction Automaton (chemistry-like)

- **State representation**: same lattice, but each site holds a small
  vector of discrete species counts (e.g. 4-8 species, 0-15 each,
  packed in a few bytes) rather than an opcode/operand tuple. No
  instruction is carried by matter; a small FIXED catalog of local
  reaction rules (rate constants, stoichiometry, at most 2-site range)
  is a law of the universe, not something a cell can rewrite.
- **Local update law**: event-driven. Each site independently draws
  reaction/diffusion events from a Poisson process parameterized by its
  local species counts and the fixed rate catalog (Gillespie-style
  continuous-time next-reaction, or a per-cell asynchronous clock).
  "Rules emerge from interaction" (concentration-dependent propensities)
  rather than "matter carries rules."
- **Source of change**: local (nearest-neighbor diffusion/reaction),
  but temporally asynchronous -- no universal tick; different sites
  update at different simulated times.
- **Information persistence**: concentration/ratio patterns (e.g. an
  autocatalytic cycle sustaining a species ratio against diffusion)
  rather than byte-identical templating. Persistence is a dynamical
  attractor property, not literal copying.
- **Causal construction**: one region can catalyze production of a
  species in a neighboring region (a real, measurable causal flux), but
  "construction" here means shifting concentrations, not assembling a
  discrete described object -- much harder to point to a single
  discrete construction *event*.
- **Resource/energy model**: naturally dissipative -- reactions consume
  a fixed "fuel" species supplied by an external gradient/boundary
  source and produce a "waste" species; scarcity is intrinsic to the
  reaction network's stoichiometry, not bolted on afterward.
- **Failure modes**: total fuel exhaustion (everything reaches a dead
  equilibrium); explosive autocatalysis (fuel consumed instantly,
  patterns strobe once and die); pure diffusion homogenization (any
  early pattern gets smeared out before reactions can sustain it);
  small-catalog degeneracy (the fixed reaction catalog turns out to
  support only one or two attractors regardless of initial condition).
- **GPU mapping**: POOR without approximation. Exact Gillespie
  next-reaction selection requires a global priority queue over event
  times -- pathological serial dependence (violates R12 directly). A
  synchronous tau-leaping approximation restores parallelism but
  introduces a second, harder-to-remove source of numerical
  non-reproducibility (leap-size-dependent bias) on top of the usual
  float/order concerns -- a real tension with R11 (exact replay).
- **Major hidden priors**: the reaction catalog itself is a huge,
  consequential design choice made once, up front, by us -- effectively
  hand-designing a chemistry, which risks smuggling in exactly the kind
  of privileged "useful mechanism" Aether is supposed to avoid presuming
  (R14). Continuous/real-valued rate constants also reopen float
  reproducibility problems AETH-00 deliberately avoided by staying
  uint8/uint64-only.
- **What it may accidentally privilege**: whatever autocatalytic cycles
  the hand-chosen catalog happens to support -- i.e., life-like
  organization defined by us in advance via the reaction network, which
  is close to the opposite of Aether's founding stance.

## Candidate 3 -- Mobile-Particle Dynamic-Adjacency Automaton

- **State representation**: discrete particles occupying positions in
  continuous or fine-grained 2-D space; each particle carries a small
  fixed state vector (a few bytes). Adjacency is NOT a fixed lattice
  edge -- two particles are neighbors iff within an interaction radius,
  so the interaction graph changes as particles move.
- **Local update law**: pairwise collision/binding rules, symmetric
  functions of both particles' states (billiard/molecular-dynamics
  style), applied whenever two particles come into range; a bound pair
  becomes a rigid or semi-rigid unit (an edge in a growing graph).
- **Source of change**: local and pairwise, but position updates
  (movement) are a first-class physical quantity here, not a byproduct
  of copying as in Candidate 1.
- **Information persistence**: via bound complexes -- once particles
  bind, the resulting graph structure persists until an explicit
  unbinding rule fires; state also persists trivially by particles
  simply not meeting anyone.
- **Causal construction**: very direct and literal -- adding a particle
  to a complex via a new bond IS a construction event, visible as a
  literal graph-edge addition with a definite cause (the collision that
  created it).
- **Resource/energy model**: naturally supports momentum/kinetic-energy
  conservation from the collision law itself; binding/unbinding can be
  tied to a local energy budget (making/breaking bonds costs or
  releases energy), a physically well-motivated fit for R8.
- **Failure modes**: universal crystallization (everything binds into
  one static maximal complex -- FROZEN); universal dispersion (nothing
  ever gets close enough to bind -- effectively DEAD); runaway
  fragmentation/aggregation oscillation; jamming (a densely packed
  region blocks all further movement).
- **GPU mapping**: MODERATE difficulty, well-precedented (GPU molecular
  dynamics is a mature field: spatial hashing/binning gives each cell
  of a coarse grid a bounded neighbor-candidate list, updated every
  step) -- plausible, but a materially bigger engineering lift than
  Candidate 1's fixed-lattice gather, and dynamic neighbor lists
  reintroduce order-dependence risk in collision resolution that must
  be arbitrated as carefully as AETH-00's WRITE contests.
- **Major hidden priors**: privileges spatial self-assembly / geometric
  packing as THE construction mechanism; "genome" would have to be
  reinterpreted as bond topology or spatial arrangement, which is
  scientifically interesting but means information storage capacity is
  tied to how much particles can physically pack together, not to an
  independent state-space (unlike Candidate 1, where a byte's meaning
  is decoupled from its neighbors' geometry).
- **What it may accidentally privilege**: crystal-like/close-packing
  organization and crack-propagation-style "growth," which resembles
  physical/chemical self-assembly far more than anything resembling
  computation or heredity-by-copying -- construction is easy to get,
  computation is not.

## Selection: Candidate 1 (Costed Executable Lattice) for AETH-01

Reasons, in order of weight:

1. **Direct, honest continuity with a validated conformance
   methodology.** AETH-00's arbitration law, replay-identity discipline,
   dual-oracle differential harness, and CPU/GPU mapping story are
   already built and 85-test validated. Extending the SAME lattice
   ontology (adding one field and reusing the identical arbitration
   hash unmodified) lets AETH-01 inherit that trust rather than
   re-earning it on unrelated machinery, at zero extra freedom-to-cheat
   (the extension is additive and small enough to fully specify below).
2. **GPU viability (R12) is not aspirational, it is proven.** Candidate
   2 is fundamentally hostile to R12 (exact Gillespie is serial by
   construction; the parallel-friendly approximation reopens R11).
   Candidate 3 is plausible but a substantially larger, riskier
   engineering bet for a first milestone beyond AETH-00.
3. **Construction/movement ambiguity is a feature here, not a bug
   (R6).** Because Candidate 1 has no literal particle-movement
   primitive, a "traveling pattern" and a "self-copying pattern" are
   PHYSICALLY IDENTICAL processes (repeated neighbor-copying), which
   directly instantiates the exact adversarial case (R6, and Design
   Task 8's "traveling structure vs. constructor") that a later
   heredity detector must resolve -- the physics forces the hard
   question to exist rather than defining it away.
4. **Resource economics (R8) attaches to the existing WRITE semantics
   with a small, fully specified addition** (one new field, one cost
   rule, one conservative transfer rule), rather than requiring an
   entirely new subsystem, keeping the whole spec small enough to
   formalize completely (Design Task 2) and to differentially test at
   AETH-00's scale of rigor.
5. Candidate 2's reaction catalog and Candidate 3's collision-binding
   law both require US to hand-pick a nontrivial rule set that already
   encodes a notion of "useful chemistry" -- a bigger R14 risk (baking
   in what organization must look like) than Candidate 1's single
   opcode.

Candidates 2 and 3 are **not discarded** -- they are credible AETH-02+
directions (chemistry-like reaction automata solve R6/R8 differently and
may be revisited once GPU tau-leaping or an event-driven GPU scheduling
trick is worth the R11 cost; mobile-particle systems remain the most
physically natural home for literal movement and momentum-based
resource models). Full specifications above are preserved for Astra's
independent judgment on whether Candidate 1 was the right call.
