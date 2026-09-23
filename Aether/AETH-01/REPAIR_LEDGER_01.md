# AETH-01 -- repair ledger against ASTRA_REVIEW_01.md

Status: repair-cycle record. Base reviewed design: `5e41c1d679fc52394cbb6efd2f56a41bd8483604`.
Controlling review: `ASTRA_REVIEW_01.md` (verdict `PROCEED_TO_REPAIR`).
This ledger does not edit or erase the review. Every item S01-S06,
M01-M09, N01-N04, B01-B03, K1-K8 is dispositioned below. "REJECT"
entries carry a counterexample or derivation, not an appeal to intent,
per instructions.

Column legend: **Disposition** in {ACCEPT, ACCEPT_WITH_QUALIFICATION,
REJECT}. **Changes** lists which of {semantics, experiment_design,
inference_contract, instrumentation, engineering_only} the repair
touches. **New semantics_id?** states whether the repair changes
`aeth01.v1`'s transition law (yes => folded into the repaired freeze
candidate as part of the SAME still-unfrozen draft id, since `aeth01.v1`
was never frozen) or is documentation/tooling only (no).

## STOP-SHIP items

### S01 -- mandatory energy identity contradicts the transition law

- **Claim:** the printed conservation identity double-subtracts
  `TransferLost`/`OverflowSpillage`, which are already implied by
  `-TransferAttempted[t] + TransferCredited[t]`. Proven by the 2-donor
  counterexample (predicted 0, actual 1).
- **Disposition:** ACCEPT.
- **Reasoning:** the counterexample is arithmetically exact. Let
  `A = C + L + O` (attempted = credited + lost + overflow, at a given
  target/tick). `E - X - A + C - D + R` reduces to `E - X - L - O - D + R`
  by substitution -- the two forms Astra names are the SAME quantity,
  not two independent checks; the reviewed spec used a THIRD, wrong,
  combined form (`E - X - A + C - L - O - D + R`) that adds `-L-O` on
  top of a term that already contains `-L-O`. No defense exists; this
  is pure algebra.
