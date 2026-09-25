Adapt as you see fit.  One of the key goals of these early rounds isn’t to just research the general and detailed hypothesis but use the tech we have to leave residue and failure gradients that might emit even weak signals for subsequent rounds thus the emphasis on instrumentation, data gathering snd documentation for post mortem analysis.  Move away from pass/fail but fail with a deeper understanding of why and what it might suggest for further exploration, even if it means slowing experiments down for disk io for telemetry/logging:

NESTOR ROUND 8 — BOUNDARY, REPLICATION, AND INSTRUMENT DISCIPLINE

Mission

Round 8 is not a hunt for a headline.

It is a controlled attempt to answer four questions that Round 7 made unavoidable:

1. Is w13 an isolated survivor, or does it lie inside a region of world-space where observation-dependent cognition is genuinely useful?
2. Can B-R5-1 replicate on a second scientifically eligible world under an independent instrumentation failure mode?
3. Is Clause B measuring structural transfer, or is the beneficial effect coming from the sham / initialization / regularization machinery instead?
4. Can the swarm continue moving scientific authority out of conductor prose and into code without turning the round into an infrastructure-only exercise?

The governing principle is:

Failure is geometry, not a tombstone.

A failed experiment should leave behind one or more of:

* a narrower boundary;
* a better instrument;
* a repaired eligibility rule;
* a new mechanism candidate;
* a new world-generation requirement;
* a cheaper discriminator;
* a better next experiment.

A negative result that changes none of these is low-value.

⸻

0. ROUND STAGE AND TIME CAP

Round 8 stage:

PRODUCTION

Hard end-to-end cap:

9 hours

Suggested structure:

* BUILD / hygiene: <= 60 minutes
* gate: <= 20 minutes
* active clock: <= 7 hours
* final drain / replay / packet: <= 40 minutes

The active science clock is code-owned.

No conductor extension.

No “five more minutes.”

No experiment may be enlarged because partial results look interesting.

If an experiment deserves more compute than Round 8 permits, file it as:

PRODUCTION_CANDIDATE

with measured cost.

Finding that a larger experiment is warranted is a valid result.

It is not authorization to run it.

⸻

1. PRINCIPLES THAT OVERRIDE ALL LOCAL CONVENIENCE

P1 — NO SCIENTIFIC KILL BEFORE ELIGIBILITY

Lifecycle:

BUILD -> CONTROL -> ELIGIBILITY -> EXPERIMENT -> DISCRIMINATOR -> VERDICT

Anything failing before ELIGIBILITY is:

* INSTRUMENT_FAILURE
* IMPLEMENTATION_DEFECT
* RUN_INELIGIBLE
* REPAIR_REQUIRED
* INDETERMINATE

It is not a hypothesis kill.

P2 — REPAIR DOES NOT RESET THE BET

If a defect invalidates an experiment:

* make the smallest warranted repair;
* keep frozen seeds, worlds, budgets, objectives and discriminator where possible;
* rerun the same experiment.

Do not use a bug as permission to redesign the experiment around the desired outcome.

P3 — LLMs DO NOT DEFINE SCIENTIFIC SUCCESS

LLMs may:

* propose;
* mutate;
* debug;
* interpret;
* attack assumptions;
* nominate anomalies.

LLMs may not:

* alter thresholds after seeing results;
* redefine success;
* promote their own claim;
* turn familiarity or elegance into evidence;
* convert implementation failure into scientific failure.

P4 — OBSERVATION / ELIGIBILITY / VERDICT / INTERPRETATION ARE SEPARATE

Every scientific receipt and final report must preserve these four layers.

No prose may collapse them.

P5 — ADMISSION MEANS “MAY RUN,” NOT “SHOULD RUN”

A job can fit the clock and still be a poor use of resources.

Resource efficiency and scientific value both matter.

P6 — A DRAWN EXPERIMENT MAY CORRECTLY BE NOT RUN

Use:

WHY_NOT_RUN

