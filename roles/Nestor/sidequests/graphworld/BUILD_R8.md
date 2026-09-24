# BUILD_R8 -- GATE SPECIFICATIONS AND BUILDER ASSIGNMENT

Companion to `SWARM_R8.md` (rules, rulings R1-R15) and `LAUNCH_R8.md` (reproduction spec).
Build window target: **<= 60 min**, followed by a <= 20 min gate. The clock is CAP-ANCHORED: a build overrun
consumes SCIENCE time automatically (ADAPT-2), so the window is real, not advisory.

Every gate below has TESTABLE acceptance criteria. A gate is "landed" only when its tests pass in the launch
gate run, and admission refuses dependent work with `GATE_NOT_LANDED:<id>` at zero CPU otherwise. That is the
graceful-degradation mechanism: an over-subscribed build degrades by MACHINE REFUSAL, never by conductor
judgement.

---

## CRITICAL PATH WARNING (conductor, requires an operator decision)

The seven gates touch overlapping files. Serial time is roughly 145 minutes of work; the window is 60. That
only fits if the work runs in parallel AND no two builders edit the same file.

| gate | primary files | est |
|---|---|---|
| G1 vocabulary loud-fail + lint | `fabric/envelope.py`, rows emit path, gate lint | 15 min |
| G6 `open_candidate()` | `fabric/envelope.py` | 10 min |
| G5 telemetry minimum | `fabric/worker.py`, new telemetry module, FINAL.json schema | 25 min |
| G7 export + cursor | `ops/bus_export.py`, `ops/epoch.py` | 25 min |
| G2 cell-binding pre-check | `score/anti_prior.py` | 25 min |
| G3 scheduling cluster | `fabric/broker.py`, `fabric/worker.py` | 30 min |
| G4 close/watch protocol + lint | `ops/epoch.py`, protocol lint | 15 min |

**Collisions:** G1+G6 both edit `envelope.py`. G5+G3 both touch `worker.py`. G7+G4 both touch `epoch.py`.
So the parallel-safe grouping is four independent tracks, not seven:

    TRACK-1  envelope.py     G1 -> G6                       25 min
    TRACK-2  broker/worker   G3, then G5's worker hooks      30-40 min
    TRACK-3  ops/            G8 -> G7 -> G4                  50 min
    TRACK-4  anti_prior.py   G2                              25 min

**PHASE BUDGET: RULED (operator prompt 28).** Build 60 + gate 20 + teardown 60 = 140 min against a 120 min
setup/teardown allocation. **The ~20 min comes out of SCIENCE. The science clock is approximately 11 h 40 min
rather than 12 h, and this is ACCEPTED.**

**Do NOT shorten, overlap or weaken gate verification to preserve a nominal 12.0 h clock.** Twenty minutes of
science is almost irrelevant against the possibility of running eleven-plus hours behind a falsely green gate
-- and gate integrity is currently part of the experiment, having just failed in exactly that way during
launch prep (a shell quoting error silently deleted 2 of 12 checks and the gate still printed PASS).

No cap extension follows from a build overrun. No hard gate is dropped to recover science time.
**Gate output must report the NUMBER OF CHECKS ACTUALLY EXECUTED, not merely PASS/FAIL.**

Four tracks at ~40 min worst case fits the 60 min window **only if four builders run concurrently and each
owns its files exclusively**. Round 7 ran four builders (F, G, H, E) and its build took 52 minutes for a
smaller list.

## R8 BUILD RULING (operator prompt 28) -- IN FORCE

**Run the four build tracks CONCURRENTLY under the exclusive file ownership specified below. G8 is first
priority on Track 3.**

- **Builders may not cross ownership boundaries to rescue another track.** No conductor heroics, no
  cross-track emergency editing, no "just make this one fix".
- **Missing hard gates cause MACHINE REFUSAL of dependent work.** They are not waived, and they are not
  repaired ad hoc after launch.
- **The gate map is the FAIL-SAFE, not the build strategy.** Do not plan around it. Attempt the build.
- **G** may prepare the frozen world-set machinery in its non-colliding files, but must not interfere with the
  four tracks. **E's conditionals run only where they genuinely do not threaten the critical path.**
- **Conditional work loses to the critical path**, always.

Rationale, in the operator's terms: parallelism is safe when interfaces are shared but WRITABLE STATE is not.
The tracks are drawn on file ownership rather than task size for that reason, and it is the architectural
principle being adopted across the wider ecosystem -- not merely a scheduling convenience for this round.

---

## BUILDER ASSIGNMENT (strict file ownership; no two builders edit one file)

