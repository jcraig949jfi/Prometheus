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

    TRACK-1  envelope.py     G1 -> G6                     25 min
    TRACK-2  broker/worker   G3, then G5's worker hooks    30-40 min
    TRACK-3  epoch/export    G7 -> G4                     40 min
    TRACK-4  anti_prior.py   G2                           25 min

Four tracks at ~40 min worst case fits the 60 min window **only if four builders run concurrently and each
owns its files exclusively**. Round 7 ran four builders (F, G, H, E) and its build took 52 minutes for a
smaller list.

**OPERATOR DECISION REQUIRED:** either (a) run four build tracks with strict file ownership as assigned below,
accepting that G5's telemetry work is the likeliest item to overrun; or (b) accept that an overrun consumes
science clock via the cap-anchored rule and let the gate map refuse whatever did not land. The conductor will
not silently drop a gate to make the window fit.

---

## BUILDER ASSIGNMENT (strict file ownership; no two builders edit one file)

| builder | track | gates | exclusive files |
|---|---|---|---|
| **F** | TRACK-1 | G1, G6 | `primordial/fabric/envelope.py` |
| **P** | TRACK-2 | G3, G5 | `primordial/fabric/broker.py`, `primordial/fabric/worker.py`, telemetry module |
| **Q** | TRACK-3 | G7, G4 | `primordial/ops/bus_export.py`, `primordial/ops/epoch.py` |
| **H** | TRACK-4 | G2 | `primordial/score/anti_prior.py` |
| **G** | (science prep) | L-band generator + frozen manifests | `primordial/metric/` world-set module |
| **E** | conditionals | C2, C3 | `score/signflip*`, `ops/residue.py` registration path |

G builds the world-set generator during the build window because stratum L is a prerequisite for its own
science, not a gate. E takes the conditionals because its round-7 work already touched both.

---

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
