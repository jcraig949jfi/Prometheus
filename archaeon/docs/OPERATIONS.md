# Archaeon producer — operations

Archaeon is an autonomous producer of experiments. It reads the fossil record,
decides whether and what to propose, publishes at most one experiment to the
canonical queue, and forgets it.

    PEW/SFE fossils -> tick() -> viv.research_experiment_queue -> [forget] -> sleep

**Archaeon is fire-and-forget across execution.** Once a row is written,
Vivarium owns that experiment's lifecycle: Archaeon does not track completion,
poll status, wait, or retry, and keeps no per-experiment state. Its only
persistent feedback channel is PEW, where new fossils are simply new evidence on
a later tick, whoever produced them.

That is about *operation*, not *evaluation*. Each row carries `policy_version`
and `template_id` in `source_evidence` (and, once Vivarium carries them
through, in the PEW producer block) so outcomes can be measured by policy and
template after the fact — against a frozen random baseline, with Harmonia
adjudicating. The tick never does that; the record makes it possible.

The two loops are independent and need no synchronous coordination:

    Archaeon:  PEW -> proposal -> queue
    Vivarium:  queue -> execution -> PEW

## Seat boundary

**Archaeon does not run Vivarium.** Another agent owns that process. Nothing in
this document asks you to start a consumer, and Archaeon must not start one
itself — including to demonstrate its own output. Archaeon publishes and stops;
the consumer side is observed, never driven.

If a proposal sits `queued`, report it. Do not start a consumer to move it.

## Architecture

    archaeon/producer/
      contract.py    the executable experiment vocabulary (kind + params)
      readers.py     recent_fossils (science in) / publication_record (own outbox)
      randomgen.py   the RANDOM policy: a boring valid experiment, no corpus read
      specbuild.py   build + validate against VIVARIUM'S validator
      tick.py        one decision cycle -- the only thing the loop calls
      loop.py        the daemon

    archaeon/vivqueue.py   the writer: cadence, relation columns, candidate sets
    archaeon/cadence.py    gate + evaluation (database clock, DB-enforced cap)

## Start (deployed): a scheduled task, not a daemon

    powershell -ExecutionPolicy Bypass -File archaeon/deploy/register_archaeon_tick.ps1

Registers `ArchaeonTick`: one `tick()` every 15 minutes via
`archaeon/deploy/archaeon_tick.cmd`. **There is deliberately no long-lived
process.** Each run is one complete cycle; cadence is enforced by the database;
a reboot or a crash loses nothing because there is nothing to lose. This is why
"no process supervision" stopped being a blocker — the thing that needed
supervising was removed.

15 minutes is how often to **ask**, not how often to write. Against the
four-hour cadence roughly 15 of every 16 runs return `NO_WRITE_CADENCE`, which
is the design working.

    schtasks /Query /TN ArchaeonTick /V /FO LIST      # inspect
    schtasks /Delete /TN ArchaeonTick /F              # kill switch
    Get-Content archaeon/deploy/archaeon_tick.log -Tail 40

Set `ARCHAEON_LANE` in the task's environment to use a lane other than `prod`.

## Start (interactive): the loop

    python -m archaeon.producer.loop --interval 900

For debugging and demonstrations. Same `tick()`, in a foreground process.
Options: `--lane`, `--max-cycles`, `--log-level`.

## Stop

Deployed: `schtasks /Delete /TN ArchaeonTick /F`. A run already in progress
finishes its single cycle (seconds) and exits.

Interactive loop: Ctrl-C, or `SIGTERM`. The current cycle finishes, the next
does not start, and the process exits 0. There is no pidfile and no
daemonisation.

**Safe to kill at any point.** Every write is one transaction, so a process
killed mid-cycle either wrote its row or did not; there is no partial state to
clean up. Restart is simply starting it again — no recovery step, because
Archaeon keeps no per-experiment state to recover.

## One cycle by hand

    python -m archaeon.producer.loop --once              # decide and write
    python -m archaeon.producer.loop --once --dry-run    # decide, write nothing

Both print the full tick record as JSON.

## Status and health

    python -m archaeon.producer.loop --status --lane prod

Reports publication rate and cadence position only:

    published, published_today, last_published_at, seconds_since_last

It deliberately does **not** report claimed/running/completed/failed. Those
describe experiments already handed off, and reporting them here would
reintroduce the tracking this seat does not do. **Queue execution state is
Vivarium's to report** (`vivarium status`, `vivarium ls`).

`last_published_at` counts only rows that consumed quota, exactly as the cadence
evaluator does. Counting all rows made health say "24 minutes ago" while cadence
said "never" — a contradiction that teaches an operator to distrust both.

## Logs

One line per cycle on stdout:

    2026-09-06 07:39:18 INFO archaeon.producer cycle 3 WROTE cd8cb298-... (WROTE_WEAK_SIGNAL, sha256:2a0790408d9ea1a)
    2026-09-06 07:41:18 INFO archaeon.producer cycle 4 no-write: NO_WRITE_CADENCE (last autonomous proposal was 120s ago; 14400s required)

Redirect to a file; there is no log rotation built in.

Decisions are **also durably recorded** in `archaeon.cadence_log`, including the
no-writes, with `detail.tick_decision` carrying tick's richer vocabulary. A
refused cycle and a cycle that never ran must be distinguishable, or the loop's
health is unknowable:

    SELECT decided_at, decision, detail->>'tick_decision', detail->>'experiment_id'
      FROM archaeon.cadence_log WHERE lane='prod' ORDER BY decided_at DESC LIMIT 20;

## Cadence

At most **six** autonomous proposals per UTC day per lane, at least **four
hours** apart. Enforced in PostgreSQL, not in this code:

