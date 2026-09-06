# VIVARIUM — Tier 0 + Tier 1 report

2026-09-06. Implementing the approved invariant:

> **The sealed spec contains exactly the execution inputs.
> Provenance lives outside the hash.**

Evidence: `roles/Vivarium/TEST_RESULTS_TIER1_2026-09-06.txt`
(82 Vivarium tests, 108 Archaeon tests, all against real PostgreSQL and — where
reachable — the live engine and the live fossil service).

---

## 0. Coordination: Archaeon had already built Tier 0

Before writing anything I read `roles/Archaeon/TODO.md` @ 251a78560 and found
Archaeon had independently done the merge the same day, in
`archaeon/migrations/003_adopt_vivarium_queue.sql`, and **applied it live**.
The two designs converged on the same contract — identical column names,
constraint names, index names, the same `candidate_sets` view, the same
extension of the freeze trigger.

Their design was better than mine in one place I had got wrong, and I adopted
theirs: **`cadence_day_ordinal` is NULL for registered-but-cancelled
candidates**, so registering twenty candidates does not consume twenty of the
six daily slots. My version keyed the ordinal requirement on `source_reason`,
which would have made candidate registration unaffordable and killed the
class-B→class-A conversion before it was used.

Resolution: Vivarium's migration is authoritative (it owns the table and it is
`{schema}`-parameterised, so tests can apply the identical DDL to a throwaway
schema); Archaeon's 003 was reduced by them to the retirement note in their own
schema. Two corrections were needed to move it, both mechanical:

* constraint-existence guards keyed on `conname` alone were tested globally, so
  applied to a second schema the guard found production's constraint and
  silently skipped creating the test schema's. Now keyed on
  `(conname, conrelid)`.
* `CREATE OR REPLACE VIEW` cannot add or drop a column; `DROP VIEW IF EXISTS`
  + `CREATE VIEW`.

---

## 1. Final queue/schema changes

`viv.research_experiment_queue`, additive only. Every column below is
PROVENANCE: frozen, recorded, never hashed, never reachable from the executor.

    IDENTITY   request_key text UNIQUE (partial, WHERE NOT NULL)
               replication_of uuid REFERENCES ...(experiment_id)
                 + req_replication_not_self CHECK (<> experiment_id)
    RELATION   family_id text
               arm_id text          + req_arm_needs_family CHECK
               candidate_set_id text
    CADENCE    cadence_lane text
               cadence_day_ordinal int   (0..5, NULL = consumes no quota)
               cadence_utc_day date GENERATED ALWAYS AS
                                    ((created_at AT TIME ZONE 'UTC')::date)
               uq_req_cadence_day_ordinal UNIQUE
                   (cadence_lane, cadence_utc_day, cadence_day_ordinal)
                   WHERE cadence_day_ordinal IS NOT NULL

Two views, both DERIVED, nothing stored:

    viv.execution_attempts   crossed_execution_boundary, rejected_before_execution,
                             failed_during_execution, holding_the_slot
    viv.candidate_sets       registered / cancelled / retained / executed,
                             first and last registration timestamp, registrars

`viv.enforce_queue_transition()` extended: the relation declaration
(`family_id`, `arm_id`, `replication_of`, `candidate_set_id`, `request_key`,
`cadence_lane`, `cadence_day_ordinal`) is now immutable for the row's whole
life, alongside the spec and the original provenance. **A comparison cannot be
re-drawn after its outcomes are visible.**

`archaeon.experiment_queue` is RETIRED — commented, readable, not dropped (it
holds one real never-executed proposal, and deleting a pre-execution register
to tidy an architecture is the erasure S15 classes as an unobservable selection
mechanism). `archaeon.queue.enqueue()` now **raises `QueueRetired`** naming its
replacement, so no code path can write a second live queue. Regression test:
`archaeon/tests/test_cadence.py::test_the_retired_writer_refuses`.

Cadence gate and decision log stay in the `archaeon` schema — they are
Archaeon's audit surface, not the queue's.

---

## 2. The exact sealed-spec boundary

    {
      "spec_version": 2,
      "world":        {"seed_root": <int>},
      "hypothesis":   <non-empty string>,
      "prediction":   <object> | null,     <- explicit null, never omitted
      "work":         {"kind": <registered kind>, "payload": {...exact...}},
      "outcome_rule": {field, op, value, if_true, if_false,
                       if_indeterminate} | null,
      "pew":          {encounter_id, players, world_binding_id?, required?,
                       producer?} | null
    }

