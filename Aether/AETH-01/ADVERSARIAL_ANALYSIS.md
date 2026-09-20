# AETH-01 -- adversarial self-attack (Design Task 10)

Status: DRAFT. 22 specific ways AETH-01 could fool us, each with a
failure mode, a misleading observation, a boring explanation, and an
experiment/control that exposes it. This is a required, not optional,
part of the design (AETHER_DOCTRINE.md item 4).

**1. Reproduction actually caused by environment.** Observation: a
pattern appears to "make a copy of itself." Boring explanation: an
unrelated neighboring active cell happens to template both the
"parent" and the "child" from a third source. Control: lineage-graph
intervention (HEREDITY_REQUIREMENTS.md) -- perturb the alleged parent
only; if the child is unaffected, environment did it.

**2. Heredity caused by spatial persistence, not causation.** Observation:
two similar regions coexist for a long time. Boring explanation: both
are simply RESERVED_INERT and nobody ever addressed them (persistence
by neglect, PHYSICS_SPEC_DRAFT.md accessibility analysis). Control:
check `proposal_won` trace rows targeting each region; zero rows over
the window falsifies any causal claim.

**3. Synchronization artifact from the global tick.** Observation:
distant regions change "in step." Boring explanation: the tick itself
is a shared clock; anything gated only by starvation thresholds or
replenishment timing can look synchronized without any spatial
interaction. Control: compare against an equivalent world with
per-cell-independent replenishment phase offsets; true coupling should
survive phase-randomization, clock artifacts should not.

**4. Topology-induced recurrence.** Observation: a pattern "returns to
itself" periodically. Boring explanation: toroidal wraparound at small
H/W literally re-presents the same neighbor relationships on a fixed
cycle. Control: rerun at H,W large enough that wrap-induced
self-neighboring is impossible in the observed window; periodicity
that survives is not a topology artifact.

**5. Detector recovers the seeded instrument.** Observation: a
"spontaneous" run's detector fires and its structure resembles the
regime-3 positive control. Boring explanation: campaign-script
contamination leaked the seeded pattern into a nominally spontaneous
initial state. Control: the mandatory structural-fingerprint
cross-check against the seeded-pattern library (EXPERIMENTS.md) before
any spontaneous claim is filed.

**6. Deterministic arbitration as a hidden global field.** Observation:
certain coordinates seem to "win" contests more often, read as
territorial dominance. Boring explanation: the SplitMix64 priority
function is a fixed, deterministic function of absolute coordinates --
AETHER_SPEC.md's own caveat that it is order-independent but NOT proven
statistically neutral. Control: rerun the identical scenario at a
translated/rotated coordinate offset; a "dominant" pattern that follows
the translation is behavioral, one that stays at the same absolute
coordinates is a hash artifact.

**7. Resource accounting secretly acting as fitness.** Observation:
cells with more energy simply act more and "win" more, read as
selection for a trait. Boring explanation: energy is initial-condition
luck, not a measured behavioral trait, and nothing computes a fitness
score (R9) -- but the *effect* can still look identical to a fitness
gradient. Control: hold initial energy fixed and identical across a
comparison set, vary only the trait of interest, before attributing
outcome differences to that trait.

**8. Compression rewards frozen structures.** Observation: a FROZEN
region scores as highly "structured" by compressibility. Boring
explanation: a static, unchanging block compresses trivially well
regardless of any interesting dynamics. Control: always pair
compressibility with `change_rate` (OBSERVATORY.md); require nonzero
sustained change before crediting a high compression score to anything
other than freezing.

**9. GPU implementation changes semantics.** Observation: a GPU run's
trajectory diverges from the CPU oracle after some tick. Boring
explanation: floating-point, warp-scheduling, or atomic-ordering
differences silently altered arbitration or energy accounting. Control:
bit-exact CPU/GPU differential testing on the full replay-identity
tuple (REQUIREMENTS.md) before any GPU-produced trajectory is used for
a scientific claim.

**10. Boundary detector invents organisms.** Observation: an arbitrary
spatial partition is drawn and reported as "two populations." Boring
explanation: any partition of a lattice produces *some* flux/boundary
statistic; a boundary existing does not mean the physics itself
produced or "knows about" that partition (R1). Control: require a
boundary to be independently rediscovered by an unsupervised
detector (e.g. from `spatial_autocorr` discontinuities) rather than
hand-drawn, before treating it as a finding.

**11. Mutation's bit-index and trigger bits are correlated.**
Observation: mutation appears biased toward certain bit positions,
read as a "directional" evolutionary pressure. Boring explanation: `Mu`
reuses one 64-bit hash for both the trigger decision (top 32 bits) and
the bit index (bottom 3 bits) -- if `M`'s output has any residual
correlation between these bit ranges, the mutation spectrum is
non-uniform for a purely mechanical reason. Control: an explicit
statistical test (chi-square over `bit_index` conditional on
`triggered=true`, across many independent (seed,tick,target) draws)
before any claim of biological "directionality" in mutation.

