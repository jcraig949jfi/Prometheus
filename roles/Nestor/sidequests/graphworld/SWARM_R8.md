# SWARM R8 -- BOUNDARY, REPLICATION, AND INSTRUMENT DISCIPLINE

Adopted from operator prompt 24
(`roles/Nestor/prompts/2026-09-14_graphworld_swarm/24_OPERATOR_R8_BOUNDARY_REPLICATION_INSTRUMENT_DISCIPLINE.md`,
sha256 e3bfff54b10d45b6b406e36d1714a81e7ecac6a1ffe24ece85716c186453d5c8).

Stage: PRODUCTION.

**TIME BUDGET SUPERSEDED BY OPERATOR PROMPT 25** (sha256 in MANIFEST). Prompt 24's 9 h cap is replaced by:

| allocation | duration | owner |
|---|---|---|
| SCIENCE clock | **12 h** | code-owned, no conductor extension |
| setup + teardown | **2 h** | build + gate, then drain + close + packet |
| iterative refinement | **1 h** | interactive with the operator, in the originating conversation |
| **end-to-end cap** | **15 h** | hard |

The active science clock is code-owned. No conductor extension. Conductor (A) is logistics only: A does not
score, does not set or move a threshold, does not authorise compute, and does not fill idle lanes with
invented work.

**[ADAPT-12] The refinement hour is scoped, because an unscoped one violates P3.** It covers instruments,
logistics and sizing only; it CLOSES before any scientific result exists; and it may never move a threshold,
redefine success, or re-size an experiment because partial results look interesting. Design changes after
data exist are not refinement, they are the failure mode P3 names.

Everything below marked **[ADAPT-n]** is a conductor adaptation under the operator's "adapt as you see
fit", with its reason stated. Adaptations that would change a SCIENTIFIC rule are not taken -- they are
raised as questions in section 14 instead.

---

## 0. GOVERNING PRINCIPLE AND THE RESIDUE RULE

Failure is geometry, not a tombstone. The product of round 8 is residue and failure gradients that emit
usable signal for later rounds. Telemetry, eligibility repair and boundary-narrowing are first-class
deliverables. Disk IO spent on logging is an accepted cost, not waste, and a slower experiment that leaves
a reusable gradient beats a faster one that leaves a bare verdict.

**[ADAPT-1] O-RESIDUE (new, enforced at receipt time).** Every receipt must declare `residue`: a non-empty
list drawn from the operator's seven classes, or the explicit token `NONE`.

    narrower_boundary | better_instrument | repaired_eligibility_rule | new_mechanism_candidate |
    new_world_generation_requirement | cheaper_discriminator | better_next_experiment | NONE

The close packet reports the count of receipts declaring NONE. Reason: the operator's rule "a negative
result that changes none of these is low-value" is otherwise unmeasurable. This makes it countable without
letting anyone score the science -- the lane declares, code records, the packet counts. It adds no
threshold and decides no verdict.

**We are not abolishing PASS/FAIL.** The verdict classes stay exactly as they are. What changes is that a
verdict alone is no longer a complete deliverable: a receipt with `residue: NONE` is admissible, recorded,
and visible as such at close.

### 0.1 ARCHIVAL SUFFICIENCY (operator prompt 26)

The program explores terrain for which no LLM has priors. Telemetry exists so that anomalies and ripples
that nobody can currently interpret remain recoverable later: a model in 2028 may separate signal from noise
where a model in September 2026 cannot. The standard for round 8 is therefore not "did we log a lot" but:

> **A future analyst with no access to this session can (a) re-derive every verdict, (b) RE-RUN the
> experiment, and (c) mine the record for anomalies nobody thought to look for at the time.**

Two rules make this safe, and they are in tension unless stated explicitly:

**[ADAPT-14] TELEMETRY IS WRITE-ONLY WITH RESPECT TO SCIENCE.** No telemetry field may enter an eligibility
check, an admission decision, a control, a discriminator or a verdict. Instrumentation is additive and
observational, never a modifier. Operator prompt 26: "we don't adjust the science to this but rather ensure
we can comb over the data long after the experiment." Hard PASS/FAIL stays exactly as frozen -- it will
produce false positives and false negatives on alien terrain, and the answer to that is a richer RECORD, not
a softer rule. A lane that finds an anomaly in telemetry files it as an anomaly or a candidate; it does not
relabel a verdict.

**[ADAPT-15] THE BUS IS NOT AN ARCHIVE -- and today the richest telemetry is not archived at all.**
Measured, not assumed:
- `primordial/bus/bus.py:126` posts with `maxlen=100_000, approximate=True`. Every bus stream ages out.
- The epoch export commits `pm_swarm`, `pm_results`, `pm_anomalies` and `pm_boards_claims` only.
- **There is NO export of the job done stream.** `epoch.py` reads `DONE` solely to aggregate `cpu_s` into
  per-cohort summaries. So `cpu_s`, `wall_s`, `granted_threads`, `numba_threads`, `segment`, `sha`,
  `predicate_id`, `rows_path` -- and every section-12 telemetry field -- exist ONLY in a capped Redis stream
  and are never committed.
- Proof of the gap: the conductor's own round-8 cost analysis (section 4.4) reads `pm:jobs:G:done` from
  Redis and therefore **cannot be reproduced by a future analyst from the repository**.

Required before the clock (gate G7): the per-epoch export covers the job done stream and every telemetry
stream, committed as row files. Anything that must survive the round must land in a committed file, never
only on the bus.