Closed key set. Explicit `null` is required rather than omission for
`prediction`, `outcome_rule` and `pew`: an omitted field and a declared absence
are different experiments, and only one of them was requested.

The world name is **derived**: `viv-<spec_hash[7:23]>`. Two arms running
byte-identical specs therefore produce byte-identical world names.

---

## 3. Fields removed from / added to spec_hash

REMOVED (each measured to change `spec_hash` without changing execution):

    notes             free text, read by nothing
    experiment_kind   free text, read by nothing
    world.name        author-supplied metadata; S14 burned a result on
                      trusting one. Now derived from spec_hash.

Also now **refused with a reason naming the offender**, not merely as "unknown
key": `family_id`, `family`, `arm_id`, `arm`, `candidate_set_id`,
`replication_of`, `request_key`, `policy`, `created_by`, `source_reason`,
`source_evidence`, and `spec_hash` itself (a hash may not live inside the
object it hashes — with it embedded, Archaeon's value could never have equalled
the `content_hash` SFE seals at commit).

ADDED to the hash: nothing. `outcome_rule.if_indeterminate` is a new required
sub-field of an already-hashed object.

The same rule is enforced on both sides of the seam:
`viv/spec.py::_BANISHED` and `archaeon/vivqueue.py::FORBIDDEN_SPEC_KEYS`.
Archaeon's `propose.build_spec` and `explore.build_spec` no longer embed the
`archaeon{detector, intent, chart, policy, seed, candidate_set_hash}` block or
`spec_hash`; the policy metadata is returned by `probe_provenance()` /
`exploration_policy_provenance()` and rides in `source_evidence`, a column.

**Canonicalization is now single-sourced.** `archaeon/vivqueue._spec_hash` had
its own copy that omitted `ensure_ascii=False`, so any spec containing a
non-ASCII character (a hypothesis with an accent was enough) hashed differently
from what SFE seals — silently, and only sometimes. It now imports
`viv.spec.spec_hash`, and `tests/test_spec.py` asserts that against
`sfe.ids.content_hash`.

---

## 4. Validation and default removal

`viv/kinds.py` is a registry: one entry per execution kind, declaring the
**exact** parameter set (not a minimum), whether an executor exists here, and
which seat owns the entry.

    noop_v0             IMPLEMENTED  vivarium   params: (none)
    evaluate_bitstring  IMPLEMENTED  vivarium   params: bits, length
    archaeon.probe.v0   external     archaeon   params: procedure, probe_kind,
                                                replicates, worlds, players,
                                                target, hold_fixed, controls
                                                [PROVISIONAL — see §11]

Validation rejects a missing parameter AND an extra one. No executor may
default anything: `int(inner.get("length", 24))` is gone, and `length` is a
scientific parameter — the engine derives the hidden target from
`sha256("target:<seed_root>:<length>")`, so 24 and 32 are different landscapes.
`executors._params()` re-checks the contract at execution as defence in depth.

`outcome_rule.if_indeterminate` is required, and `apply_outcome_rule` **raises**
rather than defaulting if called on a spec without a rule. An executable kind
must declare a rule at all, because SFE records an outcome for every
observation and Vivarium will not author one.

`implemented=False` kinds are **admissible but not runnable**: the queue is a
register and a candidate need not be executable today. Executing one raises
`EXECUTOR_NOT_IMPLEMENTED`, terminal and named.

---

## 5. Idempotency and replication semantics

* `request_key` UNIQUE. Enqueueing a key that exists raises `DuplicateRequest`
  naming the existing `experiment_id` and its status — including when that
  status is `completed`. A concurrent race on the same key resolves to the same
  refusal, not a crash.
* A deliberate replication is a **different request**: a new `request_key` plus
  `replication_of` naming an existing row. Self-reference is refused by CHECK;
  a dangling target is refused before insert.
* Two rows may share a `spec_hash` — replication must remain possible. Only the
  accident is foreclosed.

**Deviation from the instruction, stated plainly.** The brief asked that
replication "propagate through the existing SFE replication semantics".
It does not, and should not: SFE's `replication` flag is scoped to one world
and experiment (`is_repeat` keys on `world_id + exp_id`, runtime.py:1773) and
Vivarium always creates a fresh world. Passing it would be a no-op that reads
like a guarantee, and it would simultaneously disarm SFE's F3 refusal of an
accidental second observation of the same experiment. The relation is recorded
where it is load-bearing instead: the frozen `replication_of` column, and the
PEW producer block. PEW's own `(encounter_id, run_id)` model already expresses
"one specification, many runs" natively. **If you want the flag passed anyway,
say so and it is one line.**

---

