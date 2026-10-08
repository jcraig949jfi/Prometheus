+============================================================================+
| RSO COMPLETION PUSH -- CLOSEOUT (operator directive 2026-10-07, C-004-OP8) |
| Author: Palamedes, harry1/M4, claude-opus-5-5, instance harry1-679179c6    |
| Date:   2026-10-07 (directive received 00:25Z; window to 2026-10-10T00:25Z)|
| Status: COMPLETION CONDITION MET EARLY (s7), about 14.3 of 72 hours.       |
+============================================================================+

1. COMPLETION CONDITION (directive s7), item by item
-----------------------------------------------------
  1. C-004 dispositioned and closed honestly    YES  INCOMPLETE CLOSURE
                                                     (rso/slice001/S5_FINAL_DISPOSITION.md)
  2. Successor closes claim-critical surfaces   YES  C-009 CLOSED, scoped to
                                                     flat inventories
                                                     (rso/binding/CLOSURE.md)
  3. One native witness executed                YES  C-010, Ares W15, 3 launches
  4. Reduced to a bounded result                YES  S4 NEGATIVE, S15 NEGATIVE;
                                                     instrument QUALIFIED
  5. Result, costs, escapes, next question      YES  rso/witness/RESULT.md
     committed

2. WHAT COMPLETED
------------------
C-004 closed (T048 integrated as authoritative). C-009: execution binding
(rso/binding), CC1-CC4, one repair round, closed scoped. C-010: preregistration
frozen before any subject run; adapter, driver, evaluator, config generator;
independent challenge W1, one repair round (incl. a pre-outcome NULL amendment),
re-check W2; subjects, seed lists, custody, three witness launches, evaluation.

3. QUALIFIED / NOT-QUALIFIED SURFACES
--------------------------------------
  QUALIFIED (within coverage)  binding BX1, BX2, BX7; BX5/BX5b for flat
                               inventories; witness storage; P-FLAT; the
                               evaluator's repaired surfaces R3-R5; P-CAL on
                               this run
  NOT CLOSED, recorded         BX5b nested / digestless siblings (outside the
                               witness path); W2 pair-gate byte tie and R1
                               census pin (audit shows the run conforms);
                               W1 two-back leak (unreachable under the
                               registered runtime); producer-forgery class
  NOT QUALIFIED                any claim from C-004's G-INV attribution; any
                               channel claim (P-CHAN not reached); anything
                               beyond these two genomes in W15

4. BLOCKERS
------------
None open. One decision is the operator's to revisit at will: the NULL
amendment (rso/witness/AMENDMENT_v1.0.1.md), made pre-outcome by the
coordinator; it made the control stricter and P-CAL passed.

5. RESOURCES
-------------
  C-009  10 of 12 launches; 31.8 of 90 CPU-min; ~1.5 of 2 reviewer-h
  C-010   8 of 10 launches; 26.2 of 60 CPU-min; 10.3 of 200 MB;
          ~1.7 of 1.5 reviewer-h (OVERRUN ~0.2 h, recorded)
  $0, GPU 0 throughout. Seat-hours not metered.

6. WHERE THE OBSERVATORY STILL NEEDED BESPOKE COORDINATION (s8 purpose)
------------------------------------------------------------------------
- Headless seats die when they end a turn waiting on background jobs (lost
  two reviewer sessions); fixed by prompt rule, not by tooling.
- `workgraph ready` does not filter on capability class; a seat's comms
  record can misreport its model (Pallas showed Fable while running Opus 5).
- Implementers twice moved a packet to GREEN without a RED transition and
  once pushed work to main; the coordinator pushed red twice (validation not
  gated). Integration mutations caught two real test gaps the authors missed.
- Interface mismatches between parallel packets surfaced only in the dry run.

7. NEXT PACKET TO RESUME LATER
-------------------------------
C-010-T040 (PROPOSED, operator's call): one preregistered replication of a
published Ares cycle-2 W15 configuration as a positive-candidate subject on
the same frozen instrument, with the GA fitness record committed before the
ruler runs (RESULT.md s8). Not opened as READY: it is a new scientific
question, and the directive's completion condition is met.