**RERUN SUFFICIENCY.** Beyond metrics, the archive must carry what is needed to re-execute: seed manifests
and RNG family assignments, genome bytes for every candidate and control arm, per-generation trajectories
(not only endpoints), raw oracle outputs, the code sha plus the transitive import-closure fingerprint, the
env fingerprint (python / numba / driver / GPU), the host spec, the predicate refs, and the captured payloads
of ABORTED runs (D29 showed those payloads are recoverable and they are exactly the "ripples" worth keeping).
Retention is append-only: nothing is rotated, trimmed or deleted to save space.

---

## 1. CLOCK

**[ADAPT-2] The round clock is CAP-ANCHORED, not start-anchored.** `end_ts` is derived from the **15 h** cap
measured from round start (prompt 25), not from `launch_ts + N*epoch_s`.

Reason: prompt 24's suggested structure (60 + 20 + 420 + 40 minutes) summed to exactly 540 minutes, i.e. the
entire 9 h cap with zero slack. Prompt 25 widened the cap to 15 h with a 12 h science clock, but the
zero-slack hazard is unchanged in kind: build and gate still precede the clock, and any overrun has to come
out of something. Round 7 lost ~6 minutes at launch to a conductor script defect and had a
build-phase deadlock (D18). Under a start-anchored clock any build or launch overrun silently consumes the
packet window or forces an extension, which section 21 prohibits. Under a cap-anchored clock an overrun
automatically consumes SCIENCE clock, the round still ends on time, and no conductor judgement is involved.

Formally: `SCIENCE_END_TS = min(science_start + 12 h, T0 + 15 h - teardown_reserve)` with
`teardown_reserve = 60 min`. A build or gate overrun therefore consumes SCIENCE time automatically and the
round still ends inside the cap, with no conductor decision and no extension.

Targets (science clock shrinks if build/gate overrun; the cap does not move):

| phase | target | notes |
|---|---|---|
| BUILD / hygiene | <= 60 min | see section 3 triage |
| gate | <= 20 min | includes gate->blocked-work map |
| REFINE (interactive) | <= 60 min | ADAPT-12; closes before any result exists |
| active clock | **12 h**, code-owned | 12 x 3600 s epochs; last boundary precedes drain |
| drain + close + packet | <= 60 min | close is code-owned |

---

## 2. PRINCIPLES (operator section 1, adopted unchanged)

P1 no scientific kill before ELIGIBILITY; anything failing earlier is INSTRUMENT_FAILURE /
IMPLEMENTATION_DEFECT / RUN_INELIGIBLE / REPAIR_REQUIRED / INDETERMINATE, never a hypothesis kill.
P2 repair does not reset the bet: smallest warranted repair, frozen seeds/worlds/budgets/discriminator, rerun
the same experiment.
P3 LLMs do not define scientific success. They may propose, mutate, debug, interpret, attack, nominate.
They may not move thresholds after seeing results, redefine success, promote their own claim, or convert
implementation failure into scientific failure.
P4 OBSERVATION / ELIGIBILITY / VERDICT / INTERPRETATION stay four separate layers in every receipt and every
final. No prose collapses them.
P5 admission means MAY run, not SHOULD run.
P6 a drawn experiment may correctly be NOT RUN -> structured `WHY_NOT_RUN`.
P7 at least one exploration channel stays blind to the semantic meaning of what it creates.
P8 scientific cohort share is not permanent CPU ownership; idle compute may move, evidence ownership does not.

---

## 3. BUILD PHASE: HARD GATES AND TRIAGE

**[ADAPT-3] The build list is over-subscribed for a 60-minute window, and the round degrades gracefully by
code rather than by conductor judgement.**

Reason: round 7's build took 52 minutes with four builders and delivered less than this list (four hard-gate
families, six minimum telemetry items, three conditional fixes). Honest estimate: 2-3x the window. The
operator's own wording is the solution -- each gate "must land before affected work begins" -- so each gate
blocks only its dependent science, and ADMISSION enforces it.

**Gate -> blocked work map (enforced at admission, refusal reason `GATE_NOT_LANDED:<id>`):**

| gate | operator ref | blocks |
|---|---|---|
| G8 the `ROUNDS["r8"]` row + complete `lane_repos` | launch prep | **THE CLOCK ITSELF, therefore everything.** Measured: with no r8 row, `plan()` falls back to `DEFAULT_ROUND="r7"` and silently returns 8 epochs / 9.00 h, raising nothing |
| G1 row/evidence vocabulary loud-fail + lint (D29) | 2.3 | ALL row-emitting science |
| G2 anti-prior cell-binding pre-check (PC 1789523009420-0) | 2.1 | all new anti-prior draws; BETA sweep |
| G3 scheduling cluster D15+D22+D30 + queue telemetry | 2.2 | shared-CPU multi-lane science |
| G4 close/watch protocol + protocol lint (D31) | 2.4 | nothing in-round; blocks CLOSE correctness |
| G5 telemetry minimum (section 12) | 3 | nothing; but a round without it fails its own mission |
| G6 `envelope.open_candidate()` -- file a candidate with no refusal event (D27) | prompt 26 | nothing directly; without it every WHY_NOT_RUN and residue record needs a hand-written stub |
| G7 per-epoch export of the job done stream + telemetry streams to COMMITTED rows (ADAPT-15) | prompt 26 | nothing directly; without it the round's telemetry does not survive the round |
| C1 D23 gpuq worktree isolation | 2.5 | cross-lane GPU work |
| C2 D25 signflip_p ordering | 2.5 | any verdict depending on the MC signflip branch |
| C3 D28 registration TTL | 2.5 | long-lived registered services |

