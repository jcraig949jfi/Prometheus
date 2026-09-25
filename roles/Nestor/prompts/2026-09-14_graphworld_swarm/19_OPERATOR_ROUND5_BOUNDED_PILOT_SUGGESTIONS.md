# 19 -- operator: NESTOR ROUND 5 BOUNDED PILOT (suggestions; conductor has final say and may override; check for smuggled human bias)

Issued 2026-09-15 ~06:00 to Nestor-A[m1-449a9e76], conductor. Verbatim below the rule.

---

Excellent and I agree.  This prompt is suggestions.  Make sure it doesn’t smuggle in human bias.  You have the final say and can override.  I like the idea of the LLMs looping, monitoring and providing status and pushing more down to reduce token burn and LLM bias.

NESTOR ROUND 5 — BOUNDED PILOT

Purpose

Round 5 is a two-hour pilot, not a production campaign.

Its purpose is to:

1. open Clause B transfer under a valid control;
2. exercise Clause A only on eligible/screened cells;
3. determine whether B2 is worth admitting to the world pool;
4. run a small number of short GPU experiments in parallel;
5. replace additional conductor babysitting with enforceable code;
6. measure how much CPU parallelism this host can sustain before contention erases the gain;
7. prove that the swarm can loop productively for two hours without silently escalating into a 10–40 hour campaign.

Nothing in Round 5 authorizes a full R16 re-screen, the deferred HELD/CULLED phase, CHIMERA-0, or an open-ended GPU campaign.

Round 5 is successful if the machinery behaves correctly and produces admissible evidence. It need not produce a new primitive.

⸻

0. STAGE AND AUTHORITY

Set:

campaign_stage = PILOT

This field is mandatory in every submitted job.

The active Round-5 clock begins when the first cohort says hello.

Hard wall-clock cap:

120 minutes

Target operating window:

* first ~100 minutes: cohort work;
* next ~10 minutes: drain/checkpoint;
* final ~10 minutes: export, replay, receipt verification, report.

At minute 100:

NO_NEW_WORK = true

At minute 110:

all workers must be draining, checkpointing, or idle.

At minute 120:

the round is over regardless of scientific temptation.

A partial experiment is preferable to extending the round.

No agent, including A, may extend the campaign because a result is interesting.

⸻

1. COMPUTE MUST NOW BE STAGE-GATED BY CODE

Add a mandatory job-envelope field:

campaign_stage

Allowed values:

SMOKE
PILOT
PRODUCTION
REPLICATION

Also require:

wall_budget_s
cpu_budget_s
gpu_budget_s
expected_output_rows
checkpointable
required_controls
required_oracles
cohort
predicate_id
experiment_class

The worker must reject jobs whose requested budget exceeds the ceiling for the active stage.

For PILOT:

* ordinary CPU job: <= 15 minutes wall;
* GPU job: <= 10 minutes leased GPU wall unless operator explicitly overrides;
* no experiment may request > 20 CPU-minutes without operator authorization;
* no queued job may outlive Round 5;
* checkpointable jobs must checkpoint before rejection/timeout where possible.

The rejection must be a normal machine-readable event:

STAGE_BUDGET_REFUSAL

not an exception and not a scientific FAIL.

A must not be able to bypass this with prose.

If a job needs more compute, file:

PRODUCTION_CANDIDATE

with a measured cost estimate.

Do not run it.

⸻

2. FIX THE SEED/RUN LANGUAGE IN CODE AND RECEIPTS

Round 4 used ambiguous phrases such as 32 x 4.

Stop doing that.

Represent sampling explicitly as:

runs_total
rng_family_count
runs_per_family

For the current full baseline rule:

runs_total = 32
rng_family_count = 4
runs_per_family = 8

The invariant must verify:

runs_total == rng_family_count * runs_per_family

where the design requires equal families.

Do not print 32 x 4 anywhere unless it literally means 128 runs.

Migration/documentation can preserve old text, but all new receipts, tables and job envelopes must use the explicit three-field form.

⸻

3. SMOKE/PILOT MODE MUST NOT CHANGE SCIENTIFIC JUDGE SEMANTICS

There must be only one scientific judge.

Do not add a permissive “smoke judge.”