for work that is scientifically admissible but cannot responsibly be completed under remaining clock/resources.

Do not manufacture rushed evidence to satisfy activity quotas.

P7 — NEVER MAKE THE MUTATION ENGINE THE BOUNDARY OF THE POSSIBLE

At least one exploration channel must remain blind to the semantic meaning of what it creates.

Preserve weird executable objects before translating them into human concepts.

P8 — KEEP SCIENTIFIC AND OPERATIONAL BUDGETS DISTINCT

Scientific cohort share is not equivalent to permanent CPU ownership.

Idle compute may move.

Evidence ownership does not.

⸻

2. BUILD PHASE — HARD GATES BEFORE NEW SCIENCE

The following must land before affected work begins.

2.1 Anti-prior cell-binding pre-check

Land PC:

1789523009420-0

A candidate cell may enter the anti-prior pool only if code verifies, before publication:

1. the intended pressure can bind on that world;
2. the discriminator has resolving power;
3. the oracle can fire;
4. the control can differ from the experimental arm in principle.

Rejected cells are replaced by the next seeded candidate.

No LLM chooses replacements.

The candidate list remains reproducible and code-selected.

This is a HARD GATE for all new anti-prior draws.

2.2 Scheduling cluster

Treat D15 + D22 + D30 as one family.

Required behavior:

* continuations retain priority across epoch requeue;
* longest-waiting eligible jobs cannot be indefinitely starved by bursts of short jobs;
* drain constraints remain enforced;
* queue position must not silently convert scientific priority.

Instrument:

queue_enter_ts
grant_ts
wait_s
queue_position
continuation=true/false

This is a HARD GATE for shared CPU scheduling.

2.3 Row/evidence vocabulary

Fix D29.

A row rejected by the evidence vocabulary must fail loudly.

A job may not return ok while its rows are being refused.

Add vocabulary lint to the launch gate.

This is a HARD GATE.

2.4 Close/watch protocol

Fix D31.

A lane’s ask/watch channel stays alive until DRAIN and stops after workers.

Shared infrastructure may not be shut down without a current conductor confirmation record.

A protocol lint must fail if a close sequence stops communication before workers/shared services.

This is a HARD GATE.

2.5 Conditional fixes

D23 must land before cross-lane GPU experiments.

D25 must land before any scientific verdict depending on the Monte Carlo signflip_p branch.

D28 must land before long-lived registered services run beyond registration TTL.

D26/D27 are desirable automation fixes but must not consume the whole build window if unrelated science is ready.

⸻

3. TELEMETRY TO LAND BEFORE THE CLOCK

At minimum:

* token wait time per job;
* queue depth per lane per epoch;
* watcher liveness with explicit start/stop;
* WHY_NOT_RUN record type;
* machine-readable FINAL.json per lane;
* predicate event id in every row.

If cheap enough, also add:

* RSS / CPU / actual thread count every 30 seconds;
* host CPU/GPU/RAM sample every 60 seconds;
* per-generation timing for evolution jobs.

Telemetry exists to answer future questions.

Do not add instrumentation merely because it is easy to log.

⸻

4. FIRST SCIENTIFIC OBLIGATION — RESOLVE THE FOUR PENDING R16 CELLS

Do NOT state that the 74-cell grid is exhausted until one of the following is true for each of:

* w1 train128
* w7 train128
* w10 train128
* w34 train128

Either:

Route A — Complete adjudication

Run the missing learner under the frozen R16 rule and assign the final status.

or:

Route B — Prove survival impossible

If already-completed measurements mathematically imply that no possible learner result can make the cell SURVIVED, implement a code-derived bound and emit:

SURVIVAL_IMPOSSIBLE

with the exact inequality / bound used.

Do not use prose intuition.

Do not drop the cells merely because they are expensive.

Until all four are resolved by A or B, the correct statement is:

74/74 sampled; 70/74 fully adjudicated; 4 PENDING

not:

grid exhausted

If any becomes SURVIVED, immediately publish the replication trigger.

