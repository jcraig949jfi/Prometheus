# Necropolis Seams

How Necropolis objects interoperate with existing Prometheus machinery. Necropolis deliberately
**reuses** the autopsy and consumption ledgers rather than forking parallel infrastructure. This
document names the intended seams; it does NOT wire automation in the founding pass (LAW N3, and
"do not wire automation merely for completeness").

## Upstream: the autopsy layer (reuse, read-only)

- `engine/ledger/AGENT_AUTOPSIES.jsonl` — 21 typed autopsy records
  (`agent_id, autopsied, by, design_choice, failure_class, boundary_localization,
  representation_hint, evidence, repair_log`). A Necropolis dossier is a **compatible superset**:
  - autopsy record `failure_class`     -> dossier `autopsy.failure_classes[]`
  - autopsy record `boundary_localization` -> dossier `autopsy.kill_boundary`
  - autopsy record `representation_hint`   -> dossier `residue.representation_hints[]`
  - autopsy record `design_choice`/`evidence` -> dossier `original_organism` + `observed_history`
  A dossier for an already-autopsied agent should ingest that record rather than re-derive it, and
  cite it in `autopsy.prior_verdicts` (still subject to LAW N11 re-audit).
- `engine/ledger/AUTOPSY_TAXONOMY.md` — the 5-cluster mechanistic taxonomy. `failure_classes[]`
  SHOULD reference a cluster name so dossiers and the taxonomy stay joinable.

## The consumption-proof seam (reuse — this is how LAW N6 is discharged)

- `engine/queues/CONSUMPTION.jsonl` — rows of `{ts, object, consumed_by, effect, summary}`. This
  is the existing, canonical proof-of-consumption format. A descendant's `consumption_proof`
  should name the specific `object` it will emit and the `consumed_by` that will register a
  measured `effect`. A descendant is "alive" when such a row exists with a real effect — not when
  the process merely runs.

## The preregistered-experiment analogue (pattern to mirror)

- `ama_game/arena/<...>/runs/<id>/{claim.json, disposition.json, verify.py}` — the existing
  pattern for a preregistered claim with an executable verifier and a recorded disposition. A
  Cleric's resurrection experiment (LAW N9) should mirror this shape: the descendant ships a
  `verify.py` that EXECUTES the discriminating test, not a prose assertion.

## Downstream decision/queue ledgers (future wiring, not built here)

- `engine/queues/DECISIONS.jsonl`, `engine/queues/WORK.jsonl`, `engine/queues/BACKLOG.jsonl`,
  `engine/ledger/CLOSURE_RECORDS.json` — when Necropolis matures, an accepted dossier can enqueue
  a Cleric work item and a disposition decision through these existing ledgers rather than a new
  queue. The intended edge:
  ```
  QUEUE.jsonl (READY) -> Necromancer -> dossiers/<agent>.dossier.json
     -> DECISIONS.jsonl (disposition + HITL sign-off)
        -> WORK.jsonl (Cleric task, if a descendant is accepted)
           -> descendants/<id>/verify.py -> CONSUMPTION.jsonl (effect)
  ```
  Left as a documented seam, not automated, until there is a real accepted dossier to carry.

## Disposition/thoughtwork lineage (evidence source, immutable)

- `pivot/PROCESS_TABLE_2026-06-24.md` (the 43-subset advisory dispositions),
  `pivot/COMPONENT_DOSSIERS_2026-06-24.md` (39 thoughtwork dossiers),
  `pivot/COMPONENT_THOUGHTWORK_REVIEW_2026-06-24.md` (the flow
  `candidate -> PENDING-REVIEW -> dossier -> HITL -> {REVIVE|REFACTOR|RETIRE}`).
  Necropolis' lifecycle is a rigorous descendant of that flow. These docs are cited as evidence
  (`autopsy.prior_verdicts`) and never edited.

## What Necropolis must never seam into

- H0-H5 machinery, queues, hypotheses, experiment packets, or M1 workflows (LAW N12).
- Any `.env` / key / credential file (repo CLAUDE.md security rule).
