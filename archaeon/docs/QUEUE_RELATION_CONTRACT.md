# Archaeon ↔ Vivarium — queue and experimental-relation contract

**Status:** design + non-scientific integration tests complete. Stage 1 NOT built.
Writer `archaeon/vivqueue.py`. Tests `archaeon/tests/test_vivqueue_integration.py`
(28 tests, real PostgreSQL). Full suite 107 passing.

**The schema migration is VIVARIUM'S, not Archaeon's.** The Vivarium seat was
working this seam concurrently and wrote
`vivarium/migrations/002_relations_cadence_idempotency.sql`. The two designs
converged independently on the same contract -- identical column, constraint and
index names, the same `candidate_sets` view, the same extension of
`enforce_queue_transition` freezing the relation declaration. That convergence is
evidence the contract is right; two migrations competing to own it is not.
`viv.research_experiment_queue` is Vivarium's table, so their migration is
authoritative and `archaeon/migrations/003` was reduced to the one thing that is
actually Archaeon's: retiring `archaeon.experiment_queue`.

Their version is a strict superset -- it adds `req_replication_not_self` and an
`executed` column on the view (`count FILTER (started_at IS NOT NULL)`) that
separates "registered but never started" from "actually executed", which
Archaeon needs for any per-experiment endpoint.

The collision also exposed a real defect in my version: it used
`CREATE OR REPLACE VIEW`, which cannot drop a column, so once their view added
`executed` mine failed with *cannot drop columns from view* and the whole
migration set became un-re-runnable. `evidence_wiki/migrations/007` documents
this exact trap from a previous occurrence. Their `DROP VIEW IF EXISTS` +
`CREATE VIEW` is the correct pattern.

Archaeon now **never** performs DDL on that table: `vivqueue.assert_queue_ready`
fails loudly with a pointer to the missing migration, and a test asserts no DDL
statement appears anywhere in `vivqueue.py`. A consumer that silently ALTERs a
producer's schema is how one contract becomes two divergent definitions.

## 1. Schema chosen

`viv.research_experiment_queue` is now **the single canonical pre-execution
register**. `archaeon.experiment_queue` is **retired, not dropped** — it holds a
real proposal, and deleting a pre-execution register to tidy an architecture is
itself the kind of erasure S15 classes as an unobservable selection mechanism.
It carries a `RETIRED` table comment and nothing writes to it (enforced by an
AST-level test, not a substring grep).

Columns added, **all provenance, none hashed**:

```
family_id            text     comparison/family identity
arm_id               text     arm within the family  (CHECK: needs family_id)
replication_of       uuid     declared repeat -> FK to the original row
candidate_set_id     text     membership of a pre-selection candidate set
request_key          text     idempotency, UNIQUE
cadence_lane         text     Archaeon quota namespace
cadence_day_ordinal  int      0..5, NULL unless the row consumed quota
cadence_utc_day      date     GENERATED from created_at
```

Plus `viv.candidate_sets`, a **view** (`registered`, `cancelled`, `retained`,
`executed`, `registered_at`, `last_registered_at`, `registrars`), and one unique index
`(cadence_lane, cadence_utc_day, cadence_day_ordinal)` that caps the day at six
as a database property.

Vivarium's `enforce_queue_transition` trigger gains one check beyond its
original six: the relation declaration is immutable. A mutable `family_id` would
let a comparison be re-drawn after its outcomes were visible, which is the
retrospective grouping this whole contract exists to prevent. Both seats wrote
this check independently and identically; Vivarium's is the one that ships.
`active_singleton` survives untouched.

## 2. Execution input vs provenance

The partition is Vivarium's (BOUNDARY_REVIEW §3), extended:

- **SEALED EXECUTION INPUTS** — `experiment_spec`, `spec_hash`. Hashed, handed
  to the executor. Archaeon adds nothing here, ever.
- **PROVENANCE** — `created_by`, `source_reason`, `source_evidence`, `priority`,
  `not_before`, and every column above. Immutable, recorded, **never visible to
  the execution path**, never in `spec_hash`.
- **EXECUTION RESULT** — status, timestamps, `sfe_experiment_id`,
  `pew_reference`, `result_summary`, `error`.

The rule, from Harmonia S14 via Vivarium's review: *the sealed spec contains
exactly the execution inputs; provenance lives outside the hash.* `spec_hash` is
the substrate's grouping surface, so an arm label inside it would split the
derived universe along the arm boundary — the policy would leak into the sealed
scientific record.