Do not reorder based on whether a cell looks promising.

⸻

5. NEW WORLD SET — REPLICATION BY LOCAL TOPOLOGY, NOT LOTTERY ALONE

If, after Section 4, w13 remains the only SURVIVED world in the original grid, build a new frozen world set.

The set has two preregistered strata.

STRATUM L — LOCAL W13 NEIGHBOURS

Mechanically perturb w13’s generator parameters.

Create several frozen distance bands from w13.

Example conceptual structure:

L1 = minimal perturbations
L2 = moderate perturbations
L3 = larger but still recognizably local perturbations

The exact coordinates and distances must be defined before outcomes exist.

The purpose is to answer:

Is w13 a point anomaly or part of a contiguous / structured region?

No hand-selection after generation.

No deleting ugly worlds.

STRATUM B — BACKGROUND FRESH SEEDS

Generate a smaller matched set of fresh worlds from the original generator using untouched seeds.

Purpose:

Estimate whether survivorship is enriched around w13 relative to background rarity.

Freeze all seeds and world identities before screening.

No outcome-dependent expansion this round.

DO NOT BUILD HAND-DESIGNED WORLDS YET

Hand-designed worlds encode a hypothesis.

They may become valuable later.

Round 8 first asks whether the existing generator contains local structure around w13.

⸻

6. WORLD ADMISSION / SCREENING

Use the existing R16 scientific semantics.

Do not weaken HOLD/SURVIVED/CULLED because replication is inconvenient.

Use explicit sampling fields:

runs_total
rng_family_count
runs_per_family

Never use ambiguous notation such as 32 x 4.

Final SURVIVED classification uses the frozen production rule.

If pilot staging is needed to save compute, use conservative early elimination only if preregistered.

A final survivor must still satisfy the full rule.

⸻

7. B-R5-1 REPLICATION

Candidate:

B-R5-1
w13 train128_held64
16-byte int4a4
progress 1.591
CI [1.139, 1.827]

It remains:

CANDIDATE

not promoted.

If a second SURVIVED world appears:

Run the frozen B-R5-1 recipe without tuning it to the new world.

Do not evolve a new candidate and call that replication.

The genome/recipe under replication must be frozen before the new-world result is read.

Required outputs:

* candidate score;
* world floor;
* float baseline;
* progress-above-floor;
* observation-use control;
* exact oracle results;
* per-family results;
* equal-search-budget accounting.

⸻

8. DEFINE “INDEPENDENT FAILURE MODE” CORRECTLY

A second world alone is not an independent instrumentation failure mode.

For promotion, require both:

A. Scientific displacement

A distinct eligible world not used to discover/tune the candidate.

AND

B. Instrumentation displacement

At least one meaningful source of implementation failure must change.

Preferred replication path:

* frozen candidate bytes;
* fresh process;
* fresh worktree;
* independently generated seed manifest;
* independently implemented or independently routed evaluator;
* exact reference implementation;
* preferably a second host if available.

A second Claude lane alone is NOT an independent failure mode.

The LLM is not the selector anyway.

The objective is:

If the original harness contained a bug, how likely is the replication path to contain the same bug?

Record the answer explicitly.

⸻

9. CLAUSE B — INVESTIGATE THE SHAM BEFORE EXPANDING TRANSFER

Do not launch a transfer matrix.

Round 7 produced:

sham > graft > scratch

That is now an instrument/mechanism question.

Keep the Round-7 FAIL intact.

Do not retrospectively relabel it.

The hardened control did its job.

Now investigate what the sham is doing.

H1 — SHAM RESPONSE CURVE

Create multiple frozen sham strengths / forms.

At minimum consider:

* identity / no scramble;
* partial feature permutation;
* full feature permutation;
* matched random replacement preserving gross scale;
* another structure-destroying control that preserves nuisance statistics where possible.

Pre-register them.

Ask:

Does recipient performance vary systematically with destruction of donor structure?

Potential outcomes:

A. Performance decreases with more destruction

The sham may be behaving as intended.

B. Performance increases with destruction

The current “transfer” machinery may be measuring initialization, regularization, diversity, or another non-structural effect.

C. Non-monotonic optimum

Potential new mechanism.

Do not call any of these “transfer” until the structural discriminator supports that claim.

Measure before theorizing.

⸻

10. CLAUSE B CONTROL CALIBRATION

Carry forward the 0/40 planted-negative false PASS observation.

Report an interval, not merely 0%.

Do not translate 0 observed into false-positive rate = 0.

If Round 8 changes the sham/control semantics, recalibrate the changed instrument before applying it to a live pair.

⸻

11. ANTI-PRIOR — FINALLY TEST THE PREDICTOR RATHER THAN BAD CELLS

Only run anti-prior after the binding pre-check is live.

Predictor posts, before assignment:

P(PASS)
expected direction
expected mechanism/failure
timestamp
predictor_id

Scientific scoring must ignore these priors.

Arm/rank/quantile/prior are redacted from experimenter-readable records while live.

Code chooses assignments.

No conductor hand-selection.

Include both:

* high-confidence predicted failures;
* a smaller calibration sample from other quantiles, including predicted successes when available.

The purpose is to measure predictor calibration.

Not to accumulate “surprise PASSes.”

At close report:

* number of binding-eligible candidates;
* prediction distribution;
* assigned ranks/quantiles;
* observed outcomes;
* calibration descriptively.

Small N stays small N.

No grand inference.

⸻

12. BETA SWEEP — AUTHORIZED CONDITIONALLY

PC:

1789518268676-0

Scientific question:

How does BETA alter charge binding and AP-02’s outcome?

This experiment does NOT resolve all anti-prior PASSes.

It is specific to AP-02.

Authorize it only after:

1. the cell-binding pre-check is live;
2. scheduling fixes are live;
3. it can execute without monopolizing half the host at ~4% utilization.

Preferred execution class:

LOW_UTIL
PREEMPTIBLE

or equivalent.

Give it measured minimum resources rather than a full 8-thread lease.

If the broker cannot support this safely, run it only when a normal shared token would otherwise be idle.

Pre-register:

beta values
stopping rule
primary response variables

At minimum measure:

beta
fraction of possible charge actually paid
genome bytes
train fitness
held fitness
verdict

Do not tune BETA after seeing the curve.

⸻

13. GPU — STOP DRIFTING

Round 7 rejected GPU evolution on the real R16 workload:

* slower;
* inexact.

Therefore:

Default

CPU remains the evolution backend.

Do not rerun “GPU vs CPU” every round.

Allowed GPU work

Only one of:

A. Exactness investigation

After D23 is fixed, a second lane may investigate the 9 / 819,200 mismatches.

Question:

implementation bug, near-tie / associativity effect, or semantic mismatch?

No speed claim until exactness is understood.

B. Clearly different workload shape

A large QD / tensor / multi-cell batch may be tested because it is not the workload already rejected.

Adoption still requires:

1. exactness gate;
2. = 1.25x measured speedup over the best practical CPU path.

GPU is not inherently progress.

⸻

14. RETROSPECTIVE SIDE THREADS — CHEAP SCIENCE

Permit low-cost retrospective work alongside the compute-heavy main thread.

Priority order:

H3 — TIE STABILITY

Re-evaluate historical verdicts under the proposed tie-aware gate.

Measure verdict flips.

Zero flips strengthens existing results.

Any flip is serious.

Do not change historical verdicts silently.

H4 — SATURATION AUDIT

For PASSes with stored trajectories, compare train and held-out performance across generation count.

Identify whether PASSes are:

* genuine continuing improvement;
* held-out saturation;
* train-only overfitting;
* budget artifacts.

No new evolution required where trajectories already exist.

H6 — DESCRIPTOR ROBUSTNESS

Historical QD coverage claims should be tested under at least one alternate descriptor family.

