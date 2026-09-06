# VIVARIUM — selector/executor boundary review

Written 2026-09-05, after reading Harmonia S13/T-B, S14, S15, S17, S18 and
`roles/Archaeon/TODO.md` @ 251a78560. **Review document. No code changed.**

---

## 0. The governing principle, stated once

Harmonia T-B (`s13_corrections.json`, invariant VI):

> THE SYSTEM VERIFIES STATEMENTS INSIDE A SUPPLIED BOUNDARY AND CANNOT VERIFY
> THAT THE SUPPLIED BOUNDARY IS THE SCIENTIFICALLY RELEVANT ONE.

Vivarium is named in that invariant's instance list — *"attestation: the
executor supplies the execution boundary"*. Vivarium cannot escape being an
instance. What it can do is make the boundary it supplies **as narrow as
possible and mechanically forced rather than merely conventional.**

Harmonia S14's archaeology correction gives the operational form:

> spec_hash is a fixed point against an adversary who VARIES the spec, but not
> against one who makes every spec identical.

Since `spec_hash` is the substrate's grouping surface, and since S18 will
eventually compare a fossil-directed arm against a random arm, one rule
follows and it drives most of this review:

> **THE SEALED SPEC CONTAINS EXACTLY THE EXECUTION INPUTS. PROVENANCE LIVES
> OUTSIDE THE HASH.**

Anything in the spec that does not change what is executed is a channel by
which the selecting policy can leak into the sealed scientific record and
split the derived universe. Anything outside the spec that *does* change what
is executed is a hidden execution difference between arms. Both directions are
fatal to "the result is attributable to SELECTION".

---

## 1. Does Vivarium currently make selector choices?

**No decision that changes WHICH experiment runs.** Order is
`(priority, created_at)` with `not_before`, all supplied by the requester;
there is no reordering, no batching, no scoring, no retry, and no path from a
result to the next claim. On the letter of the question, the answer is clean.

**But there are four channels through which the selector can reach execution,
and one place where Vivarium supplies a scientific value.** These are the real
findings.

### F1 — the executor is handed the provenance (CONFIRMED)

`loop._execute` passes the whole queue row to `runner.run(row)`.
That row carries `created_by`, `source_reason`, `source_evidence`, `priority`,
`claimed_by`. Nothing reads them today. Nothing *prevents* reading them, and
under S18 `created_by` will literally be the policy label
(`A_random` vs `C_frozen_S17`).

An executor that can see which arm it is in is not a blinded apparatus, and
"we checked, it doesn't look" is not a property — it is a code review that has
to be repeated forever.

### F2 — three non-execution fields are inside the sealed hash (CONFIRMED)

Measured, against the current validator:

    notes            changes spec_hash: True
    experiment_kind  changes spec_hash: True
    world.name       changes spec_hash: True

None of the three changes what is executed. `notes` and `experiment_kind` are
free text that nothing consumes. `world.name` is passed to SFE verbatim, and
S14's own correction is that world names are author-supplied metadata *an
archaeologist is not entitled to trust* — Harmonia burned a result on exactly
that mistake.

So today: an arm label written into `experiment_kind` or a world name prefix
would (a) leak the policy into the sealed record and (b) give the two arms
different `spec_hash`es for otherwise identical science, which splits any
spec_hash-derived universe along the arm boundary. That is the worst possible
failure for S18-in-reality.

### F3 — Vivarium supplies a scientific parameter by default (CONFIRMED)

`viv/executors.py:55`

    ex = BitStringExecutor(length=int(inner.get("length", 24)))

`length` is not cosmetic. The engine derives the hidden target from
`sha256(f"target:{seed_root}:{length}")`, so:

    length 24 -> 101000000100110110011000
    length 32 -> 01000111100111101011010100011000

A spec that omits `length` is currently **accepted by validation** and then
silently run against a Vivarium-chosen landscape. This is precisely
"silently changing seeds, parameters, estimators". It is one line, and it is
the exact class of defect the seat exists to prevent.

More generally: `work.payload` is validated only as "an object". Its contents
are unvalidated, so *every* executor parameter is a potential silent default.