Build order is **G8, G1, G6, G5, G7, G2, G3, G4**, then conditionals. G8 first because without an `r8` row the
clock silently runs r7's 8 epochs instead of the ruled 12 -- see `BUILD_R8.md`. Rationale, by what each unblocks:

- **G1 first** because a silently refused row corrupts every downstream count -- the failure that produced D29.
- **G6 next** because section 4 is the first scientific obligation and its feasibility precommit emits
  WHY_NOT_RUN records; without `open_candidate()` every one of those needs a hand-written stub.
- **G5 then G7 together**: G5 captures the telemetry, G7 makes it durable. Either alone is close to useless --
  telemetry that ages out of a capped bus stream is not a breadcrumb.
- **G2** gates the anti-prior draws and the BETA sweep; **G3** covers shared-CPU fairness; **G4** is needed only
  at close.

**D27 is NO LONGER dropped** -- operator prompt 26 ("Yes, Do D27") promotes it to gate G6, superseding
prompt 24 section 2.5's permission to drop it and the conductor's own earlier recommendation (ADAPT-13).
**D26 remains dropped/conditional** and is not scheduled.

If a gate has not landed at gate time, its dependent science is refused at admission at zero CPU and the
refusal is recorded. That is a legitimate round-8 outcome, not a conductor decision.

---

## 4. FIRST SCIENTIFIC OBLIGATION: THE FOUR PENDING R16 CELLS

Until each of w1/w7/w10/w34 train128 is resolved by Route A or Route B, the standing statement is:

    74/74 sampled; 70/74 fully adjudicated; 4 PENDING

not "grid exhausted". The round-7 packet's "the grid is exhausted" phrasing is superseded by this rule.

### 4.1 MEASURED COST (from R16_LEARNER_PLAN_R7.json, not recalled)

Cost model, committed before round 7, a function of the plan's `t_x_s` field and the world only:

    cpu_s(cell, 32 runs) = (12030.94 / 32) * t_x_s = 375.97 * t_x_s

**LABEL WARNING for the future analyst (conductor correction, 2026-09-16).** `t_x_s` in
R16_LEARNER_PLAN_R7.json is the SCREENING CELL's train size, **not** the world's `T*S` from
`wforge.world.expand`. These are different quantities and an earlier draft of this section conflated them.
Computed: w13's world is `T=32, S=1, W=1` so its world `T*S` is **32**, while its `train128_held64` cell
records `t_x_s = 128`. The arithmetic below is unaffected -- it uses the plan file's own `t_x_s` values --
but the two must never be read as the same field.

| cell | t_x_s (train size) | plan estimate CPU-s | w26-measured scaling CPU-s |
|---|---|---|---|
| w1 train128  | 128 |  48,123.76 | 32,601.6 |
| w10 train128 | 128 |  48,123.76 | 32,601.6 |
| w7 train128  | 256 |  96,247.52 | 65,203.2 |
| w34 train128 | 256 |  96,247.52 | 65,203.2 |
| TOTAL        |     | **288,742.56** | **195,609.6** |