* a partial unique index on `(cadence_lane, cadence_utc_day, cadence_day_ordinal)`
  caps the day at six even if the application is wrong;
* a `FOR UPDATE` gate serialises concurrent instances;
* the four-hour check uses the **database** clock, never the process clock.

Running the loop twice by accident cannot double-issue. Only a *selected* row
consumes quota — registered-then-cancelled candidates are free.

Decision codes: `WROTE_WEAK_SIGNAL`, `WROTE_RANDOM`, `NO_WRITE_CADENCE`,
`NO_WRITE_NO_CANDIDATE`, `NO_WRITE_ERROR`.

## Queue inspection

    SELECT experiment_id, created_at, source_reason, spec_hash, cadence_day_ordinal
      FROM viv.research_experiment_queue
     WHERE cadence_lane='prod' ORDER BY created_at DESC LIMIT 10;

Candidate sets, counted by the register rather than attested by anyone:

    SELECT * FROM viv.candidate_sets ORDER BY registered_at DESC LIMIT 10;

## Last decision

    python -m archaeon.producer.loop --once --dry-run    # what it would do now

or read the durable record from `archaeon.cadence_log` (above). The proposal's
full reasoning is in the queue row's `source_evidence`:

    SELECT source_evidence FROM viv.research_experiment_queue
     WHERE experiment_id = '<id>';

## Verifying an Archaeon proposal reached PEW

Normal operation does **not** do this — it is a diagnostic, not a loop step.
Vivarium records the reference on the queue row it owns:

    SELECT sfe_experiment_id, pew_reference, status
      FROM viv.research_experiment_queue WHERE experiment_id = '<id>';

    -- pew:encounter/<encounter_id>:<exp_id>:<work_id>

Then confirm the fossil independently:

    SELECT encounter_id, run_id, sfe_event_id, sfe_entry_hash, outcome
      FROM ew.fossil_encounters WHERE encounter_id = '<encounter_id>';

The `encounter_id` is the one **Archaeon** minted in the spec's `pew` block —
Vivarium never mints scientific identity.

## Common failure modes

| symptom | cause | action |
|---|---|---|
| every cycle `NO_WRITE_CADENCE` | working as designed; ~23h in 24 | none |
| `NO_WRITE_ERROR`, `QueueContractMissing` | Vivarium migration 002 not applied | apply `vivarium/migrations/` |
| `NO_WRITE_NO_CANDIDATE` | 16 draws all already published in this lane | widen `ALLOWED_LENGTHS`, or use a new lane |
| queue row stuck `failed`, `no PEW token configured` | `VIV_PEW_TOKEN` unset for the **consumer** | report to the Vivarium agent; not Archaeon's to set |
| proposal sits `queued` indefinitely | no consumer is running | report it; do NOT start one |
| loop logs a cycle then backs off | consecutive errors; backoff 30s→600s | check the error, DB reachability |
| `SpecInvalid` from the validator | Vivarium's spec contract changed | run the contract test; coordinate |

Archaeon never retries a failed experiment. A failed row is terminal and
visible; re-running it is a decision for an operator, not a producer.

## Independence check

    python -c "from archaeon.producer import contract; print(contract.check_against_vivarium())"

Reports whether Archaeon's emitted kind still matches Vivarium's live registry.
A silent divergence between the two sides of this seam has already produced two
queues and two migrations; this makes it loud.

## Tests

    python -m pytest archaeon/tests/ -q

`archaeon/tests/conftest.py` redirects `VIV_SCHEMA` to a throwaway schema.
**This protection is not optional.** Before it existed the suite wrote 245 rows
into the production register and a live Vivarium cycle claimed one and tried to
execute it. Three tests assert the protection is in force, including that the
precondition checks the same schema the writer writes to.

## The signal campaign's instrument: the substrate census

Every tick writes one row to `archaeon.substrate_census`: rows, regions,
attributed players, the declared tenancy, per-detector eligible/total/cause,
S17 units, and a WISHLIST naming the structure that would flip each blocked
detector and the lane it belongs to. Its slope over time is the campaign's
progress measure.

    python -m archaeon.producer.census --lane prod            # the time series
    python -m archaeon.producer.census --lane prod --wishlist # what would move it next

## Declared tenancy (what the reader counts as the corpus)

Per Daedalus's consumer contract, the reader applies in SQL, inside one
transaction, after a schema guard: `evidence_class = 'ENGINE_WORK_RESULT'` and
a declared client-name set (`config.TenancyConfig.include_client_names`).
Excluded attested observations are counted by client name in every corpus
window. Change the set in one line of config; never by editing SQL.

## The menu: templates

    archaeon/templates/*.json          ADMITTED -> drawn from
    archaeon/templates/inbox/*.json    PROPOSED -> never drawn from

`bitstring.uniform.v0` is the frozen random baseline. Admission is a human act:
set `status`, `admitted_by`, `admitted_at`, and `admitted_content_hash`
(compute with `templates._content_hash`). An admitted template that later
changes is refused on load. A template whose kind Vivarium does not implement
is an expansion request and cannot be on the menu.

    python -c "from archaeon.producer import templates as T; import json; print(json.dumps(T.menu_growth(), indent=2))"

CHAOS proposes perturbed copies into the inbox and never admits:

    python -c "from archaeon.producer import chaos, templates as T; print(chaos.mutate(T.admitted()[:1], 'WIDEN', nonce='1'))"

## Program health / monoculture report

    python -m archaeon.producer.health_report --days 7 --lane prod

Measurements against stated thresholds; flags name a lane and what they would
unblock. Each fired flag is an entry for `roles/Archaeon/EXPANSIONS.md`.
