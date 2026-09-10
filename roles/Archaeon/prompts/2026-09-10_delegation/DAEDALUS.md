DAEDALUS -- SCHEMA 8 DEPLOYMENT, NK KIND, COST-VECTOR SEAM, RECON-2
(operator 2026-09-10, via Archaeon; see 00_COMMON.md for authority)

State: joint Track A part 1 PASS 29/29 on a DEV engine (schema 8). Prod
engine on M1 is schema 7 at f1e36c062. Archaeon's producer cost vector is
now engine-postable by construction (archaeon/producer/costs.py
to_engine_entries: five methods, four scopes, no enforcement_class,
provenance in refs). cs-c3-2 is still executing on prod.

DELIVER
1. DEPLOY SCHEMA 8 TO M1 -- authority granted in the operator's name,
   with three conditions: (a) not before cs-c3-2 has 0 queued and 0
   running rows (Archaeon's readout or `viv.cli status` says so); (b)
   Vivarium restarts the consumer after, and you confirm the restart in
   your report; (c) a rollback command and the pre-deploy DB backup path
   are in the committed runbook before the deploy. Commit
   SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOY_SCHEMA8_2026-09-10.md
   with the exact commands, the engine instance id before and after, and
   the source hash. Archaeon moves its reader guard to 8 on your report.
2. POST ONE ARCHAEON VECTOR: on the dev engine, post the output of
   `costs.to_engine_entries(event)` for a real producer CostEvent (e.g.
   from archaeon/docs/h0h5/ISSUE_RECEIPTS_2026-09-10.h1h0_p1.json,
   `engine_entries`) and commit the 200 response with the enforcement
   classes the engine stamped. That closes TRACKA-VECTOR-1 end to end.
3. TRACKA-RECON-2: accepted -- join on the DIGEST. Make the executor's
   and engine's cost entries carry the artifact digest in refs where an
   artifact moved, so Archaeon's reconcile can join on it. Path + SHA.
4. NK LANDSCAPE KIND: status of nk_landscape (or whatever it is named)
   as a Vivarium-registered kind with result_schema; if not started, the
   obstruction and the smallest slice you can land today. This gates
   Archaeon's A2 templates (Track E).
5. BRANCHES: none of yours are listed as stale; confirm.

REPORT: SHA on main and path per item; exact commands; deploy conditions
(a)-(c) each with its evidence.
