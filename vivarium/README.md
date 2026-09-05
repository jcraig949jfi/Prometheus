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
| `viv/loop.py` | the service |
| `viv/cli.py` | the status surface |
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
```

`status` exits non-zero when anything is stranded, so it works as a check.

## The specification

Archaeon authors these. Vivarium validates strictly (unknown key = rejected)
and stores the object **byte-for-byte as supplied** — a normalised spec is a
different experiment with the same name.

```json
{
  "spec_version": 1,
  "experiment_kind": "onemax_probe",
  "world": {"name": "...", "seed_root": 424242},
  "hypothesis": "...",
  "prediction": {"...": "optional; registered BEFORE commit"},
  "work": {"kind": "evaluate_bitstring", "payload": {"bits": "0...", "length": 24}},
  "outcome_rule": {"field": "solved", "op": "==", "value": false,
                   "if_true": "SURVIVED", "if_false": "FALSIFIED"},
  "pew": {"encounter_id": "...", "players": ["..."], "required": false},
  "notes": "optional"
}
```

`outcome_rule` is the requester's **pre-registered** decision procedure.
Vivarium evaluates it mechanically and records the provenance of the
evaluation. No rule, or a field the result does not carry, yields
`INCONCLUSIVE` — a missing measurement is not a negative one.

`pew` is the only place scientific identity enters. Vivarium mints no
`encounter_id` and no `player_id`; it supplies only the execution half it
witnessed.

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