## 6. Failure fossilization

A run that **crossed the execution boundary** (reached `running`, i.e. its SFE
experiment was committed) is fossilized even when it fails. The fossil:

* anchors on `EXPERIMENT_COMMITTED`, which binds `exp_id`, so `verify-anchor`
  can confirm the experiment really was committed — it attests that execution
  was *attempted*;
* carries `failure_class` (`EXECUTOR_ERROR`, `WORK_NOT_CLAIMABLE`,
  `EXECUTOR_NOT_IMPLEMENTED`) and `resources_used.attempted = true`;
* carries **no `outcome`** unless a work item actually reached a terminal
  status. Absence of a result is recorded as absence. The outcome rule is not
  run.

A run that never crossed the boundary (spec rejected while `claimed`) is
fossilized nowhere, correctly: nothing was executed.

A spec declaring `pew: null` is still fossilized nowhere. Making PEW mandatory
for every execution is Tier 2 item 9 and remains deferred.

Tests: `test_relations.py::test_a_failed_execution_is_fossilized_without_
inventing_a_result` asserts `"outcome" not in enc`.

---

## 7. Candidate registration and cancellation

Representable, **never mandatory**. A candidate set is N rows sharing
`candidate_set_id`; the unchosen are moved to the terminal `cancelled` state,
never deleted. `archaeon.vivqueue.submit()` registers the set and selects one
in ONE transaction, so a set registered across several transactions cannot be
presented as a complete one. A single-candidate set is legal and is an honest
statement that one candidate was considered.

