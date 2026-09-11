# Hypatia -- the old queue, classified

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Base SHA 8bc5d295b9f6eb9308f1492dc41d5e0b48121f26.

Booting an old seat is an archaeological event, not an instruction to resume
its last queue. Every item of Hypatia's May commitments and of the salvage
and option lists later written about it is classified below against the
current north star and ecosystem. Only STILL_LIVE is executable work.

Counts over 18 items: STILL_LIVE 0, NEEDS_REPREMISE 6, PARKED 4,
SUPERSEDED 6, TRANSFERRED 1, RETIRED 1.

## Why STILL_LIVE is zero

Not because the machinery broke. The machinery ran for eight days and did
what it was told. STILL_LIVE is zero because the instruction was void: the
charter's per-tick contract asks a deep-research model to "decompose the
PROOF of the following result" against a catalog that is 532 of 537 unproven
conjectures. There is no proof to decompose for 99.1 percent of the backlog.

Resuming any item that presupposes that task would re-run a null AND
manufacture confabulated training data on a schedule, which is worse than
producing nothing. The MATH-0008 report is the demonstration and it is
committed: 2621 seconds spent discovering the statement was open, then a
fabricated R1-R5 ladder for a substituted theorem, emitted to satisfy the
output contract.

## The table

| # | item (as it stood in May, or as later proposed) | class | evidence / reason |
|---|---|---|---|
| 1 | Pick one problem per day from the 537-catalog and dispatch a Type-D proof-decomposition query | NEEDS_REPREMISE | the task is impossible on 532/537 of the catalog; re-measured today. The cadence machinery is fine, the question is not |
| 2 | Bias selection by Pheme's demand profile | SUPERSEDED | the seam raises TypeError before any bias applies (science/seam_contract_test.py, CONFIRMED today) and Pheme produced 0 profiles in 354 ticks. Both halves dead. Pheme is itself BLOCKED on PHEME-01 |
| 3 | Land R1-R5 JSONL into ergon/learner/corpus/.../worked_solutions/ | SUPERSEDED | the directory does not exist and never did; the charter itself calls the ingester "TBD, currently manual". Whether such a corpus should exist at all is HYPATIA-12, addressed to Ergon |
| 4 | Emit a null_*.json sentinel on every skipped tick (anti-silence) | RETIRED | this is the autopsied defect (LIVENESS-AS-ARTIFACT). Not to be rebuilt. Liveness goes to the heartbeat channel only |
| 5 | Fire SELF_AUDIT_NULL at 50 consecutive null ticks | SUPERSEDED | the alarm had no route, which is the same defect Atalanta recorded: an alarm with no destination is not an alarm. Base rule 7 now governs this centrally |
| 6 | Emit CATALOG_SATURATED when the 30-day window eats the catalog | PARKED | never fired; correct in shape; meaningless until item 1 is re-premised |
| 7 | Maintain the single-instance pid lock and atomic state writes | PARKED | good engineering, still good, inert while nothing runs. Needs the D-23 guard added (HYPATIA-06) before it could ever run again |
| 8 | Detached launch via scripts/hypatia_loop_launch.bat | SUPERSEDED | launches from the canonical checkout, forbidden by D-23 s1. Annotated, not deleted |
| 9 | Propose catalog expansion when saturated (proposal-only, never mutate questions.jsonl) | PARKED | the hard stop stands and is carried into the seat file. Whether the catalog has an owner today is HYPATIA-16 |
| 10 | Salvage: the R1-R5 ladder taxonomy | NEEDS_REPREMISE | the one piece other lanes might use; it is a schema, not a loop, and needs no daemon. HYPATIA-04 extracts it. Whether anyone ever consumed it is HYPATIA-15, and the honest expectation is zero |
| 11 | Salvage: the daemon scaffold (lock, atomic state, dual logging, sentinels) | NEEDS_REPREMISE | reusable as a template minus the anti-silence stream, which is item 4 and is retired |
| 12 | Salvage: the dispatch provenance schema (queue_ref, verdict_back_to, ergon_demand_target) | NEEDS_REPREMISE | sound; ergon_demand_target carries the broken dict shape and must be re-typed with it |
| 13 | Salvage: the 8 completed deep-research reports | NEEDS_REPREMISE | genuine literature surveys, useless as training data. Whether they have standalone value is HYPATIA-10, with an explicit NULL branch |
| 14 | Dossier option: REFACTOR-to-solved-corpus (repoint at proved theorems) | NEEDS_REPREMISE | the most direct repair of item 1; requires a solved-theorem catalog the program does not have. Folded into HYPATIA-03 |
| 15 | Dossier option: ADAPT-to-spine (decompose the program's own kill-geometry) | PARKED | closest to the current north star, and the seat's preferred branch, but it is a new premise needing a preregistration and an operator ruling first. Folded into HYPATIA-03 |
| 16 | Dossier option: REVIVE-only-after-ingester | SUPERSEDED | conditions (a) corpus dir, (b) cite-leak fixed, (c) solved backlog are all unmet, and (c) is the void premise again. Superseded by HYPATIA-03, which asks the prior question |
| 17 | BACKLOG row AUTOPSY-HYPATIA ("file Hypatia failure modes as typed trace vectors") | RETIRED | status DONE; the P63 autopsy delivered it, and the class was reused on Nephele the same day |
| 18 | BACKLOG row PROF-Hypatia ("ladder profile: run artifacts/config through phase0+R4 probes") | TRANSFERRED | status PARKED on a budget gate; the profiler owns it, not this seat. Named here so it is not double-owned |

## What was searched to build this table

git log for every commit touching agents/hypatia (exactly one, e6b3746f0);
git grep for "hypatia" across tracked .md/.py/.json/.jsonl/.bat;
roles/*/prompts/ and roles/*/INBOX* (no hit addressed to this seat);
archaeon/docs/expansion/DECISIONS.md (no hit);
engine/queues/BACKLOG.jsonl (two rows, items 17 and 18);
engine/ledger/AGENT_AUTOPSIES.jsonl (the P63 autopsy, and Nephele's reuse);
engine/necropolis/ROSTER.jsonl on origin/necropolis/foundation (UNQUEUED);
pivot/COMPONENT_DOSSIERS_2026-06-24.md (the Hypatia and Pheme sections);
pivot/agent_roster_2026-05-21.md; agents/hypatia/CHARTER.md;
the comms inbox at first sync (broadcasts only).

## What was NOT done

No file outside roles/Hypatia/ and agents/hypatia/CHARTER.md was modified.
The daemon was not run. Nothing was dispatched. No ledger belonging to
another lane was edited, including the one this seat believes carries a wrong
number (RESPONSIBILITIES.md section 2).