(The measured column scales w26's actual 509.4 CPU-s per learner run, which came in ~32% under its estimate.)

Structure per cell: 8 chunks x 4 runs + 1 assembly = 9 jobs, checkpointable, `wall_budget_s` 2400 per chunk.
**A cell decides nothing until all 8 chunks and the assembly complete.** Round 7 proved this: cells at 90%,
40%, 3% and 0% would all have expired UNSCREENED.

### 4.2 AGAINST ROUND-8 CAPACITY

Round-8 total CPU capacity for the **12 h** science clock (43,200 s), per prompt 25:

    at round 7's REALIZED sustained concurrency (7.25 threads):  313,200 CPU-s
    at a perfect 16 threads:                                     691,200 CPU-s

The four cells at plan estimate (288,743 CPU-s) are **92% of the realized-capacity budget** and 42% of the
perfect-parallelism budget. At the measured scaling (195,610) they are 62% and 28%.

Wall-clock for Route A on all four, if nothing else ran:

    at 16 threads:    18,046 s = 5.01 h  (plan est) | 12,226 s = 3.40 h (measured scaling)
    at 7.25 threads:  39,827 s = 11.06 h (plan est) | 26,981 s = 7.50 h (measured scaling)

**Conclusion (arithmetic, not preference): under the 12 h clock Route A for all four is now POSSIBLE but
not AFFORDABLE.** At round 7's realized concurrency it would consume 11.06 of the 12 science hours and leave
nothing for sections 5-11. The Route-B-first ordering below is therefore retained for scheduling reasons
rather than for impossibility. Establishing that a larger experiment is warranted remains a valid result and
is not authorisation to run it (operator section 0).

### 4.3 ORDER OF OPERATIONS [ADAPT-4]

1. **Route B first, for all four.** Derive a code bound: given the cell's already-committed measurements, is
   there any possible learner result that yields SURVIVED? If no, emit `SURVIVAL_IMPOSSIBLE` with the exact
   inequality. This is cheap, it is code-derived (never prose intuition), and it is the only path that can
   resolve all four inside this round. It also unblocks section 5 early.
2. **Route A only for cells the bound does not resolve**, in ascending cost (w1, w10, then w7, w34 -- the
   frozen cost-ascending rule, not outcome-ordered).
3. **[ADAPT-5] FEASIBILITY PRECOMMIT before starting any Route A cell.** Project completion at the measured
   sustained concurrency at that moment. Start the cell only if it completes before no-new-work with margin;
   otherwise emit `WHY_NOT_RUN` carrying the projection. Reason: a partially completed cell decides nothing
   and consumes capacity that could finish a cheaper cell. This is not dropping a cell for being expensive
   (prohibited) -- it is refusing to spend the round producing an undecidable fragment, with the number
   attached.

If any cell becomes SURVIVED, the replication trigger publishes immediately (code, not conductor). Never
reorder because a cell looks promising.

---

### 4.4 SCREENING COST IS NOT PREDICTABLE FROM WORLD PARAMETERS (computed for Q6/R11)

Measured over the 30 worlds that have BOTH a committed screening cost (48 `g-r16-cell-*` jobs, 130,307
CPU-s) and committed gate features. Learner chunks were excluded; folding them in inflates per-cell cost
by ~12%.

| candidate driver | pearson r | r (log-log) |
|---|---|---|
| n_gates | **-0.168** | -0.320 |
| T | 0.255 | 0.380 |
| gens / genomes | -0.178 | -0.217 |
| cells | -0.305 | -0.409 |
| qd_wall_s | 0.095 | 0.028 |
| screen_k | n/a (constant 64) | n/a |

No parameter explains cost, and `n_gates` -- the natural hypothesis -- is NEGATIVELY correlated. The
per-unit view shows why: w16 spends 10,664 CPU-s over 1,092 gates (9,766 CPU-s per 1k gates) while w31
spends 5,479 over 86,870 gates (63 per 1k). That is a **~500x spread in cost per gate, inversely related to
search size**: cheap-per-gate worlds are ones where search moves freely; expensive ones are where each gate
evaluation is itself costly. Cost is an emergent property of a world's difficulty and is discoverable only
by running it.

    cpu_s per 1k gates:  median 612.22  mean 2671.81  min 19.48  max 9765.93  (n=30)

**Therefore a fixed stratum N cannot be honestly costed before generation.** Sizing uses R11's
measure-then-size rule. Quoting the 2,222 CPU-s median per cell as a planning constant would be a real
number answering a different question -- the same class of error as the round-7 "4-core host".

CAVEAT recorded for the future analyst: **w13 was never screened in round 7** (it is the carried-over origin
cell), so there is no measured screening cost for the very world stratum L perturbs around.

---

## 5. NEW WORLD SET (conditional on section 4)

If w13 remains the only SURVIVED world, build a new **frozen** set in two preregistered strata:

- **STRATUM L -- local w13 neighbours.** Mechanical perturbation of w13's generator parameters into frozen
  distance bands (L1 minimal, L2 moderate, L3 larger but recognisably local). Coordinates and distances are
  defined BEFORE any outcome exists. Question: is w13 a point anomaly or part of a structured region?
- **STRATUM B -- background fresh seeds.** A smaller matched set from the original generator on untouched
  seeds, to estimate whether survivorship is enriched around w13 relative to background rarity.

No hand-selection after generation. No deleting ugly worlds. No outcome-dependent expansion this round.
No hand-designed worlds this round -- they encode a hypothesis and come later.

### 5.1 MEASURED: HOW A w13 NEIGHBOUR IS ACTUALLY BUILT (conductor survey, read-only)

A world is NOT a parameter vector. `E4.Spec(gen_seed)` calls `primordial.soup.b1.common.make_world`, which is
`expand(de_novo(GRAMMAR_VERSION, seed))` against **wforge**, a READ-ONLY production seat that Nestor must never
edit. GRAMMAR_VERSION = `wforge-grammar-0.1` and any frozen band rule MUST pin it.

`wforge.genome` already provides the mechanism stratum L needs, as a PUBLIC API requiring no edit to the seat:
`mutate(parent, op, op_seed)` returns a frozen DESCENDANT genome; the op is interpreted at EXPANSION time, so
the descendant genome alone reproduces the mutated world bit-for-bit. `parent_ids` carries lineage and
`world_id` is a content hash over the canonical serialisation including mutation history. This satisfies the
prompt-26 rerun requirement natively.

Seed adjacency is NOT world adjacency and must not be used: w13 is T=32 n=32 while w12 is T=256 n=512 and
w14 is T=128 n=128.

Measured on w13 (`Wf250db380cb2afd3`, T=32 S=1 W=1, n=32, lin_ops=4, corrupt_rate=16, obs_delay=0, SHORT):

| op | effect at distance 1 | size |
|---|---|---|
| PARAM_PERTURB | one scalar (yield_amt 10->9/8/13; start_charge at distance 2) | n=32 |
| PRIMITIVE_INSERT | lin_ops 4->5 | n=32 |
| PRIMITIVE_DELETE | lin_ops 4->3 | n=32 |
| REWIRE | act_targets [5]->[1]/[2]/[6]/[3] | n=32 |
| BUDGET_MUTATE | horizon 32->64 on 1 of 4 seeds, else NOTHING | n=32 or 64 |
| INTERFACE_MUTATE | corrupt_rate 16->0 AND obs_delay 0->2 AND horizon_class SHORT->MEDIUM, identical every seed | n=32 |

THREE CONSTRAINTS ON ANY BAND RULE:
1. The ops are NOT equal in magnitude. PARAM_PERTURB moves one scalar by +/-4; INTERFACE_MUTATE changes three
   observational properties at once. A band defined as bare mutation COUNT would call these equidistant.
2. SILENT MUTATIONS EXIST. PARAM_PERTURB seed 4 and BUDGET_MUTATE seeds 2-4 yield a DIFFERENT world_id with an
   IDENTICAL mechanism. A band rule must expand and DEDUPLICATE ON THE MECHANISM, never trust the genome id,
   or the same world is screened twice and counted as two points.
3. horizon_class is DERIVED, never authored, and shifts as a side effect. It is not an independent axis.

CONDUCTOR CORRECTION: an earlier conductor message reported w13 as corrupt_rate 0. It is **16** -- w13 already
corrupts observations, so INTERFACE_MUTATE switches corruption OFF while switching delay ON. That is a trade of
one observational difficulty for another, not a clean-to-noisy step.

**RULED BY THE OPERATOR (prompt 27) -- this is now ruling R13, not a proposal.** L1 = exactly one
PARAM_PERTURB / REWIRE / PRIMITIVE_INSERT / PRIMITIVE_DELETE (size-preserving, single-axis); BUDGET_MUTATE and
INTERFACE_MUTATE held to L2/L3 as LABELLED structural steps; mechanism-level dedup mandatory. The frozen,
reproduction-grade statement of the rule -- with w13's base mechanism, the per-op measured effects and the
dedup requirement -- is `LAUNCH_R8.md` section 6, which is the authoritative version for the builders.

**[ADAPT-6] Generation and screening are separately gated.** Generating and freezing the manifest is cheap
and is a round-9 de-risking artifact in its own right; screening is expensive. Freeze the set as soon as
section 4 resolves, then screen as much as the clock allows, with the unscreened remainder carrying
`WHY_NOT_RUN` and a measured size. Reason: it preserves the preregistration requirement (frozen before
outcomes) while preventing section 4 from starving section 5 of even its cheap half.

Screening uses existing R16 semantics unchanged. Explicit fields only: `runs_total`, `rng_family_count`,
`runs_per_family`. Never "32 x 4". A final SURVIVED must satisfy the full frozen production rule; any pilot
staging must be preregistered and conservative.

---

## 6. B-R5-1 REPLICATION AND INDEPENDENT FAILURE MODE

B-R5-1 (w13 train128_held64, 16-byte int4a4, progress 1.591, CI [1.139, 1.827]) remains CANDIDATE.

Replication runs the FROZEN recipe, untuned to the new world, frozen before the new-world result is read.
Evolving a new candidate is not replication. Required outputs: candidate score, world floor, float baseline,
progress-above-floor, observation-use control, exact oracle results, per-family results, equal-search-budget
accounting.

Promotion requires BOTH scientific displacement (a distinct eligible world not used to discover or tune the
candidate) AND instrumentation displacement.

**[ADAPT-7] The second host does not exist.** The operator's preferred path lists "preferably a second host
if available" -- this machine is a single 8-core/16-thread host with one GPU. Instrumentation displacement
must therefore be achieved by the other five means: frozen candidate bytes, fresh process, fresh worktree,
independently generated seed manifest, and an independently implemented or independently routed evaluator
against an exact reference implementation. The round must record explicitly: *if the original harness
contained a bug, how likely is the replication path to contain the same bug?* A second Claude lane is NOT an
independent failure mode and may not be claimed as one.

---

## 7. CLAUSE B: INVESTIGATE THE SHAM

No transfer matrix. The round-7 FAIL stands and is not relabelled; the hardened control did its job.

**H1 sham response curve.** Preregister multiple frozen sham strengths/forms: identity/no scramble; partial
feature permutation; full feature permutation; matched random replacement preserving gross scale; and at
least one further structure-destroying control that preserves nuisance statistics where possible. Ask
whether recipient performance varies systematically with destruction of donor structure. Outcomes: (A)
decreasing with destruction -- sham behaving as intended; (B) increasing -- the transfer machinery may be
measuring initialisation/regularisation/diversity rather than structure; (C) non-monotonic -- possible new
mechanism. None of these may be called "transfer" until a structural discriminator supports it.

**Calibration.** Carry the 0/40 planted-negative observation forward as an INTERVAL.
**[ADAPT-8]** The interval to report: one-sided 95% upper bound = 1 - 0.05^(1/40) = **7.2%**; the rule of
three gives ~7.5%. Report "false-PASS rate <= ~7.2% (95% one-sided), 0/40 observed", never "0%". If round 8
changes sham or control semantics, the CHANGED instrument is recalibrated before any live pair.

---

## 8. ANTI-PRIOR

Runs only after G2 is live. The predictor posts `P(PASS)`, expected direction, expected mechanism/failure,
timestamp and `predictor_id` BEFORE assignment. Scientific scoring ignores priors. Arm/rank/quantile/prior
are redacted from experimenter-readable records while the round is live (closing round 7's disclosure
channel by construction rather than by discipline). Code chooses assignments; no conductor hand-selection.

The draw includes both high-confidence predicted failures AND a smaller calibration sample from other
quantiles including predicted successes where available. The purpose is to measure predictor calibration,
not to accumulate surprise PASSes. At close, report binding-eligible candidate count, prediction
distribution, assigned ranks/quantiles, observed outcomes, and calibration descriptively. Small N stays
small N; no grand inference.

---

## 9. BETA SWEEP (PC 1789518268676-0) -- CONDITIONALLY AUTHORISED

Specific to AP-02. It does not resolve all anti-prior PASSes. Authorised only after G2 and G3 are live and
only if it can run without monopolising half the host at ~4% utilisation.

**[ADAPT-9]** If the LOW_UTIL/PREEMPTIBLE class does not land in BUILD without displacing G1/G2/G5, BETA runs
under the operator's own fallback: admitted only when a shared token would otherwise be idle. Reason:
section 19 prohibits scheduler engineering consuming the science window, and the fallback needs no new class.

Preregister beta values, stopping rule and primary response variables. Measure at minimum: beta, fraction of
possible charge actually paid, genome bytes, train fitness, held fitness, verdict. Do not tune BETA after
seeing the curve.

---

## 10. GPU

CPU remains the evolution backend. Do not re-benchmark GPU evolution. Permitted: (A) exactness investigation
of the 9/819,200 mismatches after C1 lands, by a lane other than the arbiter's host lane, with no speed claim
until exactness is understood; or (B) a clearly different workload shape (large QD/tensor/multi-cell batch),
still subject to the exactness gate and the speedup bar.

**[ADAPT-10 -- QUESTION, NOT A DECISION]** Operator section 13 reads "2. = 1.25x measured speedup". This is
preserved verbatim in the prompt file and is almost certainly ">= 1.25x", matching round 7's adoption rule.
The conductor will not interpret a threshold. See question Q1.

---

## 11. RETROSPECTIVE SIDE THREADS (cheap, run alongside)

- **H3 tie stability** -- re-evaluate historical verdicts under the tie-aware gate; count flips. Zero flips
  strengthens existing results; any flip is serious. Historical verdicts are never changed silently.
- **H4 saturation audit** -- for PASSes with stored trajectories, compare train vs held-out across generation
  count; classify as genuine improvement / held-out saturation / train-only overfitting / budget artifact.
- **H6 descriptor robustness** -- test historical QD coverage claims under at least one alternate descriptor
  family; a claim that reverses becomes DESCRIPTOR_DEPENDENT. No cherry-picking the descriptor that preserves
  the story.

These need little or no new simulation and are the natural companions to a compute-heavy main thread.

---

## 12. TELEMETRY (must land before the clock)

Minimum: token wait time per job; queue depth per lane per epoch; watcher liveness with explicit start/stop;
`WHY_NOT_RUN` record type; machine-readable `FINAL.json` per lane; predicate event id in every row.
Queue fields required by operator 2.2: `queue_enter_ts`, `grant_ts`, `wait_s`, `queue_position`,
`continuation` (bool).

If cheap: RSS/CPU/actual-thread-count every 30 s; host CPU/GPU/RAM every 60 s; per-generation timing for
evolution jobs.

**[ADAPT-11] Measure the telemetry overhead itself.** One calibration pair with sampling on and off, reported
as a percentage. Reason: the operator has explicitly accepted slower experiments in exchange for logging. To
keep that a decision rather than a hope, round 9 needs to know what it cost. This is residue about the
residue-gathering, and it is cheap.

Telemetry exists to answer future questions. Do not log merely because logging is easy.

---

## 13. COHORTS

- **B exploit/replication** -- B-R5-1 replication iff code publishes a valid second SURVIVED world; otherwise
  idle. Correct idleness is a result; do not invent substitute work.
- **C distant-QD / anti-prior** -- true anti-prior only from binding-eligible cells; optionally one
  distant-QD draw; no hand-selected redemption experiments.
- **D anomaly hunter** -- cheap minimum discriminators; BETA if admitted under the low-util class; GPU
  exactness if C1 landed; B-R5-1 residual anomalies. No open-ended campaigns.
- **E watchmaker / transfer instrument** -- sham-response experiment; changed-control calibration; required
  instrument fixes. No broad transfer matrix.
- **G world / screen execution** -- resolve the four PENDING cells (section 4); then the new frozen world
  screen if prerequisites hold.
- **H judge / replay / rule consistency** -- independent replay; rule consistency; the anti-prior binding
  pre-check; historical tie-stability if capacity exists.
- **R prior predictor** -- predict only, never experiment, never see outcomes before predictions seal.
- **A conductor** -- logistics only.

---

## 14. CONDUCTOR CORRECTION AND ERROR METABOLISM

Every lane emits machine-readable `FINAL.json`: receipts, row files, production candidates, why-not-run
records, unresolved claims, self-disclosed errors, disputes with A, interventions received, and jobs
started/completed/refused/paused/died. **A's packet is generated from these structured records plus
code-owned streams. Prose may explain; prose may not be the source of counts.** Where a lane disputes A's
characterisation, both statements are preserved; the dispute is never overwritten.

This exists because round 7 established that conductor summaries drift cleaner than reality: five of A's
characterisations were corrected by lanes and two more by the tally.

Error metabolism: DETECT -> DISCLOSE -> LOCALIZE -> REPAIR OR RETRACT -> PRESERVE LINEAGE. Self-disclosure is
evidence of institutional health. Do not reward trivial self-created bugs; do preserve the lineage. An error
is not erased because it was repaired.

---

## 15. INTERPRETATION RULES

HELD is a distinct scientific state and is never read as "almost SURVIVED" or as replication. Thresholds are
not relaxed because survivor density turned out to be low. The 5 HELD cells may be analysed descriptively for
sensitivity only; any future threshold change requires a new preregistered experiment.

---

## 16. RESOURCE BROKER

Instrument before adding concurrency. Record queue wait, grant duration, actual threads used, CPU
utilisation, checkpoint/preemption. The 1x16 vs 2x8 question is a BOUNDED capacity experiment only, run in
BUILD with a frozen criterion -- the existing concurrency latency rule is NOT relaxed inside the round
because throughput looks attractive. A low-utilisation resource class may be prototyped if it fits BUILD.
Scheduler engineering must not consume the science window.

---

## 17. OPERATOR RULINGS (prompt 25) AND THE QUESTIONS THEY ANSWER

Prompt 25: "Go with all recommendations you suggest. Allocate 12 hours of science. 2 hours of setup teardown
and 1 hour of iterative refinement. This conversation."

**RULINGS IN FORCE:**

| # | ruling |
|---|---|
| R1 | GPU adoption bar is **">= 1.25x"** measured speedup over the best practical CPU path. |
| R2 | **Route B first** for all four PENDING cells, then Route A in ascending cost behind the feasibility precommit (ADAPT-4, ADAPT-5). Sections 5-11 are preserved. |
| R3 | **Cap-anchored clock APPROVED** (ADAPT-2), now against the 15 h cap with a 12 h science clock. |
| R4 | **O-RESIDUE ADOPTED** at receipt time. `residue: NONE` is COUNTED in the close packet, NOT flagged for review -- flagging would invite lanes to write residue claims to avoid attention. |
| R5 | Perturbation bands L1/L2/L3 are chosen by **CODE, from a frozen rule published before generation**. No hand-picked coordinates. |
| R6 | **ANSWERED by R11 (measure-then-size); no fixed N is set.** Stratum sizes. The recommendation was "operator gives a number, or the conductor computes cost first". With R5 settled, A computes screening cost per world under the frozen rule and brings a number. A does not choose the sizes. |
| R7 | The new world set is **frozen regardless** of how section 4 resolves; only screening is clock-gated (ADAPT-6). |
| R8 | With no second host, the five-element instrumentation displacement is sufficient for a **CANDIDATE -> REPLICATED** step but **NOT for promotion**. Promotion waits for genuinely independent hardware. |
| R9 | Telemetry overhead ceiling **5%**, measured, with the measurement itself reported (ADAPT-11). |
| R10 | **SUPERSEDED by prompt 26: "Yes, Do D27."** D27 is promoted into the build as gate **G6**. D26 remains dropped/conditional. The conductor's retraction (ADAPT-13) is accepted. |
| R11 | **Q6 answered by computation (prompt 26 "Compute cost"), and the answer is that a fixed N cannot be costed in advance -- see section 4.4.** Stratum sizing uses the measure-then-size rule: freeze the L1 band, screen it, measure actual cost, let CODE size the remainder against remaining clock. |
| R12 | Archival sufficiency adopted (section 0.1): telemetry is write-only with respect to science (ADAPT-14), and the export gap is gate G7 (ADAPT-15). |
| R13 | **L-BAND RULED (prompt 27).** L1 = exactly one size-preserving single-axis op {PARAM_PERTURB, REWIRE, PRIMITIVE_INSERT, PRIMITIVE_DELETE}. BUDGET_MUTATE and INTERFACE_MUTATE are held to L2/L3 as LABELLED structural steps. **Mechanism-level deduplication is mandatory** -- silent mutations are measured and real. Full frozen rule in `LAUNCH_R8.md` section 6. |
| R14 | **G7 CONFIRMED (prompt 27) as export PLUS cursor.** The per-epoch export gains the job done stream and every telemetry stream, AND a per-stream cursor so each boundary writes only rows since the last one. Without the cursor, 12 boundaries x full re-dumps of growing telemetry is quadratic write amplification -- spending the authorised disk-IO budget on redundant copies instead of breadcrumbs. One full authoritative dump is still taken at close. |
| R15 | Launch is specified for REPRODUCTION in `LAUNCH_R8.md` (prompt 27): measured hardware, measured software versions, frozen seeds and start values, the launch sequence, the archival contract, and an explicit statement of what will NOT reproduce. |
| R16 | **R8 BUILD RULING (prompt 28).** Four build tracks run CONCURRENTLY under exclusive file ownership: F = G1->G6; P = G3->G5 hooks; Q = **G8 first** ->G7->G4; H = G2. Builders may NOT cross ownership boundaries to rescue another track. Missing hard gates cause machine refusal of dependent work and are never waived or repaired ad hoc after launch. **The gate map is the fail-safe, not the build strategy.** G prepares world-set machinery in non-colliding files only; E's conditionals run only where they do not threaten the critical path; conditional work always loses to the critical path. Principle: parallelism is safe when interfaces are shared but WRITABLE STATE is not. |
| R17 | **NO COMPRESSION OF BUILD+GATE (prompt 28).** Build <= 60 min and the FULL <= 20 min gate are preserved. The science clock is therefore approximately **11 h 40 min**, not 12 h, and that is ACCEPTED. Verification is never shortened, overlapped or weakened to protect a nominal 12.0 h clock. No cap extension follows from overrun; no hard gate is dropped to recover science time. **Gate output must report the NUMBER OF CHECKS EXECUTED, not merely PASS/FAIL.** |
| R18 | **UNKNOWN ROUND IDS FAIL CLOSED (prompt 28).** Adding the r8 row is not sufficient: `RC.plan(..., round_id="r9")` must RAISE/REFUSE until r9 is explicitly defined. A convenience fallback may remain for development utilities, but a production campaign clock never infers its identity. Tightens gate G8. |

**[ADAPT-13] A RETRACTS ITS OWN D26/D27 RECOMMENDATION.** The advice to drop them was reasoned from a
60-minute build window and a round whose product was verdicts. Under prompt 24's mission -- residue, failure
gradients, WHY_NOT_RUN records, measured costs attached to everything -- both are mission-relevant:
D26 is "attach the measured cost to the residue you left" (it blocked E from superseding a Clause B estimate
with the measured 8.61 h actual) and D27 is "file a record deliberately rather than as a side-effect of a
refusal" (it forced two hand-written stubs in round 7, and D27 is itself a candidate filed via the workaround
it describes). A recommends promoting **D27** into the build as gate G6, and leaving D26 conditional.
This requires an operator ruling because it reverses an approved recommendation; until ruled, R10 stands.

