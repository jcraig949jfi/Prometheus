# Vivarium notes — 2026-09-08 to 09-11

*Kept for combing, not for reading once. Incidents with their cost, the
patterns underneath them, and what actually changed. My own errors are in here
at the same weight as everyone else's; a post-mortem that only records other
seats' mistakes is a status report.*

---

## 1. Incidents, with what they cost

### I-1 · 48 phase-2 rows died on a fix that was already written
**Cost:** 48 rows, one campaign re-issue, ~6 hours of calendar.
**Date:** 09-10.

The consumer running phase 2 was PID 29884, started **07:29:23**. The fallback
it needed landed at **12:16:52** — 4h47m later. A running interpreter does not
pick up a file edit.

Two things had to be true at once, and both were:

1. I restarted that process in the morning *before* writing the fallback.
2. When the fallback landed I declined to restart, because a row was in flight
   and the only stop available was `taskkill /F`, which strands it.

Declining was right. **Not saying loudly enough that phase 2 must wait for a
restart was not.** Archaeon issued on a standing word that I had already
satisfied on main, and "it is on main" read as "it is running".

**Changed:** `viv.cli stop` (C4, `ab90609e5`) — a flag checked between ticks, so
a restart costs neither a stranded row nor a wait. Backlog C6 (record the
running SHA in the heartbeat) is still open and would have made the diagnosis a
single query instead of a traceback plus a process-start-time comparison.

### I-2 · I reported two engine defects that were one mistake of mine
**Cost:** a day of a peer's attention, a wrong finding in two reports.
**Date:** 09-10 → 09-11.

I put `refs` on the cost **event**. The engine checks and indexes
`resources[i].refs.artifact_digest` — `refs` is a field on the **resource
entry**. An event-level `refs` is sealed, echoed and never branched on.

So the mistake was silent **in both directions at once**: no refusal (there was
no claim to refuse) and no index entry (nothing to index). I read the two
symptoms as two engine defects, probed four combinations, and reported both
with confidence. Daedalus reproduced the opposite result and proposed the echo
as the discriminator. It resolved in one call: entry refs came back `{}`.

**The general shape:** *two independent-looking symptoms with a single cause
are more likely than two coincident defects, and "accepted but inert" is what a
dropped field looks like from the outside.* I had the evidence to see it — my
own probe printed the empty echo — and did not look at it, because the status
code said 200.

**Changed:** the receipt now keeps `refs_echoed` and an `indexed` boolean, and
the test asserts the **echo** rather than the acceptance (`7ee8d8045`).

### I-3 · 24 C3-hist rows lost to `null` vs `[null]`
**Cost:** an entire arm, 24 worlds, 24 PEW encounters, all terminal.
**Date:** 09-10. **Owner of the payload:** Archaeon. **Owner of the pattern:** me.

Archaeon sent `"ic_density_set": null` where the contract wants `[null]`. My
validator refused correctly, with a message that names the fix — **at execution
time**, after each row had created a world and a fossil, and a failed row is
terminal.

The kind contract validates **keys** exactly and **values** not at all. So a row
that can only ever fail is admitted, queued, claimed, given an engine world, and
then refused.

**Still open:** backlog D2, admission-time value validation. This is the
cheapest unbuilt thing in the file.

### I-4 · A live consumer read as DEAD
**Cost:** near-miss only — I nearly released a row that was executing.
**Date:** 09-10.

`_alive.py` reported PID 29884 dead with a stranded row. The process was fine;
that row completed in **227.19s**. The heartbeat only fires between stages, so
any row longer than the staleness window makes a working consumer look
stranded. Releasing such a row resolves it to `failed` and throws away a real
result.

**Still open:** backlog C1/C2/C3.

---

## 2. Where I was wrong, specifically

Kept separate because these are the combable ones.

| # | What I believed | What measurement said |
|---|---|---|
| W-1 | Seeding CEGIS constraints makes rejection cheaper. | It cut oracle calls everywhere, cut VM ops on fast targets, and **raised VM ops ~47%** on the target that scans its whole space. A constraint that does not fire is pure added cost paid by every survivor. Caught **before** it became a claim; the docstring said the wrong thing for about an hour. |
| W-2 | The component library helps H0's cells. | At `vm_op_cap=30000` it **solved maj3** (unreachable without it) and **lost xor3** (its extra leaves push xor3 further down the same enumeration). Both cells scored 5/6 and the aggregate contrast was zero *while both were moving*. |
| W-3 | Perturbing table entry 0 or 127 separates `at_T` from `stable`. | It does not. Once a uniform configuration stops being a fixed point the lattice never rests there, so `at_T` has already excluded those ICs. Measured both ways before writing it down. |
| W-4 | My dependency-cycle test constructed a cycle. | It asserted nothing. A content-addressed cycle is **unconstructible** — each hash is an input to the other's preimage. The test now establishes the impossibility and says the guard is defence in depth. |
| W-5 | The `by_artifact` index was broken. | See I-2. |
| W-6 | `maj` has a structural zero. | It scores 0.0 under both mask criteria and **0.5919** per-cell. The zero was a property of the criteria, not the rule — and the masks could not tell `maj` from a random table at all. |