**There is no `candidate_set_size` column, and there will not be one.**
`viv.candidate_sets` counts the rows the register actually holds. A stored
count is an attestation and can be wrong; a derived count is the register
counting itself. Vivarium is handed one candidate by construction and will not
attest a number it never saw — which also means it declines S15's stated
"minimal change to move M4 to class A" ("the executor must attest how many
candidates it produced"). That obligation cannot land here honestly.
Regression test: `test_vivarium_reports_no_count_it_did_not_observe` asserts no
such column exists.

---

## 8. The Archaeon relation-metadata contract

Agreed and in force on both sides:

* **Columns, never spec:** `family_id`, `arm_id`, `replication_of`,
  `candidate_set_id`, `request_key`, plus `created_by`, `source_reason`,
  `source_evidence`. All frozen at admission.
* **`arm_id` requires `family_id`** (CHECK + Python guard).
* Two rows in different arms **may and must be able to** carry byte-identical
  specs.
* Archaeon's writer refuses a spec carrying any of them
  (`RelationContractViolation`), and Vivarium's validator refuses the same set
  independently. Neither side relies on the other being correct.
* Policy metadata (which detector fired, the exploration seed, the candidate
  set hash) belongs in `source_evidence`.

---

## 9. Blinding-test result

`vivarium/tests/test_blinding.py` — 15 tests, all passing. It establishes the
stronger claim, not "the executor currently ignores provenance":

**Provenance cannot reach the executor.**
* `ExecutionRequest` has exactly three fields —
  `(experiment_id, spec_json, spec_hash)` — asserted against
  `dataclasses.fields`, so widening it is a visible act.
* `from_queue_row` names exactly those three; a marker string planted in
  `created_by`, `source_reason`, `source_evidence`, `family_id`, `arm_id`,
  `candidate_set_id` and `request_key` appears nowhere in the request.
* `runner.run()` raises `TypeError` on a dict, a queue row, `None` or an int —
  it is not duck-typed.
* The request is self-verifying: a tampered spec cannot be constructed at all.
* **The transcript test.** Two rows, byte-identical specs, opposite arms
  (`A_random` vs `C_frozen_S17`), different `created_by`, `source_reason`,
  `source_evidence`, `candidate_set_id`, `request_key` → the recorded SFE call
  sequence is *equal*, and a planted marker appears nowhere in the traffic.

**A real execution input must change execution identity.** Parameterised over
`seed_root`, `bits`, `length`, `hypothesis`, `outcome_rule`, `prediction` and
`work.kind`: each changes `spec_hash` AND the derived world name, and a payload
change changes the transcript.

**Live confirmation** (`demo_family.py`, run against the real engine and the
real fossil service, family `demo-family-7342e0ac`):

    distinct spec_hash across arms : 1
    sealed hash    sha256:b2dcae6a3702b82aa70dbd4abd85c4ecad525abd6c420a605d757e7076a32150
    derived world  viv-b2dcae6a3702b82a          (identical in both arms)
    arm A_random       completed  exp_194daf1822a8b6698ebe094b
    arm C_frozen_S17   completed  exp_0c4a2aecbee88146c5534f53
    arm/family in the SFE audit envelope : ABSENT   (both arms)
    both arms: identical sealed hash, identical world NAME, DIFFERENT world ids
    both fossilized under encounter enc_demo_family_7342e0ac

Part B of the same run registered 4 candidates through **Archaeon's own
writer**, selected one, cancelled three, and read the count back as DERIVED.

---

## 10. Migration / backward-compatibility consequences

* **Spec v1 rows cannot execute.** 2 completed and 70+ cancelled v1-era rows
  are terminal and frozen; they are never re-validated. One `queued` v1-era row
  was picked up during the demo and **failed visibly at validation before
  reaching `running`** — the intended behaviour, and a live demonstration of
  it. Any surviving v1 `queued` row will do the same.
* **`archaeon.experiment_queue` keeps its one proposal (AX-9ec1f5fc35ae) and
  is not migrated.** Moving it would require either weakening validation or
  rewriting its spec into v2, and rewriting a request is exactly what Vivarium
  must not do. It is readable where it is; the table is commented RETIRED and
  no code can write to it.
* **`archaeon.cadence.evaluate()` is now dead code** — it still queries the
  retired table. `vivqueue._evaluate_cadence` is the live path. Some Archaeon
  cadence tests still exercise the dead one; they pass, and pruning them is
  Archaeon's call.
* Migration 002 is idempotent and re-runnable; applied to production `viv`.

---

## 11. What still prevents the claim "differences between arms are
attributable to selection"

Ranked. The first is new, was found by this work, and is the most serious.

1. **Archaeon's test suite writes into the PRODUCTION register.** Measured:
   245 rows arrived in `viv.research_experiment_queue` during one test run
   (03:03–03:11 today, on top of Archaeon's 70 real Stage-0 rows at 02:55), and
   **a live Vivarium cycle claimed one and tried to execute it.** It failed
   validation and nothing was harmed, but a well-formed test row would have
   executed against the real engine and written a real PEW fossil. Root cause:
   `vivqueue.QUEUE` was the constant string `"viv.…"`, so Archaeon's writer had
   no way to target a test schema.
   **Fixed**: `vivqueue` now resolves the schema through `viv.db.schema()`,
   `archaeon/tests/conftest.py` creates and drops a throwaway schema, and a
   re-run confirmed production stopped growing.
   **NOT fixed, needs your decision**: the 245 rows already there. They are all
   `cancelled` so nothing will execute them, but they are indistinguishable
   from real candidate registrations except by timestamp, and they will corrupt
   any future `candidate_sets` analysis. Deleting register rows is destructive
   and is the erasure S15 warns about, so I have not done it.
2. **`archaeon.probe.v0` has no executor and its contract is PROVISIONAL.** I
   transcribed the parameter set from what `propose.build_spec` emits; Archaeon
   owns that entry and should confirm it. Until an executor exists, Archaeon's
   probes register and fail — visibly, but they do not run. Archaeon's newer
   `{seed, length, executor}` shape is a third vocabulary and needs
   re-expressing in v2; that is their side of the contract, not mine to guess.
3. **The SFE work lease is still not heartbeated.** `lease_s=120`, no
   heartbeat, `max_attempts: 3` on the work item. An execution longer than 120s
   loses its lease; the claim_id fencing token means nothing corrupt is
   written, but the engine may re-enqueue. Tier 2 item 10.
4. **No `result_contract`.** A rule naming one field of a five-metric result
   still narrows silently (Harmonia S14/A3). Tier 2 item 8.
5. **Arms must use an identical hypothesis and prediction template.** Those ARE
   execution inputs and are correctly hashed, so if the two arms word them
   differently the specs differ legitimately and the arms are no longer
   comparable on `spec_hash`. Nothing in Vivarium can enforce this — it is
   Archaeon's obligation and belongs in the family's pre-registration.
6. **Class-B selection remains invisible unless Archaeon registers candidates.**
   Vivarium provides the register; using it is Archaeon's choice, correctly.
   Vivarium sees one candidate by construction and will not attest otherwise.
7. **Single-host only.** Every run so far is on M1, where the DB, SFE and PEW
   all live. Cross-machine execution is untested.
8. **PEW is not mandatory.** A spec with `pew: null` executes and is fossilized
   nowhere, so "experiments executed" is not yet countable from the fossil
   record alone. Tier 2 item 9 — and it needs Mnemosyne's sign-off.

Not proceeding to Tier 2, and not running Archaeon's prospective scientific
family, pending review.
