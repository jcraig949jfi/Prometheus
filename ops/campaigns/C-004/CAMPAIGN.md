# C-004 -- RSO methods slice S1-S5 (RSO-METHODS-SLICE-001)

Thread TH-RSO-BUILD (ops/threads/TH-RSO-BUILD.md), epic EP-PHASE3 (ops/epics/EP-PHASE3/); added 2026-10-03.

Opened 2026-10-03 as the first operator-selected work-graph campaign (roles/base-role/DISTRIBUTED_WORK.md;
ops/README.md note of the same day). Authority: the operator directive of 2026-10-03, verbatim at
roles/Achilles/prompts/2026-10-03_rso_builder_cell/. Coordinator: Palamedes. Members: the RSO Builder Cell
(roles/rso-builder-role/). Set up by Achilles, who is outside the cell.

Why: Phase 3's design review is closed (docs/phase3/closure/FABLE-5.1/CLOSURE_REVIEW_v0.4.md,
ACCEPT_WITH_MINOR_AMENDMENTS). The next thing is to build the bounded S1-S5 methods slice of
docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/NEXT_ROUND_PLAN_v0.4.md with amendments C1-C5 folded into S1,
let an independent reviewer try to break it once, repair once, and report. Sources: roles/rso-builder-role/SOURCES.md.