**QUESTIONS AS ORIGINALLY PUT (retained as the record):**

> NOTE: the figures inside Q2 below (a 182,700 CPU-s round budget, "158% of the round") were computed against
> prompt 24's **7 h** science clock and are SUPERSEDED by prompt 25's 12 h clock -- see section 4.2 for the
> current arithmetic (313,200 CPU-s realized-capacity budget; the four cells are 92% of it, not 158%). The
> question text is preserved unedited because it is the record of what was asked and answered, not a live
> statement of capacity.

Q1 **[BEFORE LAUNCH]** Section 13 adoption bar reads "= 1.25x". Confirm ">= 1.25x measured speedup over the
   best practical CPU path"? The conductor will not interpret a threshold.
Q2 **[BEFORE LAUNCH]** Section 4 arithmetic: the four PENDING cells are 288,743 CPU-s (plan) or ~195,610
   (measured scaling) against a 182,700 CPU-s round budget at round 7's realized concurrency. Confirm the
   Route-B-first ordering and the feasibility precommit (ADAPT-4, ADAPT-5)? If you would rather spend the
   entire round finishing cells by Route A and defer sections 5-11, that is a coherent alternative round and
   only you can choose it.
Q3 **[BEFORE LAUNCH]** Does the cap-anchored clock (ADAPT-2) have your approval, given it makes a build
   overrun consume science time automatically rather than requiring a conductor decision?