| builder | track | gates | exclusive files |
|---|---|---|---|
| **F** | TRACK-1 | G1, G6 | `primordial/fabric/envelope.py` |
| **P** | TRACK-2 | G3, G5 | `primordial/fabric/broker.py`, `primordial/fabric/worker.py`, telemetry module |
| **Q** | TRACK-3 | **G8**, G7, G4 | `primordial/ops/round_clock.py`, `primordial/ops/bus_export.py`, `primordial/ops/epoch.py` |
| **H** | TRACK-4 | G2 | `primordial/score/anti_prior.py` |
| **G** | (science prep) | L-band generator + frozen manifests | `primordial/metric/` world-set module |
| **E** | conditionals | C2, C3 | `score/signflip*`, `ops/residue.py` registration path |

G builds the world-set generator during the build window because stratum L is a prerequisite for its own
science, not a gate. E takes the conditionals because its round-7 work already touched both.

---

## G8 -- THE r8 ROUNDS ROW. HARD GATE. BLOCKS THE CLOCK ITSELF, THEREFORE EVERYTHING.

**Found during launch prep, not planned: this is a SILENT failure and it would not have announced itself.**

`primordial/ops/round_clock.py` has rows for r5, r6, r7 only, with `DEFAULT_ROUND = "r7"`, and `plan()` does
`ROUNDS.get(round_id, ROUNDS[DEFAULT_ROUND])`. Measured:

    RC.plan(start, round_id="r8")  ->  epochs 8, epoch_s 3600, total span 32400 s = 9.00 h

So starting r8 today runs **8 science hours, not the ruled 12**, with r7's `lane_repos`, and raises NOTHING.
This is the D18 shape exactly: a stale round definition producing confident, wrong behaviour.

**Lands:** an explicit `ROUNDS["r8"]` row.

    "r8": {"stage": "PRODUCTION", "epoch_s": 3600.0, "epochs": 12,
           "drain_s": 1800.0, "close_s": 1800.0,          # SWARM_R8 s1, operator prompt 25
           "lane_repos": {...}}                            # see below

**RECONCILE `epochs` WITH THE CAP -- do not leave this to inference.** Ruling R17 makes the science clock
approximately 11 h 40 min, not 12 h, but `plan()` computes `nnw = start_ts + epochs*epoch_s` and knows nothing
about the cap. Computed: build 60 + gate 20 + refine 60 = 2 h 20 m, so `science_start = T0 + 2h20m`, and
`min(science_start + 12 h, T0 + 15 h - 60 min) = T0 + 14 h`, i.e. **42,000 s = 11.67 epochs of 3600 s**.

Taking the row's `epochs: 12` literally would run the round PAST the cap. The row therefore holds the NOMINAL
value, and **the launcher computes the actual epoch count from the remaining cap at start time and passes it
explicitly** -- `plan()` already accepts `epochs` as an override. Acceptance: a test asserts that a launch at
`T0 + 2h20m` yields an `end_ts` at or before `T0 + 14 h`, and that no epoch boundary falls after it.

**`lane_repos` must be complete this time.** r7 declared only `B,C,D,E,G,R,gpu`; `A,F,H,P,Q` had none. Any
lane running a WORKER from an undeclared repo is FOREIGN_REPO residue (D14). Round 8 adds build lanes P and Q,
whose worktrees `nestor-bld-p` and `nestor-bld-q` already exist. Declare every lane that will run a worker --
including `gpu` if the arbiter starts at all.

**Acceptance:**
1. `RC.plan(t, round_id="r8")` returns `epochs == 12`, `epoch_s == 3600.0`, span `12*3600 + drain + close`.
2. A test asserts `"r8" in ROUNDS` -- i.e. the fallback is never what defines a live round.
3. `residue.allowed_repos(r, "r8")` resolves from `ROUNDS["r8"]["lane_repos"]`, source string names r8.
4. A test asserts every lane that will run a worker has a declared repo, so FOREIGN_REPO cannot fire on a
   legitimate lane.
5. **UNKNOWN ROUND IDS FAIL CLOSED (operator prompt 28, ruling R18).** A warning is NOT sufficient.
   `RC.plan(..., round_id="r9")` must RAISE/REFUSE until r9 is explicitly defined. A convenience fallback may
   remain for DEVELOPMENT utilities, but **a production campaign clock never infers its identity.** Silently
   substituting another round's clock and lane_repos is the defect; the missing row was only how it surfaced.
   A test asserts that an undefined round id raises, and that `DEFAULT_ROUND` cannot supply a live round's
   parameters.