### F4 — the indeterminate branch is Vivarium's, not the requester's

`spec.apply_outcome_rule` returns `INCONCLUSIVE` when the rule's field is
absent from the result or the comparison raises. That behaviour is *correct*
(a missing measurement is not a negative one) but it is **Vivarium's choice,
applied under a condition the requester never anticipated**. Standing rule:
every pre-registered rule needs a declared INDETERMINATE branch. Here the
branch exists but Vivarium authored it.

### F5 — a single-field rule silently narrows a multi-metric result (S14/A3)

The rule names one field. If the executor returns five metrics, Vivarium
records an outcome as though one metric were the analysis, and the multiplicity
is invisible. This is S14 attack A3 (`adaptive_metric_choice`, all v6 checks
silent, conclusion false by construction), reproduced at Vivarium's seam. The
archaeologist's note there was *"all five metrics are in the observation
content, so the multiplicity is RECOVERABLE by counting keys, but nothing
declares it."*

---

## 2. Is a specification complete enough to execute without filling blanks?

**No — see F3.** `work.payload` has no per-kind contract, so completeness is
unenforced and the gap is closed by executor defaults.

The fix is not a general schema language. It is: each executor kind declares
the exact parameter names it consumes, beside the executor; validation requires
all of them and rejects any extra; executors are forbidden to use a default for
anything a result depends on. A missing parameter must be a *rejected
specification*, never a Vivarium-chosen value.

Second gap, smaller: nothing declares what the execution is *expected to
produce*. See F5 and the `result_contract` proposal in §9.

---

## 3. What must be frozen when the queue row is accepted?

Already frozen by the BEFORE UPDATE trigger, for the row's whole life:
`experiment_spec`, `spec_hash`, `created_at`, `created_by`, `source_reason`,
`source_evidence`. Terminal rows are frozen whole. That part is right and
should not change.

What is *missing* from the freeze is not a column but a **partition of the
row**:

    SEALED EXECUTION INPUTS   experiment_spec, spec_hash
        -> hashed, handed to the executor, sealed again by SFE at commit

    PROVENANCE                created_by, source_reason, source_evidence,
                              priority, not_before, request_key
        -> immutable, recorded, carried into PEW as producer metadata,
           and NEVER visible to the execution path

    EXECUTION RESULT          status, claimed_by, timestamps,
                              sfe_experiment_id, pew_reference,
                              result_summary, error
        -> written once, then frozen

Both halves are immutable today. The defect is that the boundary between the
first two is a convention rather than a type (F1) and is drawn in the wrong
place (F2).

---

## 4. Retries, crashes and partial executions

**Current behaviour is right in the large and wrong in one specific place.**

Right: Vivarium never retries. A failure is terminal and preserved. A stranded
row is left stranded and released only by an operator, always to `failed`,
never back to `queued`. `c.fail(..., retry=False)` is passed on executor error
so the *engine* does not re-enqueue either.

This matters more than it looked when I built it. Harmonia S15 classified
retry as the **only class A mechanism of the eight tested** —
`M5_retry_inside_engine`, `unavoidable_fossil: YES -- six worlds, six event
chains, six observations`. Retry is the one selection mechanism the substrate
*can* see. So a silent retry inside Vivarium would not merely be selection; it
would be selection that shows up in the fossil record as six experiments and
misleads any count. Refusing to retry is the correct posture and should be
written down as a standing invariant rather than left as an implementation
detail.

**Wrong (F6, CONFIRMED by inspection):** the SFE work lease.
`runner.run` claims with `lease_s=120.0` and never heartbeats it, and the
engine's work item carries `max_attempts: 3`. An execution longer than 120s
has its lease expire mid-run. The claim_id fencing token means the stale
attempt's `complete` is *rejected* — so nothing corrupt is written — but the
engine may re-enqueue the work, and Vivarium reports a confusing failure. The
minimum honest fix is to heartbeat the lease for the duration of the execution,
or to derive `lease_s` from a spec-declared execution budget and fail cleanly
at it. Today, a slow experiment is a partially-defined outcome.