Q4 Is O-RESIDUE (ADAPT-1) adopted as a receipt-time requirement, and should a `residue: NONE` receipt be
   merely reported at close or actively flagged for review?
Q5 Section 5 requires distance bands L1/L2/L3 "defined before outcomes exist". Who defines the perturbation
   coordinates and band boundaries -- code by a frozen rule, or operator specification? The conductor should
   not choose them.
Q6 How many worlds in stratum L and stratum B? This sizes the only genuinely new science in the round and it
   is a preregistration decision, not a scheduling one.
Q7 If section 4 consumes the clock, should section 5 generation still proceed (ADAPT-6 says yes, because
   freezing the manifest is cheap)? Confirm.
Q8 Promotion definition: with no second host available (ADAPT-7), is the five-element instrumentation
   displacement sufficient for promotion, or does promotion wait for a genuinely independent host?
Q9 Section 12 accepts slower experiments for telemetry. Is there a ceiling -- e.g. reject any sampler whose
   measured overhead exceeds X%? Without one, "slower is acceptable" has no bound.
Q10 D26/D27 are explicitly droppable. Confirm they are dropped for round 8 rather than attempted.

---

## 18. SUCCESS CONDITIONS (operator section 20, adopted verbatim in substance)

1 four PENDING cells adjudicated or mathematically bounded away from SURVIVED; 2 frozen new world set with
local and background strata if w13 remains unique; 3 enough of it screened to judge local enrichment
plausibility or to size the follow-up; 4 B-R5-1 replicated iff a second valid SURVIVED world exists;
5 independent failure mode implemented as instrumentation displacement; 6 the sham advantage gets an aimed
discriminator; 7 anti-prior draws only from binding-eligible cells; 8 the predictor placed at genuine
calibration risk; 9 scheduling loses no continuations and starves no lane; 10 refused rows cannot coexist
with an ok job; 11 lane communication survives until DRAIN; 12 all drawn-but-unrun work carries structured
WHY_NOT_RUN; 13 no threshold weakened because the landscape is sparse; 14 nothing promoted for being
interesting; 15 the round ends on its own clock.