- **Affected docs:** `PHYSICS_SPEC_DRAFT.md` ("Conserved / accounted
  quantities", "Creation / destruction rules"), `OBSERVATORY.md`
  (conservation-equation-check metric), `REQUIREMENTS.md` (Part 2,
  "energy conservation equation... checked as an exact property").
- **Exact repair:** adopt the single `A`/`C` form as the ONE authoritative
  identity: `E[t+1] = E[t] + ReplenishAccepted[t] - ExecutionCost[t]
  - TransferAttempted[t] + TransferCredited[t] - MaintenanceRemoved[t]`.
  `TransferLost` and `OverflowSpillage` remain separately traced
  quantities (required for forensic attribution, ADVERSARIAL_ANALYSIS
  #17) but are DERIVED diagnostics (`L = A - C - O` at each contest),
  never separately subtracted in the identity. `ExecutionCost` is added
  to the "Creation/destruction rules" destruction list, which the
  reviewed draft omitted. See `AETH01_REPAIRED_FREEZE_CANDIDATE.md`
  "Energy semantics" for the full corrected statement and
  `KILL_GATES_01.md` K1 for hand-worked reconciliation on 6 cases.
  Also closes the specific instrumentation naming gap S01 itself named
  ("maintenance needs an identifiable trace amount/reason, not an
  implied event hidden among debits"): `PHYSICS_SPEC_DRAFT.md`'s
  Instrumentation list gains a distinct `energy_decayed` event for `D`,
  separate from `energy_debited` (`X`/`A`); the CPU oracle
  (`oracle_aeth01.py`) implements this distinction.
- **Falsifier/test:** K1 hand ledger (6 cases) plus an executable
  property test asserting the identity holds with zero tolerance on
  every generated case (already required by REQUIREMENTS.md Part 2;
  now checked against the CORRECTED formula).
- **Changes:** semantics (the accounted quantity formula itself),
  instrumentation (drops the redundant `energy_lost`/`energy_overflow_
  spilled` terms from the identity while keeping them as trace rows).
- **New semantics_id?** No new transition-law behavior (the actual
  per-tick byte-level dynamics were never wrong -- only the checked
  identity was); folded into the still-unfrozen `aeth01.v1` draft as a
  documentation/instrumentation correction.

### S02 -- packet not formally complete over its declared parameter domain

- **Claim (a):** `REPLENISH_NUMER`/`MUT_NUMER` declared `uint32` with
  legal endpoint `2^32`, which no `uint32` can hold.
- **Claim (b):** EXPERIMENTS.md regime 7 permits spatially-varying run
  parameters, but the replay tuple and transition law are five GLOBAL
  scalars with no parameter map.
- **Claim (c) (constructive, not a defect):** source-before-credit
  debit ordering and self-transfer paying execution cost are already
  correct and should be preserved explicitly.
- **Disposition:** ACCEPT (a), ACCEPT (b), ACCEPT (c) (record as
  preserved, not changed).
- **Reasoning (a):** `uint32`'s maximum value is `2^32 - 1`; the stated
  domain `[0, 2^32]` is self-contradictory as written. This is a plain
  representability error, not a judgment call.
- **Reasoning (b):** the transition law (`PHYSICS_SPEC_DRAFT.md` "Tick
  semantics") reads exactly five scalar run parameters with no spatial
  index; a runner that let regime 7 vary them by zone would be
  executing a DIFFERENT, unspecified transition law while claiming the
  `aeth01.v1` replay tuple, silently. Per operator instruction 2.A
  ("prefer the smaller repair unless scientific requirements genuinely
  require spatially varying law"), the repair narrows the EXPERIMENT
  DESIGN rather than widening the PHYSICS.
- **Affected docs:** `PHYSICS_SPEC_DRAFT.md` (run-parameter table),
  `EXPERIMENTS.md` (regime 7).
- **Exact repair:** (a) redefine `REPLENISH_NUMER` and `MUT_NUMER` as
  integers with legal domain `0..=2^32` inclusive (33-bit range),
  stored in a machine word wide enough to hold `2^32` exactly (a
  64-bit unsigned field is sufficient and is what any real
  implementation would use regardless of the nominal "uint32" label);
  the trigger condition `(key >> 32) < NUMER` is UNCHANGED arithmetic
  and now correctly represents probability exactly 1 when
  `NUMER == 2^32`, since `key >> 32` ranges over `0..=2^32-1`, strictly
  less than `2^32` always. (b) regime 7 ("heterogeneous environment")
  is narrowed to heterogeneous INITIAL BYTE CONTENT ONLY (different
  initial energy levels, densities, or field values by zone) under the
  SAME five global scalar run parameters for the whole world; a
  genuinely spatially-varying LAW (per-zone `WRITE_COST` etc.) is
  explicitly named as a DIFFERENT, not-yet-specified physics requiring
  its own `semantics_id` and its own replay-tuple extension (a
  parameter MAP, not five scalars) if ever pursued. (c) explicitly
  restated as a preserved, unchanged, correct property in the freeze
  candidate.
- **Falsifier/test:** K1 boundary case for `NUMER=2^32` (guaranteed
  trigger every opportunity); a static check that no campaign
  configuration ever sets per-zone run parameters while claiming
  `aeth01.v1`.
- **Changes:** semantics (parameter representation), experiment_design
  (regime 7 scope narrowed).
- **New semantics_id?** No -- (a) is a representation fix with
  identical trigger arithmetic; (b) removes an experiment-design
  overreach rather than adding law. Still folded into the unfrozen
  `aeth01.v1` draft.

### S03 -- accessibility justification describes a different mutation process

- **Claim:** the "at-most-eight-event path between any two bytes" /
  "approximately one-in-eight activation" / "neutral drift of dormant
  machinery" narrative describes an unconditional per-byte random walk
  that the actual rule does not implement. The real rule mutates only
  the WINNING SOURCE PAYLOAD of a successful WRITE; an all-WRITE-free
  world mutates nothing, ever, at any `MUT_NUMER`.
- **Disposition:** ACCEPT.
- **Reasoning:** exact mechanism mismatch, proven by the fixed
  payload-0-writer counterexample (recipient's opcode can only ever
  become `0` or one of the eight powers of two, never `3`, however many
  such events occur) and by construction (mutation triggers only inside
  the WRITE proposal path, `PHYSICS_SPEC_DRAFT.md` "Mutation (Mu)" is
  invoked only for "a winning proposal"; a world with zero winning
  WRITE proposals invokes `Mu` zero times, regardless of `MUT_NUMER`).
  No counterexample to Astra is possible here; the reviewed prose is
  simply describing a different process than the specified one.
- **Affected docs:** `PHYSICS_SPEC_DRAFT.md` ("Representation &
  accessibility analysis"), `EXPERIMENTS.md` (regime-3/4 rationale
  language implying background drift), `ECONOMICS.md` ("dormant wins"
  bullet, which correctly says a dormant cell's bytes "can drift
  neutrally" -- this specific sentence is ALSO an instance of the same
  error and needs the same correction).
- **Exact repair:** replace the accessibility narrative with an
  explicit statement that AETH-01's mutation is **copy-coupled**: it is
  an error process attached to a SUCCESSFUL incoming WRITE event, not
  an autonomous process on stored/dormant bytes. Its precise reachable
  set from a donor payload `p` (fields 0-3, uniform bit-index sampling)
  is: with probability `1 - MUT_NUMER/2^32`, the stored value is exactly
  `p`; with probability `MUT_NUMER/2^32`, it is `p` with one uniformly
  random bit flipped (8 equally likely outcomes, including possibly
  `p` again is NOT possible since flipping any bit changes the byte --
  8 distinct Hamming-1 neighbors of `p`, each with conditional
  probability 1/8). A byte that is NEVER the target of a winning WRITE
  never changes, at any `MUT_NUMER`, including `MUT_NUMER = 2^32`
  (probability 1). "Dormant machinery survives free" (already correctly
  stated elsewhere) and "dormant machinery MUTATES for free" are now
  explicitly separated as two different, non-implied properties -- only
  the first is true. `KILL_GATES_01.md` K2 gives the exact conditional
  table required (fixed donor payload repeated overwrite; all-inert
  world; all 256 `arg1` selector bytes; every 1-bit `arg1` neighbor).
  Per the operator's explicit prohibition, NO background mutation is
  added to make the old narrative true; the choice is stated as
  intentionally copy-coupled, full stop.
- **Falsifier/test:** K2 (below); a property test asserting zero
  `mutation_applied` events in an all-`RESERVED_INERT` world at
  `MUT_NUMER = 2^32`.
- **Changes:** experiment_design/inference_contract narrative only
  (the transition law's mutation RULE is unchanged; only its
  description was wrong).
- **New semantics_id?** No.

### S04 -- claim ladder can certify a relay as recursive construction

- **Claim:** a preconfigured A->B->C forwarding chain (B and C already
  wired to forward before A ever acts) can satisfy the reviewed
  `RECURSIVE_CONSTRUCTION` tier, because it shows a genuine causal
  chain of VALUE changes, even though neither B's nor C's ABILITY to
  construct was ever built by anything -- it pre-existed in the initial
  condition.
- **Disposition:** ACCEPT.
- **Reasoning:** correct by construction of the counterexample: the
  tier-3 definition (`HEREDITY_REQUIREMENTS.md` original tiers) only
  required "the constructed region itself goes on to satisfy
  CAUSAL_CONSTRUCTION for a further target," which a relay trivially
  does using machinery it always had. The document conflates
  "B's stored VALUE was caused by A" (true, and cheap) with "B's
  CAPACITY to cause things was caused by A" (the actually interesting
  claim, and not tested at all by the reviewed ladder). Additional
  named sub-issues (strict resemblance prerequisite, Mu-origin-only
  heritable variation, resource-flow exclusion, parent-intact/consumed
  as a movement discriminator) are each independently valid restriction
  errors, addressed together below.
- **Affected docs:** `HEREDITY_REQUIREMENTS.md` (claim tiers, adversarial
  case table), `OBSERVATORY.md` ("Lineage-like construction evidence").
- **Exact repair:** see `HEREDITY_REQUIREMENTS.md` (repaired) and
  `KILL_GATES_01.md` K3 for the full separated-axis ladder and the two
  required fixtures (relay negative; constructed-capacity positive).
  Summary of the repair shape: introduce an explicit CONSTRUCTED_
  CAPACITY evidence axis, separate from value transport, defined as
  "the target's OWN enabling state (opcode/arg0/arg1 -- the fields that
  determine WHETHER and WHERE it can act) was itself caused to change
  by the alleged constructor, verified by ablation" (as opposed to only
  its payload/content changing). `RECURSIVE_CONSTRUCTION` now requires
  CONSTRUCTED_CAPACITY at every step, not merely CAUSAL value transport.
  Resemblance, origin-of-variation, and resource-mediated evidence are
  decoupled from each other and from the tier ladder (see M05/S04
  combined repair below); "parent-intact vs. parent-consumed" is
  dropped as a required discriminator (B02, `SONNET_CONCERN_OVERRATED`-
  adjacent: it is a real distinguishing observable in SOME cases but
  not a universal one) in favor of directly testing whether a
  successor's construction CONSUMED the predecessor's ability to act
  (an observable, not an assumed universal law).
- **Falsifier/test:** K3 fixtures must receive DIFFERENT verdicts under
  the repaired ladder (relay: value-transport only, capped below
  RECURSIVE_CONSTRUCTION; constructed-capacity fixture: qualifies for
  CONSTRUCTED_CAPACITY at the A->B step). If they cannot be
  discriminated, `KILL_GATES_01.md` requires reporting
  `INFERENCE_CONTRACT_UNRESOLVED`, not shipping the ladder anyway.
- **Changes:** inference_contract.
- **New semantics_id?** No (physics/state unchanged; only the future
  claim-evaluation contract, which is not implemented in AETH-01 per
  the operator's own instructions).

### S05 -- GPU stopping rule changes the sampled science

- **Claim:** finite low-activity/low-change windows are treated as
  proof a world cannot change again; this is false (a starved writer
  can be replenished later; a same-value winner can later mutate; a
  currently-losing writer can win under a later tick's priority; even
  an all-inert world's ENERGY can still be changing under
  replenishment/decay). Lattice-hash recurrence is also conflated with
  recurrence of the full replay state, ignoring that `tick` itself
  feeds the mutation/replenishment hash chains.
- **Disposition:** ACCEPT.
- **Reasoning:** each named reactivation path is a direct, checkable
  consequence of the transition law as specified; none is hypothetical.
  The PERIODIC-label argument is also correct: `Mu`/`Rho` both hash in
  `tick` (`PHYSICS_SPEC_DRAFT.md`), so `S[t1] == S[t2]` for `t1 != t2`
  does NOT imply `S[t1+1] == S[t2+1]`, because the two continuations
  are keyed by different tick values even from an identical lattice
  state.
- **Affected docs:** `GPU_RUNPOD.md` ("Early termination of absorbing
  regimes"), `HABITABILITY.md` (DEAD/FROZEN/PERIODIC signatures).
- **Exact repair:** split early stopping into two DIFFERENT mechanisms
  with different epistemic status, never conflated: (1) a **certified
  absorbing fast-path**, mathematically provable and safe to hard-stop
  on: a world with (i) zero cells anywhere carrying `opcode=WRITE`,
  (ii) `REPLENISH_NUMER=0`, is provably unable to ever change its
  fields 0-3 again (no WRITE proposal can ever be emitted, so no
  `mutation_applied` event can ever fire either, since mutation only
  triggers on a winning WRITE) and its energy field is monotonically
  non-increasing under `MAINTENANCE_COST` with no inflow, reaching a
  fixed floor within at most `ceil(255 / MAINTENANCE_COST)` ticks (or
  immediately if `MAINTENANCE_COST=0`) -- after that many ticks with
  this precondition, `S[t]` is provably fixed forever and the run may
  be hard-stopped and labeled `DEAD_CERTIFIED`; (2) **budget-limited
  heuristic quiescence** (near-zero `activity_density`/`change_rate`
  for N ticks under any OTHER parameter combination) is a RIGHT-CENSORED
  stop, never a proof, labeled `QUIESCENT_CENSORED_AT_TICK_<t>`, with the
  exact stopping tick and trigger metric recorded so `K5`-style
  continuation audits (deferred to a future kill gate, named but not
  executed in this cycle) can later check for reactivation on a
  resampled subset. PERIODIC requires confirming forward-trajectory
  agreement for several ticks past the matched lag (not a single
  lattice-hash match), stated explicitly in `HABITABILITY.md`.
- **Falsifier/test:** a property test that the certified fast-path's
  two preconditions are jointly sufficient (no `stored_bits_changed` or
  `mutation_applied` event ever fires afterward, checked over a
  randomized horizon); a property test that PERIODIC claims are
  rejected if forward trajectories diverge after the claimed lag.
- **Changes:** experiment_design, instrumentation.
- **New semantics_id?** No (a labeling/campaign-tooling repair; the
  transition law itself is unaffected).

### S06 -- resource overlays can launder seeded controls into spontaneous evidence

- **Claim:** `EXPERIMENTS.md` regimes 5-7 ("resource-rich/poor/
  heterogeneous," which may wrap "any of the above," including the
  seeded regime-3 copier) are simultaneously declared spontaneous-origin
  ("no hand-authored functional pattern"); a seeded copier with altered
  energy satisfies both descriptions at once, a direct contradiction.
- **Disposition:** ACCEPT.
- **Reasoning:** the contradiction is textual and exact (`EXPERIMENTS.md`
  lines 47-55 vs. 66-71 in the reviewed draft); no defense possible.
- **Affected docs:** `EXPERIMENTS.md`.
- **Exact repair:** origin classification (`instrument_class`) is
  redefined to compose through ALL overlays: `instrument_class =
  SEEDED_CONTROL` if ANY hand-authored functional byte pattern (from
  regimes 3-4) is present ANYWHERE in the initial lattice content,
  regardless of which resource/energy/heterogeneity overlay (regimes
  5-7) is additionally applied on top; `instrument_class = SPONTANEOUS`
  only if the ENTIRE initial lattice content derives exclusively from
  unstructured generation (regimes 1-2), under ANY overlay. Regimes 5-7
  are redefined as OVERLAYS (resource/energy/zone parameter choices)
  applicable to either a regime-1/2 base (giving SPONTANEOUS) or a
  regime-3/4 base (giving SEEDED_CONTROL), never a base regime with an
  origin label of its own. The structural-fingerprint cross-check
  (already required) is re-stated explicitly as a DIAGNOSTIC/
  INVESTIGATION TRIGGER only -- it never overrides the logged
  initialization recipe, which is the sole provenance truth.
- **Falsifier/test:** K6 (below): every resource/environment overlay
  crossed with every seeded (3-4) AND every random (1-2) base recipe;
  assert `instrument_class` is `SEEDED_CONTROL` for every seeded-based
  combination, with no exception.
- **Changes:** experiment_design, inference_contract.
- **New semantics_id?** No.

## MAJOR items

### M01 -- modulo five removes an inherited neutral subspace

- **Claim:** `arg1 mod 5` is not a harmless additive extension of
  AETH-00's `arg1 mod 4`; because no power of two is divisible by 5,
  EVERY single-bit flip of `arg1` changes its target-field residue,
  destroying the old "top six bits neutral" property entirely, and the
  256-value encoding is non-uniform across the 5 fields (52/51/51/51/51).
- **Disposition:** ACCEPT_WITH_QUALIFICATION.
- **Reasoning:** the arithmetic claim is exactly correct and not
  disputable. However, per the operator's explicit prohibition on
  "friendlier ... rules" and the review's own "DO NOT REPAIR YET"
  guidance (do not redesign an exact mechanism reactively merely
  because it is unfamiliar/inconvenient), CHANGING the field-selector
  encoding to restore neutrality would itself be an unreviewed physics
  change with its own new hidden priors (e.g. any bit-preserving
  encoding necessarily gives 3-4x more of the 256 byte values to
  whichever fields it favors) -- trading one undisclosed prior for
  another, not a repair. Astra's finding is that the encoding's true
  behavior was MISDESCRIBED as harmless, not that mod-5 is physically
  wrong.
- **Affected docs:** `PHYSICS_SPEC_DRAFT.md` ("Field encoding"),
  `DECISIONS.md` (D-AETH01-02/-08 language).
- **Exact repair:** keep `arg1 mod 5` UNCHANGED in the frozen candidate;
  strike the word "additive"/"harmless extension" wherever it implies
  preserved neutrality; state plainly that mod-5 selection has NO
  single-bit-neutral subspace at all (every 1-bit `arg1` flip changes
  the targeted field) and an encoding skew of 52:51:51:51:51 across the
  5 fields for a uniform byte. The full 256-value x 8-bit-position
  adjacency table is required as part of K2 (exhaustive, not sampled).
- **Falsifier/test:** K2's exhaustive arg1 table (below); a future
  falsifier is recorded: if a scout-tier sweep run under an alternative,
  neutrality-preserving field-selector encoding shows materially
  different habitability-label distributions than the mod-5 encoding at
  matched parameters, the encoding choice (not just its description)
  should be revisited as a new `semantics_id` -- not before.
- **Changes:** experiment_design/documentation narrative only.
- **New semantics_id?** No.

### M02/M03 -- economics charges reserves not persistence; several exact incentives

- **Claim:** the four template bytes persist at zero energy under every
  maintenance setting (maintenance taxes stored ENERGY, not information
  retention), so "persistent state is costly" is false as stated;
  merging positive energy reserves can REDUCE total future maintenance
  (a concentration/hoarding incentive, since maintenance is presumably
  charged per occupied energy-bearing site up to a floor, not per unit);
  several other exact incentives are named (broadcasting is the boring
  baseline; passive/dead matter never pays execution cost; zero-amount
  transfer contestants can win while destroying an opponent's entire
  offered amount; unconditional sender debits penalize convergent
  multi-donor support).
- **Disposition:** ACCEPT.
- **Reasoning:** each incentive is a direct, checkable consequence of
  the already-specified rules (flat per-site `MAINTENANCE_COST` floored
  at 0; unconditional sender debit; winner-take-all credit); none
  requires a new assumption to derive.
- **Affected docs:** `ECONOMICS.md` (all sections describing maintenance
  as buying "persistent information").
- **Exact repair:** correct `ECONOMICS.md`'s prose to state precisely
  what maintenance taxes (occupied energy RESERVES, charged per cell
  regardless of activity, floored at 0 -- never information retention;
  the four template bytes are free and immortal under every parameter
  setting) and name the concentration/hoarding, zero-amount-jamming, and
  sacrificial-loser incentives explicitly as PROPERTIES of Regime B, not
  bugs to fix now (per the operator's prohibition on "friendlier
  transfer/refund rules" and "charge informational storage"). The
  economic narrative no longer claims maintenance makes memory costly;
  it states memory is free and reserves are taxed, as two SEPARATE,
  now-correctly-labeled facts.
- **Falsifier/test:** K4 (deferred; named, not executed this cycle --
  isolated pulse-budget cell, equal-mean rain pair, two-site pooling,
  zero-amount vs. large-amount contest) is recorded as required BEFORE
  any campaign report characterizes Regime B's incentive structure.
- **Changes:** experiment_design/documentation narrative.
- **New semantics_id?** No (the mechanism was already exactly this; only
  its description was wrong).

### M04 -- mean inflow is not a sufficient habitability axis

- **Claim:** combining `REPLENISH_NUMER x REPLENISH_AMOUNT` into one
  "mean inflow" axis hides burstiness; probability 1/2 amount 2 and
  probability 1/16 amount 16 have the same mean but qualitatively
  different behavior at `MAINTENANCE_COST=2, WRITE_COST=3` (only the
  second ever permits emission). Even-power-of-two-only grid sizes also
  privilege the torus's bipartite structure; a 4x4 uniform-soup world
  has ~94% chance of zero writers at init, an absence-of-machinery
  confound distinct from extinction.
- **Disposition:** ACCEPT.
- **Reasoning:** the numeric counterexample is exact; the parity and
  soup-density arguments are direct probability calculations.
- **Affected docs:** `HABITABILITY.md` (campaign design, parameter
  axes).
- **Exact repair:** sweep `REPLENISH_NUMER` (probability) and
  `REPLENISH_AMOUNT` separately, not as one collapsed product axis; add
  at least one odd and one non-power-of-two `H`/`W` pair to the campaign
  scope; require initial-writer-count to be reported and distinguished
  from later extinction in every campaign summary.
- **Falsifier/test:** none executed this cycle (habitability campaign
  itself is out of scope for this repair pass); recorded as a required
  campaign-design fix before HABITABILITY.md's sweep is run.
- **Changes:** experiment_design.
- **New semantics_id?** No.

### M05 -- winner provenance is not the causal graph of construction

- **Claim:** following only winning-value suppliers misses enabling
  conditions, energy thresholds, losing proposals that blocked
  alternatives, and redundant/multi-source contributions; naive
  Hamming-divergence attribution can mistake destroyed routing/energy
  for destroyed information.
- **Disposition:** ACCEPT.
- **Reasoning:** consistent with, and largely a deeper elaboration of,
  the S04 finding; no counterexample needed beyond the general
  observation that the reviewed `OBSERVATORY.md` lineage metric records
  only `proposal_won` edges.
- **Affected docs:** `OBSERVATORY.md` ("Lineage-like construction
  evidence").
- **Exact repair:** the lineage/provenance requirement (not a built
  detector, still deferred per the operator's rules) is expanded to
  require preservation of: all contenders (not just the winner) per
  contest, the winning proposal's pre- and post-mutation payload, energy
  thresholds/starvation status of the source, and content-vs-enabling
  perturbation as two distinct intervention types (see S04/`HEREDITY_
  REQUIREMENTS.md` repair). This is a requirements/instrumentation
  change, not a detector implementation.
- **Falsifier/test:** none executed this cycle; folded into the K3
  fixture design (both K3 fixtures require full-contender trace
  preservation to be distinguishable at all).
- **Changes:** inference_contract, instrumentation.
- **New semantics_id?** No.

### M06 -- scout funnel can select artifacts and hide its own false negatives

- **Claim:** STRUCTURED/MOBILE/CHAOTIC labels require tier-2/3 data that
  scouts do not have, so scout-tier promotion using these labels is
  incoherent; CPU/GPU verification of only PROMOTED worlds cannot catch
  a GPU bug that makes an interesting world look dead; adaptive
  boundary refinement can miss rare/rare-frequency events between
  sampled grid points.
- **Disposition:** ACCEPT.
- **Reasoning:** direct dependency-graph inconsistency (a label whose
  computation requires tier-2 data cannot be assigned at tier 1); the
  false-negative-audit gap and the `0.99^8 ~= 92%` miss-probability
  example are both straightforward.
- **Affected docs:** `HABITABILITY.md`, `GPU_RUNPOD.md`, `OBSERVATORY.md`.
- **Exact repair:** scout tier may only assign PROVISIONAL labels
  computed strictly from tier-1 counters (`activity_density`,
  `change_rate`, `state_entropy`, cheap `spatial_autocorr`,
  `compression_ratio` sampled coarsely, coarse periodicity); STRUCTURED/
  MOBILE/CHAOTIC/METASTABLE become CONFIRMED only after deepen-tier
  tier-2/3 data is actually computed. A mandatory randomized audit
  (fixed, preregistered fraction, e.g. 5%) of scout-tier DEAD/FROZEN/
  UNKNOWN worlds is promoted to the qualify tier regardless of their
  scout label, specifically to measure the false-negative rate;
  denominators, censoring reasons, and the audit sample's own outcome
  distribution are required campaign-report fields (K7, deferred, not
  executed this cycle).
- **Falsifier/test:** K7 (deferred).
- **Changes:** experiment_design, inference_contract.
- **New semantics_id?** No.

### M07 -- RNG marginal correctness is not independence of the environment

- **Claim:** the three hash domains (arbitration/mutation/replenishment)
  share a single seed/tick/coordinate input space; an exact tick choice
  exists that makes the mutation and replenishment chains' internal
  words coincide, so "never share input material in a way that
  correlates outcomes" is an overclaim, even though the POSITIVE result
  (fixed-opportunity marginal uniformity, exact trigger/index
  independence) is real and correctly derivable.
- **Disposition:** ACCEPT_WITH_QUALIFICATION.
- **Reasoning:** the exact structural relation is a correct derivation
  (a specific `t_r` exists); the practical exploitability at any
  in-campaign tick is unmeasured, and Astra says so explicitly (M07 body,
  B03 reviewer qualification) -- this is a scope/wording defect, not a
  reason to redesign the hash (explicitly listed under the operator's
  "DO NOT REPAIR YET"-equivalent guidance and Astra's own "do not
  redesign the hash" instruction).
- **Affected docs:** `PHYSICS_SPEC_DRAFT.md` (Replenishment section's
  independence claim).
- **Exact repair:** soften "never share input material in a way that
  would correlate their outcomes" to state the two things actually
  established: (1) for a FIXED opportunity, the Mu key is uniform and
  its trigger/index bits are exactly independent (a real, provable
  property); (2) cross-domain / cross-tick / realized-trajectory
  independence is NOT proven and is named as an open statistical
  question requiring an AETH-01-scale rerun of AETH-00A's stratified
  diagnostic before being relied upon (already partially required by
  `GPU_RUNPOD.md`'s "must be VERIFIED" language for cross-seed
  independence; now extended explicitly to cross-domain).
- **Falsifier/test:** an AETH-01-scale statistical diagnostic rerun
  (named, not executed this cycle -- out of scope for a repair-only
  pass).
- **Changes:** documentation narrative only.
- **New semantics_id?** No.

### M08 -- heredity/novelty observatory has an ontology of its own

- **Claim:** component tracking/centroid grouping can manufacture
  individuality from an observer's scale/window choice; naive centroids
  jump at torus wrap boundaries; removing opcode terminology in the
  novelty assay can conceal an ordinary relay rather than reveal an
  alien mechanism.
- **Disposition:** ACCEPT.
- **Reasoning:** each point follows directly from how component tracking
  and the (deferred, not-yet-built) novelty assay are described;
  torus-wrap centroid discontinuity is a plain geometric fact.
- **Affected docs:** `OBSERVATORY.md` (component tracking), `HEREDITY_
  REQUIREMENTS.md` (novelty assay requirements).
- **Exact repair:** add an explicit requirement that any future component
  tracker use torus-aware (wrap-corrected) displacement, not naive
  Euclidean centroids; state plainly that component identity is a
  BOOKKEEPING CONVENIENCE, never evidence of individuality by itself
  (already partly stated; strengthened); add a calibration requirement
  to the novelty assay (already deferred, not built) that known,
  disguised, FAMILIAR mechanisms must be run through the identical
  pipeline BEFORE any AETH-01 specimen's low-recognition score is
  interpretable -- this requirement already existed in the reviewed
  draft and is retained/emphasized, not newly invented.
- **Falsifier/test:** deferred (novelty assay is not built in AETH-01).
- **Changes:** inference_contract.
- **New semantics_id?** No.

### M09 -- engineering inheritance promoted into physics selection evidence

- **Claim (part A, GPU):** `PHYSICS_CANDIDATES.md` calls GPU viability
  (R12) "not aspirational, it is proven," when the only implementation
  that exists (`Aether/production/aeth00.py`) is CPU-only, gather-shaped.
  Gather locality is a strong FEASIBILITY argument, not measured GPU
  qualification.
- **Claim (part B, trace/instrumentation):** the old AETH-00 trace
  on/off tests establish NONINTERFERENCE (enabling the trace does not
  change committed bytes), not the trace's TRUTH or causal completeness.
  Production computes `proposal_emitted` through a decoding path
  separate from the one that decides the winner. An independent event
  ledger comparison is needed before an AETH-01 instrument is used as
  evidence. The 100,000-case differential test mostly compares one-step
  small-world transitions; it is not a bound on all campaign failures or
  an economic-scientific qualification.
- **Disposition:** ACCEPT (both parts).
- **Reasoning:** part A -- the receipt this claim is supposed to be
  grounded in (`AETH-00B_RECEIPT.md`) itself states the implementation
  is CPU-only; the word "proven" is simply inconsistent with the cited
  evidence. Part B -- noninterference (same bytes with trace on/off) and
  truth (trace rows accurately/completely describe what happened) are
  logically independent properties; AETH-00B's test suite only exercises
  the former, and a decoding-path bug in trace emission would pass every
  existing test while still misreporting events. Property-based/
  differential test COUNT is also not itself a claim about scope; a
  large count of single-tick small-world cases says nothing about
  multi-tick campaign-level failure modes or the sufficiency of trace
  data for a scientific (heredity/construction/novelty) claim.
- **Affected docs:** `PHYSICS_CANDIDATES.md` ("Selection" reason 2),
  `REQUIREMENTS.md` (R12 status note; R10 status note; Part 2 new
  independent event-ledger cross-check requirement; property-test scope
  note), `OBSERVATORY.md` (opening R10 separation statement).
- **Exact repair (part A):** reword "GPU viability (R12) is not
  aspirational, it is proven" to "GPU viability (R12) rests on a strong,
  unmeasured feasibility argument: Candidate 1's per-cell gather shape
  maps onto AETH-00's proven gather ontology unchanged, which makes GPU
  implementation plausible and low-risk, but no GPU implementation of
  ANY AETH candidate has been built or measured; R12 remains OPEN until
  this cycle's RunPod canary (`REVIEW_PACKET_REPAIR_01.md`) actually
  runs." R12's `REQUIREMENTS.md` status changes from `SATISFIED` to
  `SATISFIED (feasibility argument only; not yet measured)`.
- **Exact repair (part B):** R10's `REQUIREMENTS.md` status changes to
  "SATISFIED for noninterference; TRUTH/COMPLETENESS NOT YET
  ESTABLISHED," naming the `proposal_emitted` decoding-path risk
  explicitly; `REQUIREMENTS.md` Part 2 gains a new REQUIRED item, an
  independent event-ledger cross-check (a second, independently-coded
  pass reading only raw before/after state, never the production
  trace-emission code path, compared field-by-field against the
  production trace) that must pass before any AETH-01 trace is treated
  as scientific evidence; the property-based-testing bullet gains an
  explicit scope note (one-step transition-law correctness only, not a
  campaign-level or economic-scientific bound); `OBSERVATORY.md`'s
  opening statement is repaired to state the noninterference/truth
  distinction and cross-reference the event-ledger requirement and K7.
- **Falsifier/test:** part A -- the RunPod canary itself (this cycle's
  deliverable, not yet launched). Part B -- K7 (tiny audit of
  oracle/trace agreement, including intentionally suppressed events;
  deferred, see KILL_GATES_01.md).
- **Changes:** documentation narrative; `REQUIREMENTS.md` status
  wording and new instrumentation requirement; `OBSERVATORY.md` framing.
- **New semantics_id?** No.

## MINOR items

### N01 -- performance and scope arithmetic

- **Claim:** the ~300K cell-steps/s baseline implies ~10.24s for a
  3,000-tick 32x32 replay, not "a fraction of a second" as claimed; the
  full sweep is 25,000-134,456 worlds before refinement.
- **Disposition:** ACCEPT.
- **Reasoning:** `32*32*3000 / 300000 ~= 10.24s`; plain arithmetic error
  in the reviewed draft.
- **Affected docs:** `GPU_RUNPOD.md`.
- **Exact repair:** correct the arithmetic example; state plainly that
  all such figures are ESTIMATES from a CPU-only, pre-AETH-01 baseline
  and must be re-profiled once an AETH-01 CPU oracle exists (this
  cycle's `production_aeth01.py`, see below) before any budget
  commitment is made.
- **Changes:** documentation narrative.
- **New semantics_id?** No.

### N02 -- impossible/unmeasured examples

- **Claim:** "every proposal loses" is impossible for a nonempty
  contest (every nonempty contest has a winner); four neighbors CAN
  update all four non-energy fields of a center in one tick (multi-
  source single-tick construction is possible; sequential partial
  construction is not structurally forced); the differential test's
  "dense four-way contention" fixture actually supplies at most two
  incoming competitors.
- **Disposition:** ACCEPT.
- **Reasoning:** each is a direct reading of the arbitration and test
  code; no counterexample needed to accept a correction.
- **Affected docs:** `HABITABILITY.md`, `PHYSICS_SPEC_DRAFT.md`
  ("Multi-component cooperative construction" claim), test file
  docstring.
- **Exact repair:** remove the impossible "every proposal loses" example
  from `HABITABILITY.md`; correct `PHYSICS_SPEC_DRAFT.md`'s "necessarily
  accumulates over multiple ticks" language to "typically accumulates
  over multiple ticks; a single tick CAN update all four non-energy
  fields of one target simultaneously via 4 distinct source neighbors,
  so multi-tick accumulation is common, not structurally forced";
  rename the test fixture's docstring to remove "dense" and note the
  true two-incoming-competitor count, pointing to the existing full
  four-way fixture as the actual four-way-arbitration coverage.
- **Changes:** documentation/test-docstring narrative.
- **New semantics_id?** No.

### N03 -- operational metric definitions are drafts

- **Claim:** measurement windows, field selections, Gini conventions,
  normalization, and label thresholds are unfrozen; `change_rate`'s
  exact scope (energy settlement/replenishment vs. only winning
  template changes) is unstated; global aggregate metrics cannot alone
  establish resemblance; a diffusion null is not automatically
  appropriate.
- **Disposition:** ACCEPT.
- **Reasoning:** these are acknowledged gaps, not disputed claims.
- **Affected docs:** `HABITABILITY.md`, `OBSERVATORY.md`.
- **Exact repair:** none executed this cycle (habitability campaign
  itself is out of scope for a repair-only pass); recorded as a
  MANDATORY pre-campaign freeze item -- these definitions must be fixed
  BEFORE any campaign run, not adjusted after seeing results, and
  `change_rate` is explicitly defined (as part of this repair cycle) to
  count `stored_bits_changed=true` events on fields 0-3 ONLY (winning
  template changes), separately from energy-settlement events, which
  get their own `energy_change_rate` metric -- resolving the specific
  named ambiguity now even though the full campaign-metric freeze is
  deferred.
- **Changes:** instrumentation (the one resolved sub-item), experiment_
  design (the rest, deferred).
- **New semantics_id?** No.

### N04 -- the three candidates are not equally specified

- **Claim:** Candidates 2 and 3 are informative families, not complete
  rival universes (open reaction catalogs, rates, collision laws); this
  asymmetry must not be read as scientific inferiority, and Candidate
  1's typo-level issues should not be conflated with the larger
  selection-uncertainty question.
- **Disposition:** ACCEPT.
- **Reasoning:** factually correct description of the current state of
  `PHYSICS_CANDIDATES.md`.
- **Affected docs:** `PHYSICS_CANDIDATES.md`.
- **Exact repair:** add an explicit note to `PHYSICS_CANDIDATES.md`'s
  "Selection" section stating this asymmetry and that Candidates 2/3
  remain live, not inferior, alternatives, unaffected by this repair
  cycle's Candidate-1-specific fixes.
- **Changes:** documentation narrative.
- **New semantics_id?** No.


## Pass B additional findings (B01-B03)

### B01 -- several proposed discriminating controls do not discriminate as stated

- **Disposition:** ACCEPT.
- **Reasoning:** each sub-item (self-analysis #1 timing/redundancy gap,
  #2 short-window causal-null fallacy, #3/#6 forcing-dependence vs.
  artifact conflation, #8/#10 sustained-change/boundary-detector not
  being neutral admission criteria, #19's scope conflict with keeping
  component metrics off scouts) is a direct reading of the ORIGINAL
  `ADVERSARIAL_ANALYSIS.md` controls against the actual mechanism, and
  each holds up on inspection.
- **Affected docs:** `ADVERSARIAL_ANALYSIS.md` (controls #1, #2, #3, #6,
  #8, #10, #19).
- **Exact repair:** annotate the affected `ADVERSARIAL_ANALYSIS.md`
  entries with a one-line qualification pointing at the sharper
  standard (M05/S04's intervention/redundancy requirements; M06's
  scout/tier-2-metric scope fix for #19); no control is deleted, each is
  narrowed to what it actually establishes.
- **Changes:** inference_contract documentation.
- **New semantics_id?** No.

### B02 -- some small-physics concerns are overstated

- **Disposition:** ACCEPT (as a correction to the ORIGINAL self-review,
  not to Astra).
- **Reasoning:** Astra's own corrections are exactly right: dimension-2
  self-aliasing (not just dimension-1) requires the caveat; a
  self-transfer cannot manufacture net energy even in a degenerate
  torus (debit/credit cancel except execution cost, which is a pure
  loss); a saturated (255) cell genuinely IS storing 255 units
  (saturation is a confound for ADAPTIVE-storage claims, not evidence of
  non-storage); excluding energy from Mu is not itself proof that
  resource-handling traits are uninheritable (routing/capacity-use
  patterns, encoded in fields 0-3, can still vary).
- **Affected docs:** `ADVERSARIAL_ANALYSIS.md` #13, #17; `REQUIREMENTS.md`
  R3 note.
- **Exact repair:** correct #13's dimension claim (`<=2` not `<=1`) and
  add the self-transfer non-metabolism derivation; correct #17 to say
  saturation is a storage-vs-adaptive-storage confound, not a
  non-storage claim; add one sentence to R3's tension note in
  `REQUIREMENTS.md` clarifying that the MORE restrictive fact is the
  future OBSERVER's planned categorical exclusion of resource-only
  construction evidence (S04 repair), not the mutation exclusion itself.
- **Changes:** documentation narrative.
- **New semantics_id?** No.

### B03 -- decision falsifiers need observable endpoints, not interestingness

- **Disposition:** ACCEPT.
- **Reasoning:** phrases like "reasonably thorough" or "never favored
  anywhere" in `DECISIONS.md` D-AETH01-01/-02/-03/-05/-06/-10 do not
  specify a finite adjudication procedure, as charged.
- **Affected docs:** `DECISIONS.md`.
- **Exact repair:** each flagged falsifier is tightened to name a
  BOUNDED probe (a specific kill-gate ID, a specific parameter range, or
  an explicit sample size) rather than an open-ended qualitative
  judgment; see `DECISIONS.md` (repaired) for the exact rewordings, and
  the new decision entries below (`D-AETH01-15..19`) recording this
  repair cycle's own choices with the same discipline.
- **Changes:** documentation narrative (decision ledger).
- **New semantics_id?** No.

## Kill-gate methodology dispositions (K1-K8)

Execution and exact outcomes are in `KILL_GATES_01.md`. This section
records only whether each proposed kill EXPERIMENT DESIGN itself is
accepted as an adequate falsifier, per operator instruction 3.

- **K1 (accounting)** -- ACCEPT the experiment design; EXECUTED this
  cycle (mandatory per operator instruction). See `KILL_GATES_01.md`.
- **K2 (mutation/accessibility)** -- ACCEPT; EXECUTED this cycle
  (mandatory).
- **K3 (relay vs. constructed capacity)** -- ACCEPT; EXECUTED this cycle
  (mandatory).
- **K4 (economics: pulse-budget, pooling, zero-amount contest)** --
  ACCEPT the design as a valid future falsifier; NOT executed this cycle
  (not in the operator's mandatory K1/K2/K3/K6 list for this pass;
  M02/M03's repair is documentation-only and does not require it to
  proceed). Recorded as required before any Regime-B economic claim.
- **K5 (continuation audit of DEAD/FROZEN stops)** -- ACCEPT the design;
  NOT executed this cycle (requires a running campaign, out of scope for
  a repair-only pass; the S05 repair's certified-vs-heuristic split
  already prevents the specific overclaim K5 targets from being made
  before K5 is run).
- **K6 (provenance composition)** -- ACCEPT; EXECUTED this cycle
  (mandatory).
- **K7 (instrumentation/funnel audit)** -- ACCEPT the design; NOT
  executed this cycle (requires a running scout campaign; M06's repair
  already mandates it before any scout-tier promotion is trusted).
- **K8 (bounded path/assembly witness)** -- ACCEPT the design; NOT
  executed this cycle (a full accessibility-path census is a
  post-freeze, post-implementation activity, explicitly out of scope
  for a design-repair pass; K2's exhaustive mutation table is the
  necessary prerequisite this cycle DOES complete).