**Representation.** Partial executions are already distinguishable without a
new state, and this is worth making explicit rather than adding states:

    status='failed' AND started_at IS NULL   -> NEVER ATTEMPTED
                                                (spec rejected while claimed)
    status='failed' AND started_at NOT NULL  -> ATTEMPTED, and sfe_experiment_id
                                                names where to look
    status IN ('claimed','running') and the worker is gone -> STRANDED,
                                                operator decides

`mark_running` writes `sfe_experiment_id` *before* any work is claimed, so even
a crash one millisecond later leaves the SFE identity attached to the row. That
is what makes the third case decidable by a human instead of guessable by a
machine.

---

## 5. Keeping every attempted execution visible

Visible in the **queue**: yes, already. Terminal rows are frozen, the event log
refuses UPDATE and DELETE, and `cancelled` is a permanent record that a
candidate was registered and not run.

Visible in the **fossil record**: **no, and this is the biggest hole.**

* A run whose spec declares no `pew` block produces no fossil at all. The
  execution exists in SFE and in the queue; PEW — the fossil record — never
  hears about it.
* A run that *fails* after reaching SFE produces no fossil either, because
  the PEW write only happens on the success path.

Under the stated architecture (PEW = fossil record) that is backwards: the
failures are exactly the executions an S18-style efficiency endpoint needs to
count. "Failures discovered per experiment executed" requires *executed* to be
countable from the fossil record.

PEW's live contract makes the fix cheap: `GET /api/v1/fossil/contract` reports
`required: [encounter_id, sfe_entry_hash, sfe_event_id]` — `players` is
**optional**, and `outcome` and `failure_class` are accepted fields. So a
player-less, failed execution is already expressible as a fossil encounter.
See §9 for the encounter_id question, which needs Mnemosyne's consent.

---

## 6. Preventing silent changes to seeds, parameters, estimators, stopping rules

Ranked by what is actually enforced today.

* **Seeds** — `world.seed_root` is required, typed, inside the hash, and passed
  through unchanged. Enforced. But it is the only seed: there is no separate
  execution seed, so an executor with internal randomness has nowhere to
  declare it. Fine for the two deterministic executors; a trap for the third.
* **Parameters** — NOT enforced. F3.
* **Estimators** — not expressible at all today. S15/M8 (`estimator_search_
  offline`) is class B and its stated minimal change is *"declare the estimator
  BEFORE the source set is readable"*. That is a spec field Vivarium does not
  have. Naming it now costs nothing and forecloses the informal version later.
* **Stopping rules** — not expressible, and correctly so for v0: a single work
  item has no stopping rule. The moment a spec can request N repetitions,
  a declared stopping rule becomes mandatory *before* that feature ships, not
  after. Record it as a precondition.
* **Reproducibility class** — the executor returns
  `BIT_DETERMINISTIC|SEMANTIC|PARTIAL|NONDETERMINISTIC` and Vivarium passes it
  through without checking it against anything. The spec should declare the
  expected class and a mismatch should fail. One comparison; the field already
  exists on both sides.

The general mechanism that covers all of these is already in place and is the
strongest thing in the current build: `attestation={"executed_config": spec}`,
which the engine re-hashes with the same canonicalization that produced
`spec_hash`. A faithful executor matches by construction. What that does *not*
cover is anything the executor consumes which is **not in the spec** — which is
exactly F3. Close F3 and the attestation becomes a real guarantee instead of a
tautology over an incomplete object.

---

## 7. Provenance: queue request -> execution -> PEW

Present today, and it works end to end (verified live, see the v0 deliverable):

    queue.experiment_id      -> queue.sfe_experiment_id  (written at mark_running)
                             -> queue.pew_reference      (written at completion)
    spec_hash                -> SFE sealed_spec_hash_in_ledger (checked, pre-execution)
                             -> PEW producer.spec_hash
    run_id = exp_id:work_id  -> PEW run_id
    anchor                   -> PEW sfe_event_id / sfe_entry_hash / sfe_event_seq
                                (OBSERVATION_RECORDED, so verify-anchor returns
                                 binds_exp_id and binds_obs_id)
    engine + session lineage -> PEW sfe_engine_instance_id, sfe_ledger_head_hash,
                                sfe_session_id, sfe_session_key_fp