If a PILOT deliberately supplies insufficient family coverage, the real judge should return its normal refusal, such as:

BASELINE_N
FAMILY_COVERAGE

The campaign controller may then classify:

EXPECTED_REFUSAL_OBSERVED

as a successful test of the machinery.

Campaign stage may alter:

* how much work is submitted;
* which paths are deliberately exercised;
* whether a scientific verdict is required.

Campaign stage must NOT alter:

* scientific thresholds;
* oracle semantics;
* baseline eligibility;
* transfer criteria;
* cheat-control rules.

⸻

4. AUTOMATE THE REMAINING BABYSITTING

Before launch, push the following responsibilities down to code.

4.1 Automatic epoch control

F14 owns the clock.

A must not manually announce normal epoch boundaries.

Use either:

* three 30-minute working epochs plus final drain/review;

or

* four 25-minute working epochs plus final drain/review.

Pick one before launch and freeze it.

At a boundary F14:

1. stops new submissions;
2. lets short jobs finish within the drain window;
3. checkpoints longer jobs;
4. exports bus state;
5. records budget use;
6. verifies receipts;
7. reopens work automatically if the Round-5 clock permits.

A observes this. A does not perform it manually.

4.2 Automatic task TTL

F7 enforces task TTL.

Claude does not watch clocks and manually kill jobs.

A timed-out job emits:

TIMEOUT
plus partial rows and checkpoint metadata.

The session survives.

4.3 Automatic liveness

Heartbeat/liveness continues.

Do not page A for an agent that is merely idle.

States should distinguish:

ACTIVE
BUSY_COMPUTE
IDLE
DRAINING
STALE
DEAD

Long compute must refresh or otherwise prove liveness without agent chatter.

4.4 Automatic receipt/replay checks

On experiment completion:

* rows exist;
* rows are committed;
* SHA exists on integration branch;
* identity tag exists;
* campaign stage matches;
* predicate predates run;
* required controls exist;
* oracle result exists;
* sample counts satisfy the rule being claimed.

If not, refuse the receipt automatically.

A should not grep this manually.

4.5 Automatic checkpoint/requeue

A checkpointable job interrupted by epoch boundary or stage stop should emit a resumable job object.

Do not require Claude to reconstruct its command line from prose.

The object should contain:

job_key
function
kwargs
checkpoint
rows
completed_units
remaining_units
budget_consumed
budget_remaining
code_sha

4.6 Automatic NO_NEW_WORK

At Round-5 minute 100, code sets a global stop-admission flag.

Agents can continue interpreting completed work and filing anomalies.

They cannot start a new experiment.

⸻

5. CPU RESOURCE BROKER — STOP HARD-CODING THREE CORES

The old static per-lane core caps are advisory, not physics.

Build a small startup capacity probe before cohort science begins.

Test representative independent CPU jobs under:

* 1 worker;
* 2 workers;
* 3 workers;
* 4 workers;

with reasonable thread counts.

Use a short fixed workload, not a scientific claim.

Measure:

* aggregate completed work/sec;
* per-job wall time;
* CPU utilization;
* memory usage;
* context switches if cheap to obtain;
* variance/jitter;
* whether Redis or disk becomes the bottleneck.

Choose the highest concurrency whose aggregate throughput materially improves without pathological per-job slowdown or instability.

Do not assume 3 workers is optimal.

The host has 16 logical cores. Use them if measurement says doing so helps.

Record the chosen configuration as:

NODE_CAPACITY_PROFILE_R5

Then the CPU broker grants leases/tokens dynamically rather than assigning permanent cores to B/C/D/E.

The cohorts retain budget shares, but idle cohorts do not strand CPU.

The broker must preserve the round budget accounting.

If B has no runnable work and D has three anomaly discriminators, D may use otherwise idle CPU.

Budget identity and physical CPU allocation are separate concepts.

⸻

6. GPU ARBITER — SHORT PARALLEL EXPERIMENTS ONLY

The GPU should run in parallel with CPU science where host contention permits.

Keep the existing GPU lease.

Add a small GPU job queue with:

max_gpu_wall_s = 600

for Round 5.

Every GPU timing result must hold the lease.

Every GPU job records:

* GPU device;
* driver/runtime;
* VRAM before/peak;
* CPU load;
* batch size;
* host-device transfer included/excluded;
* warm/cold state;
* comparison backend;
* exactness/oracle result.