What: CAMPAIGN.json (classes, coordinator, open operator decisions) and tasks/*/TASK.json. At setup there is
one READY task, C-004-T000, for Palamedes: decompose the slice into packets. Everything else is created by
Palamedes.

Open operator decisions at setup (they gate work, not the decomposition): OP-1 caps; OP-2 anchor keeper (C5);
OP-3 the S1 expected-answer author and the S3/S4 first-sight reviewer.

## Work graph (Palamedes, C-004-T000, 2026-10-03)

    S1   T001 draft A world/reset/observer/C3 (Cadmus Q2)  T002 draft B receipt/C1/C2/C4/C5/graph (Argus Q2)
         T003 package skeleton + CI command (Eupalamus Q1)
         T004 assemble + FREEZE contract (Palamedes Q2)    <- T001 T002 T003 OP1
         T005 independent expected-answer table (Dionysus Q3, Pallas eligible)  <- T004 OP3
    S2   T010 finite world (Cadmus)  <- T004 T003
         T011 reset/restart/observer + T03-T08 (Cadmus)  <- T010    T012 ruler + calibration T01/T02 (Cadmus) <- T010
         T013 receipt C1/C4 (Argus) <- T004 T003   T014 evidence graph/C5/E01-E05 (Argus) <- T013
         T015 checker + C2 renderer (Argus) <- T014   T016 adapter (Cadmus) <- T010 T013
         T017 mutation runner (Argus) <- T003   T018 E06 twins (Cadmus) <- T010 T012
         T019 run inventory + caps ledger (Eupalamus Q1) <- T003 T004
         T020 integration + matrix vs T005 + FREEZE_S2 (Palamedes) <- T005 T010-T019
    S3   T030 first-sight challenge 5/5/10 (Dionysus Q3, Pallas eligible)  <- T020 OP3     [PROPOSED]
    S4   T040 repair triage -> T04N repair packets (Palamedes) <- T030                   [PROPOSED]
         T041 closure challenge 2/2/3 (Dionysus Q3, Pallas eligible) <- T040            [PROPOSED]
    S5   T050 methods-only report, costs, release receipt, OP5 (Palamedes) <- T041       [PROPOSED]
    OPERATOR  OP1 caps (gates T004, hence all of S2)   OP2 anchor keeper (gates nothing; default custody
              UNQUALIFIED)   OP3 reviewer (gates T005, T030, T041)

S1 and S2 packets are READY (S2 waits on its dependencies); S3-S5 stay PROPOSED until their inputs exist and the
reviewer is named. Pallas has no packet unless OP-3 names it; Q3 is used only for the independent reviewer role.

## Coverage table

    item                                              packet(s)
    ------------------------------------------------  -----------------------------------------------
    S1 claim (retained bit, named boundary, channel)  T001 (text), T004 (freeze)
    S1 state (organism, pending channel, counters)    T001, T010
    S1 truth (world-side enumeration, horizon)        T001, T010
    S1 reset vs restart (separate predicates)         T001, T011
    S1 receipt schema                                 T002, T013
    S1 anchors + attempted-run inventory              T002, T014 (anchors), T019 (inventory)
    S1 gate: typed verdict + reason, prerequisites    T002, T015
    S1 scope: deterministic finite only               T001, T004
    S1 concrete files + finite bounds                 T001, T004
    S1 source/exposure record, trust boundary         T004, T005 (reviewer exposure)
    S1 approved absolute caps                         OP1 -> T004 (contract.json caps), T019 (ledger)
    S1 challenge minimums + reviewer ownership        T004 (S3 5/5/10, S4 2/2/3), OP3
    S1 independent expected-answer table              T005
    C1 execution / authority / outcome                T002, T013, T015 (eligibility), T012 (T02 wording)
    C2 relative claim rendering                       T002, T015
    C3 finite reset model (H, R, escape placement)    T001, T011 (IN-MODEL escapes as fixtures)
    C4 authority stage                                T002, T013; T030 (first-sight), T041 (closed)
    C5 anchor keeper / custody                        OP2, T002, T014
    T01 lawful retained bit                           T012
    T02 no carry: calibration PASS, ruler NEGATIVE    T012
    T03 clean reset + preservation                    T011
    T04 display-only erase, late packet               T011
    T05 indiscriminate wipe                           T011
    T06 complete vs incomplete restart                T011
    T07 observer heals before score                   T011
    T08 repeated-boundary / split-channel leak        T011
    E01 complete bound receipt, unaffected branch     T014
    E02 missing prereq / bad scope / relabel          T014
    E03 dependency stripping / byte alteration        T014
    E04 withdrawn upstream qualification              T014, T015
    E05 fabricated data + fabricated anchors          T014 (custody UNQUALIFIED unless OP2)
    E06 encoding / flattened twin (reported only)     T018, T020
    S2 finite fixture + producer/consumer boundary    T010, T013, T016
    S2 sound + broken cases                           T011, T012, T014, T018
    S2 semantic mutation support                      T017
    S2 integration + matrix + freeze                  T020
    S3 first-sight challenge                          T030
    S4 one repair + fresh closure                     T040, T04N, T041
    S5 report, costs, operator decision               T050 (creates OP5)

Field decisions (rso-builder-role s2.7), recorded here:
- Code lives in a new stdlib-only package rso/slice001/ (uncertainty: layout preference of the builders and the
  native witness; reversible: one rename commit before the S2 freeze; revisit if T003 or the witness needs another).
- Operator decisions are packets with owner_role "operator" (a nominal quality_class Q2, since CAMPAIGN.json
  declares no operator class) so dependency edges show exactly what each decision gates (reversible: replace with
  escalations if the census treats them as seat work; revisit at the first census that miscounts them).
- The contract is drafted in two parallel sections by the owning engineers and assembled by Palamedes, rather than
  written by one seat (uncertainty: merge friction; reversible: T004 may rewrite either draft; revisit if T004
  finds the drafts disagree on a shared field).

## Disposition (2026-10-07, Palamedes) -- CLOSED: INCOMPLETE CLOSURE

T048 (R2 re-check, Pallas Q3) is authoritative (operator directive 2026-10-07, C-004-OP8): C1 CLOSED; C2 NOT
CLOSED (world axis, edit Y1); B3.3 NOT CLOSED (later-window run admitted; FAILED row accepted). OP6's native-witness
condition is not met; no third repair round (OP6). Record: rso/slice001/S5_FINAL_DISPOSITION.md. Earlier freezes
and first-sight results preserved unchanged. Successor: C-009 (RSO-EXEC-BINDING-001), not a repair round of C-004.