Scientific promotion is optional. Institutional honesty is mandatory.

---

## 19. PROHIBITIONS (operator section 21, in force)

Do not: call the grid exhausted while PENDING cells remain; drop PENDING cells as inconvenient absent a
bound; redefine HELD as replication; hand-design worlds after seeing perturbation outcomes; tune B-R5-1 to a
second world and call it replication; call another Claude lane an independent failure mode; run malformed
anti-prior cells; infer predictor miscalibration from non-discriminating cells; treat a vacuous PASS as
support; weaken the Clause B sham because it caused a FAIL; run a transfer matrix; re-benchmark GPU evolution
after a measured rejection; count 0/40 as proof of zero false positives; change resource rules after seeing
throughput; let an epoch boundary silently reorder scientific priority; let row refusal hide inside an ok job;
stop the communication channel before workers/shared services; use compute merely because time remains;
manufacture activity for an idle cohort; extend the round.

---

## 20. CLOSE

Per `POST_ROUND_FINAL_STEPS.md`, with the operator's section 22 packet structure: facts, interpretations and
proposals never mixed; sections 1-15 as specified. Before delivery: rederive every flattering count from
machine state, query hardware rather than recall it, verify every receipt, verify every row file is cited or
explicitly UNRECEIPTED_OBSERVATION, verify every prediction predates assignment, verify every new world was
frozen before outcomes, verify every threshold existed before the run, and preserve every lane dispute.