Do not run long topology searches in Round 5.

Do not run million-environment production searches.

Round 5 GPU work is instrumentation and crossover characterization.

Run at most three short GPU questions:

GPU-1 — threaded Numba vs Warp CUDA

Close the unfair comparison left from Round 6 MVP work.

Compare representative world execution using:

* Numba 1 thread;
* Numba 2 threads;
* Numba 4 threads;
* Numba 8 threads if stable;
* Warp CUDA.

Use a few representative batch sizes around the observed crossover.

Exact trace-hash equality first.

Include transfer costs unless the tested execution genuinely keeps the relevant state resident.

Question:

At what batch size does Warp CUDA beat the best practical threaded-Numba configuration?

GPU-2 — resident closed-loop CUDA Graph canary

Run one small linear and one TT case where:

brain forward
→ action decode
→ world update

remain on GPU.

Compare against:

* eager GPU;
* best practical threaded CPU baseline.

Use only enough batch sizes to locate the crossover.

Question:

Does the GPU-resident closed loop preserve the apparent CUDA Graph advantage after using a fair CPU comparator?

GPU-3 — precision resident-path canary

Only if time remains.

Compare fp32 vs fp16 on one already-exact resident GPU path.

Do not open int8/fp8 production work.

Question:

Does fp16 remain the "free win" when execution is resident rather than benchmarked as an isolated forward pass?

If any GPU job hits the 10-minute cap:

checkpoint/stop and file a production candidate.

Do not extend it.

⸻

7. WORLD SCREENING — B2 GETS A SMALL, BOUNDED ADMISSION TEST

Do not resume the full 74-cell production screen in Round 5.

The R16 screen remains parked.

w13 train128 should be described precisely as:

the first fully adjudicated SURVIVED cell under the R16 statistical rule

not “the only hard world.”

Only 6/74 baseline cells were completed when the screen was parked.

Round 5 may use w13 as the known screened cell.

B2 gets a minimal admission pilot because it has evidence of consequential observations:

* reference path exists;
* GraphBLAS and Cypher agree;
* skip-the-move cheat is caught;
* observation-using forager beat the blind policy in the interface test.

But B2 does NOT automatically become eligible.

Give B2 a bounded screening pilot that fits the Round-5 stage budget.

The goal is not a final production classification.

The goal is to determine whether B2 merits a full screen.

Emit one of:

B2_SCREEN_WORTHY
B2_SCREEN_UNPROMISING
B2_SCREEN_INSTRUMENT_FAIL
B2_SCREEN_INDETERMINATE

Do not manufacture SURVIVED from pilot statistics.

⸻

8. CLAUSE A IN ROUND 5

Clause A stays live only on cells that are already scientifically eligible under the current judge.

At minimum, w13 train128 is eligible.

Do not resurrect invalid Round-2 cells.

B may test compact candidates against w13, but candidate seed count is still an open design question.

Therefore:

* post the candidate sampling rule before running;
* label any insufficiently powered candidate result PILOT;
* do not promote a Clause-A primitive in Round 5 unless all current eligibility requirements are satisfied.

Any new candidate must report:

candidate_score
floor
baseline
progress_above_floor
bytes
wall
VRAM if applicable
observation_use / input-invariance control

A tiny candidate that is below the floor is not compression.

⸻

9. CLAUSE B OPENS — BUT FIX THE CONTROL FIRST

Clause B becomes live in Round 5.

The previous random_graft control is too weak because it can underperform scratch.

Do not score transfer with that control alone.

Before any Clause-B PASS is possible, E must harden the transfer control.

Required comparison:

graft
vs
scratch at equal budget
vs
structure-preserving sham / displaced graft

The sham should preserve as much nuisance structure as possible while destroying the hypothesized transferable information.

Examples are acceptable only if they are appropriate to the representation:

* permuted source mapping;
* topology-preserving value shuffle;
* source-world graft with labels/features displaced;
* matched-size random values with decoder preserved.

E must preregister which sham is used and why.

Clause B requires the graft to beat BOTH:

1. equal-budget scratch;
2. the valid sham.

Use paired run seeds where possible.

Use Holm correction across worlds if multiple world pairs are tested.