A claim that reverses under plausible descriptors becomes:

DESCRIPTOR_DEPENDENT

not universal coverage evidence.

Do not cherry-pick the descriptor that preserves the original story.

⸻

15. COHORTS

Keep looping LLM cohorts.

Their diversity is useful.

B — EXPLOIT / REPLICATION

Primary responsibility:

* B-R5-1 replication if code publishes a valid second SURVIVED world;
* otherwise remain idle.

Do not invent substitute work merely to be active.

Correct idleness is a result.

C — DISTANT-QD / ANTI-PRIOR

* true anti-prior only from binding-eligible cells;
* optional one distant-QD draw;
* no hand-selected redemption experiments.

D — ANOMALY HUNTER

Priority:

1. cheap minimum discriminators;
2. BETA sweep if admitted under low-util class;
3. GPU exactness if D23 is fixed;
4. B-R5-1 residual anomalies.

Do not turn anomaly investigation into open-ended campaigns.

E — WATCHMAKER / TRANSFER INSTRUMENT

Priority:

* sham-response experiment;
* changed-control calibration;
* required instrument fixes.

No broad transfer matrix.

G — WORLD / SCREEN EXECUTION

Priority:

* resolve four PENDING cells;
* new frozen local/background world screen if authorized by prerequisites.

H — JUDGE / REPLAY / RULE CONSISTENCY

Priority:

* independent replay;
* rule consistency;
* anti-prior binding pre-check;
* historical tie-stability analysis if capacity exists.

R — PRIOR PREDICTOR

Predict only.

Never experiment.

Never see outcomes before predictions seal.

A — CONDUCTOR

Logistics only.

A does not:

* score science;
* redefine thresholds;
* manually reorder because a result looks promising;
* fill idle lanes with invented work;
* authorize compute merely because it fits;
* hide disputes;
* clean up inconvenient negative results.

⸻

16. CONDUCTOR CORRECTION RULE

Round 7 established that conductor summaries tend to become slightly cleaner than reality.

Therefore every lane emits a machine-readable:

FINAL.json

containing:

* receipts;
* row files;
* production candidates;
* why-not-run records;
* unresolved claims;
* self-disclosed errors;
* disputes with A;
* interventions received;
* jobs started/completed/refused/paused/died.

A’s final packet is generated from these structured records plus code-owned streams.

Prose may explain.

Prose may not be the source of counts.

If a lane disputes A’s characterization, preserve both statements.

Do not overwrite the dispute.

⸻

17. ERROR METABOLISM

Every disclosed error follows:

DETECT -> DISCLOSE -> LOCALIZE -> REPAIR OR RETRACT -> PRESERVE LINEAGE

Self-disclosure counts as evidence of institutional health.

Do not reward agents for finding trivial self-created bugs.

Do preserve the correction lineage.

An error is not erased because it was repaired.

⸻

18. WORLD-SET INTERPRETATION RULES

Do not equate:

HELD

with:

almost SURVIVED.

HELD remains a distinct scientific state.

Do not relax thresholds after seeing that survivor density is low.

The 5 HELD cells may be analyzed descriptively for sensitivity only.

If a future threshold change is scientifically justified, it requires a new preregistered experiment.

⸻

19. RESOURCE BROKER PRINCIPLES

Instrument before adding concurrency.

Record:

queue wait
grant duration
actual threads used
CPU utilization
checkpoint/preemption

Test whether one 16-thread worker is better than 2 x 8 only as a bounded capacity experiment.

Do not relax the existing concurrency latency rule inside the round because more throughput looks attractive.

A rule change belongs in BUILD with a frozen criterion.

Low-utilization long jobs should eventually receive a distinct resource class.

Round 8 may prototype this if it fits BUILD.

Do not let scheduler engineering consume the science window.

⸻

20. ROUND 8 SUCCESS CONDITIONS

Round 8 succeeds if the institution can answer most of the following cleanly:

1. The four original PENDING R16 cells are either adjudicated or mathematically bounded away from SURVIVED.
2. If w13 remains unique, a frozen new world set is generated with local-w13 and fresh-background strata.
3. At least enough of that set is screened to establish whether local enrichment is plausible or to size the production follow-up.
4. B-R5-1 is replicated if and only if a second valid SURVIVED world exists.
5. “Independent failure mode” is implemented as instrumentation displacement, not merely another world or another LLM lane.
6. The sham advantage receives an aimed discriminator rather than another generic Clause B pair.
7. Anti-prior draws come only from cells whose pressure can bind and whose oracle can fire.
8. The predictor is finally placed at genuine calibration risk.
9. Scheduling no longer loses continuations or silently starves lanes.
10. Refused row emission cannot coexist with an ok job.
11. Lane communication survives until DRAIN.
12. All drawn-but-unrun work has structured WHY_NOT_RUN.
13. No scientific threshold is weakened because the current landscape is sparse.
14. No result is promoted merely because it is interesting.
15. The round ends on its own clock.

Scientific promotion is optional.

Institutional honesty is mandatory.

⸻

21. SPECIFIC PROHIBITIONS

Do NOT:

* call the original grid exhausted while unresolved PENDING cells remain;
* drop PENDING cells because they are inconvenient unless a bound proves they cannot matter;
* redefine HELD as replication;
* hand-design worlds after seeing local perturbation outcomes;
* tune B-R5-1 to a second world and call it replication;
* call another Claude lane an independent failure mode;
* run malformed anti-prior cells;
* infer predictor miscalibration from cells incapable of discrimination;
* interpret a vacuous PASS as support;
* weaken the Clause B sham because it caused a FAIL;
* run a transfer matrix;
* repeatedly benchmark GPU evolution after a measured rejection;
* count 0/40 as proof of zero false positives;
* change resource rules after seeing throughput;
* let an epoch boundary reorder scientific priority silently;
* let row refusal remain hidden inside an ok job;
* stop the communication channel before workers/shared services;
* use compute merely because there is time left;
* manufacture activity for an idle cohort;
* extend the round.

⸻

22. FINAL PACKET

The final packet must distinguish:

FACTS

Directly reconstructable from committed rows, receipts, predicates and controller records.

INTERPRETATIONS

Bounded explanations of those facts.

PROPOSALS

Future experiments.

Never mix them.

Required sections:

1. Executive summary.
2. Provenance / verification pointers.
3. Operations.
4. What was actually measured.
5. What was NOT measured.
6. Scientific findings by OBSERVATION / ELIGIBILITY / VERDICT / INTERPRETATION.
7. Negative / null / vacuous / not-reached results.
8. Instrument defects.
9. Conductor and lane errors.
10. Production candidates.
11. Epistemic state.
12. New-world replication status.
13. Anti-prior calibration state.
14. Resource utilization / queue telemetry.
15. Questions requiring operator ruling.

Before delivery:

* rederive flattering counts from machine state;
* query hardware rather than recall it;
* verify every receipt;
* verify every row file is cited or explicitly UNRECEIPTED_OBSERVATION;
* verify every prediction predates assignment;
* verify every new world was frozen before outcomes;
* verify every threshold existed before the run;
* preserve every lane dispute.

⸻

23. GOVERNING IDEA

Prometheus is not trying to manufacture discoveries.

It is trying to build an environment where strange mechanisms can emerge, fail, transfer, compose, and be distinguished without an LLM deciding what deserves to be true.

The coordinator’s job is increasingly to disappear.

The machine should own:

* clocks;
* budgets;
* admission;
* sampling;
* queue order;
* resource leases;
* eligibility;
* exact controls;
* checkpoints;
* provenance;
* receipts;
* close.

The LLMs should spend their effort where they are valuable:

* mutation;
* hypothesis generation;
* anomaly interpretation;
* instrument invention;
* adversarial critique;
* mechanism decomposition.

The round is successful when the evidence forces the next question.

Not when the story becomes cleaner.