**Assigned:** Q (owns `primordial/ops/`; `round_clock.py` does not collide with `epoch.py`/`bus_export.py`).
**Est:** 10 min. Build it FIRST -- gate numbering is historical, not priority.

## G1 -- ROW/EVIDENCE VOCABULARY LOUD-FAIL (D29). HARD GATE. BLOCKS ALL ROW-EMITTING SCIENCE.

**Lands:** a row rejected by the evidence vocabulary fails LOUDLY. A job may not return `ok` while its rows
are being refused. Refusal happens at emit/submit, not silently per row. A vocabulary lint runs in the gate.

**Why first:** in round 7 a lane's rows were refused one at a time while the JOB still reported `ok`, so the
rows were recoverable only as captured payloads. A silently refused row corrupts every downstream count, and
every count in the close packet rests on this.

**Acceptance (all testable):**
1. A job emitting a row with an invalid `status` or `evidence_class` ends with job status `error`, not `ok`.
2. The refusal names the offending value and the row index.
3. No alias is introduced -- `observation` is NOT silently mapped onto an existing status (A's round-7 ruling).
4. The gate's vocabulary lint fails on any status/evidence_class token not in the frozen vocabulary.
5. A regression test reproduces the round-7 shape: N rows refused, job status is NOT `ok`.

## G6 -- `envelope.open_candidate()` (D27). HARD GATE (operator prompt 26: "Yes, Do D27").

**Lands:** a code path that opens a PRODUCTION_CANDIDATE with NO refusal event.

**Context (measured):** `envelope.py:159` is the ONLY `xadd` to `CANDIDATES` in the entire codebase, and it
sits inside `refuse()` behind `if not stub: return`. So a candidate currently cannot exist without a refusal.
The stub dict is already fully constructed there; `open_candidate()` is an extraction of that block.

**Acceptance:**
1. `open_candidate(r, lane, question, basis, requested_cost=None, dependencies=None, experiment_class=None)`
   returns `{ok: True, stub_id}` with no refusal event written.
2. The stub appears in `open_candidates(r)` and carries a caller-supplied `source_event`.
3. `file_candidate()` still works against a stub opened this way (measured cost can be filed onto it).
4. A test asserts no `*_REFUSAL` event is emitted by the call.

## G5 -- TELEMETRY MINIMUM. HARD GATE for the round's own mission.

**Lands (minimum, operator s3):** token wait time per job; queue depth per lane per epoch; watcher liveness
with explicit start/stop; `WHY_NOT_RUN` record type; machine-readable `FINAL.json` per lane; predicate event
id in every row. Queue fields required by operator s2.2: `queue_enter_ts`, `grant_ts`, `wait_s`,
`queue_position`, `continuation` (bool).

**If cheap:** RSS/CPU/thread-count per job every 30 s; host CPU/GPU/RAM every 60 s; per-generation timing.

**Acceptance:**
1. Every done record carries the five queue fields.
2. `FINAL.json` validates against a committed schema: receipts, row files, candidates, why-not-run records,
   unresolved claims, self-disclosed errors, disputes with A, interventions received, job status counts.
3. Every emitted row carries the predicate event id.
4. **Measured telemetry overhead <= 5%** (ruling R9), from a calibration pair with sampling on and off, and
   the measurement itself is committed.
5. **ADAPT-14 respected:** no telemetry field is read by any eligibility check, control, discriminator or
   verdict. A test asserts the verdict path does not import or reference telemetry fields.

## G7 -- EXPORT + CURSOR (ADAPT-15, ruling R14). HARD GATE for archival sufficiency.

**Lands:** the per-epoch export covers the job done stream and every telemetry stream, AND each stream has a
per-epoch cursor so a boundary writes only rows since the previous boundary. One full authoritative dump is
still taken at close.

**Context (measured):** `bus_export.export()` calls `r.xrange(bus.SWARM)` etc. with NO start argument and
opens each file with `"w"`, so every boundary re-dumps each stream from the beginning. Round 7 wrote nine
near-identical swarm copies (1,295 / 1,296 / 1,303 rows). With 12 epochs plus per-job and host samplers, full
re-dumps are quadratic write amplification -- spending the authorised disk-IO budget on redundant copies.

**Acceptance:**
1. `pm:jobs:<L>:done` for every lane is exported to committed rows.
2. Epoch N's export contains ONLY rows with ids after epoch N-1's cursor.
3. The cursor state is itself durable (committed), so a reproduction can replay the exact partition.
4. The close produces one full dump per stream, and it is byte-identical to concatenating the per-epoch
   deltas in order (a test asserts this).
5. Round-7's failure is covered by a regression test: the conductor's cost analysis reads `pm:jobs:G:done`
   from Redis and must become reproducible from committed rows alone.

## G2 -- ANTI-PRIOR CELL-BINDING PRE-CHECK (PC 1789523009420-0). HARD GATE for all anti-prior draws and BETA.

**Lands:** a candidate cell enters the pool only if CODE verifies, before publication, that (1) the intended
pressure can bind on that world, (2) the discriminator has resolving power, (3) the oracle can fire, and
(4) the control can differ from the experimental arm in principle. Rejected cells are replaced by the next
seeded candidate. No LLM chooses replacements.

**Why:** all four round-7 assignments failed for CELL-CONSTRUCTION reasons, so the predictor's
confident-failure calls were never put at risk and the calibration question is untested after two rounds.

**Acceptance:**
1. A planted cell whose pressure cannot bind is REJECTED with a recorded reason.
2. A planted cell whose oracle can never fire is REJECTED (round 7 AP-01's meter needed a free-stream
   eligible episode that k=1 winners could never produce).
3. A planted cell with zero resolving power is REJECTED (round 7 AP-03: all 64 runs both arms returned
   exactly 31.71875, IQR 0.0).
4. The published list is reproducible from seed `20260921` alone, including replacements.
5. Rejection reasons are committed, so the rejected set is itself analysable residue.

## G3 -- SCHEDULING CLUSTER D15 + D22 + D30. HARD GATE for shared-CPU multi-lane science.

**Lands:** continuations retain priority across an epoch requeue; the longest-waiting eligible job cannot be
indefinitely starved by bursts of short jobs; drain constraints remain enforced; queue position cannot
silently convert scientific priority.

**Acceptance:**
1. A continuation requeued at an epoch boundary is granted before jobs submitted after it (D30 regression:
   round 7 stranded four nearly-finished cells behind 44 later learner jobs).
2. A starvation test: a burst of short jobs cannot delay the longest-waiting eligible job beyond a bounded
   wait (D22: a lane was starved ~7 min).
3. Non-checkpointable wall stays capped at 900 s (D15) and drain still completes.
4. The five queue telemetry fields are emitted for every grant.

## G4 -- CLOSE/WATCH PROTOCOL + LINT (D31). HARD GATE for close correctness.

**Lands:** a lane's ask/watch channel stays alive until DRAIN and is stopped AFTER workers. Shared
infrastructure may not be shut down without a current conductor confirmation record.

**Context:** D31 is the CONDUCTOR's defect. A's own close-sequence note told lanes to stop their watchers; a
lane complied and its gpuq arbiter exited ~1 min after a conductor ruling said to keep it. Measured deaf
window 683 s. It ended harmlessly by luck, not by a working channel.

**Acceptance:**
1. A protocol lint FAILS on any close sequence that stops the ask watch before workers or shared services.
2. Stopping a service listed as shared without a confirmation record is flagged by the residue or close sweep.
3. A lane's watcher emits explicit start and stop beacons (shared with G5).

## CONDITIONALS (operator s2.5 -- must not consume the window)

- **C1 D23** gpuq worktree isolation. Required BEFORE any cross-lane GPU work. Unassigned unless a track frees.
- **C2 D25** canonical ordering in `signflip_p`. Required before any verdict depending on that MC branch.
- **C3 D28** registration survives a job longer than its TTL (refresh must re-create a missing key).
- **D26** remains DROPPED (ruling R10). Note for the record: the fix is shallower than the conductor first
  estimated -- `file_candidate` refuses a second filing via `r.hsetnx(FILED, ...)`, so a filings LIST would
  suffice. Still dropped; recorded because the conductor's original cost estimate was wrong.

---

## GATE RUN (<= 20 min)

1. Full test suite green.
2. Discovered build tests: every test file added or modified in the build window runs.
3. Planted EVIDENCE_N_v1 refusals -- `16/1/16`, `32/4/(16,8,4,4)`, `32/4/(29,1,1,1)` -- all refused at
   admission with ZERO rows written.
4. G1's vocabulary lint and G4's protocol lint both run and pass.
5. Live residue scan clean; no stop flags; 0 registrations; conductor worktree clean.
6. Capacity profile present and readable by the broker.
7. The gate records the exact tip sha -- that sha, not any earlier one, is the reproduction anchor.
8. Gate->blocked-work map computed and published: any gate that did NOT land is recorded, and its dependent
   science is refused at admission for the whole round.