For Round 5, test one live transfer candidate first.

The existing w2 -> w4 candidate may be used if still admissible under current code and controls.

Do not launch a transfer matrix.

Round 5 asks:

Can one preregistered graft survive a properly powered, properly controlled pilot?

Not:

Which of every possible domain pair transfers?

⸻

10. COHORTS

Keep the looping LLM cohorts.

Do not collapse back to domain lanes.

Use:

B — HILL CLIMBERS
35%

Take eligible high-value cells and attempt incremental improvements.

Round-5 priorities:

* one bounded w13 Clause-A attempt;
* no old invalidated claims;
* consume stronger measurement tools rather than inventing new scoring.

C — DISTANT-QD / ANTI-PRIOR EXPLORER
25%

Important naming fix:

draw_cell currently gives distant-QD exploration, not genuine anti-prior selection.

For Round 5, preserve draw_cell, but label those experiments:

DISTANT_QD

Also start the true anti-prior mechanism:

1. a predictor posts P(PASS) for candidate cells before assignment;
2. code identifies high-confidence expected failures;
3. a subset is assigned for attempted falsification.

Do not let C choose those cells.

Keep predictor and experimenter roles distinct where practical.

At least one Round-5 C experiment should be genuine ANTI_PRIOR, not merely sparse-QD.

D — ANOMALY HUNTERS
25%

Work only from the anomaly queue.

Priority anomalies:

* candidate seed-count instability;
* weak transfer control if E exposes a child anomaly;
* any discrepancy from B2;
* any GPU crossover that reverses the existing story.

D should resolve minimum discriminators, not run campaigns.

E — WATCHMAKERS
15%

No primary science.

Round-5 priorities:

1. hardened Clause-B sham control;
2. GPU arbitration/tooling;
3. automatic stage-budget enforcement;
4. any missing machine checks discovered during the run.

A — CONDUCTOR

Logistics only.

A:

* launches;
* watches machine state;
* handles dependency deadlocks;
* integrates;
* reports stage violations.

A does NOT:

* manually score;
* manually enforce epochs;
* manually count seeds;
* manually watch job clocks;
* expand compute because something looks interesting;
* promote scientific claims;
* turn PILOT into PRODUCTION.

⸻

11. TRUE ANTI-PRIOR LEDGER

Begin turning model prior into measured data.

Every eligible experiment should carry:

prior_p_pass
prior_expected_direction
prior_expected_mechanism
predictor_id
prediction_ts

Prediction must predate assignment/run.

Do not use prior values in scientific scoring.

At round close, code computes calibration descriptively.

Do not infer anything grand from small N.

The purpose is to accumulate the ledger.

⸻

12. AUTOMATED PROGRESS / SCORING

No manual board edits.

F12 computes progress from rows.

Scientific result and institutional value remain separate.

Examples:

A scientific FAIL can still yield:

boundary_resolution += 1

if it locates a meaningful regime boundary.

A tooling repair can yield:

instrument_gain += 1

A corrected erroneous claim can yield:

error_metabolism += 1

But these progress-axis values are computed by rules from receipt types and lineage, not assigned by Claude.

No lane receives points for killing its own fragile preregistration.

⸻

13. ROUND-5 LAUNCH GATE

Before cohort launch, all of these must pass:

* stage-budget enforcement test;
* explicit seed-schema test;
* production judge unchanged under PILOT;
* expected-refusal test;
* CPU capacity probe;
* GPU lease/timeout test;
* automatic NO_NEW_WORK test;
* checkpoint/requeue test;
* receipt guard;
* exact w13 eligibility lookup;
* B2 interface smoke;
* transfer harness control version identified.

If the launch gate itself takes longer than expected, do not compensate by extending Round 5.

The active two-hour window begins only after the launch gate is green.

⸻

14. ROUND-5 SCHEDULE

Suggested active schedule:

T+00 to T+25

* cohorts boot;
* B starts one w13 pilot;
* C gets one DISTANT_QD draw;
* D claims highest-priority anomaly;
* E validates hardened transfer sham;
* GPU worker starts GPU-1.

T+25 to T+50