Two gaps:

1. **The reverse direction is missing.** Nothing in SFE or PEW names the queue
   row. Given a fossil, an archaeologist cannot get back to the request, its
   `source_reason` or its `source_evidence` — so the fossil cannot say which
   policy proposed it, which is the one thing S18-in-reality must be able to
   answer. `experiment_id` and `request_key` belong in the PEW `producer`
   block, and the SFE spec must NOT carry them (they would enter the hash).
2. **Nothing links the queue row to the arm.** `created_by` /
   `source_evidence` hold it, and they never leave the queue. Same fix.

---

## 8. Can random-control and fossil-directed experiments share one path?

Today: **the same code path, but not a guaranteed-identical one.** The three
divergence channels are F1 (executor sees the policy), F2 (policy can be
written into hashed fields), and world naming.

The property that should hold, and that should be a test rather than a claim:

> Two queue rows whose `experiment_spec` is byte-identical and whose provenance
> differs arbitrarily must produce identical execution: the same `spec_hash`,
> the same sequence of SFE calls with the same arguments, the same
> `executed_config`, and world/hypothesis/prediction objects that differ in no
> field derived from anything but the spec.

That is directly testable with a recording fake client and it is cheap. Once it
exists, "attributable to selection" stops being an architectural intention and
becomes a regression test.

---

## 9. Duplicate / idempotent execution: does it need an explicit contract?

**Yes, and there is none today.** Two queue rows carrying the same
`experiment_spec` both execute, producing two SFE experiments with the same
sealed `spec_hash` in different worlds. Nothing distinguishes:

* a deliberate **replication** (legitimate, must remain possible),
* an accidental **double submission** by Archaeon (must be refused),
* a **resubmission after a crash** where it is unknown whether the first ran.

All three look identical in the queue and identical in the fossil record. Under
S14/A5-style scrutiny they are also how an accidental multiplicity gets built.

Proposed contract, one column and one index:

* `request_key text` — supplied by the requester, `UNIQUE`. The same key is the
  same request: a resubmission is refused, idempotently. A deliberate
  replication supplies a new key.
* `replication_of uuid REFERENCES ...` — a repeat must *say* it is a repeat.
  When set, Vivarium passes SFE's existing `replication=True` on the
  observation, so the engine records a retest that never re-adjudicates the
  original (SFE F3) rather than a second independent result.

This keeps replication possible, makes it declared, and makes the accident
impossible — without Vivarium deciding anything.

---

## 10. Minimum state machine

**The six states are already minimal, and the right move is to add none.**

    queued  -> claimed | cancelled
    claimed -> running | failed
    running -> completed | failed
    completed / failed / cancelled -> nothing

Justification for each, since "minimum" was the question:

* `queued` / `cancelled` — a candidate that was registered and not run is the
  only class-A trace of a selection decision anywhere in the architecture
  (see §11). Cancelled must be terminal and permanent, not a delete.
* `claimed` vs `running` — **these cannot be merged.** The transition is the
  boundary between "certainly never executed" and "may have executed", and it
  is the only thing that makes crash recovery decidable without guessing.
  Merging them forces the operator to guess, and the guess is what double-runs
  science.
* `completed` / `failed` — terminal, frozen whole, no retry.

The temptation to add a seventh state (`rejected`, for a spec that failed
validation) should be resisted: `status='failed' AND started_at IS NULL`
already decides it exactly, and a state you can compute is a state you should
not store. Publish it as a view, not a status.

The one structural thing worth keeping in mind: `active_singleton` enforces one
execution globally *in the database*. When Archaeon's cadence machinery merges
onto this table, that index must survive the merge.

---

## 11. Out of scope for Vivarium, but Archaeon should hear it