**The pattern across W-1, W-2 and W-6:** *the plausible mechanism was right about
direction and wrong about sign or scope.* In each case the arithmetic was
available and cheap, and the first version of the write-up asserted the
plausible thing. What caught them was measuring the case I expected to be
boring.

---

## 3. Recurring patterns

**P-1 · Deployed is not live.** Hit three times in two days (I-1, then twice
more when a fix could not reach the running consumer). A commit on main, a
file on disk, and a running process are three different states. Anything that
reports "the fix is in" should name the *process*.

**P-2 · Aggregates hide the finding.** W-2: seven arms all at 5/6, and
underneath, one cell winning a task and losing another. I only saw it because I
printed the per-task matrix after the totals tied. **A tie in a small comparison
deserves the breakdown before it deserves a conclusion.**

**P-3 · Exact keys without exact values.** I-3. The contract's strictness
stopped at one level and the failure moved from admission to execution.

**P-4 · A dev build that lags production produces false negatives.** My dev
engine refused `refs` on a resource entry (`extra_forbidden`) because it
predated Daedalus's change. Useful this time — it surfaced as a recorded
`settle_error`, which is the first time that path fired in anger — but the same
lag would have hidden a real regression.

**P-5 · A stamped identifier is only true once something outside it confirms.**
I stamped a receipt with its own commit's SHA; an amend orphaned it before it
left the machine. Same family as the 08-31 cron rebase, reached from the other
direction: there the SHA moved under the file, here the file moved the SHA.

**P-6 · Peer disagreement is cheap and fast when both sides post evidence.**
Daedalus and I got opposite results on the same four probes. What resolved it
was neither of us re-arguing: they named a field (`resources[0].refs`) whose
value would distinguish the hypotheses, and it did, in one call. Worth
imitating — *ask what observation would tell us apart* rather than re-running
the disagreement at higher volume.

---

## 4. Measurements worth keeping

**Throughput, 09-10, from the register (not impressions):**

```
hour   n   total_s   executor_s   the kind itself
07:00  26     13.0        0.4          0.0
08:00  34     98.4        1.5          0.1
09:00  23    155.0        3.2          0.1
10:00  18    192.7        2.7          0.1   (max 1318s)
11:00  24    155.8        1.6          0.1
```

The science is **0.1s**. The row is **95–193s**. **98%+ is SFE round-trips.**
Individual writes measured 0.03–0.32s when free and **23.46s** when not,
minutes apart — bimodal, i.e. write-lock contention on the engine's SQLite,
not database growth. PEW health 0.06s throughout: not PEW. Onset was 08:00,
progressive, not a 10:00 step change as first reported.

**Process-tree kill, 09-11:** a Windows job object with `KILL_ON_JOB_CLOSE`
reaps a parent and a grandchild that forked before the kill. `taskkill /T`
races a fork and is best-effort by documentation. Evidence kept as
`vivarium/tools/probe_process_tree_kill.py`.

**Exact-symmetry null:** six genomes × three transforms — identical accuracy,
incorrect counts, witness ICs **and** mask digests. Not close: equal.

**Three criteria at campaign scale (149 cells, 320 steps):** the five
classifiers agree exactly between `at_T` and `cellwise`; `maj` is 0.0/0.0/0.5919;
random tables 0.4946/0.5037/0.5131 against a predicted interval around 0.5.

---

## 5. Environment facts that cost time

- **`wmic` is gone on this Windows build.** `Get-CimInstance Win32_Process` is
  the replacement. Cost: one confusing `FileNotFoundError` inside a probe.
- **`taskkill` kills the shell wrapper, not the `python.exe` child.** Verify
  with a process query and kill the real PID. (Already in seat memory; hit
  again.)
- **ctypes on Windows needs `restype` declared.** An untyped
  `GetCurrentProcess()` truncates the pseudo-handle into a 64-bit parameter and
  the call fails silently — peak memory read as `unavailable` until the
  signature was declared, then 13,373,440 bytes. **`unavailable` is the honest
  reading of a failed call, which is exactly why it must not be allowed to
  stand for a counter that works.**
- **The production engine was schema 7 while my dev build was 8**, then the
  reverse a day later. Read `/v2/version` rather than assuming either way.
- **The main checkout `F:\Prometheus` is parked on a stale branch**, which is
  why the consumer there predated everything. The consumer now runs from a
  `.claude/worktrees/` path that can be pruned. Backlog C5; operator's call.

---

## 6. Contract changes, and why each was said out loud

The `ca_density_v0` parity fixture was repinned **three times in one day**:
`transform` joining the contract, then F-20's flags, then the third criterion.
**The arithmetic never moved across any of them** — accuracy 0.875, witness
[6, 8] throughout. What changed was what the row *says about itself*.

That is the case for a whole-object digest: it makes a change in what is
recorded as visible as a change in what is computed. It is also the case
*against* absorbing such a change quietly, since three silent repins would have
looked like drift.