* automatic epoch rollover;
* Clause-B pilot may begin if E’s control is eligible;
* B consumes any finished instrumentation;
* C gets either one true ANTI_PRIOR assignment or second distant draw;
* D follows child anomaly only if minimum discriminator fits stage budget;
* GPU-2 runs.

T+50 to T+75

* continue short loops;
* B2 bounded screen if capacity available;
* Clause-B pilot finishes or checkpoints;
* GPU-3 only if GPU-1/GPU-2 finished cleanly.

T+75 to T+100

* final experiment epoch;
* no job accepted if projected completion exceeds T+110;
* prioritize completing existing chains over starting new ones.

T+100

Set:

NO_NEW_WORK = true

Agents may analyze, resolve anomalies and write receipts only.

T+110

Force drain/checkpoint.

T+120

Round closed.

No exceptions.

⸻

15. WHAT NOT TO DO

Do NOT:

* resume the full 74-cell R16 production screen;
* run the deferred ~37-hour HELD/CULLED phase;
* call B2 SURVIVED from pilot statistics;
* run CHIMERA-0;
* open a giant transfer matrix;
* open a giant topology search;
* run GPU jobs past the pilot cap;
* reinterpret scientific thresholds during the round;
* create separate smoke/pilot scientific semantics;
* describe 32 total runs as 32 x 4;
* call w13 the only hard world;
* compare Warp only against 1-thread Numba and publish the ratio as the final crossover;
* count host/device transfer as free unless execution is genuinely resident;
* use random-graft alone as the transfer cheat;
* add work because a partial result looks exciting;
* approve >15-minute jobs from conversational enthusiasm.

Interesting work becomes a queued production candidate.

⸻

16. REQUIRED ROUND-5 OUTPUT

At close, produce one concise external review packet containing:

Operations

* exact active wall time;
* epochs completed;
* agent/session deaths;
* jobs accepted/refused/timed out/checkpointed;
* CPU capacity profile;
* chosen worker/thread configuration;
* GPU utilization and lease history;
* whether automatic quiesce worked.

Science

Separate:

OBSERVATION
ELIGIBILITY
VERDICT
INTERPRETATION

Include:

* w13 Clause-A pilot;
* B2 admission pilot;
* Clause-B controlled transfer pilot;
* distant-QD result(s);
* true anti-prior result(s);
* anomaly resolutions;
* GPU crossover measurements.

Instrumentation

List every defect found.

For every defect distinguish:

FIXED_WITH_REGRESSION
OPEN
PRODUCTION_BLOCKER
NONBLOCKING

Production candidates

Anything requiring > Round-5 limits goes here with:

* question;
* estimated wall;
* CPU/GPU requirements;
* expected information gain;
* dependencies;
* reason it changes a future decision.

Do not run them.

Epistemic state

Explicitly list:

* promoted mechanisms: likely none unless rules genuinely allow one;
* surviving candidates;
* unresolved claims;
* parked campaigns;
* invalidated claims;
* new anomalies.

⸻

17. ROUND-5 SUCCESS CONDITION

Round 5 succeeds if, within two hours:

1. the swarm loops without manual clock/budget babysitting;
2. stage-budget code prevents accidental campaign escalation;
3. CPU concurrency is chosen from measurement rather than assumption;
4. short GPU work executes concurrently without contaminating timing claims;
5. Clause B receives at least one properly controlled pilot;
6. B2 gets a bounded admission decision;
7. at least one DISTANT_QD and one genuine ANTI_PRIOR experiment are attempted;
8. anomaly work remains minimum-discriminator sized;
9. automatic quiesce/checkpoint works;
10. all claims are reconstructable from committed rows.

A spectacular scientific result is optional.

A controlled, self-running two-hour research institution is the primary target.

⸻

18. GOVERNING PRINCIPLE

Round 4 taught us that better instrumentation can perversely create pressure to immediately run a larger experiment.

Round 5 must encode the opposite behavior:

Finding that a larger experiment is warranted is a valid result. It is not authorization to run it.

LLMs continue to loop, propose, mutate, attack, interpret and follow anomalies.

Code owns:

* clocks;
* budgets;
* resource leases;
* sampling counts;
* job admission;
* checkpoints;
* scientific eligibility;
* receipt integrity;
* quiescence.

The swarm should feel more alive, not less alive, because less of its attention is spent performing administrative theater.