S15 found seven of eight selection mechanisms are **class B — information-
theoretically absent from the substrate.** Their listed minimal changes are all
the same shape:

    M1 seed shopping      "require every candidate seed to be REGISTERED before any is run"
    M2 config search      "declare the search space before the run"
    M3 policy search      "register candidate policy hashes before evaluation"
    M4 candidate batching "the executor must attest how many candidates it produced"
    M8 estimator search   "declare the estimator BEFORE the source set is readable"

**The queue is the only pre-execution register in the whole architecture.** It
is the one object written before anything runs, immutable once accepted, with
an append-only event log and a permanent `cancelled` terminal state. If
Archaeon writes its *candidate set* to the queue and cancels the unchosen —
rather than writing only the survivor — then M1–M4 become class A at the queue,
which nothing else in the system can do.

That is Archaeon's design decision and Vivarium must not require it. Vivarium's
only contribution is to keep the queue a faithful pre-execution register, which
it already is. Worth telling them; M4 in particular ("the executor must attest
how many candidates it produced") would otherwise land on Vivarium as a
requirement it cannot honestly meet — Vivarium sees one candidate by
construction, and should say so rather than attest to a number it cannot know.

---

## 12. Proposed iteration, tiered

**TIER 0 — blocking, not Vivarium's call alone.**
Resolve the queue seam. `roles/Archaeon/TODO.md` records two live tables
(`archaeon.experiment_queue`, `viv.research_experiment_queue`), Archaeon's
proposals going nowhere, and Archaeon's own recommendation: keep Vivarium's
table and move the cadence mechanism onto it. I agree with that direction —
cadence is a property of *writing* to the queue — but it changes another seat's
live schema and needs the operator's decision, not mine.

**TIER 1 — the boundary. This is the proposed smallest iteration.**
Self-contained, no new subsystems, roughly a day's work, all inside `vivarium/`.

1. **`ExecutionRequest`.** The runner receives a frozen
   `(experiment_id, spec, spec_hash)` and nothing else. Provenance becomes
   structurally unreachable from the execution path. (F1)
2. **The hash covers exactly the execution inputs.** Drop `notes`; drop
   `experiment_kind` or close its vocabulary; remove `world.name` from the spec
   and derive it as `viv-<spec_hash[7:23]>`. Policy labels then have nowhere to
   live except provenance, which is where they belong. (F2)
3. **No defaults, anywhere.** Each executor kind declares the exact parameters
   it consumes; validation requires all of them and rejects extras; no
   `.get(k, default)` for any value a result depends on. (F3)
4. **`outcome_rule.if_indeterminate` becomes required.** The indeterminate
   branch is declared by the requester, never authored by Vivarium. (F4)
5. **Idempotency contract:** `request_key` unique, `replication_of` declared,
   SFE `replication=True` passed through. (§9)
6. **Fossilize every attempted execution, including failures** —
   `outcome`/`failure_class` on the encounter, with `experiment_id` and
   `request_key` in the `producer` block so the fossil points back at the
   request. (§5, §7)
7. **The blinding test:** identical spec + arbitrary provenance ⇒ identical
   execution, asserted against a recording fake client. (§8)

**TIER 2 — recommended, separable, one needs another seat's consent.**

8. `result_contract`: declare the full expected result key set before the run;
   a mismatch fails visibly. Closes S14/A3 at this seam. (F5)
9. PEW encounter for *every* execution, with `encounter_id` derived from
   `spec_hash` when the requester supplies no Proteus encounter identity.
   **Needs Mnemosyne's sign-off** — it introduces a naming convention into
   their record.
10. Heartbeat the SFE work lease for the duration of execution. (F6)
11. Declared reproducibility class, checked against what the executor reports.
12. Name `estimator` and `stopping_rule` as spec fields now — even if v0 only
    accepts `null` — so the informal version can never appear later. (§6)

**TIER 3 — state it, do not build it.**

13. Tell Archaeon about §11: the queue can convert class-B selection to class A
    if the candidate set is registered, and Vivarium will not attest to a
    candidate count it cannot see.

**Explicitly NOT proposed:** no scheduler, no optimizer, no planner, no retry
policy, no result-dependent behaviour of any kind. Every item above either
removes a choice from Vivarium or forces a choice to be declared by the
requester.