`vivqueue.assert_spec_is_execution_only` **refuses** a spec carrying `notes`,
`experiment_kind`, `family_id`, `arm_id`, `arm`, `family`, `candidate_set_id`,
`replication_of`, `policy`, `source_reason`, `created_by`, or `world.name`. The
first three are Vivarium's measured offenders (F2); Archaeon must not add a
fourth.

The property that proves the line is drawn correctly, and is a test:

> Two candidates in **different arms** of one family may carry **byte-identical
> specs and the same `spec_hash`**.

If arm identity had to live in the spec, two arms could never share a hash and
the comparison would be split by construction.

## 3. Candidate registration

`vivqueue.submit(candidates=[...], selected_index=k)` — **one transaction**:
take the cadence gate → evaluate cadence → insert every candidate → assign the
ordinal to the selected row only → `UPDATE ... SET status='cancelled'` on the
rest → log → commit.

Four properties, each tested:

- **Atomic.** A partially registered set cannot exist, so "registered before
  selection" is a property rather than a claim. A bad row rolls the set back
  and `candidate_sets` shows nothing.
- **Never attested.** There is deliberately **no `candidate_set_size` column**.
  A stored count is an assertion and can be wrong; `viv.candidate_sets` derives
  it from rows that actually exist — the register counting itself. This also
  resolves Vivarium's §11 objection to S15's M4 ("the executor must attest how
  many candidates it produced"): Vivarium sees one candidate by construction and
  should never attest a number it cannot know. Nobody attests; the register is
  read.
- **Not required globally.** A row with `candidate_set_id IS NULL` is an
  ordinary experiment, not a deficient one. A single candidate is an honest set
  of one.
- **Affordable.** Registering twenty candidates consumes **one** of the six
  daily slots, not twenty. Only the selected row gets a `cadence_day_ordinal`.
  Priced any other way, the class-B → class-A conversion would never be used.

`registered_at` and `last_registered_at` are both exposed: a set written across
a wide span was not registered atomically, and its "before selection" claim is
correspondingly weaker. That is visible rather than assumed.

## 4. Cancellations and failures stay visible

- **Cancelled is terminal and permanent**, never a delete. A registered-and-not-run
  candidate is the only class-A trace of a selection decision anywhere in the
  architecture (S15; Vivarium §11).
- **Terminal rows are frozen whole** by the trigger; the event table refuses
  UPDATE and DELETE.
- **Cadence refusals are durable** — written to `archaeon.cadence_log` and
  committed even though no queue row is created, so a refusal is distinguishable
  from a cycle that never ran.

**One gap, and it is Vivarium's, already self-reported (§5):** a failed run
produces **no PEW fossil**, because the PEW write is on the success path only.
Under "PEW is the fossil record" that is backwards — failures are exactly what an
efficiency endpoint must count, since *failures per experiment executed* requires
`executed` to be countable from the fossil record. Vivarium's Tier 1 item 6
fixes it. Until then, executed-and-failed is visible in the queue but invisible
in the fossil record, and any endpoint computed from PEW alone would be biased
toward successes.

## 5. Cadence preserved

Unchanged in meaning: ≤6 autonomous proposals per UTC day per lane, ≥4 hours
apart, DB-enforced, database clock, gate taken first, refusals logged. Verified
on the new table including a 6-thread concurrency test (exactly one admitted).
Autonomy remains keyed on `source_reason`, never on a `created_by` name.

## 6. What Vivarium still owes (their Tier 1, unchanged by this)

Nothing here does Vivarium's work. Their `ExecutionRequest` blinding (F1),
dropping `notes`/`experiment_kind`/`world.name` from the hash (F2), removing the
`length` default (F3), and required `if_indeterminate` (F4) remain theirs. This
contract is written so that none of it conflicts: every field added is outside
the hash, so dropping fields from the hash cannot collide with it.

## 7. Blocking capability gap — see `PROSPECTIVE_FAMILY_F1.md`

`runner.run()` calls `create_world()` on every row and records exactly **one**
`observation`. One queue row = one new world = one observation, with no path to
reuse a world. S17 needs **>3 observations within a world** for lag-1
autocorrelation. **No family issued through Vivarium as currently built can ever
produce an eligible claim-unit**, at any volume. This is a capability gap, not a
tuning problem, and it must be closed before the prospective family can run.