`SUCCESS_CRITERIA` was widened from two to three, and the test that asserts the
vocabulary is closed was updated deliberately rather than left to pass by
accident.

---

## 7. Open, ranked

1. **C1 / C2 / C3** — consumer observability. A status endpoint Archaeon can
   read instead of `ps`; heartbeat during a long row; distinguish "slow" from
   "gone". I-4 was a near-miss that these close.
2. **D2** — admission-time value validation. I-3 cost an arm.
3. **C5** — a durable home for the consumer. It runs from a prunable path.
4. **C6** — running SHA in the heartbeat. Would have made I-1 a one-query
   diagnosis.
5. **E1 / E2** — reconciliation: `by_artifact` now works (I-2 was mine), but the
   producer/executor stage vocabulary still differs (`transfer` vs `retrieval`)
   and that is Archaeon's word to pick, not mine.

## 8. What I would tell the next seat in this chair

The three failures that cost real work — I-1, I-2, I-3 — were none of them
science and none of them hard. They were: *a fix that was not running*, *a field
in the wrong object*, and *a validator that checked keys and not values*. The
loader, the sealed identities, the symmetry nulls and the criterion work all
behaved. **The expensive defects live in the seam between a correct thing and
the machine that is actually executing.**

---

## 9. I-5 — the frame reader was wrong a second time, and I nearly shipped it

Daedalus swept their ledger for experiments committed with no observation (119
of 3868), declined to classify them, and handed the verdict here: whether an
unclaimed QUEUED work item will ever be claimed is a fact about my register.
Their own first classifier had returned all five runs I had confirmed abandoned
as "pending", because each of those worlds still holds a queued work item
nobody will ever claim. **Holding work is not evidence of progress.**

Classifying them turned up three things I did not expect, in increasing order
of how much they should bother me.

**The frame reader was wrong again.** `_failing_call` exists because I once
reported all 13 lost h5 rows as dying at `create_world`, having matched
`http/client.py` with a pattern meant for sfclient. I fixed the path match. It
was *still* wrong: the five orphaned h5 rows have exactly one sfclient frame,
`_req`, sitting under `audit_envelope` in my own runner — and the function
preferred the client frame, so it answered `_req`. "An HTTP request." The frame
above it says the run had **already committed**. That is the entire question
the function exists to answer.

The same defect, twice, in the same twenty lines: *a name that is not the name
of what happened*. The first time the wrong name came from another library; the
second time it came from preferring a layer that cannot describe the operation.
What saved it was that the module's answer disagreed with an answer I had
already established by hand — I had written "4 at audit_envelope" in a message
to Archaeon days earlier, so when the tool said `_req` there was a contradiction
sitting in the repo. **Without that earlier written record I would have believed
the tool.** This is the argument for writing the by-hand answer down even when a
tool is about to replace it.

**Twenty-four of the thirty-three "abandoned" were not stall casualties at
all.** My first read of the breakdown was that `cs-c3-1` had lost 24 runs to
the engine, which would have made the 2026-09-11 stall a much larger event than
I reported. They died of `EXECUTOR_ERROR: ic_density_set must be a non-empty
list` — the kind refused the payload *after* the world and experiment were
committed. Committed-but-unobserved has at least two causes and the ledger
cannot distinguish them, because the cause is in my error text, not in
Daedalus's tables. Had I not checked the error before writing the report, I
would have sent two seats a stall that never happened. **The fact that a
scan finds a scar does not tell you what cut it.**

I also checked whether `cs-c3-1`'s 12/6/6 split across null/base/hist was an
arm-level asymmetry — the shape that turns into a fake effect. It is exactly
proportional to arm size (18/6/6). Checking took four minutes; reporting it
unchecked would have cost Archaeon a day.

**Seven orphans are mine and have no queue row at all.** The world name is
derived (`viv-<spec_hash[7:23]>`), so the engine records which orphans came out
of my runner regardless of whether a row ever sealed them. Seven `viv-` worlds
from 2026-09-06 — `evaluate_bitstring` and `noop_v0`, from v0 bring-up — match
no spec in my register, which holds 35 rows of those same two kinds. They were
executed straight against the engine with nothing behind them.

The tempting classification was NOT_FROM_THIS_REGISTER, which is even true in a
narrow sense: no row seals them. It would also have filed **my own
unaccountable writes under someone else's problem**, which is why they got
their own verdict. A classifier's categories are where you hide things from
yourself; the one category I did not want to exist is the one that had to.

The residual invariant is on the backlog: my runner can write to the ledger
with no register row behind it, producing an orphan **nobody** can adjudicate.
That is a worse property than the boundary-flag window I fixed yesterday, which
at least left a row that could be found.

### What I would tell the next seat, updated

Section 8 says the expensive defects live in the seam between a correct thing
and the machine executing it. I-5 adds the other half: **the expensive defects
in *analysis* live in the gap between a signal and its cause.** A scar, an
orphan, a contiguous gap, a 100% rate — each of those was a real measurement
that pointed at the wrong story until I read one more field. In all three cases
the extra field was already in the database.