**12. Energy as a pure initial-condition-luck artifact (R5 tension).**
Observation: one region "persists" much longer than another, read as
endogenous robustness. Boring explanation: it simply started with more
energy; nothing about its structure or behavior caused the difference.
Control: matched-initial-energy comparison (as in #7); persistence
claims require the SAME starting energy across compared instances.

**13. Toroidal self-aliasing lets a cell "feed itself."** Observation:
at H<=2 or W<=2, a cell's own opposite neighbors coincide, so an
energy-transfer proposal can resolve to the source itself, appearing as
self-sustaining closed-loop metabolism. Boring explanation: it is a
topological degeneracy of small dimensions (AETHER_SPEC.md's mandatory
adversarial fixture case), not an evolved strategy. Control: exclude
H,W in {1,2} from any metabolic-self-sufficiency claim; require the
same pattern to reproduce at H,W>=3 where self-aliasing cannot occur.

**14. Zero-effect "activity" inflates activity metrics.** Observation:
`activity_density` looks high. Boring explanation: many of those
proposals are same-value writes or zero-amount transfers --
`proposal_won=true` with `stored_bits_changed=false` -- physically
inert despite being counted as "activity." Control: always report
`change_rate` alongside `activity_density`; never characterize a regime
from the latter alone.

**15. Correlated starvation from shared low-probability replenishment.**
Observation: a whole region "goes dormant together," read as a
coordinated signal or synchronized life-cycle. Boring explanation: at
low `REPLENISH_NUMER`, independent per-cell Bernoulli draws still
produce long simultaneous dry spells across a small region purely by
chance (a shared statistical tail event, not shared causation).
Control: compare the observed simultaneous-dormancy rate against the
analytically expected rate for independent draws at the same
`REPLENISH_NUMER`; only an excess over that baseline is evidence of
real coupling.

**16. Arbitration hotspots read as territorial dominance.** Observation:
some (target,field) contests are won by a fixed set of source
coordinates far more often than chance. Boring explanation: the
priority hash, while proven tie-free, is not proven statistically
neutral (AETHER_SPEC.md's own explicit caveat) -- apparent dominance may
be a hash artifact of specific coordinate values, not a competitive
outcome. Control: AETH-00A-style statistical-diagnostic sweep
(stratified, pre-registered) rerun for AETH-01's actual contest
population before crediting any "dominance" to behavior.

**17. Energy saturation at 255 mimics evolved resilience.** Observation:
a cell that received lots of inflow never seems to run out, read as a
"storage adaptation." Boring explanation: it is simply capped at the
uint8 ceiling and any further inflow is destroyed as overflow spillage
-- the appearance of inexhaustibility is a numeric artifact. Control:
check `energy_overflow_spilled` trace rows; a cell frequently at the
cap with nonzero spillage is not "storing" anything, it is just full.

**18. Drift misread as adaptation.** Observation: opcode/payload
composition trends in some direction over a run. Boring explanation:
`Mu` triggers uniformly regardless of context; in a small world, pure
sampling drift under a neutral or near-neutral process produces
apparent trends with no selective cause. Control: compare the observed
trend's magnitude against a null model (the same mutation process with
no differential survival, e.g. run on an all-RESERVED_INERT world)
before calling any trend "adaptive."

**19. Inert-majority camouflage hides real activity (a false-negative
risk, not just false-positive).** Observation: lattice-wide entropy/
compressibility look unremarkable. Boring-but-wrong inference: "nothing
interesting is happening." Actual risk: 255 of 256 opcode values are
RESERVED_INERT, so a small, genuinely interesting active region can be
statistically invisible in a lattice-wide aggregate. Control: always
compute metrics on the connected-component/active-region scale
(OBSERVATORY.md component tracking) IN ADDITION TO lattice-wide
aggregates, never only the latter.

**20. Checkpoint/replay drift from incomplete replay-identity capture.**
Observation: a "phenomenon" appears only after resuming from a
checkpoint. Boring explanation: the checkpoint format omitted one of
the five new run parameters or a domain-separation constant, so the
resumed run is silently running under different physics from the
original. Control: a checkpoint round-trip test comparing a
non-interrupted run against a checkpoint-interrupted-and-resumed run
over the identical span, byte-for-byte (REQUIREMENTS.md).

**21. Trace instrumentation leaks non-determinism.** Observation: a
run's outcome differs depending on whether tracing is enabled. Boring
explanation: an implementation detail (e.g. iteration order over an
unordered collection) happens to depend on whether trace bookkeeping
touches that collection first. Control: AETH-00B-style trace-on/off
byte-identity property test (already proven for AETH-00; must be
re-proven for AETH-01's larger state and event set before any AETH-01
result is trusted).

**22. Majority-vote habitability labels hide bimodality.** Observation:
a parameter point is reported as "60% STRUCTURED." Boring explanation:
outcomes may be genuinely bimodal (roughly half DEAD, half STRUCTURED)
rather than a single noisy-but-coherent regime -- majority voting
erases this distinction. Control: HABITABILITY.md's campaign must
report the full label distribution per grid point, and flag
high-disagreement points explicitly, never collapse to a single
majority label without also reporting disagreement rate.
