# VIVARIUM — Charter

Seat opened 2026-09-05.

## What this seat is

The trustworthy mechanical hand at the research bench.

    QUEUE  ->  EXECUTE FAITHFULLY  ->  RECORD  ->  REPEAT

Vivarium is the execution service between the seat that decides what to run
and the records that say what was run:

    Archaeon  ->  PostgreSQL experiment queue  ->  VIVARIUM
              ->  SFE / worlds / players  ->  PEW  ->  Archaeon

## What this seat is NOT

**Vivarium is not a scientist.** It has no opinion, and is architecturally
prevented from forming one:

* it does not decide whether an experiment is interesting;
* it does not decide whether a signal is real;
* it does not decide whether a lineage should continue;
* it does not draw a conclusion from a result;
* it does not decide what runs next on any ground other than
  `(priority, created_at)`;
* it does not rewrite an experiment because another version would be better.

Where a decision is genuinely required at execution time — the one place being
an experiment's `outcome`, which SFE demands — the decision procedure is
**pre-registered by the requester in the specification** and Vivarium evaluates
it mechanically, recording the provenance of that evaluation. Absent a rule, it
records `INCONCLUSIVE` and says why. It never invents an adjudication.

## Standing invariants

1. A queue item never executes twice because of a race.
2. A malformed experiment never silently mutates into a different experiment.
3. The sealed spec hash corresponds to what Vivarium received, and to what the
   SFE ledger holds — both checked, the second before any work runs.
4. A completed, failed or cancelled experiment is never reclaimed.
5. A failure is preserved and visible. There is no silent retry.
6. A stranded run is left visibly stranded. Vivarium never guesses that
   repeating it is safe; an operator releases it explicitly.
7. Mutable orchestration state (the queue) and the immutable scientific record
   (SFE, PEW) are never confused. The queue holds pointers, never copies.

## Deliberate non-goals for v0

No scheduling intelligence. No scientific interpretation. No LLM. No
recommendation engine. No throughput optimisation. Exactly one experiment runs
globally at a time, and the *database* enforces that, not the loop.

Small on purpose: Harmonia should be able to attack the whole thing.

## Boundary with sibling seats

* **Archaeon** owns what to run and why (`source_reason`, `source_evidence`,
  `outcome_rule`). Vivarium never authors these.
* **SFE / Daedalus** own the scientific ledger and its semantics. Vivarium
  consumes the published `/v2` API and modifies no engine semantics.
* **PEW / Mnemosyne** own the authoritative fossil record. Vivarium writes only
  the execution half it witnessed, into identities the requester declared.
* **Proteus** owns player identity. Vivarium mints no `organism_id` and no
  `encounter_id`, ever.
* **Harmonia** attacks it.
