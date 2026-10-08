# C-009 RSO-EXEC-BINDING-001 -- closure (Palamedes, 2026-10-07)

Result: CLOSED, SCOPED TO FLAT INVENTORIES. The binding is qualified for the path the native witness uses; two
BX5b survivors outside that path are recorded, not repaired (CONTRACT.md s3 CC3, registered before any outcome:
"A survivor outside the path the native witness will use is recorded, not repaired"; operator directive 2026-10-07
s5: "no unresolved applicable survivor on the path used by that witness").

## Closure conditions

CC1  HELD. Every C-004 survivor shape has an end-to-end fire case, RED on FREEZE_R2 code, GREEN on C-009 code
     (C-009-T011; 30/30 rows; 7 shapes admitted by FREEZE_R2 on the real S4 bundle). X3 and Y1 verbatim were
     not applicable after the rewrite; their ports X3P and Y1P were killed (recorded at T011 integration).
CC2  HELD. Fresh produce (R1, launches 1-5): matrix identical to S4 bar the predicted E02.MISSING citation
     (O-S4-1 resolved); 30 claims identical in every verdict field (R1/REGRESSION.md; one normalisation gap in
     the prediction text recorded).
CC3  Challenge B1 (Pallas, Q3): BX7 CLOSED; BX1, BX2, BX5 NOT CLOSED (SIBLING_UNREPORTED; E2, E3, E4). The one
     repair round (C-009-T031 + an integrator pin) and its regression (R1/R2CHECK, Q1-Q4 held). Re-check B2
     (C-009-T034, Pallas, Q3): BX1, BX2 CLOSED within coverage; BX5/BX5b NOT CLOSED with two survivors:
       NESTED_SIBLING  a COMPLETED row of a presented node whose parent is the presented node row, not the launch
       E6              BX5b ignores a COMPLETED sibling that carries no digest (edit survives 528 tests)
     Applicability, verified by the coordinator in the committed code, not taken from the report:
     rso/witness/ares_client.py Launch.produce and rso/witness/run_witness.py launch write every node row with
     parent_run_id = the launch, every COMPLETED row with receipt_sha256, FAILED rows without a digest, and
     refuse duplicate nodes at config load. Neither survivor shape can be produced on the witness path.
     So CC3 holds on the registered rule for the witness path and is NOT met for an arbitrary BX6 adapter.
     To make the scope a deterministic predicate rather than a judgment, the witness campaign carries a P-FLAT
     gate (C-010 PREREGISTRATION s5): a witness bundle is refused unless every RECEIPT row's parent is the
     anchored launch, every COMPLETED RECEIPT row carries a digest, and no node has two RECEIPT rows.
CC4  HELD. Stage records regenerated and registered before each first check (rows 48-55, 56-61).

## Qualified surfaces after C-009

  BX1 launch identity                CLOSED within coverage (B1, B2)
  BX2 cited-row binding              CLOSED within coverage (B1 repaired, B2)
  BX5/BX5b own-launch and siblings   CLOSED FOR FLAT INVENTORIES ONLY; NESTED_SIBLING and E6 open (recorded)
  BX7 custody of the inventory       CLOSED within coverage (B1)
  producer side                      unchallenged; CC2 / T033 regressions are its record
Every reviewer is of the builders' vendor family; challenge sizes buy a small challenge, not an error rate.

## Reading not taken, and reversibility

The stricter reading (any BX6 adapter) would close C-009 INCOMPLETE. The operator may choose it at any time; then
witness results are reported as "from a binding closed only for flat inventories", which is what they are under
either reading. Nothing computed under this closure is rewritten by that choice.

## Costs

launches 10 of 12 (R1 produce 5; B1 3, one torn; B2 2); CPU 31.8 of 90 ledgered minutes (LEDGER.jsonl);
artifacts 13.4 MB of 150; GPU 0; $0; repair rounds 1 of 1; reviewer about 1.5 h of 2 h (B1 ~1.0 h, B2 ~0.5 h).
Process failures recorded: two headless reviewer sessions exited mid-run waiting on background jobs (T030, T034);
both finished by same-seat resumes without changing any committed set or outcome.

## Carried forward

1. If a future adapter nests node executions or writes digestless COMPLETED rows: repair BX5b (walk parent_run_id
   to the launch; refuse a digestless COMPLETED sibling), with B2's fixtures as fire cases.
2. workgraph `ready` does not filter on capability class (Pallas, #1786).
3. Headless seats must not use background jobs (two lost sessions).
