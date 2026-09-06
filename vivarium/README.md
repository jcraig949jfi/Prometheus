# VIVARIUM

The experimental execution service. **Vivarium is not a scientist.**

    QUEUE  ->  EXECUTE FAITHFULLY  ->  RECORD  ->  REPEAT

It does not decide whether an experiment is interesting, whether a signal is
real, whether a lineage should continue, or what conclusion follows. It runs
what it is given, exactly as given, once, and writes down what happened.

    Archaeon  ->  PostgreSQL queue  ->  Vivarium  ->  SFE / worlds / players
                                                   ->  PEW  ->  Archaeon

---

## What is where

| | |
|---|---|
| `migrations/001_vivarium_queue.sql` | the queue, the event log, the state machine (in the DB) |
| `viv/db.py` | connection + credential precedence + migration apply |
| `viv/spec.py` | canonical spec hash (SFE-identical) and strict validation |
| `viv/queue.py` | the legal moves and their event rows |
| `viv/runner.py` | the SFE adapter: session -> world -> experiment -> work -> observation |
| `viv/executors.py` | local executors (`noop_v0`, `evaluate_bitstring`) |
| `viv/pew.py` | the fossil write (`pew.fossil.v2`) |
| `viv/loop.py` | the nine stages and `tick()` |
| `viv/daemon.py` | the thin loop around `tick()` |
| `viv/cli.py` | the status surface |
| `migrations/003_register_errata.sql` | contamination recorded, never erased |
| `specs/` | example specifications |

## Configuration

No credential is committed. Precedence, highest first:

1. environment — `VIV_DB_HOST` / `VIV_DB_NAME` / `VIV_DB_USER` /
   `VIV_DB_PASSWORD` / `VIV_SCHEMA` / `VIV_SFE_TOKEN` / `VIV_PEW_TOKEN`
2. `vivarium/config.local.json` — gitignored (repo `.gitignore`)
3. `evidence_wiki`'s existing loader — the established shared-Postgres
   credential mechanism, reused rather than duplicated, so there is one place
   to rotate
4. `vivarium/config.json` — non-secret defaults only

## Operating it

```bash
cd vivarium
python -m viv.cli migrate                      # idempotent
python -m viv.cli enqueue specs/example_bitstring.json \
       --by archaeon --reason "why this experiment exists"
python -m viv.cli run --once                   # or: run  (long-running)
python -m viv.cli status
python -m viv.cli trace                        # queue -> SFE -> PEW
python -m viv.cli show <experiment_id>
python -m viv.cli kinds                        # the per-kind contracts
python -m viv.cli family <family_id>           # a comparison, by arm
python -m viv.cli candidates <candidate_set_id># OBSERVED set extent
python -m viv.cli tick                         # exactly one tick, JSON out
python -m viv.cli health                       # machine-readable health
python -m viv.cli errata                       # declared contamination
```

## The machine

    recover -> claim -> validate -> build_request -> dispatch
            -> collect -> fossilize -> finalize

`tick()` composes those nine stages and processes **at most one** runnable
item. `daemon.py` is a loop around `tick()` and holds no policy: fixed idle
interval, no batching, no reordering, no retry. `run --once` is one tick;
`run --stop-when-idle` drains and exits 0; a stranded row exits **2**.

Tick outcomes are a closed set: `IDLE BUSY EXECUTED FAILED REJECTED BLOCKED`.

## Contamination

Excluded rows are never deleted. `viv.register_errata` + `register_errata_rows`
enumerate them; **analysis reads `viv.register_clean`**, and a `candidate_sets`
row with `excluded > 0` is contaminated. See `python -m viv.cli errata`.

`status` exits non-zero when anything is stranded, so it works as a check.

## The sealed specification (v2)

> **The sealed spec contains exactly the execution inputs.
> Provenance lives outside the hash.**

`spec_hash` is the substrate's grouping surface, so anything hashed that does
not change what is executed is a channel by which the selecting policy leaks
into the sealed record. Every key below is an execution input; everything about
*who asked and why* is a queue column.

```json
{
  "spec_version": 2,
  "world": {"seed_root": 424242},
  "hypothesis": "...",
  "prediction": null,
  "work": {"kind": "evaluate_bitstring",
           "payload": {"bits": "0...", "length": 24}},
  "outcome_rule": {"field": "solved", "op": "==", "value": false,
                   "if_true": "SURVIVED", "if_false": "FALSIFIED",
                   "if_indeterminate": "INCONCLUSIVE"},
  "pew": {"encounter_id": "...", "players": [], "required": false}
}
```

* **No `notes`, no `experiment_kind`, no `world.name`.** All three were
  measured to change `spec_hash` without changing what is executed. The world
  name is derived: `viv-<spec_hash[7:23]>`.
* **Explicit `null`, never omission** for `prediction`, `outcome_rule`, `pew`.
  An omitted field and a declared absence are different experiments.
* **`work.payload` must match its kind's contract exactly** — every parameter
  present, none extra, no executor default anywhere. `vivarium kinds` prints
  the contracts.
* **`outcome_rule.if_indeterminate` is required.** The branch taken when the
  rule cannot be evaluated is the requester's declaration, not Vivarium's.
* **`pew`** is the only place scientific identity enters. Vivarium mints no
  `encounter_id` and no `player_id`.

## Provenance and experimental relations (queue columns, never hashed)

| column | meaning |
|---|---|
| `created_by`, `source_reason`, `source_evidence` | who asked and why |
| `family_id`, `arm_id` | a comparison declared BEFORE execution |
| `replication_of` | a deliberate repeat, declared as one |
| `candidate_set_id` | membership of a set registered before selection |
| `request_key` | idempotency: the same key is the same request |
| `cadence_lane`, `cadence_day_ordinal` | Archaeon's autonomous quota |

All are frozen by the BEFORE UPDATE trigger, so a comparison cannot be re-drawn
after its outcomes are visible. None of them reaches the executor: the runner
receives an `ExecutionRequest` of exactly `(experiment_id, spec_json,
spec_hash)`, and `tests/test_blinding.py` asserts that it cannot.

## The state machine

    queued  --claim-->  claimed  --execution begins-->  running  -->  completed
       |                   |                              |
       |                   +-------> failed <-------------+
       +---> cancelled

Terminal rows are frozen whole. Every transition appends to
`research_experiment_events`, which refuses UPDATE and DELETE.

## Crash recovery

A worker that dies mid-run leaves its row `claimed` or `running`. Vivarium does
**not** adopt, reset, or retry it: guessing that a stranded run did not happen
is exactly the guess that runs an experiment twice.

```bash
python -m viv.cli stranded
# inspect the SFE experiment named in the row, then:
python -m viv.cli release <id> --by <you> --reason "verified in SFE: ..."
```

`release` always resolves to `failed`, never back to `queued`. Requeueing would
assert the experiment did not run, and the queue cannot know that.

## Tests

```bash
cd vivarium && python -m pytest tests -q
```

Every test runs against real PostgreSQL in a throwaway schema — `FOR UPDATE
SKIP LOCKED`, the partial unique index and the plpgsql triggers *are* the
mechanism, and a mock would only prove the mock works. `test_live_sfe.py`
skips when the engine is unreachable; `test_live_pew.py` additionally needs
`VIV_LIVE_PEW=1`, because a test suite must not write to a shared append-only
scientific record just because it happened to run.
